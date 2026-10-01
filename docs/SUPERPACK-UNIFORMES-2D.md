# Uniformes 2D no Superpack v6

Levantamento de 2026-10-01 sobre `C:\games\we2002\Superpackv6\We2002\Uniformes 2D`:
25 arquivos em 8 pastas, 2.031.265 bytes. Todo texto da pasta foi lido inteiro —
dois tutoriais (`.doc`, em português e espanhol), um `README.TXT` e um guia `.htm`
(italiano), uma planilha de offsets (`.xlsx`, as duas abas) —, os dois executáveis
VB6 tiveram as strings lidas, e os treze `.bmp` e os dois `.act` foram abertos.
Nada da pasta entra no repositório: binário sem fonte, documento de terceiro, e
nenhum deles com licença.

O **uniforme 2D** é a camisinha que aparece na tela de opções de partida — onde se
escolhe clima, estádio e qual dos dois uniformes cada time veste. Não é o
uniforme que o boneco veste em campo: esse é o 3D, mora nos 105 `TEX_*.BIN` e
está no [SUPERPACK-UNIFORMES.md](/docs/SUPERPACK-UNIFORMES.md). A distinção é a
abertura do capítulo 8 da Bíblia
([/docs/biblia-we2002/08-uniformes.md](/docs/biblia-we2002/08-uniformes.md)),
e o §8a de lá é o tutorial do botão PAINT que a pasta repete.

O que este documento acrescenta é o cruzamento: a comunidade diz **onde** o 2D
mora no disco e **como** o edita; o repositório já tocava nesse dado por três
caminhos — o `FlagKitDialog` do port, a engenharia reversa do editor do Obocaman
em `wte/re/`, e os leitores de contêiner de `tools/pes2/` — sem nunca ter cruzado
uma coisa com a outra. Cada número de terceiro abaixo diz se **bateu** no disco,
se **não foi medido**, ou se **diverge**; o §7 tem o comando ou o snippet que
produziu cada medição, e a saída colada.

---

## 1. A pasta — inventário

```
Uniformes 2D/                                          2 arquivos   2.031.265 B
├── Editor modelos uniformes 2D - ramonpsx/            1 arquivo       53.248 B
├── Shirt preview - Fratel Coniglio/                   6 arquivos   1.135.248 B
└── Uniformes 2D - polipoli/                           4 arquivos     658.331 B
    └── Modelos/                                       0 arquivos      54.426 B
        ├── Editado/                                   3 arquivos      29.496 B
        │   └── Camiseta/                              6 arquivos       4.560 B
        └── Original/                                  3 arquivos      24.930 B
```

| pasta | autor | arquivos | o que é |
|---|---|---|---|
| raiz | **GOKUW11** (W11.com.br / WEleven.com.br) | `Edição de uniformes 2D - GOKUW11.doc` (172.544 B) | o tutorial do botão PAINT do WE Team Editor — o mesmo texto do §8a da Bíblia, com as figuras |
| raiz | pascutti | `Remeras test - pascutti.bmp` (11.894 B, 177×128, 4 bpp) | uma folha de teste de camisas; sem texto que a explique |
| `Uniformes 2D - polipoli/` | **polipoli** (espanhol, 2008–2017 nas datas do `.doc`) | `Tutorial uniformes 2D - polipoli.doc` (577.024 B, 11 páginas), `Offsets y modelos uniformes 2D - polipoli.xlsx` (25.341 B, duas abas), `Paleta 7 DAT2D.act` (768 B), `16 colores diferentes.act` (772 B) | **o documento central da pasta**: diz em que arquivo do disco estão os gráficos, as paletas e os "indicadores de modelo" de cada time, com os offsets dos 95 |
| `…/Modelos/Original/` | polipoli | `22 - 7.bmp`, `23 - 7.bmp`, `24 - 7.bmp` (8.310 B cada, 128×128, 4 bpp) | as três imagens originais do disco, exportadas pelo Wecompressor com a paleta 7 — o §2.3 mede que são byte a byte as do `DATSEL.BIN` |
| `…/Modelos/Editado/` | polipoli | os mesmos três nomes (8.312 B cada) e `Camiseta/01..06 - Modelo *.bmp` (760 B cada, 40×32) | os gráficos dele, redesenhados ao estilo do PES 2008, e seis modelos de camisa para compor |
| `Editor modelos uniformes 2D - ramonpsx/` | **ramonpsx** ("RAHZ Software"; projeto `UNIFORME2D EDIT\Proyecto1.vbp`) | `EditorUniformesWE2002.exe` (53.248 B, VB6) | troca o "modelo" de uniforme de quatro times — Irlanda, Escócia, Gales, Inglaterra — gravando um dos oito valores da planilha do polipoli nos offsets 2728872..2728900 da imagem |
| `Shirt preview - Fratel Coniglio/` | **FratelConiglio** (italiano, `fratel_coniglio@inwind.it`), offsets de **Adesy** | `Shirt_Preview.exe` (770.048 B, VB6, v1.00.0004), `COMDLG32.OCX`, `TABCTL32.OCX`, `README.TXT` (2.032 B), `PS_       .ADD` (122 B), `GuidaRadar.htm` (13.758 B) | recolore a *preview* Home/Away de um time direto na imagem (`.bin` CDRWIN ou `.img` CloneCD), exporta/importa `.ADD`, e edita a cor dos pontinhos do radar pelo guia do **SimoSapo** |

Os três `.bmp` de `Original/` e os de `Editado/` têm digest diferente — os
editados são obra dele, não cópia. Os dois `.act` são tabelas de cor do
Photoshop: `Paleta 7 DAT2D.act` traz as 16 primeiras entradas de uma rampa
preto→amarelo→branco e o resto `FF`; `16 colores diferentes.act` traz 16 cores
todas distintas, para pintar zonas sem confundir uma com a outra, e o trailer
`0010 ffff` (16 cores, nenhuma transparente).

