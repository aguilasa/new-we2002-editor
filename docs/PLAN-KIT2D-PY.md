# Plano — visualizador e editor do uniforme 2D, em Python + Qt

Proposta de 2026-10-01. **Nenhuma fase foi executada**; o que está marcado como
medido foi medido ao escrever este plano, com o comando ou o snippet ao lado
(§1.2 e §7 do [SUPERPACK-UNIFORMES-2D.md](/docs/SUPERPACK-UNIFORMES-2D.md)).

Segue as premissas do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md): núcleo e
interface separados por uma fachada só, núcleo Python puro sem Qt, CLI como
segundo cliente, janela mínima em Fusion, venv compartilhado, gates no `ctest`
com *skip* 77, e nada do Superpack no git. Onde este plano repete uma regra de
lá, é de propósito — os dois projetos vão ser absorvidos pela mesma aplicação.

## 0. Escopo

### Objetivo

Uma ferramenta que abre a imagem de CD do WE2002 e, para cada um dos 95 times,
**mostra o uniforme 2D como o jogo o desenha** — a camisinha com calção e meião
da tela de opções de partida e da seleção de time, titular e suplente lado a
lado como na tela de seleção — e **edita o que a comunidade edita**:

- as **16 cores** de cada uniforme (`SELECT2.BIN` +172096, `OFS_KIT_PREVIEW`);
- o **modelo** do uniforme, trocando o ponteiro do time por um dos **190**
  que o disco já tem (`SELECT2.BIN` +225808) — o fluxo do polipoli e do
  `EditorUniformesWE2002.exe`;
- a **cor do pontinho do radar** (`SELECT.BIN` +0x3F534 titular, +0x3F634
  suplente), com a regra de pareamento do SimoSapo como aviso.

As edições ficam em memória até **Aplicar**, que grava **in-place numa cópia** da
imagem; **Cancelar** descarta; trocar de time ou fechar com edição pendente
pergunta antes. O render do uniforme é fiel ao jogo; o resto da janela é Qt
comum.

### Não-objetivos

- **Não edita os gráficos do `DATSEL.BIN`** (as imagens 22/23/24 que o polipoli
  redesenha). Fica para uma v2, e o motivo é de risco, não de vontade: reinjetar
  exige comprimir com o nosso LZSS, que sai 0,2–2 % maior que o da Konami
  (`tools/pes2/lzss.py`), num esquema fit-or-fail (`asset_write.py`); e o §4.3
  do [SUPERPACK-UNIFORMES.md](/docs/SUPERPACK-UNIFORMES.md) mede que o
  Wecompressor, que faz isso para TEX, quebra no console. Decisão do usuário em
  2026-10-01.
- **Não abre arquivo avulso.** A origem é sempre a imagem de CD: o desenho
  precisa do `DATSEL.BIN`, da composição do `SELECT2.BIN` e da paleta, e os três
  só existem juntos no disco. `.m2002` do port e `.ADD` do FratelConiglio são
  formatos de paleta e entram, se entrarem, como importar/exportar numa v2.
  Decisão do usuário em 2026-10-01.
- **Não edita a bandeira.** O `FlagKitDialog` do port já faz; a bandeira ao lado
  do uniforme, como na tela de opções, é v2.
- **Não é a tela do jogo.** Desenha o uniforme, não o fundo azul, os textos nem
  a moldura; o `looks` é quem imita tela.
- **Não recalcula EDC/ECC** ao gravar — regra do port, herdada do `ed.exe`.
- **Não é uma interface elaborada.** Vai ser absorvida por uma aplicação única;
  o que precisa durar é o núcleo.

### Definição de pronto

1. A janela abre uma ROM, o combobox lista os 95 times por nome (regra do §3.3
   do `kits`: inglês por tabela se o disco é o japonês, o nome da ROM nos
   outros), e **qualquer** time mostra titular e suplente sem índice fora da
   paleta e sem sprite fora da imagem.
2. O render **bate com o quadro do emulador** (§5.1) num time em que titular e
   suplente diferem, e um controle com outro time ou outro modelo diverge.
3. Editar as 16 cores, o modelo e o radar fica em memória; **Aplicar** grava os
   bytes certos — 32, 4 e 2 por uniforme, nos offsets da §1.1 — e nada mais;
   **Cancelar** descarta; sujo é guardado ao trocar de time e ao fechar.
4. A mesma edição de paleta feita nesta ferramenta e pelo `Database::Save` do
   port dá **imagens byte-idênticas** (§5.2).
5. A CLI faz tudo o que a janela faz sem importar nada além de `core/api.py`, e
   a janela sai igual no Windows e no Linux.

