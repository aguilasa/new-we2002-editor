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

**(f) O índice do contêiner: 16 bytes por entrada, dois tipos — medido em
2026-09-01, pela [PES2-TASK-27](/docs/tasks/27-conteiner-e-tim.md).** A §5
Fase 10 do `PLAN-FEATURES` previa um `DATA_HEADER` de 32 bytes. São **16**, e
há duas espécies:

| campo | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| significado | tipo | `vram_x` | `vram_y` | largura | altura | 0 | offset | `0x800f` |

O byte baixo do campo 0 é `0x0a` para **imagem** e `0x09` para **CLUT**; o
byte alto é 0 em toda imagem e varia nos CLUT. Listas terminam na halfword
`0x00ff`. A carga de uma imagem é um fluxo LZSS; a de um CLUT é **crua**.

**Onde a lista mora não é fixo, e por isso ela é achada, não calculada.**
`DAT2D.BIN` põe os 21 registros de imagem numa lista só depois do último
fluxo, e uma segunda lista de 266 CLUTs depois dela; `TEX_00.BIN` põe **um**
registro depois de cada fluxo, onze listas ao todo. As duas se leem do mesmo
jeito: achar o `0x800f 0x00ff` que fecha uma lista e andar para trás de 16 em
16 enquanto a etiqueta se mantiver.

**A largura do CLUT é o que diz a profundidade da imagem — do par
imagem-paleta, não do arquivo.** O registro de imagem não tem campo de bpp.
256 cores ⇒ **8 bpp**, 16 cores ⇒ **4 bpp**, e os dois aparecem no mesmo
disco: `TITLE.BIN` é 8 bpp e `LOGO.BIN` é 4. O retângulo é sempre em unidades
de 16 bits, então a imagem tem `largura × 2` pixels a 8 bpp e `largura × 4` a
4 bpp — a contagem de bytes é a mesma, `largura × altura × 2`, só a leitura de
um byte muda. Assumir 256 em toda parte faz a paleta de 32 bytes do
`LOGO.BIN` ser lida como 512 e passar do fim do arquivo.

**E os dois aparecem no mesmo *contêiner*, que é o que obriga a regra a ser do
par.** O `/BIN/DAT2D.BIN` das duas releases de PES2 tem **261 CLUTs de 16
cores contra 5 de 256** — é o único contêiner de largura mista dos quatro
discos, e é justamente aquele para onde as cores de bandeira mandam olhar.
Responder pelo arquivo deixaria as 5 decidirem contra as 261, e **em
silêncio**: a contagem de bytes não muda com a profundidade, então o gate
segue verde e só a imagem sai errada — medido, 64×128 em vez de 128×128.

Como o contêiner **não diz qual CLUT vai com qual imagem** (limite já escrito
acima), a profundidade de uma imagem de `DAT2D.BIN` **está em aberto** até
esse par ser resolvido. O `bin_archive.py` passou a dizer isso em vez de
escolher: `ls` mostra as duas geometrias para contêiner de largura mista,
`export` tira a profundidade do CLUT que recebeu em `--clut`, e `check` conta
quantos contêineres são mistos — **1 nas duas releases de PES2, 0 nas duas
imagens de WE2002**.

```
python3 tools/pes2/bin_archive.py ls    "<track1.bin>" --file /BIN/TITLE.BIN
python3 tools/pes2/bin_archive.py check "<track1.bin>"
python3 tools/pes2/bin_archive.py export "<track1.bin>" --file /BIN/TITLE.BIN --out <dir>
```

| Disco | contêineres com índice | registros de imagem | exatos | duplos | falham | CLUTs |
|---|---:|---:|---:|---:|---:|---:|
| PES2 `(EsIt)` | 139 | 918 | 798 | 105 | 15 | 804 |
| PES2 `(EnFrDe)` | 141 | 960 | 840 | 105 | 15 | 804 |
| WE2002 European Deluxe | 109 | 637 | 530 | 82 | 20 | 447 |
| WE2002 japonês | 130 | 815 | 688 | 105 | 22 | 547 |

*Exato* quer dizer `largura × altura × 2 == bytes descomprimidos`. As três
colunas que não são exatas, cada uma com causa medida:

- **Duplos.** Um registro por `TEX_*.BIN`, sempre o mesmo — VRAM (704, 256),
  64×64 —, cujo fluxo rende o dobro dos 8.192 declarados. Aparece nos quatro
  discos, e fica **aberto**: não há evidência aqui de se o excedente é uma
  segunda transferência ou folga.
- **Falham.** Nos três discos originais, todas em `GDC_*`, que a (d) já põe
  fora de escopo. Na European Deluxe há **mais uma, fora dos estádios**: o
  registro em 18052 de `/BIN/TEX_70.BIN`, cujo fluxo morre em `distance 0 at
  16938`. 20 falhas menos as 19 de estádio. É o mesmo estrago dos cinco
  *outros* logo abaixo, e pela mesma razão — **é a imagem hackeada**.
