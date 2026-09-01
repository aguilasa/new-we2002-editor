# Plano de mapeamento — Pro Evolution Soccer 2 (PSX), rumo a um editor

> **Objetivo final: mapear o banco de dados de times e jogadores de
> *Pro Evolution Soccer 2* (PlayStation, Konami, 2002) na imagem de CD, ao
> nível de detalhe que o `newWe2002` já tem para o Winning Eleven 2002, e
> tornar viável um editor escrito do zero.**
>
> | Item | Valor |
> |---|---|
> | Alvo | `roms/Pro Evolution Soccer 2 (Europe) (EsIt)/…(Track 1).bin` |
> | ID do disco | **SLES-03957** (`SYSTEM.CNF`: `BOOT = cdrom:SLES_039.57;1`) |
> | Formato | MODE2/2352, **multi-track** — 1 track de dados + 7 de áudio |
> | Track 1 | 466.768.512 B = 198.456 setores exatos |
> | Editor existente | **nenhum conhecido** — é o ponto de partida do projeto |
> | Âncora | os 69 `OFS_*` de [`Offsets.hpp`](../src/core/include/we2002/Offsets.hpp), já verificados contra o `ed.exe` |
> | Estado | **Fase 0 concluída e verde** (§5.1). A §1 é diagnóstico medido; as Fases 1–6 não começaram. |
>
> Data da análise inicial: 2026-08-29
>
> Este é um projeto **separado** do `newWe2002` e do `wte/`. Não mistura
> código nem build. O que compartilha é conhecimento de formato — e nesse
> ponto o empréstimo é enorme, pela razão da §1.4.

---

## 0. Escopo

### Objetivo

Produzir um **mapa de offsets versionado** da imagem de PES2 — arquivo,
offset relativo, extensão, tipo de registro, codificação — cobrindo pelo
menos nomes de time, abreviações, nomes de jogador, atributos, formações,
uniformes e bandeiras; e, sobre esse mapa, um editor que lê e grava direto
no `.bin`, como o `ed.exe` faz no WE2002.

### Não-objetivos

- **Não** portar o `newWe2002` para abrir PES2. Os offsets não batem e o
  `Database` do core é declarado sobre o layout do WE2002. Fazer um `if` de
  jogo dentro daquele core estragaria os golden tests que hoje o sustentam.
- **Não** mexer nas trilhas de áudio (2–8), no `MOVIE/ISS_2002.STR` (37 MB)
  nem nos `/SD/DA/*.DA` (112 MB de CD-XA). Nada de banco de dados mora ali, e
  os `.DA` nem estão no Track 1 (§6.5).

  **Emenda de 2026-09-01: os `SD/*.RA` saíram desta linha.** A razão original
  continua verdadeira — dado de jogo não mora ali —, mas ela mede o objetivo
  errado depois que a Fase 7 entrou: `.RA` não é streaming, é **banco de som
  VAB**, e editar som é feature de editor. Medição na §1.14, task na
  [PES2-TASK-31](/docs/tasks/31-audio-ra-e-vag.md). O `MOVIE/` e os `.DA`
  continuam fora.
- **Não** recalcular EDC/ECC. O `ed.exe` não recalcula e o jogo não confere;
  gravação in-place preservando os 280 bytes de cauda é a política herdada.
- **Não** decidir agora a linguagem nem a UI do editor. O mapa vem antes;
  sem ele não há o que a UI mostre. A Fase 7 entra nessa mesma conta: um
  editor desenhado sem saber que há grade de imagem × paleta nasce sem lugar
  para ela, e é por isso que a PES2-TASK-30 é portão da PES2-TASK-22.

### Definição de pronto (Fase 6)

Três condições, todas mensuráveis:

1. Um `pes2_map.json` versionado que localize, para cada campo, o
   **conjunto de cópias** que precisam ser gravadas (a §1.5 mostra que o
   jogo duplica as tabelas em quatro ou mais overlays).
2. Uma ferramenta `pes2_poke` que altere um campo pelo mapa e o resultado
   apareça **na tela do emulador**, no menu certo, sem travar o jogo.
3. Um round-trip: ler a imagem inteira pelo mapa, regravar sem editar nada,
   e o `.bin` sair **byte a byte idêntico** ao original.

---

## 1. Diagnóstico da imagem — o que já está medido

Tudo nesta seção foi medido em 2026-08-29 sobre o dump em `roms/`, não
inferido.

### 1.1 A imagem é multi-track; a anterior não era

As duas imagens de teste do `newWe2002` são `.bin` de arquivo único. Esta
não: o `.cue` declara oito arquivos, o primeiro `MODE2/2352` e os sete
seguintes `AUDIO`. **Toda ferramenta nova recebe o caminho do Track 1**, e a
tentação de aceitar a pasta ou o `.cue` deve ser resistida enquanto não
houver motivo — offset absoluto só faz sentido dentro de um arquivo.

Existe também um dump `(EnFrDe)` ao lado, com Track 1 de 466.770.864 B
(2.352 B a mais, um setor). É a mesma release em outro conjunto de idiomas;
serve de **segunda amostra** para separar o que é dado de jogo do que é
texto localizado — ver a Fase 2.

> O `CLAUDE.md` diz "`Pro Evolution Soccer 2 (Europe) (EnFrDe)` — **NÃO
> USAR**". Aquilo vale para o **`newWe2002`**, que corrompe a imagem porque
> o layout diverge do WE2002 depois de ~2 MB. Não é proibição de estudar o
> disco; é exatamente a divergência que este plano existe para mapear.

### 1.2 A geometria de setor é a mesma

Setor de 2.352 B = 24 de cabeçalho (12 sync + 4 header + 8 subheader) +
2.048 de dados + 280 de EDC/ECC. O setor 16 traz o PVD com `CD001` e
`PLAYSTATION`. Ou seja: **toda a aritmética de setor do
[PLAN-LINUX.md](/docs/PLAN-LINUX.md) §"Formato da imagem" se aplica sem
mudança** — inclusive o fato de que um registro pode atravessar a fronteira
de setor e o offset "salta" 304 bytes ali.

Conversão que toda ferramenta vai precisar, nas duas direções:

```
offset_absoluto  -> lba = off // 2352 ;  byte_no_setor = off % 2352 - 24
offset_no_arquivo -> (lba - lba_do_arquivo) * 2048 + byte_no_setor
```

### 1.3 O sistema de arquivos

ISO9660 comum, legível sem montar. Raiz com 34 entradas, mais `BIN/` (239
arquivos), `SD/` (áudio streaming) e `MOVIE/`. Total: **252 arquivos**.

Os que interessam à primeira vista:

| Arquivo | LBA | Tamanho | O que é |
|---|---|---|---|
| `SLES_039.57` | 24 | 333.824 | executável PS-X EXE |
| `ENDING.BIN` | 430 | 395.400 | overlay; **carrega nomes de time** |
| `RESULT.BIN` | 800 | 19.481 | overlay; nomes de time em caixa mista |
| `SELECT.BIN` | 850 | 216.472 | overlay de seleção; **nomes + abreviações** |
| `SELECT8.BIN` | 1800 | 131.156 | overlay; abreviações |
| `SELECTC.BIN` | 1950 | 88.780 | overlay; **nomes de jogador** |
| `SELFORM.BIN` | 2050 | 96.224 | overlay de formação |
| `REPLAYS.BIN` | 2400 | 68.708 | overlay; abreviações |
| `GAME.BIN` | 2550 | 761.394 | overlay de partida |
| `BIN/DAT2D.BIN` | 5300 | 68.556 | dados 2D (no WE2002, cores de bandeira) |

### 1.4 O atalho: PES2 e WE2002 são a mesma árvore de disco

Esta é a descoberta que muda o custo do projeto.

Comparando o ISO do `golden-european-deluxe.bin` com o do PES2:

- WE2002 tem 245 arquivos, PES2 tem 252;
- **223 caminhos são idênticos**;
- e os overlays da §1.3 estão **no mesmo LBA nos dois discos** —
  `ENDING.BIN` em 430, `SELECT.BIN` em 850, `SELECTC.BIN` em 1950,
  `GAME.BIN` em 2550, `BIN/DAT2D.BIN` em 5300. Só os tamanhos mudam, e
  pouco.

O que difere é periférico e explicável: o WE2002 japonês tem
`BIN/T_NAME.BIN` e `BIN/DATSEL*.BIN` no singular, e PES2 os replica por
idioma (`T_NAME_I`/`T_NAME_S`, `DATSEL_I`/`DATSEL2I`/`DATSEL3I`), mais
`BIN/LC_*` e `BIN/CG*` por língua e `FNOTE_{G,I,S}.BIN`. Isto é, **a
diferença é a localização europeia, não a engine.**

Consequência prática: os 69 `OFS_*` do `newWe2002` não são só curiosidade —
são o **índice de onde procurar**. Mapeados de volta ao ISO do WE2002 eles
caem em treze arquivos:

| Arquivo (WE2002) | nº de `OFS_*` | primeiro |
|---|---|---|
| `SLPM_870.56` (o exe) | 9 | `OFS_PLAYER_NAME` = 387792 |
| `SELECT.BIN` | 32 | `OFS_TEAM_NAME_KANJI` = 2002316 |
| `SELECT2.BIN` | 6 | `OFS_ML_TEAM_NAME_8` = 2476048 |
| `REPLAYS.BIN` | 5 | `OFS_TEAM_ABBREV_2` = 5651068 |
| `BIN/DAT2D.BIN` | 4 | `OFS_FLAG_COLOURS_SENEGAL` = 12545758 |
| `ENDING.BIN` | 3 | `OFS_TEAM_NAME_1` = 1012640 |
| `SELFORM.BIN` | 3 | `OFS_TEAM_NAME_5` = 4822908 |
| `SELECT4.BIN` | 2 | `OFS_COST_NATIONAL` = 3067404 |
| `RESULT.BIN`, `OPENNING.BIN`, `SELECT3.BIN`, `SELECT8.BIN`, `SELECTC.BIN` | 1 cada | — |

**Cada `OFS_*` do WE2002 é uma hipótese testável no PES2**: mesmo arquivo,
mesmo tipo de conteúdo, offset relativo próximo.

A tabela completa — os 69, cada um como `(arquivo, offset relativo)` — está
em [/docs/samples/pes2-ofs-map.md](/docs/samples/pes2-ofs-map.md), gerada
por `tools/pes2/ofs_map.py`. **Os 69 caem em 13 arquivos e nenhum ficou de
fora**, e os 13 existem no PES2, contando o executável, cujo nome é o
único que muda (`SLPM_870.56` × `SLES_039.57`).

Cinco desses pares já se pode afirmar, porque o lado PES2 está localizado
por marcador:

| `OFS_*` | Arquivo | WE2002 | PES2 `(EsIt)` | Δ |
|---|---|---:|---:|---:|
| `OFS_TEAM_NAME_1` | `ENDING.BIN` | 1256 | 1256 | **0** |
| `OFS_TEAM_ABBREV_3` | `SELECT8.BIN` | 860 | 1016 | +156 |
| `OFS_TEAM_NAME_2` | `RESULT.BIN` | 344 | 524 | +180 |
| `OFS_TEAM_ABBREV_2` | `REPLAYS.BIN` | 5636 | 11000 | +5364 |
| `OFS_TEAM_MIXED_CASE_NAME` | `SELECTC.BIN` | 10652 | 16576 | +5924 |

