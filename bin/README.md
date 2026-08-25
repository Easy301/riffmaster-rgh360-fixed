# Prebuilt plugin

| File | Description |
|---|---|
| **`riffmaster.xex`** | Patched retail build (~94 KB). Same file attached to [GitHub Releases](https://github.com/Easy301/riffmaster-rgh360-fixed/releases). |

Use this file for installation. The original unpatched release from Durg5's repository is
~324 KB and does not include the fixes in this project.

## Build info (2026-08-25)

- **MD5:** `0620F5564CA2D7E1B7F03E9FDDB66160`
- **Size:** 96,256 bytes

Previous build (2026-08-22) MD5 was `F5BA2366FD6D1630375DF5F3AD91A4E0`.

## Rebuild without the XDK

1. Place the original unpatched xex as `bin/riffmaster-upstream.xex`
2. Run `python tools/apply_full_patch.py` (requires `tools/xextool.exe`)