- **Outros.** Zero nos três discos originais, e **cinco na European Deluxe** —
  fluxos que rendem 15.481, 16.395, 16.430, 16.501 e 16.345 onde o registro
  declara 16.384 ou 8.192. É a imagem **hackeada**: o hack reinseriu gráfico
  sem respeitar o retângulo do próprio índice, e o `DAT2D` dela é um dos
  cinco. Isto explica de onde vinha o `16.345` que a §5c registrava para o
  `DAT2D` daquele disco.

**O veredito do gate, disco a disco.** `bin_archive.py check` sai **0 nos três
discos originais**. Na European Deluxe são **seis** registros que não cabem no
próprio retângulo — os cinco *outros* mais o `TEX_70` —, e a ferramenta os
conta como categoria própria em vez de reprovar, do mesmo modo que já faz com
os estádios da (d): um gate vermelho por motivo que ninguém pretende consertar
é ruído, não sinal. **A contagem é a asserção** — as seis são permitidas, uma
sétima não é, e o disco é reconhecido pelo rótulo que a tabela da (e) resolve
a partir da contagem de contêineres. Um `check --file` isolado **não** recebe a
permissão, e diz isso.

**O registro é o índice; a varredura de ressincronização da (e) é uma
aproximação dele.** Onde as duas discordam, o registro ganha, e dá para
mostrar: em `TEX_01.BIN` a varredura começa um fluxo em 5276 e rende 16.381
bytes — número que não é potência de dois —, e o registro diz 5284, que rende
16.384 exatos.

**Os onze `CG*.BIN` não são contêiner gráfico.** Sem fluxo LZSS (e) e **sem
registro nenhum** (f): depois dos ponteiros de RAM vem `0x41` = 65 e uma
tabela cuja carga é coordenada assinada de 16 bits terminada em `0x00f0`, que
é geometria. Vão com os estádios, para fora do escopo 2D, e isso **corrige** a
§5 Fase 10 do `PLAN-FEATURES`, que os listava entre os contêineres a extrair.

**Trinta e seis contêineres têm fluxo e nenhuma lista de registros** —
`DATSEL_I.BIN`, `DATSEL2I.BIN`, `DAT_CG.BIN` e `EDTR_2D.BIN` entre os que
interessam. Neles a geometria da entrada não está declarada em lugar nenhum do
arquivo, e é um limite a escrever, não a contornar.

**As cores de bandeira são entradas de CLUT, e é por isso que o WE2002 as
cravava.** Os quatro `OFS_FLAG_COLOURS*` da §1.4 caem em `/BIN/DAT2D.BIN` nos
offsets relativos **69798, 73254, 73728 e 75776**, e o que está ali são
halfwords BGR555 com o bit de semitransparência — `0x8dc3 0x8982 0x97bd …` em
69798 **na imagem japonesa**; a European Deluxe, que é a hackeada, tem outros
valores ali —, fechando em `0x8000 0x8000 0x8000 0x0000`.

Os cinco `OFS_FLAG_SHAPE_COPY_*` são **outra coisa** — forma de bandeira, não
cor — e moram noutros arquivos: `/OPENNING.BIN` +20820, `/SELECT.BIN` +5580 e
+286580, `/SELFORM.BIN` +72400 e `/REPLAYS.BIN` +58304. O **72400** que esta
frase citava até a [CORR-PES2-015](/docs/tasks/CORR-PES2-015.md) é o do
`/SELFORM.BIN`, e em `DAT2D.BIN` +72400 lê-se `0x0d4d 0x118f 0x11d2 0x1613`,
com o bit alto **apagado** — o contrário do que a frase descreve. Quem localiza
os nove é `python3 tools/pes2/ofs_map.py <img>`. Só que o `DAT2D.BIN` do WE2002 tem **23
registros de imagem e zero de CLUT** nas duas imagens: a região de paleta
começa em 65876 e o contêiner não a indexa. No PES2 o mesmo arquivo indexa —
266 CLUTs, cargas em 53372..64284. É a via de entrada da
[PES2-TASK-14](/docs/tasks/14-bandeiras.md), e a linha está escrita lá.

**(g) Gravar de volta: fit-or-fail, medido — 2026-09-01, pela
[PES2-TASK-29](/docs/tasks/29-gravacao-de-asset.md).** O
`tools/pes2/asset_write.py` importa PNG indexado, recomprime **só** a entrada
tocada, confere antes de escrever e recusa o que não couber.

**São dois orçamentos, não um.** O da §5(a) do `PLAN-FEATURES` é o do
*extent*: o arquivo não pode mudar de tamanho, e sai de graça porque o
`iso.py write_file` recusa qualquer mudança de comprimento. O que morde é o da
**entrada**: a distância do offset de um fluxo até o próximo registro ou
próximo fluxo, o que vier antes. E ele é apertadíssimo — a folga medida nas
entradas de `TITLE.BIN` e `LOGO.BIN` é de **0 a 3 bytes**.

