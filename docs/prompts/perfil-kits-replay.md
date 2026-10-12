# Profile — kits-replay

<!--
The cycle profile is read by every /rite command in this cycle. Keep it short
(rite.toml [profile].max_kb); dated pitfall histories go to the pitfalls file,
which commands search instead of reading whole.
-->

## Contexto essencial — decisões já confirmadas

<!-- Decisions the user confirmed. One line each, with the date and where it was decided. -->

- **A ferramenta de leitura de replay vem antes das melhorias do desenho**, porque elas a usam (usuário, 2026-10-12; [§10](/docs/PLAN-KITS-REPLAY.md#10)).
- **O goleiro passa a ser desenhado pela família 13**, com a pose medida e a 92 no lugar da 15; reabre a [K3D-TASK-10](/docs/tasks/concluidos/kits-3d/10-duas-figuras.md) (usuário, 2026-10-12; [§4](/docs/PLAN-KITS-REPLAY.md#4)).
- **Entram no ciclo** jogador real no seletor, vista dos dois times, câmera "replay" em perspectiva e `confront --tab` (usuário, 2026-10-12; [§0](/docs/PLAN-KITS-REPLAY.md#0)).
- **Faixa, manga, cor, paleta e sombreamento não mudam**: fechados pelas três investigações de replay ([§0](/docs/PLAN-KITS-REPLAY.md#0); [item (h)](/docs/KITS-REPLAYS-9-10.md#h-o-que-não-muda)).
- **Não inventa geometria nem UV**; só o medido entra no desenho ([§0 do PLAN-KITS-PY](/docs/PLAN-KITS-PY.md#0)).
- **O 3D é desenhado em software no núcleo e mostrado por `QPainter`; texto da UI só do `tools/kits/ui/i18n.py`** ([§3.4 do PLAN-KITS-PY](/docs/PLAN-KITS-PY.md#3.4); [§0](/docs/PLAN-KITS-REPLAY.md#0)).
- **O código de análise sai do `oracle.py` por move, não por cópia**; o oracle fica com os gates ([§2.2](/docs/PLAN-KITS-REPLAY.md#2.2)).

## Sources of truth

<!-- Plan sections, specs, reference outputs. Items point here through `source_of_truth`. -->

- [docs/PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md): o plano do ciclo.
- [docs/KITS-REPLAYS-9-10.md](/docs/KITS-REPLAYS-9-10.md): o relatório das medições de replay que o plano usa; os números ficam lá.
- [docs/PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md): valem o [§0](/docs/PLAN-KITS-PY.md#0), o [§3.4](/docs/PLAN-KITS-PY.md#3.4), o [§4.3](/docs/PLAN-KITS-PY.md#4.3) e o [§4.7](/docs/PLAN-KITS-PY.md#4.7).

## Generated artifacts

<!-- Output -> generator -> check command. Never edit the output. -->

## Gates deste ciclo

<!-- Commands that must pass before any item of this cycle closes (in addition to rite.toml [gates].global). -->

## Hot files

<!-- Files many items touch; batches serialize on them. -->

## Serialized resources

<!-- Cycle-specific resources that cannot be used by two workers at once (rite.toml [resources] has repo-wide ones). -->

## Pull-ahead precedents

<!-- When the user allowed work from a later task to be done early, and why. -->

## Verificações específicas por fase

<!-- One entry per phase used by tasks ("### Phase 1 — ..."). The reviewer runs these; a phase without an entry is a finding. -->