A primeira linha é a confirmação mais forte desta seção: a cópia de nome
de time do `ENDING.BIN` está no **mesmo offset relativo nos dois jogos**.
As outras quatro se deslocam, e pela mesma razão da §1.12 — o texto de
interface que as precede tem outro tamanho.

### 1.5 O que já foi localizado no PES2

Quatro tabelas, achadas por varredura de string ASCII nos arquivos
extraídos:

**Nomes de time**, `SELECT.BIN` offset relativo **3128**, começando com o
literal `MASTER DATA` e seguindo com os nomes fictícios da release europeia
— `PATAGONIA`, `MARMARA`, `BYZANTINOBUL`, `PELOPONNISOS`, `RUHR`, `ANHALT`,
`WESTFALEN`, `ABRUZZI`, `TOSCANA`, `EMILIA`, `UMBRIA`, `LOMBARDIA`,
`PIEMONTE`, … — depois as seleções (`ALWAYS ARGENTINA`, `BELOVED BRAZIL`, …,
`SCOTLAND`, `IRELAND`), os *classic* e os *allstars*.

**Abreviações de três letras**, mesmo arquivo, offset **4292**, na mesma
ordem: `PTA`, `MRA`, `BZA`, `PNS`, `RUR`, `AHT`, `WES`, …, `SCT`, `IRL`.
Registro de 4 B, terminador incluso.

**Cópias das duas tabelas** — e este é o ponto que decide a arquitetura do
editor:

| Tabela | cópias medidas (offset em `(EsIt)`) | entradas |
|---|---|---|
| nomes de time, caixa alta | `SELECT.BIN` @3128 | 106 |
| nomes de time, caixa alta | `ENDING.BIN` @1256 | 95 |
| nomes de time, caixa mista | `SELECTC.BIN` @16576 | 99 |
| nomes de time, caixa mista | `REPLAYS.BIN` @11380 | 123 |
| nomes de time, caixa mista | `RESULT.BIN` @524 | 94 |
| nomes de time, caixa mista | `SELECT.BIN` @33188 | 32 |
| nomes de time, caixa mista | `SELECT3.BIN` @9448 | 99 |
| nomes de time, caixa mista | `SELFORM.BIN` @460 | 99 |
| abreviações | `SELECT.BIN` @4292 | 95 |
| abreviações | `SELECT8.BIN` @1016 | 95 |
| abreviações | `REPLAYS.BIN` @11000 | 95 |

Os offsets saem de `tools/pes2/tables.py`, que os resolve por marcador nas
duas releases; os de `RESULT.BIN`, `REPLAYS.BIN` e `SELECTC.BIN` são
outros em `(EnFrDe)` — ver a §1.12.

É o mesmo padrão do WE2002, onde o editor grava seis cópias de nome e três
de abreviação. **Gravar uma só cópia produz um jogo inconsistente**, com o
nome novo numa tela e o velho na outra.

**E a coluna de contagem já avisa o que a §6.1 cobra: as oito "cópias"
de nome de time não são a mesma lista.** Uma tem 106 entradas, outra 95,
outra 99, outra 123, outra 94, outra 32. Casar qualquer par delas por
índice grava no time errado.

**Eram cinco até 2026-09-01.** As três últimas — a segunda lista de
`SELECT.BIN`, e as de `SELECT3.BIN` e `SELFORM.BIN` — apareceram quando o
`poke` da PES2-TASK-02 gravou as cinco conhecidas e varreu o disco atrás
do nome velho. Ver a §1.6.

**Nomes de jogador**, `SELECTC.BIN` offset relativo **17604**, em duas
famílias contíguas — e os dois números que circulam são os dois extremos da
mesma tabela, não uma correção do outro:

| offset | o que é |
|---|---|
| **17604** | onde a tabela **começa**, com os fictícios (`Di Sephoro`, `Filimol`, `Karpes`, `Dimaz`, `Orimas`, …) |
| **20736** | onde, dentro dela, começam os **reais** (`Cavallero`, `Bonano`, `Batistuta`, `Caniggia`, `Aimar`, `Gallardo`, …) |

São 1.399 entradas no total. Um mapa construído a partir de 20736 perde a
primeira família inteira — e ela é metade do problema da §1.7.

Uma segunda massa de nomes vive no próprio executável, `SLES_039.57`
@284720: **1.449 registros de 10 B fixos**. Medido em 2026-08-30 por
`tools/pes2/player_map.py`, a relação entre as duas é exata e é o
contrário do que a diferença de 50 sugere:

- as duas guardam **os mesmos 1.399 nomes distintos**; nenhuma tem um que
  a outra não tenha;
- `SELECTC.BIN` guarda cada nome **uma vez**; o executável **repete 50**
  deles;
- `SELECTC.BIN` é **subsequência exata** do executável lido de trás para
  frente.

Isto é: **`SELECTC.BIN` é um pool de string deduplicado e o executável é
ordenado por vaga.** Jogador que está em dois elencos ganha dois registros
lá e um aqui. `Baser`, `Amabri`, `Emakrif` são parte dela, em @291750.

E ainda há mais nome em `SELECTC.BIN` **depois** do pool: 25 blocos, cerca
de 2.000 trechos, de 31552 até por volta de 50000, nenhum entre os 1.399.
Ver a Fase 2.

### 1.6 Contagem e ordem — medido, não estimado

A varredura fechou as tabelas de texto por inteiro. Estes são números
duros, não hipóteses — e desde 2026-08-30 eles saem de uma ferramenta
versionada, `tools/pes2/tables.py`, que reproduz a medição inteira em
menos de um segundo:

| Tabela | Arquivo | Offset `(EsIt)` | Entradas | Registro |
|---|---|---:|---:|---|
| nome de time, caixa alta | `SELECT.BIN` | 3128 | **106** | 2 de cabeçalho + 104 times |
| abreviação de 3 letras | `SELECT.BIN` | 4292 | **95** | fixo de 4 B |
| jogador de clube | `SELECT.BIN` | 5320 | **463** | fixo de 10 B |
| nome de time, caixa alta (cópia) | `ENDING.BIN` | 1256 | **95** | terminado em `NUL` |
| abreviação (cópia) | `SELECT8.BIN` | 1016 | **95** | fixo de 4 B |
| abreviação (cópia) | `REPLAYS.BIN` | 11000 | **95** | fixo de 4 B |
| nome de time, caixa mista (cópia) | `REPLAYS.BIN` | 11380 | **123** | terminado em `NUL` |
| nome de time, caixa mista (cópia) | `RESULT.BIN` | 524 | **94** | terminado em `NUL` |
| nome de time, caixa mista | `SELECTC.BIN` | 16576 | **99** | terminado em `NUL` |
| nome de time, caixa mista (cópia) | `SELECT.BIN` | 33188 | **32** | terminado em `NUL` |
| nome de time, caixa mista (cópia) | `SELECT3.BIN` | 9448 | **99** | terminado em `NUL` |
| nome de time, caixa mista (cópia) | `SELFORM.BIN` | 460 | **99** | terminado em `NUL` |
| nome de jogador | `SELECTC.BIN` | 17604 | **1.399** | terminado em `NUL` |
| nome de jogador | executável de boot | 284720 | **1.449** | fixo de 10 B |

```
python3 tools/pes2/tables.py "<track1.bin>" --check     # conta e digere
python3 tools/pes2/tables.py "<track1.bin>" --dump team-names
```

O `--check` confere a contagem **e um digest SHA-256 das entradas
concatenadas**. Os catorze digests são idênticos em `(EsIt)` e
`(EnFrDe)`, o que transforma a conclusão da §1.12 — mesmo banco, um editor
só — de lembrança em teste.

**As três últimas cópias de nome de time entraram em 2026-09-01**, pela
PES2-TASK-02, e não por varredura nova: o `poke` gravou as cinco que esta
tabela listava e depois varreu todo arquivo `form1` atrás do nome velho.
Ele sobreviveu em três lugares. `SELECT3.BIN` e `SELFORM.BIN` guardam a
lista de 99 com o **mesmo digest** de `SELECTC.BIN`; `SELECT.BIN` guarda
uma **segunda** lista, em caixa mista, só com os 32 clubes fictícios —
ela termina em `Aragon` e emenda direto nas strings de interface
localizadas, e é por isso que a regra de fim dela é o último clube e não
`IRELAND`. A lição é da §6.1 e vale repetir: **o conjunto de cópias não se
declara, se varre.**

As duas primeiras entradas do bloco de nomes são `MASTER DATA` e
`? ? ? ?` — cabeçalho e *placeholder* de slot vazio, não times. Os 104
times seguem nesta ordem, e **é esta a ordem canônica** a que toda tabela
numérica paralela vai obedecer:

1. **32 clubes fictícios** — `PATAGONIA`, `MARMARA`, `BYZANTINOBUL`,
   `PELOPONNISOS`, `RUHR`, `ANHALT`, `WESTFALEN`, `ABRUZZI`, `TOSCANA`,
   `EMILIA`, `UMBRIA`, `LOMBARDIA`, `PIEMONTE`, `MARCHE`, `FLANDRE`,
   `NOORDZEEKANAAL`, `RIJNKANAAL`, `MEDOC`, `NORMANDIE`, `LANGUEDOC`,
   `PROVENCE`, `CANTABRIA`, `ANDALUCIA`, `NAVARRA`, `CATALUNA`,
   `VASCONGADAS`, `HIGHLANDS`, `YORKSHIRE`, `EUROPORT`, `LIGURIA`,
   `LONDON`, `ARAGON`;
2. **7 seleções "temáticas"** — `ALWAYS ARGENTINA`, `BELOVED BRAZIL`,
   `GENUINE GERMANY`, `IMMORTAL ITALY`, `HEROIC HOLLAND`,
   `FOREVER FRANCE`, `ETERNAL ENGLAND`;
3. `WORLD ELITE`, `EURO ELITE`;
4. **54 seleções reais**, de `AUSTRALIA` a `IRELAND`;
5. **7 *classic*** (`CLASSIC ARGENTINA` … `CLASSIC ENGLAND`) e
   `WORLD ALLSTARS`, `EURO ALLSTARS`.

**As abreviações cobrem só os 95 primeiros** — 32 + 7 + 2 + 54. Os sete
*classic* e os dois *allstars* **não têm abreviação**, e um editor que
assuma paralelismo de 1 para 1 entre as duas tabelas grava fora do lugar.

A tabela de caixa mista de `SELECTC.BIN` **não é a mesma lista**: ela abre
com quatro seleções que não estão na de caixa alta — `Belarus`, `Georgia`,
`Uzbekistan`, `Iceland` — antes de `Patagonia`. São nações extras do modo
de edição. Mais uma razão para nunca casar tabelas por índice sem conferir
o comprimento das duas.

### 1.7 Nome de jogador: real numa metade, fictício na outra

O disco mistura os dois regimes, e a divisão é por tipo de time:

