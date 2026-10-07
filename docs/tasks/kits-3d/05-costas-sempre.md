---
id: K3D-TASK-05
---

# K3D-TASK-05 — Cópia das costas sempre e conserto do que a contagem achar

## Goal

A cópia medida das costas (`BACK_COPY`) vale sempre, com ou sem Number, e o resto do que a K3D-TASK-04 contar é consertado só com regra medida.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/figure.py`, `tools/kits/core/api.py`
  - `tools/kits/ui/app.py`, `tools/kits/ui/i18n.py` (a dica `figure_hint`)
  - `tools/kits/ui_check.py`, `tools/kits/selftest.py`, `tools/kits/controls.py`
  - `docs/KITS-AJUSTES-3D.md` (G5: o que foi consertado e o que ficou, com a contagem)
- Out: inventar texel ou geometria (§0)

## Done criteria

- [x] a ferramenta da K3D-TASK-04 dá 0 px vindos da lacuna do torso, em todo giro, nas duas figuras, sem Number
- [x] a planta que tira o `BACK_COPY` do caminho sem Number fica vermelha
- [x] toda falta restante na contagem está listada em G5 com a causa medida, ou zerada
- [x] `figure_hint` deixa de dizer que as costas saem vazadas, nas duas línguas
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Reabre a decisão de 2026-10-05 (KITS-TASK-37): registrar datada em G5.

Da K3D-TASK-04 (2026-10-07): a contagem é `python3 tools/kits/cli.py holes <disco> --tag 00`.
Hoje, além da lacuna do torso (yaw 0: 3.853 px no jogador, 3.857 no goleiro), ela acha em todo
giro triângulos `skipped` (UV sem área, 108 a 514 px por giro) e `misordered` (pintura por
profundidade média invertendo seções vizinhas, 124 a 427 px por giro). A transcrição inteira está no Log da 04.

## Log de Execução

**O que mudou.** `scene_of` (`core/figure.py`) termina em `numbered_scene(built, …, None)`: a
cópia `BACK_COPY` vale sempre, e `numbered_indices` só pinta dígitos quando há número. O
`palette_swap` (controle 4 da §5) passou a comparar contra os índices com a mesma cópia; sem
isso os 8 casos dele ficavam vermelhos, porque a figura já não é o TEX cru na lacuna. A
`figure_hint` foi reescrita nas duas línguas.

**`skipped` e `misordered` não foram consertados.** Os dois são do desenho em
`ui/figure_view.py`, que esta task não cobre, e estão listados em G5 com a causa. A causa dos
`skipped` (UV com canto repetido ou colinear) também foi vista numa sonda descartável, que listou
os UVs dos triângulos pulados; nenhum número dela entrou em documento.

Evidência (2026-10-07):

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py holes roms/japanese-shift-jis.bin --tag 00 --top 60 | grep -c "gap torso"
0
(resumo das 48 linhas: jogador transparent 0-30, skipped 108-514, misordered 124-427;
 goleiro transparent 0-13, skipped 203-423, misordered 146-418; transparent só nas
 zonas/lacunas do colarinho)

$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py
  ok    Number unticked, the torso gap shows through at no turn of either figure (48 turn(s), 0 with the torso gap)
        plant 'back copy only with Number': the torso gap shows through at 42 turn(s): figure 0 yaw   0, figure 0 yaw  15, ...
  ok    plant 'back copy only with Number' fails the back copy judge
kits_ui: 0 failure(s)

$ python3 tools/kits/selftest.py --no-plant
  ok    the 3D hint no longer says the back shows through, in any language (G5)
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/selftest.py --image
  ok    cli.py holes: from the back the torso gap shows through on neither figure, the shirt back copied in with Number unticked (G5), and its --negative sees a planted gap
figure: 0 failure(s)

$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
$ python3 tools/kits/controls.py
controls: 30 of 30 red
```

A planta da cópia é do `PLANTS` do `ui_check.py` (alvo `../core/figure.py`), porque a figura
só se monta com o disco; o `controls.py` roda o selftest sem imagem e não ganhou entrada.

Varredura: `docs/PLAN-KITS-PY.md:375` ainda descreve a dica antiga ("as costas saem vazadas").
É o plano do ciclo `kits`, já arquivado, e fica como registro; a decisão nova está em G5.
- **Closed** — commit `eb6ded5` (2026-10-07): feat(kits): copy the shirt back into the torso gap on every figure
  - Files (`git show --name-status eb6ded5`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/tasks/kits-3d/05-costas-sempre.md`
    - `M tools/kits/core/figure.py`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui/i18n.py`
    - `M tools/kits/ui_check.py`
- **Reviewed** (2026-10-07) at `1dafb8e`: CORR-K3D-003
