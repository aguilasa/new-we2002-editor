---
id: LOOKS-TASK-11
title: "A contradição 8 × 3.568 — qual imagem do `DAT2D.BIN` é o cabelo"
type: engenharia-reversa
category: textura
phase: 3
depends_on: [LOOKS-TASK-10]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#1.8"
reviewed_on: 2026-09-15
review_commit: null
done_on: 2026-09-15
done_commit: "2273318"
---

# LOOKS-TASK-11: Qual imagem é o cabelo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.8 e
  §1.7.
- **Dois documentos da cena se contradizem.** A tabela do CARP rotula o offset
  **8** como *"Pelos Cuerpos y botines"* e o **3.568** como *"Caras"*; o
  tutorial do `zeta` manda abrir o **3.568** para achar os cabelos.
- Os dois não podem estar certos, e **o disco decide**. É barato: exportar as
  duas imagens e olhar.
- Enquanto não estiver decidido, **nenhum código pode cravar nenhum dos dois**.

---

- **A primitiva diz qual página ela amostra, e isso entra na contradição.**
  Desde 2026-09-14 (§1.6, medida pela
  [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md)) sabe-se que
  os bytes 6..7 de cada primitiva são uma **página de textura**, e que nos dois
  arquivos ela vale `0x18`, `0x1A` ou `0x99` — VRAM (512, 256), (640, 256) e
  (576, 256). **A primeira é o gráfico do offset 8**, o que o CARP chama de
  *"Pelos"*; o do offset 3.568 cai em (544, 256), que **nenhuma primitiva
  nomeia como base de página**.

  **Esta linha dizia "evidência a favor do CARP e contra o tutorial do `zeta`",
  e a execução mediu o contrário** (2026-09-15). A ressalva que ela mesma trazia
  era o caminho certo, e a conta é menor do que a linha sugeria: não é preciso
  o `u` passar de 256, basta passar de **127**. Uma página de 4 bits cobre 256
  texels e as imagens deste arquivo têm 128, então a base (512, 256) alcança
  (544, 256) com `u` ≥ 128 — e é lá que `HAIR` e `FACE` amostram. Fica aqui como
  registro de uma leitura que parecia sustentar um lado e sustentava o outro.
- **E `HAIR` anda `v` de `0x20` em `0x20`**, nas quatro quinas das primitivas 1
  e 14 da `MODEL.BIN` seção 24. Se o cabelo é uma faixa de 32 pixels de altura
  num atlas, é nessa página que a faixa tem de aparecer.

---