| Time | Regime | Amostra medida |
|---|---|---|
| seleção real | **nome real** | `Ono`, `Toda`, `Inamoto`, `Matsuda` (Japão); `Chivu`, `Galca`, `Popescu` (Romênia); `Litmanen`, `Forssell` (Finlândia); `Bonano`, `Batistuta`, `Veron` (Argentina) |
| clube | **fictício** | `Di Sephoro`, `Filimol`, `Karpes`, `Dimaz`, `Orimas` |
| *classic* | **fictício** | `Frolao`, `Recezo` (Brasil); `Haltern`, `Badenfauer` (Alemanha); `Tardisi`, `Callavoti` (Itália); `Oranges089`, `Oranges087` (Holanda) |

O caso `Oranges089` merece nota: é *placeholder* numerado sobrevivendo no
disco final. Onde aparecer, é sinal de slot que a Konami não preencheu — e
de que o campo é editável sem quebrar nada.

O corte por 23 jogadores por time bate aproximadamente (1.399 = 60 × 23 +
19), o que **não fecha** e portanto não serve de prova. O tamanho de elenco
tem de sair da tabela numérica de elenco, não da contagem de nomes; ver a
Fase 3.

**O elenco de 23 está confirmado por fora**, porém: o FAQ do BigCj34 lista
63 seleções com exatamente 23 jogadores cada, e o alinhamento automático
contra o disco casou **27 desses 63 com 20 ou mais dos 23 nomes** (8 com os
23 em cheio). O que ainda falta é a fronteira exata de cada bloco, não o
tamanho.

Uma coisa esse alinhamento sugeriu: em `SELECTC.BIN` o elenco está na
ordem inversa da de exibição — a Irlanda termina em `Given`, o goleiro,
que os FAQs listam primeiro. **Mas isso não vale para o disco inteiro.**
A §3.3 mediu os 54 elencos contra o memory card: os 49 que moram em
`SELECTC.BIN` estão invertidos, e os dois que moram em `SLES_039.57`
estão na ordem direta. A ordem é propriedade da tabela. Ver
[/docs/PES2-NOMES.md](/docs/PES2-NOMES.md).

### 1.8 O que o disco **não** tem: o clube real

`PIEMONTE` não carrega em lugar nenhum a informação de que é a Juventus.
A release europeia é integralmente fictícia nos clubes, e **nenhuma tabela
do disco guarda o nome real** — nem oculta, nem comprimida, nem em outro
idioma (as duas releases, `(EsIt)` e `(EnFrDe)`, não diferem nisso).

O mapa fictício → real é, portanto, **conhecimento externo**. Ele não afeta
o mapeamento de offsets em nada, mas afeta muito a usabilidade de um
editor: mostrar "PIEMONTE (Juventus)" ao lado do slot é a diferença entre
uma tabela e uma ferramenta. Duas fontes possíveis, nesta ordem:

1. **os elencos**, uma vez que a Fase 3 ligue jogador a time — reconhecer
   um plantel identifica o clube sem depender de ninguém. É a via
   preferida, porque é verificável;
2. **FAQs de terceiros**, que trazem a correspondência tabulada.

**Resolvido em 2026-08-30 pela segunda via.** O usuário baixou os dois FAQs
(o GameFAQs recusa requisição automatizada com HTTP 403 e desafio
Cloudflare) e os 32 clubes estão mapeados em
[/docs/PES2-NOMES.md](/docs/PES2-NOMES.md), com a procedência separada do
que foi medido: índice, nome e offset saem do disco; o clube real vem dos
FAQs. As duas fontes concordam nos 32, e **30 dos 32 caem na posição
prevista** ao casar as listas em ordem inversa — o que dá à tabela uma
verificação estrutural que nenhuma das duas fontes traz sozinha.

O apêndice também registra o que os FAQs **não** resolvem: a grafia do
jogo só está tabelada para sete dos 63 elencos, e nenhum elenco de clube
está listado.

### 1.9 A codificação, e por que a busca ingênua falhou

Primeira tentativa: `grep` por `JUVENTUS`, `BARCELONA`, `ARSENAL` na imagem
inteira. Zero. Segunda: busca por **padrão de delta** — a diferença entre
letras consecutivas, que acha o nome sob qualquer mapa de caractere linear,
com passo 1 e passo 2. Também zero.

A explicação não é criptografia: **os times licenciados não existem nesta
release**. `PIEMONTE` é a Juventus, `LOMBARDIA` é um clube de Milão,
`CATALUNA` é o Barcelona. Os nomes estão em **ASCII puro** o tempo todo — só
não são os que eu procurava.

Isso é uma diferença dura em relação ao WE2002 japonês, que guarda nome de
time em **Shift-JIS de largura dupla** e por isso precisa do
`KanjiToAscii`/`AsciiToKanji` do
[`TextCodec.cpp`](../src/core/TextCodec.cpp). No PES2 europeu **não há
codec a portar** para esses campos. (Os nomes de jogador do WE2002, esses,
já eram ASCII de caixa mista — `Toldo`, `Materazzi`, `Cannavaro` — em
registros fixos de 10 B no executável.)

### 1.10 Registro de tamanho variável — a armadilha estrutural

Os registros do PES2 **não são de tamanho fixo**. São a string mais um
terminador, alinhados a 4 bytes:

```
Bonano\0\0            8 B
Batistuta\0\0\0      12 B
Caniggia\0\0\0\0     12 B
Aimar\0\0\0           8 B
Almeyda\0             8 B
```

O WE2002 usava passo fixo de 10 B nos nomes de jogador e alinhamento a 4 nos
nomes de time. Aqui o alinhamento a 4 é a regra geral, e **não há tabela de
ponteiros de 32 bits apontando para o bloco** — a varredura achou três
candidatos isolados, ruído. Há 624 candidatos de 16 bits, que é o que
merece a primeira investigação da Fase 3.

Enquanto isso não estiver resolvido, a regra do editor é conservadora:
**um nome novo só pode ocupar até o tamanho do slot alinhado que já existe.**
Escrever mais longo desloca todo o resto do bloco e quebra qualquer índice
sequencial que o jogo mantenha.

**Mas isto não é regra geral do jogo** — é regra desta família de tabelas.
Existe pelo menos uma outra, achada em 2026-08-30, com esquema oposto:
`SELECT.BIN` 5320…9950, **463 registros de 10 bytes fixos**, preenchidos
com `NUL` à direita e **sem terminador quando o nome ocupa os 10**. No
disco lê-se `NachtegallHeggem` corrido. Detalhe em
[/docs/PES2-NOMES.md](/docs/PES2-NOMES.md).

Um editor que trate as duas do mesmo jeito erra nos dois sentidos: trunca
onde caberia mais, e **corrompe o primeiro caractere do vizinho** ao
terminar em `NUL` um nome de 10 letras. O esquema é propriedade da tabela,
e o mapa tem de declará-lo por tabela.

### 1.11 O que ainda não foi localizado

Atributos de jogador, posição, número de camisa, formação, cores de
uniforme, forma e cores de bandeira, elenco por time (que jogador pertence a
que clube), custos de Master League. Nada disso aparece como texto, por
definição — é numérico. É o trabalho das Fases 3 e 4.

Um sinal já colhido: os `BIN/GRDM_*.BIN` (17 arquivos, ~40–47 kB) têm
centenas de literais de três letras `ZZZ` e `FFF`, com aparência de
*placeholder* de placa de publicidade ou de nome curto não preenchido. Vale
uma olhada, não é prioridade.

### 1.12 As duas releases europeias são o mesmo jogo — um editor só

`(EsIt)` e `(EnFrDe)` **não são jogos diferentes**. São o mesmo título com
outro conjunto de idiomas, e o banco de dados é o mesmo. Medido em
2026-08-30:

| Comparação | Resultado |
|---|---|
| arquivos em comum | 236 (252 × 257 no total) |
| **byte a byte idênticos** | **202** |
| diferem | 27 |
| não comparáveis a partir do Track 1 | 7 |
| exclusivos de cada lado | 16 × 21 — os `LC_*`/`T_NAME_*`/`DAT2D_*`/`FNOTE_*`/`DATSEL*` por idioma, os `SD/PES2*.RA` de narração, e o executável |
| executável | `SLES_039.57` (EsIt) × `SLES_039.46` (EnFrDe) |

**Estes não são os números que esta seção trazia até 2026-08-30**, que
eram 204 idênticos e 32 diferentes. Aqueles foram contados à mão, sem
procedimento escrito, e não voltaram. Os de agora saem de
`tools/pes2/diff_releases.py`, com a lista completa em
[/docs/samples/pes2-diff-releases.md](/docs/samples/pes2-diff-releases.md):

```
python3 tools/pes2/diff_releases.py "<esit>" "<enfrde>" --check
python3 tools/pes2/diff_releases.py "<esit>" "<enfrde>" --markdown > docs/samples/pes2-diff-releases.md
```

Os 7 não comparáveis são os `/SD/DA/*.DA`: eles moram nas trilhas de
áudio, e o Track 1 não guarda versão nenhuma deles para comparar (§6.5).
O único arquivo Form 2, `/MOVIE/ISS_2002.STR`, **é idêntico** nas duas — a
comparação dele é de setor cru, porque ele não tem área de 2.048 B.

Dos 27 que diferem, 19 mudam de tamanho (texto localizado) e 8 mantêm o
tamanho e mudam conteúdo: `GAME.BIN` (38.213 B), `SELECT4.BIN` (6.884),
`ENTER.BIN` (3.272), `PKMATCH.BIN` (242), `TRAINING.BIN` (126),
`FNOTE_G.BIN` (105), `MOVIE.BIN` (79) e `SYSTEM.CNF` (2, que é o nome do
executável). São esses oito que merecem olhar na Fase 1, porque ali pode
haver dado de jogo e não texto.

E, sobretudo: **as tabelas de nome têm conteúdo idêntico nas duas.** As
201 entradas de nome de time + abreviação de `SELECT.BIN` e as 1.498 de
`SELECTC.BIN` casam entrada por entrada, na mesma ordem. Nenhum time,
nenhum jogador, nenhuma abreviação muda.

O que muda é **onde a tabela cai dentro do overlay**, porque o texto de
interface localizado que a precede tem tamanho diferente:

| Tabela | Arquivo | EsIt | EnFrDe | deslocamento |
|---|---|---|---|---|
| nome de time | `SELECT.BIN` | 3128 | 3128 | **0** |
| abreviação | `SELECT.BIN` | 4292 | 4292 | **0** |
| nome de time (cópia) | `ENDING.BIN` | 1256 | 1256 | **0** |
| abreviação (cópia) | `SELECT8.BIN` | 1016 | 1016 | **0** |
| caixa mista (cópia) | `RESULT.BIN` | 524 | 632 | +108 |
| abreviação (cópia) | `REPLAYS.BIN` | 11000 | 16244 | +5244 |
| times + jogadores | `SELECTC.BIN` | 16576 | 25180 | +8604 |

Quatro coincidem e três não. Um mapa de offsets **constante** atenderia
metade das cópias e escreveria lixo na outra metade — que é o modo de
falha mais caro possível, porque parece funcionar.

**Conclusão de projeto: um editor só, e o mapa não guarda offset fixo.**

### 1.13 Ancoragem por marcador, em vez de offset constante

