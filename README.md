# new-we2002-editor

Editor for **Winning Eleven 2002** (PlayStation) CD images — teams, players,
tactics, kits and flags, written straight into the `.bin`.

A port of the original Windows/MFC tool to a cross-platform **Qt 6**
application. Linux first; Windows is a first-class target, not an afterthought.

> **Status: it works on Linux and on Windows.** Both are verified byte for byte
> against the original `ed.exe` — under Wine on Linux, natively on Windows. The
> MSVC build writes exactly the bytes the GCC build writes, on both test images.
>
> See [docs/PLAN-LINUX.md](docs/PLAN-LINUX.md) for the phase-by-phase plan,
> [docs/PLAN-WINDOWS.md](docs/PLAN-WINDOWS.md) for how the Windows parity was
> proved, and [CLAUDE.md](CLAUDE.md) for the architecture.

## Building

Needs a C++20 compiler, CMake 3.21+, Qt 6.3+ and libcurl.

```sh
sudo apt install build-essential cmake qt6-base-dev qt6-base-dev-tools \
                 libcurl4-openssl-dev
cmake --preset debug
cmake --build --preset debug
ctest --preset debug
```

On Windows, from an *x64 Native Tools Command Prompt for VS 2022*, with Qt in
`C:\Qt\6.5.3\msvc2019_64` and vcpkg in `C:\vcpkg`:

```bat
vcpkg install curl:x64-windows
cmake --preset windows-release
cmake --build --preset windows-release
ctest --preset windows-release
```

The Linux presets refuse to configure on Windows on purpose: without an
explicit generator CMake picks the Visual Studio one, which is multi-config and
ignores `CMAKE_BUILD_TYPE` — asking for Release would quietly build Debug. The
`windows-*` presets use Ninja. For Qt or vcpkg somewhere else, override with
`-DCMAKE_PREFIX_PATH=` / `-DCMAKE_TOOLCHAIN_FILE=`.

Without Qt 6 the core library and its tests still build; only the GUI is
skipped. That is deliberate — the byte-comparison tests have to run headless.

### The Makefile

There is a `Makefile` at the root. It is a thin wrapper over the presets, not a
second build system, and it is optional — everything below has a plain CMake
equivalent. `make` with no target prints the list.

| Target | What it does |
|---|---|
| `make build` | configure if needed, then build |
| `make run` | build, copy the image to `work/`, open the editor on the **copy** |
| `make run-jp` | the same with the Japanese image |
| `make run-99` | `run` on the local `Xvfb :99`, sorting out that server's `XAUTHORITY` |
| `make oracle` | open the **original Windows `ed.exe`** under Wine (Bottles runner) |
| `make oracle-99` | the same on `:99` |
| `make fresh` | throw the working copies away and re-copy from the original |
| `make test` | unit checks (`ctest` without the byte-comparison tests) |
| `make test-release` | the same in Release, where `_FORTIFY_SOURCE` is active |
| `make golden`, `make golden-gui` | the byte-comparison tests, with `WE2002_GOLDEN_IMAGE` filled in |
| `make gen`, `make gen-check` | re-run the code generators / check the tree against them |
| `make install` | Release build, then install into `PREFIX` (default `~/.local`) |
| `make clean`, `make distclean` | current preset's artefacts / every `build*/` and `work/` |

`PRESET=debug|release|asan|ubsan` picks the preset and the matching build
directory; `IMAGE=` picks the CD image; `JOBS=` the parallelism. So
`make run PRESET=release IMAGE=roms/japanese-shift-jis.bin` does what it says.

The point of `make run` is the copy. The editor writes in place, so opening an
original by mistake edits it; the target always copies to `work/` first and
never touches the source. The copy survives between runs, so edits persist —
`make fresh` starts over.

#### Running the original editor: `make oracle`

`make oracle` opens `Debug/ed.exe` — the 2002 Windows/MFC binary this project
ports — under Wine, so its behaviour can be compared against the port screen by
screen. It is the same binary the byte-comparison tests measure against.

```sh
make oracle                                    # inherits DISPLAY
make oracle-99                                 # on the Xvfb :99
make oracle IMAGE=roms/japanese-shift-jis.bin  # any image
```

It runs on the Wine runner that ships with Bottles. Override the path with
`WINE_BIN=<directory containing wine64>` for a different runner or a system
Wine.

