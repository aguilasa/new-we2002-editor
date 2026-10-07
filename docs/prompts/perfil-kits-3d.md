# Profile — kits-3d

<!--
The cycle profile is read by every /rite command in this cycle. Keep it short
(rite.toml [profile].max_kb); dated pitfall histories go to the pitfalls file,
which commands search instead of reading whole.
-->

## Contexto essencial — decisões já confirmadas

<!-- Decisions the user confirmed. One line each, with the date and where it was decided. -->

- **Kit 1 é Home/Casa, kit 2 é Away/Visitante**: convenção do futebol, não medição. O campo "Set"/"Conjunto" vira "Kit"/"Uniforme" (usuário, 2026-10-07; [G1](/docs/KITS-AJUSTES-3D.md#g1--set-vira-kit-homeaway-uniforme-casavisitante)).
- **Não inventa geometria.** Nem geometria nem UV remapeado à mão; só o medido entra no desenho ([§0 do PLAN-KITS-PY](/docs/PLAN-KITS-PY.md#0); [Para o ciclo](/docs/KITS-AJUSTES-3D.md#para-o-ciclo)).
- **O 3D segue em `QPainter` por software, e o texto da UI só sai do catálogo `tools/kits/ui/i18n.py`** ([§3.4 do PLAN-KITS-PY](/docs/PLAN-KITS-PY.md#3.4); [Para o ciclo](/docs/KITS-AJUSTES-3D.md#para-o-ciclo)).

## Sources of truth

<!-- Plan sections, specs, reference outputs. Items point here through `source_of_truth`. -->

- [docs/KITS-AJUSTES-3D.md](/docs/KITS-AJUSTES-3D.md): o plano do ciclo, com as lacunas G1 a G5 encontradas na aba 3D.
- [docs/PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md): o plano do ciclo `kits`, já arquivado. Valem o [§0](/docs/PLAN-KITS-PY.md#0), o [§3.4](/docs/PLAN-KITS-PY.md#3.4) (interface), o [§4.3](/docs/PLAN-KITS-PY.md#4.3) (manga longa e braçadeira, medidas) e o [§4.7](/docs/PLAN-KITS-PY.md#4.7) (as costas e o número, medidos).

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
