---
id: DMCP-TASK-03
---

# DMCP-TASK-03 — Regras de desenho (a), (c), (d) no selftest, e o `controls.py` da lib

## Goal

O selftest afirma as regras (a) sem dependência fora da stdlib no import, (c) nada de jogo dentro de `tools/duckmcp/` — serial no padrão `S[LC][EPU][SM]-\d{5}`, nome de projeto, endereço fora das faixas de hardware — e (d) só `env.py` lê ambiente. `tools/duckmcp/controls.py` planta cada uma numa cópia da árvore e exige o vermelho.

## Arquivos a criar ou modificar

- In:
  - as três regras e os controles delas
- Out:
  - a regra (b), que só fecha na Fase 4

## Done criteria

- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] `python3 tools/duckmcp/controls.py` sai 0 e a última linha diz quantos controles e de que regra
- [x] cada controle aparece vermelho no Log: `import PIL` em `errors.py`; `SLES-03957` num comentário que não é de linhagem; `os.environ` fora do `env.py`
- [x] `grep -rnE 'S[LC][EPU][SM]-[0-9]{5}|pes2|looks|kits' tools/duckmcp --include='*.py'` lista só linhas marcadas como linhagem ou dentro do próprio `selftest.py`/`controls.py`

## Notes

A faixa de endereço permitida mora no `psx.py`, que nasce na Fase 3; até lá a regra usa as faixas de RAM, scratchpad e I/O escritas no próprio selftest, e a DMCP-TASK-13 as move.

## Log de Execução

### 2026-10-22

