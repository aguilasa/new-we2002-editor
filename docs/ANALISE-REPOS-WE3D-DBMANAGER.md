# Análise — `Darkensses/we3d` e `zetaprog/We2002-Data-Base-Manager`

> Dois repositórios externos, analisados em **2026-08-09**, com o que dá para
> trazer para cá e o que não dá.
>
> Regra que valeu na análise: **nada entra como suposição**. Toda afirmação
> sobre formato foi conferida contra `roms/golden-european-deluxe.bin` (e, onde
> fazia sentido, contra `roms/japanese-shift-jis.bin`). Onde a conferência
> falhou ou não foi feita, está dito.
>
> Complementa a §1 do [PLAN-FEATURES.md](/docs/PLAN-FEATURES.md), que já
> cataloga os 21 repositórios do CARP. Nenhum dos dois abaixo estava lá.

---

## 1. Resumo executivo

| | `we3d` | `We2002-Data-Base-Manager` |
|---|---|---|
| Autor | Darkensses | zetaprog |
| O que é | Visualizador/editor 3D web de TMD e `MODEL.BIN`, + editor de bandeiras de escanteio via `SELECT.BIN` | DLL VB.NET que lê/grava o bloco de 12 bytes de atributos de jogador |
| Linguagem | JavaScript (Three.js, Vite) | VB.NET |
| Licença | **MIT** — reaproveitável com crédito | **Nenhuma** — mesma situação do nosso `legacy/` |
| Vale a pena | **Sim, muito** — resolve uma lacuna aberta do [PLAN-STADIUMS.md](/docs/PLAN-STADIUMS.md) e abre um arquivo novo | **Sim, como confirmação independente** — não como código |

O ganho concreto de cada um:

- **`we3d`** documenta o `MODEL.BIN` inteiro e o método de derivar o
  endereço-base de RAM sem emulador. A §2.4 do PLAN-STADIUMS deixava o
  `MODEL.BIN` como *"provável modelo de jogador, fora de escopo"* — agora é
  formato conhecido e **verificado no nosso disco**. Além disso revela o
  `SELECT.BIN`, arquivo que nenhum plano nosso menciona.
- **`We2002-Data-Base-Manager`** é uma reimplementação independente do
  bit-packing dos 12 bytes de atributo. Ela **concorda com o nosso
  `Player::Decode()` em 25 dos 29 campos**, o que é a melhor evidência
  disponível de que a Fase 2 acertou. Nos 4 campos em que diverge, a medição
  no disco decide — e decide a nosso favor.

---

## 2. `Darkensses/we3d`

### 2.1 O que o repo tem

```
src/lib/BinaryReader.js       leitor de buffer (cursor + tipos LE)
src/lib/TMDParser.v2.js       parser TMD completo (12 KB), com patchVertex()
src/lib/ModelBINParser.js     parser do MODEL.BIN
src/lib/SelectBINParser.js    tabela de bandeiras de escanteio em SELECT.BIN
src/lib/coords.js             PSX <-> mundo, com teste
src/lib/stadiums.js           os 17 estádios: id, letra, arquivo, nome real
docs/MODEL_BIN_FORMAT.md      engenharia reversa do MODEL.BIN (a joia)
assets/Filefrmt_tmd.pdf       spec oficial Sony do TMD
```

### 2.2 O `MODEL.BIN` — **verificado no nosso disco**

O documento `MODEL_BIN_FORMAT.md` descreve um formato próprio, **não TMD**:
tabela de ponteiros de RAM seguida de seções de geometria de passo fixo.

Rodei a descrição dele contra o `MODEL.BIN` extraído do nosso
`golden-european-deluxe.bin` (`/BIN/MODEL.BIN`, LBA 8100, 64.800 bytes — o
mesmo tamanho que a §2.4 do PLAN-STADIUMS já tinha medido):

| Afirmação do `we3d` | Medido aqui | |
|---|---|---|
| Tabela de ponteiros `0x000..0x717` (1816 bytes) | 1º ponteiro `0x8016e848`; geometria começa em 1816 | ✓ |
| `BASE = 0x8016E800` | `0x8016e848 − BASE = 0x48`, dentro da tabela, como o doc prevê | ✓ |
| 106 seções contíguas a partir de `0x718` | percorridas 106 seções, terminando **exatamente** em 64.800 = EOF | ✓ |
| Seção 0 em `0x718`: 107 vértices, 88 primitivas | `(1816, 107, 88)` | ✓ |
| Seções 1–3: `(0x12B8, 50, 48)`, `(0x18D0, 33, 22)`, `(0x1BF0, 8, 5)` | `(4792, 50, 48)`, `(6352, 33, 22)`, `(7152, 8, 5)` | ✓ |
| Ponteiros da tabela batem nas seções | 106 de 106 seções têm ponteiro; 124 endereços distintos na tabela | ✓ |

