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
- proven by: CORR-KITS-089 (2026-10-07); also 012, 015, 024, 043, 046, 049, 055, 056, 075, 078, 081, 085, 086; CORR-K3D-002, 006, 018, 025, 028 (2026-10-07 a 2026-10-11)
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

### Juiz não tira o esperado do medido
- tags: gate, juiz, oráculo
- paths: tools/kits/oracle.py, tools/kits/ui_check.py
- proven by: CORR-K3D-020 (2026-10-09); also 012
- rule: o valor que o plano afirma vira constante esperada por (slot, linha) no oráculo; cabeça, número ou contagem lidos da própria captura só provam consistência interna.

### Planta que fica vermelha por outro ramo
- tags: gate, planta, controle
- paths: tools/kits/oracle.py, tools/kits/ui_check.py, tools/kits/controls.py
- proven by: CORR-K3D-016 (2026-10-09); also 007, 013, 024
- rule: a planta tem de derrubar a asserção que diz cobrir, o juiz imprime qual asserção falhou e o Log mostra essa linha; vermelho por reenquadramento da vista, por diferença de pixel no lugar do tempo ou por "no second figure" não conta.

### Linha `$` diferente do que rodou
- tags: log, transcrição, comando
- paths: docs/tasks/kits-3d/*.md, docs/KITS-AJUSTES-3D.md
- proven by: CORR-K3D-033 (2026-10-12); also 004, 010
- rule: a linha `$` traz toda flag que a corrida usou (inclusive `--frame-json`), a saída vai inteira, e recorte ou montagem de imagem só entra com comando versionado.

### Controle físico vazando ao fork no :98
- tags: emulador, sdl, ambiente
- paths: tools/kits/oracle.py
- proven by: CORR-K3D-031 (2026-10-12)
- rule: o `[Pad1]` da máquina é `SDL-0` e o SDL entrega o controle a qualquer display, então desligue o controle físico antes de dirigir o fork; corridas seguidas que divergem sem toque são o sintoma.

### Reordenou botão ou constante, refaça corrida e prosa
- tags: docstring, negativa, oráculo
- paths: tools/kits/oracle.py, docs/KITS-AJUSTES-3D.md
- proven by: CORR-K3D-022 (2026-10-09); also 021
- rule: docstring e negativa escritas antes de uma reordenação descrevem um comando que a HEAD não roda; refaça a corrida na HEAD e reescreva as duas.
