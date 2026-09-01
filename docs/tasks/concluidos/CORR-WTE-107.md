---
id: CORR-WTE-107
title: "Correção: a lista de arquivos da WTE-TASK-35 não menciona o repasse escrito na WTE-TASK-36"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-107: a lista da WTE-TASK-35 omite o repasse para a 36

## Problema identificado

O commit que fechou a
[WTE-TASK-35](/docs/tasks/concluidos/35-divergencias-deliberadas.md) (`2e70784`) tocou
**nove** arquivos. A lista do Log nomeia oito e defere o resto ao
`git show --stat`. O que falta nela é
[`docs/tasks/concluidos/36-buffers-e-truncamento.md`](/docs/tasks/concluidos/36-buffers-e-truncamento.md),
com 27 linhas novas.

**E este é o pior a faltar dos nove**, porque é o único que não é arquivo de
ferramenta: é o **repasse**. Ele escreve na task 36 que ela é a dona da única
linha que a 35 deixou aberta, o que a 36 deve devolver, em que forma, e que a
régua nova — se ganhar isenção — tem de passar pelo `check_divergencias.py`.

É exatamente o remédio que a [CORR-WTE-105](/docs/tasks/concluidos/CORR-WTE-105.md) pediu
uma task antes: *"pendência encaminhada por prosa de uma task para outra, sem
entrada no destino"*. A 35 fez certo — e não registrou que fez.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
git show --stat --format= 2e70784 | tail -3
grep -n "36-buffers" docs/tasks/35-divergencias-deliberadas.md
```

```text
 wte/tools/golden_suite.sh                 |  17 ++
 wte/tools/test_compara_tela.py            |  46 ++++-
 9 files changed, 765 insertions(+), 30 deletions(-)
```

O `grep` acha a task 36 **citada uma vez** no corpo (linha 333, como dona
nomeada do truncamento) e **nenhuma** na lista de arquivos:

```text
333:      nomeado** ([WTE-TASK-36](/docs/tasks/36-buffers-e-truncamento.md)), que é
```

O que o commit escreveu lá, e que a lista não conta:

```text
+> **Entrada aberta pela WTE-TASK-35 em 2026-08-25 — esta task é a dona do
+> último item em aberto do registro de divergências.**
...
+> **O que a 36 deve devolver para a 35, e em que forma.** [...] a entrada
+> **nasce aqui e volta para o `divergencias.md`** com os seis campos
```

| Afirmado | Medido |
|---|---:|
| oito arquivos nomeados no Log | **nove** no commit |

## Causa raiz

O repasse foi escrito no fim da execução, junto com a decisão de onde a linha
aberta ia morar, e não voltou para a lista de arquivos.

## Correção

### Arquivo: `docs/tasks/concluidos/35-divergencias-deliberadas.md`

Acrescentar aos modificados:

> `docs/tasks/concluidos/36-buffers-e-truncamento.md` — o repasse: a 36 passa a ser a dona
> declarada da única linha em aberto da §7 do registro, com a forma de devolução
> escrita (os seis campos) e a obrigação de passar pelo `check_divergencias.py`
> se a régua ganhar isenção

É a quarta vez que a lista de uma task fica devendo um item
([CORR-WTE-078](/docs/tasks/concluidos/CORR-WTE-078.md),
[-087](/docs/tasks/concluidos/CORR-WTE-087.md), [-099](/docs/tasks/concluidos/CORR-WTE-099.md)). A
099 já recomendou fechar a porta no `01-executar.md`, conferindo a lista contra
`git show --stat --format= HEAD` ao fechar a task; enquanto isso não entra, a
conta continua sendo paga uma revisão por vez.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/concluidos/35-divergencias-deliberadas.md` | modificar |

## Verificação

- [x] A lista da task cobre os nove arquivos de `git show --stat --format= 2e70784`
      — conferido por script, 9 de 9
- [x] `make -C wte check` verde (809 testes)
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-25

**Resumo do que foi feito:**

O `docs/tasks/concluidos/36-buffers-e-truncamento.md` entrou na lista de arquivos da
WTE-TASK-35, dizendo o que ele é — o **repasse**, e não mais um arquivo de
ferramenta: a 36 passa a ser a dona declarada da única linha em aberto da §7,
com a forma de devolução (os seis campos) e a obrigação de passar pelo
`check_divergencias.py` se a régua ganhar isenção.

Conferido por script contra `git show --stat --format= --name-only 2e70784`:
**9 de 9** cobertos, contando o próprio arquivo da task pela forma
convencional ("este arquivo").

**Problemas encontrados:**

**A regra que deveria ter pego isto já existe — e o contador dela envelheceu.**
A [CORR-WTE-099](/docs/tasks/concluidos/CORR-WTE-099.md) recomendou fechar a porta, e
fechou: o `01-executar.md` tem o bloco *"a lista de arquivos se confere contra o
commit, não contra a memória"*, com o `git show --stat --format= HEAD`, e o
wrapper `.claude/commands/executar.md` reafirma. Os dois diziam **três vezes**
— esta é a quarta, e o contador é o que dá peso à regra. Atualizados os dois,
com a -107 nomeada e o motivo de ela ser o pior item a faltar.

Vale registrar que a regra existir não bastou: ela pede conferir a lista contra
o commit, e a lista da 35 defere ao `git show --stat` em vez de o rodar. Deferir
não é conferir — mas isso é observação, não conserto desta correção.

**Arquivos criados/modificados:**

- `docs/tasks/concluidos/35-divergencias-deliberadas.md` — o item que faltava
- `docs/prompts/01-executar.md` — o contador da regra, de três para quatro
- `.claude/commands/executar.md` — o mesmo contador no wrapper
