# Profile — kit2d

<!--
The cycle profile is read by every /rite command in this cycle. Keep it short
(rite.toml [profile].max_kb); dated pitfall histories go to the pitfalls file,
which commands search instead of reading whole.
-->

## Contexto essencial — decisões já confirmadas

<!-- Decisions the user confirmed. One line each, with the date and where it was decided. -->

- **Projeto próprio em `tools/kit2d/`, ciclo `kit2d`, que importa de `tools/pes2/`, `tools/kits/` e `tools/looks/` sem copiar** (usuário, 2026-10-01; [§2](/docs/PLAN-KIT2D-PY.md#2)).
- **A v1 não edita os gráficos do `DATSEL.BIN` nem abre arquivo avulso; a origem é sempre a ROM** (usuário, 2026-10-01; [§0](/docs/PLAN-KIT2D-PY.md#0), [§3.2](/docs/PLAN-KIT2D-PY.md#3.2)).
- **Os nomes dos times vêm do `tools/kits/core/teams.py`, por import; nunca uma segunda tabela** ([§3.3](/docs/PLAN-KIT2D-PY.md#3.3)).
- **Texto da janela só do catálogo `tools/kit2d/ui/i18n.py`, na forma do `tools/kits/ui/i18n.py`, en-US por default** (usuário, 2026-10-19; [§3.4](/docs/PLAN-KIT2D-PY.md#3.4)).
- **Palavras 0 e 1, modelo e radar são divergência deliberada do `ed.exe`; o `PARIDADE-FUNCIONAL.md` não se toca** ([§6](/docs/PLAN-KIT2D-PY.md#6)).
- **Nenhum render entra em gate antes de a fase 0 medir a base de carga** ([§4.1](/docs/PLAN-KIT2D-PY.md#4.1)).
- **Tasks que precisam do state da tela de opções nascem `blocked` por `test -f work/kit2d-states/SLPM-87056_1.sav`** (usuário, 2026-10-19; [§4.4](/docs/PLAN-KIT2D-PY.md#4.4)).

## Sources of truth

<!-- Plan sections, specs, reference outputs. Items point here through `source_of_truth`. -->

- [docs/PLAN-KIT2D-PY.md](/docs/PLAN-KIT2D-PY.md): o plano do ciclo.
- [docs/SUPERPACK-UNIFORMES-2D.md](/docs/SUPERPACK-UNIFORMES-2D.md): as medições dos três dados e do radar que o plano usa; os números ficam lá.
- [docs/PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md): valem o [§3.3](/docs/PLAN-KITS-PY.md#3.3) e o [§3.4](/docs/PLAN-KITS-PY.md#3.4).

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
