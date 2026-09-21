---
id: CORR-LOOKS-050
title: "Correção: o `corpus.py` julga a pele 47 de 47 com doze peles desenhadas erradas, e o erro que ele achou não o deixa vermelho"
type: correção
category: verificação
status: done
depends_on: []
origin: LOOKS-TASK-18
severity: medium
done_on: 2026-09-16
done_commit: a82f922
---

# CORR-LOOKS-050: o gate do corpus não fica vermelho no erro sistemático que existe para achar

## Problema identificado

O objetivo da LOOKS-TASK-18 é "usar o corpus para procurar erro sistemático",
e ela achou um: nas cabeças que não são `A1`, uma pele diferente de `A` pinta só
a testa e deixa o rosto na pele pálida — a
[`CORR-LOOKS-049`](/docs/tasks/looks/CORR-LOOKS-049.md), Alta, **pendente**.

A mesma corrida, com esse defeito presente, termina assim:

```text
the corpus, 47 picture(s), the best render agrees on: skin_colour 47/47, ...
corpus: ok
```

**Pele 47 de 47, com doze peles desenhadas erradas.** A leitura natural da
linha é "a pele sai certa em 47"; o que ela mede é outra coisa: se **o render
de maior nota** para cada JPEG tem a letra de pele do nome. Para `D-I3-A-A-A` o
nosso render da própria tupla tira 0,266, quem vence é `D-A1-A-A-A` — outra
cabeça, com a pele `D` inteira — e a letra `D` bate. Um render parcialmente
errado nunca reprova o campo, desde que **algum** render com a letra certa
vença; e um defeito de cor parcial, preso a um grupo de cabeças, é exatamente
o que a corrida achou.

Quem viu o erro não foi um julgamento: foi a tabela **impressa** de
autopontuação por grupo, lida por gente.

```text
hair style not A1 skin not A  12 picture(s), mean 0.411, lowest 0.266
```

Nada nela é asserção. E a verificação da própria CORR-049 depende dela —
"o grupo 'not A1 / not A' deixa de ser o outlier" —, então o conserto também
vai ser conferido lendo um número, e uma regressão depois dele volta verde.

## Evidência

Remedido na árvore de hoje (`a2f122f`), com os renders refeitos por `--run` e
depois só o `--score`, duas vezes: as três saídas são idênticas, e a CORR-049
continua `status: pendente`.

```text
$ python tools/looks/corpus.py --run <pasta>
      the corpus, 47 picture(s), the best render agrees on: skin_colour 47/47,
          hair_colour 47/47, beard_colour 26/26, hair_style 26/47 (reported),
          beard_style 23/47 (reported)
      self-score, grouped by head and skin:
        hair style A1     skin A       9 picture(s), mean 0.721, lowest 0.660
        hair style A1     skin not A  14 picture(s), mean 0.641, lowest 0.540
        hair style not A1 skin A      12 picture(s), mean 0.697, lowest 0.544
        hair style not A1 skin not A  12 picture(s), mean 0.411, lowest 0.266
      the 6 lowest self-scores:
        D-I3-A-A-A   own 0.266  best D-A1-A-A-A   0.553
        C-I3-A-C-A   own 0.312  best C-A1-A-A-A   0.671
        B-I3-A-A-A   own 0.316  best B-A1-A-A-A   0.730
        ...
corpus: ok
```

Nas seis piores o "best" é sempre a **cabeça `A1` com a pele certa** — é por
isso que a pele "concorda". E a tira `work/looks-corpus/worst.png`, olhada
nesta revisão, mostra o que o Log descreve: no JPEG o rosto inteiro na pele do
nome, no nosso só a faixa de cima.

## Causa raiz

O campo de cor é julgado pelo **rótulo do vencedor da linha**, que é uma
pergunta sobre a matriz, e o defeito é da **nota do próprio render**, que o
gate só imprime.

## Correção

### Arquivo: `tools/looks/corpus.py`

Julgar a autopontuação, não só imprimi-la, e sem escolher número à mão — que é
o que o módulo tem de melhor e deve manter. O controle que a task já tem serve
de régua: os quadros do emulador são tupla conhecida, e os grupos se comparam
**entre si**. Uma forma possível: um grupo cuja média fica abaixo da menor nota
do grupo de referência (`A1`/`A`, onde nada é emprestado) é outlier, e outlier
falha. Hoje isso dá 0,411 contra um piso de 0,660 — vermelho; os outros três
grupos, com médias de 0,641 a 0,721, ficam acima.

Enquanto a CORR-049 estiver aberta, o gate ficaria vermelho, e o caminho que
este ciclo já usa é nomear o resíduo — como o `confront.EXPECTED` fez com o
goleiro — **com a condição de que ele deixe de valer quando o grupo se
recuperar**: um resíduo esperado que continua isento depois do conserto é um
buraco com data.

E trocar a frase da linha de campo para dizer o que ela mede — "o render de
maior nota tem a letra certa" —, porque "agrees 47/47" é lido como pele certa
em 47.

