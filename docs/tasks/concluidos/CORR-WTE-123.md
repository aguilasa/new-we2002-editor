---
id: CORR-WTE-123
title: "Correção: os seis roteiros da PAR-TASK-01 não estão em lugar nenhum, e a 'Definição de pronto' promete o comando"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-123: as seis corridas verdes que ninguém consegue repetir

## Problema identificado

A [PAR-TASK-01](/docs/tasks/concluidos/PAR-TASK-01.md) fecha com este item marcado:

```markdown
- [x] Cada item com evidência: o comando, a faixa que saiu do golden_compare.py,
      e o veredito
```

**A faixa e o veredito existem** — estão na §8.1 do
[/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md), item a item. **O
comando não existe em lugar nenhum.** Os seis roteiros `GOLDEN_GUI_EDIT` /
`GOLDEN_EDIT` que produziram os seis estímulos foram shell avulso, e o commit
que fechou a task (`b5997b7`) só tocou três markdowns — nenhum arquivo em
`tools/`, nenhum bloco de roteiro nos três.

O que isso custa, em ordem de gravidade:

1. **As seis corridas não são repetíveis.** Verde de golden é asserção sobre um
   estímulo; sem o estímulo versionado, a asserção não tem sujeito. Não há como
   re-rodar a §8.1 depois de um commit no `TeamView.cpp` — não é regressão, é
   memória.
2. **A [PAR-TASK-10](/docs/tasks/concluidos/PAR-TASK-10.md) é literalmente o mesmo
   trabalho na outra plataforma** ("aqui não há Citrix filtrando input"), e
   depende da 01. Ela herda o bloqueio e não herda o roteiro.
3. **As PAR-TASK-02 a 09 repetem a navegação.** O Log documenta em prosa as
   duas descobertas de navegação (`Home` antes do `Down`; `End` cai em
   `Master League (default)`, e um `Up` dá o último clube), mas **não** o
   terceiro fato, sem o qual nenhuma das duas funciona — ver a evidência.

Isto é a versão de processo da mesma lição que a task aprendeu no conteúdo:
ela mostrou que **verde sem controle positivo não mede nada**, e o controle
positivo também é um comando que não ficou escrito.

## Evidência

Esta revisão teve de **reconstruir** o roteiro do primeiro item do zero para
poder medir. A reconstrução exigiu uma decisão que o Log não registra:

> **O clique no `CMB_TEAM` abre o popup, e `Home`+`Down` só movem o item
> destacado — a seleção não é confirmada sem um `Return`.** Medido nesta
> revisão, no `:98`, com captura da janela: sem o `Return` o popup continua
> aberto e o formulário não troca de time. Com ele, os dois lados chegam a
> `Nation 1 - Ireland`.

O roteiro reconstruído (o que deveria estar versionado):

```sh
xdotool mousemove --window $MAIN 315 20 click 1; sleep 2   # CMB_TEAM
xdotool key --clearmodifiers Home;   sleep 1
xdotool key --clearmodifiers Down;   sleep 1
xdotool key --clearmodifiers Return; sleep 2               # confirma o popup
i=1
for y in 59 80 101 122 143 165; do                         # TXT_TEAM_NAME1..6
  xdotool mousemove --window $MAIN 72 $y click 1; sleep 1
  xdotool key --clearmodifiers End;       sleep 1
  xdotool key --clearmodifiers shift+Home; sleep 1
  xdotool key --clearmodifiers BackSpace;  sleep 1
  xdotool type --delay 40 "GOLDEN$i"; sleep 1
  i=$((i+1))
done
xdotool mousemove --window $MAIN 72 208 click 1; sleep 2   # tira o foco do 6º
```

Com ele, as duas medições que a task afirma se reproduzem. O golden:

```text
$ WE2002_GOLDEN_MODE=gui GOLDEN_EDIT="$(cat routine.sh)" \
  GOLDEN_GUI_EDIT="$GOLDEN_EDIT" bash tools/golden_check.sh roms/ptbr-remaster.bin
OK: identico ao oraculo, exceto o slot 64 conhecido (405724..405739)
```

E o controle positivo (cópia gravada contra a imagem original), que é o que
prova que o estímulo chegou ao disco:

