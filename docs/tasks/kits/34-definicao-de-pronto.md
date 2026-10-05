---
id: KITS-TASK-34
---

# KITS-TASK-34 — Conferir a Definição de pronto do §0, item por item

## Goal

Os cinco itens da Definição de pronto do §0 conferidos na HEAD, cada um com o comando e a saída.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-PY.md`

## Done criteria

- [x] Item 1: 105 TEX, 6 imagens × 5 paletas, sem imagem cinza e sem índice fora (contagem)
- [x] Item 2: 3D veste jogador e goleiro, titular e suplente de um time que difere, e o confronto 3 concorda
- [x] Item 3: TEX do WETex abre; TEX quebrado recusado com motivo
- [x] Item 4: §4.6 fechada com a lista do que sobra
- [x] Item 5: CLI importa só a fachada; captura igual no Windows e no Linux

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#definição-de-pronto).

Da KITS-TASK-33: o `kits_ui` julga a aba Diagnóstico nos `TEX_48`, `TEX_70` e `TEX_13` da European Deluxe só com `WE2002_KITS_ED_IMAGE` apontando o `roms/golden-european-deluxe.bin`; sem ela ele passa e imprime `note: WE2002_KITS_ED_IMAGE is not set`. Corrida desta task leva a variável.

### O que falta fazer no Windows (destrava o item 5) — feito em 2026-10-05

Os passos abaixo rodaram na HEAD `71c65f3`; a saída está no Log, em
"no Windows". Sobra só o fechamento no Linux, no último parágrafo desta seção.

A única captura do Windows é a da KITS-TASK-19, de antes das abas 3D e
Diagnóstico, do seletor de idioma e do inglês por default; contra a janela de
hoje ela dá 47,56 % e reprova. Na máquina Windows, com o repositório na HEAD e o
venv `work/venv-looks` com PySide6:

1. `git pull` na raiz do repositório.
2. Feche qualquer janela do `kits` aberta e rode, **da raiz do repositório**
   (o caminho relativo `roms/...` aparece na barra de cima e entra na
   comparação):

   ```
   work/venv-looks/Scripts/python.exe tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot work/kits-ui-windows.png
   ```

   A janela sobe fora da tela (`window up, at -32000,-32000`) e o comando
   imprime `wrote work/kits-ui-windows.png, 980x640`. Sem `--lang` e sem
   `WE2002_KITS_LANG` definida: a captura tem de sair em inglês, como a do
   Linux.
3. Opcional, para ter o número já lá: o mesmo estado no Windows contra si
   mesmo, `python tools/kits/ui_check.py --compare work/kits-ui-windows.png work/kits-ui-windows.png`, tem de dar 0 %.

De volta ao Linux, a captura aparece em
`/media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png` (o `C:`
montado), e o fechamento da task é: refazer `work/kits-ui-linux.png` pelo mesmo
comando no `:98` (com `work/venv-looks/bin/python`) e rodar
`python3 tools/kits/ui_check.py --compare /media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png work/kits-ui-linux.png`,
que tem de ficar abaixo de 5 % (`CROSS_LIMIT`), com a cor de janela e o painel
Fusion acima de 10 % nas duas; depois `rite mark KITS-TASK-34 pending`, o Log
com a saída, o item 5 marcado e `rite finish`.

## Log de Execução

### 2026-10-05

Na HEAD `f3d3b20`, com `WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin` e
`WE2002_KITS_ED_IMAGE=roms/golden-european-deluxe.bin`.

**Item 1** — `python3 tools/kits/cli.py survey roms/japanese-shift-jis.bin`:

```
  TEX_<tag>.BIN containers                       105
  shape 6 images + 5 CLUTs, same rects/order     105 of 105
```

`python3 tools/kits/cli.py flat roms/japanese-shift-jis.bin`:

```
945 pairings painted (9 per kit): 0 with an index past its palette, 0 of a single colour; 420 of 420 work bitmaps 256x128; index 0 transparent in 397 of 525 palettes; 0 kit(s) refused
```

`cli.py teams`: `95 teams: 95 table; 0 empty name(s); 95 with a kit tag` no
japonês e `95 teams: 95 rom; …` na European Deluxe; o combobox lista os times
(KITS-TASK-31, juiz `selector` do `kits_ui`).

**Item 2** — `ctest --test-dir build -R kits -V` (4 de 4), a linha do 3D:

```
  ok    3D TEX_00: the four combinations draw a figure, and set 1 is not set 2 for either figure (set 1 fig 0 784f604a6c19, set 1 fig 1 7fad0b56a394, set 2 fig 0 eb2833994286, set 2 fig 1 cfe1677a295b)
