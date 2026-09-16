---
id: CORR-LOOKS-030
title: "Correção: a treze seções de cabelo faltou uma na lista — o `E2` e a seção 54 não aparecem em lugar nenhum"
type: correção
category: engenharia-reversa
status: pendente
depends_on: []
---

# CORR-LOOKS-030: a décima terceira seção do mapa de cabelo não está escrita

## Problema identificado

Três lugares afirmam que o `HAIR_MAP` nomeia **treze** seções, e os três
enumeram **doze**:

| onde | o que enumera |
|---|---|
| `docs/PLAN-LOOKS-PY.md` §6(c) | "A é a 24, B a 26, C a 30, D a 48, F a 52, G a 28, I a 34, J a 36, K a 32, L a 46, O a 44 e P a 50" |
| `tools/looks/layout.py`, `HEAD_RUNS` | a mesma lista de doze |
| `docs/tasks/looks/14-tabela-de-montagem.md`, critério | a mesma lista de doze |

A que falta é a **54**, que é do `E2`. Ela não aparece em nenhuma das três
listas, e a letra `E` não aparece em nenhuma delas — só de passagem, e por
outro motivo: "o `E1` é uma quarta esquisitice: ele reescreveu a seção do `D`,
o que **pode ser o jogo devolvendo a cabeça do `D` em vez de nomear a dele**".

Essa leitura fica ao lado de uma medição que ninguém escreveu: o `E` **tem**
seção própria, a 54, nomeada pelo `E2`. O que o `E1` faz continua estranho,
mas a hipótese de que o `E` não foi nomeado é a que o próprio mapa desmente.

E o "par de treses" — três estilos mudos, três seções pares nunca nomeadas
(38, 40, 42) — **só fecha com a 54 contada como nomeada**: as seções pares do
bloco 24..55 são dezesseis, e 16 − 13 = 3. Pela lista escrita, de doze, as não
nomeadas seriam quatro (38, 40, 42 e 54), e a simetria que os três documentos
chamam de sugestiva desapareceria.

## Evidência

O mapa, lido do módulo e cruzado com `looks.HAIR_STYLES`:

```text
distinct sections: 13
  24 ['A1', 'A2', 'A3']
  26 ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']
  28 ['G1']
  30 ['C1', 'C2']
  32 ['K1']
  34 ['I1', 'I2', 'I3']
  36 ['J1']
  44 ['O1']
  46 ['L1', 'L2', 'L3']
  48 ['D1', 'D2', 'E1']
  50 ['P1']
  52 ['F1', 'F2', 'F3']
  54 ['E2']
NONE at 19 H1 / 28 M1 / 29 N1
```

`assembly.HAIR_MAP_SECTIONS = 13` está certo, e é conferido no `--check-image`.
O que falta é a linha `E` nas três prosas, e o reconhecimento de que a letra
`E` é a única partida em duas seções — 48 com o `D` e 54 sozinha.

## Causa raiz

A lista de letras foi escrita a partir das seções que cada família rotulava
por inteiro, e o `E`, que se parte em duas, ficou fora das duas contagens.

## Correção

### Arquivo: `docs/PLAN-LOOKS-PY.md` (§6(c))

Acrescentar `E` à enumeração, dizendo o que ela é: **`E1` cai na 48, que é do
`D`, e `E2` na 54, que é só dela** — treze seções, doze letras inteiras e uma
partida. E reescrever a frase do `E1`: a dúvida é por que o `E1` usa a seção do
`D`, não se o `E` tem seção.

### Arquivo: `tools/looks/layout.py`

A mesma correção no docstring do `HEAD_RUNS`, que repete a lista.

### Arquivo: `tools/looks/assembly.py`

O docstring do `HAIR_MAP` diz "every one of those letters' variants rewrites
that same section" — verdadeiro para as doze e falso para o `E`. Nomear a
exceção ali, que é onde o leitor do mapa está.

### Arquivo: `docs/tasks/looks/14-tabela-de-montagem.md`

O critério repete a lista de doze; acrescentar o `E` e a 54.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `tools/looks/layout.py` | modificar |
| `tools/looks/assembly.py` | modificar |
| `docs/tasks/looks/14-tabela-de-montagem.md` | modificar |

## Verificação

- [ ] as três listas têm treze seções, e a aritmética 16 − 13 = 3 aparece ao
      lado do "par de treses"
- [ ] `python tools/looks/assembly.py --check` verde
      (`HAIR_MAP_SECTIONS` segue 13)
- [ ] `python tools/looks/selftest.py --quiet` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
