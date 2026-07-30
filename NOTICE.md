# NOTICE

## Lineage

This project descends from a chain of prior work. Credit where it is due:

| Author | Year | Contribution |
|---|---|---|
| **Francesco Moriero** | 2002 | Original tool, *"we2002 mania editor 1.2 English (final version)"*. Wrote the MFC application and reverse-engineered the WE2002 CD image layout — the ~69 hardcoded byte offsets that make this program possible. See [`readme.txt`](readme.txt) for the original release notes and the community credits (cicco, walxer, honome_wec, luha, haplo, adesy, actaruss, alex1, `#winningmania`, walxer's forum). |
| **thyddralisk** | 2015 | Published the sources on GitHub at <https://github.com/thyddralisk/WE2002-editor-2.0> and added the SoFIFA database import feature. |
| **aguilasa** | 2026 | Cross-platform Qt port (in progress). |

## Copyright and license status

**This project has no license.**

Neither Francesco Moriero nor thyddralisk released their work under any
license:

- The 2002 `readme.txt` contains only a liability disclaimer — no grant of
  rights to copy, modify, or redistribute.
- `ed.rc` carries a bare `LegalCopyright "Copyright (C) 2002"` with no named
  holder.
- The upstream GitHub repository has no `LICENSE` file and no license metadata.
- No source file contains a license header.

By default, that means the inherited code is **all rights reserved** by its
original authors. No permission has been granted to anyone, including the
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
