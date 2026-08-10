---
id: CORR-WTE-048
title: "Correção: o `fase-3.md` ainda diz que o `wte.exe` não passa da tela de carga"
type: correção
category: verificação
status: concluído
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

- [x] `grep -rn "tela de carga" wte/ docs/` só devolve documento que **narra** a
      história, nunca afirmação viva. Os sítios que sobraram, conferidos um a
      um: `wte/re/offsets.md:306` (*"Isso acabou"*), `wte/re/crash-causa.md:160`
      (o desfecho — a 19 *"volta a poder levar o editor além da tela de
      carga"*), `docs/tasks/19-…:369,407` (Log da 3ª e da 4ª passagens),
      `docs/tasks/progresso.md:346` (riscado, com a data da resolução) e os
      `CORR-*`
- [x] `python3 wte/tools/compare_dumps.py --check` verde; duas gerações dão o
      mesmo md5 (`872a5645…`)
- [x] `make -C wte check` verde — 383 testes, `rc=0`
- [x] `roms/` intocada — a correção é de texto gerado

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

A abertura da seção "O oráculo aqui é o de formato" trocou de justificativa.
Antes ela dizia que o `wte.exe` não serve *porque não passa da tela de carga*
— afirmação que a CORR-WTE-044 aposentou, e com um link para essa mesma
correção ao lado. Agora ela diz o que continua verdadeiro depois dela: o
`wte.exe` é o oráculo de **comportamento**, e a pergunta desta task é de
**formato**. Ele é dirigível, com `roms/japanese-shift-jis.bin`, e mesmo assim
não sabe dizer o que os bytes significam — mostra o que o editor *faz*, não o
que o campo *é*.

O ponteiro para o `crash.md` deu lugar ao `crash-causa.md`, que é onde está a
razão de a ROM ser a japonesa. O parágrafo do `we2002_core` como oráculo desta
task ficou como estava, em bloco próprio.

Isso importa para a [WTE-TASK-22](/docs/tasks/22-harness-golden.md): o gate
dela depende de o `wte.exe` ser dirigível, e quem lesse esta seção antes sairia
com a conclusão oposta.

**Problemas encontrados:**

Nenhum. A varredura por `"tela de carga"` devolveu mais cinco sítios além
deste; todos narram a história com a resolução ao lado, e nenhum afirma o
estado atual — estão listados na Verificação.

**Arquivos criados/modificados:**

- `wte/tools/compare_dumps.py` — o texto da seção do oráculo
- `wte/re/fase-3.md` — regerado
