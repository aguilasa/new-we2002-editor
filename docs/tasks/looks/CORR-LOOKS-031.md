---
id: CORR-LOOKS-031
title: "Correção: a constante `AGREEMENT` justifica o piso com 0,005 e a medição dá 0,008"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-LOOKS-031: o número que justifica o piso do corpus não é o número medido

## Problema identificado

O piso do cross-check do corpus é `AGREEMENT = 0.8`, e o docstring diz por que
não é 1,0:

```python
# tools/looks/assembly.py
AGREEMENT = 0.8
"""...
Not 1.0, and the reason is measured: HAIR and H.COL sit at 0.25 and 0.44 of the
head on the disc and their renders change within 0.005 of each other, so which
of the two is higher is inside the noise of both.
"""
```

A distância medida entre as duas é **0,008**, não 0,005 — e é 0,008 o que o
plano e o Log da task escrevem. O docstring é o único dos três que carrega o
outro número, e é justamente ele que sustenta a escolha do piso.

Importa porque o piso não tem folga: com quatro linhas, o rho de Spearman só
assume 1,0, 0,8, 0,6 … — 0,8 é exatamente **uma** inversão entre vizinhas, e é
o valor que a corrida entrega. O argumento de que a inversão está dentro do
ruído é o que separa esse piso de um limiar calibrado no resultado; um
argumento assim se lê pelo número que traz.

## Evidência

```text
python tools/looks/assembly.py --corpus "<os 50 JPGs>"
      HAIR     the mesh puts it at 0.246 of the head, and the renders change at 0.361
      H.COL    the mesh puts it at 0.438 of the head, and the renders change at 0.353
      SKIN     the mesh puts it at 0.447 of the head, and the renders change at 0.576
      FACE     the mesh puts it at 0.710 of the head, and the renders change at 0.660
      the two orderings agree to rho = 0.80 (the floor is 0.80)
```

`0.361 − 0.353 = 0.008`. Duas corridas, o mesmo número.

Os outros dois lugares acertam:

```text
docs/PLAN-LOOKS-PY.md:  A única inversão é HAIR × H.COL, que na imagem distam 0,008
docs/tasks/looks/14-…:  que nos renders distam 0,008 — dentro do ruído
```

## Causa raiz

O número do docstring foi escrito à parte da corrida que o mede, e ficou 0,005
enquanto os dois documentos ficaram 0,008.

## Correção

### Arquivo: `tools/looks/assembly.py`

Trocar `0.005` por `0.008` no docstring de `AGREEMENT`, e — já que a frase é o
que impede o piso de parecer calibrado no resultado — dizer ali que, com quatro
linhas, 0,8 é o degrau imediatamente abaixo de 1,0, de modo que o piso tolera
exatamente uma inversão entre vizinhas e nada mais.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/assembly.py` | modificar |

## Verificação

- [x] `python tools/looks/assembly.py --corpus <pasta>` verde, e o número do
      docstring é a diferença que ele imprime — 0,361 − 0,353 = **0,008**
- [x] `python tools/looks/assembly.py --check` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

A corrida confirma o que o plano e o Log já diziam, e o docstring não:

```text
HAIR     the mesh puts it at 0.246 of the head, and the renders change at 0.361
H.COL    the mesh puts it at 0.438 of the head, and the renders change at 0.353
the two orderings agree to rho = 0.80 (the floor is 0.80)
```

`0,361 − 0,353 = 0,008`. O docstring agora **traz os dois números impressos** e
a diferença ao lado, em vez de um só valor arredondado por fora da corrida —
que é como o 0,005 apareceu.

### E a frase ganhou o que faltava para ela sustentar o piso

O argumento contra "limiar calibrado no resultado" precisa de duas metades, e
só uma estava escrita. A segunda entrou: com quatro linhas, o rho de Spearman
só assume 1,0, 0,8, 0,6 … — **0,8 é o degrau imediatamente abaixo de 1,0**, e
uma inversão entre vizinhas custa exatamente 0,2. O piso tolera **uma** e mais
nada; não é um número escolhido por caber.

### Problemas encontrados

Nenhum. Varredura por `0.005` em `docs/` e `tools/looks/`: os dois acertos que
sobram são de outro assunto — a deriva de célula do `oracle.py`, 0,005265 e
0,005682 —, e o terceiro é o texto da própria CORR no
`correcoes-progresso.md`, que é o registro do achado.

### Arquivos criados/modificados

- `tools/looks/assembly.py` — o docstring do `AGREEMENT`
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-031.md` — este arquivo
