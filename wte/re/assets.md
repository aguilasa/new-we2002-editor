# Convenção dos assets — os 198 bitmaps e o `dat.bin`

Produto da **WTE-TASK-08**. Responde como cada família de arquivo em
`we-team-editor/image/` e `we-team-editor/data/` é endereçada pelo
`we-team-editor.exe`, com o sítio da evidência para cada afirmação.

- **Alvo:** `we-team-editor/we-team-editor.exe` (C++Builder 6, PE32), lido; nunca escrito.
- **Entrada de RE anterior:** [`strings.tsv`](strings.tsv) (WTE-TASK-05),
  [`published_methods.tsv`](published_methods.tsv) (WTE-TASK-04),
  [`dfm/`](dfm/) (WTE-TASK-03), [`offsets.md`](offsets.md) (WTE-TASK-06).
- **Ressalva legal:** isto é *especificação recuperada por observação* — contagens,
  endereços, tamanhos e ordem de operação. Nenhum decompilado (§2 do
  [plano](../../docs/PLAN-WTE-LAZARUS.md)). As poucas linhas de assembly citadas
  seguem o formato já usado em [`offsets.md`](offsets.md): endereço, mnemônico e
  comentário.

---

## 0. Rota escolhida: comando inline, sem gerador

**Não foi escrita ferramenta.** Cada número abaixo traz o comando exato que o
reproduz, no espírito do que a CORR-WTE-002 exigiu de
[`ambiente.md`](ambiente.md).

O critério foi o do [`tools/README.md`](../tools/README.md) ao contrário: gerador
existe para **enumerar** — 766 strings, 96 handlers, 189 offsets —, e o `--check`
existe para provar que ninguém editou a enumeração à mão. Aqui o produto não é
uma enumeração: são ~15 medidas (cinco contagens de arquivo, três endereços de
tabela, quatro deslocamentos de paleta, dois tamanhos de bloco), cada uma de uma
linha, e um texto que as amarra. Um `assets_dump.py` seria andaime em volta de
prosa, e o `--check` estaria guardando a prosa, não a medida.

O que **é** enumerável aqui — as três tabelas de 95 entradas — não vira arquivo
nesta task: a task 08 declara `wte/re/assets.md` como único arquivo a criar, e
quem precisa da tabela linha a linha é a **WTE-TASK-32**. O comando que a extrai
está na §3.2 e na §4.1; que ela vire TSV é decisão de lá.

### 0.1 Os dois utilitários usados em todo comando

Ler um endereço virtual de `.data` como offset de arquivo. As seções vêm de
`objdump -h`: `.data` tem VMA `0x00423000` e *file offset* `0x00022200`, logo
`off = va - 0x423000 + 0x22200`.

```sh
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
objdump -h we-team-editor/we-team-editor.exe | sed -n '4,12p'
```

Desmontar uma faixa:

```sh
objdump -d -M intel --start-address=0xAAAA --stop-address=0xBBBB \
        we-team-editor/we-team-editor.exe
```

---

## 1. O inventário: **198**, não 197

```sh
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
find we-team-editor -iname '*.bmp' | wc -l                       # 198
for d in we-team-editor/image/*/; do
  printf '%-40s %s\n' "$d" "$(ls "$d" | wc -l)"; done
ls we-team-editor/image/*.bmp
```

| Família | Arquivos | Nomes |
|---|--:|---|
| `image/banderas/` | 53 | `bandera0..43`, `bandera52..60` |
| `image/uniformes2d/` | 105 | `camiseta0..98` (99) + `pantalon0..5` (6) |
| `image/pelo/` | 32 | `pelo_0..31` |
| `image/barba/` | 7 | `barba_0..6` |
| `image/careto_base.bmp` | 1 | nome fixo |
| **total** | **198** | |

**Veredito sobre 198 × 197.** Não há bitmap a mais nem a menos: a §1.8 do plano
lista as cinco linhas certas — 53 + 105 + 32 + 7 + 1 — e a prosa logo abaixo
delas diz "197 bitmaps". **O erro é de soma na prosa, não no inventário.** O
`careto_base.bmp` que o [`../README.md`](../README.md) apontou como "diferença
provável" está contado nas duas listas; ele apenas mora solto na raiz de
`image/`, o que faz o olho pular a linha ao somar os quatro subdiretórios
(53+105+32+7 = 197). Reconciliar o texto da §1.8 é da **WTE-TASK-09**; este
documento deixa o número medido.

### 1.1 Formato: todos os 198 são BMP de 256 cores, sem compressão

```sh
python3 - <<'PY'
import struct, glob, collections
def hdr(p):
    d = open(p,"rb").read(54)
    return (*struct.unpack_from("<ii", d, 18),          # width, height
            struct.unpack_from("<H", d, 28)[0],          # bits per pixel
            struct.unpack_from("<I", d, 30)[0],          # compression
            struct.unpack_from("<I", d, 10)[0])          # offset dos pixels
for g, pat in (("banderas","image/banderas/*.bmp"),
               ("camiseta","image/uniformes2d/camiseta*.bmp"),
               ("pantalon","image/uniformes2d/pantalon*.bmp"),
               ("pelo","image/pelo/*.bmp"),
               ("barba","image/barba/*.bmp"),
               ("careto_base","image/careto_base.bmp")):
    c = collections.Counter(hdr(p) for p in glob.glob("we-team-editor/"+pat))
    print(f"{g:12s} {dict(c)}")
PY
```

