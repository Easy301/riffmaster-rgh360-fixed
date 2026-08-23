# Fork notice

This repository is a **community patch fork** of
**[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360)**.

The upstream project is a fork of **[EinTim23/hiddriver360](https://github.com/EinTim23/hiddriver360)**.
Almost all of the engineering credit belongs to those authors and the projects
listed in [NOTICE.md](NOTICE.md).

## What this fork adds

Three fixes for real-world setups that upstream did not cover when this fork was
created:

- RiffMaster units whose RSA self-test fails due to a different (valid) cert
- Using **UsbdSecPatch** with a **CRKD** (or similar) guitar alongside RiffMaster
- Dashboard input for those guitars while riffmaster stays loaded in DashLaunch

See [CHANGELOG.md](CHANGELOG.md) for technical detail.

## Relationship to upstream

- **Not an official release** from Durg5 or EinTim23
- Intended to be merged upstream or published separately after review
- If upstream adopts these fixes, prefer their release over this fork

## Licence

GPL-3.0, same as upstream. See [LICENSE](LICENSE).