Consequência que um editor precisa saber antes de prometer round-trip:
**reimportar a imagem exportada sem alterar nada é recusado em algumas
entradas.** `TITLE.BIN` entrada 0 pede 7.858 B e tem 7.836 — 22 acima. Não é
defeito: é o compressor daqui não ser o da Konami, o que a §5c já media no
agregado (−0,8% no `T_NAME_I`) e que por entrada vai para os dois lados. Das
13 entradas de `TITLE.BIN` e `LOGO.BIN`, **9 recomprimem dentro do próprio
orçamento e 4 não**.

Os dois números saem de `python3 tools/pes2/asset_write.py budget <copia.bin>
--file <contêiner>`, que imprime a conta e a faixa de folga. Ele existe porque
a primeira versão desta seção dizia *10 de 13* e *0 a 4*: veio de uma listagem
filtrada para caber na tela, que escondia a entrada 8 do `LOGO.BIN` — 1.081
bytes contra 1.076 de folga (CORR-PES2-018).

O que o gravador garante, e o `check` afirma a cada corrida:

| Garantia | Medida |
|---|---|
| abrir e salvar sem editar devolve a imagem idêntica | 139 contêineres com índice reescritos, imagem byte a byte igual |
| entrada não editada nunca recomprime | só a tocada é regenerada; o resto é carregado |
| toda reescrita é conferida **antes** do disco | `decompress(compress(x)) == x` sobre os bytes que vão ser gravados, sem flag |
| estouro recusa com a conta | `TITLE.BIN` entrada 0: 22 bytes acima, nada gravado |
| controle negativo | um pixel no `LOGO.BIN` entrada 2 muda **745 bytes**, o primeiro exatamente no offset da entrada |
| uma cor de paleta toca o que deve | 2 bytes, **1 setor** (4711), no offset absoluto previsto 11081454 |
| `roms/` recusado | como no `poke.py` |
| import recusa a profundidade errada | um PNG de 4 bpp num slot de 8 bpp é recusado, com as duas profundidades no texto |
| import recusa paleta que não é a do slot | compara com o CLUT do destino e diz a primeira cor que difere; `--repaint` aceita conscientemente |

**A validação de import não pode ser por dimensão.** Um retângulo de VRAM tem
a **mesma** largura em pixels nas duas profundidades — 32 unidades são 128 px
a 4 bpp e 64 unidades são 128 px a 8 bpp — e a contagem de bytes também é a
mesma. Um PNG de 4 bpp exportado do `LOGO.BIN` foi aceito e gravado no
`TITLE.BIN`, que é 8 bpp, com as três validações antigas verdes
(CORR-PES2-019). A profundidade agora sai do tamanho da `PLTE` do PNG e é
comparada com a do slot, e a recusa é exercitada pelo `check`.

Paleta é carga **crua**: não há fluxo para caber, e por isso a gravação de cor
nunca esbarra em orçamento — é a via barata para verificar em tela, e foi a
usada na §6.7.

**A divergência da §5c, fechada.** Ela dizia que o fluxo de `TEX_00.BIN`
começa em **28**; a varredura de (a) dizia **48**. É **48**, nos quatro
discos: 24, 28, 32 e 44 falham, e falham na primeira distância que aponta para
antes do começo da saída. A linha da §5c foi corrigida no arquivo dela. O
provável motivo de a medição antiga não se reproduzir também ficou medido:
na imagem golden European Deluxe **18 dos 105 `TEX_*.BIN` são Form 2**, e o
`iso.py` recusa lê-los — não há área de 2.048 bytes num setor Form 2. O
`TEX_00.BIN`, que é justamente o arquivo da divergência, é um deles; quem o
leu em 2026-08-02 leu com outro fatiamento de setor, o que casa com o
`16.400 = 16.384 + 16` que ela registrava. As outras cinco linhas daquela
tabela **se reproduzem exatamente**.

Os **outros 87 são Form 1** e são lidos normalmente — os relatórios de
`TEX_03`, `TEX_06`, `TEX_28`, `TEX_70` e `TEX_84` da (f) saem deles. Os 18,
por nome:

`TEX_00`, `TEX_01`, `TEX_02`, `TEX_10`, `TEX_13`, `TEX_17`, `TEX_34`,
`TEX_36`, `TEX_41`, `TEX_43`, `TEX_48`, `TEX_50`, `TEX_51`, `TEX_52`,
`TEX_63`, `TEX_73`, `TEX_81` e `TEX_83`

Nas outras três imagens os 105 são Form 1. O número sai de `iso.py`:

