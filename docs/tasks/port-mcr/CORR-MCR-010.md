---
id: CORR-MCR-010
title: "Correção: são dois os nomes que enchem os dez bytes, não um — o slot 5 também"
type: correção
category: dados
status: concluído
depends_on: []
---

# CORR-MCR-010: o slot 5 enche os dez bytes e não está registrado

## Problema identificado

A §1.6 do [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) — fonte de verdade da
MCR-TASK-07 — registra o campo de nome assim:

> E o campo **não é cadeia terminada em NUL**: o slot 20 usa os 10 bytes.

A [MCR-TASK-07](/docs/tasks/port-mcr/07-dorsais-e-nome.md) herdou a frase no
Contexto e no critério (*"inclusive o slot 20, que enche os 10 bytes"*).

**São dois slots, não um.** O slot **5** (`ジｮｰ･ﾛﾚﾝｿﾝ`) também ocupa os dez
bytes sem NUL, e o próprio `text.py --check` o marca — a ferramenta já sabe, o
documento é que não:

```
 5  83 57 ae b0 a5 db da dd bf dd  'ジｮｰ･ﾛﾚﾝｿﾝ'  <-- fills all ten bytes
20  83 4b d8 bd a5 db 83 6f b0 bd  'ガﾘｽ･ﾛバｰｽ'   <-- fills all ten bytes
```

A afirmação de invariante — "não é cadeia terminada em NUL" — **continua
certa**; o que está incompleto é a enumeração. E a enumeração é o que um teste
copia: um caso escrito só contra o slot 20 acha que cobriu a situação, quando
há um segundo exemplar, com o separador `･` numa posição diferente.

## Evidência

Leitura independente da cópia da fixture, sem passar pelo módulo:

```sh
python3 - <<'PY'
d = open("work/mcr-entrada.mcr", "rb").read()
base = 0x5910
print([j for j in range(23) if 0 not in d[base + 32*j : base + 32*j + 10]])
PY
# [5, 20]
```

| slot | bytes | cp932 |
|---:|---|---|
| 5 | `83 57 ae b0 a5 db da dd bf dd` | `ジｮｰ･ﾛﾚﾝｿﾝ` |
| 20 | `83 4b d8 bd a5 db 83 6f b0 bd` | `ガﾘｽ･ﾛバｰｽ` |

E o que o documento diz:

```
$ grep -n 'slot 20' docs/PLAN-MCR-PY.md
167:E o campo **não é cadeia terminada em NUL**: o slot 20 usa os 10 bytes. O
```

Todo o resto da task remediu exato — os 23 dorsais lidos com leitor próprio dão
`1 5 4 3 2 7 6 11 10 9 8 16 17 13 19 22 12 18 20 14 15 21 23`, o slot 24 guarda
0 e lê 1, os 23 nomes reencodam byte a byte, e o `KanjiToAscii` transcrito à
mão devolve **23/23 em branco e 0 reproduzidos**.

## Causa raiz

A medição original citou o exemplo que apareceu primeiro e a frase virou
enumeração ao ser copiada para a task.

## Correção

### Arquivo: `docs/PLAN-MCR-PY.md` (§1.6)

```markdown
E o campo **não é cadeia terminada em NUL**: os slots **5** (`ジｮｰ･ﾛﾚﾝｿﾝ`) e
**20** (`ガﾘｽ･ﾛバｰｽ`) usam os dez bytes. São dois na fixture, e
`python3 tools/mcr/text.py <cartão> --check` marca os dois com
`<-- fills all ten bytes` — a contagem sai da ferramenta, não desta frase.
```

### Arquivo: `docs/tasks/port-mcr/07-dorsais-e-nome.md`

A mesma correção no Contexto e no critério — "inclusive os slots 5 e 20, que
enchem os dez bytes".

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-MCR-PY.md` | modificar (§1.6) |
| `docs/tasks/port-mcr/07-dorsais-e-nome.md` | modificar |

## Verificação

- [ ] `python3 tools/mcr/text.py work/mcr-entrada.mcr --check` continua
      `23/23`, marcando **dois** slots com `fills all ten bytes`
- [ ] a varredura independente devolve `[5, 20]`
- [ ] o plano e a task nomeiam os dois
- [ ] `roms/` e `work/entrada.mcr` intocados — digest
      `e53f4895affe075bced499a32ba736d10a20f72b010c9c8c05c1269e77c47546`

## Log de Execução

**Executado em:** 2026-09-07

**Resumo do que foi feito:**

A §1.6 do plano e as quatro ocorrências da MCR-TASK-07 passaram a nomear os
**dois** slots que enchem os dez bytes — o **5** (`ジｮｰ･ﾛﾚﾝｿﾝ`) e o **20**
(`ガﾘｽ･ﾛバｰｽ`) — e a frase do plano agora diz de onde sai a contagem: do
`text.py --check`, que marca os dois com `<-- fills all ten bytes`, não da
prosa. A afirmação de invariante ("não é cadeia terminada em NUL") já estava
certa e ficou; o que era incompleto era a enumeração.

**Medições:**

| gate | resultado |
|---|---|
| varredura independente da fixture | `[5, 20]` |
| `text.py --check` | `23/23`, com **2** slots marcados `fills all ten bytes` |
| `check_tasks.py` / `ctest -R tasks` | `100 task(s), ok` / `1/1 Passed` |
| fixture | `e53f4895…`, inalterada |

**Problemas encontrados:**

**Um terceiro sítio que a CORR não listava**, achado pela varredura: a tabela
"Estado medido" do
[`progresso.md`](/docs/tasks/port-mcr/progresso.md) do ciclo, linha 152, também
dizia "o slot 20 usa os 10 bytes sem terminador". Corrigido na mesma passagem.
Depois disso o termo só sobrevive na descrição do sintoma dentro do próprio
`correcoes-progresso.md`, que é evidência.

**Arquivos criados/modificados:**

- `docs/PLAN-MCR-PY.md` — §1.6
- `docs/tasks/port-mcr/07-dorsais-e-nome.md` — Contexto, critério e as duas
  passagens do Log
- `docs/tasks/port-mcr/progresso.md` — a linha "Nome" da tabela "Estado medido"
  (discrepância da varredura)
