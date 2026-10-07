---
id: KITS-TASK-10
---

# KITS-TASK-10 — Confronto 2: os pares `_BND.bin`/`_BND.tim` do Superpack

## Goal

A descompressão do `.bin` de cada par do `Banderas 3D/` devolve os pixels do `.tim` byte a byte — oráculo que não passou pelo nosso código. Lê de `WE2002_KITS_CORPUS`; nada do Superpack entra no git.

## Arquivos a criar ou modificar

- `tools/kits/confront.py`
- `tools/kits/selftest.py`
- `tools/kits/controls.py` — o controle `confront2-blind`, e o `expect` do `cli-imports-survey`, cuja linha passou a nomear os dois clientes da fachada
- `tools/kits/core/tex.py`, `core/errors.py`, `core/api.py` — `decompress_stream` e `StreamError`: o `confront.py` é cliente da fachada como o `cli.py`, e o fluxo avulso do WEZip passa pelo mesmo decodificador dos registros do TEX
- `NOTICE.md`, `docs/PLAN-KITS-PY.md` (§5.2, o número medido)
- `docs/tasks/kits/28-confronto-3.md` — uma nota: o `confront.py` passou a existir aqui como o confronto 2, sem subcomando, e é onde o `--score` da KITS-TASK-28 entra (acrescentado ao Escopo pela [CORR-KITS-024](/docs/tasks/concluidos/kits/CORR-KITS-024.md))

## Done criteria

- [x] Com `WE2002_KITS_CORPUS`, o confronto imprime quantos pares foram lidos e quantos batem; a contagem é a da ferramenta, colada no Log
- [x] Sem a variável, sai 77 com a frase do que faltou
- [x] Controle: um `.tim` com um pixel trocado (cópia no scratchpad) reprova
- [x] `git status` não mostra arquivo do Superpack
- [x] A seção do `kits` no `NOTICE.md` credita, no mesmo commit, os autores que aparecem **dentro** do `Banderas 3D/`: quem produziu os `.bin` (WEZip — Lagarto, com a descompressão de WarlockDC e Jordinator) e o autor de cada bandeira onde o arquivo o nomear; quem não for nomeado fica dito como não identificado. O Superpack não é citado

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#5).

O formato, medido antes de escrever o leitor: o `.bin` é **um fluxo LZSS avulso** começando no byte 0 (não um contêiner), e o `.tim` é um TIM de 8 bits com bloco de CLUT de 524 bytes e um bloco de imagem, em sete retângulos diferentes — (704,256), (960,0), (896,0) e (0,0), em 128×64 ou 128×128 (a contagem é a do `--report` abaixo). O `confront.py` lê o TIM com um leitor próprio (o TIM não passa pelo nosso código) e descomprime o `.bin` por `api.decompress_stream`; um par é `.bin` + `.tim` de mesmo nome, em qualquer caixa (`ALVS_BND.TIM`).

O que a pasta tem, contado com `find`: 161 `.bin` e 273 `.tim`; 160 pares. O `.bin` sem par é o `LENS_BND.bin`, que tem `.bmp` ao lado e não `.tim`. Dos 113 `.tim` sem par, 109 são de `Banderas 3D Nacionales`, que não tem `.bin`, e 4 de `Banderas 3D - Mixto` (`BILB_BAND`, `BTS_BND`, `LEVK_BND`, `RNG_BND`). Dos 160 pares, 152 se chamam `*_BND` e 8 não. Contado pela ferramenta desde a [CORR-KITS-022](/docs/tasks/concluidos/kits/CORR-KITS-022.md) (antes a descrição saía de amostra):

```
$ python tools/kits/confront.py --report      # exit 0
Banderas 3D - Mixto/: 161 .bin, 164 .tim, 160 pair(s)
  1 .bin without a partner: LENS_BND
  4 .tim without a partner: BILB_BAND, BTS_BND, LEVK_BND, RNG_BND
Banderas 3D Nacionales/: 0 .bin, 109 .tim, 0 pair(s)
  109 .tim without a partner: (109, not listed)
pairs: 160, 152 named *_BND, 8 otherwise: BAND_ARG, BAND_AUS, BAND_BRA, BAND_CMR, BAND_ING, BAND_IRA, BAND_URU, WBRE_BAND
  TIM flags 9, CLUT block 524 bytes: 160
  image at (704,256) 128x64 px: 76
  image at (960,0) 128x128 px: 41
  image at (896,0) 128x128 px: 28
  image at (0,0) 128x64 px: 11
  image at (0,0) 128x128 px: 2
  image at (704,256) 128x128 px: 1
  image at (960,0) 128x64 px: 1
```

