"""Patch working riffmaster xex: RSA fix + clearer coexist log strings (no XDK rebuild)."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(r"C:\Users\narom\Downloads\riffmaster-rgh360-main")
XEXTOOL = ROOT / "tools" / "xextool.exe"
SRC_XEX = Path(r"C:\Users\narom\Desktop\riffmaster.xex")
if not SRC_XEX.exists():
    SRC_XEX = ROOT / "bin" / "riffmaster.xex"

WORK = ROOT / "patch-work"
EXE = WORK / "riffmaster-coexist.exe"
DECRYPTED = ROOT / "bin" / "riffmaster-coexist-decrypted.xex"
OUT_XEX = ROOT / "bin" / "riffmaster-coexist.xex"
DESKTOP = Path(r"C:\Users\narom\Desktop") / "riffmaster-coexist.xex"
PACKAGE = Path(r"C:\Users\narom\Desktop\RiffMaster-Xbox360-Fixed\FixedXEX\riffmaster-coexist.xex")

RSA_PATCH_OFF = 0x14678
NOP = bytes.fromhex("60000000")

# Same length or shorter than originals (NUL-padded).
STRING_PATCHES = [
    (
        b"EINTIM: HID add device %p\n",
        b"RIFFMASTER: HID dev %p\r\n\x00\x00",
    ),
    (
        b"EINTIM: Controller detected. Initialising custom handler.\n",
        b"RIFFMASTER: *** HID CLAIM - blocks other drivers! ***\r\n   ",
    ),
    (
        b"EINTIM: Unrelated USB Device. Calling original...\n",
        b"RIFFMASTER: HID pass-through (not claiming)\r\n     ",
    ),
    (
        b"EINTIM: HID device vendor id: %x, product id: %x\n",
        b"RIFFMASTER: HID VID=%x PID=%x (CRKD check)\r\n     ",
    ),
    (
        b"EINTIM: No free index!\n",
        b"RIFF: no HID slot!\n\x00\x00\x00",
    ),
]


def run(cmd):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.check_call(cmd)


def patch_bytes(buf: bytearray, label: str) -> int:
    n = 0
    for old, new in STRING_PATCHES:
        if len(new) > len(old):
            raise ValueError(f"{label}: new string longer than old: {new!r}")
        idx = 0
        while True:
            off = buf.find(old, idx)
            if off < 0:
                break
            patched = new + b"\x00" * (len(old) - len(new))
            buf[off : off + len(old)] = patched
            print(f"  string @ 0x{off:X}: {old[:40]!r} -> {patched[:40]!r}")
            n += 1
            idx = off + len(old)
    return n


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    run([str(XEXTOOL), "-e", "u", "-o", str(EXE), str(SRC_XEX)])

    data = bytearray(EXE.read_bytes())
    old_rsa = data[RSA_PATCH_OFF : RSA_PATCH_OFF + 4]
    if old_rsa != NOP:
        print(f"RSA patch @ 0x{RSA_PATCH_OFF:X}: {old_rsa.hex()} -> {NOP.hex()}")
        data[RSA_PATCH_OFF : RSA_PATCH_OFF + 4] = NOP
    else:
        print("RSA patch already applied")

    n = patch_bytes(data, "exe")
    print(f"Patched {n} string occurrence(s)")
    EXE.write_bytes(data)

    run([str(XEXTOOL), "-e", "e", "-c", "c", "-m", "r", "-r", "a", "-o", str(OUT_XEX), str(EXE)])
    shutil.copy2(OUT_XEX, DECRYPTED.with_suffix(".xex"))
    shutil.copy2(OUT_XEX, DESKTOP)
    if PACKAGE.parent.exists():
        shutil.copy2(OUT_XEX, PACKAGE)
    print(f"\nDone: {DESKTOP}")
    print(f"      {OUT_XEX}")


if __name__ == "__main__":
    main()
