# Uniformes (TEX) no Superpack v6

Levantamento de 2026-09-29 sobre `C:\games\we2002\Superpackv6\We2002\TEX`: 2.778
arquivos em 30 pastas, dos quais o conteúdo textual foi lido inteiro — 22
tutoriais (`.doc`, `.docx`, `.pdf`, `.htm`, `.rtf`, em espanhol, italiano,
português e inglês), os `leeme`/`readme` das ferramentas, as tabelas de medida e
de offset, e o fonte VB6 do TEX Editor do ramonpsx. As imagens-mapa de zona
foram abertas e o mapa do polipoli foi **medido pixel a pixel**. O que ficou de
fora está na última seção.

O capítulo 8 da Bíblia ([/docs/biblia-we2002/08-uniformes.md](/docs/biblia-we2002/08-uniformes.md))
já ensina o fluxo básico passo a passo. Este documento é o que o Superpack sabe
**além** dele: o formato, o mapa de zonas, as regras de paleta, as ferramentas e
as armadilhas, juntando o que cada autor descobriu por conta própria.

## 1. O que é um TEX

Cada time tem um arquivo `/BIN/TEX_<tag>.BIN` no disco — 105 ao todo. Os
tutoriais chamam o arquivo de **TEX** porque é o nome dentro do jogo; o conteúdo
é um contêiner de imagens comprimidas (LZSS) e paletas, o mesmo formato dos
outros `BIN/*.BIN`.

### 1.1 A estrutura, medida no disco

`tools/pes2/bin_archive.py` lê o contêiner. Sobre o `TEX_00.BIN` do disco
japonês (29.944 bytes):

```sh
MSYS_NO_PATHCONV=1 python tools/pes2/bin_archive.py ls roms/japanese-shift-jis.bin --file /BIN/TEX_00.BIN
```

| # | tipo | VRAM | tamanho | o que é (nome da comunidade) |
|---|---|---|---|---|
| 1 | imagem 8 bpp | (576, 256) | 128×128 | uniforme **titular**: jogador + goleiro |
| 2 | imagem 8 bpp | (576, 384) | 128×128 | mangas longas e braçadeira, **titular** |
| 3 | CLUT 256 | (0, 486) | 512 B | paleta do **jogador** titular |
| 4 | CLUT 256 | (0, 488) | 512 B | paleta do **goleiro** titular |
| 5 | imagem 8 bpp | (576, 256) | 128×128 | uniforme **suplente** |
| 6 | imagem 8 bpp | (576, 384) | 128×128 | mangas longas, **suplente** |
| 7 | CLUT 256 | (0, 486) | 512 B | paleta do jogador suplente |
| 8 | CLUT 256 | (0, 488) | 512 B | paleta do goleiro suplente |
| 9 | imagem 8 bpp | (704, 256) | 128×64 no registro | **bandeira** da torcida |
| 10 | CLUT 256 | (256, 480) | 512 B | paleta da bandeira |
| 11 | imagem 8 bpp | (768, 384) | 128×128 | **árbitro** |

São **6 imagens e 5 paletas** — exatamente o que o WE Image Manager mostra
("6 gráficos, 5 paletas", robinsonwi09) e a ordem dos campos do WETex (Titular,
Suplente, Equipo). As duas colunas se confirmam uma à outra: a ordem no arquivo
é a ordem em que o WETex monta.

Duas consequências para o [PLAN-LOOKS-PY.md](/docs/PLAN-LOOKS-PY.md), que deixou
as duas perguntas abertas:

- **A quinta paleta, em (256, 480), é a da bandeira.** Ela vem logo depois da
  imagem da bandeira, e toda ferramenta da época a trata assim (CLUTEd: "Team
  flag"; WETex: "Paleta Bandera"). A geometria do boneco não a nomeia porque a
  bandeira não veste ninguém.
- **"Casa e fora" é o que a comunidade inteira afirma**, e a ordem do arquivo
  concorda: o primeiro par (imagem, mangas, paleta 486, paleta 488) é o
  titular, o segundo é o suplente. Continua não medido na tela — ninguém trocou
  o uniforme em jogo para ver qual par se move.

Na ferramenta WE Image Manager os índices aparecem assim, e é por eles que os
tutoriais mandam trocar a cor do número:

| combinação | uso |
|---|---|
| gráfico 1 + paleta 1 | jogador titular |
| gráfico 1 + paleta 2 | goleiro titular |
| gráfico 3 + paleta 3 | jogador suplente |
| gráfico 3 + paleta 4 | goleiro suplente |
| gráfico 5 + paleta 5 | bandeira |
| gráfico 6 | árbitro (a paleta dele não está no TEX — ver §5) |

### 1.2 Por que duas paletas para uma imagem

Jogador e goleiro estão **na mesma imagem** e compartilham a mesma área de
**números**. O que separa um do outro é a paleta: o jogador desenha com a de
(0, 486), o goleiro com a de (0, 488). Por isso o número pode ter cor diferente
nos dois — mesmos pixels, entrada de paleta diferente (Welagarto).

### 1.3 Como o arquivo original organiza a paleta

Nos TEX **originais** da Konami a paleta de 256 cores é uma grade de **16 linhas
de 16 tons**: cada linha é a rampa de sombra de uma zona do uniforme. É isso que
torna possível "trocar só a cor" sem mexer na imagem (Paintex, CLUTEd). O
mapeamento é quase fixo:

| linha | zona |
|---|---|
| 0 | braçadeira de capitão |
| 1 | cor principal da camisa |
| 2 | cor secundária da camisa |
| 3, 4 | detalhes da camisa |
| 5 | calção |
| 6 | meias |
| 7 | gola (até a 7ª caixa) |
| 8–14 | detalhes que variam de uniforme para uniforme |
| 15 | **número** (as 4 primeiras caixas) |

Três ressalvas que os autores registraram:

- A correspondência linha→zona do **goleiro** é diferente da do **jogador**,
  mas é a mesma entre o 1º e o 2º uniforme de cada um. Dá para combinar a
  textura de goleiro de um TEX com a de jogador de outro (Wetigre).
- Zonas podem estar **ligadas**: mudar uma linha muda duas partes (ex.: listra
  da meia e lateral da camisa).
- Recolorir não muda o desenho: de um uniforme liso não sai um listrado. Parta
  do TEX mais parecido com o alvo.

TEX **feito pela comunidade** não segue essa grade: a paleta sai da indexação do
editor de imagem, e o número vai para onde a regra do §3 o colocou.

## 2. O mapa de zonas

Toda edição trabalha sobre um **BMP de 256×128** que junta as imagens 1 e 2 do
TEX lado a lado: à esquerda o uniforme (128×128), à direita as mangas longas
(128×128). Titular e suplente juntos dão 512×128 (ou 256×256, empilhados).

As coordenadas abaixo foram **medidas** sobre `Zonas kits y tex - polipoli/We2002/Zonas We2002.png`
(componentes de cor sólida, x e y em pixels a partir do canto superior
esquerdo), com os nomes do `Zonas We2002 explicadas.png` e das tabelas de
ramonpsx e polipoli. As posições da braçadeira, das luvas, do cotovelo e dos
números batem com as que o TEX Editor do ramonpsx usa para colar as peças
(`rsc/Form1.frm`).

### 2.1 Metade esquerda — uniforme (imagem 1 / 5 do TEX)

Jogador em x 0–63, goleiro em x 64–127, no topo.

| zona | jogador (x, y, L×A) | goleiro (x, y, L×A) |
|---|---|---|
| ombros (2 peças) | (4, 0) e (24, 0), 16×8 | (68, 0) e (88, 0), 16×8 |
| laterais da camisa | (0, 8) e (32, 8), 12×22 | (64, 8) e (96, 8), 12×22 |
| frente (com a gola) | (12, 6), 20×24 | (76, 6), 20×24 |
| costas | (44, 0), 20×30 | (108, 0), 20×30 |
| calção: laterais | (0, 30) e (32, 30), 12×18 | — |
| calção: frente | (12, 30), 20×18 | — |
| calção: trás / do goleiro | (44, 30), 20×18 | (64, 30), 32×18 (uma perna só; a outra é espelho) |
| meias | (0, 48), 32×18 | (96, 30), 32×18 |
| entreperna | (32, 48), 16×18 | (56, 48), 8×18 |
| cotovelo | — | (48, 48), 8×8 |
| manga (ombro→cotovelo) | — | (64, 48), 32×15 (8 + 7) |
| antebraço (cotovelo→pulso) | — | (96, 48), 32×9 |
| luvas | — | (96, 57), 32×11 |
| manga curta direita | (0, 66), 32×14 | — |
| manga curta esquerda | (32, 66), 32×14 | — |
| **números** 0–9 | (64, 68), 60×12, compartilhados | ← |

O resto da metade esquerda (y ≥ 80) não é usado.

O jogo discorda em dois pontos, medidos contra a geometria em 2026-10-02
([PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) §4.6): a seção de torso amostra
(0,80) 20×24 no jogador e (100,104) 20×24 no goleiro — índice 0 em todo kit do
disco —, e o quad da gola cobre o recorte que o mapa deixa vazio entre os
ombros. A frente, aliás, não é o retângulo (12, 6) 20×24 inteiro: a gola sobe
entre os ombros e o resto das duas linhas de cima é dos ombros.

**A manga do goleiro do cotovelo ao pulso é espelhada** em relação à parte do
ombro ao cotovelo: uma listra à esquerda em cima vai à direita embaixo (Xylon).

### 2.2 Metade direita — mangas longas e capitão (imagem 2 / 6 do TEX)

Na imagem de 256×128 a coluna útil é x 160–191 (32 px de largura). A coluna x
128–159 é a dos **figurantes que entram com as bandeiras** antes da partida; os
tutoriais mandam não mexer ("pode deixar sem editar, não afeta a TEX").

| y | altura | zona |
|---|---|---|
| 0 | 14 | antebraço **esquerdo** do jogador (manga longa) |
| 14 | 14 | manga longa esquerda **com braçadeira** — faixa em y 20, 32×5 |
| 28 | 14 | manga longa esquerda |
| 42 | 14 | manga longa direita |
| 56 | 15 | manga curta do goleiro, esquerda, **com braçadeira** — faixa em y 63 |
| 71 | 14 | manga curta do jogador, esquerda, **com braçadeira** — faixa em y 77 |
| 85 | 8 | cotovelos: esquerdo em x 160, direito em x 184 (8×8 cada) |
| 93 | 14 | antebraço **direito** do jogador |

As zonas "com braçadeira" só valem para quem usa a braçadeira; as outras, para
o resto do time (WeHispano). A manga de capitão é padrão separado do da camisa.

### 2.3 Face por face

Cada peça é o tecido aberto; os tutoriais descrevem a ordem das faces
(robinsonwi09, SubMarcos, Rick38):

- **Camisa**: lateral direita (vista de trás) · frente · lateral esquerda ·
  costas. A parte de cima das costas aparece quando o jogador se abaixa depois
  de levar gol; o topo da frente são os ombros. A linha de 20×5 no pé da camisa
  é a "camisa por dentro do calção".
- **Calção**: lateral direita · frente · lateral esquerda · trás; a entreperna
  fica embaixo, na mesma cor.
- **Meias**: frente · direita · trás · esquerda.
- **Manga direita**: trás · lado externo (onde vão as listras) · frente · lado
  interno. **Manga esquerda**: a ordem inversa — interno · frente · externo ·
  trás.
- **Números**: cada dígito tem **6 px de largura**, e o desenho não pode sair
  da faixa de 6 px do seu dígito (Xylon).

### 2.4 Medidas de referência

Das tabelas de ramonpsx (`Medidas TEX we2002.txt`) e polipoli
(`Instrucciones Macro Photoshop…txt`), usadas pelos redimensionadores:

| peça | jogador | goleiro |
|---|---|---|
| frente | 20×22 (22×22 no ramonpsx) | idem |
| costas | 20×30 (20×25 visível) | idem |
| lateral da camisa | 12×22 | 12×22 |
| ombro | 16×8 | 16×8 |
| mini-gola | 20×2 | 20×2 |
| camisa por dentro | 20×5 | 20×5 |
| calção | 20×18 + laterais 12×18 (4+5+3) | 32×18 (13+5+14) |
| entreperna | 16×18 | 8×18 |
| meias | 32×18 | 32×18 |
| manga curta | 32×14 | 32×15 |
| manga longa | 32×14 | 32×9 (antebraço) |
| braçadeira | 32×5 | 32×5 |
| cotovelo | 8×8 | 8×8 |
| luvas | — | 32×11 (as do TEX Editor têm 32×12) |
| números | 60×12 | compartilhados |

## 3. Regras de cor e paleta

São as regras que todo tutorial repete, e as que mais custam quando esquecidas.

1. **Preto puro `000000` é transparente.** Todo o fundo fica nele; para pintar
   preto no uniforme use `1E1E1E` (30,30,30), `252525` ou `303030`. No TIMUTIL,
   marque **"Transparent for black"** — obrigatório na bandeira, e o Rick38
   marca em todas.
2. **Tudo em 8 bits, 256 cores, uma paleta só por uniforme.** Por isso se
   trabalha com o 256×128 inteiro (ou o 512×128 dos dois uniformes) até o fim:
   as duas metades de 128×128 precisam sair **da mesma paleta**. Cortar antes de
   indexar dá paletas diferentes e erro na montagem.
3. **O número vai numa cor que não existe no resto do uniforme** — verde
   fluorescente (`00FF00`) por convenção — para depois ser achado e trocado no
   CLUTEd/WE Image Manager sem arrastar outra zona junto. Titular e suplente
   usam **o mesmo verde**.
4. **O número tem no máximo 4 tons** (5 cores contando o fundo), e cada linha de
   pixel do dígito é de uma cor só (Xylon). Depois da sombra os tons do número
   saem como rampas horizontais.
5. **Fixe a posição do verde na paleta.** Dois métodos documentados:
   - *polipoli* (Photoshop): indexar com paleta **forçada personalizada**, com
     amarelo `FFFF00` na 1ª posição, preto `000000` na 2ª e verde `00FF00` na
     3ª; depois, na tabela de cores, trocar a 1ª (amarelo, o fundo) por `000000`
     e a 2ª por um preto que não seja zero (ex.: `000008`). Resultado: índice 0
     transparente, número fixo no **índice 2** nas duas paletas. Indexar antes no
     Paint Shop Pro evita o problema do `000` virando transparência no meio do
     uniforme.
   - *Alex / SubMarcos*: fundo `E8C830` como 1ª cor da paleta (que é a
     transparente) e os 4 tons do número nas posições 2–5, carregando uma
     paleta de 5 cores salva como "Forçada: Personalizada".
6. **Cor diferente de número para o goleiro** = mesma imagem salva de novo com as
   entradas do número trocadas; esse segundo BMP/TIM vira a "Paleta Arquero".
7. **Pouca cor ajuda.** Alex colore com no máximo 24 cores antes da sombra; o
   sombreador antigo do Obocaman exige **15 cores**; o árbitro fica melhor com
   menos de 30.
8. **Tamanho comprimido conta.** O arquivo novo tem de caber no espaço do que ele
   substitui: o árbitro original tem 5,00 KB comprimido (ramonpsx) e o Xylon
   manda comprimir "sobre um TEX preexistente, desde que seja grande o
   bastante". Muitos detalhes = compressão pior.

## 4. O fluxo completo

A receita consolidada (Rick38, Nathan, Sejotax, NEO2K3, Bíblia):

1. **Desenhar** as zonas sobre uma base (§6) em 24 bits, sem sombra. Fundo
   `000000` (ou o amarelo de trabalho, se for usar o truque do §3.5), números
   em verde.
2. **Sombrear** — antes dos logotipos:
   - WE Mod Center: `File → Texture → Open` (o BMP precisa estar em 8 bits,
     senão dá *Stream Read Error*), `Texture → Change color depth → Increase to
     32 bit`, `Texture → Shadow → %Intensity → PS1 Uniform`, 70–75 % (74–75 %
     para cores escuras, 71–72 % para claras), `Decrease to 8 bit`, salvar. Ao
     reduzir aparece uma falha no rodapé da imagem — pintar de preto.
   - ou colar `Sombra We2002.bmp` / `Sombra We8.bmp` (512×128) como camada em
     modo **Multiplicar** (+15 brilho, +15 contraste se escurecer demais);
   - ou o WE2002 Shadow Caster 0.2.
3. **Detalhes**: escudo reduzido a 3–4 px (4×4 no peito), patrocinador a 12–14
   px de largura, ajustados pixel a pixel. Logo vetorial perde tudo ao virar
   bitmap; redimensionar no próprio editor e retocar à mão dá melhor resultado.
4. **Indexar** a imagem inteira (256×128, ou os dois uniformes juntos) a 256
   cores, com a regra de paleta do §3.
5. **Cortar** em duas de 128×128 por uniforme: `uniforme` e `mangas`. O
   256×128 inteiro fica como **fonte de paleta**. O WE2002_CUT TEX (Fabio FJA)
   corta o 512×128 em quatro; como o corte separa a paleta, salve antes a paleta
   em `.ACT`, copie a imagem, carregue a paleta e cole de volta em cada parte.
6. **TIM**: converter cada BMP no TIMUTIL (nomes de até 8 letras) ou salvar
   direto pelo plugin TIM do Photoshop (`timplug.zip` / `Tim plugin
   photoshop.zip`).
7. **Comprimir** no WEZip (`Comprimir`, opção 8 bits) só as imagens: uniforme,
   mangas e bandeira. **As paletas não se comprimem** — o TIM de 256×128 entra
   cru no campo de paleta.
8. **Montar** no WETex:

   | grupo | campo | arquivo |
   |---|---|---|
   | Titular | Imagen comprimida | `uni1.bin` |
   | | Paleta jugador | `1.tim` (ou o 256×128 do titular) |
   | | Paleta arquero | `1.tim`, ou a variante com número do goleiro |
   | | Mangas largas | `manga1.bin` |
   | Suplente | idem | `uni2.bin`, `2.tim`, `2.tim`, `manga2.bin` |
   | Equipo | Imagen bandera | `b.bin` |
   | | Paleta bandera | `b.tim` |
   | | Árbitro | `.bin` de árbitro (o diálogo pede TIM; trocar o filtro para "todos os arquivos") |

   O árbitro é o mesmo para todos os TEX; quem não fez o seu tira o de outro TEX.
   `Crear camiseta` grava o TEX.
9. **Cor do número**: CLUTEd (`File → Extract clut from TEX file`, escolher
   "Players shirt #1 palette" etc., trocar o verde, `File → Inject clut in TEX
   file`) ou WE Image Manager (escolher gráfico+paleta, `Clut Editor`, trocar os
   verdes pelas barras R G B, `Inserir`, `Gravar BIN`). Quatro paletas, uma por
   vez. A cor certa de um kit de PES está no `font.png`/`numbers.png` (PES
   5–2010), no `back.png`/`chest.png` (PES 2014), ou na cor do texto "COLLAR"
   no canto do kit (FIFA 16).
10. **Inserir na imagem do jogo**, de uma cópia:
    - **WE Team Editor 0.99** (Obocaman): escolher o time, abrir o TEX no campo
      *Shirt* e clicar no botão de gravar. Também extrai o TEX de um time.
    - **WE Shirt Editor 1.8** (Walxer): *Game Selection* = Winning Eleven 2002,
      *BIN Image File Name* = a imagem, *Shirt Swap Selection* = o TEX, *Shirt
      To Read* = Custom, *Shirt To Overwrite* = o time; *Proceed*.
    - **CDMage**: `BIN/TEX_xx.BIN` → *Import File*.
11. Testar no emulador. Dica do Rick38: teste cedo, com um uniforme só repetido
    nos quatro lugares e qualquer bandeira, antes de fazer tudo.

### 4.1 Caminho curto: só recolorir

Sem descomprimir nada, dá para mudar só a paleta de um TEX **original**: CLUTEd
ou WE Paintex (Obocaman), que mostra as 16 linhas de rampa, gera degradê entre
duas cores e grava o TEX direto na imagem. Não serve para TEX feito com
compressor, e não muda o desenho (§1.3). Para achar qual linha pinta qual zona:
encher uma linha com verde vivo, gravar, olhar no emulador (modo Edit, trocar
número dá boa vista), anotar, repetir.

### 4.2 Caminho de extração

WEZip → `Descomprimir`, formato **"TEX Camisetas"** → 10 TIMs:
`_eqTITjug`, `_eqTITarq`, `_eqSUPjug`, `_eqSUParq`, `_eqTITmlJUG`,
`_eqTITmlARQ`, `_eqSUPmlJUG`, `_eqSUPmlARQ`, `_bandera`, `_arbitro`. Os pares
jug/arq são **a mesma imagem com paletas diferentes** (as imagens 1/2/5/6 do
§1.1 vistas com a paleta 486 ou 488). TIMUTIL converte para BMP e de volta.

### 4.3 O atalho que quebra no console

O **WECompressor / Tex Manager** do Walxer (0.5+) aceita o BMP de 256×128
direto, extrai TEX ("Estrai maglia") e monta tudo numa tela — e **corrompe
partes do TEX**: fica perfeito no emulador e **transparente no PSX de verdade**
(Xylon); a Bíblia registra que ele **trava o jogo**. O Rick38 chama o caminho
WETex de "o correto, que funciona no PLAY". Use o WETex; o Xylon, se usar o
Walxer, manda comprimir as duas metades de 128×128 separadas.

## 5. Árbitro

- A **textura** está em cada TEX (imagem 6, em VRAM (768, 384)). O jogo só usa
  a **faixa do meio** da textura (ramonpsx).
- As **paletas** não estão no TEX: são quatro, no `SELECT.BIN`, e três no
  `OPENNING.BIN`. As duas tabelas do Superpack divergem em 32 bytes, e nenhuma
  foi conferida aqui:

  | cor | ramonpsx (decimal) | polipoli (decimal / hex) |
  |---|---|---|
  | amarelo | `SELECT.BIN` 256820 · `OPENNING.BIN` 22356 | 256852 / `3EB54` |
  | vermelho | 257332 · 22868 | 257364 / `3ED54` |
  | preto | 257844 · 23380 | 257856 / `3EF40` |
  | verde | 258356 (só no `SELECT.BIN`) | 258388 / `3F154` |

  O ramonpsx anota ainda "offset do árbitro nos BIN = 25640", mas avisa que o
  offset da imagem 6 **muda de TEX para TEX** e deve ser lido no WE Image
  Manager; no `TEX_00.BIN` japonês ela começa em 24.392.
- **TEX Arbitro Edit v2** (ramonpsx) insere a textura comprimida num TEX já
  pronto (sobre a imagem 6) e as quatro paletas no `SELECT.BIN`; o `SELECT.BIN`
  volta para a imagem pelo CDMage. Inserir sobre um TEX que já não tem o árbitro
  original pode apagar a imagem 6 — aí só refazendo o TEX.
- Bases: `Tex arbitro 0.1/0.2 - Masteron20.psd`, `ALBITRO1-4.bin`,
  `PALETA ALBITRO.TIM`, `paleta 1-4.bmp`.

## 6. Bandeira

- É a imagem 5 do TEX, a bandeira que a torcida agita. São **8 quadros de
  animação** desenhados à mão, pixel a pixel; os que aparecem dobrados (3º e 4º
  de cima, 1º e 2º de baixo) só mostram metade do escudo (Bíblia, WeHispano).
  Pinte a face da frente e a de trás de cores diferentes para ver o movimento.
- A paleta é a 5ª; use cores escuras nas partes sombreadas, e indexe com
  `000000` forçado como cor transparente.
- A imagem é **128×64**, como o registro declara. O fluxo descomprime para
  16.384 bytes, mas a 2ª metade tem um só valor de byte nos 105 TEX do disco
  japonês — é enchimento (medido em 2026-09-29, ver o §1.1 do
  [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md)). As bandeiras prontas do Superpack
  vêm nos dois tamanhos (TIMs de 8.736 e 16.928 bytes).
- `Banderas 3D/` traz ~160 bandeiras prontas (`*_BND.bin` + `.tim`), a base
  `01 BASE_BAND_3D.bmp` (128×128) e `Hinchas por banderas 3D - Kosmo.psd`.
- **Remover as bandeiras 3D dos estádios** (Fabio FJA) é outra coisa: um patch
  `.ppf` no `SLPM_870.56` que zera os bytes 279360–279631 (move as bandeiras
  para a parte oculta do estádio) e escreve `99…` em 279728–279823 (esconde o
  mastro das grandes). Só o estádio 3 mantém os mastros.

## 7. Ferramentas do Superpack

| ferramenta | autor | o que faz |
|---|---|---|
| **WEZip 1.0** | Lagarto (descompressão de WarlockDC e Jordinator), WeHispano 2003 | TIM ↔ BIN comprimido; descomprime TEX em 10 TIMs |
| **WETex 1.0** | Lagarto e Warlock | monta o TEX a partir dos BIN e TIM |
| **TIMUTIL** | — | BMP ↔ TIM; nomes 8.3; "Transparent for black" |
| Plugin TIM para Photoshop | — | salva TIM direto (`timplug.zip`) |
| **CLUTEd** | LuHa | extrai e injeta as 5 paletas de um TEX |
| **WE Image Manager 0.6 beta** | Bat | vê as 6 imagens × 5 paletas, edita CLUT, mostra offsets, grava o BIN |
| **WE Mod Center 2.5c** | Obocaman | sombra "PS1 Uniform", profundidade de cor; o resto é para WE6/WE7/PES3 de PS2 |
| **WE2002 Shadow Caster 0.2** | Obocaman | aplica a sombra de WE2002 (`sombra_we2002.bin`, 16.384 bytes = 128×128) |
| WE Paintex / WE Painter | Obocaman | recolore as 16 rampas e grava o TEX na imagem (citados pelo Wetigre; não estão na pasta `TEX`) |
| **WE Shirt Editor 1.8** | Walxer | insere um TEX sobre o de um time; ENG e ITA |
| WECompressor / Tex Manager | Walxer | monta TEX do BMP 256×128 — **corrompe no console** (§4.3) |
| WE Team Editor 0.99 | Obocaman | extrai/insere TEX por time; camisa 2D |
| **TEX Editor v2.0** | ramonpsx, VB6 **com fonte** | sobre o BMP 512×128: cola números, luvas (32×12), braçadeiras (32×5, nas posições do §2.2), mangas curtas do goleiro em quatro tons de pele, sombra WE2002 ou WE8 |
| Modificador de TEX v1.0 | ramonpsx | o mesmo tipo de colagem (mangas de goleiro, luvas, números) |
| **TEX Arbitro Edit v2** | ramonpsx | árbitro (§5) |
| **WE2002_CUT TEX** | Fabio FJA | corta 512×128 em quatro 128×128 |
| We Tex Color Tool | JavES | ferramenta de cor/paleta de TEX (traz `.clu` e `.act` de exemplo; sem documentação) |
| **Jersey Joyer 3.0** | Joystick@WECN, 2003 | pré-visualização 3D (OpenGL) de `jersey.bmp` + `sleeve.bmp`, 128×128 24 bits, com capitão, manga longa e goleiro |
| Editor Camisetas Deluxe / Tutorial deluxe | Jordinator / WeHispano | tutorial executável; não foi executado, só teve o texto lido |

Os de fonte aberto estão no [SUPERPACK-CODIGO-FONTE.md](/docs/SUPERPACK-CODIGO-FONTE.md).

## 8. Converter kits de PES e FIFA

Quase metade da pasta (`Kits Pes/`, `Kits Fifa/`) é conversão de kits de PC
para o layout de WE2002. Duas famílias:

- **Ações de Photoshop (`.atn`) do polipoli**, uma por jogo: PES5, PES6, PES
  2009/2010, PES 2014, FIFA 16. Mesma receita em todas: copiar a pasta `Tex`
  para `C:\Tex`, pôr o GDB folder renomeado para `Kit` (subpastas `ga gb pa pb`
  — ou `g-1 g-2 p-1 p-2` no PES 2014; no FIFA, oito PNGs com nome fixo
  `gas gat ghs ght pas pat phs pht`), rodar `Redimensionar`, retocar
  `03.png`/`06.png` (números sempre verde puro), rodar `Sombra`/`Contraste`,
  indexar no PSP, reindexar no Photoshop com a paleta forçada do §3.5, rodar
  `Tim`, e seguir com WEZip/WETex/WE Image Manager. A ação `Auxiliar` recorta,
  gira e cola peça a peça na ordem gola, ombros, mini-gola, braçadeira, resto.
- **Programas e PSDs de terceiros**: Sampler (Editor de adaptação 1.0 +
  Redimensionador 1.0) e zeta (`kits we2002` 1.1/2.0/2.2, PES6/PES 2008, kits
  512×512 ou 1024×1024 → BMP com escolha de luvas, manga de goleiro, estilo de
  número e braçadeira; tirar a braçadeira do kit antes), ramonpsx (PSD para PES6
  512×512 e redimensionador de luvas v1.2), MatiWE (PES 2009 e PES 2015, kits
  2048×2048, camada `Base` com jogador à esquerda e goleiro à direita),
  Will-i-am (PES 2009 → PES 2008, para reusar os conversores de 2008).

Luvas de PES: girar 90° no sentido horário e redimensionar para **32×11**
(Leandro e zeta; pacote com Adidas, Kappa, Nike, Puma, Reebok).

Os `config.txt` dos exemplos são configurações do GDB Manager do PES (cor,
modelo, posição de número); servem só para achar a cor do número.

## 9. Bases e modelos

- `Base Para Crear TEXs de WE2002 v0.2 - masteron20 y Leandro (kkpp).psd` (5,4 MB).
- NEO2K3 v1.4 (2005): PSD com camadas de estilo de número, sombra "WE8-LE" e
  "WE2K2", modelos Adidas e Nike, manga curta de goleiro com tom de pele.
- `Base Para Crear TEXs de WE2002 v1.2.psd`, `1.bmp` (512×128) e `Numeros.bmp`
  (60×12) do Lad; o Lad exporta 512×128 com paleta otimizada de 256 cores pelo
  CorelDRAW e corta em dois 256×128.
- `Sombras, cuello, fondo, brazalete capitan - polipoli/`: sombras WE2002, WE8 e
  WE2000 U-23, sombra WE2002 sem gola, gola, fundos amarelo e preto, braçadeira.
- `Zonas kits y tex - polipoli/`: os mapas de zona de WE2002, PES5, PES6, PES
  2009, PES 2014 e FIFA 16, e **20 capturas** do capitão (jogador/goleiro × manga
  curta/longa × frente, costas, direita, esquerda, agachado) para ver onde cada
  zona cai no boneco.
- `Tutorial - Alex/`, `Tutorial - Wehispano/`: `Maglia`/`Patron` (128×128),
  `Maniche_lunghe_capitano`/`Mangas_largas_capitan` e `Bandera` (128×128).

## 10. O que ficou de fora

- **Vídeos**: `Tutorial tex por Kosmo.mp4` (166 MB), os 19 `.swf` do Romualdo
  (camisetas e detalhes — o texto das páginas que os hospedam está vazio) e o
  instalador de gravador de tela do Leandro. Nenhum foi assistido.
- **Os binários** não foram executados, inclusive o `Tutorial_deluxe.exe`, do
  qual só as strings de texto foram lidas.
- **Os `.psd` e `.atn`** não foram abertos; o que se sabe deles vem dos
  tutoriais que os acompanham.
- As pastas de `Paint Shop Pro 5` trazem instalador e crack; foram ignoradas.
- Os `.tim` e `.bin` de exemplo (~1.100 TIMs, ~200 BINs) não foram
  inventariados um a um.

## 11. Ligação com este repositório

- O port **não edita TEX**. O `FlagKitDialog` (ex-`graf.cpp`) mexe nas paletas
  de 16 cores da **camisa 2D** e da **bandeira 2D** — o "uniforme 2D" do §8a da
  Bíblia —, não no uniforme 3D. Onde o 2D mora no disco (`SELECT2.BIN`,
  `DATSEL.BIN`, `DAT2D.BIN`) e o que a pasta `Uniformes 2D` do Superpack sabe
  dele está no [SUPERPACK-UNIFORMES-2D.md](/docs/SUPERPACK-UNIFORMES-2D.md).
- O `tools/looks/` **lê** os TEX para vestir o boneco da tela `LOOKS SET`, e o
  `oracle.py --kit` mede que a tela dos states usa o `TEX_A4`. As regras deste
  documento sobre as duas paletas por imagem e a paleta da bandeira respondem,
  do lado da comunidade, as perguntas que o [PLAN-LOOKS-PY.md](/docs/PLAN-LOOKS-PY.md)
  deixou abertas.
- **18 dos 105 `TEX_*.BIN` têm os últimos 1–3 setores marcados Form 2** na
  `golden-european-deluxe.bin`, e o `iso.py` os recusa; no disco japonês e na
  tradução inglesa os 105 são Form 1. O dado nesses setores está no leiaute
  Form 1 — detalhe no §2.1 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md). Uma
  ferramenta que grave TEX precisa saber disso.
- Nenhuma ferramenta de escrita de TEX existe aqui. Se um dia existir, a regra do
  §3.8 (caber no espaço do original) e a do §4.3 (o que funciona no emulador
  pode quebrar no console) são as duas que um golden test não pega sozinho.