```

e o jogo: `python3 tools/kits/oracle.py --slot 3 --cue $PWD/work/we2002-english.cue --out <scratchpad>/dod --expect 01=1 --expect 13=2`
→ `control: two dumps a frame apart give the same 8 match(es)` e
`ok    TEX_01 in set 1, TEX_13 in set 2`; sobre o `screen.png` dessa corrida
(sha256 `ee1bfba6e7dc…`, o fixado), `confront.py --score`:

```
  TEX_01 players: our TEX_01 leads our TEX_13 by 0.342
  TEX_13 players: our TEX_13 leads our TEX_01 by 0.410
confront 3: 2 of 2 team(s) score their own kit 0.05 over the other's
```

e `--score --negative`: `the swapped renders give 2 failure(s) of 2 -- the control holds`.

**Item 3** — não havia TEX de WE2002 feito pelo WETex no Superpack (só os 105
originais de cada jogo e dois TEX do WE4, outro formato), então um foi feito
aqui. O WETex 1.0 (`Superpackv6/We2002/Imagen/WEZIP y WETex - Lagarto, Warlock
y Jordinator/WETex.exe`, VB6) roda sob o Wine 32 bits do Bottles num prefix só
dele (`work/wineprefix-wetex`), com o `msvbvm60.dll`, o `COMDLG32.OCX` e o
`MSCOMCTL.OCX` copiados do `C:\Windows\SysWOW64` desta máquina e registrados
— nada disso entra no git. As onze entradas saíram dos registros do `TEX_00`
japonês (`/BIN/TEX_00.BIN` por `iso.py extract`): o fluxo LZSS cru de cada
imagem (registros 0, 1, 4, 5, 8 e 10) como `.bin`, e cada paleta (2, 3, 6, 7,
9) como bloco de CLUT de um TIM de 8 bits; os campos se preenchem pelos
diálogos de arquivo (os de texto são só leitura), e "Crear Camiseta" respondeu
`Listo` com `work/wetex/wetex00.bin`, 29.928 bytes contra os 29.944 do
original, sha256 `de2e2d49f07b11d8…` — bytes diferentes (`cmp`: `differ: byte
1`), o mesmo uniforme:

```
$ python3 tools/kits/cli.py tex work/wetex/wetex00.bin
PASS   wetex00.bin (29928 bytes): 6 images, 5 palettes
```

As seis imagens exportadas por `cli.py export --palette N` dos dois arquivos
dão o mesmo sha256 nas cinco paletas (ex.: paleta 2, `bb973416f3a4` nos dois).
A janela o abre: `work/venv-looks/bin/python tools/kits/ui/app.py
work/wetex/wetex00.bin --screenshot work/kits-wetex00.png` sai 0, `lone TEX ·
… 29928 bytes`, e `--list-diagnosis` dá `read, nothing to report`.

TEX quebrado recusado com o motivo: a linha do `kits_ui` acima, da KITS-TASK-33:

```
  ok    the Diagnosis tab lists the guard's refusal and the reading notes, and nothing for a sound kit (sound 0 row(s), 0 text px in its list, planted 1 row(s), ED TEX_48 2 row(s), ED TEX_70 3 row(s), ED TEX_13 2 row(s))
```

**Item 4** — `python3 tools/kits/cli.py zones roms/japanese-shift-jis.bin`:

```
figure 0: 237 primitive(s) -- 201 in one zone, 7 across zones, 29 in a declared gap, 0 outside the map
figure 1: 429 primitive(s) -- 377 in one zone, 23 across zones, 29 in a declared gap, 0 outside the map
gaps: what the game samples and the map leaves without a zone (6)
zones no primitive samples: 16 of 49
verdict: section 4.6 holds
```

**Item 5 — a metade da fachada passa, a do Windows não pôde ser medida.**
`kits_selftest`: `ok cli.py and confront.py import only core.api and the
standard library (section 3.1)`, `ok ui/app.py shows no text outside tr()`,
`language: 0 failure(s)`. A comparação entre plataformas **reprova**, e não
por defeito da janela: a única captura do Windows é a da KITS-TASK-19
(`/media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png`, sha256
`e973a8aa5991a7ff…`), de antes do 3D, do Diagnóstico, do seletor de idioma e do
inglês por default — a janela de hoje tem uma linha a mais embaixo, e o plano
inteiro desce:

```
$ python3 tools/kits/ui_check.py --compare /media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png work/kits-ui-linux.png
kits-ui-windows.png: 980x640, window colour 23.1 %, Fusion pane 18.8 %
kits-ui-linux.png: 980x640, window colour 22.4 %, Fusion pane 18.2 %
298315 of 627200 pixels differ (47.56 %)
FAIL  47.56 % differ, above the 5.0 % limit
```

Falta uma captura do Windows na HEAD, que só sai no Windows. Destrava assim: lá,
da raiz do repositório,
`work/venv-looks/Scripts/python.exe tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot work/kits-ui-windows.png`;
aqui, `python3 tools/kits/ui_check.py --compare /media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png work/kits-ui-linux.png`
com o `work/kits-ui-linux.png` refeito pelo mesmo comando no `:98`.
### 2026-10-05, no Windows — a metade do Windows feita

Na HEAD `71c65f3`, Windows 11, `WE2002_KITS_LANG` vazia. A captura antiga da
KITS-TASK-19 ficou guardada como `work/kits-ui-windows-task19.png` (fora do git)
e a nova tomou o lugar dela:

```
$ work/venv-looks/Scripts/python.exe tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot work/kits-ui-windows.png
  wrote work/kits-ui-windows.png, 980x640
  window up, at -32000,-32000
