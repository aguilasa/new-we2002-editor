---
id: WTE-TASK-06
title: "re/offsets.md — a tabela em .data cruzada com Offsets.hpp"
type: extração
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-02"]
status: pendente
---

# WTE-TASK-06: Mapa de offsets

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §1.7 e Fase 1 item 4.
- **É o atalho do projeto inteiro.** Nenhum trabalho de RE começa sabendo o
  formato do arquivo-alvo; este começa.

Medido: **19 dos 69 `OFS_*`** de
[`Offsets.hpp`](../../src/core/include/we2002/Offsets.hpp) aparecem literalmente
no binário do Obocaman, quase todos num bloco contíguo de `.data` a partir de
`0x004231a0`:

```
va 0x004231a0  =  2002316   OFS_TEAM_NAME_KANJI
va 0x004231a4  =  4598596   OFS_TEAM_MIXED_CASE_NAME
va 0x004231b8  =  2003996   OFS_TEAM_NAME_3
va 0x004231bc  =  1012640   OFS_TEAM_NAME_1
...
va 0x004231d8  =  5651068   OFS_TEAM_ABBREV_2
```

Consequência: **qualquer instrução que indexe `0x004231a0` está mexendo em nome
de time**, e isso se sabe sem decompilar.

---

## Objetivo

`wte/re/offsets.md` respondendo três coisas.

### 1. Onde a tabela começa e onde termina

Medido no protótipo: o bloco tem buracos (`= 0`) e é seguido de dados que **não
são offsets** — `1869507948` é ASCII `l,km`. Achar o limite superior e o
inferior, com critério escrito.

**Esta é a armadilha §8.7 do plano.** Tratar como array algo que termina antes
do que se pensa é exatamente o bug do slot 64 num array de 63 que o `newWe2002`
já documentou. O limite tem de ser medido, não estimado pelo olho.

### 2. Quais dos 69 batem, e o que os outros 50 são

Os 50 restantes não aparecem como literal. Duas hipóteses, e o mapa deve dizer
qual vale para cada um: aritmética (`base + constante`, com a base na tabela),
ou região que o Moriero nomeou e o Obocaman não.

Não é preciso resolver os 50 aqui — a WTE-TASK-19 faz isso por diff dirigido.
Aqui basta **classificar** e deixar a lista de alvos.

### 3. Que offsets o Obocaman tem e nós não

O caminho inverso, e é o mais valioso: varrer `.data` e `.text` por dword
plausível (entre 1.000.000 e 8.000.000, alinhado, referenciado por código) que
**não** esteja em `Offsets.hpp`. Cada um é uma região do formato que este
repositório ainda não nomeou.

O `ed.exe` não edita camisa 2D nem lê `.mcr`; então os offsets dessas regiões,
se existirem, só existem do lado do Obocaman.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_offsets.py` | criar |
| `wte/re/offsets.md` | criar |
| `wte/re/offsets.tsv` | criar |

---

## Critério de conclusão

- [ ] Limite da tabela medido, com o critério escrito (§8.7)
- [ ] Os 19 confirmados, com VA e nome nosso
- [ ] Os 50 restantes classificados por hipótese
- [ ] Candidatos a offset que **não** estão em `Offsets.hpp` listados
- [ ] Nenhum número no doc veio de contagem à mão
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