## 1. O que já se sabe

### 1.1 Os três dados, e o radar — medidos

Tudo no [SUPERPACK-UNIFORMES-2D.md](/docs/SUPERPACK-UNIFORMES-2D.md), com snippet
e saída colada no §7 de lá. O resumo que este plano usa:

| dado | arquivo | onde | forma |
|---|---|---|---|
| paleta | `/SELECT2.BIN` (LBA 1050) | +172096 + 64 × time; suplente a +32 | 16 × BGR555; palavra 0 = `0000` e palavra 1 = `4208` nos 190 jogos dos discos originais |
| modelo | `/SELECT2.BIN` | +225808, 760 bytes = 95 × (titular, suplente) | ponteiro de RAM, **190 distintos**, `0x800FB8AC..0x8010000C` |
| gráficos | `/BIN/DATSEL.BIN` (LBA 6000) | streams LZSS 21, 22, 23 (offsets 126536, 129208, 132000) | 128×128 a 4 bpp cada; idênticos nos três discos |
| paleta "7" | `/BIN/DAT2D.BIN` (LBA 5300) | +68484 | a que o polipoli usa para ver os gráficos; **não** é a do jogo |
| radar | `/SELECT.BIN` (LBA 850) | +0x3F534 titular, +0x3F634 suplente, 2 bytes × time | 8 cores válidas (SimoSapo) |

Os LBAs e tamanhos são os mesmos nos três discos de `roms/`. A ordem dos 95 é a
do `TEAM_NAMES[120]` de `src/core/Tables.cpp` (Ireland, Scotland, Wales,
England…), que é o índice do `ed.exe`: 1..63 seleções (`teams[id-1]`), 64..95
clubes de ML (`ml_teams[id-64]`, `src/app/Commands.cpp:65`).

### 1.2 A composição: listas de sprites de 10 bytes — medido em parte

É o que o SUPERPACK-UNIFORMES-2D deixou aberto e este plano começou a medir.
Snippet, da raiz do repositório, sobre o disco japonês:

```sh
python3 - <<'PY'
import struct, collections

LBA_SELECT2, SIZE_SELECT2 = 1050, 271540       # iso.py ls
TABELA_MODELOS = 225808                        # SUPERPACK-UNIFORMES-2D §2.2
CORRIDA = 198372                               # a corrida de ponteiros logo antes dos registros


def read_file(img, lba, size):
    out = bytearray()
    with open(img, "rb") as f:
        while len(out) < size:
            f.seek(lba * 2352 + 24)
            out += f.read(2048)
            lba += 1
    return bytes(out[:size])


s2 = read_file("roms/japanese-shift-jis.bin", LBA_SELECT2, SIZE_SELECT2)
u32 = lambda o: struct.unpack_from("<I", s2, o)[0]

i = CORRIDA
while u32(i - 4) >> 16 == 0x800F:
    i -= 4
j = CORRIDA
while u32(j) >> 16 in (0x800F, 0x8010):
    j += 4
run = [u32(k) for k in range(i, j, 4)]
base = run[0] - j                              # o 1o alvo e o byte seguinte a corrida
print(f"corrida de ponteiros: {i}..{j}, {len(run)} ponteiros, {run[0]:08X}..{run[-1]:08X}")
print(f"base inferida: {base:08X}  tabela em RAM: {base + TABELA_MODELOS:08X}  fim do overlay: {base + SIZE_SELECT2:08X}")

table = [u32(TABELA_MODELOS + k) for k in range(0, 760, 4)]
offs = sorted({p - base for p in table})
print(f"alvos dos 190 ponteiros no arquivo: {offs[0]}..{offs[-1]} (tabela em {TABELA_MODELOS})")
after = {a: b for a, b in zip(offs, offs[1:])}


def records(off, limit):
    out = []
    for o in range(off, limit, 10):
        x, y, attr, w, h, u, v = struct.unpack_from("<hhHBBBB", s2, o)
        out.append((x, y, attr, w, h, u, v))
    return out


for name, k in (("IRL titular", 0), ("IRL suplente", 1), ("ING titular", 6)):
    off = table[k] - base
    end = after.get(off, off + 60)
    print(f"{name}: {table[k]:08X} -> {off}, {end - off} bytes ate o proximo ponteiro")
    for r in records(off, min(end, off + 80)):
        print("    x=%4d y=%4d attr=%04X w=%3d h=%3d u=%3d v=%3d" % r)


def list_until_ff(off):
    """Records up to and including the first whose attr low byte is 0xFF."""
    out = []
    for r in records(off, off + 10 * 64):
        out.append(r)
        if r[2] & 0xFF == 0xFF:
            break
    return out


wh, lo, hi, lens = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
closed = covered = 0
for off in offs:
    lst = list_until_ff(off)
    lens[len(lst)] += 1
    if lst[-1][2] & 0xFF == 0xFF:
        closed += 1
    nxt = after.get(off)
    if nxt is not None and off + 10 * len(lst) == nxt:
        covered += 1
    limit = (nxt - off) // 10 if nxt is not None else len(lst)
    for r in lst[:limit]:                      # only what lies before the next pointer
        wh[(r[3], r[4])] += 1
        lo[r[2] & 0xFF] += 1
        hi[r[2] >> 8] += 1
print(f"listas cortadas no primeiro FF: {closed} de {len(offs)} fecham em ate 64 registros; {covered} de {len(offs) - 1} acabam exatamente no ponteiro seguinte")
print("registros ate o FF, por lista:", sorted(lens.items()))
print("so os registros antes do ponteiro seguinte --")
print("  (w,h) mais comuns:", wh.most_common(8))
print("  byte baixo de attr:", sorted(lo.items())[:6], "...", " byte alto distinto:", len(hi), "faixa %02X..%02X" % (min(hi), max(hi)))
PY
```

