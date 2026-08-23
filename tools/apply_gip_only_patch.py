"""Disable HID detours in riffmaster xex (GIP-only): fixes CRKD 'unknown controller mapping' conflict."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(r"C:\Users\narom\Downloads\riffmaster-rgh360-main")
XEXTOOL = ROOT / "tools" / "xextool.exe"
SRC_XEX = Path(r"C:\Users\narom\Desktop\riffmaster.xex")
WORK = ROOT / "patch-work"
EXE = WORK / "riffmaster-giponly.exe"
OUT_XEX = ROOT / "bin" / "riffmaster-giponly.xex"
DESKTOP = Path(r"C:\Users\narom\Desktop\riffmaster-giponly.xex")
FIXED_DIR = Path(r"C:\Users\narom\Desktop\RiffMaster-Xbox360-Fixed\FixedXEX")

RSA_PATCH_OFF = 0x14678
NOP = bytes.fromhex("60000000")

# Verified in riffmaster-giponly.exe (Aug 9 2026 retail build):
#   0x1C248 / 0x1C260 = HidAddDeviceDetour.Install / HidRemoveDeviceDetour.Install
#   0x1C2B4          = MakeThread(MappingManagerThreadProc) - mapping assistant watcher
GIP_ONLY_NOPS = [
    (0x1C248, "HidAddDeviceDetour.Install"),
    (0x1C260, "HidRemoveDeviceDetour.Install"),
    (0x1C2B4, "MappingManagerThreadProc launch"),
]

# XInputdReadStateHook: skip inherited HID context range so CRKD/UsbdSecPatch
# guitars reach the original kernel read. GIP path (exact 0x10000009 match) is
# above this instruction and is not touched.
#   0x17E2C was: blt cr6, original  (if context < 0x10000005)
#   patched to:  b original          (always pass non-GIP devices through)
HID_READSTATE_OFF = 0x17E2C
HID_READSTATE_OLD = bytes.fromhex("41980334")
HID_READSTATE_NEW = bytes.fromhex("48000334")


def run(cmd):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.check_call(cmd)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    src_xex = SRC_XEX if SRC_XEX.exists() else ROOT / "bin" / "riffmaster.xex"
    run([str(XEXTOOL), "-e", "u", "-o", str(EXE), str(src_xex)])

    data = bytearray(EXE.read_bytes())

    old_rsa = data[RSA_PATCH_OFF : RSA_PATCH_OFF + 4]
    if old_rsa != NOP:
        print(f"RSA patch @ 0x{RSA_PATCH_OFF:X}: {old_rsa.hex()} -> {NOP.hex()}")
        data[RSA_PATCH_OFF : RSA_PATCH_OFF + 4] = NOP
    else:
        print("RSA patch already applied")

    for off, label in GIP_ONLY_NOPS:
        old = data[off : off + 4]
        if old == NOP:
            print(f"  {label} @ 0x{off:X} already NOP")
        else:
            print(f"  NOP {label} @ 0x{off:X}: {old.hex()} -> {NOP.hex()}")
            data[off : off + 4] = NOP

    old_rs = data[HID_READSTATE_OFF : HID_READSTATE_OFF + 4]
    if old_rs == HID_READSTATE_NEW:
        print(f"  HID ReadState pass-through @ 0x{HID_READSTATE_OFF:X} already applied")
    elif old_rs == HID_READSTATE_OLD:
        print(f"  HID ReadState pass-through @ 0x{HID_READSTATE_OFF:X}: {old_rs.hex()} -> {HID_READSTATE_NEW.hex()}")
        data[HID_READSTATE_OFF : HID_READSTATE_OFF + 4] = HID_READSTATE_NEW
    else:
        raise RuntimeError(
            f"Unexpected bytes at HID ReadState 0x{HID_READSTATE_OFF:X}: {old_rs.hex()} "
            f"(expected {HID_READSTATE_OLD.hex()} or {HID_READSTATE_NEW.hex()})"
        )

    EXE.write_bytes(data)
    run([str(XEXTOOL), "-e", "e", "-c", "c", "-m", "r", "-r", "a", "-o", str(OUT_XEX), str(EXE)])

    shutil.copy2(OUT_XEX, DESKTOP)
    if FIXED_DIR.exists():
        shutil.copy2(OUT_XEX, FIXED_DIR / "riffmaster.xex")
        print(f"  Updated {FIXED_DIR / 'riffmaster.xex'}")

    print(f"\nDone: {DESKTOP}")


if __name__ == "__main__":
    main()
