# Prebuilt plugin

| File | Description |
|---|---|
| **`riffmaster.xex`** | Stable **v1.0.2-fixed** (~94 KB). Default download from [Releases](https://github.com/Easy301/riffmaster-rgh360-fixed/releases/latest). |
| **`riffmaster-v1.0.0-fixed.xex`** | Previous stable (rollback). MD5 `F5BA2366FD6D1630375DF5F3AD91A4E0`. |
| **`riffmaster-beta.xex`** | Same bytes as current stable — kept for older release links. |

The original unpatched release from Durg5's repository is ~324 KB and does not include
the fixes in this project.

## Build info (v1.0.2-fixed)

- **MD5:** `D042E7830893347D539D4C7A47DB01A0`
- **Size:** 96,256 bytes

v1.0.1-fixed was pulled — it broke RiffMaster. v1.0.0-fixed is still on GitHub if you
need to roll back.

## Rebuild without the XDK

1. Place the original unpatched xex as `bin/riffmaster-original.xex` (~324 KB)
2. Run `python tools/apply_full_patch.py`
3. Run `python tools/apply_notify_beta_patch.py` (writes v1.0.2 over `bin/riffmaster.xex`)

Requires `tools/xextool.exe`.
