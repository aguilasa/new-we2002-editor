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

## Lineage of the `BIN/*.BIN` asset tooling

`tools/pes2/lzss.py` is the first file in this repository derived from the
**CARP** tool suite. Section 9 of
[`docs/PLAN-FEATURES.md`](docs/PLAN-FEATURES.md) made this section a
*blocking* requirement of that file existing, so it lands in the same commit.

| Author | Work | What was taken |
|---|---|---|
| **Maximiliano Ducoli (CARP)** | [WECompressor](https://github.com/maxiducoli/WECompressor) and the companion tools — `SinSala-BIN`, `GraphicsTools`, `T_NAME-Maker`, `WEVagExtractor` | The `.BIN` container and `.RA` audio formats, and the LZSS codec of `WECompress.cpp`, ported to Python in `tools/pes2/lzss.py`. His condition is **non-commercial use, with credit to him as original author**; this project is non-commercial and carries the credit here. |
| **Author unknown** | `WECompress.cpp` itself | The codec predates CARP's suite and he maintained it rather than wrote it: its comments are in **Italian** (`"esci dal ciclo"`, `"numero di bytes da arretrare"`), the same language as `legacy/mfc/edDlg.cpp`, which points at the 2002–2003 Italian modding scene that produced `ed.exe`. Authorship is **not established**; the credit above is to the publisher, and this row exists so the gap is on the record rather than quietly filled. |
| **BAT_WE** | [Winning Eleven Image Manager](https://github.com/maxiducoli/Winning-Eleven-Image-Manager---by-BAT-2005-) (2005) | Nothing yet. Listed because the plan adopts its image-grid × palette-grid model when a browser is built, and the credit is owed at that point, not after. |

**What crossed over, and what did not.** What `lzss.py` implements is the
**format** — the flag byte read low bit first, the three command shapes, the
`0xFF` terminator — written fresh in Python from a reading of the C. Two
behaviours are reproduced deliberately because the data requires them, and both
are commented at the site: the signed `k3` of `while (k3-- >= 0)`, and the
`0xC0..0xFE` block-literal opcode that the CARP compressor leaves commented out
while its decompressor reads it. The match search is **not** his: the ring
buffer and hash chain were replaced by a three-byte-key index, which is legal
for this format because the encoder may pick any valid match. The consequence
was already measured in §5(c) of `PLAN-FEATURES` and holds here — recompressed
output is never byte-identical to Konami's, so the invariant asserted is
`decompress(compress(x)) == x` and never the reverse.

No file of his is redistributed here, and no game asset is.

If you are Maximiliano Ducoli, or hold rights to `WECompress.cpp`, and want
this use licensed, relicensed, or taken down, please open an issue.

## Lineage of the `.mcr` editor port (the `tools/mcr/` tree)

`tools/mcr/` is a fifth product in this repository: a Python port of
**Easy MCR**, Zetaprog's VB.NET/WinForms editor for the Winning Eleven 2002
save inside a PlayStation memory card. It edits a `.mcr`, never a CD image, and
shares no build and no code with `newWe2002`, `wte/` or the PES2 tooling.

| Author | Work | What was taken |
|---|---|---|
| **Zetaprog** | [Easy-Mcr-Winning-Eleven-2002-PS1](https://github.com/zetaprog/Easy-Mcr-Winning-Eleven-2002-PS1), SHA `30af1fe59cf96beee3b066f6cdfcb1b6f3df37cc`, five commits all dated 2026-05-27 | The semantics his sources add over our own reverse engineering: that `0x62A8`/`0x62B2`/`0x63D5` are X, Y and positional role of the ten outfield players; the label tables (hairstyles, positions, beards, boots, foot, the twenty roles, the formation presets); and the field names of the packed 12-byte attribute record. |

**There is no license, and the decision to port it anyway is the repository
owner's.** The upstream has no `LICENSE` file, no source header, `"license":
null` in the GitHub API, and a bare `<Copyright>Copyright ©  2023</Copyright>`
in `fifatomcr/fifatomcr.vbproj`. All rights reserved by default. The owner was
told this in as many words on 2026-09-07 and chose to port literally; §2 of
[`docs/PLAN-MCR-PY.md`](docs/PLAN-MCR-PY.md) records the decision and this
section records its consequence. The repository's position does not change: it
still has no `LICENSE`, for the reasons stated below.

**Why the method here differs from the `wte/` tree — and it does.** Above, in
the Lazarus section, transcribing decompiler output is refused *as a matter of
method*: Obocaman shipped a binary and no source, so his editor is treated as
something to **measure**, never to copy, and each of the 96 handlers got a
written specification before a line of Pascal existed. Here there is source,
and the owner decided to transcribe it. The two positions are not in conflict
and neither supersedes the other — a future reader needs both reasons side by
side so as not to conclude the rule quietly changed:

- against Obocaman's `.exe` there was **nothing to copy** short of decompiler
  output, which is a derivative work of a binary nobody licensed. Measuring was
  the only honest route, and it was also the cheaper one, because a
  specification is reviewable and decompiled C++ is not;
- against Zetaprog's repository there **is** readable source, and the thing it
  contributes is *semantics* — which byte means "role", what the twenty role
  labels are called. Semantics cannot be measured out of our fixture: the
  bytes are there either way, and only he says what they mean. Reimplementing
  from a paraphrase would be the same act with a thinner paper trail.

So the boundary is drawn per module instead of per project, and §3.4 of the
plan makes every module state which side of it each of its facts came from:
`card.py` and `layout.py` are ours, `attributes.py` is checked against
`src/core/Player.cpp` and takes only names from him, and `formation.py` and
`domains.py` are his labels, marked as third-party labels rather than
measurements.

**What does not enter this repository.** The VB sources are cloned to
`work/easy-mcr/` (gitignored, the same arrangement `we-team-editor/` and
`roms/` already have) at the SHA pinned above; only the port is versioned. Of
the upstream's 2,853 files and 476,688,515 bytes, 2,781 files and 471,937,179
bytes are build output, restored NuGet packages, an embedded WebView2 browser
cache, Visual Studio caches, and art — none of it save data. Named
specifically, because each is a thing someone might otherwise assume was
omitted by accident: `lite/fifatomcr/BD.accdb` (his private Access database of
appearances and faces, 2,543,616 B), the `.bmp` faces and `cancha.bmp` pitch
art, the two copies of the `fifatomcr_TemporaryKey.pfx` signing key, and the
`bin/`+`obj/` trees. Two kinds sit *inside* the remaining 72 files rather than
among those 2,781, and are just as unportable: the three copies of
`PlayerStatsSkills.dll` (11,776 B each), a third-party binary with no source,
and 8 `.ico`/`.jpg` art files that no discounted prefix or extension reaches.
Nor is his scraper of Sofifa, Transfermarkt, FMInside and PESMaster ported: it
is not save data, and §0 of the plan lists it under non-objectives.

If you are Zetaprog, and want this use licensed, relicensed, or taken down,
please open an issue.

## Copyright and license status

**This project has no license.**

Neither Francesco Moriero, thyddralisk, Obocaman, nor Zetaprog released their
work under any license:

- The 2002 `readme.txt` contains only a liability disclaimer — no grant of
  rights to copy, modify, or redistribute.
- `ed.rc` carries a bare `LegalCopyright "Copyright (C) 2002"` with no named
  holder.
- The upstream GitHub repository has no `LICENSE` file and no license metadata.
- No source file contains a license header.
- `we-team-editor.exe` ships with no license text of any kind, and no source.
  It is not in this repository for that reason.
- Zetaprog's Easy MCR repository has no `LICENSE`, reports `"license": null`
  through the GitHub API, and states only `<Copyright>Copyright ©  2023</Copyright>`
  in its `.vbproj`. Its sources are not in this repository either.

By default, that means the inherited code — and Obocaman's binary, which is
studied but not inherited, and Zetaprog's sources, which are read but not
redistributed — is **all rights reserved** by its original authors. No permission has been granted to anyone, including the
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
