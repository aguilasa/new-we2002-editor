---
id: K2D-TASK-03
---

# K2D-TASK-03 — Base de carga do overlay medida na RAM pelo MCP

## Goal

Com o jogo de pé no state da [§4.4](/docs/PLAN-KIT2D-PY.md#4.4), `oracle.py --base` acha os 760 bytes da tabela de modelos na RAM (`read_memory` sobre 2 MiB e `bytes.find`) e a base deixa de ser inferida: `layout.py` passa a dizer "medida" e o valor, e as listas lidas da RAM são conferidas contra as do arquivo.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/oracle.py`
  - `tools/kit2d/core/layout.py`
  - `docs/PLAN-KIT2D-PY.md`
- Out:
  - o render (fase 1)

## Done criteria

- [ ] `python3 tools/kit2d/oracle.py --base` imprime o endereço achado e a base (endereço − 225808), colados no Log
- [ ] o mesmo comando confere as 190 listas da RAM contra o arquivo e imprime `N de 190 iguais`
- [ ] controle: a busca por uma tabela deslocada de 10 bytes não acha nada, vista no Log
- [ ] `layout.py` não tem mais a palavra "inferida" ao lado da base, ou tem o valor medido que a contradiz e o §1.2 do plano é corrigido na mesma task

## Notes

State: `work/kit2d-states/SLPM-87056_1.sav`, gravado em 2026-10-21; o que ele mostra está em [KIT2D-STATES.md](/docs/KIT2D-STATES.md). Armadilha da CORR-LOOKS-062: número na faixa não prova alinhamento.

## Log de Execução

- **blocked** (2026-10-19): precisa do save state da tela de opções de partida (§4.4): test -f work/kit2d-states/SLPM-87056_1.sav
