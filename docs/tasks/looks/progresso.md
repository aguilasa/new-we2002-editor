---
cycle: looks
prefix: LOOKS
profile: /docs/prompts/perfil-looks.md
order: [LOOKS-TASK-01, LOOKS-TASK-02, LOOKS-TASK-03, LOOKS-TASK-04, LOOKS-TASK-05, LOOKS-TASK-06, LOOKS-TASK-07, LOOKS-TASK-08, LOOKS-TASK-09, LOOKS-TASK-10, LOOKS-TASK-11, LOOKS-TASK-12, LOOKS-TASK-13, LOOKS-TASK-14, LOOKS-TASK-15, LOOKS-TASK-16, LOOKS-TASK-17, LOOKS-TASK-18, LOOKS-TASK-19, LOOKS-TASK-20, LOOKS-TASK-21, LOOKS-TASK-22, LOOKS-TASK-23, LOOKS-TASK-24, LOOKS-TASK-25, LOOKS-TASK-26, LOOKS-TASK-27, LOOKS-TASK-28, LOOKS-TASK-29, LOOKS-TASK-30, LOOKS-TASK-31, LOOKS-TASK-36, LOOKS-TASK-37, LOOKS-TASK-38, LOOKS-TASK-39, LOOKS-TASK-40, LOOKS-TASK-32, LOOKS-TASK-33, LOOKS-TASK-34, LOOKS-TASK-35]
---
# Progresso — visualizador 3D da aparência do jogador

Rastreamento das tasks de [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md),
que é a fonte de verdade do projeto. Este arquivo registra **andamento**; o
plano registra **objetivo e critério**. Divergência entre os dois se resolve a
favor do plano.

**Pasta deste ciclo:** `docs/tasks/looks/`. Todos os caminhos deste arquivo e
das tasks ao lado dele saem daqui, e é o nome desta pasta que os comandos
recebem como argumento (`/rite:execute looks`, `/rite:review looks`,
`/rite:fix looks`). Sem argumento, os comandos continuam lendo `docs/tasks/`
raso — o ciclo de PES2.

**Perfil deste ciclo:** [`/docs/prompts/perfil-looks.md`](/docs/prompts/perfil-looks.md).

**Prefixo dos IDs:** `LOOKS-TASK-`. O pool de correções é `CORR-LOOKS-`,
declarado em
[`/docs/tasks/looks/correcoes-progresso.md`](/docs/tasks/looks/correcoes-progresso.md).

**Projeto separado do `newWe2002`, do `wte/`, do PES2 e do port do `.mcr`.**
Não compartilha build nem código: `tools/looks/` é Python 3, e a UI é PySide6
num venv próprio. O que compartilha é **ferramenta de leitura de disco** —
`tools/pes2/iso.py`, `lzss.py`, `bin_archive.py`, `mcp.py`, `fork.py` — e
**conhecimento de formato**: o codec de 12 bytes de `src/core/Player.cpp` e o
formato de seção da §2.2 do
[`/docs/ANALISE-REPOS-WE3D-DBMANAGER.md`](/docs/ANALISE-REPOS-WE3D-DBMANAGER.md).
A §0 do plano **proíbe** estender o `we2002_core`.

**Este ciclo nasce em 2026-09-14**, depois de uma sessão de investigação que
mediu o formato dos dois arquivos de modelo com o jogo rodando instrumentado.
O plano já nasce com a §1 medida; o que as tasks fazem é construir sobre ela.

**E reabre em 2026-09-17 para a v2**, a pedido do usuário, com a v1 fechada nas
tasks 01 a 20: a **tela `LOOKS SET`** do jogo — as doze linhas trocáveis, como
os save states dos slots 1 e 2 a mostram — com o boneco **montado**,
**vestido** e **andando** dentro dela, como uma gravação de tela do usuário
mostra. As tasks 21 a 40 são as Fases 8 a 11, e a fonte de verdade delas é a
§10 do plano.

## Resumo

