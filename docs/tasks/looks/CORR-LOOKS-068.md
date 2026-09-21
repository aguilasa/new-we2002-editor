---
id: CORR-LOOKS-068
title: "Julgar os pixels das setas, não só a lista, e medir a CLUT da ◀"
origin: LOOKS-TASK-36
severity: medium
files: [tools/looks/oracle.py, tools/looks/ui_check.py, tools/looks/sprites.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-21
done_commit: 9716a6be
---

# CORR-LOOKS-068 — Julgar os pixels das setas, não só a lista, e medir a CLUT da ◀

Origin: [LOOKS-TASK-36](/docs/tasks/looks/36-os-sprites-estaticos.md)

## Problema identificado

Nenhum gate confere os **pixels** das setas que a janela pinta. O
`oracle.frame_arrows` separa as setas do jogo só por página e `uv` e nunca
compara a CLUT. O `--keys` compara o relatório da janela
(`LooksSet.arrows()`, que devolve `screen.State.arrows()` e portanto concorda
com a tabela por construção), não o que ela desenha. O `ui_check` não amostra
pixel de seta nenhum.

E `sprites.ARROW_CLUT = (80, 497)` foi medida **só para a ▶**: a linha da
tabela do §10.3 diz "a seta ▶ ... (704,0), (80,497)", e o contexto da task
registra que a ◀ nunca apareceu num quadro medido. A CLUT da ◀ é suposta. Uma
CLUT de seta errada fica verde em tudo que roda sem emulador.

## Evidência

Revisão da LOOKS-TASK-36 em 2026-09-21, sobre `2b698730`:

```text
$ grep -n "def frame_arrows" -A23 tools/looks/oracle.py
4749:        if tuple(one["page"]) != layout.ARROW_PAGE:
4751:        side = sides.get(tuple(one["uv"]))
4756:        out.append({"side": side, "point": list(one["point"])})      # sem clut, sem cor

$ grep -n "arrow" tools/looks/ui_check.py
746/747/748: só lê a linha "arrows " do relatório; 967: o controle da tecla de seta -- nenhum pixel de seta amostrado

# plantado numa cópia (git archive HEAD tools): ARROW_CLUT = (64, 496)  (a CLUT da ajuda)
$ python <cópia>/tools/looks/sprites.py --check-image
the left arrow is the right one mirrored
sprites --check-image: 0 problem(s)
$ python <cópia>/tools/looks/sprites.py
sprites.py: 0 failure(s)

# sprites na página (704,0) em work/looks-scenery/slot{1,2}.json
slot 1: ([128, 248], [80, 497], [76, 76, 76])
slot 2: ([128, 248], [80, 497], [84, 84, 84])   -- só a ▶ foi gravada com CLUT
```

## Causa raiz

(hipótese) O critério 3 foi lido como "a lista de setas concorda entre jogo,
tabela e janela". O lado da janela é a própria tabela — a armadilha "janela e
tabela concordam de graça" do `CLAUDE.md` —, então os texels desenhados e a
CLUT nunca encontram o jogo.

## Correção

- `tools/looks/oracle.py`, `frame_arrows`: gravar a CLUT de cada seta e recusar
  a que diferir de `sprites.ARROW_CLUT`; isso mede a ◀ na primeira vez que o
  walk a vir.
- `tools/looks/ui_check.py`: amostrar pixel de seta (os pixels da seta do jogo
  numa linha e ponta conhecidas, escalados pela cor 128 contra a do pulso, ou
  comparados pela forma do texel sem modulação), com um controle plantado de
  CLUT ou `uv` errados que tem de ficar vermelho.

## Arquivos a criar ou modificar

- `tools/looks/oracle.py`
- `tools/looks/ui_check.py`
- `tools/looks/sprites.py`

## Verificação

Plantar `ARROW_CLUT = (64, 496)` numa cópia e rodar `python
tools/looks/ui_check.py` (ou `oracle.py --keys "Down,Right,Right,Right,Right"
2`). Hoje passa; depois da correção tem de ficar vermelho.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-21, HEAD `36d1aaed`: **reproduzida**.

```text
oracle.py:4756  out.append({"side": side, "point": list(one["point"])})   # frame_arrows filtra só página e uv
ui_check.py: "arrow" só em 746-748 (linha "arrows " do relatório), 967 (o controle) e 1064 (docstring)
# cópia plantada (git archive HEAD tools), ARROW_CLUT = (64, 496), WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin
$ python <cópia>/tools/looks/sprites.py --check-image
arrow left uv (128, 240): 22 of 64 texels opaque
arrow right uv (128, 248) ...
the left arrow is the right one mirrored
sprites --check-image: 0 problem(s)
$ python <cópia>/tools/looks/sprites.py
sprites.py: 0 failure(s)
# work/looks-scenery/slot{1,2}.json, página (704,0): só a ▶ (uv 128,248) com CLUT (80,497); nenhuma ◀
```

### Correção, 2026-09-21 (HEAD `568f87e6`)

**Reproduzida de novo, pelo gate inteiro.** Cópia de `HEAD` (`git archive`)
com `ARROW_CLUT = (64, 496)`, sob `work/corr068-before/`:

```text
$ python work/corr068-before/tools/looks/ui_check.py
...
looks_ui: 14 of 14 negative control(s) red, and the window drew every tuple ...
exit=0
```

**Causa raiz confirmada.** O `frame_arrows` separava as setas por página e
`uv` e jogava fora a CLUT; o `ui_check` só lia a linha `arrows` do relatório da
janela, que sai do `screen.State.arrows()` — janela e tabela concordando de
graça. Nenhum dos dois encontrava os **pixels** do jogo.

**A CLUT da ◀, medida:** `(80, 497)`, a mesma da ▶. Lida da lista que o
quadro entrega ao GPU, em `DEFAUL` (uma `Up` depois da carga), nos dois slots,
três leituras em cada um:

```text
2 ('Up',) (384, 43) uv (128, 240) clut (80, 497) colour 64/72/80  frame (115,90,0)/(132,107,0)/(148,115,0)
1 ('Up',) (384, 43) uv (128, 240) clut (80, 497) colour 108/116/124 frame (198,156,0)/(214,165,0)/(231,181,0)
```

A seta só usa a entrada 15 da CLUT — `(255, 198, 0)`, laranja; a mesma
entrada da `(64, 496)` da ajuda é `(214, 214, 214)`. E a cor da lista **não** é
a do quadro à unidade: a seta pulsa alguns passos por quadro, e a lista lida é
a do quadro seguinte (cor 96 sobre um quadro que corresponde a ~100).

**O que mudou:**

- `oracle.py`, `frame_arrows`: recusa a seta desenhada de CLUT diferente de
  `sprites.ARROW_CLUT` e guarda as CLUTs vistas em `ARROW_CLUTS_SEEN`; o
  `--keys` e o `--screen` imprimem a linha `the arrows' CLUT, read off the
  list`.
- `oracle.py --scenery [--write]`: `_arrow_samples` anda os `ARROW_WALKS` (a
  carga, que mostra a ▶, e `Up`, que mostra a ◀ em `DEFAUL`), lê cada um duas
  vezes como controle (mesmos pontos, `uv` e CLUT; a cor fica de fora porque
  pulsa) e grava em `slotN.json` a lista `arrows` com os 22 texels opacos de
  cada seta — onde olhar sai do disco com o `uv` e a CLUT **do jogo**, a cor sai
  do frame buffer.
- `ui_check.py`: `measure_arrows` fotografa a janela depois das mesmas teclas,
  modula o pixel dela como a GPU (`min(255, texel * cor // 128)`) em cada cor a
  até `ARROW_PULSE = 16` da da lista, e exige o melhor dentro de
  `ARROW_SLACK = 9`. `arrow_gap` é puro e tem quatro checks no self-check. Dois
  controles plantados em `ARROW_BREAKS`: a CLUT da ajuda e os dois `uv`
  trocados.
- `sprites.py`: nada — a constante estava certa; o defeito era não haver quem a
  medisse.

**Verificação, depois:**

```text
$ python tools/looks/oracle.py --scenery --write
    arrows after the load: > at (480, 55), uv (128, 248), CLUT (80, 497), colour (96, 96, 96); 22 opaque texel(s) sampled
    arrows after Up: < at (384, 43), uv (128, 240), CLUT (80, 497), colour (64, 64, 64); 22 opaque texel(s) sampled
    (slot 1: colour 60 e 108)
oracle --scenery: 0 problem(s) over 2 slot(s)

# melhor distância da janela ao jogo, por seta (gap, cor achada)
2 []     96 -> (2, 100)    2 ['Up'] 64 -> (1, 58)
1 []     60 -> (1, 58)     1 ['Up'] 108 -> (2, 100)

# os dois controles plantados
(True, "slot 2 after the load: the right arrow at (480, 55) is not the game's -- 133 apart at best (colour 80); at (480,57) the game shows (198, 156, 0) and the window (214, 214, 214)")
(True, "slot 2 after the load: the right arrow at (480, 55) is not the game's -- 198 apart at best (colour 80); at (480,57) the game shows (198, 156, 0) and the window (0, 53, 55)")

$ python tools/looks/oracle.py --keys "Down,Right,Right,Right,Right" 2
  the arrows' CLUT, read off the list: < (80,497)
oracle --keys: 0 difference(s) after 5 press(es), across the game, screen.json and our window
$ python tools/looks/oracle.py --keys "Up" 1
  the arrows' CLUT, read off the list: < (80,497)
oracle --keys: 0 difference(s) after 1 press(es), across the game, screen.json and our window

# a mesma sequência numa cópia da árvore corrigida com ARROW_CLUT = (64, 496)
oracle FAILED: the left arrow at (384, 67) is drawn from CLUT (80, 497), and the window cuts it from sprites.ARROW_CLUT (64, 496)
exit=1

# a Verificação do item: o gate inteiro numa cópia da árvore corrigida com ARROW_CLUT = (64, 496)
$ python work/corr068-after/tools/looks/ui_check.py
FAIL: slot 2 after the load: the right arrow at (480, 55) is not the game's -- 133 apart at best (colour 80); ...
FAIL: slot 2 after Up: the left arrow at (384, 43) is not the game's -- 80 apart at best (colour 48); ...
FAIL: slot 1 after the load: the right arrow at (480, 55) is not the game's -- 73 apart at best (colour 44); ...
FAIL: slot 1 after Up: the left arrow at (384, 43) is not the game's -- 153 apart at best (colour 92); ...
exit=1

# e na árvore corrigida
$ python tools/looks/ui_check.py
  the arrows the window paints are the game's: 88 pixel(s) sampled over slots 2, 1, every one within 9 at the game's colour
negative: breaking the arrows' CLUT reddens the arrows -- ... 133 apart at best ...
negative: breaking the arrows' uv reddens the arrows -- ... 198 apart at best ...
looks_ui: 16 of 16 negative control(s) red, ...
exit=0
```

Antes 14 controles, agora 16: os dois de `ARROW_BREAKS`.
- **Closed** — commit `9716a6be` (2026-09-21): fix(looks): judge the arrows' pixels against the game and measure the ◀ CLUT — (80,497), the same as the ▶
  - Files (`git show --name-status 9716a6be`):
    - `M docs/tasks/looks/CORR-LOOKS-068.md`
    - `M tools/looks/oracle.py`
    - `M tools/looks/ui_check.py`
