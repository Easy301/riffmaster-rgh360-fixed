# Credits and attribution

This repository is a **community patch fork** of
**[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360)**, which is a
fork of **[EinTim23/hiddriver360](https://github.com/EinTim23/hiddriver360)**. It is
licensed **GPL-3.0**, inherited from upstream. See [LICENSE](LICENSE), [CREDITS.md](CREDITS.md),
and [FORK-NOTICE.md](FORK-NOTICE.md).

## Durg5 — riffmaster-rgh360

**[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360)** added the RiffMaster
GIP protocol, USB claim, RSA auth handshake, input translation, and game compatibility work
on top of hiddriver360. **Most of the credit for anything guitar-related belongs here.**

## hiddriver360 — EinTim23

## hiddriver360 — EinTim23

The foundation, and the genuinely hard part of this problem.

hiddriver360 established that a DashLaunch plugin can detour the Xbox 360's USB stack and
register a **virtual controller inside XAM**, such that the entire console UI — ring of
light, sign-in, games — treats it as a real controller. It supports up to four concurrent
controllers alongside or instead of original pads, on both 17559 retail and 17489 devkit,
with no USB patches and no dongles.

This project reuses that whole half essentially unchanged: the plugin structure, the
detour mechanism, the kernel and XAM ordinal resolution, and the XAM registration path.
Building a working guitar on top of it took protocol work and a USB claim; building it
from nothing would have taken an order of magnitude more.

Files inherited largely or entirely unmodified: `Detours.h`, `Detours.cpp`,
`hid_parser.h`, `hid_parser.cpp`, `mapping.h`, `mapping.cpp`, `usb.h`, `rapidjson/`,
`xkelib/`, the project and solution files, and the overall shape of `main.cpp`.

## jpdown / hiddriver360-rb1wii

**[jpdown/hiddriver360-rb1wii](https://github.com/jpdown/hiddriver360-rb1wii)**, branch
`rb1wiidrums`, is prior art for the specific transformation this project performs: turning
a gamepad driver into an **instrument** driver.

It adds a `HARMONIX_ROCK_BAND_1_WII` controller type and sets
`capabilities->SubType = XINPUT_DEVSUBTYPE_DRUM_KIT`. That is drums rather than guitar, so
the *value* did not transfer — but it showed exactly which line governs how a device
presents itself to a game, which was the hardest open design question at the start of this
project.

## iMoD1998 — Detours

The PowerPC branch-detour implementation (`Detours.h` / `Detours.cpp`, V3.1) that makes
on-console function hooking possible. Vendored via hiddriver360.

## PlasticBand

**[PlasticBand](https://github.com/TheNathannator/PlasticBand)** — documentation of
plastic instrument protocols, licensed CC BY-SA 4.0.

The Xbox 360 guitar target format used here — subtype values, the button map, the analog
axis assignments, the overlaid solo-fret scheme — comes from PlasticBand's documentation
and its capability dumps of real hardware, including the Rock Band 1 Stratocaster values
this plugin reports.

## RB4InstrumentMapper

**[RB4InstrumentMapper](https://github.com/TheNathannator/RB4InstrumentMapper)** carries a
dedicated RiffMaster parser matched on this exact VID/PID. It was the primary
cross-check for the input report map, and the two agree on every field. The tilt
star-power threshold (`0xD0`) is inherited from it — including, in fairness, its own
comment that the value "should probably be configurable".

## xone

**[medusalix/xone](https://github.com/medusalix/xone)** — the Linux GIP host driver. Its
`gip.c` header parser and initialisation sequence were the reference for GIP framing,
including the variable-length length encoding that a naive fixed-size header gets wrong.

## Xenia

**[xenia](https://github.com/xenia-project/xenia)** — used as an independent second source
for XAM and kernel export ordinals, cross-checking the values derived from hiddriver360's
source.

---

## Reading the citations in the source

Comments in `src/riffmaster/` cite their sources with paths like:

```
refs/xone/bus/protocol.c:244-262
refs/PlasticBand/Docs/Descriptor Dumps/Xbox 360/...
refs/xenia/src/xenia/kernel/xam/xam_table.inc:197-199
```

`refs/` is not a directory in this repository. It refers to a **local checkout of the
upstream project named in the path** — `xone`, `PlasticBand`, `xenia`,
`RB4InstrumentMapper — all linked above. Line numbers are from the revision current when
the comment was written, so treat them as a strong hint rather than an exact offset.

The convention exists because every non-obvious constant in this driver — every offset,
every opcode, every ordinal — is supposed to be traceable to either a packet capture or a
citable source, rather than to somebody's memory. If you add one, cite it.

## On upstream bugs

Two defects were found in inherited code during this work. Both are noted in the source
where they occur, and both are worth reporting upstream:

1. **`XamInputGetCapabilities` (400) and `XamInputGetState` (401) are not hooked.** Only
   402 and 685 are. Titles using the non-`Ex` entry points — Rock Band among them — see no
   device at all.
2. **`XamInputGetCapabilitiesExHook` falls off the end of a non-void function** on its most
   common path (a real, connected controller, queried ~8 times per 100 ms). It has worked
   by accident because MSVC leaves the status value in `r3`; that is register allocation,
   not semantics.
