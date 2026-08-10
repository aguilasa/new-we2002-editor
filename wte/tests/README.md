# `tests/` — os programas de teste compilados

O que existe hoje:

| Arquivo | Origem | O que é |
|---|---|---|
| `test_offsets.pas` | WTE-TASK-16, **gerado** | despeja as constantes lidas do Pascal |
| `test_offsets.cpp` | WTE-TASK-16, **gerado** | despeja as mesmas, lidas do C++ |
| `roteiros/` | WTE-TASK-13 | os roteiros de trace de evento |

Os dois `test_offsets.*` saem de `wte/tools/gen_tables_pas.py` e **não se edita à
mão** — correção entra no gerador e o arquivo é regerado, e o `--check` reprova
quem tentar.

## A pasta não é só Pascal, e o par bilíngue é o ponto

Aqui moram **programas de teste que precisam ser compilados**. O par de dumpers
é deliberadamente de duas linguagens: a conferência dos 69 offsets e das 16
tabelas só vale porque cada lado vem de um **compilador diferente** — o `fpc`
lendo o Pascal gerado, o `g++` lendo o C++ original. Um dumper só, ou dois na
mesma linguagem, provaria bem menos: erro de leitura de literal apareceria
idêntico dos dois lados.

**Não há alvo do `Makefile` que construa estes dois isoladamente.** Quem os
compila, roda e compara é `wte/tools/test_gen_tables_pas.py`, alcançado por
`make -C wte test` — de que `check` depende. Sem `fpc` ou sem `g++` o teste
**pula** e diz o que deixou de medir, em vez de passar em silêncio.

## O que ainda vai chegar

A **WTE-TASK-20** traz o round-trip headless contra o `we2002_core` nas duas
ROMs — o dumper de estado em Pascal e o comparador.

## O que **não** mora aqui

O **golden test** — o gate de verdade, a partir da WTE-TASK-22 — é script de
shell em `tools/`, porque precisa de Wine, do `:99` e de ~1 GB de temporário por
rodada. Nada disso roda em CI.

Teste de **ferramenta Python** também não: fica em `tools/test_<gerador>.py`, ao
lado do gerador que testa. Ver [`../tools/README.md`](../tools/README.md). A
pergunta "onde ponho o teste do `dfm_extract.py`?" ficou sem resposta uma vez, e
a verificação acabou em código descartável (CORR-WTE-005).
