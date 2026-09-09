---
id: CORR-MCR-023
title: "Correção: a MCR-TASK-16 conta quatro cartões de PES2 e cinco recusas, e são cinco e seis"
type: correção
category: dados
status: concluído
depends_on: []
---

# CORR-MCR-023: quatro/cinco no critério, cinco/seis na ferramenta

## Problema identificado

A MCR-TASK-16 é a **própria fonte de verdade** dela (§Critério de conclusão), e
dois números do critério não batem com o que o `check_card` faz sobre os oito
`.gme` de `mcr/`:

| onde | o que diz | o que a ferramenta mede |
|---|---|---|
| `16-conteiner-gme.md:67` (armadilha 1) | "**Quatro** dos oito `.gme` de `mcr/` são de PES2 … quem recusa **cinco** deles é o `check_card`" | 5 de PES2; 6 recusados |
| `16-conteiner-gme.md:99` (critério, item 2) | "**cinco deles** continuam sendo recusados por `check_card`" | **6** |
| `16-conteiner-gme.md:282` (Log, decisão do `convert`) | "**quatro dos oito** `.gme` são de PES2" | **5** |
| `tools/mcr/README.md:281` (escrito por esta task) | "**quatro dos oito** `.gme` versionados são de PES2" | **5** |

O erro é um só e se propaga: são **cinco** cartões de PES2, não quatro, e a
conta de recusas é `5 (PES2) + 1 (WE2002 sem option file) = 6`.

**O `mcr/README.md`, do commit anterior (`cea0c31`), já diz certo** — a tabela
dele atribui `17738`, `18432`, `22507` e `7110` à `(EnFrDe)` e `29818` à
`(EsIt)`, cinco ao todo, e marca o `34978` como o único sem `*-OPT`. O critério
da task contradiz um documento versionado do mesmo repositório, e a task
copiou o número errado para o `README` do `tools/mcr/`.

A camada está certa: o contêiner abre os oito, e quem recusa é o `check_card`,
um nível acima, exatamente como a task desenhou. **O defeito é a contagem.**

## Evidência

```
$ for f in mcr/*.gme; do out=$(python3 tools/mcr/cli.py info "$f" 2>&1);
    echo "$out" | grep -qi '^error' && echo "REFUSED $(basename $f)" \
                                    || echo "ACCEPTED $(basename $f)"; done
REFUSED  pro-evolution-soccer-2.17738.gme
REFUSED  pro-evolution-soccer-2.18432.gme
REFUSED  pro-evolution-soccer-2.22507.gme
REFUSED  pro-evolution-soccer-2.29818.gme
ACCEPTED pro-evolution-soccer-2.29939.gme
ACCEPTED pro-evolution-soccer-2.34218.gme
REFUSED  pro-evolution-soccer-2.34978.gme
REFUSED  pro-evolution-soccer-2.7110.gme
```

Seis recusas, duas aceitas. O mesmo pela porta do módulo, sem passar pelo CLI:

```
$ python3 - <<'PY'
import sys, glob; sys.path.insert(0, 'tools/mcr')
import mcrio, gme
n = 0
for p in sorted(glob.glob('mcr/*.gme')):
    try: mcrio.check_card(gme.read_card(p))
    except Exception: n += 1
print("refused:", n)
PY
refused: 6
```

E de que jogo é cada um, lido das entradas do diretório do cartão:

```
17738  PES2    BESLES-03946PES-{D2A,OPT}
18432  PES2    BESLES-03946PES-OPT
22507  PES2    BESLES-03946PES-{D2A,OPT}
29818  PES2    BESLES-03957PES-{D2A,OPT}
29939  WE2002  BISLPM-87056WEW-OPT
34218  WE2002  BISLPM-87056WEW-{D2A,D2B,D4A,OPT}
34978  WE2002  BISLPM-87056WEW-D0A          <- sem OPT
7110   PES2    BESLES-03946PES-{D2A,D4B,OPT,R0A}
PES2: 5   WE2002: 3
```

## Causa raiz

A contagem foi escrita na redação da task, de cabeça, em vez de sair do
`mcr/README.md` que a mesma task cita como fixture — e o Log e o
`tools/mcr/README.md` a copiaram sem remedir.

## Correção

### Arquivo: `docs/tasks/port-mcr/16-conteiner-gme.md`

Três lugares, e a conta explicitada onde ela é usada como critério:

- linha 67 (armadilha 1): "**Cinco** dos oito `.gme` de `mcr/` são de PES2
  (`…PES-OPT`) e um de WE2002 **não tem option file** (só `WEW-D0A`) … quem
  recusa **seis** deles é o `check_card`";
