# Prebuilt plugin

| File | Description |
|---|---|
| **`riffmaster.xex`** | Stable v1.0.0-fixed (~94 KB). Default download from [Releases](https://github.com/Easy301/riffmaster-rgh360-fixed/releases/latest). |
| **`riffmaster-beta.xex`** | v1.0.2-beta pre-release — possible FTP + third-party guitar freeze fix. See [release notes](../docs/RELEASE-NOTES-v1.0.2-beta.md). |

Use **`riffmaster.xex`** unless you are testing the beta. The original unpatched release from Durg5's repository is
~324 KB and does not include the fixes in this project.

## Build info (2026-08-22)

- **MD5:** `F5BA2366FD6D1630375DF5F3AD91A4E0`
- **Size:** 96,256 bytes

v1.0.1-fixed was pulled — it broke RiffMaster. Use this file.

## Rebuild without the XDK

1. Place the original unpatched xex as `bin/riffmaster-upstream.xex`
2. Run `python tools/apply_full_patch.py` (requires `tools/xextool.exe`)
