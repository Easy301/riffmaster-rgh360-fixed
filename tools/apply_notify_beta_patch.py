"""Build v1.0.2-beta xex: NOP mapping-assistant notify stores, keep JRPC2.

v1.0.1 yanked because it NOPed all three notify stores and broke the RiffMaster.
This beta only NOPs type-80 and the 1500 ms timer. JRPC2 (0x409A -> 0x4800) stays.

Usage (from repo root):
  python tools/apply_notify_beta_patch.py

Requires tools/xextool.exe and bin/riffmaster.xex (v1.0.0-fixed, MD5 F5BA...).
Output: bin/riffmaster-beta.xex
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
COPY_XEX = WORK / "riffmaster-beta-src.xex"
EXE = WORK / "riffmaster-beta.exe"
OUT_XEX = ROOT / "bin" / "riffmaster-beta.xex"
EXPECTED_MD5 = "F5BA2366FD6D1630375DF5F3AD91A4E0"

NOP = bytes.fromhex("60000000")
STH_TYPE80 = bytes.fromhex("b3ddb7a6")
LI_1500 = bytes.fromhex("394005dc")
STH_TIMER = bytes.fromhex("b14b0000")
LI_4800 = bytes.fromhex("39404800")
STH_JRPC = bytes.fromhex("b14b0030")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd))
    subprocess.check_call(cmd)


def patch_exe(data: bytearray) -> None:
    type80 = data.find(STH_TYPE80)
    if type80 < 0:
        raise RuntimeError("notify type-80 store (b3ddb7a6) not found")

    if data[type80 : type80 + 4] != NOP:
        print(f"  NOP type-80 store @ 0x{type80:X}: {data[type80:type80+4].hex()}")
        data[type80 : type80 + 4] = NOP
    else:
        print(f"  type-80 store @ 0x{type80:X} already NOP")

    window = data[type80 : type80 + 0x80]
    li = window.find(LI_1500)
    if li < 0:
        raise RuntimeError("li r10, 1500 not found near type-80 store")
    sth = window.find(STH_TIMER, li, li + 16)
    if sth < 0:
        raise RuntimeError("timer sth after li 1500 not found")
    abs_timer = type80 + sth
    if data[abs_timer : abs_timer + 4] != NOP:
        print(f"  NOP XNotify timer store @ 0x{abs_timer:X}: {data[abs_timer:abs_timer+4].hex()}")
        data[abs_timer : abs_timer + 4] = NOP
    else:
        print(f"  XNotify timer store @ 0x{abs_timer:X} already NOP")

    li2 = window.find(LI_4800)
    if li2 < 0:
        raise RuntimeError("li r10, 0x4800 not found near type-80 store")
    sth2 = window.find(STH_JRPC, li2, li2 + 12)
    if sth2 < 0:
        raise RuntimeError("JRPC2 sth after li 0x4800 not found")
    abs_jrpc = type80 + sth2
    if data[abs_jrpc : abs_jrpc + 4] == NOP:
        raise RuntimeError("JRPC2 store is already NOP — would repeat the broken 1.0.1 build")
    print(f"  KEEP JRPC2 notify store @ 0x{abs_jrpc:X}: {data[abs_jrpc:abs_jrpc+4].hex()}")


def main() -> int:
    if not XEXTOOL.exists():
        print("ERROR: tools/xextool.exe not found", file=sys.stderr)
        return 1
    if not SRC_XEX.exists():
        print(f"ERROR: {SRC_XEX} not found", file=sys.stderr)
        return 1

    src_md5 = hashlib.md5(SRC_XEX.read_bytes()).hexdigest().upper()
    if src_md5 != EXPECTED_MD5:
        print(f"ERROR: {SRC_XEX} MD5 {src_md5}, expected {EXPECTED_MD5}", file=sys.stderr)
        return 1

    WORK.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC_XEX, COPY_XEX)
    run([str(XEXTOOL), "-e", "u", "-c", "u", "-o", str(EXE), str(COPY_XEX)])

    data = bytearray(EXE.read_bytes())
    print(f"Image size {len(data)}")
    patch_exe(data)
    EXE.write_bytes(data)

    run([str(XEXTOOL), "-e", "e", "-c", "c", "-m", "r", "-r", "a", "-o", str(OUT_XEX), str(EXE)])

    after = hashlib.md5(SRC_XEX.read_bytes()).hexdigest().upper()
    if after != EXPECTED_MD5:
        print("ERROR: bin/riffmaster.xex was rewritten — restore from git", file=sys.stderr)
        return 1

    out_md5 = hashlib.md5(OUT_XEX.read_bytes()).hexdigest().upper()
    print(f"\nDone: {OUT_XEX}")
    print(f"Size: {OUT_XEX.stat().st_size}")
    print(f"MD5:  {out_md5}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