- **As paletas do `DAT2D.BIN` já estão achadas e lidas** — 267, por
  `python tools/looks/texture.py --report`, medido em 2026-09-15 pela
  [`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md). O que esta
  task ganha com isso é poder **exportar a imagem candidata já colorida**, em
  vez de olhar índices: o cabelo mora em `MODEL.BIN` seção 24, cujas primitivas
  amostram (16, 480) e (144, 480) — dentro da paleta larga da pele corrente.
- **E quatro dos nove CLUT ids da geometria não estão neste arquivo:** os três
  de 8 bits em (0, 485), (0, 486) e (0, 488) — que são os uniformes, jogador de
  linha e goleiro — e um estreito em (336, 510). Junto com as duas páginas de
  textura que a §1.7 já registrava como ausentes, é a mesma pergunta: **de qual
  contêiner vem o resto**. Achar isso é desta task, e o `texture.py` lê qualquer
  `BIN/*.BIN` do disco, não só o `DAT2D.BIN`.
- **Seis seções do `MODEL.BIN` compartilham a paleta da chuteira**, e são
  candidatas nomeáveis pelo mesmo método que nomeou as onze peças. Medido em
  2026-09-15 ([`CORR-LOOKS-023`](/docs/tasks/looks/CORR-LOOKS-023.md)): as
  seções **11, 12, 22, 23, 63 e 64**, cinco primitivas cada, amostram
  (0, 484) — a paleta que no `EDT_MOD.BIN` é só do pé. A cabeça **não** está
  entre elas: a seção 24 amostra (16, 480) e (144, 480) e nunca (0, 484), o que
  reforça que a geometria da cabeça é outra coisa. Luva, meião ou o que for, o
  gesto que nomeia é o da LOOKS-TASK-09 — trocar a opção no jogo e ver o que
  muda.
- **A tabela do CARP acertou os dois rótulos de paleta** (as quatro "Pieles" e
  "Botines"), o que diz que ela foi feita olhando o arquivo — e **não** diz nada
  sobre os rótulos de imagem, que são justamente o que contradiz o tutorial do
  `zeta`. §1.8 do plano.

---

## Objetivo

Resolver a contradição por exportação, e deixar o rótulo de cada uma das 23
imagens conferido ou marcado como não conferido.

---

## Critério de conclusão

- [x] As imagens de offset 8 e 3.568 exportadas para PNG e **olhadas**.
- [x] O veredito registrado com a evidência, e o documento da cena que errou
      fica nomeado — não para culpar, para que ninguém volte a ele.
- [x] Cross-check barato feito, e **os `.tim` não existem**: a pasta
      `Caras - zeta\` traz `cabellowe2002.bmp` (8,1 KB, 128×128 a 4 bpp), o
      `DAT2D.BIN` inteiro já editado e um `.ppf`, e nenhum `.tim` — este
      critério citava dois que não estão lá (corrigido 2026-09-15). O
      `DAT2D.BIN` do próprio `zeta` é um cross-check **melhor** que um `.tim`,
      porque é o contêiner inteiro e se compara registro a registro; foi por
      ele que o BMP se resolveu em 100,0% contra o registro 8.
- [x] Os 23 rótulos ficam numa tabela, cada um marcado **conferido** ou
      **opinião de terceiro**.

---

## Log de Execução

**Executado em:** 2026-09-15

### O veredito: o cabelo é o 3.568, e o `zeta` estava certo

`python tools/looks/atlas.py --check-image`:

```text
  the head is 18 primitive(s): 14 sample the first half of the page and 4 the second
      first half : u  16..62  -> record(s) [8]
      second half: u 152..199 -> record(s) [3568]
  primitive  1 -- HAIR moves it -- samples the record at 3568
  primitive 14 -- HAIR moves it -- samples the record at 3568
  primitive  8 -- FACE moves it -- samples the record at 3568
  primitive 13 -- FACE moves it -- samples the record at 3568
```

**A página é o argumento inteiro, e ela não precisa de olho nenhum.** Uma página
de textura do PSX tem 64 halfwords de VRAM de largura; a 4 bits isso são **256
texels**, e as imagens deste arquivo têm 32 unidades — **128 texels**. Então uma
página cobre **duas** imagens lado a lado:

```text
página (512, 256)   u   0..127  ->  VRAM x 512..543  ->  o registro em 8
                    u 128..255  ->  VRAM x 544..575  ->  o registro em 3.568
```

As dezoito primitivas da cabeça declaram todas `tpage=0x0018`, que é essa página
a 4 bits. As de `HAIR` têm `u` 176..199 e as de `FACE` 152..174 — as quatro na
segunda metade. **Nenhum dos dois campos toca o registro em 8.**

### As primitivas de `FACE`, medidas — e as duas que quase viraram uma

`python tools/looks/oracle.py --fields FACE`, nos dois slots, a partir de
`load_state`:

```text
  FACE, slot 1 (goalkeeper): 43 byte(s)
      /BIN/MODEL.BIN section 24: 8 byte(s), at byte [1, 5, 9, 13] of the primitive
          +15353 primitive 8: 0 -> 16      +15473 primitive 13: 0 -> 16
          +15357 primitive 8: 16 -> 32     +15477 primitive 13: 12 -> 28
          +15361 primitive 8: 0 -> 16      +15481 primitive 13: 0 -> 16
          +15365 primitive 8: 12 -> 28     +15485 primitive 13: 16 -> 32
```

Idêntico no slot 2. **A primeira corrida mostrou só a primitiva 8**, porque o
`report_field` imprimia `hits[:4]` — e quatro linhas são *exatamente* um quad
texturizado. Um campo que move duas primitivas imprimia uma e deixava a outra
para o leitor deduzir. O corte saiu; a seção que um campo toca é pequena por
construção, e listá-la inteira não custa nada.

### Duas testemunhas independentes, e nenhuma é ferramenta nossa

- **O tutorial, lido em vez de resumido:** *"ubiquémonos en el gráfico en el
  offset 3568 ... Tendremos la imagen base de los cabellos"*, e as **32 linhas**
  da tabela dele têm 3.568 em toda a coluna *Gráfico*.
- **A tabela de paletas do mesmo tutorial reproduz a LOOKS-TASK-10** sem ter
  sido perguntada: quatro colunas — *blanca, amarilla, canela, negra* — em
  **65.892 / 66.404 / 66.916 / 67.428**, que são as quatro "Pieles", e oito
  tipos de cabelo andando **32 bytes** dentro de cada uma. Trinta e dois bytes
  são 16 halfwords de VRAM, que é um passo de `x` no CLUT id — e `(16, 480)` é
  justamente o CLUT que as primitivas da cabeça carregam. Duas medições com
  dezenove anos de distância e métodos sem nada em comum, no mesmo lugar.

### O arquivo com o nome da resposta é a outra imagem

`python tools/looks/atlas.py --compare "…/Caras - zeta/cabellowe2002.bmp"`:

```text
  cabellowe2002.bmp: 128x128, 16384 texel(s)
      @     8   85.7% equal   (index  7 covers 19.3% of the record, so a blind guess of it scores 16.6%)
      @  3568    9.2% equal   (index 13 covers 22.3% of the record, so a blind guess of it scores 16.4%)
  closest: the record at 8, 85.7% equal
```

Contra o `DAT2D.BIN` que o próprio `zeta` distribui, o mesmo BMP dá **100,0%**
no registro 8 e 8,6% no 3.568: é **byte a byte** a imagem editada dele. O
arquivo se chama *cabelo* e é a folha de corpos e chuteiras.

**O nulo é o que faz esses números se lerem.** Num registro em que um índice
cobre um quinto dos texels, chutá-lo em toda parte já dá ~16%; 85,7% é acerto e
9,2% é *pior que o chute* — não "diferente", **não relacionado**. Sem a coluna
do nulo os dois números eram indistinguíveis de opinião, e é por isso que o
`--compare` a imprime linha a linha.

### O que sobra, e o que não se cravou

`python tools/looks/atlas.py --labels` — 23 linhas, cada uma marcada:

| offset | VRAM | primitivas | rótulo | proveniência |
|---:|---|---:|---|---|
| 8 | (512, 256) | 1297 | corpos, chuteiras e pele nua | **medido** |
| 3568 | (544, 256) | 369 | cabelo e rosto | **medido** |
| 7456 | (512, 384) | 0 | *Cuerpo* | opinião do CARP |
| 9296 | (544, 384) | 0 | *Redes del arco* | opinião do CARP |
| 10248 | (672, 384) | 136 | não é o jogador: só as seções 0 e 1 do `MODEL.BIN` | **medido** |
| 22200 | (608, 0) | 0 | *Banderitas del menu* | opinião do CARP |
| os outros 17 | — | 0 | — | **sem rótulo** |

A 10.248 é a que exige disciplina: 136 primitivas a amostram, e o CARP diz
"bandeirinha e bolas". O que se mediu é o que ela **não** é — nenhuma das doze
peças da [`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md) a toca
— e o rótulo dela continua sendo opinião.

### E de onde vem o uniforme: a pendência da §1.7, fechada

`python tools/looks/atlas.py --elsewhere`, varrendo os 235 contêineres:

```text
  VRAM rect(s) the geometry samples and /BIN/DAT2D.BIN does not hold:
      ( 576, 256)   1520 corner(s)  in 107 container(s): DATSEL2.BIN, SELECT2.BIN, TEX_00.BIN ...
      ( 576, 384)    652 corner(s)  in 105 container(s): TEX_00.BIN, TEX_01.BIN, TEX_02.BIN ...
      ( 608, 256)   1984 corner(s)  in 107 container(s): DATSEL2.BIN, SELECT2.BIN, TEX_00.BIN ...
  CLUT id(s) the geometry names and /BIN/DAT2D.BIN does not hold:
      (   0, 485) x256     85 primitive(s)  in   0 container(s)  -- IN NONE OF THEM
      (   0, 486) x256    414 primitive(s)  in 105 container(s): TEX_00.BIN x2, TEX_01.BIN x2 ...
      (   0, 488) x256    540 primitive(s)  in 105 container(s): TEX_00.BIN x2, TEX_01.BIN x2 ...
      ( 336, 510) x16     136 primitive(s)  in   0 container(s)  -- IN NONE OF THEM
```

**O uniforme é por time**, e é por isso que não está no arquivo comum: mora nos
**105 `TEX_*.BIN`**. Cada um deles tem **cinco** paletas de 256 entradas, e o
`x2` da saída acima é quantas respondem *àquela id*, não quantas o arquivo tem:

```text
      (   0, 486) x256    414 primitive(s)  in 105 container(s): TEX_00.BIN x2 ...
          256-entry palette(s) per container, in total: 5 in 105 file(s)
```

Duas em (0, 486), duas em (0, 488) e **uma em (256, 480) que a geometria não
nomeia** — o mesmo em todos os 105. Duas ids ficam abertas, em contêiner
nenhum: (0, 485) e (336, 510) — esta última a das 136 primitivas da 10.248.

> **Hipótese, não medição: "casa e fora".** O par por id é explicação plausível
> para `x2`, e **nenhuma corrida desta task trocou o uniforme do time na tela
> para ver qual das duas se move** — que é o método que a
> [`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md) estabeleceu.
> A frase original dizia "duas por arquivo — casa e fora" ao lado de números
> medidos e com a mesma tipografia; corrigida em 2026-09-15
> ([`CORR-LOOKS-025`](/docs/tasks/looks/CORR-LOOKS-025.md)). Quem decidir isto
> troca o uniforme na tela e mede — e a quinta paleta, a de (256, 480), fica
> como pergunta aberta junto.

### Gates medidos

```text
python tools/looks/selftest.py --quiet
  modules:  0 failure(s)
  rules:    0 failure(s)      ..... rule 1 swept 11 file(s), 6438 line(s)
  controls: 0 failure(s)      ..... 21 of 21 controls red
  looks_selftest: 0 failure(s)
```

```text
python tools/looks/atlas.py --check          ->  atlas.py: 0 failure(s)
python tools/looks/atlas.py --check-image    ->  atlas --check-image: ok
python tools/looks/texture.py --check        ->  texture.py: 0 failure(s)
python tools/looks/texture.py --check-image  ->  texture --check-image: ok
python tools/looks/pieces.py --check         ->  pieces.py: 0 failure(s)
python tools/looks/pieces.py --check-image   ->  pieces --check-image: ok
python tools/looks/modelfile.py --check-image->  ok
python tools/looks/oracle.py --check         ->  oracle.py: 0 failure(s)
python tools/check_tasks.py                  ->  123 task(s), ok
```

Os dois controles novos são os dois jeitos de perder este veredito sem sintoma:
`atlas-page-is-one-record` faz o `image_at()` ignorar a coluna — e aí as duas
metades da página viram o mesmo registro, o cabelo e os corpos viram a mesma
folha, e o rótulo do CARP que esta task derrubou voltaria a parecer confirmado;
`atlas-depth-fixed-at-four` fixa a profundidade em 4 bits — e as 1.039
primitivas de kit caem uma página à esquerda, onde o `DAT2D.BIN` *tem*
registros, de modo que a varredura do que falta volta vazia.

Toda leitura de disco saiu do **japonês**, por `WE2002_LOOKS_IMAGE` e pela
guarda do `iso_source`; o emulador bootou o `.cue` **inglês**, e dele não se leu
textura nenhuma. O Superpack foi **lido onde está** — o PDF, o BMP e o
`DAT2D.BIN` do `zeta` —, e nada dele entrou no git. `roms/` só foi lida.

### Arquivos criados/modificados

- `tools/looks/atlas.py` — **novo**. `texel()`, `corners()`, `image_at()`,
  `sampled_by()`, `read_image()`, `write_png()`, `bmp_indices()`,
  `label_rows()`, as tabelas `CARP_LABELS` e `VERDICT`, `self_check()` com os
  casos vermelhos, e os comandos `--check`, `--check-image`, `--labels`,
  `--export`, `--elsewhere` e `--compare`
- `tools/looks/layout.py` — `HEAD_SECTION`, `HAIR_PRIMITIVES`,
  `FACE_PRIMITIVES`, `HAIR_IMAGE`, `SKIN_IMAGE`, `FLAG_IMAGE` e
  `DAT2D_SCENE_LABELS`, com a proveniência de cada um
- `tools/looks/oracle.py` — o `report_field()` imprime **todos** os hits de uma
  seção, não quatro; quatro é um quad, e um campo que move duas primitivas
  mostrava uma
- `tools/looks/controls.py` — `atlas-page-is-one-record` e
  `atlas-depth-fixed-at-four`
- `tools/looks/selftest.py` — `atlas` no `MODULES`
- `docs/PLAN-LOOKS-PY.md` — §1.8 reescrita com o veredito e a evidência, e §1.7
  com a pendência das quatro CLUT ids fechada
- `docs/prompts/perfil-looks.md` — armadilha 13 remedida e a 14 aberta (o nulo),
  o terceiro gate de disco na tabela, e a página nas verificações da Fase 3
- `docs/tasks/looks/12-pele-paleta-ou-vertice.md` — a testemunha de fora e a
  grade de sub-paletas
- `docs/tasks/looks/13-campos-e-dominios-de-looks.md` — a quinta testemunha dos
  domínios, e as duas primitivas de `FACE`
- `docs/tasks/looks/14-tabela-de-montagem.md` — as duas linhas novas, e que a
  linha precisa de imagem além de peça e paleta
- `docs/tasks/looks/15-visualizador-opengl.md` — o atlas exportável, e o
  uniforme que vem de outro arquivo
- `docs/tasks/looks/progresso.md` — tabela e checklist da Fase 3
- `docs/tasks/looks/11-qual-imagem-e-o-cabelo.md` — este arquivo

### Problemas encontrados

- **O cross-check barato que o critério previa deu a resposta contrária, e
  estava certo.** O `cabellowe2002.bmp` devia confirmar o 3.568 e é o 8. Não é
  falha do método: é que o nome do arquivo é rótulo de terceiro como qualquer
  outro. O que salvou a leitura foi o **nulo** — sem ele, 85,7% e 9,2% são dois
  números sem escala, e a tentação é ler o primeiro como "parecido" em vez de
  "é o mesmo arquivo editado".
- **`read_image()` recebia bits onde todo o resto recebe o código de
  profundidade da página**, e `texels_per_unit(4)` respondia 1 em silêncio. A
  exportação saiu **32 px de largura em vez de 128** e não houve erro nenhum —
  só um PNG com a forma errada. A função agora recusa o que não for 0, 1 ou 2.
- **Uma imagem cuja paleta não existe não é motivo para parar.** A 10.248
  amostra `(336, 510)`, que contêiner nenhum do disco tem; o `--export`
  desenhava exceção. Agora desenha em cinza e **diz** que a paleta não existe,
  que é a diferença entre um resultado e um travamento.
- **O `--labels` começou com uma asserção invertida:** exigia que o conjunto dos
  rótulos medidos fosse *igual* ao dos registros amostrados. Registro amostrado
  e ainda não medido é trabalho por fazer, não defeito; a asserção agora é só
  numa direção — rótulo medido sem ninguém que o amostre é que seria uma
  afirmação sem evidência.
- **Duas afirmações da própria task estavam erradas, e as duas foram
  corrigidas no lugar.** A do Contexto dizia que a página `0x18` era
  "evidência a favor do CARP"; a do critério prometia dois `.tim` ao lado do
  BMP, e a pasta do `zeta` não tem nenhum — tem o `DAT2D.BIN` editado inteiro,
  que é cross-check melhor. Divergência entre doc e disco é achado; a correção
  ficou na linha, com a data, e não num apêndice.
- E o de sempre: `ctest -R looks` neste worktree responde `No tests were
  found!!!` e sai 0 ([`CORR-LOOKS-015`](/docs/tasks/looks/CORR-LOOKS-015.md));
  os gates acima saíram da coluna do meio do
  [`perfil-looks.md`](/docs/prompts/perfil-looks.md).
