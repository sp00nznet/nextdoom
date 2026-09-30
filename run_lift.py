#!/usr/bin/env python3
"""NeXTDoom 1.2 (NeXTSTEP 3.3, i386 slice) lift driver.

Lifts every function of Doom.app/Doom with the shared pcrecomp lifter
(tools/lift/generate.py + lift32.py). The Mach-O front end is pcrecomp's
tools/macho:

  * the catalog is MachO.gcc_functions() -- gcc prologue to next prologue,
    exact for a NeXT gcc build (see its docstring); checked below by decoding
    each body linearly and requiring it to land on the next start;
  * the Lifter's iat_map is survey.import_map(): every shlib branch-table slot
    the code calls, so libsys / libNeXT calls lift to RECOMP_ICALL(slot) and
    the runtime (runtime/nextstep) binds each by its symbol name.

    py -3 run_lift.py [--exe original/Doom.app/Doom] [--out src/recomp/gen]
"""
import argparse, os, sys, time

_HERE = os.path.dirname(os.path.abspath(__file__))
_PC = os.path.join(os.environ.get('PCRECOMP') or os.path.join(_HERE, '..', 'pcrecomp-macho'), 'tools')
sys.path[:0] = [os.path.join(_PC, d) for d in ('lift', 'disasm', 'macho')]

from capstone import Cs, CS_ARCH_X86, CS_MODE_32            # noqa: E402
from generate import linear_disassemble_function, lift_function_linear, write_chunk  # noqa: E402
from lift32 import Lifter                                   # noqa: E402
from macho import MachO, slices                             # noqa: E402
from survey import import_map, load_shlibs                  # noqa: E402

HOST_SHIM = set()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--exe', default=os.path.join(_HERE, 'original', 'Doom.app', 'Doom'))
    ap.add_argument('--shlibs', default=os.path.join(_HERE, 'original', 'shlib'))
    ap.add_argument('--out', default=os.path.join(_HERE, 'src', 'recomp', 'gen'))
    ap.add_argument('--split', type=int, default=300)
    args = ap.parse_args()

    m = MachO(dict(slices(open(args.exe, 'rb').read()))['i386'])
    iat = import_map(m, load_shlibs(m, args.shlibs))
    text = m.section('__TEXT', '__text')
    cs, ce = text['addr'], text['addr'] + text['size']
    code = m.sect_bytes(text)
    fns = m.gcc_functions()
    known = {a for a, _ in fns}
    print('[*] code=0x%08X-0x%08X entry=0x%08X functions=%d imports=%d'
          % (cs, ce, m.entry, len(fns), len(iat)))

    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    lifter = Lifter(iat_map=iat, lifted=known)
    os.makedirs(args.out, exist_ok=True)
    for fn in os.listdir(args.out):
        if fn.startswith('recomp_') and fn.endswith('.c'):
            os.remove(os.path.join(args.out, fn))
    entries, chunk, idx, errors, straddle, t0 = [], [], 0, 0, [], time.time()
    for addr, end in fns:
        name = 'sub_%08X' % addr
        if addr in HOST_SHIM:
            chunk.append(('/* %s: host shim */\nextern void %s(void);\n' % (name, name), addr, name))
        else:
            try:
                insns, leaders = linear_disassemble_function(md, code, cs, addr, end)
                # The split is only right if the body decodes onto the next start,
                # give or take the linker's alignment padding (00 / 90).
                tail = code[insns[-1].end_address - cs:end - cs] if insns else b''
                if tail.strip(b'\x00\x90'):
                    straddle.append((addr, end, insns[-1].end_address))
                body = (lift_function_linear(lifter, name, insns, leaders, addr) if insns
                        else 'void %s(void) { }\n' % name)
                chunk.append((body, addr, name))
            except Exception as e:                              # noqa: BLE001
                chunk.append(('/* ERROR %s: %s */\nvoid %s(void) {}\n' % (name, e, name), addr, name))
                errors += 1
        entries.append((addr, name))
        if len(chunk) >= args.split:
            write_chunk(args.out, idx, chunk)
            idx, chunk = idx + 1, []
    if chunk:
        write_chunk(args.out, idx, chunk)
        idx += 1

    with open(os.path.join(args.out, 'recomp_funcs.h'), 'w', newline='\n') as f:
        f.write('/* NeXTDoom recomp - AUTO-GENERATED */\n#pragma once\n#include <stdint.h>\n\n')
        for a, n in entries:
            f.write('void %s(void);  /* 0x%08X */\n' % (n, a))
    with open(os.path.join(args.out, 'recomp_dispatch.c'), 'w', newline='\n') as f:
        f.write('/* NeXTDoom recomp - AUTO-GENERATED */\n'
                '#include "recomp_types.h"\n#include "recomp_funcs.h"\n\n'
                'const recomp_dispatch_entry_t recomp_dispatch_table[] = {\n')
        for a, n in sorted(entries):
            f.write('    { 0x%08Xu, %s },\n' % (a, n))
        f.write('};\nconst uint32_t recomp_dispatch_count = %d;\n' % len(entries))

    lines = sum(sum(1 for _ in open(os.path.join(args.out, fn), encoding='utf-8', errors='replace'))
                for fn in os.listdir(args.out) if fn.endswith('.c'))
    print('=' * 60)
    print('  functions %d   errors %d   files %d   lines %s   %.1fs'
          % (len(entries), errors, idx, format(lines, ','), time.time() - t0))
    print('=' * 60)
    if straddle:
        # A prologue byte pattern inside another instruction: that "start" is false.
        for a, e, got in straddle[:10]:
            print('[!] 0x%08X..0x%08X decodes to 0x%08X, not onto the next start' % (a, e, got))
        sys.exit(1)


if __name__ == '__main__':
    main()
