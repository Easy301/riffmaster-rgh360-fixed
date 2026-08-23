# Install (patched build)

## Easiest: GitHub Release

1. Open **[Releases](https://github.com/PLACEHOLDER/riffmaster-rgh360-fixed/releases)** on this repo.
2. Download **`riffmaster.xex`** from the latest release.
3. Copy it to your Xbox 360 as:
   ```
   Hdd:\riffmaster.xex
   ```
4. Add to `launch.ini` (example):
   ```ini
   [Plugins]
   plugin1 = Hdd:\UsbdSecPatch.xex
   plugin2 = Hdd:\Debug\Xbdm.xex
   plugin3 = Hdd:\riffmaster.xex
   ```
5. **Hard reboot** (full power off).
6. Plug the **RiffMaster dongle**, turn the **guitar** on, wait ~10 seconds.

**UsbdSecPatch** can stay enabled. This build lets RiffMaster and CRKD-style guitars
work together without the mapping popup.

## From `bin/` in this repo

Same file: `bin/riffmaster.xex` (~94 KB, retail encrypted).

## Requirements

Same as upstream — see [INSTALL.md](INSTALL.md):

- RGH/JTAG 360, kernel **17559** (retail) or **17489** (devkit)
- DashLaunch with plugins enabled
- PDP RiffMaster dongle (VID `0E6F`, PID `0248`)
- Disc tray closed at boot

## What this build fixes

See [CHANGELOG.md](../CHANGELOG.md).

## Troubleshooting

| Symptom | Check |
|---|---|
| Mapping popup on CRKD | Wrong xex — use Release `riffmaster.xex` (~94 KB), not stock upstream (~324 KB) |
| RiffMaster no auth | Old unpatched xex; look for `RSA SELFTEST: FAIL` with no `AUTH HANDSHAKE COMPLETE` in xbdm log |
| CRKD dead in dash | Same — need ReadState pass-through fix (this release) |
| Nothing loads | Tray open at boot, wrong kernel, or plugin path in `launch.ini` |
