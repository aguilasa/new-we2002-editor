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

**Conferência, 2026-10-05 ([KITS-TASK-34](/docs/tasks/concluidos/kits/34-definicao-de-pronto.md)):**
os itens 1 a 4 conferem na HEAD, cada um com o comando no Log da task. O 3 foi
feito com um TEX montado aqui pelo próprio WETex 1.0, sob Wine, a partir dos
registros do `TEX_00`: o arquivo sai com outros bytes (29.928 contra 29.944) e
passa a guarda com as mesmas imagens nas cinco paletas. O item 5 fechou com
uma captura nova do Windows na HEAD: contra a do Linux, 2,37 % de pixels
diferentes (limite 5 %), com outro kit no lugar dando 49,98 %. A captura velha
da KITS-TASK-19, de antes do 3D e do inglês por default, dava 47,56 %.
A metade "a CLI faz tudo o que a janela faz" ficou de fora dessa conferência
— a CLI não desenhava a figura 3D — e fechou com o `cli.py figure`
([CORR-KITS-062](/docs/tasks/concluidos/kits/CORR-KITS-062.md)).

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
([CORR-KITS-013](/docs/tasks/concluidos/kits/CORR-KITS-013.md)). Então o `source.py` também **não** confia no tamanho:
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

A **CLI** (`tools/kits/cli.py`: `info`, `teams`, `export`, `figure`) é o segundo
cliente da fachada e a prova de que ela basta: se a CLI precisar importar algo
além de `api`, a fachada está incompleta. O `figure` é a aba 3D sem janela: a
mesma chamada `api.figure`, na pose de abertura, impressa como peças e digest
por conjunto e figura; o `kits_image` confere que o digest é o da janela e o
`--negative` (conjunto ignorado) fica vermelho
([CORR-KITS-062](/docs/tasks/concluidos/kits/CORR-KITS-062.md); o `check` que esta
lista dava nunca existiu). Ao lado desses quatro ela tem `open`,
o que a fachada faz de cada arquivo (§3.2; `open --negative` monta as fixtures e
confere cada recusa), entrado na KITS-TASK-06 para a evidência sair de comando
versionado, `tex`, a guarda de forma sobre cada TEX de uma origem (§2.1;
`--iso-size` refaz a leitura pelo tamanho ISO, `--negative` o controle 4 do
§5), entrado na KITS-TASK-07 pelo mesmo motivo, e as sondas de medição da fase 0 (`survey`, `rects`, `prims`, `uv`)
([CORR-KITS-012](/docs/tasks/concluidos/kits/CORR-KITS-012.md)).

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
  Windows e no Xvfb, que é o que o `kits_ui` compara (KITS-TASK-25). Um botão
  **Reset view** (e o duplo clique na vista) volta ao giro de abertura. A dica
  da aba dizia que as costas saem vazadas porque a área que o torso amostra está
  vazia no TEX, que o jogo copia as costas da camisa para ela (medido, §4.7) e
  que marcar **Number** pinta ali o painel que a partida monta — sem a caixa, o
  desenho seguia os dados (decisão do usuário, 2026-10-05; KITS-TASK-37,
  CORR-KITS-066, KITS-TASK-40). **Reaberto em 2026-10-07** (K3D-TASK-05, G5 do
  [KITS-AJUSTES-3D](/docs/KITS-AJUSTES-3D.md#g5--figura-inteira-em-qualquer-giro)):
  toda figura recebe a cópia das costas, com ou sem Number, e a dica diz que a
  lacuna sai com as costas que o jogo copia. O seletor de figura tinha um
  terceiro item, **match player**, a figura de partida do `MODEL.BIN` na pose
  medida no jogo (§4.3, KITS-TASK-47). **Reaberto em 2026-10-08** (K3D-TASK-10,
  G3 do [KITS-AJUSTES-3D](/docs/KITS-AJUSTES-3D.md#g3--sem-match-player-só-player-e-goalkeeper)):
  o seletor tem só jogador e goleiro, e a braçadeira e a manga longa vestem o
  jogador do `EDT_MOD.BIN` com as seções do `MODEL.BIN`.
- **Os três checkboxes da aba 3D** (KITS-TASK-40) desenham só o que foi
  medido. **Number**, com o campo do número (0 a 99, abre em 10), pinta nas
  costas de uma figura da `LOOKS SET` o painel que a partida monta (§4.7).
  **Captain armband** e **Long sleeves** só existem no `MODEL.BIN` (§4.3). Com o
  jogador da `LOOKS SET`, marcar um dos dois passava a desenhar a figura de
  partida; desde a K3D-TASK-10, as seções vestem o próprio jogador (G3 do
  KITS-AJUSTES-3D), e o que segue sobre **match player** é registro. Com **match player**, a manga segue o checkbox: longa marcada,
  curta desmarcada. O que não foi medido ficava desligado, com a frase no texto
  do próprio checkbox: a braçadeira no goleiro (até a K3D-TASK-11) e o número
  na figura de partida. O **Long sleeves** ficava **escondido** com o goleiro, que não tem
  manga longa de jogador de linha. **Reaberto em 2026-10-09** (K3D-TASK-11, G4
  do [KITS-AJUSTES-3D](/docs/KITS-AJUSTES-3D.md#g4--number-captain-armband-e-long-sleeves-em-qualquer-combinação-nas-duas-figuras)):
  as três caixas aparecem nas duas figuras. No goleiro, a braçadeira é a seção
  92 medida no jogo, e o **Long sleeves** fica marcado e desligado, com a frase
  de que ele não usa outra manga. Na linha de comando, `ui/app.py --number N`,
  `--armband` e `--long-sleeves` marcam cada um, e `--list-3d` imprime o estado
  dos três. O `kits_ui` julga a mudança de cada um vista das costas, em toda
  combinação das outras, e os checkboxes por figura e língua; as plantas que o
  derrubam são as linhas `plant '…'` de
  `DISPLAY=:98 WE2002_LOOKS_IMAGE=… python3 tools/kits/ui_check.py`.
- **A vista não espelha mais** (KITS-TASK-40). A cena é o espaço do GTE, x à
  direita, y para baixo e z para longe da câmera, com o y invertido pelo
  `looks` (`UP`). Isso deixa um referencial de mão esquerda, e desenhado com x
  para a direita toda figura saía espelhada. O número mostrou isso: "10" saía
  "01". Na figura de partida, a braçadeira aparecia no braço direito. O
  `ui/figure_view.py` agora desenha x com o sinal trocado. Depois da troca o
  "10" lê certo, a braçadeira fica no braço esquerdo e o escudo no peito
  esquerdo. A prova matemática é a do parágrafo do `figure_view.py`; nenhuma
  captura de jogo de costas confronta a vista.
- **Aba "Diagnóstico"**: a lista do `kit.problems`, uma linha por problema da
  guarda ("Refused: …") e uma por nota de leitura ("Note: …"), nas palavras do
  núcleo, com um resumo em cima; TEX sadio lido sem nota deixa a lista vazia
  (KITS-TASK-33). O `kits_ui` julga a aba num `TEX_00` avulso, sadio e com o
  byte do `cli.py tex --negative`, e, com `WE2002_KITS_ED_IMAGE` apontando a
  European Deluxe, nos `TEX_48`, `TEX_70` e `TEX_13` dela; sem a variável ele
  diz que não os julgou.

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

**Primeira metade medida em 2026-09-30 ([KITS-TASK-03](/docs/tasks/concluidos/kits/03-primitivas-por-retangulo.md)),**
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
([CORR-KITS-005](/docs/tasks/concluidos/kits/CORR-KITS-005.md)). Ficou aberta a outra metade, fechada abaixo pela KITS-TASK-39: se a
manga longa e a braçadeira são outra geometria, fora do `EDT_MOD.BIN` — a
imagem existe e o jogo a envia à VRAM, mas quem a desenha não está nesta tela.
Em que retângulo do mapa de zonas cai cada primitiva não foi medido aqui — é o
cruzamento do §4.6, que a
[KITS-TASK-16](/docs/tasks/concluidos/kits/16-zonas.md) fechou sobre a lista de retângulos UV
([CORR-KITS-007](/docs/tasks/concluidos/kits/CORR-KITS-007.md)): nenhuma fora do mapa, e as
15 zonas da imagem de mangas sem primitiva, pelo motivo acima.

A outra metade — quem amostra a imagem de mangas, e portanto quem desenha a
braçadeira e a manga longa — foi medida pela [KITS-TASK-39](/docs/tasks/concluidos/kits/39-medir-bracadeira.md),
logo abaixo: seções do `MODEL.BIN`. As duas só entram na aba 3D com essa
geometria lida. A manga longa entra por pedido do usuário (2026-10-05), num
checkbox que só aparece com o jogador de linha (KITS-TASK-40).

**Medido no jogo em 2026-10-05 ([KITS-TASK-39](/docs/tasks/concluidos/kits/39-medir-bracadeira.md)),
na lista que o quadro entrega ao GPU.** A conta é por primitiva texturizada,
pela página, pelo CLUT e pelos texels de cada uma, e só conta primitiva de 8
bits com CLUT de kit: linhas 486 a 493, x 0. Numa partida, as páginas de kit
também guardam gráficos de 4 bits que não são uniforme.

| slot | tela | primitivas texturizadas | imagem de uniforme | imagem de mangas | manga longa | braçadeira | outras (cotovelo) |
|---|---|---|---|---|---|---|---|
| 2 | `LOOKS SET`, linha | 418 | 104 | **0** | 0 | 0 | 0 |
| 1 | `LOOKS SET`, goleiro | 430 | 190 | **0** | 0 | 0 | 0 |
| 5 | partida, Noruega × Equador, os dois de manga longa, o capitão norueguês com a bola | 789 | 154 | **96** | 80 | 8 | 8 |

As três últimas colunas são uma partição da imagem de mangas: cada primitiva
conta uma vez, a braçadeira primeiro (`oracle.sleeves_kind`). A tabela dizia
88 \| 8 até a [CORR-KITS-068](/docs/tasks/concluidos/kits/CORR-KITS-068.md): os 8 quads da
braçadeira contavam também como manga longa, e os 8 de cotovelo como nada.

**Na `LOOKS SET` a imagem de mangas não é desenhada**, e o jogo confirma a
medição do disco. **Na partida ela é desenhada, por outra geometria:** cada um
dos 48 quads distintos que a amostram está no `/BIN/MODEL.BIN` (48 de 48),
pelos quatro cantos de texel no leiaute `POLY_FT4` que o `section.py` lê. Os
mesmos quads deslocados um texel não estão em arquivo nenhum. Dentro do
`MODEL.BIN`, pelas seções que o `section.scan` acha:

- **a braçadeira é a seção 93**: 6 quads, todos na zona "armband, long sleeve"
  e cada um tocando também uma das duas zonas de capitão acima e abaixo dela;
- **a manga longa são as seções 95 a 102**: 8, 8, 6, 8, 3, 2, 3 e 2 quads. Dois
  deles, nas seções 96 e 98, caem no cotovelo e não numa zona de manga longa.

Na lista do quadro, a Noruega fica na página (576,256) e o Equador na
(640,256), com 45 e 51 primitivas na imagem de mangas. As zonas de capitão do
mapa ("long sleeve, left, captain" e "…, under the armband") aparecem com 4
primitivas cada na lista por zona, que conta uma primitiva em toda zona que
ela toca: são os próprios quads da braçadeira, não outra geometria — o total
exclusivo de manga longa, 80, já é a soma das quatro zonas sem capitão (23 +
22 + 21 + 14).

Comando: `python tools/kits/oracle.py --sleeves 1|2 --expect-sleeves none` e
`--sleeves 5 --expect-sleeves drawn`, com `WE2002_LOOKS_IMAGE` e
`WE2002_LOOKS_DRIVE_IMAGE`. O slot 5 tem cópia mestra em `work/kits-states/`.
O controle é o `--plant-sleeves`, que leva cada texel para a outra imagem e um
texel para a direita. Ele sai 1 nos dois vereditos.

Duas ressalvas. Primeira: é **uma** partida e **um** par de kits, e a regra
diz onde a geometria mora, não que todo time a use igual. Segunda: as
contagens da `LOOKS SET` no quadro (104 e 190) ficam abaixo das 237 e 429 do
disco. A comparação não foi feita peça a peça, e a suspeita, **não medida**, é
que as faces de costas para a câmera saem da lista.

**O encaixe, medido em 2026-10-06 ([KITS-TASK-43](/docs/tasks/concluidos/kits/43-medir-encaixe-mangas.md)),
no mesmo slot 5.** Cada primitiva de kit do quadro foi casada com a primitiva
de modelo que tem os mesmos quatro cantos de texel, e só contou o casamento
com uma seção única. Os jogadores na tela foram separados por contato das
caixas de tela.

- **A figura de partida é o `MODEL.BIN`, não o `EDT_MOD.BIN`.** Das 250
  primitivas de kit, 244 casam só com o `MODEL.BIN`, 0 com o `EDT_MOD.BIN` e 6
  com nenhum dos dois. A aba 3D desenha o `EDT_MOD.BIN`, o modelo da `LOOKS
  SET`.
- **A braçadeira substitui uma peça.** Os jogadores de linha comuns desenham
  as seções `2 7 8 9 10 95 96 97 98`. Os dois capitães, um de cada time,
  desenham `2 7 8 9 10 93 95 96 98`: **a 93 entra no lugar da 97**, a peça de
  manga longa que ela veste. As duas estão num grupo de seis seções (59, 91, 93, 94,
  97 e 100) que guardam o mesmo quad de texels, e esse quad fica de fora da
  conta.
- **O goleiro usa outro conjunto**, `56 61 62 63 64 99 100 101 102`, e as
  mangas longas dele são as 99 a 102.
- **Manga curta contra longa não foi medida aqui**, porque os dois times desta
  partida estão de manga longa. As candidatas eram as seções 91 e 94, do mesmo
  grupo de quad compartilhado. A KITS-TASK-46 mediu depois, logo abaixo: as
  peças de manga curta são a 3, a 5, a 4 e a 6, e a braçadeira de manga curta é
  a 90.

Comando: `python tools/kits/oracle.py --attach 5`, com `WE2002_LOOKS_IMAGE` e
`WE2002_LOOKS_DRIVE_IMAGE`. O quadro fica em `work/kits-oracle/attach-5.json`,
e `--frame-json` relê o arquivo sem emulador. O controle é o
`--plant-attach`, que dá o nome de braçadeira à seção 94 e sai 1 com `no
player draws section 94`.

**Negativa medida: a mesma câmera não separa peça de peça aqui.** Uma câmera
projetiva geral ajustada a cada seção sozinha erra de 0,56 a 2,18 px, fora a
seção 99 do goleiro, com 16,69 px. Ajustada a duas seções juntas, erra de 1,28
a 9,00 px; o par mais justo (95 com 2, no jogador 1) dá 1,28 px contra 1,09 px
da 95 sozinha, dentro da faixa de uma seção só, e mesmo assim não decide nada.
Com 9 ou 10 pontos por seção, contra 11 incógnitas, o ajuste é frouxo
demais para dizer se duas peças dividem a matriz. Isso é limite da medida, e a
resposta exigiria ler a matriz do GTE, como o `looks` faz com o `--pose`.

**O encaixe pela matriz do GTE, medido em 2026-10-06 ([KITS-TASK-44](/docs/tasks/concluidos/kits/44-matriz-gte-model-bin.md)),
no slot 5.** A partida carrega a matriz de cada peça pela mesma instrução que
a `LOOKS SET` (`layout.POSE_PIECE_MATRIX`, 0x8001229C), e os ponteiros vivos
nomeiam seções do `MODEL.BIN`. Valem as duas armadilhas do `looks`: a matriz
de uma parada é da peça que a parada **seguinte** nomeia. Em 600 paradas:

- **Toda peça tem matriz própria.** As 600 matrizes são todas diferentes
  (`600 stop(s), 600 distinct matrices (452 distinct rotations)`), e
  nenhuma seção vestida (93, 95 a 102) divide a matriz com outra peça da mesma
  figura, em nenhuma das 51 figuras inteiras.
- **A braçadeira ocupa o lugar da 97 na ordem de desenho.** Os jogadores de
  linha desenham `cabeça 2 95 96 97 98 7 9 11 8 10 12`, e os dois capitães, de
  cabeças 30 e 34, desenham a mesma ordem com a 93 no lugar da 97. Então a 93
  é a mesma peça do corpo que a 97, só que com outra geometria. O goleiro
  desenha `cabeça 56 99 101 100 102 61 63 62 64`, e a manga longa dele são as
  99 a 102.
- **O atraso de ponteiro se confirma.** Com a matriz dada à peça nomeada uma
  parada depois, as translações de cada figura ficam a 119 a 210 unidades da
  mediana dela, ou seja, um jogador. Dada à peça nomeada na própria parada,
  uma figura pega a cabeça do jogador seguinte, e o espalhamento vai a 878 a
  4.065.

Comando: `python tools/kits/oracle.py --attach-matrix 5`, com
`WE2002_LOOKS_IMAGE` e `WE2002_LOOKS_DRIVE_IMAGE`. As paradas ficam em
`work/kits-oracle/matrix-5.json`, e `--frame-json` relê sem emulador. Os
controles são `--plant-matrix lag` (sem o atraso), que sai 1 nas 51 figuras,
e `--plant-matrix slot` (a braçadeira esperada no lugar da 98), que também sai
1.

Isso fecha a pergunta que o ajuste projetivo da KITS-TASK-43 deixou aberta,
"matriz compartilhada ou própria", e responde **própria**. A
[CORR-KITS-071](/docs/tasks/concluidos/kits/CORR-KITS-071.md) reabriu essa pergunta.
A manga curta foi medida depois, logo abaixo.

**Manga curta, medida em 2026-10-06 ([KITS-TASK-46](/docs/tasks/concluidos/kits/46-manga-curta-partida.md)),
no slot 6:** a mesma partida, Noruega × Equador, com os dois times de manga
curta e o camisa 10 da Noruega, capitão, com a bola. **Manga curta e longa são
seções alternativas das mesmas peças**, na mesma posição da ordem de desenho:

| peça, na ordem | manga longa (slot 5) | manga curta (slot 6) |
|---|---|---|
| jogador de linha, os quatro braços | 95 96 97 98 | 3 5 4 6 |
| braçadeira do capitão | 93, no lugar da 97 | 90, no lugar da 4 |
| goleiro, os quatro braços | 99 101 100 102 | 57 58 59 60 |

O resto da figura não muda: `cabeça 2 … 7 9 11 8 10 12` no jogador de linha e
`cabeça 56 … 61 63 62 64` no goleiro. De manga curta, a imagem de mangas só é
amostrada pela braçadeira, com 4 primitivas na zona "armband, short sleeve",
das seções 90 e 91, que guardam os mesmos quads. Dos braços curtos, o
`--attach 6 --sleeve-length short` vê pelas texturas só as seções 3 e 4 (e as
57 e 59 do goleiro) nas páginas de kit; as 5 e 6, e as 58 e 60, não aparecem
por texel próprio neste quadro ([CORR-KITS-079](/docs/tasks/concluidos/kits/CORR-KITS-079.md)).
Cada peça continua com matriz própria.

Pelo texel a troca da braçadeira não se decide aqui: a 90 tem 5 quads no disco,
1 só dela, e esse não é desenhado neste quadro. O `--attach` com
`--sleeve-length short` diz isso, confere que a 90 aparece em quads
compartilhados e que os capitães são os jogadores de linha sem a 4, e deixa a
troca para o `--attach-matrix`, que a julga pelos ponteiros.

Comando: `python tools/kits/oracle.py --attach-matrix 6 --sleeve-length short`,
`--attach 6 --sleeve-length short` e `--sleeves 6`. O `--plant-attach` com
`--sleeve-length short` sai 1. O controle é o `--plant-matrix slot` com `--sleeve-length
short`, que espera a braçadeira no lugar da 6 e sai 1. A regra de manga longa
aplicada ao slot 6 também sai 1, com `no figure draws section 93`. A tabela
dos dois comprimentos mora em `SLEEVE_LENGTHS`, do `core/figure.py` desde a
KITS-TASK-47; o `oracle.py` a importa de lá.

Foi uma partida, dois times e um capitão por time. O que decide o comprimento
da manga não foi medido.

O `oracle.py --sleeves-image SLOT --page X --tag T`, que compara a imagem de
mangas da VRAM com a do disco bloco a bloco, é **só relatório**: não tem valor
esperado nem planta e sai sempre 0. Os números dele são pista, não veredito, e
nenhuma regra desta seção se apoia neles
([CORR-KITS-082](/docs/tasks/concluidos/kits/CORR-KITS-082.md)).

**O que isso pede da aba 3D.** Desenhar a braçadeira e a manga longa é
desenhar a figura de partida: as seções do `MODEL.BIN` na ordem medida, com a
93 no lugar da 97 de manga longa, ou a 90 no lugar da 4 de manga curta, e uma
pose para elas. Em 2026-10-06 o usuário decidiu abrir esse trabalho:
[KITS-TASK-45](/docs/tasks/concluidos/kits/45-pose-figura-partida.md) captura a pose,
[KITS-TASK-46](/docs/tasks/concluidos/kits/46-manga-curta-partida.md) mediu a manga curta
no slot 6 (a tabela acima), e
[KITS-TASK-47](/docs/tasks/concluidos/kits/47-figura-partida-aba-3d.md) desenha a figura
na aba. Os checkboxes da KITS-TASK-40 vêm depois.

**A pose, medida em 2026-10-06 ([KITS-TASK-45](/docs/tasks/concluidos/kits/45-pose-figura-partida.md)),
no slot 5.** Numa só corrida, com dois breakpoints, o jogo para em cada carga
de matriz por peça (`layout.POSE_PIECE_MATRIX`) e em cada envio de lista ao
GPU (`layout.GPU_LIST_SUBMIT`). As matrizes carregadas desde o envio anterior
são as da lista que o envio entrega: um quadro tem 70 paradas e 6 jogadores na
tela. A projeção do GTE é a mesma nas 70: `H` 1376, `OFX` e `OFY` zero.

O confronto passa os vértices do disco pela matriz de cada peça
(`SX = OFX + H·X/Z`, rotação em 4.12) e compara cada canto com o canto da
primitiva da lista que tem o mesmo texel. Ele se faz dentro do jogador da tela
em que as peças caem melhor. Cada peça das duas figuras escolhidas, com as 12
peças de cada uma, a cabeça e as chuteiras inclusive, cai a uma média de 0,62 a
1,01 px, o arredondamento da coordenada inteira. As figuras são o capitão
(cabeça 30, `30 2 95 96 93 98 7 9 11 8 10 12`) e um jogador de linha (cabeça
24, a mesma ordem com a 97). O limite é 2,0 px (`oracle.POSE_LIMIT`). O
controle é o `--plant-pose`, que dá a cada peça a matriz da parada em que ela
é nomeada, sem o atraso de ponteiro. Com ele a melhor peça fica a 4,72 px, a
pior a 264,70, e a corrida sai 1.

Uma descoberta de leitura: **o texel de cada canto segue a ordem gravada dos
índices** (`Primitive.indices`), não a ordem `corners` que o `section.py`
oferece como desembaraçada. Pareado por `corners`
(`oracle.py --match-pose 5 --pair-by corners`), as peças erram de 1,48 a
4,05 px, 21 das 24 acima do limite de 2,00; pela ordem gravada, o pior é
1,01 px ([CORR-KITS-083](/docs/tasks/concluidos/kits/CORR-KITS-083.md)).

A pose de cada corrida mora em `work/kits-pose/slot5-<cabeça>.json`, fora do git (a
versionada é a do parágrafo seguinte): a projeção
e, por peça, a seção, a rotação e a translação, na ordem de desenho. Comando
que refaz: `python tools/kits/oracle.py --match-pose 5`, com
`WE2002_LOOKS_IMAGE` e `WE2002_LOOKS_DRIVE_IMAGE`. A captura fica em
`work/kits-oracle/pose-5.json`, e `--frame-json` a relê sem emulador. São duas
figuras de um quadro: a pose de um instante de corrida, não um ciclo.

**A figura de partida na aba 3D, desde 2026-10-06 ([KITS-TASK-47](/docs/tasks/concluidos/kits/47-figura-partida-aba-3d.md)).**
*Nota de 2026-10-08 ([K3D-TASK-10](/docs/tasks/kits-3d/10-duas-figuras.md)): a janela não desenha mais
a figura de partida. A aba 3D mostra só `player` e `goalkeeper` do `EDT_MOD.BIN`, vestidos com as
seções de manga e braçadeira do `MODEL.BIN` pela tabela `ARM_PIECES`. O núcleo (`api.match_figure`)
e o `--match-silhouette` continuam; o que este parágrafo diz da aba é registro.*
A pose que a aba lê é versionada em `tools/kits/core/match_pose.json`, escrita
por `python tools/kits/oracle.py --match-pose 5 --write` e nunca à mão. O
`work/kits-pose/` continua sendo a saída de cada corrida. O núcleo
(`api.match_figure`) monta as seções do `MODEL.BIN` na ordem medida, cada uma
pela matriz que o jogo lhe deu. Cada primitiva é texturizada como o
`assembly.draw_list` resolve as da `LOOKS SET`: página e CLUT do disco,
procuradas primeiro no `DAT2D.BIN` e depois no TEX aberto. A cabeça usa os
CLUTs do disco, sem edição de tupla.

A braçadeira e a manga entram por posição na ordem. A peça trocada fica com a
matriz que o jogo deu àquela posição: a 93 no lugar da 97, e na manga curta
3 5 4 6 no lugar de 95 96 97 98, com a 90 no lugar da 4. A troca se apoia no
disco: a 93 e a 97 têm a mesma caixa de vértices, e as curtas diferem das
longas em 3 unidades de x. Na aba a figura é vista no referencial do próprio
torso (seção 2), em pé. Para o confronto ela sai na vista da câmera do jogo.

O confronto é `python tools/kits/oracle.py --match-silhouette 5 --tag 14`. Ele
desenha as duas figuras com o `TEX_14` na vista da câmera, projetadas pelo
`H` medido. O capitão sai com a braçadeira, o jogador de linha sem. Cada
silhueta é comparada com a do jogador que o jogo desenhou no mesmo quadro da
captura (as primitivas do grupo cujos texels uma seção da figura guarda), em
células de 1/4 de pixel. Medido: IoU 0,800 no jogador de linha e 0,821 no
capitão. O limite é 0,70 (`oracle.SILHOUETTE_LIMIT`). O controle é o
`--plant-silhouette`, que desenha toda peça com a matriz do torso, dá 0,322 e
0,284 e sai 1. A borda de uma figura de uns quarenta pixels é o que segura o
IoU abaixo de 1: arredondar nossos cantos ao pixel inteiro dá 0,793 e 0,787,
sem ganho.

### 4.4 (d) O que é (608, 256) e o que é (704, 256)

O [PLAN-LOOKS-PY.md](/docs/PLAN-LOOKS-PY.md)
§1.7 escreve (608, 256) entre os retângulos que só os TEX têm; o `layout.py` e a
leitura do §1.1 dizem (704, 256), que é a bandeira. E na `LOOKS SET` o (704, 256)
é a página da fonte (`EDT_2D.BIN`). Suspeita: a linha do plano do `looks` está
velha. Conferir antes de o 3D pedir qualquer coisa à bandeira.

**Fechada em 2026-09-30 ([KITS-TASK-02](/docs/tasks/concluidos/kits/02-retangulos-608-e-704.md))**,
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
([CORR-KITS-003](/docs/tasks/concluidos/kits/CORR-KITS-003.md)).

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
([CORR-KITS-029](/docs/tasks/concluidos/kits/CORR-KITS-029.md)).

**A entrada da conferência foi medida em 2026-09-30 ([KITS-TASK-04](/docs/tasks/concluidos/kits/04-uv-no-bitmap-de-trabalho.md)).**
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

**Veredito, medido em 2026-10-02 ([KITS-TASK-16](/docs/tasks/concluidos/kits/16-zonas.md)): a
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
rodou ([CORR-KITS-028](/docs/tasks/concluidos/kits/CORR-KITS-028.md)).

### 4.7 (g) As costas e o número

Pedido do usuário em 2026-10-05: o boneco de costas sai vazado e sem número, e
ele quer ligar número e braçadeira na aba 3D. O vazado é a lacuna do torso do
§4.6: 28 primitivas da seção de torso de cada figura amostram (0,80) 20×24 no
jogador e (100,104) 20×24 no goleiro, área de índice 0 em todo pixel dos 210
bitmaps e transparente em 190. O desenho está fiel ao disco; o que não se sabe
é se o jogo **preenche** essa área em tempo de execução — com as costas e o
número de camisa — antes de desenhar.

O que medir, nessa ordem
([KITS-TASK-38](/docs/tasks/concluidos/kits/38-medir-costas-numero.md)):

1. a VRAM da imagem de uniforme em (576,256) + (0,80) 20×24 e + (100,104)
   20×24 com a `LOOKS SET` na tela, pelos dois states: o jogo escreveu ali ou
   continua índice 0;
2. se não escreveu, o mesmo numa partida — o que pede um save state novo,
   decisão do usuário;
3. se escreveu, de onde vêm os texels: a zona "numbers 0-9" (64,68) 60×12, que
   nenhuma primitiva da `LOOKS SET` amostra, é a candidata, e a regra diz onde
   cada dígito cai.

O número só entra na aba 3D com essa regra medida, e nunca por remapeamento de
UV feito à mão (§0). Sem a regra, o checkbox de número fica desligado com a
frase de que não foi medido (KITS-TASK-40).

**Medido em 2026-10-05 ([KITS-TASK-38](/docs/tasks/concluidos/kits/38-medir-costas-numero.md)),
na `LOOKS SET`, nos dois states e com o `TEX_A4` que a tela veste:** o jogo
**escreve** nas duas lacunas, e o que escreve são **as costas, sem número**.

- Fora das lacunas, a página de uniforme em VRAM é a do disco, halfword por
  halfword (0 de 8.192 diferem); dentro delas, os 480 pixels de cada uma têm
  índice diferente de 0, contra 0 no disco.
- A origem é uma **cópia reta da própria página**: o retângulo 20×24 em (44,6)
  vai para (0,80) no jogador, e o em (108,6) vai para (100,104) no goleiro —
  as linhas 6 a 29 da zona "shirt back" de cada figura, pixel por pixel, sem
  espelhar.
- Como a cópia é idêntica à origem, **nenhum dígito é desenhado ali nesta
  tela**. A zona "numbers 0-9" não aparece na lacuna.

Comando: `python tools/kits/oracle.py --back 1|2 --expect-back written`, com
`WE2002_LOOKS_IMAGE` e `WE2002_LOOKS_DRIVE_IMAGE`. O controle é
`--plant-back numbers` (a zona dos números lida no lugar da lacuna) e
`--plant-back tex` (o `TEX_00` como lado do disco); os dois saem 1.

Duas ressalvas do instrumento e da amostra. A VRAM volta como PNG, que perde o
bit STP de cada halfword: o pixel ímpar guarda 7 dos 8 bits do índice, e a
comparação é feita nesses 7. E é **um** kit numa tela: a regra da cópia vale
para o `TEX_A4` na `LOOKS SET`. O número numa partida foi medido depois, logo
abaixo.

**Medido numa partida em 2026-10-06 ([KITS-TASK-42](/docs/tasks/concluidos/kits/42-medir-numero-partida.md)),
no slot 5 que o usuário salvou** (Noruega × Equador, `work/kits-states/`)**:**
na partida o jogo **escreve o número**. Ele usa a área abaixo do mapa, linhas
80 a 127, como uma **grade de painéis de costas** de 20×24, um por jogador em
campo.

- **Onde ficam os painéis.** Os dois do torso começam as fileiras: dez de
  jogador de linha em (20k, 80) e (20k, 104), com k de 0 a 4, e o do goleiro
  em (100,104). São 11 painéis para os 11 em campo. Fora deles, a página é a do
  disco, halfword por halfword. O goleiro pode vestir o outro conjunto: o do
  Equador veste o 2 (§4.1), e as zonas de goleiro saem daí.
- **De onde vêm os texels.** O fundo de cada painel é a zona "shirt back" da
  figura dele, as linhas 6 a 29 em (44,6), ou em (108,6) no goleiro, igual à
  cópia que a `LOOKS SET` faz. Os dígitos vêm da zona "numbers 0-9" (64,68)
  60×12, um glifo de 6×12 por dígito, de 0 a 9 da esquerda para a direita. Só
  a tinta é copiada, e o fundo da zona fica de fora.
- **Onde cai cada dígito.** Na linha 7 do painel, centrados, um glifo a cada
  8 pixels: um dígito em x 7, dois em x 3 e 11. O camisa 10 da Noruega tem o
  "1" em (3,7) e o "0" em (11,7) do painel (60,104).
- **Sobra zero.** Em todos os 22 painéis das duas páginas, todo pixel é fundo
  ou dígito.

| página | TEX | números nos painéis, na ordem da grade |
|---|---|---|
| (576,256) | `TEX_14`, Noruega, conjunto 1 | 3 4 2 5 8 / 6 9 7 10 11 / goleiro 1 |
| (640,256) | `TEX_47`, Equador, conjunto 1, goleiro no 2 | 17 2 3 4 5 / 16 19 10 11 9 / goleiro 1 |

Comandos, com `WE2002_LOOKS_IMAGE` e `WE2002_LOOKS_DRIVE_IMAGE`:
`python tools/kits/oracle.py --back 5 --page 576 --tag 14 --panels` e
`--back 5 --page 640 --tag 47 --keeper-set 2 --panels`. Os controles são dois.
O TEX trocado entre as páginas sai 1: `--page 576 --tag 47` dá 4.557 halfwords
diferentes fora dos painéis. E `--plant-back panels`, que lê cada painel uma
linha acima, sai 1 em todos os 11.

O que **não** foi medido. A ordem da grade não é a dos números, e não se sabe
como o jogo escolhe o painel de cada jogador. A suspeita é que ele troca o UV
do torso de cada um, que no disco aponta para (0,80), mas isso não foi visto.
Para a aba 3D a regra já basta: o painel do número escolhido, montado em (0,80)
ou (100,104), é o que o jogo desenharia nas costas. Também foi uma partida só, com dois
times e números de um e de dois dígitos.

**Na aba 3D desde 2026-10-06 ([KITS-TASK-40](/docs/tasks/concluidos/kits/40-checkboxes-numero-bracadeira.md)).**
O `api.numbered` monta esse painel na lacuna do torso de uma figura da `LOOKS
SET`, com as costas copiadas de (44,6) ou (108,6) e a tinta dos glifos por
cima, e recolore as superfícies do kit pela mesma janela de paleta. O TEX não
é regravado: a composição acontece nos índices já descomprimidos. A prova é o
leitor que mediu os painéis da partida (`oracle.read_panel`, KITS-TASK-42),
aplicado ao painel do núcleo no selftest. Ele lê 7, 10 e 23 nas posições
medidas (linha 7; x 7, ou 3 e 11), sem pixel inexplicado, e o mesmo painel
espelhado não lê 10. As constantes do painel (`GLYPH_W`, `DIGIT_Y`,
`DIGIT_STEP`, `BACK_COPY`) moram no `core/figure.py`, e o `oracle.py` as
importa de lá. Na figura de partida o número não entra: não foi medido qual
painel o torso dela amostra.

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
     `cli.py tex --negative` ([CORR-KITS-014](/docs/tasks/concluidos/kits/CORR-KITS-014.md));
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
| 10 | aba 3D: reset do giro e a dica das costas; costas, número (§4.7), braçadeira e manga longa (§4.3) medidos no jogo, e os checkboxes de número, braçadeira e manga longa (este só com o jogador de linha) com o que se mediu | 6, 7 |
| — | árbitro com a paleta do jogo: só depois da §4.5 | 0 |

As fases 1 a 3 não têm janela nenhuma, de propósito: o núcleo fica pronto e
testado pela CLI antes de existir interface, e é assim que ele chega inteiro à
aplicação única.

**O que não pode ser pulado:** a fase 7. Sem ela o 3D pode trocar titular e
suplente em todos os times, com todo gate verde — é exatamente o que o `TEX_A4`
esconderia.
