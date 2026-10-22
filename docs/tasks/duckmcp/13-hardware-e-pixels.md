---
id: DMCP-TASK-13
---

# DMCP-TASK-13 — `psx.py`, `gpu.py`, `png.py` e `vram.py`

## Goal

As constantes de hardware PS1 moram em `psx.py` (e a regra (c) passa a lê-las dali); `gpu.py` anda uma lista GP0 a partir de `read(address, size)`; `png.py` é o leitor PNG stdlib único; `vram.py` faz BGR555 ↔ RGB.

## Arquivos a criar ou modificar

- In:
  - os quatro módulos
- Out:
  - trocar `atlas.read_png` e `asset_write.read_png` pelos da lib (Fases 5 e 6)

## Done criteria

- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] o selftest decodifica com `png.py` um PNG gerado pelo próprio teste e compara pixel a pixel; e `vram` faz ida e volta de todos os 32768 valores de 15 bits
- [x] `gpu.py` anda uma lista sintética com um pacote de cada tamanho e termina no marcador de fim, e uma lista em laço é recusada
- [x] a regra (c) importa as faixas de `psx.py`; plantar uma faixa a mais em `selftest.py` não muda o veredito, visto no Log

## Notes

- **Arredondamento do BGR555: não houve escolha a fazer.** As cópias concordam: para baixo é `canal >> 3` (`_halfword` e `_five_bits` do `looks/oracle.py`, `vram_rows` e as leituras das linhas 1762, 1933 e 2566 do `kits/oracle.py`); para cima é `cinco << 3`, sem replicação de bit (a paleta do `save_picture` do `kits/oracle.py` e as linhas 3149 e 3243). O `vram.py` faz as duas, então 31 vira 248, e não 255. Um canal que o emulador tenha gravado com replicação (`v << 3 | v >> 2`) volta igual, porque o `>> 3` descarta exatamente esses bits — há um check só para isso. O bit de máscara não sobrevive a PNG em nenhum dos dois sentidos.
- **`gpu.py` segue o hardware onde o `commands_of` do `looks` não seguia**, e são três diferenças: (1) opcode que o `looks` não conhecia (`01`, `1F`, `03..1E`, `E0`, `E7..FF`) levava o resto do nó, e aqui leva uma palavra, como no GPU; o CPU→VRAM (`A0..BF`) leva os 3 de cabeçalho mais `ceil(w*h/2)` de dados; (2) o terminador de polilinha só é testado onde o próximo vértice — no gouraud, a cor dele — começaria, depois de dois vértices, e não em toda palavra a partir da segunda; (3) nó revisitado sai como `GpuListLoop`, separado de `GpuListTooLong`, comparando pelo endereço de 24 bits para pegar laço entre espelhos. Ficou no `looks`, porque é leitura de tela: vértice, página, CLUT, blend, cor, o centro da cena (`sprites_of`, `furniture_of`, `PAGE_WORD`). Em lista real as diferenças (1) e (2) só mudam o resultado se o nó tiver opcode desconhecido ou um vértice com `5` nos nibbles altos de `x` e `y` — a migração da Fase 5 tem de conferir isso contra as capturas, não presumir.
- **Formato de `read_png` para as migrações.** `png.read_png(path)` devolve `(width, height, rows)` com linhas de tuplas `(r, g, b)` — o mesmo formato do `atlas.read_png` nos tipos 0, 2, 3 e 6 (RGBA perde o alpha nos dois). `png.read_indexed(path)` devolve `(width, height, indices, palette)` com a paleta em `(r, g, b, a)` e o alpha do `tRNS` — o formato do `asset_write.read_png`. Três diferenças que quem migra precisa saber: o erro é `png.PngError` (subclasse de `ValueError`), não `atlas.NoImage` nem `asset_write.Refused`, e o chamador tem de embrulhar; o `png.py` confere o CRC de cada chunk e recusa arquivo truncado, coisa que as duas cópias não faziam; e aceita também o tipo 4 (cinza + alpha).
- **As faixas da regra (c) moram em `psx.HARDWARE_RANGES`**, e o `selftest.py` as lê pelo módulo a cada chamada (`psx.HARDWARE_RANGES`), nunca por um nome ligado no próprio arquivo — é isso que faz uma constante plantada no `selftest.py` não mudar o veredito.
- **Os vetores fixos do `png.py`** foram decodificados uma vez pelo Pillow 12.3.0 em 2026-10-22 e guardados como constante; o módulo não importa o Pillow. Eles existem porque a ida e volta sozinha não pega um erro que o codificador e o decodificador compartilhem — o desempate do Paeth trocado passava verde na ida e volta.

