# How it works

The problem in one sentence: **the RiffMaster dongle speaks GIP, the Xbox 360 has no GIP
driver, and it never will.**

A stock console enumerates the dongle perfectly well — reads its descriptors, assigns it a
device handle — then looks for a driver, finds none, and drops it. Everything this plugin
does follows from picking the device up at that exact moment.

---

## 1. Claiming the dongle

`[VERIFIED]` The dongle presents as USB interface class `FF` / subclass `47` / protocol
`D0` — vendor-specific, **not HID**.

That matters because upstream hiddriver360 hooks the HID driver's own AddDevice callback,
and a vendor-class device never reaches it. A test build that logged every device arriving
at that hook saw a DualSense but never saw the dongle or even a USB flash drive. The hook
sits downstream of class dispatch.

The opening is one layer up. When the USB core gives up on a device it calls:

```c
UsbdAddDeviceComplete(deviceHandle, 0xC0000001)   // STATUS_UNSUCCESSFUL, driver = NULL
```

That is a **kernel export, ordinal 740**, resolvable with `XexGetProcedureAddress` — no
reverse engineering, no kernel dump. We detour it. At that moment we hold a live device
handle, know the VID/PID and interface class, and control the status that gets passed on.

For VID `0E6F` / PID `0248`, interface 0 only (interface 1 is audio and has no endpoints),
we complete with status `0` instead. The device is ours.

## 2. GIP bring-up

`SET_CONFIGURATION` over the default endpoint, then open both interrupt endpoints
(`0x81` IN, `0x02` OUT, 64 bytes, `bInterval` 4 — read from the descriptors, not assumed).

The device then sends `ANNOUNCE` (`0x02`) unprompted, and the handshake runs:
`IDENTIFY` → chunk ACKs → locale → power-on → LED.

Two details that are easy to get wrong and were both expensive here:

- **Every chunk of one GIP message shares a single sequence number, and ACKs must echo the
  sequence being acknowledged.** Get this wrong and the device ACKs each chunk — looking
  perfectly healthy — while never reassembling, then goes silent instead of erroring.
- **GIP length fields are varints,** and headers are padded to an even length. A fixed
  4-byte header parses input reports fine and then silently corrupts the longer
  announce/descriptor packets, which are exactly the ones needed for init.

Full byte-level spec: [PROTOCOL.md](PROTOCOL.md).

## 3. Authentication

`[VERIFIED]` PDP guitars will not stream input until a TLS-like handshake completes. This
is mandatory — there is no skip.

It needs **no Microsoft secret**. The device sends its own certificate; the host extracts
the RSA-2048 public key from it, encrypts a random premaster secret to that key, and the
two sides derive session state from the transcript.

Implementation notes worth keeping:

- `XeCryptBnQwNeRsaPubCrypt` could not be made to work — 729 parameter permutations were
  searched with no match, and `qwReserved` appears to need an undocumented Montgomery
  constant. **The plugin uses its own 2048-bit bignum modexp** (`gip_auth.h`), validated
  offline against Python before ever running on console. There is a self-test at runtime:
  `RSA SELFTEST: PASS`.
- `XeCryptSha256` is not declared in `xkelib` (it appears only in an ordinal comment) but
  *is* present in `kernelext.lib`. Declare it with `XeCryptSha`'s three-buffer signature.
- **Transcript hashing is asymmetric.** Sent packets hash `[6, 6 + data_len)`, excluding
  the 8-byte trailer; received packets hash `[6, len)`. REQUEST packets and bare ACKs are
  never hashed.
- The device takes **~680 ms** to RSA-decrypt the premaster, so the tail of the handshake
  must be response-driven, not fired back-to-back.

## 4. Input decode and 360 translation

GIP input reports (command `0x20`) are decoded with **explicit masks and shifts, never
bitfields** — MSVC allocates bitfields MSB-first on PowerPC and LSB-first on x86, so a
struct copied from an x86 reference compiles cleanly and decodes wrong with no warning.

Frets map to face buttons, strum to D-pad up/down, whammy and tilt to analog axes. All
multi-byte values are byteswapped: the USB stream is little-endian, the 360 is big-endian.

The one non-obvious transform: **solo frets.** The 360 reports them as a flag overlaid on
the normal frets, while GIP sends them independently, so the independent GIP inputs are
collapsed back into the 360's overlaid scheme.

## 5. Registering with XAM

This half is upstream hiddriver360's work and is the reason this project forked it rather
than starting fresh.

