---
id: CORR-WTE-048
title: "Correção: o `fase-3.md` ainda diz que o `wte.exe` não passa da tela de carga"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-048: a afirmação aposentada sobrevive num quinto sítio, e ele é gerado

## Problema identificado

O commit `dd2f2a9` (*"docs: retire the 'oracle is blocked' claim from four
places"*) aposentou a afirmação de que o `wte.exe` não passa da tela de carga:
a [CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) mediu **0 violação de acesso** com
`roms/japanese-shift-jis.bin` contra 49.749 com a europeia, e a
[WTE-TASK-19](/docs/tasks/19-os-50-offsets-restantes.md) fechou dirigindo o
oráculo por dois roteiros novos.

Ele varreu quatro arquivos. O quinto ficou:
[`wte/re/fase-3.md`](../../wte/re/fase-3.md), produto da
[WTE-TASK-20](/docs/tasks/20-round-trip-headless.md), abre a seção do oráculo
com

> Não é o `wte.exe` — esse **não passa da tela de carga**
> (`[crash.md](crash.md)`, `[CORR-WTE-044](../../docs/tasks/CORR-WTE-044.md)`).

O link ao lado aponta justamente para a correção que **desfez** a frase.

A razão de o sweep ter passado por cima é de ordem: `e12a999` (a WTE-TASK-20,
que gerou o `fase-3.md`) é **anterior** a `dd2f2a9`, então o arquivo já existia
quando a varredura rodou e não estava na lista dela.

O que a frase quer dizer continua verdadeiro e é o ponto da seção — o oráculo
desta task é o `we2002_core`, o de **formato**, e não o de comportamento. A
justificativa é que está errada, e é ela que um leitor carrega para a
[WTE-TASK-22](/docs/tasks/22-harness-golden.md), cujo gate depende exatamente de
o `wte.exe` ser dirigível com a imagem japonesa.

## Evidência

A frase viva, no gerado:

```
$ grep -n "tela de carga" wte/re/fase-3.md
12:Não é o `wte.exe` — esse não passa da tela de carga
```

E na fonte dela, `wte/tools/compare_dumps.py:278`:

```python
    w("Não é o `wte.exe` — esse não passa da tela de carga")
```

O que o sweep alcançou:

```
$ git show --stat dd2f2a9 | tail -6
 docs/tasks/19-os-50-offsets-restantes.md | 10 ++++++++++
 docs/tasks/22-harness-golden.md          | 29 +++++++++++++++++++++++++---
 wte/re/offsets-novos.md                  | 26 +++++++++++++-----------
 wte/re/visual.md                         | 14 +++++++++++---
 wte/tools/analisar_io.py                 | 26 +++++++++++++-----------
```

`wte/re/fase-3.md` não está na lista, e a ordem explica: `e12a999` (WTE-TASK-20)
vem antes de `dd2f2a9` no histórico.

## Causa raiz

O sweep da CORR-WTE-044 varreu os arquivos que existiam na cabeça daquele
momento e não incluiu o `fase-3.md`, gerado por um commit anterior.

## Correção

### Arquivo: `wte/tools/compare_dumps.py`

O alvo é gerado — a correção entra no gerador. Trocar a justificativa por uma
que continue verdadeira depois da CORR-WTE-044: o `wte.exe` é o oráculo de
**comportamento** e não responde *o que estes bytes significam*; é dirigível com
a ROM japonesa, e nem por isso serve para esta pergunta. Algo como:

```python
    w("Não é o `wte.exe` — ele é o oráculo de **comportamento**, e a")
    w("pergunta desta task é de **formato**. Ele é dirigível desde a")
    w("[CORR-WTE-044](../../docs/tasks/CORR-WTE-044.md), com")
    w("`roms/japanese-shift-jis.bin`, e continua não sabendo dizer o que")
    w("os bytes significam.")
```

### Arquivo: `wte/re/fase-3.md`

Regerar (`python3 wte/tools/compare_dumps.py`, sem `--check`).

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/compare_dumps.py` | modificar |
| `wte/re/fase-3.md` | modificar (regerado) |

## Verificação

- [ ] `grep -rn "tela de carga" wte/ docs/` só devolve documento que **narra** a
      história (os `CORR-*`, o `crash.md`, o `crash-causa.md`), nunca afirmação
      viva
- [ ] `python3 wte/tools/compare_dumps.py --check` verde
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