<!-- rite:begin tasks -->
| ID | Title | Phase | Type | Depends on | Status | Done on | Reviewed on |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | Base legal e linhagem — `we3d` (MIT), Superpack e o fonte `en_we2000edit` | 0 | documentação | — | done | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-02](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md) | Ambiente — o venv, os dois discos e seus papéis, e a armadilha do MSYS | 0 | infraestrutura | LOOKS-TASK-01 | done | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-03](/docs/tasks/looks/03-fonte-de-disco-e-layout.md) | `iso_source.py` e `layout.py` — a fachada de disco e o monopólio de endereço | 1 | implementação | LOOKS-TASK-02 | done | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-04](/docs/tasks/looks/04-formato-de-secao.md) | `section.py` — primitiva de 24 B, vértice de 8 B e o separador de zeros | 1 | implementação | LOOKS-TASK-03 | done | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-05](/docs/tasks/looks/05-arquivos-de-modelo.md) | `modelfile.py` — as 106 seções do `MODEL.BIN` e as 20 do `EDT_MOD.BIN` | 1 | implementação | LOOKS-TASK-04 | done | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-06](/docs/tasks/looks/06-harness-controles-e-selftest.md) | `harness.py`, `controls.py` e `selftest.py` — o gate e os primeiros casos vermelhos | 1 | implementação | LOOKS-TASK-05 | done | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-07](/docs/tasks/looks/07-oraculo-e-rota-ate-a-tela.md) | `oracle.py` — o emulador por MCP e a rota até a tela `LOOKS SET` | 2 | implementação | LOOKS-TASK-06 | done | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-08](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) | Incógnita (a) — de onde vem o boneco: `EDT_MOD.BIN` ou os TMDs de `0x00168xxx` | 2 | engenharia-reversa | LOOKS-TASK-07 | done | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-09](/docs/tasks/looks/09-nomear-as-onze-pecas.md) | Incógnita (b) — nomear as onze peças pelo emulador, não pelo tamanho | 2 | engenharia-reversa | LOOKS-TASK-08 | done | 2026-09-15 | 2026-09-15 |
| [LOOKS-TASK-10](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md) | A lista de CLUTs do `DAT2D.BIN` que o `bin_archive.py` não acha | 3 | engenharia-reversa | LOOKS-TASK-08 | done | 2026-09-15 | 2026-09-15 |
| [LOOKS-TASK-11](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md) | A contradição 8 × 3.568 — qual imagem do `DAT2D.BIN` é o cabelo | 3 | engenharia-reversa | LOOKS-TASK-10 | done | 2026-09-15 | 2026-09-15 |
| [LOOKS-TASK-12](/docs/tasks/looks/12-pele-paleta-ou-vertice.md) | Incógnita (d) — pele é troca de paleta ou de cor de vértice? | 3 | engenharia-reversa | LOOKS-TASK-11 | done | 2026-09-15 | 2026-09-15 |
| [LOOKS-TASK-13](/docs/tasks/looks/13-campos-e-dominios-de-looks.md) | `looks.py` — os doze campos, seus domínios e os rótulos | 4 | implementação | LOOKS-TASK-09 | done | 2026-09-15 | 2026-09-15 |
| [LOOKS-TASK-14](/docs/tasks/looks/14-tabela-de-montagem.md) | `assembly.py` — campo de LOOKS → peça + paleta | 4 | engenharia-reversa | LOOKS-TASK-12, LOOKS-TASK-13 | done | 2026-09-16 | 2026-09-16 |
| [LOOKS-TASK-15](/docs/tasks/looks/15-visualizador-opengl.md) | `ui/viewer.py` e `ui/app.py` — `QOpenGLWidget`, câmera orbital e uma tupla na tela | 5 | implementação | LOOKS-TASK-14 | done | 2026-09-16 | 2026-09-16 |
| [LOOKS-TASK-16](/docs/tasks/looks/16-contratos-da-ui.md) | `ui_check.py` — a UI julgada de fora, e o alvo `looks_ui` | 5 | implementação | LOOKS-TASK-15 | done | 2026-09-16 | 2026-09-16 |
| [LOOKS-TASK-17](/docs/tasks/looks/17-confronto-com-o-emulador.md) | Confronto — nosso quadro contra o quadro do emulador, na mesma tupla | 6 | verificação | LOOKS-TASK-16 | done | 2026-09-16 | 2026-09-16 |
| [LOOKS-TASK-18](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md) | Os 50 renders do Superpack como corpus independente | 6 | verificação | LOOKS-TASK-17 | done | 2026-09-16 | 2026-09-16 |
| [LOOKS-TASK-19](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md) | `cli.py` e os quatro alvos de `ctest` | 7 | implementação | LOOKS-TASK-18 | done | 2026-09-17 | 2026-09-17 |
| [LOOKS-TASK-20](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md) | Reconciliação do plano, `perfil-looks.md` e os entregáveis | 7 | documentação | LOOKS-TASK-19 | done | 2026-09-17 | 2026-09-17 |
| [LOOKS-TASK-21](/docs/tasks/looks/21-a-tela-medida.md) | Incógnita (q) — a tela `LOOKS SET` medida no jogo: texto de cada valor, ajuda, cursor e valores iniciais | 8 | investigação | LOOKS-TASK-20 | done | 2026-09-17 | 2026-09-17 |
| [LOOKS-TASK-22](/docs/tasks/looks/22-a-tela-na-janela.md) | A tela `LOOKS SET` na janela — doze linhas trocáveis, e o boneco redesenhado a cada troca | 8 | implementação | LOOKS-TASK-21 | done | 2026-09-17 | 2026-09-17 |
| [LOOKS-TASK-23](/docs/tasks/looks/23-default-por-nacionalidade.md) | Incógnita (r) — `DEFAUL` e `NAT`: a nação escolhida e o default que ela aplica | 8 | implementação | LOOKS-TASK-22 | done | 2026-09-17 | 2026-09-17 |
| [LOOKS-TASK-24](/docs/tasks/looks/24-de-onde-vem-a-pose.md) | Incógnita (j) — de onde vem a pose: `ANIME.BIN`, código ou outra tabela | 9 | investigação | LOOKS-TASK-20 | done | 2026-09-17 | 2026-09-18 |
| [LOOKS-TASK-25](/docs/tasks/looks/25-a-pose-de-referencia.md) | A pose de referência — as matrizes de cada peça num quadro contado, e a hierarquia | 9 | investigação | LOOKS-TASK-24 | done | 2026-09-18 | 2026-09-18 |
| [LOOKS-TASK-26](/docs/tasks/looks/26-o-formato-do-anime-bin.md) | `anime.py` — o formato do `ANIME.BIN`, medido contra a pose capturada | 9 | implementação | LOOKS-TASK-25 | done | 2026-09-18 | 2026-09-18 |
| [LOOKS-TASK-27](/docs/tasks/looks/27-o-boneco-montado.md) | As peças no lugar — `scene.py` aplica a pose, e o painel da tela mostra o boneco montado | 9 | implementação | LOOKS-TASK-22, LOOKS-TASK-26 | done | 2026-09-18 | 2026-09-18 |
| [LOOKS-TASK-28](/docs/tasks/looks/28-a-camera-do-jogo.md) | A câmera do jogo — projeção medida, e a silhueta como testemunha de forma | 9 | implementação | LOOKS-TASK-27 | done | 2026-09-18 | 2026-09-18 |
| [LOOKS-TASK-29](/docs/tasks/looks/29-altura-e-corpo.md) | Incógnita (s) — `HEIG` e `BODY`: o que mudam no desenho, medido pela pose | 9 | investigação | LOOKS-TASK-22, LOOKS-TASK-28 | done | 2026-09-18 | 2026-09-19 |
| [LOOKS-TASK-30](/docs/tasks/looks/30-o-uniforme.md) | Incógnita (n) — o uniforme: qual `TEX_*.BIN`, na guarda, e as primitivas vestidas | 10 | implementação | LOOKS-TASK-20 | done | 2026-09-20 | 2026-09-20 |
| [LOOKS-TASK-31](/docs/tasks/looks/31-o-painel-e-o-cenario.md) | Incógnita (o) — o painel e o cenário da tela: do disco ou da GPU | 10 | implementação | LOOKS-TASK-22, LOOKS-TASK-28 | done | 2026-09-21 | 2026-09-21 |
| [LOOKS-TASK-36](/docs/tasks/looks/36-os-sprites-estaticos.md) | Os sprites estáticos da tela — placa, caixas, ícone, barra, título e setas, lidos do disco | 10 | implementação | LOOKS-TASK-31 | done | 2026-09-21 | 2026-09-21 |
| [LOOKS-TASK-37](/docs/tasks/looks/37-a-tabela-de-glifos.md) | A tabela de glifos — o texto da tela desenhado com a fonte do `EDT_2D.BIN` | 10 | implementação | LOOKS-TASK-31 | done | 2026-09-22 | 2026-09-22 |
| [LOOKS-TASK-38](/docs/tasks/looks/38-o-alinhamento-dos-valores.md) | O alinhamento dos valores — a caixa do objeto de texto no `screen.json`, e o valor à direita | 10 | implementação | LOOKS-TASK-37 | done | 2026-09-22 | 2026-09-22 |
| [LOOKS-TASK-39](/docs/tasks/looks/39-o-texto-da-ajuda.md) | O texto da ajuda — quem escreve a página (832,256) na VRAM, e de onde | 10 | investigação | LOOKS-TASK-37 | done | 2026-09-22 | 2026-09-23 |
| [LOOKS-TASK-40](/docs/tasks/looks/40-a-camera-do-close-up.md) | A câmera do close-up — o painel aproxima na cabeça quando a linha é de cabeça | 10 | implementação | LOOKS-TASK-28 | done | 2026-09-23 | pending |
| [LOOKS-TASK-32](/docs/tasks/looks/32-o-ciclo-da-caminhada.md) | Incógnita (p) — o ciclo da caminhada: quadros por passada, interpolação e balanço | 11 | investigação | LOOKS-TASK-26 | pending | — | — |
| [LOOKS-TASK-33](/docs/tasks/looks/33-a-janela-animada.md) | A janela animada — o boneco caminhando na tela `LOOKS SET`, no ritmo do jogo | 11 | implementação | LOOKS-TASK-28, LOOKS-TASK-32, LOOKS-TASK-40 | pending | — | — |
| [LOOKS-TASK-34](/docs/tasks/looks/34-o-goleiro-andando.md) | O goleiro — figura 1 montada e andando na tela, conferida no slot 1 | 11 | verificação | LOOKS-TASK-33 | pending | — | — |
| [LOOKS-TASK-35](/docs/tasks/looks/35-fechamento-da-v2.md) | Fechamento da v2 — gates, `make.ps1 looks` e reconciliação do plano | 11 | documentação | LOOKS-TASK-23, LOOKS-TASK-29, LOOKS-TASK-30, LOOKS-TASK-31, LOOKS-TASK-34, LOOKS-TASK-36, LOOKS-TASK-37, LOOKS-TASK-38, LOOKS-TASK-39, LOOKS-TASK-40 | pending | — | — |
<!-- rite:end -->

