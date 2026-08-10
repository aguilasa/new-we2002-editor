# `re/fase-3-fechamento.md` — o aceite da fase 3

**Gerado por [`wte/tools/check_fase3.py`](../tools/check_fase3.py) — não editar à mão.**

Produto da [WTE-TASK-21](../../docs/tasks/21-fechamento-fase-3.md). O
irmão é [`fase-3.md`](fase-3.md), da WTE-TASK-20, e a divisão é de
pergunta: lá se mede se **os valores batem**; aqui, **quem escreveu o**
**código que os produz** e **quem o consome**.

---

## 1. A camada de dados é gerada — e quanto dela é transpilação

Os oito `.pas` são saída de gerador, sem exceção: nenhum foi editado à
mão, e quem prova isso é o `--check` dos dois geradores, na bateria.
Mas **arquivo gerado não quer dizer conteúdo transpilado**: as peças da
rota 3 ([`recusas.md`](recusas.md)) são Pascal escrito à mão que mora
nas constantes `MANUAIS` e `TRECHOS_MANUAIS` do gerador, e sai emitido
junto. A coluna **à mão** conta essas linhas, e cada bloco é conferido
dentro da própria saída antes de entrar na conta.

| arquivo | gerador | linhas | à mão | por regra |
|---|---|---:|---:|---:|
| `wte/src/we2002_types.pas` | `port_database_pas.py` | 151 | 87 | 64 |
| `wte/src/we2002_team.pas` | `port_database_pas.py` | 147 | 0 | 147 |
| `wte/src/we2002_cdimage.pas` | `port_database_pas.py` | 182 | 130 | 52 |
| `wte/src/we2002_textcodec.pas` | `port_database_pas.py` | 163 | 0 | 163 |
| `wte/src/we2002_player.pas` | `port_database_pas.py` | 194 | 0 | 194 |
| `wte/src/we2002_database.pas` | `port_database_pas.py` | 2147 | 60 | 2087 |
| `wte/src/we2002_offsets.pas` | `gen_tables_pas.py` | 106 | 0 | 106 |
| `wte/src/we2002_tables.pas` | `gen_tables_pas.py` | 602 | 0 | 602 |
| **total** | | **3692** | **277** | **3415** |

**92.5% da camada de dados é transpilação por regra** — 3415 linhas contra 277 escritas à mão, e as
escritas à mão são as quatro peças que o
[`tipos.md`](tipos.md) já tinha decidido que **não são** transpiláveis:
`CdImage` (`std::fstream`), `SquadNumbers` (bitfield), o sidecar
`_url.txt` e o `Reporter` (`std::function`).

A tese da §4.5 do plano — *a Fase 3 deixa de ser porte manual e vira
execução de gerador mais conferência* — se sustenta com essa ressalva
escrita: o que sobrou de manual não foi porte de lógica do editor, foi
o encontro com a biblioteca padrão de outra linguagem.

---

## 2. Entrada × saída

**A razão é por gerador.** Os oito `.pas` saem de *dois*, e dividir a
soma dos dois pela entrada de um só creditava ao transpilador linhas que
o `gen_tables_pas.py` emitiu
([CORR-WTE-050](../../docs/tasks/CORR-WTE-050.md)).

| entrada | gerador | linhas |
|---|---|---:|
| `src/core/Tables.cpp` | `gen_tables_pas.py` | 704 |
| `src/core/include/we2002/Tables.hpp` | `gen_tables_pas.py` | 53 |
| `src/core/include/we2002/Offsets.hpp` | `gen_tables_pas.py` | 95 |
| `src/core/include/we2002/Types.hpp` | `port_database_pas.py` | 147 |
| `src/core/include/we2002/Team.hpp` | `port_database_pas.py` | 91 |
| `src/core/Team.cpp` | `port_database_pas.py` | 16 |
| `src/core/include/we2002/CdImage.hpp` | `port_database_pas.py` | 77 |
| `src/core/CdImage.cpp` | `port_database_pas.py` | 89 |
| `src/core/include/we2002/TextCodec.hpp` | `port_database_pas.py` | 18 |
| `src/core/TextCodec.cpp` | `port_database_pas.py` | 77 |
| `src/core/include/we2002/Player.hpp` | `port_database_pas.py` | 95 |
| `src/core/Player.cpp` | `port_database_pas.py` | 130 |
| `src/core/include/we2002/Database.hpp` | `port_database_pas.py` | 60 |
| `src/core/Database.cpp` | `port_database_pas.py` | 1704 |

