"""Apply all current fixes to stock riffmaster.xex (no XDK required).

Patches: RSA self-test, HID Install NOPs, HID class pass-through, mapping-thread NOP,
ReadState pass-through.

Usage (from repo root):
  python tools/apply_full_patch.py

Requires xextool.exe in tools/ (not redistributed — obtain separately).
Input:  bin/riffmaster-upstream.xex  OR  first stock xex found in bin/
Output: bin/riffmaster.xex
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XEXTOOL = ROOT / "tools" / "xextool.exe"
WORK = ROOT / "patch-work"
EXE = WORK / "riffmaster-patched.exe"
OUT_XEX = ROOT / "bin" / "riffmaster.xex"

NOP = bytes.fromhex("60000000")
RSA_PATCH_OFF = 0x14678
# 0x1C248 / 0x1C260 were the WRONG Install() calls (not DllMain HID).
# Real retail HID add/remove Install() sites are 0x18788 / 0x187C8 — see
# tools/apply_coexist_hid_install.py. Mapping thread NOP is still correct.
GIP_ONLY_NOPS = [
    (0x1C248, "wrong-site Install (legacy v1.0.0)"),
    (0x1C260, "wrong-site Install (legacy v1.0.0)"),
    (0x1C2B4, "MappingManagerThreadProc launch"),
    (0x18764, "devkit HidAddDeviceDetour.Install"),
    (0x18788, "retail HidAddDeviceDetour.Install"),
    (0x187C8, "retail HidRemoveDeviceDetour.Install"),
]
HID_READSTATE_OFF = 0x17E2C
HID_READSTATE_OLD = bytes.fromhex("41980334")
HID_READSTATE_NEW = bytes.fromhex("48000334")
# HidAddDeviceHook: class==3 claimed the device. Always take "Unrelated USB" path.
HID_CLASS_BNE_OFF = 0x1765C
HID_CLASS_BNE_OLD = bytes.fromhex("409A0300")
HID_CLASS_BNE_NEW = bytes.fromhex("48000300")


def find_input() -> Path:
    for name in ("riffmaster-upstream.xex", "riffmaster-original.xex", "riffmaster.xex"):
        p = ROOT / "bin" / name
        if p.exists() and p.stat().st_size > 200_000:
            return p
    raise FileNotFoundError(
        "Place an unpatched upstream xex in bin/riffmaster-upstream.xex (~324 KB)"
    )


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)


def patch_exe(data: bytearray) -> None:
    old_rsa = data[RSA_PATCH_OFF : RSA_PATCH_OFF + 4]
    if old_rsa != NOP:
        print(f"RSA @ 0x{RSA_PATCH_OFF:X}: {old_rsa.hex()} -> {NOP.hex()}")
        data[RSA_PATCH_OFF : RSA_PATCH_OFF + 4] = NOP

    for off, label in GIP_ONLY_NOPS:
        old = data[off : off + 4]
        if old != NOP:
            print(f"  NOP {label} @ 0x{off:X}: {old.hex()} -> {NOP.hex()}")
            data[off : off + 4] = NOP

    old_rs = data[HID_READSTATE_OFF : HID_READSTATE_OFF + 4]
    if old_rs == HID_READSTATE_NEW:
        print(f"  ReadState @ 0x{HID_READSTATE_OFF:X}: already patched")
    elif old_rs == HID_READSTATE_OLD:
        print(f"  ReadState @ 0x{HID_READSTATE_OFF:X}: {old_rs.hex()} -> {HID_READSTATE_NEW.hex()}")
        data[HID_READSTATE_OFF : HID_READSTATE_OFF + 4] = HID_READSTATE_NEW
    else:
        raise RuntimeError(f"Unexpected bytes @ 0x{HID_READSTATE_OFF:X}: {old_rs.hex()}")

    old_hid = data[HID_CLASS_BNE_OFF : HID_CLASS_BNE_OFF + 4]
    if old_hid == HID_CLASS_BNE_NEW:
        print(f"  HID pass-through @ 0x{HID_CLASS_BNE_OFF:X}: already patched")
    elif old_hid == HID_CLASS_BNE_OLD:
        print(f"  HID pass-through @ 0x{HID_CLASS_BNE_OFF:X}: {old_hid.hex()} -> {HID_CLASS_BNE_NEW.hex()}")
        data[HID_CLASS_BNE_OFF : HID_CLASS_BNE_OFF + 4] = HID_CLASS_BNE_NEW
    else:
        raise RuntimeError(f"Unexpected bytes @ 0x{HID_CLASS_BNE_OFF:X}: {old_hid.hex()}")


def main() -> int:
    if not XEXTOOL.exists():
        print("ERROR: tools/xextool.exe not found", file=sys.stderr)
        return 1

    src = find_input()
    WORK.mkdir(parents=True, exist_ok=True)
    run([str(XEXTOOL), "-e", "u", "-o", str(EXE), str(src)])

    data = bytearray(EXE.read_bytes())
    patch_exe(data)
    EXE.write_bytes(data)

    run([str(XEXTOOL), "-e", "e", "-c", "c", "-m", "r", "-r", "a", "-o", str(OUT_XEX), str(EXE)])
    print(f"\nDone: {OUT_XEX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
