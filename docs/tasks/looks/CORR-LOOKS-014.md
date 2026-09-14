---
id: CORR-LOOKS-014
title: "Correção: o título da LOOKS-TASK-05 ainda diz onze seções; a tabela do progresso já diz vinte"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-LOOKS-014: o título da task e o da tabela discordam

## Problema identificado

A [`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md) mediu que o
`EDT_MOD.BIN` tem vinte seções, e a correção atualizou o título da
LOOKS-TASK-05 **na tabela do `progresso.md`** e não **no frontmatter do arquivo
da task**. Os dois discordam:

```
docs/tasks/looks/05-arquivos-de-modelo.md:3
  title: "`modelfile.py` — as 106 seções do `MODEL.BIN` e as 11 do `EDT_MOD.BIN`"

docs/tasks/looks/progresso.md:41
  | LOOKS-TASK-05 | `modelfile.py` — as 106 seções do `MODEL.BIN` e as 20 do `EDT_MOD.BIN` | ...
```

O corpo da task está certo — o critério pede vinte, o Log mede vinte, e o
`--check-image` afirma vinte. Sobrou o título, que é a primeira linha que
alguém lê ao abrir o arquivo, e é o número **que a correção derrubou**.

O `check_tasks.py` não pega: ele confere `id`, `status`, `depends_on`,
`fonte_de_verdade`, o link na tabela e a fase contra o perfil — não o título,
que não é campo estrutural. Verde, portanto, com os dois textos divergindo.

## Evidência

```
$ grep -n "^title:" docs/tasks/looks/05-arquivos-de-modelo.md
3:title: "`modelfile.py` — as 106 seções do `MODEL.BIN` e as 11 do `EDT_MOD.BIN`"

$ grep -n "LOOKS-TASK-05" docs/tasks/looks/progresso.md | head -1
41:| [LOOKS-TASK-05](...) | `modelfile.py` — as 106 seções do `MODEL.BIN` e as 20 do `EDT_MOD.BIN` | ...

$ python tools/check_tasks.py
check_tasks: 123 task(s), ok
```

E o número que vale, medido nesta revisão:

```
/BIN/EDT_MOD.BIN from 216: 20 sections, 1218 vertices, 1074 primitives, end 36072 = EOF
```

## Causa raiz

A correção alterou o título na tabela e não no frontmatter, que é o outro lugar
onde ele mora.

## Correção

### Arquivo: `docs/tasks/looks/05-arquivos-de-modelo.md`

O `title:` do frontmatter passa a dizer **20**, igual ao da tabela. O `#` do
corpo (*"Os dois arquivos de modelo"*) não cita número e fica como está.

Vale conferir de uma vez os outros dezenove: título de task e célula da tabela
têm de bater sempre, e este é o primeiro caso em que se soube que podem
divergir.

```bash
python - <<'PY'
import glob, re, io
prog = io.open("docs/tasks/looks/progresso.md", encoding="utf-8").read()
for path in sorted(glob.glob("docs/tasks/looks/[0-9][0-9]-*.md")):
    head = io.open(path, encoding="utf-8").read()
    title = re.search(r'^title:\s*"(.*)"', head, re.M).group(1)
    ident = re.search(r'^id:\s*(\S+)', head, re.M).group(1)
    row = [l for l in prog.splitlines() if "|" in l and ident + "]" in l]
    if row and title not in row[0]:
        print("DIVERGE", ident)
PY
```

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/looks/05-arquivos-de-modelo.md` | modificar |

## Verificação

- [ ] o `title:` do frontmatter e a célula da tabela dizem a mesma coisa
- [ ] o laço acima não imprime `DIVERGE` para nenhuma das vinte tasks
- [ ] `python tools/check_tasks.py` verde
- [ ] a conferência de links do `.claude/rules/links.md` sai vazia

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
