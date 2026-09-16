---
id: CORR-LOOKS-038
title: "Correção: a cor de barba troca a superfície e não muda um pixel do quadro"
type: correção
category: verificação
status: pendente
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

- [ ] um comando diz quais índices de paleta os quads da barba usam
- [ ] o desfecho está escrito: ou "não muda o desenho, e eis por quê", ou o
      conserto do caminho da superfície
- [ ] `python tools/looks/scene.py --check-image` verde, com asserção sobre o
      pixel e não só sobre a superfície
- [ ] `python tools/looks/selftest.py --quiet` verde, com todos os controles
      vermelhos
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
