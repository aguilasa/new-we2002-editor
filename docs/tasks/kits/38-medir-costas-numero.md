---
id: KITS-TASK-38
---

# KITS-TASK-38 — Medir as costas e o número no jogo

## Goal

Responder com medição a pergunta da §4.7: o jogo preenche a lacuna do torso em tempo de execução, (0,80) 20×24 no jogador e (100,104) 20×24 no goleiro, com as costas e o número? Se preenche, de onde vêm os texels e onde cai cada dígito. Se não preenche, a negativa fica medida.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`: uma opção nova (`--back SLOT`) que lê a VRAM da imagem de uniforme (576,256) nos dois retângulos e diz, por pixel, se o índice ainda é 0. O controle é o mesmo retângulo lido do TEX do disco
  - `tools/kits/selftest.py`, se a opção ganhar parte pura testável sem emulador
  - `docs/PLAN-KITS-PY.md`: §4.7 com o resultado
- Out: desenhar o número na janela (KITS-TASK-40)

## Done criteria

- [x] `oracle.py --back 1` e `--back 2` (os dois states da `LOOKS SET`) colados no Log, com a contagem de pixels de índice diferente de 0 em cada retângulo
- [x] Um vermelho visto: o retângulo errado (a zona dos números, por exemplo) ou o TEX trocado, e a ferramenta acusando
- [x] Se a `LOOKS SET` não escreve ali, a task fica **blocked**, com `--unblocked-by` nomeando o save state de partida que falta. Esse state é decisão do usuário, nunca improvisado
- [x] Se escreve: a regra (origem dos texels, posição do dígito) na §4.7, com o comando que a mede

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.7).

Recursos: emulador e save-states (fixture em `work/looks-states/`). A zona "numbers 0-9" (64,68) 60×12 é a candidata a origem. Nenhuma primitiva da `LOOKS SET` a amostra (`WHY_NUMBERS` em `tools/kits/core/zones.py`).

## Log de Execução

2026-10-05. Ambiente: `DISPLAY=:98`, `XAUTHORITY` vazio,
`WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin`,
`WE2002_LOOKS_DRIVE_IMAGE=work/looks-disc/we2002-english.cue`, fork MCP.

**`--back 1` e `--back 2`.** Comando: `python3 tools/kits/oracle.py --back N
--expect-back written`. Saída idêntica nos dois slots, exit 0:

```
  control: the uniform page (576,256) 64x128 read twice, identical
  disc side TEX_A4: 0 halfword(s) of 8192 differ from VRAM outside the gaps
  player     gap (0,80) 20x24: index != 0 in 480 of 480 pixel(s) in VRAM, 0 on the disc; 480 differ -- written
             VRAM indices: 25 x83, 16 x82, 26 x55, 27 x54, 28 x42, 23 x25, 24 x24, 21 x19
             the same pixels elsewhere in the page: (44,6) straight -- inside the shirt back
  goalkeeper gap (100,104) 20x24: index != 0 in 480 of 480 pixel(s) in VRAM, 0 on the disc; 480 differ -- written
             VRAM indices: 160 x43, 32 x43, 41 x42, 169 x41, 170 x28, 42 x27, 171 x27, 43 x27
             the same pixels elsewhere in the page: (108,6) straight -- inside the shirt back
  ok    every gap written
```

**Vermelhos vistos.** Os dois controles foram rodados com
`--back 2 --expect-back written`, e os dois saem 1:

- `--plant-back numbers`: `FAIL  player gap: written, but not a copy of the
  shirt back (the copy found sits in no zone of its figure)`, e o mesmo no
  goleiro.
- `--plant-back tex`: `disc side TEX_00: 4968 halfword(s) of 8192 differ` e
  `FAIL  the disc page differs from VRAM in 4968 halfword(s) outside the gaps`.

Na parte pura, `selftest.py` traz seis checagens `oracle --back`. Para ver o
vermelho, a ordem dos bytes de `pixel_index` foi trocada: três delas falham,
entre elas `FAIL  oracle --back: the copy is found at (44,6), inside the shirt
back  [] None`. O código foi restaurado depois.

**O jogo escreve ali**, então o critério de bloqueio não se aplica. O que ele
escreve são as costas e não o número. A regra das costas está na §4.7: cópia
reta, sem espelhar, da zona "shirt back", linhas 6 a 29. O critério também
pedia a posição do dígito, e ela não existe nesta tela: a cópia é idêntica à
origem e a zona "numbers 0-9" não aparece na lacuna. Medir o número numa
partida pede save state de partida, decisão do usuário. A nota disso ficou na
KITS-TASK-40.
- **Closed** — commit `71cd597` (2026-10-05): feat(kits): oracle.py --back measures the torso gap on LOOKS SET
  - Files (`git show --name-status 71cd597`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/38-medir-costas-numero.md`
    - `M docs/tasks/kits/40-checkboxes-numero-bracadeira.md`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
