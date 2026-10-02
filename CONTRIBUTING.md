# Contributing

This is a recompilation project, which changes what a useful contribution looks
like. Three rules matter more than the rest.

## No game or system files, ever

Nothing from a NeXTSTEP install goes in the repository, in any form: no
`Doom.app`, no WAD, no shlib, no disk image, and nothing regenerated from one --
no lifted source, disassembly listing, reconstructed header, or test file with a
lifted function in it.

The tool ships; the game does not. Everyone brings their own NeXTSTEP 3.3 Intel
install and points the tools at it. `.gitignore` covers `original/` and
`src/recomp/gen/`; if something slips past it, that is a bug worth reporting on
its own.

Screenshots and recordings of the game running are fine, and are the point of
the README.

## Where your code comes from

Contributions have to be your own work or under a licence compatible with MIT.
The live risk is a fix ported from a GPL project, which would relicense it by
accident and is very hard to untangle later. The ones most likely to be open
next to this are **id's released Doom source** and its source ports
(GPL-2.0), and **GNUstep** (LGPL/GPL) for AppKit behaviour. Reading them to
understand a behaviour is fine; copying code from them is not. If something in
your PR came from somewhere, say where.

## Toolkit fixes go to pcrecomp

Most of the work here is in [pcrecomp](https://github.com/sp00nznet/pcrecomp):
the lifter, `tools/macho`, and `runtime/nextstep`. A change that any NeXTSTEP
title could need belongs there, as its own PR; this repo keeps only what is
specific to Doom.

## The usual

- Imperative commit subjects; the body explains *why* when it is not obvious.
- Community pull requests are merged with a merge commit, never squashed or
  rebased, so your commits stay yours. Anything the maintainer adds goes in
  separate commits on top.
- Comments explain the reasoning, not the syntax.
- AI-assisted contributions are welcome, provided a human understood and
  verified the change -- ran it, and can say what it does.
