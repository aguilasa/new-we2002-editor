# Plano — visualizador de uniformes (TEX), 2D e 3D, em Python + Qt

Proposta de 2026-09-29. **Nenhuma fase foi executada**; o que está marcado como
medido foi medido ao escrever este plano, com o comando ao lado.

## 0. Escopo

### Objetivo

Uma ferramenta que abre os uniformes dos times — os 105 `TEX_<tag>.BIN` da
imagem do jogo, ou um TEX avulso feito com WETex — e os mostra de duas formas:

- **2D plano**: as imagens do contêiner como a comunidade as edita (o BMP de
  trabalho de 256×128), com a paleta de verdade, a grade de 16×16 cores e o mapa
  de zonas por cima;
- **3D**: o jogador inteiro vestindo aquele uniforme — titular ou suplente,
  jogador de linha ou goleiro —, montado, na pose e sob a câmera do jogo, com a
  geometria que o `tools/looks/` já lê e já confrontou com o emulador.

### Não-objetivos

- **Não grava.** Nem na imagem nem no TEX. É a mesma decisão do `looks`, pelo
  mesmo motivo: o que falta medir é leitura. Um editor de TEX é outro projeto e
  herdaria as armadilhas do §3.8 e do §4.3 do [SUPERPACK-UNIFORMES.md](/docs/SUPERPACK-UNIFORMES.md).
- **Não inventa geometria.** Manga longa e braçadeira só aparecem no 3D se a
  geometria que as desenha for achada e medida (§4.3). Até lá o 2D as mostra,
  e o 3D diz que não as tem.
- Não é a tela `LOOKS SET`. Aquela janela é a tela do jogo e decide nada; esta
  é uma ferramenta de inspeção, com controles que o jogo não tem.
- **Não é uma interface elaborada.** Ela vai ser absorvida por uma aplicação
  única no futuro; o que precisa durar é o núcleo, e a janela é o mínimo que o
  exercita (§3).

### Definição de pronto

1. A janela abre uma ROM, o combobox lista os times (em inglês se o disco é o
   japonês, com o nome da ROM nos outros), e qualquer dos 105 TEX mostra as 6
   imagens com as 5 paletas, sem uma imagem cinza e sem um índice fora da paleta.
2. O 3D veste o jogador e o goleiro com o titular e o suplente de um time em que
   os dois **diferem** — e o confronto com o emulador (§5) diz que é o mesmo
   uniforme que o jogo desenha.
3. A mesma janela abre um TEX feito com WETex, e um TEX quebrado é **recusado
   com o motivo**, não desenhado torto.
4. O mapa de zonas sobreposto ao 2D foi conferido contra a geometria: toda zona
   que o boneco amostra cai dentro de uma zona do mapa, e o que sobra está
   listado.
5. A CLI faz tudo o que a janela faz sem importar nada além da fachada do
   núcleo, e a janela sai com a mesma paleta e o mesmo painel Fusion no
   Windows e no Linux — a diferença entre as capturas fica na rasterização de
   texto, abaixo do limite que o `ui_check.py --compare` afirma (§3.4). Todo
   texto da janela sai do catálogo de idioma: **inglês dos EUA por default**, e o
   português do Brasil escolhível sem reabrir (§3.4, *Idioma da interface*).

## 1. O que já se sabe

### 1.1 O contêiner, medido nos 105

`tools/pes2/bin_archive.py` lê o TEX, e a leitura dos 105 do disco japonês
(`python tools/kits/cli.py survey roms/japanese-shift-jis.bin`) deu:

| medida | resultado |
|---|---|
| forma | **uma só nos 105**: 6 imagens + 5 CLUTs, sempre nos mesmos retângulos de VRAM e na mesma ordem |
| titular = suplente (imagens e paletas) | **só no `TEX_A4`** |
| imagens diferem entre titular e suplente | 103 |
| só as paletas diferem | 1 (`TEX_98`) |
| paleta do jogador = paleta do goleiro (titular) | 1 (`TEX_A4`) |
| bandeira | o fluxo descomprime em 16.384 bytes, mas a 2ª metade tem **um só valor de byte** em cada um dos 105 (`0xFF` em 93, `0x00` em 12): a imagem é 128×64, como o registro declara, e o resto é enchimento |
| árbitro | **idêntico nos 105** |
| tamanho do arquivo | 25.948 a 34.200 bytes |

A ordem, que o [SUPERPACK-UNIFORMES.md](/docs/SUPERPACK-UNIFORMES.md) §1.1
detalha: imagem uniforme (576, 256), imagem mangas (576, 384), CLUT jogador
(0, 486), CLUT goleiro (0, 488) — duas vezes, titular e suplente —, bandeira
(704, 256) com a CLUT (256, 480), e árbitro (768, 384).

**A consequência que muda o `looks`:** o uniforme que as duas save states vestem
é justamente o **único** em que titular e suplente são iguais. Tudo o que o
`looks` mediu sobre o uniforme é verdade, e nada disso distingue um conjunto do
outro. A pergunta "casa e fora" do [PLAN-LOOKS-PY.md](/docs/PLAN-LOOKS-PY.md)
§1.7 não pode ser respondida com o `TEX_A4`.

### 1.2 Como o uniforme chega ao boneco hoje, no `looks`

- `scene.from_image(..., kit=<tag>)` já aceita **qualquer** das 105 tags, e o
  `ui/app.py --looks <tupla> --kit <tag>` desenha com ela. O `scene.Builder`,
  que alimenta a tela, tinha o `TEX_A4` fixo; desde a KITS-TASK-21 aceita
  `kit=`, com o `TEX_A4` de default.
- Não existe uma VRAM simulada. `assembly.draw_list` monta bancos na ordem
  `[DAT2D, TEX]`, e cada primitiva pede ao `atlas.image_at` o **primeiro**
  registro que cobre o texel; a paleta vem do `texture.covering`, que também
  fica com o primeiro. **Resultado: o titular sempre ganhava**, e não havia
  parâmetro para o suplente. Desde a KITS-TASK-22 há o `kit_set`: o banco do
  TEX é buscado em `texture.in_set_order`, que põe o 2º registro de cada
  retângulo repetido no lugar do 1º, e o `scene.build` ordena as paletas do
  mesmo jeito.
- A paleta de jogador ou de goleiro **não é escolhida em código**: é o CLUT id
  que a própria primitiva carrega. A figura 0 é o jogador de linha, a 1 o
  goleiro.
