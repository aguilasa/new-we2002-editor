# PES2 — nomes fictícios e seus originais

> Apêndice de [/docs/PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md). Traz o que o
> disco **não** guarda: a correspondência entre o nome fictício de cada clube
> e o clube real.
>
> Medido/verificado em 2026-08-30 sobre
> `roms/Pro Evolution Soccer 2 (Europe) (EsIt)`, `SLES-03957`.

---

## Procedência, e o que é medido contra o que é de terceiro

Duas colunas de natureza diferente convivem aqui, e a distinção importa:

| Coluna | Origem | Confiança |
|---|---|---|
| índice, nome no disco, abreviação, offset | **lido do disco** | fato |
| clube real | **dois FAQs de terceiros** | consenso de duas fontes, não verificável no disco |

Os FAQs são:

- **BigCj34**, *Pro Evolution Soccer 2 FAQ for PSone*, v6, jan/2004 —
  `docs/Pro Evolution Soccer 2 FAQ for PSone.md`, seção 3;
- **Denis Dzanic**, *Pro Evolution Soccer 2*, v2.00, 2003 —
  `docs/Pro Evolution Soccer 2.md`, capítulo Master League.

O segundo credita ~70% dos nomes ao primeiro, então **não são independentes**.
Ainda assim os dois foram comparados linha a linha: **concordam nos 32
clubes**. As divergências são de grafia, não de identificação — "Bayern
Munich" × "Bayern Munchen", "Dinamo Kiev" × "Dynamo Kyev", "Inter Milan" ×
"Internazionale". Onde discordaram na grafia do **nome do disco**, quem
decidiu foi o disco: `PATAGONIA` (BigCj34 escreveu "Pantagonia"),
`VASCONGADAS` ("Vasgongadas"), `NOORDZEEKANAAL` ("Noordzeenkanaal").

Nenhum arquivo de FAQ entra no versionamento — são obra de terceiro,
com nota de copyright própria, e o segundo diz literalmente *"may not be
published"*. Ficam no disco do usuário, como `roms/`. Os `.txt` originais
foram convertidos em Markdown por `tools/pes2/faq2md.py` (sem perda de
conteúdo, conferido por contagem de palavras) e **descartados**; se for
preciso reconverter, os originais têm de ser baixados de novo.

---

## A ordem do disco é o inverso da ordem das listas

Verificação que dá confiança à tabela abaixo: as duas listas de FAQ
aparecem em **ordem exatamente inversa à do disco**. Casando por índice,
**30 dos 32 clubes caem na posição prevista** (`FAQ[31-i] == disco[i]`).

Os dois que não caem são `MEDOC` e `NORMANDIE`, transpostos **na lista do
BigCj34**. A lista do Dzanic os traz na ordem do disco, e os dois FAQs
concordam no mapeamento (`MEDOC` = Bordeaux, `NORMANDIE` = PSG) — é erro
de ordem de digitação, não ambiguidade.

A mesma inversão vale para os elencos **de `SELECTC.BIN`**: a Irlanda ali
termina em `Given` (goleiro), enquanto os FAQs a começam por `Given`. Um
editor que mostre essa lista na ordem do arquivo apresenta o goleiro por
último.

**Mas a inversão não é regra do disco.** Medido em 2026-08-30 contra o
memory card do DuckStation, que guarda os 54 elencos rotulados: os 49 que
moram em `SELECTC.BIN` estão invertidos, e a França e a Alemanha, que
moram em `SLES_039.57`, estão na ordem direta. A ordem é propriedade da
tabela, e o mapa tem de declará-la por tabela — como já acontece com o
esquema de registro. Ver a §3.3 do plano.

O agrupamento por liga confirma a leitura: os seis últimos índices são os
clubes ingleses, os cinco anteriores os espanhóis, e assim por diante —
apesar de os nomes fictícios não respeitarem geografia (`LIGURIA` é o
Chelsea, `ARAGON` é o Manchester United).

---

## Os 32 clubes

Índice, nome e offset saem de `SELECT.BIN` da imagem `(EsIt)`; os mesmos
offsets valem para `(EnFrDe)`, conferido.

