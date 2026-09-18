# Correções — visualizador 3D da aparência do jogador

Correções abertas pelo `/revisar` sobre as tasks deste ciclo. O andamento das
**tarefas** fica em [`progresso.md`](/docs/tasks/looks/progresso.md).

**O prefixo deste pool é `CORR-LOOKS-`**, com numeração contínua a partir de
`001`. O pool é único dentro do ciclo, e não se cruza com o de nenhuma outra
pasta — o ciclo de PES2 tem o seu em
[`/docs/tasks/correcoes-progresso.md`](/docs/tasks/correcoes-progresso.md), o
do port do `.mcr` em
[`/docs/tasks/port-mcr/correcoes-progresso.md`](/docs/tasks/port-mcr/correcoes-progresso.md),
e o ciclo arquivado, o dele em
[`/docs/tasks/concluidos/correcoes-progresso.md`](/docs/tasks/concluidos/correcoes-progresso.md).

## Resumo

| ID | ID Task Origem | Título | Criticidade | Status | Concluída em |
| -- | -------------- | ------ | ----------- | ------ | ------------ |
| [CORR-LOOKS-001](/docs/tasks/looks/CORR-LOOKS-001.md) | [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | A raiz do Superpack tem treze pastas de jogo, não catorze | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-002](/docs/tasks/looks/CORR-LOOKS-002.md) | [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | O comentário do `.gitignore` guarda o número que a própria task derrubou | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-003](/docs/tasks/looks/CORR-LOOKS-003.md) | [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | `superpack_count.py` descarta entrada ilegível em silêncio | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-004](/docs/tasks/looks/CORR-LOOKS-004.md) | [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | A LOOKS-TASK-18 se contradiz sobre as 50 tuplas em dois bullets seguidos | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-005](/docs/tasks/looks/CORR-LOOKS-005.md) | [LOOKS-TASK-02](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md) | A guarda dos dois discos não tem quem a chame, e nada obriga a 03 a chamá-la | Alta | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-006](/docs/tasks/looks/CORR-LOOKS-006.md) | [LOOKS-TASK-02](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md) | A recusa do `/SELECT.BIN` sai como `digest mismatch` pelado | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-007](/docs/tasks/looks/CORR-LOOKS-007.md) | [LOOKS-TASK-02](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md) | O `layout.py` diz que não faz I/O, e faz | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-008](/docs/tasks/looks/CORR-LOOKS-008.md) | [LOOKS-TASK-03](/docs/tasks/looks/03-fonte-de-disco-e-layout.md) | O `BASE` é derivável e nunca é derivado — `require_base()` não tem chamador nenhum | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-009](/docs/tasks/looks/CORR-LOOKS-009.md) | [LOOKS-TASK-03](/docs/tasks/looks/03-fonte-de-disco-e-layout.md) | A varredura da regra 1 não tem caso vermelho, e nada diz quanto ela varreu | Alta | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-010](/docs/tasks/looks/CORR-LOOKS-010.md) | [LOOKS-TASK-04](/docs/tasks/looks/04-formato-de-secao.md) | O `EDT_MOD.BIN` tem 20 seções e duas listas de onze — a varredura começou a 15.704 | Alta | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-011](/docs/tasks/looks/CORR-LOOKS-011.md) | [LOOKS-TASK-04](/docs/tasks/looks/04-formato-de-secao.md) | O `sweep_addresses()` guarda duas regex mortas com o nome das vivas | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-012](/docs/tasks/looks/CORR-LOOKS-012.md) | [LOOKS-TASK-05](/docs/tasks/looks/05-arquivos-de-modelo.md) | O perfil promete o `looks_image` desde a 05, e `ctest -R looks` sai 0 sem achar teste | Alta | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-013](/docs/tasks/looks/CORR-LOOKS-013.md) | [LOOKS-TASK-05](/docs/tasks/looks/05-arquivos-de-modelo.md) | O cabeçalho do `MODEL.BIN` foi descrito por metade — duas corridas, e a lista 0 declara o 1816 | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-014](/docs/tasks/looks/CORR-LOOKS-014.md) | [LOOKS-TASK-05](/docs/tasks/looks/05-arquivos-de-modelo.md) | O título da LOOKS-TASK-05 ainda diz onze seções; a tabela já diz vinte | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-015](/docs/tasks/looks/CORR-LOOKS-015.md) | [LOOKS-TASK-06](/docs/tasks/looks/06-harness-controles-e-selftest.md) | O gate obrigatório não é alcançável por `ctest` nesta máquina, e pedir por ele sai 0 | Alta | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-016](/docs/tasks/looks/CORR-LOOKS-016.md) | [LOOKS-TASK-06](/docs/tasks/looks/06-harness-controles-e-selftest.md) | Os dois alvos de `looks` ficaram fora do `if(Python3_FOUND)` que guarda os outros oito | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-017](/docs/tasks/looks/CORR-LOOKS-017.md) | [LOOKS-TASK-07](/docs/tasks/looks/07-oraculo-e-rota-ate-a-tela.md) | Sem `WE2002_LOOKS_IMAGE` o `--check-live` sobe o emulador e morre num traceback, em vez de pular com 77 | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-018](/docs/tasks/looks/CORR-LOOKS-018.md) | [LOOKS-TASK-08](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) | A palavra de página declara a profundidade da CLUT, e 1.039 das 2.841 primitivas dizem 8 bits | Alta | [x] concluída | 2026-09-15 |
| [CORR-LOOKS-019](/docs/tasks/looks/CORR-LOOKS-019.md) | [LOOKS-TASK-08](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) | O `--tmds` promete dizer se algum campo move um TMD e não pergunta: a metade negativa do veredito não sai de comando | Média | [x] concluída | 2026-09-15 |
| [CORR-LOOKS-020](/docs/tasks/looks/CORR-LOOKS-020.md) | [LOOKS-TASK-09](/docs/tasks/looks/09-nomear-as-onze-pecas.md) | Quatro seções têm dois parceiros de espelho, e o `mirrors()` fica com o primeiro sem dizer que havia escolha | Média | [x] concluída | 2026-09-15 |
| [CORR-LOOKS-021](/docs/tasks/looks/CORR-LOOKS-021.md) | [LOOKS-TASK-09](/docs/tasks/looks/09-nomear-as-onze-pecas.md) | "Mesma malha, uniforme diferente" não vale para quatro das onze peças, e o tronco está do lado errado da conta | Média | [x] concluída | 2026-09-15 |
| [CORR-LOOKS-022](/docs/tasks/looks/CORR-LOOKS-022.md) | [LOOKS-TASK-10](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md) | Os "2.151 registros a mais em 40 contêineres" que decidem onde o conserto mora não reproduzem por nenhuma leitura | Alta | [x] concluída | 2026-09-15 |
| [CORR-LOOKS-023](/docs/tasks/looks/CORR-LOOKS-023.md) | [LOOKS-TASK-10](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md) | A exclusividade da paleta de chuteira é conferida só no `EDT_MOD.BIN`, e seis seções do `MODEL.BIN` a amostram | Baixa | [x] concluída | 2026-09-15 |
| [CORR-LOOKS-024](/docs/tasks/looks/CORR-LOOKS-024.md) | [LOOKS-TASK-11](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md) | A §1.7 ainda diz que o cabelo está no offset 8 e que 1.175 primitivas amostram fora do arquivo | Média | [x] concluída | 2026-09-15 |
| [CORR-LOOKS-025](/docs/tasks/looks/CORR-LOOKS-025.md) | [LOOKS-TASK-11](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md) | Cada `TEX_*.BIN` tem cinco paletas de 256, não duas, e o "casa e fora" é inferência sem medição | Média | [x] concluída | 2026-09-15 |
| [CORR-LOOKS-026](/docs/tasks/looks/CORR-LOOKS-026.md) | [LOOKS-TASK-12](/docs/tasks/looks/12-pele-paleta-ou-vertice.md) | A grade dá conta do que os três campos alcançam, não do que o registro é — 948 primitivas moram na coluna 1 | Média | [x] concluída | 2026-09-15 |
| [CORR-LOOKS-027](/docs/tasks/looks/CORR-LOOKS-027.md) | [LOOKS-TASK-13](/docs/tasks/looks/13-campos-e-dominios-de-looks.md) | O cross-check contra os 50 JPGs é critério marcado e não existe comando que o rode | Baixa | [x] concluída | 2026-09-15 |
| [CORR-LOOKS-028](/docs/tasks/looks/CORR-LOOKS-028.md) | [LOOKS-TASK-14](/docs/tasks/looks/14-tabela-de-montagem.md) | O `draw_list` aplica a primeira das faixas que o `HAIR_MAP` mediu e descarta as outras, sem dizer | Alta | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-029](/docs/tasks/looks/CORR-LOOKS-029.md) | [LOOKS-TASK-14](/docs/tasks/looks/14-tabela-de-montagem.md) | O `HEAD_RUNS` diz "todo corpo distinto, cada um com sua janela" e o disco diz doze corpos e catorze janelas | Média | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-030](/docs/tasks/looks/CORR-LOOKS-030.md) | [LOOKS-TASK-14](/docs/tasks/looks/14-tabela-de-montagem.md) | A décima terceira seção do mapa de cabelo — o `E2` na 54 — não está em nenhuma das três listas | Baixa | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-031](/docs/tasks/looks/CORR-LOOKS-031.md) | [LOOKS-TASK-14](/docs/tasks/looks/14-tabela-de-montagem.md) | A constante `AGREEMENT` justifica o piso do corpus com 0,005 e a medição dá 0,008 | Baixa | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-032](/docs/tasks/looks/CORR-LOOKS-032.md) | [LOOKS-TASK-14](/docs/tasks/looks/14-tabela-de-montagem.md) | O bloco de gates da LOOKS-TASK-14 ficou na primeira passagem — 29 controles contra 32 | Baixa | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-033](/docs/tasks/looks/CORR-LOOKS-033.md) | [LOOKS-TASK-14](/docs/tasks/looks/14-tabela-de-montagem.md) | A §6(c) do plano ainda se declara medida em parte, com a task pendente | Baixa | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-034](/docs/tasks/looks/CORR-LOOKS-034.md) | [LOOKS-TASK-15](/docs/tasks/looks/15-visualizador-opengl.md) | Nenhum campo de cor alcança a cabeça quando o cabelo não é da família A | Alta | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-035](/docs/tasks/looks/CORR-LOOKS-035.md) | [LOOKS-TASK-15](/docs/tasks/looks/15-visualizador-opengl.md) | A definição de pronto do plano pede uma tupla que a tabela recusa | Média | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-036](/docs/tasks/looks/CORR-LOOKS-036.md) | [LOOKS-TASK-15](/docs/tasks/looks/15-visualizador-opengl.md) | O critério da LOOKS-TASK-15 conta 11.789 linhas e a árvore dela tem 11.831 | Baixa | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-037](/docs/tasks/looks/CORR-LOOKS-037.md) | [LOOKS-TASK-15](/docs/tasks/looks/15-visualizador-opengl.md) | As alturas da cabeça e da chuteira estão escritas com o sinal trocado | Baixa | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-038](/docs/tasks/looks/CORR-LOOKS-038.md) | [LOOKS-TASK-15](/docs/tasks/looks/15-visualizador-opengl.md) | A cor de barba troca a superfície e não muda um pixel do quadro | Média | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-039](/docs/tasks/looks/CORR-LOOKS-039.md) | [LOOKS-TASK-16](/docs/tasks/looks/16-contratos-da-ui.md) | Os pares do `looks_ui` nunca saem da família A, e o defeito da CORR-LOOKS-034 passou por eles | Média | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-040](/docs/tasks/looks/CORR-LOOKS-040.md) | [LOOKS-TASK-16](/docs/tasks/looks/16-contratos-da-ui.md) | O `looks_ui` só julga a cabeça, e passa com a figura inteira apagada | Média | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-041](/docs/tasks/looks/CORR-LOOKS-041.md) | [LOOKS-TASK-16](/docs/tasks/looks/16-contratos-da-ui.md) | O bloco de gates da LOOKS-TASK-16 diz 12.609 linhas e a árvore dela tem 12.613 | Baixa | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-042](/docs/tasks/looks/CORR-LOOKS-042.md) | [LOOKS-TASK-17](/docs/tasks/looks/17-confronto-com-o-emulador.md) | Os quads de cabelo saem uma linha curtos — o jogo desenha v 15 onde o disco guarda 14 | Média | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-043](/docs/tasks/looks/CORR-LOOKS-043.md) | [LOOKS-TASK-17](/docs/tasks/looks/17-confronto-com-o-emulador.md) | O goleiro desenha qualquer estilo de cabelo como família A, e não recusa | Média | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-044](/docs/tasks/looks/CORR-LOOKS-044.md) | [LOOKS-TASK-17](/docs/tasks/looks/17-confronto-com-o-emulador.md) | A tabela diz que a tela da barba alcança cinco valores, e a tela alcança sete | Alta | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-045](/docs/tasks/looks/CORR-LOOKS-045.md) | [LOOKS-TASK-17](/docs/tasks/looks/17-confronto-com-o-emulador.md) | O veredito `ranked` aceita qualquer liderança acima de zero, e a razão escrita só cobre teto pequeno | Média | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-046](/docs/tasks/looks/CORR-LOOKS-046.md) | [LOOKS-TASK-17](/docs/tasks/looks/17-confronto-com-o-emulador.md) | Um `.refused` velho faz o `--score` pular uma tupla que já desenha, e o gate passa sem julgá-la | Alta | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-047](/docs/tasks/looks/CORR-LOOKS-047.md) | [LOOKS-TASK-17](/docs/tasks/looks/17-confronto-com-o-emulador.md) | O mapa de cabelo do goleiro não foi medido, e 136 dos 179 goleiros do disco são recusados | Média | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-048](/docs/tasks/looks/CORR-LOOKS-048.md) | [LOOKS-TASK-17](/docs/tasks/looks/17-confronto-com-o-emulador.md) | Ninguém leu o que as barbas `F` e `G` escrevem, e 28 jogadores do disco e 16 renders do corpus são recusados | Média | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-049](/docs/tasks/looks/CORR-LOOKS-049.md) | [LOOKS-TASK-18](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md) | Nas cabeças que não são A1, a pele pinta só a testa e a barba não aparece — os índices emprestados da seção 24 erram | Alta | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-050](/docs/tasks/looks/CORR-LOOKS-050.md) | [LOOKS-TASK-18](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md) | O `corpus.py` julga a pele 47 de 47 com doze peles desenhadas erradas, e o erro que ele achou não o deixa vermelho | Média | [x] concluída | 2026-09-16 |
| [CORR-LOOKS-051](/docs/tasks/looks/CORR-LOOKS-051.md) | [LOOKS-TASK-19](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md) | O `looks_live` perde a sessão MCP no primeiro `pause`, uma vez em catorze corridas | Média | [x] concluída | 2026-09-17 |
| [CORR-LOOKS-052](/docs/tasks/looks/CORR-LOOKS-052.md) | [LOOKS-TASK-19](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md) | "O `modelfile` roda primeiro" é regra com controle, e a ordem não muda o veredito do `cli.py check` | Baixa | [x] concluída | 2026-09-17 |
| [CORR-LOOKS-053](/docs/tasks/looks/CORR-LOOKS-053.md) | [LOOKS-TASK-19](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md) | A LOOKS-TASK-19 diz "quatro alvos" no título e "três" no objetivo, e mantém como convenção o `if(UNIX …)` que ela mediu errado | Baixa | [x] concluída | 2026-09-17 |
| [CORR-LOOKS-054](/docs/tasks/looks/CORR-LOOKS-054.md) | [LOOKS-TASK-21](/docs/tasks/looks/21-a-tela-medida.md) | O `screen.json` guarda o título `LOOKS SET`, a tela desenha `S SET`, e nenhum gate compara os dois | Baixa | [x] concluída | 2026-09-17 |
| [CORR-LOOKS-055](/docs/tasks/looks/CORR-LOOKS-055.md) | [LOOKS-TASK-21](/docs/tasks/looks/21-a-tela-medida.md) | `screen.py --report` morre no `■` da ajuda, e a mensagem de falha do `--screen` morreria igual | Média | [x] concluída | 2026-09-17 |
| [CORR-LOOKS-056](/docs/tasks/looks/CORR-LOOKS-056.md) | [LOOKS-TASK-22](/docs/tasks/looks/22-a-tela-na-janela.md) | O `CLAUDE.md` descreve um ciclo fechado e um visualizador de tupla, e o que existe é a tela `LOOKS SET` num ciclo aberto | Baixa | [x] concluída | 2026-09-17 |
| [CORR-LOOKS-057](/docs/tasks/looks/CORR-LOOKS-057.md) | [LOOKS-TASK-23](/docs/tasks/looks/23-default-por-nacionalidade.md) | O docstring do `layout.PLAYER_NATION` ensina a regra `código = índice − 1` que a própria task desmentiu | Média | [x] concluída | 2026-09-17 |
| [CORR-LOOKS-058](/docs/tasks/looks/CORR-LOOKS-058.md) | [LOOKS-TASK-24](/docs/tasks/looks/24-de-onde-vem-a-pose.md) | O docstring do `layout.POSE_MATRIX` reparte as 40 paradas de um jeito que a ferramenta não reproduz | Baixa | [x] concluída | 2026-09-18 |
| [CORR-LOOKS-059](/docs/tasks/looks/CORR-LOOKS-059.md) | [LOOKS-TASK-24](/docs/tasks/looks/24-de-onde-vem-a-pose.md) | O plano diz que o `derive_base()` responde `0x8017EE60` para o `ANIME.BIN`, e ele recusa o arquivo | Baixa | [x] concluída | 2026-09-18 |
| [CORR-LOOKS-060](/docs/tasks/looks/CORR-LOOKS-060.md) | [LOOKS-TASK-25](/docs/tasks/looks/25-a-pose-de-referencia.md) | "Todos os outros ficam abaixo de 2,3x" — a corrida imprime 2,5x na cabeça do slot 2 | Baixa | [x] concluída | 2026-09-18 |

