"""ddis.py VA [count] -- disassemble Doom's i386 slice with import/selector names."""
import sys, os, json
sys.path[:0] = [os.path.join(os.environ.get('PCRECOMP') or os.path.join(os.path.dirname(__file__), '..', '..', 'pcrecomp'), 'tools', 'macho')]
from macho import MachO, slices
from survey import load_shlibs, import_map
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
root = os.path.join(os.path.dirname(__file__), '..', 'original')
m = MachO(dict(slices(open(os.path.join(root, 'Doom.app', 'Doom'), 'rb').read()))['i386'])
imp = {va: n for va, (_, n) in import_map(m, load_shlibs(m, os.path.join(root, 'shlib'))).items()}
md = Cs(CS_ARCH_X86, CS_MODE_32)
a, n = int(sys.argv[1], 16), int(sys.argv[2]) if len(sys.argv) > 2 else 60
for i in md.disasm(m.read(a, n * 8), a, count=n):
    note = ''
    for tok in i.op_str.replace('[', ' ').replace(']', ' ').replace(',', ' ').split():
        if tok.startswith('0x'):
            v = int(tok, 16)
            if v in imp: note = imp[v]
            elif 0x243a0 <= v < 0x27928 or 0x8c000 <= v < 0x8e000:
                s = m.cstr_at(v)
                if s and s.isprintable() and len(s) > 1: note = repr(s[:40])
                elif 0x8c17c <= v < 0x8c214: note = 'SEL ' + repr(m.cstr_at(m.u32(v)))
                elif 0x8c214 <= v < 0x8c224: note = 'CLS ' + repr(m.cstr_at(m.u32(v)))
    print('  %06x: %-6s %-38s %s' % (i.address, i.mnemonic, i.op_str, note))
    if i.mnemonic == 'ret': break
