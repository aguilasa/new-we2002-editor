---
id: K3D-TASK-15
---

# K3D-TASK-15 — Fechamento da fase 5

## Goal

A fase 5 (G6) conferida na HEAD, com capturas para o usuário conferir de olho o que motivou a fase.

## Arquivos a criar ou modificar

- In:
  - nenhum de código — só conferência
- Out: —

## Done criteria

- [x] as verificações da Fase 5 do perfil, cada uma com o comando e a saída colados no Log
- [x] capturas do TEX_00 de costas (yaw 0) e de lado (yaw 90 e 270), jogador e goleiro, enviadas ao usuário, com os caminhos no Log
- [x] `rite check --cycle kits-3d`: 0 erros
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

## Log de Execução

### 2026-10-08 — conferência na HEAD `8ef184d`

Ambiente: `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`.

**Verificações da Fase 5 do perfil:**

1. `python3 tools/kits/cli.py holes $WE2002_LOOKS_IMAGE --tag 00`: 48 linhas (24 giros × 2 figuras);
   `grep -c "skipped 0; misordered 0)"` dá `48`. O que sobra é só `transparent`, todo em zona ou
   lacuna do colarinho (seção 0 do jogador, seção 11 do goleiro); o pior giro é
   `figure 0 yaw 180: silhouette 15161, missing 30 (transparent 30, backdrop 0; skipped 0; misordered 0)`
   (`shirt front, collar 18`, `collar tip, first 5`, `collar tip, second 5`, `gap collar, between its tips (21,6) 2x1 2`).
   De costas: `figure 0 yaw   0: ... missing 0` e `figure 1 yaw   0: ... missing 0`.
2. Casos sintéticos vermelhos, `python3 tools/kits/controls.py | grep -E "raster|holes-alpha"`:
   `RED    raster-skips-flat-uv         kits/core/raster.py :: draw`,
   `RED    raster-mean-order            kits/core/raster.py :: draw`,
   `RED    holes-alpha-ignored          kits/core/raster.py :: draw`.
3. Vista contra `--export-3d`, `ctest --test-dir build -R kits_ui -V`:
   `ok    the 3D view is the core's drawing, pixel for pixel, ... (figure 0 yaw 0 0 px off, 114 ms; figure 0 yaw 180 0 px off, 115 ms; figure 1 yaw 0 0 px off, 126 ms; figure 1 yaw 180 0 px off, 114 ms)`
   e `ok    plant 'the view back to the old drawing' fails the core drawing judge` (995 / 714 / 873 / 816 px off).
4. Tempo de quadro abaixo de `FRAME_LIMIT_MS = 400`: 114–126 ms no `kits_ui` acima; nas capturas
   abaixo, `3d view: at 20,169, 940x409, yaw 90, pitch 0, frame 147 ms` e o maior,
   `yaw 270 ... frame 179 ms` (jogador).
5. `ctest --test-dir build -R kits`: `100% tests passed, 0 tests failed out of 4`, nenhum *skipped*;
   `python3 tools/kits/controls.py`: `controls: 32 of 32 red`.

**Capturas** (enviadas ao usuário), por
`work/venv-looks/bin/python tools/kits/ui/app.py $WE2002_LOOKS_IMAGE --tag 00 --tab 3d --figure F --yaw Y --screenshot work/k3d-15/figF-yawY.png --export-3d work/k3d-15/core-figF-yawY.png`
com F em 0 e 1 e Y em 0, 90 e 270, recortadas na caixa da vista (`940x409+20+169`):
`work/k3d-15/crop-fig{0,1}-yaw{0,90,270}.png`, e a folha `work/k3d-15/sheet.png` (linha de cima o
jogador, de baixo o goleiro). De costas a bermuda fecha inteira nas duas pernas e na junção com a
camiseta — o defeito do relato de 2026-10-08 não aparece.

Recorte e folha, comandos reconstruídos depois pela
[CORR-K3D-010](/docs/tasks/kits-3d/CORR-K3D-010.md) (ImageMagick 6, `convert`/`montage`; o `magick`
do IM7 não está instalado) e conferidos contra os arquivos desta corrida:

```
$ cd work/k3d-15
$ for f in 0 1; do for y in 0 90 270; do convert fig$f-yaw$y.png -crop 940x409+20+169 +repage crop-fig$f-yaw$y.png; done; done
$ montage crop-fig0-yaw{0,90,270}.png crop-fig1-yaw{0,90,270}.png -tile 3x2 -geometry 470x205+4+4 -background grey20 sheet.png
```

Refeitos num diretório à parte, `compare -metric AE` dá 0 nos seis recortes e 0 na folha. O
controle é a mesma montagem sem `-background grey20`, que dá 32784 contra a `sheet.png`.

**`rite check --cycle kits-3d`:** `check: 0 error(s), 0 warning(s) in 1 cycle(s)`.
- **Closed** — commit `982c294` (2026-10-08): docs(kits): verify phase 5 at HEAD and record the back and side captures
  - Files (`git show --name-status 982c294`):
    - `M docs/tasks/kits-3d/15-fechamento-fase-5.md`
- **Reviewed** (2026-10-08) at `97b580b`: CORR-K3D-010
