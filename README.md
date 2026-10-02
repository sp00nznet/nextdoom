# NeXTDoom — Static Recompilation

![NeXTDoom's attract demo running recompiled: the shotgun against an imp](docs/screenshots/hero.gif)

Static recompilation of **NeXTDoom 1.2** — id Software's Doom as it shipped
for NeXTSTEP 3.3, the platform Doom was written on — from the i386 slice of
its fat `Doom.app/Doom` binary to native C. Every function in the game is
lifted to C and compiled into a new program; the NeXTSTEP it expects
(libsys, the Objective-C runtime, the slice of AppKit it touches) is a host
runtime on SDL2. No emulator.

Built on the [pcrecomp](https://github.com/sp00nznet/pcrecomp) toolchain:
its Mach-O front end
([`tools/macho`](https://github.com/sp00nznet/pcrecomp/tree/main/tools/macho)) and
NeXTSTEP host runtime
([`runtime/nextstep`](https://github.com/sp00nznet/pcrecomp/tree/main/runtime/nextstep)),
both on pcrecomp's `main` since
[#25](https://github.com/sp00nznet/pcrecomp/pull/25), and following its shared
house style for recompilation projects.

**Generated source is not distributed.** You supply your own NeXTSTEP 3.3
install; the lifter runs on your machine and writes the C into a gitignored
folder.

## Status

**v0.1.0 — alpha. It boots and plays the attract demo.**

crt0, `main`, the nib, `appDidInit:` and D_DoomMain all run as recompiled
code: the title screen comes up and the demos play. Everything on screen below
is the game's own code, recompiled.

| Part | State |
|---|---|
| Lift | 676 functions, 0 errors, every body decodes onto the next start |
| 3D renderer, sprites, status bar, palette effects | Working (attract demos) |
| `R_DrawColumn` / `R_DrawSpan` (hand-written assembly) | Working |
| Keyboard | Wired through `VGAView keyDown:/keyUp:`, not play-tested |
| Mouse, sound, window scaling, netgames | Not yet ([roadmap](ROADMAP.md)) |
| Headless `--record`, conformance harness | Not yet ([roadmap](ROADMAP.md)) |

## Screenshots

| | |
|---|---|
| ![Title screen](docs/screenshots/title.png) | ![An imp in the computer room](docs/screenshots/imp.png) |
| Title screen | Shotgun versus imp, demo 1 |
| ![Firing at a fireball](docs/screenshots/fireball.png) | ![The blue-floored room, gibs on the floor](docs/screenshots/blue-room.png) |
| A fireball coming down the corridor | The blue-floored room |

![The attract demo, later](docs/screenshots/attract.gif)

## Getting Started

You need a **NeXTSTEP 3.3 Intel** install (a disk image is fine) with
`/LocalApps/Doom.app` on it. Nothing else from it is used except `/usr/shlib`.

### Step by step

Prerequisites, on Windows 10 or 11:

- [MSYS2](https://www.msys2.org/) with the mingw64 toolchain, SDL2, CMake and
  Ninja (tested with gcc 15.2, CMake 4.2, Ninja 1.13):
  `pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-SDL2 mingw-w64-x86_64-cmake mingw-w64-x86_64-ninja`
- Python 3.11+ with `capstone` (tested with 3.13 and capstone 5.0.7):
  `py -3 -m pip install capstone`
- A checkout of [pcrecomp](https://github.com/sp00nznet/pcrecomp) next to this
  one (`../pcrecomp`), or anywhere, named by `PCRECOMP` for the Python scripts
  and `-DPCRECOMP=<path>` for CMake.

Commands are for a Git Bash or MSYS2 shell, from this folder:

1. Copy the game out of the disk image with pcrecomp's UFS reader:
   ```bash
   UFS=../pcrecomp/tools/macho/ufs.py
   MSYS_NO_PATHCONV=1 py -3 $UFS hd.img get /LocalApps/Doom.app original/Doom.app
   MSYS_NO_PATHCONV=1 py -3 $UFS hd.img get /usr/shlib original/shlib
   ```
2. Lift:
   ```bash
   py -3 run_lift.py
   ```
   Expected:
   ```
   [*] code=0x00003990-0x00022E50 entry=0x00003990 functions=676 imports=59
   ============================================================
     functions 676   errors 0   files 3   lines 92,838   1.3s
   ============================================================
   ```
3. Build:
   ```bash
   export PATH=/c/msys64/mingw64/bin:$PATH
   cmake -S . -B build -G Ninja -DCMAKE_C_COMPILER=gcc
   cmake --build build
   ```
   Expected: `build/nextdoom.exe`, about 1.4 MB.
4. Run: `./build/nextdoom.exe`. The window opens on the title screen and the
   attract demos start.

Usual trip-ups: `py` vs `python` (use the `py` launcher; the Microsoft Store
`python` alias is not a real interpreter), `MSYS_NO_PATHCONV=1` (without it
MSYS rewrites `/LocalApps/...` into a Windows path), and a `PATH` change that
needs a new terminal.

A one-click `Setup.cmd` quick start is on the [roadmap](ROADMAP.md).

## Usage

`./build/nextdoom.exe` runs the game from `original/` (the path is baked in at
configure time). Diagnostics are environment variables:

| variable | effect |
|---|---|
| `NS_TRACE=1` | log every import bound and every message sent |
| `NS_SHOT=first,count,path%05d.bmp` | save frames `first`..`first+count-1` (how these screenshots were made) |

```bash
NS_SHOT=400,1,shot%05d.bmp ./build/nextdoom.exe
```

## How it works

[docs/architecture.md](docs/architecture.md) covers the design: how the
function catalog is found, how shlib imports and Objective-C methods bind to
host shims, the startup path, and video.

## Building from source

See *Step by step* above. `run_lift.py` and `CMakeLists.txt` document each step.

## License

MIT — see [LICENSE](LICENSE). This covers the code in this repository only.
Doom is © id Software and NeXTSTEP is © NeXT / Apple; no game or system code
or data is included.
