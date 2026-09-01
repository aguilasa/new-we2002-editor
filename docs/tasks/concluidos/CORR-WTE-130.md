---
id: CORR-WTE-130
title: "Correção: o roteiro da §8.5 troca completa por incompleta, e o PAR_INCOMPLETE=1 roda a completa"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-130: a caixa marcada é a substituição **completa**, e o roteiro diz o contrário

## Problema identificado

O cabeçalho do `tools/par/8.5-selecao-nacional.sh` afirma:

> `CHK_COMPLETE_SWAP` (19,197,93,10) tem o rótulo "incomplete substitution":
> **DESMARCADO é a troca completa** (os dois jogadores trocam de lugar) e
> **MARCADO é a incompleta** (o de origem é duplicado). `PAR_INCOMPLETE=1`
> marca a caixa.

**As duas atribuições estão invertidas**, e a variável faz o oposto do nome:

| estado da caixa | o que o código faz | quantos registros toca |
|---|---|---:|
| **marcada** | *complete substitution* — os dois jogadores trocam de lugar | **2** |
| **desmarcada** | *incomplete* — o escolhido é duplicado no slot | **1** |

Como `PAR_INCOMPLETE=1` **marca** a caixa, pedir `PAR_INCOMPLETE=1` roda a
substituição **completa**. Quem quiser a incompleta e confiar no nome recebe a
outra, sem aviso.

O erro não invalida medição nenhuma: o roteiro exercita os dois modos de todo
jeito, e o golden dos dois saiu `OK` nesta revisão. Ele quebra **reuso** — a
§8.9 (operações em massa) e qualquer nova corrida que precise de um modo
específico.

O mesmo par invertido aparece no Log da
[PAR-TASK-05](/docs/tasks/concluidos/PAR-TASK-05.md), na tabela de evidência:

> | complete × incomplete | 1 registro de jogador contra **2** |

Lida na ordem em que está escrita, ela diz que a completa toca 1 e a incompleta
toca 2 — o inverso do medido. **A §8.5 do
[/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) está certa**, porque
descreve por estado de caixa e não por nome: "desmarcado toca **um** registro
[...], marcado toca **dois**".

## Evidência

O port, em `src/app/PlayerSelectDialog.cpp:254-265`:

```cpp
if (ui_->CHK_COMPLETE_SWAP->isChecked()) {
    // "Complete substitution": the two players trade places, so the
    // squad the chosen player came from gets the one being replaced.
    we2002::Player spare;
    CopyPlayerFields(spare, db_.players[chosen], true);
    CopyPlayerFields(db_.players[chosen], db_.players[slot_player_], true);
    CopyPlayerFields(db_.players[slot_player_], spare, true);
} else {
    // "Incomplete": the chosen player is duplicated into the slot and
    // stays where they were as well.
    CopyPlayerFields(db_.players[slot_player_], db_.players[chosen], true);
}
```

O original faz o mesmo — `legacy/mfc/selezDlg.cpp:546`, `if(chk_sc.GetCheck()
== 1)` seguido do "appoggia giocatore da sostituire", que é a troca de três
tempos. **O comportamento do port está certo**; errado está o texto do roteiro.

E o rótulo confirma, porque ele é reescrito ao alternar
(`PlayerSelectDialog.cpp:201-205`): marcada mostra `complete substitution`,
desmarcada mostra `incomplete substitution`.

Medido nesta revisão, na `ptbr-remaster.bin`, com o controle positivo de cada
corrida contra a imagem original:

```text
PAR_INCOMPLETE=0   7 run(s)   ... OFS_PLAYER_NAME+0, OFS_PLAYER_ATTR+0
PAR_INCOMPLETE=1   9 run(s)   ... os mesmos, mais dois

$ golden_compare.py <copia PAR_INCOMPLETE=0> <copia PAR_INCOMPLETE=1>
2 run(s), 18 byte(s) differ
    388836   388841   6   6   165  data  OFS_PLAYER_NAME+1044
   2180684  2180695  12  12   927  data  OFS_PLAYER_ATTR_1+356
```

`PAR_INCOMPLETE=1` é a corrida que toca **dois** registros — a completa.

Os dois goldens saíram
`OK: identico ao oraculo, exceto o slot 64 conhecido (405724..405739)`, como os
outros cinco da seção.