```python
[p for p in sorted(img.files)
 if p.startswith("/BIN/TEX_") and not img.is_form1(p)]
```

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
3a. **Nem toda tela mostra nome de time — várias mostram bandeira.** Medido
   em 2026-09-02 percorrendo uma partida inteira: o placar em jogo, o
   replay, o `RESULTADO` e o menu pós-resultado identificam os times por
   **bandeira**, não por texto. O registro de replay gravado no cartão
   também: ele traz as duas bandeiras, o placar, `Goleador` e `Pasador`. Isso
   limita o que uma tela pode verificar — um `poke` num nome de time **não
   se vê** nessas telas, e a verificação de `RESULT.BIN` @524 e de
   `REPLAYS.BIN` @11380 precisa achar onde esses nomes de fato aparecem.
   `SELECT.BIN` @3128 continua verificável: a grade de seleção de time
   mostra o nome em texto.
3b. **Os nomes dos atributos, lidos da tela.** O Modo Editar mostra os
   **dezesseis** campos por jogador, em ordem, e a ordem de tela costuma ser
   a ordem do registro: `Ataque`, `Defensa`, `Equilib.`, `Resisten`,
   `Velocid.`, `Acelerar`, `Respues.`, `Regate`, `Pase`, `Precisión`,
   `Potencia`, `Cabezazo`, `Salto`, `Técnica`, `Efecto`, `Positivo` — mais
   `Nación`, `Altura`, `Edad`, `Posición` e `Pie` no bloco de identificação.
   Capturado em 2026-09-02 por `drive.py --screen edit`. **Ele só edita
   jogador criado**, não os times embutidos, então o nome de time de
   `SELECTC.BIN` @16576 fica atrás de criar um jogador primeiro.
4. **Desmontagem do MIPS**, para os campos que a estatística não resolver.
   É o último recurso, e é o mais caro. Existe ferramenta de terceiro que o
   resolveria quase inteiro, avaliada e **não adotada** — o porquê, e o
   caminho mais barato a tentar antes dela, na §6.14.

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

**Decidido por medição em 2026-09-01, pela
[PES2-TASK-29](/docs/tasks/29-gravacao-de-asset.md), e havia divergência a
resolver.** A §5(b) do [PLAN-FEATURES](/docs/PLAN-FEATURES.md) decidiu
**recalcular** EDC/ECC no caminho de assets; esta seção decide **preservar**.
As duas não podem valer no mesmo comando, e a medida decide:

1. **A gravação preserva a cauda, e isso é verificável.** O
   `tools/pes2/asset_write.py` grava só a área de 2.048 bytes de dados, pelo
   `iso.py write_file`. Depois de reescrever uma cor de paleta do
   `/BIN/TITLE.BIN`, o setor 4711 tem **2 bytes de dados diferentes**,
   cabeçalho igual e os **280 B de cauda idênticos**; o mesmo no setor 4608 do
   `/BIN/LOGO.BIN`, com 89 bytes de dados. O `check` do gravador afirma isso a
   cada corrida.
2. **O jogo boota e desenha com a cauda obsoleta.** Depois de repintar as
   paletas do `LOGO.BIN` e do `TITLE.BIN` de uma cópia de trabalho — 598 bytes
   em 2 setores —, o disco chega à tela de título no DuckStation e o
   logotipo, o `PRESS ANY BUTTON`, o `POWERED BY UMBRO` e o aviso de copyright
   aparecem todos em magenta. **11.854 de 76.800 pixels** diferem do mesmo
   quadro do disco original. É a prova direta de que o jogo não confere EDC.

**A regra, portanto:** preservar é o padrão e o único comportamento do caminho
de gravação. Um recálculo, se algum dia entrar, é **comando avulso e opt-in** —
o `fixecc` que o próprio `PLAN-FEATURES` prevê — e nunca fica ligado a gravar.
Preservar é o que mantém honestos o round-trip da §0 e o controle negativo do
`iso.py`; recalcular apagaria os dois.

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

### 6.11 Vinte e seis armadilhas ao dirigir o DuckStation

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
4. **O lançador não configura o DuckStation, e isso é decisão.** Este item
   dizia, até 2026-09-02, "um `settings.ini` escrito à mão não tem binding
   nenhum, então declare `[Pad1]`". O `[Pad1]` foi declarado e continuou sem
   efeito, pela armadilha 14. A saída não foi insistir na configuração
   própria: **a máquina roda DuckStation para este projeto**, então a
   configuração dele é a que vale, o lançador não escreve nenhuma, e o
   `drive.py` **lê** os bindings do arquivo em vigor. Remapear um botão na
   interface do DuckStation basta; não há nada a mudar no repositório.

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

10. **Toque não é apertar, e foi isto que travou a Fase 2 inteira.**
    `xdotool key X` é press e release no mesmo instante, e o jogo **não vê**
    o botão: na tela de título, três formas de tocar — simples, com
    `windowfocus`, com `--clearmodifiers` — deixaram o quadro idêntico até a
    sexta casa decimal, e um `keydown` / **1 s** / `keyup` entrou. Um jogo de
    PSX lê o pad uma vez por quadro, e um toque cai inteiro entre duas
    leituras. Com 0,4 s ainda não basta.
