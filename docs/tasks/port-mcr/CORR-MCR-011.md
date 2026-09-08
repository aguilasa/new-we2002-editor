---
id: CORR-MCR-011
title: "Correção: a tabela de controles da MCR-TASK-07 voltou à prosa, e a linha ambígua custa duas tentativas"
type: correção
category: verificação
status: pendente
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

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
