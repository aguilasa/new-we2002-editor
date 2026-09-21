---
id: CORR-LOOKS-014
title: "Correção: o título da LOOKS-TASK-05 ainda diz onze seções; a tabela do progresso já diz vinte"
type: correção
category: processo
status: done
depends_on: []
origin: LOOKS-TASK-05
severity: low
done_on: 2026-09-14
done_commit: 03ef739
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

- [x] o `title:` do frontmatter e a célula da tabela dizem a mesma coisa
- [x] o laço acima não imprime `DIVERGE` para nenhuma das vinte tasks
- [x] `python tools/check_tasks.py` verde
- [x] a conferência de links do `.claude/rules/links.md` sai vazia

## Log de Execução

**Executado em:** 2026-09-14

**Resumo do que foi feito:**

O `title:` do frontmatter da
[`LOOKS-TASK-05`](/docs/tasks/looks/05-arquivos-de-modelo.md) passou a dizer
**20**, igual ao da tabela do `progresso.md`. O `#` do corpo não cita número e
ficou como está.

O laço da CORR, sobre as vinte tasks do ciclo:

```
$ python - <<'PY'   (o laço desta CORR)
conferidas: 20
```

Nenhum `DIVERGE`. `check_tasks: 123 task(s), ok` e a conferência de links vazia.

**Problemas encontrados:**

**Uma guarda permanente para isto seria errada, e foi medido antes de não a
escrever.** O impulso é óbvio — a regra deste repositório é que regra que só
vive na prosa não impede ninguém, e foi assim que as
[`CORR-LOOKS-005`](/docs/tasks/looks/CORR-LOOKS-005.md) e
[`CORR-LOOKS-009`](/docs/tasks/looks/CORR-LOOKS-009.md) fecharam. Aqui não
serve. Rodando o laço sobre **todos** os ciclos:

```
tasks com title+linha: 147   divergencias: 70
  docs/tasks           13  (PES2)
  docs/tasks/port-mcr   7  (MCR)
  docs/tasks/concluidos 37 (WTE, arquivado)
```

E as 70 não são erro: são **abreviações deliberadas**, a célula da tabela
resumindo o título.

```
PES2-TASK-01 task  : Ferramental das fases 3 e 4 — numpy e desmontador MIPS
PES2-TASK-01 tabela: `numpy` e desmontador MIPS — decisão do dono da máquina

MCR-TASK-06  task  : `attributes.py` — o codec de 12 bytes, contra `Player::Decode/Encode`
MCR-TASK-06  tabela: `attributes.py` — `Player::Decode/Encode`
```

Pôr isso no `tools/check_tasks.py` deixaria o alvo `tasks` — **gate global,
compartilhado pelos quatro ciclos** — vermelho em 70 linhas que estão certas. O
invariante "o título da task é substring da célula" simplesmente não vale neste
repositório; o que valia aqui era outra coisa: a célula dizia **20** e o título
dizia **11**, que é contradição de número medido, não resumo. O ciclo `looks`
é o único em que os vinte batem ao pé da letra, e fica assim.

Fica registrado para não se re-litigar: **não é descuido não haver guarda, é
medição.**

**Arquivos criados/modificados:**

- `docs/tasks/looks/05-arquivos-de-modelo.md` — o `title:`
- `docs/tasks/looks/CORR-LOOKS-014.md` — este Log
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
