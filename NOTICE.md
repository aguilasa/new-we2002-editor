# NOTICE

## Lineage

This project descends from a chain of prior work. Credit where it is due:

| Author | Year | Contribution |
|---|---|---|
| **Francesco Moriero** | 2002 | Original tool, *"we2002 mania editor 1.2 English (final version)"*. Wrote the MFC application and reverse-engineered the WE2002 CD image layout — the ~69 hardcoded byte offsets that make this program possible. See [`readme.txt`](readme.txt) for the original release notes and the community credits (cicco, walxer, honome_wec, luha, haplo, adesy, actaruss, alex1, `#winningmania`, walxer's forum). |
| **thyddralisk** | 2015 | Published the sources on GitHub at <https://github.com/thyddralisk/WE2002-editor-2.0> and added the SoFIFA database import feature. |
| **Obocaman** | 2002 | *WE2002 Team Editor v0.99* (`we-team-editor.exe`), a separate editor for the same game, written in Borland C++Builder 6. It is **not** an ancestor of the Qt port: it is the subject of the reverse engineering described below, and the behavioural oracle its tests are measured against. |
| **aguilasa** | 2026 | Cross-platform Qt port (in progress), the application icon, and *WE2002 - Lazarus Editor* — a from-specification reimplementation of Obocaman's editor in Object Pascal. |

The icon in `src/app/resources/` is **not** inherited work. It is drawn from
scratch by [`tools/make_icon.py`](tools/make_icon.py) and is not derived from
Moriero's `legacy/mfc/res/ed.ico`, which stays in the tree unchanged as history.
The only thing taken from it is the maroon of the stripes. This matters because
everything else here is unlicensed third-party code, and the boundary is worth
recording.

## Lineage of *WE2002 - Lazarus Editor* (the `wte/` tree)

`wte/` is a second, separate product in this repository: a reimplementation of
**Obocaman's WE2002 Team Editor v0.99** as a native Lazarus/LCL application for
Linux. Obocaman's binary carries no license either — same position as the code
inherited from Moriero and thyddralisk — so the boundary between what was
*measured* and what was *copied* is worth stating precisely.

**What this reimplementation is made of:**

- **Behaviour, written down as specification.** Each of the 96 published
  handlers has a document in `wte/re/spec/` that says what it reads, what it
  writes and under which conditions. The Pascal is written **from the
  document**, never from decompiler output — transcribing decompiled C++ would
  produce a derivative work, and it is refused as a matter of method, not of
  effort. See §2 and §8.10 of
  [`docs/PLAN-WTE-LAZARUS.md`](docs/PLAN-WTE-LAZARUS.md).
- **A data layer that does not come from the `.exe` at all.** The CD image
  format is read and written by code generated from `we2002_core`, this
  repository's own C++ core — the one already proven byte-identical to
  Moriero's `ed.exe` on both test images. Obocaman's binary answers *what does
  this operation write*; it is never the source of *how*.
- **Forms converted from format, not copied from code.** The 18 `.lfm` files
  are produced by `wte/tools/dfm2lfm.py` from the `.dfm` resources read out of
  the executable. What crosses over is layout data — coordinates, captions,
  and the 118 embedded bitmaps the forms need in order to be comparable
  against the original. The decision to version those blobs, and its limits,
  is recorded in [`wte/re/dfm/README.md`](wte/re/dfm/README.md).

**What is not redistributed.** The editor's art and data — the 198 `.bmp` under
`image/` and `data/dat.bin` — stay out of this repository, like the CD images
do. Supplying that folder is the user's business, the same arrangement `roms/`
already has. The application resolves the folder at run time, in a fixed search
order; the rule for the missing case is that it must name the files it wants
and the directory it wants them in, never a bare file-not-found. Today it says
only `data/dat.bin nao encontrado` and keeps running — closing that gap is
[WTE-TASK-39](docs/tasks/concluidos/39-empacotamento.md), which owns the run-time
resolution.

**The product name is deliberately not Obocaman's.** *WE2002 Team Editor* names
his program; this one is *WE2002 - Lazarus Editor*. Beyond the courtesy, two
practical reasons: the original binary stays on disk as the test oracle, and
the test harness finds windows by title — a shared name would make it drive the
wrong side.

If you are Obocaman, or hold rights to *WE2002 Team Editor*, and want this work
licensed, relicensed, or taken down, please open an issue.

## Copyright and license status

**This project has no license.**

Neither Francesco Moriero, thyddralisk, nor Obocaman released their work under
any license:

- The 2002 `readme.txt` contains only a liability disclaimer — no grant of
  rights to copy, modify, or redistribute.
- `ed.rc` carries a bare `LegalCopyright "Copyright (C) 2002"` with no named
  holder.
- The upstream GitHub repository has no `LICENSE` file and no license metadata.
- No source file contains a license header.
- `we-team-editor.exe` ships with no license text of any kind, and no source.
  It is not in this repository for that reason.

By default, that means the inherited code — and Obocaman's binary, which is
studied but not inherited — is **all rights reserved** by its original
authors. No permission has been granted to anyone, including the
maintainer of this repository.

Consequently, no `LICENSE` file is provided here. Adding one would claim
rights this project does not hold and would mislead anyone who relied on it.

**What this means for you:** this repository is published for preservation,
study, and use within the WE2002 modding community. It carries no warranty and
no grant of rights. If you intend to redistribute it or build on it, be aware
you are in the same position as this repository — working with unlicensed
third-party code.

If you are Francesco Moriero, or hold rights to the original work, and want
this repository licensed, relicensed, or taken down, please open an issue.

## Third-party components

- **libcurl** (`libcurl.dll`, bundled for the Windows build) is distributed
  under the curl license, an MIT/X-derivative. See
  <https://curl.se/docs/copyright.html>. Its license text must accompany any
  redistribution of the binary.

## Trademarks

*Winning Eleven*, *World Soccer Winning Eleven*, and *Pro Evolution Soccer* are
trademarks of Konami. This project is an unofficial, non-commercial fan tool
and is not affiliated with, endorsed by, or sponsored by Konami.

No game data, ROM, or CD image is distributed with this project. You must
supply your own legally obtained copy.
