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
12. **Nove armadilhas ao dirigir o DuckStation**, todas medidas. (§6.11)

---

## As fontes de verdade binárias

| Fonte | Papel | Pode escrever? |
| --- | --- | --- |
| `roms/Pro Evolution Soccer 2 (Europe) (EsIt)/` | amostra de trabalho A, dump multi-track | **não** — sempre cópia |
| `roms/Pro Evolution Soccer 2 (Europe) (EnFrDe)/` | amostra de trabalho B, o confronto entre releases | **não** — sempre cópia |
| `roms/golden-european-deluxe.bin`, `roms/japanese-shift-jis.bin` | as duas imagens de **WE2002**; desde a Fase 7 elas são amostra deste ciclo também, porque o formato de contêiner é o mesmo (§1.14) | **não** — leitura pura aqui |
| o memory card do usuário | save real, alinha elenco e fecha fronteira | **não** — nunca escrito; o `run_duckstation.sh` usa cartão próprio |
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
python3 tools/pes2/faq_check.py --image "<track1.bin>"

tools/pes2/run_duckstation.sh        # sobe o jogo no :98, isolado; --kill encerra
tools/pes2/boot_check.sh             # mede que ele botou -- janela, quadro vivo, dois quadros diferentes

ctest --test-dir build -R pes2       # pes2_selftest, pes2_image, pes2_boot
```

Os três alvos do `ctest`: **`pes2_selftest`** monta um disco sintético de 24
setores e roda em qualquer lugar; **`pes2_image`** precisa de
`WE2002_PES2_IMAGE`; **`pes2_boot`** precisa do DuckStation e do `:98`, e leva
~90 s. Os dois últimos se reportam *skipped* sem o que precisam.

| Se a tarefa ou correção tocou | Gate |
| --- | --- |
| ferramenta de `tools/pes2/` | o `--check` dela verde; `pes2_selftest` verde |
| qualquer coisa que escreva na imagem | `iso.py roundtrip` verde **e** o `negative` provando que ele sabe ficar vermelho |
| gravação de nome de time | `poke.py --self-check` verde nas duas releases: recusas, varredura sem sobra, e a imagem de volta byte a byte |
| gravação de asset, ou conjunto de cópias | `lang_map.py --check` verde nas duas releases, e `--self-check` provando que toda cópia recebeu e que nenhum arquivo do disco ficou com o conteúdo antigo |
| índice de contêiner, imagem ou paleta | `bin_archive.py check` **exit 0 nos quatro discos**. Nas imagens não hackeadas não há entrada cujo retângulo discorde do fluxo; na European Deluxe são **seis** — cinco de tamanho e o `TEX_70.BIN` em 18052, que nem decodifica —, contadas como categoria própria e não como falha, com a linha `is a hacked image: its 6 record(s) …`. A **contagem é asserção**: uma sétima fica vermelha (§1.14(f)) |
| codec ou contêiner de `/BIN/` | `lzss.py --check` verde nos **quatro** discos — as duas releases de PES2 e as duas imagens de WE2002 —, cada um **reconhecido pelo nome** (`recognised PES2 (EsIt) by its 208 containers`) e batendo nas quatro contagens medidas: 208/172/3/33/2.153, 210/174/3/33/2.195, 177/141/3/33/1.842 e 195/159/3/33/2.027 (contêineres/`whole`/`partial`/`none`/blocos). E `--roundtrip` 100% nos blocos que o disco tocado tem |
| offset ou tabela | remedido nas **duas** releases; a divergência sai por marcador, não por offset absoluto |
| comportamento em tela | `boot_check.sh`, com o número medido (desvio-padrão e contagem de pixels), e o quadro **fora** do git |
| número em doc | veio de ferramenta, não de soma à mão |

**O emulador não está no `PATH`** — é um AppImage em `~/Applications/`. O
`run_duckstation.sh` usa um `XDG_DATA_HOME` isolado: configuração e cartão
próprios, só o BIOS emprestado por link.

---

## Arquivos quentes deste ciclo

Presumir conflito em: [`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md),
[`PES2-NOMES.md`](/docs/PES2-NOMES.md),
[`PES2-AJUSTES.md`](/docs/PES2-AJUSTES.md), `tools/pes2/*`, e o
`pes2_map.json` quando existir.

Recursos serializados deste ciclo, além dos do repositório: o **DuckStation** e
o `XDG_DATA_HOME` isolado dele (uma instância por vez no `:98`), e o
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

As seis fases são as do [`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md) §5, e o
quadro de tasks está no [`progresso.md`](/docs/tasks/progresso.md).

**Fases 0 e 1 — infra e diferencial barato — estão fechadas.** Não há task de
trabalho nelas; o que entregaram (o `iso.py`, o round-trip, o controle negativo,
o emulador, as âncoras `OFS_*` e o diff entre releases) é premissa das
seguintes. Revisar uma task que as toque significa conferir que a premissa não
foi quebrada, não reexecutá-las.

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
