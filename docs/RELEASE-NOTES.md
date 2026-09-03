# 1.04 stable

Download **`riffmaster.xex`** from [Releases](https://github.com/Easy301/riffmaster-rgh360-fixed/releases/latest). Copy to `Hdd:\riffmaster.xex`, hard reboot.

| | Detail |
|---|---|
| Version | 1.04 stable |
| File | `riffmaster.xex` |
| MD5 | `8994AF9F905F823F716A9E460D5971DB` |
| Size | 96,256 bytes |

---

## What changed in 1.04

This is the current stable build. It includes everything needed for RiffMaster on RGH/JTAG
360, plus fixes discovered after the first patched release:

1. **RiffMaster authentication** — GIP auth no longer aborts when your guitar’s certificate
   is valid but differs from the one used in the original author’s testing.
2. **Other guitars with riffmaster loaded** — Wired HID guitars (Revival Kit, Santroller,
   and similar) no longer get stolen by riffmaster’s HID hook. UsbdSecPatch can own them
   while the RiffMaster dongle stays active. CRKD-type XInput guitars worked earlier
   because they never hit that HID path; wired HID units needed an extra pass-through fix.
3. **FTP + hot-plug** — Fewer freezes when you plug a third-party guitar while a PC FTP
   client is connected to the console.

The RiffMaster GIP/dongle path is unchanged from the first working patch — 1.04 is the
build that also gets coexistence and FTP behavior right.

---

## Install

1. Copy **`riffmaster.xex`** to **`Hdd:\riffmaster.xex`** (overwrite any older copy)
2. **Hard reboot** (full power off)
3. Boot to the dashboard, **then** plug guitars

Full walkthrough: [INSTALL-FIXED.md](INSTALL-FIXED.md)

---

## Rebuild from source xex

```text
python tools/apply_full_patch.py
python tools/apply_notify_beta_patch.py
python tools/apply_coexist_hid_install.py
python tools/apply_hid_passthrough.py
```

Requires `tools/xextool.exe` and the original unpatched xex. See [bin/README.md](../bin/README.md).
