---
id: CORR-LOOKS-029
title: "Correção: o `HEAD_RUNS` diz \"todo corpo distinto, cada um com sua janela\" e o disco diz doze corpos e catorze janelas"
type: correção
category: engenharia-reversa
status: concluído
depends_on: []
---

# CORR-LOOKS-029: "32 corpos distintos" são 32 seções distintas, e as janelas não são 32

## Problema identificado

O docstring do `layout.HEAD_RUNS` afirma duas coisas sobre o primeiro bloco de
cabeças, e o disco contradiz as duas:

```python
# tools/looks/layout.py
HEAD_RUNS = ((24, 56), (74, 106))
"""...
**Thirty-two sections each, every body distinct**, measured 2026-09-16.  All
32 of the first run sample HAIR_IMAGE, each with its own window on that sheet;
of the second run, 16 do.
...
The first run is therefore **sixteen pairs** rather than 32 independent heads
"""
```

O mesmo docstring diz **"every body distinct"** no primeiro parágrafo e
**"sixteen pairs rather than 32 independent heads"** no último. As duas não
podem valer, e é a segunda que o disco sustenta.

O número 32 vem do `assembly.head_runs`, que conta `bytes(data[offset:end])` —
**blobs de seção**, não corpos — e imprime `distinct body(ies)`:

```text
python tools/looks/assembly.py --check-image
  MODEL.BIN sections 24..55: 32 distinct body(ies), 32 of them sampling the hair sheet
```