Créditos: nenhum nome de arquivo de bandeira nomeia quem a desenhou — no `NOTICE.md` ficaram como não identificados. Três nomes aparecem nas pastas irmãs dentro de `Banderas 3D` e foram creditados pela [CORR-KITS-023](/docs/tasks/concluidos/kits/CORR-KITS-023.md), pelo que fizeram e sem que o confronto 2 leia nada deles: **Neo2k3**, um modelo-base de bandeira 3D de 128×128 (`.psd`, que pode ser a base das bandeiras — o `Mixto` tem um `01 BASE_BAND_3D.bmp` de 128×128 ao lado delas —, ligação não provada); **Kosmo**, um `.psd` de torcida com bandeiras 3D; e **Fabio FJA**, um patch `.ppf` com tutorial `.docx` que tira as bandeiras 3D dos estádios. O WEZip é creditado pelo `leeme.txt` que acompanha o executável em outras pastas da mesma coleção: "Secuencia de descompresion hecha por WarlockDC y Jordinator / Programado por LaGaRTo / Todos los derechos reservados para WeHispano España 2003". Os arquivos não dizem que ferramenta escreveu cada `.bin`; o `NOTICE.md` diz isso.

O `kits_selftest` ganhou a seção `confront 2`, sem corpus: um par montado ali (pixels comprimidos pelo `lzss.compress`, TIM escrito à mão) tem de bater, um pixel trocado tem de dar `differ` naquele pixel, um TIM cortado tem de ser recusado como TIM e um `.bin` que não decodifica tem de ser dito. O `confront.py` entrou na regra da fachada (`FACADE_CLIENTS`).

## Log de Execução

### 2026-10-01

```
$ export WE2002_KITS_CORPUS="C:/games/we2002/Superpackv6/We2002/TEX/Banderas 3D"
$ python tools/kits/confront.py; echo exit=$?
confront 2: 160 pairs read, 160 match byte for byte (no mismatch)
exit=0
```

Sem a variável:

```
$ env -u WE2002_KITS_CORPUS python tools/kits/confront.py; echo exit=$?
confront 2: skipped -- WE2002_KITS_CORPUS is not set (a folder with the community's *_BND.bin / *_BND.tim pairs)
exit=77
```

O controle, com a cópia no scratchpad:

```
$ python tools/kits/confront.py --negative --scratch <scratchpad>/confront2; echo exit=$?
control: 9JUL_BND.tim copied to <scratchpad>/confront2, pixel byte 1000 (file byte 1544) XOR 0x01
  clean:   match (16384 bytes at (960,0) 64x128)
  planted: differ (1 byte(s) differ, first at 1000)
control held: the changed copy is refused
exit=0
```

Nada do corpus no repositório:

```
$ git status --short
 M docs/tasks/kits/progress.json
 M docs/tasks/kits/progresso.md
 M tools/kits/core/api.py
 M tools/kits/core/errors.py
 M tools/kits/core/tex.py
?? tools/kits/confront.py
```

(antes de `NOTICE.md`, `selftest.py`, `controls.py` e o plano entrarem; nenhum `.bin`, `.tim` ou `.bmp`).

O gate, depois de tudo:

```
$ python tools/kits/controls.py | tail -2
  RED    confront2-blind              kits/confront.py :: compare_pair
controls: 12 of 12 red
$ python tools/kits/selftest.py --quiet | grep -E "FAIL|controls red|kits_selftest:"
  ..... 12 of 12 controls red
kits_selftest: 0 failure(s)
```

Um vermelho errado visto no caminho: a linha da regra da fachada passou a nomear `cli.py and confront.py`, e o controle `cli-imports-survey`, que procurava `FAIL  cli.py imports only core.api`, saiu `GREEN` (`10 of 11 controls red`). O `expect` dele foi atualizado.
- **Closed** — commit `c05f012b` (2026-10-01): feat(kits): add confront 2, the community's 3D flag pairs as an outside oracle
  - Files (`git show --name-status c05f012b`):
    - `M NOTICE.md`
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/10-confronto-2-superpack.md`
    - `M docs/tasks/kits/28-confronto-3.md`
    - `M docs/tasks/kits/progress.json`
    - `M docs/tasks/kits/progresso.md`
    - `A tools/kits/confront.py`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/core/errors.py`
    - `M tools/kits/core/tex.py`
    - `M tools/kits/selftest.py`
- **Reviewed** (2026-10-01) at `aa6d60ce`: CORR-KITS-022, CORR-KITS-023, CORR-KITS-024
