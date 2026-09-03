# Changelog

Changes in this release relative to the original
[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360) patch.

---

## Summary

Download **`riffmaster.xex`** (**1.04 stable**) from
**[Releases](https://github.com/Easy301/riffmaster-rgh360-fixed/releases/latest)**.

| # | Fix | User impact |
|---|---|---|
| 1 | RSA self-test | RiffMaster works on consoles that meet the original requirements |
| 2 | HID pass-through | UsbdSecPatch guitars stay usable alongside riffmaster |
| 3 | Notify patch | Fewer freezes when plugging a third-party guitar while a PC FTP client is connected |

Install guide: [docs/INSTALL-FIXED.md](docs/INSTALL-FIXED.md)

---

## [1.04 stable] — 2026-08-27

**Current release.** MD5 `8994AF9F905F823F716A9E460D5971DB`

Stable build with all three fixes above. Wired HID guitars (Revival Kit, Santroller, and
similar) no longer get claimed by riffmaster’s HID hook while the RiffMaster dongle stays
active. The RiffMaster GIP path is unchanged from the first working patch.

Release notes: [docs/RELEASE-NOTES.md](docs/RELEASE-NOTES.md)

---

## Development history (not published separately)

Earlier numbered builds (1.0.0 through 1.0.3) were internal steps toward 1.04. They are
not kept on GitHub Releases — use **1.04 stable** only.

### First working patch (basis for 1.04)

- RSA self-test no longer aborts auth on a valid but different device certificate
- GIP-only mode: HID detours and mapping assistant disabled by default
- ReadState pass-through so UsbdSecPatch guitars keep working while riffmaster is loaded
- `tools/apply_full_patch.py` — rebuild without the Xbox 360 XDK

Licensed under **GPL-3.0**, same as the original project.