11. **O fast-forward corta a abertura de dois minutos para 25 segundos**, e
    é o único jeito de passar dela: `Cross` **não** pula o vídeo — vinte e
    quatro pressionamentos ao longo de oitenta segundos deixaram o FMV
    correndo. `Tab` é o binding *default* do DuckStation, o que é a razão de
    ele ter funcionado durante todo o período em que o arquivo de
    configuração era ignorado (armadilha 14).

12. **A Citrix não é a culpada aqui, e a suspeita custa caro.** A
    `libAppProtection.so` do `/etc/ld.so.preload` exporta `XNextEvent`,
    `XPeekEvent`, `xcb_poll_for_event`, `xcb_wait_for_event` e
    `XRecordQueryVersion` — é um anti-keylogger, e a leitura óbvia é que ela
    filtra o XTEST do `xdotool`. **Não filtra:** o input chega, e o
    `tools/run-sanitized.sh` não é necessário para dirigir o emulador. A
    frase do [CLAUDE.md](../CLAUDE.md) sobre a Citrix filtrar input sintético
    é do **Windows**; no `:98` ela não vale. Testado em 2026-09-01, antes de
    gastar o namespace num problema que não existia.
13. **Não edite um `.sh` enquanto ele roda.** O bash relê o arquivo por
    offset, então uma edição no meio da execução corrompe o que ainda não foi
    lido — e o sintoma é um `unexpected EOF while looking for matching "`
    numa linha que está perfeita em disco. Custou uma corrida de dois minutos
    e uma investigação de sintaxe que não tinha o que achar.

14. **`XDG_DATA_HOME` não isola este AppImage, e acreditar que isolava custou
    um dia.** Ele resolve o diretório de dados a partir do **`$HOME`**, então
    toda corrida até 2026-09-02 usou `~/.local/share/duckstation` — o do
    usuário. A prova é de uma linha: `StartFullscreen = true` no arquivo que
    o lançador escrevia, e a janela sai com 800×655. Consequências medidas:
    o `[Pad1]` do lançador nunca valeu, dois save states nossos foram parar
    no diretório do usuário, e o `F2` que parecia não gravar **gravava** — no
    lugar errado. O cartão de memória não foi tocado (digest conferido antes
    e depois). Sobrescrever `HOME` isola de verdade, mas aí o primeiro boot
    para no assistente de configuração (armadilha 20).

    **Encerrado por decisão, não por conserto:** o usuário determinou em
    2026-09-02 que esta máquina roda DuckStation para este projeto e que
    isolar não interessa. O lançador deixou de escrever configuração — um
    arquivo que ninguém lê é pior que nenhum, porque passa um dia parecendo
    aplicado — e o `drive.py` lê o que está em vigor. Save state e cartão
    caem em `~/.local/share/duckstation` como em qualquer sessão do
    emulador.
15. **Tecla que funciona não prova que a configuração foi lida.** `Tab`,
    `Enter` e as quatro setas funcionaram o tempo todo — porque são
    **defaults** do DuckStation, não porque o arquivo tivesse efeito. A
    tabela de defaults está no próprio binário e sai com
    `strings`: `UpArrow`, `DownArrow`, `LeftArrow`, `RightArrow`, `Enter`,
    `Backspace`, `Space`, `Escape`, `Tab`, `F1`–`F4`, `F10`, `F11`, os
    dígitos `1`–`4` e as letras `A D E F G H I J K L Q S T W`. Para saber se
    o arquivo vale, mude algo que **não** seja default e confira o efeito.
16. **São dois espaços de nomes de tecla, e eles discordam.** O valor no
    `settings.ini` é o nome do DuckStation; o que o `xdotool` manda é keysym
    do X. `UpArrow` contra `Up`, `Enter` contra `Return`, `Backspace` contra
    `BackSpace`. Manter os dois numa tabela só está errado em um dos lados.
17. **A tela de título aceita `Start`, não `Cross`.** Cinco `Cross` nela não
    mudaram nada — o quadro seguia idêntico até a sexta decimal — e o preto
    que vinha depois era a tela expirando sozinha para o laço de atração,
    não o botão. Com `Start` ela sai na hora. E o título é **passageiro**:
    entre reconhecê-lo e capturá-lo cabe um `import`, e num deles a média
    caiu de 0,550 para 0,197 nesse intervalo — pressione antes de capturar.
18. **Um pressionamento não basta, e o segundo não é desperdício.** Uma tela
    recém-desvanecida engole o primeiro: na tela de idioma o mesmo `Down`
    registrou na primeira tentativa numa corrida e só na **quinta** noutra.
    Rota que pressiona uma vez e conclui "o botão não funciona" está medindo
    o fade, não o binding.
19. **Hotkey ganha de binding de pad.** `Keyboard/Space` é nome válido e é a
    tecla de pausa do DuckStation: ligar `Cross` nela **pausa o emulador** em
    vez de apertar botão. O sintoma engana — todo quadro seguinte fica
    idêntico, que é exatamente como "o jogo travou" se parece —, e o que
    denuncia é o glifo de pausa no canto da captura.
