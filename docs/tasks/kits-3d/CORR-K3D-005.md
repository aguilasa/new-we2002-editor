---
id: CORR-K3D-005
---

# CORR-K3D-005 — Números de sonda nas tasks 13 e 14 (0,10 s e 218 px)

Origin: [K3D-TASK-13](/docs/tasks/kits-3d/13-rasterizador-nucleo.md)

## Problem

Dois números em arquivos de task saíram de sonda descartada, não de ferramenta
versionada. (a) As notas da [K3D-TASK-14](/docs/tasks/kits-3d/14-vista-rasterizador.md),
editadas pelo commit `3982070` da [K3D-TASK-13](/docs/tasks/kits-3d/13-rasterizador-nucleo.md),
dizem "Medido na 13: 0,10 s a 940×409, de costas" e admitem "a medida é de sonda". (b)
As notas da K3D-TASK-13 dizem que a seção 5 perde "218 px" para triângulos de UV sem
área de costas, mas `cli.py holes` no desenho antigo (commit pai `1aa4b87`) imprime 221.
Regra do projeto: número de sonda só entra em texto depois que a sonda vira opção de
ferramenta.

## Evidência

```text
$ grep -n '0,10 s\|218 px' docs/tasks/kits-3d/13-rasterizador-nucleo.md docs/tasks/kits-3d/14-vista-rasterizador.md
docs/tasks/kits-3d/14-vista-rasterizador.md:29:... Medido na 13: 0,10 s a 940×409, de costas, no TEX_00 — a medida é de sonda; ...
docs/tasks/kits-3d/13-rasterizador-nucleo.md:32:Medido em G6 (2026-10-08): de costas, a bermuda (seção 5) perde 218 px
$ git archive 1aa4b87 | tar -x -C <tmp>; cd <tmp>; ln -s <repo>/roms roms
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py holes roms/japanese-shift-jis.bin --tag 00 | grep 'figure 0 yaw   0:'
figure 0 yaw   0: silhouette 15161, missing 714 (transparent 0, backdrop 0; skipped 514; misordered 200)  skipped /BIN/EDT_MOD.BIN section 5 - 221; ...
```

O revisor cronometrou `api.draw_figure(d, 180, 0, 940, 409)` numa sonda e obteve 0,127 s
(figura 0) e 0,112 s (figura 1): o 0,10 s não se reproduz como escrito.

## Root cause

Hipótese: o tempo e a divisão por seção foram medidos com sondas descartáveis e colados
como texto; o 218 veio da sonda de planejamento do G6 (commit `1aa4b87`), que modelava a
vista em vez de rodar `cli.py holes`.

## Fix

Em `docs/tasks/kits-3d/14-vista-rasterizador.md`, tirar o 0,10 s ou trocá-lo pela saída de
uma opção de cronometragem versionada — a K3D-TASK-14 já precisa registrar um limite de
tempo de quadro, que é o lugar natural. Em `docs/tasks/kits-3d/13-rasterizador-nucleo.md`,
trocar 218 pelo 221 que a ferramenta imprime, citando o comando, ou marcá-lo como número
da sonda do G6.

## Arquivos a criar ou modificar

- docs/tasks/kits-3d/14-vista-rasterizador.md
- docs/tasks/kits-3d/13-rasterizador-nucleo.md

## Verificação

```sh
grep -n '0,10 s\|218 px' docs/tasks/kits-3d/13-rasterizador-nucleo.md docs/tasks/kits-3d/14-vista-rasterizador.md
```

Imprime duas linhas hoje; depois, nada — ou o número da ferramenta com o comando ao lado.

## Log de Execução

- 2026-10-08 — triagem inline: **REPRODUCED**. O `grep` imprimia as duas linhas. O passo
  `git archive` da Evidência tem marcadores (`<tmp>`) e não roda como está; rodado à mão num
  diretório do scratchpad, o `cli.py holes` sobre `1aa4b87` imprime `section 5 - 221` e
  `misordered … section 5 over … section 7 70`.
- Notes da K3D-TASK-13: 221 com o comando e a saída colados. A frase também dizia "a seção 7
  sai pintada sobre a 5"; pelo `core/figure.py:562` a seção mostrada é a 5, por cima da 7 —
  corrigido na mesma frase.
- Notes da K3D-TASK-14: o 0,10 s de sonda saiu; o tempo de quadro fica para o `app.py`.
- Verificação: o `grep` não imprime nada (exit 1).
