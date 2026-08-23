# Installing

Applies to both the prebuilt `bin/riffmaster.xex` and one you built yourself.

## Before you start

- **Your console must be on kernel 17559 (retail) or 17489 (devkit).** The plugin checks
  this at load and aborts on anything else — deliberately, because every raw kernel
  address it patches is build-specific. Applying them to a different build would patch
  whatever happens to live at those addresses, which is how you brick a boot.
- **Back up your `launch.ini`.** You are about to edit it.
- **Close the disc tray.** The plugin refuses to load with the tray open (an inherited
  upstream check).
- Read [KNOWN_ISSUES.md](KNOWN_ISSUES.md). This is beta software that patches live kernel
  code.

## 1. Copy the plugin to the console

Put `riffmaster.xex` in the root of the console's HDD, so it is reachable as
`Hdd:\riffmaster.xex`.

Any of these work:

- **Xbox 360 Neighborhood** or `xbcp`, if you run `xbdm.xex`
- **FTP** — Aurora's built-in FTP server, or FreeStyle Dash's. Note Aurora's FTP only
  runs while Aurora is running: it disappears the moment a game loads.
- Pull the drive and use FATXplorer

The path the console sees as `Hdd:\` may appear as `Hdd1` over FTP. They are the same
place.

> **Verify the copy.** A truncated or partially-written xex will not load, and the
> failure looks exactly like "the plugin does nothing". Compare file sizes, or MD5 the
> file on both ends if your tool can.

## 2. Add it to `launch.ini`

Find the `[Plugins]` section and add **one** line in a free slot:

```ini
[Plugins]
plugin1 = Hdd:\xbdm.xex
plugin2 = Hdd:\xbNetwork.xex
plugin3 = Hdd:\riffmaster.xex     <-- add this
plugin4 =
plugin5 = Hdd:\XDRPC.xex
```

- **Do not remove, replace, or reorder the plugins already there.**
- Use a slot that is genuinely empty.
- **Only one hiddriver360-derived plugin may be loaded at a time.** Two of them detour the
  same kernel addresses, and the second trampoline points back into the first — the
  console freezes on entering the dashboard. If you already run hiddriver360 itself for a
  DualShock or Switch Pro controller, you cannot run both. There is no workaround short of
  merging them.

If you edit `launch.ini` from within DashLaunch, **save it explicitly** — "Save \ Load
launch.ini" → save to HDD. DashLaunch silently discards unsaved edits, which costs
everyone one confused test cycle exactly once.

## 3. Hard reboot

Power the console fully off and back on. A soft reboot does **not** reliably reload a
plugin that has changed on disk — you will test the old binary and draw the wrong
conclusion. This matters a lot when iterating.

## 4. Connect the guitar

1. Plug the **dongle** into any USB port.
2. Turn the **guitar** on.
3. Wait a few seconds. The RSA handshake takes about a second, and the device needs
   ~680 ms of that just to decrypt the premaster.

The guitar should then drive the dashboard.

## Verifying it loaded

With `xbdm.xex` running and **xbWatson** attached you should see, once the guitar is on:

```
RIFFMASTER: UsbdOpenDefaultEndpoint -> 0x00000000 OK
RIFFMASTER: interrupt OUT EP 02 -> 0x00000000 OK
RIFFMASTER: *** interrupt IN endpoint OPEN - starting GIP reads ***
RIFFMASTER: SET_CONFIGURATION completed status=0x00000000
RIFFMASTER: *** RSA SELFTEST: PASS ***
RIFFMASTER: *** registered virtual GUITAR in XAM, user index N ***
RIFFMASTER: *** AUTH HANDSHAKE COMPLETE ***
```

That last pair is the success condition.

Two things that will otherwise waste your time:

- **The plugin's load banner prints during boot, before xbWatson can attach.** Seeing
  nothing at connect time means nothing. Turn the guitar on *after* attaching.
- **xbWatson prints newest-first.** Read its output bottom-to-top.

To confirm the plugin is resident without any logging at all, ask the debug monitor
directly — connect to TCP port 730 and send `modules`. `riffmaster.xex` should appear with
base `0x81f00000`.

## Troubleshooting

**Nothing happens at all, no `RIFFMASTER:` lines**
- Plugin not actually loaded: check the `launch.ini` edit saved, and that the file really
  is at `Hdd:\riffmaster.xex`.
- Wrong kernel: the plugin aborts on anything but 17559/17489.
- Disc tray open at boot.
- **Base address collision** at `0x81F00000` with another plugin. This is a silent
  failure mode. Rebuild with a different `<baseaddr>` in `src/riffmaster/xex.xml`.
- Another hiddriver360-derived plugin loaded at the same time.

**The dongle is never claimed**
- Confirm it is the right device: VID `0E6F`, PID `0248`. Other RiffMaster revisions or a
  different dongle will not match and are not supported.
- Try with `UsbdSecPatch` present. Whether the plugin works without it is genuinely
  unverified — see the README.

**Auth never completes**
- Make sure you are watching for at least ~5 s after powering the guitar on.
- The handshake is response-driven and can be disrupted by an unreliable USB port. Try a
  different port, and preferably not through a hub.

**The guitar works but a game does not see it**
- Try a build with `-DRIFFMASTER_SUBTYPE=0x07` — see the README's Rock Band vs Guitar Hero
  section. Please report which title needed it.

**The console freezes**
- Note exactly what you were doing, grab the xbWatson output, and open an issue. The
  disconnect freeze that dominated this project's development is fixed, but "fixed on one
  console" is the honest claim, not "fixed".

## Uninstalling

Remove or blank the `pluginN =` line for `riffmaster.xex`, save the ini, and hard reboot.
Nothing else is modified — the plugin makes no persistent changes to the console. All
kernel patches are applied in memory at load and are gone after a power cycle.