**Legenda de status:** `[ ] pendente` · `[~] em andamento` · `[x] concluída`

**Criticidade** é sobre o efeito, não sobre o tamanho do conserto:

- **Alta** — a task entregou algo que mede errado, ou um gate que passa sem
  medir. Neste ciclo isso inclui qualquer guarda que fique verde lendo o disco
  errado, porque esse erro não tem sintoma.
- **Média** — o resultado está certo mas a evidência não sustenta, ou o código
  viola uma das três regras de desenho.
- **Baixa** — documentação, número que não reproduz, link ou nome.

## Checklist

- [x] CORR-LOOKS-001 — treze pastas na raiz do Superpack, não catorze
- [x] CORR-LOOKS-002 — o `.gitignore` ainda descreve a raiz com o número da subpasta
- [x] CORR-LOOKS-003 — `superpack_count.py` tem de falhar alto no que não conseguiu ler
- [x] CORR-LOOKS-004 — o primeiro bullet da LOOKS-TASK-18 desmente o terceiro
- [x] CORR-LOOKS-005 — nada obriga o `iso_source.py` a passar pela guarda
- [x] CORR-LOOKS-006 — o `/SELECT.BIN` recusa sem dizer que o disco é o inglês
- [x] CORR-LOOKS-007 — o docstring do `layout.py` promete o que a dívida da 03 ainda deve
- [x] CORR-LOOKS-008 — nenhum comando redeixa o `BASE` a partir dos arquivos reais
- [x] CORR-LOOKS-009 — o `--sweep` só foi visto verde, e não diz quanto varreu
- [x] CORR-LOOKS-010 — a varredura do `EDT_MOD.BIN` leu 11 de 20 seções
- [x] CORR-LOOKS-011 — duas regex mortas no `sweep_addresses()`, com o nome das vivas
- [x] CORR-LOOKS-012 — não existe alvo `looks_image`, e pedir por ele sai verde
- [x] CORR-LOOKS-013 — 12 listas miram 104 e 4 miram 232; a lista de 72 declara o 1816
- [x] CORR-LOOKS-014 — título da 05 no frontmatter diz 11, a tabela diz 20
- [x] CORR-LOOKS-015 — `ctest -R looks` não acha os alvos em build nenhum, e sai 0
- [x] CORR-LOOKS-016 — os dois alvos de `looks` estão fora da guarda de Python
- [x] CORR-LOOKS-017 — o quarto pré-requisito do `--check-live` não tem caminho de skip
- [x] CORR-LOOKS-018 — 1.039 de 2.841 primitivas amostram em CLUT de 8 bits, e o plano só diz 4
- [x] CORR-LOOKS-019 — nenhum comando cruza o resíduo do `--fields` com o mapa de TMDs
- [x] CORR-LOOKS-020 — o pareamento de espelho escolhe entre dois candidatos em silêncio
- [x] CORR-LOOKS-021 — braço e antebraço têm malha diferente nos dois bonecos, e o resumo diz que não
- [x] CORR-LOOKS-022 — o número que justifica não tocar o `bin_archive.py` não reproduz
- [x] CORR-LOOKS-023 — trinta primitivas do `MODEL.BIN` também amostram a paleta da chuteira
- [x] CORR-LOOKS-024 — a §1.7 guarda as duas afirmações que a §1.8 derrubou, e a §1.8 diz seis por três
- [x] CORR-LOOKS-025 — são cinco paletas de 256 por `TEX_*.BIN`, e "casa e fora" não foi medido
- [x] CORR-LOOKS-026 — nove primitivas da cabeça não andam com campo de cor nenhum, e a coluna 1 tem 948 moradores
- [x] CORR-LOOKS-027 — nenhum comando lê os nomes dos 50 JPGs, e o critério diz que leu
- [x] CORR-LOOKS-028 — a segunda faixa medida do cabelo é descartada em silêncio
- [x] CORR-LOOKS-029 — "32 corpos distintos" são 32 seções; as malhas são 12 e 24
- [x] CORR-LOOKS-030 — o `E2` e a seção 54 faltam nas três listas que dizem treze
- [x] CORR-LOOKS-031 — o piso do corpus é justificado com 0,005 e a medição dá 0,008
- [x] CORR-LOOKS-032 — os gates transcritos são de antes dos controles da própria task
- [x] CORR-LOOKS-033 — a fonte de verdade ainda diz que a LOOKS-TASK-14 está pendente
- [x] CORR-LOOKS-034 — SKIN, H.COL, H.F.COL. e FACE não movem um pixel fora da seção 24
- [x] CORR-LOOKS-035 — o item 3 da definição de pronto sai 2
- [x] CORR-LOOKS-036 — a varredura da regra 1 foi anotada antes do fim da task
- [x] CORR-LOOKS-037 — os intervalos de y são os do render, não os do arquivo
- [x] CORR-LOOKS-038 — a cor de barba muda a superfície e não muda o desenho
- [x] CORR-LOOKS-039 — o gate da UI mede a única cabeça em que o código funcionava
- [x] CORR-LOOKS-040 — onze das doze peças estão fora do gate da UI
- [x] CORR-LOOKS-041 — a varredura foi anotada antes da última edição, outra vez
- [x] CORR-LOOKS-042 — o jogo reescreve o `v` do quad de cabelo, e nós somamos ao do disco
- [x] CORR-LOOKS-043 — a recusa do `head_of` só vale para a figura 0
- [x] CORR-LOOKS-044 — `FACE` recusa `F` e `G`, que a tela oferece nos dois slots
- [x] CORR-LOOKS-045 — o piso do confronto é zero, e a justificativa diz outra coisa
- [x] CORR-LOOKS-046 — o `.refused` velho tira da matriz a tupla que a próxima medição destrava
- [x] CORR-LOOKS-047 — a figura 1 só desenha o `A1`, e três em cada quatro goleiros são recusados
- [x] CORR-LOOKS-048 — `F` e `G` estão na tela e o que escrevem não foi lido
- [x] CORR-LOOKS-049 — o corpus mede errado o índice de cor emprestado da seção 24
- [x] CORR-LOOKS-050 — o gate do corpus não fica vermelho no erro sistemático que existe para achar
- [x] CORR-LOOKS-051 — `missing or invalid MCP-Session-Id` logo depois de o emulador subir
- [x] CORR-LOOKS-052 — um controle vermelho por uma propriedade que o gate não tem
- [x] CORR-LOOKS-053 — prosa vencida dentro da própria task
- [x] CORR-LOOKS-054 — o título da tela não passa pela conferência contra os glifos
- [x] CORR-LOOKS-055 — o gate imprime texto medido numa saída que não o codifica
- [x] CORR-LOOKS-056 — a seção do `looks` no `CLAUDE.md` ficou na v1
- [x] CORR-LOOKS-057 — a regra errada do código de nação sobrevive no `layout.py`
- [x] CORR-LOOKS-058 — 18 e 17 no módulo, 18 e 18 em toda corrida
- [x] CORR-LOOKS-059 — a base errada não é a que a regra responde, é a que sobra dela
- [x] CORR-LOOKS-060 — o limiar da hierarquia escrito 0,2 abaixo do medido

