---
id: KITS-TASK-40
---

# KITS-TASK-40 — Checkboxes de número e braçadeira na aba 3D

## Goal

A aba 3D ganha três checkboxes, **Number**, **Captain armband** e **Long sleeves**, que desenham na figura só o que as KITS-TASK-38 e 39 mediram. O de manga longa, pedido do usuário em 2026-10-05, só aparece com a figura de jogador de linha: com o goleiro ele fica escondido, e não apenas desligado. O que não foi medido fica com o checkbox desligado e a frase "not measured" no catálogo. Remapear UV à mão não vale (§0).

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/app.py`, `tools/kits/ui/i18n.py`
  - `tools/kits/core/figure.py` e `tools/kits/core/api.py`, se a regra medida pedir composição de texels ou geometria a mais
  - `tools/kits/ui_check.py`: a verificação e a planta
  - `docs/PLAN-KITS-PY.md`: §3.4
- Out: árbitro (§4.5)

## Done criteria

- [ ] Para cada checkbox com regra medida: as capturas de costas (`--yaw 0`) ligado e desligado diferem dentro da vista, e a planta que ignora o checkbox fica vermelha no `kits_ui`
- [ ] Para cada checkbox sem regra: aparece desligado com a frase, nas duas línguas, e o `kits_ui` afirma que está desligado
- [ ] Manga longa: o checkbox está visível com a figura 0 e escondido com a figura 1. O `kits_ui` afirma pelos dois `--figure`, e a planta que o deixa sempre visível fica vermelha
- [ ] `ctest --test-dir build -R kits`: 4/4

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.7).

O título no estado diz "número e braçadeira". A manga longa entrou depois, pelo corpo, porque o CLI não renomeia task.

Se as 38 e 39 terminarem as duas blocked, por falta do save state de partida, esta task também espera. Entregar só os checkboxes desligados é decisão do usuário.

Da KITS-TASK-38 (2026-10-05, §4.7): na `LOOKS SET` o jogo **preenche** a lacuna do torso com uma cópia reta da zona "shirt back" — (44,6) 20×24 para (0,80) no jogador, (108,6) para (100,104) no goleiro — e **não desenha número** ali. Duas consequências aqui. As costas têm regra medida, e o 3D pode copiar esse bloco antes de desenhar; a dica da aba (`figure_hint` em `ui/i18n.py`, da KITS-TASK-37) dizia que as costas "not measured yet" — a [CORR-KITS-066](/docs/tasks/kits/CORR-KITS-066.md) já a acertou. E o número continua sem regra: o checkbox **Number** fica desligado com a frase, a menos que o usuário dê um save state de partida.

Da KITS-TASK-39 (2026-10-05, §4.3), que ficou **blocked**: na `LOOKS SET` nenhuma primitiva amostra a imagem de mangas. São 0 de 418 no slot 2 e 0 de 430 no slot 1, pelo `oracle.py --sleeves`. Sem save state de partida não há regra para **Captain armband** nem para **Long sleeves**, e os dois checkboxes ficam desligados com a frase.

## Log de Execução
