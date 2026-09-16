---
id: CORR-LOOKS-032
title: "Correção: o bloco de gates da LOOKS-TASK-14 ficou na primeira passagem — 29 controles contra 32"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-LOOKS-032: os gates transcritos na task são de antes dos controles que ela mesma criou

## Problema identificado

A LOOKS-TASK-14 fecha com uma seção `### Gates medidos`, que é a evidência de
que a árvore está verde na conclusão. Os números dela são os da **primeira**
passagem, e a task teve quatro:

```text
python tools/looks/selftest.py --quiet
  rules:    0 failure(s)      ..... rule 1 swept 14 file(s), 8916 line(s)
  controls: 0 failure(s)      ..... 29 of 29 controls red
```

A própria task diz, mais abaixo, que os controles foram a 31 na terceira
passagem (`assembly-hair-map-defaults` e `assembly-hair-map-is-one-section`,
"29 → 31") e a 32 na quarta (`assembly-hair-quads-guessed`, "31 → 32"). O
bloco de gates não acompanhou.

Quem conferir a árvore pelo bloco encontra três controles a mais do que ele
declara — e, o que pesa mais no método, encontra o número **anterior** aos
casos vermelhos que esta task existe para ter plantado.

## Evidência

Medido na árvore commitada em `cef4921`:

```text
python tools/looks/selftest.py --quiet
  modules: 0 failure(s)
  rules self-check
    ..... rule 1 swept 14 file(s), 10182 line(s)
  controls self-check
    ..... 32 of 32 controls red
  looks_selftest: 0 failure(s)
```

| afirmado no bloco | medido |
|---|---|
| 8.916 linhas varridas | **10.182** |
| 29 de 29 controles vermelhos | **32 de 32** |
| 14 arquivos | 14 — bate |

E os cinco controles de montagem existem, contados no arquivo:

```text
tools/looks/controls.py:234  assembly-table-off-by-one
tools/looks/controls.py:244  assembly-effects-do-not-compose
tools/looks/controls.py:253  assembly-hair-quads-guessed
tools/looks/controls.py:262  assembly-hair-map-defaults
tools/looks/controls.py:271  assembly-hair-map-is-one-section
```

## Causa raiz

O bloco foi transcrito na primeira passagem, e as três seguintes acrescentaram
controles sem reexecutar o gate dentro dele.

## Correção

### Arquivo: `docs/tasks/looks/14-tabela-de-montagem.md`

Substituir o bloco `### Gates medidos` pela saída da árvore como ela está ao
fechar a task — 14 arquivos, 10.182 linhas, 32 de 32 controles vermelhos —,
mantendo o resto da lista de comandos, que reproduz. Se valer guardar a corrida
da primeira passagem, ela fica **datada**, dentro da seção daquela passagem, e
não na seção que fecha a task.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/looks/14-tabela-de-montagem.md` | modificar |

## Verificação

- [x] `python tools/looks/selftest.py --quiet` e o bloco da task dizem o mesmo
      número de arquivos, de linhas e de controles — **na árvore que fecha a
      task**, que o bloco agora nomeia pelo commit
- [x] `python tools/check_tasks.py` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

O número novo veio de comando, e de um comando rodado **na árvore certa**: um
worktree destacado em `cef4921`, o commit que fecha a task.

```text
$ git worktree add --detach <tmp> cef4921
$ cd <tmp> && python tools/looks/selftest.py --quiet
  ..... rule 1 swept 14 file(s), 10182 line(s)
  ..... 32 of 32 controls red
  looks_selftest: 0 failure(s)
```

É o que o bloco diz agora, com **o commit escrito ao lado**. Essa parte não
estava na CORR e é o que impede a correção de envelhecer outra vez: a árvore
anda a cada correção — enquanto este lote corria ela foi de 32 para 33
controles e de 10.182 para 10.348 linhas —, então um bloco que declara
"a árvore" sem dizer **qual** volta a estar errado no commit seguinte. A task
fechou uma árvore, e é essa que ela declara.

Os cinco controles de montagem que a task plantou estão nomeados ali, com a
passagem de cada um, porque é isso que o bloco existe para testemunhar.

### A corrida da primeira passagem virou nota

Ela não foi apagada: fica num bloco `>` ao lado, dizendo o que media — 8.916
linhas, 29 de 29 — e que era a árvore **anterior** aos casos vermelhos que a
própria task existe para ter plantado. Apagá-la perderia justamente o que torna
o achado legível.

### Problemas encontrados

Nenhum.

### Arquivos criados/modificados

- `docs/tasks/looks/14-tabela-de-montagem.md` — o bloco `### Gates medidos`
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-032.md` — este arquivo
