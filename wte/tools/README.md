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
| `diff_dirigido.sh` ✅ | 19 | copia a ROM, dirige o `wte.exe` sob `strace` por roteiro, `cmp` contra a cópia limpa, e funde as **duas** réguas nos TSV versionados (`--fundir-io` chegou na 27; até então só o `cmp` tinha porta automática). **Não é gerador** — é `.sh` de propósito, para ficar fora do `--check` |
| `compare_dumps.py` ✅ | 20 | **o aceite da fase 3**: compila os dois dumpers de `tests/`, roda sobre cópia das duas ROMs, confronta leitura (`diff` vazio) e gravação (byte a byte) → `re/fase-3.md`. A medição é `--medir` e **não** roda no `check` — são ~1,9 GB de cópia |
| `check_fase3.py` ✅ | 21 | os produtos da fase 3 → `re/fase-3-fechamento.md`: a fração da camada de dados que é transpilação por regra, a entrada × saída, quem dá `uses` na camada (a resposta medida a *o app já lê o jogo?*) e as citações de Ghidra nos artefatos da fase. O irmão `compare_dumps.py` mede se os valores batem; este mede quem escreveu o código |
| `spec_index.py` ✅ | 23 | os 96 handlers + as specs → `re/spec/INDICE.md`, **e valida cada spec** |
| `dump_legendas.py` ✅ | 26 | o inicializador da unidade (`0x00401da8`) → `re/legendas.md`/`.tsv` e `src/wte_legendas.pas`: as legendas enumeradas da ficha do jogador. Elas são **zero no arquivo** — `AnsiString` montada em tempo de execução —, e o que só está na ordem das chamadas é qual cadeia vai em qual slot. Confere a atribuição linha→controle contra o `Max` do DFM, que é outra fonte |
| `dump_zonas.py` ✅ | 26 | o corpo do `estrategia.FormCreate` → `re/zonas.md`/`.tsv` e `src/wte_zonas.pas`: os 11 retângulos em que cada bola do campinho pode ser solta. Também `.bss`, também montada em tempo de execução; confere cada retângulo contra o tamanho do `campo` no `.lfm` e a contagem contra os `bolaN` do formulário |
| `dump_truncamento.py` ✅ | 26 | os 18 `.dfm` + as três chamadas a `SetMaxLength` no `.text` + a camada de dados → `re/truncamento.md`/`.tsv`: onde cada campo editável corta o texto. As três fontes não se falam, e o gerador **aborta** se a expressão lida do `.exe` não casar com a largura do campo de destino |
| `check_edicao.py` ✅ | 26 | os 28 handlers de edição → `re/edicao-cobertura.md`: o instrumento de cada um. **Não gera medição** — confere que cada handler tem instrumento nomeado, que ele existe, que o estático passa no próprio `--check`, e que o de tela aparece na evidência de trace da corrida que diz cobri-lo |
| `gravacao_controle.py` ✅ | 27 | as duas réguas já versionadas (`re/io-medido.tsv` e `re/cmp-medido.tsv`) → `re/gravacao-controle.md`: o **diff de controle** da gravação, que o enunciado da task manda medir antes de implementar qualquer coisa. Não mede nada sozinho — cruza. As duas colunas de contagem não são a mesma: `escreveu` é syscall, `mudou` é `cmp`, e a diferença entre elas é gravação de valor igual, que nenhum `cmp` enxerga |
| `conta_ml.py` ✅ | 33 | os blocos livres de Master League: extrai do `.exe` a tabela de quantos jogadores *non-contract* cada um dos 120 times tem (`0x00423424`), confere-a contra o `START_LINK[]` do `we2002_core` — as duas codificações da mesma tabela — e emite `re/ml-slots.{md,tsv}` mais o include Pascal `src/we2002_ml_tabela.inc`. `--medir <copia>` conta numa imagem e escreve `re/ml-slots-medido.tsv`. **Recusa** se a tabela não somar 462 ou se os dois oráculos divergirem num time que tenha algum NC |
| `gen_tables_pas.py` | 16 | `Tables.cpp` + `Offsets.hpp` → constantes Pascal |
| `port_database_pas.py` | 17 | `we2002_core` → camada de dados |
| `roteiro.sh` ✅ | 19, 22 | **biblioteca, nao executavel** — o dialeto de roteiro, a busca de janela (por nome, por tamanho e filtrada por `_NET_WM_PID`) e a fixacao do `:99`. `source`ada pelo `diff_dirigido.sh` e pelos dois lados do gate; duas copias divergiriam em silencio |
| `golden_run_wte.sh` ✅ | 22 | o lado **oraculo** do gate: dirige o `wte.exe` sob Wine por um roteiro. Reprova com codigo 4 se achar `c0000005` no log — oraculo que morreu no meio grava menos, e o diff sairia menor |
| `golden_run_laz.sh` ✅ | 22 | o lado **port**: dirige o app Lazarus. Reprova roteiro com `! tecla`/`! texto`, porque o `:99` sem window manager nao entrega tecla ao GTK2 |
| `golden_veredito.py` ✅ | 22 | as divergencias medidas contra as **declaradas** no roteiro (`conhecida: a..b`). Tres codigos: 0 passou, 1 divergencia nao declarada, **3 faixa declarada que sumiu**. Nao gera arquivo — como o `check_lcl_props.py`, o `--check` dele confere outra coisa: que as declaracoes dos roteiros do gate sao legiveis, antes de uma corrida de dez minutos descobrir que nao |
| `golden_check.sh` ✅ | 22 | **o gate**, em tres modos: `controle` (oraculo × oraculo), `positivo` (byte plantado tem de ser detectado) e `golden` (oraculo × port). As quatro guardas do harness do `newWe2002`, e o comparador reusado de `tools/golden_compare.py`. `--artefato <nome>` chegou na 27, para o `grabar_memory`: ele nao escreve na imagem, emite um `.mcr` -- comparar so as imagens aprovaria um port inerte, entao o script compara tambem o arquivo que cada lado produziu em `work/` |
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
| `test_check_fase3.py` ✅ | as guardas do `check_fase3.py` com entrada plantada — bloco de porte a mão que sumiu da saída, e o dedupe da constante alcançada por dois caminhos (`MANUAL_TIPOS["we2002_types"]` **é** `MANUAL_TYPES.interface`, e somar os dois contava 320 linhas onde há 277) — mais a árvore real: a fração, a entrada de 11 arquivos e o fato de que só teste consome a camada |
| `test_check_fase2.py` ✅ | as dez rotas de aborto do `check_fase2.py` sobre uma árvore de fase 2 sintética: stub que sumiu, stub duplicado, stub na unidade que não declara a classe, formulário sem `.lfm`, `.lfm` sem `.dfm`, formulário sem veredito visual, `eventos.md` sem achado — mais a partição do hex de blob, que é o que mantém a fração honesta |
| `test_golden_veredito.py` ✅ | os tres codigos de saida do veredito com relatorio plantado, a leitura de `conhecida:` do cabecalho do roteiro, e o caso que separa este gate de um `cmp` com lista de exclusao: **faixa declarada que nao aparece reprova**. Mais a fronteira 0-based (um byte de diferenca no limite ja e outra faixa — CORR-WTE-025) |
| `test_analisar_io.py` ✅ | o parser do trace com linha plantada — `_llseek`+`read` sequencial, `pread64`, leitura curta, fd de outro arquivo, syscall que falhou —, o classificador de papel no `Database.cpp` com fonte plantado, e a evidência commitada cruzada com o `Offsets.hpp` e com a geometria de setor. Um dos testes é o **critério da WTE-TASK-19**: nenhum dos 50 `OFS_*` `ausente` pode ficar sem veredito |
| `test_gravacao_controle.py` ✅ | o cruzamento das duas réguas com TSV plantado — gravação de valor igual, ação que não gravou, faixa do `cmp` de outra ação que não pode ser creditada — e o par de sondas `27-descarga-sem`/`-com`, que só é medida enquanto tiver **uma** variável de diferença: o teste compara os dois roteiros linha a linha e exige que o resultado medido seja oposto |
| `test_conta_ml.py` ✅ | os dois guards com tabela plantada, a conta sobre imagem sintética (o par de enchimento, o corte por `b1 < 23`, bloco repetido, índice além do vetor) e o confronto Pascal × Python: o `fpc` compila o `we2002_ml` e o `tests/test_ml.pas` conta a **mesma** cópia que o Python |
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
