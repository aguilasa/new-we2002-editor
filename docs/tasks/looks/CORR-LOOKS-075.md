---
id: CORR-LOOKS-075
title: "As linhas de --keys do log não rodam como estão escritas"
origin: LOOKS-TASK-38
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-075 — As linhas de --keys do log não rodam como estão escritas

Origin: [LOOKS-TASK-38](/docs/tasks/looks/38-o-alinhamento-dos-valores.md)

## Problema identificado

Quatro das cinco linhas `--keys` do Log de Execução da LOOKS-TASK-38 usam uma
abreviação de repetição (`"<Right x10>"`, `"<Down x7, Right x40>"`,
`"<Down x2, Right x30>"`) que o `screen.parse_keys` recusa: rodadas como estão
escritas, elas erram em vez de medir. A quinta, `"Up,Left"`, roda. As medições
em si se reproduzem — o que não roda é a transcrição.

## Evidência

```text
$ python tools/looks/oracle.py --keys "<Right x10>" 2
oracle FAILED: '<Right x10>' is not one of the four this screen answers to: Up, Down, Left, Right

$ python tools/looks/oracle.py --keys "Right,Right,Right,Right,Right,Right,Right,Right,Right,Right" 2
  control: ... the same 117 glyph(s)
    NAT       'Swi'
oracle --keys: 0 difference(s) after 10 press(es), across the game, screen.json and our window
```

## Causa raiz

O log abreviou as teclas repetidas à mão; o `parse_keys`
(`tools/looks/screen.py:1084-1091`) não tem sintaxe de repetição.

## Correção

Reescrever as quatro linhas `$` do bloco de Evidência com as teclas separadas
por vírgula realmente usadas — ou acrescentar a sintaxe de repetição ao
`parse_keys` e manter a abreviação.

## Arquivos

- docs/tasks/looks/38-o-alinhamento-dos-valores.md (Evidência, linhas 139-145)

## Verificação

Toda linha `$ python tools/looks/oracle.py --keys …` copiada do arquivo da task
sai com código 0.

## Log de Execução