A saída é localizar cada tabela em tempo de abertura, por um literal que
só aparece uma vez no arquivo. `python3 tools/pes2/iso.py anchors
<track1.bin>` reconfere **onze** desses pares (arquivo, literal) nas duas
releases, e **todos ocorrem exatamente uma vez** no arquivo que lhes toca.

Marcador e tabela não são a mesma contagem, e vale separar: os onze pares
ancoram **catorze** localizações de tabela, porque dois deles
servem a mais de uma — `Belarus\0Georgia\0` acha os times e, 1028 bytes
adiante, os jogadores; `PTA\0MRA\0BZA\0` acha três cópias de abreviação e,
380 bytes adiante em `REPLAYS.BIN`, mais uma de nome de time. Quem resolve
as catorze é `tools/pes2/tables.py`.

| Marcador | Arquivo | acha | deslocamento |
|---|---|---|---:|
| `MASTER DATA\0` | `SELECT.BIN` | início da tabela de nome de time | 0 |
| `PTA\0MRA\0BZA\0` | `SELECT.BIN`, `SELECT8.BIN`, `REPLAYS.BIN` | as três cópias de abreviação | 0 |
| `PATAGONIA\0` | `ENDING.BIN` | cópia de nome de time | 0 |
| `Patagonia\0` | `RESULT.BIN` | cópia em caixa mista | 0 |
| `Patagonia\0` | `SELECT.BIN` | a segunda lista do arquivo, 32 clubes | 0 |
| `Belarus\0Georgia\0` | `SELECTC.BIN` | times em caixa mista | 0 |
| `Belarus\0Georgia\0` | `SELECT3.BIN`, `SELFORM.BIN` | cópias da lista de 99 | 0 |
| `Belarus\0Georgia\0` | `SELECTC.BIN` | nomes de jogador | +1028 |
| `PTA\0MRA\0BZA\0` | `REPLAYS.BIN` | cópia em caixa mista | +380 |
| `Given\0\0\0\0\0Staunton\0\0` | executável de boot | jogadores de 10 B | 0 |
| `Oranges001` | `SELECT.BIN` | jogadores de clube, 10 B | **−1740** |

O mapa passa então a guardar **(arquivo, marcador, deslocamento a partir
do marcador)** em vez de offset absoluto. Três ganhos, além de resolver a
divergência da §1.12:

1. sobrevive a qualquer outra release europeia sem remapear nada;
2. **falha alto** — marcador ausente é erro imediato e legível, não
   gravação silenciosa no lugar errado;
3. serve de verificação de que a imagem aberta é mesmo PES2.

A identidade da release, quando for preciso saber, sai do `SYSTEM.CNF`:
`BOOT = cdrom:SLES_039.57;1` contra `SLES_039.46;1`.

**Duas coisas que a lista acima já obriga o formato do mapa a ter, e que a
redação original de "(arquivo, marcador, deslocamento)" não previa:**

1. **O deslocamento é assinado.** `Oranges001` **não marca o começo** da
   tabela que ancora: ele resolve em 7060 nas duas releases e a tabela de
   10 B começa em 5320 — é o registro **174** de 463, e o delta é
   **−1740**. Marcador dentro do meio da tabela é caso normal, não
   exceção, porque quem escolhe o literal é quem procura um trecho único,
   não um trecho inicial.
2. **O mapa tem de declarar a contagem, por tabela.** Nenhuma tabela deste
   disco tem sentinela de fim. O que separa uma da seguinte é só o número
   de entradas — e no caso mais apertado, **zero byte**: os 106 nomes de
   time ocupam de 3128 a 4292, e 4292 é exatamente onde `PTA\0` começa. No
   disco lê-se `EURO ALLSTARS\0\0\0PTA\0` corrido. Escrever um 107º nome
   invade a primeira abreviação. A §6.2 já manda truncar em vez de
   deslocar; a margem que ela protege é nula.

`tools/pes2/tables.py` é onde essas três coisas — marcador, delta assinado
e regra de fim — estão escritas para cada tabela, e `--check` as reconfere
contra o disco.

**Ressalva:** isto está provado para as tabelas de texto, que têm literal
óbvio. As tabelas numéricas das Fases 3 e 4 não têm, e ali a âncora terá
de ser outra coisa — o fim da tabela de texto que as precede, uma
assinatura de conteúdo, ou um offset relativo a um marcador próximo.
Decidir isso caso a caso é trabalho da Fase 5.

### 1.14 Os assets do disco são os mesmos do WE2002 — medido

A §1.4 mostrou que os dois jogos compartilham a árvore de disco. Esta seção
mostra que compartilham também o **formato de dentro dos arquivos** — e é o
que traz para o PES2 o [PLAN-FEATURES](/docs/PLAN-FEATURES.md) inteiro, que
foi escrito para o WE2002 a partir das ferramentas do CARP.

Medido em **2026-09-01**, extraindo os contêineres das duas imagens com o
`tools/pes2/iso.py` — que, notado de passagem, **lê a imagem do WE2002 sem
adaptação**, e portanto já entrega a Fase 8 daquele plano.

**(a) O cabeçalho de contêiner é um array de ponteiros de RAM, e a largura
bate arquivo a arquivo.** As primeiras palavras de 32 bits de todo `BIN/*.BIN`
são endereços da RAM da PSX (`0x800xxxxx`); o fluxo comprimido começa depois
da última. Contando quantas palavras cada arquivo tem, o histograma de
`/BIN/` é **o mesmo nos dois jogos**:

| palavras de cabeçalho | WE2002 (JP) | PES2 `(EsIt)` | exemplo |
|---:|---:|---:|---|
| 0 | 1 | 1 | `DEMODATA.BIN` |
| 1 | 2 | 5 | `T_NAME*.BIN`, `DAT2D_I.BIN` |
| 2 | 20 | 30 | `DAT2D.BIN`, `LOGO.BIN`, `TITLE.BIN` |
| 4 | 1 | 1 | `DATSEL*.BIN` |
| 6 | 3 | 3 | `CGAS.BIN` |
| 7 | 39 | 39 | `CGAF.BIN` |
| 8 / 9 / 15 / 18 | 1 cada | 1 cada | `CGEU`, `CGAM`, `CGLE`, `MODEL` |
| 12 | **105** | **105** | `TEX_*.BIN` |
| 26 / 28 / 29 | 9 / 7 / 2 | 9 / 7 / 2 | `GRDM_*`, `ENDCSR` |
| 46 / 204 | 1 / 1 | 1 / 1 | `ENDANIME`, `ANIME` |
| **total `form1` em `/BIN/`** | **195** | **208** | |

Os treze de diferença são todos cópia de idioma, e caem nos baldes de 1, 2 e
7 palavras — os únicos três que se movem. Todo o resto é igual **na contagem**,
não só na forma.

**(b) O fluxo comprimido é o mesmo codec, e no começo os mesmos bytes.**
Comparando `BIN/DAT2D.BIN` do WE2002 japonês (81.124 B) com o do PES2 `(EsIt)`
(68.556 B), a partir do byte 8 de cada um:

```
prefixo comum = 2.070 bytes byte a byte idênticos
```

Dois jogos diferentes, de anos diferentes, com 2 kB de fluxo comprimido
idêntico. É o mesmo compressor e, no começo, o mesmo gráfico. A §2 do
`PLAN-FEATURES` já provara que o descompressor do `WECompressor` consome esse
arquivo no lado WE2002; o prefixo o estende ao PES2.

**(c) O `.RA` de áudio começa com um cabeçalho VAB da Sony, idêntico nos dois
discos.** `/SD/W2002J00.RA` e `/SD/PES2000.RA` estão **no mesmo LBA 20000**, e
os 32 primeiros bytes são o mesmo cabeçalho:

```
"VABp"  versão 7  vabid 0  fsize 251.152  programas 4  tones 64
VAGs 29  mvol 127  pan 64
```

O `fsize` de 251 kB num arquivo de 20 MB diz que o `.RA` é **mais de um
banco**. Isto corrige a §5 Fase 14 do `PLAN-FEATURES`, que registra que o
índice do `.RA` não é documentado: o começo dele é um VAB comum, que é.

**(d) Os estádios também batem.** 51 arquivos `GDC_*`/`GRDM_*` em cada jogo,
`GDC_AD.BIN` no **mesmo LBA 12560** nos dois. São TMD, e ficam fora — pelo
motivo do [PLAN-STADIUMS](/docs/PLAN-STADIUMS.md), que é projeto e não
feature. Registrado aqui para não ser redescoberto.

**O que isto muda no custo.** As fases 8 a 14 do `PLAN-FEATURES` não precisam
ser refeitas para o PES2: o formato é o mesmo, e a Fase 8 já está pronta do
lado de cá. O que sobra é a Fase 7 deste plano — verificar, e adaptar onde a
localização europeia multiplicou os arquivos.

**(e) O codec lê os quatro discos — medido em 2026-09-01, pela
[PES2-TASK-26](/docs/tasks/26-codec-lzss.md).** O `tools/pes2/lzss.py` porta o
LZSS do `WECompress.cpp` (crédito e condição no [NOTICE.md](../NOTICE.md)) e
foi apontado para todo `BIN/*.BIN` `form1` das duas releases de PES2 e das
duas imagens de WE2002:

| Disco | contêineres | inteiro | parcial | não é LZSS | blocos |
|---|---:|---:|---:|---:|---:|
| PES2 `(EsIt)` | 208 | **172** | 3 | 33 | 2.153 |
| PES2 `(EnFrDe)` | 210 | **174** | 3 | 33 | 2.195 |
| WE2002 European Deluxe | 177 | **141** | 3 | 33 | 1.842 |
| WE2002 japonês | 195 | **159** | 3 | 33 | 2.027 |
| **total** | **790** | **646** | **12** | **132** | **8.217** |

```
python3 tools/pes2/lzss.py "<a>" "<b>" "<c>" "<d>" --check
python3 tools/pes2/lzss.py "<track1.bin>" --roundtrip
```

Os três verdictos, como a ferramenta os define:

- **inteiro** — um fluxo decodifica exatamente no offset que o cabeçalho de
  (a) nomeia. O codec lê o arquivo, e a regra de largura acha a porta.
- **parcial** — há fluxo, mas não onde o cabeçalho diz. São sempre os mesmos
  três, `GDC_AD`, `GDC_AN` e `GDC_BN`: estádios, que a (d) já põe fora.
- **não é LZSS** — nada decodifica **para um bloco de 1 KiB ou mais**, em
  offset nenhum. O limiar é o `MIN_BLOCK` da ferramenta, e é ele que separa
  este verdicto do primeiro: com 64 em vez de 1024, *todo* arquivo desta
  lista produz bloco. Medido em 2026-09-01 sobre os quatro discos, o menor
  bloco real tem **1.152 B** — nos quatro —, de modo que a **margem sob o
  limiar é de 128 bytes**; `lzss.py --sizes` reimprime a distribuição.
  São 33 por disco, **a mesma lista nos quatro**: os 17 `GRDM_*` e o
  `MODEL.BIN` (estádios e malha, fora por (d)), `ANIME`, `DEMODATA`,
  `EDT_MOD`, `ENDANIME`, e **onze
  `CG*.BIN`** — estes últimos são o achado que a
  [PES2-TASK-27](/docs/tasks/27-conteiner-e-tim.md) tem de explicar, porque a
  §5 Fase 10 do `PLAN-FEATURES` contava com eles como contêiner gráfico.

