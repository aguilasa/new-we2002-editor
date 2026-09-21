---
id: CORR-LOOKS-021
title: "Correção: \"mesma malha, uniforme diferente\" não vale para quatro das onze peças, e o tronco está do lado errado da conta"
type: correção
category: engenharia-reversa
status: done
depends_on: []
origin: LOOKS-TASK-09
severity: medium
done_on: 2026-09-15
done_commit: e674f10
---

# CORR-LOOKS-021: o resumo do goleiro contra o jogador de linha diz o contrário do que o arquivo diz

## Problema identificado

O último item de "O que cada campo faz" fecha a comparação entre os dois bonecos
assim:

> **Goleiro contra jogador de linha:** as peças de tamanho igual entre os dois
> bonecos (coxa, perna, pé) e as de tamanho diferente (tronco, braço,
> antebraço) se separam sozinhas — e as que diferem, diferem **só** em `u`, `v`
> e CLUT, mais dois bytes de vértice. Mesma malha, uniforme diferente.

Três coisas erradas, e a terceira é a que custa:

1. **O tronco está do lado errado.** As seções 0 e 11 têm o **mesmo** tamanho:
   `84/71` vértices e primitivas nas duas, 2.384 bytes nas duas, e extensão
   `108, 150, 76` nas duas. Quem diz isso primeiro é a tabela da **§1.5 do
   próprio plano**, que a task acabou de atualizar. As peças de tamanho
   diferente são **duas**, não três: braço e antebraço.
2. **"Mais dois bytes de vértice" vale só para o tronco.** Medido seção contra
   seção: o tronco difere em **2** bytes de vértice, as coxas em **22**, e as
   pernas em **zero**. Um número que descreve uma das três aparece como se
   descrevesse as três.
3. **E por isso "mesma malha, uniforme diferente" não se sustenta para quatro
   das onze peças.** Braço e antebraço têm **contagem de vértice diferente** nos
   dois bonecos — 30/24 contra 40/34, e 80/78 contra 88/86 —, o que é malha
   diferente pela definição mais forte que existe. As coxas diferem em 22 bytes
   de vértice. Só a perna e o pé são de fato a mesma malha.

