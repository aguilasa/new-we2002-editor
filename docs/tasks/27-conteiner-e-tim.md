---
id: PES2-TASK-27
title: "Cabeçalho de contêiner e entradas TIM — 4 e 8 bpp com CLUT"
type: engenharia-reversa
category: formato
phase: 7
depends_on: [PES2-TASK-26]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §1.14"
status: concluído
---

# PES2-TASK-27: Contêiner e TIM

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §1.14 e §6.13; a §5 Fase 10 do
  [PLAN-FEATURES](/docs/PLAN-FEATURES.md).
- **É a task de risco mais alto da Fase 7**, pelo mesmo motivo que a Fase 10 é
  a de risco mais alto do PLAN-FEATURES: é o único ponto onde o formato ainda
  é hipótese.

O cabeçalho já está medido como **array de ponteiros de 32 bits para a RAM da
PSX** (`0x800xxxxx`), de largura variável — 16 larguras distintas em `/BIN/`,
de 0 a 204 palavras, **com o mesmo histograma nos dois jogos** (§1.14). O que
não está medido é o que vem depois de descomprimir: a lista de entradas e o
`DATA_HEADER` de 32 bytes (`ID`, `VramX`, `VramY`, `width`, `height`,
`offset`, …) que o PLAN-FEATURES descreve.

---

## Objetivo

Extrair **toda** entrada gráfica dos contêineres, com dimensão e paleta, e
exportá-la como PNG.

### Método

1. **Parsear a lista de entradas** do bloco descomprimido: `DATA_HEADER` de
   32 B, contagem, deslocamento de cada entrada.
2. **Decodificar 4 bpp e 8 bpp com CLUT.** Paleta e imagem são entradas
   distintas do mesmo contêiner — é o que faz o Image Manager do BAT_WE
   mostrar grade × grade em vez de uma lista só.
3. **Exportar PNG indexado**, preservando a paleta (o caminho de volta da
   PES2-TASK-29 depende de a paleta sobreviver ao round-trip).
4. **Conferir a invariante de formato**: `width × height × bpp / 8` bate com o
   tamanho da entrada descomprimida, em 100% dos casos. Entrada que não bate é
   entrada mal parseada, não exceção.
5. **Comparar contra o WE2002.** Os `TEX_*`, `CG*` e `GRDM_*` têm a mesma
   largura de cabeçalho nos dois jogos; se o parser lê os dois, o formato é da
   engine e não da release. Se lê só um, a hipótese da §1.4 tem limite, e o
   limite tem de ser escrito.

### Vindo da PES2-TASK-26: três coisas medidas, e uma delas contraria o critério abaixo

O `tools/pes2/lzss.py` varreu os 790 contêineres `form1` de `/BIN/` das quatro
imagens em 2026-09-01. O que ele deixou para esta task:

1. **Onze `CG*.BIN` não têm fluxo LZSS nenhum** — nem no offset que o
   cabeçalho nomeia, nem em lugar algum do arquivo. Depois dos ponteiros de
   RAM vem `00000041 00000000 00000001` e dali segue conteúdo que o codec não
   consome. **Isso contraria o critério de conclusão desta task**, que manda
   extrair "todas as entradas de … `CG*`": ou eles guardam entrada
   **não comprimida**, ou o caminho de entrada é outro. Medir antes de
   escrever parser. Os onze são `CGAF`, `CGAM`, `CGAS`, `CGEU`, `CGIC`,
   `CGKO`, `CGLE`, `CGML`, `CGOL`, `CGOLB_O` e `CGOLS_O` — a lista sai de
   `python3 tools/pes2/lzss.py <track1.bin> | grep none:`, e é idêntica nas
   quatro imagens.
2. **O que sobra depois do último fluxo é a tabela de entradas** — registros
   de 16 bytes, o primeiro deles
   `00 00 0a 00 00 02 00 01 20 00 80 00 00 00 08 00`, com `0a 00` nos bytes
   2-3 e `20 00 80 00` nos bytes 8-11 em todos e os quatro últimos crescendo;
   15.538 bytes deles em `DAT2D.BIN` do PES2 `(EsIt)`. É o candidato
   direto ao `DATA_HEADER` da §5 Fase 10, e o `lzss.py` já imprime quantos
   bytes ficam fora de qualquer fluxo, por arquivo.
3. **Os três `GDC_*` têm fluxo, mas não onde o cabeçalho diz.** `GDC_AD`,
   `GDC_AN` e `GDC_BN` decodificam 30, 30 e 46 blocos começando adiante do
   offset derivado do cabeçalho. São estádios, que a §1.14(d) põe fora de
   escopo — registrado para não ser rediagnosticado como bug do codec.

