> **Fork notice:** This is a **patched community fork** of
> **[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360)** with fixes for
> RiffMaster RSA auth on some units and **UsbdSecPatch / CRKD coexistence**. The vast
> majority of credit belongs to **Durg5**, **EinTim23**, and everyone listed in
> [NOTICE.md](NOTICE.md) and [CREDITS.md](CREDITS.md). See [FORK-NOTICE.md](FORK-NOTICE.md)
> and [CHANGELOG.md](CHANGELOG.md).

<p align="center">
  <img src="docs/logo.png" alt="riffmaster-rgh360" width="620">
</p>

<p align="center">
  <b>Use a PDP RiffMaster (TESTED ONLY WITH PC/XBOX SERIES S/X) wireless guitar on an RGH/JTAG Xbox 360, as a real guitar
  controller, in Guitar Hero and Rock Band.</b>
</p>

<p align="center">
  A single DashLaunch plugin. No donor Xbox 360 controller, no external hardware,
  no companion app, no NAND changes.
</p>

> ⚠️ **BETA.** Developed and tested on exactly one console against one guitar. It patches
> live kernel code and claims a USB device out from under the console's own USB core. It
> works well there — full songs, start to finish — but the sample size is one. Worst case
> is a console needing a hard power-off, so back up anything you care about.
> See [docs/KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) before putting it in a daily driver.

---

## How it works

The RiffMaster and its 2.4 GHz dongle speak **GIP**, the Xbox One / Series protocol. The
Xbox 360 has no GIP driver and never will, so a stock console enumerates the dongle, finds
no driver, and ignores it. This plugin fills that gap entirely on-console:

1. **Claims the dongle** — the kernel reports it unclaimed via `UsbdAddDeviceComplete`,
   which we detour.
2. **Brings up GIP** — `SET_CONFIGURATION`, both interrupt endpoints, then
   `ANNOUNCE` → `IDENTIFY` → chunk ACKs → locale → power-on → LED.
3. **Completes the auth handshake** — PDP guitars will not stream input until a TLS-like
   RSA-2048 exchange finishes. No Microsoft secret needed: the host encrypts a random
   premaster to the device's own public key, taken from the certificate the device sends.
4. **Decodes the input reports** and translates them to the Xbox 360 guitar format.
5. **Registers a virtual controller inside XAM** as `XINPUT_DEVSUBTYPE_GUITAR`, so the
   whole console UI — ring of light, sign-in, games — sees a real guitar.

Full detail in [docs/HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md); the byte-level protocol spec
is in [docs/PROTOCOL.md](docs/PROTOCOL.md).

## What works

- Frets, strum, whammy, tilt, Start/Back, guide button, and the solo frets
- Navigating the dashboard and Aurora with the guitar
- Real Xbox 360 controllers on other ports keep working normally
- **Disconnecting behaves like a real controller.** Unplug the dongle or power the guitar
  off mid-song and the game pauses with the normal reconnect prompt; plug back in and it
  re-enumerates, re-authenticates and resumes. No freeze, no reboot.
- **Upstream hiddriver360's controller support is left switched on** — DualShock 3/4,
  DualSense, Switch Pro and other USB HID gamepads via its mapping system. It has not been
  re-tested since the guitar work landed, but nothing in those paths was changed. This
  matters because only one hiddriver360-derived plugin can be loaded at a time, so
  stripping it out would mean choosing between the guitar and your DualSense.

## What doesn't, or is unproven

Full detail in [docs/KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md):

- **No rumble.** Inherited from upstream, irrelevant for a guitar.
- **Tilt threshold is a guess** and may trigger spurious star power.
- **The pickup switch mapping is unverified** — it was never actuated during capture.
- **Only tested on one console and one guitar.**
- **A device object leaks on every plug/unplug cycle.** Bounded and slow, but real.

---

## Install

