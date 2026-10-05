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

- [ ] `oracle.py --sleeves 1` e `--sleeves 2` colados no Log. Na `LOOKS SET` o esperado pelo disco é 0 (§4.3, 0 de 593 e 0 de 629)
- [ ] Um vermelho visto: a mesma contagem para a imagem de uniforme (576,256) tem que dar diferente de 0
- [ ] Se for 0 na `LOOKS SET`, a task fica **blocked**, com `--unblocked-by` nomeando o save state de partida que falta, decisão do usuário. Se não for 0, a geometria que amostra e de que arquivo ela sai vão para a §4.3. As primitivas que caem nas zonas de manga longa e as que caem nas de braçadeira contam separadas, pelo mapa de `tools/kits/core/zones.py`

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.3).

Recursos: emulador e save-states. A braçadeira e a manga longa ficam na imagem de mangas, x 160–191 (zonas em `tools/kits/core/zones.py`, 112–122). Da braçadeira, e o SUPERPACK-UNIFORMES §1.3 diz que ela usa a linha 0 da paleta. Isso é dado de comunidade, não medição.

## Log de Execução
