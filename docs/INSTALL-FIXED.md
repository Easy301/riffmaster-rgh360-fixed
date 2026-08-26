# Installation Guide

This guide is for the **patched** `riffmaster.xex` from
**[Releases](https://github.com/Easy301/riffmaster-rgh360-fixed/releases)**.

---

## Before you start

| Requirement | Detail |
|---|---|
| Console | RGH or JTAG Xbox 360 |
| Software | DashLaunch with plugin support |
| Kernel | **17559** (retail) or **17489** (devkit) |
| Hardware | PDP RiffMaster guitar + USB dongle |
| Boot | Disc tray closed when you power on |

Back up your `launch.ini` before making changes.

---

## 1. Download the correct file

From **[Releases](https://github.com/Easy301/riffmaster-rgh360-fixed/releases)**,
download **`riffmaster.xex`**.

| File size | What it is |
|---|---|
| **~94 KB** | Patched build from this repo — **use this** |
| **~324 KB** | Original unpatched release — missing fixes most users need |

---

## 2. Copy to your Xbox

Place the file so the console sees it at:

```
Hdd:\riffmaster.xex
```

Common methods: FTP (Aurora/FSD), Xbox 360 Neighborhood, FATXplorer, or USB transfer.

After copying, confirm the file size on the console side matches (~94 KB). A partial
copy often looks like "the plugin does nothing."

---

## 3. Enable the plugin

### Option A — DashLaunch (recommended)

1. Boot to your dashboard
2. Open **DashLaunch**
3. Go to **Plugins**
4. Select an empty slot and set the path to `Hdd:\riffmaster.xex`
5. **Save** `launch.ini` to the HDD

### Option B — Edit `launch.ini`

Add one line under `[Plugins]` in any free slot:

```ini
[Plugins]
plugin1 = Hdd:\UsbdSecPatch.xex
plugin2 = Hdd:\riffmaster.xex
```

Adjust slot numbers and paths to match your setup. Keep plugins you still need.

> If you edit from inside DashLaunch, you must save explicitly. Unsaved changes are lost.

---

## 4. Hard reboot

Power the console fully off, then back on. A soft reboot may not reload a changed plugin.

---

## 5. Connect the guitar

1. Plug in the **RiffMaster dongle**
2. Turn the **guitar** on
3. Wait a few seconds for authentication
4. Test the strum bar on the dashboard

---

## Using a second guitar (UsbdSecPatch)

If you also play on other third-party guitars that require **UsbdSecPatch** on a modded
360 (for example CRKD-type guitars), leave UsbdSecPatch enabled alongside riffmaster:

```ini
plugin1 = Hdd:\UsbdSecPatch.xex
plugin2 = Hdd:\riffmaster.xex
```

This patched build is designed for that setup — second guitars stay responsive while
riffmaster remains loaded.

---

## Troubleshooting

| Problem | Likely cause |
|---|---|
| Plugin does nothing | `launch.ini` not saved, wrong file path, or tray was open at boot |
| Wrong kernel | Plugin only loads on kernel 17559 or 17489 |
| Guitar does not work on the 360 | Downloaded the original ~324 KB file instead of this ~94 KB patched build |
| Second guitar unresponsive while riffmaster is loaded | Use the patched release from this repo (~94 KB) |
| Console freezes when plugging CRKD (or similar) | Use **v1.0.2-fixed** from [Releases](https://github.com/Easy301/riffmaster-rgh360-fixed/releases/latest). On v1.0.0 rollback: connect guitars before FTP on your PC |

### FTP and third-party guitars

**v1.0.2-fixed** targets freezes when you plug a third-party guitar while a PC FTP client
is connected. Aurora FTP can stay on.

If you roll back to **v1.0.0-fixed**, connect guitars before you open FTP on your PC. Close
the FTP program before hot-plugging.

For advanced troubleshooting (base address conflicts, debug logging, etc.), see
[INSTALL.md](INSTALL.md) from the original project.

---

## What this build fixes

*Technical summary — skip if you only need the install steps above.*

### RiffMaster authentication

On the original release, the guitar often failed to work when connected to the 360 — the
dongle may look paired, but the console never receives input. This build corrects that.

### Coexistence with UsbdSecPatch

The original release can intercept unknown USB controllers for its own HID mapping layer.
Second guitars that rely on UsbdSecPatch (e.g. CRKD) became unresponsive and unusable
unless riffmaster was unloaded. This build limits riffmaster to the RiffMaster GIP path
so both plugins can run together.

Source changes and patch offsets: [CHANGELOG.md](../CHANGELOG.md)