```text
$ python3 tools/golden_compare.py roms/ptbr-remaster.bin ctrl.bin
11 run(s), 77 byte(s) differ
   1013936    1013942       7       6     431   data  OFS_TEAM_NAME_1_A+200
   1882896    1882902       7       6     800   data  OFS_TEAM_NAME_2+928
   2004988    2004994       7       6     852   data  OFS_TEAM_NAME_3+992
   2830940    2830946       7       6    1203   data  OFS_TEAM_NAME_4+780
   4824020    4824026       7       6    2051   data  OFS_TEAM_NAME_5_A+44
   5652904    5652910       7       6    2403   data  OFS_TEAM_NAME_6_B+540
```

Seis faixas, `span` 7 cada, contra o `(7)` dos seis rótulos — que é o item 1 da
§8.1, medido de novo. As outras cinco linhas são as não-idempotências que o Log
já nomeia (`OFS_PLAYER_ATTR_8`, `OFS_KICKER`, `OFS_PLAYER_NAME_7+471`).

**A medição confirma a task.** O que ela não confirma é a repetibilidade: o
roteiro acima é uma reconstrução desta revisão, não o que a task rodou, e os
outros cinco continuam sem original nem reconstrução.

## Causa raiz

A série não tem onde guardar roteiro. O `wte/` resolveu o mesmo problema com
roteiros versionados e um TSV de vereditos (`wte/re/golden-ptbr.tsv`); o lado
`newWe2002` nunca precisou, porque até aqui o `golden_gui` rodava sem edição.

## Correção

### Arquivo: `tools/par/` (novo diretório)

Um arquivo de roteiro por item da §8, nomeado pelo item, contendo só o trecho
de shell que os dois hooks recebem:

```
tools/par/8.1-nomes-6-slots.sh
tools/par/8.1-kanji-e-mista.sh
tools/par/8.1-abreviacoes.sh
tools/par/8.1-copy-selecao.sh
tools/par/8.1-copy-clube-ml.sh
tools/par/8.1-clube-ml-extras.sh
```

Cada um roda nos dois lados sem alteração — é o que o `$MAIN` comum garante. O
cabeçalho de cada arquivo diz o item da §8 que ele exercita e o time que
seleciona.

### Arquivo: `docs/tasks/concluidos/PAR-TASK-01.md`

No Log, apontar cada um dos cinco itens para o seu roteiro, e registrar o
terceiro fato de navegação (o `Return` que confirma o popup) junto dos dois que
já estão lá.

### Arquivo: `docs/PARIDADE-FUNCIONAL.md` §8.1

Em cada item, o nome do roteiro ao lado da faixa medida — assim "o comando, a
faixa e o veredito" passa a ser verdade literal.

**Se algum dos cinco roteiros restantes não puder ser recuperado**, reconstruí-lo
e **remedir** o item, registrando a faixa nova. Roteiro reconstruído com faixa
remedida é evidência; roteiro ausente com faixa antiga é lembrança.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/par/8.1-*.sh` (6) | criar |
| `docs/tasks/concluidos/PAR-TASK-01.md` | modificar |
| `docs/PARIDADE-FUNCIONAL.md` | modificar |

## Verificação

- [x] Os seis roteiros existem e cada um roda nos dois hooks sem edição
- [x] Cada item da §8.1 nomeia o seu roteiro
- [x] Ao menos um item re-rodado do zero pelo arquivo versionado dá o mesmo
      veredito: `bash tools/golden_check.sh roms/ptbr-remaster.bin` com
      `WE2002_GOLDEN_MODE=gui` e os dois hooks apontando para o arquivo
- [x] O controle positivo de cada roteiro está registrado com as faixas, não só
      o veredito do golden
- [x] `python3 tools/check_tasks.py` continua `ok`
- [x] `roms/` intocada — toda corrida sobre cópia

## Log de Execução

**Executado em:** 2026-08-28

**Resumo do que foi feito:**

Os seis roteiros foram **reconstruídos e remedidos** — nenhum dos originais
existia para recuperar —, e vivem em `tools/par/`, um por corrida, nomeados
pelo item da §8 que exercitam. Cada arquivo é o trecho de shell que os dois
hooks recebem sem alteração: preâmbulo com `par_click` (centro de um controle,
a partir da geometria em DLU do `ed.rc`) e `par_type` (limpa com `End`,
`shift+Home`, `BackSpace` — `Ctrl+A` não seleciona tudo num `CEdit`), depois a
seleção do time e o estímulo.

As doze corridas — seis pares golden + controle positivo — saíram na
`ptbr-remaster.bin`. **Todas as seis deram
`1 run(s)` em `405724..405739`**, a faixa conhecida, e nada mais. Os controles
positivos, descontadas as cinco não-idempotências que aparecem em todas
(`OFS_PLAYER_NAME_7+471`, três de `OFS_PLAYER_ATTR_8`, `OFS_KICKER+384`):

| Roteiro | Regiões | Faixas |
|---|---|---|
| `8.1-nomes-6-slots.sh` | 6 | `OFS_TEAM_NAME_1_A+200`, `_2+928`, `_3+992`, `_4+780`, `_5_A+44`, `_6_B+540` — span 7 cada |
| `8.1-kanji-e-mista.sh` | 2 | `OFS_TEAM_NAME_KANJI_A+53` span 13 / diff 7; `OFS_TEAM_MIXED_CASE_NAME+820` span 7 |
| `8.1-abreviacoes.sh` | 3 | `OFS_TEAM_ABBREV_1/_2/_3+376` — span 3 cada |
| `8.1-copy-selecao.sh` | 11 | 6 nomes (7), 3 abreviações (2), mista (7), kanji span 13 / diff 7 |
| `8.1-copy-clube-ml.sh` | 13 | as 11 acima com offsets `+0` do clube, mais `OFS_ML_TEAM_NAME_7`/`_8` (7); kanji span 9 / diff 4 |
| `8.1-clube-ml-extras.sh` | 8 | nomes 1–3 span 10, 4–6 span 7, `OFS_ML_TEAM_NAME_7` span 7, `_8` span 10 |

O item 1 foi ainda re-rodado **do zero pelo arquivo versionado**, pelo caminho
literal da Verificação:

```text
$ R="$(cat tools/par/8.1-nomes-6-slots.sh)"
$ WE2002_GOLDEN_MODE=gui GOLDEN_EDIT="$R" GOLDEN_GUI_EDIT="$R" \
    bash tools/golden_check.sh roms/ptbr-remaster.bin