A palavra é a mesma que o `head_pairs` usa no sentido oposto ("not thirty-two
independent **bodies**"), e foi lida no sentido de malha: a segunda passagem da
LOOKS-TASK-14 concluiu dali "**Dois blocos de 32 cabeças**", que a terceira
passagem teve de desfazer.

## Evidência

Script próprio sobre `roms/japanese-shift-jis.bin`, comparando os arrays de
vértices em vez dos bytes da seção:

```text
run 24..55: 32 distinct section blob(s), 12 distinct vertex arra(ys)
run 74..105: 32 distinct section blob(s), 24 distinct vertex arra(ys)
pairs=16 differ=91 columns={(1, 1): 18, (1, 9): 32, (9, 9): 41};
    pairs sharing the vertex array: 15
```

**Doze** malhas no primeiro bloco e **24** no segundo, não 32 e 32. Quinze dos
dezesseis pares compartilham o array de vértices byte a byte; só o par 32/33
não.

A segunda afirmação, a das janelas, medida do jeito que a própria task define
janela (as primitivas da folha de cabelo na coluna 1 do CLUT — é a leitura sob
a qual a 24 dá `v` 1..14 e a 52 dá `v` 8..126, os dois números que a task cita):

```text
run 1: 32 sections, 14 distinct column-1 hair windows
   None         [32, 33, 36, 37]
   (0, 14)      [25, 26, 27]
   (0, 15)      [42, 43]
   (1, 14)      [24]
   (2, 15)      [34, 35, 40, 41]
   (8, 126)     [52]
   ...
   (66, 79)     [38, 39, 46, 47]
```

**Catorze** janelas para 32 seções, e **quatro seções sem janela nenhuma**.
Pela leitura mais larga — todas as primitivas na folha, sem filtrar coluna —
são **22** distintas para 32 seções. Nenhuma das duas leituras dá 32.

A mesma frase está no Log da task:

```text
docs/tasks/looks/14-tabela-de-montagem.md:300
Cada uma das 32 do primeiro bloco tem janela própria na folha
```

## Causa raiz

`head_runs` conta blobs de seção e chama o resultado de "body", e a frase
"cada um com sua janela" foi escrita da mesma contagem, sem comparar as
janelas entre si.

## Correção

### Arquivo: `tools/looks/assembly.py`

Trocar o rótulo impresso por aquilo que a contagem é — `32 byte-distinct
section(s)` —, e, se a malha interessa (interessa: é o que separa 32 cabeças de
dezesseis pares), acrescentar a contagem de arrays de vértices distintos ao
lado, com asserção no `--check-image`: 12 e 24.

### Arquivo: `tools/looks/layout.py`

Reescrever o primeiro parágrafo do `HEAD_RUNS` para o que está medido: 32
seções byte a byte distintas por bloco, **doze** malhas no primeiro e 24 no
segundo, e quinze dos dezesseis pares partilhando o array de vértices — que é
o que torna o último parágrafo verdadeiro em vez de contraditório. Trocar
"each with its own window" pelas 14 janelas sobre 28 seções, com as quatro sem
janela nomeadas (32, 33, 36 e 37).

### Arquivo: `docs/tasks/looks/14-tabela-de-montagem.md`

A linha da segunda passagem é registro histórico do raciocínio e fica — mas a
afirmação de janela própria é factual e está errada; corrigir no lugar, com a
medição ao lado, como manda o perfil ("o plano se corrige na seção que muda").

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/layout.py` | modificar |
| `tools/looks/assembly.py` | modificar |
| `docs/tasks/looks/14-tabela-de-montagem.md` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar, se a §6(c) repetir o número |

## Verificação

- [x] `python tools/looks/assembly.py --check-image` imprime blobs e malhas
      separados, e afirma 12 e 24
- [x] `python tools/looks/assembly.py --check` verde
- [x] `python tools/looks/selftest.py --quiet` verde, 33 de 33 controles
      vermelhos
- [x] nenhuma frase restante diz "every body distinct" ou "janela própria" —
      as duas transcrições que sobram estão dentro de bloco de saída da
      segunda passagem, com a nota de correção ao lado
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

As duas medições reproduzem, e as duas contrariam o docstring:

```text
run 24..55:  32 distinct section blob(s), 12 distinct vertex arra(ys)
run 74..105: 32 distinct section blob(s), 24 distinct vertex arra(ys)
run 1: 32 sections, 14 distinct column-1 hair windows
```

O conserto começou onde a palavra nasceu. O `head_runs` contava
`bytes(data[offset:end])` e chamava aquilo de `body`; agora conta as duas
coisas e imprime as duas, com o nome de cada uma:

```text
MODEL.BIN sections 24..55: 32 byte-distinct section(s) but only 12 distinct
    mesh(es), 32 of them sampling the hair sheet
MODEL.BIN sections 74..105: 32 byte-distinct section(s) but only 24 distinct
    mesh(es), 16 of them sampling the hair sheet
and they take 14 distinct window(s) on the hair sheet, not 32: 32, 33, 36, 37
    take none at all
```

`HEAD_RUN_MESHES = (12, 24)`, `HEAD_RUN_WINDOWS = 14` e
`HEAD_RUN_NO_WINDOW = (32, 33, 36, 37)` são asserção do `--check-image`, não
prosa — é a mesma lição da CORR-LOOKS-026 uma linha adiante: o número que
decide alguma coisa vem de comando.

### A segunda afirmação era a mais cara

"Cada uma das 32 tem janela própria" não é erro de rótulo: é a frase que faria
alguém ler 32 janelas onde há **catorze**, com as 25, 26 e 27 dividindo uma e
quatro seções sem nenhuma. Ela sustentava, do outro lado, a leitura "dois
blocos de 32 cabeças" que a terceira passagem teve de desfazer — e o docstring
do `HEAD_RUNS` se contradizia dentro de si mesmo, dizendo "every body distinct"
no primeiro parágrafo e "sixteen pairs rather than 32 independent heads" no
último. Os dois parágrafos agora dizem a mesma coisa, que é a medida.

### Problemas encontrados

Nenhum. As duas transcrições que ainda dizem `distinct body(ies)` estão dentro
do bloco de saída da segunda passagem da task, que é **registro da corrida
daquele dia** — reescrever seria falsificar a evidência. Ganharam a nota de
correção ao lado, que é o precedente do ciclo.

### Arquivos criados/modificados

- `tools/looks/assembly.py` — `head_runs` com as duas contagens,
  `hair_windows()`, `HEAD_RUN_MESHES`, `HEAD_RUN_WINDOWS`,
  `HEAD_RUN_NO_WINDOW` e as asserções
- `tools/looks/layout.py` — o docstring do `HEAD_RUNS`, sem a contradição
- `docs/tasks/looks/14-tabela-de-montagem.md` — a nota ao lado da transcrição
  e a frase da janela corrigida no lugar
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-029.md` — este arquivo
