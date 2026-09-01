---
id: CORR-WTE-070
title: "Correção: a tabela \"Arquivos a criar ou modificar\" da WTE-TASK-27 aponta para arquivos que não existem"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-070: `wte/tools/roteiros/gravacao-*.sh` nunca existiu

## Problema identificado

A WTE-TASK-27 fechou com esta tabela intacta desde o enunciado:

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar (4) |
| `wte/src/ep2002_*.pas` | modificar |
| `wte/tools/roteiros/gravacao-*.sh` | criar (4) |

A terceira linha não corresponde a nada:

```text
$ ls wte/tools/roteiros/
ls: não é possível acessar 'wte/tools/roteiros/': Arquivo ou diretório inexistente
```

O que a task entregou de fato foram **roteiros declarativos** em
`wte/tests/roteiros/`: dez pares `golden-NN-*.txt` / `.port.txt`, o `golden-02-gravacao.txt` sem par, e nove sondas
`27-*.txt`. A substituição é boa — roteiro em arquivo fixo é exatamente o que a
Etapa 3 da revisão exige, contra driver de shell que reage à tela —, e a
primeira linha também ficou defasada: as specs criadas são bem mais que quatro
(as quatro gravações, mais `dorsalClick` e os sete de mover).

O problema é de rastreabilidade: a task está `concluído` e a única lista do que
ela devia produzir aponta para um caminho que não existe. A
[WTE-TASK-33](/docs/tasks/concluidos/33-slots-de-master-league.md) tratou o mesmo caso do
jeito certo — mudou o destino de `wte/re/spec/ml-slots.md` para `wte/re/` e
**anotou na própria tabela**, com data e motivo.

## Evidência

```text
$ ls wte/tools/roteiros/ 2>&1
ls: não é possível acessar 'wte/tools/roteiros/': Arquivo ou diretório inexistente

$ ls wte/tests/roteiros/ | grep -c '^golden-'
21
$ ls wte/tests/roteiros/ | grep -c '^27-'
9
```

| fonte | diz |
|---|---|
| `docs/tasks/concluidos/27-handlers-de-gravacao.md`, tabela de arquivos | `wte/tools/roteiros/gravacao-*.sh`, 4 arquivos `.sh` |
| árvore | `wte/tests/roteiros/*.txt`, 21 roteiros de gate (10 pares + o `golden-02-gravacao`) + 9 sondas, nenhum `.sh` |

## Causa raiz

A tabela é do enunciado de 2026-08-11 e ninguém a reconciliou quando o formato
de roteiro mudou de script para arquivo declarativo.

## Correção

### Arquivo: `docs/tasks/concluidos/27-handlers-de-gravacao.md`

Reescrever a tabela com o que existe, no formato que a WTE-TASK-33 usou —
a linha corrigida mais uma nota `*(data)*` dizendo o que mudou e por quê:

| Arquivo | Ação |
|---|---|
| `wte/re/spec/MainForm.*.md` | criar (as quatro gravações, o `dorsalClick` e os sete de mover) |
| `wte/src/impl/ep2002_mainform.*.inc`, `wte/src/we2002_estado.pas`, `wte/src/we2002_ml.pas` | modificar |
| `wte/tests/roteiros/golden-NN-*.txt` + `.port.txt` | criar — o roteiro do gate, em arquivo fixo |
| `wte/tests/roteiros/27-*.txt` | criar — as sondas |

E a nota: roteiro virou **arquivo declarativo** em vez de script de shell
porque driver que reage à tela muda o estímulo quando um lado diverge, e os
dois lados deixam de receber a mesma entrada.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/concluidos/27-handlers-de-gravacao.md` | modificar |

## Verificação

- [x] A tabela da 27 não cita mais `wte/tools/roteiros/`
- [x] Todo caminho citado na tabela existe:
      `for p in <caminhos>; do ls $p >/dev/null || echo QUEBRADO $p; done`
- [x] A mudança de formato está anotada com data e motivo, como na WTE-TASK-33
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-20

**Resumo do que foi feito:**

A tabela de arquivos da WTE-TASK-27 foi reescrita contra a árvore: as specs
criadas são doze (as quatro gravações, o `dorsalClick` e os sete de mover), os
fontes modificados são os `.inc` do `ep2002_mainform` mais o `we2002_estado` e
o `we2002_ml`, e o que a linha de `.sh` prometia são os 21 roteiros
`golden-*.txt` e as 9 sondas `27-*.txt` de `wte/tests/roteiros/`. A nota datada
segue a forma que a WTE-TASK-33 usou: diz o que a tabela dizia, o que existe, e
por que o formato mudou — roteiro declarativo em vez de script, porque driver
que reage à tela muda o estímulo quando um lado diverge, e aí os dois lados
deixam de receber a mesma entrada.

**Problemas encontrados:**

Nenhum. Conferido depois da edição que todo caminho citado existe e que as
contagens batem: 21 `golden-*`, 9 `27-*`, nenhum `.sh` em lugar nenhum da
árvore de roteiros.

**Arquivos criados/modificados:**

- `docs/tasks/concluidos/27-handlers-de-gravacao.md`