- linha 99 (critério): "e **seis deles continuam sendo recusados** por
  `check_card` — os cinco de PES2 e o `34978`, que não tem `WEW-OPT`";
- linha 282 (Log): "**cinco dos oito** `.gme` são de PES2 e um não tem option
  file".

### Arquivo: `tools/mcr/README.md`

Linha 281: "**cinco dos oito** `.gme` versionados são de PES2 e um não tem
option file".

### E o que impede a próxima

O número vive em prosa em três arquivos e é medível em uma linha. O barato é o
`gme.py --check` **imprimir** quantos dos contêineres carregam um save que o
`check_card` aceita — na forma que a [CORR-MCR-017](/docs/tasks/port-mcr/CORR-MCR-017.md)
já escolheu para o `controls.py` — e a prosa apontar para a saída. Fica a
critério de quem executar: o mínimo desta CORR são os quatro números.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/port-mcr/16-conteiner-gme.md` | modificar |
| `tools/mcr/README.md` | modificar |

## Verificação

- [x] `grep -rn "quatro dos oito" docs/tasks/port-mcr tools/mcr` sai vazio
- [x] `grep -n "cinco deles" docs/tasks/port-mcr/16-conteiner-gme.md` sai vazio
- [x] o número escrito bate com o laço de `cli.py info` acima: **6 recusados,
      2 aceitos**
- [x] `python3 tools/mcr/gme.py --check` continua `8/8 containers round-trip
      byte-identical`
- [x] `python3 tools/mcr/selftest.py` e `python3 tools/mcr/controls.py` verdes
- [x] `python3 tools/check_tasks.py` verde
- [x] `mcr/` e `roms/` intocadas

## Log de Execução

**Executado em:** 2026-09-09

**Resumo do que foi feito:**

Os quatro números, com a **derivação à vista** em vez do total solto: onde a
conta é usada como critério, ela agora diz de onde vem — "os cinco de PES2 mais
o `34978`" — e aponta para a tabela do `mcr/README.md`, que é quem separa os
oito por jogo. Um número derivado errado se denuncia na leitura; um total solto,
não. Sobram dois aceitos, o `29939` e o `34218`, e isso passou a estar escrito.

**Problemas encontrados:**

**A segunda metade da CORR — "o que impede a próxima" — foi recusada, com
motivo.** Ela propunha o `gme.py --check` imprimir quantos contêineres trazem um
save que o `check_card` aceita, na escolha que a
[CORR-MCR-017](/docs/tasks/port-mcr/CORR-MCR-017.md) fez para o `controls.py`.
Não dá, e não é detalhe de implementação: `mcrio.py` importa `gme.py`, então
`gme.py` chamar `check_card` fecha um ciclo de import — e, pior, faria o módulo
do **contêiner** saber o que é um save do WE2002, que é exatamente a separação
de camadas que a MCR-TASK-16 defende na armadilha 1 ("misturar as duas camadas
troca 'não é um cartão' por 'não é o cartão que eu queria'"). O lugar onde a
conta caberia é o `cli.py`, que importa os dois; não vale um número a mais em
código vivo para uma frase de prosa. A defesa que ficou é a derivação escrita.

Nenhum outro lugar do repositório repetia a contagem: a varredura por
`"dos oito"` em `docs/`, `.claude/`, `CLAUDE.md`, `tools/mcr/` e `mcr/` só
devolve as linhas certas (três de cabeçalho zerado, cinco assinados, sete com
`*-OPT`) e a transcrição do defeito dentro do próprio
`correcoes-progresso.md`, que é evidência e não se reescreve.

**Medições:**

| gate | número |
|---|---|
| `mcrio.check_card` sobre os oito | **6 recusados, 2 aceitos** |
| `cli.py info` sobre os oito | idem, seis `error:` e dois relatórios |
| entradas de diretório, por jogo | **5 PES2, 3 WE2002** (um sem `WEW-OPT`) |
| `gme.py --check` | `8/8 containers round-trip byte-identical` |
| `check_tasks.py` | `102 task(s), ok` |
| `grep -rn "quatro dos oito" docs/tasks/port-mcr tools/mcr` | vazio |
| `mcr/` e `roms/` | intocadas |

**Arquivos criados/modificados:**

- `docs/tasks/port-mcr/16-conteiner-gme.md` — as três linhas, com a derivação
- `tools/mcr/README.md` — a linha do `convert`, apontando para o `mcr/README.md`
