---
id: K3D-TASK-04
---

# K3D-TASK-04 — Ferramenta que conta o que falta na figura por ângulo

## Goal

Uma ferramenta versionada conta, por giro e por figura, os pixels do boneco por onde se vê o fundo (texel transparente, triângulo pulado, ordem de profundidade), e diz de qual peça e zona do TEX cada falta vem.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/cli.py` (ou `tools/kits/oracle.py`): a opção nova
  - `tools/kits/core/` se a contagem pedir apoio no núcleo
  - `tools/kits/selftest.py`, `tools/kits/controls.py`
- Out: consertar o que a contagem achar (é a K3D-TASK-05)

## Done criteria

- [ ] o comando imprime uma linha por (figura, yaw) de 0 a 345 em passos de 15, com os pixels vazados e as peças/zonas responsáveis; transcrição inteira no Log
- [ ] controle plantado: uma lacuna nova no TEX aumenta a contagem e fica vermelha no `controls.py`
- [ ] a contagem de hoje mostra a lacuna do torso (0,80) 20×24 no jogador e (100,104) 20×24 no goleiro com Number desmarcado
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Causas candidatas em G5: lacuna do torso, RGBA, ordem por profundidade média, triângulo degenerado pulado.

## Log de Execução
