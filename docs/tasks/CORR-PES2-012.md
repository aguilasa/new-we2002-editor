---
id: CORR-PES2-012
title: "Correção: o estado medido diz 208 contêineres no PES2 e 195 no WE2002; os quatro discos medem 208, 210, 177 e 195"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-PES2-012: a contagem de contêineres é por disco, não por jogo

## Problema identificado

A tabela **"Estado medido, herdado das Fases 0 e 1"** do
[`progresso.md`](/docs/tasks/progresso.md) diz:

> | Contêineres `form1` em `/BIN/` | **208** no PES2, 195 no WE2002 — os 13 de
>   diferença são cópia de idioma |

E o checklist da Fase 7, no mesmo arquivo, e o critério de conclusão da
PES2-TASK-26 dizem *"os **208** contêineres de cada release"*.

A PES2-TASK-26 mediu os quatro discos e a conta é outra: **208** em PES2
`(EsIt)`, **210** em PES2 `(EnFrDe)`, **177** na imagem golden European Deluxe
e **195** na japonesa. O número não é do jogo, é do disco — e a explicação dos
"13 de diferença" compara justamente as duas pontas de uma faixa que agora
tem quatro valores.

A própria task já registra os quatro números na tabela do Log; o que ficou por
reconciliar são as três frases que ainda falam por jogo.

## Evidência

```
$ python3 tools/pes2/lzss.py <os quatro discos> --check
Pro Evolution Soccer 2 (Europe) (Es,It) (Track 1).bin   208 container(s) in /BIN/
Pro Evolution Soccer 2 (Europe) (En,Fr,De) (Track 1).bin 210 container(s) in /BIN/
golden-european-deluxe.bin                              177 container(s) in /BIN/
japanese-shift-jis.bin                                  195 container(s) in /BIN/
TOTAL over 4 disc(s): 790 container(s) …
```

Contra a linha do `progresso.md` ("208 no PES2, 195 no WE2002") e o item
`[x] Os 208 contêineres de cada release classificados`.

## Causa raiz

A medição de 2026-08-30 usou uma release de cada jogo e generalizou para o
jogo. A varredura de quatro discos da PES2-TASK-26 é a primeira que tinha como
mostrar a diferença.

## Correção

### Arquivo: `docs/tasks/progresso.md`

- A linha da tabela de estado passa a dar os quatro números, por disco, e a
  apontar para a §1.14(e), que os publica com o comando que os reproduz. A
  explicação dos "13 de diferença são cópia de idioma" ou some ou passa a dizer
  entre **quais dois discos** ela vale.
- O item do checklist da Fase 7 perde o número: *"os contêineres de cada
  release classificados"*, com a conta dos três verdictos — que é o que ele
  quer garantir.

### Arquivo: `docs/tasks/26-codec-lzss.md`

As três menções a "208" no Contexto e no critério passam a dizer o que se
mediu. O Log já está certo e não se toca.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/progresso.md` | modificar |
| `docs/tasks/26-codec-lzss.md` | modificar |

## Verificação

- [x] `grep -rn "208 contêineres\|208 no PES2" docs/ CLAUDE.md` não devolve
      afirmação por jogo
- [x] os quatro números batem com o `lzss.py --check`
- [x] `python3 tools/check_tasks.py` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito.** A linha da tabela de estado passou a dar os
quatro números por disco — 208, 210, 177 e 195, 790 no total — e a apontar
para a §1.14(e). A explicação dos "13 de diferença" **não sumiu**: ela ficou,
dizendo entre quais dois discos vale. É a segunda opção que a CORR abre, e é
a certa, porque a frase é verdadeira nesse par: 208 − 195 são `(EsIt)` contra
a japonesa, exatamente as duas colunas do histograma da §1.14(a), que já se
rotulam por disco. O item da Fase 7 e o critério da task perderam o número e
ficaram com a conta dos três verdictos, que é o que eles querem garantir.

**Problemas encontrados.** Dois.

1. **A mesma afirmação estava também no plano, fora da lista da CORR.** O
   `PLAN-PES2-PSX.md`, no resumo da Fase 7, mandava *"descomprimir os 208
   contêineres das duas releases"* — e são 208 e 210. Corrigido junto.
2. **Duas ocorrências de "208" ficam de propósito, e não são esta
   afirmação.** A §6.13 do plano e o item correspondente do `progresso.md`
   dizem *"constante lê do lugar errado em 205 dos 208 arquivos"*. É uma
   razão medida sobre um disco, não uma contagem generalizada para o jogo;
   reescrevê-la sem remedir o numerador em cada disco trocaria um número
   medido por um palpite. Fica como está.

**Gates.** Os quatro números saíram do `lzss.py --check` sobre os quatro
discos nesta mesma corrida (208/210/177/195, total 790) — nenhum somado à
mão. `grep -rn "208 contêineres\|208 no PES2" docs/ CLAUDE.md` sem afirmação
por jogo. `check_tasks.py` 82 tasks ok; conferência de link sem quebrado novo.
`roms/` intocada — correção de doc.

**Arquivos criados/modificados:**

- `docs/tasks/progresso.md`
- `docs/tasks/26-codec-lzss.md`
- `docs/PLAN-PES2-PSX.md` (o resumo da Fase 7, não previsto pela CORR)
