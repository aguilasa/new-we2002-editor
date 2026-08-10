---
id: CORR-WTE-047
title: "Correção: a segunda régua (`cmp`) das sessões 10 e 11 não ficou registrada em lugar nenhum"
type: correção
category: verificação
status: pendente
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

- [ ] toda sessão do `io-medido.tsv` com pelo menos uma faixa `W` tem veredito
      das duas réguas no `offsets-novos.md`
- [ ] teste reprova quando uma sessão com escrita não tem esse veredito
- [ ] `python3 wte/tools/analisar_io.py --check` verde
- [ ] `make -C wte check` verde
- [ ] nenhuma corrida nova aponta para `roms/` — só cópia em `work/`

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