**A tabela acima é gerada** pelo `rite.py sync` a partir do frontmatter de cada task — não edite
dentro dela. **Status:** `pending` · `in-progress` · `done` · `blocked` · `skipped`.

**As duas colunas de data são datas de commit**, não datas de intenção.

**A ordem da tabela é a ordem de execução, não a ordem dos números.** Em
2026-09-21, a pedido do usuário, a LOOKS-TASK-31 fechou com a medição e a
mobília, e o que faltava dela virou as tasks 36 a 40, na fase 10 — com IDs
novos e as linhas logo depois da 31, porque renumerar arrastaria as tasks 32
a 35 e todo link para elas. Essa ordem mora no `order:` do frontmatter deste arquivo, que é o
que o `rite next` e a tabela seguem.

- **"Done on"** — a data do commit de trabalho, escrita pelo `rite close`. Tarefa pendente leva `—`.
- **"Reviewed on"** — `pending` enquanto a tarefa concluída espera revisão; a data, depois do
  `rite mark-reviewed`; `—` se a tarefa nem começou.

---

## Escopo e fases

O projeto entrega um visualizador Python + Qt do modelo 3D que o WE2002 desenha
na tela `LOOKS SET`, lendo geometria, textura e paleta **direto do disco**. Ele
se verifica contra o próprio jogo rodando instrumentado por MCP, e contra um
corpus de 50 renders de terceiro. Ver
[`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §0 e §5.

| Fase | Tasks | O que entrega |
| --- | --- | --- |
| 0 — abertura | 01 a 02 | linhagem registrada, venv, e a regra dos dois discos com guarda |
| 1 — leitor e formato | 03 a 06 | as duas varreduras fechando no EOF, com gate e controle negativo |
| 2 — o que o jogo desenha | 07 a 09 | a rota até a tela, a incógnita (a) e as onze peças nomeadas |
| 3 — textura | 10 a 12 | a lista de CLUTs, a contradição 8 × 3.568, e a incógnita (d) |
| 4 — montagem | 13 a 14 | os doze campos e a tabela `LOOKS → peça + paleta` |
| 5 — render | 15 a 16 | a janela `QOpenGLWidget` e o gate que a julga de fora |
| 6 — confronto | 17 a 18 | a diferença medida contra o emulador e contra os 50 JPGs |
| 7 — fechamento | 19 a 20 | os quatro alvos de `ctest` e a reconciliação do plano |
| 8 — a tela (v2) | 21 a 23 | a tela `LOOKS SET` medida no jogo, a janela que a reproduz com as linhas trocáveis, e o default por nacionalidade |
| 9 — montado (v2) | 24 a 29 | de onde vem a pose, a pose de referência, o `ANIME.BIN`, as peças no lugar, a câmera do jogo, e altura e corpo |
| 10 — vestido (v2) | 30, 31 e 36 a 40 | o uniforme dos `TEX_*.BIN`; o painel e o cenário da tela, medidos; os sprites, o texto, o alinhamento e a ajuda lidos do disco; e a câmera do close-up |
| 11 — andando (v2) | 32 a 35 | o ciclo medido, a janela animada, o goleiro e o fechamento |

**O que não pode ser pulado**, com a razão de cada ordem:

- **A 08 antes de tudo que é geometria ou textura.** Enquanto não se souber se o
  boneco vem do `EDT_MOD.BIN` ou dos quatro TMDs de `0x00168xxx`, caçar paleta
  ou escrever montagem é trabalhar sobre dado que pode não ser o desenhado.
- **A Fase 2 antes da 14.** Tabela de índice escrita contra peça não
  identificada produz mapeamento plausível e errado — é a armadilha das oito
  listas de nome de time do PES2 (§6.1 do
  [`/docs/PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md)), onde casar por índice
  gravava no time errado e a tela parecia certa.
