---
id: CORR-LOOKS-041
title: "Correção: o bloco de gates da LOOKS-TASK-16 diz 12.609 linhas e a árvore dela tem 12.613"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-LOOKS-041: a varredura foi anotada antes da última edição, outra vez

## Problema identificado

O Log da LOOKS-TASK-16 transcreve o gate obrigatório:

```text
$ python tools/looks/selftest.py --quiet
  ..... rule 1 swept 18 file(s), 12609 line(s)
  ..... 37 of 37 controls red
```

Arquivos e controles batem. As linhas não: a árvore que a task commitou tem
**12.613**. São quatro linhas, e elas têm nome — foram as que a própria task
acrescentou ao docstring do `ui_check.py` no fim da execução, ao trocar o
`make looks-venv` (que não existe) pela receita de duas linhas da §4.1.

É a terceira vez no ciclo, e a segunda em duas tasks seguidas:
[`CORR-LOOKS-032`](/docs/tasks/looks/CORR-LOOKS-032.md) mediu 8.916 contra
10.182 na LOOKS-TASK-14, e
[`CORR-LOOKS-036`](/docs/tasks/looks/CORR-LOOKS-036.md) mediu 11.789 contra
11.831 na LOOKS-TASK-15 — esta última **já executada**, com o conserto que
manda nomear o commit ao lado do número. A LOOKS-TASK-16 foi escrita antes
desse conserto existir e repetiu o erro na mesma linha do arquivo.

## Evidência

Nos dois commits da task, o mesmo número, e não é o escrito:

```text
$ git worktree add --detach <tmp> 9f1e3af && cd <tmp>
$ python tools/looks/selftest.py --quiet
  ..... rule 1 swept 18 file(s), 12613 line(s)

$ git worktree add --detach <tmp2> cb26d88 && cd <tmp2>
$ python tools/looks/selftest.py --quiet
  ..... rule 1 swept 18 file(s), 12613 line(s)
  ..... 37 of 37 controls red
```

| afirmado | medido nos dois commits da task |
|---|---|
| 18 arquivos | 18 — bate |
| 37 de 37 controles | 37 — bate |
| 12.609 linhas | **12.613** |

O resto do Log reproduz inteiro, medido hoje: os três pares de percentuais
(47,13%, 17,17% e 0,00%), a recusa saindo 2 sem escrever arquivo, os dois
caminhos de pulo com 77, os três controles vermelhos, e o `ctest -R looks`
dando 1 passed / 2 skipped numa máquina limpa e 3 passed com a imagem
apontada.

## Causa raiz

A transcrição do gate foi copiada antes da última edição do próprio
`ui_check.py`, e o gate não foi reexecutado ao fechar a task.

## Correção

### Arquivo: `docs/tasks/looks/16-contratos-da-ui.md`

Trocar 12.609 por **12.613** no bloco de gates e **nomear o commit** ao lado —
`cb26d88` —, na forma que a CORR-LOOKS-036 deixou na task vizinha. A árvore
anda a cada correção (hoje são 39 controles e outra contagem de linhas), então
um bloco que declara "a árvore" sem dizer qual volta a estar errado no commit
seguinte.

**E vale consertar a causa, não só o número:** três ocorrências em três tasks
dizem que o passo "reexecutar o gate ao escrever o Log" não está em lugar
nenhum que quem executa leia. O destino natural é a seção "gates" do
[`perfil-looks.md`](/docs/prompts/perfil-looks.md) — uma linha dizendo que a
transcrição do gate se tira **depois** do último commit da task, e que ela
nomeia o commit.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/looks/16-contratos-da-ui.md` | modificar |
| `docs/prompts/perfil-looks.md` | modificar (a regra, na seção de gates) |

## Verificação

- [x] o número do bloco é o que a varredura imprime no commit que ele nomeia
- [x] o perfil diz quando a transcrição do gate se tira, com as três
      ocorrências nomeadas e o comando de remedir
- [x] `python tools/check_tasks.py` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

Remedido nos **dois** commits da task, e o número é o mesmo nos dois:

```text
$ git worktree add --detach <tmp> 9f1e3af && cd <tmp>
  ..... rule 1 swept 18 file(s), 12613 line(s)
$ git worktree add --detach <tmp2> cb26d88 && cd <tmp2>
  ..... rule 1 swept 18 file(s), 12613 line(s)
```

O bloco diz **12.613** e nomeia `cb26d88`, na forma que a CORR-LOOKS-036 deixou
na task vizinha.

### E a causa, que é o que esta CORR acrescenta às outras duas

Três ocorrências em três tasks seguidas dizem que "reexecutar o gate ao
escrever o Log" não estava em lugar nenhum que quem executa leia. Entrou na
seção de gates do [`perfil-looks.md`](/docs/prompts/perfil-looks.md) — que é o
arquivo que os cinco prompts carregam — com as três medições nomeadas,
a forma que sobrevive (`# na arvore de <sha>` ao lado do comando) e o comando
de remedir depois (`git worktree add --detach`).

Vale o número que mostra por que a forma importa: enquanto **este lote** corria,
a mesma varredura foi de 12.613 para **12.999** linhas e os controles de 37
para 41. Um bloco que diz "a árvore" sem dizer qual erra no commit seguinte.

### Problemas encontrados

Nenhum. O resto do Log da task reproduz inteiro, como a CORR já dizia.

### Arquivos criados/modificados

- `docs/tasks/looks/16-contratos-da-ui.md` — o bloco de gates
- `docs/prompts/perfil-looks.md` — a regra, na seção de gates
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-041.md` — este arquivo
