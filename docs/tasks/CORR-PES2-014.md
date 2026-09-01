---
id: CORR-PES2-014
title: "Correção: não são os 105 `TEX_*.BIN` da European Deluxe que são Form 2 — são 18"
type: correção
category: formato
status: concluído
depends_on: []
---

# CORR-PES2-014: 18 de 105, e a própria PES2-TASK-27 lê os outros 87

## Problema identificado

Quatro lugares afirmam, como medido, que na imagem golden European Deluxe
**todos os 105 `TEX_*.BIN` são Form 2** e o `iso.py` recusa lê-los:

| onde | frase |
|---|---|
| `docs/PLAN-PES2-PSX.md` §1.14(e) | "na imagem golden European Deluxe os 105 `TEX_*.BIN` são **Form 2**" |
| `docs/PLAN-FEATURES.md` §5c | idem |
| `docs/tasks/26-codec-lzss.md`, Log | idem |
| `docs/tasks/27-conteiner-e-tim.md`, Contexto | "os 105 `TEX_*.BIN` são Form 2, e o `iso.py` recusa lê-los" |

Medido: são **18**. Os outros **87 são Form 1**, e a ferramenta desta mesma
task os lê — os relatórios de `TEX_03`, `TEX_06`, `TEX_28`, `TEX_70` e
`TEX_84` do `check` no golden saem justamente deles.

A frase serve de desculpa para uma cobertura menor ("um parser que se diga
rodando nas duas imagens de WE2002 tem de dizer qual arquivo ele não
alcançou"), e a desculpa é maior que o buraco: 87 dos 105 são alcançáveis.

## Evidência

```
$ # is_form1() do iso.py, por arquivo
golden-european-deluxe.bin        TEX_* total= 105 form1=  87 form2=  18
   form2 examples: /BIN/TEX_00.BIN /BIN/TEX_01.BIN /BIN/TEX_02.BIN /BIN/TEX_10.BIN …
japanese-shift-jis.bin            TEX_* total= 105 form1= 105 form2=   0
PES2 (EsIt)                       TEX_* total= 105 form1= 105 form2=   0
```

E a própria PES2-TASK-27 lendo um deles no mesmo disco:

```
$ python3 tools/pes2/bin_archive.py check roms/golden-european-deluxe.bin
  /BIN/TEX_84.BIN: image @  11712  vram ( 576, 256)  64x128 declares 16384 B,
                   the stream gives 16501
```

`TEX_84` é Form 1 na European Deluxe. `TEX_00`, o arquivo que originou a
frase, é Form 2 — a generalização de um para 105 é a falha inteira.

## Causa raiz

A PES2-TASK-26 mediu o `TEX_00.BIN` (o da divergência 28 × 48), viu o
`Form 2` e escreveu "os 105"; a PES2-TASK-27 repetiu no seu Contexto sem
remedir, embora sua ferramenta lesse 87 deles.

## Correção

### Arquivos: os quatro acima

Trocar "os 105" por **"18 dos 105"**, com o comando que produz o número, e
dizer que os outros 87 são Form 1 e são lidos normalmente. Onde a frase
justifica cobertura menor (o Contexto da PES2-TASK-27 e a §5c), o ajuste muda
a conclusão: o que não se alcança na European Deluxe são 18 arquivos
nomeáveis, não a família inteira.

A explicação de por que a medição de 2026-08-02 do `TEX_00` não se reproduz
**continua válida** — o `TEX_00` daquele disco é um dos 18.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-PES2-PSX.md` | modificar |
| `docs/PLAN-FEATURES.md` | modificar |
| `docs/tasks/26-codec-lzss.md` | modificar |
| `docs/tasks/27-conteiner-e-tim.md` | modificar |

## Verificação

- [x] o número 18 sai de comando versionado (`iso.py`/`is_form1`), citado no
      texto
- [x] `grep -rn "105 .TEX_" docs/` não devolve mais a afirmação antiga
- [x] `python3 tools/check_tasks.py` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito.** Os quatro textos passaram a dizer **18 dos 105**,
e os 18 entraram **por nome**, que é o que a §1.14 pedia sem ter: `TEX_00`,
`01`, `02`, `10`, `13`, `17`, `34`, `36`, `41`, `43`, `48`, `50`, `51`, `52`,
`63`, `73`, `81` e `83`. O plano leva junto o trecho de `iso.py` que os
produz, e a lista impressa por ele bate com a do texto, nome a nome:

```
18 TEX_00 TEX_01 TEX_02 TEX_10 TEX_13 TEX_17 TEX_34 TEX_36 TEX_41 TEX_43
   TEX_48 TEX_50 TEX_51 TEX_52 TEX_63 TEX_73 TEX_81 TEX_83
```

Nas outras três imagens os 105 são Form 1 — medido, `form2=0`.

**Onde a frase justificava cobertura menor, a conclusão mudou de fato.** No
Contexto da PES2-TASK-27 ela dizia que um parser honesto tem de dizer "qual
arquivo não alcançou"; agora diz que tem de **nomear os 18**, e registra que
esta mesma task lê os outros 87 — os relatórios de `TEX_03`, `TEX_06`,
`TEX_28`, `TEX_70` e `TEX_84` do `check` no golden saem justamente deles. A
desculpa era cinco vezes maior que o buraco.

A explicação de 2026-08-02 **continua válida e ficou mais forte**: o
`TEX_00.BIN`, que é o arquivo da divergência 28 × 48, é um dos 18. Isso está
dito em cada um dos quatro lugares agora, em vez de depender da generalização.

**Problemas encontrados.** Nenhum. Os quatro lugares eram os quatro que a CORR
listou; a varredura por `105 \`TEX_` não devolve mais nada fora dos arquivos
de correção.

**Gates.** O número e os nomes saíram de `iso.py`/`is_form1`, não de contagem
à mão. `check_tasks.py` 82 tasks ok; conferência de link sem quebrado novo.
`roms/` intocada — leitura pura.

**Arquivos criados/modificados:**

- `docs/PLAN-PES2-PSX.md`
- `docs/PLAN-FEATURES.md`
- `docs/tasks/26-codec-lzss.md`
- `docs/tasks/27-conteiner-e-tim.md`
