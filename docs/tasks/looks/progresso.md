# Progresso — visualizador 3D da aparência do jogador

Rastreamento das tasks de [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md),
que é a fonte de verdade do projeto. Este arquivo registra **andamento**; o
plano registra **objetivo e critério**. Divergência entre os dois se resolve a
favor do plano.

**Pasta deste ciclo:** `docs/tasks/looks/`. Todos os caminhos deste arquivo e
das tasks ao lado dele saem daqui, e é o nome desta pasta que os comandos
recebem como argumento (`/executar looks`, `/revisar looks`,
`/corrigir looks`). Sem argumento, os comandos continuam lendo `docs/tasks/`
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

## Resumo

| ID | Tarefa | Fase | Dependências | Status | Concluída em | Revisado em |
| -- | ------ | ---- | ------------ | ------ | ------------ | ----------- |
| [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | Base legal e linhagem — `we3d` (MIT), Superpack e o fonte `en_we2000edit` | 0 | — | ✅ Concluído | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-02](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md) | Ambiente — o venv, os dois discos e seus papéis, e a armadilha do MSYS | 0 | 01 | ✅ Concluído | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-03](/docs/tasks/looks/03-fonte-de-disco-e-layout.md) | `iso_source.py` e `layout.py` — a fachada de disco e o monopólio de endereço | 1 | 02 | ✅ Concluído | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-04](/docs/tasks/looks/04-formato-de-secao.md) | `section.py` — primitiva de 24 B, vértice de 8 B e o separador de zeros | 1 | 03 | ✅ Concluído | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-05](/docs/tasks/looks/05-arquivos-de-modelo.md) | `modelfile.py` — as 106 seções do `MODEL.BIN` e as 20 do `EDT_MOD.BIN` | 1 | 04 | ✅ Concluído | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-06](/docs/tasks/looks/06-harness-controles-e-selftest.md) | `harness.py`, `controls.py` e `selftest.py` — o gate e os primeiros casos vermelhos | 1 | 05 | ✅ Concluído | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-07](/docs/tasks/looks/07-oraculo-e-rota-ate-a-tela.md) | `oracle.py` — o emulador por MCP e a rota até a tela `LOOKS SET` | 2 | 06 | ✅ Concluído | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-08](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) | Incógnita (a) — de onde vem o boneco: `EDT_MOD.BIN` ou os TMDs de `0x00168xxx` | 2 | 07 | ✅ Concluído | 2026-09-14 | 2026-09-14 |
| [LOOKS-TASK-09](/docs/tasks/looks/09-nomear-as-onze-pecas.md) | Incógnita (b) — nomear as onze peças pelo emulador, não pelo tamanho | 2 | 08 | ✅ Concluído | 2026-09-15 | 2026-09-15 |
| [LOOKS-TASK-10](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md) | A lista de CLUTs do `DAT2D.BIN` que o `bin_archive.py` não acha | 3 | 08 | ✅ Concluído | 2026-09-15 | 2026-09-15 |
| [LOOKS-TASK-11](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md) | A contradição 8 × 3.568 — qual imagem do `DAT2D.BIN` é o cabelo | 3 | 10 | ✅ Concluído | 2026-09-15 | 2026-09-15 |
| [LOOKS-TASK-12](/docs/tasks/looks/12-pele-paleta-ou-vertice.md) | Incógnita (d) — pele é troca de paleta ou de cor de vértice? | 3 | 11 | ✅ Concluído | 2026-09-15 | 2026-09-15 |
| [LOOKS-TASK-13](/docs/tasks/looks/13-campos-e-dominios-de-looks.md) | `looks.py` — os doze campos, seus domínios e os rótulos | 4 | 09 | ✅ Concluído | 2026-09-15 | 2026-09-15 |
| [LOOKS-TASK-14](/docs/tasks/looks/14-tabela-de-montagem.md) | `assembly.py` — campo de LOOKS → peça + paleta | 4 | 12, 13 | ✅ Concluído | 2026-09-16 | 2026-09-16 |
| [LOOKS-TASK-15](/docs/tasks/looks/15-visualizador-opengl.md) | `ui/viewer.py` e `ui/app.py` — `QOpenGLWidget`, câmera orbital e uma tupla na tela | 5 | 14 | ⬜ Pendente | — | — |
| [LOOKS-TASK-16](/docs/tasks/looks/16-contratos-da-ui.md) | `ui_check.py` — a UI julgada de fora, e o alvo `looks_ui` | 5 | 15 | ⬜ Pendente | — | — |
| [LOOKS-TASK-17](/docs/tasks/looks/17-confronto-com-o-emulador.md) | Confronto — nosso quadro contra o quadro do emulador, na mesma tupla | 6 | 16 | ⬜ Pendente | — | — |
| [LOOKS-TASK-18](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md) | Os 50 renders do Superpack como corpus independente | 6 | 17 | ⬜ Pendente | — | — |
| [LOOKS-TASK-19](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md) | `cli.py` e os três alvos de `ctest` | 7 | 18 | ⬜ Pendente | — | — |
| [LOOKS-TASK-20](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md) | Reconciliação do plano, `perfil-looks.md` e os entregáveis | 7 | 19 | ⬜ Pendente | — | — |

**Legenda:** ⬜ Pendente · 🔄 Em andamento · ✅ Concluído · ❌ Bloqueado · ⏭️ Pulado

**As duas colunas de data são datas de commit**, não datas de intenção.

- **"Concluída em"** — o commit que fechou a tarefa. Tarefa pendente leva `—`.
- **"Revisado em"** — o commit da revisão. Tarefa concluída e ainda não revisada
  leva `⬜ pendente`; tarefa que nem começou leva `—`.

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
| 7 — fechamento | 19 a 20 | os três alvos de `ctest` e a reconciliação do plano |

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

- [ ] `--looks A-I3-A-F-A` desenha aquela tupla.
- [ ] Nenhuma janela aparece para o usuário.
- [ ] Duas tuplas diferentes produzem imagens diferentes.

### Fase 6 — confronto

- [ ] Três tuplas confrontadas contra o emulador, com a métrica nomeada.
- [ ] Cada fonte de diferença atribuída.
- [ ] Os 50 JPGs medidos, e os piores casos olhados.

### Fase 7 — fechamento

- [ ] `ctest -R looks` = 1 passed, 2 skipped numa máquina limpa.
- [ ] Cada incógnita da §6 com veredito.
- [ ] `check_tasks.py` verde.

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
   errado. É o par de zeros que separa grupos.
3. **`MSYS_NO_PATHCONV=1`** ou o caminho de dentro do ISO vira caminho Windows,
   e o erro culpa a coisa errada — diz que o arquivo não é form1.
4. **`bin_archive.py` responde `0 clut(s)` sem reclamar.** Ler isso como "não
   tem paleta" é erro; a lista existe e o varredor não a acha.
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
│   ├── texture.py looks.py assembly.py oracle.py
│   ├── harness.py controls.py selftest.py check_image.py cli.py
│   ├── ui_check.py
│   └── ui/app.py ui/viewer.py
└── work/venv-looks/                  ← fora do git
```

---

## Notas de execução

*(preenchido conforme as tasks forem executadas)*
