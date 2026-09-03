---
id: CORR-PES2-026
title: "Correção: o offset da RAM no fluxo inflado ficou em 6799; o leitor corrigido mede 6754"
type: correção
category: dados
status: pendente
depends_on: []
---

# CORR-PES2-026: a correção de 45 bytes arrumou os dois endereços e esqueceu o deslocamento

## Problema identificado

A §6.14 do [`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md), na descrição do save
state, diz:

> **O deslocamento é derivado, nunca presumido.** `Bus` abre com o tamanho da
> RAM em u32, e a RAM termina onde `DMA` começa, então o início é uma
> subtração; nos estados medidos ela cai no offset **6799** do fluxo inflado,
> mas esse número é resultado, não constante.

O Log da [PES2-TASK-32](/docs/tasks/32-poc-do-mcp-do-duckstation.md) repete o
mesmo 6799.

O `savestate.py` mede **6754** em todos os estados desta máquina — incluindo
um salvo hoje. A diferença é exatamente os **45 bytes** que a
[PES2-TASK-33](/docs/tasks/33-compilar-e-validar-o-mcp.md) corrigiu: a RAM não
é a última coisa que `Bus` escreve, `MEMCTRL.regs` e `RAM_SIZE.bits` vêm
depois dela. Aquela correção reescreveu os dois endereços do fluxo C
(`0x000714EE` → `0x0007151B`, `0x00137BE5` → `0x00137C12`, +45 cada) e
**não** reescreveu o deslocamento, que anda no sentido oposto: 6799 − 45 =
6754.

O número está marcado como "resultado, não constante", o que é a defesa
certa — mas ele continua sendo o valor que alguém confere quando o leitor
parece errado, e hoje ele confere contra o número de antes do conserto.

## Evidência

O que a ferramenta mede, nos oito estados que a POC usou mais um de hoje:

```
$ for f in scan/*.sav scan2/*.sav ~/.local/share/duckstation/savestates/SLES-03957_1.sav; do
      python3 tools/pes2/savestate.py info "$f" | grep '^  RAM'; done
  RAM               2097152 B at payload offset 6754      (x8, todos)
```

O que os documentos dizem:

```
$ grep -rn "6799" docs/ | grep -v concluidos
docs/PLAN-PES2-PSX.md:2104:subtração; nos estados medidos ela cai no offset 6799 do fluxo inflado, mas
docs/tasks/32-poc-do-mcp-do-duckstation.md:162:máquina cai em 6799, que é resultado e não constante.
```

A aritmética que liga os dois, e que fecha:

```
6799 - 45 = 6754              # a base desceu 45
0x000714EE + 45 = 0x0007151B  # e por isso o endereço subiu 45
0x00137BE5 + 45 = 0x00137C12
```

## Causa raiz

A varredura de reconciliação da PES2-TASK-33 procurou pelos **endereços**
publicados e não pelo **deslocamento** que os produzia — e os dois se movem
em sentidos opostos, então nenhum `grep` por um acha o outro.

## Correção

### Arquivo: `docs/PLAN-PES2-PSX.md`, §6.14

Trocar 6799 por 6754, e dizer de onde ele vem, para o próximo conserto de
base não deixar o número para trás de novo:

```markdown
subtração; nos estados desta máquina ela cai no offset **6754** do fluxo
inflado — medido por `savestate.py info`, e resultado, não constante. (Era
6799 até 2026-09-03: a PES2-TASK-33 achou os 45 bytes de `MEMCTRL.regs` e
`RAM_SIZE.bits` que vêm depois da RAM dentro de `Bus`. O deslocamento desce
45 e os endereços sobem 45 — quem reconciliar um tem de reconciliar o outro.)
```

### Arquivo: `docs/tasks/32-poc-do-mcp-do-duckstation.md`

Mesma troca no Log. O bloco **Corrigido em: 2026-09-03** já existe ali e é o
lugar certo para a menção.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-PES2-PSX.md` | modificar |
| `docs/tasks/32-poc-do-mcp-do-duckstation.md` | modificar |

## Verificação

- [ ] `grep -rn "6799" docs/ | grep -v concluidos` só devolve a menção
      histórica, nunca uma afirmação do valor corrente
- [ ] o número escrito bate com
      `python3 tools/pes2/savestate.py info <state.sav> | grep '^  RAM'`
- [ ] `python3 tools/pes2/savestate.py selftest` continua verde
- [ ] `ctest --test-dir build -R pes2_selftest` verde

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
