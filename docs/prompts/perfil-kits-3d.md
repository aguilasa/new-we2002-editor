# Profile — kits-3d

<!--
The cycle profile is read by every /rite command in this cycle. Keep it short
(rite.toml [profile].max_kb); dated pitfall histories go to the pitfalls file,
which commands search instead of reading whole.
-->

## Contexto essencial — decisões já confirmadas

<!-- Decisions the user confirmed. One line each, with the date and where it was decided. -->

- **Kit 1 é Home/Casa, kit 2 é Away/Visitante**: convenção do futebol, não medição. O campo "Set"/"Conjunto" vira "Kit"/"Uniforme" (usuário, 2026-10-07; [G1](/docs/KITS-AJUSTES-3D.md#g1--set-vira-kit-homeaway-uniforme-casavisitante)).
- **G1 vale para a interface e para o CLI:** `--kit home|away` ao lado de `--set 1|2` (usuário, 2026-10-07; [G1](/docs/KITS-AJUSTES-3D.md#g1--set-vira-kit-homeaway-uniforme-casavisitante)).
- **G3 mede antes de desenhar:** como a geometria do `MODEL.BIN` entra na figura do `EDT_MOD.BIN` é medido, não escolhido (usuário, 2026-10-07; [G3](/docs/KITS-AJUSTES-3D.md#g3--sem-match-player-só-player-e-goalkeeper)).
- **A braçadeira do goleiro é medida no emulador**; sem o save state, a task fica blocked (usuário, 2026-10-07; [G4](/docs/KITS-AJUSTES-3D.md#g4--number-captain-armband-e-long-sleeves-em-qualquer-combinação-nas-duas-figuras)).
- **A cópia das costas vale sempre**, e o que ainda falta se conta por ângulo com ferramenta (usuário, 2026-10-07; [G5](/docs/KITS-AJUSTES-3D.md#g5--figura-inteira-em-qualquer-giro)).
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

### Fase 1 — texto e layout (G1, G2)

- `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: 4/4, sem *skipped*.
- `python3 tools/kits/controls.py`: todos os controles vermelhos, e as plantas novas da fase aparecem no catálogo.
- Toda chave nova do catálogo existe em en-US e em pt-BR (`ui/i18n.py`), e o `kits_ui` lê os rótulos nas duas línguas.
- `cli.py --kit home|away` dá o mesmo digest que `--set 1|2`.

### Fase 2 — figura inteira (G5)

- A ferramenta de contagem por ângulo foi vista vermelha com uma lacuna plantada.
- Nenhum texel entra no desenho sem regra medida: o único preenchimento novo é o `BACK_COPY` (§4.7 do PLAN-KITS-PY).
- `ctest -R kits` 4/4 e `controls.py` todo vermelho.

### Fase 3 — medidas de geometria (G3, G4)

- Todo número da regra escrita em G3 e G4 sai de uma opção versionada do `oracle.py`, e não de sonda.
- Resultado negativo não fecha critério: sem o save state, a task vai a blocked com `--unblocked-by`.
- `controls.py` todo vermelho, com o controle novo de cada medição no catálogo.

### Fase 4 — duas figuras e caixas livres (G3, G4)

- Nenhum UV remapeado à mão (§0 do PLAN-KITS-PY): a geometria vem da regra da fase 3.
- As decisões reabertas (KITS-TASK-37, 40 e 47) aparecem datadas no plano.
- O `kits_ui` cobre as 8 combinações nas 2 figuras, com uma planta por caixa.
- `ctest -R kits` 4/4 e `controls.py` todo vermelho.
