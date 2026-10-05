---
id: KITS-TASK-39
---

# KITS-TASK-39 — Medir quem desenha a braçadeira

## Goal

Fechar a metade aberta da §4.3: que primitiva amostra a imagem de mangas (576,384) e a que geometria ela pertence. Nessa imagem moram a braçadeira de capitão e a manga longa, que o usuário pediu em 2026-10-05; as duas se medem nesta task. A medição anda a lista que o quadro entrega ao GPU atrás do texpage e do CLUT dessa imagem.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`: uma opção nova (`--sleeves SLOT`) que anda a lista de primitivas do quadro, como o `tools/looks/oracle.py --scenery`, e conta as que amostram (576,384)
  - `docs/PLAN-KITS-PY.md`: §4.3 com o resultado, separado em braçadeira e manga longa
- Out: desenhar a braçadeira ou a manga longa (KITS-TASK-40)

## Done criteria

- [x] `oracle.py --sleeves 1` e `--sleeves 2` colados no Log. Na `LOOKS SET` o esperado pelo disco é 0 (§4.3, 0 de 593 e 0 de 629)
- [x] Um vermelho visto: a mesma contagem para a imagem de uniforme (576,256) tem que dar diferente de 0
- [ ] Se for 0 na `LOOKS SET`, a task fica **blocked**, com `--unblocked-by` nomeando o save state de partida que falta, decisão do usuário. Se não for 0, a geometria que amostra e de que arquivo ela sai vão para a §4.3. As primitivas que caem nas zonas de manga longa e as que caem nas de braçadeira contam separadas, pelo mapa de `tools/kits/core/zones.py`

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.3).

Recursos: emulador e save-states. A braçadeira e a manga longa ficam na imagem de mangas, x 160–191 (zonas em `tools/kits/core/zones.py`, 112–122). Da braçadeira, e o SUPERPACK-UNIFORMES §1.3 diz que ela usa a linha 0 da paleta. Isso é dado de comunidade, não medição.

## Log de Execução

2026-10-05. Ambiente: `DISPLAY=:98`, `XAUTHORITY` vazio,
`WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin`,
`WE2002_LOOKS_DRIVE_IMAGE=work/looks-disc/we2002-english.cue`, fork MCP.

**`--sleeves 2`**, exit 0:

```
  418 textured primitive(s) in the frame's list
  kit page (576,256): uniform image 104, sleeves image 0, both 0; other pages 314
  of those touching the sleeves image: long sleeve zones 0, armband zones 0
  on the kit page, by CLUT and depth: (0,486) 8-bit x104
  ok    the control holds: 104 primitive(s) sample the uniform image
```

**`--sleeves 1`**, exit 0:

```
  430 textured primitive(s) in the frame's list
  kit page (576,256): uniform image 190, sleeves image 0, both 0; other pages 240
  of those touching the sleeves image: long sleeve zones 0, armband zones 0
  on the kit page, by CLUT and depth: (0,488) 8-bit x190
  ok    the control holds: 190 primitive(s) sample the uniform image
```

**Vermelhos vistos.**

- A contagem na imagem de uniforme não é 0 (104 e 190), e é ela o controle.
- `--sleeves 2 --plant-sleeves` sai 1, com `FAIL  no primitive samples the
  sleeves image: the list read is not the figure's`.
- Na parte pura, o `selftest.py` traz três checagens `oracle --sleeves`.
  Plantando `IMAGE_HEIGHT = 256`, a primeira falha com `{'uniform': 2,
  'sleeves': 0, ...}`, e o código foi restaurado depois.

**Resultado: 0 na `LOOKS SET`.** Pelo terceiro critério, a task fica
**blocked**. Ela espera um save state de partida, com o jogador de linha de
manga longa ou de capitão na tela, e esse state é decisão do usuário. A §4.3
traz a tabela.
- **blocked** (2026-10-05): oracle.py --sleeves 1|2 on LOOKS SET: 'sleeves image 0' (0 of 418, 0 of 430). Armband and long sleeves are drawn only in a match: needs a match save state with a long-sleeved or captain outfield player on screen, user's decision. Unblocked when 'python tools/kits/oracle.py --sleeves <match slot>' reports a sleeves image count above 0. Partial work b88d9c1.
