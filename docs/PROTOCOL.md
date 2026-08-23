# RiffMaster GIP protocol spec

> **Note added at release.** This document was written during protocol capture, before the
> driver existed. Two things have since been settled on hardware and the text below has
> not been rewritten:
>
> - **The `0x06` auth handshake IS mandatory.** The spec below records this as an open
>   question. It is not — a PDP RiffMaster sends no input at all until the RSA handshake
>   completes. See [HOW_IT_WORKS.md](HOW_IT_WORKS.md#3-authentication).
> - **The pickup switch mapping is still unverified**, exactly as noted below. It was never
>   actuated during capture.
>
> Everything else here was cross-checked against a working implementation and holds up.

**Status: input report map COMPLETE and cross-verified. Enumeration/init sequence COMPLETE
(§5).**

Every value here is derived from one of:
- **[CAPTURE]** `riffmaster_systematic.pcapng` (34 MB, 89.8 s, 106301 frames, captured
  2026-08-06), parsed with `tools/parse_capture.py`, `tools/timeline.py`, `tools/analog.py`.
- **[RB4IM]** `refs/RB4InstrumentMapper/` — has a **dedicated RiffMaster struct** matched on
  this exact VID/PID.
- **[XONE]** `refs/xone/` — the Linux GIP host driver.

Where sources disagree, the capture wins (CLAUDE.md Phase 1e). **No disagreements were
found.** The capture and RB4InstrumentMapper's struct agree on every single field.

---

## 1. Device identity `[VERIFIED — CAPTURE + RB4IM]`

| Field | Value | Source |
|---|---|---|
| `idVendor` | **`0x0E6F`** (PDP / Performance Designed Products) | capture frame 56 |
| `idProduct` | **`0x0248`** | capture frame 56 |
| `bcdDevice` | `0x0102` | capture frame 56 |
| `bDeviceClass` | `0xFF` (vendor-specific) | capture frame 56 |
| `bDeviceSubClass` | `0x47` | capture frame 56 |
| `bDeviceProtocol` | `0xD0` | capture frame 56 |
| `bMaxPacketSize0` | `64` | capture frame 56 |

The GIP signature `0xFF / 0x47 / 0xD0` appears at **both** device and interface level.

Independently corroborated: `refs/RB4InstrumentMapper/RB4InstrumentMapper.Core/Mapping/MapperFactory.cs:28`
`{ (0x0E6F, 0x0248), GetGuitarMapper }, // PDP Riffmaster`, and again at
`MapperFactory.cs:207-211`.

Note `refs/xone/transport/wired.c:550` matches PDP by **vendor ID only**
(`{ XONE_WIRED_VENDOR(0x0e6f) }`) plus interface `0xFF/0x47/0xD0` on interface 0 — it never
matches on product ID. Product `0x0248` does **not** appear anywhere in xone; xone has no
RiffMaster support.

## 2. Interface and endpoint layout `[VERIFIED — CAPTURE]`

**Raw descriptor bytes: `docs/riffmaster_descriptors.bin` (64 bytes)** — the complete
configuration descriptor tree, extracted from the device-29 enumeration
(`python tools/parse_capture.py captures/riffmaster_systematic.pcapng --device 29
--dump-descriptors docs/riffmaster_descriptors.bin`). The table below is decoded from those
raw bytes and independently agrees with Wireshark's dissected fields.

Config descriptor: `wTotalLength=64`, `bNumInterfaces=2`, `bmAttributes=0xA0`
(bus-powered, remote-wakeup), **`bMaxPower=500 mA`**.

| Interface | Alt | Class | SubClass | Protocol | Endpoints |
|---|---|---|---|---|---|
| 0 | 0 | `0xFF` | `0x47` | `0xD0` | 2 |
| 1 | 0 | `0xFF` | `0x47` | `0xD0` | 0 |
| 1 | 1 | `0xFF` | `0x47` | `0xD0` | 2 |

**Endpoints — this table is the single source of truth for the rest of the project
(CLAUDE.md Phase 1a). Transfer type was READ FROM THE DESCRIPTOR, not assumed:**

| Endpoint | Dir | Transfer type | `wMaxPacketSize` | `bInterval` | Purpose |
|---|---|---|---|---|---|
| **`0x81`** | **IN** | **INTERRUPT** | **64** | **4** | **GIP input reports — this is the one we service** |
| **`0x02`** | **OUT** | **INTERRUPT** | **64** | **4** | **GIP host→device commands** |
| `0x83` | IN | ISOCHRONOUS | 110 | 1 | headset audio (irrelevant to us) |
| `0x03` | OUT | ISOCHRONOUS | 220 | 1 | headset audio (irrelevant to us) |

**Interrupt, 64-byte, `bInterval=4`.** Interface 1 is a headset audio interface and should
be left alone — claim interface 0 only. This matches xone, which also uses interrupt
endpoints with 64-byte packets (`refs/xone/transport/wired.c:19`,
`#define XONE_WIRED_LEN_DATA_PKT 64`).

## 3. GIP framing `[VERIFIED — XONE + CAPTURE]`

**CLAUDE.md's hypothesis was right about the field order and right to flag the length
field. Confirmed: the length is a VARINT, and the header is NOT fixed at 4 bytes.**

Decoder: `refs/xone/bus/protocol.c:264-282` (`gip_decode_header`), varint at
`refs/xone/bus/protocol.c:200-213` (`gip_decode_varint`):

```c
for (i = 0; i < sizeof(*val) && i < len; i++) {
    *val |= (data[i] & GENMASK(6, 0)) << (i * 7);   /* 0x7f */
    if (!(data[i] & BIT(7)))                        /* 0x80 continuation */
        break;
}
```

Wire layout:

| Offset | Field |
|---|---|
| 0 | `command` |
| 1 | `options` — low nibble = client id, bit4 `ACKNOWLEDGE`, bit5 `INTERNAL`, bit6 `CHUNK_START`, bit7 `CHUNK` |
| 2 | `sequence` (u8, never zero) |
| 3.. | `packet_length` **varint** (1–4 bytes, `0x80` = continue) |
| .. | `chunk_offset` **varint**, present only when `options & 0x80` |

Two further rules that a fixed-offset parser gets wrong
(`refs/xone/bus/protocol.c:215-262`):
1. **The header is padded to an even total length.** If the varint makes the header odd, the
   encoder sets the continuation bit on the last length byte and appends a `0x00`. A
   decoder must tolerate a redundant trailing zero group.
2. When `GIP_OPT_CHUNK` is set a **second varint** follows.

`refs/xone/bus/protocol.c:12-13`: `GIP_HDR_CLIENT_ID = GENMASK(3,0)`,
`GIP_HDR_MIN_LENGTH 3`. Multiple GIP packets may be packed into one 64-byte USB transfer —
xone loops (`protocol.c:1509-1533`). **Our reader must loop too, not assume one packet per
URB.**

**For the RiffMaster input report specifically**, payload length is 32 (`0x20`), which
encodes as a single varint byte with no continuation, giving a **4-byte header** — verified
in every one of the 2491 captured reports (byte 3 is constant `0x20`). But do not hardcode
4: the announce/identify packets during enumeration are exactly the ones that can exceed
127 bytes and chunk.

### Command bytes `[VERIFIED — XONE refs/xone/bus/protocol.c:30-49]`

`0x01` ACKNOWLEDGE · `0x02` ANNOUNCE · `0x03` STATUS · `0x04` IDENTIFY · `0x05` POWER ·
`0x06` AUTHENTICATE · `0x07` VIRTUAL_KEY · `0x08` AUDIO_CONTROL · `0x0A` LED ·
`0x0B` HID_REPORT · `0x0C` FIRMWARE · `0x1E` SERIAL_NUMBER · `0x60` AUDIO_SAMPLES ·
`0x09` RUMBLE (client) · **`0x20` INPUT (client)**.

`0x20` is dispatched only when `GIP_OPT_INTERNAL` (bit 5 of options) is **clear**
(`protocol.c:1433-1436`). Observed options byte for RiffMaster input = `0x00`. ✓

---

## 4. INPUT REPORT MAP — command `0x20`, 36 bytes total `[VERIFIED]`

Observed: 2491 reports, all exactly 36 bytes, **~40 Hz** over 62.4 s.
4-byte header + 32-byte payload. Byte 3 constant `0x20` = 32. ✓

**This map is confirmed by two fully independent sources that agree exactly**: the observed
per-byte activity windows in the capture, and
`refs/RB4InstrumentMapper/RB4InstrumentMapper.Core/Parsing/Packets/Guitar/XboxRiffmasterInput.cs:8-24`
composed over `.../XboxGuitarInput.cs:38-60`.

| Pkt byte | Payload off | Size | Field | Capture evidence |
|---|---|---|---|---|
| 0 | — | u8 | GIP command = `0x20` | constant |
| 1 | — | u8 | options = `0x00` | constant |
| 2 | — | u8 | sequence | 255 distinct, increments |
| 3 | — | u8 | length varint = `0x20` (32) | constant |
| **4** | 0 | u8 | **Buttons low byte** | 7 distinct, active 0–16 s & 30–34 s |
| **5** | 1 | u8 | **Buttons high byte** | 7 distinct, active 8–22 s, 34–40 s, 42–46 s |
| **6** | 2 | u8 | **TILT** | rest `0x08`, range `0x00`–`0xF2`, swept 42–64 s |
| **7** | 3 | u8 | **WHAMMY** | rest `0x00`, range `0x00`–`0xFF`, swept 22–26 s |
| **8** | 4 | u8 | **PICKUP SWITCH** | **CONSTANT `0x00` — never actuated, see Gaps** |
| **9** | 5 | u8 | **UPPER FRETS** (bitfield) | 5 bits, active 0–10 s |
| **10** | 6 | u8 | **LOWER / SOLO FRETS** (bitfield) | 5 bits, active 8–18 s |
| **11** | 7 | u8 | **AUTO-CAL LIGHT SENSOR** (disabled by default) | constant `0x00` |
| **12–13** | 8–9 | u16 LE | **AUTO-CAL AUDIO SENSOR** (disabled by default) | constant `0x00` |
| **14–15** | 10–11 | **i16 LE** | **JOYSTICK X** (left −, right +) | active 43.9–46 s |
| **16–17** | 12–13 | **i16 LE** | **JOYSTICK Y** (up +, down −) | active 43.9–46 s |
| **18–35** | 14–31 | u8×18 | **CONSOLE FUNCTION MAP**; byte 18 bit0 = **SHARE** | `0x01` at 31.2 s only; rest constant `0x00` |

**Correction to an earlier reading:** payload offsets 7/8/9 are *not* unknown.
`refs/RB4InstrumentMapper/.../Guitar/XboxGuitarInput.cs:49-51` calls them `unk1..unk3`, but
`refs/PlasticBand/Docs/Instruments/5-Fret Guitar/Rock Band/Xbox One.md:78-85` identifies
them as the **auto-calibration light and audio sensors**. They read zero here because
auto-calibration is off by default — it must be enabled with **output report `0x21`**
(1 byte: `0`=off, `1`=light, `2`=audio, `254`=both), per that doc lines 158-168. Irrelevant
to us; we never enable it.

`[DISCREPANCY — capture wins per CLAUDE.md]` PlasticBand states the RiffMaster input report
is **28 bytes** and that the console function map is 14 bytes, noting *"the specification
says the console function map occupies 18 bytes, but the Riffmaster only provides 14"*
(`Xbox One.md:87-97`). **Our capture shows a 32-byte payload with an 18-byte function map**
— i.e. this dongle/firmware (`bcdDevice 0x0102`) matches the MS-GIPUSB spec length, not
PlasticBand's observed 14. PlasticBand's own descriptor dump lists `bcdDevice 0x0101`, one
revision older, which plausibly explains it. **Do not hardcode 28 or 36 — read the length
varint.**

### Buttons word (bytes 4–5, u16 little-endian) `[VERIFIED]`

Bit values from `refs/RB4InstrumentMapper/.../Gamepad/XboxGamepadInput.cs:9-28` reinterpreted
by `.../Guitar/XboxGuitarInput.cs:9-20`. **Every single one was observed in the capture.**

| Mask | Pkt byte.bit | Meaning | Observed at |
|---|---|---|---|
| `0x0001` | b4.0 | Sync | not pressed |
| `0x0004` | b4.2 | **Menu** (→360 Start) | 32.33 s ✓ |
| `0x0008` | b4.3 | **View** (→360 Back) | 30.14 s ✓ |
| `0x0010` | b4.4 | Green (duplicate of fret byte) | 1.5 s, 9.9 s ✓ |
| `0x0020` | b4.5 | Red (duplicate) | 3.2 s, 11.6 s ✓ |
| `0x0040` | b4.6 | **Blue** (duplicate) — note X, not Y | 6.4 s, 15.1 s ✓ |
| `0x0080` | b4.7 | **Yellow** (duplicate) | 4.7 s, 13.4 s ✓ |
| `0x0100` | b5.0 | **STRUM UP** (DpadUp) | 19.28 s, 34.45 s ✓ |
| `0x0200` | b5.1 | **STRUM DOWN** (DpadDown) | 21.19 s, 36.04 s ✓ |
| `0x0400` | b5.2 | Dpad Left | 37.47 s ✓ |
| `0x0800` | b5.3 | Dpad Right | 39.13 s ✓ |
| `0x1000` | b5.4 | Orange (duplicate) | 8.2 s, 17.1 s ✓ |
| `0x4000` | b5.6 | **Joystick click OR solo-fret flag — SHARED BIT** | 43.98 s ✓ |

**Yellow/Blue are swapped relative to a normal gamepad**: `Yellow = Y (0x0080)`,
`Blue = X (0x0040)`. Do not "fix" this.

**The colour bits in bytes 4–5 are a redundant merged view.** RB4InstrumentMapper ignores
them entirely and reads colours from bytes 9/10 instead
(`XboxGuitarInput.cs:53-57` uses `UpperFrets | LowerFrets`). Our capture confirms why: a
green press sets b4.4 whether it came from the upper row (1.5 s) or the lower row (9.9 s) —
bytes 4–5 alone **cannot** distinguish them. **Read bytes 9 and 10.**

### Fret bitfield — bytes 9 (upper) and 10 (lower/solo) `[VERIFIED]`

`refs/RB4InstrumentMapper/.../Guitar/XboxGuitarInput.cs:22-33`. Same 5 bits in both bytes:

| Bit | Colour | Upper (b9) observed | Lower/solo (b10) observed |
|---|---|---|---|
| `0x01` | Green | 1.51 s ✓ | 9.95 s ✓ |
| `0x02` | Red | 3.25 s ✓ | 11.65 s ✓ |
| `0x04` | Yellow | 4.77 s ✓ | 13.40 s ✓ |
| `0x08` | Blue | 6.43 s ✓ | 15.18 s ✓ |
| `0x10` | Orange | 8.21 s ✓ | 17.19 s ✓ |

All ten frets individually confirmed, in order, from a clean systematic capture.

### ⚠ The `0x4000` shared bit — a real trap `[VERIFIED — RB4IM + CAPTURE]`

`0x4000` (b5.6) is **overloaded**: it means *either* joystick-click *or* solo-fret-held.
`refs/RB4InstrumentMapper/.../Guitar/XboxRiffmasterInput.cs:22-23` disambiguates:

```csharp
public bool JoystickClick => (Base.Buttons & (ushort)XboxGamepadButton.LeftStickPress) != 0
    && !Base.LowerFretsPressed; // Overlaps with the solo fret flag
```

i.e. **`0x4000` set AND byte 10 == 0 ⇒ real joystick click. `0x4000` set AND byte 10 != 0
⇒ solo-fret flag.** Trust byte 10, not the flag.

The capture independently proves the overload: at **43.98 s** `0x4000` asserted **with byte
10 == 0**, and joystick bytes 14–17 went active in the same 12 ms window — that was a
**joystick click**, not a solo fret. Conversely, during the lower-fret presses at 9.9–17.4 s,
byte 10 was non-zero and `0x4000` was **never set** — so on the RiffMaster the flag does not
even track the solo frets reliably.

**This corrects `refs/xone/driver/pdp_jaguar.c:24` `GIP_JA_FRET_LOWER = BIT(14)`.** That is
the older RB4 Jaguar's meaning for the bit. Do not port xone's Jaguar interpretation to the
RiffMaster; use bytes 9/10.

### Guide button — NOT in the input report `[VERIFIED — CAPTURE + XONE + RB4IM]`

Guide arrives as a **separate GIP packet, command `0x07`** (VIRTUAL_KEY), key `0x5B`:

```
27.989 s  EP 0x81  07 20 3e 02 01 5b     Guide DOWN
28.129 s  EP 0x81  07 20 43 02 00 5b     Guide UP
57.414 s  EP 0x81  07 20 39 02 01 5b     Guide DOWN
```

Payload = `{u8 down; u8 key;}` (`refs/xone/bus/protocol.c:113-116`); only key `0x5B` is
valid (`protocol.c:24`, `:1196`). Same in
`refs/RB4InstrumentMapper/.../System/XboxKeystroke.cs:19-36`.

### Battery / status — command `0x03` `[VERIFIED — CAPTURE + XONE]`

```
 6.969 s  03 20 06 04 8b 00 00 00    status 0x8b
26.973 s  03 20 1b 04 8b 00 00 00
46.982 s  03 20 a7 04 8b 00 00 00
62.470 s  03 20 e3 04 0b 00 00 00    status 0x0b  ← bit7 CLEAR = DISCONNECTED
```

`refs/xone/bus/protocol.c:20-22, 92-95, 1084-1113`: bit7 = connected, bits3:2 = battery
type, bits1:0 = battery level. `0x8b` = connected, type 2, level 3 (full). The final `0x0b`
is the guitar disconnecting at end of capture. Roughly one status packet every 20 s
unprompted.

---

## 5. ENUMERATION / INIT SEQUENCE `[VERIFIED — CAPTURE]`

**This was captured after all.** The same `riffmaster_systematic.pcapng` contains a full
unplug/replug at the end: the dongle re-enumerated as **USB device address 29** at
t≈82.85 s (the earlier analysis covered address 28 only). User's own account of the tail of
the capture: *guitar off → dongle unplugged → dongle plugged in → ~5 s wait → guitar on.*

Decode it with the real GIP header parser (varint + chunk offset + even padding):

```
python tools/decode_init.py captures/riffmaster_systematic.pcapng --device 29 --ascii
```

Times below are relative to the first control transfer (absolute 82.8536 s).

### Stage 1 — plain USB enumeration (t+0.00 → t+0.06)

```
+0.0000  CTL  GET_DESCRIPTOR DEVICE   wLength=18
+0.0335  CTL  GET_DESCRIPTOR CONFIG   wLength=9
+0.0415  CTL  GET_DESCRIPTOR CONFIG   wLength=64
+0.0495  CTL  GET_STATUS              wLength=2
+0.0575  CTL  SET_CONFIGURATION       wLength=0
```

Standard. Note `SET_CONFIGURATION` is the last control transfer — **everything after this is
GIP over the interrupt endpoints**, no further control traffic. hiddriver360 already sends
`SET_CONFIGURATION` in its device-add path (`hiddriver360/hiddriver/main.cpp:1289-1298`).

### Stage 2 — GIP bring-up (t+1.57 → t+1.74)

**This confirms xone's model exactly: the host is reactive; there is no magic init blob.**

| Time | Dir | Packet | Wire bytes |
|---|---|---|---|
| +1.5739 | IN | **ANNOUNCE** seq=1 len=28 | `02 20 01 1C` + 28B payload |
| +1.5861 | OUT | **IDENTIFY** seq=1 len=0 | **`04 20 01 00`** |
| +1.6096 | IN | IDENTIFY reply, **chunked, 235 B total** | `04 F0 02 3A EB 01` + … |
| +1.6097 | OUT | ACKNOWLEDGE seq=2 len=9 | `01 20 02 09 00 04 20 3A 00 00 00 B1 00` |
| … | | 4 more 58-byte chunks, each ACKed | |
| +1.7058 | OUT | **POWER** seq=2 **len=15** | `05 20 02 0F 06 00 00 00 00 00 00 55 53 00 00 00 00 00 00` |
| +1.7093 | OUT | **POWER ON** seq=3 len=1 | **`05 20 03 01 00`** |
| +1.7133 | OUT | **LED** seq=4 len=3 | **`0A 20 04 03 00 01 14`** |
| +1.7379 | IN | STATUS seq=3 len=4 | `03 20 03 04 8B 01 00 00` (connected) |

`[VERIFIED]` The **IDENTIFY request is `04 20 <seq> 00`** and **POWER ON is
`05 20 <seq> 01 00`** — byte-for-byte what `refs/xone/bus/protocol.c:410-418` and `:420-433`
predicted.

`[NEW — not in xone]` The **15-byte POWER packet at +1.7058** is sent *before* power-on and
is **not something xone ever emits**. Payload `06 00 00 00 00 00 00 55 53 00 00 00 00 00 00`
contains ASCII **`US`** at payload offset 7–8 — evidently a locale/region field. Purpose
unconfirmed; it may be optional. Worth trying without it first.

`[NEW]` The **LED packet `0A 20 04 03 00 01 14`** sets the guitar's light. Not required for
input, presumably cosmetic.

### Stage 3 — ANNOUNCE payload `[VERIFIED]`

```
13 1D CA 69 DA A8 00 00 | 6F 0E | 48 02 | 01 00 00 00 01 00 03 00 01 00 01 00 ...
\____ device address ___/  \_VID_/ \_PID_/
```

Payload offsets 8–9 = `6F 0E` = **`0x0E6F` little-endian** ✓, offsets 10–11 = `48 02` =
**`0x0248`** ✓. Matches `refs/xone/bus/protocol.c:1052-1082` (`gip_handle_pkt_announce`
reads VID/PID/versions). Offsets 0–5 look like a MAC/serial.

### Stage 4 — IDENTIFY reply content `[VERIFIED]`

The 235-byte chunked reply carries ASCII class strings, directly readable in the capture:

```
PDP.Xbox.Guitar.Jaguar
Windows.Xbox.Input.NavigationController
```

**This confirms `refs/PlasticBand/Docs/Instruments/5-Fret Guitar/Rock Band/Xbox One.md:36-38`
exactly**, and means the RiffMaster identifies as the **same GIP class string as the PDP
Jaguar** — which is why `refs/xone/driver/pdp_jaguar.c:188-190`
(`.class = "PDP.Xbox.Guitar.Jaguar"`) binds it on Linux despite xone never having heard of
product `0x0248`.

Followed by interface GUIDs, including bytes `F6 6A 26 1A 46 3A E3 45 B9 B6 0F 2C 0B 2C 1E BE`
= **`1A266AF6-3A46-45E3-B9B6-0F2C0B2C1EBE`** and
`FE D2 DD EC 87 D3 94 42 BD 96 1A 71 2E 3D C7 7D` =
**`ECDDD2FE-D387-4294-BD96-1A712E3DC77D`** — both matching PlasticBand's documented
RiffMaster GUIDs.

### Stage 5 — AUTHENTICATE (t+1.75 → t+3.75) ⚠ `[VERIFIED it happens; NOT verified it is required]`

Windows runs a **full certificate-based auth handshake**, GIP command `0x06`, lasting ~2 s:

- Host → device: 58-byte challenge (`00 41 00 01 00 2C 01 01 00 28 …`)
- Device → host: an **825-byte chunked certificate** in 58-byte chunks, each ACKed
- Host → device: a **274-byte chunked** response
- Several further rounds (`00 41 …` / `00 42 …` / `00 C1 …` / `00 C2 …`)

**First `0x20` INPUT report arrives at absolute 86.6036 s (t+3.75), i.e. after the auth
exchange.** 109 input reports follow, to the end of capture.

`[HYPOTHESIS — the single most important open question for Phase 4]` **Is auth required
before the dongle streams input?** The capture cannot answer this: Windows always
authenticates, so "auth then input" is the only ordering observable here. The guitar was
also powered on manually around this time, which independently gates when input could start.

**Evidence that auth is skippable — strong but not proof:**
`refs/xone/driver/madcatz_strat.c:163-169` states outright *"We skip the handshake instead,
as it is not required."* xone contains no auth implementation in its device drivers, and
`refs/xone/driver/pdp_jaguar.c` — which binds the **same class string this dongle
reports** — works on Linux without it.

If auth turns out to be mandatory for this dongle, replaying a captured exchange will not
work (it is challenge/response), and that would be a serious problem worth escalating
before further Phase 4 work. **Test this early: bring the device up with
enumerate → IDENTIFY → POWER ON only, skip `0x06` entirely, and see whether `0x20` reports
arrive.**

### Minimum bring-up to attempt first

```
1. USB SET_CONFIGURATION
2. wait for ANNOUNCE  (0x02) from device
3. send IDENTIFY      04 20 <seq> 00
4. read + ACK the chunked identify reply   (ACK: 01 20 <seq> 09 00 <cmd> <opts> <len> ...)
5. send POWER ON      05 20 <seq> 01 00
6. (skip 0x06 AUTHENTICATE — verify empirically)
7. read 0x20 input reports on EP 0x81
```

Note `<seq>` is an adapter-global counter that is **never zero**
(`refs/xone/bus/protocol.c:335-337`).

## 6. Other host→device traffic

The capture contains **exactly one** host→device packet, at the very end:

```
62.4718 s  EP 0x02 OUT  05 20 08 01 01
```

Decoded: cmd `0x05` POWER, options `0x20` (INTERNAL, client 0), seq `0x08`, length varint
`0x01`, payload `0x01`. It is sent **0.9 ms after the disconnect status packet** — this is a
**shutdown**, not an init.

`[UNKNOWN]` xone's enum calls mode `0x01` `GIP_PWR_SLEEP` (`refs/xone/bus/protocol.h:29-34`)
but **xone never transmits mode `0x01`** — only `0x00` (ON) and `0x04` (OFF) are ever sent.
So xone confirms the framing but is not authority for this value's semantics. Treat "mode
`0x01` = sleep/standby" as unconfirmed.

### The init sequence we still need `[HYPOTHESIS — from xone, not from our capture]`

Per `refs/xone/transport/wired.c:475-525` and `bus/protocol.c`, xone is **purely reactive** —
there is no magic init blob. Sequence:
1. Host sends nothing at enumeration; submits an interrupt-IN URB and idle OUT URBs.
2. Device spontaneously sends **ANNOUNCE `0x02`** (VID/PID/versions), `protocol.c:1052-1082`.
3. Host sends **IDENTIFY `0x04`** — on the wire `04 20 <seq> 00` (`protocol.c:410-418`).
4. Device replies with the identify descriptor, usually **chunked** → host ACKs with `0x01`
   (`protocol.c:387-408`). ← *the packets most likely to exceed 127 bytes and need the varint*
5. Driver probe: **POWER ON** = `05 20 <seq> 01 00` (`protocol.c:420-433`), then LED/battery,
   then **AUTHENTICATE `0x06`**.
6. Device streams `0x20` input reports.

Relevant warning for instrument hardware,
`refs/xone/driver/madcatz_strat.c:163-169`: the Stratocaster *"sends auth chunks without
specifying the acknowledgment option while still expecting an acknowledgment. The Windows
driver handles this by sending an acknowledgment after 100 ms... We skip the handshake
instead, as it is not required."* Auth may be skippable — worth knowing for the 360 side.

---

## 6. Gaps — what this capture does NOT answer

1. ~~No enumeration / init sequence.~~ **RESOLVED — see §5.** The replug at the end of the
   capture enumerated as device address **29** and contains the complete sequence. (The
   original analysis missed it by only examining address 28.) The remaining open item is not
   the sequence itself but **whether the `0x06` auth handshake is mandatory** — see §5
   stage 5.
2. **Pickup switch never actuated.** `[GAP]` Byte 8 is constant `0x00` across all 2491
   reports. RB4IM says values are `0x00,0x10,0x20,0x30,0x40`
   (`GuitarvJoyMapper.cs:41-70`) — plausible but **unverified on this hardware**.
3. **Tilt range not fully swept.** Observed `0x00`–`0xF2` with rest `0x08`. RB4IM notes tilt
   *"seems to have a threshold of around 0x70, after a certain point values will get floored
   to 0"* (`GuitarvJoyMapper.cs:56-58`) — not reproduced/confirmed here.
4. **Joystick range not fully swept.** Only ~2 s of movement at 43.9–46 s. Full-range
   min/max per axis unknown.
5. **No wireless-sync or multi-guitar behaviour** captured.
6. **Guide release at 57.41 s never arrived** — the device disconnected first. Not a bug,
   just an artefact.

## 7. Reproducing this analysis

```
python tools/parse_capture.py riffmaster_systematic.pcapng   # auto-detects the GIP device
python tools/timeline.py     riffmaster_systematic.pcapng --device 28
python tools/analog.py       riffmaster_systematic.pcapng --device 28
```

`parse_capture.py` auto-detects the dongle by GIP signature rather than hardcoded address,
is transfer-type-agnostic, and diffs reports to surface changing bytes/bits from data
(CLAUDE.md Phase 1d).

`docs/riffmaster_descriptors.bin` was **NOT** produced: USBPcap did not record the raw
`GET_DESCRIPTOR` payload bytes for this capture (descriptors were recovered from
Wireshark's dissected fields instead). The re-capture should fix this.
