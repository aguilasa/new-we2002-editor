---
id: KITS-TASK-07
title: Ler o TEX com guarda de forma e a cauda marcada Form 2 no leiaute Form 1
type: "implementação"
phase: 1
depends_on: [KITS-TASK-06]
source_of_truth: "/docs/PLAN-KITS-PY.md#2.1"
files: ["tools/kits/core/tex.py", "tools/kits/core/source.py", "tools/kits/core/api.py", "tools/kits/core/errors.py", "tools/kits/core/survey.py", "tools/kits/cli.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-07 — Ler o TEX com guarda de forma e a cauda marcada Form 2 no leiaute Form 1

## Goal

`tex.py` lê um TEX, nomeia as 6 imagens e as 5 paletas e preenche `kit.problems` registro a registro; a cauda marcada Form 2 com dado no leiaute Form 1 é lida como Form 1 e o diagnóstico diz que leu assim.

## Arquivos a criar ou modificar

- `tools/kits/core/tex.py`
- `tools/kits/core/source.py`
- `tools/kits/core/api.py`
- `tools/kits/core/errors.py` — `KitError` e filhas; `survey.SurveyError` passou a derivar de `KitsError`
- `tools/kits/core/survey.py` — importa `EXPECTED_SHAPE` do `tex.py`
- `tools/kits/cli.py` — subcomando `tex`, para a evidência sair de comando versionado (como o `open` da KITS-TASK-06)

## Done criteria

- [x] Os 105 TEX do disco japonês abrem com `problems` vazio (número da ferramenta no Log)
- [x] Na `golden-european-deluxe.bin`, lida pelo tamanho ISO (`--iso-size`): dos 18 com cauda Form 2, 16 abrem com a nota de leitura Form 1; `TEX_13` é recusado por ter 10 registros; `TEX_48` é recusado pelo LZSS da primeira imagem (distance 0 no byte 4.810) — saída colada
- [x] Na `golden-european-deluxe.bin`, lida até onde o cabeçalho de cada TEX acaba (o default, decisão de 2026-10-01 abaixo): o `TEX_13` abre com os 11 registros e a nota de leitura além do tamanho ISO; o `TEX_48` continua recusado pelo mesmo motivo; cada recusa diz o registro — saída colada
- [x] Controle: um byte trocado no fluxo LZSS de um TEX sadio é recusado com a frase do registro (§5, controle 4)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#2.1).

Da KITS-TASK-01: os 11 retângulos do TEX (`EXPECTED_SHAPE`) estão em `tools/kits/core/survey.py`; pelo §3.1 endereço mora no `layout.py` do `looks` — mover para lá (ou justificar) quando o `tex.py` os usar, e o `survey.py` passar a importar de um lugar só.

Da KITS-TASK-06: o `core/source.py` reconhece TEX por `survey._shape_of` e `survey.EXPECTED_SHAPE` — quando os retângulos saírem do `survey.py`, o `source.py` passa a usar a função pública do módulo novo. E `survey.SurveyError` deriva de `Exception`; trazê-la para baixo de `errors.KitsError` junto, para `except KitsError` pegar tudo o que o núcleo levanta.

Os retângulos (`EXPECTED_SHAPE`) saíram do `survey.py` para o `tex.py`, não para o `layout.py` do `looks`: o §2 limita as mudanças no `tools/looks/` às duas da fase 5, e o `looks` não lê esses retângulos (ele amostra o kit por ponto de VRAM). Um lugar só continua valendo — `survey.py` e `source.py` importam do `tex.py`. Justificativa também no docstring do módulo.

**Decisão de 2026-10-01 (usuário, nesta execução):** ler o TEX pela extensão que o próprio cabeçalho declara. O critério original pedia o `TEX_13` recusado por 10 registros, e isso é verdade **só lido pelo tamanho ISO** — que a European Deluxe deixou desatualizado em 64 dos 105 TEX. Pergunta feita com os números; resposta: ler pelo cabeçalho, corrigir o §2.1 e o critério. O critério original ficou como o caso `--iso-size`, e um novo critério cobre a leitura default. Varrido: §2.1 e §3.1 do plano, perfil (fases 1 e 9), critério e nota da KITS-TASK-33.

## Log de Execução

### 2026-10-01

Japonês, os 105:

```
$ python tools/kits/cli.py tex roms/japanese-shift-jis.bin | tail -1      # exit 0
105 kits: 105 pass, 0 refused; 0 read past the ISO size, 0 with sectors marked Form 2 read as Form 1
```

European Deluxe pelo tamanho ISO (a leitura que o §2.1 mediu em 2026-09-30):

```
$ python tools/kits/cli.py tex --iso-size roms/golden-european-deluxe.bin > i.txt; tail -1 i.txt
105 kits: 40 pass, 65 refused; 0 read past the ISO size, 18 with sectors marked Form 2 read as Form 1
$ grep -B1 "note:" i.txt | grep "^REFUSE"
REFUSE TEX_13 (31792 bytes): it has 10 image/palette records where a kit container has 11
REFUSE TEX_48 (31464 bytes): record 0 (uniform, first set) has an LZSS stream that does not decode: stream at 48: distance 0 at 4810
$ grep -B1 "note:" i.txt | grep -c "^PASS"
16
```

European Deluxe pelo cabeçalho (default):

```
$ python tools/kits/cli.py tex roms/golden-european-deluxe.bin > e.txt; echo "exit $?"; tail -1 e.txt
exit 1
105 kits: 97 pass, 8 refused; 64 read past the ISO size, 67 with sectors marked Form 2 read as Form 1
$ grep "^REFUSE" e.txt | cut -c1-140
REFUSE TEX_03 (32026 bytes): record 5 (sleeves, second set) decompresses to 15481 bytes where its rectangle asks for 16384
REFUSE TEX_06 (31894 bytes): record 4 (uniform, second set) has an LZSS stream that does not decode: stream at 11784: past the 16384-byte ca
REFUSE TEX_28 (33734 bytes): record 8 (flag) has an LZSS stream that does not decode: stream at 23496: past the 16384-byte cap
REFUSE TEX_48 (31464 bytes): record 0 (uniform, first set) has an LZSS stream that does not decode: stream at 48: distance 0 at 4810
REFUSE TEX_70 (32730 bytes): record 4 (uniform, second set) has an LZSS stream that does not decode: stream at 11948: distance 0 at 16938
REFUSE TEX_84 (32314 bytes): record 4 (uniform, second set) has an LZSS stream that does not decode: stream at 11712: past the 16384-byte ca
REFUSE TEX_92 (30298 bytes): record 10 (referee) decompresses to 16357 bytes where its rectangle asks for 16384
REFUSE TEX_A2 (32738 bytes): record 10 (referee) has an LZSS stream that does not decode: stream at 27200: distance 1 reaches before the sta
$ grep -A2 "TEX_13" e.txt
PASS   TEX_13 (32146 bytes): 6 images, 5 palettes
  note: its ISO size is 31792 bytes and its own header ends at byte 32146, before the next file; read to 32146.
  note: 1 of the 16 sectors read (8675) are marked Form 2 with the data in the Form 1 layout (bytes 2072-2347 zero); read as Form 1.
```

Controle 4 do §5. O vermelho visto primeiro: trocar um byte **literal** (`+1`, `0x00 -> 0xff`) não é defeito de forma — o fluxo ainda descomprime em 16.384 — e a guarda passou (`planted: passes`, `control FAILED`). O controle troca o primeiro byte de flags:

```
$ python tools/kits/cli.py tex --negative roms/japanese-shift-jis.bin      # exit 0
control: TEX_00, byte 48 (record 0 stream +0) 0xea -> 0x15
  clean:   passes
  planted: record 0 (uniform, first set) has an LZSS stream that does not decode: stream at 48: distance 144 reaches before the start of 0 bytes of output
control held: the planted kit is refused on record 0
```

Regressão da KITS-TASK-06 e do levantamento:

```
$ python tools/kits/cli.py open --negative roms/japanese-shift-jis.bin | tail -1
11 of 11 expectations held
$ python tools/kits/cli.py survey --negative roms/japanese-shift-jis.bin | tail -1
4 of 4 controls red
```