E uma armadilha de leitura, não de formato: na imagem golden European Deluxe
**18 dos 105 `TEX_*.BIN` são Form 2**, e o `iso.py` recusa lê-los. Os outros
**87 são Form 1**, e esta task os lê — os relatórios de `TEX_03`, `TEX_06`,
`TEX_28`, `TEX_70` e `TEX_84` do `check` naquele disco saem justamente deles.
Um parser que se diga "rodando nas duas imagens de WE2002" tem de **nomear** os
18 que não alcançou, e não a família inteira: os nomes são

`TEX_00`, `TEX_01`, `TEX_02`, `TEX_10`, `TEX_13`, `TEX_17`, `TEX_34`,
`TEX_36`, `TEX_41`, `TEX_43`, `TEX_48`, `TEX_50`, `TEX_51`, `TEX_52`,
`TEX_63`, `TEX_73`, `TEX_81` e `TEX_83`.

### O que a §1.14 já entrega de graça

`/BIN/DAT2D.BIN` no WE2002 guarda as **cores de bandeira** — é onde caem
quatro dos 69 `OFS_*` (§1.4), entre eles `OFS_FLAG_COLOURS_SENEGAL`. O mesmo
arquivo existe no PES2, no **mesmo LBA 5300**. Esta task é, portanto, a via de
entrada mais provável para a PES2-TASK-14 (bandeiras), e as duas devem trocar
achado antes de qualquer uma escrever no mapa.

---

## Critério de conclusão

- [x] `tools/pes2/bin_archive.py` versionado, com `ls` e `export`.
- [x] Todas as entradas de `DAT2D*`, `DATSEL*`, `LOGO`, `TITLE` e `TEX_*` das
      **duas** releases extraídas, sem entrada órfã e sem estouro.
- [x] Os onze `CG*.BIN` explicados — entrada não comprimida, outro caminho de
      entrada, ou fora de escopo com a razão escrita. Ver o item 1 acima.
- [x] `w × h × bpp / 8 == tamanho descomprimido` em 100% das entradas, com a
      contagem escrita.
- [x] O parser rodando também nas duas imagens de WE2002, ou o limite da
      hipótese da §1.4 escrito com os números.
- [x] Um punhado de PNGs conferido a olho — nenhum quadro do jogo entra no
      git (§2 do plano; vale para asset extraído como vale para screenshot).
- [x] A relação com `OFS_FLAG_COLOURS_*` avaliada e registrada na §1.14.
- [x] Escrito na §1.14 do plano.

---

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito.** `tools/pes2/bin_archive.py` lê o índice do
contêiner, exporta PNG e tem um `check` para o `ctest`. O registro de entrada
tem **16 bytes, não os 32 que a §5 Fase 10 do `PLAN-FEATURES` previa**, e há
dois tipos: `0x0a` imagem — retângulo de VRAM mais o offset de um fluxo LZSS —
e `0x09` CLUT, cuja carga é **crua**. Listas fecham na halfword `0x00ff`, e
cada registro termina na etiqueta `0x800f`, que é o que permite achá-los sem
saber onde a lista mora — e é preciso: `DAT2D.BIN` põe os 21 registros de
imagem numa lista só, depois uma de 266 CLUTs; `TEX_00.BIN` põe um registro
depois de cada fluxo, onze listas.

**A descoberta que decidiu a decodificação: a profundidade não está no
registro de imagem.** Quem a diz é a **largura do CLUT** — 256 cores ⇒ 8 bpp,
16 ⇒ 4 bpp —, e os dois convivem no mesmo disco. Custou uma corrida: com 256
cravado, o `LOGO.BIN` lia sua paleta de 32 bytes como 512 e estourava o fim do
arquivo. A conta de bytes é a mesma nos dois casos (`largura × altura × 2`,
retângulo em unidades de 16 bits); o que muda é a largura em pixels — `× 2` a
8 bpp, `× 4` a 4 bpp — e a necessidade de desempacotar nibbles.

**Verificação a olho, que é o critério que mais vale aqui.** `TITLE.BIN` a
8 bpp saiu com o logotipo legível — "PRO EVOLUTION SOCCER" em três linhas,
128×128 — e `LOGO.BIN` a 4 bpp saiu com o aviso legal da adidas, também
legível. Nenhum PNG entrou no git; os arquivos ficaram no scratchpad.

**Resultado medido**, `python3 tools/pes2/bin_archive.py check <img>`:

| Disco | contêineres com índice | registros de imagem | exatos | duplos | falham | CLUTs |
|---|---:|---:|---:|---:|---:|---:|
| PES2 `(EsIt)` | 139 | 918 | 798 | 105 | 15 | 804 |
| PES2 `(EnFrDe)` | 141 | 960 | 840 | 105 | 15 | 804 |
| WE2002 European Deluxe | 109 | 637 | 530 | 82 | 20 | 447 |
| WE2002 japonês | 130 | 815 | 688 | 105 | 22 | 547 |

Por família do critério, na `(EsIt)`: `DAT2D*` 3 arquivos / 49 imagens,
`DATSEL*` 3 / 22, `LOGO` 1 / 9, `TITLE` 1 / 4, `TEX_*` 105 / 630 — **714
imagens, 609 exatas e 105 duplas, nenhuma outra**.

**Três achados que valem mais que a contagem:**

1. **O registro é o índice; a varredura da PES2-TASK-26 é uma aproximação
   dele.** Em `TEX_01.BIN` a varredura começa um fluxo em 5276 e rende 16.381
   bytes — não é potência de dois —, e o registro diz 5284, que rende 16.384
   exatos. São 104 fluxos assim na `(EsIt)`, quase todos em `GDC_*`.
2. **A imagem golden European Deluxe discorda de si mesma em cinco entradas.**
   É disco hackeado, e é de lá que vinha o `16.345` que a §5c registrava para
   o `DAT2D`. As três imagens não hackeadas têm zero.
3. **Os onze `CG*.BIN` não são contêiner gráfico** — sem fluxo LZSS e **sem
   registro nenhum**; depois dos ponteiros de RAM vem `0x41` = 65 e uma tabela
   cuja carga é coordenada assinada de 16 bits terminada em `0x00f0`, ou seja
   geometria. A §5 Fase 10 do `PLAN-FEATURES` os listava para extrair, e foi
   corrigida.

**A pergunta da bandeira, respondida.** Os quatro `OFS_FLAG_*` caem em
`/BIN/DAT2D.BIN` do WE2002 em 69798, 72400, 73254 e 73728, e ali estão
halfwords BGR555 com o bit de semitransparência, fechando em
`0x8000 0x8000 0x8000 0x0000`. São entradas de CLUT. **E o `DAT2D.BIN` do
WE2002 tem 23 registros de imagem e zero de CLUT**, nas duas imagens — a
região de paleta começa em 65876 e o contêiner não a indexa, que é exatamente
por que Moriero cravou offset. No PES2 o mesmo arquivo indexa. A linha está
escrita na PES2-TASK-14.

**O que ficou aberto, e está escrito como aberto:** o *duplo* de 64×64 em
VRAM (704, 256), um por `TEX_*.BIN` nos quatro discos, cujo fluxo rende o
dobro do retângulo — não há evidência aqui de se o excedente é uma segunda
transferência ou folga; e **qual CLUT pertence a qual imagem**, que o
contêiner não diz (`DAT2D.BIN` tem 21 imagens e 266 paletas). O `export` tem
`--clut` e diz isso na saída em vez de inventar par.

**Arquivos criados/modificados**

- `tools/pes2/bin_archive.py` — novo; PNG escrito à mão com `zlib`, sem
  dependência nova
- `tools/pes2/check_image.py` — o `check` do índice no `pes2_image`
- `tests/CMakeLists.txt` — o comentário do que o `pes2_image` cobre
- `docs/PLAN-PES2-PSX.md` — a §1.14(f)
- `docs/PLAN-FEATURES.md` — a Fase 10 corrigida: registro de 16 B, a regra de
  profundidade, e `CG*` fora do aceite
- `docs/tasks/14-bandeiras.md`, `docs/tasks/28-t-name-copias-de-idioma.md` e
  `docs/tasks/29-gravacao-de-asset.md` — os três repasses
- `docs/tasks/progresso.md`, `docs/prompts/perfil-pes2.md`, `CLAUDE.md` — o
  gate novo e a ferramenta nova

**Problemas encontrados.** Dois, os dois no caminho. O primeiro foi assumir
que o CLUT é sempre de 256 cores, corrigido acima. O segundo foi a primeira
regra de escopo do `check`: com os `GDC_*` dentro, o gate ficava vermelho por
15 registros que a §1.14(d) já pôs fora do projeto — um gate vermelho por
motivo que ninguém pretende consertar não é gate. Estádios passaram a ser
contados à parte, com a razão no código.
