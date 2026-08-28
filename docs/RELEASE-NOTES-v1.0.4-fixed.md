# v1.0.4-fixed — other USB guitars work with riffmaster loaded

Download **`riffmaster.xex`** from this release. Copy to `Hdd:\riffmaster.xex`, hard reboot.

| | Detail |
|---|---|
| File | `riffmaster.xex` |
| MD5 | `8994AF9F905F823F716A9E460D5971DB` |
| Size | 96,256 bytes |

---

## What this is

1.0.0 made the RiffMaster itself work, and it looked like other guitars would too — CRKD
did. Wired HID guitars did not. That took a few iterations to pin down, because CRKD is
XInput and never walked into riffmaster’s HID claim. Revival Kit / Santroller still got
grabbed, went dead, and could freeze the box on plug.

This build hands those HID devices back to the original driver. UsbdSecPatch can own them.
The RiffMaster dongle path is the same as 1.0.0.

Use **1.0.4**. The in-between version numbers (1.0.1–1.0.3) were the work that got us here.

---

## Install

1. Copy **`riffmaster.xex`** to **`Hdd:\riffmaster.xex`** (overwrite the old one)
2. **Hard reboot** (full power off)
3. Boot to the dashboard, **then** plug guitars

---

## Roll back

[v1.0.0-fixed](https://github.com/Easy301/riffmaster-rgh360-fixed/releases/tag/v1.0.0-fixed)
— MD5 `F5BA2366FD6D1630375DF5F3AD91A4E0`. If you use that build, connect third-party
guitars before you open FTP on your PC.

---

## Rebuild

```text
python tools/apply_full_patch.py
```

Requires `tools/xextool.exe` and the original unpatched xex. See [bin/README.md](../bin/README.md).
