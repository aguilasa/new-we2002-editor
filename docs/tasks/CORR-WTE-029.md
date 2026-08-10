---
id: CORR-WTE-029
title: "Correção: o Log da WTE-TASK-16 diz que a reconciliação do `fase-2.md` saiu em commit próprio, e ela saiu no mesmo commit"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-029: a reconciliação da fase 2 não teve commit próprio

## Problema identificado

O Log de Execução da [WTE-TASK-16](/docs/tasks/16-gerador-de-tabelas.md) afirma
duas vezes que a mudança do `check_fase2.py` e do `wte/re/fase-2.md` foi
separada num commit próprio:

- em **Arquivos criados/modificados**: «`wte/tools/check_fase2.py`,
  `wte/re/fase-2.md` — reconciliação, em commit próprio (ver abaixo)»;
- em **Problemas encontrados**, item 2: «Reconciliação em commit separado, com
  esta task nomeada no corpo».

Não existe esse commit. Os dois arquivos entraram no **mesmo** commit da task,
`6dab6bb`, e o corpo dele diz o contrário com todas as letras — a decisão foi
deliberada, e a razão está escrita ali:

> That reconciliation rides along here rather than in a commit of its own
> because this task is what caused it, and splitting it would leave one commit
> with a red `make -C wte check`.

Ou seja: a decisão está certa e bem justificada no commit; quem ficou
desatualizado foi o Log. O «(ver abaixo)» também não aponta para nada — não há
nada abaixo dele no arquivo da task.

Por que importa: o Log é a única narrativa que sobrevive fora do `git log`, e é
dele que a revisão seguinte parte. Log que manda procurar um commit inexistente
custa o tempo de procurá-lo, e é exatamente o tipo de afirmação que o
`/revisar` existe para pegar.

## Evidência

```console
$ git log --oneline -- wte/tools/check_fase2.py wte/re/fase-2.md | head
6dab6bb feat(wte): generate the Pascal offsets and tables from we2002_core
6848208 docs(wte): close phase 2, and drop the "navigable" criterion it could never meet

$ git show --stat 6dab6bb | tail -12
 docs/tasks/16-gerador-de-tabelas.md |  76 ++++-
 docs/tasks/progresso.md             |   4 +-
 wte/re/fase-2.md                    |   6 +
 wte/src/we2002_offsets.pas          | 106 +++++++
 wte/src/we2002_tables.pas           | 602 +++++++++++++++++++++++++++++++++++
 wte/tests/test_offsets.cpp          | 139 ++++++++
 wte/tests/test_offsets.pas          | 146 +++++++++
 wte/tools/check_fase2.py            |  30 +-
 wte/tools/gen_tables_pas.py         | 615 ++++++++++++++++++++++++++++++++++++
 wte/tools/test_gen_tables_pas.py    | 224 +++++++++++++
 10 files changed, 1935 insertions(+), 13 deletions(-)
```

`6848208` é o commit de fechamento da fase 2 (WTE-TASK-14), anterior à task 16.
Não há nenhum commit entre `35c2002` e `6dab6bb`.

## Causa raiz

O Log foi redigido com o plano de dividir o commit e não foi reescrito quando a
divisão foi abandonada — a razão do abandono ficou só no corpo do commit.

## Correção

### Arquivo: `docs/tasks/16-gerador-de-tabelas.md`

Trocar as duas afirmações pela que o commit registra, sem perder a razão:

- Em **Arquivos criados/modificados**, a linha da reconciliação passa a dizer
  que os dois arquivos entraram **no mesmo commit** da task, e por quê:
  separá-los deixaria um commit com `make -C wte check` vermelho.
- No item 2 de **Problemas encontrados**, trocar «Reconciliação em commit
  separado, com esta task nomeada no corpo» pela mesma constatação, e remover o
  «(ver abaixo)», que não tem destino.

Nada de código muda: o `check_fase2.py` e o `fase-2.md` estão corretos, o
`make -C wte check` está verde, e a exclusão dos `we2002_*.pas` do censo da
casca está documentada dentro do próprio `fase-2.md`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/16-gerador-de-tabelas.md` | modificar |

## Verificação

- [ ] `grep -n 'commit próprio\|commit separado\|ver abaixo' docs/tasks/16-gerador-de-tabelas.md`
      não devolve nada
- [ ] `git log --oneline -- wte/tools/check_fase2.py wte/re/fase-2.md` continua
      mostrando `6dab6bb` como o commit da reconciliação, e o Log agora diz isso
- [ ] `make -C wte check` continua verde (nenhum arquivo gerado é tocado)
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

Trocadas as duas afirmações do Log da WTE-TASK-16 pela que o commit
`6dab6bb` registra: a reconciliação do `check_fase2.py` e do `fase-2.md`
entrou **no mesmo commit** da task, e a razão vai junto — separá-la deixaria
um commit com `make -C wte check` vermelho, porque o `fase-2.md` só volta a
bater depois de as duas unidades novas existirem. O `(ver abaixo)` sem destino
saiu.

Executada fora do `/corrigir`: o defeito foi **criado pela própria leva** que
escreveu a WTE-TASK-16, e apareceu na varredura de concorrência pedida logo
depois. Corrigir na hora custa menos que deixar aberto e arriscar que alguém
"conserte" um arquivo já certo.

**Problemas encontrados:** Nenhum.

**Arquivos criados/modificados:** `docs/tasks/16-gerador-de-tabelas.md`
