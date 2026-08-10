# `tools/` — geradores e scripts de verificação

O que mora aqui, e em que task. Quem já existe leva ✅.

| Script | Task | O que gera |
|---|---|---|
| `dfm_extract.py` ✅ | 03 | `.rsrc` → os 18 DFM em texto |
| `dump_published.py` ✅ | 04 | VMT + DFM → os 96 handlers, com dono |
| `dump_strings.py` ✅ | 05 | `.data`/`.text` → o inventário de strings |
| `dump_offsets.py` ✅ | 06 | `.data`/`.text` → o mapa de offsets |
| `dump_units.py` ✅ | 07 | imports → veredito sobre as quatro unidades VCL duvidosas |
| `check_fase1.py` ✅ | 09 | os produtos da fase 1 → as quatro conferências cruzadas e a reconciliação |
| `dfm2lfm.py` ✅ | 10 | DFM → `.lfm` + esqueleto das unidades |
| `check_lcl_props.py` ✅ | CORR-020 | **não gera nada** — remede a tabela `PROPRIEDADES` do `dfm2lfm.py` contra as seções `published` da LCL instalada |
| `check_fase2.py` ✅ | 14 | os produtos da fase 2 → `re/fase-2.md`: os 96 stubs cruzados com o TSV, os 18 formulários, os 18 vereditos e a fração de código gerado |
| `analisar_io.py` ✅ | 19 | trace de `strace` do `wte.exe` → `re/offsets-novos.md`: que faixa da imagem cada ação endereça |
| `analisar_crash.py` ✅ | 19 | log de exceção do Wine (`+seh,+loaddll`) → `re/crash.md`: **onde** o `wte.exe` morre, com nome de função. O `analisar_io.py` mede I/O e chega até a leitura vizinha da falha; este resolve o endereço contra a tabela de exportação do módulo e acha os sítios de chamada no `.exe` |
| `diff_dirigido.sh` ✅ | 19 | copia a ROM, dirige o `wte.exe` sob `strace` por roteiro, `cmp` contra a cópia limpa. **Não é gerador** — é `.sh` de propósito, para ficar fora do `--check` |
| `compare_dumps.py` ✅ | 20 | **o aceite da fase 3**: compila os dois dumpers de `tests/`, roda sobre cópia das duas ROMs, confronta leitura (`diff` vazio) e gravação (byte a byte) → `re/fase-3.md`. A medição é `--medir` e **não** roda no `check` — são ~1,9 GB de cópia |
| `spec_index.py` ✅ | 23 | os 96 handlers + as specs → `re/spec/INDICE.md`, **e valida cada spec** |
| `gen_tables_pas.py` | 16 | `Tables.cpp` + `Offsets.hpp` → constantes Pascal |
| `port_database_pas.py` | 17 | `we2002_core` → camada de dados |
| `golden_check.sh` | 22 | o gate: `wte.exe` contra o app Lazarus |
| `golden_suite.sh` | 34 | a bateria completa |
| `ghidra/` | 24 | scripts de nomeação e convenção Borland |
| `make_icon.py` | 39 | ícone |

**Todo gerador daqui aceita `--check`**, e `make -C wte check` roda todos. Sem
o `--check` não há como provar que ninguém editou a saída à mão — que é a regra
da §4.4 do plano.

Nem todo item da tabela é gerador. O `check_lcl_props.py` não escreve arquivo
nenhum: ele confere uma **tabela dentro de outro script** contra a realidade do
disco. Entra pela mesma porta porque cumpre o mesmo contrato — `--check`, sai 2
quando diverge — e existe porque `--check` de gerador compara a saída consigo
mesma, o que não diz nada sobre a tabela que produziu a saída.

O `check` do Makefile enumera `tools/*.py` por `wildcard`: script novo entra na
bateria sozinho, sem editar o Makefile. O preço é que um script que **não**
aceite `--check` quebra o alvo — o que é o comportamento desejado.

## Teste de ferramenta: `tools/test_<gerador>.py`