## Log de Execução

### 2026-10-22 — implementação (HEAD `26254854`, árvore com os quatro módulos novos e o `selftest.py` alterado, ainda sem commit)

Criados `tools/duckmcp/psx.py`, `gpu.py`, `png.py` e `vram.py`, cada um com `self_check()`; o `selftest.py` perdeu a constante local de faixas, passou a julgar endereço por `psx.HARDWARE_RANGES` e chama os quatro `self_check()`. Nenhum chamador foi migrado.

Gate:

```
$ python3 tools/duckmcp/selftest.py; echo exit=$?
...
duckmcp_selftest: 339 check(s) ran, 0 failure(s)
exit=0
```

As linhas que respondem pelos critérios 2 e 3 (`python3 tools/duckmcp/selftest.py | grep -E '^  ok    (gpu|png|vram): ' | grep -E 'filter|vector|Paeth|32768|walk|command_size'`):

```
  ok    gpu: command_size gives every opcode shape its hardware size
  ok    gpu: walk returns one node per packet, skipping empty OT slots
  ok    gpu: walk ends at the end marker: the last read is the last node
  ok    gpu: walk refuses a list looping back to its head as a loop
  ok    gpu: walk refuses a list looping back to the middle as a loop
  ok    gpu: walk sees a loop through two mirrors
  ok    gpu: walk refuses a list longer than its limit
  ok    png: filter 0: an RGB image decodes pixel for pixel
  ok    png: filter 1: an RGB image decodes pixel for pixel
  ok    png: filter 2: an RGB image decodes pixel for pixel
  ok    png: filter 3: an RGB image decodes pixel for pixel
  ok    png: filter 4: an RGB image decodes pixel for pixel
  ok    png: one image with all five filters, one per row, decodes
  ok    png: a fixed vector of all five filters decodes as Pillow did
  ok    png: Paeth breaks its ties left, then up, then upper-left, as Pillow did
  ok    png: decode refuses an unknown filter type
  ok    vram: to_halfword(to_rgb(h)) == h for all 32768 values
  ok    vram: join(split(h)) == h for all 32768 values
```

A lista sintética do `gpu` tem um pacote de cada forma de opcode (26: no-op, clear cache, IRQ, E1, E5, F0, fill, os oito polígonos, linha e polilinha nas duas sombras, os retângulos variável, texturizado, 1x1 e 16x16, as três cópias de VRAM), cada um atrás de um slot vazio de OT, e o último nó aponta para o marcador de fim.

**Vermelho visto dos checks novos**, numa cópia do pacote no scratchpad (a árvore não foi tocada): `GpuListLoop` trocado por `GpuListTooLong` no `walk`, o desempate do Paeth trocado (upper-left primeiro) e `to_rgb` com `b << 2`:

```
  FAIL  gpu: walk refuses a list looping back to its head as a loop  GpuListTooLong: the GPU list from 0x80000100 loops: node 0x800001a0 points back to node 0x80000100, visited 10 node(s) earlier
  FAIL  gpu: walk refuses a list looping back to the middle as a loop  GpuListTooLong: the GPU list from 0x80000100 loops: node 0x800001a0 points back to node 0x8000017c, visited 3 node(s) earlier
  FAIL  gpu: walk sees a loop through two mirrors  GpuListTooLong
  FAIL  png: Paeth breaks its ties left, then up, then upper-left, as Pillow did  [10, 12, 20, 16, 6, 44, 26, 54]
  FAIL  vram: to_halfword(to_rgb(h)) == h for all 32768 values  [1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031]
  FAIL  vram: the mask bit is dropped, never kept
  FAIL  vram: white is 248, not 255 (no bit replication)  (248, 248, 124)
duckmcp_selftest: 339 check(s) ran, 7 failure(s)
exit=1
```