## Detalhes por correção

### CORR-LOOKS-001

- **Arquivo com problema:** `NOTICE.md`, `docs/PLAN-LOOKS-PY.md` §2 e o Log da
  `01-base-legal-e-linhagem.md`
- **Sintoma:** os três dizem "catorze pastas de jogo" na raiz do Superpack; são
  treze, e a frase do plano lista treze nomes logo em seguida
- **Como foi detectado:** `python tools/looks/superpack_count.py
  "C:/games/we2002/Superpackv6"` imprime catorze **linhas**, das quais uma é o
  `Cronologia We-Pes-IssPro.htm`; um `os.listdir` separando por tipo dá 13 e 1
- **Fix:** trocar o número nos três, dizendo "pastas" e não "jogos" — as três
  `We2000 *` são um jogo só

### CORR-LOOKS-002

- **Arquivo com problema:** `.gitignore`, comentário da entrada `/Superpackv6/`
- **Sintoma:** o comentário descreve a coletânea inteira como "4,2 GB, 28.720
  arquivos", que é a subpasta `We2002\` — exatamente o erro que esta task
  corrigiu no plano e no `NOTICE.md`, no mesmo commit
- **Como foi detectado:** confronto das três descrições do Superpack no
  repositório contra a saída do `superpack_count.py` (4,50 GiB, 31.790)
