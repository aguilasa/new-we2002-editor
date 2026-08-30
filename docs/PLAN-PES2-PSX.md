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
> | Estado | **plano. Nenhuma fase executada.** A §1 é diagnóstico já medido. |
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
  nem nos `SD/*.RA` (117 MB de streaming). Nada de banco de dados mora ali.
- **Não** recalcular EDC/ECC. O `ed.exe` não recalcula e o jogo não confere;
  gravação in-place preservando os 280 bytes de cauda é a política herdada.
- **Não** decidir agora a linguagem nem a UI do editor. O mapa vem antes;
  sem ele não há o que a UI mostre.

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
mesmo tipo de conteúdo, offset relativo próximo. A Fase 2 transforma essa
lista em busca dirigida em vez de varredura cega.

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

| Tabela | cópias medidas |
|---|---|
| nomes de time (caixa alta) | `SELECT.BIN` @3128, `ENDING.BIN` @1256 |
| nomes de time (caixa mista) | `RESULT.BIN` @~304 (`Patagonia`, `Marmara`, …) |
| abreviações | `SELECT.BIN` @4292, `SELECT8.BIN` @1016, `REPLAYS.BIN` @11000 |

É o mesmo padrão do WE2002, onde o editor grava seis cópias de nome e três
de abreviação. **Gravar uma só cópia produz um jogo inconsistente**, com o
nome novo numa tela e o velho na outra.

**Nomes de jogador**, `SELECTC.BIN` offset relativo **20736**, em duas
famílias contíguas: os reais (`Bonano`, `Batistuta`, `Caniggia`, `Aimar`,
`Gallardo`, `Almeyda`, `Sorin`, `Placente`, `Pochettino`, `Sensini`,
`Ortega`, `C.Lopez`, `Crespo`, `Veron`, …) e, antes deles, os fictícios
(`Dalcorso`, `Kediaves`, `Mondiz`, `Chele`, `Obegone`, …). Uma segunda massa
de nomes fictícios vive no próprio executável, `SLES_039.57` @291750
(`Baser`, `Amabri`, `Emakrif`, …).

### 1.6 Contagem e ordem — medido, não estimado

A varredura fechou as tabelas de texto por inteiro. Estes são números
duros, não hipóteses:

| Tabela | Arquivo | Offset relativo | Entradas |
|---|---|---|---|
| nome de time, caixa alta | `SELECT.BIN` | 3128 | **106** (2 de cabeçalho + 104 times) |
| abreviação de 3 letras | `SELECT.BIN` | 4292 | **95** (registro fixo de 4 B) |
| nome de time, caixa mista | `SELECTC.BIN` | 16576 | **99** |
| nome de jogador | `SELECTC.BIN` | 17604 | **1.399** |
| nome de jogador (2ª massa) | `SLES_039.57` | ~288460 | continua além |
| jogador de clube, **10 B fixos** | `SELECT.BIN` | 5320 | **463** |

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

Uma coisa esse alinhamento já provou: **o disco guarda cada elenco na ordem
inversa da de exibição.** A Irlanda termina em `Given`, o goleiro, que os
FAQs listam primeiro. A mesma inversão vale para a lista de clubes. Ver
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
| **byte a byte idênticos** | **204** |
| diferem | 32 |
| exclusivos de cada lado | os `LC_*`/`T_NAME_*`/`DAT2D_*`/`FNOTE_*`/`DATSEL*` por idioma, os `SD/PES2*.RA` de narração, e o executável |
| executável | `SLES_039.57` (EsIt) × `SLES_039.46` (EnFrDe) |

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
só aparece uma vez no arquivo. Sete marcadores foram testados nas duas
releases e **todos ocorrem exatamente uma vez** em cada arquivo:

| Marcador | Arquivo | acha |
|---|---|---|
| `MASTER DATA\0` | `SELECT.BIN` | início da tabela de nome de time |
| `PTA\0MRA\0BZA\0` | `SELECT.BIN`, `SELECT8.BIN`, `REPLAYS.BIN` | as três cópias de abreviação |
| `PATAGONIA\0` | `ENDING.BIN` | cópia de nome de time |
| `Patagonia\0` | `RESULT.BIN` | cópia em caixa mista |
| `Belarus\0Georgia\0` | `SELECTC.BIN` | times em caixa mista + jogadores |

O mapa passa então a guardar **(arquivo, marcador, deslocamento a partir
do marcador)** em vez de offset absoluto. Três ganhos, além de resolver a
divergência da §1.12:

1. sobrevive a qualquer outra release europeia sem remapear nada;
2. **falha alto** — marcador ausente é erro imediato e legível, não
   gravação silenciosa no lugar errado;
3. serve de verificação de que a imagem aberta é mesmo PES2.

A identidade da release, quando for preciso saber, sai do `SYSTEM.CNF`:
`BOOT = cdrom:SLES_039.57;1` contra `SLES_039.46;1`.

**Ressalva:** isto está provado para as tabelas de texto, que têm literal
óbvio. As tabelas numéricas das Fases 3 e 4 não têm, e ali a âncora terá
de ser outra coisa — o fim da tabela de texto que as precede, uma
assinatura de conteúdo, ou um offset relativo a um marcador próximo.
Decidir isso caso a caso é trabalho da Fase 5.

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
Bottles), Bottles, PCSX2, e as ferramentas deste repositório.

### 3.2 O que falta, e é bloqueante

| Falta | Para quê | Bloqueia |
|---|---|---|
| **Emulador de PlayStation** — DuckStation ou Mednafen | rodar o jogo e ver o efeito de um `poke` | Fases 2–6 |
| **Debugger de RAM** no emulador (DuckStation tem; Mednafen tem via `mednafen`+`debugger`) | achar a struct carregada e correlacionar com o disco | Fase 3 |
| `numpy` | varredura de padrão em 466 MB em tempo civilizado | Fase 2 |
| Desmontador MIPS — Ghidra, ou `radare2`/`rizin` | ler o código que consome a tabela, quando a estatística empacar | Fase 4 |

Nenhum está instalado. PCSX2 **não serve** — é PS2.

### 3.3 Confirmar antes de começar

1. O jogo dá boot no emulador escolhido, a partir do `.cue` multi-track, e
   chega ao menu de seleção de time.
2. O emulador tem *save state* e dump de RAM (`.sav`/`.state` ou o painel de
   memória), porque a Fase 3 depende disso.
3. O emulador aceita cartão de memória em `.mcr`, porque a Fase 3.2 depende
   disso.
4. Cópia do Track 1 no scratchpad, com o `.cue` ajustado para apontá-la.

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

- Instalar emulador + debugger; confirmar boot (§3.3). **Pendente** — é
  instalação de pacote de sistema, e depende de decisão do usuário.
- `tools/pes2/iso.py`: listar, extrair e **reinjetar** arquivo do ISO
  preservando setor e cauda EDC/ECC. Reinjeção é o que permite o ciclo de
  `poke`; sem ela cada teste é edição manual em hexeditor. **Feito** —
  `ls`, `extract`, `inject`, `anchors`, `roundtrip`.
- Guarda de round-trip: extrair todos os 252 arquivos e reinjetá-los sem
  mudança tem de devolver o `.bin` **byte a byte idêntico**. Se não devolver,
  a ferramenta está errada e tudo o que vier depois é ruído. **Feito e
  verde**, com controle negativo — ver §5.1.

#### 5.1 O que a Fase 0 mediu

`python3 tools/pes2/iso.py roundtrip <track1.bin>` copia a imagem, lê e
regrava os **244** arquivos legíveis e compara: **byte a byte idêntico**.