| # | nome no disco | abrev. | offset | clube real | liga |
|---:|---|---|---:|---|---|
| 0 | `PATAGONIA` | `PTA` | 3148 | Boca Juniors | Argentina |
| 1 | `MARMARA` | `MRA` | 3160 | Dínamo Kiev | Ucrânia |
| 2 | `BYZANTINOBUL` | `BZA` | 3168 | Galatasaray | Turquia |
| 3 | `PELOPONNISOS` | `PNS` | 3184 | Olympiakos | Grécia |
| 4 | `RUHR` | `RUR` | 3200 | Bayer Leverkusen | Alemanha |
| 5 | `ANHALT` | `AHT` | 3208 | Bayern de Munique | Alemanha |
| 6 | `WESTFALEN` | `WES` | 3216 | Borussia Dortmund | Alemanha |
| 7 | `ABRUZZI` | `ABR` | 3228 | Roma | Itália |
| 8 | `TOSCANA` | `TSC` | 3236 | Fiorentina | Itália |
| 9 | `EMILIA` | `EML` | 3244 | Parma | Itália |
| 10 | `UMBRIA` | `UMB` | 3252 | Lazio | Itália |
| 11 | `LOMBARDIA` | `LBD` | 3260 | Milan | Itália |
| 12 | `PIEMONTE` | `PMT` | 3272 | Juventus | Itália |
| 13 | `MARCHE` | `MRC` | 3284 | Internazionale | Itália |
| 14 | `FLANDRE` | `FLD` | 3292 | PSV Eindhoven | Países Baixos |
| 15 | `NOORDZEEKANAAL` | `NZK` | 3300 | Feyenoord | Países Baixos |
| 16 | `RIJNKANAAL` | `RNK` | 3316 | Ajax | Países Baixos |
| 17 | `MEDOC` | `MDC` | 3328 | Bordeaux | França |
| 18 | `NORMANDIE` | `NMA` | 3336 | Paris Saint-Germain | França |
| 19 | `LANGUEDOC` | `LNG` | 3348 | Olympique de Marselha | França |
| 20 | `PROVENCE` | `PRO` | 3360 | Monaco | França |
| 21 | `CANTABRIA` | `CNT` | 3372 | Deportivo La Coruña | Espanha |
| 22 | `ANDALUCIA` | `AND` | 3384 | Valencia | Espanha |
| 23 | `NAVARRA` | `NAV` | 3396 | Real Madrid | Espanha |
| 24 | `CATALUNA` | `CTL` | 3404 | Barcelona | Espanha |
| 25 | `VASCONGADAS` | `VAS` | 3416 | Aston Villa | Inglaterra |
| 26 | `HIGHLANDS` | `HGL` | 3428 | Newcastle United | Inglaterra |
| 27 | `YORKSHIRE` | `YOK` | 3440 | Leeds United | Inglaterra |
| 28 | `EUROPORT` | `ERO` | 3452 | Liverpool | Inglaterra |
| 29 | `LIGURIA` | `LIG` | 3464 | Chelsea | Inglaterra |
| 30 | `LONDON` | `LDN` | 3472 | Arsenal | Inglaterra |
| 31 | `ARAGON` | `AGN` | 3480 | Manchester United | Inglaterra |

---

## O que os FAQs **não** resolvem

### Grafia de jogador: só para uma minoria dos times

O FAQ do BigCj34 traz os 63 elencos de seleção, 23 jogadores cada — 1.449
nomes. Mas **em quase todos ele dá apenas o nome correto**, não a grafia
que está no jogo. Só sete times trazem as duas colunas (`grafia do jogo` →
`nome real`): Wales, Holland, Czech Republic, South Korea, Saudi Arabia e
as sete seleções "clássicas".

Para os demais o FAQ é uma lista de *o que digitar no Edit Mode*, não um
mapa. Um editor não consegue rotular automaticamente `Navdid` como
"Nedved" a partir dele, exceto nesses sete.

Consequência prática: o alinhamento automático FAQ × disco casou **27 dos
63 elencos com 20 ou mais dos 23 nomes**, e 8 com os 23. O resto falha por
grafia divergente, não por o elenco ser outro.

### Clube nenhum tem elenco listado

Nenhum dos dois FAQs lista quem joga em `PIEMONTE`. O primeiro explica por
quê: **jogador de clube não é editável no PES2 de PSone**, então ninguém
teve motivo para tabelar. Ligar jogador a clube continua sendo trabalho da
Fase 3 do plano.

---

## Dois achados que os FAQs entregaram de brinde

### O elenco inicial da Master League

O FAQ do Dzanic lista os 23 jogadores com que toda Master League começa,
qualquer que seja o clube escolhido: Ivanov, Stromer, Daric, Valery,
Iorga, Cellini, Ximenes, Espinas, Miranda, Castello, Baroja, Cecil,
Vorlander, Eddington, Nachtegall, Harty, Matt, Ostwald, Burchet, Njord,
Oranges102, Kelsen, Zamenhof.

Vinte e um dos 23 foram encontrados em `SELECT.BIN`, **no mesmo offset nas
duas releases**. Os dois "ausentes" não faltam — são o achado seguinte.

### Uma segunda tabela de nomes, e ela é de largura fixa

`Nachtegall` e `Oranges102` têm exatamente 10 caracteres e **não têm
terminador**: no disco lê-se `NachtegallHeggem` e
`Oranges102Cudicini` corridos. Isso descobriu uma tabela que o levantamento
anterior não tinha visto:

| | |
|---|---|
| arquivo | `SELECT.BIN` |
| offset | **5320 … 9950** (idêntico nas duas releases) |
| registro | **10 bytes fixos**, preenchidos com `NUL` à direita, **sem terminador quando cheios** |
| entradas | **463** |
| conteúdo | jogadores de clube — inclui `Yawke`, a grafia de Dwight Yorke que o FAQ do BigCj34 cita nominalmente |
| enchimento | 36 `OrangesNNN` (*placeholder*) e um rabo de `Dummy` |

Isto **contradiz a generalização** de que o PES2 usa registro de tamanho
variável. Ele usa os dois esquemas, em tabelas diferentes:

| Esquema | Onde | Consequência para o editor |
|---|---|---|
| variável, alinhado a 4, com `NUL` | nomes de time e a massa de `SELECTC.BIN` | nome novo não pode passar do slot |
| **fixo de 10 B, sem terminador** | `SELECT.BIN` 5320…9950 | nome novo cabe em 10 caracteres, e **escrever 10 sem `NUL` é o correto** |

O segundo caso é idêntico ao dos nomes de jogador do WE2002
(`Toldo\0\0\0\0\0`, 10 B), o que reforça a §1.4 do plano: a engine é a
mesma. E é uma armadilha real — um editor que sempre termine em `NUL`
corrompe o primeiro caractere do vizinho em todo nome de 10 letras.