A virtual controller is registered via `XamUserBindDeviceCallback` with a magic context,
then these are detoured to answer for the virtual index while passing every real index
through untouched:

| Ordinal | Function | |
|---|---|---|
| 400 | `XamInputGetCapabilities` | |
| 401 | `XamInputGetState` | |
| 402 | `XamInputSetState` | hooked upstream |
| 685 | `XamInputGetCapabilitiesEx` | hooked upstream |
| 486 | `XInputdReadState` | kernel-side |

**Upstream only hooks 402 and 685.** Guitar Hero goes through the `Ex` path and worked;
Rock Band uses the plain non-`Ex` calls and saw no device at all until 400 and 401 were
added. That is likely a genuine upstream bug.

Also: **`capabilities->Gamepad` is a capability *mask*, not live state.** Upstream fills it
from `XInputGetState`, which is semantically wrong. This plugin reports a real Rock Band 1
Stratocaster's values — Flags `0x000C`, Buttons `0xF57F`, RightThumb X/Y `0xFFC0`.

The capability hooks are **hot** — roughly 8 calls per 100 ms. Unconditional `DbgPrint`
there saturates xbdm and hangs the console. All logging on those paths is rate-limited or
compiled out.

---

## The disconnect problem

Worth reading if you intend to change the USB code, because the obvious fixes are all
wrong and were all tried.

**Symptom:** with the guitar claimed, unplugging the dongle or letting the guitar sleep
froze the console completely — no video, no xbdm, no FTP, ARP entry gone. Recovery was a
hard power-off.

### What it was not

An additive build ladder was used: start from a plugin that does nothing and add one
subsystem per rung. Levels 0–6 — between them, *all* of stock hiddriver360 — survive
removal. Only the rung that adds this project's claim froze.

Then the claim itself was split apart:

| Build | Removes | Result |
|---|---|---|
| `passive` | our entire teardown | froze |
| `noxam` | XAM registration | froze |
| `once` | re-claim churn during the bounce storm | froze |
| `noread` | the interrupt read loop entirely | froze |
| **`claimonly`** | **everything except the claim** | **froze** |

`claimonly` opens no endpoints, queues no transfers, never touches XAM and runs no auth.
Its entire contribution is:

```c
h->driver = &g_gipExt;
UsbdAddDeviceComplete(h, 0);
```

And `keepdriver` — which claims but never writes `h->driver`, leaving it `00000000` —
froze too.

### What it is

**Reporting the claim is the fatal act, not the fabricated extension pointer.**

The core asks each driver in turn to take the device; all decline; the final decline
arrives as status `0xC0000001`. Converting that to success makes the core believe *some
driver owns this device* — and that driver has no record of it. On removal the core hands
the device back to its supposed owner, and that takes the dashboard's input path, and
therefore the render thread, down with it.

A legitimate claim looks different. Mass storage, from a probe build:

```
ADDCOMPLETE handle=E1EBF3B0 status=0x00000000 (CLAIMED) driver=801A87E0
```

`0x801A87E0` is kernel `.data` — a real driver object. Ours pointed into the plugin.

### Why not simply not claim

Tried. `noclaim` passes the failure status through and never writes `h->driver`. It
**survives removal perfectly** — our handle does not even enter the removal path, the core
just drops it.

But the guitar is dead: **the core accepts transfers for an unowned device and never
services them.** `UsbdOpenDefaultEndpoint` returns success, `SET_CONFIGURATION` is queued,
and its completion never arrives.

So: claim = works but freezes; no claim = safe but dead.

### The fix

Claim it, drive it, and **never tell the core the removal finished.**

In `UsbdRemoveDeviceCompleteHook`, for our device only, do the teardown and `return 0`
without calling the original. Every other device still takes the kernel's normal path.

This is the same shape upstream already uses for HID devices — `HidRemoveDeviceHook`
frees its extension and returns `0` without calling through.

`[VERIFIED]` Survives a hot dongle unplug and the guitar powering off, and re-claims
cleanly on replug with full GIP bring-up, RSA auth and XAM registration.

**The cost:** the core never completes teardown of that device object, so a handle pair
leaks per plug cycle. See [KNOWN_ISSUES.md](KNOWN_ISSUES.md#structural-issues).

### If you want to do better

The right fix is presumably to give the core a **genuine driver object** rather than
fabricating an extension, so that removal dispatches somewhere that can actually handle
it. That needs reverse engineering of the 360 USB core's driver registration, which needs
a decrypted `xboxkrnl.exe` — work this project never did. Every kernel address here came
from upstream's source, not from a dump.
