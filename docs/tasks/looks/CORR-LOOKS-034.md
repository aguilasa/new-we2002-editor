---
id: CORR-LOOKS-034
title: "Correção: nenhum campo de cor alcança a cabeça quando o cabelo não é da família A"
type: correção
category: núcleo
status: concluído
depends_on: []
---

# CORR-LOOKS-034: as quatro linhas de cor só pintam a seção 24

## Problema identificado

O `assembly.EFFECTS` endereça as quatro linhas de cor pela constante

```python
HEAD = (layout.MODEL, layout.HEAD_SECTION)      # (…/MODEL.BIN, 24)
```

e o `sections_of()` desenha **a cabeça que o `head_of()` nomeia**, que é a 24
só para os três estilos da família `A`. Para os outros 29 a chave do plano —
`(MODEL, 24)` — não casa com nenhuma seção desenhada, o `combine()` recebe um
dicionário vazio, e `SKIN`, `H.COL`, `H.F.COL.` e `FACE` **não fazem nada**.

O `HAIR` escapa porque o `draw_list` o aplica à seção escolhida
(`plan.setdefault((layout.MODEL, chosen), {})[quads] = …`); as outras quatro
ficaram na constante de antes de a LOOKS-TASK-14 medir que a linha **escolhe**
uma seção em vez de editar a 24.

O boneco desenha perfeitamente. Trocar a pele de um jogador de cabelo `I3` não
muda um pixel, e nada avisa.

## Evidência

Na tabela, os mesmos dois campos, duas famílias:

```text
python tools/looks/assembly.py --tuple A-A1-A-A-A   |  --tuple B-A1-A-A-A
    MODEL.BIN section 24 … palette (144, 480, 16)   |  … palette (144, 481, 16)
    MODEL.BIN section 24 … palette  (16, 480, 16)   |  … palette  (16, 481, 16)

python tools/looks/assembly.py --tuple A-I3-A-A-A   |  --tuple B-I3-A-A-A
    MODEL.BIN section 34 … palette (144, 480, 16)   |  … palette (144, 480, 16)
    MODEL.BIN section 34 … palette  (16, 480, 16)   |  … palette  (16, 480, 16)
```

Na tela, medido com o decodificador de PNG do `ui_check.py` — que não é o
`--compare` do `app.py`, e concorda com ele:

```text
família A (cabeça 24):
  A-A1-A-A-A vs B-A1-A-A-A   193050 (47.13%)
  A-A1-A-A-A vs A-A1-C-A-A    70336 (17.17%)
família I (cabeça 34):
  A-I3-A-A-A vs B-I3-A-A-A         0 (0.00%)     SKIN
  A-I3-A-A-A vs A-I3-C-A-A         0 (0.00%)     H.COL
  A-I3-A-A-A vs A-I3-A-E-A         0 (0.00%)     FACE
  A-I3-A-A-A vs A-I3-A-A-E         0 (0.00%)     H.F.COL.
```

Quatro linhas da tela, quatro quadros **byte a byte idênticos**. E não é efeito
do `--piece head`: com a figura inteira, `A-A1` contra `B-A1` move 0,32% dos
pixels e `A-I3` contra `B-I3` move **zero**.

**Por que nenhum gate viu.** O `scene.py --check-image` tem a asserção certa —
"uma cor de cabelo tem de mudar as superfícies" — e a faz sobre
`A-A1-A-A-A` contra `A-A1-C-A-A`: as duas da única família em que o código
funciona. A asserção vizinha, a da troca de cabeça, confere que `A-I3-A-A-A`
desenha outra seção e **não** que a cor ainda chega nela. Cruzar as duas é o
caso que faltava.

## Causa raiz

A LOOKS-TASK-14 ensinou a cabeça a mudar de seção e deixou as quatro linhas de
cor endereçadas à seção 24, que era a única cabeça quando elas foram medidas.

## Correção

### Arquivo: `tools/looks/assembly.py`

As quatro linhas de cor da cabeça têm de ser endereçadas à **cabeça que a tupla
desenha**, não a uma constante. O `HEAD` deixa de ser chave fixa no `EFFECTS`:
ou o `edits()` passa a receber a seção escolhida (`head_of(values)[0]`) e a
montar a chave com ela, ou o `draw_list` re-endereça o plano da cabeça depois
de escolher a seção, do mesmo jeito que já faz com a faixa do `HAIR`.

**Um cuidado que a medição impõe:** os índices de primitiva
(`SKIN_COLOUR_PRIMITIVES`, `HAIR_COLOUR_PRIMITIVES`, `FACE_PRIMITIVES`) foram
medidos **na seção 24**, e as treze cabeças não têm o mesmo número de
primitivas — a 34 desenha 23 onde a 24 desenha 18. Aplicar os mesmos índices às
outras doze é a suposição plausível que este ciclo recusa em outros lugares
(`HAIR_QUADS` cobre quatro cabeças de treze **por medição**, e o `head_of`
recusa três estilos em vez de inventá-los). Então o conserto honesto tem duas
metades, e a segunda pode ser outra task:

1. re-endereçar a chave para a seção desenhada, que é defeito puro e sem dúvida;
2. dizer **quais primitivas** de cada uma das treze cabeças cada linha move —
   medição de emulador, irmã da que a LOOKS-TASK-14 fez com o `--writes` — ou,
   enquanto não estiver medida, marcar o resultado como "cor não medida nesta
   cabeça" em vez de pintar por índice emprestado. O caminho existe: o
   `Scene.notes` já carrega `band unmeasured`.

### Arquivo: `tools/looks/scene.py`