## Causa raiz

O rótulo do controle no `.rc` é o do estado **desmarcado**
(`incomplete substitution`), e o cabeçalho o leu como se nomeasse a caixa
marcada.

## Correção

### Arquivo: `tools/par/8.5-selecao-nacional.sh`

Inverter as duas frases do cabeçalho e renomear a variável para o que ela faz:

```sh
# CHK_COMPLETE_SWAP (19,197,93,10) nasce DESMARCADO e com o rótulo
# "incomplete substitution", que é o nome do estado em que está: desmarcado
# duplica o escolhido no slot (1 registro), marcado troca os dois de lugar
# (2 registros) e o rótulo passa a "complete substitution".
# PAR_COMPLETA=1 marca a caixa.
```

Manter `PAR_INCOMPLETE` como sinônimo aceito não vale a pena: ninguém depende
dele fora desta seção, e um nome invertido preservado por compatibilidade é o
mesmo problema com uma nota de rodapé.

### Arquivo: `docs/tasks/concluidos/PAR-TASK-05.md`

Na tabela de evidência do Log, escrever a linha pelo estado da caixa, como a
§8.5 já faz — `desmarcada (incompleta) 1 registro × marcada (completa) 2`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/par/8.5-selecao-nacional.sh` | modificar |
| `docs/tasks/concluidos/PAR-TASK-05.md` | modificar |

## Verificação

- [x] `grep -n PAR_INCOMPLETE tools/ docs/` não devolve nada
- [x] O cabeçalho do roteiro diz que **marcada** é a completa, de 2 registros
- [x] `PAR_COMPLETA=1` produz as duas faixas a mais
      (`OFS_PLAYER_NAME+1044` e `OFS_PLAYER_ATTR_1+356`) no controle positivo,
      e `PAR_COMPLETA=0` não
- [x] Os dois goldens continuam `OK`
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-29

**Resumo do que foi feito:**

O cabeçalho do roteiro passou a descrever a caixa **pelo estado**, com a razão
de o rótulo enganar: `CHK_COMPLETE_SWAP` nasce desmarcado e mostra
`incomplete substitution`, que é o nome do estado em que ele **está** — o
rótulo é reescrito ao alternar (`PlayerSelectDialog.cpp:201-205`). A variável
virou `PAR_COMPLETA`, sem sinônimo.

Remedido nos dois modos, na `ptbr-remaster.bin`, os dois goldens `OK`:

| | faixas no controle positivo | registros de jogador |
|---|---:|---|
| `PAR_COMPLETA=0` (desmarcada, *incomplete*) | 7 | `OFS_PLAYER_NAME+0`, `OFS_PLAYER_ATTR+0` — **1** |
| `PAR_COMPLETA=1` (marcada, *complete*) | 9 | os mesmos, mais `OFS_PLAYER_NAME+1044` e `OFS_PLAYER_ATTR_1+356` — **2** |

E as duas cópias uma contra a outra, que isola o que o modo muda:

```text
$ python3 tools/golden_compare.py port-0.bin port-1.bin
2 run(s), 18 byte(s) differ
    388836    388841    6    6   165  data  OFS_PLAYER_NAME+1044
   2180684   2180695   12   12   927  data  OFS_PLAYER_ATTR_1+356
```

`PAR_COMPLETA=1` é a de dois registros — a completa, como o nome agora diz.

**Problemas encontrados:**

**A §8.5 do inventário não nomeia roteiro em item nenhum**, só no cabeçalho
("Roteiros em `tools/par/8.5-*.sh`"). Com a variável renomeada, quem ler o item
1 não tem como re-rodar nenhum dos dois modos — a incompletude passa a doer por
causa desta correção. Os quatro itens ganharam o nome do seu roteiro, e o item
1 também o da variável, em **commit próprio** de reconciliação.

**Arquivos criados/modificados:**

- `tools/par/8.5-selecao-nacional.sh` — cabeçalho e nome da variável
- `docs/tasks/concluidos/PAR-TASK-05.md` — a linha da tabela de evidência, escrita pelo
  estado da caixa
- `docs/PARIDADE-FUNCIONAL.md` — §8.5, no commit de reconciliação