O layout, então, é este e está confirmado:

```
seção:      uint32 numVertex | uint32 numPrimitive
            primitiva[numPrimitive]   (24 bytes cada)
            vértice[numVertex]        (8 bytes cada)

primitiva:  4 x cor RGB (B,G,R,pad)  +  índices v1,v0,v3,v2 (uint16)
            = pacote TMD "4-vertex Gradation No-Texture No-Light"
              (mode 0x39, flag 0x01) com o header de 4 bytes removido

vértice:    int16 x | int16 y | int16 z | uint16 pad(0)
```

O `we3d` ainda deduziu, só do dado, que os 106 blocos se combinam em **14
definições de jogador de 11 peças cada**, com peças compartilhadas (11 e 12
aparecem em 11 das 14) e um sistema de variantes que troca um slot só para
mudar pele/uniforme. Isso não conferi — é a parte do documento que continua
hipótese.

**O que isso muda para nós:** a §2.4 do PLAN-STADIUMS pode sair de
"anotado, fora de escopo" para "formato conhecido". Continua sendo outro
projeto (modelo de jogador tem animação esqueletal atrás), mas o custo de
entrada caiu de "engenharia reversa do zero" para "ler um documento de duas
páginas".

### 2.3 O método de derivar o `BASE` — e o limite dele

A parte reaproveitável **não é o número**, é o procedimento. O `we3d` derivou
`BASE` sem emulador assim:

1. parsear a geometria de forma independente da tabela, obtendo o conjunto de
   offsets de arquivo onde as seções começam;
2. para todo par (ponteiro da tabela, offset de seção), calcular
   `candidato = ponteiro − offset`;
3. o candidato com mais acertos é o `BASE`. No `MODEL.BIN` deu 55/55 — e aqui
   deu 106/106.

Isso ataca de frente o **item que a §2.2 do PLAN-STADIUMS chama de "maior
incerteza técnica do plano"**: o endereço-base dos `GRDM_*`/`GDC_*`.

**Mas testei nos `GRDM_*` e não transfere direto.** Em `GRDM_A.BIN` (46.773
bytes) os 15 TMDs começam em 336, 5872, 11408, …; a tabela tem 16 ponteiros
não-nulos, e eles são `0x80162060`, `0x80162070`, `0x80162080`, … —
**espaçados de 16 em 16 bytes, fora de ordem, com zeros intercalados**. Nenhum
`BASE` casa mais de 1 ponteiro com um início de TMD. Ou seja: a tabela do
`GRDM_*` **não aponta para a geometria**; ela aponta para uma estrutura de
descritores de 16 bytes que vive em outro lugar da RAM.

Conclusão honesta: o `we3d` dá o *método* e prova que ele funciona, mas o
conjunto de offsets a cruzar nos `GRDM_*` ainda não é conhecido. A fase S1 do
PLAN-STADIUMS continua necessária — só que agora com uma técnica pronta e um
resultado negativo já registrado, o que economiza a primeira tentativa.

### 2.4 `SELECT.BIN` — arquivo novo, não coberto por nenhum plano nosso

O `we3d` tem um segundo editor (`flags.html`) que edita a posição das
**bandeiras de escanteio/lateral** por estádio, gravando em `SELECT.BIN`:

```
TABLE_BASE   = 0x41770 (268144)
STRIDE       = 228 bytes por estádio
FLAGS_OFFSET = +108
FLAG_COUNT   = 10, cada uma int16 x,y,z (6 bytes) = 60 bytes, +108..+167
tamanho esperado do arquivo = 300648
```

Conferido no nosso disco: `/SELECT.BIN`, LBA 850, **300.648 bytes exatos**. E
os valores lidos são coerentes — 10 posições por estádio, x espalhado ao longo
da linha lateral, e as 10 partidas em dois grupos de altura (7 em y ≈ −1.100 a
−1.400, 3 em y = −3.840):

