---
id: CORR-LOOKS-038
title: "Correção: a cor de barba troca a superfície e não muda um pixel do quadro"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-LOOKS-038: `H.F.COL.` chega à textura e não chega à tela

## Problema identificado

A [`CORR-LOOKS-034`](/docs/tasks/looks/CORR-LOOKS-034.md) consertou a colisão
que fazia o `H.F.COL.` desaparecer do plano — `H.F.COL.` e `FACE` nomeiam as
mesmas duas primitivas da barba, e a chave do plano guardava só as primitivas,
de modo que a segunda substituía a primeira. Depois do conserto a linha chega:
o CLUT id anda da coluna 9 para a 13, o `assembly --tuple` imprime a paleta
nova, e o `Scene` constrói **outra superfície**.

O quadro renderizado continua **byte a byte idêntico**.

Isso não é necessariamente defeito — pode ser que os texels da barba usem só as
dez entradas que as duas janelas têm iguais —, e é justamente esse o problema:
**ninguém mediu**, e a diferença entre "correto" e "a cor não chega ao
desenho" é invisível hoje. É a mesma forma dos dois achados que a
CORR-LOOKS-034 corrigiu, um degrau adiante: lá a tabela não mudava e o boneco
desenhava perfeitamente; aqui a tabela muda, a textura muda, e o boneco desenha
perfeitamente igual.

**Por que custa adiante:** a [`LOOKS-TASK-17`](/docs/tasks/looks/17-confronto-com-o-emulador.md)
confronta o nosso quadro com o do emulador tupla a tupla. Se o jogo mudar a
barba e nós não, a diferença aparece lá como discrepância de render sem causa
nomeada — e o `scene --check-image` já terá passado verde, porque a asserção
dele é sobre **superfície**, e a superfície muda.

## Evidência

O plano e a superfície mudam, medido depois da CORR-LOOKS-034:

```text
$ python tools/looks/assembly.py --tuple A-A1-A-A-A   |  --tuple A-A1-A-A-E
    MODEL.BIN section 24 … palette (144, 480, 16)     |  … palette (208, 480, 16)

$ python - <<'PY'   (scene.from_image, as primitivas 8 e 13 da seção 24)
A-A1-A-A-A prim 8 surface (3568, 0, 30729)
A-A1-A-A-E prim 8 surface (3568, 0, 30733)
PY
```

As duas janelas do registro de pele **não** são iguais:

```text
columns  9 vs 13 differ at [2, 5, 12, 13, 14, 15]
```

E o quadro não muda, nem na cabeça medida nem na emprestada:

```text
$ … app.py --looks A-A1-A-A-A --piece head …  vs  A-A1-A-A-E
    0 of 409600 pixel(s) differ (0.00%)
$ … A-I3-A-A-A  vs  A-I3-A-A-E
    0 of 409600 pixel(s) differ (0.00%)
```

Para comparar, as outras três linhas de cor movem pixels na mesma cabeça:
`SKIN` 14,54%, `H.COL` 2,90%, `FACE` 0,09%.

## Causa raiz

Não medida. Duas leituras cabem, e a diferença entre elas é uma corrida:

1. **correto** — os texels dos dois quads da barba caem só nas dez entradas que
   as janelas 9 e 13 têm iguais, e o desenho realmente não muda;
2. **defeito** — a superfície nova é construída e não chega ao quad na hora de
   desenhar (`surface_for` guardado por chave, `uvs`, ordem de desenho).

## Correção

### Arquivo: `tools/looks/scene.py`

O que decide é **quais índices os texels dos quads 8 e 13 realmente usam**, que
é leitura pura do disco: se a interseção com `[2, 5, 12, 13, 14, 15]` for
vazia, a leitura 1 está certa e isso vira uma linha escrita — um caso conhecido
de "muda a paleta e não muda o desenho", que a LOOKS-TASK-17 precisa saber
antes de confrontar. Se não for vazia, é a leitura 2 e o conserto é no
caminho da superfície.

