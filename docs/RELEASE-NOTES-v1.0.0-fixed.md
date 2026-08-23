## RiffMaster Xbox 360 — patched build (1.0.0-fixed)

**Download `riffmaster.xex` below and copy it to `Hdd:\riffmaster.xex` on your console.**

### What this fixes

1. **RSA self-test** — some RiffMaster units fail auth with `RSA SELFTEST: FAIL`
2. **CRKD / UsbdSecPatch mapping popup** — "Unknown controller connected..."
3. **CRKD no dashboard input** — guitar connects but buttons do nothing

### Verified on

- RGH Xbox 360, kernel 17559, Aurora 0.7b2
- PDP RiffMaster (VID `0E6F` / PID `0248`) + CRKD via UsbdSecPatch
- Both plugins in DashLaunch at once

### Install

1. Download **`riffmaster.xex`** from this release
2. Copy to `Hdd:\riffmaster.xex`
3. Add to `launch.ini`:
   ```ini
   plugin3 = Hdd:\riffmaster.xex
   ```
4. **Hard reboot** (full power off)
5. Plug dongle, turn guitar on, wait ~10 seconds

Full guide: [docs/INSTALL-FIXED.md](https://github.com/Easy301/riffmaster-rgh360-fixed/blob/main/docs/INSTALL-FIXED.md)

### File checksum

| | |
|---|---|
| **MD5** | `F5BA2366FD6D1630375DF5F3AD91A4E0` |
| **Size** | 96,256 bytes |

**Important:** patched xex is ~94 KB. Stock upstream is ~324 KB — do not install the wrong file.

### Credits

Based on **[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360)** and **[EinTim23/hiddriver360](https://github.com/EinTim23/hiddriver360)**. See [CREDITS.md](https://github.com/Easy301/riffmaster-rgh360-fixed/blob/main/CREDITS.md).

### Licence

GPL-3.0 — see [LICENSE](https://github.com/Easy301/riffmaster-rgh360-fixed/blob/main/LICENSE).