- **Fix:** `4,5 GiB, 31.790 arquivos` no comentário, com meia linha dizendo que
  28.720 deles estão em `We2002\`

### CORR-LOOKS-003

- **Arquivo com problema:** `tools/looks/superpack_count.py`
- **Sintoma:** arquivo ilegível some da conta (`except OSError: continue`),
  entrada de topo ilegível some da repartição (`except OSError: pass`) e
  subpasta sem permissão some inteira, porque `os.walk` roda com o
  `onerror=None` de default. A saída sai somada e com cara de completa
- **Como foi detectado:** leitura dirigida pela pergunta que o `02-revisar.md`
  faz de toda ferramenta — falha alto ou emite parcial? — e por
  `os.walk` sobre raiz ilegível devolver zero entrada sem erro. O número de
  hoje está certo: a revisão o reproduziu byte a byte
- **Fix:** contar o que foi pulado, imprimir `skipped: N`, sair != 0 quando
  `N > 0`, e um caso vermelho no `self_check()` exigindo `skipped == 1`

### CORR-LOOKS-004

- **Arquivo com problema:** `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md`
- **Sintoma:** o primeiro bullet do Contexto diz que os 50 JPGs são "nomeados
  pela tupla exata" e o terceiro diz que são 49 — o achado entrou por bullet
  novo sem corrigir a frase que ele desmente
- **Como foi detectado:** leitura do arquivo contra a §5.4 do plano, que a
  mesma execução corrigiu certo, mais a contagem da pasta (50 `.jpg`, o
  primeiro em ordem sendo `0.jpg`)
- **Fix:** reescrever o primeiro bullet na forma da §5.4

### CORR-LOOKS-005

- **Arquivo com problema:** `docs/tasks/looks/03-fonte-de-disco-e-layout.md` e
  a §4.5 do plano
- **Sintoma:** `layout.require()` recusa certo, mas o único chamador é o
  `_check_discs()` — que a 03 tem por critério **mover**. Nenhum critério da 03
  manda o `iso_source.py` passar pela guarda, e fechada ao pé da letra o ciclo
  fica com uma guarda testada e inalcançável
- **Como foi detectado:** `grep -rn "require(" tools/ --include=*.py` acha três
  ocorrências, todas dentro do próprio `layout.py`, mais a leitura do critério
  da 03
- **Fix:** item de critério na 03 exigindo que toda leitura passe por
  `layout.require()`, com caso vermelho vivo pelo `iso_source.py`, e a §4.5
  dizendo quem chama a guarda e não só que ela existe

### CORR-LOOKS-006

- **Arquivo com problema:** `tools/looks/layout.py`, ramo de dica do `require()`
- **Sintoma:** `/SELECT.BIN` não está em `TEXTURE_FILES` nem em
  `GEOMETRY_FILES`, então recusa com `digest mismatch` pelado — a mensagem que
  o docstring do módulo diz ser a errada. É um dos dois arquivos que diferem
  entre os discos, e a causa provável da recusa é a mesma do `DAT2D.BIN`
- **Como foi detectado:** `require(layout.SELECT, …)` direto, comparado com o
  mesmo estímulo no `DAT2D.BIN`; e os digests dos dois discos remedidos
  (`86d14a66…` × `c9e1eaf8…`)
- **Fix:** dica própria para o `/SELECT.BIN` e um `assert` no `self_check()` de
  que **todo** caminho de `DIGEST` produz dica não vazia

### CORR-LOOKS-007

- **Arquivo com problema:** `tools/looks/layout.py`, docstring de topo
- **Sintoma:** diz "It also does no I/O" e o `_check_discs()` do mesmo arquivo
  abre duas imagens de CD. A dívida é conhecida e está na 03; o que está errado
  é afirmar hoje a propriedade que só vale depois dela
- **Como foi detectado:** leitura do módulo contra ele mesmo — `grep -n
  "iso.Image\|import iso" tools/looks/layout.py` dá três linhas
- **Fix:** ressalva no docstring, com a data e o destino, e a linha da 03
  mandando removê-la junto com a função

### CORR-LOOKS-008

- **Arquivo com problema:** `tools/looks/iso_source.py` (o `_check_discs()`), e
  a §4.5 do plano
- **Sintoma:** `derive_base()` e `require_base()` só rodam sobre vetores
  sintéticos dentro do `self_check()`. O único comando que abre os discos reais
  confere digest e não deriva base nenhuma, então as duas constantes de `BASE`
  ficam cravadas na prática, contra o que o critério da task pede. Os números do
  Log (2/18 palavras, 642/1.703, 24/240, alvos 8..112 e 72..1.712) vieram de
  script descartado, e reconferi-los exigiu escrever outro
- **Como foi detectado:** `grep -rn "require_base\|derive_base" tools/
  --include=*.py | grep -v layout.py` sai vazio; a derivação reproduzida à mão
  bate com o Log nos dois arquivos
- **Fix:** o `--check-discs` chama `require_base()` nos dois arquivos de
  geometria, nos dois discos, imprime cabeçalho/base/constante e sai != 0 em
  `WrongBase`

### CORR-LOOKS-009

- **Arquivo com problema:** `tools/looks/layout.py` (`sweep_addresses()`) e o
  critério da `06-harness-controles-e-selftest.md`
- **Sintoma:** a varredura que faz cumprir a regra 1 é a única peça do módulo
  sem caso vermelho, e nunca foi observada achando nada. Filtro quebrado, raiz
  errada ou blanqueamento demais imprimem a mesma frase verde, porque a saída
  não diz quantos arquivos varreu. E nenhum alvo a roda: o critério da 06 não
  nomeia o `sweep_addresses()`, então autoriza um segundo varredor
- **Como foi detectado:** `grep -n sweep tools/looks/layout.py` não acha
  ocorrência dentro do `self_check()`; árvore sintética em `tempfile` mostra
  que a varredura funciona — teste que esta revisão teve de escrever e que não
  fica
- **Fix:** caso vermelho no `self_check()` com os cinco sub-casos (hex,
  subpasta, escape na linha, escape na linha de cima, `layout.py` sintético),
  contagem de arquivos e linhas na saída, isenção do dono por caminho e não por
  nome, e a 06 obrigada a reusar a função

### CORR-LOOKS-010

- **Arquivo com problema:** a §1.5 do plano, o critério da
  `05-arquivos-de-modelo.md`, e o Log da `04-formato-de-secao.md`
- **Sintoma:** a varredura do `EDT_MOD.BIN` começa no offset 15.704 — a 43% do
  arquivo — e o Log a reporta como "11 seções … termina em 36.072 EXATO", sem
  dizer de onde partiu. Do offset 216, que é o primeiro alvo da **segunda** lista
  de ponteiros do cabeçalho, a mesma ferramenta acha **20 seções, 1.218
  vértices, 1.074 primitivas**. São dois modelos de onze peças, compartilhando
  15.704 e 17.572. A região que a §1.5 chama de "material de textura" é
  geometria, e o "cabeçalho TIM em 3.228" cai dentro da seção 2.608–3.432
- **Como foi detectado:** `section.scan(edt, 216)` contra `section.scan(edt,
  15704)`, mais o dump das duas listas e dos bytes em 3.228
- **Fix:** §1.5 reescrita no lugar; o critério da 05 pede 20/1.218/1.074 a
  partir de 216 e modelo **por lista**; a 08 ganha a linha de que são três
  candidatos e não dois; e o início do `EDT_MOD.BIN` passa a ser derivado ou
  constante do `layout.py`

### CORR-LOOKS-011

- **Arquivo com problema:** `tools/looks/layout.py`, topo do `sweep_addresses()`
- **Sintoma:** a reescrita para `tokenize` deixou `hex_literal` e `big_decimal`
  compiladas e sem uso na função do comando, enquanto as que decidem vivem no
  `_address_lines()` **com os mesmos nomes** e padrões ancorados. Quem for
  mudar o que conta como endereço edita as de cima e não muda nada
- **Como foi detectado:** `awk '/^def sweep_addresses/,/^def _address_lines/'
  tools/looks/layout.py | grep hex_literal` — duas atribuições, nenhuma leitura
- **Fix:** apagar as duas linhas mortas, ou promover as vivas a constante de
  módulo com nome próprio; um nome, uma definição

### CORR-LOOKS-012

- **Arquivo com problema:** `tests/CMakeLists.txt` (o alvo que falta) e a tabela
  de gates de `docs/prompts/perfil-looks.md`
- **Sintoma:** o perfil dá o `looks_image` como existente desde a LOOKS-TASK-05
  e não há linha nenhuma sobre `looks` no `tests/CMakeLists.txt`.
  `ctest --test-dir build -R looks` imprime `No tests were found!!!` e **sai
  0** — ausência indistinguível de verde, que é o que o próprio perfil proíbe
  ("mediu e passou, ou pulou com 77"). A verificação existe e é o
  `modelfile.py --check-image`, que ninguém roda sem se lembrar dele. E a
  LOOKS-TASK-19 diz criar "os três alvos", o que contradiz a tabela
- **Como foi detectado:** `grep -rn looks tests/CMakeLists.txt` vazio, e
  `ctest --test-dir build -R looks` com `echo $?`
- **Fix:** registrar o `looks_image` (77 sem `WE2002_LOOKS_IMAGE`), e alinhar a
  tabela de gates do perfil com a 19 sobre quem cria cada alvo

### CORR-LOOKS-013

- **Arquivo com problema:** o docstring de `layout.geometry_start()`, o último
  item do critério da `05-arquivos-de-modelo.md`, a §1.5 do plano e a linha
  encaminhada à `08-de-onde-vem-o-boneco.md`
- **Sintoma:** "16 das 18 listas abrem com tag `0x80` mirando o offset 104" —
  16 abrem com `0x80`, mas só **12** miram 104; **4** miram **232**, uma
  **segunda** corrida de ponteiros (32 contra 64). E "1816 é fato que as listas
  não declaram" — a lista de 72 tem uma entrada só, tag `0x02`, mirando
  exatamente 1816; a de 88 mira 4792. A decisão de não derivar o início do
  `MODEL.BIN` continua certa (`min` de todos os alvos é 104), mas a evidência
  escrita não a sustenta, e a segunda corrida não está registrada em lugar
  nenhum
- **Como foi detectado:** `layout.read_pointer_entries()` sobre as 18 listas,
  mais um parser independente que concorda, e `section.read_section()` em 104,
  232, 1816 e 4792
- **Fix:** corrigir os quatro textos com os números medidos, registrar as duas
  corridas e as duas listas de uma entrada, e dizer o motivo verdadeiro de a
  constante ficar

### CORR-LOOKS-014

- **Arquivo com problema:** `docs/tasks/looks/05-arquivos-de-modelo.md`,
  frontmatter
- **Sintoma:** o `title:` ainda diz "as 11 do `EDT_MOD.BIN`" e a célula da
  tabela do `progresso.md` já diz "as 20" — a CORR-LOOKS-010 atualizou um dos
  dois lugares onde o título mora. O `check_tasks.py` não confere título e fica
  verde
- **Como foi detectado:** `grep -n "^title:"` na task contra a linha 41 do
  `progresso.md`
- **Fix:** frontmatter passa a dizer 20, e um laço confere as vinte tasks de uma
  vez

### CORR-LOOKS-015

- **Arquivo com problema:** `docs/prompts/perfil-looks.md` (a tabela de gates) e
  a `19-alvos-de-ctest-e-cli.md`
- **Sintoma:** o `looks_selftest` está registrado no `tests/CMakeLists.txt` e
  **nenhum** dos três diretórios de build deste worktree o conhece:
  `ctest -R looks` responde `No tests were found!!!` e sai **0** nos três. O
  remédio que o Log da task propõe — reconfigurar o build — não funciona aqui:
  `cmake -S . -B <novo>` morre em `Could NOT find CURL`
  (`src/core/CMakeLists.txt:1`), e o `tools/looks/` não precisa de curl, de Qt
  nem de compilador. É o mesmo sintoma da CORR-LOOKS-012, que foi fechada sem
  que o `ctest` desta máquina jamais tivesse listado o alvo
- **Como foi detectado:** `ctest --test-dir {build,build-mingw,
  build-windows-release} -R looks` com `echo $?`; `grep -rl looks --include=
  CTestTestfile.cmake .` vazio; `CMAKE_HOME_DIRECTORY` do `build/` apontando
  para `/home/ingmar/...`; e uma configuração nova falhando em CURL
- **Fix:** o perfil passa a dizer, por alvo, o comando que roda **nesta**
  máquina (`python tools/looks/selftest.py`), a armadilha do `ctest -R` vazio
  saindo 0 entra na lista, e a 19 fecha a conta com o comando que existe.
  Tornar os alvos de `looks` configuráveis sem o `src/core` é decisão do dono
  do repositório, não de execução

### CORR-LOOKS-016

- **Arquivo com problema:** `tests/CMakeLists.txt`, linhas 205 e 210
- **Sintoma:** os oito testes Python do arquivo estão dentro de
  `if(Python3_FOUND)`; os dois de `looks` ficaram em `depth=0`. Sem Python
  detectado, `${Python3_EXECUTABLE}` expande para nada e o `looks_selftest` —
  o gate que "nunca pula" — aparece como **Failed** por executável inexistente,
  mandando quem o vir procurar defeito em `tools/looks/`
- **Como foi detectado:** mapa de `if`/`endif` do arquivo com a profundidade de
  cada `add_test`
- **Fix:** envolver os dois em `if(Python3_FOUND)`, e de passagem pôr cada
  comentário imediatamente acima do `add_test` que ele explica — hoje eles estão
  na ordem inversa

### CORR-LOOKS-017

- **Arquivo com problema:** `tools/looks/oracle.py`, a preflight do
  `check_live()`
- **Sintoma:** o `--check-live` precisa de **quatro** coisas e confere três.
  Sem `WE2002_LOOKS_IMAGE` ele sobe o emulador, esconde a janela, roda cinco
  verificações e então morre com `RuntimeError` e traceback (rc=1) dentro do
  `verify_load()` — nem mediu nem pulou com 77, que é o contrato do perfil. A
  mensagem certa já existe no `iso_source.image_from_env()`, e o módulo irmão
  (`modelfile.py --check-image`) já converte esse mesmo erro em skip 77
- **Como foi detectado:** rodando `--check-live` só com
  `WE2002_LOOKS_DRIVE_IMAGE` posta; os outros três caminhos de skip foram
  reproduzidos e saem 77 corretamente. Com as duas variáveis, o comando fecha
  verde e **todos** os números do Log reproduzem
- **Fix:** conferir a imagem japonesa na preflight, antes de qualquer `launch`,
  convertendo o `RuntimeError` em skip 77; e listar os pré-requisitos num só
  lugar, para o quinto não repetir a história

### CORR-LOOKS-018

- **Arquivo com problema:** `tools/looks/section.py` (`Primitive.tpage_vram`),
  `docs/PLAN-LOOKS-PY.md` §1.6 e §1.7
- **Sintoma:** a releitura da primitiva registrou **onde** a página de textura
  está e não **como** ela é amostrada. Os bits 7-8 do `tpage` são a
  profundidade, e os três valores do disco não concordam: `0x18` e `0x1A` são
  4 bits, `0x99` é **8 bits** — e ele é **1.039 das 2.841** primitivas, 666
  de 1.074 no `EDT_MOD.BIN`. O plano só tem a frase `4-bit CLUT`, de uma
  amostra do `get_gpu_state`, e a §1.7 diz "128×128 a 4 bpp cada". CLUT de 4
  bits tem 16 entradas, a de 8 tem 256: a LOOKS-TASK-10 caça a lista de
  paletas por marcador e erra em silêncio com a largura errada. De quebra,
  **duas das três páginas não têm entrada no `DAT2D.BIN`**
- **Como foi detectado:** remedindo os 2.841 `tpage` do disco japês com o
  `section.py` commitado e decodificando os bits do campo — as contagens por
  arquivo e por página estão na CORR
- **Fix:** `Primitive` expondo profundidade e semitransparência, com
  `self_check()` afirmando as duas páginas; §1.6 com a contagem por página e a
  profundidade de cada uma; §1.7 sem o "4 bpp" generalizado; e o critério da
  LOOKS-TASK-10 exigindo as duas larguras

### CORR-LOOKS-019

- **Arquivo com problema:** `tools/looks/oracle.py` — `check_tmds()` e
  `report_field()`
- **Sintoma:** o docstring do `check_tmds()` pergunta *"and does any field move
  one?"* e a função nunca aperta tecla; o `--fields`, que move campo, não
  conhece TMD e joga tudo que não cai nos dois arquivos de modelo num contador
  único (`in no model file: 202 byte(s)`). "Fora dos arquivos de modelo" e
  "fora dos TMDs" são afirmações diferentes, e a segunda — que é a metade
  negativa do veredito da incógnita (a) — não sai de comando nenhum
- **Como foi detectado:** rodando `--tmds` e `--fields` e procurando a linha que
  cruza os dois. Ela não existe; o cruzamento foi feito nesta revisão com
  script descartável sobre a mesma API, e dá **0 de 202** (`SKIN` no slot 2) e
  **0 de 124** (`HAIR` no slot 1) dentro de `0x800c1678..0x800c4948`+4 KiB — a
  conclusão está certa, a evidência é que não está versionada
- **Fix:** `_tmd_headers()` devolvendo extensão, um `tmd_spans()` no feitio do
  `spans()`, o `report_field()` com **três** baldes (modelo, TMD, resto) e um
  controle negativo que estrague o mapa de TMD e exija vermelho

### CORR-LOOKS-020

- **Arquivo com problema:** `tools/looks/pieces.py`, `mirrors()`
- **Sintoma:** o `break` assume parceiro único, e **quatro seções têm dois** —
  7, 8, 18 e 19 —, porque as pernas dos dois bonecos têm conjunto de vértices
  idêntico (7≡18 e 8≡19, sem espelho). O resultado de hoje está certo por
  adjacência de índice, não por regra: alimentado com as seções na ordem
  `7, 19, 8, 18`, o `mirrors()` pareia **cruzando os dois bonecos** e nada na
  saída diz que houve escolha. Todos os nomes dependem do pareamento, porque o
  `limbs()` corta por onde o lado troca
- **Como foi detectado:** chamando o `mirror_axis()` commitado para todos os
  pares de seções do `EDT_MOD.BIN` e contando candidatos por seção; e rodando
  o `mirrors()` em três ordens diferentes das mesmas seções
- **Fix:** parear **dentro da lista do cabeçalho** (a definição de esquerda e
  direita do mesmo boneco, e as listas já estão lidas), recusar com
  `BadPieces` a ambiguidade que sobrar, e controle novo mais caso sintético no
  `self_check()`

### CORR-LOOKS-021

- **Arquivo com problema:** `docs/tasks/looks/09-nomear-as-onze-pecas.md`, o
  item "Goleiro contra jogador de linha"; e a §1.5 do plano, que não registra
  a comparação
- **Sintoma:** o resumo põe o **tronco** entre as peças de tamanho diferente, e
  ele é igual nos dois bonecos — `84/71`, 2.384 bytes, extensão
  `108, 150, 76`, como a tabela da própria §1.5 diz; generaliza "mais **dois**
  bytes de vértice", que vale só do tronco (a coxa difere em **22** e a perna
  em **zero**); e conclui "mesma malha, uniforme diferente", que **não vale**
  para braço e antebraço, cuja contagem de vértice difere entre os dois bonecos
  (30/24 contra 40/34, 80/78 contra 88/86). Quem ler a frase ao escrever
  montagem carrega uma malha e desenha o goleiro com o braço do jogador de
  linha
- **Como foi detectado:** comparando byte a byte as nove seções
  correspondentes das duas listas, e conferindo contra a tabela da §1.5
- **Fix:** o item reescrito com os números separados e a leitura certa — o
  segundo modelo é o mesmo esqueleto com **duas peças remodeladas** —, a
  comparação registrada na §1.5, a ressalva na LOOKS-TASK-14, e a conta virando
  asserção no `pieces.py` para não poder envelhecer sozinha

### CORR-LOOKS-022

- **Arquivo com problema:** `tools/looks/texture.py`, o docstring do
  `plausible()`; e o parágrafo "Onde o conserto mora, e por quê" da
  LOOKS-TASK-10
- **Sintoma:** o número que decide a única questão de arquitetura da task
  aparece duas vezes, **atribuído a dois mecanismos diferentes** — no Log ao
  "aceitar qualquer palavra de banco", no código ao próprio `plausible()` —, e
  não reproduz por nenhuma das duas: a do Log dá **80 registros a mais em 5
  contêineres, nenhum estádio**; a do código dá **70.978 em 228**; só o teste de
  `kind` dá **197 em 54**. Nenhuma dá 2.151 em 40, nem neste disco nem na
  trilha do PES2 `(EsIt)`. De quebra: das cinco condições do `plausible()`, só
  o teste de `kind` suprime alguma coisa neste disco — retirar qualquer uma das
  outras, ou três juntas, muda **zero**
- **Como foi detectado:** rodando o `texture.tables()` commitado sobre os 245
  arquivos do disco japonês com sete variações do `plausible()`, e contra um
  `tables()` restrito ao `tag` fixo que o `bin_archive.py` aceita
- **Fix:** docstring corrigido com o que a medição dá (e a observação de que
  quatro condições não separam nada aqui), a conta alcançável por comando, e a
  decisão mantida com o argumento que sobrevive: o `bin_archive.py` é varredor
  de outro projeto, cujo gate não é medido aqui

### CORR-LOOKS-023

- **Arquivo com problema:** `tools/looks/texture.py`, a linha do "Botines" do
  `_check_image()`
- **Sintoma:** *"the only palette the foot section(s) sample ... and no other
  piece touches it"* é conferido só dentro do `EDT_MOD.BIN`. **Seis seções do
  `MODEL.BIN`** — 11, 12, 22, 23, 63 e 64 — amostram a mesma paleta, cinco
  primitivas cada; o próprio relatório diz `x142` duas linhas acima, e as
  seções 9 e 10 respondem por 112. As outras trinta não aparecem em conta
  nenhuma, e quem as encontrar depois vai suspeitar da leitura do CLUT
- **Como foi detectado:** contando, por seção e por arquivo, quem amostra
  (0, 484) nos dois arquivos de modelo — `112 + 30 = 142`
- **Fix:** a linha dizendo **entre as peças nomeadas** e quantas primitivas de
  fora compartilham a paleta; o relatório somando cada id de CLUT **por
  arquivo**; e as seis seções escritas na LOOKS-TASK-11 como candidatas a
  nomear pelo mesmo método das onze peças

### CORR-LOOKS-024

- **Arquivo com problema:** `docs/PLAN-LOOKS-PY.md`, §1.7 (tabela de rótulos e
  o parágrafo das páginas ausentes) e §1.8 (a conta dos rótulos)
- **Sintoma:** a §1.8 foi reescrita com o veredito, mas a §1.7 — que é o
  `fonte_de_verdade` da task 10 e a seção que o Contexto da 11 manda ler —
  continua traduzindo o rótulo do CARP como *"cabelos, corpos e chuteiras"* no
  offset 8, que é o erro derrubado; e continua dizendo **1.175** primitivas
  amostrando de páginas fora do arquivo, quando o medido é **1.039** — as 136
  da diferença são as seções 0 e 1 do `MODEL.BIN`, `u` 130..186 e `v` 130..187,
  **dentro** do registro em 10.248. Contar por base de página é o método que
  esta task substituiu por contar por texel. E a §1.8 diz que das **vinte**
  restantes "seis" carregam o rótulo do CARP e dezessete nenhum: 6 + 17 = 23, e
  o comando imprime **três**
- **Como foi detectado:** rodando `atlas.py --check-image` e comparando linha a
  linha com o texto das duas seções; e remedindo as 136 primitivas de
  `tpage=0x1a` no disco
- **Fix:** §1.7 sem a tradução "cabelos" e apontando para a §1.8; o número
  1.039 com a explicação das 136 e a regra que a Fase 4 vai usar (**o que
  resolve um registro é o texel, não a base da página**); e "seis" virando
  "três" na §1.8

### CORR-LOOKS-025

- **Arquivo com problema:** o Log da LOOKS-TASK-11, seção "E de onde vem o
  uniforme"; e o `--elsewhere` do `tools/looks/atlas.py`, que tem os dados e não
  os imprime
- **Sintoma:** *"mora nos 105 `TEX_*.BIN`, com **duas** paletas de 256 entradas
  em cada — casa e fora"*. Medido: **cinco** por arquivo, idêntico nos 105 —
  duas em (0, 486), duas em (0, 488) e uma em (256, 480), que a geometria não
  nomeia. O `x2` da saída é por id, não por arquivo. E "casa e fora" é leitura
  do par: ninguém trocou o uniforme na tela para ver qual das duas se move, que
  é o método que a task 09 estabeleceu. A LOOKS-TASK-14 vai escolher entre as
  duas, e escolher errado desenha perfeitamente nas cores erradas
- **Como foi detectado:** varrendo os 105 contêineres com o `texture.palettes()`
  commitado — `{5: 105}`, e `210 / 210 / 105` por id
- **Fix:** a frase com os cinco e a id não nomeada; "casa e fora" marcado como
  hipótese, com o gesto que a decide; e o `--elsewhere` imprimindo quantas
  paletas de 256 o contêiner tem ao todo, ao lado do `x2`

### CORR-LOOKS-026

- **Arquivo com problema:** `tools/looks/skin.py`, o bloco *"the sixteen
  columns of a skin record, accounted for"*
- **Sintoma:** a conta fecha em dezesseis medindo **o que os três campos
  alcançam**, e lê-se como o que cada coluna **é**. Medido: **948 primitivas em
  50 seções do `MODEL.BIN`** amostram a linha 480 coluna 1 — a coluna que a
  tabela chama de "cor de cabelo 1" — e nenhum dos três campos toca 932 delas;
  **nove das dezoito primitivas da própria cabeça** não são movidas por campo de
  cor nenhum, e continuam na paleta da pele branca depois de trocar a pele; e a
  **primitiva 4** anda com `H.COL` e **não** com `SKIN`, única exceção ao
  "linha × coluna". Quem escrever a tabela de montagem a partir da frase mapeia
  932 primitivas para uma cor de cabelo que elas não têm, e desenha
  perfeitamente
- **Como foi detectado:** rodando `--fields SKIN`, `--fields H.COL H.F.COL.` nos
  dois slots e tirando a união dos três conjuntos (nove de dezoito); e contando
  no disco quem amostra (16, 480)
- **Fix:** o bloco imprimindo quem amostra cada coluna, a linha de fecho dizendo
  o que é verdade, asserção sobre o que **não** se move, e as nove primitivas
  escritas na LOOKS-TASK-09 como o que falta nomear na cabeça

### CORR-LOOKS-027

- **Arquivo com problema:** `tools/looks/looks.py` (sem comando de corpus); o
  critério da LOOKS-TASK-13, que marca as duas testemunhas da tupla como feitas
- **Sintoma:** das duas, só a do `data/defaultlook.txt` virou asserção — o
  `--check` afirma as 95 nações e as cinco colunas. Os **50 nomes de JPG** não
  são lidos por comando nenhum: o `--report` recebe **tupla**, não pasta, e
  `grep` por `.jpg`, `parsed:` ou `refused:` em `tools/looks/` não acha nada. Os
  números (49 parseiam, 1 recusa, e o round-trip para o próprio nome) reproduzem,
  e a cobertura `4/9/4/6/2` foi **encaminhada à LOOKS-TASK-18 como medida**
- **Como foi detectado:** rodando `--report` com a pasta (recusa, porque espera
  tupla), grepando os módulos, e remedindo os 50 nomes com um script sobre o
  `looks.parse_tuple`/`format_tuple` commitados
- **Fix:** um `--corpus <pasta>` que conte parse, recusa e round-trip, imprima a
  cobertura por campo, **exija** a recusa e **pule com 77** sem a pasta — o
  contrato dos outros gates de dado externo, já que o Superpack não entra no
  git; mais o caso sintético no `self_check()`, que roda em qualquer clone


### CORR-LOOKS-028

- **Arquivo com problema:** `tools/looks/assembly.py`, o `draw_list`
- **Sintoma:** o `HAIR_MAP` guarda **as faixas** em que os quads de cada estilo
  caíram, e dez dos 29 estilos mapeados têm mais de uma; o `draw_list` escreve
  `bands[0]` em todos os quads nomeados e não registra que a escolha não é
  medida. Alcança um estilo hoje — o `B1`, faixas (0, 1) na seção 26, cujos
  quads (1 e 3) saem os dois em `band +0` —, porque os outros nove moram em
  seções sem quad nomeado. É o mesmo tipo de dúvida que o `head_of` **recusa**
  em vez de preencher
- **Como foi detectado:** listando as entradas de faixa múltipla do `HAIR_MAP`
  contra o `layout.HAIR_QUADS`, e rodando `assembly.py --tuple A-B1-A-A-A`
- **Fix:** medir a atribuição quad↔faixa pelo `oracle.py --writes`, que já lê
  `a0` e `a2` no mesmo acerto; enquanto não estiver medida, recusar ou aplicar
  com o comentário e um caso vermelho

### CORR-LOOKS-029

- **Arquivo com problema:** `tools/looks/layout.py` (`HEAD_RUNS`),
  `tools/looks/assembly.py` (`head_runs`) e o Log da LOOKS-TASK-14
- **Sintoma:** o docstring afirma "thirty-two sections each, **every body
  distinct**" e "each with its **own window** on that sheet", e fecha dizendo
  que o bloco é "**sixteen pairs** rather than 32 independent heads" — as duas
  primeiras contra a terceira. Medido no disco: 32 blobs de seção distintos,
  mas **12** arrays de vértices distintos no primeiro bloco e **24** no
  segundo, com 15 dos 16 pares partilhando o array; e **14** janelas distintas
  para as 32 seções, quatro delas (32, 33, 36, 37) sem janela nenhuma. O 32
  impresso vem de contar `bytes(data[offset:end])` e chamar isso de `body`
- **Como foi detectado:** script próprio sobre `roms/japanese-shift-jis.bin`
  comparando arrays de vértices e janelas de `v`, ao lado de
  `assembly.py --check-image`
- **Fix:** imprimir "byte-distinct section(s)" e acrescentar a contagem de
  malhas, com asserção de 12 e 24; reescrever as duas frases do `HEAD_RUNS` e a
  linha do Log com as janelas medidas

### CORR-LOOKS-030

- **Arquivo com problema:** `docs/PLAN-LOOKS-PY.md` §6(c),
  `tools/looks/layout.py` (`HEAD_RUNS`), `tools/looks/assembly.py`
  (`HAIR_MAP`) e o critério da LOOKS-TASK-14
- **Sintoma:** os três dizem **treze** seções e enumeram **doze** — falta a 54,
  que é do `E2`. A letra `E` não aparece em nenhuma das listas, só na frase que
  chama o `E1` de esquisitice por reescrever a seção do `D` e sugere que o `E`
  não foi nomeado; o mapa mostra que foi. E o "par de treses" (três estilos
  mudos, três seções pares nunca nomeadas) **só fecha com a 54 contada**:
  16 pares − 13 nomeadas = 3
- **Como foi detectado:** cruzando `assembly.HAIR_MAP` com `looks.HAIR_STYLES`
  e contando as seções distintas — 13, que é o que `HAIR_MAP_SECTIONS` afirma
- **Fix:** acrescentar o `E` às três listas, dizendo que é a única letra
  partida em duas seções (48 com o `D`, e a 54 sozinha), e reescrever a frase
  do `E1`

### CORR-LOOKS-031

- **Arquivo com problema:** `tools/looks/assembly.py`, o docstring de
  `AGREEMENT`
- **Sintoma:** ele justifica o piso de 0,80 dizendo que os renders de `HAIR` e
  `H.COL` mudam "within 0.005 of each other"; a corrida imprime 0,361 e 0,353,
  que distam **0,008** — e é 0,008 o que o plano e o Log da task escrevem. É a
  frase que impede o piso de parecer calibrado no resultado, então o número
  dela é o que se lê
- **Como foi detectado:** `assembly.py --corpus` sobre os 50 JPGs, duas vezes,
  com o mesmo resultado
- **Fix:** 0,008 no docstring, mais a razão aritmética do piso — com quatro
  linhas o rho só assume 1,0, 0,8, 0,6, de modo que 0,8 tolera exatamente uma
  inversão entre vizinhas

### CORR-LOOKS-032

- **Arquivo com problema:** `docs/tasks/looks/14-tabela-de-montagem.md`, a
  seção `### Gates medidos`
