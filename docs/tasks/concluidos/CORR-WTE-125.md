---
id: CORR-WTE-125
title: "Correção: Escape num combo de cobrador descarta a navegação no port e não no ed.exe"
type: correção
category: paridade
status: concluído
depends_on: []
---

# CORR-WTE-125: `Escape` no combo de cobrador diverge

## Problema identificado

Navegar a lista de um combo de cobrador **com as setas** e desistir com
`Escape` grava no `ed.exe` e **não** grava no port.

Medido em 2026-08-28 na `ptbr-remaster.bin`, pela
[PAR-TASK-03](/docs/tasks/concluidos/PAR-TASK-03.md) item 1. Roteiro: selecionar
`Nation 1 - Ireland`, clicar em `CMB_KICK_LONG_FK`, três `Down`, `Escape`,
gravar.

| imagem | `teams[0].kick_long_fk` |
|---|---:|
| original | 3 |
| **`ed.exe`** | **6** |
| `newWe2002` | 3 |

```text
FALHOU: 1 divergencia(s) nao esperada(s):
  2329056..2329056  1 byte(s)  data  OFS_KICKER+0
```

Três `Down` a partir de 3 dão 6, então **o original gravou o valor navegado**.

## Causa raiz

A diferença é de framework, e está no que `Escape` significa para cada combo:

- no **MFC**, navegar com as setas move o `CurSel` do combo; `Escape` fecha a
  lista mas **mantém** a seleção nova, e o `CBN_KILLFOCUS` seguinte — disparado
  quando o clique em `CMB_WRITE` tira o foco — grava esse valor;
- no **Qt**, `Escape` no popup de um `QComboBox` **reverte** para o item que
  estava antes de abrir, e o `FocusOut` grava o valor original.

Os dois gravam em perda de foco, que é o que a §3.5 do
[PARIDADE-FUNCIONAL](/docs/PARIDADE-FUNCIONAL.md) descreve corretamente. O que
não estava previsto é que **o valor a gravar no momento do killfocus é outro**.

**A §3.5 precisa de reparo junto com o código.** Ela hoje diz:

> o original usava `CBN_KILLFOCUS` justamente para navegar a lista com as setas
> sem gravar

A primeira metade está certa e a segunda não: medido, o original **grava** o
que foi navegado. Quem não grava é o port.

## Correção

O port tem de reproduzir o original, que é a regra do projeto — a diferença é
observável e cai num campo que o jogo lê.

1. interceptar `Escape` no popup do `QComboBox` dos seis controles de cobrador
   (`CMB_KICK_*` e `CMB_CAPTAIN`), mantendo o índice navegado em vez de
   reverter — um `eventFilter` no popup, irmão do que já existe para `FocusOut`;
2. conferir que `Escape` **sem** ter navegado continua não gravando nada;
3. corrigir a frase da §3.5 do `PARIDADE-FUNCIONAL.md`.

**Cuidado com o irmão que já passa:** escolher com `Return` e sair com `Tab`
está **verde** (item 2 da mesma task, `kick_long_fk` 3 → 5 nos dois lados, os
outros cinco campos intactos). A correção não pode quebrá-lo.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `src/app/MainWindow.cpp` | modificar — o `eventFilter` dos combos de cobrador |
| `docs/PARIDADE-FUNCIONAL.md` | modificar — a frase da §3.5 e o item 1 da §8.3 |
| `docs/tasks/concluidos/PAR-TASK-03.md` | modificar — o item 1 e o Log |

## Verificação

- [x] `Escape` depois de navegar grava o valor navegado, igual ao `ed.exe`
- [x] `Escape` sem navegar não grava nada
- [x] O item 2 da §8.3 (escolher + `Tab`) continua verde
- [x] `golden_check.sh` em modo `gui` com o roteiro do item 1 sai `OK`
- [x] A §3.5 não afirma mais que o original não grava ao navegar
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-29

**Resumo do que foi feito:**

Um `eventFilter` na **view do popup** dos seis combos de cobrador
(`src/app/MainWindow.cpp`): no `KeyPress` de `Escape` ele lê a linha corrente da
view, fecha o popup e chama `setCurrentIndex` com ela, consumindo o evento. O
`FocusOut` que já existia continua sendo quem grava — o que muda é só o valor
que chega lá.

