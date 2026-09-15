---
id: CORR-LOOKS-025
title: "Correção: cada `TEX_*.BIN` tem cinco paletas de 256, não duas, e o \"casa e fora\" é inferência sem medição"
type: correção
category: textura
status: concluído
depends_on: []
---

# CORR-LOOKS-025: o uniforme foi localizado, e a contagem que veio junto não bate

## Problema identificado

A task fechou a pendência da §1.7 — de onde vem o que o `DAT2D.BIN` não tem — e
a resposta está certa: os CLUT ids de 8 bits que a geometria nomeia moram nos
`TEX_*.BIN`. A frase que a registra é esta:

> **O uniforme é por time**, e é por isso que não está no arquivo comum: mora
> nos **105 `TEX_*.BIN`**, com **duas** paletas de 256 entradas em cada — casa e
> fora.

Duas coisas nela não vêm de medição:

**1. São cinco paletas de 256 por arquivo, não duas.** Medido nos **105**
contêineres, e o número é o mesmo em todos: duas em (0, 486), duas em (0, 488) e
uma em (256, 480). As duas ids que a geometria nomeia levam **duas cada** — que
é o `x2` que a saída do `--elsewhere` imprime —, e existe uma quinta que a
geometria não nomeia e sobre a qual não se disse nada.

**2. "Casa e fora" é leitura do `x2`, não medição.** Nada nesta task trocou o
uniforme no jogo para ver qual das duas paletas de uma id se move — que é
exatamente o gesto que a [`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md)
estabeleceu como o método deste ciclo, e que aqui nem foi tentado. A explicação
é plausível e pode estar certa; o problema é que ela está escrita ao lado de
números medidos, com a mesma tipografia, e a distinção entre as duas coisas é a
disciplina que o ciclo cobra desde a
[`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md).