- **A 05 antes da 06.** Controle negativo que não tem o que deixar vermelho é
  cerimônia.
- **A 12 antes da 14.** Sem saber se a cor é paleta ou vértice, metade da tabela
  de montagem é chute.
- **A 02 antes de qualquer leitura de textura.** É ela que planta a guarda que
  recusa ler paleta do disco errado — e esse erro é silencioso.
- **A 21 antes da 22.** Janela escrita antes de a tela ser medida inventa o
  texto de cada valor, e o gate dela confere a invenção contra ela mesma.
- **A 24 antes de tudo da Fase 9.** Um leitor de `ANIME.BIN` escrito sem saber
  que a pose sai dele lê perfeitamente e desenha outra coisa — é a 08 outra vez.
- **A 37 antes da 38 e da 39, e a 40 antes da 33.** O alinhamento depende da
  largura de cada glifo, e a ajuda provavelmente sai da mesma fonte; e a
  janela animada precisa saber qual câmera vale em cada linha.
- **A 25 antes da 26, a 28 antes de qualquer silhueta, a 32 antes da 33.** A
  pose capturada é o gabarito do leitor, a câmera do jogo é o que torna o
  desenho comparável, e o ritmo medido é o que impede uma caminhada inventada
  (§10.5 do plano).

---

## Grafo de dependências

