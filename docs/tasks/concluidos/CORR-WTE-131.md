---
id: CORR-WTE-131
title: "Correção: as edições do DefaultTacticsDialog não chegam ao disco no port, e chegam no ed.exe"
type: correção
category: paridade
status: concluído
depends_on: []
---

# CORR-WTE-131: o diálogo de presets não tem como confirmar no port

## Problema identificado

Editar um preset no `DefaultTacticsDialog` — renomear e mexer na geometria de
um slot — grava no `ed.exe` e **não grava** no port.

Medido em 2026-08-30 na `ptbr-remaster.bin`, pela
[PAR-TASK-06](/docs/tasks/concluidos/PAR-TASK-06.md) item 4. Roteiro em
[`tools/par/8.7-preset-renomear.sh`](../../../tools/par/8.7-preset-renomear.sh).

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

> **Esta seção foi reescrita em 2026-08-30, na execução da correção.** A
> primeira redação atribuía o defeito a "o commit do diálogo depende de
> `accept()`", e isso é **falso** — a medição abaixo mostra o que é. A redação
> antiga fica registrada no Log de Execução, porque a hipótese errada é parte
> do que se aprendeu.

**O `IDOK` do diálogo é `NOT WS_VISIBLE` no próprio `ed.rc`**, linha 627:

```
DEFPUSHBUTTON   "OK",IDOK,197,17,50,14,NOT WS_VISIBLE
```

O `rc2ui.py` traduz isso corretamente para `visible: false` no
`DefaultTacticsDialog.ui`, e o `DefaultTacticsDialog.cpp:97` liga o botão a
`QDialog::accept`. **A tradução está certa; o efeito é que diverge.**

O que **não** é a causa: o port **já** aplica as edições campo a campo. O
`MainWindow::OnPresetTactics` (`MainWindow.cpp:517`) passa
`db_.preset_formations` **por ponteiro**, e o diálogo escreve direto nele —
`OnNameEdited` no `editingFinished` do `TXT_FORMATION_NAME`, e os dois lambdas
de `editingFinished` dos `TXT_SLOT_X/Y`. Nada disso espera pelo `accept()`.

O que **é** a causa: **os dois lados são modais e os dois bloqueiam a gravação
enquanto o diálogo está de pé; o que difere é fechá-lo.**

- No **MFC**, um `DEFPUSHBUTTON` invisível continua sendo o default do diálogo:
  `Return` ativa o `IDOK`, o `EndDialog` roda, o diálogo principal volta a
  aceitar clique, e o `CMB_WRITE` grava.
- No **Qt**, um `QPushButton` com `visible: false` não é auto-default: `Return`
  não o ativa, ele não pode ser clicado, e o `exec()` continua bloqueando o
  diálogo principal. O clique em `CMB_WRITE` é engolido e o
  `Database::Save()` nunca roda — daí o `IDENTICAL`.

**A janela que sobra no `:98` enganou a primeira redação.** Depois do roteiro,
`xdotool search --onlyvisible` lista o "Modify default tactics" nos **dois**
lados — o do oráculo é uma janela X que o Wine deixa mapeada para o
`tattDlg dlg_tatt` membro, reusado entre chamadas, e não significa que o modal
esteja de pé. Quem separa os dois casos é a corrida sem o `Return` final:

```text
# oráculo, mesmo roteiro SEM o `Return` final
$ tools/golden_run.sh <copia>
tools/golden_run.sh: a gravacao nao confirmou
$ cmp roms/ptbr-remaster.bin <copia>   ->  IDENTICAL
```

Sem o `Return` o oráculo também não grava. Logo o `Return` **fecha** o modal do
`ed.exe`, e é exatamente isso que falta ao port.

## Correção

O port precisa de um caminho de confirmação para o diálogo, que é o que o
`DEFPUSHBUTTON` invisível dá ao original. Três saídas, e a decisão de qual não
está tomada:

1. **Tornar o `IDOK` o botão default do `QDialog`** (`setDefault(true)` mesmo
   invisível), para que `Return` chame `accept()` como no MFC. **É a que
   reproduz o original** — mas exige medir se o Qt ativa por `Return` um
   default que está invisível; se não ativar, esta saída não existe e as outras
   duas é que valem.
