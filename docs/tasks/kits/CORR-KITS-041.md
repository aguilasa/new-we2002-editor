---
id: CORR-KITS-041
---

# CORR-KITS-041 — Escrever no Log como comando a captura sobre a ROM golden

Origin: [KITS-TASK-36](/docs/tasks/kits/36-ui-i18n.md)

## Problem

Para o critério 5 da KITS-TASK-36 ("Capturas `--screenshot` em en-US e pt-BR sobre a ROM golden"), o bloco de evidência do Log tem uma linha de lugar, `$ (o mesmo estado sobre roms/golden-european-deluxe.bin)`, seguida de duas linhas "wrote". O comando que produziu as capturas da ROM golden não está escrito. As capturas reproduzem quando o comando é escrito por extenso.

## Evidência

```text
$ grep -c '^\$ (o mesmo estado' docs/tasks/kits/36-ui-i18n.md
1
$ export DISPLAY=:98 XAUTHORITY=; for L in en-US pt-BR; do work/venv-looks/bin/python tools/kits/ui/app.py roms/golden-european-deluxe.bin --lang $L --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot <scratch>/golden-$L.png; done
wrote .../golden-european-deluxe-en-US.png, 980x640
wrote .../golden-european-deluxe-pt-BR.png, 980x640
```

(linha de status: "... 1 of the 16 sectors read (8415) are marked Form 2 with the data in the Form 1 layout ...; read as Form 1.")

## Root cause

O Log abreviou um comando repetido sobre uma segunda ROM (inferido do texto).

## Fix

No Log da `docs/tasks/kits/36-ui-i18n.md` (critério 5), trocar a linha de lugar pelo laço literal sobre `roms/golden-european-deluxe.bin`. Só o Log muda. A captura golden não é comparável à de referência japonesa (`--compare` dá 61,02 %, outro disco): o Log deve dizer que ela foi só olhada, não comparada.

## Arquivos a criar ou modificar

- `docs/tasks/kits/36-ui-i18n.md`

## Verificação

```sh
grep -c '^\$ (o mesmo estado' docs/tasks/kits/36-ui-i18n.md
```

Dá 1 hoje; 0 depois do conserto.

## Log de Execução

### 2026-10-03

Reproduzido na HEAD `b5f4730`: `grep -c '^\$ (o mesmo estado' docs/tasks/kits/36-ui-i18n.md` dá `1`.

Conserto: a linha de lugar trocada pelo laço literal, rodado aqui com os mesmos caminhos do Log (regravou `work/kits-ui-golden-*.png`), e a saída colada inteira — três linhas por captura, com a nota de Form 2 do núcleo. Logo abaixo do bloco, a frase de que a golden foi só olhada, com a medida:

```
$ export DISPLAY=:98 XAUTHORITY=; for L in en-US pt-BR; do work/venv-looks/bin/python tools/kits/ui/app.py roms/golden-european-deluxe.bin --lang $L --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot work/kits-ui-golden-$L.png; done
  wrote work/kits-ui-golden-en-US.png, 980x640
  TEX_00 · image work bitmap, 1st set · [...] read as Form 1.
  window up, at -32000,-32000
  wrote work/kits-ui-golden-pt-BR.png, 980x640
  TEX_00 · image bitmap de trabalho, 1º conjunto · [...] read as Form 1.
  window up, at -32000,-32000
$ python3 tools/kits/ui_check.py --compare work/kits-ui-linux.png work/kits-ui-golden-en-US.png | tail -2
382703 of 627200 pixels differ (61.02 %)
FAIL  61.02 % differ, above the 5.0 % limit
$ grep -c '^\$ (o mesmo estado' docs/tasks/kits/36-ui-i18n.md
0
```
- **Closed** — commit `997a217` (2026-10-03): docs(kits): write the golden-ROM capture as a command in the KITS-TASK-36 log
  - Files (`git show --name-status 997a217`):
    - `M docs/tasks/kits/36-ui-i18n.md`
    - `M docs/tasks/kits/CORR-KITS-041.md`