**Round-trip: 8.217 de 8.217 blocos**, `decompress(compress(x)) == x` nos
quatro discos. O sentido contrário não é exigido e não vale a pena tentar — a
§5c do `PLAN-FEATURES` mediu por quê: o compressor do CARP deixa comentado o
opcode `0xC0..0xFE`, que o da Konami emite, e a saída recomprimida sai sempre
0,2% a 2,0% menor.

**O que fica fora de qualquer fluxo é a tabela de entradas**, não defeito:
registros de 16 bytes — o **primeiro** deles
`00 00 0a 00 00 02 00 01 20 00 80 00 00 00 08 00` —, 15.538 bytes deles
depois do último bloco de `DAT2D.BIN` no PES2 `(EsIt)`. Os quatro primeiros
diferem justamente nos oito bytes iniciais; o que é **comum** aos quatro é
`0a 00` nos bytes 2-3, `20 00 80 00` nos bytes 8-11, e os quatro últimos
crescendo de registro a registro (`0800`, `0e1c`, `1d4c`, `247c` lidos como
dois inteiros de 16 bits little-endian), que é o que se espera de
deslocamento acumulado. É o candidato direto ao `DATA_HEADER` da Fase 10, e é
assunto da PES2-TASK-27; o `lzss.py` mede quantos bytes são, por arquivo, e
não os julga.

Os 15.538 são o que vem **depois do último bloco**, a partir de 53018. A
coluna `outside` do `lzss.py` diz **15.574** para o mesmo arquivo, e a
diferença são os 36 bytes de cabeçalho de contêiner, que também ficam fora de
qualquer fluxo: são duas medidas diferentes, as duas certas.

> Esta frase citava `0f 80 0a 00 20 02 80 01` como o início dos registros até
> a [CORR-PES2-011](/docs/tasks/CORR-PES2-011.md). É o **quarto** deles, em
> 53066 — três registros depois do começo da cauda, em 53018.

**A divergência da §5c, fechada.** Ela dizia que o fluxo de `TEX_00.BIN`
começa em **28**; a varredura de (a) dizia **48**. É **48**, nos quatro
discos: 24, 28, 32 e 44 falham, e falham na primeira distância que aponta para
antes do começo da saída. A linha da §5c foi corrigida no arquivo dela. O
provável motivo de a medição antiga não se reproduzir também ficou medido: na
imagem golden European Deluxe os 105 `TEX_*.BIN` são **Form 2**, e o `iso.py`
recusa lê-los — quem os leu em 2026-08-02 leu com outro fatiamento de setor, o
que casa com o `16.400 = 16.384 + 16` que ela registrava. As outras cinco
linhas daquela tabela **se reproduzem exatamente**.

---

## 2. Ressalva legal

O disco é software comercial da Konami, sem licença de redistribuição. Vale
a mesma disciplina do resto do repositório:

- `roms/` continua **no `.gitignore`**. Nenhum byte do jogo entra no git —
  nem dump, nem trecho extraído, nem tabela copiada literalmente de dentro
  da imagem. O que se versiona é **o mapa** (offset, tamanho, tipo), que é
  fato sobre o formato, não conteúdo dele.
- Trabalhar **sempre sobre cópia**. O editor grava in-place e o Track 1 tem
  466 MB; um `poke` errado sem cópia custa um novo download.
- O repositório **não tem `LICENSE`** e não vai ganhar um por causa deste
  plano — ver [NOTICE.md](../NOTICE.md).

---

## 3. Ferramental

### 3.1 O que já existe na máquina

`cdrdao`, Python 3, ImageMagick, `xdotool`, `ffmpeg`, `Xvfb`, Wine (via
Bottles), Bottles, PCSX2, e as ferramentas deste repositório. Desde
2026-09-01, também `numpy`, `radare2` e `mipsel-linux-gnu-objdump` — ver a
§3.2, que é quem registra a decisão e como invocá-los.

E, em `tools/pes2/`, o que a Fase 0 deixou pronto. Nenhuma delas depende do
`we2002_core` nem do Qt; são Python 3 e shell, e só o `iso.py` é importado
pelas outras:

| Ferramenta | Para quê |
|---|---|
| `iso.py` | `ls`, `extract`, `inject`, `anchors`, `roundtrip`, `negative` |
| `tables.py` | acha, conta e despeja as catorze tabelas de texto da §1.6 |
| `diff_releases.py` | o confronto entre as duas releases da §1.12 |
| `memcard.py` | alinha o memory card contra o disco — as fronteiras de elenco da §3.3 |
| `team_map.py` | alinha as oito listas de nome de time entre si — §6.1 |
| `poke.py` | grava um nome de time em **todas** as cópias, e varre o disco atrás do que sobrou — §6.1, §6.2 |
| `player_map.py` | relaciona as duas tabelas de nome de jogador |
| `strings_inventory.py` | varre o disco por texto e agrupa em blocos densos |
| `ofs_map.py` | os 69 `OFS_*` do WE2002 como `(arquivo, offset relativo)` — §1.4 |
| `faq_check.py` | confere a `docs/PES2-NOMES.md` contra o disco e contra os dois FAQs |
| `selftest.py` | disco sintético de 24 setores; é o `ctest -R pes2_selftest` |
| `check_image.py` | roda tudo que precisa de imagem; é o `ctest -R pes2_image` |
| `run_duckstation.sh` | sobe o jogo no `:98`, isolado, e imprime PID e janela |
| `boot_check.sh` | mede que ele botou de verdade — §3.4 |
| `faq2md.py` | converte os FAQs de terceiros em Markdown |

### 3.2 O emulador: **resolvido em 2026-08-30**

O plano listava o emulador como bloqueante das Fases 2–6. Ele já está na
máquina, instalado pelo usuário em 2026-08-29:

| | |
|---|---|
| binário | `~/Applications/DuckStation-x64.AppImage` (não é Flatpak, e não está no `PATH`) |
| dados | `~/.local/share/duckstation/` |
| BIOS | **quatro** — `scph1001`, `scph5500`, `scph5501`, `scph7502` |
| biblioteca | `RecursivePaths = /home/ingmar/ROMs/psx`, onde a pasta `(EsIt)` está |
| já rodou | sim — há `gameicons/SLES-03957.png` e um memory card gravado |

Isso destrava o oráculo da §4.1 e, de brinde, a alavanca da §4.2.3 já
tem munição: ver a §3.3.

O que faltava — `numpy` e um desmontador MIPS — **foi instalado em
2026-09-01** (PES2-TASK-01), a pedido do dono da máquina:

| Ferramenta | Versão | Como entrou |
|---|---|---|
| `numpy` | 2.5.2 | `pip3 install numpy`, no Python 3.13 do `mise` |
| `radare2` | 5.5.0 | `apt-get install radare2` |
| `mipsel-linux-gnu-objdump` | 2.42 | `apt-get install binutils-mipsel-linux-gnu` |

**Ghidra ficou de fora, e a razão é escrita:** não está nos repositórios do
Zorin 18.1, o `.zip` oficial pesa ~1,2 GB e exige JDK 21 — a máquina tem o 17.
O que ele traz a mais é o **decompilador**; para *ler uma rotina de acesso a
tabela*, que é o uso previsto na §4.2.4, o par acima basta. Se a Fase 4 pedir
decompilação de verdade, instalar Ghidra é uma decisão de meia hora tomada
naquele momento, e não antes.

São **dois** desmontadores de propósito, e não é redundância: o `objdump` é
determinístico e roteirizável — a saída entra em `diff` sem esforço —, e o
`radare2` é o que se usa para navegar, seguir referência cruzada e achar quem
lê um endereço.

**O overlay não é ELF, e os dois precisam da base explícita.** O executável de
boot é `PS-X EXE`: cabeçalho de 2.048 B, `t_addr` em `+0x18` e `pc0` em `+0x10`
— no `(EsIt)` valem `0x80010000` e `0x80010008`. Medido em 2026-09-01, os dois
comandos abaixo desmontam o mesmo laço de zeragem de BSS na entrada:

```sh
# objdump: --adjust-vma = t_addr − 0x800, para o cabeçalho não deslocar tudo
mipsel-linux-gnu-objdump -D -b binary -m mips:3000 -EL \
  --adjust-vma=0x8000f800 --start-address=0x80010000 SLES_039.57

# radare2: mesma conta no -m; ele reconhece PS-X EXE e já marca o entry0
r2 -qq -a mips -b 32 -e cfg.bigendian=false -m 0x8000f800 \
   -c 's 0x80010008; pd 6' SLES_039.57
```

**O `-EL` do `objdump` é redundante aqui, e quem mente é o `-EB`.** O
`mipsel-linux-gnu-objdump` 2.42 já tem alvo `elf32-tradlittlemips`, então
omitir o `-EL` não muda uma instrução sequer — medido em 2026-09-01, 1.017
linhas com e sem ele, mnemônicos idênticos; o que muda é só a coluna de palavra
crua (`03e00008` contra `0800e003`). Vale mantê-lo explícito porque o mesmo
comando com um `objdump` de alvo big-endian sai errado, e é o **`-EB`** que
produz a saída plausível-e-falsa: ele não falha, decodifica `j 0x8003800c` e
`bltz s4,0x800108fc` sobre esse mesmo laço de BSS, alvo de salto que parece
endereço e não é.

Os demais overlays (`SELECT.BIN` e irmãos) **não** têm esse cabeçalho: são
código realocado, e a base sai de onde o carregador os põe, não do arquivo.
Descobri-la é trabalho da Fase 4 — até lá, desmontar overlay com base chutada
produz alvo de `jal` que parece endereço e não é.

PCSX2 **não serve** — é PS2.

### 3.3 O memory card já existente, e o que ele entrega

`~/.local/share/duckstation/memcards/…(Es,It)_1.mcd` — 128 KiB, formato
cru de cartão PSX, o mesmo `.mcr` que a §4.2.3 pede. Três slots ocupados:

| Slot | Nome | Tamanho | O que é |
|---|---|---|---|
| 1–2 | `BESLES-03957PES-OPT` | 16 KiB | **as opções e a tabela de nomes editável** |
| 3 | `BESLES-03957PES-D4A` | 8 KiB | uma formação salva |

Os dois nomes de arquivo confirmam as strings `LES-03957PES-OPT` e
`LES-03957PES-D0A` já vistas em `SELECT.BIN` — o jogo monta o nome com um
dígito variável.

**O título do save está em Shift-JIS de largura dupla, e o
`KanjiToAscii` do WE2002 o decodifica sem uma linha de adaptação:**
`ProEvolutionSoccer2 OPTION FILE` e `ProEvolutionSoccer2 FORMATION1`.
Mais uma confirmação da §1.4 — é a mesma engine.

#### A tabela de nomes do cartão

Dentro do `PES-OPT`, no offset **516**, começam **1.242 registros de 10
bytes fixos**, preenchidos com `NUL` à direita. E 1.242 = **54 × 23**
exato: as 54 seleções reais, 23 jogadores cada. Bate com o que o FAQ do
BigCj34 diz — só jogador de seleção é editável.

