---
id: CORR-DMCP-017
---

# CORR-DMCP-017 — Capturar PngError no live.main para a última linha ser sempre o veredito

Origin: [DMCP-TASK-15](/docs/tasks/duckmcp/15-fechamento-fase-3.md)

## Problem

O docstring do `tools/duckmcp/live.py` promete "The last line is always
`duckmcp_live: <ok|FAIL|skipped> ...`". Mas o `read_back` decodifica a VRAM com `png.read_png`, que
levanta `PngError(ValueError)`, e o `main` só captura `Skip`, `Fail`, `NotRunning` e `ToolError`. Um
arquivo de VRAM que não decodifica encerra o gate com traceback, não com linha de veredito. O
`ValueError` que o `read_ram` levanta num tamanho errado também escapa.

## Evidência

```text
$ python3 - <<'PY'
import sys; sys.path.insert(0, "tools")
from duckmcp import fork, live, session
class C(session._FakeClient):
    def tools(self): return ["x"]
fork.running_pids = lambda: []
fork.kill = lambda verbose=True: 0
fork.launch = lambda image, display=None: (1, 2, C())
try:
    rc = live.main(["--image", "/x/a.cue"])
    print("rc", rc)
except BaseException as e:
    print("ESCAPED", type(e).__name__, e)
PY
read_ram: 2097152 bytes from 0x80000000
ESCAPED PngError /tmp/duckmcp-live-2ay9q8rl/vram.png does not open with a PNG signature
```

## Root cause

O caminho novo de leitura trouxe um tipo de exceção novo (`png.PngError`, um `ValueError`), e a tupla
de `except` do `main` não foi alargada.

## Fix

No `main` do `tools/duckmcp/live.py`, capturar também `png.PngError` (ou embrulhá-lo em `ToolError`
dentro do `read_back`) e imprimir `duckmcp_live: FAIL -- ...`; idem para o `ValueError` de tamanho.

## Arquivos a criar ou modificar

- `tools/duckmcp/live.py`

## Verificação

O heredoc da Evidência imprime `duckmcp_live: FAIL -- PngError: ...` seguido de `rc 1`, e não
`ESCAPED`.

## Log de Execução
