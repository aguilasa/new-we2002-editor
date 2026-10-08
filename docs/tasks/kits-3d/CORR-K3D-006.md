---
id: CORR-K3D-006
---

# CORR-K3D-006 — Edição na K3D-TASK-14 fora do escopo e fora do Log da 13

Origin: [K3D-TASK-13](/docs/tasks/kits-3d/13-rasterizador-nucleo.md)

## Problem

O commit `3982070` da [K3D-TASK-13](/docs/tasks/kits-3d/13-rasterizador-nucleo.md) muda
`docs/tasks/kits-3d/14-vista-rasterizador.md`, arquivo fora do `files` declarado da 13, e
o Log de Execução não menciona a edição; só o registro de fechamento do Rite a acusa em
"Outside declared files". A edição acrescenta uma nota de passagem: a assinatura de
`api.draw_figure`, o tempo de sonda tratado na correção irmã, e uma pendência de
atualizar a tabela do G5.

## Evidência

```text
$ git show --stat 3982070 | grep 14-vista
 docs/tasks/kits-3d/14-vista-rasterizador.md  |   4 +-
$ grep -n '14-vista-rasterizador' docs/tasks/kits-3d/13-rasterizador-nucleo.md
129:    - `M docs/tasks/kits-3d/14-vista-rasterizador.md`
137:    - `docs/tasks/kits-3d/14-vista-rasterizador.md`
```

As duas linhas são do registro gerado pelo Rite; o Log escrito não nomeia a edição.

## Root cause

Hipótese: a nota de varredura para a task seguinte foi para o arquivo dela dentro do
commit de trabalho e não foi declarada.

## Fix

Nomear no Log de Execução da K3D-TASK-13 a edição em `14-vista-rasterizador.md` como a
varredura que ela é. Para os próximos itens, pôr o arquivo da task seguinte no `files`
(via `rite set`) quando houver nota de passagem planejada.

## Arquivos a criar ou modificar

- docs/tasks/kits-3d/13-rasterizador-nucleo.md

## Verificação

```sh
grep -n '14-vista-rasterizador' docs/tasks/kits-3d/13-rasterizador-nucleo.md
```

Hoje só imprime as linhas 129 e 137, do registro gerado; depois, também a linha do Log
que nomeia a edição.

## Log de Execução

- 2026-10-08 — triagem inline: **REPRODUCED**. `git show --stat 3982070` lista
  `14-vista-rasterizador.md | 4 +-`; o `grep` só achava as linhas do registro gerado.
- Log da K3D-TASK-13 com um parágrafo "Varredura fora do `files`" nomeando a edição e o que ela
  leva. Verificação: o `grep` agora acha também a linha 140, do Log escrito.
- **Closed** — commit `79954f3` (2026-10-08): docs(kits): name the K3D-TASK-14 note edit in the K3D-TASK-13 log
  - Files (`git show --name-status 79954f3`):
    - `M docs/tasks/kits-3d/13-rasterizador-nucleo.md`
    - `M docs/tasks/kits-3d/CORR-K3D-006.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
