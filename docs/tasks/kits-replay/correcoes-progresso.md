# Fixes — kits-replay

<!-- rite:begin fixes -->
| ID | Title | Origin | Severity | Status | Done on |
| --- | --- | --- | --- | --- | --- |
| [CORR-KRP-001](/docs/tasks/kits-replay/CORR-KRP-001.md) | Figure sem o membro pieces de §2.1, e a ausência fora da lista de desvios | KRP-TASK-01 | low | done | 2026-10-12 |
| [CORR-KRP-002](/docs/tasks/kits-replay/CORR-KRP-002.md) | Comparação antes/depois do Log depende de work/krp02/run.sh, não versionado | KRP-TASK-02 | medium | done | 2026-10-12 |
| [CORR-KRP-003](/docs/tasks/kits-replay/CORR-KRP-003.md) | PLAN §2.2 diz nove controles movidos para o leitor; na fase 1 foram onze | KRP-TASK-03 | medium | done | 2026-10-13 |
| [CORR-KRP-004](/docs/tasks/kits-replay/CORR-KRP-004.md) | Leitores figure, figures, walk e panel sem asserção de chaves nem controle plantado | KRP-TASK-04 | medium | done | 2026-10-13 |
| [CORR-KRP-005](/docs/tasks/kits-replay/CORR-KRP-005.md) | Log da KRP-TASK-04 cola resumo de extrator não versionado e pasta placeholder | KRP-TASK-04 | medium | done | 2026-10-13 |
| [CORR-KRP-006](/docs/tasks/kits-replay/CORR-KRP-006.md) | Selftest do show não pega desenho espelhado nem sem rotação | KRP-TASK-05 | medium | done | 2026-10-13 |
| [CORR-KRP-007](/docs/tasks/kits-replay/CORR-KRP-007.md) | Comentário do selftest do show diz 21x21; o quadrado pinta 20x20 | KRP-TASK-05 | low | stale | 2026-10-13 |
| [CORR-KRP-008](/docs/tasks/kits-replay/CORR-KRP-008.md) | Intervalos entre toques de R1 na virada não são guardados nem julgados contra os 390 quadros | KRP-TASK-07 | low | done | 2026-10-14 |
| [CORR-KRP-009](/docs/tasks/kits-replay/CORR-KRP-009.md) | kits_selftest leva 260-275 s contra TIMEOUT 300 e estoura sob carga | KRP-TASK-07 | low | done | 2026-10-14 |
| [CORR-KRP-010](/docs/tasks/kits-replay/CORR-KRP-010.md) | confront --tab só guarda game_side; a escolha de buffer em game_pixels não tem asserção nem controle | KRP-TASK-06 | medium | done | 2026-10-15 |
| [CORR-KRP-011](/docs/tasks/kits-replay/CORR-KRP-011.md) | confront --tab não passa --kit-set ao app.py e o JSON declara um set que a aba não desenhou | KRP-TASK-06 | medium | done | 2026-10-15 |
| [CORR-KRP-012](/docs/tasks/kits-replay/CORR-KRP-012.md) | Log da KRP-TASK-06 traz resumo feito à mão e placeholder replay-<f> em vez da saída do confront --tab | KRP-TASK-06 | medium | done | 2026-10-15 |
| [CORR-KRP-013](/docs/tasks/kits-replay/CORR-KRP-013.md) | confront_tab fixa work/venv-looks/bin/python em vez de reusar confront.VENV_PYTHON | KRP-TASK-06 | low | done | 2026-10-15 |
| [CORR-KRP-014](/docs/tasks/kits-replay/CORR-KRP-014.md) | KITS-REPLAYS-9-10.md item 5 ainda diz que a frente nunca foi comparada | KRP-TASK-06 | low | done | 2026-10-15 |
| [CORR-KRP-015](/docs/tasks/kits-replay/CORR-KRP-015.md) | PLAN-KITS-REPLAY.md:60 aponta para âncora que não existe no KITS-REPLAYS-9-10.md | CORR-KRP-012 | low | done | 2026-10-15 |
| [CORR-KRP-016](/docs/tasks/kits-replay/CORR-KRP-016.md) | Filtro de caixa da peça em head_samples sem controle; as CLUTs vizinhas da §3.1 não se reproduzem por ferramenta | KRP-TASK-09 | medium | done | 2026-10-15 |
| [CORR-KRP-017](/docs/tasks/kits-replay/CORR-KRP-017.md) | Log da KRP-TASK-10 explica a frente de Marcos e as colunas de barba com o que a medição desmente | KRP-TASK-10 | medium | done | 2026-10-16 |
| [CORR-KRP-018](/docs/tasks/kits-replay/CORR-KRP-018.md) | Coluna de barba, match_scene com player e head --drawn sem controle plantado | KRP-TASK-10 | medium | done | 2026-10-16 |
| [CORR-KRP-019](/docs/tasks/kits-replay/CORR-KRP-019.md) | Log da KRP-TASK-10 cola resumo condensado sob dois comandos figure --json | CORR-KRP-017 | low | done | 2026-10-16 |
| [CORR-KRP-020](/docs/tasks/kits-replay/CORR-KRP-020.md) | KRP-TASK-11 edita docs/PLAN-KITS-REPLAY.md sem declará-lo, e as tasks de fechamento pendentes repetem o modelo | KRP-TASK-11 | medium | done | 2026-10-16 |
| [CORR-KRP-021](/docs/tasks/kits-replay/CORR-KRP-021.md) | Parágrafo da fase 3 lista como diferença do plano o que o plano já previa | KRP-TASK-11 | low | done | 2026-10-16 |
| [CORR-KRP-022](/docs/tasks/kits-replay/CORR-KRP-022.md) | KRP-TASK-22 declara docs/PLAN-KITS-REPLAY.md no files mas não em Arquivos a criar ou modificar | KRP-TASK-22 | medium | done | 2026-10-16 |
| [CORR-KRP-023](/docs/tasks/kits-replay/CORR-KRP-023.md) | Linhas $ do Log da KRP-TASK-22 encurtadas e o lado antes (ca147a8e) não mostrado | KRP-TASK-22 | medium | pending | — |
| [CORR-KRP-024](/docs/tasks/kits-replay/CORR-KRP-024.md) | head_judge não pega painel de cabeça largo demais, e o exit 2 de --player-looks inválido não tem gate | KRP-TASK-22 | low | done | 2026-10-16 |
| [CORR-KRP-025](/docs/tasks/kits-replay/CORR-KRP-025.md) | Altura da vista 3D depende do comprimento do caminho da imagem (940x409 contra 940x379) | KRP-TASK-22 | low | done | 2026-10-16 |
<!-- rite:end -->
