# v1.0.3-fixed — UsbdSecPatch guitars no longer stolen by HID hooks

Download **`riffmaster.xex`** from this release. Copy to `Hdd:\riffmaster.xex`, hard reboot.

| | Detail |
|---|---|
| File | `riffmaster.xex` |
| MD5 | `F78D30F691ED3CDCDDB7197E3C94E32C` |
| Size | 96,256 bytes |

Includes everything from **v1.0.2-fixed**, plus the real HID-detour disable.

---

## What was wrong

v1.0.2 was *supposed* to stop riffmaster from grabbing other USB guitars. That was hard to catch because **CRKD still worked**. CRKD enumerates as a 360 **XInput** device, so it never walked into riffmaster’s HID claim. Wired Santroller / Retro Cult Revival Kit guitars do expose a **HID** interface. Riffmaster still installed its HID add/remove hooks, claimed those guitars (`Assigning controller…`), and left them dead — often with **no** “unknown controller” popup, because v1.0.2 had already NOPed the mapping notify.

The GIP-only patch had NOPed the **wrong** `Detour::Install()` calls. HID hooks were still going in on retail.

This build NOPs the actual DllMain sites:

- retail `HidAddDeviceDetour.Install` (`0x800E4D68`)
- retail `HidRemoveDeviceDetour.Install` (`0x800E4D28`)

GIP claim for the RiffMaster dongle is unchanged. XInput ReadState pass-through is unchanged.

---

## What we think this means

With **UsbdSecPatch** still loaded, third-party guitars that depend on it (CRKD, Revival Kit / Santroller in XInput, other UsbdSecPatch instruments) should work **while riffmaster is loaded**. Plug them after the dashboard is up, same as before.

If something still gets stolen, the debug line to look for is `Assigning` / `EINTIM` on plug — that means HID claim is back.

---

## Install

1. Download **`riffmaster.xex`** from this release
2. Copy to **`Hdd:\riffmaster.xex`**
3. **Hard reboot** (full power off)
4. Boot to the dashboard, **then** plug guitars

---

## Roll back

- **v1.0.2-fixed** — MD5 `D042E7830893347D539D4C7A47DB01A0` (FTP notify fix, HID still claims HID gamepads)
- **v1.0.0-fixed** — MD5 `F5BA2366FD6D1630375DF5F3AD91A4E0`

---

## Rebuild

```text
python tools/apply_full_patch.py
python tools/apply_notify_beta_patch.py
python tools/apply_coexist_hid_install.py
```

Last step reads v1.0.2 `bin/riffmaster.xex` and writes the HID Install NOPs. Requires `tools/xextool.exe`.