```
corrida de ponteiros: 198372..198788, 104 ponteiros, 800FB1B4..800FB678
base inferida: 800CA930  tabela em RAM: 80101B40  fim do overlay: 8010CDE4
alvos dos 190 ponteiros no arquivo: 200572..218844 (tabela em 225808)
IRL titular: 800FB8AC -> 200572, 80 bytes ate o proximo ponteiro
    x= -37 y=  62 attr=1800 w= 40 h= 32 u= 80 v=  0
    x= -49 y=  65 attr=1800 w= 24 h=  8 u=  0 v=112
    x= -41 y=  97 attr=1800 w= 24 h= 24 u=152 v=  0
    x= -41 y= 104 attr=18FF w= 16 h= 24 u=  0 v=128
    x= -55 y=  79 attr=1900 w= 16 h= 24 u= 16 v=128
    x= -18 y=  79 attr=1900 w= 16 h= 16 u=192 v= 32
    x= -37 y=  62 attr=1900 w=  8 h=  8 u=144 v= 48
    x= -50 y=  82 attr=1900 w=  8 h=  8 u=152 v= 48
IRL suplente: 800FB8FC -> 200652, 180 bytes ate o proximo ponteiro
    x= -15 y=  82 attr=1900 w= 40 h= 32 u= 80 v=  0
    x= -49 y=  65 attr=1900 w= 24 h=  8 u=  0 v=112
    x= -41 y=  97 attr=1900 w= 24 h= 24 u=128 v= 24
    x= -41 y= 104 attr=19FF w= 16 h= 24 u=128 v= 80
    x= -55 y=  79 attr=1A00 w= 16 h= 24 u=144 v= 80
    x= -18 y=  79 attr=1A00 w= 16 h= 16 u=176 v= 48
    x= -37 y=  62 attr=1A00 w=  8 h=  8 u=136 v= 48
    x= -21 y=  71 attr=1A00 w=  8 h=  8 u=128 v= 48
ING titular: 800FBAA0 -> 201072, 60 bytes ate o proximo ponteiro
    x= -55 y=  79 attr=1F00 w= 16 h= 24 u=208 v= 80
    x= -18 y=  79 attr=1F00 w= 16 h= 16 u= 80 v= 64
    x= -37 y=  62 attr=1F00 w= 40 h= 32 u= 80 v=  0
    x= -49 y=  65 attr=1F00 w= 24 h=  8 u=  0 v=112
    x= -41 y=  97 attr=1F00 w= 24 h= 24 u=128 v=  0
    x= -41 y= 104 attr=1FFF w= 16 h= 24 u=  0 v=128
listas cortadas no primeiro FF: 137 de 190 fecham em ate 64 registros; 18 de 189 acabam exatamente no ponteiro seguinte
registros ate o FF, por lista: [(1, 1), (2, 22), (3, 1), (4, 32), (6, 32), (7, 1), (8, 15), (9, 1), (10, 4), (12, 4), (13, 1), (14, 4), (15, 1), (16, 7), (18, 4), (20, 2), (22, 2), (24, 1), (26, 1), (28, 1), (64, 53)]
so os registros antes do ponteiro seguinte --
  (w,h) mais comuns: [((8, 8), 335), ((16, 24), 127), ((24, 24), 98), ((40, 32), 88), ((24, 8), 88), ((79, 0), 53), ((97, 0), 29), ((16, 16), 28)]
  byte baixo de attr: [(0, 694), (24, 3), (32, 2), (40, 2), (48, 1), (62, 16)] ...  byte alto distinto: 100 faixa 00..FF
```

