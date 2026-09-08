---
id: CORR-MCR-011
title: "Correção: a tabela de controles da MCR-TASK-07 voltou à prosa, e a linha ambígua custa duas tentativas"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-MCR-011: a convenção da CORR-MCR-009 não alcançou a task seguinte

## Problema identificado

A [CORR-MCR-009](/docs/tasks/port-mcr/CORR-MCR-009.md), aberta e fechada em
2026-09-07, estabeleceu que a tabela de controles negativos registra a
**substituição literal**, não a descrição do efeito — porque "trocar dois campos
no encoder" tem mais de uma leitura, e cada uma dá uma contagem de falhas
diferente.

A [MCR-TASK-07](/docs/tasks/port-mcr/07-dorsais-e-nome.md), escrita no mesmo
dia, traz a tabela de novo em prosa:

| módulo | defeito plantado | resultado |
|---|---|---|
| `numbers` | montar a tabela do zero em vez de RMW | 🔴 2 falhas (bits sobrando, slot 24) |

**As seis contagens estão certas** — replantadas nesta revisão, as seis
reproduzem exatamente: 7, 7, 2, 16, 1, 2, com `rc=1` nas seis. O problema é
outro: uma das seis descrições não identifica a linha, e a linha que ela descreve
**aparece duas vezes no arquivo**.

`raw = int.from_bytes(table, "little")` está na linha **70**, dentro de
`decode_table`, e na **93**, dentro de `encode_table`. Só a segunda é o
read-modify-write da gravação. Plantar na primeira — que é o que um
`replace(..., 1)` faz, e o que esta revisão fez na primeira tentativa — devolve
**6 falhas** em vez de 2, com o `--self-check` acusando que a fixture "reads
as the plan measured" falhou. O leitor conclui que o Log erra, e ele não erra.

## Evidência

Primeira tentativa, substituindo a **primeira** ocorrência:

```
  FAIL  a full table round-trips  got=[1, 1, 1, ...]
  FAIL  changing one slot leaves the other 23 alone  disturbed=[0..23]
  FAIL  writing 23 slots leaves slot 24 untouched
  FAIL  the fixture reads as the plan measured  got=[1, 1, 1, ...]
  FAIL  re-encoding the fixture table changes no byte
  FAIL  tripwire: 23/23 agree with the player records  differ=[...]
numbers.py: 6 failure(s)
```

Segunda tentativa, na linha 93 (`encode_table`), que é o controle que o Log
descreve:

```
  FAIL  the 2 spare bits of each group survive a write
  FAIL  writing 23 slots leaves slot 24 untouched
numbers.py: 2 failure(s)
```

Os outros cinco reproduzem de primeira, cada um com a contagem escrita:

| plantação | falhas |
|---|---:|
| `stored = number - STORED_BIAS` → `stored = number` | 7 |
| `_group_and_offset` devolvendo `(0,5,2,7,4,1)[within]` | 7 |
| `ENCODING = "cp932"` → `"ascii"` | 16 |
| `raw.rstrip(bytes([PAD]))` → `raw.split(bytes([PAD]))[0]` | 1 |
| `if len(raw) > NAME_BYTES:` → `if False:` | 2 |

## Causa raiz

A convenção da CORR-MCR-009 foi aplicada ao arquivo que a originou e não virou
regra do ciclo, então a task seguinte, escrita no mesmo dia, repetiu a forma
antiga.

## Correção

### Arquivo: `docs/tasks/port-mcr/07-dorsais-e-nome.md`

Trocar a coluna "defeito plantado" pelas substituições literais acima —
identificando a de `numbers` pela **função**, não só pela expressão:

```markdown
| `numbers` | `raw = int.from_bytes(table, "little")` → `raw = 0`, **na `encode_table`** (a mesma linha existe na `decode_table`, e plantar lá dá 6 falhas, não 2) | 🔴 2 falhas |
```

### Arquivo: `docs/prompts/perfil-mcr.md`

A convenção sobe para o perfil, onde as tasks 08 a 14 a leem antes de começar —
é o lugar do que é do ciclo:

```markdown
- **Controle negativo se registra pela substituição literal**, nunca pela
  descrição do efeito: a linha de origem, a de destino e a função onde ela mora.
  Duas contagens da MCR-TASK-06 e uma da MCR-TASK-07 não reproduziram da prosa
  ([CORR-MCR-009](/docs/tasks/port-mcr/CORR-MCR-009.md),
  [CORR-MCR-011](/docs/tasks/port-mcr/CORR-MCR-011.md)). E a cópia plantada roda
  com `PYTHONPATH=tools/mcr`, senão morre em `ModuleNotFoundError` antes de
  medir.
```

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/port-mcr/07-dorsais-e-nome.md` | modificar |
| `docs/prompts/perfil-mcr.md` | modificar |

## Verificação

- [ ] cada linha da tabela de controles da MCR-TASK-07 nomeia a substituição e a
      função, e replantar exatamente aquilo devolve a contagem escrita ao lado
- [ ] o perfil carrega a convenção, e ela não cita nenhuma task pelo número
      fora dos dois links de precedente
- [ ] `python3 tools/mcr/numbers.py work/mcr-entrada.mcr --check` continua
      `23/23`, e `text.py --check` continua `23/23`
- [ ] os dois `--self-check` continuam verdes — 17 e 23 asserções — e
      determinísticos
- [ ] `roms/` e `work/entrada.mcr` intocados

## Log de Execução

**Executado em:** 2026-09-07

**Resumo do que foi feito:**

A tabela dos seis controles da MCR-TASK-07 passou a trazer a **substituição
literal**, e a terceira linha nomeia a **função** — `raw = int.from_bytes(table,
"little")` → `raw = 0` **na `encode_table`** —, dizendo ao lado que a mesma
linha existe na `decode_table` e que plantar lá dá **6** falhas, não 2. Entrou
também a nota "Como replantar".

A convenção subiu para o `perfil-mcr.md`, entre as decisões confirmadas, onde as
tasks 08 a 14 a leem antes de começar: controle negativo se registra pela
substituição literal — origem, destino e a função onde ela mora.

**Medições — os seis controles replantados, com `PYTHONPATH=tools/mcr`:**

| substituição | falhas |
|---|---:|
| `stored = number - STORED_BIAS` → `stored = number` | 7 |
| `return group, WIDTH * within` → `(0, 5, 2, 7, 4, 1)[within]` | 7 |
| `raw = int.from_bytes(table, "little")` → `raw = 0`, na **`encode_table`** | **2** |
| a mesma, na **`decode_table`** — a leitura errada | **6** |
| `ENCODING = "cp932"` → `"ascii"` | 16 |
| `raw.rstrip(bytes([PAD]))` → `raw.split(bytes([PAD]))[0]` | 1 |
| `if len(raw) > NAME_BYTES:` → `if False:` | 2 |

**6/6 vermelhos, `rc=1`**, com as contagens que o Log já trazia — 7, 7, 2, 16,
1, 2. A ambiguidade da terceira linha confirma-se: 6 contra 2.

Os demais gates:

| gate | resultado |
|---|---|
| `numbers.py --self-check` | **17 asserções, 0 falhas**, determinístico |
| `text.py --self-check` | **23 asserções, 0 falhas**, determinístico |
| `numbers.py --check` / `text.py --check` | `23/23` nos dois |
| `check_tasks.py` / `ctest -R tasks` | `100 task(s), ok` / `1/1 Passed` |
| fixture | `e53f4895…`, inalterada |

**Problemas encontrados:**

**O meu próprio harness produziu o falso verde que esta CORR descreve**, e isso
merece registro porque é a prova do ponto. Ao replantar o segundo controle, meu
literal (`return group, within`) não casava com o fonte — a linha real é
`return group, WIDTH * within` —, e o script deixou a cópia **intacta**: a
corrida saiu `rc=0`, `0 falhas`. Lido depressa, parece um controle que não fica
vermelho; é o defeito não ter sido plantado. Por isso a nota "Como replantar"
manda **conferir que a substituição casou**, e a mesma frase foi para o perfil.

**Uma discrepância que a promoção ao perfil criou.** Com a convenção valendo
para o ciclo, duas linhas da tabela da
[MCR-TASK-05](/docs/tasks/port-mcr/05-layout-e-cross-check.md) deixaram de
cumpri-la — "tabela de cobradores em ordem crescente" e "deslocamentos
`(0,1,2,3,4,5)`" não dizem a linha. Foram para a forma literal, com as
substituições que a [CORR-MCR-008](/docs/tasks/port-mcr/CORR-MCR-008.md)
replantou e mediu, e o cabeçalho da coluna acompanhou.

A [MCR-TASK-04](/docs/tasks/port-mcr/04-conteiner-do-cartao.md) **ficou como
está, e cumpre a convenção**: as cinco linhas dela já são substituições
literais (`if offset < HEADER_BYTES:` → `if False:` e as outras quatro); só a
palavra do cabeçalho difere, e trocá-la mexeria numa tabela cuja nota datada
preserva de propósito o texto de uma corrida anterior.

**Arquivos criados/modificados:**

- `docs/tasks/port-mcr/07-dorsais-e-nome.md` — a tabela dos seis controles e a
  nota "Como replantar"
- `docs/prompts/perfil-mcr.md` — a convenção, entre as decisões confirmadas
- `docs/tasks/port-mcr/05-layout-e-cross-check.md` — duas linhas para a forma
  literal e o cabeçalho da coluna (discrepância criada pela promoção)