20. **Um diretório de dados virgem para no assistente de configuração**, e
    `SetupWizardIncomplete = false` não pula. Medido com a bandeira presente,
    com os `resources/` semeados de uma instalação que funciona e com o BIOS
    como arquivo de verdade em vez de link: as nove páginas sobem do mesmo
    jeito e nenhuma janela de jogo aparece atrás delas. Registrado porque é o
    que fecha a porta da isolação, caso ela volte a interessar — a armadilha
    14 foi encerrada por decisão, não por conserto.

21. **O d-pad quer toque, o botão de face quer pressão — e os dois requisitos
    brigam.** A armadilha 10 estabeleceu que tocar não é apertar, e isso vale
    para os botões. Para a direção vale o **contrário**: um `Down` de 1 s
    dispara o auto-repeat do próprio jogo, e num menu de sete itens ele dá a
    volta inteira e para no item de onde saiu — diferença de 0,0004, que se
    lê exatamente como tecla perdida. Medido lado a lado no menu principal:
    a 1,0 s **duas de seis** "sumiram"; a 0,15 s as seis moveram, diferenças
    de 0,0136 a 0,0178. A duração é escolhida por botão, não fixada uma vez.
22. **Apertar-até-mudar está errado numa lista.** A tentativa extra move uma
    linha a mais, e o resultado é confirmar o item errado calado: cinco
    linhas pedidas viraram dez teclas e a rota do `Modo Editar` caiu no
    `Modo Copa`. Numa lista, tecla lenta a desenhar e tecla perdida são
    indistinguíveis, então **espere mais em vez de apertar de novo**, e
    conte quantas linhas registraram — quem para curto é visível, quem passa
    do ponto não é.

23. **O relógio da partida não anda até o passe inicial.** O saque fica
    parado em `1°  0:00` esperando o `Cross` do jogador 1, e uma partida
    parada no saque **é indistinguível de uma partida correndo** para
    qualquer medida sobre o quadro inteiro: a câmera se mexe, os jogadores
    respiram, a média fica em ~0,30. Foi assim que uma corrida registrou
    "onze minutos de fast-forward não terminaram a partida" medindo uma
    partida que nunca começou. O teste honesto é recortar **só o relógio**
    (`(560,90)-(760,130)` na janela de 800×649) e comparar dois quadros:
    parado dá **0,00000**, andando dá diferença franca. Hipótese do usuário,
    confirmada por medição em 2026-09-02.
24. **Três telas seguidas se parecem para a média, e o desvio as separa.**
    Abertura de estádio, entrada dos times e saque têm todas média entre
    0,21 e 0,30, e duas sondas pressionaram `Cross` na tela errada por
    isso. O que separa é o **desvio-padrão da faixa do topo**
    `(0,60)-(800,200)`, onde o saque tem a barra uniforme do placar sobre
    gramado: saque **0,1170–0,1204**, entrada dos times **0,1531**,
    abertura de estádio **0,2317–0,2537**. Usado em conjunção com o relógio
    congelado, porque cada um sozinho já deu falso positivo uma vez — o
    relógio recortado sobre o céu da abertura também fica parado.
    E `Start` pula a abertura de estádio, o que economiza a espera.
25. **`pgrep -f` e `pkill -f` casam a linha de comando do próprio shell.**
    Está registrado dentro do `run_duckstation.sh` desde a armadilha 7, para
    o padrão `DuckStation` — e vale para **qualquer** padrão: um
    `pkill -f probe28.py` digitado num shell cujo comando contém
    `probe28.py` mata o shell antes de ele fazer o que ia fazer, e o
    sintoma é um script que nunca chega a ser escrito. Duas corridas
    perdidas assim em 2026-09-02. Exclua o próprio PID, ou mate por PID.

26. **Todo gol devolve um saque, e ele também espera `Cross`.** A armadilha
    23 vale para o saque inicial e a leitura fácil é que basta dá-lo uma vez.
    Não basta: a cada gol a partida volta à formação de saque e **congela de
    novo**, com tela e relógio em `0,00000`. Um roteiro que só segura o
    fast-forward para no primeiro gol e fica parado até o orçamento acabar —
    exatamente o sintoma que produziu o "onze minutos não terminaram a
    partida". O laço certo é *acelerar → detectar congelamento → `Cross` →
    retomar*, e está no `pad.py run`. Medido em 2026-09-02, com o usuário
    olhando a tela: **179 segundos e nove saques** do início ao `RESULTADO`,
    contra a estimativa de ~28 minutos que a versão sem `Cross` sugeria.
    Um `Cross` só serve para as duas coisas quando há replay na frente: ele
    sai do replay **e** dá o saque.

---

### 6.12 Asset também tem conjunto de cópias — e ele é por idioma