O que isso diz, e o que não diz:

- **Cada ponteiro de modelo cai numa lista de registros de 10 bytes**
  `x:int16 y:int16 attr:u16 w:u8 h:u8 u:u8 v:u8`, todas na faixa
  200572..218844 do arquivo, logo antes da tabela. Os tamanhos são os das peças
  do uniforme — **40×32 é a camisa**, o tamanho exato dos `Camiseta/0N.bmp` do
  polipoli; 24×8 (gola), 24×24 (calção), 16×24 (meião ou sombra), 8×8 e 16×16
  (detalhes) —, e `u,v` ficam em 0..255 × 0..184, o que cabe nas três imagens
  de 128×128 postas lado a lado na VRAM.
- **A base de carga `0x800CA930` é inferida, não medida.** Veio de uma corrida
  de 104 ponteiros em 198372..198788 cujo primeiro alvo cai no byte seguinte à
  corrida; com ela as listas alinham em registros de 10 bytes e a camisa de
  40×32 aparece onde devia. A referência `lui/addiu` à tabela em `0x80101B40`
  **não foi achada** no código do overlay (a única coincidência de `lo16` era
  um `jal`). Base errada em ±10 desalinha tudo com todo número "na faixa" — é o
  erro da [CORR-LOOKS-062](/docs/tasks/concluidos/looks/CORR-LOOKS-062.md) de
  novo, e por isso a §4.1 mede no emulador antes de qualquer render.
- **`attr` é little-endian: `00 18` lê-se `0x1800`.** O byte alto cresce com o
  time (`0x18`, `0x19` para Irlanda; `0x1F`, `0x20` para Inglaterra) e tem cara
  de **índice de CLUT**; o byte baixo é `00` em 694 registros e `FF` no quarto
  de cada lista — a camisa, a gola, o calção e o meião, e **depois** vêm os
  detalhes com o id seguinte. Então `FF` **não** é terminador de lista (137 de
  190 "fecham" antes de 64 registros e só 18 acabam no ponteiro seguinte), e
  "até o próximo ponteiro" também não é a regra (a lista de Inglaterra tem 6
  registros em 60 bytes; a de Irlanda, 8 em 80, com dois ids). O que delimita
  uma lista, e o que `FF` marca — talvez "peça base" contra "detalhe por cima",
  a ordem do polipoli —, é a §4.2.
- **`x,y` são relativos a uma âncora**, negativos; a camisa titular da Irlanda
  está em x = −37 e a suplente em x = −15, o que lembra os dois uniformes lado
  a lado da tela de seleção — mas isso é leitura, não medição.

### 1.3 O que o repositório empresta

| de onde | o quê | para quê |
|---|---|---|
| `tools/pes2/iso.py` | `Image`, leitura por LBA, `write_file` in-place que recusa mudar tamanho | ler os quatro arquivos; gravar a cópia |
| `tools/pes2/lzss.py` | `decompress`, `scan` | os streams 21/22/23 do `DATSEL.BIN` |
| `tools/pes2/asset_write.py` | `refuse_roms` | nunca gravar em `roms/` |
| `tools/kits/core/source.py` | reconhecer ROM pelo conteúdo (imagem, `.cue`) | a origem do §3.2 |
| `tools/kits/` (KITS-TASK-12/13, pendentes) | o gerador de `TEAM_NAMES`/`OFS_TEAM_NAME_*` com `--check` e `teams.py` | os nomes do §3.3 |
| `tools/kits/controls.py`, `selftest.py` | o padrão de controle negativo plantado e o `harness` do `looks` | os gates do §5 |
| `tools/pes2/mcp.py`, `fork.py`, `tools/looks/oracle.py` | subir o fork, apertar botão, `read_memory`, `read_vram_region`, `take_screenshot`, `save_state`/`load_state` | a fase 0 e os confrontos |
| `src/core/include/we2002/Offsets.hpp`, `src/app/FlagKitDialog.*` | `OFS_KIT_PREVIEW*`; o que o `ed.exe` expõe (palavras 2..15) | os offsets; a divergência deliberada da §6 |
| `tests/golden_tool.cpp`, `tools/par/8.8-*.sh` | o `Database::Save` headless; o roteiro do diálogo de uniforme no `ed.exe` (Linux) | o confronto de gravação (§5.2) |

