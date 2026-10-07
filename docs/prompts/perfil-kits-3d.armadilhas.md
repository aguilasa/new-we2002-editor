# Measured pitfalls — kits

<!--
One entry per pitfall. Commands search this file by tag or path; it is never read whole.
Format:

### <short title>
- tags: <tag>, <tag>
- paths: <glob>
- proven by: <FIX-ID or commit> (<YYYY-MM-DD>)
- rule: <what to do instead, in one sentence>
-->

### Edição fora do `files` declarado
- tags: escopo, files, passagem
- paths: docs/tasks/kits/*.md, docs/PLAN-KITS-PY.md, docs/prompts/perfil-kits.md
- proven by: CORR-KITS-089 (2026-10-07); also 012, 015, 024, 043, 046, 049, 055, 056, 075, 078, 081, 085, 086
- rule: nota de passagem a outra task, defeito achado no caminho ou edição de plano/perfil entra por `rite set <ID> --files …` e uma linha em "Arquivos a criar ou modificar" no mesmo commit, ou fica fora do commit.

### Constante nova acima da docstring da anterior
- tags: docstring, constante, python
- paths: tools/kits/**/*.py
- proven by: CORR-KITS-088 (2026-10-07); also 065, 070
- rule: cada constante leva a docstring logo abaixo; constante nova entra depois da docstring da anterior, nunca na linha seguinte à constante.

### Receita de gate no Log sem caminho absoluto
- tags: log, ctest, ambiente
- paths: docs/tasks/kits/*.md
- proven by: CORR-KITS-063 (2026-10-05); also 060, 034
- rule: o `ctest` roda de `build/tests`, então `WE2002_LOOKS_IMAGE=$PWD/…` absoluto, e toda variável vai dentro do comando transcrito, nunca de um shell já exportado.

### Juiz que imprime em vez de afirmar
- tags: gate, juiz, planta
- paths: tools/kits/ui_check.py, tools/kits/oracle.py
- proven by: CORR-KITS-087 (2026-10-06); also 047, 073, 082
- rule: tudo o que o critério diz, inclusive onde e em que conjunto, é asserção com planta vista vermelha; linha só impressa conta como gate ausente.

### Resultado negativo não fecha critério
- tags: fechamento, critério, bloqueio
- paths: docs/tasks/kits/*.md
- proven by: CORR-KITS-071 (2026-10-05); also 062, 079
- rule: se o instrumento planejado foi trocado ou o caso que decide não rodou, a task vai a blocked com `--unblocked-by`, não a done.