| Teste | Cobre |
|---|---|
| `test_dfm_extract.py` ✅ | os 21 `TValueType`, as três flags de objeto e as rotas de aborto do `dfm_extract.py` |
| `test_dump_strings.py` ✅ | o decodificador de comprimento x86-32 — mapa de opcodes caso a caso, os sete abortos, o `extent()`, a conferência contra o `objdump`, e a identidade entre as **duas** cópias (`dump_strings.py` e `dump_units.py`) |
| `test_dump_offsets.py` ✅ | o critério de limite da tabela em `.data`: os dois sentidos da discordância (um aborta, o outro avisa) e a faixa de plausibilidade herdada do `Offsets.hpp` |
| `test_dfm2lfm.py` ✅ | o mapeamento VCL→LCL do `dfm2lfm.py`: as assinaturas por par (classe, evento), as propriedades sem par na LCL, a rota de blob ausente e os abortos |
| `test_check_fase1.py` ✅ | o perímetro da varredura de sítios do `check_fase1.py`: quem entra, onde a leitura para (o Log de Execução), o corte por contexto que separa os `430` componentes do setor 430 do outro projeto, e a forma de história (`velho → corrente`), que não conta |
| `test_check_fase2.py` ✅ | as dez rotas de aborto do `check_fase2.py` sobre uma árvore de fase 2 sintética: stub que sumiu, stub duplicado, stub na unidade que não declara a classe, formulário sem `.lfm`, `.lfm` sem `.dfm`, formulário sem veredito visual, `eventos.md` sem achado — mais a partição do hex de blob, que é o que mantém a fração honesta |
| `test_analisar_io.py` ✅ | o parser do trace com linha plantada — `_llseek`+`read` sequencial, `pread64`, leitura curta, fd de outro arquivo, syscall que falhou —, o classificador de papel no `Database.cpp` com fonte plantado, e a evidência commitada cruzada com o `Offsets.hpp` e com a geometria de setor. Um dos testes é o **critério da WTE-TASK-19**: nenhum dos 50 `OFS_*` `ausente` pode ficar sem veredito |
| `test_analisar_crash.py` ✅ | o parser do log de exceção com linha plantada — exceção completa, `6ba` da subida que **não** pode contar, registro que não vaza para a exceção seguinte, módulo builtin descartado, prólogo e `call` relativo —, mais o par de roteiros 07/08 (idênticos até `ARRANQUE`, uma ação de diferença), que é o que faz da atribuição uma medida |
| `test_compare_dumps.py` ✅ | o comparador de bytes com arquivo plantado (a folga de 16 nos dois sentidos), o par de dumpers pelo que dá para conferir sem compilar (mesma versão de formato, mesmo `--roundtrip`, `Sofifa.cpp` fora), e a evidência do `fase-3.tsv` — inclusive a guarda de que o round-trip **mexeu** na imagem, sem a qual zero contra zero passaria verde sem medir nada. A remedição completa fica sob `WTE_ROUNDTRIP=1` |
| `test_check_lcl_props.py` ✅ | as três guardas do `check_lcl_props.py`, com entrada plantada nos três sentidos — `ACEITA` inventada, `DESCARTA` que a LCL tem, `LCL_VERSAO` divergindo do disco —, sobre uma LCL sintética montada em diretório temporário |
| `test_spec_index.py` ✅ | **as 15 rotas de recusa** do `spec_index.py` sobre specs sintéticas — 15 é `grep -c "raise SpecError" spec_index.py`, e é assim que se remede: TSV ausente, TSV só com cabeçalho, spec sem frontmatter, frontmatter não fechado, linha de frontmatter sem `:`, chave obrigatória ausente, decompilado colado nas sete formas de nome inventado mais o cast do Ghidra (`(int)*(int *)`, com o caso negativo em prosa), frontmatter discordando do TSV, veredito e evidência fora do vocabulário, seção faltando, seção sem evidência, `nao portado` sem justificativa, `implementado` só com observação de tela, spec órfã. **É a única coisa que mede essas regras** — `--check` verde sobre 96 `aberto` não exercita nenhuma |

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

## Código duplicado entre geradores tem de ter guarda

Cada gerador daqui roda sozinho — decisão do [`../README.md`](../README.md).
O preço é duplicação real: o leitor de PE aparece em cinco arquivos, e o
decodificador de comprimento x86-32 (`_fill`, `decode`, `extent`) vive **verbatim**
no `dump_strings.py` e no `dump_units.py`.

A decisão não está em discussão; o que ela exige é uma guarda. Cópia sem teste
está livre para divergir em silêncio, e a do `dump_units.py` sustenta a
fronteira dos 96 corpos, que decide o único veredito não trivial da
WTE-TASK-07. `TestCopiaVerbatim`, no `test_dump_strings.py`, compara o
texto-fonte das três funções mais os mapas de opcode montados, e a tabela de
comprimento roda contra os dois módulos.

**Ao duplicar de novo, duplique a guarda junto.** "Os dois têm de andar juntos"
escrito em comentário não segurou ninguém — foi preciso um teste.
