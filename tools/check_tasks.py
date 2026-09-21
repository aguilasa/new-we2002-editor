#!/usr/bin/env python3
"""Confere as convencoes das tasks de `docs/tasks/` -- hoje, pelo Rite.

Desde a migracao para o plugin Rite (configuracao em `rite.toml`), quem confere
as convencoes que este script conferia a mao -- fonte de verdade por task,
estado no frontmatter, links, `depends_on` dentro do ciclo, entrada da fase no
perfil do ciclo -- e o `rite.py check`. O arquivo fica para o `ctest -R tasks`
manter nome e sentido: ele so acha o CLI do Rite e o roda sobre todos os
ciclos, arquivados inclusive.

O CLI e procurado em `RITE_PY` e depois no cache de plugins do Claude Code.
Sem ele o teste e pulado (saida 77, `SKIP_RETURN_CODE` em
`tests/CMakeLists.txt`): o plugin e ferramenta da maquina de quem desenvolve,
nao parte deste repositorio.
"""

from __future__ import annotations

import glob
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = 77


def find_rite() -> str | None:
    explicit = os.environ.get("RITE_PY")
    if explicit and Path(explicit).is_file():
        return explicit
    cache = Path.home() / ".claude" / "plugins"
    found = sorted(glob.glob(str(cache / "**" / "rite" / "bin" / "rite.py"), recursive=True),
                   key=lambda p: Path(p).stat().st_mtime, reverse=True)
    return found[0] if found else None


def main() -> int:
    rite = find_rite()
    if not rite:
        print("check_tasks: CLI do Rite nao encontrado (instale o plugin ou defina RITE_PY); pulado")
        return SKIP
    return subprocess.call([sys.executable, rite, "check", "--all", "--include-archived",
                            "--root", str(ROOT)])


if __name__ == "__main__":
    sys.exit(main())