```text
Fase 0   01 ──► 02
                 │
Fase 1           └──► 03 ──► 04 ──► 05 ──► 06
                                            │
Fase 2                                      └──► 07 ──► 08 ──┬──► 09 ──┐
                                                             │         │
Fase 3                                                       └──► 10 ──► 11 ──► 12
                                                                       │        │
Fase 4                                                    13 ◄─────────┘        │
                                                           └──────► 14 ◄────────┘
                                                                     │
Fase 5                                                    15 ◄───────┘
                                                           └──► 16
                                                                 │
Fase 6                                                    17 ◄───┘
                                                           └──► 18
                                                                 │
Fase 7                                                    19 ◄───┘
                                                           └──► 20
                                                                 │
Fase 8   (v2, a tela)                                     21 ◄───┤
                                                           └──► 22 ──► 23
                                                                 │
Fase 9   (v2, montado)                     24 ◄──────────────────┤
                                            └──► 25 ──► 26 ──► 27 ◄── 22
                                                              └──► 28 ──► 29 ◄── 22
                                                                    │
Fase 10  (v2, vestido)                     30 ◄── 20        31 ◄── 22, 28
                                                             ├──► 36
                                                             └──► 37 ──┬──► 38
                                                                       └──► 39
                                                            40 ◄── 28
                                                                    │
Fase 11  (v2, andando)                     32 ◄── 26               │
                                            └──────────► 33 ◄──────┘  (e 28)
                                                          └──► 34
                                           35 ◄── 23, 29, 30, 31, 34, 36 a 40
```

**Sequência mínima de execução:**

```text
1.  01, 02              abertura
2.  03 ► 04 ► 05 ► 06   o leitor, em cadeia
3.  07 ► 08             a rota e a incógnita de maior risco
4.  09 e 10 em paralelo — as duas só dependem da 08
5.  11 ► 12             textura, em cadeia
6.  13 pode andar junto com 10-12 — só depende da 09
7.  14 ► 15 ► 16 ► 17 ► 18 ► 19 ► 20
8.  21 ► 22 ► 23                    a tela LOOKS SET, sobre a v1 como está
9.  24 ► 25 ► 26 ► 27 ► 28 ► 29     o boneco montado
10. 30 pode andar junto — só depende da 20; 31 depois da 28
11. 36; 37 ► 38 ► 39; 40            sprites, texto, alinhamento, ajuda, close-up
12. 32 depois da 26; 33 ► 34; 35 fecha
```

**A 13 é a candidata natural a antecipação.** Ela depende só da 09, é barata —
transcrição conferida contra quatro implementações que já concordam — e o
`--looks` da UI e o parser de tupla do corpus dependem dela. Antecipá-la
enquanto a Fase 3 mede textura não custa nada e destrava duas tasks adiante.

---

## Checklist geral

### Fase 0 — abertura

- [x] `NOTICE.md` distingue os três materiais de terceiro e suas licenças.
- [x] `work/venv-looks/` com PySide6, fora do git.
- [x] A guarda que recusa ler textura do disco inglês existe e tem caso vermelho.

### Fase 1 — leitor e formato

- [x] `MODEL.BIN`: 106 seções, 2.461 vértices, 1.767 primitivas, EOF exato (a partir de 1816).
- [x] `EDT_MOD.BIN`: **20** seções, 1.218 vértices, 1.074 primitivas, EOF exato (a partir de 216) — as 11/690/611 são **uma das duas listas** ([CORR-LOOKS-010](/docs/tasks/looks/CORR-LOOKS-010.md)).
- [x] Nenhum endereço fora de `layout.py`.
- [x] `looks_selftest` roda sem imagem, sem venv e sem display.

### Fase 2 — o que o jogo desenha

- [x] `load_looks()` chega à tela sozinha, pelos dois save states que já existem — e prova pelo quadro **qual** deles carregou.
- [x] A incógnita (a) tem veredito com evidência: **o boneco vem dos dois arquivos de modelo**, e de TMD nenhum — e a §1.6, que era a contradição de maior risco do plano, era leitura errada da primitiva.
- [x] As onze peças têm nome, e ao lado como se soube — cinco argumentos, três implementados no `pieces.py` e dois conferidos contra o emulador.

### Fase 3 — textura

- [x] A lista de CLUTs do `DAT2D.BIN` é achada por marcador — **267 registros**, 262 de 16 entradas e 5 de 256, e o que a escondia era o campo 7 do registro: banco de 64 KiB, não tag constante.
- [x] A contradição 8 × 3.568 tem veredito: **o cabelo é o 3.568** — as primitivas que `HAIR` e `FACE` movem têm `u` 152..199, e numa página de 4 bits isso é a segunda metade. O tutorial do `zeta` acertou; o *"Pelos"* do CARP no offset 8 está errado.
- [x] A incógnita (d) diz o que o renderizador tem de implementar: **textura com CLUT e nenhuma cor de vértice** — um registro de 256 entradas é uma grade de dezesseis janelas de 16, e os três campos de cor são duas coordenadas dela (`SKIN` a linha, `H.COL` e `H.F.COL.` a coluna). A paleta em VRAM é a do arquivo e não se mexe; o que se mexe é o id.

### Fase 4 — montagem

- [x] Os doze campos com domínio conferido contra `src/core/Player.cpp`, mecanicamente: o `looks.py` lê as expressões do `Player::Decode()` e roda as duas implementações lado a lado. **Dez guardam alguma coisa** — `DEFAUL` e `NAT` são o default por nacionalidade, não campo —, e os registros do `/SELECT.BIN` são **1.449**, não 1.242.
- [x] Os 32 cabelos e as 4 peles resolvidos, ou o buraco nomeado. A linha `HAIR` **escolhe uma seção de cabeça** — a letra do rótulo é uma das treze seções pares do bloco 24..55 e o dígito é a faixa da folha 3.568 —, e o `SKIN` anda a linha do CLUT em quatro. O buraco que sobrou tem nome: três estilos que o mapa não alcança, e o `head_of` recusa em vez de devolver a cabeça da família A.

