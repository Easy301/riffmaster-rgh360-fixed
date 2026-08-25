# Changelog

Changes in this release relative to the original
[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360) patch.

---

## Summary

Download the patched xex from **[Releases](https://github.com/Easy301/riffmaster-rgh360-fixed/releases)**.

| # | Fix | User impact |
|---|---|---|
| 1 | RSA self-test | RiffMaster works on consoles that meet the original requirements |
| 2 | GIP-only mode + ReadState pass-through | UsbdSecPatch guitars (e.g. CRKD) stay usable alongside riffmaster |
| 3 | Turn off leftover notify patches | Console should not freeze when you plug a guitar in |

Install guide: [docs/INSTALL-FIXED.md](docs/INSTALL-FIXED.md)

---

## [1.0.1-fixed] — 2026-08-25

Sometimes the dash froze when you plugged in a guitar (CRKD or RiffMaster), especially
right after copying a file over FTP. The plugin was still patching Xbox notification
code left over from the old “unknown controller mapping” popup, which this build does
not use.

That leftover patch is off now. RiffMaster and CRKD still work the same way — you do
not need to close FTP first.

Prebuilt `bin/riffmaster.xex` MD5 `0620F5564CA2D7E1B7F03E9FDDB66160`.

---

## [1.0.0-fixed] — 2026-08-22

**Tested on:** RGH Xbox 360, kernel 17559, Aurora 0.7b2 — PDP RiffMaster + CRKD guitar
(UsbdSecPatch), both plugins in DashLaunch.

### Fixed

1. **RSA self-test aborts auth on some RiffMaster units**  
   Guitars with a valid but different device certificate failed a hardcoded known-answer
   check and never completed the GIP handshake. Auth now continues unless cryptography
   actually fails.

2. **UsbdSecPatch devices hijacked by HID mapping**  
   Inherited hiddriver360 HID hooks claimed third-party guitars (e.g. CRKD) as unknown USB
   pads and showed *"Unknown controller connected. Starting mapping process..."* on the
   dashboard. GIP-only mode disables those detours and the mapping assistant thread.

3. **UsbdSecPatch guitars connect but buttons do nothing**  
   `XInputdReadStateHook` intercepted native USB guitar contexts (`>= 0x10000005`) and
   returned an error instead of calling through. Non-GIP devices now pass through. The
   RiffMaster GIP path is unchanged.

### Added

- `RIFFMASTER_GIP_ONLY` default for level-7 builds
- `tools/apply_full_patch.py` — rebuild the patched xex without the Xbox 360 XDK
- Installation guide and documentation for end users

### Unchanged

- RiffMaster dongle claim (VID `0E6F` / PID `0248`)
- XAM guitar registration and game compatibility table from the original project
- GPL-3.0 licence
