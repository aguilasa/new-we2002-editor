---
id: K2D-TASK-02
---

# K2D-TASK-02 — Sondas de disco versionadas: cli.py base e cli.py sprites reproduzem o §1.2

## Goal

O snippet do [§1.2](/docs/PLAN-KIT2D-PY.md#1.2) vira duas opções versionadas: `cli.py base` (a corrida de ponteiros e a base inferida) e `cli.py sprites --team N --set 1|2` (os registros de 10 bytes de um modelo). Daqui em diante número do §1.2 sai delas, não do snippet.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/cli.py`
  - `tools/kit2d/core/probe.py`
  - `tools/kit2d/selftest.py`
- Out:
  - a medição na RAM (K2D-TASK-03)

## Done criteria

- [ ] `python3 tools/kit2d/cli.py base <japonês>` imprime `corrida de ponteiros: 198372..198788, 104 ponteiros` e `base inferida: 800CA930`, colados no Log da HEAD entregue
- [ ] `cli.py sprites --team 1 --set 1` imprime os 8 registros da Irlanda titular do §1.2, colados no Log
- [ ] o mesmo comando sobre a `golden-european-deluxe` e o European original dá a mesma base (digest dos `SELECT2.BIN` lidos no Log, para saber quantos conteúdos distintos foram medidos)
- [ ] um `SELECT2.BIN` com a corrida truncada (planta no selftest) faz `base` recusar com mensagem, vista vermelha

## Notes

`WE2002_KIT2D_IMAGE`, default `WE2002_LOOKS_IMAGE`, aponta a imagem (§3.5).

## Log de Execução