Nenhum arquivo da pasta cita `ed.exe`, "Kits To We2002", "PasionWEMod" ou "Multi
Tool". Os nomes que aparecem são WE Team Editor (e o seu botão PAINT), WE Painter
do Obocaman, Wecompressor, WE Image Manager, CDMage e o ePSXe.

---

## 2. Os três dados que compõem o 2D

A tese do polipoli, no primeiro parágrafo do tutorial dele:

> Las imágenes se encuentran en el archivo Datsel.bin, ID 22, 23 y 24. Las
> paletas se encuentran en el archivo Select2.bin. Los indicadores de los modelos
> de uniforme de cada equipo se encuentran en el archivo Select2.bin.

São três coisas, em dois arquivos, e as três **bateram** no disco. A ordem abaixo
é a de dependência: a paleta é o que todo editor já mexia; o modelo é o que diz
qual desenho a paleta pinta; o gráfico é o desenho.

### 2.1 As paletas: `SELECT2.BIN` +172096 = `OFS_KIT_PREVIEW`

A planilha do polipoli (aba "Paletas uniformes 2D", cabeçalho "PALETAS:
SELECT2.BIN / MANUAL, 4 BITS") dá para cada um dos 95 times um "OFFSET U1" e um
"OFFSET U2" dentro do `Select2.bin`: Irlanda 172096 e 172128, Escócia 172160 e
172192, … Boca Jrs 178112 e 178144. Ou seja **64 bytes por time, o segundo
uniforme 32 bytes depois do primeiro**, e cada uniforme são 16 cores BGR555 de
2 bytes.

Esse 172096 é exatamente o `OFS_KIT_PREVIEW` do port. O
[`Offsets.hpp`](../src/core/include/we2002/Offsets.hpp) o guarda como offset
absoluto da imagem, 2667256, e o
[`pes2-ofs-map.md`](/docs/samples/pes2-ofs-map.md) já o tinha localizado em
`/SELECT2.BIN` relativo 172096; o `SELECT2.BIN` começa no LBA 1050, e
1050 × 2352 + 84 × 2352 + 24 + 64 = 2667256 (§7, snippet 1). A engenharia
reversa do editor do Obocaman chegou ao mesmo lugar por um terceiro caminho:
[`dump_blococor.py`](../wte/tools/dump_blococor.py) tem `BASE_UNIFORME =
0x0025AEF8` (= 1050 × 2352 + 24, o primeiro byte de dado do `SELECT2.BIN`) e
`LOGICO_UNIFORME_0 = 0x2A042` (= 172096 + 2). **Três fontes independentes — o
`ed.exe` de 2002, o editor do Obocaman de 2002 e a planilha do polipoli de
2008–2017 — apontam o mesmo byte.**

O que cada editor expõe das 16 palavras difere, e o disco explica por quê:

| | palavras editáveis | fonte |
|---|---|---|
| `ed.exe` / `FlagKitDialog` | 2..15 | [`FlagKitDialog.hpp`](../src/app/FlagKitDialog.hpp), "each kit uses words 2..15" |
| WE Team Editor (Obocaman) | 1..15 | [`wte/re/render2d.md`](../wte/re/render2d.md): "15 entradas a partir da palavra 1" |
| polipoli | as 16, pelo WE Image Manager em modo "Manual, 4 bits" | planilha |

Medido nos três discos (§7, snippet 1): **a palavra 0 é `0000` nos 190 jogos**
de todos eles, e **a palavra 1 é `4208` nos 190 jogos dos dois discos
originais** (japonês e `ptbr-remaster`). Na `golden-european-deluxe`, que é
hackeada, a palavra 1 varia — `0000, 0208, 2104, 4208, a514, c61c` — então
alguém a editou, e só o editor do Obocaman a expõe. `0x0842` em BGR555 é um
cinza escuro (R=2, G=2, B=2 de 0..31); o que ele pinta no desenho não foi
medido na tela.

Sobre os quatro `OFS_KIT_PREVIEW*` do port: o `Database::Load()`
([`Database.cpp`](../src/core/Database.cpp), o bloco `//kit preview !!!!`) lê
32 bytes de `home_kit` e 32 de `away_kit` por time, salta para
`OFS_KIT_PREVIEW_A` (+174080 = time 31) depois do time 30 — é a fronteira de
setor, 174080 = 85 × 2048 — e lê os clubes de ML a partir de `OFS_KIT_PREVIEW_B`
(+176128 = time 63). `OFS_KIT_PREVIEW_C` (+178176 = time 95) é declarado e nunca
usado: é o primeiro byte depois do último time.

### 2.2 Os modelos: 760 bytes em `SELECT2.BIN` +225808

A mesma aba da planilha traz, à direita, "OFFSETS DE LOS MODELOS DE LOS
UNIFORMES 2D / OFFSETS ISO": para cada time dois offsets **da imagem** e dois
valores de 4 bytes. Irlanda 2728872 `ACB80F80` e 2728876 `FCB80F80`, Inglaterra
2728896 `A0BA0F80`, … Boca Jrs 2729624 `F4FE0F80` e 2729628 `0C001080`. A
segunda aba ("Cambiar modelos uniformes 2D") monta os 95 pares a partir de um
número de modelo de 1 a 8 e manda colar o resultado, **760 bytes**, no offset
decimal 2728872 da ISO com um editor hexadecimal.

O 2728872 é offset cru da imagem, e cai dentro do `SELECT2.BIN`: setor 1160,
byte 552 do setor = byte 528 do dado, ou seja **lógico 225808** do arquivo (§7,
snippet 1). Lido de lá nos três discos, o bloco de 760 bytes é **idêntico** e
bate com a planilha nos pontos conferidos — Irlanda `800FB8AC`/`800FB8FC`,
Inglaterra `800FBAA0`, Boca `800FFEF4`/`8010000C` (os bytes `F4FE0F80`
e `0C001080` da planilha, lidos como little-endian).

Dois fatos que a planilha não diz e a medição diz:

- **São 190 valores distintos, um por uniforme**, todos no intervalo
  `0x800FB8AC..0x8010000C`. Isso é o formato de um **ponteiro de RAM do PSX**
  (`0x8000_0000` + endereço), com o `SELECT2.BIN` carregado como overlay — cada
  uniforme aponta para uma estrutura própria dentro do arquivo carregado. Os "8
  modelos" do polipoli são a classificação **visual** dele sobre o que esses 190
  ponteiros desenham, não oito valores que se repetem; ele mesmo nota que
  Inglaterra `A0BA0F80` e Dinamarca `F0BF0F80` são "modelo 1" com detalhes
  diferentes. Para onde cada ponteiro aponta dentro do arquivo depende da base
  de carga do overlay, que **não foi medida** (§8).
- A planilha usa um só valor por modelo ao regravar — modelo 1 = `A0BA0F80`
  (o de Inglaterra), 2 = `74BE0F80` (Itália), 3 = `B0B90F80` (Escócia), 4 =
  `2CC50F80` (Croácia), 5 = `ECBE0F80` (R. Checa), 6 = `28BA0F80` (Gales), 7 =
  `80EE0F80` (Feyenoord), 8 = `70D70F80` (Japão) — e o
  `EditorUniformesWE2002.exe` do ramonpsx guarda exatamente esses oito, em
  decimal (`160 186 15 128` = `A0BA0F80`), para gravar nos quatro primeiros
  times. É a mesma tabela, portanto; o `.exe` é a planilha com botão.

O que cada ponteiro escolhe, segundo o tutorial: camisa, gola, calção, mangas e
detalhes — "los indicadores de uniformes 2D indican camiseta, cuello, pantalón,
mangas y detalles". Ele prova por troca: pôs o ponteiro e a paleta de Croácia
em Irlanda e os dois times passaram a mostrar o mesmo uniforme sem mexer em
gráfico nenhum.

### 2.3 Os gráficos: `DATSEL.BIN`, streams 21/22/23, com a paleta 7 do `DAT2D.BIN`

O tutorial descreve as três imagens assim:

- **imagem 22**: as camisas e as golas; no canto inferior esquerdo, a parte de
  baixo da camisa; no canto superior direito, detalhes que se sobrepõem; os
  números marcam os oito modelos, parte de cima e parte de baixo;
- **imagem 23**: no canto superior esquerdo, os calções; no superior direito, o
  gráfico que dá a sombra ao uniforme; embaixo, mangas longas, mais golas e
  detalhes;
- **imagem 24**: golas e mangas longas.

E recomenda a paleta 7 do `Dat2d.bin` para vê-las, "porque los 16 colores son
diferentes, no se repite ninguno".

O `DATSEL.BIN` está no LBA 6000, 223.496 bytes, **idêntico** no disco japonês e
na `golden-european-deluxe` (§7, snippet 2). O
[`bin_archive.py`](../tools/pes2/bin_archive.py) acha nele **0 imagens e 0
CLUTs**: é um contêiner de outro leiaute, já anotado na §1.14 do
[PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md) para os `DATSEL*` do PES2 — começa com
um cabeçalho de quatro ponteiros de RAM (`80125DA8 80126118 801264E0 801268E8`)
e os registros do fim do arquivo guardam ponteiro em vez de offset. O
[`lzss.py`](../tools/pes2/lzss.py), que não depende do índice, varre **56
streams**, 46 deles de 8.192 bytes — o tamanho de uma imagem 128×128 a 4 bpp.

Os três `.bmp` de `Modelos/Original/` são **byte a byte** os streams de índice
**21, 22 e 23** dessa varredura (offsets 126536, 129208 e 132000 dentro do
arquivo), depois de duas conversões de formato e nenhuma de conteúdo: inverter a
ordem das linhas (o BMP guarda de baixo para cima) e trocar os nibbles de cada
byte (o BMP põe o pixel da esquerda no nibble alto; o PSX, no baixo). Então a
numeração "22, 23, 24" do Wecompressor é a mesma varredura, contada de 1.

A "paleta 7 do Dat2d.bin" também bateu. Os 16 RGB do `.act`, convertidos a
BGR555 (`0000 2900 ac00 2f01 d201 5602 f902 7c03 ff03 ff13 ff27 ff37 ff4b ff5b
ff6f ff7f`), aparecem em **`DAT2D.BIN` +68484** nos três discos. O `DAT2D.BIN`
do WE2002 tem 23 registros de imagem e **nenhum de CLUT** — a região de paleta
começa em 65876 e o contêiner não a indexa (§1.14 do PLAN-PES2-PSX) —, e 68484 −
65876 = 2608 não é múltiplo de 32: a numeração de paleta do WE Image Manager não
é `(offset − 65876) / 32`, e como ele conta não foi medido.

**O que não se sabe sobre os gráficos**: qual retângulo de VRAM cada um ocupa e
como o jogo compõe camisa + gola + calção + sombra a partir deles. O polipoli
edita trocando o desenho inteiro e apagando com preto `000` tudo que se sobrepõe
(golas, detalhes, mangas longas) — "lo malo de esto es que no van a aparecer las
mangas largas en el menú de partido, pero es un mal menor". É o custo de não
saber a composição.

---

## 3. Radar: os pontinhos (SimoSapo)

O `GuidaRadar.htm` do SimoSapo, que o FratelConiglio anexa porque o
`Shirt_Preview.exe` incorporou a função, diz: no `SELECT.BIN`, offset
hexadecimal **3F534**, começam as cores dos pontinhos do radar dos uniformes
*home*, 2 bytes por time, o primeiro é o da Eire (`E003`, verde); em **3F634**
os dos uniformes *away*, o primeiro `FF7F` (branco). Só oito cores servem:

| cor | BGR555 |
|---|---|
| Bianco | `FF7F` |
| Nero | `2104` |
| Verde | `E003` |
| Giallo | `FF03` |
| Rosso | `1F00` |
| Blu | `007C` |
| Celeste | `E07F` |
| Violetto | `1F7C` |

E a regra de uso: quando dois times têm o mesmo pontinho *home* (ou cores
parecidas — rosso/violetto), a CPU veste o segundo uniforme no visitante; por
isso, dois times com a mesma camisa devem ter o **mesmo** pontinho *home*, e
nunca um par *home*/*away* entre bianco–celeste, celeste–giallo, bianco–giallo
ou rosso–violetto.

**Bateu no disco original.** `SELECT.BIN` (LBA 850) +0x3F534 no japonês e no
`ptbr-remaster` começa `E003 007C 1F00 FF7F` — verde para o time 0, que é a
Irlanda nos dois —, e +0x3F634 começa `FF7F FF7F FF7F 1F00` (§7, snippet 3). Na
`golden-european-deluxe` começa `007C 2104 1F00 1F00`: editado, como os times.
Os `0x100` bytes entre as duas tabelas comportam 128 times; os 95 ocupam 190.

O radar não é "uniforme 2D", mas a comunidade o trata junto porque é o terceiro
dado que precisa concordar com o uniforme: paleta 2D, textura 3D e pontinho.

---

## 4. Shirt Preview (FratelConiglio)

O `README.TXT`, na íntegra:

> Questo programma è sullo stile di WE Painter di Obocaman, da cui ho preso
> spunto, in questo caso però, serve solo per modificare la preview delle maglia
> Home e Away prima di una partita amichevole tra le squadre nazionali oppure
> quando si sceglie la squadra della ML. C'è da precisare un particolare però,
> cioè quello che in WE è possibile cambiare solo il colore dell'anteprima maglia
> e non il tipo, quindi l'immagine inserita nel programma, che rappresenta una
> maglia serve solo come guida, poichè le zone colorate che andremo a modificare
> sono diverse per alcune maglie delle varie squadre. Per questo motivo quando
> importiamo una maglia nel gioco, questa potrà apparire diversa da come era
> rappresentata in precedenza per un'altra squadra. A proposito
> dell'importazione delle maglie, il file .ADD che aprite contiene sia la maglia
> Home sia quella Away, però il salvataggio della modifica è indipendente per i
> due tipi di maglia, cioè in poche parole per ogni squadra dovrete salvare due
> volte la modifica sia per la maglia Home sia per quella Away in modo da
> lasciarvi liberi di sceglierne anche una sola e non tutte due insieme. In
> ultimo vorrei ringraziare Adesy che è stato così gentile poichè mi ha rivelato
> gli offset e le caratteristiche della preview delle maglie.
>
> Aggiunta la possibilità di cambiare il colore dei pallini nel radar che è
> fondamentale per l'abbinamento dei colori delle maglie 3D, per cui ringrazio
> SimoSapo per l'ottimo documento pubblicato sul sito WE Group, di cui allego
> una copia per chi non l'avesse ancora letto.
>
> P.S. Se avete problemi con i files Ocx, nel senso che il programma non dovesse
> funzionare dovete registrarli (chi ha win98 o ME deve registrarli nella
> cartella SYSTEM, chi ha winXP deve farlo nella cartella SYSTEM32). Per
> registrare il file, dovete fare "start"-->"Esegui"-->"regsvr32
> c:\windows\system32\nome file
>
> Per qualsiasi errore, problema e consigli per miglioramenti contattatemi
> all'indirizzo: fratel_coniglio@inwind.it
>
> by FratelConiglio

Três coisas a tirar dele:

- **"Só a cor, não o tipo."** É a mesma limitação do `FlagKitDialog` e do PAINT
  do Obocaman: todos editam a paleta da §2.1. A imagem de camisa que o programa
  mostra "serve solo come guida" — o desenho real é o do ponteiro da §2.2, que
  nenhum dos três editores toca. O polipoli, anos depois, é quem mexe no
  ponteiro e no gráfico.
- **O `.ADD`** é um export de texto: `PS_       .ADD` são 120 caracteres
  hexadecimais numa linha, 60 bytes, **30 palavras BGR555 = 15 da Home + 15 da
  Away** — as palavras 1..15 de cada paleta, a convenção do Obocaman, de quem
  ele diz ter tirado a ideia. Começa `4208 E015 E015 9C73 …`: o `4208` é a
  palavra 1 constante da §2.1, e `E015 E015 9C73 E015` são as palavras 2..5 da
  Irlanda no disco original (§7, snippet 1, `IRL home` do japonês). O arquivo é
  a Irlanda exportada. Compare com o `.m2002` do port (`f.m.magl` + 16 palavras,
  40 bytes, binário): outro formato para o mesmo dado.
- O `.exe` abre `.bin` CDRWIN ou `.img` CloneCD, lista os times por nome
  (contém os bytes `82 60..82 9A` e `81 44`, letras e ponto de largura dupla em
  Shift-JIS — ele lê os nomes do disco japonês), e guarda as oito cores de radar
  da §3 com os valores. Os offsets dele não aparecem como string; a planilha e o
  `wte/re/` suprem.

---

## 5. O fluxo da comunidade

Dois fluxos, de épocas diferentes, com alcances diferentes.

**Recolorir (GOKUW11, §8a da Bíblia; e o FratelConiglio).** Abrir a ISO no WE
Team Editor, escolher o time, clicar em PAINT, escolher 2D SHIRTS e HOME ou AWAY,
mexer nas 16 cores da barra, Accept, testar no ePSXe. O `.doc` do GOKUW11 é esse
texto com nove figuras, "Tutorial Retirado de W11.com.br … Copyright © por
WEleven.com.br". Mexe só na paleta da §2.1. É o que o `FlagKitDialog` do port
faz também, sem desenhar a camisa.

**Trocar o desenho (polipoli).** O fluxo dele, nas palavras do tutorial:

1. Exportar as imagens 22, 23 e 24 do `Datsel.bin` com o **Wecompressor**, com a
   paleta 7 do `Dat2d.bin` carregada.
2. Apagar com preto `000` golas, detalhes e mangas longas — tudo que se sobrepõe
   e complica —, deixando camisas, calções e a sombra.
3. Desenhar o modelo novo. Ele substituiu os oito originais por um só modelo "como
   el uniforme 2D del Pes2008, que es una idea que me dio zeta", em quatro
   variantes de camisa que cobrem qualquer time — **vertical** (Atlético de Madrid,
   Real Madrid, Galatasaray, PSG), **horizontal** (Celtic, Real Madrid, Boca),
   **diagonal** (Croácia, Atlético, Celtic, River, Real Madrid) e **total** (todos
   os anteriores mais PSG e Boca) — e o modelo 4 repetido nas vagas 5 a 8. Os
   seis `Camiseta/0N - Modelo *.bmp` de 40×32 são essas peças, mais dois
   "especiais"; pintados com `16 colores diferentes.act` para as zonas não se
   confundirem. Calção e meião são sempre os mesmos.
4. Reinserir com o Wecompressor; colorir com o **WE Image Manager**
   ("gravar bin"); trocar o `Select2.bin` na ISO com o **CDMage**.
5. Se um time precisa de outro modelo, trocar o ponteiro da §2.2 — pela aba
   "Cambiar modelos" da planilha e um editor hexadecimal, ou pelo `.exe` do
   ramonpsx para os quatro primeiros times.

A reinserção pelo Wecompressor é a mesma ferramenta que o
[SUPERPACK-UNIFORMES.md](/docs/SUPERPACK-UNIFORMES.md) §4.3 registra como a que
"corrompe no console" para TEX; se o mesmo vale para o `DATSEL.BIN`, ninguém
disse. Fica na §8.

---

## 6. O que o repositório já tinha, e onde bate

| o repositório | onde | o que a pasta diz | veredito |
|---|---|---|---|
| `OFS_KIT_PREVIEW` 2667256, `_A` 2669544, `_B` 2671896, `_C` 2674248 (ex-`OFS_ANT_MAGLIE*`) | [`Offsets.hpp`](../src/core/include/we2002/Offsets.hpp); [`pes2-ofs-map.md`](/docs/samples/pes2-ofs-map.md) os põe em `/SELECT2.BIN` +172096/+174080/+176128/+178176 | "OFFSET U1" da planilha = 172096 + 64 × time | **bate** (§2.1) |
| `home_kit[16]`, `away_kit[16]` por time, 32 + 32 bytes | [`Team.hpp`](../src/core/include/we2002/Team.hpp), [`Database.cpp`](../src/core/Database.cpp) | U2 = U1 + 32 | **bate** |
| o diálogo expõe as palavras 2..15 | [`FlagKitDialog.hpp`](../src/app/FlagKitDialog.hpp) | o Obocaman expõe 1..15; o `.ADD` exporta 1..15 | **palavra 0 é `0000` e palavra 1 é `4208` nos originais** (§2.1); nenhum editor erra, só escolhem o que mostrar |
| `BASE_UNIFORME = 0x0025AEF8`, `LOGICO_UNIFORME_0 = 0x2A042`, `_1 = 0x2A062`, passo 64 | [`wte/tools/dump_blococor.py`](../wte/tools/dump_blococor.py) | idem | **bate**: 0x25AEF8 = LBA 1050 × 2352 + 24; 0x2A042 = 172096 + 2 |
| a forma da camisa 2D no editor do Obocaman vem de uma tabela do `.exe` (`0x004232a6`, 95 × 4, `(camiseta, pantalon)` por time e por uniforme), "não é lida da imagem de CD" | [`wte/re/assets.md`](../wte/re/assets.md) §4 | o ponteiro da §2.2 é o que o **jogo** lê; os 99 `camiseta*.bmp` do Obocaman são a reprodução dele em PC | **complementar**: duas classificações do mesmo dado (99 padrões dele × 8 modelos do polipoli × 190 ponteiros do disco), nenhuma derivada da outra — não comparadas (§8) |
| `ABS_PADRAO_CAMISA = 0x00DB3F7C`; combo NORMAL `00 65`, ROMBOIDAL `28 61`, EXTRA `00 64` | [`dump_blococor.py`](../wte/tools/dump_blococor.py), [`ficha_color.lista_col3Change.md`](../wte/re/spec/ficha_color.lista_col3Change.md) | nada na pasta | **medido agora**: 0xDB3F7C = 14368636 cai no **último setor do `DATSEL.BIN`** (LBA 6109, lógico 223476), e ali está `00 65 12 80` = o ponteiro `0x80126500`, nos três discos (§7, snippet 3). Os três valores do combo são a metade baixa de `0x80126500`, `0x80126128` e `0x80126400` — o editor troca para onde um registro do `DATSEL` aponta, dentro da faixa dos quatro ponteiros do cabeçalho. É o mesmo mecanismo da §2.2, do lado do gráfico |
| `ABS_QUARTA_PALETA = 0x00BF690C`, 30 bytes gravados | [`dump_blococor.py`](../wte/tools/dump_blococor.py), [`ficha_color.BitBtn3Click.md`](../wte/re/spec/ficha_color.BitBtn3Click.md) | nada na pasta | **medido agora**: 0xBF690C = 12544268 cai em `DAT2D.BIN` lógico **68612** = 68484 + 128, quatro paletas de 32 bytes depois da paleta 7, e é uma rampa de cinza `ffff efbd 10c2 … defb` (no `ptbr-remaster` a primeira entrada é `ff7f`, sem o bit 15). O que ela pinta não foi medido; a janela Paint tem uma aba "Nets", e redes são brancas |
| `DAT2D.BIN`: 23 imagens, 0 CLUTs indexadas, paletas a partir de 65876 | [PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md) §1.14 | "paleta 7 del Dat2d.bin" | **bate** em +68484 (§2.3); a contagem do WE Image Manager não foi decifrada |
| `DATSEL*.BIN`: "a geometria da entrada não está declarada em lugar nenhum do arquivo" | [PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md) §1.14 | imagens 22, 23, 24 | **bate**: `bin_archive.py` acha 0 registros; `lzss.py` acha os streams, e 21/22/23 são os `.bmp` (§2.3) |
| §8a da Bíblia | [/docs/biblia-we2002/08-uniformes.md](/docs/biblia-we2002/08-uniformes.md) | o `.doc` do GOKUW11 | **mesmo texto**, com figuras |
| o `kits` (ciclo vivo) e o `looks` lêem os `TEX_*.BIN` | [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md), [PLAN-LOOKS-PY.md](/docs/PLAN-LOOKS-PY.md) | nada: a pasta é só 2D | **fora de escopo** dos dois ciclos; nenhum lê `SELECT2.BIN` nem `DATSEL.BIN` |

---

## 7. Como reproduzir cada número

Tudo abaixo é só leitura e roda sobre os originais de `roms/`. No Git Bash, as
ferramentas de `tools/pes2/` que recebem caminho de dentro do ISO precisam de
`MSYS_NO_PATHCONV=1`.

**Os quatro arquivos, com LBA e tamanho** — iguais nos três discos:

```sh
MSYS_NO_PATHCONV=1 python tools/pes2/iso.py ls roms/golden-european-deluxe.bin \
  | grep -E '/(BIN/DAT2D|BIN/DATSEL|SELECT|SELECT2)\.BIN'
```

```
  /BIN/DAT2D.BIN                     lba=   5300 size=     81124 form1
  /BIN/DATSEL.BIN                    lba=   6000 size=    223496 form1
  /SELECT.BIN                        lba=    850 size=    300648 form1
  /SELECT2.BIN                       lba=   1050 size=    271540 form1
```

**O que o leitor de contêiner vê nos dois `BIN/`:**

```sh
MSYS_NO_PATHCONV=1 python tools/pes2/bin_archive.py ls roms/golden-european-deluxe.bin --file /BIN/DATSEL.BIN
MSYS_NO_PATHCONV=1 python tools/pes2/bin_archive.py ls roms/golden-european-deluxe.bin --file /BIN/DAT2D.BIN | head -1
```

```
/BIN/DATSEL.BIN          223496 B   0 image(s), 0 clut(s)
/BIN/DAT2D.BIN            81124 B   23 image(s), 0 clut(s)
```

**Snippet 1 — paletas e tabela de modelos** (§2.1, §2.2). Da raiz do repositório:

```sh
python3 - <<'PY'
import struct

LBA_SELECT2, SIZE_SELECT2 = 1050, 271540      # iso.py ls
OFS_KIT_PREVIEW_REL = 172096                  # docs/samples/pes2-ofs-map.md
TABELA_MODELOS_REL = 225808                   # 2728872 raw, convertido abaixo


def read_file(img, lba, size):
    out = bytearray()
    with open(img, "rb") as f:
        while len(out) < size:
            f.seek(lba * 2352 + 24)
            out += f.read(2048)
            lba += 1
    return bytes(out[:size])


def raw(lba, logical):
    return lba * 2352 + (logical // 2048) * 2352 + 24 + (logical % 2048)


print("raw(SELECT2 +172096) =", raw(LBA_SELECT2, OFS_KIT_PREVIEW_REL), "(OFS_KIT_PREVIEW)")
print("raw(SELECT2 +225808) =", raw(LBA_SELECT2, TABELA_MODELOS_REL), "(offset ISO do polipoli)")

for name in ("golden-european-deluxe", "japanese-shift-jis", "ptbr-remaster"):
    s2 = read_file(f"roms/{name}.bin", LBA_SELECT2, SIZE_SELECT2)
    w0, w1 = set(), set()
    for team in range(95):
        for kit in (0, 32):
            o = OFS_KIT_PREVIEW_REL + 64 * team + kit
            w0.add(s2[o:o + 2].hex())
            w1.add(s2[o + 2:o + 4].hex())
    t = s2[TABELA_MODELOS_REL:TABELA_MODELOS_REL + 760]
    v = [struct.unpack_from("<I", t, i)[0] for i in range(0, 760, 4)]
    print(f"{name}:")
    print("  IRL home:", s2[OFS_KIT_PREVIEW_REL:OFS_KIT_PREVIEW_REL + 32].hex())
    print("  palavra 0:", sorted(w0), " palavra 1:", sorted(w1))
    print("  modelos IRL %08X %08X  ING %08X  BOCA %08X %08X" % (v[0], v[1], v[6], v[188], v[189]))
    print("  distintos:", len(set(v)), " faixa: %08X..%08X" % (min(v), max(v)))
PY
```

```
raw(SELECT2 +172096) = 2667256 (OFS_KIT_PREVIEW)
raw(SELECT2 +225808) = 2728872 (offset ISO do polipoli)
golden-european-deluxe:
  IRL home: 000042088165816508218165082108210821734e082108218165816508218165
  palavra 0: ['0000']  palavra 1: ['0000', '0208', '2104', '4208', 'a514', 'c61c']
  modelos IRL 800FB8AC 800FB8FC  ING 800FBAA0  BOCA 800FFEF4 8010000C
  distintos: 190  faixa: 800FB8AC..8010000C
japanese-shift-jis:
  IRL home: 00004208e015e0159c73e015e015e015e015734ee0155a6b5a6b31465a6be015
  palavra 0: ['0000']  palavra 1: ['4208']
  modelos IRL 800FB8AC 800FB8FC  ING 800FBAA0  BOCA 800FFEF4 8010000C
  distintos: 190  faixa: 800FB8AC..8010000C
ptbr-remaster:
  IRL home: 00004208e015e0159c73e015e015e015e015734ee0155a6b5a6b31465a6be015
  palavra 0: ['0000']  palavra 1: ['4208']
  modelos IRL 800FB8AC 800FB8FC  ING 800FBAA0  BOCA 800FFEF4 8010000C
  distintos: 190  faixa: 800FB8AC..8010000C
```

**Snippet 2 — os streams do `DATSEL.BIN` contra os `.bmp` do polipoli, e a
paleta 7** (§2.3). Precisa da pasta do Superpack no caminho de `SUPERPACK`:

```sh
python3 - <<'PY'
import struct, sys
sys.path.insert(0, "tools/pes2")
import lzss

SUPERPACK = r"C:\games\we2002\Superpackv6\We2002\Uniformes 2D\Uniformes 2D - polipoli"
LBA_DATSEL, SIZE_DATSEL = 6000, 223496
LBA_DAT2D, SIZE_DAT2D = 5300, 81124


def read_file(img, lba, size):
    out = bytearray()
    with open(img, "rb") as f:
        while len(out) < size:
            f.seek(lba * 2352 + 24)
            out += f.read(2048)
            lba += 1
    return bytes(out[:size])


def bmp_4bpp_topdown(path):
    b = open(path, "rb").read()
    off = struct.unpack_from("<I", b, 10)[0]
    w, h = struct.unpack_from("<ii", b, 18)
    stride = ((w * 4 + 31) // 32) * 4
    rows = [b[off + r * stride: off + r * stride + stride] for r in range(h)]
    return b"".join(reversed(rows)), (w, h)


def swap_nibbles(d):
    return bytes(((x & 0xF) << 4) | (x >> 4) for x in d)


golden = read_file("roms/golden-european-deluxe.bin", LBA_DATSEL, SIZE_DATSEL)
jp = read_file("roms/japanese-shift-jis.bin", LBA_DATSEL, SIZE_DATSEL)
print("DATSEL.BIN golden == jp:", golden == jp)
print("cabecalho:", ["%08X" % w for w in lzss.header_words(jp)])
blocks = lzss.scan(jp)
print("streams:", len(blocks), " de 8192 bytes:", sum(1 for b in blocks if b[2] == 8192))
decoded = {i: lzss.decompress(jp, off)[0] for i, (off, used, plain) in enumerate(blocks) if plain == 8192}
for n in (22, 23, 24):
    pix, dims = bmp_4bpp_topdown(rf"{SUPERPACK}\Modelos\Original\{n} - 7.bmp")
    hits = [i for i, p in decoded.items() if swap_nibbles(p) == pix]
    hits_raw = [i for i, p in decoded.items() if p == pix]
    print(f"  polipoli {n} - 7.bmp {dims}: stream {hits} (nibble trocado), {hits_raw} (cru)",
          "offset", [blocks[i][0] for i in hits])

act = open(rf"{SUPERPACK}\Paleta 7 DAT2D.act", "rb").read()
to555 = lambda r, g, b: (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)
seq = b"".join(struct.pack("<H", to555(*act[i * 3:i * 3 + 3])) for i in range(16))
print("paleta 7 em BGR555:", seq.hex())
for name in ("golden-european-deluxe", "japanese-shift-jis", "ptbr-remaster"):
    d2 = read_file(f"roms/{name}.bin", LBA_DAT2D, SIZE_DAT2D)
    i = d2.find(seq)
    print(f"  {name}: DAT2D.BIN +{i}", " (+128):", d2[i + 128:i + 160].hex() if i >= 0 else "-")
PY
```

```
DATSEL.BIN golden == jp: True
cabecalho: ['80125DA8', '80126118', '801264E0', '801268E8']
streams: 56  de 8192 bytes: 46
  polipoli 22 - 7.bmp (128, 128): stream [21] (nibble trocado), [] (cru) offset [126536]
  polipoli 23 - 7.bmp (128, 128): stream [22] (nibble trocado), [] (cru) offset [129208]
  polipoli 24 - 7.bmp (128, 128): stream [23] (nibble trocado), [] (cru) offset [132000]
paleta 7 em BGR555: 00002900ac002f01d2015602f9027c03ff03ff13ff27ff37ff4bff5bff6fff7f
  golden-european-deluxe: DAT2D.BIN +68484  (+128): ffffefbd10c231c652ca94d2b5d6d6daf7de18e339e75aeb7befbdf7defb0000
  japanese-shift-jis: DAT2D.BIN +68484  (+128): ffffefbd10c231c652ca94d2b5d6d6daf7de18e339e75aeb7befbdf7defb0000
  ptbr-remaster: DAT2D.BIN +68484  (+128): ff7fefbd10c231c652ca94d2b5d6d6daf7de18e339e75aeb7befbdf7defb0000
```

**Snippet 3 — radar, padrão de camisa e quarta paleta** (§3, §6):

```sh
python3 - <<'PY'
LBA_SELECT, SIZE_SELECT = 850, 300648
ABS_PADRAO_CAMISA = 0x00DB3F7C    # wte/tools/dump_blococor.py
ABS_QUARTA_PALETA = 0x00BF690C


def read_file(img, lba, size):
    out = bytearray()
    with open(img, "rb") as f:
        while len(out) < size:
            f.seek(lba * 2352 + 24)
            out += f.read(2048)
            lba += 1
    return bytes(out[:size])


def where(absolute):
    lba, rest = divmod(absolute, 2352)
    return lba, rest - 24


for name in ("golden-european-deluxe", "japanese-shift-jis", "ptbr-remaster"):
    img = f"roms/{name}.bin"
    sel = read_file(img, LBA_SELECT, SIZE_SELECT)
    with open(img, "rb") as f:
        f.seek(ABS_PADRAO_CAMISA - 4); padrao = f.read(12)
        f.seek(ABS_QUARTA_PALETA); quarta = f.read(32)
    print(f"{name}:")
    print("  radar home +0x3F534:", sel[0x3F534:0x3F534 + 8].hex(), " away +0x3F634:", sel[0x3F634:0x3F634 + 8].hex())
    print("  ABS_PADRAO_CAMISA -4..+8:", padrao.hex())
    print("  ABS_QUARTA_PALETA:", quarta.hex())

for label, a in (("ABS_PADRAO_CAMISA", ABS_PADRAO_CAMISA), ("ABS_QUARTA_PALETA", ABS_QUARTA_PALETA)):
    lba, inner = where(a)
    print(f"{label} = {a}: LBA {lba}, byte {inner} do dado")
print("  DATSEL.BIN = LBA 6000..6109 -> logico", (6109 - 6000) * 2048 + where(ABS_PADRAO_CAMISA)[1])
print("  DAT2D.BIN  = LBA 5300..5339 -> logico", (5333 - 5300) * 2048 + where(ABS_QUARTA_PALETA)[1])
PY
```

```
golden-european-deluxe:
  radar home +0x3F534: 007c21041f001f00  away +0x3F634: ff7fff7fff7fff7f
  ABS_PADRAO_CAMISA -4..+8: 8000000000651280ff000000
  ABS_QUARTA_PALETA: ffffefbd10c231c652ca94d2b5d6d6daf7de18e339e75aeb7befbdf7defb0000
japanese-shift-jis:
  radar home +0x3F534: e003007c1f00ff7f  away +0x3F634: ff7fff7fff7f1f00
  ABS_PADRAO_CAMISA -4..+8: 8000000000651280ff000000
  ABS_QUARTA_PALETA: ffffefbd10c231c652ca94d2b5d6d6daf7de18e339e75aeb7befbdf7defb0000
ptbr-remaster:
  radar home +0x3F534: e003007c1f00ff7f  away +0x3F634: ff7fff7fff7f1f00
  ABS_PADRAO_CAMISA -4..+8: 8000000000651280ff000000
  ABS_QUARTA_PALETA: ff7fefbd10c231c652ca94d2b5d6d6daf7de18e339e75aeb7befbdf7defb0000
ABS_PADRAO_CAMISA = 14368636: LBA 6109, byte 244 do dado
ABS_QUARTA_PALETA = 12544268: LBA 5333, byte 1028 do dado
  DATSEL.BIN = LBA 6000..6109 -> logico 223476
  DAT2D.BIN  = LBA 5300..5339 -> logico 68612
```

Os três snippets são sonda, não ferramenta: a regra da casa diz que número que
entra em documento vem de ferramenta versionada, e a forma de honrar isso aqui
foi deixá-los inteiros no texto, como o [`wte/re/assets.md`](../wte/re/assets.md)
§4.1 faz. Promovê-los a `--check` de uma ferramenta de `tools/` é o primeiro
item da §8.

---

## 8. O que ficou de fora e o que continua aberto

- **Uma ferramenta versionada** com `--check` que reproduza os três snippets —
  paletas, tabela de ponteiros, os 56 streams e o casamento com os `.bmp`, a
  paleta 7, o radar. Cabe no ciclo `kits` ou num ciclo próprio; não é deste doc.
- **Para onde apontam os 190 ponteiros.** `0x800FB8AC..0x8010000C` é dentro do
  `SELECT2.BIN` carregado; a base de carga do overlay não foi medida, então o
  offset de arquivo de cada "modelo" e a estrutura dele (camisa, gola, calção,
  mangas, detalhes — os cinco campos que o polipoli infere) continuam por ler. O
  `savestate.py` e o fork do DuckStation de `tools/pes2/` são o caminho.
- **O leiaute do `DATSEL.BIN`.** Cabeçalho de quatro ponteiros `0x8012xxxx`,
  registros no fim do arquivo com ponteiro no lugar do offset (`00 65 12 80` no
  lógico 223476 é um deles). O `bin_archive.py` não os lê; a §1.14 do
  [PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md) já o tinha como limite. Quais
  retângulos de VRAM as 46 imagens de 8.192 bytes ocupam, e como o jogo compõe
  camisa + gola + calção + sombra, é o que falta para editar sem apagar as golas.
- **Os três ponteiros do combo do Obocaman** (`0x80126500`, `0x80126128`,
  `0x80126400`): o que cada um escolhe no desenho não foi visto na tela.
- **A quarta paleta** (`DAT2D.BIN` +68612): a hipótese "Nets" vem da aba da
  janela Paint e da rampa de cinza, nada mais.
- **A contagem de paletas do WE Image Manager**: "paleta 7" está em +68484, e
  o passo desde 65876 não é 32.
- **As três classificações de forma** — os 99 `camiseta*.bmp` do Obocaman
  (tabela 95 × 4 do `.exe`), os 8 modelos do polipoli, os 190 ponteiros do
  disco — nunca foram postas lado a lado. Se a tabela do Obocaman for uma função
  do ponteiro, ela é uma leitura da composição que ninguém documentou.
- **A palavra 1 = `0x0842`** e a **palavra 0 = `0x0000`**: o que pintam. O
  `ed.exe` esconde as duas; o Obocaman mostra a 1.
- **Nada foi conferido na tela do emulador** — nem que a paleta da §2.1 é a que
  a tela de opções usa, nem o efeito de trocar um ponteiro. Todo veredito
  "bate" acima é bate **com o disco** e com a leitura dos editores, não com o
  quadro do jogo.
- **Wecompressor e o console.** O §4.3 do
  [SUPERPACK-UNIFORMES.md](/docs/SUPERPACK-UNIFORMES.md) mede que o TEX montado
  por ele quebra no console; para o `DATSEL.BIN` ninguém mediu.
- `Remeras test - pascutti.bmp`: sem texto que o acompanhe; não se sabe o que
  testa.
- Os dois `.exe` não foram executados; tudo que se diz deles saiu das strings.

---

## 9. Créditos e procedência

- **polipoli** — tutorial, planilha de offsets, os três `.bmp` originais e os
  editados, as duas paletas `.act`. Agradece a **zeta** pela ideia do modelo
  PES 2008. O `.doc` registra 2008 na criação e 2017 na última edição.
- **GOKUW11** — tutorial do PAINT, "Tutorial Retirado de W11.com.br", copyright
  WEleven.com.br.
- **ramonpsx / RAHZ Software** — `EditorUniformesWE2002.exe`.
- **FratelConiglio** — `Shirt_Preview.exe` e `README.TXT`; os offsets são de
  **Adesy**; a ideia é do WE Painter do **Obocaman**.
- **SimoSapo** — `GuidaRadar.htm`, publicado no site WE Group.
- **pascutti** — `Remeras test - pascutti.bmp`.
- Ferramentas citadas, de outros autores: Wecompressor (Walxer), WE Image
  Manager (Bat), CDMage, WE Team Editor e WE Painter (Obocaman).

Nenhum destes concedeu licença, e nada da pasta foi copiado para o repositório:
os números e os trechos citados acima são o que este documento guarda. A regra
é a do [NOTICE.md](../NOTICE.md), a mesma de `roms/` e do `we-team-editor.exe`.