Os 1.242 nomes existem todos em `SELECTC.BIN`. Isso torna o cartão uma
**chave de alinhamento**: cada bloco de 23 do cartão é um elenco
rotulado, e procurá-lo no disco dá a fronteira exata daquele elenco.

#### As fronteiras de elenco, fechadas

Foi o que se fez, e desde 2026-08-30 com ferramenta versionada:

```
python3 tools/pes2/memcard.py "<card.mcd>" "<track1.bin>" --check
```

Dos 54 elencos, **os 54 casam exatos**, 23 de 23 nomes:

| | |
|---|---|
| **49** | em `SELECTC.BIN`, offsets de 19344 a 30640, **em ordem reversa** |
| **5** | no executável de boot, **em ordem direta** — França @286100, Alemanha @287480, Noruega @287940, Argentina @295300, Austrália @296910 |

Isso resolve o que a §1.7 deixou em aberto: o tamanho de elenco é 23 e as
fronteiras agora são medidas, não estimadas.

**Correção de 2026-08-30:** esta seção dizia 49 + 2 exatos e três
parciais — Noruega, Argentina e Austrália, "19, 15 e 21 dos 23 nomes". Os
três são exatos. A varredura da vez procurava no executável só onde a
França e a Alemanha já haviam aparecido; a tabela de 10 B de lá tem
**1.449 entradas** (§1.5), e os três estavam nela o tempo todo. Não havia
par editado/original nenhum a colher, e a alavanca da §4.2.3 continua
inteira — só não foi ela que aconteceu aqui.

**E há uma razão mecânica para serem exatamente esses cinco.** Como a
§1.5 mostra, `SELECTC.BIN` é um pool deduplicado: cada nome aparece uma
vez. Os cinco elencos que só casam no executável são, cada um, um elenco
que contém **um** jogador cujo nome se repete em outro elenco —

| Elenco | Índice no executável | Nome repetido |
|---|---:|---|
| França | 138–160 | `Petit` |
| Alemanha | 276–298 | `Butt` |
| Noruega | 322–344 | `Sorensen` |
| Argentina | 1058–1080 | `Zanetti` |
| Austrália | 1219–1241 | `Moore` |

— e no pool essas 23 vagas viram 22, então deixam de ser um trecho
contíguo. Nada está faltando; o pool só não repete. Os outros 45 dos 50
repetidos ficam numa janela de 46 vagas, que é 2 × 23: os dois elencos
*elite*, cujos membros já estão, por construção, em alguma seleção.

#### A ordem de armazenamento é por tabela, não do jogo

Os 49 de `SELECTC.BIN` casaram **todos em ordem reversa** à do cartão, e
nenhum em ordem direta. Os 5 do executável casaram todos em ordem
**direta**.

Ou seja: `SELECTC.BIN` guarda o elenco de trás para frente e o executável
de frente para trás. **A ordem é propriedade da tabela.** Um leitor que
assuma uma delas inverte 23 jogadores por time em metade das tabelas — e
o erro é invisível, porque a lista continua parecendo um elenco.

A inversão vale para a tabela inteira, não só para os elencos: as 1.449
entradas de 10 B do executável são a mesma faixa das 1.399 de
`SELECTC.BIN`, do fim para o começo.

### 3.4 Confirmar antes de começar

| | Estado |
|---|---|
| 1. O jogo dá boot a partir do `.cue` multi-track | **verificado em 2026-08-30, no `:98`**, e reverificável: `tools/pes2/boot_check.sh` |
| 2. O emulador tem *save state* e dump de RAM | disponível; nenhum feito ainda |
| 3. O emulador aceita cartão em `.mcr` | **sim** — o `.mcd` do DuckStation é o mesmo formato cru de 128 KiB, e já foi lido (§3.3) |
| 4. Cópia do Track 1 no scratchpad | **feita** — as oito faixas, 571 MiB |

Tudo isso roda no **`DISPLAY=:98`**, por decisão do usuário em 2026-08-30,
que é a regra do [CLAUDE.md](../CLAUDE.md) sem exceção para este projeto.

A receita está em **`tools/pes2/run_duckstation.sh`**, e não em histórico
de shell, porque quase nada nela é adivinhável — ver a §6.11. Ele imprime
o PID e o id da janela, prontos para um script de direção.

O `run_duckstation.sh` usa um `XDG_DATA_HOME` **isolado**: configuração
própria, cartão de memória próprio, e só o BIOS emprestado por link
simbólico. O `settings.ini` e o memory card do usuário nunca são escritos
— o cartão dele é dado de save real e é insubstituível.

#### A evidência de que ele bota, e por que ela é medida e não guardada

"Dá boot" foi escrito depois de alguém olhar uma vez. Afirmação que
ninguém consegue repetir é lembrança, não verificação — a mesma regra que
o `CLAUDE.md` aplica aos golden. `tools/pes2/boot_check.sh` refaz a
afirmação e mede três coisas:

1. a janela aparece, com o tamanho que o emulador diz;
2. o quadro **não é chapado** — emulador morto e emulador carregando são
   idênticos num log e opostos num desvio-padrão;
3. dois quadros separados por alguns segundos **diferem**, que é o que
   separa "rodando" de "travado no primeiro quadro".

Medido em 2026-08-30 sobre a cópia de trabalho de `(EsIt)`, janela de
**800×655** no `:98`: quadro 1 com desvio-padrão 0,228, quadro 2 com
0,243, e **259.994 de 524.000 pixels diferentes** entre os dois. Aos ~2
min de execução a tela é a partida de demonstração, em 3D de tempo real.

Os quadros **não entram no repositório**: são de um jogo comercial, e
seguem a mesma regra de `roms/` e dos FAQs. O que entra é o script e o
número.

Se for preciso comparar contra um quadro de referência, `PES2_REFERENCE`
aponta um PNG de fora do repositório e `PES2_TOLERANCE` diz quanto pode
diferir. Medido nos dois sentidos: contra o quadro de outra corrida no
mesmo instante do vídeo de abertura, 8.178 de 76.800 pixels diferem
(10,6%) e passa; contra o quadro da partida de demonstração, 58.451
(76,1%) e falha. O default de 35% fica entre os dois.

---

## 4. Estratégia

### 4.1 A diferença que define tudo: **não há oráculo**

O `newWe2002` teve o `ed.exe`; o `wte/` teve o `we-team-editor.exe`. Os dois
puderam ser verificados por comparação byte a byte contra um programa que
sabia a resposta. **Para o PES2 não existe editor conhecido.**

Isso proíbe a forma de teste que sustenta os outros dois projetos e obriga a
outra: **o oráculo é o próprio jogo, rodando.** Um campo só está mapeado
quando um `poke` nele muda o que a tela mostra, do jeito previsto. É mais
lento, é manual, e é o motivo de o emulador estar na lista de bloqueantes.

### 4.2 Quatro alavancas, da mais barata para a mais cara

1. **Empréstimo do WE2002** (§1.4). Mesmo arquivo, mesmo tipo de conteúdo,
   offset relativo próximo. Cobre provavelmente a maior parte dos campos e
   custa quase nada.
2. **Diferencial entre as duas releases.** `(EsIt)` e `(EnFrDe)` são o mesmo
   jogo com idiomas diferentes. O que difere entre elas é texto localizado;
   **o que é igual e não é código é candidato a dado de jogo.** Um `cmp` por
   arquivo separa os dois conjuntos de graça.
3. **Diferencial de memory card.** O Edit Mode do PES2 grava o time editado
   no cartão. Editar *um* atributo de *um* jogador, salvar, e comparar dois
   `.mcr` isola o campo — com rótulo, porque eu sei o que editei. O layout
   do cartão não é o do disco, mas a **ordem dos campos dentro do registro
   costuma ser a mesma**, e isso dá a estrutura do registro de jogador quase
   pronta. (O editor do Obocaman já importa `.mcr` do WE2002 — ver
   [PLAN-WTE-LAZARUS.md](/docs/PLAN-WTE-LAZARUS.md).)
4. **Desmontagem do MIPS**, para os campos que a estatística não resolver.
   É o último recurso, e é o mais caro.

### 4.3 Ordem: texto antes de número

Nome de time e de jogador já estão localizados e são **auto-rotulados** —
eu leio `PIEMONTE` e sei o que é. Eles dão, de graça, a **ordem canônica das
entidades**: qual é o time 0, o time 1, o jogador 0. Toda tabela numérica
paralela vai estar nessa mesma ordem, e é assim que se identifica uma:
`N` registros de tamanho constante, `N` igual ao número de nomes já contado.

Por isso a Fase 2 fecha o inventário de texto inteiro antes de a Fase 3
tocar num byte numérico.

### 4.4 O que é gerado e o que é escrito à mão

Como no `newWe2002`: **o mapa é o fonte**. `pes2_map.json` é escrito à mão
(ou por ferramenta de descoberta) e revisado; os headers, tabelas e código
de leitura/gravação saem dele por gerador, com `--check` no `ctest`, para
que editar o gerado falhe em teste. Nunca o contrário.

---

## 5. Fases

### Fase 0 — Infra

- Instalar emulador + debugger; confirmar boot (§3.4). **Feito** — o
  DuckStation já estava instalado (§3.2) e o boot foi verificado no
  `:98`, com a receita versionada em `tools/pes2/run_duckstation.sh`.
- `tools/pes2/iso.py`: listar, extrair e **reinjetar** arquivo do ISO
  preservando setor e cauda EDC/ECC. Reinjeção é o que permite o ciclo de
  `poke`; sem ela cada teste é edição manual em hexeditor. **Feito** —
  `ls`, `extract`, `inject`, `anchors`, `roundtrip`, `negative`.
- Guarda de round-trip: extrair todos os 252 arquivos e reinjetá-los sem
  mudança tem de devolver o `.bin` **byte a byte idêntico**. Se não devolver,
  a ferramenta está errada e tudo o que vier depois é ruído. **Feito e
  verde**, com controle negativo — ver §5.1.

#### 5.1 O que a Fase 0 mediu

`python3 tools/pes2/iso.py roundtrip <track1.bin>` copia a imagem, lê e
regrava os **244** arquivos legíveis e compara: **byte a byte idêntico**.

Guarda verde não vale nada sem prova de que sabe ficar vermelha, então o
mesmo caminho de escrita é exercitado com um controle negativo — e ele
também é comando, não prosa:

```
python3 tools/pes2/iso.py negative <track1.bin> --tmpdir <~450 MiB livres>
```

Trocar o `P` de `PIEMONTE` por `X` em `SELECT.BIN` muda **exatamente um
byte** em toda a imagem de 445 MiB, no offset absoluto **2002800** — que é
o que a aritmética de setor prevê, e ele cai dentro da área de dados
(`24..2071`), com cabeçalho e cauda intactos. O comando calcula o offset
esperado a partir do LBA do arquivo e confere contra onde o byte de fato
se mexeu, então ele falha tanto se a escrita errar quanto se a aritmética
mudar.

O caso não é trivial: o registro fica no offset 3272 de um arquivo que
começa no LBA 850, então **atravessa a fronteira de setor** — 3272 ÷ 2048
= LBA 851, resto 1224, mais os 24 de cabeçalho = 1248. É exatamente a
armadilha da §6.3, e ela está coberta.

