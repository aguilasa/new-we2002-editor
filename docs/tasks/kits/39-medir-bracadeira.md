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
- [x] Se for 0 na `LOOKS SET`, a task fica **blocked**, com `--unblocked-by` nomeando o save state de partida que falta, decisão do usuário. Se não for 0, a geometria que amostra e de que arquivo ela sai vão para a §4.3. As primitivas que caem nas zonas de manga longa e as que caem nas de braçadeira contam separadas, pelo mapa de `tools/kits/core/zones.py`

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
- **pending** (2026-10-05): user saved match state slot 5 (Norway x Ecuador, long sleeves, Norway's no. 10 captain on the ball); oracle.py --sleeves 5 reports sleeves image 96

**Destravada em 2026-10-05.** O usuário salvou o slot 5: Noruega × Equador,
os dois de manga longa, com o camisa 10 da Noruega, que é o capitão, com a
bola. A cópia mestra está em `work/kits-states/SLPM-87056_5.sav` (sha256
começando por `c08b761ad75bccc2`). O `oracle.py --slot 5` acha a Noruega
(`TEX_14`) em (576,256) e o Equador (`TEX_47`) em (640,256). O `--sleeves`
passou a aceitar slot de partida (`load_slot`), a ler todas as páginas de kit
e a filtrar por 8 bits e CLUT de kit. Também passou a afirmar o veredito
(`--expect-sleeves`) e a achar a geometria no disco. A planta virou "cada
texel para a outra imagem e um texel para a direita". O `--plant-sleeves`
antigo, que exigia a imagem de mangas, não ficava vermelho na partida.

Corridas finais, todas na HEAD da entrega:

- `--sleeves 1 --expect-sleeves none` sai 0: `uniform image 190, sleeves image 0`.
- `--sleeves 2 --expect-sleeves none` sai 0: `uniform image 104, sleeves image 0`.
- `--sleeves 5 --expect-sleeves drawn` sai 0:

```
  789 textured primitive(s) in the frame's list
  kit pages: uniform image 154, sleeves image 96, both 0; other pages 539
    page (576,256): sleeves 45, uniform 71
    page (640,256): sleeves 51, uniform 83
  of those touching the sleeves image: long sleeve zones 88, armband zones 8
  where the sleeves quads' texels are on the disc (48 distinct quad(s), every Form 1 file read raw):
    /BIN/MODEL.BIN               48 of 48
  control, the same quads one texel right: found in no file
  in the sections of /BIN/MODEL.BIN (quads by zone):
    section 93   long sleeve 0, armband 6, other 0
    section 95   long sleeve 8, armband 0, other 0
    section 96   long sleeve 8, armband 0, other 1
    section 97   long sleeve 6, armband 0, other 0
    section 98   long sleeve 8, armband 0, other 1
    section 99   long sleeve 3, armband 0, other 0
    section 100  long sleeve 2, armband 0, other 0
    section 101  long sleeve 3, armband 0, other 0
    section 102  long sleeve 2, armband 0, other 0
  ok    154 primitive(s) sample the uniform image; sleeves drawn
```

Os vermelhos:

- `--sleeves 2 --expect-sleeves none --plant-sleeves` sai 1, com `FAIL  104
  primitive(s) sample the sleeves image, not none`.
- `--sleeves 5 --expect-sleeves drawn --plant-sleeves` sai 1, com `FAIL  no disc
  file holds every sleeves quad (none found)`.
- O `selftest.py` traz seis checagens `oracle --sleeves`, verdes, e duas delas
  são vermelhas plantadas.

O resultado está na §4.3: a braçadeira é a seção 93 do `MODEL.BIN` e a manga
longa são as seções 95 a 102, separadas pelas zonas do `core/zones.py`.
