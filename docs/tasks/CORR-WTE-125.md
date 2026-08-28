---
id: CORR-WTE-125
title: "Correção: Escape num combo de cobrador descarta a navegação no port e não no ed.exe"
type: correção
category: paridade
status: pendente
depends_on: []
---

# CORR-WTE-125: `Escape` no combo de cobrador diverge

## Problema identificado

Navegar a lista de um combo de cobrador **com as setas** e desistir com
`Escape` grava no `ed.exe` e **não** grava no port.

Medido em 2026-08-28 na `ptbr-remaster.bin`, pela
[PAR-TASK-03](/docs/tasks/PAR-TASK-03.md) item 1. Roteiro: selecionar
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
| `docs/tasks/PAR-TASK-03.md` | modificar — o item 1 e o Log |

## Verificação

- [ ] `Escape` depois de navegar grava o valor navegado, igual ao `ed.exe`
- [ ] `Escape` sem navegar não grava nada
- [ ] O item 2 da §8.3 (escolher + `Tab`) continua verde
- [ ] `golden_check.sh` em modo `gui` com o roteiro do item 1 sai `OK`
- [ ] A §3.5 não afirma mais que o original não grava ao navegar
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*
