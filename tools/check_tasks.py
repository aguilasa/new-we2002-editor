#!/usr/bin/env python3
"""Confere as convencoes de `.claude/rules/tasks.md` nas tasks de `docs/tasks/`.

Quatro coisas, e a razao de cada uma esta na regra:

1. toda task tem `fonte_de_verdade` no frontmatter, apontando para arquivo que
   existe -- task que nao diz contra o que se mede nao e executavel;
2. `status:` do frontmatter bate com o simbolo na tabela do `progresso.md` --
   os prompts leem os dois, e divergencia faz o `/executar` escolher uma task
   bloqueada;
3. toda task tem linha COM LINK no `progresso.md` -- e assim que o prompt acha
   o arquivo, desde que o mapeamento `ID -> arquivo` saiu dos prompts;
4. `depends_on` so cita IDs que existem.

Sai com 1 e imprime o que falhou. Sem argumento, confere tudo.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TASKS = RAIZ / "docs" / "tasks"
PROGRESSO = TASKS / "progresso.md"

SIMBOLO = {
    "pendente": "⬜ Pendente",
    "bloqueado": "❌ Bloqueado",
    "concluído": "✅ Concluído",
    "em andamento": "🔄 Em andamento",
    "pulado": "⏭️ Pulado",
}


def frontmatter(texto: str) -> dict[str, str]:
    if not texto.startswith("---\n"):
        return {}
    fim = texto.index("\n---", 4)
    campos = {}
    for linha in texto[4:fim].splitlines():
        if ":" in linha and not linha.startswith(" "):
            chave, _, valor = linha.partition(":")
            campos[chave.strip()] = valor.strip().strip('"')
    return campos


def main() -> int:
    progresso = PROGRESSO.read_text(encoding="utf-8")
    arquivos = sorted(
        p for p in TASKS.glob("*.md")
        if not p.name.startswith("CORR-") and p.name not in
        ("progresso.md", "correcoes-progresso.md")
    )
    if not arquivos:
        print("check_tasks: nenhuma task encontrada", file=sys.stderr)
        return 1

    ids = {frontmatter(p.read_text(encoding="utf-8")).get("id") for p in arquivos}
    erros: list[str] = []

    for p in arquivos:
        texto = p.read_text(encoding="utf-8")
        fm = frontmatter(texto)
        nome = p.name
        tid = fm.get("id")
        if not tid:
            erros.append(f"{nome}: sem `id` no frontmatter")
            continue

        # 1. fonte_de_verdade
        fonte = fm.get("fonte_de_verdade")
        if not fonte:
            erros.append(f"{nome}: sem `fonte_de_verdade` -- ver .claude/rules/tasks.md")
        else:
            m = re.match(r"(/docs/[A-Za-z0-9._/-]+\.md)", fonte)
            if not m:
                erros.append(f"{nome}: `fonte_de_verdade` nao comeca com caminho /docs/...: {fonte!r}")
            elif not (RAIZ / m.group(1).lstrip("/")).is_file():
                erros.append(f"{nome}: `fonte_de_verdade` aponta para arquivo inexistente: {m.group(1)}")

        # 3. linha com link no progresso
        if f"({nome})" not in progresso and f"/docs/tasks/{nome})" not in progresso:
            erros.append(f"{nome}: sem linha COM LINK no progresso.md")
            linha = None
        else:
            linha = next((l for l in progresso.splitlines()
                          if l.lstrip().startswith("|") and
                          (f"({nome})" in l or f"/docs/tasks/{nome})" in l)), None)

        # 2. status x simbolo
        status = (fm.get("status") or "").lower()
        if status not in SIMBOLO:
            erros.append(f"{nome}: `status: {status}` desconhecido")
        elif linha and SIMBOLO[status] not in linha:
            atual = next((s for s in SIMBOLO.values() if s in linha), "nenhum")
            erros.append(f"{nome}: frontmatter diz `{status}` e a tabela diz `{atual}`")

        # 4. depends_on
        for dep in re.findall(r'"([A-Z][A-Z-]*-TASK-\d+)"', fm.get("depends_on", "")):
            if dep not in ids:
                erros.append(f"{nome}: `depends_on` cita {dep}, que nao existe")

    if erros:
        print(f"check_tasks: {len(erros)} problema(s) em {len(arquivos)} task(s):",
              file=sys.stderr)
        for e in erros:
            print(f"  {e}", file=sys.stderr)
        return 1

    print(f"check_tasks: {len(arquivos)} task(s), ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