| Família | Dimensão | bpp | Compressão | Pixels em |
|---|---|--:|---|--:|
| `bandera*` | 20 × 16 | 8 | `BI_RGB` | 1078 |
| `camiseta0..49` | 40 × 42 | 8 | `BI_RGB` | 1078 |
| `camiseta50..98` | 51 × 42 | 8 | `BI_RGB` | 1078 |
| `pantalon*` | 40 × 22 | 8 | `BI_RGB` | 1078 |
| `pelo_*` | 140 × 150 | 8 | `BI_RGB` | 1078 |
| `barba_*` | 57 × 50 | 8 | `BI_RGB` | 1078 |
| `careto_base` | 182 × 224 | 8 | `BI_RGB` | 1078 |

1078 = 54 (cabeçalho) + 256 × 4 (paleta). **Isso não é detalhe de formato: é a
razão de toda a mecânica da §6.** Os bitmaps guardam *forma*; a *cor* mora na
paleta, e é a paleta que o editor reescreve.

---

## 2. Onde o app procura: `GetCurrentDir()`, não o diretório do executável

Seis `AnsiString` globais montadas em `MainForm.FormCreate` (`0x004107c8`):

```
4107f6:  call 0x422408              ; rtl60.bpl :: @Sysutils@GetCurrentDir$qqrv
4107fe:  mov  eax,0x432e84          ; 0x432e84 <- diretorio corrente
41081e:  lea  edx,[edi+0x8f2]       ; "\image"   (edi = 0x424754)
41084a:  mov  eax,0x432e6c          ; 0x432e6c <- <cwd>\image
```

O import foi resolvido pela IAT, não por adivinhação: o thunk em `0x00422408`
salta por `ds:0x0043e53c`, e essa entrada é `@Sysutils@GetCurrentDir$qqrv`.

```sh
objdump -d -M intel --start-address=0x410790 --stop-address=0x410a70 \
        we-team-editor/we-team-editor.exe | grep -E '0x432e|edi\+0x[89]'
```

| Global | Conteúdo | Consumidor |
|---|---|---|
| `0x00432e84` | `<cwd>` | base de tudo |
| `0x00432e6c` | `<cwd>\image` | base das quatro pastas de imagem |
| `0x00432e70` | `<cwd>\image\barba` | `sub_407338` |
| `0x00432e74` | `<cwd>\image\pelo` | `sub_407110` |
| `0x00432e78` | `<cwd>\image\banderas` | `sub_405270`, `sub_405468` |
| `0x00432e7c` | `<cwd>\image\uniformes2d` | `sub_4056c8` |
| `0x00432e80` | `<cwd>\data` | `dat.bin` (§8) |

Os seis literais de diretório estão contíguos em `.data`, em
`0x00425046`…`0x00425071`, e são consumidos nessa ordem — `\image`, `\barba`,
`\pelo`, `\banderas`, `\uniformes2d`, `\data`. O
[`strings.tsv`](strings.tsv) os traz sem `referenciada_por` justamente porque
`.text` os alcança por `edi + deslocamento`, não por imediato.

> **Para a WTE-TASK-39.** O original **não** resolve relativo ao executável: usa
> o diretório corrente. É por isso que existe a mensagem `The file "dat.bin" must
> be in the "data" directory` (`0x004250bd`) — clicar no `.exe` a partir de outra
> pasta quebra tudo. A ordem de busca acordada na decisão 1 do
> [`../README.md`](../README.md) (`$WTE_ASSETS_DIR` → ao lado do executável →
> prefixo instalado → árvore de fonte) é, portanto, uma **divergência
> deliberada**, e das boas. Registrar em §7.3 do plano quando a 39 for executada.

---

## 3. Bandeiras: o número é a **forma** da bandeira, não o país

### 3.1 Como o nome é montado

Dois renderizadores gêmeos, um por lista de time da tela principal:

| Função | Time | String base | Chamada por |
|---|---|---|---|
| `sub_405270` | 1 | `"\bandera"` `0x004247ea` | `MainForm.lista_equiposChange`, e 10 sítios de `ficha_color` |
| `sub_405468` | 2 | `"\bandera"` `0x004247fd` | `MainForm.lista_equipos_2Change` |

O caminho é concatenação simples, sem `%d`: `*0x432e78 + "\bandera" + <n> + ".bmp"`.

```
4052c3:  mov  edx,0x4247ea          ; "\bandera"
405303:  mov  edx,0x4247f3          ; ".bmp"
4052d8:  mov  eax,0x432e78          ; <cwd>\image\banderas
```

```sh
objdump -d -M intel --start-address=0x405270 --stop-address=0x405470 \
        we-team-editor/we-team-editor.exe
```

> **Onde o [`strings.tsv`](strings.tsv) parece falhar e não falha.** A coluna
> `handler` está vazia para `\bandera`, `\camiseta`, `\pantalon`, `\pelo_`,
> `\barba_` e `\careto_base.bmp`. Está certa: os sítios estão em auxiliares
> **não publicados** (`sub_405270`, `sub_4056c8`, …), fora dos 96 corpos que a
> WTE-TASK-04 delimitou. Quem tem dono publicado é o *chamador*, e é ele que as
> tabelas deste documento nomeiam.

