---
id: CORR-PES2-001
title: "Correção: o -EL do objdump não é o que a §3.2 diz que é — quem mente é o -EB"
type: correção
category: infra
status: pendente
depends_on: []
---

# CORR-PES2-001: o `-EL` do `objdump` não é o que a §3.2 diz que é

## Problema identificado

A §3.2 do [plano](/docs/PLAN-PES2-PSX.md) e o Log da
[PES2-TASK-01](/docs/tasks/01-ferramental-das-fases-3-e-4.md) afirmam, como
coisa **medida em 2026-09-01**:

> `objdump` precisa de `-b binary -m mips:3000 -EL`: sem o `-EL` a saída é MIPS
> big-endian sobre bytes little-endian, e ela **não** falha, só mente.

Medido de novo em 2026-09-01, contra o mesmo `/SLES_039.57` da release
`(EsIt)`: **omitir o `-EL` não muda uma instrução sequer.** O
`mipsel-linux-gnu-objdump` 2.42 já tem alvo little-endian por default
(`elf32-tradlittlemips`), então `-EL` é redundante nesse binário.

Quem produz a saída plausível-e-errada é o **`-EB`**, que a §3.2 não menciona.
A lição está certa — "não falha, só mente" — e está pendurada no flag errado.

## Evidência

Perímetro de 4 KiB a partir do `pc0`, com e sem `-EL`, só a coluna de mnemônico:

```
$ mipsel-linux-gnu-objdump -D -b binary -m mips:3000 -EL \
    --adjust-vma=0x8000f800 --start-address=0x80010000 \
    --stop-address=0x80011000 SLES_039.57 | cut -f3- > a.txt
$ mipsel-linux-gnu-objdump -D -b binary -m mips:3000 \
    --adjust-vma=0x8000f800 --start-address=0x80010000 \
    --stop-address=0x80011000 SLES_039.57 | cut -f3- > b.txt
$ diff a.txt b.txt && echo IDENTICAL
IDENTICAL
```

1.017 linhas de cada lado, mnemônicos idênticos. O que muda é **só** a coluna
de palavra crua, exibida com os bytes trocados:

```
com -EL:   80010000:  03e00008   jr   ra
sem -EL:   80010000:  0800e003   jr   ra
```

Com `-EB`, aí sim a decodificação mente — e mente de forma convincente, com
alvo de salto que parece endereço de código:

```
$ mipsel-linux-gnu-objdump -D -b binary -m mips:3000 -EB \
    --adjust-vma=0x8000f800 --start-address=0x80010000 SLES_039.57
80010000:  0800e003   j      0x8003800c
80010008:  0680023c   bltz   s4,0x800108fc
8001000c:  400a4224   .word  0x400a4224
80010010:  0880033c   j      0x82000cf0
```

Contra o que o laço de zeragem de BSS realmente é (as duas ferramentas
concordam, e a §3.2 transcreve certo):

```
80010008:  lui   v0,0x8006
8001000c:  addiu v0,v0,2624
80010010:  lui   v1,0x8008
80010014:  addiu v1,v1,-8624
80010018:  sw    zero,0(v0)
8001001c:  addiu v0,v0,4
80010020:  sltu  at,v0,v1
80010024:  bnez  at,0x80010018
```

Default do binário, para fechar a causa:

```
$ mipsel-linux-gnu-objdump -i | head -3
BFD header file version (GNU Binutils for Ubuntu) 2.42
elf32-tradlittlemips
 (header little endian, data little endian)
```

O `objdump` genérico do host não entra na conta — ele nem aceita o alvo:
`objdump: can't use supplied machine mips:3000`.

## Causa raiz

O flag foi anotado pelo que se esperava dele, não pelo que a ausência dele
produziu: ninguém rodou a variante sem `-EL` para ver se a saída mudava.

## Correção

### Arquivo: `docs/PLAN-PES2-PSX.md` (§3.2)

Trocar a frase do `-EL` por uma que diga o que foi medido, sem perder a lição:

> `objdump` desmonta com `-b binary -m mips:3000`. O `-EL` é **redundante**
> neste host — o `mipsel-linux-gnu-objdump` já tem alvo `elf32-tradlittlemips`
> —, e vale mantê-lo explícito porque o mesmo comando com um `objdump` de alvo
> big-endian sai errado. Quem mente é o **`-EB`**: ele não falha, decodifica
> `j 0x8003800c` e `bltz s4,...` sobre o mesmo laço de BSS, alvo de salto que
> parece endereço e não é.

O bloco de comando pode ficar como está — manter o `-EL` explícito é a escolha
certa; o que muda é a razão escrita ao lado dele.

### Arquivo: `docs/tasks/01-ferramental-das-fases-3-e-4.md`

Mesma correção no terceiro marcador do Log, que é de onde a frase do plano
saiu. Log é registro do que aconteceu: corrigir a afirmação, e dizer em uma
linha que a remedição veio da revisão.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-PES2-PSX.md` | modificar (§3.2) |
| `docs/tasks/01-ferramental-das-fases-3-e-4.md` | modificar (Log) |

## Verificação

- [ ] O `diff` de mnemônicos com e sem `-EL` continua `IDENTICAL`, e o texto do
      plano concorda com isso
- [ ] O bloco de `-EB` do plano reproduz: `j 0x8003800c` na primeira linha
- [ ] `python3 tools/check_tasks.py` verde
- [ ] `roms/` intocada — a extração vai para o scratchpad, via
      `iso.py extract ... -o`

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