### Fase 5 — render

- [x] `--looks <tupla>` desenha aquela tupla — e a `A-I3-A-F-A` deste item é uma **recusa** medida: o `assembly` mediu a tela da barba chegando a cinco valores e recusa o `F`, com a mensagem dela e saída 2. Desenhadas e olhadas: `A-A1-A-A-A`, `A-I3-A-A-A`, `A-I3-A-E-A`, `A-A1-C-A-A` e `B-A1-A-A-A`.
- [x] Nenhuma janela apareceu para o usuário: a janela é posta em −32000,−32000 antes do `show()`, e o relatório de cada corrida imprime onde ela está.
- [x] Duas tuplas diferentes produzem imagens diferentes, medido pelo `app.py --compare`: 47,13% dos pixels entre `A-A1-A-A-A` e `B-A1-A-A-A`, 17,17% para a cor de cabelo `C` e 36,57% para o estilo `I3`. As três imagens foram olhadas, não só contadas.
- [x] O alvo `looks_ui` existe e **julga o PNG de fora**: o `ui_check.py` decodifica a imagem em `zlib` puro — não pelo `--compare` do código sob teste, cujo número ele apenas exige que bata — e reprova quadro em branco, tamanho errado, tupla que não chega ao desenho e visualizador que oscila entre corridas. Três controles plantados, três vermelhos. Numa máquina limpa, `ctest -R looks` dá **1 passed, 2 skipped**.

### Fase 6 — confronto

- [x] Três tuplas confrontadas contra o emulador, com a métrica nomeada — cinco pontuadas e uma recusa, nos dois slots, por interseção de histogramas de cor de 15 bits (`confront.py`); nenhuma tupla fora do primeiro lugar da própria linha.
- [x] Cada fonte de diferença atribuída — pose e câmera fora da métrica por construção, cor exata, sem filtro; o resto virou `CORR-LOOKS-042` a `044` e três incógnitas escritas na LOOKS-TASK-20.
- [x] Os 50 JPGs medidos, e os piores casos olhados — `corpus.py`: o `0.jpg` é quadro branco, 47 das 49 tuplas desenham; pele, cor de cabelo e cor de barba acertam em todos (47/47, 47/47, 26/26), forma não é testemunhável por cor (controle do emulador); os seis piores, olhados, deram a `CORR-LOOKS-049`.

### Fase 7 — fechamento

- [x] `ctest -R looks` = **1 passed, 3 skipped** numa máquina limpa — eram 2 skipped até a LOOKS-TASK-19 registrar o quarto alvo, `looks_live`; e 4 passed com as duas variáveis, o venv e o fork.
- [x] Cada incógnita da §6 com veredito — (a) a (d) respondidas; os resíduos da (c) e as cinco novas, (e) a (i), abertas com a razão e o que as destravaria.
- [x] `check_tasks.py` verde — `123 task(s), ok`, na árvore de `4023c65`.

### Fase 8 — a tela (v2)

- [x] O texto de cada valor, a ajuda, o cursor e os valores iniciais dos dois slots medidos no jogo — `tools/looks/screen.json`, escrito e remedido por `oracle.py --screen`.
- [x] A janela é a tela `LOOKS SET`: doze linhas trocáveis, o boneco redesenhado a cada troca, e a mesma sequência de teclas dando o mesmo texto que no jogo — `oracle.py --keys`, 0 diferença nos dois slots, com o controle do jogo contra si mesmo antes.
- [x] `NAT` e `DEFAUL` medidos no jogo: `DEFAUL` é o botão de confirmar e não aplica default nenhum; `NAT` guarda a nacionalidade fora dos doze bytes, com um código que não é a posição na linha — `oracle.py --default`.

### Fase 9 — montado (v2)

- [x] A fonte da pose medida: é o `ANIME.BIN`, na RAM byte a byte, com a entrada 5 do cabeçalho, a lista de quadros que dá a volta, os ângulos empacotados e as duas instruções que carregam o GTE — `oracle.py --pose`.
- [x] A pose de referência capturada num quadro contado, repetível, com a hierarquia medida — `oracle.py --pose <SLOT> <N>`: 12 cargas por passada nos dois slots, a matriz e a translação de cada peça lidas da struct que o jogo copia para o GTE, a captura repetida como controle antes de qualquer número, e a matriz medida **absoluta** (a câmera composta com a volta da peça). A hierarquia: cinco juntas se separam por 4,6x a 14,6x e nenhuma linha fora delas passa de 2,5x — o esqueleto do jogo não é rígido, e o leitor não compõe.
- [x] O `anime.py` reproduz as matrizes do jogo exatamente, e a varredura fecha no EOF — a partir do offset 816: **197 blocos, 3.952 quadros, terminando em 396.804 = EOF, 0 buraco**; e contra as capturas de pose dos dois slots, **96 de 96 julgadas (de 192 capturadas) peças trazem os ângulos do par que o jogo leu** e **90 das 96 matrizes saem exatas entrada por entrada**, sendo as 6 restantes misturas que o próprio jogo faz.
- [x] O painel mostra o boneco montado — nos dois slots, com as doze peças na ordem que o `scene.standing` afirma contra o disco. O que faltava não era o arquivo: o ponteiro de modelo na parada da carga nomeia a peça **anterior** (`oracle.DRAW_LAG`), e lido na hora a chuteira herdava a matriz do quadril. Medido pelo tornozelo — dispersão 5,0 no atraso certo contra 158,8 no outro, com a canela errada de controle em 357,3 —, pela simetria dos pares e pela hierarquia da captura viva. **A silhueta contra a do emulador é a task 28.** E a silhueta concorda com a do emulador com a câmera do jogo ([LOOKS-TASK-28](/docs/tasks/looks/28-a-camera-do-jogo.md)): `H` = 1376 lido do GTE, o painel desenhando com ela, seis comparações de pose a 7–18% da tinta, e três estilos de cabelo no close-up, cada foto escolhendo o próprio — 6 de 6.
- [x] `HEIG` e `BODY` mudam o desenho como mudam no jogo — **pela câmera**, uma escala por eixo aplicada às colunas da rotação da figura, com a regra lida das instruções do `/SELECT8.BIN` ([LOOKS-TASK-29](/docs/tasks/looks/29-altura-e-corpo.md)): a altura escala os três eixos, o corpo só largura e profundidade. `oracle.py --stature` nos dois slots: os 56 valores de `HEIG` e os 8 de `BODY`, 0 fora da regra, e 12 de 12 peças exatas em cada captura de pose; a janela reaponta a câmera quando uma das duas linhas muda.

