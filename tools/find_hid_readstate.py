"""Find XInputdReadStateHook HID context compare (0x10000005)."""
from pathlib import Path

exe = Path(r"C:\Users\narom\Downloads\riffmaster-rgh360-main\patch-work\riffmaster-giponly.exe")
if not exe.exists():
    exe = Path(r"C:\Users\narom\Downloads\riffmaster-rgh360-main\patch-work\riffmaster.exe")
data = exe.read_bytes()
print("file", exe, "size", len(data))

# 0x10000005 as big-endian word
needle = (0x10000005).to_bytes(4, "big")
idx = 0
while True:
    off = data.find(needle, idx)
    if off < 0:
        break
    print(f"word 0x10000005 @ 0x{off:X}")
    idx = off + 1

# addis/lis 0x1000 then ori/addi 5 nearby
hits = []
for off in range(0, len(data) - 8, 4):
    w = int.from_bytes(data[off : off + 4], "big")
    if (w >> 26) == 15 and (w & 0xFFFF) == 0x1000:  # addis rD, rA, 0x1000
        for off2 in range(off + 4, min(off + 0x20, len(data) - 4), 4):
            w2 = int.from_bytes(data[off2 : off2 + 4], "big")
            op2 = w2 >> 26
            imm2 = w2 & 0xFFFF
            if op2 in (14, 24) and imm2 == 5:
                hits.append((off, off2, w, w2))

print("lis 0x1000 + imm 5 pairs:", len(hits))
for a, b, w, w2 in hits:
    print(f"  lis @ 0x{a:X} ({w:08X})  imm5 @ 0x{b:X} ({w2:08X})")
    start = max(0, a - 0x20)
    end = min(len(data), b + 0x40)
    from capstone import Cs, CS_ARCH_PPC, CS_MODE_32

    md = Cs(CS_ARCH_PPC, CS_MODE_32)
    for ins in md.disasm(data[start:end], 0x81F00000 + start):
        print(f"    0x{ins.address - 0x81F00000:05X}: {ins.mnemonic} {ins.op_str}")
    print()
