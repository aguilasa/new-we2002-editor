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
- **A pele do corpo da figura da aba segue a Cor da Pele do jogador**, pela regra da `LOOKS SET`; o `match_scene` não muda (usuário, 2026-10-16; [§3.3](/docs/PLAN-KITS-REPLAY.md#3.3)).
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

- `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9), todos passando, sem *skipped*. A contagem mora só no §9.
- `python3 tools/kits/controls.py`: última linha `controls: N of N red`.

## Hot files

<!-- Files many items touch; batches serialize on them. -->

- `tools/kits/oracle.py`, `tools/kits/core/replay.py`, `tools/kits/replay.py`, `tools/kits/core/figure.py`, `tools/kits/ui/app.py`, `tools/kits/selftest.py`, `tools/kits/controls.py`.

## Serialized resources

<!-- Cycle-specific resources that cannot be used by two workers at once (rite.toml [resources] has repo-wide ones). -->

## Pull-ahead precedents

<!-- When the user allowed work from a later task to be done early, and why. -->

## Verificações específicas por fase

<!-- One entry per phase used by tasks ("### Phase 1 — ..."). The reviewer runs these; a phase without an entry is a finding. -->

### Fase 1 — o leitor puro (§2.1, §2.2)

- Nenhuma das dezenove funções de análise do §2.2 é definida no `oracle.py` (`grep -cE '^def (…)'` dá `0`); elas moram só em `tools/kits/core/replay.py`.
- `core/replay.py` não importa `tools/looks/oracle`, `fork` nem `mcp`.
- A saída do `oracle.py --replay*`/`--replay-field` com `--frame-json` é byte-idêntica antes e depois do move, nas sete capturas.
- Os casos sintéticos de replay do `selftest.py` migraram, não se duplicaram.
- Gates do ciclo.

### Fase 2 — a linha de comando, a captura e o confronto (§2.3 a §2.6)

- Todo `--json` traz `"schema": "kits-replay/1"` e chaves fixas; `replay.py figure --json` reproduz a linha `ok` do `oracle.py --replay … --frame-json` nas cinco capturas de perto.
- `kits_replay` visto 77 sem `WE2002_KITS_REPLAY_DIR`, e vermelho com digest trocado.
- `capture` recusa joystick antes de subir o emulador, imprime os quadros de cada sequência e nunca passa dos 390.
- `confront --tab` compara frente com frente e costas com costas, e registra número sem afirmar limite.
- Gates do ciclo.

### Fase 3 — cabeça por jogador (§3)

- A regra da cabeça escrita no §3.1 sai de `replay.py head`, medida nos 22 dos dois laços, ou a negativa está escrita com comando e saída.
- Nenhuma seção ou CLUT de cabeça escolhida à mão: o desenho usa só a regra medida; sem a opção, o digest é o de antes.
- `confront --tab` antes e depois colado no Log da task de desenho.
- Gates do ciclo.

### Fase 3a — controles da cabeça na aba (§3.3)

- Nenhum `QLineEdit` na aba 3D; com "Cabeça do jogador" marcada, o painel à direita mostra os cinco combos com 4, 32, 8, 7 e 7 itens; desmarcada, o painel some.
- Os rótulos são os cinco do §3.3, literais, nas duas línguas, escritos no `ui_check.py` e não lidos do `i18n.py`.
- Troca de idioma ao vivo reajusta a largura do painel, com planta que a deixa fixa vista vermelha.
- Sem a caixa marcada, digest e `--export-3d` iguais aos de antes; `confront --tab --player` antes e depois colado no Log.
- Gates do ciclo.

### Fase 4 — goleiro pela família 13 (§4)

- Nenhum UV nem vértice escrito à mão: toda seção vem do `MODEL.BIN`.
- A ordem de seções do goleiro impressa por opção versionada bate com o item 3 do relatório.
- A reabertura da K3D-TASK-10 aparece datada no §4 do plano.
- Gates do ciclo.

### Fase 5 — corrida (§5)

- A pose de corrida sai do `ANIME.BIN` com animação e quadro impressos, ou a negativa está no §5.1 e a pose capturada versionada é o fallback declarado.
- O esperado por (slot, foco) é constante no código, e a planta o derruba com dado real.
- Com a pose de caminhada, o digest é o de antes.
- Gates do ciclo.

### Fase 6 — jogador real e dois times (§6, §7)

- Nada muda em `src/`.
- Texto novo nas duas línguas do `tools/kits/ui/i18n.py`, e o `kits_ui` cobre cada seletor novo com planta.
- O jogador escolhido sai com a faixa, a cabeça e o painel que a captura de replay do mesmo jogador diz.
- Gates do ciclo.

### Fase 7 — câmera replay (§8)

- A projeção usa H 1376 e OFX/OFY 0 do item 9; o erro de projeção contra o jogo é impresso por opção versionada.
- Sem o preset, o digest é o de antes; `cli.py holes --tag 00` continua `skipped 0`.
- `confront --tab` refeito nas cinco capturas com a câmera nova.
- Gates do ciclo.