### Fase 10 — vestido (v2)

- [x] O uniforme lido pela guarda e desenhado; zero primitiva sem textura, ou o resto nomeado — os 105 `TEX_*.BIN` na guarda com digest medido (form 1 e idênticos nos dois discos), e **qual deles a tela veste medido na VRAM** ([LOOKS-TASK-30](/docs/tasks/looks/30-o-uniforme.md)): é o `TEX_A4` nos dois states, que reproduz exatas uma página e duas paletas onde nenhum outro contêiner reproduz nenhuma. Com ele, 593 de 593 primitivas texturizadas na figura 0 e 629 de 629 na figura 1; o `looks_ui` passou a exigir isso e o `confront.py --kit-control` mede que o uniforme de outro time fica 0,063 a 0,218 mais longe da foto do jogo.
- [x] O painel e o cenário da tela medidos, e a mobília reproduzida ([LOOKS-TASK-31](/docs/tasks/looks/31-o-painel-e-o-cenario.md)): cada elemento lido da lista que o quadro entrega ao GPU — 43 pacotes de mobília, desenhados como o GPU desenha, e 142 sprites, com os texels de cada grupo do `EDT_2D.BIN` ou do `DAT2D.BIN` iguais à VRAM, e a ajuda escrita pelo jogo em tempo de execução. `confront.py --outside` 0 problema em 7 regiões nos dois slots.
- [x] Os sprites estáticos e as setas desenhados do disco ([LOOKS-TASK-36](/docs/tasks/looks/36-os-sprites-estaticos.md)): título, ícone, caixas da camisa, barra e placa montados do `EDT_2D.BIN` e do `DAT2D.BIN` pela guarda, com a CLUT da placa vindo da **posição** do jogador — (192,499) no goleiro, (208,499) no de linha. `oracle.py --scenery --write` amostrou **359 pixels de 13 sprites** — a barra, transparente em todo o seu corte, não dá amostra —, cada um da cor que o quadro do jogo mostra ali, e o `looks_ui` conferiu **718 amostras nos dois slots, todas dentro de 8**, com 14 de 14 controles vermelhos. As setas saem de `uv` (128,240) e (128,248), 22 de 64 texels opacos e a ◀ sendo a ▶ espelhada, com o x de cada uma fixo por linha e gravado no `screen.json` pelo walk; `oracle.py --keys` 0 diferença após 19 teclas nos dois slots, e `confront.py --outside` 0 problema em 11 regiões.
- [x] O texto desenhado com os glifos do `EDT_2D.BIN` ([LOOKS-TASK-37](/docs/tasks/looks/37-a-tabela-de-glifos.md)): a regra código → (`u`, `v`, largura) não estava na overlay que o ciclo lia — a rotina (0xfb04) e a tabela de **95 pares** (0x11008) moram no `/SELECTC.BIN`, achado por conteúdo, e são iguais byte a byte no japonês, no inglês e na RAM do jogo, embora o arquivo difira em 5.201 bytes de texto traduzido; a regra é lida do **japonês** pela guarda e recusada se o sha256 da rotina mudar. `oracle.py --glyphs`: 134 glifos e 13 espaços por quadro, **121 de 121 sprites de fonte iguais à regra** em `uv`, tamanho e CLUT, 0 sem dono, nos dois slots, com a tabela lida um par fora casando 0 deles; e `confront.py --outside` compara os rótulos **pixel a pixel dentro de `OUTSIDE_SLACK` (16) por canal — 0 de 16.416 diferentes**, contra 2.875 se o quadro do jogo anda um pixel.
- [x] Os valores alinhados como no jogo ([LOOKS-TASK-38](/docs/tasks/looks/38-o-alinhamento-dos-valores.md)): o byte 13 do objeto de texto é o modo — **0** começa na esquerda da caixa, **2** encosta na borda direita, **3** centra arredondando para baixo —, lido das chamadas de desenho, com o `\t` pondo a caneta na coluna e o código de controle 13 trocando a cor em vigor (tabela de saltos em 0x800FC048 do `/SELECTC.BIN`), que é por que o `O.K.` do `DEFAUL` sai cinza. A caixa é por **valor**, não por linha — o objeto do `NAT` anda de x −80 com `Unknown` para −104 com uma nação —, e o walk a grava em `rows[*].layouts`. `confront.py --outside` passou a comparar as duas colunas **pixel a pixel dentro de `OUTSIDE_SLACK` (16) por canal**: **0 de 16.416** nos rótulos e **0 de 23.472** nos valores, nos dois slots, contra 2.875 e 3.075 se o quadro do jogo anda um pixel; `oracle.py --keys` 0 diferença em cinco sequências (19, 10, 47, 32 e 2 teclas), e o alinhamento pela esquerda plantado deixa o `--keys` vermelho linha por linha.
- [ ] A origem do texto da ajuda medida, e desenhada se for do disco ([LOOKS-TASK-39](/docs/tasks/looks/39-o-texto-da-ajuda.md)).
- [ ] A câmera do close-up por linha de cabeça ([LOOKS-TASK-40](/docs/tasks/looks/40-a-camera-do-close-up.md)).

