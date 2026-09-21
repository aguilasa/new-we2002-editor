#!/usr/bin/env python3
"""Confere as convencoes das tasks de `docs/tasks/` -- hoje, pelo Rite.

Desde a migracao para o plugin Rite (configuracao em `rite.toml`), quem confere
as convencoes que este script conferia a mao -- fonte de verdade por task,
estado no frontmatter, links, `depends_on` dentro do ciclo, entrada da fase no
perfil do ciclo -- e o `rite.py check`. O arquivo fica para o `ctest -R tasks`
manter nome e sentido: ele so acha o CLI do Rite e o roda sobre todos os
ciclos, arquivados inclusive.

O CLI e procurado em `RITE_PY`, depois no `installPath` do plugin em
`~/.claude/plugins/installed_plugins.json` e, por fim, no cache de plugins
(`cache/<marketplace>/rite/<versao>/bin/rite.py`). O clone do marketplace
(`marketplaces/rite/`) fica de fora: segue o `main` do Rite, nao a versao
instalada.
Sem ele o teste e pulado (saida 77, `SKIP_RETURN_CODE` em
`tests/CMakeLists.txt`): o plugin e ferramenta da maquina de quem desenvolve,
nao parte deste repositorio.
"""

from __future__ import annotations

import glob
import json
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
    plugins = Path.home() / ".claude" / "plugins"
    try:
        installed = json.loads((plugins / "installed_plugins.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        installed = {}
    for key, entries in installed.get("plugins", {}).items():
        if key.split("@")[0] != "rite":
            continue
        for entry in entries:
            cli = Path(entry.get("installPath", "")) / "bin" / "rite.py"
            if cli.is_file():
                return str(cli)
    found = sorted(glob.glob(str(plugins / "cache" / "*" / "rite" / "*" / "bin" / "rite.py")),
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
