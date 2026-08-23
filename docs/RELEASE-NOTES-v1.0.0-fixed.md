## RiffMaster Xbox 360 — Patched Release (v1.0.0-fixed)

**[Download `riffmaster.xex`](#)** · Copy to `Hdd:\riffmaster.xex` · Enable in DashLaunch · Hard reboot

---

### About

Patched community release based on **[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360)**.
Credit for the underlying driver belongs to **Durg5** and **EinTim23** — see [CREDITS.md](https://github.com/Easy301/riffmaster-rgh360-fixed/blob/main/CREDITS.md).

**Most people need this build for the RiffMaster alone** — on the original release, the
guitar often failed to work when connected to the 360. This fixes that.

If you also use **UsbdSecPatch** for other third-party guitars (e.g. CRKD), this build
lets those stay usable while riffmaster stays loaded.

---

### Install

1. Download **`riffmaster.xex`** from this page (~94 KB)
2. Copy to `Hdd:\riffmaster.xex` on your Xbox HDD
3. **DashLaunch → Plugins** → select the file → save `launch.ini`  
   *or* add `pluginN = Hdd:\riffmaster.xex` to `launch.ini`
4. **Hard reboot**
5. Plug in the dongle, turn the guitar on, wait a few seconds

📖 Full guide: [docs/INSTALL-FIXED.md](https://github.com/Easy301/riffmaster-rgh360-fixed/blob/main/docs/INSTALL-FIXED.md)

---

### Verified on

- RGH Xbox 360, kernel 17559, Aurora 0.7b2
- PDP RiffMaster (primary fix)
- Also tested with a CRKD guitar via UsbdSecPatch on the same console

---

### File details

| | |
|---|---|
| **MD5** | `F5BA2366FD6D1630375DF5F3AD91A4E0` |
| **Size** | 96,256 bytes (~94 KB) |

Use this ~94 KB file. The original unpatched release is ~324 KB.

---

### Licence

GPL-3.0 — [LICENSE](https://github.com/Easy301/riffmaster-rgh360-fixed/blob/main/LICENSE)
