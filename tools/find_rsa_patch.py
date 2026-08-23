from pathlib import Path

exe = Path(r"C:\Users\narom\Downloads\riffmaster-rgh360-main\patch-work\riffmaster.exe")
data = exe.read_bytes()
base = 0x81F00000


def find_refs(addr: int) -> list[int]:
    b = addr.to_bytes(4, "big")
    refs = []
    off = 0
    while True:
        i = data.find(b, off)
        if i < 0:
            break
        refs.append(i)
        off = i + 1
    return refs


for name, off in [("expect", 0x51B4), ("str_rsa", 0x51DC)]:
    va = base + off
    refs = find_refs(va)
    print(f"{name} va=0x{va:08X} file=0x{off:X} refs={len(refs)}")
    for r in refs[:20]:
        print(f"  ref at 0x{r:X}")

s = b"RIFFMASTER: *** RSA SELFTEST: %s ***"
i = data.find(s)
print("fmt at", hex(i), "va", hex(base + i))
for r in find_refs(base + i)[:20]:
    print(" fmt ref", hex(r))

refs = find_refs(base + 0x51B4)
code_refs = [r for r in refs if 0x10000 <= r < 0x40000]
print("code refs to expect", [hex(x) for x in code_refs[:10]])
for r in code_refs[:2]:
    start = max(0, r - 0x100)
    chunk = data[start : r + 0x100]
    print(f"\n=== context around ref 0x{r:X} ===")
    for j in range(0, len(chunk), 16):
        addr = start + j
        hexpart = " ".join(f"{b:02X}" for b in chunk[j : j + 16])
        print(f"{addr:06X}: {hexpart}")
