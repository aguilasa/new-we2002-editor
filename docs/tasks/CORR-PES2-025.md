---
id: CORR-PES2-025
title: "Correção: a §3.2 do plano ainda chama a morada do fork de \"item aberto da PES2-TASK-34\""
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-PES2-025: uma linha da §3.2 ficou para trás da reconciliação da §6.14

## Problema identificado

A tabela do emulador na §3.2 do
[`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md), linha 1004, diz:

```
| binário de trabalho, desde 2026-09-03 | o **fork** ... Decisão e
consequências na §6.14; onde ele passa a morar é item aberto da
[PES2-TASK-34](/docs/tasks/34-rotas-mcp-no-lugar-do-drive.md) |
```

A PES2-TASK-34 fechou esse item em 2026-09-03, e a própria §6.14 registra o
resultado duas mil linhas abaixo:

> **Onde o binário mora.** `~/Applications/duckstation-mcp/`, escolhido pelo
> usuário, ao lado do AppImage oficial que continua instalado.

O `CLAUDE.md` e o `perfil-pes2.md` já dizem o mesmo. Só a §3.2 continua
descrevendo o item como aberto — e ela é a tabela que alguém abre primeiro
quando quer saber onde o emulador está.

## Evidência

A única ocorrência viva:

```
$ grep -n "item aberto" docs/PLAN-PES2-PSX.md
1004:| binário de trabalho, desde 2026-09-03 | ... onde ele passa a morar é
item aberto da [PES2-TASK-34](...) |
```

Contra o que está no disco:

```
$ ls ~/Applications/duckstation-mcp/
bin  COMMIT  lib  plugins
$ python3 tools/pes2/fork.py which
/home/ingmar/Applications/duckstation-mcp/bin/duckstation-qt
```

O resto da seção que a task tocou **foi** reconciliado — a §6.14 marca os
seis itens como fechados e diz onde cada um foi parar, inclusive os dois que
estavam errados.

## Causa raiz

A varredura de reconciliação da task cobriu a §6.14, o `CLAUDE.md` e o
perfil, e não voltou à §3.2, que fala do emulador num contexto diferente
(infra da Fase 0).

## Correção

### Arquivo: `docs/PLAN-PES2-PSX.md`, §3.2, linha 1004

Substituir a oração final pelo lugar, já que ele é conhecido:

```
| binário de trabalho, desde 2026-09-03 | o **fork** `sadnescity/duckstation`,
branch `mcp`, compilado localmente — é o único com servidor MCP. Mora em
`~/Applications/duckstation-mcp/`, fora do repositório por licença; sobe pelo
`tools/pes2/fork.py`, e `fork.py recipe` diz como reconstruí-lo. Decisão e
consequências na §6.14 |
```

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-PES2-PSX.md` | modificar |

## Verificação

- [x] `grep -n "item aberto" docs/PLAN-PES2-PSX.md` não devolve nada
- [x] a §3.2 e a §6.14 dizem o mesmo caminho, e ele bate com
      `python3 tools/pes2/fork.py which`
- [x] nenhum caminho do fork entrou no repositório

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-09-03

**Resumo do que foi feito:** a oração final da linha 1004 da §3.2 foi
substituída pelo lugar. A tabela do emulador agora diz onde o fork mora
(`~/Applications/duckstation-mcp/`), por que ele não está no repositório
(licença CC-BY-NC-ND-4.0, mesma regra de `roms/`), quem o sobe
(`tools/pes2/fork.py`) e onde está a receita de reconstruí-lo
(`fork.py recipe`) — que é o conjunto que a §6.14, o `CLAUDE.md` e o perfil
já traziam, e que faltava justamente na tabela que se abre primeiro para
saber onde o emulador está.

**Problemas encontrados:** nenhum. A varredura por `duckstation-mcp` mostrou
que os outros quatro lugares (§6.14, perfil, e duas linhas do `CLAUDE.md`) já
concordavam entre si; a §3.2 era o único fora.

**Gates:**

```
$ grep -n "item aberto" docs/PLAN-PES2-PSX.md
(vazio)
$ python3 tools/pes2/fork.py which
/home/ingmar/Applications/duckstation-mcp/bin/duckstation-qt
installed
```

O caminho impresso pela ferramenta bate com o escrito na §3.2 e na §6.14.
`git ls-files | grep -i duckstation` devolve só o markdown da PES2-TASK-32 e
o `run_duckstation.sh` — nenhum binário nem árvore do fork no repositório.

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `docs/PLAN-PES2-PSX.md` | modificado (§3.2, linha 1004) |