Guarda verde não vale nada sem prova de que sabe ficar vermelha, então o
mesmo caminho de escrita foi exercitado com um controle negativo: trocar
o `P` de `PIEMONTE` por `X` em `SELECT.BIN` mudou **exatamente um byte**
em toda a imagem de 445 MiB, no offset absoluto **2002800** — que é o que
a aritmética de setor prevê, e ele cai dentro da área de dados
(`24..2071`), com cabeçalho e cauda intactos.

O caso não é trivial: o registro fica no offset 3272 de um arquivo que
começa no LBA 850, então **atravessa a fronteira de setor** — 3272 ÷ 2048
= LBA 851, resto 1224, mais os 24 de cabeçalho = 1248. É exatamente a
armadilha da §6.3, e ela está coberta.

O `anchors` resolve os oito marcadores da §1.13 nas duas releases, cada um
ocorrendo uma única vez.

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
  em *idêntico* / *difere*. *(Feito — §1.12. 204 idênticos, 32 diferem.
  Falta classificar **por que** cada um dos 32 difere: os que mudam de
  tamanho são texto localizado; os que mantêm tamanho e mudam conteúdo —
  `GAME.BIN` com 38.213 bytes, `SELECT4.BIN` com 6.884, `ENTER.BIN` com
  3.272 — são os que merecem olhar, porque ali pode haver dado de jogo.)*
- Mapear os 69 `OFS_*` do WE2002 para `(arquivo, offset relativo)` e
  publicar a tabela (a §1.4 tem o esqueleto; falta o offset relativo de
  cada um).
- Saída: `docs/samples/pes2-diff-releases.md` e a tabela de âncoras.

### Fase 2 — Inventário de texto

- Varredura de string em todos os 252 arquivos, com classificação:
  nome de time, abreviação, nome de jogador, texto de interface, lixo.
  *(As cinco tabelas da §1.6 já estão fechadas; falta o restante do
  disco e a segunda massa de nomes do executável.)*
- Fechar **contagem e ordem** de cada tabela: quantos times, quantas
  seleções, quantos jogadores, e em que ordem.
- Confirmar as cópias (§1.5) e procurar as que faltam — a suspeita, pelo
  padrão do WE2002, é que existam mais de duas de nome e mais de três de
  abreviação.
- Primeiro `poke` de validação: renomear `PIEMONTE`, dentro do slot, em
  **todas** as cópias, e ver o nome novo no emulador em todas as telas.
  É esse teste que fecha a fase, não a varredura.

### Fase 3 — O registro de jogador

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

Só aqui se decide linguagem e UI. As três condições da §0 são o portão.

---

## 6. Armadilhas conhecidas

### 6.1 Uma cópia gravada é pior que nenhuma

A §1.5 mostra a mesma tabela em três e quatro arquivos. Um editor que grava
só a de `SELECT.BIN` produz um jogo que mostra o nome novo na seleção de
time e o velho no replay e no resultado. **Toda gravação é para o conjunto
de cópias**, e o mapa declara o conjunto.

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

Emulador é GUI. Se ele for dirigido por script, roda no `DISPLAY=:98`,
pelas razões do [CLAUDE.md](../CLAUDE.md). Sessão de mapeamento manual, com
o usuário olhando a tela, é caso legítimo de `:1` — **mas pergunte antes**,
como a regra manda.

---

## 7. Entregáveis

| Fase | Entregável |
|---|---|
| 0 | `tools/pes2/iso.py` + teste de round-trip de extração/reinjeção — **feito**, menos o emulador |
| 1 | tabela de âncoras `OFS_* → (arquivo, offset relativo)`; diff entre releases |
| 2 | inventário de texto; contagem e ordem canônica; primeiro `poke` verificado |
| 3 | estrutura do registro de jogador |
| 4 | estrutura de time, formação, uniforme, bandeira, Master League |
| 5 | `pes2_map.json` + gerador + round-trip headless |
| 6 | editor |
