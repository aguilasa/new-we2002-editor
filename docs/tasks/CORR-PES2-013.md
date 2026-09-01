---
id: CORR-PES2-013
title: "Correção: o `check` do `bin_archive.py` sai vermelho na imagem golden, e nenhum documento diz isso"
type: correção
category: verificação
status: pendente
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

- [ ] `bin_archive.py check` nos quatro discos, com o resultado de cada um
      escrito — três verdes e o veredito da European Deluxe
- [ ] a §1.14(f) nomeia o `TEX_70.BIN` entre as falhas do disco hackeado
- [ ] `ctest --test-dir build -R pes2_image` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