O que **não** existe e o plano precisa: uma rota de botões ou um save state do
WE2002 **na tela de opções de partida** (o `looks` gravou os seus à mão; o
`mcr` mediu a tela em
[MCR-OPCOES-PARTIDA.md](/docs/MCR-OPCOES-PARTIDA.md) sem registrar a rota); e
`savestate.py` exige `zstd` no `PATH`, ausente nesta máquina — RAM se lê pelo
MCP com o jogo de pé.

## 2. A decisão: projeto novo em `tools/kit2d/`, por import

**Recomendação, confirmada pelo usuário em 2026-10-01: `tools/kit2d/`, projeto
próprio com ciclo Rite `kit2d`, que importa de `tools/pes2/`, `tools/kits/` e
`tools/looks/` sem copiar.**

Por que não dentro do `kits`: o `kits` **só lê**, por decisão de §0 de lá, e é
um ciclo vivo; um editor que grava três coisas na imagem é outra regra e outra
guarda, e crescer o ciclo vivo com escrita mistura o que ele mede. Por que não
copiar: `iso.py`, `lzss.py` e `refuse_roms` custaram tasks e estão confrontados;
a guarda de origem do `kits` idem. O preço é o do `kits` §6: acoplamento. O
`kit2d_selftest` roda os self-checks do que importa, para a quebra aparecer aqui.

### 2.1 Os discos

Para tudo o que este plano lê, **os três discos de `roms/` são iguais**: mesmos
LBAs e tamanhos dos quatro arquivos, `DATSEL.BIN` idêntico, a tabela de 760
bytes idêntica. O que difere é dado editado na `golden-european-deluxe`
(hackeada): a palavra 1 das paletas sai de `4208` em alguns times, e o radar
começa `007C 2104` em vez de `E003 007C`. **É diagnóstico, não recusa**: a aba
da §3.4 mostra "palavra 1 fora do original" e "radar fora das 8 cores", e a
ferramenta desenha e grava igual. A guarda de digest do `looks` não se aplica —
o motivo de abrir uma ROM aqui é editá-la.

## 3. Arquitetura

**A regra que manda em todo o resto: núcleo e interface separados por um
contrato só** (`kits` §3). O núcleo é o que sobrevive à aplicação única; a
janela é descartável.

### 3.1 O núcleo (`tools/kit2d/core/`)

Python puro, **sem Qt**, sem `print`, sem `sys.exit`, sem estado global;
devolve `dataclass`, `bytes` RGBA e listas; erra com exceções tipadas cuja
mensagem já é a frase da interface. A fachada é `core/api.py`, e UI e CLI só
importam ela:

```python
source = api.open_source(path)          # ROM pelo conteúdo (.bin/.iso/.cue); kind == "rom"
source.teams()                          # [TeamEntry(index, name, name_origin)], 95, ordem do jogo
source.models()                         # [Model(pointer, sprites, teams_using)], os 190 distintos
kit = source.kit(team, kit_set)         # Kit2D(team, kit_set, palette[16], model, radar, problems)
api.render(kit, scale=1)                # Picture(width, height, rgba): o uniforme composto
api.render_model(model, palette, scale) # qualquer modelo com qualquer paleta (as miniaturas)
edit = api.Edit(source)                 # o buffer: set_palette / set_model / set_radar, dirty, diff(), revert(team)
api.apply(edit, path)                   # grava in-place na cópia; devolve [Write(offset, before, after)]
api.controls(...)                       # os controles negativos do §5, plantados por comando
```

| módulo | faz |
|---|---|
| `layout.py` | **todo endereço num módulo só**: LBAs, +172096, +225808, +0x3F534, os três streams, a base de carga (até a §4.1 fechar, com a palavra "inferida" ao lado) |
| `source.py` | abre a ROM pelo conteúdo (reusa o reconhecimento do `kits`); lê os quatro arquivos pelo `iso.py`; `refuse_roms` na abertura para escrita |
| `teams.py` | os 95 nomes pela regra do §3.3 |
| `sprites.py` | as listas de registros de 10 bytes e a regra de delimitação medida na §4.2; `Model` |
| `palette.py` | BGR555 ↔ RGB (`v << 3`, teto 248, como o `wte/re/render2d.md` mede); as 8 cores do radar e a regra de pareamento |
| `graphics.py` | os três streams do `DATSEL.BIN` descomprimidos, 4 bpp, nibble baixo primeiro |
| `render.py` | o compositor: para cada sprite, recorta `(u, v, w, h)` da imagem certa, aplica a paleta pelo índice, cola em `(x, y)` relativo à âncora; índice 0 transparente até a §4.3 dizer outra coisa |
| `edit.py` | o buffer de edições por time e uniforme; `diff()` em bytes; `revert` |
| `writer.py` | aplica o `diff()` na cópia pelo `iso.write_file`: tamanhos fixos (32, 4, 2), sem EDC/ECC; recusa qualquer escrita que mude o tamanho |
| `generated/` | as tabelas copiadas do C++ pelo gerador do `kits` (§3.3), nunca à mão |