$ sha256sum work/kits-ui-windows.png
82cc3da377931656e2aeee2a0c90097e993b39aabe0eb1d69289d9254d7f2d7c
$ python tools/kits/ui_check.py --compare work/kits-ui-windows.png work/kits-ui-windows.png
kits-ui-windows.png: 980x640, window colour 22.6 %, Fusion pane 18.2 %
0 of 627200 pixels differ (0.00 %)
ok    within 5.0 %, both with the fixed look
$ python tools/kits/ui_check.py --compare work/kits-ui-windows-task19.png work/kits-ui-windows.png
295615 of 627200 pixels differ (47.13 %)
FAIL  47.13 % differ, above the 5.0 % limit
```

A captura sai em inglês, com as abas Plan, 3D e Diagnosis e o seletor de
idioma (olhada). O último comando é o controle: a captura velha contra a nova
reprova, e com a mesma cifra da corrida do Linux, então era a captura que
estava velha. Falta a metade do Linux: refazer `work/kits-ui-linux.png` no `:98`
e o `--compare` contra
`/media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png` (sha256
acima).

- **blocked** (2026-10-05): Item 5: python3 tools/kits/ui_check.py --compare /media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png work/kits-ui-linux.png -> FAIL 47.56 % differ, above the 5.0 % limit; the only Windows capture (sha256 e973a8aa5991a7ff) predates the 3D/Diagnosis tabs and en-US default. Needs a new capture on Windows at HEAD (app.py roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot work/kits-ui-windows.png). Items 1-4 checked in 24beba1.
- **blocked** (2026-10-05): Item 5: Windows half done (work/kits-ui-windows.png at 71c65f3, sha256 82cc3da37793, 0 % vs itself, see Log). Remaining: on Linux, redo work/kits-ui-linux.png on :98 and run python3 tools/kits/ui_check.py --compare /media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png work/kits-ui-linux.png, must be under 5 %.
- **pending** (2026-10-05): Windows capture at HEAD now exists (sha256 82cc3da37793, commit 8d1ab8d); Linux compare runs

### 2026-10-05, no Linux — item 5 fechado

Na HEAD `bfa36b9`, Xvfb `:98` sem `-auth`, `WE2002_KITS_LANG` vazia. (A
primeira tentativa achou o `:98` caído — o Qt saiu com `could not connect to
display :98` e o `--compare` leu o PNG de ontem; o servidor foi subido de novo
e a captura refeita do zero, com o arquivo apagado antes.)

```
$ work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot work/kits-ui-linux.png
  wrote work/kits-ui-linux.png, 980x640
$ sha256sum work/kits-ui-linux.png
8f8b9dbddb7b541b1b3327a2f966fcdbdd8c82811834bfbc404841610b23a126  work/kits-ui-linux.png
$ python3 tools/kits/ui_check.py --compare /media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png work/kits-ui-linux.png
kits-ui-windows.png: 980x640, window colour 22.6 %, Fusion pane 18.2 %
kits-ui-linux.png: 980x640, window colour 22.4 %, Fusion pane 18.2 %
14895 of 627200 pixels differ (2.37 %)
ok    within 5.0 %, both with the fixed look
```

A captura do Linux saiu com o mesmo sha256 da de ontem: a janela é
determinística no `:98`. Controle: o mesmo estado com `--tag A4` contra a
captura do Windows reprova — `313502 of 627200 pixels differ (49.98 %)`,
`FAIL  49.98 % differ, above the 5.0 % limit`. A fachada e o catálogo, já
colados acima, completam o item.