2. **Tratar `Return` no `keyPressEvent` do diálogo**, chamando `accept()`.
   Reproduz o efeito sem depender de o Qt honrar um default invisível.
3. Tornar o `IDOK` visível — **não fazer**: o `.rc` diz `NOT WS_VISIBLE`, e a
   regra do projeto é reproduzir o original, não corrigi-lo.

**Commit por campo não entra na lista**: já existe, e não é o que falta.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `src/app/DefaultTacticsDialog.cpp` | modificar — commit por campo |
| `docs/PARIDADE-FUNCIONAL.md` | modificar — o item 4 da §8.7 e a nota do `IDOK` |
| `docs/tasks/concluidos/PAR-TASK-06.md` | modificar — o item 4 e o Log |

## Verificação

- [x] `golden_check.sh` em modo `gui` com `tools/par/8.7-preset-renomear.sh`
      sai `OK`
- [x] O preset renomeado e a geometria editada aparecem no disco do port, nos
      mesmos offsets do `ed.exe`
- [x] O item 5 da §8.7 (`.t2002`) destrava: `CMD_IMP` e `CMD_EXP` moram nesse
      diálogo e hoje não têm como ser exercitados
- [x] `ctest` do `newWe2002` continua verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-30 — **PARCIAL: nada corrigido, diagnóstico
refeito.**

**Resumo do que foi feito:**

A evidência foi reproduzida e **o sintoma continua**: com
`tools/par/8.7-prelude.sh` + `tools/par/8.7-preset-renomear.sh`, o oráculo
grava **8 faixas / 63 bytes** contra a imagem original — incluindo as duas do
preset, `before first offset+374780` e `OFS_TEAM_MIXED_CASE_NAME+223676` — e a
cópia do port sai `IDENTICAL`, sem nem as não-idempotências que toda gravação
produz. Ou seja, no port o `Save()` **não chega a rodar**.

**A correção descrita não foi implementada, porque ela já está no código.** O
`DefaultTacticsDialog` faz commit por campo desde sempre, direto em
`db_.preset_formations`, que o `MainWindow::OnPresetTactics` passa por
ponteiro. Implementar "exatamente a seção Correção" seria um no-op, e fecharia
a CORR com o golden ainda vermelho.

**As três medições que refizeram o diagnóstico:**

1. **Sonda de janela no port**, depois do roteiro: o `DefaultTacticsDialog`
   (481×297) continua mapeado, o `golden_gui.sh` toma **ele** pela confirmação
   de gravação, imprime "gravado", e o arquivo sai intacto.
2. **Mesma sonda no oráculo**: o "Modify default tactics" (482×297) **também**
   aparece mapeado. Foi o que induziu a primeira redação a concluir que o
   original gravava com o diálogo aberto. O `dlg_tatt` do original é objeto
   **membro** (`edDlg.cpp:8434` chama `DoModal()` nele), e o Wine deixa a
   janela X mapeada depois do `EndDialog`.
3. **O desempate — oráculo sem o `Return` final**: `a gravacao nao confirmou`,
   e a cópia sai `IDENTICAL`. O modal do `ed.exe` bloqueia igual; o que o
   `Return` faz é **fechá-lo**, via o `IDOK` que continua sendo o default do
   diálogo apesar do `NOT WS_VISIBLE`.

As seções **Causa raiz** e **Correção** acima foram reescritas com isso.

**Problemas encontrados:**

**A hipótese errada era plausível e barata de acreditar**, e o que a
desmontou foi um único controle: rodar o roteiro **sem** o último `Return`.
Sonda de janela não distingue "modal de pé" de "janela X que o Wine não
destruiu" — no oráculo as duas coisas se parecem.

**A saída a implementar depende de uma medição que não foi feita:** se o Qt
ativa por `Return` um botão default **invisível**. Se ativar, a saída 1 é a
fiel e é uma linha; se não, é a 2. Escolher sem medir seria trocar uma
divergência conhecida por uma não medida — o mesmo erro que a
[CORR-WTE-127](/docs/tasks/concluidos/CORR-WTE-127.md) já cobrou uma vez.

**Pendências:**

- implementar a saída 1 ou a 2, depois de medir qual funciona;
- re-rodar `golden_check.sh` em modo `gui` com o roteiro do item 4;
- conferir se o item 5 da §8.7 (`.t2002`) destrava, já que `CMD_IMP` e
  `CMD_EXP` moram neste diálogo;