A **CLI** (`tools/kit2d/cli.py`) é o segundo cliente da fachada: `info`,
`teams`, `models`, `render --team N --set 1|2 --out PNG`, `export` (as três
imagens com a paleta do time), `set-palette`, `set-model`, `set-radar`, `apply`,
`check`, mais as sondas da fase 0 (`sprites`, `base`) promovidas a comando. Se
a CLI precisar de algo além de `api`, a fachada está incompleta.

### 3.2 A origem: só ROM

"Abrir…" aceita `.bin`, `.iso` e `.cue`; o núcleo decide pelo conteúdo. Com a
ROM aberta aparecem o **combobox de times** e o seletor **titular/suplente**.
Para gravar, o caminho passa por `refuse_roms`: `roms/` é original e a
ferramenta pede uma cópia, como `asset_write.py` e `fork.py` fazem. A gravação
é in-place, nos offsets da §1.1, com tamanho fixo e sem recálculo de EDC/ECC —
o mesmo que o port e o `ed.exe` fazem com a paleta.

### 3.3 Os nomes dos times

A **mesma regra e o mesmo gerador do `kits`** (§3.3 de lá): japonês decidido pelo
disco (boot `SLPM_870.56`, digests), tabela inglesa `TEAM_NAMES` de
`src/core/Tables.cpp` via gerador com `--check` no `ctest`, `name_origin`
dizendo de onde veio. As tasks que entregam isso são a **KITS-TASK-12** e a
**KITS-TASK-13**, pendentes em 2026-10-01. Este ciclo **não duplica**: a fase 1
importa `tools/kits/core/generated` e `teams.py` quando existirem; se o `kits`
ainda não os tiver entregue quando a fase 1 começar, a task de nomes daqui
**faz lá** (em `tools/kits/`, com os gates do `kits` verdes antes e depois) e
importa — nunca uma segunda tabela.

### 3.4 A interface (`tools/kit2d/ui/`)

Só apresentação: widgets que chamam a fachada e desenham o que ela devolve.

- **Barra de cima**: Abrir…, o caminho aberto (com "cópia" ou "original" ao
  lado), combobox de times, titular/suplente.
- **Painel central — o uniforme.** Titular e suplente **lado a lado**, como a
  tela de seleção de time; zoom de vizinho mais próximo de 1× a 8×; fundo
  escolhível entre xadrez e o azul da tela do jogo; "Exportar PNG".
- **Painel direito — a edição.**
  - **16 caixas de cor**, as 16 — não as 14 do `ed.exe` —, cada uma com o
    índice, a cor e, medido na §4.3, se o desenho a amostra. Editar a palavra 1
    é divergir do `ed.exe` (§6), e a caixa diz isso.
  - **Seletor de modelo**: a lista dos 190, cada um com miniatura renderizada
    **com a paleta do time corrente** e os times que o usam. É a planilha do
    polipoli com imagem.
  - **Radar**: as 8 cores do SimoSapo como botões, e o aviso da regra de
    pareamento (mesma cor titular em dois times de camisa igual; os quatro
    pares proibidos titular/suplente) — aviso, não recusa.
- **Aplicar / Cancelar / Reverter este time**, `QUndoStack` para desfazer e
  refazer dentro da sessão, e guarda de sujo ao trocar de time e ao fechar.
- **Aba Diagnóstico**: `kit.problems` — palavra 1 fora de `4208`, radar fora
  das 8, sprite fora da imagem, ponteiro fora dos 190, cópia versus original.
- Uma linha fixa de rodapé dizendo que **isto é o uniforme 2D de menu, não o
  3D de campo (TEX)** — a confusão que o capítulo 8 da Bíblia abre.

**Estilo**: Fusion, `QPalette` fixa, fonte em pixels, layouts Qt — o §3.4 do
`kits`, palavra por palavra, pelo mesmo motivo.

### 3.5 Idioma e ambiente

Código e docstrings em inglês, documentos em português. Venv `work/venv-looks/`
(já tem PySide6); o núcleo não precisa dele. `make.ps1 kit2d` / `make kit2d` e
`kit2d-98` abrem a janela, como `looks`. `ctest` ganha:

