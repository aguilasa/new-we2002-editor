---
id: CORR-WTE-134
title: "Correção: o `Escape` nos dez combos de papel do `DefaultTacticsDialog` diverge do original"
type: correção
category: comportamento
status: pendente
depends_on: []
---

# CORR-WTE-134: o `Escape` do combo de papel dentro do diálogo de presets

## Problema identificado

A [CORR-WTE-127](/docs/tasks/CORR-WTE-127.md) corrigiu o `Escape` depois de
navegar um combo — **nos dezesseis do `MainWindow`** (dez de papel + seis de
cobrador). O `DefaultTacticsDialog` tem **outros dez combos de papel**
(`CMB_SLOT_ROLE2..11`, os `TCMB_TAT2..11` do `.rc`), que escrevem os mesmos
`ruoli[]` — só que nos **presets**, não no time — e **eles não foram
alcançados**: não há `installEventFilter` nenhum em
[`src/app/DefaultTacticsDialog.cpp`](../../src/app/DefaultTacticsDialog.cpp).

O item 3 da §8.7 (`Escape` depois de navegar um combo de papel) está marcado
`[x]` no inventário e na [PAR-TASK-06](/docs/tasks/PAR-TASK-06.md), e a §8.7
foi fechada com "os cinco conferidos". O caminho de `Escape` deste diálogo
**nunca foi medido**, e diverge.

## Evidência

Sonda desta revisão, `ptbr-remaster.bin`, prelúdio da §8.7 mais: abrir o
`DefaultTacticsDialog` (`CMD_EDIT_PRESETS`), clicar `CMB_SLOT_ROLE2`
(199,46,38,12), três `Down`, `Escape`, clicar `TXT_FORMATION_NAME` para forçar
o killfocus, `Return` para fechar, e gravar.

```text
$ WE2002_GOLDEN_MODE=gui GOLDEN_EDIT="$R" GOLDEN_GUI_EDIT="$R" \
    tools/golden_check.sh roms/ptbr-remaster.bin
FALHOU: 1 divergencia(s) nao esperada(s):
  374189..374189  1 byte(s)  data  before first offset+374189
```

O byte, nos três arquivos (offset 374186, oito bytes):

```text
ptbr-remaster.bin 0005b5aa: 0000 0102 0607 080a     (original)
p3.bin            0005b5aa: 0000 0102 0607 080a     (port:    0x02, intacto)
o3.bin            0005b5aa: 0000 0105 0607 080a     (ed.exe:  0x05, navegado)
```

`0x02 → 0x05` com três `Down` é **exatamente** o número que a CORR-WTE-127
mediu no `MainWindow` — mesmo defeito, outro formulário.

**O caminho normal do mesmo combo não diverge**, e foi medido junto: com
`Return` no lugar do `Escape`, o golden sai
`OK: identico ao oraculo, exceto o slot 64 conhecido (405724..405739)` e o
controle positivo do port contra a imagem original acusa 6 faixas / 42 bytes,
com o byte de papel em `before first offset+374189`. O estímulo chega; o que
falha é só o `Escape`.

## Causa raiz

No original, `tattDlg` registra as duas notificações para `TCMB_TAT2..11`:
`ON_CBN_SELCHANGE` só repinta a legenda do marcador
(`changecmbtatt`, `legacy/mfc/tattDlg.cpp:237`) e **quem grava é o
`ON_CBN_KILLFOCUS`** (`exitcmbtatt`, `tattDlg.cpp:477`:
`ruoli[n] = cb->GetCurSel()+2`). As setas movem o `CurSel` do combo e o
`Escape` só fecha a lista, então o killfocus grava o item navegado.

No port o commit é `currentIndexChanged` guardado por `hasFocus()`, e o Qt
desfaz a navegação no `Escape` — o índice volta ao original e nada é escrito.

## Correção

### Arquivo: `src/app/DefaultTacticsDialog.cpp`

Reproduzir aqui o que a CORR-WTE-127 fez no `MainWindow`: instalar o
`eventFilter` no combo **e na sua `view()`**, e no `Escape` repor o índice que
a navegação deixou na linha corrente da view, antes de o Qt desfazê-la. O
diálogo já é `QDialog`; basta ele mesmo ser o filtro (`installEventFilter(this)`
nos dez `cmb_role_[i]` e nas dez `view()`), com o mesmo corpo do filtro de
[`src/app/MainWindow.cpp`](../../src/app/MainWindow.cpp) (o laço que casa
`watched` contra as views e repõe `setCurrentIndex`).

Cuidado com o commit: no `MainWindow` a escrita acontece no `FocusOut`; aqui
ela está em `currentIndexChanged` + `hasFocus()`. Repor o índice pelo filtro
tem de acabar escrevendo — se o `setCurrentIndex` do filtro rodar com o combo
já sem foco, o `hasFocus()` bloqueia a gravação e o conserto não conserta nada.
**Medir com a sonda acima antes de dar por fechado.**

### Arquivos de documentação

O item 3 da §8.7 e o da PAR-TASK-06 dizem "os dez gravam pelo **mesmo**
`FocusOut` dos seis de cobrador" — verdade para o `MainWindow`, e é preciso
dizer que existem **outros dez** no diálogo de presets, com outro caminho de
commit.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `src/app/DefaultTacticsDialog.cpp` | modificar |
| `tools/par/8.7-escape-papel-preset.sh` | criar — versionar a sonda desta CORR |
| `docs/PARIDADE-FUNCIONAL.md` | modificar — o item 3 da §8.7 |
| `docs/tasks/PAR-TASK-06.md` | modificar — o item 3 |

## Verificação

- [ ] A sonda (prelúdio + `8.7-escape-papel-preset.sh`) sai
      `OK: identico ao oraculo, exceto o slot 64 conhecido (405724..405739)`
- [ ] Controle positivo: o port contra a imagem original acusa o byte
      `before first offset+374189` **mudado para `0x05`**, e não intacto
- [ ] `tools/par/8.7-escape-papel.sh` e `8.7-escape-papel-sem-navegar.sh`
      continuam `OK` (a correção não pode mexer no `MainWindow`)
- [ ] `tools/par/8.7-preset-renomear.sh` continua `OK`
- [ ] `ctest --preset debug` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
