---
id: CORR-WTE-109
title: "Correção: quatro sítios do lado WTE atribuem a não-idempotência ao \"editor original\", que aqui é o wte.exe — e o único caminho medido não a tem"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-109: "o editor original não é idempotente" — qual editor?

## Problema identificado

A [CORR-WTE-104](/docs/tasks/CORR-WTE-104.md) mediu, em 2026-08-25, que o
`wte.exe` **não** troca os cobradores ao gravar tática duas vezes: uma gravação
e duas dão a mesma imagem, e os seis bytes de `OFS_KICKER` saem intactos dos
três estados.

A [CORR-WTE-108](/docs/tasks/CORR-WTE-108.md) conferiu o plano e o achou limpo.
**A varredura dela achou outra coisa:** quatro sítios vivos do lado WTE
afirmam a não-idempotência falando de *"o original"* ou *"o editor original"*
— e **neste projeto "o original" é o `wte.exe`**, não o `ed.exe`. O port é o app
Lazarus; o original é o binário do Obocaman.

A frase é herdada do `newWe2002`, onde ela é **verdadeira e medida** — lá o
oráculo é o `ed.exe`. Ao migrar para as tasks do WTE ela trocou de sujeito sem
trocar de palavras.

| Sítio | O que diz | Qual editor o leitor entende |
|---|---|---|
| [`wte/tools/gravacao_controle.py:197`](../../wte/tools/gravacao_controle.py) | *"o `Load`+`Save` do editor original não é idempotente"* | `wte.exe` |
| [`wte/re/gravacao-controle.md:19`](../../wte/re/gravacao-controle.md) | idem — **é gerado pelo de cima** | `wte.exe` |
| [`docs/tasks/19-os-50-offsets-restantes.md:41`](/docs/tasks/19-os-50-offsets-restantes.md) | *"O `Load`+`Save` do original **não é idempotente**"* | `wte.exe` |
| [`docs/tasks/27-handlers-de-gravacao.md:91`](/docs/tasks/27-handlers-de-gravacao.md) | *"o `Load`+`Save` do original não é idempotente"* | `wte.exe` |

O `golden-02-gravacao.txt:16` diz o mesmo, e o
`golden-24-gravacao-dupla.txt:9` também — mas este atribui (*"o `newWe2002`
registra que…"`*), o que o salva. Os de `docs/PLAN-LINUX.md` e do `CLAUDE.md`
estão **certos**: são do outro projeto, onde o oráculo é o `ed.exe`.

## Por que isto não foi consertado junto

**Porque a medição não cobre a afirmação inteira.** A CORR-WTE-104 mediu **um**
caminho de gravação — o ` Accept` da tela de tática
(`estrategia.BitBtn3Click`), que é a gravação que carrega `OFS_KICKER`. A frase
dos quatro sítios é sobre o ciclo `Load`+`Save` em geral.

Trocar "o original" por "o `ed.exe`" nos quatro seria provavelmente certo e
**não está medido**: se algum outro caminho do `wte.exe` reproduzir o vaivém, a
troca teria criado a mentira simétrica. Redimensionar isso dentro da
CORR-WTE-108 — cujo escopo é uma frase sobre o plano — seria o que o
`03-corrigir.md` chama de resolver de afogadilho.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rn "não é idempotente\|nao e idempotente" docs wte CLAUDE.md
```

```text
docs/tasks/19-os-50-offsets-restantes.md:41:O `Load`+`Save` do original **não é idempotente**: ele troca os dois primeiros
docs/tasks/27-handlers-de-gravacao.md:91:`Load`+`Save` do original não é idempotente (troca os dois primeiros cobradores
wte/tools/gravacao_controle.py:197:    w("`Load`+`Save` do editor original não é idempotente.")
wte/re/gravacao-controle.md:19:`Load`+`Save` do editor original não é idempotente.
```

E o que está medido contra isso, do `wte/re/golden.md` (gerado):

| Medida | Bytes |
|---|---:|
| uma gravação × duas gravações (tática, time 5) | **0** |
| ROM virgem × uma gravação | 11.962 |

`OFS_KICKER` do time 5: `[9, 5, 5, 5, 7, 5]` na ROM virgem, depois de uma
gravação e depois de duas.

## Causa raiz

Frase verdadeira sobre o `ed.exe`, migrada do `newWe2002` para as tasks do WTE
sem trocar o sujeito. É a mesma família da
[CORR-WTE-101](/docs/tasks/CORR-WTE-101.md) — número que migra de um documento
para outro e envelhece no destino —, com sujeito no lugar de número.

## Correção

### Primeiro medir, depois escrever

O que falta é saber se **algum** caminho de gravação do `wte.exe` troca o par.
O barato é o `gravacao-controle`: ele já grava sem editar nada e mede o que
muda de graça, nas duas ROMs. Rodá-lo **duas vezes seguidas** sobre a mesma
cópia e comparar as duas saídas responde a pergunta geral pelo mesmo preço da
resposta particular que a CORR-WTE-104 pagou.

- **Nenhum caminho troca** → os quatro sítios trocam *"o original"* por *"o
  `ed.exe`"*, com o número ao lado; o `gravacao_controle.py` é gerador, então
  a correção entra nele e o `.md` é regerado.
- **Algum troca** → a frase fica, ganha o caminho nomeado, e vira entrada da
  [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md) com o offset.

### Guarda

O `check_divergencias.py` não alcança isto — não é isenção. O lugar natural é o
próprio `gravacao_controle.py`, que já publica número medido: se ele passar a
comparar as duas gravações, a afirmação do `.md` deixa de ser herdada e passa a
sair da corrida.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/gravacao_controle.py` | modificar — a medida e a frase |
| `wte/re/gravacao-controle.md` | regerar |
| `docs/tasks/19-os-50-offsets-restantes.md` | modificar |
| `docs/tasks/27-handlers-de-gravacao.md` | modificar |
| `wte/tests/roteiros/golden-02-gravacao.txt` | modificar |

## Verificação

- [ ] A segunda gravação foi medida, e o número está escrito
- [ ] `grep -rn "do original não é idempotente" docs wte` não devolve
      afirmação sem sujeito
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada; trabalhou sobre cópia

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
