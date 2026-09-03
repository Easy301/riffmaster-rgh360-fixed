# Known issues, limitations, and unverified claims

Confidence tags are used throughout and mean what they say:
`[VERIFIED]` observed on hardware · `[HYPOTHESIS]` believed, not confirmed ·
`[UNVERIFIED]` never tested.

---

## The big one: sample size is one

**Everything here was developed and tested on a single console with a single guitar.**
One Jasper fat, RGH1.2, kernel 17559, Aurora, `UsbdSecPatch` in NAND. One PDP RiffMaster
and its dongle. Two games.

That is enough to say "this works", and nowhere near enough to say "this works for you".
Console-to-console variation in RGH setups is substantial. Treat every claim below as
scoped to that one machine.

---

## Functional gaps

### No rumble `[VERIFIED]`
Inherited from upstream hiddriver360. Irrelevant for a guitar.

### Solo frets work `[VERIFIED]`
The RiffMaster has two rows of fret buttons: the main five up the neck, and the **solo
frets**, the smaller row down near the strum bar.

Xbox 360 guitars report solo frets as a **flag overlaid on the normal frets**, not as
independent inputs — pressing a solo fret makes the normal frets read as solo. GIP-era
guitars send them independently, so this is a translation, not a passthrough: the
independent GIP solo frets are collapsed back into the 360's overlaid scheme
(`frets = upper | lower`, plus `LEFT_THUMB` whenever any lower fret is held).

`[VERIFIED]` **The solo frets register correctly and behave like the matching normal
frets.** The collapse works.

