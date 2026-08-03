# new-we2002-editor

Editor for **Winning Eleven 2002** (PlayStation) CD images — teams, players,
tactics, kits and flags, written straight into the `.bin`.

A port of the original Windows/MFC tool to a cross-platform **Qt 6**
application. Linux first; Windows is a first-class target, not an afterthought.

> **Status: the Linux application works.** It is verified byte for byte against
> the original `ed.exe` running under Wine — both through the core and through
> the Qt window. Windows is not built yet.
>
> See [docs/PLAN-LINUX.md](docs/PLAN-LINUX.md) for the phase-by-phase plan and
> [CLAUDE.md](CLAUDE.md) for the architecture.

## Building

Needs a C++20 compiler, CMake 3.21+, Qt 6.3+ and libcurl.

```sh
sudo apt install build-essential cmake qt6-base-dev qt6-base-dev-tools \
                 libcurl4-openssl-dev
cmake --preset debug
cmake --build --preset debug
ctest --preset debug
```

Without Qt 6 the core library and its tests still build; only the GUI is
skipped. That is deliberate — the byte-comparison tests have to run headless.

The unit checks pass with no image. Two of them, and the byte-comparison tests,
want a real one; point `WE2002_TEST_IMAGE` / `WE2002_GOLDEN_IMAGE` at a **copy**
of a supported release. In this working tree those images live in `roms/` as
`golden-european-deluxe.bin` and `japanese-shift-jis.bin` — named for what they
test, not for the dump they came from. The directory is deliberately not
versioned; ~780 MB of CD dumps do not belong in git.

## Running

```sh
./build/src/app/newWe2002 [image.bin]
```

The path is optional; without it the editor asks for one, as the original did.

**Always work on a copy.** Writes happen in place, and each image is ~474 MB.

An image that is not exactly 474,431,328 bytes long draws a warning and loads
anyway — the original behaves the same way, and dumps of the right layout but a
different length do work.

## Installing

```sh
cmake --preset release
cmake --build --preset release
cmake --install build-release --prefix ~/.local
```

That gives you `bin/newWe2002`, the runtime data files under `share/newWe2002/`,
a desktop entry, the icon in seven sizes and the AppStream metadata. The binary
finds its data files relative to itself, so the installed tree can be moved.

`newWe2002` names the *product*: the executable, the data directory,
`share/doc/`, the icon and the AppStream id `io.github.aguilasa.newWe2002`. The
C++ namespace, the `we2002_core` library and the `WE2002_*` build and
environment variables stay `we2002`, because they name the game and its image
format rather than this editor.

There is no distro package or AppImage yet.

## Image compatibility

The editor reads and writes **raw MODE2/2352** PSX images. Its byte offsets are
hand-calibrated to skip sector headers, so the file must be the raw `.bin` — an
ISO9660-extracted file will not work. It does not recompute EDC/ECC on write,
which is the original's behaviour and is preserved on purpose.

| Release | Status |
|---|---|
| Winning Eleven 2002 – European Deluxe 2002-03 | Works. Reference image for tests. |
| World Soccer Winning Eleven 2002 (Japan) | Works. Shift-JIS content. |
| Pro Evolution Soccer 2 (Europe) | **Incompatible.** Layout diverges past ~2 MB; the editor will corrupt the image. |

## What is and is not ported

Everything the original's dialogs expose works: the six team-name slots, the
strength bars, set-piece takers, squad numbers, the tactics pitch and its
sixteen preset formations, per-player attributes, player swaps and links, flag
and kit colours with their `.b2002`/`.m2002` import and export, the `.t2002`
formation files, and the SoFIFA import.

Not ported: the `.2002` team and `.tt2002` total import/export. Their buttons
are commented out in `ed.rc`, so they were already dead in the binary users
received, and the file format is a raw MSVC struct dump that cannot be
reproduced portably.

The SoFIFA scraper targets the site as it was in 2015 and will not match it
today. It is ported as it was; fixing it is a separate job.

## Credits and license

This is derivative work. The original tool is *"we2002 mania editor"* by
**Francesco Moriero** (2002); the SoFIFA import feature and the GitHub
publication are by **thyddralisk**
([thyddralisk/WE2002-editor-2.0](https://github.com/thyddralisk/WE2002-editor-2.0)).

**This project carries no license** — no prior author granted one, so the
inherited code remains all rights reserved. Read [NOTICE.md](NOTICE.md) before
using or redistributing it.

No game data is distributed here. Bring your own CD image.

## Repository layout

```
src/core/     we2002_core -- the CD image format and all the logic. No Qt.
src/app/      the Qt application. No parsing, no file format.
src/app/ui/   the six forms, generated from legacy/mfc/ed.rc
tests/        unit checks plus the byte-comparison tests against ed.exe
tools/        the generators, and the scripts that drive both editors
legacy/mfc/   the original MFC source -- reference, does not compile
data/         files read at run time
packaging/    desktop entry and AppStream metadata
```

`Debug/ed.exe` is the original binary, kept because it is the oracle the
byte-comparison tests measure against. Rebuilding it needs MSVC with static MFC
on Windows; MinGW and Winelib cannot, since neither ships MFC.