Three things the target handles that a bare `wine ed.exe` does not:

- **A dedicated Wine prefix**, kept in `work/wineprefix` and created once. Never
  an existing bottle: `ed.cpp` calls `COleObjectFactory::UpdateRegistryAll()`,
  which writes to the prefix's registry.
- **Its own copy of the image**, separate from the one `make run` uses, so the
  two editors never fight over the same file.
- **The file dialog.** `ed.exe` takes no argument — it opens a `CFileDialog` at
  startup, whose default filter is the literal name `we2002.bin`. The copy is
  named exactly that, and the target symlinks it into `Debug/`, which is where
  the dialog opens. So the image is in the first screen, already selectable.

`make run-99` is the equivalent for the port: it runs the Qt editor on the local
`Xvfb :99` used for visual checks, resolving that server's `XAUTHORITY` on its
own.

Neither target has anything to do with the port's own Windows build. That one is
built with MSVC on Windows (`--preset windows-release`) and run natively; there
is no `make` target that runs `newWe2002.exe` under Wine.

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
`make run` handles that for you: it copies the image into `work/` and opens the
copy, so the file in `roms/` is never the one being edited.

An image that is not exactly 474,431,328 bytes long draws a warning and loads
anyway — the original behaves the same way, and dumps of the right layout but a
different length do work.

## Installing

```sh
cmake --preset release
cmake --build --preset release
cmake --install build-release --prefix ~/.local
```

Or `make install PREFIX=~/.local`, which runs those three.

That gives you `bin/newWe2002`, the runtime data files under `share/newWe2002/`,
a desktop entry, the icon in seven sizes and the AppStream metadata. The binary
finds its data files relative to itself, so the installed tree can be moved.

`newWe2002` names the *product*: the executable, the data directory,
`share/doc/`, the icon and the AppStream id `io.github.aguilasa.newWe2002`. The
C++ namespace, the `we2002_core` library and the `WE2002_*` build and
environment variables stay `we2002`, because they name the game and its image
format rather than this editor.

There is no distro package or AppImage yet.

On Windows the same `install` rules produce the portable tree; `windeployqt`
fills in the Qt libraries, and the rest is copied beside the executable:

```bat
cmake --install build-windows-release --prefix dist\newWe2002
C:\Qt\6.5.3\msvc2019_64\bin\windeployqt.exe dist\newWe2002\bin\newWe2002.exe
copy data\defaultlook.txt dist\newWe2002\bin\
copy "data\SOFIFA attributes.txt" dist\newWe2002\bin\
copy "data\WE attributes conversion rules.txt" dist\newWe2002\bin\
copy C:\vcpkg\installed\x64-windows\bin\libcurl.dll dist\newWe2002\bin\
copy C:\vcpkg\installed\x64-windows\bin\z.dll dist\newWe2002\bin\
```

Copying the `.txt` files next to the `.exe` is what makes the tree immune to
being rearranged: that directory is the first place the editor looks. The
MSVC runtime (`msvcp140*.dll`, `vcruntime140*.dll`) has to go in too, from
`VC\Redist\MSVC\<version>\x64\Microsoft.VC143.CRT` — `windeployqt
--compiler-runtime` only finds them with the Visual Studio environment loaded.
And the curl licence ships with the binary, as [NOTICE.md](NOTICE.md) requires;
vcpkg leaves it in `installed\x64-windows\share\curl\copyright`.

Do **not** copy `data/naz.txt`. Nothing reads it — it is a C array the original
author pasted into the tree, kept as history.

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
and kit colours with their `.b2002`/`.m2002` import and export, and the `.t2002`
formation files.

Not ported: the `.2002` team and `.tt2002` total import/export. Their buttons
are commented out in `ed.rc`, so they were already dead in the binary users
received, and the file format is a raw MSVC struct dump that cannot be
reproduced portably.

**The SoFIFA import is ported but switched off.** It was the fork's own
addition, not part of the 2002 editor, and its scraper targets the site as it
was in 2015, so it will not match it today. The buttons, the 23 URL boxes and
the per-player "Import from URL" are greyed out until the port's parity with the
original has been checked screen by screen. The code is still compiled; the
switch is `app::SOFIFA_ENABLED` in `src/app/Features.hpp`. The `<image>_url.txt`
sidecar is still read and written, exactly as the original did.

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
Makefile      convenience wrapper over the CMake presets
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
