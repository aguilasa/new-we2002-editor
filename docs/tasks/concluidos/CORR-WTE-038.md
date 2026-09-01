---
id: CORR-WTE-038
title: "Correção: o Log da WTE-TASK-17 diz 41 regras de substituição, e o gerador tem 47"
type: correção
category: dados
status: concluído
depends_on: []
---

# CORR-WTE-038: o único número datilografado do Log é o único que não bate

## Problema identificado

O Log de Execução da
[WTE-TASK-17](/docs/tasks/concluidos/17-transpilador-da-camada-de-dados.md) abre assim:

> `port_database_pas.py` com os dois guards, a tabela de substituição (**41
> regras**, aplicadas em ordem) e `wte/re/transpilador.md` **gerado pelo próprio
> script** — a tabela, o que ela recusa, a contagem de seeks por arquivo e o
> worklist da WTE-TASK-18, **nenhum número digitado à mão**.

São **47**. E a frase que segue o número é o que torna o erro interessante: o
`transpilador.md`, que o próprio script gera, já dizia 47 **no mesmo commit**
(`8ae9170`). O único número da execução que foi digitado à mão é o único errado,
dentro da frase que promete que nenhum foi.

Não é dano de código — é gabarito. Quem revisar a WTE-TASK-18 contando as regras
da tabela vai achar seis a mais do que o Log manda esperar e procurar a origem
delas.

Junto, no mesmo arquivo, uma segunda coisa envelhecida: a nota do enunciado
(linhas 29-34) encaminha a reconciliação como trabalho futuro —

> a reconciliação do `tipos.md` e do plano é da
> [CORR-WTE-034](/docs/tasks/concluidos/CORR-WTE-034.md).

— enquanto o item 4 dos "Problemas encontrados", no fim do mesmo arquivo, já
registra que ela foi feita em 2026-08-10. O arquivo diz as duas coisas.

## Evidência

O número, dos dois lados:

```console
$ python3 -c "… ast … " wte/tools/port_database_pas.py
SUBS = 47
FORBIDDEN = 30
UNITS = 6
FORA_DO_TRANSPILADOR = 5

$ grep -n 'regras, aplicadas' wte/re/transpilador.md
54:## A tabela de substituição — 47 regras, aplicadas em ordem

$ grep -n 'regras, aplicadas' docs/tasks/17-transpilador-da-camada-de-dados.md
112:  regras, aplicadas em ordem) e `wte/re/transpilador.md` **gerado pelo próprio
```

Já era assim no commit que criou os dois arquivos — não é deriva posterior:

```console
$ git show 8ae9170:wte/re/transpilador.md | grep -n 'regras, aplicadas'
36:## A tabela de substituição — 47 regras, aplicadas em ordem

$ git show 8ae9170:docs/tasks/17-transpilador-da-camada-de-dados.md | sed -n '103,107p'
  `port_database_pas.py` com os dois guards, a tabela de substituição (41
  regras, aplicadas em ordem) …
```

Os outros números do Log **batem** e ficam como estão: 38 testes
(`grep -c 'def test_'` = 38), 498 recusas em 13 motivos (saída do `--check`), e
as 2.504 linhas de entrada.

A contradição interna sobre a CORR-WTE-034:

```console
$ sed -n '33,34p' docs/tasks/17-transpilador-da-camada-de-dados.md
> a reconciliação do `tipos.md` e do plano é da
> [CORR-WTE-034](/docs/tasks/CORR-WTE-034.md).

$ sed -n '184,186p' docs/tasks/17-transpilador-da-camada-de-dados.md
     A entrada real são **2.504 linhas**, não ~2.150. O `tipos.md` e a §4.5 do
     plano foram reconciliados em 2026-08-10 pela
     [CORR-WTE-034](/docs/tasks/CORR-WTE-034.md).
```

## Causa raiz

O número foi escrito de memória na prosa do Log, ao lado da frase que afirma que
a saída não tem número escrito à mão.

## Correção

### Arquivo: `docs/tasks/concluidos/17-transpilador-da-camada-de-dados.md`

1. Trocar **41** por **47** no Log, com a rota de remedição ao lado
   (`len(SUBS)`, ou a linha 54 do `transpilador.md`, que o gerador escreve).
2. Reescrever a nota do enunciado para o estado corrente: a lista de cinco
   arquivos e o "~2.150" são o texto original da task, e a reconciliação **foi
   feita** em 2026-08-10 pela CORR-WTE-034 — não é trabalho pendente de
   ninguém.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/concluidos/17-transpilador-da-camada-de-dados.md` | modificar |

## Verificação

- [ ] O Log diz 47, e o número casa com `len(SUBS)` e com a linha 54 do
      `wte/re/transpilador.md`
- [ ] `grep -rn '41 regras\|(41$' docs wte` não devolve o número aposentado
- [ ] A nota do enunciado e o item 4 dos "Problemas encontrados" contam a mesma
      história sobre a CORR-WTE-034
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

O Log da WTE-TASK-17 diz **47** regras, com a rota de remedição ao lado. A rota
escrita **não** é `len(SUBS)`: a WTE-TASK-18 acrescentou regra e o `HEAD` já
está em 53. O número desta task é histórico, e a rota que o devolve é
`git show 8ae9170:wte/re/transpilador.md | grep 'regras, aplicadas'`.

A nota do enunciado foi reescrita: a reconciliação do `tipos.md` e da §4.5 do
plano **foi feita** em 2026-08-10 pela CORR-WTE-034, e o "~2.150" com a lista de
cinco arquivos fica identificado como texto original da task. As duas passagens
contam agora a mesma história.

**Problemas encontrados:**

A varredura de discrepância puxou um sítio que a CORR não previa:
`docs/tasks/concluidos/18-camada-de-dados-gerada.md:28` repetia "41 regras" ao resumir o
que a WTE-TASK-17 entregou. Corrigido na mesma passada — `grep -rn '41 regras'
docs wte` agora só devolve os arquivos de correção, onde o número aposentado é
o assunto.

A verificação desta CORR pedia que o número casasse com `len(SUBS)`; isso
envelheceu entre a abertura e a execução, pelo mesmo commit que fechou as 498
recusas (`7b642f7`). Cumprido contra a linha 54 do `transpilador.md` **do commit
da task**, que é o que a frase descreve.

**Arquivos criados/modificados:**

- `docs/tasks/concluidos/17-transpilador-da-camada-de-dados.md`
- `docs/tasks/concluidos/18-camada-de-dados-gerada.md` (sítio achado na varredura)