Antes do vetor de empate existir, o mesmo Paeth trocado passava verde: os cinco filtros fazem ida e volta com o defeito dos dois lados. Foi o que pôs o vetor no check. E o marcador de fim ignorado (`if nxt == END_MARKER and False:`) dá:

```
  FAIL  gpu.self_check() raised ValueError: 4 byte(s) at 0x80ffffff are outside the 65536-byte dump
duckmcp_selftest: 328 check(s) ran, 1 failure(s)
exit=1
```

**A regra (c) lê as faixas do `psx.py`.** Plantada no `selftest.py` uma faixa local que cobre o `0x12345678` do controle `c-address-outside`:

```
--- planted in selftest.py:
tools/duckmcp/selftest.py:135:HARDWARE_RANGES = (("planted", 0x12340000, 0x1234FFFF),)
tools/duckmcp/psx.py:58:HARDWARE_RANGES = (
$ python3 tools/duckmcp/selftest.py --quiet; echo exit=$?
duckmcp_selftest: 339 check(s) ran, 0 failure(s)
exit=0
$ python3 tools/duckmcp/controls.py --only c-address-outside; echo exit=$?
baseline: the untouched sandbox is green
red    c-address-outside (rule c): FAIL  rule (c): errors.py has no address outside the hardware ranges  line 11: 0x12345678
duckmcp_controls: 1 control(s), 1 red as required; per rule (c) 1/1
exit=0
```

O veredito não mudou. O contrafactual — a mesma faixa plantada no `psx.py`, e não no `selftest.py` — muda, e quem acusa primeiro é a sentinela do próprio juiz:

```
--- planted in psx.py instead:
tools/duckmcp/psx.py:65:    ("planted", 0x12340000, 0x1234FFFF),
$ python3 tools/duckmcp/controls.py --only c-address-outside; echo exit=$?
the untouched sandbox is not green, so no red means anything:
  FAIL  rule (c): the address judge refuses the gaps between ranges
duckmcp_selftest: 339 check(s) ran, 1 failure(s)
duckmcp_controls: 0 control(s) run, baseline red
exit=1
```

As duas plantas foram desfeitas a partir de cópias do arquivo (`cmp` contra a cópia: idênticos); `grep -n planted tools/duckmcp/psx.py tools/duckmcp/selftest.py` só acha a palavra no docstring do `selftest.py` que já existia.

Controles:

```
$ python3 tools/duckmcp/controls.py; echo exit=$?
...
duckmcp_controls: 21 control(s), 21 red as required; per rule (a) 2/2, (c) 8/8, (client) 2/2, (d) 4/4, (fork) 3/3, (live) 1/1, (session) 1/1
exit=0
```

A constante só é definida no `psx.py`:

```
$ grep -n HARDWARE_RANGES tools/duckmcp/*.py
tools/duckmcp/selftest.py:58:     which are `psx.HARDWARE_RANGES`, read through the module;
tools/duckmcp/selftest.py:293:    return not any(lo <= value <= hi for _, lo, hi in psx.HARDWARE_RANGES)
tools/duckmcp/psx.py:9:`HARDWARE_RANGES` is the one list rule (c) of the design rules judges a
tools/duckmcp/psx.py:15:# mask_address of tools/pes2/savestate.py, and the local HARDWARE_RANGES
tools/duckmcp/psx.py:58:HARDWARE_RANGES = (
tools/duckmcp/psx.py:119:    """The name of the `HARDWARE_RANGES` entry `address` falls in, or None."""
tools/duckmcp/psx.py:120:    for name, first, last in HARDWARE_RANGES:
tools/duckmcp/psx.py:132:    spans = {name: last - first + 1 for name, first, last in HARDWARE_RANGES}
tools/duckmcp/psx.py:139:    starts = {name: first for name, first, _ in HARDWARE_RANGES}
tools/duckmcp/psx.py:146:    ordered = sorted((first, last) for _, first, last in HARDWARE_RANGES)
```

ctest:

```
$ ctest --test-dir build -R duckmcp_selftest -V | grep -E 'duckmcp_selftest:|Passed|tests passed'
24: duckmcp_selftest: 339 check(s) ran, 0 failure(s)
1/1 Test #24: duckmcp_selftest .................   Passed    1.66 sec
100% tests passed, 0 tests failed out of 1
```
