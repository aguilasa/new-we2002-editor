# PES2 — as cinco listas de nome de time, alinhadas

Gerado por `tools/pes2/team_map.py`. Offsets de `(EsIt)`.

A lista canônica é `SELECT.BIN` @3128, a única com as 106 entradas. As outras quatro são expressas como **trechos** dela.

| Lista | Arquivo | Entradas | Estrutura |
|---|---|---:|---|
| canônica | `/SELECT.BIN` | 106 | 2 de cabeçalho + 32 fictícios + 7 temáticas + 2 *elite* + 54 reais + 7 *classic* + 2 *allstars* |
| `team-names-selectc` | `/SELECTC.BIN` | 99 | [0–3] → fora; [4–98] → canônica[2–96] |
| `team-names-ending` | `/ENDING.BIN` | 95 | [0–94] → canônica[2–96] |
| `team-names-result` | `/RESULT.BIN` | 94 | [0–31] → canônica[2–33]; [32–36] → canônica[97–101]; [37–39] → canônica[103–105]; [40–93] → canônica[43–96] |
| `team-names-replays` | `/REPLAYS.BIN` | 123 | [0–31] → canônica[2–33]; [32–59] → fora; [60–122] → canônica[34–96] |

## O que a canônica não tem

**`team-names-selectc`** — 4 entradas:

```
Belarus, Georgia, Uzbekistan, Iceland
```

**`team-names-replays`** — 28 entradas:

```
Edit, Free, Default, New Zealand, Lebanon, Honduras, Trinidad And Tobago, Canada, Sierra Leone, Zambia, Liberia, Burundi, Togo, Congo The Dr, Cote D'ivoire, Guinea, Ghana, Algeria, United Arab Emirates, Jamaica, Northern Ireland, Latvia, Macedonia, Bosnia And Herzegovina, Belarus, Georgia, Uzbekistan, Iceland
```

## As três armadilhas que este alinhamento fecha

1. **`RESULT.BIN` pula nove e traz oito outras.** Onde a canônica tem as 7 seleções temáticas e as 2 *elite* (índices 34–42), ela não tem nada; e no lugar traz 6 dos 7 *classic* mais as 2 *allstars*. **`CLASSIC FRANCE`, índice canônico 102, não existe nela.**
2. **`REPLAYS.BIN` insere 28 entradas no meio** — `Edit`, `Free`, `Default` e 25 nações que só o modo de edição conhece — entre os fictícios e as seleções temáticas.
3. **`SELECTC.BIN` insere 4 no começo** — `Belarus`, `Georgia`, `Uzbekistan`, `Iceland`.

Nenhuma das três é visível para quem casa listas por índice, e todas as três fazem o editor gravar no time errado com um nome plausível.

## Cobertura por time

Quantas das cinco listas contêm cada faixa da canônica.

| Faixa canônica | O que é | Em quantas listas |
|---|---|---:|
| 0–1 | cabeçalho (`MASTER DATA`, `? ? ? ?`) | 1 |
| 2–33 | 32 clubes fictícios | 5 |
| 34–40 | 7 seleções temáticas | 4 |
| 41–42 | `WORLD ELITE`, `EURO ELITE` | 4 |
| 43–96 | 54 seleções reais | 5 |
| 97–103 | 7 *classic* | 1–2 |
| 104–105 | `WORLD ALLSTARS`, `EURO ALLSTARS` | 2 |