```
id 0x0e (Sydney):  (11552,-1147,16840) (8640,-1088,16712) (5152,-1376,17608) ...
id 0x00 (S.Denis): (11328,-1147,13896) (8640,-1088,14344) (4032,-1344,14216) ...
```

Sobram **168 dos 228 bytes** de cada registro sem uso conhecido. É um alvo de
engenharia reversa barato e de risco baixo: registro de tamanho fixo, 17
entradas, sem compressão, sem ponteiro.

### 2.5 A tabela de estádios

`src/lib/stadiums.js` mapeia, para os 17 estádios: índice de disco (= slot da
tabela do `SELECT.BIN`), letra do arquivo `GRDM_*`, ordem no carrossel, nome
real e nome do ISS Pro. Isso é dado de modding acumulado, do mesmo tipo da
tabela `tMDsFijos` do CARP que a §1 do PLAN-STADIUMS já decidiu absorver
**como dado, com crédito**. Vale absorver esta também — inclusive porque
identifica o estádio oculto (`0x10`, `GRDM_B`) e o de treino (`0x0d`,
`GRDM_I`), que o carrossel não mostra.

### 2.6 Ideias de UX

O `flags.html` tem um padrão que serve para o nosso editor tático e para o
futuro visualizador de estádio:

- **gizmo 3D e painel numérico editando o mesmo estado**, cada um refletindo o
  outro — arrastar move o campo numérico, digitar move o gizmo;
- **`Reset` por item**, contra um snapshot tirado na carga;
- **gravação no buffer a cada mudança**, e exportação só no fim;
- **fonte alternável**: arquivo embutido no app ou arquivo do usuário.

O primeiro é o mais interessante para nós: o "campinho" tático do `ed.exe` move
`CButton`s e não tem campo numérico ao lado. Ter os dois ligados seria melhoria
real — mas é **divergência de comportamento** e portanto só entra depois da
paridade fechada, pelas regras do
[PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md).

### 2.7 O que não serve

- **O stack inteiro** (Three.js, Vite, Tweakpane) é web. Nosso app é Qt/C++.
  Não há reaproveitamento de código de render.
- **O `TMDParser.v2.js`** é bom, mas o PLAN-STADIUMS já prevê parser próprio em
  C++ no `we2002_core`, e o core **não pode ganhar dependência** (regra dura do
  [CLAUDE.md](../CLAUDE.md)). O parser serve como **referência cruzada**: rodar
  o nosso contra o dele numa mesma peça e comparar contagens é um teste barato.
- **`VertexInteraction.js` / edição de vértice**: fora de escopo por muito
  tempo. Editar malha é o subprojeto que a §3 do PLAN-STADIUMS já isolou.

---

## 3. `zetaprog/We2002-Data-Base-Manager`

### 3.1 O que o repo tem

Um único arquivo com conteúdo: `FileProcessorDLL/FileProcessorDLL/Class1.vb`
(11,5 KB). Sem licença, sem README além da descrição, sem testes, sem o
aplicativo que consome a DLL. É uma reimplementação **independente** do mesmo
bit-packing que o `ed.exe` faz — o autor claramente não partiu do código do
Moriero (a técnica é outra: ele inverte os 12 bytes, monta uma string de 96
caracteres `'0'`/`'1'` e fatia com `Substring`).

Essa independência é o que dá valor ao repo: é a única confirmação externa que
temos do layout que o `Player::Decode()` reproduz.

### 3.2 Correspondência campo a campo

Derivei a posição de bit de cada `Substring` da DLL (byte = `11 − ⌊g/8⌋`, bit
= `7 − (g mod 8)`) e comparei com [src/core/Player.cpp](../src/core/Player.cpp).

**25 dos 29 campos batem exatamente**, incluindo os quatro que atravessam
fronteira de byte (`heading`, `shot_accuracy`, `strength`, `speed`) — que são
justamente onde um erro de porte seria mais provável:

| Campo nosso | Bits | Nome na DLL VB | |
|---|---|---|---|
| `foot` | raw[11] 7..6 | `Feet` | ✓ |
| `boots` | raw[11] 5..3 | `Boots` | ✓ |
| `aggression` | raw[11] 2..0 | `Aggression` | ✓ |
| `swerve` | raw[10] 7..5 | `Curve` | ✓ |
| `jump` | raw[10] 4..2 | `Jump` | ✓ |
| `heading` | raw[10] 1..0 + raw[9] 7 | `Head` | ✓ |
| `technique` | raw[9] 6..4 | `Technique` | ✓ |
| `passing` | raw[9] 3..1 | `PassAcc` | ✓ |
| `shot_accuracy` | raw[9] 0 + raw[8] 7..6 | `ShotAcc` | ✓ |
| `shot_power` | raw[8] 5..3 | `ShotPwr` | ✓ |
| `defence` | raw[8] 2..0 | `Defense` | ✓ |
| `attack` | raw[7] 7..5 | `Offense` | ✓ |
| `acceleration` | raw[7] 4..2 | `Acceleration` | ✓ |
| `speed` | raw[7] 1..0 + raw[6] 7 | `Speed` | ✓ |
| `dribbling` | raw[6] 6..4 | `Dribble` | ✓ |
| `stamina` | raw[6] 3..1 | `Stamina` | ✓ |
| `strength` | raw[6] 0 + raw[5] 7..6 | `BodyBalance` | ✓ |
| `reflexes` | raw[5] 4..2 | `Response` | ⚠ largura |
| `age` | raw[5] 1..0 + raw[4] 7..5 | `Age` | ✓ |
| `build` | raw[4] 4..2 | `Body` | ✓ |
| `skin_colour` | raw[4] 1..0 | `SkinColor` | ✓ |
| `out_of_position` | raw[3] 7 | `FeetOutside` | ⚠ **nome** |
| `number` | raw[3] 6..2 | `PlayerNumber` | ✓ |
| `height` | raw[3] 1..0 + raw[2] 7..4 | `Height` | ✓ |
| `beard_colour` | raw[2] 3..1 | `HairColorFace` | ✓ |
| `beard_style` | raw[1] 7..5 | `HairFace` | ⚠ largura |
| `hair_colour` | raw[1] 4..1 | `HairColor` | ⚠ largura |
| `hair_style` | raw[1] 0 + raw[0] 7..4 | `Hair` | ✓ |
| `position` | raw[0] 2..0 | `Position` | ⚠ largura |

Os offsets de exibição (`+12` nas dezoito habilidades, `+15` na idade, `+148`
na altura, `+1` no número) não existem na DLL, que trabalha com o valor cru.
Isso não é divergência — é a mesma coisa em outra convenção.

### 3.3 Os 4 bits de divergência — medidos, e o resultado é nulo

A DLL declara quatro campos **um bit mais largos** que os nossos:

| Campo | Nós | DLL | Bit em disputa |
|---|---|---|---|
| `position` | 3 bits | 4 | raw[0] bit 3 |
| `hair_colour` | 3 bits | 4 | raw[1] bit 4 |
| `beard_style` | 3 bits | 4 | raw[2] bit 0 |
| `reflexes` | 3 bits | 4 | raw[5] bit 5 |

Se a DLL estivesse certa, o nosso decoder estaria truncando quatro atributos.
Testei os quatro bits nos **1.449 jogadores nacionais/all-star** das duas
imagens:

```
                golden-european-deluxe      japanese-shift-jis
raw[0] bit 3         0 em 1449 / 1 em 0        0 em 1449 / 1 em 0
raw[1] bit 4         0 em 1449 / 1 em 0        0 em 1449 / 1 em 0
raw[2] bit 0         0 em 1449 / 1 em 0        0 em 1449 / 1 em 0
raw[5] bit 5         0 em 1449 / 1 em 0        0 em 1449 / 1 em 0
```

**Os quatro bits são zero em todo jogador das duas imagens de varejo.** Os
histogramas de 3 e de 4 bits são idênticos, campo a campo. Portanto:

- não há nada sendo truncado no dado de fábrica;
- a divergência é **inobservável** e não justifica mexer no `Player::Decode()`,
  o que aliás quebraria o `golden`;
- fica registrado como armadilha: uma imagem **já modificada** por essa DLL
  (que grava esses bits) seria lida diferente pelos dois editores. Se algum dia
  aparecer um relato de "jogador com posição errada depois de usar outro
  editor", é aqui que se olha.

