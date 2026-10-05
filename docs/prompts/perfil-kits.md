# Profile — kits

<!--
The cycle profile is read by every /rite command in this cycle. Keep it short
(rite.toml [profile].max_kb); dated pitfall histories go to the pitfalls file,
which commands search instead of reading whole.
-->

## Contexto essencial — decisões já confirmadas

<!-- Decisions the user confirmed. One line each, with the date and where it was decided. -->

Todas do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md), proposta de 2026-09-29. Onde
este perfil e o plano divergirem, o plano ganha.

- **Só lê.** Não grava na imagem nem no TEX — §0 (Não-objetivos).
- **Não inventa geometria.** Manga longa e braçadeira só no 3D depois de achadas e medidas; até lá o 3D diz que não as tem — §0, §4.3.
- **Projeto próprio em `tools/kits/`, que importa o núcleo do `tools/looks/` sem copiar** — §2.
- **As duas mudanças no `looks` (`scene.Builder(kit=...)`, `kit_set`) são tasks deste ciclo**, aditivas, default igual ao de hoje, com os quatro gates do `looks` verdes antes e depois — §2, §6, fase 5 da §7.
- **Geometria do disco confiável pela guarda do `looks` (`WE2002_LOOKS_IMAGE`); o TEX vem de qualquer lugar, com guarda de forma, não de digest** — §2.1.
- **Cauda marcada Form 2 com dado no leiaute Form 1 é lida como Form 1**, e o diagnóstico diz que leu assim — §2.1.
- **Núcleo × interface:** `tools/kits/core/` sem Qt, sem `print`, sem `sys.exit`, sem estado global; UI e CLI só importam `core/api.py` — §3, §3.1.
- **Endereço só em um módulo:** nomes de time em `generated/`, o resto no `layout.py` do `looks` — §3.1.
- **Origem reconhecida pelo conteúdo, não pela extensão** — §3.1, §3.2.
- **Nomes de time:** japonês decidido pelo disco (boot `SLPM_870.56`, digests), não pelo texto; tabela inglesa é o `TEAM_NAMES` de `src/core/Tables.cpp` via gerador com `--check` — §3.3.
- **Estilo Fusion, `QPalette` fixa, fonte em pixels, layouts Qt; igual no Windows e no Linux, não o do `looks`** — §3.4.
- **Código e docstrings em inglês, documentos em português; venv `work/venv-looks/`** — §3.5.
- **Nada do Superpack entra no git**; pares de bandeira por `WE2002_KITS_CORPUS` — §6.
- **Crédito é de autor, não de compilação.** O Superpack não se cita; cita-se quem aparece dentro dele (polipoli, ramonpsx, Lagarto, Obocaman…). **Todo código de terceiro que o `kits` alcança**, inclusive por import (CARP via `tools/pes2/`, `we3d` via `tools/looks/`), tem linha no `NOTICE.md`, no mesmo commit que o traz — usuário, 2026-09-30.
- **Texto da UI em inglês dos EUA por default, por catálogo i18n (`ui/i18n.py`) com `pt-BR` escolhível; núcleo e CLI só inglês** — usuário, 2026-10-03, §3.4 (*Idioma da interface*).
- **Fases 1 a 3 sem janela; a fase 7 (emulador) não pode ser pulada; manga longa/braçadeira/árbitro esperam §4.3 e §4.5** — §7.

## Sources of truth

<!-- Plan sections, specs, reference outputs. Items point here through `source_of_truth`. -->

- [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) — o plano; âncoras por `rite anchors docs/PLAN-KITS-PY.md` (incógnitas em `#4.1`…`#4.6`).

## Generated artifacts

<!-- Output -> generator -> check command. Never edit the output. -->

- `tools/kits/core/generated/team_names.py` → `python tools/kits/gen_tables.py` (de `Offsets.hpp`, `Types.hpp`, `Tables.cpp`) → `python tools/kits/gen_tables.py --check` (`ctest -R kits_gen`); `--negative` planta o vermelho.
- `tools/kits/core/generated/team_kits.py` → o mesmo `python tools/kits/gen_tables.py` (da `EDITOR_RULE` e das `EMULATOR_ROWS` dele) → o mesmo `--check`; `--editor` relê a regra do `we-team-editor.exe` (pula sem o exe) e `--negative-editor` planta o vermelho; `--negative-kits` planta os dois vermelhos do `team_kits.py` — uma linha de `EMULATOR_ROWS` que a regra contradiz e uma tag trocada numa cópia do arquivo gerado.

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

