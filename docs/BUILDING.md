# Building

Windows only. The Xbox 360 XDK is a Windows toolchain and there is no substitute for it
here — see [Why not libxenon](#why-not-libxenon-or-a-cross-compiler).

## Prerequisites

| | Notes |
|---|---|
| **Xbox 360 XDK** | Install with the **"FULL"** preset. The build reads `%XEDK%`, which the installer sets at machine scope. |
| **Visual Studio 2010** | Not for editing — the Xbox 360 platform toolset installs into the VS2010-era MSBuild tree and needs it present. |
| **Visual Studio 2019** | Optional, only if you want to open the solution in an IDE. The build script does not need it. |
| **`xextool.exe`** | Ships with XeXGUI, Velocity, and most 360 homebrew toolkits. Required — see below. |
| **MSBuild v4.0** | `C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe`, part of .NET Framework 4. Already present on any normal Windows install. |

**VS2019/VS2022's MSBuild will not work.** The Xbox 360 platform toolset lives under
`C:\Program Files (x86)\MSBuild\Microsoft.Cpp\v4.0\Platforms\Xbox 360`, and modern MSBuild
cannot consume a v4.0-style platform directory. This is not a preference — the v4.0
MSBuild is the only one that builds this project.

## Build

```powershell
powershell -ExecutionPolicy Bypass -File tools\build.ps1
```

Output: `bin\riffmaster.xex`, with its size and MD5 printed.

Options:

```powershell
tools\build.ps1 -Clean              # full rebuild
tools\build.ps1 -Out C:\some\path\riffmaster.xex
```

If `xextool.exe` is not found automatically, put it in `tools\` or point `XEXTOOL` at it:

```powershell
$env:XEXTOOL = "C:\path\to\xextool.exe"
```

### Building in the IDE instead

Open `src\riffmaster.sln` in **Visual Studio 2019**, select **`Release Retail` | `Xbox
360`**, and build.

**You must still run the xextool step by hand afterwards**, or the plugin will not load:

```
xextool.exe -r a -m r "src\riffmaster\Release Retail\riffmaster.xex"
```

## Why the xextool step is not optional

Raw XDK output is marked **Devkit** with **Allowed Media: System Flash**. A retail RGH
console silently refuses to load it from `Hdd:\` — no error, no log line, the plugin just
never appears. `xextool -r a -m r` flips it to retail and clears the media restriction.

`tools\build.ps1` runs it and then *verifies* the result, refusing to produce output unless
xextool reports both `Retail` and `All Media Types`. That check exists because the failure
it prevents is invisible on the console.

The `.vcxproj` does contain a post-build event that would do this, but it ships disabled
(`PostBuildEventUseInBuild=false`) and points at a path that does not exist.

## Build-time options

Both are ordinary preprocessor defines. Add them via
`/p:PreprocessorDefinitions` or by editing `src/riffmaster/riffmaster_build.h`, which is
the header the build script generates and the project includes.

### `RIFFMASTER_SUBTYPE`

Which XInput subtype the virtual guitar reports. Defaults to
`XINPUT_DEVSUBTYPE_GUITAR` (`0x06`), which works in both Rock Band 3 and Guitar Hero:
World Tour. Set to `0x07` (`XINPUT_DEVSUBTYPE_GUITAR_ALTERNATE`) if an older Guitar Hero
title refuses to see the guitar. See the README.

### `RIFFMASTER_VERBOSE`

Per-packet logging: GIP chunks, input reports, capability queries.

**Do not enable this for normal use.** `DbgPrint` on a hot path saturates the xbdm debug
channel and can hang the console outright — the capability hooks alone are called roughly
8 times per 100 ms. It exists for protocol debugging, nothing else.

### `RIFFMASTER_LEVEL` and the diagnostic variants

`riffmaster_build.h` carries a `RIFFMASTER_LEVEL` define, and `main.cpp` contains a number
of `#ifdef` variants with names like `RIFFMASTER_NO_CLAIM`, `RIFFMASTER_PASSIVE_REMOVE`
and `RIFFMASTER_CLAIM_ONLY`.

These are **diagnostic scaffolding from the investigation that found the disconnect
freeze**, not user options. Level 7 with no variant is the real plugin; the lower levels
progressively disable subsystems and the variants each cripple something on purpose. They
are kept in-tree because they document how the bug was localised and because the same
ladder is the fastest way to bisect the next one.

Leave `RIFFMASTER_LEVEL` at 7 and define no variant unless you are debugging.

## Changing the base address

`src/riffmaster/xex.xml`:

```xml
<baseaddr addr="0x81F00000"/>
```

If another plugin already occupies `0x81F00000`, the collision does not produce an error —
the plugin silently does nothing, or the console hangs. Change it here and rebuild.

## Why not libxenon, or a cross-compiler

libxenon / devkitXenon target bare-metal XeLL. They cannot produce a DashLaunch plugin:
the plugin is a `.xex` that is loaded into a running kernel's address space, links against
`xkelib` for kernel imports, and depends on XDK-specific XEX metadata (base address,
system-DLL flag, media types). None of that has an open-source equivalent. The XDK is
genuinely required.

## Repository layout

```
riffmaster-rgh360/
  bin/riffmaster.xex        prebuilt plugin
  src/riffmaster.sln        Visual Studio solution
  src/riffmaster/
    main.cpp                claim, GIP handling, XAM registration, 360 translation
    gip_riffmaster.h        GIP input report decode + 360 guitar mapping
    gip_auth.h              RSA-2048 bignum modexp and the auth handshake
    Detours.h/.cpp          iMoD1998's PowerPC branch detours (V3.1)
    hid_parser.*            upstream HID report descriptor parser (unused by us)
    mapping.*, rapidjson/   upstream JSON mapping system (unused by us)
    usb.h                   USB descriptor structs
    xkelib/                 kernel import library
    xex.xml                 XEX metadata, including the base address
  tools/build.ps1           build + post-process + verify
  docs/                     protocol spec, install, known issues, design notes
```

`hid_parser`, `mapping` and `rapidjson` are inherited from upstream and are not used by
the RiffMaster path. They are still compiled in so that a merge from upstream stays
straightforward; stripping them is a size optimisation nobody has needed yet.

## A note on the code

Two hazards are worth knowing before you change anything, both of which have already
caused real bugs here:

- **The Xbox 360 is 64-bit big-endian PowerPC.** Every multi-byte value from the USB
  stream is little-endian and must be byteswapped.
- **MSVC allocates bitfields MSB-first on PowerPC and LSB-first on x86.** A bitfield struct
  copied from an x86 reference will compile cleanly and decode *wrong*, silently. GIP
  report parsing here uses explicit masks and shifts for exactly this reason. Keep it that
  way.