O `anchors` resolve os oito marcadores da §1.13 nas duas releases, cada um
ocorrendo uma única vez.

##### O que roda sem imagem, e o que precisa dela

O `ctest` deste repositório conhece os dois casos desde 2026-08-30:

| Teste | Precisa de | O que faz |
|---|---|---|
| `pes2_selftest` | nada | monta um disco sintético de 24 setores em `/tmp` e exercita a aritmética de setor, o par Form 1 × Form 2, o caso `outside` e as **três recusas** do `write_file` — crescer, misto, fora da trilha |
| `pes2_image` | `WE2002_PES2_IMAGE` | âncoras (§1.13), contagens e digests (§1.6), o alinhamento das oito listas de time (§6.1), a relação entre as duas tabelas de jogador, e a `docs/PES2-NOMES.md` contra o disco. Com `WE2002_PES2_IMAGE_B`, `_CARD` e `_TMPDIR` acrescenta o diff de releases (§1.12), o alinhamento de cartão (§3.3), o controle negativo e o `poke` sobre o conjunto de cópias (§6.1) |
| `pes2_boot` | `PES2_IMAGE`, DuckStation, o `:98` | o boot medido da §3.4, ~90 s |

Sem a variável, os dois últimos se reportam **skipped**, como já fazem os
golden do `newWe2002`. O `pes2_boot` nunca roda em CI, pelo mesmo motivo
que o `golden` não roda.

#### 5.2 Oito arquivos que a ferramenta não toca, e por quê

O levantamento da §1.3 contou 252 arquivos. Nem todos são legíveis a
partir do Track 1, e isso é achado, não defeito:

| Arquivos | Estado | Motivo |
|---|---|---|
| 244 | `form1` | setores Form 1, 2.048 B de dados — tudo que interessa |
| 1 | `form2` | `/MOVIE/ISS_2002.STR`: setores Form 2, 2.324 B e sem ECC |
| 7 | `outside` | `/SD/DA/*.DA`: LBA 198606 em diante, **depois do fim do Track 1** (198456 setores) |

Os sete `.DA` moram nas **trilhas de áudio**. O diretório ISO cobre o
disco inteiro e por isso nomeia arquivos que, num dump multi-track, estão
em *outro arquivo*. Uma ferramenta que não confira isso lê depois do fim
do `.bin` e recebe menos bytes do que pediu — foi o primeiro defeito que a
guarda pegou. O `iso.py` classifica cada arquivo em `form1`/`form2`/
`outside` e recusa os dois últimos em vez de adivinhar.

Nenhum dos oito carrega dado de jogo: são vídeo e áudio.

### Fase 1 — Diferencial barato

- `cmp` arquivo a arquivo entre `(EsIt)` e `(EnFrDe)`; classificar cada um
  em *idêntico* / *difere*. **Feito, e versionado** —
  `tools/pes2/diff_releases.py`, saída em
  [/docs/samples/pes2-diff-releases.md](/docs/samples/pes2-diff-releases.md).
  202 idênticos, 27 diferem, 7 fora do Track 1 (§1.12). A classificação do
  *porquê* também está feita: 19 dos 27 mudam de tamanho e são texto
  localizado; os outros 8 mantêm tamanho e mudam conteúdo.
- Olhar os oito de tamanho fixo. **Feito, e a resposta é não** —
  `diff_releases.py --explain` classifica cada palavra que difere:

  | Arquivo | Palavras que diferem | Relocação |
  |---|---:|---:|
  | `GAME.BIN` | 21.737 | 99,8% |
  | `SELECT4.BIN` | 4.337 | 99,8% |
  | `ENTER.BIN` | 1.749 | 99,6% |
  | `PKMATCH.BIN` | 174 | 100% |
  | `TRAINING.BIN` | 94 | 100% |
  | `MOVIE.BIN` | 64 | 100% |

  São overlays de código MIPS, e quase toda diferença é **a mesma rotina
  realocada**: alvo de `j`/`jal`, imediato de `lui`/`addiu`, ou ponteiro
  `0x800xxxxx`, deslocados por um punhado de constantes — **+3176** domina.
  O resíduo é de dezenas de palavras, e o pouco que tem significado é
  constante de código (cinco `slti` de 4 para 2 em `SELECT4.BIN`), não
  banco de dados. Os dois restantes são o que aparentavam: `FNOTE_G.BIN`
  é texto alemão reescrito com o mesmo tamanho, e `SYSTEM.CNF` é o nome do
  executável. **Nenhum dos oito guarda dado de jogo diferente.**
- Mapear os 69 `OFS_*` do WE2002 para `(arquivo, offset relativo)`.
  **Feito** — `tools/pes2/ofs_map.py`, tabela em
  [/docs/samples/pes2-ofs-map.md](/docs/samples/pes2-ofs-map.md). 69 de 69
  localizados, em 13 arquivos; ver a §1.4.
- Saída: `docs/samples/pes2-diff-releases.md` **(feita)**, a tabela de
  âncoras **(feita — §1.13, e `tools/pes2/tables.py`)** e
  `docs/samples/pes2-ofs-map.md` **(feita)**.

**A Fase 1 está fechada.**

### Fase 2 — Inventário de texto

- Varredura de string em todos os arquivos, com classificação. **Feita** —
  `tools/pes2/strings_inventory.py`, saída em
  [/docs/samples/pes2-strings.md](/docs/samples/pes2-strings.md).

  Ranquear arquivo não serve: `SELECT.BIN` são 216 kB de código MIPS com
  uma ilha de 6 kB de tabela dentro, e some abaixo de qualquer arquivo
  uniformemente ruidoso. A ferramenta agrupa os trechos em **blocos
  densos**, que é a forma que uma tabela tem vista de fora, e ranqueia os
  blocos: 171.161 trechos em 217 arquivos, **281 blocos**.

  Duas armadilhas de medição que valem registro. Os `SD/*.RA` de narração
  são áudio comprimido e produzem dezenas de milhares de trechos
  "imprimíveis" por acaso; a ferramenta pontua cada arquivo contra o que o
  acaso preveria e trata como ruído o que não passa de 4×. E um nome curto
  em caixa mista cai em "texto de interface" se não houver balde para ele,
  o que apagou o achado abaixo na primeira corrida.
- **Achado que abre a Fase 3:** há **mais nomes** em `SELECTC.BIN` do que
  o pool da §1.6. Depois do fim dele (30853) vêm mais 25 blocos de nome,
  ~2.000 trechos, de 31552 a cerca de 50000 — `Tomazi`, `Navaji`,
  `Davinno`, `Beckenboer`, `Lupateli`. Nenhum está entre os 1.399. O que
  são, e a que time pertencem, é trabalho da Fase 3.
- Fechar **contagem e ordem** de cada tabela. **Feito para as catorze**
  (§1.6), com contagem e digest reconferidos por ferramenta.
- Confirmar as cópias (§1.5) e procurar as que faltam. **Feito** — havia
  uma nona, em caixa mista no `REPLAYS.BIN`, e a correspondência entre as
  oito listas de nome de time (§6.1) está em
  [/docs/samples/pes2-team-lists.md](/docs/samples/pes2-team-lists.md),
  gerada por `tools/pes2/team_map.py`. Ver a §6.1.
- **Falta:** o primeiro `poke` de validação — renomear `PIEMONTE`, dentro
  do slot, em **todas** as cópias, e ver o nome novo no emulador em todas
  as telas. É esse teste que fecha a fase, não a varredura, e ele é o
  único item que sobrou dela.

### Fase 3 — O registro de jogador

*(Começou de graça: a §3.3 já localizou a tabela de nomes do cartão, as 54
fronteiras de elenco e três times com nome divergente entre cartão e
disco.)*

- Diferencial de memory card (§4.2.3): um atributo por vez, `.mcr` antes e
  depois, isolar o byte e o bit.
- Dump de RAM com o jogo no menu de edição; achar o array carregado e
  casá-lo com o bloco do disco por assinatura de conteúdo.
- Resolver a questão dos 624 candidatos de 16 bits da §1.10: existe índice
  para o bloco de nomes, ou o jogo o percorre linearmente?
- Saída: estrutura do registro de jogador com campo, deslocamento, largura
  em bits e domínio.

### Fase 4 — O resto do banco

Times (elenco, formação, cores, uniforme, bandeira), Master League
(custos, slots, elencos), na ordem em que a §1.4 der âncora. Cada campo
fecha com `poke` verificado no emulador — nenhum entra no mapa "por
analogia".

### Fase 5 — `pes2_map.json` e o leitor

- Consolidar tudo num mapa único, com as cópias declaradas por campo.
- Gerador que produz o header de offsets e o código de leitura/gravação.
- Round-trip headless: ler tudo, regravar sem editar, `cmp` zero.

### Fase 6 — Editor

Só aqui se decide linguagem e UI. As três condições da §0 são o portão, e a
Fase 7 é a quarta: a lista de telas que a PES2-TASK-30 entrega.

### Fase 7 — Assets do disco

**Corre em paralelo com as Fases 3 a 5**, não depois. Nada aqui depende do
registro de jogador nem do mapa, e as tasks 26, 27 e 31 são **leitura pura** —
sem emulador, sem cartão, sem imagem gravável. São o trabalho barato que
continua quando a Fase 2 trava.

O que a §1.14 já entrega, e que esta fase gasta em vez de redescobrir: o
formato é o do WE2002, o `PLAN-FEATURES` já o descreve fase a fase, e a
camada ISO9660 (Fase 8 de lá) já está pronta e verde no `iso.py`.

- **Codec LZSS** ([PES2-TASK-26](/docs/tasks/26-codec-lzss.md)). Descomprimir
  os contêineres das duas releases — 208 e 210, §1.14(e); round-trip
  `decompress(compress(x)) == x`. Decide a divergência do `TEX_00` da §1.14.
- **Contêiner e TIM** ([PES2-TASK-27](/docs/tasks/27-conteiner-e-tim.md)).
  Lista de entradas, `DATA_HEADER`, 4 e 8 bpp com CLUT, export PNG. É a de
  risco mais alto — o único ponto onde o formato ainda é hipótese. Também é a
  via provável para as bandeiras da Fase 4: os quatro `OFS_FLAG_COLOURS_*`
  caem em `BIN/DAT2D.BIN` (§1.4).
- **Cópias de idioma**
  ([PES2-TASK-28](/docs/tasks/28-t-name-copias-de-idioma.md)). `T_NAME_I` e
  `T_NAME_S` são byte a byte idênticos; gravar um só repete a §6.1 uma camada
  acima. Varrer o conjunto, nunca declará-lo.
- **Gravação** ([PES2-TASK-29](/docs/tasks/29-gravacao-de-asset.md)).
  Fit-or-fail, recompressão só do editado, e a decisão de EDC/ECC entre a §6.7
  daqui e a §5(b) de lá.
- **Fechamento** ([PES2-TASK-30](/docs/tasks/30-fechamento-fase-7.md)). Os
  três números por eixo, e a lista do que a UI tem de cobrir. **É portão da
  PES2-TASK-22.**
