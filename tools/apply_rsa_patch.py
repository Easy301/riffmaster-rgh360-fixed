"""Binary patch: skip RSA known-answer early return in GipRsaSelfTest."""
from pathlib import Path
import shutil

root = Path(r"C:\Users\narom\Downloads\riffmaster-rgh360-main")
exe = root / "patch-work" / "riffmaster.exe"
out_exe = root / "patch-work" / "riffmaster-patched.exe"
xex_in = root / "bin" / "riffmaster.xex"
xex_out = root / "bin" / "riffmaster-patched.xex"
desktop = Path(r"C:\Users\narom\Desktop") / "riffmaster-patched.xex"

PATCH_OFF = 0x14678
NOP = bytes.fromhex("60000000")  # ori r0, r0, 0

data = bytearray(exe.read_bytes())
old = data[PATCH_OFF : PATCH_OFF + 4]
if old == NOP:
    print("Already patched")
else:
    print(f"Patching 0x{PATCH_OFF:X}: {old.hex()} -> {NOP.hex()}")
    data[PATCH_OFF : PATCH_OFF + 4] = NOP
    out_exe.write_bytes(data)

shutil.copy2(out_exe, exe)  # xextool reads from patch-work path below

print("Patched exe written:", out_exe)
