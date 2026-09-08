---
id: MCR-TASK-14
title: "Verificação final contra a definição de pronto"
type: verificação
category: processo
phase: 4
depends_on: ["MCR-TASK-12", "MCR-TASK-13"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §9"
status: pendente
---

# MCR-TASK-14: Fechamento

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §0 (definição
  de pronto) e §9 (entregáveis).

---

## Critério de conclusão

- [ ] Os seis itens da definição de pronto conferidos **um a um**, com o comando
      que reproduz cada um colado no Log.
- [ ] **O item 5 da definição de pronto — "a UI abre, edita, grava, e o
      arquivo gravado passa no round-trip" — só é medido com
      `WE2002_MCR_CARD` apontado.** Desde a MCR-TASK-12 o `mcr_ui` dirige os
      widgets, grava dois cartões e confere o round-trip dos dois; **sem** a
      variável ele passa com a janela sozinha e imprime `note: no
      WE2002_MCR_CARD, so the write probe did not run`. O comando do Log é
      `WE2002_MCR_CARD=$PWD/work/entrada.mcr ctest --test-dir build -R mcr -V`,
      e o que se cola é a linha `probe:`, não o `Passed` — é a mesma armadilha
      que a receita de PES2 registra, onde `100% tests passed` convivia com o
      único gate que põe o jogo na tela pulando em 0,01 s.
- [ ] O plano atualizado com o que a execução mediu — inclusive o que saiu
      diferente do previsto, que é o que vale registrar.
- [ ] **A §5.4 do plano diz "os 30 campos" e são 29.** Medido na MCR-TASK-06
      contra o próprio `Player.cpp`, que é quem define o conjunto:
      `awk '/^void Player::Decode/,/^}/' src/core/Player.cpp | grep -oE '^\t[a-z_]+ =' | sed 's/[ \t=]//g' | sort -u | wc -l`
      devolve **29**, e `python3 tools/mcr/attributes.py --self-check` afirma o
      mesmo no primeiro check. O texto da MCR-TASK-06 já foi corrigido; o plano
      não.
- [ ] **A §1.1 do plano remedida**, que a MCR-TASK-04 tocou e nenhuma outra
      task remede: ela cita a entrada 1 do diretório em bytes crus e **não diz
      que a cadeia tem dois blocos**. O comando é
      `python3 tools/mcr/card.py <cartão> --json`, e o que ele tem de dizer é
      `"blocos": [1, 2]`, `"tamanho_declarado": 16384` e um único bloco fora da
      cadeia (o 3, `0xA0`, 41 bytes não-zero). Se o plano continuar mudo sobre
      a cadeia, acrescente a frase.
- [ ] **A §3.2 do plano nomeava `io.py` e o módulo é `mcrio.py`.** Corrigida na
      MCR-TASK-09, junto com a menção na Regra 3 da §3.3; confira que as duas
      continuam batendo com o disco:
      `ls tools/mcr/*.py` e `grep -n 'mcrio' docs/PLAN-MCR-PY.md`. A razão está
      medida no `self_check` do `mcrio.py` — `import io` devolve a stdlib.
      **A mesma linha errava uma segunda vez**, e a
      [CORR-MCR-013](/docs/tasks/port-mcr/CORR-MCR-013.md) a corrigiu: ela dava
      `Card` como dataclass do `model.py`, e `Card` é classe comum e mora em
      `card.py`, `Formation` mora em `formation.py`, e o `Save` não aparecia no
      plano inteiro. Confira contra o disco:
      `grep -n '^class \|^@dataclasses.dataclass' tools/mcr/model.py
      tools/mcr/card.py tools/mcr/formation.py`.
- [ ] **A §5.1 do plano diz "as duas formas" e não diz que a forma 2 precisa de
      companheira.** Medido na MCR-TASK-09: um `Save.write()` cujo laço não
      escreve ninguém deixa toda checagem de "não mudou byte" verde, porque
      escrever ninguém não muda nada. O `model.py` ganhou um check que prova
      que o escritor rodou; se o plano continuar mudo, acrescente a frase.
- [ ] **A §3.5 do plano põe `tests/CMakeLists.txt` e o `Makefile` no mesmo
      saco, e eles não estão.** Medido na MCR-TASK-10: os comentários do
      `tests/CMakeLists.txt` são **ingleses** desde antes deste ciclo (o bloco
      de PES2 inteiro é), e o `Makefile` é português. A regra que vale — seguir
      o idioma **do arquivo** — é a mesma; a frase é que generaliza demais.
      O comando é `grep -nE '^\s*#' tests/CMakeLists.txt` e
      `sed -n '1,10p' Makefile`: **o arquivo inteiro**, não as vinte primeiras
      linhas. A MCR-TASK-12 reescreveu o bloco do `mcr_ui` em português — 6 das
      74 linhas de comentário, e nenhuma delas nas vinte primeiras —, a
      [CORR-MCR-019](/docs/tasks/port-mcr/CORR-MCR-019.md) repôs, e o episódio
      é o argumento: enquanto a §3.5 tolerar os dois idiomas neste arquivo, a
      consistência dele é o único critério que sobra, e ela se perde sem que
      varredura nenhuma reclame — a `glossary.sweep()` cobre `tools/mcr/**.py`
      e não alcança o CMake, por desenho.
- [ ] [`/docs/prompts/perfil-mcr.md`](/docs/prompts/perfil-mcr.md) com as
      decisões confirmadas, as armadilhas medidas, os gates e os arquivos
      quentes do ciclo.
- [ ] `CLAUDE.md` com a seção do projeto, no formato da de PES2: o que é, onde
      mora, como se roda, e as três armadilhas que custam tempo.
- [ ] `NOTICE.md` conferido: linhagem, SHA e a diferença de método.
- [ ] `python3 tools/check_tasks.py` e `ctest -R 'tasks|mcr'` verdes.
- [ ] Nada do upstream no repositório; `roms/` e o cartão do usuário intocados.

---

## Log de Execução

*(a preencher)*