| alvo | precisa de | pula |
|---|---|---|
| `kit2d_selftest` | nada | nunca |
| `kit2d_image` | `WE2002_KIT2D_IMAGE` (default: `WE2002_LOOKS_IMAGE`) | 77 |
| `kit2d_ui` | venv e tela (`:98` / −32000) | 77 |
| `kit2d_live` | fork, `.cue` de cópia, o state da §4.4; `RESOURCE_LOCK duckstation` | 77 |

E a convenção de sempre: um alvo que pula imprime por quê, e o Log lê a linha,
não o `Passed`.

## 4. As incógnitas, em ordem de risco

### 4.1 (a) A base de carga do overlay e o registro de sprite

`0x800CA930` é inferência (§1.2). A medição: com o jogo na tela de opções
(§4.4), ler a RAM pelo MCP, achar os 760 bytes da tabela (`read_memory` sobre
2 MiB e `bytes.find`), e a diferença entre o endereço achado e 225808 **é** a
base. Com ela, ler as listas da RAM e conferir que são as do arquivo. **Risco
alto**: base errada desenha tudo torto com todo número na faixa. Antes dela,
nenhum render entra em gate.

### 4.2 (b) O que delimita uma lista, e o que é `attr`

`FF` não termina, "até o próximo ponteiro" não delimita (§1.2). Hipóteses a
testar na mesma sessão de emulador: a lista do titular e a do suplente do mesmo
modelo são uma só, com `FF` separando a base dos detalhes; o byte alto de
`attr` é o índice de CLUT, e a paleta de +172096 é enviada à VRAM numa linha
que esse índice escolhe (`read_vram_region` em y ≥ 480 diz qual); `u,v` indexam
as três imagens 22/23/24 lado a lado (confirmar pela VRAM onde cada uma cai).
Fecha com um controle: mexer um `x` na RAM pelo `write_memory` e ver o sprite
andar na tela.

### 4.3 (c) As palavras 0 e 1

Que índices da paleta os sprites amostram de fato; se o índice 0 é
transparência, e se o 1 (`0x0842`, cinza escuro) aparece — contorno? sombra?
Sai do render medido contra a VRAM, por índice.

### 4.4 (d) Chegar à tela de opções de partida

Não há rota nem state para o WE2002. **Pré-requisito humano**: o usuário grava
um save state do fork **na tela de opções de uma partida amistosa**, com um
time em que titular e suplente diferem de cada lado, e o deixa em
`work/kit2d-states/` (`WE2002_KIT2D_STATES`), como os do `looks`. A rota de
botões, se for medida, fica registrada; sem o state as fases 0, 2 e 7 pulam, e
o plano diz que **pular não é passar**.

### 4.5 (e) O modelo é uma lista só?

