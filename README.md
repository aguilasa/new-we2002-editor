# new-we2002-editor

Editor for **Winning Eleven 2002** (PlayStation) CD images — teams, players,
tactics, kits and flags, written straight into the `.bin`.

Being ported from its original Windows/MFC codebase to a cross-platform **Qt**
application. Linux first; Windows is a first-class target, not an afterthought.

> **Status: port in progress.** The Qt application does not exist yet. What is
> in this repository today is the original MFC source plus the groundwork for
> the port. See [PLAN-LINUX.md](PLAN-LINUX.md) for the full analysis and the
> phased plan.

## Credits and license

This is derivative work. The original tool is *"we2002 mania editor"* by
**Francesco Moriero** (2002); the SoFIFA import feature and the GitHub
publication are by **thyddralisk**
([thyddralisk/WE2002-editor-2.0](https://github.com/thyddralisk/WE2002-editor-2.0)).

**This project carries no license** — no prior author granted one, so the
inherited code remains all rights reserved. Read [NOTICE.md](NOTICE.md) before
using or redistributing it.

No game data is distributed here. Bring your own CD image.

## Running today

There is no Linux build yet. The prebuilt `Debug/ed.exe` (MFC, x86-64) runs
under Wine — this is also the reference oracle for the port's byte-comparison
tests:

```sh
WINEPREFIX=<dedicated prefix> wine64 Debug/ed.exe
```

Rebuilding the `.exe` requires MSVC with static MFC on Windows. MinGW and
Winelib cannot do it — neither ships MFC.

## Image compatibility

The editor reads and writes **raw MODE2/2352** PSX images. Its byte offsets are
hand-calibrated to skip sector headers, so the file must be the raw `.bin` — an
ISO9660-extracted file will not work. It does not recompute EDC/ECC on write.

| Release | Status |
|---|---|
| Winning Eleven 2002 – European Deluxe 2002-03 | Works. Reference image for tests. |
| World Soccer Winning Eleven 2002 (Japan) | Works. Shift-JIS content. |
| Pro Evolution Soccer 2 (Europe) | **Incompatible.** Layout diverges past ~2 MB; the editor will corrupt the image. |

Always work on a copy — writes happen in place.

## Repository layout

Original MFC sources sit at the repository root: `edDlg.cpp` is the main dialog
and holds most of the logic, `ed.rc` the six dialog resources, and
`giocatore`/`squadra`/`tattica` the domain structs (identifiers are in
Italian). [CLAUDE.md](CLAUDE.md) documents the architecture, the sector-aware
offset scheme, and the code patterns worth knowing before editing anything.