**Por que isso custa adiante:** a [`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md)
vai escrever a linha `campo → peça + paleta`, e o uniforme é a que tem **duas
candidatas por id**. Escolher "a primeira" porque a prosa disse que são duas é o
erro silencioso desta fase inteira — desenha perfeitamente, nas cores erradas.
E com cinco paletas no arquivo em vez de duas, "a primeira" nem é bem definida.

## Evidência

Remedido nesta revisão, com o `texture.palettes()` commitado, sobre os 105
contêineres do disco japonês:

```text
TEX_*.BIN on the disc: 105
/BIN/TEX_00.BIN: 5 palette(s)
   vram (0,486) 256 entries @9468
   vram (0,488) 256 entries @10012
   vram (0,486) 256 entries @20332
   vram (0,488) 256 entries @20876
   vram (256,480) 256 entries @23848

palettes per TEX file: {5: 105}
palette ids across the 105: {(0,486,256): 210, (0,488,256): 210, (256,480,256): 105}
image rects across the 105: {(576,256): 210, (576,384): 210, (704,256): 105, (768,384): 105}
```

`210 = 105 × 2` nas duas ids que a geometria nomeia, e **105 × 1** numa terceira
que ela não nomeia. A saída da própria ferramenta já dizia o `x2` e não dizia o
resto:

```text
$ python tools/looks/atlas.py --elsewhere
      (   0, 486) x256    414 primitive(s)  in 105 container(s): TEX_00.BIN x2, ...
      (   0, 488) x256    540 primitive(s)  in 105 container(s): TEX_00.BIN x2, ...
      (   0, 485) x256     85 primitive(s)  in   0 container(s)  -- IN NONE OF THEM
      ( 336, 510) x16     136 primitive(s)  in   0 container(s)  -- IN NONE OF THEM
```

## Causa raiz

O `--elsewhere` conta contêineres e ocorrências por id, e a frase do Log leu o
`x2` como "o arquivo tem duas" — sem olhar o que mais o arquivo tem, e
acrescentando uma explicação para o par que nenhuma corrida produziu.

## Correção

### Arquivo: `docs/tasks/looks/11-qual-imagem-e-o-cabelo.md`

A frase com o que foi medido: **cinco** paletas de 256 por `TEX_*.BIN`, duas em
cada uma das duas ids que a geometria nomeia e uma em (256, 480) que ela não
nomeia; uniforme nos 105. E "casa e fora" marcado como **hipótese**, com o gesto
que a decidiria escrito ao lado — trocar o uniforme do time na tela e ver qual
das duas se move, que é o método da task 09.

### Arquivo: `docs/PLAN-LOOKS-PY.md`

A §1.7 fecha a pendência das ids ausentes; se ela repetir "duas", corrigir no
lugar, com a quinta paleta registrada como pergunta aberta.

### Arquivo: `tools/looks/atlas.py`

O `--elsewhere` é quem tem os dados e é onde a frase deveria ter nascido: junto
do `x2`, quantas paletas de 256 o contêiner tem ao todo. É uma linha, e é a
diferença entre "duas, casa e fora" e "duas desta id, de cinco no arquivo".

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/looks/11-qual-imagem-e-o-cabelo.md` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `tools/looks/atlas.py` | modificar |

## Verificação

- [x] a frase diz cinco por arquivo, e nomeia a id que a geometria não usa
      — (256, 480)
- [x] "casa e fora" aparece como hipótese, com o gesto que a decide
- [x] o `--elsewhere` imprime o total de paletas de 256 do contêiner ao lado do
      `x2`
- [x] `python tools/looks/atlas.py --check-image` continua `ok`
- [x] `python tools/looks/selftest.py` verde, 21 de 21 controles vermelhos
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-15

### Resumo do que foi feito

O conserto nasceu onde a frase deveria ter nascido: no comando. O
`--elsewhere` já imprimia `TEX_00.BIN x2` — quantas paletas daquele contêiner
respondem **àquela id** — e agora imprime, uma linha abaixo, quantas o
contêiner tem **ao todo**:

```text
      (   0, 486) x256    414 primitive(s)  in 105 container(s): TEX_00.BIN x2 ...
          256-entry palette(s) per container, in total: 5 in 105 file(s)
      (   0, 488) x256    540 primitive(s)  in 105 container(s): TEX_00.BIN x2 ...
          256-entry palette(s) per container, in total: 5 in 105 file(s)
```

Duas contagens que diferem por um fator de dois e meio, agora a uma linha uma
da outra. São **cinco por arquivo** — duas em (0, 486), duas em (0, 488) e uma
em **(256, 480), que a geometria não nomeia** —, idêntico nos 105:

```text
palettes per TEX file: {5: 105}
palette ids across the 105: {(0,486,256): 210, (0,488,256): 210, (256,480,256): 105}
```

### "Casa e fora" virou hipótese, com o gesto ao lado

A explicação continua plausível e pode estar certa. O que mudou é a tipografia:
ela estava escrita ao lado de números medidos, com a mesma cara deles, e
**nenhuma corrida trocou o uniforme do time na tela** para ver qual das duas
paletas de uma id se move. Esse é o método da LOOKS-TASK-09, e é o que decide.
Está escrito na task 11 e na §1.7 como hipótese, com a quinta paleta como
pergunta aberta ao lado.

Isso importa para a [`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md),
que vai escrever `campo → peça + paleta`: o uniforme é o único campo com **duas
candidatas por id**, e escolher "a primeira" porque a prosa disse que são duas
desenha perfeitamente, nas cores erradas — com cinco no arquivo, "a primeira"
nem é bem definida.

### Problemas encontrados

Nenhum. O achado não desmente o veredito da task: os CLUT ids de 8 bits que o
`DAT2D.BIN` não tem moram nos `TEX_*.BIN`, e isso reproduz.

### Arquivos criados/modificados

- `tools/looks/atlas.py` — o total de paletas por contêiner ao lado do `x2` no
  `--elsewhere`
- `docs/tasks/looks/11-qual-imagem-e-o-cabelo.md` — cinco por arquivo, a quinta
  id nomeada, e "casa e fora" como hipótese
- `docs/PLAN-LOOKS-PY.md` — §1.7, o mesmo no lugar
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-025.md` — este arquivo
