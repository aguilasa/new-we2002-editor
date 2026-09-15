---
id: LOOKS-TASK-10
title: "A lista de CLUTs do `DAT2D.BIN` que o `bin_archive.py` não acha"
type: engenharia-reversa
category: textura
phase: 3
depends_on: ["LOOKS-TASK-08"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.7"
status: concluído
---

# LOOKS-TASK-10: A lista de paletas que falta

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.7.
- Medido: `bin_archive.py ls` sobre o `DAT2D.BIN` japonês responde
  **`23 image(s), 0 clut(s)`**. As imagens saem inteiras; as paletas, não.
- Que a lista existe, a tabela do CARP diz: as paletas começam em **65.892**,
  logo depois do fim da lista de imagens (65.508 + 23×16 = 65.876).
- **Ler `0 clut(s)` como "não tem paleta" é o erro** — armadilha 6 do plano.
- **Só no disco japonês.** O `DAT2D.BIN` difere no inglês (§1.3).
- **A geometria amostra nas duas profundidades, e isso é desta task.** Medido em
  2026-09-15 ([`CORR-LOOKS-018`](/docs/tasks/looks/CORR-LOOKS-018.md)): 1.802
  das 2.841 primitivas pedem CLUT de **4 bits** e **1.039 pedem 8**, pela
  palavra de página que o `Primitive.tpage_depth` lê. São **16 entradas (32 B)
  contra 256 (512 B)** — uma varredura que assuma uma largura lê um dezesseis
  avos da paleta que existe, ou acha paleta onde não há, e **não diz nada**.

---

## Objetivo

Achar e decodificar a segunda lista, e decidir se o conserto vai em
`tools/looks/texture.py` ou no próprio `tools/pes2/bin_archive.py`.

---

## Critério de conclusão

- [x] A lista de CLUTs é localizada por **marcador**, no método que o
      `bin_archive.entries()` já usa, e não por offset constante.
- [x] A contagem de paletas é medida e registrada, com as de 256 e as de 16
      cores separadas — e o varredor **acomoda as duas larguras**, dizendo
      qual delas encontrou em cada achado. Assumir uma é o erro silencioso
      desta fase, e a geometria já provou que as duas ocorrem.
- [x] As **quatro "Pieles"** (65.892 / 66.404 / 66.916 / 67.428) e o bloco de
      **"Botines"** (67.940) que o CARP nomeia são conferidos contra o disco —
      opinião de terceiro vira medição ou cai.
- [x] Fica decidido e justificado **onde o conserto mora**: se `bin_archive.py`
      ganhar a segunda lista, o `pes2_selftest` tem de continuar verde.
- [x] Controle negativo: trocar uma paleta por outra fica vermelho.

---

## Log de Execução

**Executado em:** 2026-09-15

### A lista existia, e o que a escondia não era o varredor

`python tools/looks/texture.py --report`:

```text
Table(tag=0x800f, bank=+0, 23 record(s) at 65508..65878)
    23 image(s), 0 clut(s)
Table(tag=0x8010, bank=+1, 267 record(s) at 76836..81110)
    0 image(s), 267 clut(s)
267 palette(s): 262 of 16 entries (4 bpp), 5 of 256 entries (8 bpp)
the bank runs 65892..76836 (10944 B) and the list starts at 76836
```

A task nasceu da premissa da §1.7 — *"o `entries()` acha a lista de imagens e
**não** acha a lista de paletas deste arquivo"*. A lista está lá, nos últimos
4.272 bytes do arquivo, e o que a esconde é **uma palavra do registro**, que o
`tools/pes2/bin_archive.py` documenta assim:

```text
[7] 0x800f    a constant tag, and the thing that makes the record
              findable without knowing where the list is
```

**Não é constante e não é tag.** É o **banco de 64 KiB** do offset de 16 bits do
campo 6, com viés para o banco 0 valer `0x800f`:

```text
offset = campo[6] + (campo[7] - 0x800F) * 0x10000
```

E a prova não é a aritmética — é o que cai no endereço resolvido. Com o banco,
o fluxo LZSS de cada registro de imagem descomprime **exatamente** para o
retângulo que o próprio registro declara; sem ele, não:

| arquivo | bytes | campo 7 | banco | imagens que descomprimem para o retângulo declarado |
|---|---:|---|---:|---|
| `DAT2D.BIN` | 81.124 | `0x800f` | +0 | 23 de 23 |
| `DATSEL3.BIN` | 65.884 | `0x800f` | +0 | 20 de 20 |
| `EDTR_2D.BIN` | 73.856 | `0x8010` | +1 | 2 de 2 |
| `DATSEL2.BIN` | 124.812 | `0x8010` | +1 | 15 de 15 |
| `DAT_CG.BIN` | 101.416 | `0x8010` | +1 | 9 de 9 |
| `DATSEL.BIN` | 223.496 | `0x8012` | +3 | 6 de 6 |

A constante funciona em todo contêiner cujo payload cabe nos primeiros 64 KiB,
que é **todo contêiner dos quatro discos da família PES2**. Nunca esteve errada
lá, e nunca esteve certa.

### O ladrilho é a conferência, não o offset

262 × 32 B + 5 × 512 B = **10.944 B**, e 65.892 + 10.944 = **76.836**, que é
onde a lista começa. Os 267 payloads ladrilham sem buraco e sem sobreposição.

Isso é mais forte do que conferir offsets contra a tabela do CARP: uma
resolução errada por um banco, ou uma largura lida na profundidade errada,
deixa buraco na hora. O `self_check()` tem o caso vermelho — o mesmo contêiner
sintético com oito bytes de folga entre os payloads —, e ele fica vermelho.

### Um id de 4 bits aponta para dentro de uma paleta de 256

```text
the 9 distinct CLUT id(s) the geometry names:
    vram (0,480)     4 bpp  x446   <- 256 entries at 65892
    vram (0,484)     4 bpp  x142   <- 256 entries at 67940
    vram (0,485)     8 bpp  x85    NOT in /BIN/DAT2D.BIN
    vram (0,486)     8 bpp  x414   NOT in /BIN/DAT2D.BIN
    vram (0,488)     8 bpp  x540   NOT in /BIN/DAT2D.BIN
    vram (16,480)    4 bpp  x948   <- 256 entries at 65892
    vram (144,480)   4 bpp  x126   <- 256 entries at 65892
    vram (240,484)   4 bpp  x4     <- 256 entries at 67940
    vram (336,510)   4 bpp  x136   NOT in /BIN/DAT2D.BIN
5 of 9 resolve in this file; 4 come from elsewhere
```

A pele nua amostra (0, 480), a cabeça (16, 480) e (144, 480), e **as três são
entradas do mesmo registro largo**. Então resolver um CLUT id é achar o registro
que o **cobre**, na largura que a página da primitiva pede — não o registro que
lhe é igual. Um varredor que casasse por igualdade devolveria `NoPalette` para
948 primitivas; um que devolvesse "a mais próxima" devolveria dezesseis
entradas que desenham perfeitamente e são as cores erradas.

Os quatro ids que **não** estão neste arquivo são resultado, não falha: os três
de 8 bits são os uniformes (jogador de linha e goleiro), e ficam para a
[`LOOKS-TASK-11`](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md), ao lado das
duas páginas de textura que a §1.7 já registrava como ausentes.

### Os dois rótulos do CARP, conferidos contra o disco

```text
CARP's "Pieles": 65892, 66404, 66916, 67428 -- four 256-entry palettes on
  rows 480..483, and SKIN moves a CLUT id by one row
CARP's "Botines": 67940 -- the only palette the foot section(s) sample,
  at vram (0,484), and no other piece touches it
```

- **"Pieles"** — o passo de 512 bytes por si não confirma nada; o que confirma é
  que `SKIN` soma `0x40` ao CLUT id ([`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md)),
  **exatamente uma linha de VRAM**, e que as quatro linhas 480-483 têm um
  registro de 256 entradas cada e mais nada.
- **"Botines"** — a confirmação é independente do rótulo e vem da task anterior:
  as seções 9 e 10, que a [`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md)
  nomeou **pé** por espelho e por serem as duas únicas compartilhadas pelos dois
  bonecos, amostram **(0, 484) e mais nada**, e nenhuma outra peça a toca. A
  ferramenta calcula isso a partir do `pieces.name_pieces()`, e não de uma lista
  de seções escrita à mão.

### Onde o conserto mora, e por quê

**Em `tools/looks/texture.py`, e o `tools/pes2/bin_archive.py` não foi tocado.**
A razão é medida, não preferência: uma regra de varredura geral o bastante para
achar esta lista — aceitar qualquer palavra de banco, validando cada registro
pelo que ele declara — faz aparecerem **2.151 registros a mais em 40 outros
contêineres deste mesmo disco**, os estádios `GDC_*` incluídos, que aquele
módulo separa de propósito (`is_stadium`). Mexer no varredor que guarda o PES2
para servir a um arquivo de um quinto disco moveria o chão de um gate alheio sem
entregar nada que o `texture.py` já não entregue.

**Mas a correção do modelo de registro é dívida real com o ciclo de PES2** — lá
o `entries()` não vê as listas de `DAT_CG.BIN`, `DATSEL2I.BIN`, `DATSEL_I.BIN` e
`EDTR_2D.BIN` da release `(EsIt)`. Como o pool de correções não atravessa pasta,
a dívida está escrita na
[`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md) e na §1.7
do plano; consertá-la no outro ciclo é decisão do usuário.

`git status --short tools/pes2` sai vazio, que é a forma curta de dizer que o
critério "se `bin_archive.py` ganhar a segunda lista, o `pes2_selftest` tem de
continuar verde" não teve o que arriscar.

### Gates medidos

```text
python tools/looks/selftest.py --quiet
  modules:  0 failure(s)
  rules:    0 failure(s)      ..... rule 1 swept 10 file(s), 5499 line(s)
  controls: 0 failure(s)      ..... 19 of 19 controls red
  looks_selftest: 0 failure(s)
```

```text
python tools/looks/texture.py --check          ->  texture.py: 0 failure(s)
python tools/looks/texture.py --check-image    ->  texture --check-image: ok
python tools/looks/modelfile.py --check-image  ->  ok
python tools/looks/pieces.py --check           ->  0 failure(s)
python tools/looks/pieces.py --check-image     ->  ok
python tools/looks/oracle.py --check           ->  0 failure(s)
python tools/check_tasks.py                    ->  123 task(s), ok
```

Os dois controles novos são os dois modos de errar isto sem sintoma:
`texture-bank-ignored` tira o banco do offset — e as paletas passam a ser lidas
65.536 bytes antes, dentro das imagens comprimidas, onde os bytes ainda são
bytes e ainda fazem cor; `texture-clut-any-record` é a troca que o critério pede
literalmente — com o intervalo ignorado, toda peça resolve para a primeira
paleta do arquivo, o render continua desenhando, e a chuteira sai da cor da
pele. Os dois ficam vermelhos.

**`pes2_selftest` não roda nesta máquina** e não é regressão desta task: ele
termina em `FileNotFoundError [WinError 3] ... '/proc/self/fd'`, no laço que
procura descritor vazado. É Linux-only, e `tools/pes2/` não foi tocado.

Toda leitura saiu do **disco japonês**, por `WE2002_LOOKS_IMAGE` e através da
guarda do `iso_source`; `roms/` só foi lida.

### Arquivos criados/modificados

- `tools/looks/texture.py` — **novo**. `tables()`, `plausible()`, `Record` com o
  offset já resolvido do banco, `palettes()`, `widths()`, `tiling()`,
  `covering()`, `read_palette()`, `palette_for()`, `build_container()` para o
  caso sintético, `self_check()`, `_report()` e `_check_image()`
- `tools/looks/layout.py` — `RECORD_TAG_BASE`, `RECORD_BANK`, `RECORD_LIST_END`,
  `VRAM_WIDTH`, `VRAM_HEIGHT`, `CLUT_ROW_FIRST`, `TEXTURE_EXPECTED`,
  `TEXTURE_BANK` e `BOOTS_PALETTE`, com a proveniência de cada um
- `tools/looks/controls.py` — `texture-bank-ignored` e `texture-clut-any-record`
- `tools/looks/selftest.py` — `texture` no `MODULES`
- `docs/PLAN-LOOKS-PY.md` — §1.7 reescrita onde estava errada, §1.8 com o que o
  acerto dos rótulos de paleta diz e o que não diz, e §6 (d) com as quatro
  paletas localizadas no disco
- `docs/prompts/perfil-looks.md` — armadilha 5 remedida, o segundo gate de disco
  na tabela, e a largura por registro nas verificações da Fase 3
- `docs/tasks/looks/11-qual-imagem-e-o-cabelo.md` — as paletas já lidas, e os
  quatro ids que vêm de outro contêiner
- `docs/tasks/looks/12-pele-paleta-ou-vertice.md` — as quatro peles localizadas
- `docs/tasks/looks/14-tabela-de-montagem.md` — a regra de cobertura, e que um
  passo de `SKIN` move a linha de VRAM inteira
- `docs/tasks/looks/19-alvos-de-ctest-e-cli.md` — o segundo `--check-image`, sem
  alvo
- `docs/tasks/looks/20-reconciliacao-e-entregaveis.md` — a dívida com o ciclo de
  PES2
- `docs/tasks/looks/progresso.md` — tabela e checklist da Fase 3
- `docs/tasks/looks/10-lista-de-cluts-do-dat2d.md` — este arquivo

### Problemas encontrados

- **A premissa da task estava errada, e do jeito mais confortável.** "O varredor
  não acha" convida a consertar o varredor; medir mostrou que o varredor está
  certo para o que ele mede e que o **modelo de registro** é que estava errado,
  num arquivo de outro projeto. Resultado negativo sobre a própria pergunta é
  resultado: a §1.7 foi corrigida no lugar em vez de ganhar um apêndice.
- **Um falso padrão quase virou medição.** Do fim da lista de imagens ao EOF são
  15.232 bytes, que dão **476 × 32 exatos** — e isso parecia dizer "476 paletas
  de 16 cores, nenhuma de 256". Divide certinho e está errado: os últimos 4.272
  bytes são a lista de registros, e as 5 paletas de 256 existem. **Divisão exata
  não é fechamento**; quem fecha é o ladrilho contra um fim que outra coisa
  declara.
- **Heredoc do Bash comeu um `\x00`** e escreveu byte nulo no fonte, que o
  Python recusou com `source code cannot contain null bytes`. É a mesma
  armadilha do `\b` que já custou uma corrida neste repositório: script de
  patch se escreve em arquivo, não em heredoc.
- E o de sempre: `ctest -R looks` neste worktree responde `No tests were
  found!!!` e sai 0 ([`CORR-LOOKS-015`](/docs/tasks/looks/CORR-LOOKS-015.md));
  os gates acima saíram da coluna do meio do
  [`perfil-looks.md`](/docs/prompts/perfil-looks.md).
