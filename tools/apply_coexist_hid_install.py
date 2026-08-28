"""Stop riffmaster from claiming HID gamepads (Revival Kit, etc.).

v1.0.2 NOPed the wrong Detour::Install calls (0x1C248 / 0x1C260). HID add/remove
hooks still installed on retail, so Santroller/Revival Kit got stolen from
UsbdSecPatch. CRKD still worked because it enumerates as XInput, not HID class 03.

This NOPs the real DllMain Install() sites:

  0x18764  devkit  HidAddDeviceDetour.Install   (0x8011AE38)
  0x18788  retail  HidAddDeviceDetour.Install   (0x800E4D68)  <-- the one that fired
  0x187C8  retail  HidRemoveDeviceDetour.Install (0x800E4D28)

GIP claim (UsbdAddDeviceComplete), XAM/ReadState, RSA, and notify patches stay.

Input:  bin/riffmaster.xex  (current v1.0.2-fixed)
Output: bin/riffmaster-coexist.xex + Desktop\\riffmaster.xex
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XEXTOOL = ROOT / "tools" / "xextool.exe"
WORK = ROOT / "patch-work"
SRC_XEX = ROOT / "bin" / "riffmaster.xex"
EXE = WORK / "riffmaster-coexist.exe"
OUT_XEX = ROOT / "bin" / "riffmaster-coexist.xex"
DESKTOP = Path(r"C:\Users\narom\Desktop\riffmaster.xex")
NOP = bytes.fromhex("60000000")

# bl Detour::Install — verified against unpacked v1.0.2 (targets 0x11918)
HID_INSTALLS = [
    (0x18764, bytes.fromhex("4BFF91B5"), "devkit HidAddDeviceDetour.Install"),
    (0x18788, bytes.fromhex("4BFF9191"), "retail HidAddDeviceDetour.Install"),
    (0x187C8, bytes.fromhex("4BFF9151"), "retail HidRemoveDeviceDetour.Install"),
]

# Nearby literals so we refuse to patch the wrong image
RETAIL_HID_ADD_ORI = (0x18778, bytes.fromhex("61484D68"))  # ori r8, r10, 0x4D68
RETAIL_HID_REM_ORI = (0x18790, bytes.fromhex("60A34D28"))  # ori r3, r5, 0x4D28
EXPECTED_SRC_MD5 = "D042E7830893347D539D4C7A47DB01A0"


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd))
    subprocess.check_call(cmd)


def patch_exe(data: bytearray) -> None:
    add_ori, add_bytes = RETAIL_HID_ADD_ORI
    rem_ori, rem_bytes = RETAIL_HID_REM_ORI
    if data[add_ori : add_ori + 4] != add_bytes:
        raise RuntimeError(
            f"retail HID add ori @ 0x{add_ori:X} is {data[add_ori:add_ori+4].hex()}, "
            f"expected {add_bytes.hex()} — wrong image"
        )
    if data[rem_ori : rem_ori + 4] != rem_bytes:
        raise RuntimeError(
            f"retail HID remove ori @ 0x{rem_ori:X} is {data[rem_ori:rem_ori+4].hex()}, "
            f"expected {rem_bytes.hex()} — wrong image"
        )

    for off, expected, label in HID_INSTALLS:
        got = bytes(data[off : off + 4])
        if got == NOP:
            print(f"  {label} @ 0x{off:X} already NOP")
            continue
        if got != expected:
            raise RuntimeError(
                f"{label} @ 0x{off:X} is {got.hex()}, expected {expected.hex()} or NOP"
            )
        print(f"  NOP {label} @ 0x{off:X}: {got.hex()} -> 60000000")
        data[off : off + 4] = NOP


def main() -> int:
    if not XEXTOOL.exists():
        print("ERROR: tools/xextool.exe not found", file=sys.stderr)
        return 1
    if not SRC_XEX.exists():
        print(f"ERROR: {SRC_XEX} not found", file=sys.stderr)
        return 1

    src_md5 = hashlib.md5(SRC_XEX.read_bytes()).hexdigest().upper()
    if src_md5 != EXPECTED_SRC_MD5:
        print(
            f"ERROR: {SRC_XEX} MD5 {src_md5}, expected v1.0.2-fixed {EXPECTED_SRC_MD5}",
            file=sys.stderr,
        )
        return 1

    WORK.mkdir(parents=True, exist_ok=True)
    run([str(XEXTOOL), "-e", "u", "-c", "u", "-o", str(EXE), str(SRC_XEX)])

    data = bytearray(EXE.read_bytes())
    print(f"Image size {len(data)}")
    patch_exe(data)
    EXE.write_bytes(data)

    run([str(XEXTOOL), "-e", "e", "-c", "c", "-m", "r", "-r", "a", "-o", str(OUT_XEX), str(EXE)])
    shutil.copy2(OUT_XEX, DESKTOP)

    check = WORK / "riffmaster-coexist-verify.exe"
    run([str(XEXTOOL), "-e", "u", "-c", "u", "-o", str(check), str(OUT_XEX)])
    verify = check.read_bytes()
    for off, _expected, label in HID_INSTALLS:
        got = verify[off : off + 4]
        if got != NOP:
            raise RuntimeError(f"VERIFY FAIL {label} @ 0x{off:X} is {got.hex()}, not NOP")
        print(f"  VERIFY {label} @ 0x{off:X} is NOP")
    if verify[RETAIL_HID_ADD_ORI[0] : RETAIL_HID_ADD_ORI[0] + 4] != RETAIL_HID_ADD_ORI[1]:
        raise RuntimeError("VERIFY FAIL: HID add address literal changed")

    out_md5 = hashlib.md5(OUT_XEX.read_bytes()).hexdigest().upper()
    print(f"\nDone: {OUT_XEX}")
    print(f"Desktop: {DESKTOP}")
    print(f"Size: {OUT_XEX.stat().st_size}")
    print(f"MD5:  {out_md5}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
