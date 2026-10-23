---
id: CORR-DMCP-025
---

# CORR-DMCP-025 — A guarda de Dia/Noche em route_result não vê a troca de valor e a rota result nunca chega à tela

Origin: [DMCP-TASK-19](/docs/tasks/duckmcp/19-pes2-mcp-drive-e-pad.md)

## Problem

A rota `result` do `tools/pes2/mcp_drive.py` nunca chega à tela de resultado. Ela para em
`route_result`, na guarda que confere que o `Right` em `Dia/Noche` mudou o quadro
(`tools/pes2/mcp_drive.py:778`, `if s.capture().difference(before) < 0.0005`), e sai com
`MCP DRIVE FAILED: Right on Dia/Noche changed nothing -- the cursor is not on the first row`. O
aperto funciona — `match-options.png` mostra `Día/Noche  Al azar` e `match-options-lit.png` mostra
`Día/Noche  Día` —, mas trocar uma palavra muda o quadro inteiro em 0,00048, abaixo do limiar. O
defeito é anterior à DMCP-TASK-19: falha igual na HEAD de partida `6f6d7c7b` e depois da migração.
Sem a rota, a Fase 5 não mostra o PNG da tela de resultado igual antes e depois
([§5.2](/docs/PLAN-DUCKMCP-PY.md#5.2)), e a DMCP-TASK-19 fica bloqueada nesse critério.

## Evidência

Precisa do fork, do `:98` e dos save states de `~/.local/share/duckstation/savestates`. Três corridas
(duas na HEAD `6f6d7c7b`, uma com a migração da DMCP-TASK-19), as três iguais:

```text
$ DISPLAY=:98 XAUTHORITY= python3 tools/pes2/mcp_drive.py "work/pes2-EsIt/Pro Evolution Soccer 2 (Europe) (Es,It).cue" --screen result --out-dir "$OUT"; echo "rc=$?"
MCP DRIVE FAILED: Right on Dia/Noche changed nothing -- the cursor is not on the first row
rc=1
```

A diferença, medida com o `drive.Frame.difference` da própria guarda sobre os dois PNG que a rota
grava em volta do aperto:

```text
$ python3 -c "import sys; sys.path.insert(0,'tools/pes2'); import drive; print(drive.Frame('$OUT/match-options.png').difference(drive.Frame('$OUT/match-options-lit.png')))"
0.00048095095544579156
```

O mesmo valor, ao último dígito, nas três corridas (`before1`, `before2`, `after1`). O docstring do
`mcp_drive.py` mede o ruído de "mesma linha" em 0,0002 a 0,0005: só baixar o limiar põe a guarda
dentro do ruído.

## Root cause

Hipótese: a guarda compara o quadro inteiro, e a troca de valor de `Dia/Noche` mexe numa área pequena
demais para ultrapassar 0,0005 no todo. O limiar foi escrito para trocas de linha (0,0082 a 0,0125),
não para troca de valor dentro de uma linha.

## Fix

Em `route_result`: medir a diferença numa caixa que só contenha a linha `Dia/Noche` (o `box` do
`Frame.difference`), com o limiar medido nessa caixa contra o ruído na mesma caixa, e deixar o número
e a corrida no comentário, como o resto do arquivo faz.

## Arquivos a criar ou modificar

- `tools/pes2/mcp_drive.py`

## Verificação

- a rota `result` sai `MCP DRIVE OK` e grava a tela de resultado, com o comando da Evidência;
- a guarda continua vermelha quando o aperto não muda o valor (controle: a mesma comparação entre dois
  quadros sem aperto fica abaixo do limiar novo, valor colado);
- depois, a DMCP-TASK-19 mede o PNG de `result` antes (HEAD `6f6d7c7b` com este conserto) e depois.

## Log de Execução

2026-10-23 — conserto. O emulador ficou ocupado pela DMCP-TASK-20 até a outra sessão avisar
"emulador livre", e o `procs` estava vazio antes de cada corrida.

**Medido nas três capturas da DMCP-TASK-19** (`before1`, `before2`, `after1`):
- na caixa só do valor de `Dia/Noche`, sem as setas (`(540, 90, 745, 120)`), o `Right` dá **0,04098**
  nas três;
- o quadro inteiro dá 0,00048;
- entre corridas, a mesma caixa dá 0,00000.

**Conserto no `mcp_drive.py`:**
- A guarda compara `DIA_NOCHE_VALUE` com o limiar `DIA_NOCHE_CHANGED = 0.01`. Ela também mede o ruído na
  mesma caixa, entre duas capturas sem aperto com meio segundo de jogo entre elas, e imprime os dois
  números; ruído no limiar ou acima dele também falha.
- Com a guarda passando, a rota caiu no passo seguinte: `no frame reached mean=0.2499 (+-0.01) in 40
  slices; the closest was 0.263730`. Uma sonda de rascunho capturou o quadro onde ela parava, e era a
  tela de ordem dos cobradores, completa e parada (0,26381; 0,26387 três segundos depois).
- `KICKER_ORDER_MEAN` foi para **0,2638**. A hipótese é o estádio iluminado agora que `Día` é fixado; a
  média noturna não foi medida. O valor fica fora da faixa do gramado (0,295 a 0,315), e o
  `--self-check` continua `OK`.

Incluí a constante no conserto porque o defeito da CORR é a rota nunca chegar à tela de resultado, e
esse passo só apareceu quando a guarda deixou de travar antes dele.

Verificação, com o comando da Evidência, OUT no scratchpad:

```text
$ DISPLAY=:98 XAUTHORITY= python3 tools/pes2/mcp_drive.py "work/pes2-EsIt/Pro Evolution Soccer 2 (Europe) (Es,It).cue" --screen result --out-dir "$OUT"; echo "rc=$?"
…
  Dia/Noche value box: 0.04098 after Right, 0.00000 without a press (changed above 0.01)
  Cross confirms the options -- Start does not
  recognised  mean=0.263988
  shot kicker-order  mean=0.263988 sd=0.201402  …/kicker-order.png
  Square starts the shootout
…
  the shootout ended after 49 kicks (mean=0.275115)
  the post-match box is up (box sd=0.193563)
  shot result  mean=0.275220 sd=0.202504  …/result.png
MCP DRIVE OK: …  192.3s, 59 presses, 1212 frames stepped
rc=0
$ python3 tools/duckmcp/cli.py procs | head -1
pids: []
$ python3 tools/pes2/mcp_drive.py --self-check | tail -1
SELF-CHECK OK: routes, thresholds, regions, signatures
```

Controle da guarda, da mesma corrida: sem aperto a caixa dá **0,00000**, abaixo do limiar de 0,01, e com
aperto dá 0,04098. Um `Right` que não mudasse o valor ficaria vermelho. O `result.png` mostra
`Pasar al siguiente partido`. Ficou para a DMCP-TASK-19 medir o PNG de `result` antes e depois.