- Não há manga longa nem braçadeira em lugar nenhum do `looks`. A manga do
  goleiro é outra geometria, não outra textura.

### 1.3 O que a comunidade sabe e o disco não diz

O mapa de zonas em pixels, a ordem das faces, as medidas de cada peça, a regra de
que o índice 0 preto é transparente e a grade de 16 rampas dos TEX originais
estão no [SUPERPACK-UNIFORMES.md](/docs/SUPERPACK-UNIFORMES.md) §1.3 e §2. É a
fonte do mapa de zonas deste projeto, com a proveniência dita: **comunidade,
medido no PNG do polipoli**, e conferido contra a geometria na fase 3 (§4.6).

**A transparência é a regra do console, pela cor** — a entrada `0x0000` com o
bit STP limpo —, e o `flat.py` a aplica assim. "Índice 0 transparente" é essa
regra vista das ferramentas, que forçam preto no índice 0, e **não vale para
todo TEX**: medido na KITS-TASK-15 no disco japonês, o índice 0 é `0x0000` em
95 dos 105 kits em cada uma das quatro paletas de jogador e goleiro, e em 17 das
105 paletas de bandeira (72 têm branco ali) — `cli.py flat roms/japanese-shift-jis.bin`.

O **uniforme 2D** — a camisinha da tela de opções de partida, que não é TEX e
este projeto não cobre — tem o seu próprio levantamento no
[SUPERPACK-UNIFORMES-2D.md](/docs/SUPERPACK-UNIFORMES-2D.md): paletas em
`SELECT2.BIN` (`OFS_KIT_PREVIEW`), 190 ponteiros de modelo, gráficos no
`DATSEL.BIN`. O visualizador/editor dele é outro projeto, o
[PLAN-KIT2D-PY.md](/docs/PLAN-KIT2D-PY.md), que importa daqui o reconhecimento
de origem e os nomes de time (§3.3) — a KITS-TASK-12 e a KITS-TASK-13 passam a
ter um segundo cliente.

## 2. A decisão: projeto novo, núcleo do `looks` por import

**Recomendação: `tools/kits/`, projeto próprio, que importa o núcleo do
`tools/looks/` sem copiá-lo, mais duas mudanças pequenas e aditivas no `looks`.**

Por que não uma v3 do `looks`: a janela do `looks` **é** a tela do jogo e a regra
dela é não decidir nada. Uma aba de paletas, uma grade de zonas e um seletor de
titular e suplente são decisões que o jogo não mostra; dentro daquela janela, ou
viram exceção à regra ou viram outra janela — e outra janela é outro projeto.

Por que não copiar: a geometria, a pose, a câmera, a guarda de disco e a
decodificação de textura custaram 40 tasks e estão confrontadas com o emulador.
Uma cópia envelhece no primeiro conserto.

As duas mudanças no `looks` são **tasks deste ciclo** (fase 5 da §7), que tocam
`tools/looks/`. O ciclo `looks` está arquivado em `docs/tasks/concluidos/looks/`,
e o Rite não liga `depends_on` entre pastas — reabri-lo para duas mudanças
pequenas custaria mais do que fazê-las aqui. Elas são **aditivas**: default
igual ao de hoje, e os gates do `looks` (`looks_selftest`, `looks_image`,
`looks_ui`, `looks_live`) continuam verdes depois delas.

1. **`scene.Builder(kit=...)`**, com o `TEX_A4` de default — antes só o caminho
   de tupla avulsa aceitava outra tag. Feito na KITS-TASK-21.
2. **Escolha do conjunto.** Um parâmetro `kit_set` (1 = titular, 2 = suplente)
   que faça o banco do TEX entregar o 2º par de registros em vez do 1º. A
   pergunta é de ordem de busca, e a resposta cabe no banco — o resto do
   `looks` não muda. Feito na KITS-TASK-22.

### 2.1 Dois discos, e o TEX de fora

O `looks` recusa todo arquivo cujo digest não mediu, e os 105 digests são do
disco japonês. **Para uma ferramenta de uniformes isso é o contrário do que se
quer**: o motivo de ver um TEX é ver o de um patch, o de um BR2002, o que acabou
de sair do WETex. Então:

- **a geometria** (`MODEL.BIN`, `EDT_MOD.BIN`, `ANIME.BIN`, `DAT2D.BIN`) vem do
  disco confiável, pela guarda do `looks`, como hoje (`WE2002_LOOKS_IMAGE`);
- **o TEX** vem de onde o usuário mandar — outra imagem, uma tag, um arquivo
  solto —, e a guarda dele é **de forma**, não de digest: 11 registros, os
  retângulos e as larguras do §1.1, cada fluxo LZSS terminando dentro do arquivo
  e descomprimindo no tamanho que o retângulo pede. O que não bate é recusado
  com a frase de qual registro e por quê.

Isso vira diagnóstico de graça: o TEX corrompido do WECompressor (§4.3 do
SUPERPACK-UNIFORMES) passa a ter um nome.

**Os "18 TEX Form 2" da European Deluxe não são Form 2 — têm a cauda marcada
como Form 2.** Medido em 2026-09-30 na `golden-european-deluxe.bin`:

- nos 18, só os **últimos 1 a 3 setores** do arquivo têm o bit Form 2 no
  subcabeçalho (submode `0x20`); o resto é Form 1. O `iso.py` recusa o arquivo
  inteiro por causa desses poucos;
- nesses setores o dado está **no leiaute Form 1**: 2.048 bytes a partir do
  byte 24, e os bytes 2.072–2.347, que num Form 2 de verdade seriam dado, são
  zero; da cauda de 280 bytes só os 4 do EDC de Form 2 estão preenchidos;
- lendo os 18 com 2.048 bytes por setor, ignorando o bit, **16 saem perfeitos**
  (11 registros, toda imagem descomprime em 16.384). Lendo com 2.324, nenhum.

Leitura provável: a European Deluxe é um patch, os TEX dela são maiores que os
originais, e quem os gravou ocupou setores que antes eram Form 2 sem trocar o
subcabeçalho. O console lê 2.048 bytes por setor e não olha o bit, e é por isso
que o jogo roda. **Não verificado na tela.**

Então a ferramenta **não** herda a recusa. O `source.py` lê a cauda marcada Form
2 no leiaute Form 1 quando os bytes provam que é isso (dado depois dos 2.048
zerado), e o diagnóstico diz que leu assim. Não é trabalho de ler Form 2 de
verdade; é não confiar num bit que o patch deixou errado.