- **Áudio** ([PES2-TASK-31](/docs/tasks/31-audio-ra-e-vag.md)). VAB, VAG,
  ADPCM. **Independente e fora do portão** — dá para parar antes dela sem
  perder o salto de valor.

---

## 6. Armadilhas conhecidas

### 6.1 Uma cópia gravada é pior que nenhuma — e nenhuma cópia é cópia

A §1.5 mostra a mesma tabela em oito e três arquivos. Um editor que grava
só a de `SELECT.BIN` produz um jogo que mostra o nome novo na seleção de
time e o velho no replay e no resultado. **Toda gravação é para o conjunto
de cópias**, e o mapa declara o conjunto.

**E o conjunto não se declara: varre-se.** Medido em 2026-09-01, na
PES2-TASK-02: gravar as cinco cópias que este documento listava até
então deixava o nome velho vivo em **três** outros lugares. O `poke.py`
varre todo arquivo `form1` atrás do nome antigo depois de planejar a
gravação, e **recusa** se sobrar registro que nenhuma tabela conhece. Foi
essa varredura que achou as três.

**A armadilha de verdade, porém, é a palavra "cópia".** Medido em
2026-08-30 e reconferido em 2026-09-01: as oito listas de nome de time
têm 106, 99, 95, 94, 123, 32, 99 e 99 entradas, e as diferenças não são de
recorte, são de **conteúdo**:

| Lista | n | O que ela tem que as outras não |
|---|---:|---|
| `SELECT.BIN` @3128 | 106 | `MASTER DATA` e `? ? ? ?` de cabeçalho, mais os 7 *classic*, `WORLD ALLSTARS` e `EURO ALLSTARS` no fim |
| `SELECTC.BIN` @16576 | 99 | abre com `Belarus`, `Georgia`, `Uzbekistan`, `Iceland` — quatro nações que nenhuma outra lista traz |
| `ENDING.BIN` @1256 | 95 | só os 32 fictícios, as 7 seleções temáticas, as 2 *elite* e as 54 reais |
| `RESULT.BIN` @524 | 94 | no lugar das 7 temáticas e das 2 *elite*, traz 6 *classic* e as 2 *allstars* |
| `REPLAYS.BIN` @11380 | 123 | `Edit`, `Free`, `Default` e o elenco de nações inteiro do modo de edição |
| `SELECT.BIN` @33188 | 32 | **só** os 32 clubes fictícios; para em `Aragon` e emenda nas strings de interface localizadas |
| `SELECT3.BIN` @9448 | 99 | a lista de `SELECTC.BIN` outra vez, digest por digest |
| `SELFORM.BIN` @460 | 99 | idem, no overlay de formação |

Ou seja: o índice 34 de `SELECT.BIN` é `ALWAYS ARGENTINA` e o índice 34 de
`RESULT.BIN` é `Classic Brazil`. **Casar duas listas por índice grava no
time errado**, e o resultado — um nome plausível no lugar de outro — não
parece defeito em tela nenhuma. O mapa da Fase 5 tem de guardar, por
cópia, a lista **e a correspondência**, e a correspondência tem de sair de
comparação de conteúdo, nunca de posição.

### 6.2 Registro de tamanho variável não aceita nome maior

Ver §1.10. Até que exista prova de índice reconstruível, o editor **trunca**
em vez de deslocar. Truncar é o comportamento herdado do WE2002 e é o
seguro.

### 6.3 A fronteira de setor continua mordendo

Um registro que atravessa o fim dos 2.048 B de dados salta 304 bytes no
offset absoluto. Foi a causa dos três `OFS_TEAM_NAME_1`, `_END` e `_A` do
WE2002. **Toda ferramenta trabalha em offset relativo ao arquivo** e só
converte para absoluto na hora de gravar; misturar os dois é como se erra.

### 6.4 Multi-track: o offset é dentro do Track 1

Ver §1.1. Uma ferramenta que abra o `.cue` e concatene as trilhas produz
offsets que não existem em lugar nenhum.

### 6.5 O diretório ISO nomeia arquivo que não está no Track 1

Ver §5.2. Os sete `/SD/DA/*.DA` começam no LBA 198606 e o Track 1 acaba
em 198456. Ler por LBA sem conferir o limite devolve menos bytes do que se
pediu, em silêncio, e o erro só aparece três camadas adiante. `iso.py`
levanta `OutsideTrack`.

### 6.6 Offset constante entre releases grava lixo

Ver §1.12. Quatro das sete cópias de tabela estão no mesmo offset em
`(EsIt)` e `(EnFrDe)`, e três não. Um mapa constante calibrado numa das
duas parece funcionar na outra — até tocar `SELECTC.BIN`, deslocado
8.604 bytes. Ancorar por marcador (§1.13) é o que evita isso.

### 6.7 Não recalcular EDC/ECC, e não "consertar"

Preservar os 280 B de cauda. O jogo não confere; corrigir muda bytes que
nenhum teste espera e destrói a comparação de round-trip.

### 6.8 Os nomes licenciados não estão lá

Ver §1.9. Procurar `JUVENTUS` e concluir "está criptografado" custou uma
varredura de delta na imagem inteira. A release europeia é **inteiramente
fictícia nos clubes**; as seleções, essas, têm nome real.

### 6.9 Não estender o `we2002_core` para PES2

O core está verificado byte a byte contra o `ed.exe` em dois níveis. Um
ramo de "que jogo é este" dentro dele põe em risco a única coisa
verificada do repositório, em troca de reuso de umas poucas funções. Se
algo tiver de ser compartilhado, que seja copiado com atribuição no
comentário.

### 6.10 Regra do `:98` vale aqui também

Emulador é GUI, e roda no `DISPLAY=:98` — **inclusive a sessão de
mapeamento manual**, decidido pelo usuário em 2026-08-30. Não há exceção
de `:1` para este projeto.

### 6.11 Nove armadilhas ao dirigir o DuckStation

Todas medidas em 2026-08-30, todas resolvidas dentro do
`tools/pes2/run_duckstation.sh`. Estão aqui porque o sintoma de cada uma
aponta para o lugar errado.

1. **O AppImage não está no `PATH`** e não responde a `--help`. É `-help`,
   com um traço só.
2. **Um diálogo pede para criar atalho de lançador** na primeira execução
   com um `XDG_DATA_HOME` novo, e **bloqueia o boot**. Parece o emulador
   travando.
3. **Não existe `-renderer` na linha de comando.** Sem GPU no Xvfb, o
   `Renderer = Software` tem de ir para o `settings.ini`.
4. **Um `settings.ini` escrito à mão não tem binding nenhum**, e o
   DuckStation não cria os de teclado sozinho. Toda tecla é descartada em
   silêncio e o jogo fica no laço de atração para sempre — parece que o
   `xdotool` não funciona. (A configuração do usuário desta máquina só tem
   binding de gamepad SDL, então copiá-la não resolve.)
5. **A janela nasce fora da tela.** Sem window manager ninguém a posiciona,
   e ela escolheu `x=2480` num display de 1280. O `import` falha com
   `Resource temporarily unavailable`, que é a mesma mensagem de janela
   obscurecida por modal — e manda investigar a coisa errada.
6. **Uma instância morta ainda responde ao `xdotool search`.** Capturar
   por nome pega a janela velha e devolve quadro preto. Casar pelo
   `_NET_WM_PID` e conferir se o processo vive.
7. **`pkill -f DuckStation` mata o próprio shell**, porque o padrão casa
   com a linha de comando de quem o executa. Matar por PID.
8. **`SIGTERM` deixa o DuckStation parado num "Confirm Exit"** para
   sempre, mesmo com `ConfirmPowerOff = false`. É `kill -9`.
9. **O AppImage roda como `AppRun`, não como `DuckStation-x64`.** Um
   `pgrep -x DuckStation-x64` não casa com nada, e a limpeza de instância
   anterior vira no-op — cada execução deixa a anterior viva. O sintoma
   aparece longe da causa: janelas órfãs no `:98` que nenhum processo
   *aparentemente* sustenta, e uma captura que pega o jogo errado. Casar
   os dois nomes, conferir pelo `/proc/<pid>/cmdline`, e nunca matar o
   próprio script.

   Duas caudas disso, medidas ao consertar: o AppImage **deixa a
   montagem FUSE** em `/tmp/.mount_Duck*` quando morre por `kill -9`; e
   **desmontar antes de o processo soltar o squashfs falha em silêncio**,
   deixando o mount para trás. Esperar a morte, depois desmontar, com
   retentativa. O `run_duckstation.sh --kill` faz isso e é o jeito certo
   de encerrar.

---

### 6.12 Asset também tem conjunto de cópias — e ele é por idioma

A §6.1 vale para as tabelas de texto. Vale igual para os assets, e o caso mais
puro está medido: `/BIN/T_NAME_I.BIN` e `/BIN/T_NAME_S.BIN` têm 62.196 bytes
cada e são **byte a byte idênticos**. O jogo escolhe por idioma.

Gravar um e deixar o outro produz um disco que parece certo — para quem joga
no idioma que foi gravado. O modo de falha é o mesmo da §6.1, com o agravante
de ser **invisível na verificação** se o roteiro do emulador não trocar de
idioma.

Os outros pares que a §1.4 lista têm de ser tratados do mesmo jeito:
`DAT2D_I`/`DAT2D_S`, `DATSEL_I`/`DATSEL2I`/`DATSEL3I`, `LC_*`,
`FNOTE_{G,I,S}`. E como na §6.1, **o conjunto se varre, nunca se declara**.

### 6.13 O cabeçalho de contêiner tem largura variável — 16 larguras medidas

Não existe "cabeçalho de 8 bytes". O que existe é um array de ponteiros de RAM
cuja **contagem é propriedade do arquivo**: 0 palavras em `DEMODATA.BIN`, 2 em
`DAT2D.BIN`, 12 em todo `TEX_*`, 204 em `ANIME.BIN` — dezesseis larguras
distintas em `/BIN/`, e o mesmo histograma nos dois jogos (§1.14).

Cravar uma constante lê o fluxo comprimido a partir do lugar errado em 205 dos
208 arquivos. A largura se **deriva**, palavra a palavra, enquanto o valor
couber na RAM da PSX.

E o zero conta como palavra de cabeçalho: `TEX_00.BIN` tem uma nula no índice
6, nos dois jogos, com ponteiros válidos depois. Parar no primeiro zero
encurta o cabeçalho pela metade — que é, muito provavelmente, a origem da
divergência de `28` × `48` que a §1.14 deixou aberta.

## 7. Entregáveis

| Fase | Entregável |
|---|---|
| 0 | `tools/pes2/iso.py` + round-trip + controle negativo + o emulador — **feito e verde** (§5.1) |
| 1 | tabela de âncoras `OFS_* → (arquivo, offset relativo)`; diff entre releases |
| 2 | inventário de texto; contagem e ordem canônica; primeiro `poke` verificado |
| 3 | estrutura do registro de jogador |
| 4 | estrutura de time, formação, uniforme, bandeira, Master League |
| 5 | `pes2_map.json` + gerador + round-trip headless |
| 6 | editor |
| 7 | codec LZSS; extrator de entrada gráfica; gravação fit-or-fail; conjunto de cópias por idioma; e, fora do portão, o áudio |