`[VERIFIED]` **They also work through a full song, solo passages included.** This was the
last open question here — whether a game credits notes played on the solo frets, which is
the case the `LEFT_THUMB` flag exists to signal. Played start to finish on hardware
(single console, single guitar — see [the big one](#the-big-one-sample-size-is-one)); the
solo frets behaved correctly for the whole song.

One inherent limit, unfixable rather than unfinished: **upper-green plus solo-red at the
same time is not representable** on the 360, which has five fret bits and one solo flag.
That is a limit of the target format, not of this driver.

### Tilt threshold is fixed, not calibrated `[PARTLY RESOLVED]`
The star-power tilt threshold is `0xD0`, inherited from RB4InstrumentMapper — whose own
comment says it "should probably be configurable".

`[VERIFIED]` **In practice it feels right** — no spurious star power reported in play on
the test guitar. The earlier concern was that observed resting tilt drifted as high as
`0xDD`, above the threshold; that has not translated into a problem on hardware.

Still worth improving eventually: it is one hardcoded number for all guitars, with no
calibration at connect and no user setting. A different unit, or one that rests at a
different angle, could behave worse. If star power fires on its own for you, this is why.

### The RiffMaster has no pickup switch `[VERIFIED]`
`[VERIFIED]` The guitar has **no physical pickup switch**, so the 5-notch mapping is
untestable on this hardware and effectively unused.

The plugin still reports a pickup value on the left trigger, because a real Xbox 360 Rock
Band guitar always does and games expect the field to exist. With no switch to move, it
reports a constant (notch 1, `0x17`) — the same thing a real guitar with the switch parked
would report. Harmless.

`[UNVERIFIED]` What byte 11 of the GIP report actually carries on a switchless RiffMaster
has not been checked — it is decoded as "pickup" on the strength of the report layout, not
because the control was ever observed moving. If a RiffMaster variant with a pickup switch
exists, that is the field to look at first.

### Per-title subtype: 21 titles verified `[VERIFIED]`
`SubType 0x06` works in 20 of the 21 titles tested. **Guitar Hero III (`0x415607F7`) is the
sole exception** and gets `0x07` applied automatically. Full table in the README.

Still untested and wanted: Guitar Hero: Warriors of Rock, Rock Band Blitz, Rock Band
Country Track Pack 3 / other track packs, Green Day: Rock Band (see below), and **any
regional variant** — a PAL disc may carry a different title ID than the NTSC one in the
table, miss the override, and fail even though the game is "supported".

### Green Day: Rock Band crashes on startup `[UNATTRIBUTED]`
Crashes on launch, reproducibly (twice), before input is relevant. **This has not been
attributed to the plugin** — the obvious control, launching it with the plugin unloaded,
has not been run. Could equally be a bad rip or a missing dependency. If you have this
game, running that control would settle it.

The override table only contains titles observed to **fail** with the default. An entry
matching the default would do nothing except create somewhere for a typo to silently break
a working game. Do not populate it from a title-ID list found online; every row needs a
console log behind it.

---

## Structural issues

### A device object leaks on every plug/unplug cycle `[VERIFIED]`
**This is the cost of the disconnect fix.** For our device, the removal hook cleans up and
returns without calling the kernel's original, so the USB core never completes teardown of
that device object.

Observed: device handles advance by `0x20` per plug cycle (`E1EBF3C0` → `E1EBF3E0`), one
pair per cycle — the GIP interface and the audio interface.

Bounded and slow. **Untested past a handful of cycles.** If claiming eventually starts
failing after many plug/unplug cycles in one boot, this is why, and a reboot will clear
it. If you can stress-test this, that datapoint is wanted.

Why it is done this way, and why the obvious alternatives were all tried and rejected, is
in [HOW_IT_WORKS.md](HOW_IT_WORKS.md#the-disconnect-problem).

### Only one hiddriver360-derived plugin at a time `[VERIFIED]`
Two of them detour the same kernel addresses, and the second trampoline points back into
the first. The console freezes on entering the dashboard. If you already run hiddriver360
for a DualShock or Switch Pro controller, you cannot run this alongside it.

### Base address collisions fail silently `[VERIFIED]`
The plugin loads at `0x81F00000`. A collision with another plugin does not produce an
error — you get a silent no-op or a hang. Change `<baseaddr>` in
`src/riffmaster/xex.xml` and rebuild.

### Kernel-build specific `[VERIFIED]`
Every raw kernel address is specific to 17559 retail / 17489 devkit. The plugin refuses to
load on any other build, deliberately. Do not remove that check to "try it anyway" — the
patches would land on whatever happens to occupy those addresses.

### `UsbdSecPatch` dependency is unknown `[UNVERIFIED]`
Every result was obtained with `UsbdSecPatch` flashed into NAND. In principle it should be
unnecessary — the dongle is claimed after the kernel has already enumerated it, and
`UsbdSecPatch` only removes the XSM3 auth gate. But this has never been tested without it.

### FTP + third-party guitar freeze `[PARTLY RESOLVED]`

**1.04 stable** includes the notify patch for freezes when you plug a third-party guitar
while a **PC FTP client** is connected. Aurora's FTP server can stay on — the open session
on your PC is what matters. If you still see freezes, close the FTP program before
hot-plugging a guitar.

### Guitar-only, dongle-only `[VERIFIED]`
Matched strictly on VID `0E6F` / PID `0248`, interface 0, class `FF/47/D0`. Other
RiffMaster hardware or firmware revisions with different IDs will not be claimed.

The guitar's USB-C port is not an alternative: it only enumerates in firmware-bootloader
mode (PID `0247`), which is not a gameplay mode.

---

## Diagnostics that mislead

Three things that cost this project real time. If you debug it, know them up front.

### `D3D::DebugGpuDeadlock` does not mean the GPU is hung `[VERIFIED]`
A freeze produces a D3D banner ending `"...can't be recovered without doing a cold boot"`.
That is D3D's GPU watchdog, and it is **misleading** — dumping the GPU registers during
an actual freeze showed `CP_RB_RPTR == CP_RB_WPTR` with both indirect buffers empty. The
GPU had consumed everything submitted and was idle.

It is not deadlocked, it is **starved**: the CPU stopped feeding it. The five seconds
between the freeze and the banner is just the watchdog timeout, so the real event happened
five seconds earlier than the log suggests.

### `0x82DA0100` is a PC-side error `[VERIFIED]`
`Exception from HRESULT: 0x82DA0100` is `XBDM_CANNOTCONNECT` — *"Cannot connect to the
target system"* (`xbdm.h:704`). It is raised by **xbWatson on your PC** when it loses the
console. It is not an Xbox error code and says nothing about what went wrong.

### `0xE06D7363` exception floods are the dashboard, not you `[VERIFIED]`
`Exception : <thread> E06D7363 <addr> FirstChance` spam once Aurora loads is harmless.
`0xE06D7363` is the MSVC C++ `throw` magic, and it comes from Aurora's own ATG-framework
resource loader. It continues with the dongle physically removed. Do not chase it.

### xbWatson silence proves nothing at boot `[VERIFIED]`
The plugin's load banner prints during boot, before xbWatson can attach. Attach first,
*then* power the guitar on. To confirm the plugin is actually resident, connect to TCP
port 730 and send `modules` — `riffmaster.xex` should be listed at base `0x81f00000`.

### This console does not answer ICMP `[VERIFIED]`
`ping` times out while the console is fully up and serving xbdm. Never use ping to decide
whether a console is alive; use the debug monitor on port 730.
