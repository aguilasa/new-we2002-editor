# `tools/` — geradores e scripts de verificação

O que mora aqui, e em que task. Quem já existe leva ✅.

| Script | Task | O que gera |
|---|---|---|
| `dfm_extract.py` ✅ | 03 | `.rsrc` → os 18 DFM em texto |
| `dump_published.py` ✅ | 04 | VMT + DFM → os 96 handlers, com dono |
| `dump_strings.py` ✅ | 05 | `.data`/`.text` → o inventário de strings |
| `dump_offsets.py` ✅ | 06 | `.data`/`.text` → o mapa de offsets |
| `dump_units.py` ✅ | 07 | imports → veredito sobre as quatro unidades VCL duvidosas |
| `dfm2lfm.py` | 10 | DFM → `.lfm` + esqueleto das unidades |
| `gen_tables_pas.py` | 16 | `Tables.cpp` + `Offsets.hpp` → constantes Pascal |
| `port_database_pas.py` | 17 | `we2002_core` → camada de dados |
| `golden_check.sh` | 22 | o gate: `wte.exe` contra o app Lazarus |
| `golden_suite.sh` | 34 | a bateria completa |
| `ghidra/` | 24 | scripts de nomeação e convenção Borland |
| `make_icon.py` | 39 | ícone |

**Todo gerador daqui aceita `--check`**, e `make -C wte check` roda todos. Sem
o `--check` não há como provar que ninguém editou a saída à mão — que é a regra
da §4.4 do plano.

O `check` do Makefile enumera `tools/*.py` por `wildcard`: script novo entra na
bateria sozinho, sem editar o Makefile. O preço é que um script que **não**
aceite `--check` quebra o alvo — o que é o comportamento desejado.

## Teste de ferramenta: `tools/test_<gerador>.py`

| Teste | Cobre |
|---|---|
| `test_dfm_extract.py` ✅ | os 21 `TValueType`, as três flags de objeto e as rotas de aborto do `dfm_extract.py` |
| `test_dump_strings.py` ✅ | o decodificador de comprimento x86-32 do `dump_strings.py`: mapa de opcodes caso a caso, os sete abortos, o `extent()`, e a conferência contra o `objdump` |

Teste de ferramenta **Python** mora aqui, ao lado do gerador que ele testa, com
o prefixo `test_`. (Teste do lado **Pascal** é outra coisa e mora em
[`../tests/`](../tests/README.md).)

O `wildcard` acima faria do `test_*.py` um gerador e cobraria dele um `--check`
que ele não tem, então o Makefile o filtra:

```make
GENERATORS := $(filter-out $(CURDIR)/tools/test_%.py,$(wildcard $(CURDIR)/tools/*.py))
TESTS      := $(wildcard $(CURDIR)/tools/test_*.py)
```

Eles rodam pelo alvo `test`, do qual `check` depende — `make -C wte check`
continua sendo o único comando a decorar.

**Regra:** o teste é `unittest` de stdlib pura, e **a bateria padrão não depende
do `.exe`** — monta as entradas em memória. Isso não é preciosismo: `--check`
verde só mede o que o binário exercita, e é justamente o que ele *não* exercita
(12 dos 21 `TValueType`, o byte de flags de objeto em 0 dos 459 objetos, todo
aborto) que precisa de teste. Este é o único caminho em que as ferramentas
rodam sem o binário do Obocaman.

Caso que precise do `.exe` — ou de ferramenta externa, como o `objdump` — vai
atrás de `@unittest.skipUnless`, nunca solto: o `test_dump_strings.py` faz isso
com a conferência do decodificador contra o `objdump`, a única medida
independente que o projeto tem dele. Pular é o desfecho certo onde falta o
insumo; **falhar** ali ensinaria a ignorar vermelho, e **jogar a conferência
fora** devolveria o número à memória de quem o mediu uma vez.
