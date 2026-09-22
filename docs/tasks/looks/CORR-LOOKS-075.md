---
id: CORR-LOOKS-075
title: "As linhas de --keys do log não rodam como estão escritas"
origin: LOOKS-TASK-38
severity: medium
files: [docs/tasks/looks/38-o-alinhamento-dos-valores.md]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
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

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `edb4dbfa`: **reproduzida**.

```text
$ python tools/looks/oracle.py --keys "<Right x10>" 2
oracle FAILED: '<Right x10>' is not one of the four this screen answers to: Up, Down, Left, Right   (saída 1)
$ python tools/looks/oracle.py --keys "Right,Right,Right,Right,Right,Right,Right,Right,Right,Right" 2
  control: ... the same 117 glyph(s)
    NAT       'Swi'
oracle --keys: 0 difference(s) after 10 press(es), across the game, screen.json and our window   (saída 0)
```

Correção de contagem: são **três** linhas abreviadas, não quatro — 139, 141 e
143 do arquivo da task. A 135 passa string vazia (a sequência padrão de 19) e a
145 é `"Up,Left"`; as duas rodam.

**Corrigido em 2026-09-22**, pelo menor escopo dos dois que a Correção oferece:
as três linhas foram escritas com as teclas separadas por vírgula, e o
`parse_keys` não mudou. A transcrição **abaixo** de cada linha é de uma corrida
de verdade e ficou como estava; o que mudou é a linha `$` que a produziu.

**A divisão entre `Down` e `Right` da abreviação não bate com o alvo que o
próprio comentário de cada linha nomeia**, e o alvo é que decidiu a expansão. A
tela carrega com o cursor em `NAT` (`screen.json`, `initial`), e as linhas vêm
na ordem `DEFAUL, NAT, SKIN, HAIR, H.COL, FACE, H.F.COL., HEIG, BODY, AGE,
BOOTS, FOOT`:

| abreviação | teclas | onde ela para | o comentário diz | expansão escrita |
| --- | --- | --- | --- | --- |
| `<Right x10>` | 10 | `NAT` em `Swi` | NAT numa nação | `Right` ×10 |
| `<Down x7, Right x40>` | 47 | `BODY` em `H TYPE` | `HEIG` em 210 cm | `Down` ×6 + `Right` ×41 |
| `<Down x2, Right x30>` | 32 | `HAIR` em `O1 TYPE` | `SKIN` na ponta | `Down` ×1 + `Right` ×31 |

As duas expansões preservam a **contagem de teclas** da transcrição (47 e 32) e
levam à **linha nomeada**; o `Right` a mais só encosta na ponta, que trava (a
tela não dá a volta). Não dá para saber, da transcrição elidida (`, ...`), qual
das duas divisões rodou em 2026-09-22 — as duas imprimiriam a mesma linha —, e
por isso a escolha está dita aqui e no arquivo da task, em vez de calada.

As cinco linhas `--keys` foram então **extraídas do arquivo da task por `grep` e
rodadas como estão** (`grep '^\$ python …' 38-*.md | sed 's/^\$ //'`, cada uma
por `eval`), com `WE2002_LOOKS_IMAGE` na trilha japonesa e
`WE2002_LOOKS_DRIVE_IMAGE` no `.cue` inglês:

```text
=== python tools/looks/oracle.py --keys "" 2             # e 1
    NAT 'Unknown'   SKIN 'C TYPE'   HEIG '178 cm'
oracle --keys: 0 difference(s) after 19 press(es), across the game, screen.json and our window
exit=0
=== python tools/looks/oracle.py --keys "Right,Right,…,Right" 2  # NAT numa nacao
    NAT 'Swi'       SKIN 'A TYPE'   HEIG '175 cm'
oracle --keys: 0 difference(s) after 10 press(es), across the game, screen.json and our window
exit=0
=== python tools/looks/oracle.py --keys "Down,…,Down,Right,…,Right" 2  # HEIG em 210 cm
    NAT 'Unknown'   SKIN 'A TYPE'   HEIG '210 cm'
oracle --keys: 0 difference(s) after 47 press(es), across the game, screen.json and our window
exit=0
=== python tools/looks/oracle.py --keys "Down,Right,…,Right" 2   # SKIN na ponta
    NAT 'Unknown'   SKIN 'D TYPE'   HEIG '175 cm'
oracle --keys: 0 difference(s) after 32 press(es), across the game, screen.json and our window
exit=0
=== python tools/looks/oracle.py --keys "Up,Left" 2              # o rotulo do DEFAUL
    NAT 'Unknown'   SKIN 'A TYPE'   HEIG '175 cm'
oracle --keys: 0 difference(s) after 2 press(es), across the game, screen.json and our window
exit=0
```

(As três linhas das teclas por extenso estão abreviadas **aqui** com `…` para
caber na página; no arquivo da task elas estão inteiras, e é de lá que o `grep`
as tirou. O controle de cada corrida — a mesma sequência duas vezes no jogo —
fechou antes de qualquer comparação, como o `--keys` exige.)
