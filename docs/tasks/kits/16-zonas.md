---
id: KITS-TASK-16
---

# KITS-TASK-16 — `zones.py` com proveniência, e a §4.6 fechada contra a geometria

## Goal

O mapa de zonas como dados, cada linha com o autor da medição (polipoli ou ramonpsx, transcritos no SUPERPACK-UNIFORMES §1.3/§2), `api.zone_at(x, y)`, e a conferência mecânica da §4.6: toda UV amostrada cai numa zona, e a zona que nenhuma primitiva amostra está listada com o motivo.

## Arquivos a criar ou modificar

- `tools/kits/core/zones.py`
- `tools/kits/core/api.py`
- `tools/kits/controls.py`
- `docs/PLAN-KITS-PY.md`
- `NOTICE.md`
- `tools/kits/cli.py` — `cli.py zones` (o confronto, `--negative`, `--map`)
- `tools/kits/selftest.py` — `zones.self_check()` e as classes de retângulo no `kits_selftest`; o confronto e o controle 4 no `kits_image`
- `docs/SUPERPACK-UNIFORMES.md` (§2.1, onde o jogo discorda do mapa)

## Done criteria

- [x] O confronto imprime quantas primitivas caem em zona e quantas fora; o número que fica fora é 0 ou cada uma está listada
- [x] Controle: o mapa deslocado 1 px reprova (§5, controle 4) — vermelho no Log
- [x] A §4.6 do plano tem veredito e a lista das zonas sem primitiva
- [x] A seção do `kits` no `NOTICE.md` credita, no mesmo commit, os autores do mapa e das medidas usados — polipoli (`Zonas kits y tex - polipoli/`) e ramonpsx (`Medidas TEX we2002.txt`) —, e cada linha do `zones.py` diz de qual dos dois veio. O Superpack não é citado

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.6).

O que ficou decidido:

- **A regra de "cair numa zona"** é por pixel do retângulo envolvente de cada primitiva (o mesmo do `cli.py uv`, §4.6 nota ¹): todo pixel numa zona — de uma só (`in one zone`) ou de vizinhas (`across zones`, a costura entre duas peças) —, ou numa lacuna declarada (`in a declared gap`); o resto é `outside the map` e reprova.
- **Lacunas, não zonas inventadas.** O que o jogo amostra e o mapa não nomeia entra em `GAPS`, com `source = "KITS-TASK-16"` e o motivo, separado do `ZONES` do polipoli: o mapa continua sendo o dele. Lacuna que ninguém amostra também reprova, para a lista não envelhecer.
- **Proveniência por linha:** `ZONES` é polipoli (remedido do `Zonas We2002.png`), `MEASURES` é ramonpsx (`Medidas TEX we2002.txt`) e só é comparado, não usado como zona. A frente da camisa virou quatro linhas porque o PNG a desenha assim — a gola sobe entre os ombros (o §2.1 do SUPERPACK-UNIFORMES dava o retângulo envolvente).
- **Dois controles para o mesmo defeito:** o 4 do §5 no disco (`cli.py zones --negative`, no `kits_image`) e um literal plantado no `controls.py` (`zones-front-moved`, a frente 1 px à direita), que o `zones.self_check()` pega por sobreposição sem disco.

## Log de Execução

### 2026-10-02

O critério 1 — o confronto:

