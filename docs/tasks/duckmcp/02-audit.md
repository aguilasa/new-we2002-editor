---
id: DMCP-TASK-02
---

# DMCP-TASK-02 — `audit.py` — os sítios crus de MCP por projeto, o número do antes

## Goal

Existe `tools/duckmcp/audit.py`, a sonda versionada da regra (b) do §3.3: varre `tools/` fora de `tools/duckmcp/` e imprime, por projeto e por arquivo, os imports de `mcp`/`fork`/`savestate` de `tools/pes2/`, os `.client.call(` e `Client(` crus, e os `sys.path.insert` que apontam para `tools/pes2` ou `tools/looks`. O número que ele imprime nesta task é o "antes" do ciclo.

## Arquivos a criar ou modificar

- In:
  - `tools/duckmcp/audit.py`
  - um check no `selftest.py` que roda o audit sobre uma árvore sintética
- Out:
  - fazer a regra (b) falhar — ela só vira gate na Fase 4

## Done criteria

- [ ] `python3 tools/duckmcp/audit.py` sai 0 e a última linha dá o total; a saída inteira colada no Log
- [ ] `python3 tools/duckmcp/audit.py --json` dá o mesmo total que o modo texto
- [ ] o selftest roda o audit sobre uma árvore temporária com um `import fork` plantado e exige contagem 1, visto no Log
- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram

## Notes

Os números do §1.2 do plano vieram de leitura, não desta ferramenta; o Log não os repete.

## Log de Execução