A §6.1 vale para as tabelas de texto. Vale igual para os assets, e o caso mais
puro está medido: `/BIN/T_NAME_I.BIN` e `/BIN/T_NAME_S.BIN` têm 62.196 bytes
cada e são **byte a byte idênticos**. O jogo escolhe por idioma.

Gravar um e deixar o outro produz um disco que parece certo — para quem joga
no idioma que foi gravado. O modo de falha é o mesmo da §6.1, com o agravante
de ser **invisível na verificação** se o roteiro do emulador não trocar de
idioma.

**Varrido em 2026-09-01, pela
[PES2-TASK-28](/docs/tasks/28-t-name-copias-de-idioma.md), e o resultado
corrige a frase que estava aqui.** O `tools/pes2/lang_map.py` agrupa por
digest de conteúdo sobre **todo** arquivo `form1` do disco, e acha **três**
conjuntos de cópia por release, não os pares que esta seção listava:

| Conjunto | `(EsIt)` | `(EnFrDe)` | tamanho |
|---|---|---|---:|
| nome de apresentação | `T_NAME_I`, `T_NAME_S` | `T_NAME_E`, `T_NAME_F`, `T_NAME_G` | 62.196 B |
| `LC` | `LC_MS`, `LC_OL` | idem | 10.420 B |
| `TEX` | `TEX_99`, `TEX_A0`, `TEX_A1`, `TEX_A2` | idem | 32.752 B |

E o `T_NAME` é o **mesmo arquivo nas duas releases** — mesmo digest, mesmos
62.196 bytes. São **cinco cópias em dois discos, um conteúdo só**.

**Os outros arquivos que esta seção listava não são cópias.** `DAT2D_I` tem
39.820 bytes e `DAT2D_S` tem 37.728; os três `DATSEL*I` diferem entre si; os
catorze `LC_*` também. São **variantes de idioma**, que é o problema oposto:
gravar as duas com o mesmo conteúdo estraga uma. A distinção é medida, não
suposta, e é por isso que o agrupamento é por conteúdo.

**E o sufixo não sobrevive nem à troca de release:** a `(EsIt)` traz
`DATSEL_I`, `DATSEL2I` e `DATSEL3I` e nenhuma forma sem sufixo; a `(EnFrDe)`
traz `DATSEL`, `DATSEL2` e `DATSEL3` e nenhuma com. Quem varrer por sufixo
acha conjuntos diferentes em cada disco.

Os `FNOTE_{G,I,S}` **não estão em `/BIN/`** — estão na raiz do disco, e têm
1.896, 1.884 e 1.792 bytes: três arquivos diferentes, não um conjunto. A
varredura cobre o disco inteiro por causa deles.

```
python3 tools/pes2/lang_map.py "<track1.bin>" --check
python3 tools/pes2/lang_map.py "<track1.bin>" --asset /BIN/T_NAME_I.BIN
python3 tools/pes2/lang_map.py "<track1.bin>" --self-check --tmpdir <dir>
```

**A fonte de apresentação não está no disco — medido, e é resultado, não
desistência.** O `T_NAME` guarda os nomes **já rasterizados**: 28 entradas de
128×128 a 4 bpp, quatro nomes por entrada num passo de 32 linhas, e a primeira
traz `Ireland`, `Scotland`, `Wales` e `England`. Os glifos têm **12 a 13
pixels** de altura (`tools/pes2/tname.py bands`).

*Uma versão anterior desta seção dizia que a face vinha de dois blocos de
`/BIN/DAT2D_I.BIN`, nos offsets 20432 e 24768.* **Não vem**, e a medida é
simples: aqueles blocos têm bandas de 18, 15 e 9 pixels, e nenhuma de 12. A
semelhança que motivou a afirmação era só o itálico.

O `tools/pes2/tname.py fontscan` é a busca que fechou a questão — toda entrada
de imagem de todo contêiner que não é estádio, atrás da grade regular de
bandas curtas que uma folha de alfabeto faria neste tamanho. São 84 candidatos
na `(EsIt)` e 111 na `(EnFrDe)`, e **todos são texto já desenhado**: as
strings de interface dos `LC_*`, do `EDT_2D` e dos `CG<idioma>`, e os próprios
nomes do `T_NAME`. Alfabeto, nenhum.

Ou seja, os nomes de apresentação foram rasterizados **fora do disco**, com a
fonte que os desenvolvedores usaram — que é o que o `T_NAME-Maker` do CARP faz
do outro lado, com uma fonte de PC. E compor letra a letra a partir dos pixels
do próprio disco também não dá: a face é itálica e as letras se encostam, de
modo que `Ireland` é uma corrida ininterrupta de 92 colunas com tinta, sem
nenhuma coluna vazia onde cortar.

**O que dá, e o `tname.py swap` faz**, é mover para outro slot um nome que já
está rasterizado. É a operação que um editor pode oferecer honestamente hoje,
e exercita o caminho de gravação inteiro — geometria de banda, recompressão,
orçamento e o conjunto de cópias.