Nos dois desfechos, o `--check-image` ganha a asserção que falta: hoje ele
afirma que uma cor de cabelo muda superfície, e não afirma nada sobre o
**pixel**. Uma cor que muda superfície e não muda pixel tem de ser um caso
**declarado**, não um silêncio.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/scene.py` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar, conforme o desfecho |
| `docs/tasks/looks/17-confronto-com-o-emulador.md` | modificar, se virar caso conhecido |

## Verificação

- [x] um comando diz quais índices de paleta os quads da barba usam — o
      `scene --check-image`, por faixa do `FACE`
- [x] o desfecho está escrito: **não muda o desenho, e eis por quê** — a faixa
      0 é o rosto sem barba
- [x] `python tools/looks/scene.py --check-image` verde, com asserção sobre o
      que o texel amostra e não só sobre a superfície
- [x] `python tools/looks/selftest.py --quiet` verde, 40 de 40 controles
      vermelhos
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

**Desfecho: a leitura 1, e mais nítida do que esta CORR a formulou.** Os dois
quads da barba amostram os índices `{0, 1, 3, 4, 6, 7, 8, 9, 10, 11}` — e a
interseção com os seis que uma cor de barba move é **vazia**:

```text
primitive  8  record 3568  rect x 24..36 y 0..16  indices used: [0, 1, 3, 4, 6, 7, 8, 9, 10, 11]
   intersection with the six that differ between windows 9 and 13: []
primitive 13  record 3568  rect x 36..46 y 0..16  idem
```

**A faixa 0 do `FACE` é o rosto sem barba.** É o que a varredura por faixa
mostra, e é a resposta inteira:

```text
a beard colour moves 6 of the window's 16 entries: [2, 5, 12, 13, 14, 15]
FACE band 0 samples 0 of them: []
FACE band 1 samples 5 of them: [2, 5, 12, 14, 15]
FACE band 2 samples 6 of them: [2, 5, 12, 13, 14, 15]
FACE band 3 samples 5 of them: [2, 12, 13, 14, 15]
FACE band 4 samples 5 of them: [2, 12, 13, 14, 15]
```

E na tela, que é onde a pergunta nasceu:

```text
A-A1-A-A-A vs A-A1-A-A-E   0 of 409600 (0.00%)    FACE=A, sem barba
A-A1-A-B-A vs A-A1-A-B-E   9772 of 409600 (2.39%)
A-A1-A-E-A vs A-A1-A-E-E   10390 of 409600 (2.54%)
```

Não havia defeito no caminho da superfície: **não há barba para colorir** na
faixa 0. A cor de barba funciona nas outras quatro.

### O que o gate ganhou

O `scene --check-image` afirmava sobre **superfície** e agora afirma também
sobre o **texel**: a faixa 0 tem de amostrar zero das entradas que a cor de
barba move, e nenhuma das outras pode amostrar zero. As duas metades juntas —
uma cor de barba que parasse de chegar apareceria como as faixas 1..4
esvaziando, e não como um silêncio.

O `indices_in_quad()` saiu separado do `sampled_indices()` para ser exercitável
sem fluxo LZSS: no `self_check()` um buffer de 8×32 com índice 1 na linha 0 e 5
na linha 16 afirma que um quad amostra o que está sob ele e que **a faixa o
move**. Controle novo `scene-texel-window-ignored`: a faixa descartada na
leitura. Vermelho.

### Problemas encontrados

Nenhum. A hipótese 2 da CORR — defeito no caminho da superfície — está
descartada por medição, não por ausência de sintoma.

### Arquivos criados/modificados

- `tools/looks/scene.py` — `indices_in_quad()`, `sampled_indices()`, a
  asserção por faixa no `--check-image` e o caso sintético no `self_check()`
- `tools/looks/controls.py` — o controle `scene-texel-window-ignored`
- `docs/PLAN-LOOKS-PY.md` — §6(c), a faixa 0 como rosto sem barba
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-038.md` — este arquivo
