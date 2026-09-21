---
id: CORR-LOOKS-068
title: "Julgar os pixels das setas, não só a lista, e medir a CLUT da ◀"
origin: LOOKS-TASK-36
severity: medium
files: [tools/looks/oracle.py, tools/looks/ui_check.py, tools/looks/sprites.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
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
