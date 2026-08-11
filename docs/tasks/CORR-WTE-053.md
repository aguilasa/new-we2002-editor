---
id: CORR-WTE-053
title: "Correção: a seção 2 da WTE-TASK-22 descreve o controle como uma faixa só, e o gate declara nove"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-053: 11.952 bytes numa faixa contra 11.955 em nove, e nenhum dos dois diz de qual imagem fala

## Problema identificado

A seção **"2. O controle não é 'imagem intocada'"** da
[WTE-TASK-22](/docs/tasks/22-harness-golden.md) é a medida que define o que o
gate tem de tolerar. Ela diz:

> Aceitar o aviso de tamanho — o caminho normal, porque as imagens deste
> repositório têm 474.784.128 bytes e o editor espera 474.431.328 — grava
> **11.952 bytes** na imagem, faixa `11796..26527` — offsets 0-based,
> inclusivos —, **setores 5 a 11**, antes de qualquer edição.

O gate que a task entregou declara **nove** faixas, não uma, e as duas últimas
ficam **fora** daquele intervalo:

```
conhecida: 1921862..1921862
conhecida: 2012984..2012985
```

Medido nesta revisão, rodando o gate no modo `golden`: **9 faixas, 11.955
bytes**. As sete de setor somam exatamente os 11.952 da seção 2 — os 3 bytes que
faltam são as duas faixas que ela não menciona.

E há um segundo problema, que é o que explica o primeiro: **nenhum dos dois
textos diz de qual imagem fala.** A seção 2 veio da WTE-TASK-12, medida sobre a
**europeia** — a frase *"as imagens deste repositório têm 474.784.128 bytes"* só
vale para ela; a japonesa, que esta mesma task **fixa** no harness, tem
307.187.664. O roteiro, esse sim, declara a imagem no comentário
(*"medido com o `diff_dirigido.sh` sobre `roms/japanese-shift-jis.bin`"*).

Consequência prática: quem tomar a seção 2 como especificação do controle
declara sete faixas, roda o gate e recebe **duas divergências que ninguém
declarou** — e vai procurar bug no port. É a leitura oposta da que a seção
existe para dar.

## Evidência

O gate, nesta revisão, sobre `roms/japanese-shift-jis.bin`:

```
$ bash wte/tools/golden_check.sh wte/tests/roteiros/golden-01-arranque.txt \
       --roteiro-port wte/tests/roteiros/golden-01-arranque.port.txt \
       --modo golden --manter
PASSOU: so as faixas declaradas divergem — 11796..13831, 14136..16183,
16488..18535, 18840..20887, 21192..23239, 23544..25591, 25896..26527,
1921862..1921862, 2012984..2012985
```

O `diff.json` da mesma corrida, somado por faixa:

```
faixas: 9  bytes somados: 11955
  11796..13831  1443 B  data  before first offset
  14136..16183  2048 B  data  before first offset
  16488..18535  2035 B  data  before first offset
  18840..20887  1917 B  data  before first offset
  21192..23239  1906 B  data  before first offset
  23544..25591  1977 B  data  before first offset
  25896..26527   626 B  data  before first offset
  1921862..1921862  1 B  data  OFS_TEAM_NAME_2
  2012984..2012985  2 B  data  OFS_LINK_ML1
```

`1443+2048+2035+1917+1906+1977+626 = 11952` — o número da seção 2 é o das sete
de setor, e só delas.

Os tamanhos das duas imagens:

```
$ ls -l roms/*.bin | awk '{print $5, $NF}'
474784128 roms/golden-european-deluxe.bin
307187664 roms/japanese-shift-jis.bin
```

## Causa raiz

A seção 2 foi herdada da WTE-TASK-12, medida sobre a europeia, e não foi
reconciliada com a medição da japonesa que o gate passou a usar depois da
CORR-WTE-044.

## O número **nove** é o do commit da WTE-TASK-22 — não o copie

Esta revisão mediu a árvore no estado em que a WTE-TASK-22 a deixou. A
[WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md), em execução enquanto isto
era escrito, já reduz a declaração: o port passou a injetar os mesmos sete
setores a partir do `dat.bin`, então eles deixam de ser divergência e sobram as
**duas** sem explicação medida (`1921862` e `2012984..2012985`).

Quem executar esta correção deve tirar a contagem do
`golden-01-arranque.txt` **naquele momento**, e não deste texto — senão troca um
número vencido por outro. O que não muda com a 25 é o resto do achado: a seção 2
descreve o controle como uma faixa só e nenhuma das duas medidas diz de qual
imagem fala.

## Correção

### Arquivo: `docs/tasks/22-harness-golden.md`

Reescrever a seção 2 para dizer, nesta ordem: a imagem de cada medida; que são
**nove** faixas na japonesa, somando 11.955 bytes; que as sete de setor somam os
11.952 herdados da WTE-TASK-12 na europeia; e que as duas restantes
(`1921862`, região `OFS_TEAM_NAME_2`, e `2012984..2012985`, região
`OFS_LINK_ML1`) só aparecem na japonesa — na europeia o editor grava naquele
byte o mesmo valor que já estava, então o `cmp` não o vê (a WTE-TASK-19 já tinha
medido `1921862` como escrita do `ARRANQUE` que não muda byte).

A frase sobre o tamanho esperado precisa dizer que 474.784.128 é o tamanho da
europeia; o aviso aparece igual com a japonesa, por outro número.

A decisão que a seção anuncia — declarar a faixa como exceção em vez de o port
reproduzi-la — não muda; ela já está implementada no roteiro e verificada.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/22-harness-golden.md` | modificar |

## Verificação

- [ ] a seção 2 diz nove faixas e 11.955 bytes, nomeando a imagem de cada
      medida
- [ ] as faixas citadas na seção são as mesmas linhas `conhecida:` do
      `golden-01-arranque.txt`, uma a uma
- [ ] nenhuma afirmação de tamanho de imagem sem dizer qual imagem
- [ ] `make -C wte check` verde
- [ ] `bash wte/tools/golden_check.sh … --modo golden` continua `PASSOU` com as
      nove

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
