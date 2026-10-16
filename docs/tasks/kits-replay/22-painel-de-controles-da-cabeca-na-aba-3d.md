---
id: KRP-TASK-22
---

# KRP-TASK-22 — Painel de controles da cabeça na aba 3D, no lugar da tupla em texto

## Goal

A aba 3D não tem mais o campo de texto da tupla: com "Cabeça do jogador" marcada, um painel à direita da vista mostra um `QComboBox` por campo da tupla (pele, estilo e cor do cabelo, estilo e cor da barba), com os rótulos do [§3.3](/docs/PLAN-KITS-REPLAY.md#3.3) nas duas línguas e a largura reajustada a cada troca de idioma; a cabeça desenhada sai dos combos.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/api.py` (`PLAYER_FIELDS`, `player_tuple`, `player_fields`: a UI fala só com o `api`)
  - `tools/kits/ui/app.py` (o painel, o `--player-looks` posicionando os combos, o `--list-3d`)
  - `tools/kits/ui/i18n.py` (título do painel e os cinco rótulos)
  - `tools/kits/ui_check.py` (juiz do painel e das larguras, e as plantas)
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
- Out:
  - o sexto campo (`boots`), altura e corpo (§3.3)
  - o seletor de jogador real (KRP-TASK-17)
  - a regra da cabeça (§3.1, §3.2): não muda

## Done criteria

- [ ] nenhum `QLineEdit` na aba 3D (`grep -n player_edit tools/kits/ui/app.py` vazio)
- [ ] `app.py … --list-3d` imprime o painel oculto sem a caixa e visível com ela, e os cinco combos com 4, 32, 8, 7 e 7 itens, com os rótulos do §3.3 em en-US e pt-BR
- [ ] trocar de idioma ao vivo (`--switch-to`) muda a largura do painel e nenhum rótulo corta, julgado pelo `kits_ui`, com a planta de largura fixa vista vermelha
- [ ] sem a caixa marcada, o digest de `cli.py figure` e o PNG de `--export-3d` são os de antes da task
- [ ] `replay.py confront <captura> --tab --player` antes e depois, nas três capturas de perto, colado da HEAD no Log (registra número, não afirma limite)
- [ ] o `kits_ui` cobre o painel com plantas: painel nunca mostrado, combo de cor do cabelo ignorado, largura fixa
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Decisão do usuário (2026-10-16), com imagem: o painel à direita da vista, os rótulos literais do §3.3. Os combos ficam como atributos da janela, para o `combos()` do `app.py` (que acha combo por `vars(self)`) lhes dar `AdjustToContents` e o juiz de largura de combo existente os alcançar.

## Log de Execução
