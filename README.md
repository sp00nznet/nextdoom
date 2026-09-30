# nextdoom

Static recompilation of **NeXTDoom 1.2** (id Software, NeXTSTEP 3.3) — the
i386 slice of `Doom.app/Doom`, lifted to C with
[pcrecomp](../pcrecomp-macho) and run on its NeXTSTEP host runtime
(`runtime/nextstep`: libsys, the ObjC runtime and an AppKit slice on SDL2).

Status: boots through crt0, `main` and the nib, shows the title screen and
plays the attract demo. Keyboard goes to `VGAView keyDown:/keyUp:`.

## Build

The binaries are not in this repo. `original/` needs `Doom.app/` and
`shlib/` from a NeXTSTEP 3.3 install; pcrecomp's `tools/macho/ufs.py` pulls
them off a disk image:

```bash
MSYS_NO_PATHCONV=1 python ../pcrecomp-macho/tools/macho/ufs.py hd.img get /LocalApps/Doom.app original/Doom.app
MSYS_NO_PATHCONV=1 python ../pcrecomp-macho/tools/macho/ufs.py hd.img get /usr/shlib original/shlib

python run_lift.py                  # -> src/recomp/gen (676 functions, ~93k lines)
PATH=/c/msys64/mingw64/bin:$PATH cmake -S . -B build -G Ninja -DCMAKE_C_COMPILER=gcc
PATH=/c/msys64/mingw64/bin:$PATH cmake --build build
./build/nextdoom.exe
```

Diagnostics: `NS_TRACE=1` logs every import and message send;
`NS_SHOT=path.bmp[:frame]` saves one frame (default 300).

## How it fits together

* **Functions**: `MachO.gcc_functions()` — gcc prologue to next prologue, plus
  the two hand-written renderers (`R_DrawColumn`, `R_DrawSpan`) found through
  the pointers Doom stores to them. `run_lift.py` fails if any body does not
  decode onto the next start.
* **Imports**: calls into libsys/libNeXT lift to `RECOMP_ICALL(slot)`; the
  runtime names the slot from the shlib's symbol table and binds the shim.
* **Startup**: `main` is `[Application new]`, `loadNibSection:` (which only
  wires DRCoord as NXApp's delegate), `[NXApp run]` → `appDidInit:` →
  D_DoomMain, which never returns and pumps events via `getNextEvent:`.
* **Video**: the window reports 12-bit RGB; VGAView converts the 8-bit frame
  through its palette and `NXDrawBitmap` blits it to an SDL texture.

## Next

Sound (libMedia, not yet called by anything that runs), mouse, window
scaling (`scale1:/2:/4:` are nib actions nothing sends), and netgames
(sockets are stubbed to fail).
