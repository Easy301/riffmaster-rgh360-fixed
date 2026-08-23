from pathlib import Path
from capstone import Cs, CS_ARCH_PPC, CS_MODE_32, CS_MODE_BIG_ENDIAN

exe = Path(r"C:\Users\narom\Downloads\riffmaster-rgh360-main\patch-work\riffmaster.exe")
data = exe.read_bytes()
base = 0x81F00000

start = 0x14920
end = 0x14980
code = data[start:end]
md = Cs(CS_ARCH_PPC, CS_MODE_32 | CS_MODE_BIG_ENDIAN)
md.detail = True

for ins in md.disasm(code, base + start):
    mark = " <<<" if ins.address == base + 0x14610 else ""
    print(f"0x{ins.address:08X}: {ins.mnemonic:8} {ins.op_str}{mark}")