A frase importa adiante porque é dela que sai a decisão de montagem: um
renderizador que leia "mesma malha, uniforme diferente" carrega **uma** malha e
troca paleta e UV, e vai desenhar o goleiro com o braço do jogador de linha. A
[`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md) e a
[`LOOKS-TASK-15`](/docs/tasks/looks/15-visualizador-opengl.md) são as duas que
leriam isso.

**O que a medição de fato mostra é mais interessante que a frase**, e é o que
devia estar escrito: as peças que o goleiro tem **maiores** são exatamente as do
braço — manga comprida —, e as pernas são byte a byte a mesma malha guardada
duas vezes. Isto é, o segundo modelo não é um remapeamento de textura do
primeiro: ele é o mesmo esqueleto com **duas peças remodeladas** e o resto
copiado.

*(O pé não entra na comparação por par: as seções 9 e 10 são **compartilhadas**
pelas duas listas, então não há dois bytes a comparar — é literalmente a mesma
seção.)*

## Evidência

Contagens, do `pieces.py --check-image` e da tabela da §1.5, que concordam:

```text
  pos 0   lista A 216    84/71   |  lista B 19.440  84/71     <- tronco, IGUAL
  pos 1   lista A 2.608  30/24   |  lista B 21.832  40/34     <- braço, diferente
  pos 2   lista A 4.272  80/78   |  lista B 24.136  88/86     <- antebraço, diferente
  pos 5   lista A 9.328  72/59   |  lista B 29.704  72/59     <- coxa, igual
  pos 6   lista A 13.352 40/35   |  lista B 33.720  40/35     <- perna, igual
  pos 7   lista A 15.704 63/56   |  lista B 15.704  63/56     <- pé, a MESMA seção
```

Comparação byte a byte das seções correspondentes, feita nesta revisão sobre o
disco japonês:

```text
   0 vs 11: 505 of 2384 differ  {u: 65+65+65+65, v: 29+28+28+28, CLUT: 130,
                                 vertex byte 2: 2}
   1 vs 12: different size 824 vs 1144
   2 vs 13: different size 824 vs 1144
   3 vs 14: different size 2520 vs 2776
   4 vs 15: different size 2520 vs 2776
   5 vs 16: 250 of 2000 differ  {u: 38x4, CLUT: 76, vertex byte 2: 22}
   6 vs 17: 250 of 2000 differ  {u: 38x4, CLUT: 76, vertex byte 2: 22}
   7 vs 18: 240 of 1168 differ  {u: 24x4, v: 24x4, CLUT: 48, vertex: 0}
   8 vs 19: 240 of 1168 differ  {u: 24x4, v: 24x4, CLUT: 48, vertex: 0}
```

E o conjunto de vértices, que é o teste que o próprio `pieces.py` usa:

```text
identical vertex sets (no negation): [(7, 18), (8, 19)]
```

As pernas são idênticas vértice a vértice; as coxas não, apesar de dividirem a
caixa envolvente — que é justamente o argumento que o `mirror_axis()` escreve no
docstring, aqui com um caso real do arquivo.

## Causa raiz

A frase generalizou para as onze peças o que foi observado numa: o tronco, que
difere em dois bytes de vértice — e ainda o pôs no grupo das de tamanho
diferente, contra a tabela que a mesma task escreveu no plano.

## Correção

### Arquivo: `docs/tasks/looks/09-nomear-as-onze-pecas.md`

Reescrever o item, com os números medidos: duas peças de tamanho diferente
(braço e antebraço), tronco e coxa iguais em tamanho e diferentes em alguns
vértices (2 e 22 bytes), perna idêntica, pé compartilhado. E a leitura que sai
daí no lugar da que está: **o segundo modelo é o mesmo esqueleto com duas peças
remodeladas**, não um remapeamento de textura do primeiro.

### Arquivo: `docs/PLAN-LOOKS-PY.md`

A §1.5 tem a tabela e as "quatro leituras"; a comparação entre os dois bonecos
entra ali, onde quem for escrever montagem vai ler — hoje a §1.5 diz que as duas
listas têm a mesma **forma**, o que é verdade, e não diz que duas das peças têm
malha diferente.

### Arquivo: `docs/tasks/looks/14-tabela-de-montagem.md`

O contexto dela recebeu da task o padrão *"a peça nunca é trocada"*. Vale a
ressalva ao lado: dentro de um boneco a peça não é trocada por campo de LOOKS,
**mas os dois bonecos não compartilham a peça de braço** — quem monta escolhe a
lista primeiro.

### Como conferir sem acreditar

O confronto entre as seções correspondentes das duas listas é uma conta de
disco, sem emulador. Se ele nascer como asserção no `pieces.py` — quais pares
têm contagem igual, quantos bytes de vértice diferem, e em quais bytes da
primitiva — a frase deixa de poder envelhecer sozinha, que é o que aconteceu com
esta.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/looks/09-nomear-as-onze-pecas.md` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `docs/tasks/looks/14-tabela-de-montagem.md` | modificar |
| `tools/looks/pieces.py` | modificar |

## Verificação

- [x] o item do Log não põe mais o tronco entre as peças de tamanho diferente
- [x] os três números aparecem separados: 2 bytes de vértice no tronco, 22 na
      coxa, 0 na perna
- [x] "mesma malha, uniforme diferente" só é dito das peças de que é verdade —
      a perna e o pé
- [x] a §1.5 registra que braço e antebraço têm malha diferente entre os dois
      bonecos, e o "três dos cinco pares" dela virou **dois**
- [x] a comparação virou asserção: `pieces.py --check-image` a imprime, o
      `mesh_agrees()` a confere contra os nomes, e há três casos vermelhos no
      `--check` mais o controle `pieces-mesh-check-blind`
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-15

### Resumo do que foi feito

A frase virou **conta**. O `pieces.py` ganhou `compare_lists()`, que percorre as
duas listas posição a posição e devolve, por posição, as duas seções, se são a
mesma, se os tamanhos batem e — quando batem — quantos bytes diferem e quantos
deles são de **vértice** e não de textura. O `say_comparison()` imprime, e o
`--check-image` mostra:

```text
  the two figures, one list against the other:
      pos  0:  0 vs 11  same size, 505 of 2384 byte(s) differ, 2 of them vertex
      pos  1:  1 vs 12  DIFFERENT MESH  30/24 vs 40/34 vert/prim, 824 vs 1144 byte(s)
      pos  2:  3 vs 14  DIFFERENT MESH  80/78 vs 88/86 vert/prim, 2520 vs 2776 byte(s)
      pos  3:  2 vs 13  DIFFERENT MESH  30/24 vs 40/34 vert/prim, 824 vs 1144 byte(s)
      pos  4:  4 vs 15  DIFFERENT MESH  80/78 vs 88/86 vert/prim, 2520 vs 2776 byte(s)
      pos  5:  5 vs 16  same size, 250 of 2000 byte(s) differ, 22 of them vertex
      pos  6:  7 vs 18  same size, 240 of 1168 byte(s) differ, 0 of them vertex
      pos  7: section 9 is SHARED by both lists
      pos  8:  6 vs 17  same size, 250 of 2000 byte(s) differ, 22 of them vertex
      pos  9:  8 vs 19  same size, 240 of 1168 byte(s) differ, 0 of them vertex
      pos 10: section 10 is SHARED by both lists
```

**O tronco tem o mesmo tamanho** e difere em **2** bytes de vértice; a coxa em
**22**; a perna em **zero**; braço e antebraço são **malha diferente**; o pé é
literalmente a mesma seção. Os três números que a frase fundia agora aparecem
separados, e cada um sai de comando.

E a conta **confere contra os nomes**, que é o que a torna asserção e não
relatório: o `mesh_agrees()` exige que as peças de malha diferente sejam
exatamente a cadeia do braço — manga comprida contra manga curta — e que
nenhuma peça do braço tenha malha igual. As duas medições são independentes (a
nomeação vem do espelho, da cadeia e do emulador; esta vem dos bytes), então
uma passa a poder derrubar a outra.

### O que mudou nos documentos

- **LOOKS-TASK-09** — o item reescrito como tabela medida, com a leitura no
  lugar da frase: *o segundo boneco é o mesmo esqueleto com duas peças
  remodeladas*, não um remapeamento de textura do primeiro.
- **§1.5 do plano** — a comparação entrou onde quem escrever montagem vai ler.
  E uma discrepância que a varredura puxou: a seção dizia que **três** dos cinco
  pares mudam de contagem entre as listas; são **dois** — a própria tabela ao
  lado já dizia, e o número nunca tinha sido conferido contra ela.
- **LOOKS-TASK-14** — a ressalva ao lado do padrão *"a peça nunca é trocada"*:
  vale dentro de um boneco, e os dois não compartilham o braço. Quem monta
  escolhe a lista primeiro.

### Problemas encontrados

**Uma colisão de controle, do tipo que a LOOKS-TASK-06 já tinha pago.** O
`mesh_agrees()` nasceu abrindo com `problems = []`, que é exatamente a linha que
o controle `pieces-witness-blind` substitui — e a substituição passou a casar
**duas** vezes, o que é controle **quebrado**, não vermelho. O `--check` do
catálogo pegou antes de qualquer sandbox, e o conserto é o mesmo de lá: grafia
própria, `disagreements = []`, com o motivo no docstring.

### Arquivos criados/modificados

- `tools/looks/pieces.py` — `compare_lists()`, `mesh_agrees()`,
  `say_comparison()`; a comparação no `report()` e a asserção no
  `_check_image()`; três casos vermelhos novos no `self_check()`
- `tools/looks/controls.py` — o controle `pieces-mesh-check-blind`
- `docs/tasks/looks/09-nomear-as-onze-pecas.md` — o item reescrito
- `docs/PLAN-LOOKS-PY.md` — §1.5, a comparação e o "dois dos cinco pares"
- `docs/tasks/looks/14-tabela-de-montagem.md` — a ressalva
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-021.md` — este arquivo
