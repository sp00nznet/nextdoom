# Architecture

Three parts: the lift driver (`run_lift.py`), which turns the i386 slice of
`Doom.app/Doom` into C; the generated C; and pcrecomp's NeXTSTEP host runtime,
which maps the original images and connects the generated code to SDL2.

```
original/Doom.app/Doom ─┐
original/shlib/*  ──────┴─> run_lift.py  (pcrecomp tools/macho + lift32 + generate.py)
                                 │
                                 v
                       src/recomp/gen/*.c  (gitignored)
                                 │
                                 + src/main.c + pcrecomp runtime/nextstep
                                 v
                       build/nextdoom.exe ──maps Doom and the shlibs at their
                                            real addresses, enters crt0
```

## Functions

`MachO.gcc_functions()`: NeXT's gcc gives every function a frame, keeps switch
arms in the body and jump tables in `__const`, so prologue-to-next-prologue is
exact. The two frameless assembly renderers (`R_DrawColumn`, `R_DrawSpan`) are
found through the pointers Doom stores to them. `run_lift.py` fails if any body
does not decode onto the next start, because a prologue byte pattern inside
another instruction would otherwise produce a false function silently.

## Imports

Calls into libsys/libNeXT lift to `RECOMP_ICALL(slot)`. The shlibs are mapped
at their real addresses; the runtime names each slot from the shlib's own
symbol table and binds the host shim by that name.

## Objective-C

The classes are the images' own `__OBJC` data, so AppKit's hierarchy and ivar
layout are the real ones; host methods are bound by symbol
(`-[Window setContentView:]`) exactly like C imports.

## Startup

`[Application new]`, `loadNibSection:` (which only has to wire `DRCoord` as
NXApp's delegate), `[NXApp run]` → `appDidInit:` → D_DoomMain, which never
returns and pumps its own events through `getNextEvent:`.

## Video

The window reports 12-bit RGB; VGAView converts Doom's 8-bit frame through its
palette and `NXDrawBitmap` blits it to an SDL texture.

## Build flags

`-foptimize-sibling-calls` is load-bearing (`CMakeLists.txt`): a guest loop
split across two lifted functions tail-calls itself, which is unbounded
recursion until the compiler turns it into a jump.
