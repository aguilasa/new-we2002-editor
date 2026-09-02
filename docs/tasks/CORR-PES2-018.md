---
id: CORR-PES2-018
title: "Correção: são 9 de 13 entradas que recomprimem no orçamento, não 10 de 3, e a folga vai a 3 bytes, não 4"
type: correção
category: dados
status: pendente
depends_on: []
---

# CORR-PES2-018: Dois números da §1.14(g) não batem com a ferramenta

## Problema identificado

A PES2-TASK-29 escreveu, no Log e na §1.14(g) do plano, dois números que a
medição não sustenta:

| Afirmado | Medido | Onde está escrito |
|---|---|---|
| "**10** recomprimem dentro do próprio orçamento e **3** não" | **9** cabem, **4** não | §1.14(g) e o Log da task |
| "a folga medida … é de **0 a 4 bytes**" | **0 a 3** | §1.14(g) e o Log da task |

Os dois vieram de leitura de uma listagem **truncada** — o laço que os produziu
imprimia só `if i < 4 or ok`, de modo que a última entrada do `LOGO.BIN`, que
estoura, nunca apareceu na tela e não entrou na conta. É o caso literal da
regra do repositório: *todo número em doc vem de ferramenta*, e este veio de
somar o que a tela mostrava.

## Evidência

```
$ python3 - <<'PY'   # laço completo, sem o filtro de impressão
/BIN/TITLE.BIN      0 konami  7836 ours  7858 room  7836 folga  0 ESTOURA +22
/BIN/TITLE.BIN      1 konami  7208 ours  7263 room  7208 folga  0 ESTOURA +55
/BIN/TITLE.BIN      2 konami  3309 ours  3297 room  3312 folga  3 cabe
/BIN/TITLE.BIN      3 konami  5230 ours  5232 room  5232 folga  2 cabe
/BIN/LOGO.BIN       0 konami  2855 ours  2855 room  2856 folga  1 cabe
/BIN/LOGO.BIN       1 konami  3212 ours  3214 room  3212 folga  0 ESTOURA  +2
/BIN/LOGO.BIN       2 konami   899 ours   887 room   900 folga  1 cabe
/BIN/LOGO.BIN       3 konami   981 ours   980 room   984 folga  3 cabe
/BIN/LOGO.BIN       4 konami  1851 ours  1835 room  1852 folga  1 cabe
/BIN/LOGO.BIN       5 konami   526 ours   527 room   528 folga  2 cabe
/BIN/LOGO.BIN       6 konami  2276 ours  2256 room  2276 folga  0 cabe
/BIN/LOGO.BIN       7 konami  3144 ours  3131 room  3144 folga  0 cabe
/BIN/LOGO.BIN       8 konami  1074 ours  1081 room  1076 folga  2 ESTOURA  +5

TOTAL 9 de 13 recomprimem dentro do orcamento; 4 nao
folga (room - stream original): min 0, max 3
```

A entrada que faltava é a `/BIN/LOGO.BIN` **8**: 1.081 bytes contra 1.076 de
folga, 5 acima.

## Causa raiz

O número foi lido de uma saída filtrada em vez de sair de um comando que
imprime o total.

## Correção

### Arquivo: `tools/pes2/asset_write.py`

Acrescentar um subcomando que **imprime a conta**, para o número do doc ter de
onde vir — por exemplo `budget <copia.bin> [--file P]`, listando por entrada
`konami / ours / room / folga` e fechando com `N de M cabem` e `folga min..max`.
Sem ele, a próxima recontagem repete o erro.

### Arquivo: `docs/PLAN-PES2-PSX.md` §1.14(g)

- "10 recomprimem dentro do próprio orçamento e 3 não" → **9 … e 4 não**
- "a folga medida nas entradas de `TITLE.BIN` e `LOGO.BIN` é de 0 a 4 bytes" →
  **0 a 3 bytes**

### Arquivo: `docs/tasks/29-gravacao-de-asset.md`

As mesmas duas correções no Log de Execução, com a nota de que os números
passaram a sair do subcomando novo.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/asset_write.py` | modificar |
| `docs/PLAN-PES2-PSX.md` | modificar |
| `docs/tasks/29-gravacao-de-asset.md` | modificar |

## Verificação

- [ ] `python3 tools/pes2/asset_write.py budget <copia.bin>` imprime `9 de 13` e `0..3`
- [ ] os dois números do plano e do Log batem com essa saída
- [ ] `python3 tools/pes2/asset_write.py check <copia> --tmpdir <dir>` continua verde
- [ ] `ctest --test-dir build -R pes2` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
