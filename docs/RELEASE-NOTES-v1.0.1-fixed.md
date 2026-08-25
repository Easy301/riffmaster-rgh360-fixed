## RiffMaster Xbox 360 — v1.0.1-fixed

**[Download `riffmaster.xex`](#)** · Copy to `Hdd:\riffmaster.xex` · Enable in DashLaunch · Hard reboot

This is the same patched driver as v1.0.0-fixed, plus a freeze fix.

---

### What changed

The dash would sometimes lock up the moment you plugged in a guitar — CRKD or RiffMaster.
It happened a lot right after copying a file over FTP, but FTP itself is not the bug.
The plugin was still patching Xbox notification code that only existed for the old
mapping-assistant popup. This build never uses that popup, so that patch is off now.

RiffMaster auth, CRKD / UsbdSecPatch coexistence, and everything else from v1.0.0-fixed
are unchanged.

---

### Install

1. Download **`riffmaster.xex`** from this page (~94 KB)
2. Copy to `Hdd:\riffmaster.xex` on your Xbox HDD (replace the old one)
3. **Hard reboot** (full power off — a soft reboot can keep the old plugin in memory)
4. Plug in the dongle, turn the guitar on, wait a few seconds

Same steps as before: [docs/INSTALL-FIXED.md](https://github.com/Easy301/riffmaster-rgh360-fixed/blob/main/docs/INSTALL-FIXED.md)

---

### File details

| | |
|---|---|
| **MD5** | `0620F5564CA2D7E1B7F03E9FDDB66160` |
| **Size** | 96,256 bytes (~94 KB) |

Use this ~94 KB file. The original unpatched release is ~324 KB.

---

### Credits

Based on **[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360)**.
See [CREDITS.md](https://github.com/Easy301/riffmaster-rgh360-fixed/blob/main/CREDITS.md).

GPL-3.0
