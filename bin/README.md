# Prebuilt plugin

| File | Description |
|---|---|
| **`riffmaster.xex`** | Stable **v1.0.4-fixed** (~94 KB). Default download from [Releases](https://github.com/Easy301/riffmaster-rgh360-fixed/releases/latest). |
| **`riffmaster-v1.0.0-fixed.xex`** | First patched release (rollback). MD5 `F5BA2366FD6D1630375DF5F3AD91A4E0`. |
| **`riffmaster-beta.xex`** | Same bytes as current stable — kept for older release links. |

The original unpatched release from Durg5's repository is ~324 KB and does not include
the fixes in this project.

## Build info (v1.0.4-fixed)

- **MD5:** `8994AF9F905F823F716A9E460D5971DB`
- **Size:** 96,256 bytes

## Rebuild without the XDK

1. Place the original unpatched xex as `bin/riffmaster-original.xex` (~324 KB)
2. Run `python tools/apply_full_patch.py`

Requires `tools/xextool.exe`.
