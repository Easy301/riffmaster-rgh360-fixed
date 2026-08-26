# v1.0.2-fixed — FTP + third-party guitar freeze fix

Download **`riffmaster.xex`** from this release. Copy to `Hdd:\riffmaster.xex`, hard reboot.

| | Detail |
|---|---|
| File | `riffmaster.xex` |
| MD5 | `D042E7830893347D539D4C7A47DB01A0` |
| Size | 96,256 bytes |

Includes everything from **v1.0.0-fixed** (RSA auth, GIP-only, CRKD pass-through), plus a
partial notify patch that targets console freezes when you plug a third-party guitar while
a PC FTP client is connected.

v1.0.1 was yanked — it turned off **all** notify patches and the RiffMaster stopped working.
This build only removes the two mapping-assistant notify writes (type 80 and the 1500 ms
timer). The **JRPC2 patch stays**.

---

## Install

1. Download **`riffmaster.xex`** from this release
2. Copy to **`Hdd:\riffmaster.xex`**
3. **Hard reboot** (full power off)
4. Plug in your guitars and play

---

## Roll back to v1.0.0

If something breaks, use the previous stable build:

- MD5 `F5BA2366FD6D1630375DF5F3AD91A4E0`
- Tag [v1.0.0-fixed](https://github.com/Easy301/riffmaster-rgh360-fixed/releases/tag/v1.0.0-fixed)

On v1.0.0, if FTP freezes are still a problem: connect third-party guitars **before** you
open any FTP client on your PC. Aurora FTP can stay on.

---

## Rebuild

```text
python tools/apply_full_patch.py
python tools/apply_notify_beta_patch.py
```

Second step reads `bin/riffmaster.xex` from step one and writes the v1.0.2 notify NOPs.
Requires `tools/xextool.exe` and an upstream xex in `bin/riffmaster-original.xex`.
