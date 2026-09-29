---
id: CORR-LOOKS-106
title: "A janela cai em toda linha de cabeça quando o fontconfig põe um WOFF na reserva"
origin: LOOKS-TASK-39
severity: high
files: [tools/looks/ui/looks_set.py]  # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-29
done_commit: 1101cb5
---

# CORR-LOOKS-106 — A janela cai em toda linha de cabeça quando o fontconfig põe um WOFF na reserva

Origin: [LOOKS-TASK-39](/docs/tasks/looks/39-o-texto-da-ajuda.md)

## Problem

Nesta máquina Linux, desde 2026-09-29, a janela da `LOOKS SET` cai com
*segmentation fault* (saída 139) assim que o cursor entra em qualquer linha de
cabeça: SKIN, HAIR, H.COL, FACE, H.F.COL. As linhas de corpo inteiro não caem.
O `make looks` fica inutilizável, e o `looks_ui` do `ctest` cai junto.

## Evidência

```text
$ work/venv-looks/bin/python tools/looks/ui/app.py --state 2 --keys Down --smoke; echo $?
139
$ work/venv-looks/bin/python tools/looks/ui/app.py --state 2 --keys Up --smoke; echo $?
0
$ work/venv-looks/bin/python -X faulthandler tools/looks/ui/app.py --state 2 --keys Down --smoke
Fatal Python error: Segmentation fault
  File ".../tools/looks/ui/looks_set.py", line 585 in paintEvent
```

A linha 585 era o `drawText` da caixa de ajuda. A ajuda das linhas de cabeça
traz o glifo do botão, U+25A0 ("Skin Colour ■ Turn"). Reproduzido fora do
projeto, com um script de PySide6 que só desenha texto numa `QImage`, inclusive
em `QT_QPA_PLATFORM=offscreen`:

```text
Consolas "■": 139      DejaVu Sans Mono "■": 0      Consolas "é": 0      Consolas "→": 139
$ fc-match 'Consolas:charset=25a0' file
:file=/usr/share/fonts/woff/opendyslexic/OpenDyslexic-Bold.woff
```

## Root cause

O Consolas não tem U+25A0, então o Qt pede ao fontconfig uma fonte de reserva.
O cache do fontconfig foi reconstruído em 2026-09-29 às 11:57, depois das
atualizações do sistema, e passou a pôr o `OpenDyslexic-Bold.woff`
(`fonts-opendyslexic`, instalado desde abril) na frente para esse caractere. O
PySide6 6.11.2 cai ao carregar esse WOFF. Ontem a mesma corrida passava: nada no
código mudou.

O defeito do projeto é depender da reserva do sistema para um caractere que a
fonte escolhida não tem. `setFamilies(["Consolas", "DejaVu Sans Mono"])` e
`insertSubstitutions` continuam consultando a reserva e caem igual, e até
`QFontMetrics.inFontUcs4` cai.

## Fix

Em `tools/looks/ui/looks_set.py`, o `_font` recebe o texto e escolhe as
famílias pelos caracteres, sem perguntar ao Qt: texto só com caracteres latinos
(abaixo de U+0250) fica no Consolas; texto com qualquer outro põe o DejaVu Sans
Mono na frente (`FONT_FOR_SYMBOLS`), e o Consolas continua na lista para as
máquinas sem DejaVu. A caixa de ajuda passa o próprio texto. A ajuda já era
escrita numa fonte de apoio (a do jogo vem da ROM do console,
[LOOKS-TASK-39](/docs/tasks/looks/39-o-texto-da-ajuda.md)), então só muda a
família dessa linha quando ela tem o glifo.

O que não é deste repositório, e fica para o dono da máquina: o PySide6 cair
num WOFF, e o fontconfig preferir essa fonte. `sudo apt remove
fonts-opendyslexic` também tira o sintoma.

## Arquivos a criar ou modificar

- [tools/looks/ui/looks_set.py](/tools/looks/ui/looks_set.py)

## Verificação

```text
$ for k in Down Down,Down Up; do work/venv-looks/bin/python tools/looks/ui/app.py --state 2 --keys $k --smoke; echo $?; done
0
0
0
$ python3 tools/looks/selftest.py | tail -1
looks_selftest: 0 failure(s)
```

## Log de Execução

- 2026-09-29 — reproduzido na janela e num script mínimo; causa isolada no
  fontconfig e no WOFF; corrigido; janela de pé em toda linha.
- **Closed** — commit `1101cb5` (2026-09-29): fix(looks): keep the help box off Qt's system font fallback
  - Files (`git show --name-status 1101cb5`):
    - `A docs/tasks/looks/CORR-LOOKS-106.md`
    - `M docs/tasks/looks/correcoes-progresso.md`
    - `M tools/looks/ui/looks_set.py`
