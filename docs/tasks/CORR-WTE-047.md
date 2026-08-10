---
id: CORR-WTE-047
title: "Correção: a segunda régua (`cmp`) das sessões 10 e 11 não ficou registrada em lugar nenhum"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-047: as sessões que deram 18 dos 33 offsets não têm o resultado da conferência das duas réguas

## Problema identificado

O método da [WTE-TASK-19](/docs/tasks/19-os-50-offsets-restantes.md) tem **duas
réguas independentes**, e o `diff_dirigido.sh` diz isso no cabeçalho: o trace de
`strace` (que região o editor endereça) e o `cmp` contra a cópia limpa (o que de
fato mudou). A conferência entre elas — `analisar_io.py --conferir` — é o que
pegou os **três** defeitos de instrumento das passagens anteriores; a 4ª passagem
registrou o resultado dela em número ("19 faixas do `cmp` contidas na união de 31
faixas de escrita do trace").

Para as sessões **`10-telas-que-faltavam`** e **`11-varredura-de-times`**, que
são as que levaram os endereçados de 15 para 33, esse número não existe em lugar
nenhum:

- o `cmp.tsv` de cada corrida fica no diretório de saída da sessão, que **não é
  versionado** — só o `io.tsv` (o trace) foi fundido em
  [`wte/re/io-medido.tsv`](../../wte/re/io-medido.tsv);
- o Log da 5ª passagem não traz o número, ao contrário do da 4ª;
- o `offsets-novos.md` gerado cita o `cmp` só na seção do método, nunca como
  resultado dessas duas sessões.

As duas escreveram na imagem (9 faixas de escrita no `ARRANQUE` de cada, mais 1
em `TIME_FUNDO`), então havia o que conferir.

**Não é suspeita de que a conferência não rodou:** o `diff_dirigido.sh` tem
`set -euo pipefail` e chama `--conferir` como última etapa, e a função devolve 3
quando alguma faixa do `cmp` não aparece como escrita no trace — a corrida teria
abortado antes do `>> pronto`. O problema é de **evidência**, não de execução: um
terceiro não consegue reconferir aquilo que, por três vezes seguidas, foi o que
denunciou defeito silencioso do instrumento.

## Evidência

O que existe versionado das duas sessões é só o trace:

```
$ awk -F'\t' 'NR>1{c[$2]++} END{for(k in c) print c[k], k}' wte/re/io-medido.tsv | sort -k2
38 06-diff-dirigido
38 06-truncada
64 09-areas-com-time
102 10-telas-que-faltavam
125 11-varredura-de-times

$ git ls-files wte/re | grep -i cmp
(vazio)

$ grep -rn "duas réguas\|réguas fecham" wte/re/offsets-novos.md
(nada — o `cmp` só aparece na seção "O método, e por que não é `cmp`")
```

A conferência que roda, e não deixa rastro (`wte/tools/diff_dirigido.sh:270`):

```bash
python3 "$AQUI/analisar_io.py" --conferir "$SAIDA/io.tsv" "$SAIDA/cmp.tsv"
echo ">> pronto: $SAIDA"
```

Comparação com a 4ª passagem, que registrou:

> as duas réguas fechando (19 faixas do `cmp` contidas na união de 31 faixas de
> escrita do trace)

## Causa raiz

O `cmp.tsv` morre no diretório da sessão, e nada no fluxo carrega o resultado da
conferência para dentro de `wte/re/`.

## Correção

### Arquivo: `wte/tools/diff_dirigido.sh` (ou `analisar_io.py`)

Fundir o resultado da conferência num TSV versionado — `wte/re/cmp-medido.tsv`,
com as mesmas colunas de chave do `io-medido.tsv` (`imagem`, `sessao`, faixa) —
pela mesma porta por onde as faixas do trace entram. É dado de medição, como o
`io-medido.tsv`: não se regenera sem Wine, e por isso tem de ser versionado.

### Arquivo: `wte/tools/analisar_io.py`

Emitir, no `offsets-novos.md`, uma linha por sessão com o veredito das duas
réguas — quantas faixas do `cmp` couberam em quantas faixas de escrita do trace
—, derivada desse TSV. Assim a afirmação passa a ser gerada, como o resto do
documento, em vez de escrita à mão no Log de uma passagem e esquecida na
seguinte.

Se as duas sessões novas não tiverem mais o `cmp.tsv` no disco, refazer as duas
corridas (sobre **cópia** de `roms/japanese-shift-jis.bin`) é o caminho — os
roteiros são fixos, e é para isso que eles existem.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/cmp-medido.tsv` | criar — a evidência da segunda régua, por sessão |
| `wte/tools/diff_dirigido.sh` | modificar |
| `wte/tools/analisar_io.py` | modificar |
| `wte/tools/test_analisar_io.py` | modificar — toda sessão com escrita tem linha da segunda régua |
| `wte/re/offsets-novos.md` | modificar (regerado) |

## Verificação

- [x] toda sessão do `io-medido.tsv` com pelo menos uma faixa `W` tem veredito
      das duas réguas no `offsets-novos.md` — as cinco, e as cinco fecham
- [x] teste reprova quando uma sessão com escrita não tem esse veredito —
      plantado tirando as 9 linhas da `11-varredura-de-times`:
      `11-varredura-de-times escreveu e não tem cmp versionado`
- [x] `python3 wte/tools/analisar_io.py --check` verde; duas gerações dão o
      mesmo md5 (`2e22a36e...`)
- [x] `make -C wte check` verde — 383 testes, `rc=0`
- [x] nenhuma corrida nova aponta para `roms/` — o `diff_dirigido.sh` copia
      para `work/`, e o `mtime` de `roms/` continua 2026-08-03

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

A segunda régua passou a ter arquivo. Três peças:

1. **`wte/re/cmp-medido.tsv`** — as 51 faixas do `cmp` das cinco sessões, com
   `imagem` e `sessao` como chave, no mesmo molde do `io-medido.tsv`. É dado
   de medição: não se regenera sem Wine, e por isso é versionado.
2. **`analisar_io.py --fundir-cmp`** — a porta por onde o `cmp.tsv` da corrida
   entra, chamada pelo `diff_dirigido.sh` logo depois do `--conferir`. Ela
   **substitui** as linhas daquela sessão e preserva as demais, para que
   repetir uma corrida não duplique faixa.
3. **A seção "As duas réguas, sessão a sessão"** no `offsets-novos.md`, com
   uma linha por sessão que escreveu: quantas faixas o `cmp` viu, quantas
   delas cabem na união das faixas de escrita do trace, e quantas escritas o
   trace registrou. Derivada do TSV, como o resto do arquivo — a afirmação
   deixa de morar em prosa no Log de uma passagem.

| sessão | `cmp` | contidas | escritas |
|---|---:|---:|---:|
| `06-diff-dirigido` | 7 | 7 | 8 |
| `06-truncada` | 7 | 7 | 8 |
| `09-areas-com-time` | 19 | 19 | 31 |
| `10-telas-que-faltavam` | 9 | 9 | 10 |
| `11-varredura-de-times` | 9 | 9 | 9 |

Cinco testes novos: quatro sobre a fusão e o cálculo do veredito (sessão que
não escreveu não entra; sessão que escreveu e não tem `cmp` fica marcada;
faixa do `cmp` fora das escritas é contada; refundir a mesma sessão não
duplica), e um de evidência que exige, para **toda** sessão com escrita no
`io-medido.tsv`, que exista `cmp` versionado, que ele feche, e que a linha
esteja no markdown gerado.

**Problemas encontrados:**

O `cmp.tsv` de quatro das cinco sessões ainda estava em
`/tmp/diff-dirigido/`; o da `09-areas-com-time` não. Foi preciso **refazer a
corrida 09** sob Wine no `:99`, sobre cópia de `roms/japanese-shift-jis.bin`,
como a seção Correção previa. O resultado é confirmação independente e vale
registrar:

- o trace novo é **idêntico** ao versionado — as 64 linhas da sessão 09 no
  `io-medido.tsv` conferem uma a uma com o `io.tsv` da corrida nova, então o
  `cmp` recuperado pertence de fato àquele trace;
- o `--conferir` da corrida nova imprimiu *"as duas reguas fecham -- 19
  faixa(s) do cmp contidas em 31 faixa(s) de escrita do trace"*, que é
  exatamente o número que o Log da 4ª passagem trazia em prosa. A afirmação
  que não tinha rastro reproduziu ao pé da letra.

Um detalhe de implementação: `fundir_cmp()` imprimia o alvo com
`relative_to(ROOT)`, que estoura quando o teste aponta o TSV para um
diretório temporário. Passou a cair para o caminho absoluto fora da árvore.

**Arquivos criados/modificados:**

- `wte/re/cmp-medido.tsv` — criado (51 faixas, 5 sessões)
- `wte/tools/analisar_io.py` — `ler_cmp_medido()`, `fundir_cmp()`,
  `veredito_das_reguas()`, `--fundir-cmp` e a seção gerada
- `wte/tools/diff_dirigido.sh` — chama a fusão depois da conferência
- `wte/tools/test_analisar_io.py` — `TestSegundaRegua` (nova) e um teste em
  `TestEvidencia`
- `wte/re/offsets-novos.md` — regerado