- marcar o item 4 da §8.7 e o Log da PAR-TASK-06 **só depois** disso.

**Arquivos criados/modificados:**

- `docs/tasks/concluidos/CORR-WTE-131.md` — as seções **Causa raiz** e **Correção**
  reescritas com o medido, e este Log

---

## Log de Execução — 2026-08-30, a implementação

**Executado em:** 2026-08-30

**Resumo do que foi feito:**

Medida a saída 1 e **descartada**: `setDefault(true)` no `IDOK` invisível
**não muda nada** — o diálogo continua de pé depois do `Return` e a cópia sai
`IDENTICAL`. O Qt pula um botão default que não está visível, que era
exatamente a dúvida que a seção **Correção** mandava resolver antes de
escolher.

Implementada a **saída 2**: `DefaultTacticsDialog::keyPressEvent` trata
`Return`/`Enter` sem modificador e chama `accept()`; todo o resto, `Escape`
inclusive, segue com o `QDialog`, que rejeita — a mesma saída que o `IDCANCEL`
dava no original.

A ordem sai de graça e é a certa: o evento só chega ao diálogo depois de o
`QLineEdit` focado ignorá-lo, e ele já emitiu `returnPressed`/
`editingFinished` — então o campo em edição é gravado **antes** de a janela
fechar, como no MFC.

**Medições, na `ptbr-remaster.bin` com `8.7-prelude.sh` + `8.7-preset-renomear.sh`:**

| | diálogo depois do roteiro | cópia contra a imagem original |
|---|---|---|
| antes | de pé | `IDENTICAL` |
| saída 1 (`setDefault`) | **de pé** | `IDENTICAL` |
| saída 2 (`keyPressEvent`) | **fechou** | **7 faixas / 48 bytes** |

As duas faixas do preset saem nos mesmos offsets do oráculo:
`before first offset+374780` (o nome) e `OFS_TEAM_MIXED_CASE_NAME+223676` (a
geometria do slot). As outras cinco são as não-idempotências que toda gravação
produz. O oráculo dá 8 faixas / 63 bytes porque escreve também o slot 64
conhecido, que o port preserva — e é por isso que o golden fecha:

```text
$ R="$(cat tools/par/8.7-prelude.sh tools/par/8.7-preset-renomear.sh)"
$ WE2002_GOLDEN_MODE=gui GOLDEN_EDIT="$R" GOLDEN_GUI_EDIT="$R" \
    bash tools/golden_check.sh roms/ptbr-remaster.bin
OK: identico ao oraculo, exceto o slot 64 conhecido (405724..405739)
```

`ctest --test-dir build -E golden` 4/4; `we2002_tests` 69 checks, 0 falhas.

**Problemas encontrados:**

**A saída "fiel" não existia.** A seção Correção classificava o botão default
como "a que reproduz o original" e o `keyPressEvent` como a alternativa; medido,
a primeira não funciona no Qt e a segunda é a única que reproduz o efeito. O
que se reproduz é o **comportamento** — `Return` confirma —, não o mecanismo,
porque o mecanismo do MFC não tem equivalente aqui.

**O item 5 da §8.7 continua `[ ]`, e isso é de propósito.** O que a CORR
destravou foi a saída do diálogo: `CMD_IMP` e `CMD_EXP` agora podem ser
exercitados e o resultado pode ser gravado. Medir a ida e volta do `.t2002` é o
item da [PAR-TASK-06](/docs/tasks/concluidos/PAR-TASK-06.md), não desta correção.

**Arquivos criados/modificados:**

- `src/app/DefaultTacticsDialog.hpp` — a declaração do `keyPressEvent`
- `src/app/DefaultTacticsDialog.cpp` — o override, com o porquê e a medição da
  saída descartada
- `docs/PARIDADE-FUNCIONAL.md` — §8.7: o item 4 fechado com as faixas, o item 5
  destravado, e a nota do `IDOK` dizendo o que o conserto foi; §7, para a linha
  do `Return` não valer para o `DefaultTacticsDialog`
- `docs/tasks/concluidos/PAR-TASK-06.md` — os dois itens e o Log