O polipoli infere cinco campos (camisa, gola, calção, mangas, detalhes). Se
trocar o ponteiro troca a lista inteira, trocar de modelo pode trocar o calção
e a gola junto com a camisa — o que ele observou ("tienen en común la
camiseta, pero los detalles son diferentes"). A ferramenta mostra o que o
ponteiro desenha, e a miniatura já responde isso visualmente; a §4.2 responde
em bytes.

### 4.6 (f) Os clubes de ML

A tabela cobre os 95 e os offsets do polipoli vão até Boca; falta conferir no
emulador um clube (índice ≥ 63) — a tela de seleção de clube (a `tela_03`) é
outra tela, e a composição pode ser outra lista.

## 5. Como se verifica

1. **Render × emulador.** No state da §4.4, `read_vram_region` do retângulo
   onde o uniforme é desenhado (ou `take_screenshot`), contra `api.render` do
   mesmo time: histograma de cor como o `confront.py --score` do `looks`, e
   sobreposição pixel a pixel na caixa do uniforme. Controle: outro time, ou o
   mesmo time com outro modelo, tem de divergir.
2. **Gravação × port.** A mesma edição de paleta — um time, uma palavra, um
   valor — feita por `cli.py set-palette … apply` e pelo `we2002_golden_tool`
   (o `Database::Save` headless) sobre duas cópias dá imagens **byte-idênticas**
   fora a faixa conhecida do slot 64 (`CLAUDE.md`, golden). No Linux, o roteiro
   `tools/par/8.8-*.sh` põe o `ed.exe` como terceiro lado. Modelo e radar não
   têm oráculo no port: ficam com o round-trip e com o emulador (7).
3. **Round-trip.** Abrir e aplicar sem editar devolve a cópia idêntica (o
   `cmd_save` do `asset_write.py`); e aplicar e reabrir devolve a edição.
4. **Controles negativos plantados** por comando (`controls.py` do `kits`): um
   byte trocado numa lista de sprites tem de dar sprite fora da imagem,
   **recusado com o nome do registro**; ponteiro fora dos 190 → recusa; gravar
   em `roms/` → recusa; paleta de 17 palavras → recusa; base de carga deslocada
   de 10 bytes → o confronto 1 reprova; radar fora das 8 → **aviso**, porque o
   disco hackeado tem.
5. **Os gates `kit2d_*`** com *skip* 77, e o Log de cada task mostrando o
   vermelho de cada controle antes do verde.

## 6. Riscos de projeto

- **Base de carga errada** (§4.1): a defesa é a fase 0 inteira antes de
  qualquer render entrar em gate, e o controle "base ± 10" do §5.4.
- **Gravar o que o `ed.exe` não grava.** As palavras 0 e 1 e o ponteiro de
  modelo nunca saem do `ed.exe`; o radar nunca sai do port. É divergência
  deliberada: a ferramenta avisa na palavra 1, e o `PARIDADE-FUNCIONAL.md` não
  é tocado — isto não é paridade, é feature.
- **Acoplamento** a `pes2`, `kits` e `looks`; e a dependência da §3.3 num
  ciclo vivo.
- **Licença.** Nada da pasta `Uniformes 2D` entra no git; os números são
  medidos no disco e a planilha do polipoli é citada como fonte da hipótese,
  não copiada. Crédito por autor (polipoli, SimoSapo, FratelConiglio, ramonpsx,
  Obocaman), nunca "o Superpack". Código de terceiro alcançado por import (CARP
  via `lzss.py`) já tem linha no `NOTICE.md`.
- **Sem state não há fase 0, 2 nem 7**, e sem a fase 0 não há render que se
  possa afirmar. O plano prefere parar a desenhar do que inferiu.

## 7. Fases

| fase | entrega | depende de |
|---|---|---|
| 0 | §4.1, §4.2, §4.3 medidas no disco e no emulador (precisa do state da §4.4); `cli.py base` e `cli.py sprites` como as sondas versionadas | — |
| 1 | **núcleo, leitura**: `layout.py`, `source.py`, `graphics.py`, `sprites.py`, `palette.py`, `render.py`, `api.py`; `teams.py` por import do `kits` (§3.3); `cli.py info/teams/models/render/export` | 0 |
| 2 | **confronto 1**: render × VRAM (§5.1), com o controle negativo | 1 |
| 3 | **núcleo, escrita**: `edit.py`, `writer.py`, `refuse_roms`, round-trip (§5.3), controles (§5.4); `cli.py set-palette/set-model/set-radar/apply` | 1 |
| 4 | **confronto 2**: gravação × port (§5.2); no Linux, × `ed.exe` | 3 |
| 5 | **a janela mínima**: Abrir…, time, titular/suplente, o render lado a lado, 16 cores, Aplicar/Cancelar, guarda de sujo; `kit2d_ui`; captura igual no Windows e no Linux | 2, 3 |
| 6 | modelo (lista dos 190 com miniatura) e radar na janela; `QUndoStack` | 5 |
| 7 | **confronto final**: uma edição aplicada pela ferramenta aparece na tela do emulador — a cor nova, o modelo novo, o pontinho novo | 4, 6 |
| 8 | aba Diagnóstico; a `golden-european-deluxe` aberta sem recusa, com os avisos certos; §4.6 | 5 |
| — | **v2**: gráficos do `DATSEL.BIN` (fit-or-fail); importar/exportar `.m2002` e `.ADD`; a bandeira ao lado, como na tela de opções | 7 |

As fases 1 a 4 não têm janela, de propósito. **O que não pode ser pulado**: a
fase 0, sem a qual todo render é inferência, e a fase 7, sem a qual "grava" é
"grava bytes".

## 8. Como iniciar o ciclo

1. `/rite:new-cycle kit2d` — pasta `docs/tasks/kit2d/`, perfil
   `docs/prompts/perfil-kit2d.md` com uma entrada por fase (0 a 8) em
   "Verificações específicas por fase", e os recursos serializados `emulador`,
   `save-states` e `tela` nas tasks das fases 0, 2 e 7.
2. `/rite:plan-to-tasks kit2d docs/PLAN-KIT2D-PY.md` — `source_of_truth` com
   âncora de seção (`rite anchors docs/PLAN-KIT2D-PY.md` lista as válidas).
3. Antes do primeiro commit do ciclo: o state da §4.4 gravado pelo usuário, e
   `ctest -R tasks` verde.
4. As regras que valem o ciclo todo são as quatro do `CLAUDE.md`
   ("Convenções da documentação"): número colado da ferramenta na HEAD
   entregue; verificador sem vermelho visto não é gate; fechar um veredito é
   varrer quem dizia o anterior; um caso medido não é a regra.
