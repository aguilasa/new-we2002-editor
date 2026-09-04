# Perfil de ciclo — Pro Evolution Soccer 2 (PSX)

**Este arquivo é o perfil do ciclo PES2**, nomeado pelo campo `perfil:` do
[`docs/tasks/progresso.md`](/docs/tasks/progresso.md) e carregado pelos prompts
de `docs/prompts/`. Os prompts têm o **rito**; o que é deste ciclo mora aqui.

Fonte: [`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md). Onde este perfil e o plano
divergirem, **o plano ganha** — aqui só mora o resumo operacional, e o
`fonte_de_verdade` de cada task aponta para a seção que a mede.

---

## Contexto essencial — decisões já confirmadas

- **Não há oráculo, e isso define tudo.** No `newWe2002` e no `wte/` a evidência
  era uma faixa de bytes contra um binário que sabia a resposta. Aqui o oráculo
  é **o jogo rodando**, e a evidência é uma captura de tela mais o offset que a
  produziu. (§4.1)
- **O quadro não entra no git.** Jogo comercial, mesma regra de `roms/`. O que
  entra é o comando que produz o quadro e o número medido — como o
  `boot_check.sh` já faz com desvio-padrão e contagem de pixels.
- **Texto antes de número.** Nome é verificável a olho numa tela; atributo não.
  A ordem das fases sai disso. (§4.3)
- **O mapa é o fonte.** `pes2_map.json` é escrito à mão (ou por ferramenta de
  descoberta) e revisado; headers, tabelas e código de leitura/gravação saem
  dele por gerador, com `--check` no `ctest`. Editar o gerado falha em teste.
  Nunca o contrário. (§4.4)
- **Não estender o `we2002_core` para PES2.** Nada em `src/` sabe o que é PES2,
  e `tools/pes2/` é Python 3 e shell puros. O que se empresta é conhecimento de
  formato — as duas engines são a mesma, e o `KanjiToAscii` do WE2002 decodifica
  o título de save do PES2 sem uma linha de adaptação. (§6.9)
- **Ancorar por marcador, nunca por offset constante.** O banco é o mesmo nas
  duas releases europeias; o que muda é onde cada tabela cai dentro do overlay.
  (§1.13, §6.6)

---

## Armadilhas medidas neste ciclo

As de GUI e de cópia valem para o repositório inteiro e estão no
[`CLAUDE.md`](../../CLAUDE.md). Estas são do formato e do método.

1. **Uma cópia gravada é pior que nenhuma — e nenhuma cópia é cópia.** PES2
   grava in-place como o WE2002, e a release inteira são 571 MiB em oito
   trilhas. Copie tudo antes de apontar qualquer coisa que escreva. (§6.1)
2. **"Cópia" de tabela não quer dizer mesma lista.** As oito cópias de nome de
   time têm 106, 99, 95, 94, 123, 32, 99 e 99 entradas, e o índice 34 de uma é
   outro time no índice 34 da outra. Casar por índice grava no time errado, e o
   resultado parece plausível em tela. (§6.1)
3. **O conjunto de cópias se varre, não se declara.** Eram cinco no papel até
   2026-09-01; gravar as cinco deixava o nome velho vivo em três outros
   lugares. O `poke.py` varre todo arquivo `form1` atrás do nome antigo depois
   de planejar, e recusa se sobrar registro que nenhuma tabela conhece. (§6.1)
4. **A ordem de armazenamento é propriedade da tabela.** `SELECTC.BIN` guarda
   elenco de trás para frente; o executável de boot, de frente para trás. Quem
   assume uma inverte 23 jogadores por time na metade das tabelas, sem sintoma
   visível. (§3.3)
5. **`SELECTC.BIN` é pool deduplicado, o executável é ordenado por vaga.** Os
   dois guardam os mesmos 1.399 nomes; o executável repete 50 deles, porque
   jogador em dois elencos ocupa duas vagas. Ler o pool como lista de elenco
   desalinha tudo depois do primeiro nome repetido. (§1.5)
6. **Registro de tamanho variável não aceita nome maior.** (§6.2)
7. **A fronteira de setor continua mordendo.** Setor de 2352 B com 2048 de
   dados; offset que atravessa cabeçalho é a primeira suspeita de round-trip
   quebrado. (§6.3)
8. **Multi-track: o offset é dentro do `(Track 1).bin`.** (§6.4)
9. **O diretório ISO nomeia arquivo que não está no Track 1.** (§6.5)
10. **Não recalcular EDC/ECC, e não "consertar".** (§6.7)
11. **Os nomes licenciados não estão lá** — o disco não tem o clube real.
    (§1.8, §6.8)
12. **Trinta e seis armadilhas ao dirigir o DuckStation**, todas medidas
    (§6.11) — eram treze quando este perfil foi escrito. A última é curta e
    cara: **`press_button` sem `duration_frames` deixa o botão preso**, e um
    pad preso é indistinguível de um jogo que não avança — seis corridas
    perdidas nisso em 2026-09-04. A anterior é a que mais custa: **o fork cai
    sozinho em execução livre e não escreve nada** — quatro mortes em seis corridas, entre 15 s e 90 s, não
    determinístico, e o `mcp.py` passou a distinguir "nunca subiu" de "caiu
    agora" porque a mensagem única custou três leituras erradas numa revisão
    só. As sete anteriores são de 2026-09-03 e são sobre dirigir por **MCP**,
    que desde essa data é como as rotas dirigem: o binário do fork **não acha as próprias
    bibliotecas** fora da árvore de build (`LD_LIBRARY_PATH` *e*
    `QT_PLUGIN_PATH`), o diálogo que ele abre é o **`Automatic Updater`** e
    `Escape` não o fecha, a **porta 2346 abre antes** de ele ser dispensado,
    o filtro de `kill_leftovers` era **sensível a maiúsculas** e descartava
    o fork logo depois de achá-lo, **imobilidade exata só serve na tela
    realmente parada** (quatro das nossas piscam ou animam), **"não preto"
    não é "chegou"** — a rota do Modo Editar devolveu `mean=0.000000`
    declarando sucesso —, e **`frame_step` custa 57 ms**, três vezes o tempo
    real: quadro para precisão, relógio para distância.

---

## As fontes de verdade binárias

| Fonte | Papel | Pode escrever? |
| --- | --- | --- |
| `roms/Pro Evolution Soccer 2 (Europe) (EsIt)/` | amostra de trabalho A, dump multi-track | **não** — sempre cópia |
| `roms/Pro Evolution Soccer 2 (Europe) (EnFrDe)/` | amostra de trabalho B, o confronto entre releases | **não** — sempre cópia |
| `roms/golden-european-deluxe.bin`, `roms/japanese-shift-jis.bin` | as duas imagens de **WE2002**; desde a Fase 7 elas são amostra deste ciclo também, porque o formato de contêiner é o mesmo (§1.14) | **não** — leitura pura aqui |
| o memory card do usuário | save real, alinha elenco e fecha fronteira | **não** por ferramenta nossa. O emulador usa esse mesmo cartão desde que a isolação foi encerrada; digest conferido em 2026-09-02 e inalterado |
| `src/core/` (`we2002_core`) | empresta **conhecimento de formato**, não código | **não** — §6.9 |

**Não existe oráculo comportamental.** O que mais se aproxima é o jogo sob
DuckStation, e o que ele responde é *"esta gravação apareceu na tela certa?"* —
não *"que bytes o editor de referência gravaria?"*, porque não há editor de
referência. (§4.1)

---

## O que é gerado

| Saída | Gerador |
| --- | --- |
| headers, tabelas e código de leitura/gravação | a partir de `pes2_map.json` (Fase 5) |

Até a Fase 5 fechar, **não há árvore gerada** — `tools/pes2/` são ferramentas de
medição, escritas à mão. A regra "a correção entra no gerador" passa a valer
quando o gerador existir; até lá o alvo é a ferramenta que mediu errado.

---

## Estrutura

```text
new-we2002-editor/
  docs/
    PLAN-PES2-PSX.md       # fonte das tasks deste ciclo
    PES2-NOMES.md          # apendice de nomes ficticios
    PES2-AJUSTES.md        # registro historico do backlog anterior ao pool
  tools/pes2/              # as ferramentas -- Python 3 e shell puros
  roms/                    # as duas releases (gitignored, ~571 MiB cada)
```

---

## Gates deste ciclo

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor

python3 tools/pes2/iso.py roundtrip "<track1.bin>"      # a guarda: 244 arquivos, imagem identica
python3 tools/pes2/iso.py negative  "<track1.bin>" --tmpdir <dir>   # a prova de que a guarda fica vermelha
python3 tools/pes2/tables.py        "<track1.bin>" --check
python3 tools/pes2/diff_releases.py "<a>" "<b>" --check
python3 tools/pes2/player_map.py    "<track1.bin>" --check
python3 tools/pes2/poke.py          "<track1.bin>" --self-check --tmpdir <dir>
python3 tools/pes2/lzss.py          "<a>" "<b>" "<c>" "<d>" --check   # os quatro discos
python3 tools/pes2/lzss.py          "<track1.bin>" --roundtrip        # ~70 s por disco
python3 tools/pes2/bin_archive.py check "<track1.bin>"               # o indice de imagem e CLUT
python3 tools/pes2/lang_map.py      "<track1.bin>" --check            # os conjuntos de copia
python3 tools/pes2/lang_map.py      "<track1.bin>" --self-check --tmpdir <dir>
python3 tools/pes2/tname.py         swap "<track1.bin>" --tmpdir <dir>   # grava e desfaz
python3 tools/pes2/asset_write.py   check "<track1.bin>" --tmpdir <dir>  # o caminho de gravacao
PES2_IMAGE=<copia.cue> tools/pes2/asset_screen.sh                        # quadros do boot
python3 tools/pes2/faq_check.py --image "<track1.bin>"

python3 tools/pes2/fork.py launch "<copia.cue>"   # sobe o fork com MCP; `kill` encerra os tres binarios
python3 tools/pes2/fork.py recipe                # os dois caminhos ate o fork: baixar ou compilar
python3 tools/pes2/mcp.py --self-check           # o cliente MCP, sem emulador
python3 tools/pes2/mcp.py --list                 # as 95 ferramentas, contra o servidor vivo
python3 tools/pes2/fork.py --self-check          # caminhos, lista de kill, recusas
python3 tools/pes2/mcp_drive.py --self-check     # rotas, limiares, assinaturas
python3 tools/pes2/who_writes.py --self-check    # fluxo A: enderecos, stores, as duas esperas
python3 tools/pes2/who_writes.py 0x8007151B --nudge Cross   # quem escreve; depois de --screen team-select --keep-alive
python3 tools/pes2/mcp_drive.py "<copia.cue>" --screen edit --out-dir <dir>
python3 tools/pes2/mcp_drive.py "<copia.cue>" --screen main-menu --keep-alive  # deixa o jogo de pe no menu
python3 tools/pes2/mcp_drive.py --measure-menu   # o caso vermelho: uma tecla a mais tem de falhar
tools/pes2/run_duckstation.sh        # sobe o AppImage no :98; --kill encerra
tools/pes2/boot_check.sh             # mede que ele botou -- e diz contra qual binario
tools/pes2/boot_check.sh --self-check   # o veredito e seus casos vermelhos, sem emulador
python3 tools/pes2/drive.py "<copia.cue>" --screen team-select --out-dir <dir>
python3 tools/pes2/drive.py "<copia.cue>" --screen main-menu --save-state  # atalho
python3 tools/pes2/savestate.py selftest                              # o leitor de save state, com os casos vermelhos

ctest --test-dir build -R pes2       # pes2_selftest, pes2_image, pes2_boot
```

Os três alvos do `ctest`: **`pes2_selftest`** monta um disco sintético de 24
setores e roda em qualquer lugar; **`pes2_image`** precisa de
`WE2002_PES2_IMAGE`; **`pes2_boot`** precisa de `PES2_IMAGE` apontando o
**`.cue`** de uma cópia, do DuckStation e do `:98`, e leva ~90 s. Os dois
últimos se reportam *skipped* sem o que precisam.

**São duas famílias de variável, e a receita precisa das duas** —
`WE2002_PES2_*` para as ferramentas de disco, apontando o `(Track 1).bin`, e
`PES2_*` para as de emulador, apontando o `.cue`. Rodar `ctest -R pes2` só
com a primeira dá `100% tests passed` com o `pes2_boot` *skipped* em 0,01 s,
que é o gate que põe o jogo na tela (CORR-PES2-027):

```bash
WE2002_PES2_IMAGE="<copia>/…(Track 1).bin" \
WE2002_PES2_IMAGE_B="<copia B>/…(Track 1).bin" \
WE2002_PES2_CARD="…_1.mcd" \
WE2002_PES2_TMPDIR=<~450 MiB livres> \
PES2_IMAGE="<copia>/….cue" \
  ctest --test-dir build -R pes2
```

| Se a tarefa ou correção tocou | Gate |
| --- | --- |
| ferramenta de `tools/pes2/` | o `--check` dela verde; `pes2_selftest` verde |
| RAM lida de save state | `savestate.py selftest` verde, e ele está dentro do `pes2_selftest`. Toda extração de RAM passa pela guarda do kernel (`PS-X Control PAD Driver` nos primeiros 64 KiB): sem ela um deslocamento errado devolve 2 MiB plausíveis e a busca de valor responde com um endereço que parece um endereço (§6.14) |
| qualquer coisa que escreva na imagem | `iso.py roundtrip` verde **e** o `negative` provando que ele sabe ficar vermelho |
| gravação de nome de time | `poke.py --self-check` verde nas duas releases: recusas, varredura sem sobra, e a imagem de volta byte a byte |
| gravação de asset editado | `asset_write.py check` verde: salvar sem editar devolve a imagem idêntica, o orçamento recusa com a conta, o controle negativo fica localizado, e a cauda EDC/ECC sobrevive |
| gravação de asset, ou conjunto de cópias | `lang_map.py --check` verde nas duas releases, e `--self-check` provando que toda cópia recebeu e que nenhum arquivo do disco ficou com o conteúdo antigo |
| índice de contêiner, imagem ou paleta | `bin_archive.py check` **exit 0 nos quatro discos**. Nas imagens não hackeadas não há entrada cujo retângulo discorde do fluxo; na European Deluxe são **seis** — cinco de tamanho e o `TEX_70.BIN` em 18052, que nem decodifica —, contadas como categoria própria e não como falha, com a linha `is a hacked image: its 6 record(s) …`. A **contagem é asserção**: uma sétima fica vermelha (§1.14(f)) |
| codec ou contêiner de `/BIN/` | `lzss.py --check` verde nos **quatro** discos — as duas releases de PES2 e as duas imagens de WE2002 —, cada um **reconhecido pelo nome** (`recognised PES2 (EsIt) by its 208 containers`) e batendo nas quatro contagens medidas: 208/172/3/33/2.153, 210/174/3/33/2.195, 177/141/3/33/1.842 e 195/159/3/33/2.027 (contêineres/`whole`/`partial`/`none`/blocos). E `--roundtrip` 100% nos blocos que o disco tocado tem |
| offset ou tabela | remedido nas **duas** releases; a divergência sai por marcador, não por offset absoluto |
| comportamento em tela | `boot_check.sh`, com o número medido (desvio-padrão e contagem de pixels), o quadro **fora** do git, e a linha final dizendo **contra qual binário** ele correu. E `boot_check.sh --self-check` verde: o veredito é função e seus casos vermelhos rodam sem emulador — inclusive o quadro congelado, que é o modo de falha real. **A prova de vida amostra uma vez por segundo** ao longo do `PES2_GAP` e guarda a maior diferença; a forma antiga, de dois quadros em relógio fixo, falhava 1 em 3 numa tela de abertura parada (CORR-PES2-030) |
| rota de emulador | `mcp_drive.py --self-check` verde, e `--measure-menu` contra o jogo vivo: ele mede as sete linhas do menu e depois pede sete, o que **tem de falhar**. Verde que nunca pôde ser vermelho é decoração. **São dois comandos, e o primeiro é parte do gate:** `--screen main-menu --keep-alive` deixa o jogo de pé no menu — sem ele toda rota mata no `__exit__` o emulador que subiu, e o caso vermelho passa a depender de um save state esquecido de outra corrida. O `--measure-menu` confere a tela antes de medir, e recusa alto se não for o menu (CORR-PES2-024) |
| cliente ou lançador de MCP | `mcp.py --self-check` e `fork.py --self-check` verdes; os dois rodam sem emulador e os dois têm o caso de servidor ausente |
| endereço de RAM atribuído a um escritor | `who_writes.py --self-check` verde **e** o disparo reproduzido no endereço em questão. Sem o disparo é conjectura: "não disparou" pode ser o endereço não ser escrito naquele estado, e a ferramenta falha alto em vez de devolver vazio. O rito são **dois comandos**, como o do `--measure-menu`: `mcp_drive.py … --screen team-select --keep-alive` e depois `who_writes.py <endereço> --nudge Cross` — o `--nudge` existe porque o PES2 congela em cada saque, e ele passa `duration_frames`, **sem o que o botão fica preso** e todo cutucão seguinte é inócuo (CORR-PES2-031) |
| número em doc | veio de ferramenta, não de soma à mão |

**São dois emuladores, e nenhum está no `PATH`.** O de trabalho é o **fork
com servidor MCP** desde 2026-09-03 (§6.14 do plano), em
`~/Applications/duckstation-mcp/`; quem o sobe é o `tools/pes2/fork.py`, e
`fork.py recipe` diz como obtê-lo — dois caminhos, o download do binário
que o CI dele publica primeiro, a compilação depois. O AppImage oficial continua em
`~/Applications/` porque é o que um terceiro reproduz, e quem o sobe continua
sendo o `run_duckstation.sh`. **Nada do fork entra no repositório** — a
licença do DuckStation é CC-BY-NC-ND-4.0, mesma regra de `roms/`.

| quero | ferramenta | binário |
| --- | --- | --- |
| dirigir uma rota | `mcp_drive.py` | fork |
| mandar um comando com o usuário olhando | `pad.py` | fork |
| o caminho que um terceiro reproduz | `drive.py` + `run_duckstation.sh` | AppImage |
| o gate de boot | `boot_check.sh` | prefere o fork; `PES2_BINARY` força |

**Nenhum dos dois lançadores configura o DuckStation**: ele resolve o
diretório de dados pelo `$HOME`, e a decisão de 2026-09-02 é não isolar,
porque esta máquina roda DuckStation para este projeto. Quem manda é a
configuração do próprio emulador — o `drive.py` lê os bindings dela, e o
`mcp_drive.py` não precisa deles, porque `press_button` recebe o botão pelo
nome. Save state e cartão caem em `~/.local/share/duckstation`, que é **um
só** e serializado: uma instância por vez.

Ao subir o fork à mão, duas coisas medidas em 2026-09-03: o diálogo que sobe
é o **`Automatic Updater`** e `Escape` não o fecha, e a **porta 2346 abre
antes** de ele ser dispensado. O `fork.py launch` cuida dos dois.

---

## Arquivos quentes deste ciclo

Presumir conflito em: [`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md),
[`PES2-NOMES.md`](/docs/PES2-NOMES.md),
[`PES2-AJUSTES.md`](/docs/PES2-AJUSTES.md), `tools/pes2/*`, e o
`pes2_map.json` quando existir.

Recursos serializados deste ciclo, além dos do repositório: o **DuckStation**
e o diretório de dados dele em `~/.local/share/duckstation` — que é **um só**,
porque a isolação foi encerrada por decisão, então uma instância por vez no
`:98` e nenhuma corrida paralela que boote —, e o
**`WE2002_PES2_TMPDIR`** — o round-trip precisa de ~450 MiB livres e duas
corridas simultâneas leem o temporário uma da outra.

---

## Antecipação

**Nenhum precedente ainda neste ciclo.** Tarefa fora da vez só entra com pedido
explícito do usuário, `depends_on` inteiramente concluído e razão escrita. O
padrão que autoriza é o mesmo de sempre: tarefa de fase adiante que uma tarefa
da fase corrente precisa.

---

## Verificações específicas por fase

As oito fases são as do [`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md) §5, e o
quadro de tasks está no [`progresso.md`](/docs/tasks/progresso.md).

**Fase 1 — diferencial barato — está fechada.** Não há task de trabalho nela; o
que entregou (as âncoras `OFS_*` e o diff entre releases) é premissa das
seguintes. Revisar uma task que a toque significa conferir que a premissa não
foi quebrada, não reexecutá-la.

**Fase 0 (tasks 01, 32, 33, 34) — o ferramental da máquina:**

A fase não é sobre o disco: ela decide e constrói **com o que** se mede. Foi
dada por fechada e reaberta duas vezes depois disso — o `savestate.py`, o fork
com MCP e as rotas por MCP entraram todos como Fase 0 —, e é por isso que ela
tem lista própria em vez de virar premissa como a 1.

- A ferramenta nova tem `--self-check` que roda **sem** o recurso externo
  (sem emulador, sem imagem), e ele está dentro do `pes2_selftest`?
- O caso de recurso ausente diz o que fazer, ou despeja traceback? "o fork
  não está rodando" contra um `URLError` de `urllib`
- Todo número afirmado sobre a ferramenta externa foi contado **contra ela
  viva**, não contra o fonte dela? O `TOOLS_JSON` do fork declara 99 nomes e
  o `tools/list` devolve 95
- O binário de terceiro ficou **fora** do repositório, e a receita de obtê-lo
  é executável em vez de prosa num Log? (licença CC-BY-NC-ND-4.0, mesma regra
  de `roms/`). E ela cobre o caminho **barato**, não só o que se descobriu
  primeiro: a de 2026-09-03 só ensinava a compilar, porque a aba de releases
  do próprio fork nunca tinha sido aberta (CORR-PES2-028)
- O gate que julga comportamento **diz contra qual binário** correu? São
  dois DuckStation, e nem a mesma leitura se reproduz entre dias no mesmo
  binário (CORR-PES2-021)
- Uma decisão de máquina (onde o binário mora, `.mcp.json`, configuração do
  emulador) foi **perguntada** ao dono da máquina, e não inventada?
- Toda asserção nova foi vista **ficando vermelha**, e existe um comando
  versionado que a leva ao estado em que ela pode ser exercitada? Gate que só
  fecha a partir de um save state esquecido de outra corrida não é gate
  (CORR-PES2-024)

**Fase 2 (tasks 02 a 04) — inventário de texto:**

- A varredura de texto cobriu o disco, ou só o Track 1 que já se conhecia?
- O `poke` foi verificado **em tela**, com o comando que produz o quadro e o
  número medido — ou só no arquivo?
- A gravação passou pelo `iso.py roundtrip`, e o `negative` provou que a guarda
  sabe ficar vermelha?
- O texto foi escrito na tabela certa? **As oito cópias de nome de time não são
  a mesma lista** — casar por índice grava no time errado com resultado
  plausível em tela (§6.1)
- A medição foi repetida na **outra** release?

**Fase 3 (tasks 05 a 10) — o registro de jogador:**

- Campo, deslocamento e largura em bits foram **medidos**, ou inferidos de um
  exemplo só?
- O domínio de cada campo saiu de quantas amostras? Um valor observado uma vez
  não é domínio
- A **ordem de armazenamento** foi conferida em cada tabela, ou herdada de
  outra? `SELECTC.BIN` e o executável guardam elenco em ordens opostas (§3.3)
- A leitura tratou `SELECTC.BIN` como **pool deduplicado**, não como lista de
  elenco? Os 50 nomes repetidos desalinham tudo depois do primeiro (§1.5)
- O registro é de **tamanho variável**: nome maior não cabe (§6.2)

**Fase 4 (tasks 11 a 16) — o resto do banco:**

- Elenco, formação, uniforme, bandeira e Master League — cada um foi ancorado
  por **marcador**, ou por offset constante? Offset constante não sobrevive à
  troca de release (§6.6)
- A fronteira de setor foi conferida onde a estrutura atravessa 2048 B (§6.3)?
- EDC/ECC foi **preservado**, não recalculado nem "consertado" (§6.7)?

**Fase 5 (tasks 17 a 21) — mapa e leitor:**

- O `pes2_map.json` é o **fonte**, e o resto sai dele por gerador com `--check`
  no `ctest`? Editar o gerado tem de falhar em teste (§4.4)
- O round-trip headless fecha nas **duas** releases?
- Toda divergência conhecida está **escrita**? "100%" significa isso, não zero
  divergência

**Fase 6 (tasks 22 a 25) — editor:**

- O editor foi verificado contra a **definição de pronto** da §0 do plano, item
  a item?
- Cada gravação que ele faz tem uma verificação **em tela**, com o quadro fora
  do git e o número no doc?
- Alguma coisa em `src/` passou a saber o que é PES2? **Não deve** (§6.9)
- Algum quadro do jogo ou trecho de `roms/` foi versionado? **Não deve**

**Fase 7 (tasks 26 a 31) — os assets do disco:**

A fase entrou no quadro em 2026-09-01, junto com a §1.14 do plano, e estas
perguntas saem do que as tasks já executadas mostraram valer.

- A medição foi feita nos **quatro** discos — as duas releases de PES2 e as
  duas imagens de WE2002 — ou numa só? O formato é o mesmo nos quatro, e é
  isso que a §1.14 afirma (§1.14(e), (f))
- O que a ferramenta trata como índice é o **registro de entrada**, e não a
  varredura de ressincronização do codec? Onde as duas discordam, o registro
  ganha — em `TEX_01.BIN` a varredura começa um fluxo 8 bytes antes e rende
  16.381 em vez de 16.384 (§1.14(f))
- A **profundidade** veio da largura do CLUT, e não de um palpite por arquivo?
  O `DAT2D.BIN` tem 261 paletas de 16 cores contra 5 de 256, e um voto por
  arquivo dá a resposta errada em silêncio, porque a contagem de bytes é a
  mesma nas duas profundidades (CORR-PES2-016)
- Gravação: os **dois** orçamentos foram conferidos — o do extent e o da
  **entrada** — e o da entrada primeiro? É ele que morde: a folga medida é de
  poucos bytes, e algumas entradas não recomprimem nem sem alteração (§1.14(g))
- A validação de import recusa **profundidade e paleta** divergentes, não só
  dimensão? Um retângulo de VRAM tem a mesma largura em pixels a 4 e a 8 bpp,
  então dimensão igual não quer dizer slot compatível (CORR-PES2-019)
- **EDC/ECC preservado**, com a cauda de 280 B conferida byte a byte, e o
  recálculo fora do caminho de gravação? (§6.7)
- O conjunto de cópias do asset foi **varrido por conteúdo**, nunca declarado
  por sufixo de nome? O sufixo não sobrevive à troca de release (§6.12)
- Toda guarda nova foi vista **ficando vermelha**, ou só passou verde? Verde
  que nunca pôde ser vermelho é decoração — foi o que a CORR-PES2-009 cobrou
  no `lzss.py` e a CORR-PES2-020 no gravador
- Quadro do jogo **fora** do git; o que entra é o comando que o produz e o
  número medido
