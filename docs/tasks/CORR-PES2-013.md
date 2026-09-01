---
id: CORR-PES2-013
title: "Correção: o `check` do `bin_archive.py` sai vermelho na imagem golden, e nenhum documento diz isso"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-PES2-013: gate vermelho num dos quatro discos, sem veredito escrito

## Problema identificado

A §1.14(f) do plano afirma, sobre a coluna *falham* da tabela dos quatro
discos:

> - **Falham.** Todas em `GDC_*`, que a (d) já põe fora de escopo. **Nenhuma
>   fora dos estádios, nos quatro discos.**

Medido: na imagem golden European Deluxe **uma falha está fora dos estádios** —
`/BIN/TEX_70.BIN` —, e é ela, mais os cinco registros da coluna *outros*, que
fazem o `bin_archive.py check` **sair 1 com `CHECK FAILED`** nesse disco.

O critério de conclusão da task diz `[x] O parser rodando também nas duas
imagens de WE2002`, e ele rodou; o que não está escrito em lugar nenhum é que
**o gate fica vermelho lá**. Quem rodar o gate no golden — o perfil o lista
como gate do ciclo — não tem como saber se aquilo é esperado ou regressão.

## Evidência

```
$ python3 tools/pes2/bin_archive.py check roms/golden-european-deluxe.bin
  /BIN/DAT2D.BIN: image @      8 … declares 8192 B, the stream gives 16345
  /BIN/TEX_03.BIN: … declares 16384 B, the stream gives 15481
  /BIN/TEX_06.BIN: … declares 16384 B, the stream gives 16395
  /BIN/TEX_28.BIN: … declares  8192 B, the stream gives 16430
  /BIN/TEX_70.BIN: image record at 18052 does not decompress:
                   stream at 11948: distance 0 at 16938
  /BIN/TEX_84.BIN: … declares 16384 B, the stream gives 16501
  637 image record(s): 530 exact, 82 …, 5 other, 20 that fail to decompress
  … 3 indexed container(s) are stadiums, whose 19 failing record(s) are out
    of scope by plan 1.14(d)
CHECK FAILED
$ echo $?
1
```

20 falhas − 19 de estádio = **uma** fora deles. E ela não é estádio nem Form 2:

```
TEX_70 is_stadium: False   form1: True
```

Os outros três discos saem `CHECK OK`, exit 0 — conferido.

Os **cinco** da coluna *outros* estão escritos na §1.14(f) com os valores
certos (15.481, 16.395, 16.430, 16.501, 16.345 — remedidos, batem). O sexto
registro, o do `TEX_70`, não está em documento nenhum.

## Causa raiz

A frase da §1.14(f) foi escrita a partir dos três discos originais, onde ela é
verdadeira, e generalizada para quatro. E o disco em que ela falha é o único
cujo `check` fica vermelho — os dois fatos são o mesmo fato, e nenhum foi
registrado.

## Correção

### Arquivo: `docs/PLAN-PES2-PSX.md`

- A frase da coluna *falham* passa a dizer o que se mediu: todas em `GDC_*`
  nos três discos originais; na European Deluxe há **mais uma**, o registro em
  18052 de `TEX_70.BIN`, cujo fluxo morre em `distance 0` — o mesmo tipo de
  estrago que os cinco *outros*, e pela mesma razão: **é a imagem hackeada**.
- Entra a linha que falta: **o `check` sai 1 na European Deluxe**, por seis
  registros, e isso é **esperado** enquanto o disco for esse. É veredito, e é
  o que separa "conhecido" de "regressão".

### Arquivo: `docs/prompts/perfil-pes2.md`

A linha do gate `bin_archive.py check` diz em quais discos ele é verde e que a
European Deluxe é vermelha por seis registros conhecidos.

### Opcional, e melhor que a nota

`bin_archive.py` ganha `--known-hacked` (ou reconhece o disco), contando os
seis como categoria própria em vez de `bad`, do mesmo jeito que já faz com os
estádios da §1.14(d). Um gate que só fica vermelho por motivo que ninguém
pretende consertar é o problema que a própria task já resolveu uma vez, para
os `GDC_*`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-PES2-PSX.md` | modificar |
| `docs/prompts/perfil-pes2.md` | modificar |
| `tools/pes2/bin_archive.py` | modificar, se a saída for a categoria própria |

## Verificação

- [x] `bin_archive.py check` nos quatro discos, com o resultado de cada um
      escrito — três verdes e o veredito da European Deluxe
- [x] a §1.14(f) nomeia o `TEX_70.BIN` entre as falhas do disco hackeado
- [x] `ctest --test-dir build -R pes2_image` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito.** Foi feita a forma **opcional**, que a própria CORR
diz ser melhor que a nota: a European Deluxe é reconhecida pelo rótulo que o
`lzss.EXPECT` resolve da contagem de contêineres, e os seis registros que não
cabem no próprio retângulo viram categoria própria em vez de `bad` — a mesma
disciplina que a task já aplicou aos estádios da §1.14(d). O gate agora sai
**0 nos quatro discos**:

```
Pro Evolution Soccer 2 (Es,It)     CHECK OK   exit=0
Pro Evolution Soccer 2 (En,Fr,De)  CHECK OK   exit=0
golden-european-deluxe.bin         WE2002 European Deluxe is a hacked image:
  its 6 record(s) that do not fit their own rect are the known ones (plan
  1.14(f)), and are counted, not failed          CHECK OK   exit=0
japanese-shift-jis.bin             CHECK OK   exit=0
```

**A contagem é a asserção, não uma anistia.** Três controles negativos:

```
esperado 5, medido 6   -> CHECK FAILED: … 6 record(s) do not fit, and 5 are the measured, known ones
permissao removida     -> CHECK FAILED
check --file no golden -> the known-hacked allowance is not applied to a single
                          --file run; 1 record(s) counted as failures  CHECK FAILED
```

Uma sétima falha naquele disco fica vermelha, que é o ponto: sem isso a
permissão esconderia regressão em vez de nomear o conhecido.

A §1.14(f) passou a nomear o `TEX_70.BIN` entre as falhas — 20 menos as 19 de
estádio — e ganhou o parágrafo do veredito por disco. A linha do gate no perfil
diz o mesmo com o número.

**Problemas encontrados.** Um: **a mesma afirmação estava no `PLAN-FEATURES.md`
§5 Fase 10**, fora da lista da CORR — o critério de aceite dizia "na European
Deluxe são cinco entradas que não batem". São seis, e a sexta é de outra
natureza (não decodifica, contra cinco de tamanho). Corrigido junto.

**Gates.** `bin_archive.py check` exit 0 nos quatro discos; três controles
negativos vermelhos; `ctest -R pes2_selftest|pes2_image` 2/2 `Passed`;
`check_tasks.py` 82 tasks ok. `roms/` intocada — leitura pura.

**Arquivos criados/modificados:**

- `tools/pes2/bin_archive.py`
- `docs/PLAN-PES2-PSX.md`
- `docs/prompts/perfil-pes2.md`
- `docs/PLAN-FEATURES.md` (não previsto pela CORR)