O `selftest.py` ganhou `check_rules()`, que julga todo `.py` de `tools/duckmcp/` contra as regras (a), (c) e (d) do [§3.3](/docs/PLAN-DUCKMCP-PY.md#3.3), e o `controls.py` nasceu com onze controles, cada um uma substituição literal única numa cópia do pacote em pasta temporária.

Decisões tomadas na task:

- **Os cinco nomes legados do `env.py` têm lista de permissão própria.** A DMCP-TASK-01 deixou no Log que o `env.py` guarda `PES2_MCP_HOST`, `PES2_MCP_PORT`, `PES2_FORK`, `PES2_DUCKSTATION` e `PES2_DISPLAY` como literais, porque a decisão 3 do [§2](/docs/PLAN-DUCKMCP-PY.md#2) manda lê-los como fallback. O selftest os isenta pela constante `LEGACY_ENV_NAMES`, com docstring apontando a decisão, **só no `env.py` e só esses cinco**: um sexto `PES2_` no `env.py` (controle `c-sixth-legacy-name`) e um dos cinco fora dele (`c-legacy-name-elsewhere`) ficam vermelhos. Um check confere também que os cinco continuam no `env.py`, para a lista não sobrar morta.
- **O nome de projeto casa com fronteira não alfanumérica, não `\b`.** `_` é caractere de palavra, e `\bpes2\b` deixaria `PES2_SERIAL` passar.
- **Linhagem é bloco de comentário aberto por `# lineage:`**, e continua pelas linhas só de comentário seguintes (o `env.py` tem uma de duas linhas). Um `# lineage:` no fim de linha isenta só o comentário; o código antes dele é julgado (controle `c-code-before-lineage`). A isenção vale só para nome de projeto: serial e endereço são julgados em toda linha.
- **A regra (d) lê a árvore sintática**, não o texto: acesso `os.environ`/`os.getenv`/… , `from os import environ|getenv` e nome `environ`/`getenv` lido. O motivo é o `audit.py:366`, que tem `os.environ['K'] = 'emu'` **dentro de uma string** — fonte de uma árvore sintética do self-check dele —, e isso não lê ambiente. A menção a `XAUTHORITY` é textual.
- **A regra (a) tem duas metades**: a estática (todo `import` absoluto nomeia a stdlib ou o próprio pacote) e a carregada (um interpretador novo com `-I` importa cada módulo e diff do `sys.modules` contra `sys.stdlib_module_names`). Cada uma tem controle que só ela vê: `import PIL` derruba a estática mesmo numa máquina sem PIL, e um `__import__` de um módulo plantado ao lado do pacote só a carregada vê.
- **As faixas de endereço moram no selftest** (`HARDWARE_RANGES`: RAM e os espelhos KUSEG/KSEG1, scratchpad, I/O, BIOS) até o `psx.py` da DMCP-TASK-13; literal abaixo de `0x10000` não é julgado como endereço. Dois checks afirmam o juiz dos dois lados (aceita as faixas, recusa os vãos entre elas).
- `selftest.py` e `controls.py` ficam fora da regra (c) e da metade `XAUTHORITY` da (d), porque guardam os padrões que julgam; a (a) e a leitura de ambiente da (d) valem para eles também.
- O `controls.py` exige, além da saída diferente de zero, a linha `FAIL` da asserção que o controle diz cobrir; vermelho por outra asserção sai como `GREEN … red, but not on …`, e substituição que casa 0 ou mais de 1 vez sai `BROKEN`. Antes de qualquer controle a cópia intocada tem de sair verde.

```
$ python3 tools/duckmcp/selftest.py --quiet; echo exit=$?
duckmcp_selftest: 86 check(s) ran, 0 failure(s)
exit=0
```

```
$ python3 tools/duckmcp/controls.py; echo exit=$?
baseline: the untouched sandbox is green
red    a-import-pil (rule a): FAIL  rule (a) static: errors.py imports only the stdlib  line 11: PIL
red    a-hidden-import (rule a): FAIL  rule (a) loaded: import duckmcp.errors loads only the stdlib  dmcp_probe_dep
red    c-serial-in-comment (rule c): FAIL  rule (c): errors.py holds no game serial  line 11: SLES-03957
red    c-address-outside (rule c): FAIL  rule (c): errors.py has no address outside the hardware ranges  line 11: 0x12345678
red    c-sixth-legacy-name (rule c): FAIL  rule (c): env.py names no project outside a lineage comment  line 40: PES2
red    c-legacy-name-elsewhere (rule c): FAIL  rule (c): errors.py names no project outside a lineage comment  line 11: PES2
red    c-project-in-comment (rule c): FAIL  rule (c): errors.py names no project outside a lineage comment  line 11: pes2
red    c-code-before-lineage (rule c): FAIL  rule (c): errors.py names no project outside a lineage comment  line 11: looks
red    d-os-environ (rule d): FAIL  rule (d): errors.py does not read the environment  line 12: os.environ
red    d-from-os-getenv (rule d): FAIL  rule (d): audit.py does not read the environment  line 42: from os import getenv
red    d-xauthority (rule d): FAIL  rule (d): errors.py does not mention XAUTHORITY  line 11: XAUTHORITY
duckmcp_controls: 11 control(s), 11 red as required; per rule (a) 2/2, (c) 6/6, (d) 3/3
exit=0
```

```
$ grep -rnE 'S[LC][EPU][SM]-[0-9]{5}|pes2|looks|kits' tools/duckmcp --include='*.py'
tools/duckmcp/errors.py:8:# lineage: tools/pes2/fork.py (SKIP, Fail, Skip) and tools/pes2/mcp.py
tools/duckmcp/controls.py:64:        "\n# measured on SLES-03957\nSKIP = 77\n",
tools/duckmcp/controls.py:91:        "\n# as tools/pes2/fork.py did it\nSKIP = 77\n",
tools/duckmcp/controls.py:97:        "\nWHO = \"looks\"  # lineage: a trailing lineage comment\nSKIP = 77\n",
tools/duckmcp/selftest.py:65:literals. Exactly these five, and only in `env.py`: any other `PES2`/`pes2`
tools/duckmcp/selftest.py:72:PROJECT_RE = re.compile(r"(?<![A-Za-z0-9])(pes2|looks|kits|kit2d|we2002)"
tools/duckmcp/selftest.py:77:and `\\bpes2\\b` would let `PES2_SERIAL` through.
tools/duckmcp/selftest.py:294:    c.ok("rule (c): PROJECT_RE sees PES2_X and tools/pes2/, not pes20",
tools/duckmcp/selftest.py:296:             PROJECT_RE.search("tools/pes2/")) and not
tools/duckmcp/selftest.py:297:         PROJECT_RE.search("pes20"))
tools/duckmcp/env.py:26:# lineage: tools/pes2/fork.py:107-112, 237-246; tools/pes2/mcp.py:41-42;
tools/duckmcp/env.py:27:# tools/looks/oracle.py:330-352; tools/pes2/drive.py:185-190.
tools/duckmcp/env.py:32:# lineage: the legacy names below are the ones tools/pes2 exported before
```

Toda linha é comentário de linhagem (`errors.py:8`, `env.py:26-27` — a 27 continua o bloco aberto na 26 —, `env.py:32`) ou está dentro do `selftest.py`/`controls.py`. As linhas `PES2_*` do `env.py` não aparecem porque o `grep` é sensível a caixa; elas são as da lista de permissão.

```
$ cd build && ctest -R duckmcp_selftest
1/1 Test #24: duckmcp_selftest .................   Passed    0.16 sec
100% tests passed, 0 tests failed out of 1
```
