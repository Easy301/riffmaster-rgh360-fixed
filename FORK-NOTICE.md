# About This Release

This is a **patched community release** of
**[Durg5/riffmaster-rgh360](https://github.com/Durg5/riffmaster-rgh360)**, which is based
on **[EinTim23/hiddriver360](https://github.com/EinTim23/hiddriver360)**.

Durg5 and EinTim23 did the engineering that makes a RiffMaster guitar work on Xbox 360.
This fork adds three targeted fixes for hardware setups the original patch did not
support. See [CREDITS.md](CREDITS.md).

---

## Why this release exists

### RiffMaster authentication

On many real RiffMaster units, the original release fails during the GIP auth handshake.
The guitar looks paired to the dongle, but the Xbox never receives button input.

This release allows authentication to continue when a guitar's certificate is valid but
differs from the one used during the original author's testing.

### UsbdSecPatch coexistence

Some players use **UsbdSecPatch** for other third-party guitars on the same modded console
(for example CRKD-type instruments). With the original release loaded, those guitars were
unresponsive unless riffmaster was unloaded — often with a mapping popup. That was harder
than it looked, because some guitars (CRKD) never hit the HID claim. **v1.0.4** passes HID
devices through so UsbdSecPatch can own them. The RiffMaster dongle and UsbdSecPatch
guitars should run together.

---

## Changes in this release

| Fix | Summary |
|---|---|
| RSA self-test | Auth no longer aborts on a different (valid) device certificate |
| GIP-only mode | HID detours and mapping assistant disabled by default |
| ReadState pass-through | UsbdSecPatch guitars keep working while riffmaster is loaded |

Full technical detail: [CHANGELOG.md](CHANGELOG.md)

---

## Relationship to the original project

- Not an official release from Durg5 or EinTim23
- Offered for community testing and feedback
- If the original author incorporates these fixes, prefer their release going forward

Licensed under **GPL-3.0**, same as the original project. See [LICENSE](LICENSE).
