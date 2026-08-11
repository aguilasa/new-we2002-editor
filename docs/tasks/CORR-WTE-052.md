---
id: CORR-WTE-052
title: "Correção: o Log da WTE-TASK-22 diz 15 testes no `golden_veredito`, e são 18"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-052: 15 contra 18, nos dois sítios do Log

## Problema identificado

O Log de Execução da [WTE-TASK-22](/docs/tasks/22-harness-golden.md) afirma, em
dois lugares, que o `golden_veredito.py` tem **15 testes**:

- no resumo: *"mora no `golden_veredito.py`, com 15 testes; shell não é testável
  e esta é a peça que não pode errar"*;
- na tabela de arquivos: `| wte/tools/test_golden_veredito.py | criado — 15 testes |`.

São **18**. O arquivo commitado pela própria task (`e139f46`, 173 linhas) já
tinha os 18 — não houve acréscimo depois.

É o terceiro caso da mesma família neste projeto: a
[CORR-WTE-038](/docs/tasks/CORR-WTE-038.md) trocou 41 por 47 e a
[CORR-WTE-042](/docs/tasks/CORR-WTE-042.md) trocou 33 por 38, as duas em número
de teste afirmado em Log. E importa pelo mesmo motivo das outras duas: a frase
existe para justificar *por que o veredito é Python e não shell* — o argumento
é "esta é a peça que não pode errar, então ela é a peça testada", e o tamanho da
bateria é a evidência do argumento.

## Evidência

```
$ grep -c "    def test_" wte/tools/test_golden_veredito.py
18

$ cd wte/tools && python3 -m unittest test_golden_veredito
Ran 18 tests in 0.004s
OK
```

Os dois sítios do Log:

```
$ grep -n "15 testes" docs/tasks/22-harness-golden.md
225:  [`golden_veredito.py`](../../wte/tools/golden_veredito.py), com 15 testes;
236:  | `wte/tools/test_golden_veredito.py` | criado — 15 testes |
```

E o arquivo nasceu com os 18:

```
$ git show --stat e139f46 | grep test_golden_veredito
 wte/tools/test_golden_veredito.py | 173 +++++++++++++++++++++
```

## Causa raiz

Número escrito no Log antes da última leva de testes, e não relido depois.

## Correção

### Arquivo: `docs/tasks/22-harness-golden.md`

Trocar 15 por 18 nos dois sítios, com o comando que remede ao lado — a forma
que a CORR-WTE-042 usou:

```
$ grep -c "    def test_" wte/tools/test_golden_veredito.py
18
```

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/22-harness-golden.md` | modificar |

## Verificação

- [ ] `grep -n "15 testes" docs/tasks/22-harness-golden.md` não devolve nada
- [ ] o número no Log é o do `grep -c "    def test_"` do arquivo
- [ ] `make -C wte check` verde
- [ ] nenhuma célula do `progresso.md` alterada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
