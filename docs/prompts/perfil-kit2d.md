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
- **O `oracle.py` do `kit2d` nasce sobre a lib `tools/duckmcp/` (`duckmcp.Session`, `duckmcp.debug`), nunca sobre `tools/pes2/mcp.py`/`fork.py` nem com cliente MCP próprio** (2026-10-26; [§2](/docs/PLAN-DUCKMCP-PY.md#2)).

## Sources of truth

<!-- Plan sections, specs, reference outputs. Items point here through `source_of_truth`. -->

- [docs/PLAN-KIT2D-PY.md](/docs/PLAN-KIT2D-PY.md): o plano do ciclo.
- [docs/SUPERPACK-UNIFORMES-2D.md](/docs/SUPERPACK-UNIFORMES-2D.md): as medições dos três dados e do radar que o plano usa; os números ficam lá.
- [docs/PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md): valem o [§3.3](/docs/PLAN-KITS-PY.md#3.3) e o [§3.4](/docs/PLAN-KITS-PY.md#3.4).

## Generated artifacts

<!-- Output -> generator -> check command. Never edit the output. -->

## Gates deste ciclo

<!-- Commands that must pass before any item of this cycle closes (in addition to rite.toml [gates].global). -->

- `python3 tools/kit2d/selftest.py` sai 0 (desde a K2D-TASK-01).
- `ctest --test-dir build -R kit2d` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: os alvos do [§3.5](/docs/PLAN-KIT2D-PY.md#3.5) que já existem passam; o que pula imprime por quê, e o Log lê a linha, não o `Passed`.
- `python3 tools/kit2d/controls.py` (desde a K2D-TASK-16): última linha `controls: N of N red`.

## Hot files

<!-- Files many items touch; batches serialize on them. -->

- `tools/kit2d/core/api.py`, `tools/kit2d/core/layout.py`, `tools/kit2d/selftest.py`, `tools/kit2d/cli.py`, `tools/kit2d/oracle.py`, `tools/kit2d/ui/app.py`, `tools/kit2d/ui/i18n.py`, `tests/CMakeLists.txt`, `docs/PLAN-KIT2D-PY.md`.

## Serialized resources

<!-- Cycle-specific resources that cannot be used by two workers at once (rite.toml [resources] has repo-wide ones). -->

## Pull-ahead precedents

<!-- When the user allowed work from a later task to be done early, and why. -->

## Verificações específicas por fase

<!-- One entry per phase used by tasks ("### Phase 1 — ..."). The reviewer runs these; a phase without an entry is a finding. -->

### Fase 0 — as incógnitas medidas (§4.1, §4.2, §4.3)

- `python3 tools/kit2d/cli.py base <japonês>` reproduz a corrida e a base do [§1.2](/docs/PLAN-KIT2D-PY.md#1.2); número no Log colado da HEAD.
- `oracle.py --base` acha a tabela na RAM, e a busca deslocada de 10 bytes não acha nada (vermelho visto).
- `layout.py` é o único lugar com endereço do [§1.1](/docs/PLAN-KIT2D-PY.md#1.1): `grep -rnE '172096|225808|0x3F534' tools/kit2d --include=*.py` só lista `layout.py` e o selftest.
- Os §4.1–4.3 do plano dizem o veredito e remetem ao comando que o mede.

### Fase 1 — núcleo, leitura (§3.1, §3.2, §3.3)

- `grep -rnE '^(from|import) .*(PySide6|Qt)' tools/kit2d/core` vazio; `grep -rn 'print(\|sys.exit' tools/kit2d/core` vazio.
- `grep -nE '^(from|import) ' tools/kit2d/cli.py` só importa `core.api` do núcleo.
- Nenhuma tabela de nomes em `tools/kit2d/`: os nomes vêm de `tools/kits/core/teams.py`.
- Os 95 × 2 uniformes renderizam com `0 problema(s)`, e as plantas de registro fora da imagem e base ±10 saem vermelhas.

### Fase 2 — render contra o emulador (§5)

- `confront.py --render`: o time do state passa e os dois controles (outro time, outro modelo) reprovam.
- `ctest -R kit2d_live` passa com o state; sem ele pula 77 imprimindo por quê, e pular não conta como passar.
- O texto diz qual time foi medido, não "todos".

### Fase 3 — núcleo, escrita (§3.1, §5)

- Aplicar sem editar deixa sha256 idêntico; aplicar uma edição muda só os bytes do `diff()` (`cmp -l`, contagem no Log).
- Gravar em `roms/` é recusado.
- `python3 tools/kit2d/controls.py`: `controls: N of N red`, com cada controle do item 4 do [§5](/docs/PLAN-KIT2D-PY.md#5) nomeado; radar fora das 8 é aviso.

### Fase 4 — gravação contra o port (§5)

- A mesma edição de paleta pela ferramenta e pelo `we2002_golden_tool` difere só em 405724..405739.
- O controle (valor diferente num lado) reprova, e o controle positivo (cópia gravada contra a original) mostra a edição.
- No Linux, o `ed.exe` como terceiro lado; nenhuma janela ≥ 900×450 no `:98` antes.

### Fase 5 — a janela mínima (§3.4, §3.5)

- `grep -nE '^(from|import) ' tools/kit2d/ui/*.py` só importa `core.api` do núcleo.
- O catálogo `tools/kit2d/ui/i18n.py` tem as mesmas chaves e `{campos}` nas duas línguas, e nenhuma string visível fora dele.
- `ctest -R kit2d_ui` passa no `:98`; sem venv pula imprimindo por quê.
- Captura da janela citada no Log; nenhuma janela na sessão visível (`:98` / −32000).

### Fase 6 — modelo, radar e desfazer (§3.4)

- A lista de modelos tem 190 itens, e escolher um e Aplicar grava 4 bytes em +225808.
- O radar grava 2 bytes no offset do uniforme certo; par proibido avisa e grava.
- Desfazer até o começo deixa o buffer limpo.

### Fase 7 — a edição no jogo (§5, §7)

- `confront.py --final`: cor, modelo e radar aplicados aparecem no quadro do emulador, e a cópia sem edição não difere.

### Fase 8 — diagnóstico, disco hackeado e clubes de ML (§2.1, §3.4, §4.6)

- O japonês mostra `0` problemas; a `golden-european-deluxe` abre sem recusa e com as contagens de palavra 1 e radar fora do original iguais na CLI e na aba.
- O §4.6 diz que clube foi medido.
- Cada item da definição de pronto do [§0](/docs/PLAN-KIT2D-PY.md#0) tem a linha do comando que o prova.
