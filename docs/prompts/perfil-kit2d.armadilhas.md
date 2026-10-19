# Measured pitfalls — kit2d

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
- proven by: CORR-KITS-089 (2026-10-07); also 012, 015, 024, 043, 046, 049, 055, 056, 075, 078, 081, 085, 086; CORR-K3D-002, 006, 018, 025, 028; CORR-KRP-020, 022 (2026-10-07 a 2026-10-16)
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
- proven by: CORR-K3D-033 (2026-10-12); also 004, 010; CORR-KRP-002, 026, 028 (2026-10-12 a 2026-10-17)
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

### `--json` condensado no Log
- tags: log, transcrição, json
- paths: docs/tasks/concluidos/kits-replay/*.md
- proven by: CORR-KRP-030 (2026-10-19); also 005, 012, 019, 023
- rule: com `--json` o Log cola o documento inteiro, ou a linha `$` roda o modo texto; resumo de extrator, placeholder (`<f>`) e `…` não são saída de ferramenta.

### Fixture simétrica numa asserção geométrica
- tags: selftest, fixture, geometria
- paths: tools/kits/selftest.py
- proven by: CORR-KRP-006 (2026-10-13)
- rule: asserção de desenho usa fixture assimétrica e rotação diferente da identidade; com quadrado centrado, espelho e rotação perdida passam verdes.

### Leitor ou ramo novo sem a própria planta
- tags: gate, planta, leitor
- paths: tools/kits/selftest.py, tools/kits/controls.py, tools/kits/core/replay.py
- proven by: CORR-KRP-018 (2026-10-16); also 004, 010, 024
- rule: cada leitor, ramo e código de saída novo (chaves do JSON, buffer escolhido, exit 2) ganha planta que o derruba; reaproveitar o juiz de outro leitor não o cobre.

### Flags e venv reescritos em vez de importados
- tags: reuso, confront, venv
- paths: tools/kits/core/replay.py, tools/kits/confront.py
- proven by: CORR-KRP-011 (2026-10-15); also 013
- rule: monte as flags do `app.py` e o caminho do venv com o código do `confront.py`; a cópia perdeu o `--kit-set` e o `Scripts/python.exe`.

### Fato de pressuposto medido por sonda
- tags: sonda, check, plano
- paths: tools/kits/core/replay.py, docs/PLAN-KITS-REPLAY.md
- proven by: CORR-KRP-029 (2026-10-19); also 016
- rule: o que sustenta um breakpoint ou uma faixa ("o arquivo está na RAM", "a caixa pega o vizinho") vira opção `--check` versionada antes de entrar no plano ou numa docstring.

### Desfazer sem varrer as decisões confirmadas
- tags: varredura, veredito, revert
- paths: docs/PLAN-KITS-REPLAY.md, docs/prompts/perfil-kits-replay.md, docs/KITS-REPLAYS-9-10.md
- proven by: CORR-KRP-031 (2026-10-19); also 014, 027, 032
- rule: fechar ou desfazer um veredito varre as listas de decisões confirmadas do plano e do perfil, a linha "Feito" da seção e o doc irmão; a data do desfazer é a do commit, não a da decisão.

### Gate sem margem e medida dependente do caminho
- tags: gate, timeout, ambiente
- paths: tests/CMakeLists.txt, tools/kits/confront.py, tools/kits/ui_check.py
- proven by: CORR-KRP-025 (2026-10-16); also 009
- rule: timeout de gate fica em pelo menos 1,5× o tempo medido, e confronto de pixel se mede com o caminho da imagem fixado, porque a vista 3D perde 30 px com caminho longo.