### 3.2 O índice é **direto**, e vem da imagem de CD

`sub_4050d0` lê o estado visual do time da imagem. Um dos campos é **um byte**:

```
4050f4:  push 0x432f14              ; destino
4050f9:  mov  ecx,0x1               ; 1 byte
4050fe:  mov  edx,ds:0x4331e8       ; offset na imagem (calculado em runtime)
405106:  call 0x4033bc              ; leitura
```

Esse byte (`0x00432f14`) é copiado para `0x00432f15` e é o `<n>` do nome do
arquivo. Não há tabela de indireção entre o byte e o nome: `bandera<n>.bmp`.

O `.exe` traz, porém, **uma tabela de 95 bytes em `0x004231e8`** — a forma de
bandeira *padrão* de cada time. Ela fica exatamente colada ao limite superior da
tabela de offsets que a [WTE-TASK-06](offsets.md) mediu ("próximo endereço de
`.data` referenciado por `.text`: `0x004231e8`"). Os dois achados se encaixam: o
vizinho de cima da tabela de offsets é esta.

```sh
python3 - <<'PY'
d = open("we-team-editor/we-team-editor.exe","rb").read()
rd = lambda va,n: d[va-0x423000+0x22200 : va-0x423000+0x22200+n]
t = rd(0x4231e8, 95)
print("entradas :", len(t))
print("distintas:", len(set(t)))
print("faltando :", sorted(set(range(61)) - set(t)))
print(" ".join(f"{x:02x}" for x in t))
PY
```

```
entradas : 95
distintas: 53
faltando : [44, 45, 46, 47, 48, 49, 50, 51]
```

### 3.3 Os buracos: são **oito**, não sete, e não são buracos

O conjunto das 53 formas usadas pela tabela é **exatamente** o conjunto dos 53
arquivos em disco. Os índices ausentes são `44..51` — **oito**, não sete: o
enunciado da task e a §1.8 do plano contam 61 − 53 = 7 por engano.

```sh
comm -13 <(ls we-team-editor/image/banderas | sed 's/bandera//;s/\.bmp//' | sort -n) \
         <(seq 0 60) | tr '\n' ' '        # 44 45 46 47 48 49 50 51
```

**O app nunca pede um índice ausente**, e não por acaso: o único jeito de o
usuário trocar a forma é o combo `lista_col0` de `ficha_color`, e ele **indexa a
tabela**, não digita o número.

```
40688f:  mov  eax,[ebx+0x39c]       ; ficha_color.lista_col0
406897:  call [edx+0xc8]            ; ItemIndex
40689d:  mov  cl,[eax+0x4231e8]     ; forma = tabela[ItemIndex]
4068a3:  mov  ds:0x432f15,cl
4068a9:  call 0x405270              ; redesenha
```

O caminho inverso, ao trocar de time, procura na mesma tabela a **primeira**
posição cujo valor bate com a forma lida da imagem, e é essa posição que o combo
passa a exibir (`MainForm.lista_equiposChange`, `0x0040d1f2`…`0x0040d217`).
Consequência observável: para uma forma compartilhada, o combo mostra sempre o
primeiro time que a usa, não o time selecionado.

Os 95 itens de `lista_col0` são os nomes de time — `'  0 Irlanda'` …
`'94 Boca Juniors'` —, o que fecha a leitura "use a bandeira que o time N usa":

```sh
python3 - <<'PY'
import re
t = open("wte/re/dfm/ficha_color.dfm", encoding="latin-1").read()
m = re.search(r"object lista_col0.*?Items\.Strings = \((.*?)\)\n", t, re.S)
i = re.findall(r"'([^']*)'", m.group(1))
print(len(i), i[:2], i[-1])
PY
```

```
95 ['  0 Irlanda', '  1 Escocia '] 94 Boca Juniors
```

**95 é o número de times do formato**, o mesmo dos arrays `TEAM_NAME_LEN_*[95]`
de [`Tables.hpp`](../../src/core/include/we2002/Tables.hpp) — 63 seleções (0..62)
+ 32 clubes de Master League (63..94). O `MainForm.lista_equiposChange` corta em
`cmp eax,0x5f` (`0x0040d1d6`): índice ≥ 95 não tem bandeira.

### 3.4 Por que a forma é compartilhada

Agrupando a tabela por valor sai a explicação:

```sh
python3 - <<'PY'
import re, collections
d = open("we-team-editor/we-team-editor.exe","rb").read()
rd = lambda va,n: d[va-0x423000+0x22200 : va-0x423000+0x22200+n]
src = open("src/core/Tables.cpp", encoding="utf-8").read()
m = re.search(r"TEAM_NAMES\[120\]\[20\]\s*=\s*\{(.*?)\n\};", src, re.S)
names = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
g = collections.defaultdict(list)
for i, f in enumerate(rd(0x4231e8, 95)):
    g[f].append(names[i])
for k in (0, 7, 9):
    print(f"bandera{k}: {g[k]}")
PY
```

```
bandera0: Ireland, France, Belgium, Italy, Romania, Nigeria, Cameroon, ...
bandera7: Netherlands, Germany, Austria, Hungary, Serbia, Russia, Colombia, ...
bandera9: Denmark, Norway, Sweden, Iceland
```

Tricolor **vertical**, tricolor **horizontal**, **cruz nórdica**. O
`bandera<n>.bmp` é um **estêncil de 20 × 16 com 16 cores úteis**; a cor sai da
imagem de CD e é escrita na paleta do arquivo antes de exibir (§6). É a mesma
leitura que o `newWe2002` já carrega no nome `OFS_FLAG_SHAPE_COPY_1..5`
([`offsets.tsv`](offsets.tsv)) — "shape", não "flag".

Alvos na tela — dois recebem arquivo, dois recebem cópia:

| `TImage` | Campo | Como é preenchido |
|---|---|---|
| `MainForm.bandera` (80 × 48) | `MainForm+0x444` | `sub_405270` → `LoadFromFile` (time 1) |
| `MainForm.banderita2` (30 × 12) | `MainForm+0x450` | `sub_405468` → `LoadFromFile` (time 2) |
| `MainForm.banderita1` (30 × 12) | `MainForm+0x44c` | `TPicture::Assign` de `bandera` |
| `estrategia.bandera` (79 × 47) | — | `TPicture::Assign` de `bandera` |

`TPicture::Assign` é `0x00422632`, chamado de `lista_equiposChange`,
`lista_equipos_2Change`, `colorearClick` e `mostrar_estrategiaClick`. Quando as
duas listas apontam para o mesmo time, `lista_equipos_2Change` pula o
`sub_405468` e só copia (`0x0040e2ae`).

---

## 4. Uniformes 2D: 99 camisas + 6 calções, **por tabela**, dois jogos por time

`sub_4056c8(time, jogo)` monta os **dois** nomes de uma vez —
`*0x432e7c + "\camiseta" + <n> + ".bmp"` e `... + "\pantalon" + <n> + ".bmp"`.
Chamado de `MainForm.lista_equiposChange`, `MainForm.colorearClick` e de 11
sítios de `ficha_color`.

### 4.1 A tabela: `0x004232a6`, 95 × 4 bytes

```
405719:  lea  ecx,[edx*4+0x4232a6]  ; edx = time
405720:  mov  bl,[ecx+eax*2]        ; eax = jogo (0 ou 1)  -> camiseta
4058e7:  lea  eax,[ecx*4+0x4232a7]
4058f3:  mov  bl,[eax+edx*2]        ;                      -> pantalon
```

Layout: `camiseta = tab[time*4 + jogo*2]`, `pantalon = tab[time*4 + jogo*2 + 1]`,
com `jogo ∈ {0,1}` — os dois itens de `ficha_color.lista_col1`
(`'Primeiro'`, `'Segundo'`).

```sh
python3 - <<'PY'
d = open("we-team-editor/we-team-editor.exe","rb").read()
rd = lambda va,n: d[va-0x423000+0x22200 : va-0x423000+0x22200+n]
k = rd(0x4232a6, 95*4)
cam, pan = k[0::2], k[1::2]                       # 190 slots = 95 times x 2 jogos
print("camiseta:", min(cam), "..", max(cam), " distintas", len(set(cam)),
      " faltando", sorted(set(range(99)) - set(cam)))
print("pantalon:", sorted(set(pan)))
nat = [k[t*4+j*2] for t in range(63)     for j in (0,1)]
clu = [k[t*4+j*2] for t in range(63, 95) for j in (0,1)]
print("times  0..62 :", min(nat), "..", max(nat))
print("times 63..94 :", min(clu), "..", max(clu))
PY
```

```
camiseta: 0 .. 98  distintas 99  faltando []
pantalon: [0, 1, 2, 3, 4, 5]
times  0..62 : 0 .. 49
times 63..94 : 50 .. 98
```

**As 105 imagens são todas alcançadas, nenhuma sobra.** E o corte bate com a
largura medida na §1.1: `camiseta0..49` têm 40 px e servem as 63 seleções;
`camiseta50..98` têm 51 px e servem os 32 clubes de ML. 63 × 2 = 126 slots sobre
50 padrões, 32 × 2 = 64 slots sobre 49 — há compartilhamento nos dois lados.

Como a bandeira, **o índice é o padrão do tecido** (liso, listras verticais,
faixa…), não o time; a cor vem da imagem (§6). Diferente da bandeira em um ponto
que importa: a forma da camisa **não é lida da imagem de CD** — é constante do
`.exe`, um par fixo por time.

Alvos na tela: `MainForm.home1` (80 × 42, campos `MainForm+0x48c`) e
`MainForm.home2` (80 × 22, `+0x490`). As alturas 42 e 22 batem exatamente com as
dos bitmaps; a largura é esticada.

---

## 5. Cara, cabelo e barba: índice = posição de um `TUpDown` do formulário `jugador`

| Arquivo | Função | Índice vem de | `Max` no DFM | Arquivos |
|---|---|---|--:|--:|
| `image/careto_base.bmp` | `sub_406fe0` | — (nome fixo) | — | 1 |
| `image/pelo/pelo_<n>.bmp` | `sub_407110` | `jugador.flechasapa3` (`+0x424`) | 31 | 32 |
| `image/barba/barba_<n>.bmp` | `sub_407338` | `jugador.flechasapa5` (`+0x42c`) | 6 | 7 |

```
40712b:  mov  edx,ds:0x433e38       ; o formulario jugador
407131:  mov  eax,[edx+0x424]       ; flechasapa3
407137:  call 0x422946              ; ->Position
407172:  mov  edx,0x4249c1          ; "\pelo_"
```

`Max + 1` casa com a contagem de arquivos nas duas famílias — 32 e 7 — e nenhum
outro `TUpDown` do formulário tem esses limites em posições vizinhas:

```sh
grep -nE 'object flechasapa|Max = ' wte/re/dfm/jugador.dfm | grep -A1 flechasapa
```

Os 12 `flechasapa` têm `Max` = 7, 3, 31, 7, 6, 6, 63, 7, 31, 7, 2, 1. O
despachante `jugador.flechasapaClick` (`0x00408088`) corta o sufixo do
`Sender->Name` (`SubString(11,2)` — "flechasapa" tem 10 letras) e compara com
literais em `.data`:

| Sufixo | O que é | Redesenha |
|---|---|---|
| `2` (`Max` 3) | tom de pele | `careto_base` + `pelo` + `barba` |
| `3` (`Max` 31) | **forma** do cabelo | `pelo` |
| `4` (`Max` 7) | cor do cabelo | `pelo` |
| `5` (`Max` 6) | **forma** da barba | `barba` |
| `6` (`Max` 6) | cor da barba | `barba` |

```sh
objdump -d -M intel --start-address=0x4082f9 --stop-address=0x408440 \
        we-team-editor/we-team-editor.exe | grep -E '0x424a[89]|0x40(6fe0|7110|7338)'
```

```
4082f9:  mov  edx,0x424a89          ; "2"  tom de pele
40832a:  call 0x406fe0              ;      -> careto_base
40832f:  call 0x407110              ;      -> pelo
408334:  call 0x407338              ;      -> barba
40833f:  mov  edx,0x424a8b          ; "3"  forma do cabelo
40835e:  mov  edx,0x424a8d          ; "4"  cor do cabelo
4083b6:  call 0x407110              ;      -> pelo
4083c1:  mov  edx,0x424a8f          ; "5"  forma da barba
4083e0:  mov  edx,0x424a91          ; "6"  cor da barba
408438:  call 0x407338              ;      -> barba
```

Alvos na tela, no formulário `jugador`: `imagen_base` (185 × 225, campo `+0x45c`),
`imagen_pelo` (144 × 156, `+0x464`), `imagen_barba` (59 × 58, `+0x468`) — as três
dimensões cercam as dos bitmaps (182 × 224, 140 × 150, 57 × 50).

**`careto_base.bmp` é único porque só a paleta muda.** Não há `careto_<n>`: o
rosto é um só, e o tom de pele é uma troca de 16 entradas de paleta.

### 5.1 O campo de `Player` por trás de cada `flechasapa`

Os cinco controles não inventam nada: são a face visível de cinco campos que o
`we2002_core` **já decodifica** dos 12 bytes de atributo do jogador
([`Player.cpp`](../../src/core/Player.cpp), `Player::Decode`).

```sh
grep -n 'skin_colour\|hair_style\|hair_colour\|beard_style\|beard_colour' \
     src/core/Player.cpp
```

| Campo de `Player` | Extração do disco | Faixa no disco | `flechasapa` | `Max` | Família |
|---|---|--:|--:|--:|---|
| `skin_colour` | `raw[4] & 0x03` | 0..3 | 2 | 3 | paleta de `careto_base` (4 tons) |
| `hair_style` | `(raw[0]>>4)&0x0f` + `(raw[1]<<4)&0x10` | 0..31 | 3 | 31 | **`pelo_0..31`** — 32 arquivos |
| `hair_colour` | `(raw[1]>>1)&0x07` | 0..7 | 4 | 7 | paleta de cabelo (8 cores) |
| `beard_style` | `(raw[1]>>5)&0x07` | 0..7 | 5 | 6 | **`barba_0..6`** — 7 arquivos |
| `beard_colour` | `(raw[2]>>1)&0x07` | 0..7 | 6 | 6 | paleta de barba |

`hair_style` fecha exato: 5 bits, 32 valores, 32 arquivos.

**`beard_style` e `beard_colour` não fecham, e isso é uma armadilha.** O disco
guarda 3 bits (0..7), o `Max` do controle é 6, e só existem `barba_0..6`. O valor
**7 é representável no disco e não tem arquivo**. O original não quebra por
acidente de plataforma: `TUpDown::Position` satura em `Max`, então um 7 vindo do
disco vira 6 na tela — e, gravando de volta, **vira 6 no disco também**. A
WTE-TASK-32 precisa saturar do mesmo jeito, ou tratar o 7 explicitamente e
registrar a divergência.

---

## 6. O achado que muda o porte: **o app grava dentro dos `.bmp`**

Os seis renderizadores fazem, nesta ordem: `fopen(caminho, "r+b")` →
`fseek` → escrever paleta → `fclose` → `TPicture::LoadFromFile(caminho)`.
O modo é literalmente `"r+b"` (`0x004247f8` para bandeira/uniforme,
`0x004249cd` para cabelo/barba), e a escrita é `fwrite`/`fputc` no próprio
arquivo de asset.

| Renderizador | Seek | O que grava |
|---|--:|---|
| `sub_405270`, `sub_405468` (bandeira) | `0x36` | 16 entradas, uma a uma: `fputc` B, G, R + `fseek(+1)` sobre o byte reservado; cores convertidas de BGR555 por `sub_404dd4` a partir de `0x00432ef4` |
| `sub_4056c8` (camisa e calção) | `0x36` | idem, 16 entradas, por arquivo |
| `sub_406fe0` (`careto_base`) | `0x5e` | 0x40 bytes (16 entradas, a partir da 10) da tabela de pele `0x00423998`, passo 64, 4 tons |
| `sub_407110` (`pelo_`) | `0x5e` | os mesmos 0x40 de pele, e em seguida 0x14 bytes (5 entradas) da tabela de cabelo `0x00423a98`, passo 20, 8 cores |
| `sub_407338` (`barba_`) | `0x5e` | os mesmos 0x40 de pele, e 0x0c bytes (3 entradas) da tabela de barba `0x00423b38`, passo 12 |

`0x36` = 54 = primeira entrada da paleta. `0x5e` = 54 + 10 × 4 = entrada 10.

```sh
objdump -d -M intel --start-address=0x40703a --stop-address=0x407098 \
        we-team-editor/we-team-editor.exe        # careto
objdump -d -M intel --start-address=0x40724c --stop-address=0x4072c8 \
        we-team-editor/we-team-editor.exe        # pelo: pele + cabelo
```

### 6.1 A prova está no `mtime` dos arquivos do usuário

Isto não precisou de teste destrutivo — a pasta já carrega a marca:

```sh
ls -l --time-style=full-iso $(find we-team-editor -iname '*.bmp' -newermt 2007-01-01)
find we-team-editor -iname '*.bmp' | wc -l                    # 198
find we-team-editor -iname '*.bmp' -newermt 2007-01-01 | wc -l  #   3
find we-team-editor -iname '*.bmp' -printf '%TY\n' | sort | uniq -c   # a quebra por ano
```

```
1398 2026-08-05 12:44:59.519131420 -0300  image/banderas/bandera37.bmp
2758 2026-08-05 12:44:59.524879987 -0300  image/uniformes2d/camiseta2.bmp
1958 2026-08-05 12:44:59.528184150 -0300  image/uniformes2d/pantalon0.bmp
```

```
    176 2002
     19 2006
      3 2026
```

Os outros 195 não foram tocados, e a maioria é **mais velha** que o pacote de
2006: 176 carregam `mtime` de **2002**, o ano do próprio lançamento do editor, e
19 são de 2006. Estes três foram
reescritos **no mesmo segundo** — a sessão de `make wte` de 2026-08-05, a
primeira vez que o editor rodou nesta máquina —, e o **tamanho não mudou**: 1398,
2758 e 1958 são exatamente os do §1.1. Reescrita in-place de paleta, como o
código diz.

O trio também é coerente com um único time selecionado: `camiseta2` + `pantalon0`
é o uniforme *Primeiro* do time 1 (Scotland) na tabela da §4.1. A bandeira, não:
`table[1] = 2`, e o arquivo tocado foi o **37**. É o esperado, e vale como aviso
para a WTE-TASK-32 — **a forma da bandeira em vigor é o byte da imagem de CD, não
a entrada da tabela**; a tabela só alimenta o combo (§3.3).

### 6.2 Consequências

Três, todas para quem for escrever o lado Lazarus:

1. **A pasta de assets tem de ser gravável.** O `make -C wte assets` cria symlink
   para `we-team-editor/`, do usuário — rodar o porte com esta mecânica mexeria
   nos arquivos do Obocaman.
2. **As paletas em disco hoje não são "originais"**: guardam o último estado que
   alguma execução deixou. Só os *pixels* (índices de paleta) são o ativo; a
   paleta é rascunho.
3. **Duas instâncias não podem desenhar ao mesmo tempo.** Não há bloqueio.

> **Divergência recomendada para a WTE-TASK-32:** recolorir **em memória**
> (`TBitmap` + `Palette`/`ScanLine`), lendo o `.bmp` uma vez. Vira item do §7.3
> do plano — o registro de divergência deliberada. O motivo não é gosto: o
> original só grava no arquivo porque a VCL de 2002 carregava paleta por
> `LoadFromFile`, e reproduzir isso torna o porte read-write numa pasta de dados.

---

## 7. `TImage` do DFM: 41 dos 45 já trazem bitmap embutido

```sh
python3 - <<'PY'
import re, glob, os
tot = emb = 0
for p in sorted(glob.glob("wte/re/dfm/*.dfm")):
    txt = open(p, encoding="latin-1").read().splitlines()
    objs = [(i, m.group(1), m.group(2))
            for i, l in enumerate(txt)
            if (m := re.match(r"\s*object (\w+): (\w+)", l))]
    n = d = 0
    for k, (i, name, cls) in enumerate(objs):
        if cls != "TImage":
            continue
        end = objs[k+1][0] if k+1 < len(objs) else len(txt)
        body = "\n".join(txt[i:end])
        n += 1
        if "Picture.Data" in body: d += 1
        else: print("   sem blob:", os.path.basename(p), name)
    if n: print(f"{os.path.basename(p):22s} TImage={n:3d}  com Picture.Data={d:3d}")
    tot += n; emb += d
print(f"{'TOTAL':22s} TImage={tot:3d}  com Picture.Data={emb:3d}")
PY
```

```
   sem blob: MainForm.dfm bandera
   sem blob: MainForm.dfm banderita1
   sem blob: MainForm.dfm banderita2
MainForm.dfm           TImage= 14  com Picture.Data= 11
   sem blob: estrategia.dfm bandera
estrategia.dfm         TImage=  5  com Picture.Data=  4
ficha_about.dfm        TImage=  2  com Picture.Data=  2
ficha_color.dfm        TImage=  4  com Picture.Data=  4
jugador.dfm            TImage= 20  com Picture.Data= 20
TOTAL                  TImage= 45  com Picture.Data= 41
```

**41 de 45 carregam bitmap embutido**; os 4 vazios são exatamente as quatro
bandeiras, que só existem em runtime.

**Isso não reduz o trabalho de assets, e o motivo importa.** "Embutido" aqui não
quer dizer "não vem de arquivo": `home1`, `home2`, `imagen_base`, `imagen_pelo` e
`imagen_barba` **têm** blob de design e mesmo assim são sobrescritos a cada
`LoadFromFile`. O blob é placeholder de IDE. A conta útil é a outra:

| Papel | Quantos | Quais | Com blob |
|---|--:|---|--:|
| Recebem `LoadFromFile` de `image/` | 7 | `MainForm.bandera`, `MainForm.banderita2`, `MainForm.home1`, `MainForm.home2`, `jugador.imagen_base`, `jugador.imagen_pelo`, `jugador.imagen_barba` | 5 |
| Recebem só `TPicture::Assign` | 2 | `MainForm.banderita1`, `estrategia.bandera` | 0 |
| Cromo estático do DFM | 36 | botões, campo tático, barras de atributo, logotipos | 36 |
| **total** | **45** | | **41** |

Os sete alvos são exatamente os sete sítios de `LoadFromFile` (`0x00422594`):

```sh
objdump -d -M intel we-team-editor/we-team-editor.exe \
  | grep -E 'call +0x422594'           # 405441 4056a1 4058d9 405aac 4070d9 407304 407534
```

Os 36 do cromo saem dos blobs que o `dfm_extract.py` já grava em
`wte/re/dfm/blobs/` (diretório gitignored; renasce com
`python3 wte/tools/dfm_extract.py`) e não tocam em `image/`. **Nenhum dos 198
arquivos de `image/` é dispensável** — cada um é alcançável por uma das três
tabelas.

---

## 8. `data/dat.bin`: memory card de 128 KiB **mais** um patch de 7 setores

```sh
ls -l we-team-editor/data/dat.bin            # 145408
xxd -l 16 we-team-editor/data/dat.bin        # 4d43 ... = "MC"
python3 -c "print(145408 - 0x20000, (145408 - 0x20000) // 2048)"   # 14336 7
```

Duas metades, com dois consumidores distintos:

### 8.1 `[0x00000 .. 0x1FFFF]` — 131.072 B: molde de memory card PSX

`0x20000` = 131.072 = o tamanho exato de um memory card. `MainForm.grabar_memoryClick`
(`0x0040f69c`) copia esse bloco inteiro para o arquivo que o usuário escolher e
só depois grava os dados do jogador por cima:

```
40f7d3:  call 0x417530              ; fopen(<arquivo do usuario>)
40f7eb:  call 0x417810              ; fseek(dat.bin, 0, SEEK_SET)
40f81a:  call 0x417770              ; fread (buf, 0x20000, 1, dat.bin)
40f837:  call 0x417910              ; fwrite(buf, 0x20000, 1, saida)
40f83f:  call 0x40f150              ; grava o save por cima
```

```sh
objdump -d -M intel --start-address=0x40f7a0 --stop-address=0x40f850 \
        we-team-editor/we-team-editor.exe \
  | grep -E '0x41(7530|7810|7770|7910|7170)|0x40f150'
```

**Veredito:** não é memory card "de exemplo" nem banco de dados do editor — é o
**esqueleto** de um cartão formatado com o slot do WE2002 pronto, para que o
editor possa emitir um `.mcr` do zero. O `MC` do byte 0 é o cabeçalho real do
cartão, e é dele que vem.

### 8.2 `[0x20000 .. 0x237FF]` — 14.336 B: os 7 setores que o editor **injeta na imagem**

Os 14.336 bytes que a task pedia para explicar são 7 × 2048 — sete setores de
usuário MODE2/2352 —, e são gravados **dentro da imagem de CD** quando ela é
aberta:

```
40c0f0:  push 0x2e14                ; setor 5, byte 12 dos dados
40c10b:  call 0x418f70              ; fgetc(imagem)
40c111:  cmp  eax,0xfc              ; ja injetado? entao pula
40c11e:  push 0x20000               ; fseek(dat.bin, 0x20000, SEEK_SET)
40c139:  push 0x2e08                ; fseek(imagem, 0x2e08, SEEK_SET)
40c15d:  call 0x417770              ; fread (buf, 0x800, 1, dat.bin)
40c17a:  call 0x417910              ; fwrite(buf, 0x800, 1, imagem)
40c18a:  push 0x130                 ; fseek(imagem, +304, SEEK_CUR)
40c199:  cmp  edi,0x7               ; 7 setores
```

```sh
objdump -d -M intel --start-address=0x40c0ee --stop-address=0x40c1a0 \
        we-team-editor/we-team-editor.exe \
  | grep -E '0x2e(08|14)|0xfc|0x20000|0x130|edi,0x7'
```

`0x2e08` = 11784 = 5 × 2352 + 24 — o primeiro byte de dados do **setor 5**. O
passo `0x130` = 304 = 2352 − 2048 é o salto sobre EDC/ECC e o cabeçalho do setor
seguinte: a mesma aritmética sector-aware que o
[CLAUDE.md](../../CLAUDE.md) descreve para o `newWe2002`. O byte-sentinela em
`0x2e14` valendo `0xfc` significa "já injetado", e o bloco é pulado.

O mesmo trecho aparece duas vezes, em `MainForm.boton_dialogo_weClick`
(`0x0040bd60`) e em `MainForm.FormShow` (`0x004111d8`) — abrir a imagem pelo
diálogo ou já na carga passa pelo mesmo caminho.

### 8.3 E `dat.bin` é pré-condição de arranque

`MainForm.FormShow` monta `*0x432e80 + "\dat.bin"`, tenta `fopen`, e se falhar
mostra `The file "dat.bin" must be in the "data" directory` (`0x004250bd`) e
encerra. O `FILE*` fica num global (`0x00432e68`) aberto pela sessão inteira.

> **Para a WTE-TASK-31.** A hipótese do enunciado — "`MC` liga isto ao import de
> `.mcr`" — está **meio certa**. A primeira metade é mesmo o molde de cartão, e é
> insumo da 31, mas do lado da **exportação** (`grabar_memoryClick`), não da
> importação. A importação (`boton_mcrClick`, `0x0040c2c8`) lê o `.mcr` do
> usuário e não toca em `dat.bin`. A segunda metade não tem nada a ver com
> memory card: é payload de patch da imagem de CD, e é insumo de quem for
> reimplementar a abertura de imagem.

---

## 9. Quem consome cada achado

| Achado | Task |
|---|---|
| `bandera<n>.bmp` é estêncil; índice = byte lido da imagem; tabela padrão em `0x004231e8`; combo indexa a tabela | **32** (camisa e bandeira 2D) |
| `camiseta`/`pantalon`: tabela `0x004232a6`, 95 × 4, dois jogos por time; corte 0..49 / 50..98 | **32** |
| `pelo`/`barba`/`careto_base`: índice = `Player::hair_style` / `beard_style`; cor por `skin_colour`, `hair_colour`, `beard_colour` | **32** (e a Fase 4, pelos handlers de `jugador`) |
| `beard_style` cabe 0..7 no disco mas só há `barba_0..6`; o original satura em 6 | **32** |
| Tabelas de paleta `0x00423998` (pele), `0x00423a98` (cabelo), `0x00423b38` (barba) | **32** |
| O app grava paleta **dentro** do `.bmp` — divergência recomendada: recolorir em memória | **32**, registro em §7.3 |
| `dat.bin[0 .. 0x1FFFF]` = molde de memory card, copiado por `grabar_memoryClick` | **31** (`.mcr`) |
| `dat.bin[0x20000 ..]` = 7 setores injetados na imagem em `0x2e08`, sentinela `0xfc` em `0x2e14` | **31** e quem fizer a abertura de imagem |
| Resolução de caminho por `GetCurrentDir()`, seis globais `<cwd>\...` | **39** (empacotamento) |
| Assets precisam ser graváveis (ou o porte diverge) | **39** |
| 198 bitmaps, todos alcançáveis; nenhum dispensável | **39** |
| 198 × 197: erro de soma na prosa da §1.8 | **09** (reconciliação) |
| Buracos das bandeiras são **oito** (44..51), não sete | **09** |

---

## 10. O que ficou fora, e por quê

- **Nenhum teste destrutivo foi feito.** O método sugerido pela task — renomear
  um `.bmp` numa cópia e ver o que quebra — não foi necessário: o código não tem
  guarda de existência nenhuma entre montar o nome e `fopen`, e o combo não
  consegue pedir índice ausente (§3.3). Renomear provaria o modo de falha, não a
  convenção. Se alguém quiser o modo de falha, é `fopen` devolvendo `NULL`
  seguido de `fseek(NULL, ...)`, e depois `LoadFromFile` levantando
  `EFOpenError`.
- **Nada foi executado sob Wine.** O `:99` está reservado para a WTE-TASK-11.
- **Os nomes de campo `MainForm+0x444/0x48c/0x490` e `jugador+0x45c/0x464/0x468`**
  foram amarrados por **dimensão** (as alturas 42 e 22 de `home1`/`home2` batem
  exatamente com `camiseta`/`pantalon`; `imagen_base`/`imagen_pelo`/`imagen_barba`
  cercam `careto_base`/`pelo`/`barba`) e por **vizinhança de campo**, não pela
  ordem do DFM: a ordem de declaração dos campos publicados do C++Builder **não**
  é a ordem do DFM quando há aninhamento, e tentar calibrar por ela produz
  contradição. Corridas locais de campos consecutivos batem; a numeração global,
  não.