**End users (no XDK):** download **`riffmaster.xex`** from
**[GitHub Releases](https://github.com/PLACEHOLDER/riffmaster-rgh360-fixed/releases/latest)**
and follow [docs/INSTALL-FIXED.md](docs/INSTALL-FIXED.md).

Full install guide and troubleshooting: [docs/INSTALL.md](docs/INSTALL.md). Building from
source: [docs/BUILDING.md](docs/BUILDING.md). Patch an upstream xex without the XDK:
`python tools/apply_full_patch.py` (needs `tools/xextool.exe`).

1. Copy `riffmaster.xex` to `Hdd:\riffmaster.xex` (from Releases or `bin/`).
2. Add one line to the `[Plugins]` section of `launch.ini`, using a free slot, without
   disturbing the plugins already listed:
   ```ini
   plugin3 = Hdd:\riffmaster.xex
   ```
   In DashLaunch, save the ini properly ("Save \ Load launch.ini" → save to HDD) — edits
   do not persist otherwise.
3. **Hard reboot.** A warm reboot does not reliably reload an updated plugin.
4. Plug in the dongle, then turn the guitar on. Give it a few seconds for the handshake.

## Requirements

| | |
|---|---|
| Console | RGH / JTAG Xbox 360, able to load DashLaunch plugins |
| Dashboard | **kernel 17559** (retail) or **17489** (devkit) — the plugin refuses to load on anything else |
| DashLaunch | any version supporting `pluginN =` entries |
| Hardware | PDP RiffMaster guitar **and its 2.4 GHz USB dongle**, VID `0E6F` PID `0248` |
| Disc tray | must be closed at boot (inherited upstream check) |

The guitar's USB-C port is **not** an alternative to the dongle — it only enumerates over
USB-C in firmware-bootloader mode, which is not a gameplay mode.

**`UsbdSecPatch`:** in principle not needed, since the dongle is claimed after the kernel
has already enumerated it — but every result here was obtained on a console that has it in
NAND, so standing alone without it is unverified. If the dongle is never claimed, suspect
this first.

**Plugin base address:** the plugin loads at `0x81F00000` (set in
`src/riffmaster/xex.xml`). Two plugins at the same base collide, and the symptom is a
silent no-op or a hang rather than an error. Also note **only one hiddriver360-derived
plugin at a time** — two of them detour the same addresses and freeze the console.

---

## Game compatibility

The XDK defines two guitar subtypes: `0x06` `XINPUT_DEVSUBTYPE_GUITAR` (Rock Band) and
`0x07` `XINPUT_DEVSUBTYPE_GUITAR_ALTERNATE` (Guitar Hero). The plugin defaults to `0x06`
and **switches automatically per title** where a game is known to need otherwise.

**21 titles tested on hardware. 20 work out of the box; exactly one needs an override, and
it is applied for you.**

| Game | Title ID | Subtype | Result |
|---|---|---|---|
| Guitar Hero 1 | `0x41560883` | `0x06` | ✅ |
| Guitar Hero II | `0x415607E7` | `0x06` | ✅ |
| **Guitar Hero III: Legends of Rock** | `0x415607F7` | **`0x07`** | ✅ override applied automatically |
| Guitar Hero: Aerosmith | `0x41560819` | `0x06` | ✅ |
| Guitar Hero: World Tour | `0x4156081A` | `0x06` | ✅ |
| Guitar Hero: Metallica | `0x41560830` | `0x06` | ✅ |
| Guitar Hero: Van Halen | `0x4156083D` | `0x06` | ✅ |
| Guitar Hero: Smash Hits | `0x4156083E` | `0x06` | ✅ |
| Guitar Hero 5 | `0x41560840` | `0x06` | ✅ |
| Band Hero | `0x4156085C` | `0x06` | ✅ |
| Rock Band 1 | `0x45410829` | `0x06` | ✅ |
| Rock Band 2 | `0x45410869` | `0x06` | ✅ |
| Rock Band 3 | `0x45410914` | `0x06` | ✅ |
| Rock Band: AC/DC Live | `0x45410889` | `0x06` | ✅ |
| The Beatles: Rock Band | `0x454108B1` | `0x06` | ✅ |
| Lego Rock Band | `0x575207F0` | `0x06` | ✅ |
| RB Track Pack Vol. 2 | `0x45410881` | `0x06` | ✅ |
| RB Track Pack: Classic Rock | `0x454108B0` | `0x06` | ✅ |
| RB Country Track Pack | `0x454108CA` | `0x06` | ✅ |
| RB Country Track Pack 2 | `0x4541092C` | `0x06` | ✅ |
| RB Metal Track Pack | `0x454108CD` | `0x06` | ✅ |
| Green Day: Rock Band | — | — | ⚠️ crashes on startup |

Guitar Hero III is the only title that rejects `0x06`, with no pattern anyone has found —
**do not infer a subtype from the publisher prefix.** Green Day: Rock Band crashes before
input is relevant; that has **not** been attributed to this plugin, and it has not been
retested with the plugin unloaded.

> ⚠️ **These are NTSC discs.** Title IDs can differ by region and between reissues, so a
> PAL copy of GH3 may not match the override. Check the `title id 0x........` line in the
> log against `0x415607F7` — if it differs, the fix is one more table entry. Please report
> it.

**Adding a title:** the override table is `g_gipTitleSubTypes` in
`src/riffmaster/main.cpp`, and by design it only lists titles observed to *fail* with the
default. Boot the game, read the `RIFFMASTER: title id ... -> SubType ...` log line, and
if the guitar worked, add nothing. If it didn't, add
`{ <id>, XINPUT_DEVSUBTYPE_GUITAR_ALTERNATE, "name" }` and re-test.

---

## Credits

**Almost nothing here is original work.** This fork adds three small fixes on top of
**[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360)**, which itself
sits on years of reverse engineering published for free. **Most of the thanks belongs to
Durg5, EinTim23, and the upstream chain** — see [CREDITS.md](CREDITS.md) for the full
list and [FORK-NOTICE.md](FORK-NOTICE.md) for what this fork changed.

- 🎸 **[Durg5 / riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360)** — the
  RiffMaster GIP driver this fork is based on. Without that project, none of this exists.
- 🎸 **[EinTim23 / hiddriver360](https://github.com/EinTim23/hiddriver360)** — this project
  is a fork of it, and the single reason it exists. It proved a DashLaunch plugin can
  detour the 360's USB stack and register a virtual controller *inside XAM*, so the whole
  console UI treats it as real. Everything here sits on that foundation.
- 🥁 **[jpdown / hiddriver360-rb1wii](https://github.com/jpdown/hiddriver360-rb1wii)** —
  prior art for turning a gamepad driver into an *instrument* driver. Drums, not guitar,
  so the value didn't carry over, but it showed exactly which line governs how a device
  presents itself to a game.
- 🎵 **[TheNathannator](https://github.com/TheNathannator)** —
  [PlasticBand](https://github.com/TheNathannator/PlasticBand), the definitive
  plastic-instrument protocol documentation (subtypes, button map, axes, the overlaid
  solo-fret scheme, real hardware dumps), and
  [RB4InstrumentMapper](https://github.com/TheNathannator/RB4InstrumentMapper), whose
  RiffMaster parser was the primary cross-check for the input report map — the two agree
  on every field. ☕ **Ko-fi: <https://ko-fi.com/thenathannator>**
- 🐧 **[medusalix / xone](https://github.com/medusalix/xone)** — the Linux GIP host driver,
  and the reference for how the protocol works on the wire: header format, the
  variable-length encoding a naive fixed header corrupts, chunking, and the auth flow.
  💰 **[PayPal](https://www.paypal.com/donate?hosted_button_id=BWUECKFDNY446)**
- ⚙️ **[iMoD1998](https://github.com/iMoD1998)** — the PowerPC branch-detour implementation
  that makes hooking a live 360 kernel possible at all. Every hook here runs through it.
- 🔬 **[Xenia](https://github.com/xenia-project/xenia)** — independent second source for
  XAM and kernel export ordinals.
- 🧰 **[DashLaunch](https://github.com/Wildthing33/dashlaunch)** (cOz), the plugin loader
  this whole category depends on; **[RapidJSON](https://github.com/Tencent/rapidjson)**
  (Tencent, MIT); **xkelib**, whose original authorship is genuinely unclear — the most
  referenced copy is in
  [jogolden/testdev](https://github.com/jogolden/testdev/tree/master/xkelib), so if you
  know who deserves credit, tell me; and **xextool**, required to mark the built xex
  retail.

If you contributed to something used here and are not credited, or are credited wrongly,
**open an issue and I will fix it.** Attribution errors are bugs.

## Licence

**GPL-3.0**, inherited from hiddriver360. See [LICENSE](LICENSE). The projects credited
above carry their own differing licences; nothing from them is copied verbatim here, and
they are cited inline in the source — see [NOTICE.md](NOTICE.md).

## Contributing

The most useful contributions right now are **datapoints**, not code:

- Does it work on your console revision / kernel / dashboard?
- Does it work without `UsbdSecPatch`?
- Does upstream's DS4 / DualSense support still work?
- Does tilt star power fire when it should, and only then?
- Does the pickup switch map correctly?

Please include your console model, kernel build, dashboard, and plugin list — and if
anything goes wrong, an xbWatson log. Lines from this plugin are prefixed `RIFFMASTER:`;
upstream's are prefixed `EINTIM:`.