**E o orçamento morde.** Recomprimir a entrada 0 do `T_NAME_I` depois de
copiar a banda 3 sobre a 2 dá 1.904 bytes contra **1.868** de folga até o
próximo registro: **recusado, 36 bytes acima**. A mesma entrada com a banda 2
sobre a 3 dá 1.817 e passa. Isto é a política *fit-or-fail* da §5(a) do
`PLAN-FEATURES` acontecendo em dado real, e é da
[PES2-TASK-29](/docs/tasks/29-gravacao-de-asset.md).

**Um número da §5c a refinar.** Ela mede que recomprimir dá sempre 0,2% a 2,0%
*menor*. Sobre as 28 entradas do `T_NAME_I`, o compressor daqui dá 61.212
bytes contra os 61.688 da Konami — **−0,8%**, dentro da faixa —, mas **6 das
28 entradas saem maiores**. "Sempre menor" vale no agregado e não vale por
entrada, que é justamente a granularidade em que um gravador decide.

E como na §6.1, **o conjunto se varre, nunca se declara**: o
`lang_map.py` recusa gravar num arquivo que não tenha cópia, e depois de
gravar varre o disco atrás do conteúdo antigo — a metade da medida que uma
captura de tela no idioma certo nunca pegaria.

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

### 6.14 Ferramenta externa avaliada: `duckstation-claude-plugin`

Avaliada em 2026-09-02, a pedido do usuário. **Não adotada agora**, e o
registro existe porque ela resolve exatamente o item 4 da §4.2 — a
desmontagem do MIPS, "o último recurso, e o mais caro".

<https://github.com/sadnescity/duckstation-claude-plugin>

**O que é.** 95 ferramentas MCP sobre um servidor que roda *dentro* do
DuckStation, em `localhost:2346`, expostas ao Claude Code. Debugger de CPU
(registradores, disassembly, breakpoints), leitura e escrita de RAM e VRAM,
save states, cartões, input de controle, e sete fluxos de engenharia reversa
prontos. Instalação: `/plugin marketplace add sadnescity/claude-plugins`.

**O que custaria.** Um **fork de terceiro** do emulador —
`sadnescity/duckstation`, branch `mcp`. `EnableMCPServer` não existe no
build oficial: conferido por `strings` sobre o AppImage extraído, e as
únicas ocorrências de `2346` são número de linha de `fullscreenui_settings.cpp`.
O fork tem **3 estrelas e 0 forks**, não publica binário — o próprio README
manda baixar do upstream —, então adotá-lo é compilar um emulador C++ de
12.330 commits. E trocar de binário **invalida toda assinatura de quadro
medida**: a da tela de título (0,550 / 0,341) e a do menu (0,1405 / 0,2124)
saem do renderer e da versão, e as vinte armadilhas da §6.11 são sobre o
AppImage oficial.

**Quatro dos sete fluxos batem no que falta aqui:**

| fluxo | ferramentas | o que resolveria |
|---|---|---|
| C — busca de valor | `memory_scan`, `read_memory` | endereço de RAM de um atributo pelo valor em tela; é o caminho mais curto para os campos por jogador ainda desconhecidos |
| A — quem escreve | `breakpoint` de escrita, `read_registers`, `disassemble` | do endereço ao **carregador**, e do carregador ao offset no disco — fecha o laço disco↔RAM, hoje feito só por cutucar e olhar |
| D — diff de memória | `snapshot_memory`, `diff_memory` | "o que o Modo Editar muda?", que é a PES2-TASK-05 em RAM em vez de cartão |
| E — verificar ASM | `read_memory`, `disassemble`, `breakpoint` de execução | confirmar que um disco remendado carregou o que se esperava |

O fluxo **F (automação de UI)** duplica o `tools/pes2/drive.py`. As
ferramentas dele seriam melhores — `input_sequence()` e `load_state()` não
têm o jogo de foco `PointerRoot` nem a calibragem de tempo de tecla da §6.11
—, mas é a parte que já está de pé e medida.

**O caminho barato, a tentar primeiro.** Um save state contém a RAM inteira,
e o `F2` já funciona: os dois estados medidos tinham 1.750.327 e 1.583.714
bytes comprimidos contra os 2 MiB de RAM do PSX. O `zstd` está na máquina
(CLI 1.5.5; o módulo Python não, e não é preciso), e
`SaveStateCompression = Uncompressed` na interface do emulador dispensa até
ele. Isso entrega **os fluxos C e D em Python puro, sem fork nenhum** —
não entrega breakpoint nem disassembly, para os quais o fork é
insubstituível. O layout do arquivo **não foi medido**: é hipótese
fundamentada no tamanho, não leitura.

**Decisão:** reavaliar quando o projeto chegar na fase de RAM/MIPS, e
reavaliar **contra o caminho do save state primeiro**, que é mais barato e
não põe um fork de três estrelas no meio da cadeia de medição.

---

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
