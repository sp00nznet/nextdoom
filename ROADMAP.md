# Roadmap

## Next

- **Play-test input.** Keyboard is wired through `VGAView keyDown:/keyUp:` but
  nobody has played a level with it yet. Then the mouse.
- **Headless mode** (REPO_RULES section 10): `--headless --record out.mp4`,
  rendering offscreen and piping frames to ffmpeg. `NS_SHOT` already captures
  frames, so this is mostly a runtime change in pcrecomp's `runtime/nextstep`
  (a toolkit PR), plus the flag here.
- **Conformance harness** (REPO_RULES section 9): the attract demos are
  deterministic, so a fixed set of headless runs can check frame hashes at
  chosen tics against a reference capture. Captures stay outside the repo;
  the harness skips with a message when they are missing.
- **`Setup.cmd` quick start** (REPO_RULES section 5): check prerequisites, take
  a NeXTSTEP 3.3 Intel disk image, pull `Doom.app` and `shlib` out of it, run
  the Step by step commands, leave a shortcut.
- **CI**: lint `run_lift.py` and check the CMake configure error paths. A real
  build needs the user's NeXTSTEP files, so it can't run in CI.

## Later

- Sound (libMedia).
- Window scaling: the `scale1:/2:/4:` nib actions, which nothing sends yet.
- Netgames: sockets are stubbed to fail.

## Out of scope

- The m68k, PA-RISC and SPARC slices of the fat binary. The i386 slice is the
  same game; lifting another architecture needs another front end.
- Other Doom versions (DOS, Windows): source ports already cover them.
