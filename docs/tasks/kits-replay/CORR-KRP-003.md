---
id: CORR-KRP-003
---

# CORR-KRP-003 — PLAN §2.2 diz nove controles movidos para o leitor; na fase 1 foram onze

Origin: [KRP-TASK-03](/docs/tasks/kits-replay/03-fechamento-da-fase-1.md)

## Problem

O parágrafo "Feito na fase 1" que o commit 74018c42 acrescentou à §2.2 do
[PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#2.2) diz que "nove controles passaram a plantar no
leitor". Nove é só o que a KRP-TASK-01 moveu. A KRP-TASK-02 moveu mais dois
(`oracle-back-byte-order` e `oracle-pose-texel-order`), então na fase 1 foram 11 controles que
plantavam em `kits/oracle.py` e agora plantam em `kits/core/replay.py`.

O leitor tem 13 controles no total. Os outros 2 são novos: `replay-key-check` e `replay-v0-slot`.

## Evidência

```text
$ for c in a51525f0^ a51525f0 09203255^ HEAD; do echo "$c: $(git show "${c}:tools/kits/controls.py" | grep -cE '^\s*"[^"]+", "kits/core/replay.py"')"; done
a51525f0^: 0
a51525f0: 11
09203255^: 11
HEAD: 13
$ grep -c 'nove controles passaram' docs/PLAN-KITS-REPLAY.md
1
```

No diff das linhas controle→alvo entre a51525f0^ e HEAD, 11 entradas passam de `kits/oracle.py` a
`kits/core/replay.py`: 9 no a51525f0 e 2 no 09203255. Entram 3 novas: `replay-key-check`,
`replay-v0-slot` e `replay-copy-in-oracle`.

## Root cause

(Hipótese, não provada.) O número foi copiado do Log da KRP-TASK-01, escrito antes de a KRP-TASK-02
mover mais dois controles, e não foi recontado na HEAD para a fase inteira.

## Fix

Trocar o item da §2.2 por "onze controles passaram a plantar no leitor (nove na KRP-TASK-01, dois
na KRP-TASK-02), e dois novos plantam nele". Também serve remeter ao comando que conta, em vez de
repetir o número.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-REPLAY.md`

## Verificação

```sh
grep -c 'nove controles passaram' docs/PLAN-KITS-REPLAY.md
```

Hoje dá 1. Depois do conserto tem de dar 0.

Para conferir o número corrigido:

```sh
diff <(git show a51525f0^:tools/kits/controls.py | grep -oE '^\s*"[^"]+", "kits/[^"]+"') <(grep -oE '^\s*"[^"]+", "kits/[^"]+"' tools/kits/controls.py) | grep -c '^>.*kits/core/replay.py'
```

Ele dá 13: os 11 movidos mais os 2 novos.

## Log de Execução

2026-10-13 — reproduzida (`rite reproduce CORR-KRP-003`): a contagem por commit dá `a51525f0^: 0`,
`a51525f0: 11`, `09203255^: 11`, `HEAD: 13`, e `grep -c 'nove controles passaram'` dá `1`.

Recontagem por task, com as linhas controle→alvo de `tools/kits/controls.py` ordenadas e
comparadas (`git show "${c}:tools/kits/controls.py" | grep -oE '^\s*"[^"]+", "kits/[^"]+"'`):

- `a51525f0^` → `a51525f0` (KRP-TASK-01): nove saem de `kits/oracle.py` com prefixo `oracle-replay-`
  e voltam em `kits/core/replay.py` sem o `oracle-`; entram `replay-key-check` e `replay-v0-slot`;
- `a51525f0` → `09203255^`: nada;
- `09203255^` → HEAD (KRP-TASK-02): `oracle-back-byte-order` e `oracle-pose-texel-order` trocam
  `kits/oracle.py` por `kits/core/replay.py`; entra `replay-copy-in-oracle`, com alvo no oracle.

Conserto: o item da §2.2 diz onze movidos (nove mais dois, com os nomes dos dois) e dois novos, e
remete ao `grep` que conta os 13. Varredura: `grep -rniE "nove controles|9 controles|nine
controls"` em plano, perfil, ciclo e `tools/kits/` só acha o Log da KRP-TASK-01, que fala dos nove
dela e está certo.

Verificação:

```text
$ grep -c 'nove controles passaram' docs/PLAN-KITS-REPLAY.md
0
$ grep -cE '^\s*"[^"]+", "kits/core/replay.py"' tools/kits/controls.py
13
$ diff <(git show a51525f0^:tools/kits/controls.py | grep -oE '^\s*"[^"]+", "kits/[^"]+"') <(grep -oE '^\s*"[^"]+", "kits/[^"]+"' tools/kits/controls.py) | grep -c '^>.*kits/core/replay.py'
13
```

Gates (`rite gates --cycle kits-replay --id CORR-KRP-003`): `ctest --test-dir build -R kits` —
`100% tests passed, 0 tests failed out of 4` (`kits_image` e `kits_ui` *skipped*); `python3
tools/kits/controls.py` — `controls: 56 of 56 red`.
- **Closed** — commit `ee00001f` (2026-10-13): docs(kits): eleven controls moved to the replay reader in phase 1, not nine
  - Files (`git show --name-status ee00001f`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/CORR-KRP-003.md`