**E o tamanho ISO também mente.** Medido em 2026-10-01 na KITS-TASK-07: na
European Deluxe, **64 dos 105** TEX têm, na tabela de ponteiros do próprio
cabeçalho, uma lista de registros **depois** do tamanho que o diretório ISO
declara — o patch aumentou os arquivos e deixou o tamanho do diretório como
estava. Nos 64, o que o cabeçalho aponta cabe antes do arquivo seguinte — é a
condição para o `tex` ler além do tamanho, e a contagem "64 read past the ISO
size" abaixo é a dos que a cumpriram. Lido pelo tamanho ISO, as recusas são
65: 64 por terem de 8 a 10 registros (54 com 10, 6 com 9, 4 com 8), e o
`TEX_48`, que tem os 11 e cai no LZSS, como cai na leitura nova; lido até onde o
cabeçalho diz que o contêiner acaba, os 64 têm os 11 — sete deles caem depois,
no LZSS ou no tamanho descomprimido, e estão entre os 8 recusados abaixo
([CORR-KITS-013](/docs/tasks/kits/CORR-KITS-013.md)). Então o `source.py` também **não** confia no tamanho:
lê até o fim que o cabeçalho declara (`tex.declared_extent`) quando ele passa
do tamanho ISO e cabe antes do arquivo seguinte, e o diagnóstico diz que leu
assim. Os setores que essa leitura alcança têm o mesmo bit Form 2 errado; os
"18" acima são os que caem **dentro** do tamanho ISO.

```
$ python tools/kits/cli.py tex --iso-size roms/golden-european-deluxe.bin   # a leitura antiga
105 kits: 40 pass, 65 refused; 0 read past the ISO size, 18 with sectors marked Form 2 read as Form 1
$ python tools/kits/cli.py tex roms/golden-european-deluxe.bin
105 kits: 97 pass, 8 refused; 64 read past the ISO size, 67 with sectors marked Form 2 read as Form 1
```

**O `TEX_13` não tem 10 registros.** A versão anterior desta seção dizia que
faltava o árbitro; é o tamanho: o tamanho ISO dele é 31.792 bytes, o cabeçalho
acaba no 32.146, e o árbitro está entre os dois e descomprime em 16.384.

Os 8 que sobram são outra coisa, e são exatamente o que a aba "Diagnóstico"
existe para mostrar — fluxo LZSS que não decodifica ou que não dá o tamanho do
retângulo:

- `TEX_48`: a **primeira imagem** dá "distance 0" no byte 4.810, num setor
  Form 1 — o sintoma de TEX corrompido que o SUPERPACK-UNIFORMES §4.3 atribui
  ao compressor do Walxer;
- `TEX_70`: o 2º uniforme dá "distance 0" no 16.938; `TEX_A2`: o árbitro
  aponta antes do começo da saída;
- `TEX_06`, `TEX_84` (2º uniforme) e `TEX_28` (bandeira) passam de 16.384;
- `TEX_03` (2ª manga, 15.481) e `TEX_92` (árbitro, 16.357) ficam abaixo.

O `tools/pes2/bin_archive.py` tolera seis registros quebrados nessa imagem
(`HACKED`) e nomeia o `TEX_70` no byte 18.052; a guarda acusa o 16.938. **Não
conferido** se os seis dele são seis destes oito.

## 3. Arquitetura

**A regra que manda em todo o resto: núcleo e interface separados por um
contrato só.** A ideia é, no futuro, juntar esta ferramenta, o `looks`, o editor
de `.mcr` e o que vier numa aplicação só. O que tem de sobreviver a essa junção é
o núcleo; a janela deste projeto é descartável e pode ser trocada inteira sem
mexer em uma linha do núcleo.

### 3.1 O núcleo (`tools/kits/core/`)

Python puro, **sem Qt**, sem `print`, sem `sys.exit`, sem estado global. Recebe
caminhos e bytes, devolve dados simples — `dataclass`, `bytes` RGBA, listas — e
erra com exceções tipadas cuja mensagem já é a frase que a interface mostra. Tudo
o que ele faz roda num teste sem tela.

O contrato é **uma fachada**, `core/api.py`, e a interface só importa ela:

```python
source = api.open_source(path)        # ROM (.bin/.iso/.cue) ou TEX avulso, pelo conteúdo
source.kind                           # "rom" ou "tex"
source.teams()                        # [TeamEntry(index, name, name_origin, tag)]  -- só ROM
kit = source.kit(team_or_tag)         # ROM: pelo time; TEX avulso: o próprio arquivo
kit.problems                          # a guarda de forma, registro a registro (§2.1)
kit.flat(image, palette)              # FlatImage(width, height, indices, palette, rgba)
kit.work_bitmap(kit_set, figure)      # o 256×128 da comunidade, uniforme + mangas
kit.palette_grid(palette)             # 256 cores, BGR555 e RGB
api.zone_at(x, y)                     # zona do mapa (§1.3) num ponto do 256×128
api.figure(kit, kit_set, figure, geometry_path, frame=None)   # a cena 3D, via looks
```

`TeamEntry.name_origin` diz de onde o nome veio (`"rom"` ou `"table"`, ver
§3.3), e `tag` é `None` enquanto a incógnita da §4.2 não souber o TEX daquele time.

Os módulos atrás da fachada:

| módulo | faz |
|---|---|
| `source.py` | reconhece o que foi aberto **pelo conteúdo**, não pela extensão: imagem de CD (pelo `iso.py`) ou TEX (pela forma do §1.1); diz qual disco é (§3.3) |
| `tex.py` | lê um TEX, aplica a guarda de forma, nomeia as 6 imagens e as 5 paletas |
| `teams.py` | lê os nomes de time da ROM e aplica a regra do §3.3 |
| `zones.py` | o mapa de zonas como dados, com proveniência por linha |
| `flat.py` | imagem + paleta → RGBA; o BMP de trabalho; a grade de 16×16 |
| `figure.py` | a única ponte com o `looks`: pede a cena ao `scene` |
| `generated/` | as tabelas copiadas do C++ por gerador (§3.3), nunca editadas à mão |

