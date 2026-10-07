---
id: CORR-K3D-001
---

# CORR-K3D-001 — Nota de varredura omite i18n work_set e SUPERPACK-UNIFORMES

Origin: [K3D-TASK-01](/docs/tasks/kits-3d/01-kit-home-away.md)

## Problem

A seção "Varredura" das notas da [K3D-TASK-01](/docs/tasks/kits-3d/01-kit-home-away.md)
afirma que "Set"/"Conjunto"/"titular"/"suplente" só sobram em `PLAN-KITS-PY.md` e na
seção "Hoje" do `KITS-AJUSTES-3D.md`. Na árvore, as palavras sobram também nas chaves
`work_set_1`/`work_set_2` do catálogo de i18n (pt-BR "1º/2º conjunto", en-US "1st/2nd
set") e em `docs/SUPERPACK-UNIFORMES.md`. Nenhuma delas é o seletor 3D, então o G1
não quebra — mas a frase de varredura, como está escrita, é falsa.

## Evidência

```text
$ grep -rnI -i 'conjunto\|titular\|suplente' tools/kits docs --include='*.py' --include='*.md' | grep -v concluidos | grep -v PLAN-KITS-PY | grep -v PLAN-PES2 | grep -v kits-3d | grep -v KITS-AJUSTES-3D | head -4
tools/kits/ui/i18n.py:112:        "work_set_1": "bitmap de trabalho, 1º conjunto",
tools/kits/ui/i18n.py:113:        "work_set_2": "bitmap de trabalho, 2º conjunto",
docs/SUPERPACK-UNIFORMES.md:34:| 1 | imagem 8 bpp | (576, 256) | 128×128 | uniforme **titular**: jogador + goleiro |
docs/SUPERPACK-UNIFORMES.md:35:| 2 | imagem 8 bpp | (576, 384) | 128×128 | mangas longas e braçadeira, **titular** |
```

## Root cause

Hipótese: a varredura cobriu só as chaves do seletor 3D e os dois documentos de
planejamento; não passou pelas outras chaves do catálogo nem pelas notas de formato.

## Fix

Reescrever o parágrafo "Varredura" da K3D-TASK-01 listando o que de fato sobra e por
que cada um fica (`work_set_1/2` rotulam a lista de bitmaps de trabalho, fora do G1;
`SUPERPACK-UNIFORMES.md` descreve o formato TEX), colando o `grep` que o sustenta. Se
o dono quiser que os rótulos de bitmap de trabalho também digam Casa/Visitante, isso é
task nova, não esta correção.

## Arquivos a criar ou modificar

- docs/tasks/kits-3d/01-kit-home-away.md

## Verificação

```sh
grep -rnI -i 'conjunto\|titular\|suplente' tools/kits docs --include='*.py' --include='*.md' | grep -v concluidos | grep -v PLAN-PES2 | grep -v kits-3d
```

Todo arquivo que aparecer precisa estar nomeado na nota de varredura da task. Hoje
falha em `tools/kits/ui/i18n.py` e `docs/SUPERPACK-UNIFORMES.md`.

## Log de Execução

- 2026-10-07 — triagem inline: **REPRODUCED**. O `grep` da Evidência ainda lista
  `tools/kits/ui/i18n.py:112-113`; o `head -4` agora corta antes do
  `SUPERPACK-UNIFORMES.md` (o `PLAN-WTE-LAZARUS.md` entra na frente com
  "subconjunto"), mas o arquivo continua no resultado sem o `head`.
- A varredura ampla da Verificação acha 44 arquivos, quase todos com "conjunto" em
  outro sentido. A nota foi reescrita sobre o recorte que importa — `titular|suplente`
  fora do arquivo morto, do `kits-3d` e do PES2, nove arquivos — mais o
  `i18n.py`, e cada um com o motivo de ficar. `rite check --cycle kits-3d`: 0 erros.
- **Closed** — commit `17c4581` (2026-10-07): docs(kits): list what the K3D-TASK-01 sweep leaves, and why
  - Files (`git show --name-status 17c4581`):
    - `M docs/tasks/kits-3d/01-kit-home-away.md`
    - `M docs/tasks/kits-3d/CORR-K3D-001.md`