- **Sintoma:** ela transcreve "rule 1 swept 14 file(s), **8916** line(s)" e
  "**29 of 29** controls red", que é a árvore da primeira das quatro passagens;
  a árvore commitada dá **10.182** linhas e **32 de 32** — inclusive os três
  controles que a própria task acrescentou (29 → 31 → 32)
- **Como foi detectado:** `python tools/looks/selftest.py --quiet` sobre o
  commit `cef4921`, e `grep` dos cinco controles de montagem no `controls.py`
- **Fix:** trocar o bloco pela saída do fechamento; se a corrida da primeira
  passagem valer como registro, ela fica datada dentro da seção daquela
  passagem

### CORR-LOOKS-033

- **Arquivo com problema:** `docs/PLAN-LOOKS-PY.md`, o cabeçalho da §6(c)
- **Sintoma:** ele diz "**MEDIDA EM PARTE**, 2026-09-15 … que **continua
  pendente**", enquanto o corpo da mesma seção já traz a medição de 2026-09-16
  que fechou a task, o `progresso.md` a marca `✅ Concluído` e o frontmatter diz
  `status: concluído`. É a fonte de verdade da task contradizendo o progresso
  na primeira linha
- **Como foi detectado:** `grep -n "continua pendente" docs/PLAN-LOOKS-PY.md`
  contra a linha 50 do `progresso.md`