A **CLI** (`tools/kits/cli.py`: `info`, `teams`, `export`, `check`) é o segundo
cliente da fachada e a prova de que ela basta: se a CLI precisar importar algo
além de `api`, a fachada está incompleta. Ao lado desses quatro ela tem `open`,
o que a fachada faz de cada arquivo (§3.2; `open --negative` monta as fixtures e
confere cada recusa), entrado na KITS-TASK-06 para a evidência sair de comando
versionado, `tex`, a guarda de forma sobre cada TEX de uma origem (§2.1;
`--iso-size` refaz a leitura pelo tamanho ISO, `--negative` o controle 4 do
§5), entrado na KITS-TASK-07 pelo mesmo motivo, e as sondas de medição da fase 0 (`survey`, `rects`, `prims`, `uv`)
([CORR-KITS-012](/docs/tasks/kits/CORR-KITS-012.md)).

Endereço só em um módulo, como no `looks` (regra 1 dele): os offsets de nome de
time moram no `generated/`, o resto de endereço no `layout.py` do `looks`.

### 3.2 A origem: ROM ou TEX

A janela abre com **uma escolha só**, "Abrir…", que aceita os dois; o núcleo
decide o que é.

- **ROM**: aparece o **combobox de times**. Escolher um time carrega o TEX dele.
  Enquanto a §4.2 não fechar, o combobox lista as 105 tags (`TEX_00`…
  `TEX_A4`), com o nome do time ao lado só onde o mapeamento já for conhecido;
  fechada a §4.2, ele lista times, na ordem do jogo. **Fechada na KITS-TASK-31:**
  os 95 times na ordem do jogo, cada um com a tag que veste ("Ireland —
  TEX_00"), depois o uniforme padrão da Master League (`TEX_A4`) e por fim as
  nove tags que nenhum time veste (`TEX_95` a `TEX_A3`), que continuam
  escolhíveis. Quem decide a ordem é o núcleo (`api.kit_order`), não a janela.
- **TEX avulso**: sem combobox; o arquivo é o uniforme.

**O 3D precisa da geometria**, que não está no TEX e só foi medida nos discos
japonês e inglês (§2.1). Com um TEX avulso, ou com uma ROM cuja geometria não é a
medida, o 3D usa o disco de `WE2002_LOOKS_IMAGE`; sem ele, a aba 3D fica
desligada **com a frase do motivo**, e o 2D funciona igual.

### 3.3 Os nomes dos times

A regra pedida: **se o nome na ROM está em japonês, mostrar o equivalente em
inglês por índice, hardcoded; senão, o nome que está na ROM.**

- **O nome da ROM** é o que o `we2002_core` já lê (`Team::names`,
  `mixed_case_name`, `kanji_name`, com o `KanjiToAscii` portado verbatim) — o
  mesmo que o `ed.exe` mostra. O núcleo em Python não reescreve esse leitor à mão:
  os offsets (`OFS_TEAM_NAME_*`) e o comprimento de cada nome saem do
  `Offsets.hpp`/`Tables.cpp` por um **gerador com `--check`** registrado no
  `ctest`, como o `rc2ui.py`. Se o C++ mudar, o gerador acusa.
- **A tabela em inglês já existe**: `TEAM_NAMES[120][20]` em
  `src/core/Tables.cpp`, os nomes que o editor original exibe ("Ireland",
  "Scotland", "Wales"…), indexados pelo mesmo índice de time. Ela vai para o
  `generated/` pelo mesmo gerador. Não se escreve uma lista nova.
- **"Está em japonês" é decidido pelo disco, não pelo texto.** O `source.py`
  reconhece o disco pelo executável de boot (`SLPM_870.56` é o japonês) e pelos
  digests que o `looks` já guarda. Adivinhar pelo conteúdo do nome falha em
  silêncio: o `KanjiToAscii` devolve espaço para o que não for par `0x82`, e um
  nome japonês vira uma linha em branco com cara de nome vazio. Disco
  desconhecido cai no nome da ROM, e o `name_origin` diz isso.
- O índice que liga nome e tabela é o mesmo que o combobox de times do `ed.exe`
  usa para indexar `TEAM_NAMES` (a tabela tem 120 linhas para 63 seleções e 32
  clubes da ML; quais linhas valem para qual time se confere no `edDlg.cpp`
  antes de gerar). **Não é a tag do TEX** — essa ligação é a §4.2.

### 3.4 A interface (`tools/kits/ui/`)

Pouca coisa, e só apresentação: widgets que chamam a fachada e desenham o que ela
devolve.

- Barra de cima: **Abrir…**, o caminho aberto, e o **combobox de times** quando
  for ROM.
- **Aba "Plano"**: seletor de imagem e de paleta (só as combinações que o jogo
  usa), zoom de vizinho mais próximo, xadrez no transparente, grade 16×16,
  mapa de zonas ligável, e o mouse dizendo zona, índice e cor. Botão "Exportar
  PNG".
- **Aba "3D"**: titular/suplente, jogador/goleiro, giro livre. Desenhada por
  `QPainter` em software (`ui/figure_view.py`), não OpenGL: o mesmo quadro no
  Windows e no Xvfb, que é o que o `kits_ui` compara (KITS-TASK-25).
- **Aba "Diagnóstico"**: a lista do `kit.problems`.

**Estilo visual próprio, idêntico no Windows e no Linux, e não o do `looks`.**
O `looks` imita a tela do jogo; esta é uma ferramenta comum. Para sair igual nas
duas plataformas:

- `QApplication.setStyle("Fusion")` — um dos dois estilos que o Qt desenha ele
  mesmo nas duas (o outro é o `Windows`, datado); os nativos mudam de
  plataforma para plataforma. No Linux o Fusion já é o default do Qt, então
  tirar a linha não muda nada lá — o controle do `kits_ui` troca por `Windows`
  em vez de tirar (KITS-TASK-19);
- uma `QPalette` fixa, definida no código, sem herdar tema do sistema (claro ou
  escuro do Windows, GTK do Linux);
- fonte com família e tamanho **em pixels** fixados, para o DPI escalado do
  Windows (150 % nesta máquina) não mudar o layout;
- layouts do Qt, não geometria absoluta: esta janela não reproduz tela nenhuma.

A conferência é barata: o mesmo estado capturado nos dois sistemas e comparado
por `ui_check.py --compare A B`, que reprova acima de 5 % de pixels diferentes
(`CROSS_LIMIT`) ou se uma das capturas perde a aparência fixa. Medido em
2026-10-02: 1,95 % entre Windows e Linux, todo em rasterização de texto; outro
kit no lugar do mesmo estado passa de 47 % e reprova (KITS-TASK-19,
CORR-KITS-035).

#### Idioma da interface

Decisão do usuário, 2026-10-03: **todo texto e mensagem da janela é em inglês
dos EUA por default**, com i18n que deixe escolher o idioma. Executado pela
KITS-TASK-36, antes de qualquer outra task aberta.

- **Catálogo em Python puro**, `tools/kits/ui/i18n.py`: um dicionário por
  idioma (`en-US`, `pt-BR`), `tr(chave, **campos)` com `str.format`. Não o
  `.ts`/`.qm` do Qt — sem binário gerado nem `lrelease`, e o selftest importa o
  catálogo sem venv.
- **Quem escolhe**, em ordem: `--lang <código>` no `ui/app.py`, a variável
  `WE2002_KITS_LANG`, e por fim `en-US`. Código desconhecido é **recusado**
  (saída 2, com os códigos aceitos), não trocado pelo default em silêncio.
- **Seletor na janela**: combobox de idioma na barra de cima; trocar reescreve
  rótulos, itens de combo, abas e a linha de status e de leitura sem reabrir.
  Nada persiste entre corridas — estado guardado mudaria a aparência fixa que o
  `kits_ui` compara.
- **O que não se traduz**: o núcleo e a CLI falam só inglês (`kit.problems`,
  notas, erros, nomes de registro e de zona), e com `pt-BR` escolhido essas
  frases aparecem em inglês — limite assumido, não defeito. Nome de time também
  não, porque vem da ROM ou da tabela inglesa (§3.3).
- **A regra vale para o que vier**: a aba 3D (KITS-TASK-25), o combobox de
  times (KITS-TASK-31) e a aba Diagnóstico (KITS-TASK-33) põem todo texto novo
  no catálogo, nas duas línguas. O selftest afirma que as duas línguas têm as
  mesmas chaves e os mesmos campos, e que `ui/app.py` não tem literal de texto
  visível fora de `tr(...)`.

### 3.5 Idioma e ambiente

Como o `looks`: código e docstrings em inglês, documentos em português. O
texto da **interface** é em inglês dos EUA por default, com o português
escolhível (§3.4, *Idioma da interface*). O venv é
o `work/venv-looks/`, que já tem PySide6; o núcleo não precisa dele. `ctest`
ganha `kits_selftest` (sem nada, nunca pula), `kits_image` (com uma ROM),
`kits_ui` (venv e tela) e o `--check` do gerador do §3.3, com a convenção de
*skip* 77.

## 4. As incógnitas, em ordem de risco

### 4.1 (a) Titular e suplente são os pares 1 e 2?

A comunidade inteira diz que sim
e a ordem do arquivo concorda; o jogo nunca foi olhado. Com o §1.1, agora dá:
escolher um time com os dois pares diferentes, entrar numa partida com ele de
suplente e ler a VRAM (`oracle.py --kit` já compara retângulo por retângulo).
**Risco alto**: errar aqui troca todos os uniformes do 3D, e o 2D não percebe.

**Veredito, medido em 2026-10-04 (KITS-TASK-27): sim — titular é o par 1,
suplente é o par 2.** Partida Escócia (1º uniforme) × Dinamarca (2º), save state
`work/kits-states/SLPM-87056_3.sav`, lida por `python3 tools/kits/oracle.py
--slot 3`, que procura cada registro dos 105 TEX em qualquer ponto da VRAM. As
bandeiras dizem as tags: `TEX_01` (azul e branca) é a Escócia, `TEX_13`
(vermelha) a Dinamarca.

- **Paletas, exatas:** a de jogador do `TEX_01` é a do conjunto 1 (registro 2),
  a do `TEX_13` a do conjunto 2 (registro 6).
- **Páginas, pela mais próxima:** na partida a página não sobe inteira — parte
  dela guarda outra coisa —, então nenhuma bate exata. Dinamarca, em (640,256):
  uniforme a 2.640 de 8.192 halfwords do conjunto 2 contra 7.198 do 1; mangas
  4.093 contra 7.693. Escócia, em (576,256): uniforme 4.746 do conjunto 1 contra
  5.050 do 2, mangas 2.995 contra 4.211 — a margem é menor porque o 1º e o 2º
  uniforme dela se parecem mais; a paleta exata é o que decide.

**E o que a pergunta não previa: o goleiro escolhe à parte.** O goleiro da
Escócia veste a paleta de goleiro do conjunto **2** (registro 7), com o time de
linha no conjunto 1. O jogo decide o uniforme do goleiro separado do resto do
time, provavelmente para não repetir a cor do outro goleiro — **não verificado**.
O `kit_set` da fase 5 troca as duas paletas juntas, o que é certo para um time
inteiro de titular ou de suplente e não reproduz essa combinação.

Também medido: numa partida cada time tem seu lugar — páginas em x 576 e x 640,
paletas de jogador nas linhas 486 e 487, de goleiro em 488 e 489, cada uma com
uma cópia quatro linhas abaixo —, e não os retângulos que o TEX declara.

### 4.2 (b) Que time usa qual tag

Nada no repositório sabia, até a KITS-TASK-30. O Wetigre dá a ordem de
cabeça do WE2000 (`TEX_00` Irlanda, `01` Irlanda do Norte, `02` Escócia…); o
editor do Obocaman em `we-team-editor/` insere TEX por time e portanto contém a
tabela; o emulador responde time a time pelo `--kit`. **É ela que decide o
combobox do §3.2**: sem ela o combobox lista tags, com nome só onde já se sabe.
Os nomes (§3.3) e o mapeamento são coisas separadas — o nome sai da ROM por
índice de time, e o índice de time não diz qual TEX o time veste.

**Veredito (KITS-TASK-30): o time de índice `i` (0 a 94) veste o `TEX` de
número `i` na ordem do disco** — `TEX_00` a `TEX_94` —, e o item seguinte do
editor do Obocaman ("95 Master L." / "95 Default ML") vai para o `TEX_A4`. A
regra é a que o próprio `we-team-editor.exe` calcula no diálogo de textura,
`índice + 9 × (índice div 95)` como número do TEX, lida das instruções do exe
em dois lugares (`python tools/kits/gen_tables.py --editor`; com o divisor
trocado numa cópia, `--negative-editor` reprova). A ordem de cabeça do WE2000
do Wetigre **não** vale para o WE2002: lá o `TEX_01` seria a Irlanda do Norte,
e aqui é a Escócia, medida. A tabela é gerada em
`tools/kits/core/generated/team_kits.py`, e `gen_tables.py --report` a conta:
95 times, quatro conferidos no jogo pela VRAM (`oracle.py --expect`) —
Irlanda → `TEX_00` e Brasil → `TEX_41` no slot 4, Escócia → `TEX_01` e
Dinamarca → `TEX_13` no slot 3 —, e **nove tags que nenhum item alcança**,
`TEX_95` a `TEX_A3`: o que elas vestem continua sem resposta.

### 4.3 (c) Manga longa e braçadeira no 3D

A imagem de mangas (576, 384) é
enviada à VRAM na `LOOKS SET`, mas não se sabe quais primitivas a amostram nem se
o modelo de partida é o mesmo do `EDT_MOD.BIN`. Medir primeiro, no disco:
quantas primitivas de cada figura caem em cada retângulo do TEX e em que
retângulo do mapa de zonas. Se a manga longa e a braçadeira forem outra
geometria (outro arquivo, outra lista de seções), elas entram só quando essa
geometria for lida — **nunca** por remapeamento de UV feito à mão.

**Primeira metade medida em 2026-09-30 ([KITS-TASK-03](/docs/tasks/kits/03-primitivas-por-retangulo.md)),**
com `python tools/kits/cli.py prims roms/japanese-shift-jis.bin` (tupla
`A-A1-A-A-A`, geometria e resolução pelo `draw_list` do `looks`, e os quatro
cantos de cada primitiva conferidos contra todo registro do TEX):

| figura | primitivas | `DAT2D` | TEX, uniforme (576, 256) | mangas (576, 384) | bandeira, árbitro | caixa dos cantos no TEX |
|---|---|---|---|---|---|---|
| 0, linha | 593 | 356 | 237 | **0** | 0 | (576,256)..(607,359) |
| 1, goleiro | 629 | 200 | 429 | **0** | 0 | (600,256)..(639,383) |

**A imagem de mangas não é amostrada por primitiva nenhuma das duas figuras
da `LOOKS SET`.** Tudo o que o boneco tira do TEX sai da imagem de uniforme: o
jogador de linha da metade esquerda, o goleiro da direita, que vai até a última
linha (383) e nenhuma além. A contagem é a mesma nos 105 TEX e independe da
tupla fora a cabeça, que amostra o `DAT2D`: `python tools/kits/cli.py prims
roms/japanese-shift-jis.bin --all-kits` dá 105 kits e um resultado distinto, e
`--tuple` repetido com oito tuplas, uma por campo mexido, dá os papéis do kit
iguais nas oito (237/429) com o total mudando só com o cabelo (603/639 em
`A-P1-A-A-A`, 598/634 em `A-I3-A-G-A`). O controle das duas conferências é
`--all-kits --negative`: com o uniforme do `TEX_A4` tirado do lugar o
agrupamento se parte em 104 e 1
([CORR-KITS-005](/docs/tasks/kits/CORR-KITS-005.md)). Fica aberta a outra metade: se a
manga longa e a braçadeira são outra geometria, fora do `EDT_MOD.BIN` — a
imagem existe e o jogo a envia à VRAM, mas quem a desenha não está nesta tela.
Em que retângulo do mapa de zonas cai cada primitiva não foi medido aqui — é o
cruzamento do §4.6, que a
[KITS-TASK-16](/docs/tasks/kits/16-zonas.md) fechou sobre a lista de retângulos UV
([CORR-KITS-007](/docs/tasks/kits/CORR-KITS-007.md)): nenhuma fora do mapa, e as
15 zonas da imagem de mangas sem primitiva, pelo motivo acima.

### 4.4 (d) O que é (608, 256) e o que é (704, 256)

O [PLAN-LOOKS-PY.md](/docs/PLAN-LOOKS-PY.md)
§1.7 escreve (608, 256) entre os retângulos que só os TEX têm; o `layout.py` e a
leitura do §1.1 dizem (704, 256), que é a bandeira. E na `LOOKS SET` o (704, 256)
é a página da fonte (`EDT_2D.BIN`). Suspeita: a linha do plano do `looks` está
velha. Conferir antes de o 3D pedir qualquer coisa à bandeira.

**Fechada em 2026-09-30 ([KITS-TASK-02](/docs/tasks/kits/02-retangulos-608-e-704.md))**,
com `python tools/kits/cli.py rects roms/japanese-shift-jis.bin 608,256 704,256`:

- **(608, 256) não é origem de registro nenhum do disco** — "0 start there". É
  a metade direita do uniforme: o registro de (576, 256), 64×128 halfwords, dos
  105 TEX o cobre (duas vezes por arquivo, titular e suplente), e o
  `SELECT2.BIN` o cobre com uma imagem de 32×128 em (592, 256). A linha do
  PLAN-LOOKS §1.7 vinha do `atlas.py --elsewhere`, que agrupa os cantos
  amostrados em baldes de 32 colunas (`x // 32 * 32`): (576, 256) e (608, 256)
  são dois baldes do mesmo retângulo. A suspeita estava certa.
- **(704, 256) é origem de verdade, de 116 arquivos e dois formatos.** Nos 105
  TEX é a bandeira, 64×64 halfwords; em onze outros contêineres — `EDT_2D.BIN`
  (a fonte da `LOOKS SET`), `DATSEL3.BIN` e nove `LC_*.BIN` — é uma imagem de
  32×128 no mesmo canto. São telas diferentes carregando a própria página no
  mesmo lugar da VRAM, e as duas leituras são verdade: **na `LOOKS SET`, o
  (704, 256) é a fonte, não a bandeira** — o 3D não pode pedir a bandeira à
  VRAM daquela tela.

A lista dos onze sai de `python tools/kits/cli.py rects --all
roms/japanese-shift-jis.bin 704,256`, e o controle negativo da busca de
`python tools/kits/cli.py rects --negative roms/japanese-shift-jis.bin 608,256`:
com as duas origens de uniforme do `TEX_A4` deslocadas de 576 para 640, os donos
de (608, 256) caem de 106 para 105 arquivos e de 211 para 209 registros
([CORR-KITS-003](/docs/tasks/kits/CORR-KITS-003.md)).

### 4.5 (e) A paleta do árbitro

Não está no TEX. As duas tabelas do Superpack
divergem em 32 bytes (SUPERPACK-UNIFORMES §5). Se o `SELECT.BIN` for um
contêiner, o `bin_archive.py` acha os registros de CLUT e decide sozinho; se não
for, vale o emulador numa partida. Até lá o árbitro sai com a paleta que o
usuário escolher, e a janela diz que não é a do jogo.

### 4.6 (f) A zona do mapa bate com a geometria?

O mapa é da comunidade. A conferência
é mecânica: toda primitiva do boneco com UV no TEX cai numa zona do mapa, e zona
que nenhuma primitiva amostra traz o motivo declarado — ou está errada. Os
motivos aceitos são dois, e é a ferramenta que os imprime: a zona é da imagem de
mangas, que nenhuma primitiva desta tela amostra (manga longa, braçadeira,
cotovelos, a manga curta de capitão das duas figuras — §4.3), ou é a dos números, que
quem desenha o número de camisa não está nesta tela. A frase dizia antes "manga
longa, braçadeira e figurantes com bandeira", e o veredito abaixo aceitou os
números por outro motivo; a regra foi reescrita para bater
([CORR-KITS-029](/docs/tasks/kits/CORR-KITS-029.md)).

**A entrada da conferência foi medida em 2026-09-30 ([KITS-TASK-04](/docs/tasks/kits/04-uv-no-bitmap-de-trabalho.md)).**
Ela não é um arquivo versionado: mora no comando, que a refaz do disco —
`python tools/kits/cli.py uv <imagem> --json` dá o retângulo de UV de cada
primitiva no bitmap de trabalho de 256×128 (uniforme em x 0–127, mangas em
128–255), e o texto sem `--json` fecha com o sha256 da lista, que no disco
japonês é `2360a921…48fb84` e não muda com o TEX (é geometria).

| figura | primitivas do TEX | caixa no bitmap (px, inclusiva) | px nos retângulos¹ | fora do 256×128 |
|---|---|---|---|---|
| 0, linha | 237 | (0,0)..(63,103) | 4.117 | **0** |
| 1, goleiro | 429 | (48,0)..(127,127) | 3.825 | **0** |

¹ Cobertura pelos retângulos envolventes dos cantos, não rasterização dos
triângulos.

Toda primitiva cai dentro do bitmap, e toda na metade do uniforme — nenhuma na
das mangas (§4.3). As duas figuras dividem a imagem de uniforme e se sobrepõem
em x 48–63. A fase 3 cruza essa lista com o mapa de zonas.

**Veredito, medido em 2026-10-02 ([KITS-TASK-16](/docs/tasks/kits/16-zonas.md)): a
§4.6 vale, com seis lacunas declaradas** — tronco e gola nas duas figuras, a gola em dois retângulos cada; o número é o da linha `gaps: (...)` do `cli.py zones`. O mapa é o `ZONES` do
`tools/kits/core/zones.py` — cada linha remedida do `Zonas We2002.png` do
polipoli, e `cli.py zones --map <Zonas We2002.png>` confere: nenhum pixel pintado
fora de zona, e só a zona dos números guarda fundo dentro, porque os dígitos são
desenhados sobre ele. A frente da camisa **não é retângulo**: a gola sobe entre
os ombros, e o mapa a guarda em quatro linhas. `python tools/kits/cli.py zones
roms/japanese-shift-jis.bin`:

| figura | primitivas | numa zona | entre zonas vizinhas | em lacuna declarada | fora do mapa |
|---|---|---|---|---|---|
| 0, linha | 237 | 201 | 7 | 29 | **0** |
| 1, goleiro | 429 | 377 | 23 | 29 | **0** |

As lacunas são o que o jogo amostra e o mapa deixa sem zona — o `GAPS`, medido
aqui, não da comunidade:

- **o torso abaixo do mapa** — 28 primitivas da seção de torso de cada figura
  amostram (0,80) 20×24 no jogador e (100,104) 20×24 no goleiro, com a paleta do
  kit, onde o mapa diz "não usado". Ali o índice é 0 em todo pixel nos 210
  bitmaps de trabalho (105 kits × 2 conjuntos), transparente em 190: nos 10 kits
  cujo índice 0 não é `0x0000` (§1.3) essas primitivas saem opacas;
- **a gola entre os ombros** — o quad da gola, (19,5)..(24,7), cobre o recorte
  que o mapa deixa vazio entre os ombros: (20,5) 4×1 e (21,6) 2×1, e o mesmo
  64 px à direita no goleiro. Índice 0 em 190 dos 210, transparente em 210 no
  jogador e 207 no goleiro. É o retângulo envolvente do quad, não rasterização.

**As zonas que nenhuma primitiva amostra são 16 das 49**, cada uma com o motivo:

- **os números** (64,68) 60×12 — nenhuma primitiva da `LOOKS SET` os amostra; quem
  desenha o número de camisa não está nesta tela;
- **as 15 da imagem de mangas** (x 160–191): o antebraço esquerdo e o direito, a
  manga longa esquerda e a direita, as três faixas de capitão com a braçadeira
  (manga longa, manga curta do jogador, manga curta do goleiro) e os dois
  cotovelos — a imagem de mangas não é amostrada na `LOOKS SET` (§4.3).

Do lado do jogador e do goleiro na imagem de uniforme, toda zona é amostrada.

As medidas do ramonpsx (`Medidas TEX we2002.txt`) ficam ao lado do mapa como
`MEASURES`: 14 das 21 batem com ele. As que não batem são a frente (22×22 contra
20×22), as costas (20×25 contra 20×30; o SUPERPACK-UNIFORMES §2.4 já dizia "20×25
visível"), o calção do goleiro (64×18 contra 32×18, uma perna só no mapa) e a
"playera metida" 20×5, que o mapa não tem como zona própria.

O controle 4 do §5 é `cli.py zones --negative`: com o mapa deslocado 1 px à
direita, 11 primitivas do jogador e 5 do goleiro caem fora do mapa e o veredito
reprova; o `--map --negative` faz o mesmo contra o PNG (248 pixels pintados fora
de zona). Os dois rodam no `kits_image`; os dois do `--map` só quando
`WE2002_KITS_ZONES_PNG` aponta o `Zonas We2002.png` do polipoli, que é arquivo do
usuário e não entra no repositório — sem a variável o `kits_image` diz que não os
rodou ([CORR-KITS-028](/docs/tasks/kits/CORR-KITS-028.md)).

## 5. Como se verifica

1. **Dois decodificadores concordam.** `tex.py` e `bin_archive.py export` sobre
   as mesmas 105 tags, imagem por imagem e paleta por paleta
   (`cli.py export --confront <imagem>`; `--negative` muda um pixel do nosso
   lado, que tem de divergir).
2. **A comunidade como oráculo externo.** O Superpack tem ~150 pares
   `*_BND.bin` + `*_BND.tim` em `Banderas 3D/`: o `.bin` saiu do WEZip a partir
   do `.tim`, então a nossa descompressão do `.bin` tem de devolver os pixels do
   `.tim` byte a byte. É um oráculo que não passou pelo nosso código — o papel
   que os 50 JPGs tiveram no `looks`. Medido na KITS-TASK-10: são **160** pares,
   e os 160 batem (`WE2002_KITS_CORPUS=<…/Banderas 3D> python tools/kits/confront.py`;
   `--negative` troca um pixel de uma cópia do `.tim`, que tem de reprovar).
3. **O emulador julga o 3D.** Com o time da §4.1 em campo: o retângulo que o
   jogo enviou é o conjunto que a ferramenta disse, e o confronto por histograma
   de cor do `looks` (`confront.py --score`) é refeito com outro uniforme que não
   o `A4`.
   Medido na KITS-TASK-28, sobre o quadro de partida que
   `oracle.py --slot 3 --out work/kits-oracle/match-3` grava (Escócia `TEX_01`
   no conjunto 1 × Dinamarca `TEX_13` no 2; duas corridas deram o mesmo
   `screen.png`, sha256 `ee1bfba6…`): seis caixas de jogador de linha medidas
   nesse quadro, três por time, contra o nosso 3D de frente e de costas, com o
   limiar `KIT_CONTROL_MARGIN` do `looks` (0,05). Os jogadores da Escócia dão
   **0,770** ao nosso `TEX_01` e 0,429 ao `TEX_13`; os da Dinamarca, **0,759**
   ao `TEX_13` e 0,349 ao `TEX_01` (`python tools/kits/confront.py --score`).
   O controle troca os dois renders e tem de reprovar os dois times
   (`--score --negative`); outro quadro é recusado pelo digest, porque as caixas
   valem só para ele.
4. **Controles negativos**, plantados por comando como no `looks`:
   - trocar as paletas 486 e 488 tem de trocar jogador e goleiro no 3D;
   - um byte trocado no fluxo LZSS de um TEX tem de ser **recusado** pela guarda
     de forma;
   - na European Deluxe, dado nos bytes 2072–2347 de um setor marcado Form 2
     tem de dar `KitUnreadable`, e um arquivo posto logo depois dos setores ISO
     de um TEX cujo cabeçalho acaba além deles tem de parar a leitura no tamanho
     ISO e deixar o TEX recusado — as duas regras do §2.1, no
     `cli.py tex --negative` ([CORR-KITS-014](/docs/tasks/kits/CORR-KITS-014.md));
   - o mapa de zonas deslocado 1 px tem de reprovar a §4.6;
   - pedir o suplente do `TEX_A4` tem de dar o mesmo quadro que o titular, e
     de qualquer tag do §1.1 que difere, um quadro diferente.

## 6. Riscos de projeto

- **Mexer num projeto arquivado.** O ciclo `looks` fechou, e as duas mudanças do
  §2 são feitas por este ciclo dentro de `tools/looks/`. O risco é quebrar o que
  lá foi confrontado com o emulador sem ninguém do `looks` olhando; a defesa é a
  task da fase 5 exigir os quatro gates do `looks` verdes antes e depois, e as
  mudanças serem aditivas, com o comportamento de hoje como default.
- **Acoplamento.** Importar o núcleo do `looks` amarra este projeto às mudanças
  de lá. É o preço de não copiar; o `kits_selftest` roda os self-checks do
  `looks` que usa, para a quebra aparecer aqui e não na janela.
- **Licença.** Nada do Superpack entra no repositório — nem os mapas, nem os
  `.tim`. O mapa de zonas é reescrito como dados medidos, com a fonte citada; os
  pares de bandeira são lidos de `WE2002_KITS_CORPUS`, uma pasta do usuário, como
  o `WE2002_LOOKS_CORPUS`.

## 7. Fases

| fase | entrega | depende de |
|---|---|---|
| 0 | as medições das §4.3, §4.4 e §4.6 feitas no disco, e o levantamento do §1.1 promovido a `cli.py survey` (medição em `core/survey.py`) | — |
| 1 | **núcleo, lado TEX**: `api.py` (a fachada), `source.py`, `tex.py`, guarda de forma, `cli.py info/export`; confrontos 1 e 2 do §5 | 0 |
| 2 | **núcleo, lado ROM**: o gerador do §3.3 com `--check` no `ctest`, `teams.py`, `cli.py teams`; a regra japonês → tabela conferida nas duas imagens de `roms/` | 1 |
| 3 | `flat.py` + `zones.py`; §4.6 fechada — ainda sem janela | 1 |
| 4 | **a janela mínima**: Abrir… (ROM ou TEX), combobox, aba "Plano", estilo Fusion fixo; texto em inglês dos EUA por default, com catálogo de idioma (KITS-TASK-36); capturas do Windows e do Linux com a mesma aparência, diferindo só no texto e abaixo do limite do `--compare` | 2, 3 |
| 5 | as duas mudanças do §2 em `tools/looks/`, feitas por este ciclo; gates do `looks` verdes antes e depois | — |
| 6 | `figure.py` e a aba "3D": titular/suplente, jogador/goleiro | 4, 5 |
| 7 | §4.1 no emulador e o confronto 3 do §5 | 6 |
| 8 | §4.2: o combobox passa a listar times em vez de tags | 2 |
| 9 | aba "Diagnóstico" | 1 |
| — | manga longa, braçadeira e árbitro com a paleta do jogo: só depois das §4.3 e §4.5 | 0 |

As fases 1 a 3 não têm janela nenhuma, de propósito: o núcleo fica pronto e
testado pela CLI antes de existir interface, e é assim que ele chega inteiro à
aplicação única.

**O que não pode ser pulado:** a fase 7. Sem ela o 3D pode trocar titular e
suplente em todos os times, com todo gate verde — é exatamente o que o `TEX_A4`
esconderia.
