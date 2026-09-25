---
id: CORR-LOOKS-090
title: "Retitular a task: a medição desmentiu 'quando a linha é de cabeça'"
origin: LOOKS-TASK-40
severity: low
files: [docs/tasks/looks/40-a-camera-do-close-up.md, docs/tasks/looks/progresso.md]
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-25
done_commit: 73d81b00
---

# CORR-LOOKS-090 — Retitular a task: a medição desmentiu 'quando a linha é de cabeça'

Origin: [LOOKS-TASK-40](/docs/tasks/looks/40-a-camera-do-close-up.md)

## Problema identificado

A medição da própria task é que **seis** linhas aproximam, e uma delas, o
`BOOTS`, não é linha de cabeça. O log diz isso ("o título desta task supõe
'linha de cabeça', e o jogo aproxima em seis linhas"), e o plano, a armadilha
67 do perfil e o `CLAUDE.md` foram corrigidos — mas o `title:` do frontmatter
não. É a string que a tabela gerada do `progresso.md` renderiza, então o resumo
de uma linha de uma task fechada ainda afirma o que ela desmentiu.

## Evidência

```text
$ sed -n '3p' docs/tasks/looks/40-a-camera-do-close-up.md
title: "A câmera do close-up — o painel aproxima na cabeça quando a linha é de cabeça"

$ sed -n '86p' docs/tasks/looks/progresso.md
| [LOOKS-TASK-40](...) | A câmera do close-up — o painel aproxima na cabeça quando a linha é de cabeça | 10 | ...

$ grep -n "^67\. " docs/prompts/perfil-looks.md
67. **A câmera do painel muda com a linha sob o cursor, e são seis linhas, não cinco.**
```

## Causa raiz

O título foi escrito a partir da suposição, antes de as doze linhas serem
andadas, e corrigi-lo não fez parte do fechamento.

## Correção

Trocar o `title:` do frontmatter pela afirmação medida (por exemplo, "o painel
aproxima nas seis linhas em que o jogo aproxima") e regerar as views com `rite
sync`, para a linha da tabela acompanhar. A mesma redação serve à linha da
lista da [CORR-LOOKS-089](/docs/tasks/looks/CORR-LOOKS-089.md).

## Arquivos

- docs/tasks/looks/40-a-camera-do-close-up.md
- docs/tasks/looks/progresso.md

## Verificação

`grep -rn "linha é de cabeça" docs/tasks/looks/` não devolve nada fora da
narrativa do Contexto e dos Problemas encontrados, e `python
tools/check_tasks.py` segue em `0 error(s)`.

## Log de Execução

### 2026-09-25 — triagem inline (`/rite:fix-all looks --plan`, Rite 0.8.0)

**REPRODUCED**, decidido inline por `rite reproduce --all --cycle looks --json` na HEAD `de066fd5`.

As três saídas são as registradas.

```text
$ sed -n '3p' docs/tasks/looks/40-a-camera-do-close-up.md
title: "A câmera do close-up — o painel aproxima na cabeça quando a linha é de cabeça"
$ sed -n '86p' docs/tasks/looks/progresso.md
| [LOOKS-TASK-40](/docs/tasks/looks/40-a-camera-do-close-up.md) | A câmera do close-up — o painel aproxima na cabeça quando a linha é de cabeça | 10 | implementação | LOOKS-TASK-28 | done | 2026-09-23 | 2026-09-23 |
$ grep -n "^67\. " docs/prompts/perfil-looks.md
618:67. **A câmera do painel muda com a linha sob o cursor, e são seis linhas,
```

### 2026-09-25 — triagem inline (`/rite:fix-all looks CORR-LOOKS-089 CORR-LOOKS-090`, Rite 0.9.1)

**REPRODUCED**, decidido inline por `rite reproduce CORR-LOOKS-090 --cycle looks --json` na HEAD `da9c76c5`. Saída idêntica à da entrada anterior.

### 2026-09-25 — correção (worker, `/rite:fix-all looks CORR-LOOKS-089 CORR-LOOKS-090`, Rite 0.9.1)

Linha 3 do frontmatter de `docs/tasks/looks/40-a-camera-do-close-up.md` trocada pela afirmação
medida, alinhada com a linha da Fase 10 do `progresso.md` ("seis das doze aproximam"). O H1
(`# LOOKS-TASK-40: A câmera do close-up`) não repetia a suposição e ficou como estava; Contexto
e Log da task não foram reescritos.

```text
$ sed -n '3p' docs/tasks/looks/40-a-camera-do-close-up.md
title: "A câmera do close-up — o painel aproxima nas seis linhas em que o jogo aproxima"
$ grep -rn "linha é de cabeça" docs/tasks/looks/40-a-camera-do-close-up.md; echo "rc=$?"
rc=1
$ python tools/check_tasks.py
ERROR docs/tasks/looks/progresso.md: generated table out of sync with item frontmatter (run: rite.py sync)
... (14 WARN pré-existentes: CORR-LOOKS-092/093 e PAR-TASK-01..11)
check: 1 error(s), 14 warning(s) in 4 cycle(s)
```

O único erro é a tabela gerada do `progresso.md` (linha 86), que acompanha o título novo quando o
`rite sync` rodar; a Verificação (`0 error(s)`) fecha depois disso.
- **Closed** — commit `73d81b00` (2026-09-25): docs(looks): retitle LOOKS-TASK-40 to the measured claim
  - Files (`git show --name-status 73d81b00`):
    - `M docs/tasks/looks/40-a-camera-do-close-up.md`
    - `M docs/tasks/looks/CORR-LOOKS-090.md`
    - `M docs/tasks/looks/progresso.md`