A escolha de filtrar a `view()` e não o combo é o que torna o `Escape` sem
navegação inócuo de graça: o `showPopup` põe a view na linha corrente do combo,
então quando ninguém mexeu nas setas o índice reposto é o que já estava.

**Medido na `ptbr-remaster.bin`, com os três roteiros versionados nesta
correção:**

| Roteiro | `teams[0].kick_long_fk` | golden |
|---|---|---|
| `8.3-escape-cobrador.sh` (3 `Down` + `Escape`) | original 3 → **6 no `ed.exe`, 6 no port** | `OK` |
| `8.3-escape-sem-navegar.sh` (`Escape` na hora) | **3 nos dois**, sem `OFS_KICKER+0` no controle | `OK` |
| `8.3-escolher-e-tab.sh` (2 `Down` + `Return` + `Tab`) | **3 → 5 nos dois**, outros cinco intactos | `OK` |

Antes do conserto o primeiro dava `2 run(s)` no golden — a faixa conhecida mais
`2329056..2329056  OFS_KICKER+0` —, com o oráculo em 6 e o port em 3. Depois,
`1 run(s)`, só a faixa conhecida. Confirmado também pelo `dump_estado` nos seis
campos de cobrador, e não só no byte.

O item 2 (`Return` + `Tab`), que já passava, foi remedido depois do conserto e
continua verde — era a guarda que a CORR pedia.

`ctest -E golden` 4/4; `we2002_tests` 69 checks, 0 falhas. E o caminho literal
da Verificação:

```text
$ R="$(cat tools/par/8.3-escape-cobrador.sh)"
$ WE2002_GOLDEN_MODE=gui GOLDEN_EDIT="$R" GOLDEN_GUI_EDIT="$R" \
    bash tools/golden_check.sh roms/ptbr-remaster.bin
OK: identico ao oraculo, exceto o slot 64 conhecido (405724..405739)
```

**Problemas encontrados:**

**A §8.3 também não tinha roteiro versionado**, como a §8.2 não tinha — a mesma
lacuna que a [CORR-WTE-123](/docs/tasks/concluidos/CORR-WTE-123.md) fechou para a §8.1. Os
três desta seção foram escritos aqui, e a reprodução da evidência já saiu do
primeiro.

**A frase da §3.5 estava meio certa, e o reparo teve de dizer qual metade.** Ela
atribuía ao `CBN_KILLFOCUS` o efeito de "navegar sem gravar". Não gravar **na
hora** é verdade e continua no texto; o que não existe é o descarte — o valor
navegado sobrevive ao `Escape` no MFC. O parágrafo reescrito separa as duas
coisas e diz onde os frameworks divergiam.

**Escopo deliberadamente estreito.** O filtro cobre os seis combos de cobrador,
não os dez de papel tático (`cmb_role_`): estes gravam por
`currentIndexChanged`, não pelo mesmo caminho, e a §8.7 é quem os mede. Alargar
sem medida seria trocar uma divergência conhecida por uma não medida.

> **Este parágrafo estava errado, e a
> [CORR-WTE-127](/docs/tasks/concluidos/CORR-WTE-127.md) o corrigiu no dia seguinte.** Os
> dez combos de papel gravam pelo **mesmo** `FocusOut`, no mesmo
> `eventFilter`; o `currentIndexChanged` deles só repinta a legenda do
> marcador e não toca em dado nenhum. E a §8.7 não media este caminho — o
> único item dela sobre papel era "trocar papel e conferir a legenda". Medido:
> três `Down` e `Escape` num `CMB_SLOT_ROLE2` reprovavam o golden em
> `OFS_FORMATIONS+0`. O filtro foi estendido aos dezesseis.

**Arquivos criados/modificados:**

- `src/app/MainWindow.cpp` — o `eventFilter` do popup e o `installEventFilter`
  na `view()` dos seis
- `tools/par/8.3-escape-cobrador.sh`, `8.3-escape-sem-navegar.sh`,
  `8.3-escolher-e-tab.sh` — criados
- `docs/PARIDADE-FUNCIONAL.md` — a frase da §3.5 e os itens 1 e 2 da §8.3
- `docs/tasks/concluidos/PAR-TASK-03.md` — os itens, a Definição de pronto, o `status` e o
  adendo no Log
- `docs/tasks/concluidos/progresso.md` — a linha da PAR-TASK-03 no anexo
