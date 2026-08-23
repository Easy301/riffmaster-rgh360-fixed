# Credits

## Where the work came from

**The overwhelming majority of this repository is upstream work.** This fork exists because
three real-world bugs blocked Gregory's setup (RiffMaster + UsbdSecPatch + CRKD on one
console). The fixes are small; the engineering that makes a RiffMaster guitar work on an
Xbox 360 at all is not.

### Primary authors (please support them)

| Who | Project | Role |
|---|---|---|
| **[Durg5](https://github.com/Durg5)** | [riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360) | RiffMaster GIP driver, auth, input mapping, game table — **the project this fork is based on** |
| **[EinTim23](https://github.com/EinTim23)** | [hiddriver360](https://github.com/EinTim23/hiddriver360) | DashLaunch USB detours, virtual XAM controller — **the foundation everything inherits** |

### Full upstream chain

See [NOTICE.md](NOTICE.md) and the Credits section of [README.md](README.md) for:

- jpdown / hiddriver360-rb1wii
- TheNathannator (PlasticBand, RB4InstrumentMapper)
- medusalix / xone
- iMoD1998 (Detours)
- Xenia, DashLaunch, RapidJSON, xkelib, xextool, and others

If you find this useful, **star and support those projects first.**

## This fork

| Who | Role |
|---|---|
| **Gregory** | Hardware testing, requirements, and maintaining this patched release |
| **Community debugging / patching** | RSA self-test fix, GIP-only mode, XInput ReadState pass-through — documented in [CHANGELOG.md](CHANGELOG.md) |

This fork is **not** an official release from Durg5 or EinTim23. It is offered for review
and, if accepted, may be merged upstream or published publicly so others with the same
setup can use it without building.

## Licence

GPL-3.0, inherited from hiddriver360. See [LICENSE](LICENSE).
