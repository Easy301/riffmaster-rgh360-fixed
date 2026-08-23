# Changelog

All notable changes in this fork relative to upstream
[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360).

## [1.0.0-fixed] — 2026-08-22

**Verified on hardware:** PDP RiffMaster + CRKD guitar (UsbdSecPatch) on the same
RGH console with riffmaster left in DashLaunch.

### Fixed

1. **RSA self-test aborts auth on some RiffMaster units**  
   Guitars with a valid but different device certificate failed the hardcoded
   known-answer check and never completed the GIP handshake. Auth now continues
   unless crypto actually fails.

2. **CRKD / UsbdSecPatch guitars hijacked by HID mapping**  
   Inherited hiddriver360 HID hooks claimed the CRKD as an unknown USB pad and
   showed *"Unknown controller connected. Starting mapping process..."* on the
   dashboard. GIP-only mode disables HID detours and the mapping assistant thread
   by default.

3. **CRKD connects but buttons do nothing**  
   After fix (2), `XInputdReadStateHook` still intercepted native USB guitar
   contexts (`>= 0x10000005`) and returned an error instead of calling the
   original. Non-GIP devices now pass through. The RiffMaster GIP path is
   unchanged.

### Added

- Source defaults: `RIFFMASTER_GIP_ONLY` for level-7 builds
- `tools/apply_full_patch.py` — recreate the prebuilt xex from upstream stock
  without the Xbox 360 XDK
- This changelog and expanded install notes for end users

### Unchanged

- RiffMaster GIP dongle claim (VID `0E6F` / PID `0248`)
- XAM guitar registration and game compatibility table
- GPL-3.0 licence (inherited from upstream)