```
$ python tools/kits/cli.py zones roms/japanese-shift-jis.bin      # exit 0
section 4.6: the zone map against the UV rects of roms/japanese-shift-jis.bin
  kit TEX_A4, tuple A-A1-A-A-A, sha256 of the UV list 2360a921f7cee6f69dcbc1bb3ad2633c306a720c86399a04b918fbdf9448fb84
figure 0: 237 primitive(s) -- 201 in one zone, 7 across zones, 29 in a declared gap, 0 outside the map
figure 1: 429 primitive(s) -- 377 in one zone, 23 across zones, 29 in a declared gap, 0 outside the map
gaps: what the game samples and the map leaves without a zone (6)
  figure 0  (0,80) 20x24  torso, under the map: 28 primitive(s); index 0 in every pixel in 210 of 210 work bitmaps, transparent in 190
  figure 1  (100,104) 20x24  torso, under the map: 28 primitive(s); index 0 in every pixel in 210 of 210 work bitmaps, transparent in 190
  figure 0  (20,5) 4x1  collar, the notch between the shoulders: 1 primitive(s); index 0 in every pixel in 190 of 210 work bitmaps, transparent in 210
  figure 0  (21,6) 2x1  collar, between its tips: 1 primitive(s); index 0 in every pixel in 190 of 210 work bitmaps, transparent in 210
  figure 1  (84,5) 4x1  collar, the notch between the shoulders: 1 primitive(s); index 0 in every pixel in 190 of 210 work bitmaps, transparent in 207
  figure 1  (85,6) 2x1  collar, between its tips: 1 primitive(s); index 0 in every pixel in 190 of 210 work bitmaps, transparent in 207
zones no primitive samples: 16 of 49
  1 zone(s): no primitive of the LOOKS SET samples the shirt numbers; who draws them is not on this screen
  15 zone(s): the sleeves image is sampled by no primitive of the LOOKS SET (PLAN-KITS-PY.md section 4.3): long sleeve and armband are geometry this screen does not draw
ramonpsx against the map: 14 of 21 sizes agree
verdict: section 4.6 holds
```

(As 16 zonas saem uma por linha na saída; cortadas aqui, estão na §4.6 do plano.)

O mapa contra o PNG do polipoli, onde ele está na pasta do usuário:

```
$ python tools/kits/cli.py zones --map "<…>/Zonas kits y tex - polipoli/We2002/Zonas We2002.png"      # exit 0
map: 0 pixel(s) painted and in no zone, 1 zone(s) holding the background (numbers 0-9 by design)
verdict: every row of the map is the picture
```

O critério 2 — o mapa deslocado 1 px reprova, no disco e no PNG:

```
$ python tools/kits/cli.py zones --negative roms/japanese-shift-jis.bin      # exit 0
control: the map moved 1 px right
figure 0: 184 in one zone, 14 across zones, 28 in a declared gap, 11 outside the map
figure 1: 344 in one zone, 52 across zones, 28 in a declared gap, 5 outside the map
control red, held: section 4.6 fails on the moved map
$ python tools/kits/cli.py zones --map "<…>/Zonas We2002.png" --negative      # exit 0
map: 248 pixel(s) painted and in no zone, 30 zone(s) holding the background
control red, held: the moved map fails
$ python tools/kits/controls.py --only zones-front-moved
  RED    zones-front-moved            kits/core/zones.py :: ZONES
controls: 1 of 1 red
```

O critério 3 é a §4.6 do plano (veredito, tabela, as 16 zonas sem primitiva com o motivo). O critério 4 é o `NOTICE.md` (linhas de polipoli e ramonpsx na seção do `kits`) e o `source` de cada linha do `zones.py`:

```
$ python -c "…from core import zones as Z; Counter(z.source for z in Z.ZONES) …"
ZONES {'polipoli': 49} MEASURES {'ramonpsx': 21} GAPS {'KITS-TASK-16': 6}
$ sed -n '/^## Lineage of the kit viewer/,/^## Copyright/p' NOTICE.md | grep -o '^| \*\*[^*]*\*\*'
| **Maximiliano Ducoli (CARP)**
| **Darkensses**
| **LaGaRTo**
| **Francesco Moriero**
| **polipoli**
| **ramonpsx**
$ sed -n '/^## Lineage of the kit viewer/,/^## Copyright/p' NOTICE.md | grep -c Superpack
0
```

Gates:

```
$ python tools/kits/selftest.py --quiet | grep -E "FAIL|controls red|kits_selftest:"
  ..... 13 of 13 controls red
kits_selftest: 0 failure(s)
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir $TEMP/build-kits08 -R kits
100% tests passed out of 3
```
