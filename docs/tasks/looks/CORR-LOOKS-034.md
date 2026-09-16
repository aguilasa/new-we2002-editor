---
id: CORR-LOOKS-034
title: "Correção: nenhum campo de cor alcança a cabeça quando o cabelo não é da família A"
type: correção
category: núcleo
status: pendente
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

- [ ] `python tools/looks/assembly.py --tuple B-I3-A-A-A` move a paleta da
      seção 34, ou diz que não a mediu — nunca devolve a de `A-I3`
- [ ] `python tools/looks/scene.py --check-image` verde, com o caso cruzado
- [ ] `python tools/looks/ui_check.py` verde, e um par de família não-`A`
      diferindo acima do piso
- [ ] `python tools/looks/selftest.py --quiet` com todos os controles vermelhos
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