- **Fix:** reescrever o cabeçalho com o veredito de hoje — medida em
  2026-09-16, com o resíduo nomeado e encaminhado às tasks 15 e 17 —, deixando
  a data de 2026-09-15 no corpo, onde descreve a primeira metade


### CORR-LOOKS-034

- **Arquivo com problema:** `tools/looks/assembly.py`, a constante `HEAD` do
  `EFFECTS`
- **Sintoma:** as quatro linhas de cor são endereçadas a `(MODEL.BIN, 24)` e o
  `sections_of()` desenha a cabeça que o `head_of()` nomeia, que só é a 24 para
  os três estilos da família `A`. Nos outros 29 a chave não casa, o `combine()`
  recebe um plano vazio e `SKIN`, `H.COL`, `H.F.COL.` e `FACE` **não fazem
  nada** — quatro quadros byte a byte idênticos na cabeça 34, contra 47,13% e
  17,17% na 24. O `HAIR` escapa porque o `draw_list` o aplica à seção escolhida
- **Como foi detectado:** desenhando `A-I3-A-A-A` contra `B-I3`, `A-I3-C`,
  `A-I3-A-E` e `A-I3-A-A-E` e contando os pixels com o decodificador do
  `ui_check.py`; confirmado na tabela pelo `assembly.py --tuple`, onde a
  família `A` move a linha 480 para a 481 e a `I` não move nada. Nenhum gate
  via: o caso de cor do `scene --check-image` usa duas tuplas da família `A`
- **Fix:** endereçar a chave à cabeça desenhada; e, porque as treze cabeças não
  têm o mesmo número de primitivas, ou medir quais primitivas cada linha move
  em cada uma, ou marcar "cor não medida nesta cabeça" em vez de pintar por
  índice emprestado. Mais o caso cruzado no `--check-image` e um controle
  negativo

### CORR-LOOKS-035

- **Arquivo com problema:** `docs/PLAN-LOOKS-PY.md`, o item 3 da Definição de
  pronto
- **Sintoma:** ele manda rodar `--looks A-I3-A-F-A` e esperar "um boneco
  reconhecível"; a tupla é **recusada** desde que a LOOKS-TASK-14 mediu a linha
  `FACE` alcançando cinco valores, e o comando sai **2** sem escrever nada. A
  LOOKS-TASK-15 registrou a recusa no próprio critério e corrigiu a §5.6, mas
  esta linha — que é o critério de aceitação do projeto — ficou
- **Como foi detectado:** rodando o comando do item; e o `scene.py --corpus`
  mostra que não é caso isolado — 16 das 50 tuplas do corpus caem na mesma
  recusa (13 com `F`, 3 com `G`)
