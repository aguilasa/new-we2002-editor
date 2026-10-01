---
id: CORR-KITS-023
---

# CORR-KITS-023 — Credit or account for the authors named by Banderas 3D folders

Origin: [KITS-TASK-10](/docs/tasks/kits/10-confronto-2-superpack.md)

## Problem

O `NOTICE.md` diz que "nenhum arquivo, nome de arquivo ou nome de pasta em `Banderas 3D` nomeia quem os desenhou". Dentro de `Banderas 3D` há `Base bandera 3D - Neo2k3/Base bandera 3D - NEO2k3.psd` (um modelo-base de bandeira 3D; `Banderas 3D - Mixto/01 BASE_BAND_3D.bmp` fica ao lado das bandeiras), `Hinchas por banderas 3D - Kosmo.psd` e `Remover as bandeiras 3D ... - Fabio FJA/` (um `.docx` e um `.ppf`). O critério de pronto pede crédito aos autores que aparecem dentro de `Banderas 3D`, e o perfil manda citar quem aparece ali. Nenhum dos três nomes está no `NOTICE.md`, e a frase de "não identificados" não os menciona. É plausível que a base do Neo2k3 seja aquela sobre a qual as bandeiras foram desenhadas, mas essa ligação não está provada.

## Evidência

```text
$ cd "$WE2002_KITS_CORPUS"; find . -type f ! -iname '*.bin' ! -iname '*.tim'
./Banderas 3D - Mixto/01 BASE_BAND_3D.bmp
./Base bandera 3D - Neo2k3/Base bandera 3D - NEO2k3.psd
./Hinchas por banderas 3D - Kosmo.psd
./Remover as bandeiras 3D grandes e pequenas dos estádios - Fabio FJA/Remover as bandeiras 3D grandes e pequenas dos estádios - Fabio FJA.docx
$ grep -c -iE "neo2k3|kosmo|fabio" NOTICE.md
0
```

## Root cause

Hipótese: a busca por autor olhou só os arquivos dos pares e a pasta `Mixto`, não as pastas irmãs dentro de `Banderas 3D`.

## Fix

Na linha do kits no `NOTICE.md`, nomear o Neo2k3 como autor do modelo-base de bandeira 3D achado ao lado das bandeiras, ou dizer por que ele não é a base delas. Dizer que Kosmo e Fabio FJA aparecem na pasta, mas que o trabalho deles (um PSD de torcida; um patch SLPM com tutorial) não é lido pelo confronto 2. Atualizar o parágrafo "Créditos" das Notas da KITS-TASK-10 para bater.

## Arquivos a criar ou modificar

- `NOTICE.md`
- `docs/tasks/kits/10-confronto-2-superpack.md`

## Verificação

```text
$ grep -n -iE "neo2k3" NOTICE.md
```

Hoje não imprime nada; depois tem de imprimir a linha do kits.

## Log de Execução

### Reprodução (HEAD `f66559ad`, com `WE2002_KITS_CORPUS` apontado — o shell do `rite reproduce` não o tinha)

```text
$ cd "$WE2002_KITS_CORPUS"; find . -type f ! -iname '*.bin' ! -iname '*.tim' | grep -v "_BND\.\|BAND\.bmp"
./Banderas 3D - Mixto/01 BASE_BAND_3D.bmp
./Base bandera 3D - Neo2k3/Base bandera 3D - NEO2k3.psd
./Hinchas por banderas 3D - Kosmo.psd
./Remover as bandeiras 3D grandes e pequenas dos estádios - Fabio FJA/Remover as bandeiras 3D grandes e pequenas dos estádios - Fabio FJA.docx
./Remover as bandeiras 3D grandes e pequenas dos estádios - Fabio FJA/Remover as bandeiras 3D grandes e pequenas dos estádios - Fabio FJA.ppf
$ grep -c -iE "neo2k3|kosmo|fabio" NOTICE.md
0
```

REPRODUCED.

### O que foi feito

- `NOTICE.md`, linha do WEZip/confronto 2: "não identificados" fica para os autores das bandeiras (nenhum nome de arquivo de bandeira nomeia quem a desenhou), e os três nomes da pasta entram creditados pelo que fizeram, dizendo que o confronto 2 não lê nada deles. A ligação Neo2k3 → bandeiras fica como **possível, não provada**: o `.psd` dele (2005) e o `01 BASE_BAND_3D.bmp` do `Mixto` (2006) têm os dois 128×128 (lido do cabeçalho de cada um), e nada na pasta diz que um saiu do outro ou que as bandeiras foram desenhadas sobre eles.
- KITS-TASK-10, parágrafo "Créditos" das Notas: o mesmo.

### Verificação

```text
$ grep -n -iE "neo2k3" NOTICE.md | cut -c1-80
222:| **LaGaRTo**, with **WarlockDC** and **Jordinator** | WEZip 1.0 — compresse
$ grep -c -iE "neo2k3|kosmo|fabio" NOTICE.md
1
```
- **Closed** — commit `d30a4d78` (2026-10-01): docs(notice): credit Neo2k3, Kosmo and Fabio FJA, named inside Banderas 3D
  - Files (`git show --name-status d30a4d78`):
    - `M NOTICE.md`
    - `M docs/tasks/kits/10-confronto-2-superpack.md`
    - `M docs/tasks/kits/CORR-KITS-023.md`