No `_check_image`, cruzar os dois eixos: uma tupla que **troca a cabeça e a
cor** — `A-I3-A-A-A` contra `B-I3-A-A-A` — tem de diferir em superfícies, como
`A-A1-A-A-A` contra `A-A1-C-A-A` difere hoje. Sem esse caso o gate continua
cego para este defeito.

### Arquivo: `tools/looks/controls.py`

Um controle que devolva a chave à constante e exija o vermelho, para que o
conserto não possa voltar em silêncio.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/assembly.py` | modificar |
| `tools/looks/scene.py` | modificar |
| `tools/looks/controls.py` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar (§6(c): a chave e o que falta medir) |
| `docs/tasks/looks/17-confronto-com-o-emulador.md` | modificar, se a medição das primitivas por cabeça for de lá |

## Verificação

- [x] `python tools/looks/assembly.py --tuple B-I3-A-A-A` move a paleta da
      seção 34 **e** diz que a move por índice medido noutra cabeça
- [x] `python tools/looks/scene.py --check-image` verde, com o caso cruzado
- [x] `python tools/looks/ui_check.py` verde, e um par de família não-`A`
      diferindo acima do piso — `SKIN` move 14,54% da cabeça `I3`
- [x] `python tools/looks/selftest.py --quiet` verde, 39 de 39 controles
      vermelhos
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

A evidência reproduz inteira. Na tabela, a mesma troca de pele nas duas
famílias:

```text
A-A1-A-A-A -> B-A1-A-A-A   palette (144, 480) -> (144, 481)   move
A-I3-A-A-A -> B-I3-A-A-A   palette (144, 480) -> (144, 480)   NÃO move
```

O `edits()` passou a receber a cabeça que a tupla veste e a re-endereçar a
chave `HEAD`. Depois disso:

```text
A-I3-A-A-A vs B-I3-A-A-A   14,54% dos pixels da cabeça   (era 0,00%)
A-I3-A-A-A vs A-I3-C-A-A    2,90%                        (era 0,00%)
A-I3-A-A-A vs A-I3-A-E-A    0,09%                        (era 0,00%)
```

E a segunda metade que a CORR pede ficou escrita em vez de suposta: os índices
de primitiva foram medidos **na seção 24**, e a 34 desenha 23 primitivas onde a
24 desenha 18. Eles são aplicados — cabeça que não recebe cor nenhuma é o
defeito que esta CORR conserta —, e cada parte que eles tocam noutra cabeça sai
marcada:

```text
/BIN/MODEL.BIN section 34 … palette (16, 481, 16) band +16 x2
    COLOUR BY BORROWED INDEX: the colour rows were measured on section 24,
    not this one
```

A marca viaja pelo `Scene.notes` junto com a `band unmeasured` da
CORR-LOOKS-028 — `colour borrowed: 9` de 598 partes na `B-I3` —, e o
`scene --check-image` **exige** que ela apareça: uma cabeça não-`A` sem nenhuma
parte marcada significaria que o re-endereçamento sumiu.

### O segundo defeito, que a asserção do conserto achou

Ao afirmar que **as quatro** linhas de cor chegam à cabeça, saíram três. O
plano guardava `{primitivas: (efeito, passo)}`, e `H.F.COL.` e `FACE` nomeiam
as **mesmas** duas primitivas da barba — uma anda a coluna do CLUT, a outra a
faixa. A segunda substituía a primeira, e **`H.F.COL.` não movia nada em cabeça
nenhuma**, nem na 24:

```text
A-A1-A-A-A -> [SKIN, H.COL, FACE]
A-A1-A-A-E -> [SKIN, H.COL, FACE]      (a cor de barba E não aparece)
```

A chave interna virou `(linha, primitivas)`. Agora:

```text
A-A1-A-A-E -> [SKIN, H.COL, H.F.COL. 4, FACE]
    section 24 … palette (144, 480, 16) -> (208, 480, 16)
```

Isso **corrige a atribuição de causa da própria evidência desta CORR**: o
`A-I3-A-A-E` que ela mede em 0,00% não era só a chave da cabeça — era também a
colisão, e a colisão valia para a família `A` igualmente, onde a CORR supunha o
código funcionando.

### O que ficou aberto, e virou CORR

Com a colisão consertada, a cor de barba **muda a superfície e não muda um
pixel**: as janelas 9 e 13 do registro de pele diferem em seis das dezesseis
entradas (`[2, 5, 12, 13, 14, 15]`), o `Scene` constrói duas texturas
diferentes (CLUT `30729` contra `30733`), e o quadro sai byte a byte igual nas
duas cabeças. Pode ser correto — os texels da barba talvez só usem as dez
entradas iguais — e não está medido. Aberto como
[`CORR-LOOKS-038`](/docs/tasks/looks/CORR-LOOKS-038.md).

### Problemas encontrados

Os dois acima. Nenhum gate global quebrou em nenhum momento.

### Arquivos criados/modificados

- `tools/looks/assembly.py` — `edits(values, head)`, a chave
  `(linha, primitivas)`, `HEAD_COLOUR_MEASURED`, `colour_is_measured()`, a
  marca no `--tuple` e as asserções
- `tools/looks/scene.py` — `Part.colour_borrowed`, a nota `colour borrowed`, e
  o caso cruzado no `--check-image`
- `tools/looks/controls.py` — `assembly-colour-stays-on-24` e
  `assembly-plan-key-drops-a-row`
- `docs/PLAN-LOOKS-PY.md` — §6(c): a chave e o que falta medir
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-034.md` — este arquivo
