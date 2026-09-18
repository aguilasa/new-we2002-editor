---
id: CORR-LOOKS-058
title: "Correção: o docstring do `layout.POSE_MATRIX` reparte as 40 paradas de um jeito que a ferramenta não reproduz"
type: correção
category: dados
status: pendente
depends_on: []
---

# CORR-LOOKS-058: 18 e 17 no módulo, 18 e 18 em toda corrida

## Problema identificado

A [`LOOKS-TASK-24`](/docs/tasks/looks/24-de-onde-vem-a-pose.md) mediu quais
`ctc2` carregam a matriz do GTE nesta tela: cinco rodam, e duas levam quase
tudo. O plano e o Log da task dizem **18 e 18 de 40 paradas**, com `x2`, `x1` e
`x1` para as outras três. O docstring do `layout.POSE_MATRIX` diz outra coisa:

```text
tools/looks/layout.py:1447
(18 and 17 of 40 stops, against 2, 2 and 1 for 0x80010E38, 0x8003C990 and
0x800407C0).
```

```text
docs/PLAN-LOOKS-PY.md:2571
>    (`0x8001229C`), 18 e 18 de 40 paradas.
```

As duas repartições somam 40, e só uma é a que o comando imprime. A diferença
não é de arredondamento: o docstring dá **17** ao `POSE_MATRIX_SECOND` e **2**
ao `0x80010E38`, e a ferramenta dá 18 e 1.

O `layout.py` é o módulo dos endereços, e é nele que se lê o que cada um
significa; quem comparar uma corrida sua com essa linha vê diferença onde não
há, e quem a citar propaga o número que a ferramenta não produz.

## Evidência

Rodado hoje, na árvore de `8a32160`, nos dois slots da mesma corrida:

```text
$ python tools/looks/oracle.py --pose
  -- slot 1 (goalkeeper) --
    30 instruction(s) write the GTE's first matrix word; 5 run on this screen:
    0x80012168 x18, 0x8001229C x18, 0x8003C990 x2, 0x80010E38 x1, 0x800407C0 x1
  -- slot 2 (outfield player) --
    30 instruction(s) write the GTE's first matrix word; 5 run on this screen:
    0x80012168 x18, 0x8001229C x18, 0x8003C990 x2, 0x80010E38 x1, 0x800407C0 x1
oracle --pose: 0 problem(s)
```

O Log da própria task, na árvore de `0b2d087`, imprime a mesma linha — e o
plano a transcreve como "18 e 18". São três observações contra a do docstring.

## Causa raiz

O docstring foi escrito na corrida em que os cinco endereços foram achados, e a
contagem final — a que o comando passou a imprimir — entrou no plano e no Log,
não nele.

## Correção

### Arquivo: `tools/looks/layout.py`

O parágrafo do `POSE_MATRIX` passa a dizer a repartição que o `--pose` imprime
(18, 18, 2, 1, 1 de 40), **ou** diz que a repartição varia entre corridas e cita
a corrida de onde saiu — como a armadilha 43 do perfil já faz com a contagem de
paradas antes de a sequência repetir. Uma das duas; hoje a linha é um número
fixo que a ferramenta não reproduz.

Se a escolha for a primeira, vale conferir numa segunda corrida antes de fixar:
duas corridas deram o mesmo hoje, em dois slots.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/layout.py` | modificar |

## Verificação

- [ ] `python tools/looks/oracle.py --pose` e o docstring dizem a mesma coisa,
      ou o docstring diz que a repartição varia e nomeia a corrida
- [ ] `python tools/looks/selftest.py --quiet` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