### Fase 0 — medições no disco

- Todo número novo no plano sai de subcomando versionado de `tools/kits/cli.py`; rodar e comparar (§1.1, §4.3, §4.4, §4.6).
- `grep -rnE 'print\(|sys\.exit|PySide' tools/kits/core/` vazio.
- As §4.3, §4.4 e §4.6 têm veredito ou o aberto dito, com o comando.

### Fase 1 — núcleo, lado TEX

- `ctest -R kits` lista `kits_selftest` e `kits_image` pelo nome; `No tests were found` é vermelho.
- `python tools/kits/controls.py`: todo controle vermelho, incluindo o byte trocado no LZSS (§5.4).
- `cli.py` só importa `core.api` e stdlib (§3.1).
- `NOTICE.md` tem a seção do `tools/kits/`, com CARP e `we3d`; nenhuma linha cita o Superpack como fonte.
- European Deluxe: `cli.py tex` dá 97 que abrem e 8 recusados com o motivo, `TEX_48` entre eles; `TEX_13` abre lido além do tamanho ISO; `--iso-size` reproduz os 16 dos 18 com cauda Form 2 (§2.1).

### Fase 2 — núcleo, lado ROM

- `python tools/kits/gen_tables.py --check` sai 0 e tem vermelho plantado visto (§3.3).
- `cli.py teams` nas duas imagens de `roms/`: `table` na japonesa, `rom` na European Deluxe, nenhum nome vazio.

### Fase 3 — plano e zonas

- `git ls-files tools/kits/ui` vazio: sem janela até aqui (§7).
- Mapa deslocado 1 px reprova a §4.6; o mapa medido passa (§5.4).
- `TEX_A4`: bitmap de titular = suplente; tag que difere, diferente.

### Fase 4 — janela mínima

- `tools/kits/ui/` só importa PySide6, stdlib, `core.api` e os próprios módulos de `ui/` (o `i18n.py`) (§3.1).
- `ctest -R kits_ui` verde, e sem Fusion/`QPalette` fixa ele reprova (§3.4).
- Nenhuma janela visível: `:98` no Linux, `-32000` no Windows.
- Nenhum literal de texto visível em `tools/kits/ui/` fora do `i18n.py`; `en-US` e `pt-BR` com as mesmas chaves e campos, e o selftest reprova se não (§3.4).

### Fase 5 — mudanças no `looks`

- `ctest -R looks`: os quatro pelo nome, verdes antes e depois (§2, §6).
- Suplente do `TEX_A4` = titular; tag que difere, quadro diferente (§5.4).
- Sem argumento novo, `Builder` desenha como antes (default `TEX_A4`, `kit_set=1`).

### Fase 6 — 3D

- Texto novo da janela entra no catálogo (`ui/i18n.py`), nas duas línguas (§3.4).
- Só `core/figure.py` importa o `scene` do `looks` (§3.1); o resto do núcleo alcança o `layout` para endereço e o `survey.py` as sondas da fase 0, e nenhum pede cena — `kits_selftest` afirma (`only core/figure.py imports the looks scene`).
- Trocar as paletas 486 e 488 troca jogador e goleiro (§5.4).
- Sem `WE2002_LOOKS_IMAGE`, aba 3D desligada com a frase e o 2D igual (§3.2).

### Fase 7 — emulador

- A leitura da VRAM começa de save state, e o controle com o time de titular mostra o 1º par (§4.1).
- Escore do confronto 3 colado, com o controle cruzado reprovando (§5.3).

### Fase 8 — times em vez de tags

- Texto novo da janela entra no catálogo (`ui/i18n.py`), nas duas línguas (§3.4).
- Cada linha da tabela time → tag tem proveniência; três conferidas no emulador (§4.2).
- Nada do `we-team-editor.exe` no git.

### Fase 9 — diagnóstico e pronto

- Texto novo da janela entra no catálogo (`ui/i18n.py`), nas duas línguas (§3.4).
- `TEX_48` e `TEX_70` aparecem na aba com o motivo, e o `TEX_13` com a nota de leitura além do tamanho ISO (§0, item 3; §2.1).
- Os cinco itens da Definição de pronto conferidos com comando (§0).
