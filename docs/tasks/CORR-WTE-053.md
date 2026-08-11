---
id: CORR-WTE-053
title: "Correção: a seção 2 da WTE-TASK-22 descreve o controle como uma faixa só, e o gate declara nove"
type: correção
category: verificação
status: concluído
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

## Log de Execução

**Executado em:** 2026-08-11

**Resumo do que foi feito:**

A seção 2 da WTE-TASK-22 foi reescrita com a imagem de cada medida numa tabela
(europeia 474.784.128 B, japonesa 307.187.664 B), as sete faixas de setor
somando os 11.952 herdados da WTE-TASK-12 e as duas que só a japonesa tem — 3
bytes, 11.955 no total —, mais a explicação do recorte: os saltos entre as sete
são os 304 bytes de cabeçalho e EDC/ECC de setor, que o editor não toca. É a
mesma escrita da europeia, vista com a régua do setor.

**A contagem de faixas declaradas saiu do texto e virou ponteiro.** O aviso da
própria CORR se cumpriu: quando esta correção foi executada, a WTE-TASK-25 já
tinha baixado a declaração de nove para **duas**, ao fazer o port injetar os
sete setores a partir do `dat.bin`. Escrever "nove" na prosa teria trocado um
número vencido por outro, então a seção passou a apontar para o
`golden-01-arranque.txt`, que é o arquivo que o veredito consulta, e a citar as
nove só como o estado em que o roteiro nasceu.

Números remedidos nesta execução, não copiados da CORR:

```
$ cmp -l work/dd-clean.bin work/dd-run.bin | awk '{p=$1-1;
    if (NR==1) {ini=p; prev=p; n=1; next}
    if (p>prev+304) {print ini".."prev": "n" B"; ini=p; n=0}
    prev=p; n++} END {print ini".."prev": "n" B"}'
11796..13831: 1443 B     18840..20887: 1917 B     25896..26527:  626 B
14136..16183: 2048 B     21192..23239: 1906 B     1921862..1921862:   1 B
16488..18535: 2035 B     23544..25591: 1977 B     2012984..2012985:   2 B
# 1443+2048+2035+1917+1906+1977+626 = 11952; com as duas de baixo, 11955

$ bash wte/tools/golden_check.sh wte/tests/roteiros/golden-01-arranque.txt \
       --roteiro-port wte/tests/roteiros/golden-01-arranque.port.txt --modo golden
PASSOU: so as faixas declaradas divergem — 1921862..1921862, 2012984..2012985
```

**Discrepância consertada junto:** o `wte/re/visual.md`, para onde a seção 2
aponta, dizia *"as imagens deste repositório: elas têm 474.784.128 bytes"* — só
a europeia tem. Corrigido para dizer os dois tamanhos e para registrar que o
achado 2 inteiro é da europeia, com ponteiro para a conta por faixa da japonesa.

**Problemas encontrados:**

O `cmp -l` foi rodado sobre o par `work/dd-clean.bin` / `work/dd-run.bin` que já
estava no disco, de uma corrida anterior do `diff_dirigido.sh` — leitura pura,
sem tirar cópia nova de 307 MB só para recontar. O gate `golden` foi rodado de
verdade, e é dele que sai o `PASSOU` acima.

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `docs/tasks/22-harness-golden.md` | modificado — seção 2 reescrita |
| `wte/re/visual.md` | modificado — o tamanho por imagem, e o achado 2 rotulado como europeu |
| `docs/tasks/CORR-WTE-053.md` | `status: concluído` e este Log |
| `docs/tasks/correcoes-progresso.md` | `[x]` na tabela e no checklist |
