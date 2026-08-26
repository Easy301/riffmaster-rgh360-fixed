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

Install guide: [docs/INSTALL-FIXED.md](docs/INSTALL-FIXED.md)

---

## [1.0.2-beta] — 2026-08-25

**Pre-release.** Targets console freezes when a third-party guitar (e.g. CRKD) is plugged
in while a **PC FTP client** is connected to Aurora. Early testing: RiffMaster still works
in the dashboard. More stress testing wanted before this replaces v1.0.0.

- NOPs only the mapping-assistant notify stores (type 80 + 1500 ms timer)
- **Keeps** the JRPC2 notify patch (v1.0.1 broke the RiffMaster by removing all three)
- File: `riffmaster-beta.xex` · MD5 `D042E7830893347D539D4C7A47DB01A0`

**Stay on v1.0.0?** You do not need to turn off Aurora FTP. Disconnect your **PC FTP
client** before plugging a third-party guitar. Get third-party guitars connected in the
dashboard **before** you open any FTP client on your PC — that order usually avoids the
freeze until we ship a stable fix. See [release notes](docs/RELEASE-NOTES-v1.0.2-beta.md).

---

## [1.0.1-fixed] — yanked 2026-08-25

**Do not use this build.** Turning off leftover notify patches made the RiffMaster stop
working. Use **v1.0.0-fixed** (`bin/riffmaster.xex`, MD5 `F5BA2366FD6D1630375DF5F3AD91A4E0`).

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