### Arquivo: `docs/tasks/looks/CORR-LOOKS-049.md`

Trocar a primeira verificação por o gate que esta CORR cria, em vez de "o grupo
deixa de ser o outlier" lido na tela.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/corpus.py` | modificar |
| `tools/looks/controls.py` | modificar (um controle que desligue o julgamento do grupo) |
| `docs/tasks/looks/CORR-LOOKS-049.md` | modificar (a verificação) |
| `docs/PLAN-LOOKS-PY.md` | modificar, se a §5.4 descrever o veredito por campo |

## Verificação

- [x] `python tools/looks/corpus.py --score <pasta>` **vermelho** com o
      empréstimo de cor presente, ou verde só por resíduo nomeado que aponte a
      CORR-049
- [x] o resíduo deixa de isentar quando o grupo se recupera — com um caso no
      `self_check()` que prove isso sem os JPGs
- [x] o controle novo fica vermelho
- [x] `python tools/looks/selftest.py --quiet` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

A evidência reproduz na árvore de `faa9e1d`: `corpus.py --score` imprime
`skin_colour 47/47` e o grupo "not A1 / not A" com média 0,411, e fecha em
`corpus: ok`.

**O julgamento do grupo — e por que não é a forma sugerida.** A forma que esta
CORR propõe ("média abaixo da menor nota do grupo `A1`/`A`") não fecha com os
números que ela mesma cita: o piso seria **0,660**, e o grupo `A1`/pele não-`A`
tem média **0,641** — ficaria vermelho, num grupo onde nada é emprestado. A
frase "os outros três grupos, com médias de 0,641 a 0,721, ficam acima" está
errada por esse 0,641. A regra adotada também não escolhe número à mão:

> um grupo é **outlier** quando a **média** dele fica abaixo da **pior nota de
> todos os outros grupos** — a pior imagem de qualquer outro lugar, que já paga
> pose, câmera e JPEG. Grupo nomeado por resíduo não entra no piso dos outros.

Medido: "not A1 / not A" 0,411 contra 0,540 → outlier; os outros três passam
(pisos 0,266, 0,540 e 0,540, que viram 0,544, 0,540 e 0,540 sem o grupo do
resíduo).

- `corpus.py` — `GROUP_RESIDUES` com o grupo `(False, False)` apontando a
  CORR-LOOKS-049; `group_failures(grouped, residues)` devolve falhas e
  esperados; **o resíduo expira**: grupo nomeado que não é outlier (recuperado,
  ou fora do corpus) é falha, pedindo a remoção. A linha de campo passou a dizer
  "the best-scoring render carries the name's letter for", que é o que ela
  mede. Sete casos no `self_check()`, sem JPEG.
- `controls.py` — `corpus-groups-unjudged` (o grupo nunca vira outlier) e
  `corpus-residue-never-expires` (o resíduo isenta para sempre).
- `CORR-LOOKS-049.md` — a primeira verificação agora é este gate: verde **sem**
  o resíduo.
- `PLAN-LOOKS-PY.md` §5.4 — o que a linha de campo mede, e a regra do grupo.
- `18-corpus-dos-cinquenta-renders.md` — nota datada abaixo da transcrição.

### Gates

```text
$ python tools/looks/corpus.py --score        # com o resíduo
      the corpus, 47 picture(s), the best-scoring render carries the name's letter for: skin_colour 47/47, ...
      EXPECTED hair style not A1, skin not A: mean 0.411 under the floor 0.540 -- CORR-LOOKS-049: ...
corpus: ok

# o mesmo score com GROUP_RESIDUES = {}
      GROUP OUTLIER hair style not A1, skin not A: mean 0.411 is under 0.540, the lowest self-score of every other group, and no residue names it
corpus: 1 failure(s)

$ python tools/looks/corpus.py --check
corpus.py: 0 failure(s)
$ python tools/looks/controls.py --only corpus-groups-unjudged
  RED    corpus-groups-unjudged     corpus.py :: group_failures
$ python tools/looks/controls.py --only corpus-residue-never-expires
  RED    corpus-residue-never-expires corpus.py :: group_failures
$ python tools/looks/selftest.py --quiet
  ..... 59 of 59 controls red
looks_selftest: 0 failure(s)
```

`roms/` intocada (só leitura); os renders de `work/looks-corpus/` não foram
refeitos, só pontuados.

### Problemas encontrados

- A forma sugerida desta CORR ficaria vermelha no grupo `A1`/pele não-`A`
  (0,641 < 0,660) sem causa nenhuma; ver acima. A regra adotada é outra, e
  diz por quê.

### Arquivos criados/modificados

- `tools/looks/corpus.py`, `tools/looks/controls.py`
- `docs/tasks/looks/CORR-LOOKS-049.md` — a verificação
- `docs/PLAN-LOOKS-PY.md` — §5.4
- `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md` — a nota
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
