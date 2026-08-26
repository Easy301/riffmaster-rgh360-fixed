# v1.0.2-beta — FTP / third-party guitar freeze fix (beta)

**Pre-release.** RiffMaster still shows up in the dashboard on early testing. We want more
CRKD + FTP hammering before this replaces v1.0.0 as the default download.

Download **`riffmaster-beta.xex`**, copy to `Hdd:\riffmaster.xex`, hard reboot, then test.

| | v1.0.0-fixed (stable) | v1.0.2-beta (this release) |
|---|---|---|
| File | `riffmaster.xex` | `riffmaster-beta.xex` |
| MD5 | `F5BA2366FD6D1630375DF5F3AD91A4E0` | `D042E7830893347D539D4C7A47DB01A0` |
| RiffMaster | Verified daily driver | Early beta — works in dashboard so far |
| FTP + CRKD plug | May freeze console | Targets that freeze |

---

## What this tries to fix

Some consoles freeze when you plug in a third-party guitar (CRKD over UsbdSecPatch, etc.)
while a **PC FTP client** is connected to the Xbox. Aurora's FTP server can stay running —
it's the active client on your PC that matters, not turning FTP off in Aurora.

v1.0.1 broke the RiffMaster because it killed **all** the leftover notify patches. This
beta only removes the two mapping-assistant ones (custom type 80 and the 1500 ms timer).
The **JRPC2 patch stays** — that's what v1.0.0 needs for the RiffMaster to show up.

---

## Still on v1.0.0? Do this until the stable fix ships

You do **not** need to disable FTP in Aurora.

**Simple rule:** get your third-party guitars connected and working in the dashboard
**before** you open any FTP client on your PC.

If you need to plug a guitar in later, close FileZilla (or whatever you use) first, plug
the guitar in, wait until it's up, then reconnect FTP.

That order has been fine on the test console. Plugging a guitar **while** FTP is already
connected is the case that tends to freeze.

---

## Install (beta)

1. Download **`riffmaster-beta.xex`** from this release
2. Copy to **`Hdd:\riffmaster.xex`** (replace your current file)
3. **Hard reboot** (full power off)
4. Confirm RiffMaster still works in the dashboard
5. With FTP connected on your PC, plug a third-party guitar and see if the console stays up

If the RiffMaster vanishes or stops working, roll back to **v1.0.0-fixed**
(`riffmaster.xex`, MD5 `F5BA2366FD6D1630375DF5F3AD91A4E0`).

---

## Rebuild

```text
python tools/apply_notify_beta_patch.py
```

Requires `tools/xextool.exe` and an intact `bin/riffmaster.xex` (v1.0.0-fixed).
