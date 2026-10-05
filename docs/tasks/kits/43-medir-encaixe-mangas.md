---
id: KITS-TASK-43
---

# KITS-TASK-43 — Medir o encaixe da braçadeira e da manga longa do MODEL.BIN

## Goal

Medir, na partida do slot 5, como o jogo põe na figura as seções do `/BIN/MODEL.BIN` que a KITS-TASK-39 achou: a seção 93, que é a braçadeira, e as 95 a 102, que são a manga longa. A pergunta é que transformação cada seção recebe e a que peça do corpo ela se prende. A outra pergunta é se a figura de partida inteira é o `MODEL.BIN`, e não o `EDT_MOD.BIN` que a aba 3D desenha. Sem essa resposta, os checkboxes **Captain armband** e **Long sleeves** da KITS-TASK-40 não têm como desenhar sem inventar geometria (§0).

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`: uma opção nova, `--attach SLOT`. Ela casa cada primitiva da lista do GPU com a seção do `MODEL.BIN` de que sai, pelos texels, como a `--sleeves` já faz. Depois lê, como o `tools/looks/oracle.py --pose` faz na `LOOKS SET`, a matriz que o GTE carrega antes de cada seção
  - `tools/kits/selftest.py`, para a parte pura nova
  - `docs/PLAN-KITS-PY.md`: §4.3 com o resultado
- Out: desenhar a braçadeira e a manga longa na janela (KITS-TASK-40)

## Done criteria

- [ ] `oracle.py --attach 5` colado no Log, com duas contagens. A primeira diz quantas primitivas da figura no quadro saem do `MODEL.BIN` e quantas do `EDT_MOD.BIN`, por seção. A segunda diz, para a seção 93 e para as 95 a 102, a seção do corpo cuja matriz elas compartilham, ou a matriz própria que recebem
- [ ] A regra na §4.3: qual seção do `MODEL.BIN` substitui ou acompanha qual peça da figura, e se a manga curta e a longa são seções alternativas da mesma peça. O comando que mede vai junto
- [ ] Um vermelho visto: a seção trocada (a 94, ou uma do tronco) e a ferramenta acusando
- [ ] Se a figura de partida não for a do `EDT_MOD.BIN`, a §4.3 diz isso e diz o que a aba 3D precisaria ler para desenhar a braçadeira e a manga longa. Essa leitura é trabalho novo, decisão do usuário

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.3).

Criada em 2026-10-05, a pedido do usuário, quando a KITS-TASK-40 chegou sem regra para nenhum dos três checkboxes.

State: `work/kits-states/SLPM-87056_5.sav`, a mesma partida da KITS-TASK-42. A seção 94 do `MODEL.BIN` fica entre a braçadeira (93) e as mangas longas (95 a 102), e não apareceu no quadro. É a primeira candidata a manga curta ou a peça trocada.

O `looks` já mediu na `LOOKS SET` que a transformação por peça é absoluta e que o ponteiro de modelo numa parada nomeia a peça anterior. As duas armadilhas estão no `CLAUDE.md`, seção do visualizador de aparência. Elas valem aqui até prova em contrário.

## Log de Execução
