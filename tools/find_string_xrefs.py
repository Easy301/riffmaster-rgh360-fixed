"""Find PPC lis/addis + addi pairs for a VA."""
from pathlib import Path
from capstone import Cs, CS_ARCH_PPC, CS_MODE_32

BASE = 0x81F00000
data = Path(r"C:\Users\narom\Downloads\riffmaster-rgh360-main\patch-work\riffmaster-giponly.exe").read_bytes()
md = Cs(CS_ARCH_PPC, CS_MODE_32)


def find_va_uses(file_off: int):
    target = BASE + file_off
    hi = (target >> 16) & 0xFFFF
    lo = target & 0xFFFF
    insns = list(md.disasm(data, BASE))
    for i, ins in enumerate(insns):
        if ins.mnemonic != "addis":
            continue
        parts = ins.op_str.split(", ")
        if len(parts) < 3:
            continue
        try:
            imm = int(parts[2], 0)
        except ValueError:
            continue
        if imm != hi:
            continue
        reg = parts[0]
        for ins2 in insns[i + 1 : i + 10]:
            if reg not in ins2.op_str or ins2.mnemonic not in ("addi", "ori", "add"):
                continue
            p2 = ins2.op_str.split(", ")
            try:
                imm2 = int(p2[-1], 0)
            except ValueError:
                continue
            if imm2 == lo:
                off = ins.address - BASE
                print(f"String ref @ 0x{off:X}:")
                for x in insns[max(0, i - 15) : i + 25]:
                    mark = ">>" if x.address - BASE == off else "  "
                    print(f"{mark} 0x{x.address - BASE:05X}: {x.mnemonic} {x.op_str}")
                print()
                break


for off, name in [
    (0x65AC, "HID add device"),
    (0x6B7C, "Loading mappings"),
    (0x6CB0, "Hooks installed"),
]:
    print(f"=== {name} @ 0x{off:X} ===")
    find_va_uses(off)
