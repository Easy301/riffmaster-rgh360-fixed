# Prebuilt plugin

| File | Description |
|---|---|
| **`riffmaster.xex`** | Stable **v1.0.3-fixed** (~94 KB). Default download from [Releases](https://github.com/Easy301/riffmaster-rgh360-fixed/releases/latest). |
| **`riffmaster-v1.0.0-fixed.xex`** | Previous stable (rollback). MD5 `F5BA2366FD6D1630375DF5F3AD91A4E0`. |
| **`riffmaster-beta.xex`** | Same bytes as current stable — kept for older release links. |

The original unpatched release from Durg5's repository is ~324 KB and does not include
the fixes in this project.

## Build info (v1.0.3-fixed)

- **MD5:** `F78D30F691ED3CDCDDB7197E3C94E32C`
- **Size:** 96,256 bytes

Roll back to **v1.0.2-fixed** (`D042E7830893347D539D4C7A47DB01A0`) or **v1.0.0-fixed** on GitHub if you need an older build.

## Rebuild without the XDK

1. Place the original unpatched xex as `bin/riffmaster-original.xex` (~324 KB)
2. Run `python tools/apply_full_patch.py`
3. Run `python tools/apply_notify_beta_patch.py` (writes v1.0.2 notify NOPs)
4. Run `python tools/apply_coexist_hid_install.py` (NOPs the real HID Install sites; writes Desktop `riffmaster.xex`)

Requires `tools/xextool.exe`.
