# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- LICENSE (MIT), CONTRIBUTING, ROADMAP, this changelog, and
  `docs/architecture.md`.

### Changed

- The build uses pcrecomp's `main` (its Mach-O front end and NeXTSTEP runtime
  landed in pcrecomp#25); the default checkout is `../pcrecomp`, overridden by
  `PCRECOMP` / `-DPCRECOMP`.

## [0.1.0] - 2026-09-30

### Added

- `run_lift.py`: lifts all 676 functions of the i386 slice of `Doom.app/Doom`
  with pcrecomp's lifter and Mach-O front end, and fails if any body does not
  decode onto the next function start.
- CMake build against pcrecomp's `runtime/nextstep` on SDL2.
- Boots to the title screen and plays the attract demos as recompiled code.
- `NS_TRACE` and `NS_SHOT` diagnostics; README screenshots taken with `NS_SHOT`.

[Unreleased]: https://github.com/sp00nznet/nextdoom/compare/cd7d55e...HEAD
[0.1.0]: https://github.com/sp00nznet/nextdoom/commit/cd7d55e
