"""Locate UsbdAddDeviceCompleteHook and HidAddDeviceHook in riffmaster.exe."""
from pathlib import Path
from capstone import Cs, CS_ARCH_PPC, CS_MODE_32

data = Path(r"C:\Users\narom\Downloads\riffmaster-rgh360-main\patch-work\riffmaster.exe").read_bytes()
base = 0x81F00000
md = Cs(CS_ARCH_PPC, CS_MODE_32)

candidates = []
for off in range(0, len(data) - 8, 4):
    w = int.from_bytes(data[off : off + 4], "big")
    if (w >> 26) == 15 and ((w >> 16) & 0xFFFF) == 0x0E6F:
        candidates.append(off)

print("addis 0x0E6F hits:", len(candidates))
for off in candidates:
    start = max(0, off - 0x100)
    end = min(len(data), off + 0x280)
    print(f"\n=== file 0x{off:X} va 0x{base + off:X} ===")
    for ins in md.disasm(data[start:end], base + start):
        rel = ins.address - base
        if rel < off - 0x20 or rel > off + 0x180:
            continue
        mark = ">>>" if rel == off else "   "
        print(f"{mark} 0x{rel:05X}: {ins.mnemonic} {ins.op_str}")

for label, needle in [
    ("HidAdd", b"EINTIM: HID add device"),
    ("Unrelated", b"EINTIM: Unrelated USB"),
    ("Controller", b"EINTIM: Controller detected"),
]:
    o = data.find(needle)
    print(f"{label} string @ 0x{o:X} va 0x{base + o:X}")
