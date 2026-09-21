---
id: CORR-LOOKS-062
title: "Correção: a segunda chuteira é posta por espelho em z, cai a 258 unidades da própria canela, e nenhum gate pode ver isso"
type: correção
category: render
status: done
depends_on: []
origin: LOOKS-TASK-27
severity: medium
done_on: 2026-09-18
done_commit: c264779
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

## Log de Execução

**Executado em:** 2026-09-18

**Resumo do que foi feito**

A evidência bate inteira — `foot b` em `(-54, 12, 215)` contra `foot a` em
`(-54, 12, -215)`, a 258 unidades da própria canela, e o `--check-image` verde
—, mas **a causa é outra e maior**: o `ANIME.BIN` não carrega onze pares para
doze seções desenhadas. Carrega **doze**, e o par que faltava é o que estava
sendo lido como uma **raiz** que não desenha nada. Ele é a chuteira `b`.

A medição que o item 1 da Correção pedia foi feita, e **sem precisar de
watchpoint novo**: o que nomeia a peça é a junta rígida que já decidiu o atraso
de desenho. Três leituras, e nenhuma delas é "o desenho ficou melhor":

1. **No arquivo, sobre os dezessete quadros da caminhada.** A origem do par 12
   no referencial da canela `b` fica em `(0,2, 69,1, −2,2)` com dispersão
   máxima **5,6** — o mesmo tornozelo que a canela `a` segura a
   `(0,3, 68,2, 3,3)` com **5,1**. Contra a canela errada dá 356, e contra o
   tronco 229. Uma raiz não fica pendurada na canela que balança.
2. **Nas capturas, pelo instrumento do ciclo.** `oracle.py --pose-lag`, com o
   par novo no `LAG_CHAIN`: no atraso vencedor, `shin b → foot b` dá **4,8**
   (slot 1) e **4,3** (slot 2), contra **356,8** e **328,3** da canela errada.
   E a rotação dessa parada **balança 4362** ao longo dos oito quadros,
   acompanhando os 4074 da canela `b` — a linha que ela substitui dizia que
   essa matriz era "a da câmera a menos de uma volta pequena", e a da câmera é
   constante; quem quase não se mexe é o tronco, com 185.
3. **A aritmética fecha.** Doze cargas por passada, doze seções desenhadas, e a
   única seção que captura nenhuma nomeia é a **10**. O ponteiro não a nomeia
   porque cada carga é nomeada pelo ponteiro da parada **seguinte**, e a
   primeira parada de uma passada vem com os três registradores zerados.

Com isso, os três itens da Correção viraram:

- **item 1 — medido**, e a chuteira `b` deixou de ser posta: ela tem lugar
  próprio, que é a origem contra a qual todos os outros lugares são medidos.
  Depois do conserto ela cai a **23** unidades em `z` da própria canela, contra
  as 276,5 do espelho e as 41 da chuteira `a`.
- **item 2 — sem objeto**: não há mais nada inventado para anotar.
- **item 3 — feito, e maior.** A cadeia `b` inteira entrou no `CHAINS`
  (`torso → thigh b → shin b → foot b`, e `upper arm b → forearm b`), e a
  conferência em `z` **não** é entre as duas chuteiras: as duas de uma passada
  ficam legitimamente a até 219 uma da outra, porque é isso que uma passada é,
  então limiar entre elas só pode ser vazio. Quem tem faixa estreita é o
  **tornozelo** — 41,3 e 59,1 nos dezessete quadros —, e é ele que o
  `ANKLE_DEEP = 90` guarda.

O `SIDES_APART` subiu de **45** para **55**: o par mais aberto da caminhada é o
das chuteiras, a **36,7**, e ele aparecia como **0** justamente porque o espelho
em `z` preserva `y` — a medição antiga media a mesma peça duas vezes.

E o `--check-image` passou a medir **um boneco de cada vez**. As duas listas do
`EDT_MOD.BIN` nomeiam as seções em lugares diferentes (o tronco do jogador de
linha é a seção 0 e o do goleiro a 11), os dois se chamam `torso` aqui, e um
dicionário só guardava o último — afirmando uma figura que não é nenhuma das
duas. As chuteiras são compartilhadas, então é exatamente aí que isso importa.

**Problemas encontrados**

1. **A `--poses` precisou ser recapturada ao vivo**, e não por capricho: o nome
   do par 12 vem do instrumento, e captura antiga traz `root`. Recapturadas as
   16, o `--poses` imprime `11 foot b`, `section 10 (foot b) read 2 time(s)` e
   `0 problem(s) over 8 frame(s) and 2 slot(s)`.
2. **A hierarquia que o `--poses` imprime estava com os nomes um elo fora** —
   herança da nomeação de antes do atraso de desenho, que só foi corrigida no
   fim do dia. Os números não mudaram; os nomes, sim: o que se lia
   "raiz↔cabeça (14,5x)" é **cabeça↔tronco**, e as duas "canela↔coxa" são
   **chuteira↔canela**. Com os nomes certos, o teto de fora dos cinco pares
   passou de **2,5x** para **3,3x** (o tronco, no slot 1), o que reescreve o
   número que a [`CORR-LOOKS-060`](/docs/tasks/looks/CORR-LOOKS-060.md) tinha
   acabado de corrigir — em quatro lugares.
3. **O próprio `--poses` imprimia a conclusão velha** ("section 10 is READ and
   carries no matrix load of its own, so a piece can be drawn without one").
   Frase de ferramenta é documento: foi reescrita para dizer o que a corrida
   mede — que a seção é lida e que **nenhuma carga a nomeia**.

**Arquivos criados/modificados**

- `tools/looks/anime.py` — `PIECE_ORDER` (o par 12), `WORD_OF_BOOT_PLACE`, e as
  três medições no docstring
- `tools/looks/scene.py` — `REFERENCE_PIECE`, `pose()` sem espelho,
  `_mirrored_in_z()` removido, `CHAINS` com o lado `b`, `SIDES_APART = 55`,
  `ANKLE_DEEP`, `standing(middles, depths)`, `_figure_sections()`, o
  `--check-image` por figura, e cinco casos novos no `self_check`
- `tools/looks/oracle.py` — `UNPOINTED_PIECE`, o `LAG_CHAIN` com os dois
  tornozelos e os dois controles, e a frase do relatório
- `tools/looks/controls.py` — controle `scene-boot-may-hang-off-another-leg`
- `docs/PLAN-LOOKS-PY.md`, `docs/prompts/perfil-looks.md`, `CLAUDE.md`,
  `docs/tasks/looks/25-a-pose-de-referencia.md`,
  `docs/tasks/looks/26-o-formato-do-anime-bin.md`,
  `docs/tasks/looks/27-o-boneco-montado.md` — o que dizia "raiz", "onze pares"
  ou "desenhada sem carga de matriz própria"
