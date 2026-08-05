# `tools/` — geradores e scripts de verificação

Vazio até a **WTE-TASK-03**. O que vai morar aqui, e em que task:

| Script | Task | O que gera |
|---|---|---|
| `dfm_extract.py` | 03 | `.rsrc` → os 18 DFM em texto |
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