O reforço a favor da nossa leitura de 3 bits é o
[src/app/Commands.cpp](../src/app/Commands.cpp): a tabela de pesos das barras
de força é `kWeights[5][8]` — **oito** posições (GK CB SB DH SH OH CF WG). Os
21 `ROLE_NAMES` são outra coisa: papel tático do slot de formação, guardado no
time, não no jogador.

### 3.4 A DLL tem um bug de round-trip — e ele confirma nossa ordem

Em `ReadToFile` a DLL lê `Speed` nos bits 38–40 e `Dribble` nos 41–43 (que é a
ordem certa, igual à nossa). Em `WriteToFile` ela emite, nessa ordem,
`Acceleration`, **`Dribble`**, **`Speed`**, `Stamina` — trocado. Ler e gravar
sem editar nada **troca velocidade por drible** em todo jogador.

Registrado por dois motivos: para não copiarmos a ordem de gravação dela, e
para o caso de aparecer uma imagem que passou por essa ferramenta.

### 3.5 Números de camisa — confirmação dos dois formatos

A DLL implementa os dois esquemas separadamente, e ambos batem com o nosso:

- **Seleções** (`LeerNationNumbers`): 5 bits por jogador, **6 jogadores por
  bloco de 4 bytes**, lidos a partir do extremo menos significativo, valor `+1`.
  É exatamente o `struct SquadNumbers` de
  [src/core/include/we2002/Types.hpp](../src/core/include/we2002/Types.hpp) —
  os grupos de `6 × 5 + 2 = 32` bits que fazem o layout ficar igual entre MSVC e
  GCC. Confirmação independente de que os `pad` de 2 bits estão nos lugares
  certos.
- **Clubes de ML** (`LeerClubNumber`): **1 byte por jogador**, 23 bytes
  corridos, valor `+1`. É o `raw_numbers[23]` que o nosso
  `Database::Load()` lê em `OFS_SQUAD_NUMBERS_ML`.

A DLL, porém, só lê 23 números de seleção (`numberPlayer(22)`) mas percorre 4
blocos de 6 = 24 posições, com um `Exit For` de guarda. O nosso lê o registro
de 16 bytes inteiro. Sem consequência prática.

### 3.6 Um nome nosso que a medição não sustenta

`out_of_position` (raw[3] bit 7) veio do italiano `fuori_ruolo`
([tools/glossary.py](../tools/glossary.py):68) — nome do Moriero, não medição.
A DLL chama o mesmo bit de `FeetOutside`.

Medido na imagem golden, o bit está **ligado em 1.364 dos 1.449 jogadores
(94%)**, e a distribuição dos 85 desligados não é uniforme:

| posição | desligado | ligado | % desligado |
|---|---:|---:|---:|
| 0 (GK) | 47 | 103 | **31%** |
| 1 | 9 | 248 | 3,5% |
| 2 | 4 | 192 | 2,0% |
| 3 | 3 | 184 | 1,6% |
| 4 | 7 | 180 | 3,7% |
| 5 | 5 | 146 | 3,3% |
| 6 | 6 | 267 | 2,2% |
| 7 | 4 | 44 | 8,3% |

Um sinalizador de "fora de posição" não estaria ligado em 94% do elenco, e não
estaria desligado em um terço dos goleiros. **Nenhum dos dois nomes está
demonstrado**, mas o nosso é o menos defensável dos dois. Não é motivo para
renomear agora — renomear atravessa o glossário e os geradores — mas é motivo
para não confiar no nome ao explicar o campo a alguém.

### 3.7 O que não serve

- **O código.** VB.NET, sem licença, e faz o mesmo que o nosso `Player.cpp`
  já faz de forma testada. Copiar não é possível nem útil.
- **A técnica de string binária.** Montar 96 caracteres para ler 3 bits é
  ordens de grandeza mais lento que máscara e deslocamento, e o nosso caminho
  já é verbatim do original — mexer nele quebra o `golden`.

---

## 4. O que trazer, em ordem de custo/benefício

