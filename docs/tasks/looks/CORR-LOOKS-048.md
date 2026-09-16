---
id: CORR-LOOKS-048
title: "Correção: ninguém leu o que as barbas `F` e `G` escrevem, e 28 jogadores do disco e 16 renders do corpus são recusados"
type: correção
category: engenharia-reversa
status: pendente
depends_on: ["CORR-LOOKS-046"]
---

# CORR-LOOKS-048: a tela da barba oferece sete, e a tabela sabe cinco

## Problema identificado

A [`CORR-LOOKS-044`](/docs/tasks/looks/CORR-LOOKS-044.md) separou os dois
números: a **tela** do `FACE` oferece **7** valores, andada letra a letra nos
dois slots, e a **tabela** sabe aplicar **5** — as faixas 0 a 4 dos dois quads
de barba da seção 24. `F` e `G` são recusados como "não medido", o que é
verdade e é honesto. Ela deixou aberta a segunda metade: **o que `F` e `G`
escrevem**.

O custo, medido no disco: **28** dos 1.449 jogadores têm barba `F` (25) ou `G`
(3) — **1,9%**. No corpus de terceiro, **16** dos 50 renders caem nessa
recusa, e são a maior parte das 19 que o `scene.py --corpus` conta; a
[`LOOKS-TASK-18`](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md) só
consegue confrontar 31 das 50 enquanto isso estiver aberto.

O que já se sabe descarta a leitura óbvia: **não é uma faixa 5 e 6** da mesma
folha. A [`CORR-LOOKS-038`](/docs/tasks/looks/CORR-LOOKS-038.md) mediu as
faixas de barba — a 0 é o rosto sem barba e as 1 a 4 amostram as entradas que
a cor de barba move —, e a folha não tem faixa de barba além da 4. Pode ser
outra seção, como o `HAIR` era, ou outro par de primitivas.

## Evidência

```text
$ python - (looks.records sobre /SELECT.BIN)
records: 1449
FACE F or G (refused, not measured): 28 (1.9%)
  by value: {'A': 1326, 'C': 55, 'B': 34, 'F': 25, 'E': 6, 'G': 3}

$ python tools/looks/scene.py --corpus <os 50 JPGs>
      31 drawn, 19 refused
      13 x FACE=F is value 5: the screen offers it
       3 x FACE=G is value 6: the screen offers it

$ python tools/looks/confront.py --reach FACE
  FACE on slot 2: … the screen reaches 7 of the 8 value(s) the field holds
  FACE on slot 1: … the screen reaches 7 of the 8 value(s) the field holds
```

A mesma limitação de linha de comando da
[`CORR-LOOKS-047`](/docs/tasks/looks/CORR-LOOKS-047.md): o `--patched` não
recebe o slot.

## Causa raiz

A LOOKS-TASK-14 observou o `FACE` numa janela só — o `v` dos dois quads de
barba da seção 24 — e o que ela não viu mudar ali ficou sem leitura.

## Correção

### Medição

`python tools/looks/oracle.py --patched FACE <SLOT>` nos **dois** slots: andar
os sete valores lendo o arquivo carregado inteiro depois de cada tecla. O que
`F` e `G` mudarem — outra seção, outras primitivas, outra folha — sai da
corrida, não de dedução. Se a corrida disser que `F` e `G` **não mudam nada**
no arquivo, isso também é resposta, e a recusa passa a dizer isso.

### Arquivo: `tools/looks/assembly.py`

O `Effect` do `FACE` ganha o que a medição disser para `F` e `G`, e o `known`
sobe para o que ela alcançar. Se for outra seção, o `FACE` deixa de ser só
`BAND` e passa a escolher como o `HAIR` escolhe; se forem outras primitivas, o
`where` cresce.

### Arquivo: `tools/looks/scene.py`

A varredura de faixas da CORR-LOOKS-038 anda o `known`; se `F` e `G` não forem
faixa, ela tem de continuar andando só as faixas, e dizer isso.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/oracle.py` | o slot no `--patched`, se a CORR-LOOKS-047 ainda não o fez |
| `tools/looks/assembly.py` | modificar |
| `tools/looks/scene.py` | modificar, conforme o desfecho |
| `tools/looks/controls.py` | um controle que devolva `F`/`G` à recusa |
| `docs/PLAN-LOOKS-PY.md` | a tabela da §6(c) e o item 3 da definição de pronto |
| `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md` | o número de recusas remedido |

## Verificação

- [ ] `oracle.py --patched FACE` rodado nos dois slots, a saída no Log
- [ ] `F` e `G` desenham com o que escrevem medido — ou a recusa diz, medido,
      que não escrevem nada no arquivo
- [ ] `scene.py --corpus` remedido, e o número novo escrito onde o 31/19 está
- [ ] os 28 do disco remedidos pelo mesmo critério
- [ ] controle negativo vermelho
- [ ] `python tools/looks/selftest.py --quiet` verde
- [ ] `roms/` intocada, e os dois save states não sobrescritos

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
