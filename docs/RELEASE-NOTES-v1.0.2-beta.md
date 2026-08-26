# v1.0.2-beta — FTP / third-party guitar freeze fix (beta)

**Pre-release.** Dashboard responsiveness looks good on early testing. More CRKD + FTP
stress testing is still wanted before this replaces v1.0.0 as the default download.

Download **`riffmaster-beta.xex`** from this release. Copy to `Hdd:\riffmaster.xex`, hard
reboot, then test.

| | v1.0.0-fixed (stable) | v1.0.2-beta (this release) |
|---|---|---|
| File | `riffmaster.xex` | `riffmaster-beta.xex` |
| MD5 | `F5BA2366FD6D1630375DF5F3AD91A4E0` | `D042E7830893347D539D4C7A47DB01A0` |
| RiffMaster | Verified daily driver | Early beta — RiffMaster works in dashboard so far |
| FTP + CRKD plug | May freeze console | Targets that freeze |

---

## What this tries to fix

Some setups freeze when a **third-party guitar** (e.g. CRKD over UsbdSecPatch) is plugged
in while an **FTP client on your PC is connected** to the Xbox (Aurora's FTP server can
stay on — it is the **active client session** that matters).

v1.0.1 yanked that fix because it turned off **all** leftover XAM notify patches and the
RiffMaster stopped working. This beta only removes the two **mapping-assistant** notify
writes (custom type 80 and the 1500 ms timer). The **JRPC2 USB-notify patch stays**, which
is what v1.0.0 needs for the RiffMaster to show up.

---

## If you stay on v1.0.0-fixed (recommended until beta is confirmed)

You do **not** need to disable FTP in Aurora. Leave Aurora's FTP server running if you want.

**Do this instead:** close or disconnect your **PC FTP program** (FileZilla, WinSCP, Aurora
file manager on PC, etc.) **before** you plug in a third-party guitar. Reconnect FTP after
the guitar is up if you need it.

That workaround avoids the freeze path most of the time. It does not help if you hot-plug
the guitar while a client is already connected.

**Guitar already plugged in first?** Usually safer. If the RiffMaster (or CRKD) is already
working in the dashboard and *then* you open an FTP client, you are much less likely to
hit the freeze than plugging a guitar mid-session. We have not stress-tested every order
yet — report back if FTP-after-guitar still freezes on v1.0.0.

---

## Install (beta)

1. Download **`riffmaster-beta.xex`** from this release
2. Copy to **`Hdd:\riffmaster.xex`** (replace your current file)
3. **Hard reboot** (full power off)
4. Confirm RiffMaster still works in the dashboard
5. With an FTP client connected, plug a third-party guitar and see if the console stays up

If the RiffMaster breaks or the dashboard guitar vanishes, roll back to **v1.0.0-fixed**
(`riffmaster.xex`, MD5 `F5BA2366FD6D1630375DF5F3AD91A4E0`).

---

## Rebuild

```text
python tools/apply_notify_beta_patch.py
```

Requires `tools/xextool.exe` and an intact `bin/riffmaster.xex` (v1.0.0-fixed).