### Fase 11 — andando (v2)

- [ ] O período do ciclo medido em quadros do jogo, e qualquer quadro do ciclo reproduzido.
- [ ] O painel anima no ritmo do jogo, com a silhueta conferida em vários quadros, nos dois slots.
- [ ] `.\make.ps1 looks` abre a tela com o boneco montado, vestido e andando.

---

## Decisões de design

Vindas de [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) e da sessão de
investigação de 2026-09-13 e 2026-09-14.

| Decisão | Escolha | Razão |
| --- | --- | --- |
| Escopo da v1 | **só visualizador** | não grava nada; separa o risco de ler do risco de escrever |
| Imagem dos bytes | `roms/japanese-shift-jis.bin` | original, e é onde o `DAT2D.BIN` é o de fábrica |
| Imagem de dirigir | o `.cue` **inglês** | menus legíveis, e geometria byte a byte idêntica (§1.3) |
| Render | `QOpenGLWidget` | Qt3D é grande e meio abandonado; sem `numpy`, rasterizar em Python é inviável |
| Onde mora | `tools/looks/`, Python | não estende o `we2002_core`, como manda a §0 |
| Leitura de disco | reusa `tools/pes2/` | o `iso.py` já lê esta imagem, inclusive no Windows |

---

## Armadilhas medidas que valem para todas as fases

Cada uma custou tempo real nesta máquina. A lista completa é a §8 do plano.

1. **Dois discos, e cada um serve para uma coisa.** O inglês tem menus legíveis
   e geometria idêntica; o `DAT2D.BIN` dele **difere**. Ler paleta no inglês
   entrega gráfico diferente **sem erro nenhum**.
2. **A varredura contígua morre na seção 55 do `MODEL.BIN`** e parece formato
   errado. É a corrida de palavras zero que separa grupos — 8 bytes lá, 12 nas
   duas primeiras folgas do `EDT_MOD.BIN`; dizia "o par de zeros" até
   2026-09-17.
3. **`MSYS_NO_PATHCONV=1`** ou o caminho de dentro do ISO vira caminho Windows,
   e o erro culpa a coisa errada — diz que o arquivo não é form1.
4. **`bin_archive.py` responde `0 clut(s)` sem reclamar.** Ler isso como "não
   tem paleta" é erro; a lista existe, e o que a esconde é o campo 7 do
   registro, que é banco de 64 KiB e não tag (§1.7).
5. **Círculo confirma e precisa de 8 frames.** Com 3 a tela fica igual, o que
   parece botão errado.
6. **Uma tecla de cada vez.** Confirmação em laço fecha a caixa seguinte junto.

---

## Pendências externas

- **`numpy` não está instalado**, e instalar é decisão do dono da máquina. O
  plano contorna indo para a GPU; se a decisão mudar, o `savestate.py` do ciclo
  de PES2 também se beneficia.
- **O Superpack v6 é pasta do usuário**, fora do git. Corpus e tutoriais
  dependem dela estar no disco; sem ela, a LOOKS-TASK-18 pula.

---

## Estrutura de pastas (estado final esperado)

```text
new-we2002-editor/
├── docs/
│   ├── PLAN-LOOKS-PY.md              ← fonte de verdade
│   └── tasks/looks/
│       ├── 01-...md ... 20-...md
│       ├── progresso.md              ← este arquivo
│       └── correcoes-progresso.md
├── tools/looks/
│   ├── iso_source.py layout.py section.py modelfile.py
│   ├── texture.py atlas.py skin.py pieces.py looks.py assembly.py scene.py
│   ├── screen.py anime.py                ← v2
│   ├── screen.json                       ← v2, gerado por oracle.py --screen --write
│   ├── oracle.py confront.py corpus.py
│   ├── harness.py controls.py selftest.py superpack_count.py cli.py
│   ├── ui_check.py
│   └── ui/app.py ui/viewer.py ui/looks_set.py   ← looks_set: v2
└── work/venv-looks/                  ← fora do git
```

---

## Notas de execução

*(preenchido conforme as tasks forem executadas)*
