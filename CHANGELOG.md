# Changelog

Changes in this release relative to the original
[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360) patch.

---

## Summary

Download the patched xex from **[Releases](https://github.com/Easy301/riffmaster-rgh360-fixed/releases)**.

| # | Fix | User impact |
|---|---|---|
| 1 | RSA self-test | RiffMaster works on consoles that meet the original requirements |
| 2 | HID pass-through | UsbdSecPatch guitars stay usable alongside riffmaster |
| 3 | Notify patch | Fewer freezes when plugging a third-party guitar while a PC FTP client is connected |

Install guide: [docs/INSTALL-FIXED.md](docs/INSTALL-FIXED.md)

---

## [1.0.4-fixed] — 2026-08-27

**Current stable.** MD5 `8994AF9F905F823F716A9E460D5971DB`

Getting other USB guitars to work with riffmaster still loaded took a few iterations.
CRKD looked fine early because it enumerates as XInput, so it never walked into the HID
claim. Wired HID guitars (Revival Kit, Santroller, and similar) still got stolen, went
dead, and could freeze the console on plug.

1.0.4 is the build that actually stops that. The HID hook hands those devices back to the
original driver so UsbdSecPatch can own them. The RiffMaster GIP path is unchanged.

Version numbers 1.0.1–1.0.3 were the in-between builds. Use this one.

---

## [1.0.0-fixed] — 2026-08-22

**Tested on:** RGH Xbox 360, kernel 17559, Aurora 0.7b2 — PDP RiffMaster + CRKD guitar
(UsbdSecPatch), both plugins in DashLaunch.

- MD5 `F5BA2366FD6D1630375DF5F3AD91A4E0`

### Fixed

1. **RSA self-test aborts auth on some RiffMaster units**  
   Guitars with a valid but different device certificate failed a hardcoded known-answer
   check and never completed the GIP handshake. Auth now continues unless cryptography
   actually fails.

2. **UsbdSecPatch devices hijacked by HID mapping**  
   Inherited hiddriver360 HID hooks claimed third-party guitars as unknown USB pads and
   showed *"Unknown controller connected. Starting mapping process..."* on the dashboard.

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