| # | Ideia | Origem | Onde encaixa | Custo | Bloqueio |
|---|---|---|---|---|---|
| 1 | Atualizar a §2.4 do PLAN-STADIUMS: `MODEL.BIN` de "anotado" para formato documentado e verificado | `we3d` | [PLAN-STADIUMS.md](/docs/PLAN-STADIUMS.md) | baixo | nenhum |
| 2 | Registrar o método de derivação do `BASE` na fase S1, junto com o resultado negativo nos `GRDM_*` | `we3d` | [PLAN-STADIUMS.md](/docs/PLAN-STADIUMS.md) §2.2 | baixo | nenhum |
| 3 | Absorver a tabela dos 17 estádios (id, letra, carrossel, nome real) como dado, com crédito | `we3d` | [PLAN-STADIUMS.md](/docs/PLAN-STADIUMS.md) §1 | baixo | nenhum |
| 4 | Abrir `SELECT.BIN` como alvo próprio: 17 × 228 bytes, 60 já conhecidos, 168 por descobrir | `we3d` | [PLAN-FEATURES.md](/docs/PLAN-FEATURES.md), fase nova | médio | precisa da camada ISO9660 (Fase 8) para gravar |
| 5 | Nota de compatibilidade nos 4 bits sobressalentes e no bug speed/dribble de terceiros | DLL VB | [PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) | baixo | nenhum |
| 6 | Anotar que `out_of_position` é nome herdado e não medido | DLL VB + medição | [tools/glossary.py](../tools/glossary.py), comentário | baixo | nenhum |
| 7 | Teste cruzado do nosso parser TMD contra o do `we3d` na mesma peça | `we3d` | fase S1 | baixo | depende do parser existir |
| 8 | Gizmo 3D + campo numérico ligados no mesmo estado, com reset por item | `we3d` | editor tático / visualizador | alto | **paridade fechada primeiro** |

Os itens 1, 2, 3, 5 e 6 são só documentação e podem entrar a qualquer momento.
O 4 é o único que abre superfície nova de gravação em disco.

---

## 5. Licença e crédito

- **`we3d` é MIT.** Código e documentação podem ser reaproveitados **com aviso
  de copyright e crédito**. Se qualquer trecho de `TMDParser.v2.js` ou da
  tabela de estádios virar código nosso, o crédito vai no
  [NOTICE.md](../NOTICE.md), como já foi feito com o CARP.
- **`We2002-Data-Base-Manager` não tem licença** — todos-os-direitos-reservados,
  a mesma situação do código herdado que o [NOTICE.md](../NOTICE.md) descreve.
  Dele sai **conhecimento de formato**, que não é protegível, e nunca código.
  Nada neste documento reproduz o código dele; a tabela da §3.2 é uma
  descrição de layout binário derivada por análise.

---

## 6. Como reproduzir as medições deste documento

Todas rodaram sobre `roms/` sem modificar nada (só leitura). Os dois trechos
abaixo bastam.

Extrair um arquivo do ISO (MODE2/2352, dados em `+24`, 2048 bytes por setor):

```python
RAW, HDR, DATA = 2352, 24, 2048
def sector(f, n):
    f.seek(n*RAW + HDR)
    return f.read(DATA)
# PVD no LBA 16; raiz em pvd[156:190]; percorrer os registros de diretório.
# /BIN/MODEL.BIN  -> LBA 8100,  64.800 bytes
# /BIN/GRDM_A.BIN -> LBA 18125, 46.773 bytes
# /SELECT.BIN     -> LBA 850,  300.648 bytes
```

Percorrer as seções do `MODEL.BIN` e cruzar com a tabela de ponteiros:

```python
BASE, off, secs = 0x8016E800, 0x718, []
while off + 8 <= len(b):
    nv, npr = struct.unpack_from('<II', b, off)
    if nv == 0 and npr == 0: off += 8; continue      # separadores nulos
    secs.append((off, nv, npr))
    off += 8 + npr*24 + nv*8
# 106 seções, terminando em 64.800 = EOF
tbl = struct.unpack_from('<454I', b, 0)
addrs = {v - BASE for v in tbl if v >> 24 == 0x80}
# addrs cobre os 106 inícios de seção
```

Para os 4 bits sobressalentes do bloco de atributos, a leitura tem que
reproduzir os nove saltos de setor de `Database::Load()`
(`OFS_PLAYER_ATTR_1..9`, nos índices 44, 215, 385, 556, 727, 897, 1068, 1239 e
1409 **somados a `PLAYERS_NC = 462`**), com 4, 0, 8, 4, 0, 8, 4, 0 e 8 bytes
lidos antes de cada salto. Ler sem os saltos desalinha tudo a partir do
jogador 506 e produz histograma sem sentido.

---

## 7. Estado

Nada foi alterado no código. Este documento é só análise; os itens da §4 ainda
não viraram tarefa.
