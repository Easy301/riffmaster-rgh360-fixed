"""Apply all current fixes to stock riffmaster.xex (no XDK required).

Patches: RSA self-test, GIP-only HID/mapping NOPs, ReadState pass-through,
and skip leftover XAM mapping-assistant notify stores.


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
GIP_ONLY_NOPS = [
    (0x1C248, "HidAddDeviceDetour.Install"),
    (0x1C260, "HidRemoveDeviceDetour.Install"),
    (0x1C2B4, "MappingManagerThreadProc launch"),
]
HID_READSTATE_OFF = 0x17E2C
HID_READSTATE_OLD = bytes.fromhex("41980334")
HID_READSTATE_NEW = bytes.fromhex("48000334")

# Mapping-assistant XAM notify stores (same signatures as apply_ftp_hang_patch.py).
STH_TYPE80 = bytes.fromhex("b3ddb7a6")
LI_1500 = bytes.fromhex("394005dc")
STH_TIMER = bytes.fromhex("b14b0000")
LI_4800 = bytes.fromhex("39404800")
STH_JRPC = bytes.fromhex("b14b0030")


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

    type80 = data.find(STH_TYPE80)
    if type80 < 0:
        raise RuntimeError("notify type-80 store (b3ddb7a6) not found")
    if data[type80 : type80 + 4] != NOP:
        print(f"  NOP type-80 store @ 0x{type80:X}")
        data[type80 : type80 + 4] = NOP
    window = data[type80 : type80 + 0x80]
    li = window.find(LI_1500)
    sth = window.find(STH_TIMER, li, li + 16) if li >= 0 else -1
    if li < 0 or sth < 0:
        raise RuntimeError("XNotify timer store not found near type-80 sth")
    abs_sth = type80 + sth
    if data[abs_sth : abs_sth + 4] != NOP:
        print(f"  NOP XNotify timer store @ 0x{abs_sth:X}")
        data[abs_sth : abs_sth + 4] = NOP
    li2 = window.find(LI_4800)
    sth2 = window.find(STH_JRPC, li2, li2 + 12) if li2 >= 0 else -1
    if li2 < 0 or sth2 < 0:
        raise RuntimeError("JRPC2 notify store not found near type-80 sth")
    abs_sth2 = type80 + sth2
    if data[abs_sth2 : abs_sth2 + 4] != NOP:
        print(f"  NOP JRPC2 notify store @ 0x{abs_sth2:X}")
        data[abs_sth2 : abs_sth2 + 4] = NOP


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