| gerador | entrada | saída | razão |
|---|---:|---:|---:|
| `gen_tables_pas.py` | 852 | 708 | 0.83 |
| `port_database_pas.py` | 2504 | 2984 | 1.19 |
| **total** | **3356** | **3692** | **1.10** |

O transpilador **infla** (1.19): Pascal quer `begin` e `end`
onde o C++ tem chave, e declaração de variável no topo do corpo. O
gerador de tabelas **encolhe** (0.83): a mesma tabela cabe em
menos linha de Pascal do que de inicializador C++. Uma razão só, sobre
a soma, esconderia os dois efeitos e não descreveria nenhum dos dois
geradores.

As duas contagens saem de ferramenta: a entrada do transpilador é o
`UNITS` dele, a do outro são as três constantes do
`gen_tables_pas.py`, e o `test_nenhuma_entrada_do_core_fica_de_fora`
reprova arquivo de `src/core/` que ninguém reivindicou.

---

## 3. O app ainda não lê o jogo

A pergunta que a task manda responder, medida por `uses`:

- **0** unidade(s) da casca (`wte/src`, `wte.lpr`) importam a camada de dados;
- **2** de teste importam: `tests/dump_estado.pas`, `tests/test_camada_dados.pas`.

Ou seja: a camada compila, é exercitada por dois programas de
console e **nenhum formulário a consome**. Abrir a imagem pelo
`TOpenDialog` do `MainForm` e popular o combo de times é trabalho
de **handler**, e handler tem gate próprio — a
[WTE-TASK-22](../../docs/tasks/22-harness-golden.md) antes da
[WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md). Fazer a
integração aqui seria implementar `boton_dialogo_weClick` e
`lista_equiposChange` sem o gate que os julga, que é exatamente o
que o `progresso.md` chama de *cada implementação é opinião*.

---

## 4. Ghidra: não foi necessário

A fase 3 fecha **sem decompilador**, que é o cenário bom previsto pelo
plano. Medido nos artefatos que a fase produziu:

| artefato | linhas citando `ghidra` |
|---|---:|
| [`tipos.md`](tipos.md) | 0 |
| [`transpilador.md`](transpilador.md) | 0 |
| [`recusas.md`](recusas.md) | 0 |
| [`fase-3.md`](fase-3.md) | 0 |
| [`offsets-novos.md`](offsets-novos.md) | 0 |
| [`crash.md`](crash.md) | 0 |
| [`crash-causa.md`](crash-causa.md) | 1 |

As citações existentes são **negativas ou de contexto**, e ficam transcritas:

- `crash-causa.md`: endereço abaixo vem de comando, não de leitura do Ghidra transcrita.

O único uso real de Ghidra no projeto é a
[WTE-TASK-24](../../docs/tasks/24-ghidra-convencao-borland.md), que é
**fase 4** e existe para isso. Consequência para a estimativa: a fase 4
não herda dívida de decompilação da 3 — começa com o Ghidra já
configurado e nenhum trecho de fase 3 dependendo dele.

---

## 5. O que a fase 3 **não** prova

- **Gravar pela janela.** A fase prova leitura e prova gravação
  headless, com os dois lados byte a byte iguais. Gravação dirigida por
  clique é a WTE-TASK-22 em diante.
- **Comportamento.** Os 96 handlers continuam stubs que logam. A camada
  de dados não sabe nada sobre eles.
- **Os `OFS_*` que o `we2002_core` não nomeia.** As faixas sem dono que
  a [WTE-TASK-19](../../docs/tasks/19-os-50-offsets-restantes.md)
  mediu — a maior é a região do uniforme — não têm lado C++, então
  nenhum diff Pascal × C++ as alcança. Nomeá-las é fase 4 e 5.
- **Que o `Load` do sidecar funcione.** Nenhum dos dois lados lê
  `_url.txt` no `Load`; isso é do app.

