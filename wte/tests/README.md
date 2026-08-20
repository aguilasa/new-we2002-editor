# `tests/` — os programas de teste compilados

O que existe hoje:

| Arquivo | Origem | O que é |
|---|---|---|
| `test_offsets.pas` | WTE-TASK-16, **gerado** | despeja as constantes lidas do Pascal |
| `test_offsets.cpp` | WTE-TASK-16, **gerado** | despeja as mesmas, lidas do C++ |
| `test_camada_dados.pas` | WTE-TASK-18, escrito à mão | prova as cinco decisões de `tipos.md` contra a camada gerada |
| `dump_estado.pas` | WTE-TASK-20, escrito à mão | despeja todo o estado carregado, e `--roundtrip` faz Load+Save |
| `dump_estado.cpp` | WTE-TASK-20, escrito à mão | o irmão do lado `we2002_core`, mesmo formato e mesmo verbo |
| `test_ml.pas` | WTE-TASK-33, escrito à mão | prova a conta de blocos livres de Master League contra a do `conta_ml.py`, na mesma cópia |
| `test_mcr.pas` | WTE-TASK-28, escrito à mão | prova o leitor de `.mcr` — o contêiner, a aritmética de 5 bits do dorsal, e a leitura de um cartão de verdade contra a do `dump_mcr.py` |
| `roteiros/` | WTE-TASK-13 e 19 | os roteiros de trace de evento e o par 07/08 do travamento |

Os dois `test_offsets.*` saem de `wte/tools/gen_tables_pas.py` e **não se edita à
mão** — correção entra no gerador e o arquivo é regerado, e o `--check` reprova
quem tentar. O `test_camada_dados.pas` é o contrário: escrito à mão, porque
teste gerado do mesmo gerador que produziu o código não prova nada.

## `test_camada_dados.pas` — o que ele mede, e o que não mede

Ele **não** lê imagem: isso é a WTE-TASK-20. O que ele mede é o que a decisão de
**tipo** promete, que é a categoria que erra em silêncio — layout de bit, sinal
de `char`, semântica da cópia, leitura curta e o terminador do sidecar. São 23
casos, e a contagem está fixada no teste Python: caso que suma do programa
sumiria sem ninguém notar, e o teste continuaria verde sem medir nada.

Cada linha da saída é `OK<TAB>nome` ou `FALHA<TAB>nome<TAB>detalhe`. Quem
compila, roda e lê é `wte/tools/test_port_database_pas.py`.

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

## `dump_estado.*` — o aceite da fase 3

O par escreve o **mesmo formato** (`chave = valor`, vetor de bytes em
`<n>:<hex>` cortado no último byte não-zero) e quem compila, roda e compara é
[`../tools/compare_dumps.py`](../tools/compare_dumps.py). Duas metades:
leitura, onde o critério é `diff` **vazio**, e gravação (`--roundtrip`), onde
as duas imagens têm de sair byte a byte iguais.

O `--roundtrip` mora **dentro** do dumper, e não num binário à parte, porque
tem de ser exatamente o mesmo `Database` que o dump usa — dois executáveis
divergiriam no dia em que um fosse recompilado e o outro não.

O resultado medido está em [`../re/fase-3.md`](../re/fase-3.md). Um achado da
execução: o enunciado da task supunha a ROM japonesa como o único teste real do
codec de texto, e é o contrário — quem exercita os ramos de mapeamento do
`KanjiToAscii` é a **europeia**; a japonesa guarda katakana (`0x83`), que o
codec não conhece e transforma em espaço.

## O que **não** mora aqui

O **golden test** — o gate de verdade, a partir da WTE-TASK-22 — é script de
shell em `tools/`, porque precisa de Wine, do `:99` e de ~1 GB de temporário por
rodada. Nada disso roda em CI.

Teste de **ferramenta Python** também não: fica em `tools/test_<gerador>.py`, ao
lado do gerador que testa. Ver [`../tools/README.md`](../tools/README.md). A
pergunta "onde ponho o teste do `dfm_extract.py`?" ficou sem resposta uma vez, e
a verificação acabou em código descartável (CORR-WTE-005).