- **Fix:** trocar pela vizinha desenhável (`A-I3-A-E-A`, a que a 15 desenhou) e
  **acrescentar a recusa como segunda metade do item**: pronto é desenhar a
  tupla medida e recusar a não medida com saída 2

### CORR-LOOKS-036

- **Arquivo com problema:** `docs/tasks/looks/15-visualizador-opengl.md`, o
  último critério
- **Sintoma:** ele afirma "17 arquivos, 11.789 linhas" para a varredura da
  regra 1; a árvore que a task commitou tem **11.831**. Os arquivos batem; as
  linhas foram anotadas no meio da execução
- **Como foi detectado:** `selftest.py --quiet` num worktree destacado em
  `f2df3fc`, duas vezes, o mesmo número
- **Fix:** 11.831 no critério, com o commit nomeado ao lado — é o que a
  CORR-LOOKS-032 fez com o bloco da 14, e o que impede o número de envelhecer
  no commit seguinte

### CORR-LOOKS-037

- **Arquivo com problema:** `docs/PLAN-LOOKS-PY.md` §5.6 e o Log da
  `docs/tasks/looks/15-visualizador-opengl.md`
- **Sintoma:** os dois dizem "a cabeça vai de y -15 a 48 e a chuteira de -15 a
  18" numa frase que declara estar citando **as coordenadas do arquivo**; no
  arquivo elas são **-48..15** e **-18..15**. Os valores escritos são os do
  render, já virados pelo `scene.UP = -1`. O achado não muda; o eixo, sim
- **Como foi detectado:** lendo os vértices das seções 24, 9 e 10 pelo
  `section.scan`, e conferindo contra o "the head sits at y 17 and the boots at
  y -3, with UP = -1" do `scene --check-image`
- **Fix:** escrever os intervalos como o disco os guarda e dizer, na mesma
  frase, que o render os vira porque `UP` é `-1`


### CORR-LOOKS-039

- **Arquivo com problema:** `tools/looks/ui_check.py`, a constante `PAIRS`
- **Sintoma:** as três tuplas do gate — a referência e os dois pares — são da
  família `A`, que veste a seção 24, **a única cabeça a que as linhas de cor
  chegavam** antes da [`CORR-LOOKS-034`](/docs/tasks/looks/CORR-LOOKS-034.md).
  O `looks_ui` rodou verde durante todo o defeito; quem o achou foi a revisão,
  à mão. A CORR-034 pôs o caso cruzado no `scene.py --check-image` e não aqui
- **Como foi detectado:** replantando `where_head = HEAD` numa cópia da árvore
  e rodando os dois gates sobre ela — o do núcleo fica vermelho com duas
  queixas, e o da UI sai **0**
- **Fix:** um par de cabeça não-`A` no `PAIRS` (`A-I3-A-A-A` contra
  `B-I3-A-A-A`, medido em 14,54%), o que pede uma referência por par; mais um
  controle negativo que reponha a chave fixa e exija o vermelho

### CORR-LOOKS-040

- **Arquivo com problema:** `tools/looks/ui_check.py`, `PIECE = "head"` e o
  descarte da saída do `--smoke`
- **Sintoma:** as quatro corridas julgadas desenham só a cabeça — pela razão
  certa, que é não diluir as diferenças de cor — e **nada** julga as outras
  onze peças. A corrida de `--smoke` desenha a figura inteira e imprime as
  contagens; o gate lê dela apenas `window up` e o `-32000`. Apagando o corpo
  numa cópia (593 primitivas e 12 seções viram 18 e 1), o `looks_ui` passa
  **verde**
