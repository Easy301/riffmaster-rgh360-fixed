# `bin/` — prebuilt plugin

| File | Purpose |
|---|---|
| **`riffmaster.xex`** | **Install this.** Patched retail build (~94 KB). Same file attached to GitHub Releases. |

## Verified build (2026-08-22)

- **MD5:** `F5BA2366FD6D1630375DF5F3AD91A4E0`
- **Size:** 96,256 bytes
- **Fixes:** RSA self-test, GIP-only (no CRKD mapping popup), HID ReadState pass-through

## Do not install the wrong file

| Size | Meaning |
|---|---|
| ~94 KB | Patched encrypted retail xex — **correct** |
| ~324 KB | Stock upstream unpatched — auth / CRKD issues |

Unpatched upstream builds are available from
[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360/releases).

## Rebuild without the XDK

1. Place an unpatched upstream xex as `bin/riffmaster-upstream.xex`
2. Run `python tools/apply_full_patch.py` (requires `tools/xextool.exe`)
