---
id: CORR-WTE-131
title: "Correção: as edições do DefaultTacticsDialog não chegam ao disco no port, e chegam no ed.exe"
type: correção
category: paridade
status: pendente
depends_on: []
---

# CORR-WTE-131: o diálogo de presets não tem como confirmar no port

## Problema identificado

Editar um preset no `DefaultTacticsDialog` — renomear e mexer na geometria de
um slot — grava no `ed.exe` e **não grava** no port.

Medido em 2026-08-30 na `ptbr-remaster.bin`, pela
[PAR-TASK-06](/docs/tasks/PAR-TASK-06.md) item 4. Roteiro em
[`tools/par/8.7-preset-renomear.sh`](../../tools/par/8.7-preset-renomear.sh).

| lado | contra a imagem original |
|---|---|
| `Debug/ed.exe` | **7 faixas, 61 bytes** |
| `newWe2002` | **`IDENTICAL`** — nada foi gravado |

```text
FALHOU: 7 divergencia(s) nao esperada(s):
   374780..374790     2 byte(s)  data  before first offset+374780
   402687..402689     3 byte(s)  data  OFS_PLAYER_NAME_7+471
  2197191..2197191    1 byte(s)  data  OFS_PLAYER_ATTR_8+399
  2197272..2197283   10 byte(s)  data  OFS_PLAYER_ATTR_8+480
  2197359..2197359    1 byte(s)  data  OFS_PLAYER_ATTR_8+567
  2329440..2329609   26 byte(s)  data  OFS_KICKER+384
  4822272..4822276    5 byte(s)  data  OFS_TEAM_MIXED_CASE_NAME+223676
```

As faixas de `OFS_PLAYER_ATTR_8` e `OFS_KICKER+384` são as **não-idempotências
conhecidas**: elas aparecem aqui porque o oráculo chegou a gravar (e toda
gravação as produz) e o port não gravou nada. As outras duas —
`before first offset+374780` e `OFS_TEAM_MIXED_CASE_NAME+223676` — são as
edições do preset.

## Causa raiz

**O `IDOK` do diálogo é `NOT WS_VISIBLE` no próprio `ed.rc`**, linha 627:

```
DEFPUSHBUTTON   "OK",IDOK,197,17,50,14,NOT WS_VISIBLE
```

O `rc2ui.py` traduz isso corretamente para `visible: false` no
`DefaultTacticsDialog.ui`, e o `DefaultTacticsDialog.cpp:97` liga o botão a
`QDialog::accept`. **A tradução está certa; o efeito é que diverge.**

- No **MFC**, um `DEFPUSHBUTTON` invisível continua sendo o default do diálogo,
  e — mais importante — o original **aplica as edições enquanto se digita**,
  não só ao confirmar: o oráculo gravou com o diálogo ainda aberto.
- No **Qt**, um `QPushButton` com `visible: false` não participa: `Return` não o
  ativa, ele não pode ser clicado, e como o commit do diálogo depende de
  `accept()`, **não há caminho nenhum para aplicar as edições**.

Três caminhos de fechamento foram medidos e nenhum funciona no port: `Return`
com foco na janela, `xdotool key --window` (XSendEvent, que o Qt ignora), e
clicar na posição do botão invisível. O diálogo é, na prática, **inutilizável
no port** — o que se edita ali se perde.

## Correção

O port precisa aplicar as edições do diálogo sem depender do `accept()`, que é
o que o original faz. Duas saídas, e a primeira é a que reproduz o original:

1. **Commit por campo**, como no resto do app: ligar `editingFinished` de
   `TXT_FORMATION_NAME` e dos `TXT_SLOT_X/Y` do diálogo a uma escrita imediata
   no preset, do mesmo jeito que o `MainWindow` faz com os campos dele. O
   `accept()` continua existindo para quem tiver como chamá-lo.
2. Tornar o `IDOK` visível — **não fazer**: o `.rc` diz `NOT WS_VISIBLE`, e a
   regra do projeto é reproduzir o original, não corrigi-lo.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `src/app/DefaultTacticsDialog.cpp` | modificar — commit por campo |
| `docs/PARIDADE-FUNCIONAL.md` | modificar — o item 4 da §8.7 e a nota do `IDOK` |
| `docs/tasks/PAR-TASK-06.md` | modificar — o item 4 e o Log |

## Verificação

- [ ] `golden_check.sh` em modo `gui` com `tools/par/8.7-preset-renomear.sh`
      sai `OK`
- [ ] O preset renomeado e a geometria editada aparecem no disco do port, nos
      mesmos offsets do `ed.exe`
- [ ] O item 5 da §8.7 (`.t2002`) destrava: `CMD_IMP` e `CMD_EXP` moram nesse
      diálogo e hoje não têm como ser exercitados
- [ ] `ctest` do `newWe2002` continua verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*
