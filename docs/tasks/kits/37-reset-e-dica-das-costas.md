---
id: KITS-TASK-37
---

# KITS-TASK-37 — Botão de reset na aba 3D e a dica das costas

## Goal

A aba 3D ganha um botão **Reset view** / **Restaurar vista**, e o duplo clique na vista faz o mesmo: os dois voltam ao giro de abertura (`DEFAULT_YAW`, `DEFAULT_PITCH` de `ui/figure_view.py`). A dica da aba passa a dizer por que as costas saem vazadas: a área que o torso amostra está vazia no TEX (§4.7). O desenho continua fiel aos dados (decisão do usuário, 2026-10-05).

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/figure_view.py`: `reset()`, que chama `turn_to(DEFAULT_YAW, DEFAULT_PITCH)`, e o `mouseDoubleClickEvent`
  - `tools/kits/ui/app.py`: o botão na linha de cima da aba 3D e `--reset`, que aplica `--yaw`/`--pitch` e depois o mesmo slot do botão
  - `tools/kits/ui/i18n.py`: o rótulo do botão e a frase das costas em `figure_hint`, em en-US e pt-BR
  - `tools/kits/ui_check.py`: a verificação do reset e uma planta
  - `docs/PLAN-KITS-PY.md`: §3.4, se a forma final mudar
- Out: número, braçadeira e qualquer preenchimento das costas (KITS-TASK-38 a 40)

## Done criteria

- [x] `app.py <jp> --tag 00 --tab 3d --yaw 0 --pitch 30 --reset --screenshot A` e `… --tab 3d --screenshot B` dão o mesmo sha256 (no Log). A mesma captura sem `--reset` dá outro sha256: é o controle
- [x] `kits_ui` afirma isso, e a planta `reset to the wrong yaw` (`reset()` com `DEFAULT_YAW + 90`) o deixa vermelho, com o vermelho no Log
- [x] O selftest confere o catálogo: `language: 0 failure(s)`, com as chaves novas nas duas línguas
- [x] `ctest --test-dir build -R kits`: 4/4

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.4).

O `FigureView` não guarda zoom nem pan: a câmera reenquadra a figura a cada quadro, então o reset é só o giro. Para o vazado das costas, ver a [§4.7](/docs/PLAN-KITS-PY.md#4.7). Não é face descartada: o `FigureView` pinta as faces dos dois lados.

## Log de Execução

### 2026-10-05

`FigureView.reset()` chama `turn_to(DEFAULT_YAW, DEFAULT_PITCH)`, e o
`mouseDoubleClickEvent` o chama; o botão **Reset view** / **Restaurar vista**
fica na ponta direita da linha de cima da aba 3D, ligado ao mesmo `reset`, e
`--reset` clica nele depois de aplicar `--yaw`/`--pitch`. A dica saiu da linha
de cima para uma linha própria, com quebra (a frase das costas não cabe ao lado
dos combos): "Drag to turn, double-click to reset. The back shows through: the
area the torso samples is empty in the TEX, and the game's back and number are
not measured yet." Duas chaves no catálogo, nas duas línguas: `figure_hint`
reescrita e `reset_view` nova.

**Critério 1** — `work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --tab 3d …`, no `:98`:

```
cdd9af8b23a132f37b5bf3a7fcefae6d0a2d694fd9ad5d151e9e7b4482861f25  A.png   # --yaw 0 --pitch 30 --reset
cdd9af8b23a132f37b5bf3a7fcefae6d0a2d694fd9ad5d151e9e7b4482861f25  B.png   # sem giro
86da3dad6ad5d33a57d55660deb19e0501a095ca70524bbe1dcb13ea8170bf45  C.png   # --yaw 0 --pitch 30, sem --reset (controle)
```

**Critério 2** — juiz `reset_judge` e planta `reset to the wrong yaw` no
`ui_check.py`. As plantas só sabiam alterar o `ui/app.py`, e o `reset()` mora no
`ui/figure_view.py`: o `sandbox` ganhou o arquivo-alvo (default `app.py`) e a
tupla da planta um quinto campo opcional. `python3 tools/kits/ui_check.py`
(o gate abre o disco por caminho absoluto, por isso outros sha256):

```
  ok    Reset view after --yaw 0 --pitch 30 is the 3D as it opens, and the turn alone is not (opened cbc6490227ad, reset cbc6490227ad, turned 301947aa3854)
        plant 'reset to the wrong yaw': reset gives 23323334c919, the opened view cbc6490227ad
  ok    plant 'reset to the wrong yaw' fails the reset judge
kits_ui: 0 failure(s)
```

**Critério 3** — `python3 tools/kits/selftest.py`: `language: 0 failure(s)`,
`kits_selftest: 0 failure(s)`.

**Critério 4** — `ctest --test-dir build -R kits`: `100% tests passed, 0 tests failed out of 4`.
- **Closed** — commit `cdf41c5` (2026-10-05): feat(kits): Reset view in the 3D tab, and the hint says why the back shows through
  - Files (`git show --name-status cdf41c5`):
    - `M docs/tasks/kits/37-reset-e-dica-das-costas.md`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui/figure_view.py`
    - `M tools/kits/ui/i18n.py`
    - `M tools/kits/ui_check.py`