- **Como foi detectado:** plantando `sections_of` devolvendo `[]` e rodando os
  três gates: o `scene --check-image` fica vermelho ("no head or no boots, so
  up was not measured"), o `looks_selftest` fica vermelho, e o `looks_ui` sai 0
- **Fix:** afirmar sobre as contagens que o `--smoke` já imprime, e julgar um
  PNG da figura inteira com os mesmos juízes de quadro; mais o controle
  negativo que apaga o corpo

### CORR-LOOKS-041

- **Arquivo com problema:** `docs/tasks/looks/16-contratos-da-ui.md`, o bloco
  `### Gates medidos`
- **Sintoma:** ele transcreve "18 file(s), **12609** line(s)"; os dois commits
  da task medem **12.613**. As quatro linhas são as que a própria task
  acrescentou ao docstring do `ui_check.py` no fim, ao trocar o inexistente
  `make looks-venv` pela receita da §4.1. Terceira ocorrência do mesmo defeito
  no ciclo, e a segunda em duas tasks seguidas
- **Como foi detectado:** `selftest.py --quiet` em worktrees destacados em
  `9f1e3af` e `cb26d88` — o mesmo 12.613 nos dois
- **Fix:** 12.613 com o commit nomeado ao lado, na forma que a CORR-LOOKS-036
  deixou na task vizinha; e a regra na seção de gates do perfil, porque três
  ocorrências dizem que "reexecutar o gate ao escrever o Log" não está escrito
  onde quem executa lê

### CORR-LOOKS-042

- **Arquivo com problema:** `tools/looks/scene.py` (`part_for` soma a faixa ao
  `v` do disco) e `tools/looks/assembly.py`
- **Sintoma:** os quads 1 e 14 da seção 24 são desenhados com `v` 14 onde o
  jogo desenha 15 — uma linha de texel a menos, em toda faixa
- **Como foi detectado:** `confront.py --score`, na leitura da display list:
  `stored, one row off 2`, exatamente as duas primitivas do `HAIR_QUADS[24]`;
  o `layout.HAIR_QUAD_STORE` já documentava o `addiu v1, v0, 15`
- **Fix:** o `v` desses quads sai da regra do store, não do disco; controle que
  volte ao disco

### CORR-LOOKS-043

- **Arquivo com problema:** `tools/looks/assembly.py`, `sections_of`
- **Sintoma:** na figura 1 o `head_of` não é consultado; `A-I3-A-A-A` e
  `A-H1-A-A-A` desenham a seção 24, idênticos ao `A-A1-A-A-A`, sem recusa
- **Como foi detectado:** `confront.py --score`, slot 1 — os três renders
  intersectam em 1,000, e só o slot 2 imprime a recusa do `H1`
- **Fix:** recusar na figura 1 o que o mapa não mediu nela, ou medir o mapa no
  slot 1

### CORR-LOOKS-044

- **Arquivo com problema:** `tools/looks/assembly.py`, `Effect("FACE", ..., 5)`
- **Sintoma:** `reach` é definido como o alcance da tela, e a tela alcança
  **sete** valores nos dois slots; `F` e `G` são recusados com a frase "the
  screen was measured to reach 5", e dezesseis renders do corpus caem nela
- **Como foi detectado:** `confront.py --reach FACE`, por máscara de glifo com
  controle ocioso, e os quadros `reach-{1,2}-FACE-*.png` olhados
- **Fix:** separar o que a tela oferece do que a tabela sabe aplicar, e medir
  o que `F` e `G` escrevem

### CORR-LOOKS-045

- **Arquivo com problema:** `tools/looks/confront.py`, o `verdict`
- **Sintoma:** o gate só falha quando a tupla certa empata ou perde; toda
  liderança abaixo de `MARGIN` sai `ranked` e passa. A justificativa do
  `ranked` — o limite `I(g, a) − I(g, b) ≤ 1 − I(a, b)` — está certa e vale
  para o par de teto 0,039, onde 0,02 é metade do possível; o código não
  consulta o teto, e com dois renders a 0,5 de distância uma liderança de
  0,001 também passa, com a mensagem imprimindo o 0,5 que a desmente
- **Como foi detectado:** `confront.py --score` duas vezes sobre as capturas
  guardadas (os dois `ranked` reais são o par de teto 0,039, e estão certos);
  depois chamando o `verdict` commitado com teto 0,5 e liderança 0,001
- **Fix:** condicionar o `ranked` ao teto — a liderança tem de alcançar uma
  fração dele, ou o teto tem de estar abaixo de `2 × MARGIN` —, preservando os
  dois `ranked` reais; mais um controle que reponha `right > wrong` e um caso
  de teto largo no `self_check()`

### CORR-LOOKS-046

- **Arquivo com problema:** `tools/looks/confront.py`, o `run` e o `score`
- **Sintoma:** o `run` apaga o PNG velho e não o `.refused` velho; o `--score`
  decide pelo `.refused` primeiro. Uma tupla que passa de recusada a desenhada
  fica com os dois arquivos, sai da matriz sem ser julgada, e o confronto
  imprime `ok`
- **Como foi detectado:** leitura do código ao fechar o lote 042–045, onde o
  re-render do nosso lado precisou de script próprio que apagasse os dois
- **Fix:** apagar os dois; recusar o estado ambíguo no `--score`; o re-render
  do nosso lado como comando sem emulador. Vem antes da 047 e da 048, que são
  exatamente as que viram recusa em desenho

### CORR-LOOKS-047

- **Arquivo com problema:** `tools/looks/assembly.py` (`goalkeeper_head`) e a
  medição que ele substitui
- **Sintoma:** o `HAIR_MAP` foi medido só no slot 2; a figura 1 recusa todo
  estilo que não seja `A1`, e isso são **136 dos 179** registros de posição
  `GK` do disco
- **Como foi detectado:** contando os registros do `/SELECT.BIN` por posição e
  estilo, depois da CORR-LOOKS-043
- **Fix:** `--patched HAIR 1` no goleiro (o `--patched` ganha o slot), o mapa
  da figura 1 ao lado do da figura 0, e a recusa reduzida ao que a medição não
  alcançar

### CORR-LOOKS-048

- **Arquivo com problema:** `tools/looks/assembly.py`, o `Effect` do `FACE`
- **Sintoma:** a tela oferece 7 valores e a tabela aplica 5; `F` e `G` recusam
  como "não medido" — **28** jogadores do disco (1,9%) e **16** dos 50 renders
  do corpus
- **Como foi detectado:** contando os registros do `/SELECT.BIN` por
  `beard_style`, depois da CORR-LOOKS-044
- **Fix:** `--patched FACE` nos dois slots, e o que `F` e `G` escreverem entra
  na tabela — ou a recusa passa a dizer, medido, que não escrevem nada

### CORR-LOOKS-049

- **Arquivo com problema:** `tools/looks/assembly.py` (o empréstimo dos índices
  de cor) e `tools/looks/layout.py` (índices só da seção 24)
- **Sintoma:** em `D-I3-A-A-A`, `C-I3-A-C-A`, `B-I3-A-A-A`, `C-I3-A-A-A`,
  `C-K1-A-E-A` e `C-O1-A-A-A` a pele do nome pinta só a testa, o rosto fica na
  pele `A`, e a barba do nome não aparece
- **Como foi detectado:** `corpus.py --score` — a nota média do grupo "cabeça
  não-`A1`, pele não-`A`" é 0,411 contra 0,641 a 0,721 nos outros três; a tira
  `worst.png` olhada; `scene.py --tuple` imprime `colour borrowed 9` nessas
  cabeças e 0 na `A1`
- **Fix:** medir os índices de cor por cabeça, e recusar onde faltarem

### CORR-LOOKS-050

- **Arquivo com problema:** `tools/looks/corpus.py`, o julgamento por campo e a
  autopontuação por grupo
- **Sintoma:** com a CORR-LOOKS-049 presente — doze peles desenhadas só na
  testa —, a corrida diz `skin_colour 47/47` e `corpus: ok`. O campo é julgado
  pelo **rótulo do render de maior nota**, e nas seis piores esse render é a
  cabeça `A1` com a pele certa; o render da própria tupla tira 0,266 e não entra
  no julgamento. O erro sistemático só aparece na tabela **impressa** por grupo
  (`not A1 / not A`, média 0,411), que nada afirma — e é por ela que a própria
  CORR-049 manda verificar o conserto
- **Como foi detectado:** `corpus.py --run` e duas vezes `--score` sobre a árvore
  de `a2f122f`, saídas idênticas, com a CORR-049 pendente; e a tira
  `worst.png` olhada
- **Fix:** julgar a autopontuação por grupo contra o grupo de referência
  (`A1`/`A`), sem limiar à mão; nomear o resíduo enquanto a CORR-049 estiver
  aberta, com a condição de deixar de isentar quando o grupo se recuperar; e
  dizer na linha de campo o que ela mede

### CORR-LOOKS-051

- **Arquivo com problema:** `tools/looks/oracle.py` (`Oracle.__enter__`), ou o
  ambiente — não medido qual
- **Sintoma:** a primeira corrida do `looks_live` pelo `ctest` morreu no
  `pause` com `HTTP 400 ... missing or invalid MCP-Session-Id`, um pedido depois
  de o `initialize` ser aceito; as treze corridas seguintes passaram
- **Como foi detectado:** registrando o alvo na LOOKS-TASK-19 e rodando
  `ctest -R looks` com as duas variáveis apontadas
- **Fix:** separar as duas hipóteses por contagem (outro cliente MCP na porta,
  ou a sessão reiniciada na subida) antes de mexer; refazer a chamada em laço
  não é correção

### CORR-LOOKS-052

- **Arquivo com problema:** `tools/looks/cli.py` (`CHECK_IMAGE` e o self-check),
  o controle `cli-guard-read-not-first`, e a mesma regra na §4.4 do plano, na
  tabela de gates do perfil e no Log da LOOKS-TASK-19
- **Sintoma:** "o `modelfile` roda primeiro, senão o disco inglês passaria em
  silêncio" é regra com controle negativo, e o `cmd_check` roda os oito até o
  fim e junta os códigos no `combine()` — a ordem não muda o veredito. Com
  `pieces` primeiro e `modelfile` por último, o disco inglês sai `1 ok, 7
  failed -- FAILED`, igual à ordem commitada. O controle fica vermelho por
  asserção literal, não por deixar passar nada, e entra na contagem de guardas
  exercitadas
- **Como foi detectado:** lendo `cmd_check`/`combine` e reordenando a lista numa
  cópia da árvore, com os dois discos
- **Fix:** tirar a regra de ordem e trocar o controle por um que remova o
  `modelfile` da lista — o que de fato protege —, ou fazer o `check` parar no
  primeiro vermelho da guarda para a ordem passar a importar

### CORR-LOOKS-053

- **Arquivo com problema:** `docs/tasks/looks/19-alvos-de-ctest-e-cli.md`, o
  Contexto e o Objetivo
- **Sintoma:** o título diz **quatro** alvos e o Objetivo, duas linhas abaixo,
  **três**; o Contexto apresenta `if(UNIX AND Python3_FOUND)` como convenção
  para display/venv, que o terceiro critério da mesma task mede como errado
  neste ciclo. Os dois sem marca de "enunciado original", ao contrário das
  outras frases velhas do arquivo
- **Como foi detectado:** `grep` por "três alvos" e `UNIX AND Python3_FOUND`
  nos documentos do ciclo — o plano e o perfil já estão reconciliados, com data
- **Fix:** "quatro alvos" no Objetivo, e a convenção do Contexto com a exceção
  deste ciclo dita na mesma linha

### CORR-LOOKS-054

- **Arquivo com problema:** `tools/looks/screen.json`, `tools/looks/oracle.py`
- **Sintoma:** a tabela guarda `"title": "LOOKS SET"` nos dois slots, e o quadro
  da tela desenha `S SET` na âncora do mesmo objeto; a conferência
  decode-contra-glifo cobre as 34 strings das linhas e deixa título, placa e
  nome da camisa de fora, então `oracle.py --screen` dá `0 difference(s)` com a
  divergência presente
- **Como foi detectado:** recorte nativo de 512×240 do `work/looks-shots/vram-0.png`
  na faixa `y=0..70`, contra o `title` do `screen.json`
- **Fix:** título, placa e nome da camisa na mesma conferência das linhas; o
  `screen.json` guarda o que a tela desenha (`title`), com o que o objeto guarda
  (`title_object`) e o que a fonte pula (`title_skipped`) ao lado. **A razão foi
  medida e ocupa o lugar do resíduo:** a fonte do título tem glifo para nove dos
  71 caracteres varridos, e o que ela não tem não desenha nem anda com a caneta

### CORR-LOOKS-055

- **Arquivo com problema:** `tools/looks/screen.py`, `tools/looks/oracle.py`
- **Sintoma:** `screen.py --report` para na terceira das doze linhas com
  `UnicodeEncodeError: 'charmap' codec can't encode character '■'` e sai 1;
  só imprime com `PYTHONIOENCODING=utf-8`. O `oracle._walk_row` põe a mesma
  ajuda na mensagem do `OracleError`, então uma corrida de doze minutos que
  errasse a linha terminaria no erro do `print`, sem dizer qual linha errou
- **Como foi detectado:** varredura da CORR-LOOKS-054, ao conferir o `--report`
  depois de o título entrar nele
- **Fix:** garantir a saída antes de imprimir texto medido; o `■` fica na
  tabela, que é o que o jogo desenha

### CORR-LOOKS-056

- **Arquivo com problema:** `CLAUDE.md`
- **Sintoma:** a seção do sexto projeto diz "ciclo fechado em 2026-09-17" com a v2
  aberta e duas tasks dela concluídas; a tabela de comandos descreve o
  `app.py --looks` como o modo normal, quando o default virou a tela; e não
  menciona `screen.py`, o `screen.json` gerado, `oracle.py --screen`,
  `oracle.py --keys` nem `.\make.ps1 looks`, que é a forma de ver a tela
- **Como foi detectado:** `grep -c "screen.py\|screen.json\|make.ps1 looks\|--keys" CLAUDE.md`
  devolve 0, e o último commit do arquivo é o `4023c65`, da LOOKS-TASK-20
- **Fix:** a seção passa a dizer o ciclo aberto na v2, a tela e como abri-la, e
  os comandos novos; o perfil ganha a linha de que o `CLAUDE.md` tem seção
  deste ciclo e envelhece com ele

### CORR-LOOKS-057

- **Arquivo com problema:** `tools/looks/layout.py`
- **Sintoma:** o docstring do `PLAYER_NATION` diz que o byte é "the row's index
  minus one", e a mesma task mediu que os valores 1 a 54 guardam 0 a 53 e o
  código salta 41 daí em diante (`Iceland` 95, `Algeria` 105, fim em 119). Quem
  usa o endereço a partir do módulo dos endereços erra 25 das 79 nações, sem
  sintoma
- **Como foi detectado:** `looks.NATION_CODES` contra o docstring; a regra
  ingênua só sobrevive ali (`grep -rn "minus one" tools/looks/`), e o controle
  `looks-nation-code-is-the-index` existe para reprovar quem a escrever
- **Fix:** o docstring passa a dizer o salto e a apontar `looks.NATION_CODES`,
  com a data e o que dizia antes

### CORR-LOOKS-058

- **Arquivo com problema:** `tools/looks/layout.py`
- **Sintoma:** o docstring do `POSE_MATRIX` diz "18 and 17 of 40 stops, against
  2, 2 and 1", e o `oracle.py --pose` imprime `x18, x18, x2, x1, x1` — o plano e
  o Log da task dizem 18 e 18, como a ferramenta
- **Como foi detectado:** `oracle.py --pose` na árvore de `8a32160`, nos dois
  slots, contra a linha 1447 do `layout.py`
- **Fix:** o docstring diz a repartição que o comando imprime, ou diz que ela
  varia e nomeia a corrida de onde saiu

### CORR-LOOKS-059

- **Arquivo com problema:** `docs/PLAN-LOOKS-PY.md` §10.3 (j), a armadilha 44 do
  perfil e o Log da LOOKS-TASK-24
- **Sintoma:** os três dizem que o `derive_base()` "responde `0x8017EE60`" / que
  ele "erra por 96 bytes"; chamado sobre o `ANIME.BIN` ele levanta `WrongBase`,
  porque lê o `0x9000040A` do payload como ponteiro. O `0x8017EE60` só existe
  com a corrida cortada em 204 palavras, que é o que o `layout.ANIME_BASE` diz
  certo
- **Como foi detectado:** `layout.derive_base()` sobre o arquivo lido do disco
- **Fix:** separar as duas metades no plano, no perfil e na task, como o
  `ANIME_BASE` já as separa; a base plantada do controle continua explicada

### CORR-LOOKS-060

- **Arquivo com problema:** `docs/PLAN-LOOKS-PY.md` §10.3 (k), a armadilha 45 do
  perfil e a LOOKS-TASK-25 (critério e Log)
- **Sintoma:** os quatro dizem que, fora dos cinco pares, "todos os outros ficam
  abaixo de 2,3x"; a corrida imprime **2,5x** na `head` do slot 2, e a
  transcrição do próprio Log diz "os outros sete abaixo de 2,5x" três linhas
  adiante
- **Como foi detectado:** `oracle.py --poses` na árvore de `a2d580e`, os dois
  slots
- **Fix:** escrever o que a corrida imprime — primeiro par verdadeiro em 4,6x e
  maior dos outros em 2,5x —, que é a folga real e não envelhece
