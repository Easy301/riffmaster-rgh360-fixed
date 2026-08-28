"""Stop HidAddDeviceHook from claiming HID gamepads.

v1.0.3 NOPed DllMain HidAdd/HidRemove Install() sites, but the hook still ran
(Assigning + EINTIM on plug). Detour operator= still installs the hook, then
the class 03/00/00 check claims Revival Kit / Santroller and can freeze the box.

This turns the class==3 check into an unconditional branch to the existing
"Unrelated USB Device. Calling original..." path. GIP claim, XAM, RSA, notify,
and USB-reset / probe Install() sites are not touched.

Input:  bin/riffmaster.xex  (v1.0.3-fixed)
Output: bin/riffmaster.xex + Desktop\\riffmaster.xex
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
KEEP_V103 = ROOT / "bin" / "riffmaster-v1.0.3-fixed.xex"
EXE = WORK / "riffmaster-hid-passthrough.exe"
OUT_XEX = ROOT / "bin" / "riffmaster.xex"
DESKTOP = Path(r"C:\Users\narom\Desktop\riffmaster.xex")

EXPECTED_SRC_MD5 = "F78D30F691ED3CDCDDB7197E3C94E32C"

# HidAddDeviceHook: if (bInterfaceClass == 3) claim; else pass-through @ 0x1795C
CMP_CLASS3_OFF = 0x17658
CMP_CLASS3 = bytes.fromhex("2B080003")  # cmplwi cr6, r8, 3
BNE_PASSTHRU_OFF = 0x1765C
BNE_PASSTHRU = bytes.fromhex("409A0300")  # bne cr6, +0x300 -> 0x1795C
B_PASSTHRU = bytes.fromhex("48000300")  # b +0x300 -> 0x1795C

# Leave these alone (GIP / XAM)
GIP_INSTALL = 0x1881C


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd))
    subprocess.check_call(cmd)


def patch_exe(data: bytearray) -> None:
    got_cmp = bytes(data[CMP_CLASS3_OFF : CMP_CLASS3_OFF + 4])
    if got_cmp != CMP_CLASS3:
        raise RuntimeError(
            f"class==3 compare @ 0x{CMP_CLASS3_OFF:X} is {got_cmp.hex()}, "
            f"expected {CMP_CLASS3.hex()} — wrong image"
        )
    got_br = bytes(data[BNE_PASSTHRU_OFF : BNE_PASSTHRU_OFF + 4])
    if got_br == B_PASSTHRU:
        print(f"  HID pass-through @ 0x{BNE_PASSTHRU_OFF:X} already applied")
        return
    if got_br != BNE_PASSTHRU:
        raise RuntimeError(
            f"bne pass-through @ 0x{BNE_PASSTHRU_OFF:X} is {got_br.hex()}, "
            f"expected {BNE_PASSTHRU.hex()} or {B_PASSTHRU.hex()}"
        )
    gip = bytes(data[GIP_INSTALL : GIP_INSTALL + 4])
    if gip == bytes.fromhex("60000000"):
        raise RuntimeError("GIP Install @ 0x1881C is already NOP — refusing to use this image")
    print(f"  HID class check @ 0x{BNE_PASSTHRU_OFF:X}: {got_br.hex()} -> {B_PASSTHRU.hex()}")
    data[BNE_PASSTHRU_OFF : BNE_PASSTHRU_OFF + 4] = B_PASSTHRU


def main() -> int:
    if not XEXTOOL.exists():
        print("ERROR: tools/xextool.exe not found", file=sys.stderr)
        return 1
    if not SRC_XEX.exists():
        print(f"ERROR: {SRC_XEX} not found", file=sys.stderr)
        return 1

    src_bytes = SRC_XEX.read_bytes()
    src_md5 = hashlib.md5(src_bytes).hexdigest().upper()
    if src_md5 != EXPECTED_SRC_MD5:
        print(
            f"ERROR: {SRC_XEX} MD5 {src_md5}, expected v1.0.3-fixed {EXPECTED_SRC_MD5}",
            file=sys.stderr,
        )
        return 1

    if not KEEP_V103.exists():
        shutil.copy2(SRC_XEX, KEEP_V103)
        print(f"Kept v1.0.3 at {KEEP_V103}")

    WORK.mkdir(parents=True, exist_ok=True)
    run([str(XEXTOOL), "-e", "u", "-c", "u", "-o", str(EXE), str(SRC_XEX)])

    data = bytearray(EXE.read_bytes())
    print(f"Image size {len(data)}")
    patch_exe(data)
    EXE.write_bytes(data)

    run([str(XEXTOOL), "-e", "e", "-c", "c", "-m", "r", "-r", "a", "-o", str(OUT_XEX), str(EXE)])
    shutil.copy2(OUT_XEX, DESKTOP)

    check = WORK / "riffmaster-hid-passthrough-verify.exe"
    run([str(XEXTOOL), "-e", "u", "-c", "u", "-o", str(check), str(OUT_XEX)])
    verify = check.read_bytes()
    if verify[BNE_PASSTHRU_OFF : BNE_PASSTHRU_OFF + 4] != B_PASSTHRU:
        raise RuntimeError("VERIFY FAIL: HID pass-through branch missing")
    if verify[CMP_CLASS3_OFF : CMP_CLASS3_OFF + 4] != CMP_CLASS3:
        raise RuntimeError("VERIFY FAIL: class==3 compare changed")
    if verify[GIP_INSTALL : GIP_INSTALL + 4] == bytes.fromhex("60000000"):
        raise RuntimeError("VERIFY FAIL: GIP Install was NOPed")
    print(f"  VERIFY class check @ 0x{BNE_PASSTHRU_OFF:X} is unconditional pass-through")
    print(f"  VERIFY GIP Install @ 0x{GIP_INSTALL:X} still {verify[GIP_INSTALL:GIP_INSTALL+4].hex()}")

    out_md5 = hashlib.md5(OUT_XEX.read_bytes()).hexdigest().upper()
    print(f"\nDone: {OUT_XEX}")
    print(f"Desktop: {DESKTOP}")
    print(f"Size: {OUT_XEX.stat().st_size}")
    print(f"MD5:  {out_md5}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