OK: identico ao oraculo, exceto o slot 64 conhecido (405724..405739)
```

**Problemas encontrados:**

**A §8.1 atribuía o `span 9 / diff 4` do kanji ao `copy` em geral.** A
remedição mostrou que ele é do **clube de ML**: na seleção, para a mesma fonte
de 6 caracteres, o mesmo `CMD_COPY_TEAM_NAMES` dá `span 13 / diff 7`. O quirk
continua sendo que o kanji não acompanha o comprimento dos outros; o que muda é
que o quanto ele desanda depende do time. Corrigido no inventário.

**O terceiro fato de navegação foi confirmado e registrado.** O clique no
`CMB_TEAM` abre o popup e as teclas só movem o item destacado — sem `Return` a
seleção não é confirmada, o formulário não troca de time, e o resto do roteiro
digita em time nenhum. Está agora no Log da PAR-TASK-01, junto dos dois que já
estavam.

**A varredura de discrepância puxou dois documentos que a CORR não previa.** O
`CLAUDE.md` descrevia o modo `gui` sem dizer que os dois lados têm hooks de
nomes diferentes nem onde ficam os roteiros; e o "Método comum" da série
`PAR-TASK-*` no `progresso.md` mandava comparar com o `golden_compare.py` sem
dizer que o estímulo vai versionado. Os dois ganharam o parágrafo, porque a
próxima PAR-TASK entra por eles.

**Arquivos criados/modificados:**

- `tools/par/8.1-nomes-6-slots.sh`, `8.1-kanji-e-mista.sh`,
  `8.1-abreviacoes.sh`, `8.1-copy-selecao.sh`, `8.1-copy-clube-ml.sh`,
  `8.1-clube-ml-extras.sh` — criados
- `docs/PARIDADE-FUNCIONAL.md` — §8.1: o roteiro de cada item, a nota sobre o
  controle positivo e as faixas remedidas, e a correção do kanji
- `docs/tasks/concluidos/PAR-TASK-01.md` — itens apontando para os roteiros, o `Return` no
  Log, e o adendo desta correção
- `docs/tasks/concluidos/progresso.md` — o "Método comum" da série ganha a convenção de
  `tools/par/`
- `CLAUDE.md` — a seção do golden test ganha os dois nomes de hook, o exemplo
  com o mesmo roteiro nos dois lados, e o `tools/par/`

**Nota de rastreio, 2026-08-29.** O commit `c86e794` restaurou este arquivo
byte-idêntico ao `c2b127c`, que é o commit que abriu a correção — e com isso
devolveu `status: pendente` e apagou este Log, embora os seis roteiros e as
edições de doc já estivessem na árvore desde o `6e3be27`. O corpo era idêntico;
só o rastreio regrediu. Este Log e o `[x]` do `correcoes-progresso.md` foram
repostos, com a data do commit que de fato corrigiu.
