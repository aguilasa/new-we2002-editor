---
id: CORR-LOOKS-062
title: "Correção: a segunda chuteira é posta por espelho em z, cai a 258 unidades da própria canela, e nenhum gate pode ver isso"
type: correção
category: render
status: pendente
depends_on: []
---

# CORR-LOOKS-062: o pé que a task ia medir saiu espelhado, e a asserção que o cobriria é vazia

## Problema identificado

O Contexto da [`LOOKS-TASK-27`](/docs/tasks/looks/27-o-boneco-montado.md) diz,
com todas as letras, o que esta task tinha de responder:

```text
- a tela desenha DUAS chuteiras e só UMA carrega matriz ... Uma montagem que
  espere uma matriz por peça desenhada deixa um pé para trás ou o põe no lugar
  errado -- **medir onde a segunda chuteira cai é desta task**, e a captura da
  25 não a nomeia;
```

Ela não foi medida. O `scene.pose()` **põe** a segunda chuteira espelhando a
primeira em `z`, e o docstring é honesto sobre isso — *"The one piece whose
place is NOT measured is the second boot … placed by mirroring its partner in
z"*. O que falta é o resto: o resultado está **errado no desenho**, o critério
de conclusão não registra a pendência, e a única asserção que tocaria nela não
pode reprovar.

**Onde a chuteira cai.** No quadro 0, em unidades do arquivo:

```text
foot a   place (-54, 12, -215)      shin a  place (-54, -55, -197)
foot b   place (-54, 12,  215)      shin b  place (  1, -51,  -43)
```

A chuteira `a` fica a `(0, 67, −18)` da própria canela; a `b`, a
`(−55, 63, **258**)` da dela. O espelho troca o sinal de `z` **da raiz**, não a
relação com a perna — e as duas pernas estão em pontos diferentes da passada,
que é justamente quando espelhar não vale.

**A asserção que cobriria isso é vazia por construção.** O
`scene.standing()` percorre uma cadeia que só nomeia o lado `a`
(`CHAINS = (("head", "torso", "thigh a", "shin a", "foot a"), …)`), e o par
`a`/`b` é conferido por **`y`** contra `SIDES_APART`. O espelho preserva `y`,
então a chuteira espelhada passa sempre — e o próprio docstring do
`SIDES_APART` registra *"the boots at 0"* como se fosse medição, quando é o
zero que o espelho garante.

## Evidência

Na árvore de `85ca349`, com a imagem japonesa:

```text
$ python - (scene.pose(disc, 0), place por peça)
shin a       ('/BIN/EDT_MOD.BIN', 7)    place=(-54, -55, -197)
foot a       ('/BIN/EDT_MOD.BIN', 9)    place=(-54,  12, -215)
shin b       ('/BIN/EDT_MOD.BIN', 8)    place=(  1, -51,  -43)
foot b       ('/BIN/EDT_MOD.BIN', 10)   place=(-54,  12,  215)
```

O desenho concorda com os números. Capturado hoje, fora da tela:

```text
$ work/venv-looks/Scripts/python.exe tools/looks/ui/app.py \
      --looks A-A1-A-A-A --frame 0 --screenshot <fora>
  textured, but placed by its mirror: 56
```

Na imagem de 640×640, a perna que está no ar **termina sem chuteira** — a
canela acaba num corte — e só a perna de apoio tem a sua. A nota do relatório
("placed by its mirror: 56") é a única coisa que diz que ali há uma peça posta
sem medida; ela não aparece em documento nenhum.

E o gate que deveria pegar não pega:

```text
$ python tools/looks/scene.py --check-image
      the figure, top down: head -386, torso -298, thigh a -162, shin a -53, foot a 13
      the figure, top down: upper arm a -301, forearm a -224
scene --check-image: ok
```

A ordem afirmada é a do lado `a`; a chuteira `b` não entra em nenhuma das duas
cadeias, e a conferência de par mede `y`, que o espelho copia.

## Causa raiz

O par que falta no `ANIME.BIN` foi resolvido pela simetria das **peças**
(`pieces.py` pareia por reflexão em z), e não pela pose: numa passada de
caminhada as duas pernas não são reflexo uma da outra.

## Correção

### Arquivo: `tools/looks/scene.py`, e quem medir

1. **Medir onde o jogo põe a segunda chuteira**, que é o que o Contexto pedia:
   ela é desenhada reaproveitando o que está no GTE, então a translação usada
   sai da mesma parada — a captura da pose já para em cada carga e pode
   registrar, na parada seguinte, a matriz **em vigor** quando a seção 10 é
   desenhada (`oracle.py --pose`, watchpoint de seção da LOOKS-TASK-25).
2. Enquanto não medido, a chuteira `b` **não se desenha inventada**: ou fica de
   fora com a nota visível (como o `shelf()` é honesto por ser prateleira), ou
   é posta pela relação medida da chuteira `a` com a **própria** canela, dita
   como aproximação — nunca por espelho da raiz.
3. **A asserção deixa de ser vazia:** a cadeia `b`
   (`thigh b → shin b → foot b`) entra no `standing()`, e o par de chuteiras
   passa a ser conferido **em z** também, com o limiar medido nos dezessete
   quadros como o `SIDES_APART` foi. O docstring do `SIDES_APART` deixa de
   citar "the boots at 0" como medição.

### Arquivos: `docs/tasks/looks/27-o-boneco-montado.md` e `docs/PLAN-LOOKS-PY.md` (§10.4)

Registrar a pendência onde ela é lida: a segunda chuteira está **posta, não
medida**, com o número (258 unidades da própria canela) e o que a destravaria.
Hoje o Log diz "cada um com as duas chuteiras" e nada diz que uma delas é
aproximação.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/scene.py` | modificar |
| `tools/looks/oracle.py` | modificar (a medição da seção sem carga) |
| `docs/tasks/looks/27-o-boneco-montado.md` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |

## Verificação

- [ ] a chuteira `b` cai a uma distância da canela `b` comparável à da `a`
      (hoje 258 contra 18), **ou** não é desenhada e o relatório diz por quê
- [ ] `scene.standing()` reprova uma chuteira `b` fora de lugar — com caso no
      `self_check()` que hoje passaria
- [ ] o par de chuteiras é conferido em `z`, com limiar medido nos dezessete
      quadros
- [ ] `python tools/looks/selftest.py --quiet` verde e `ui_check.py` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
