---
id: MCR-TASK-14
title: "Verificação final contra a definição de pronto"
type: verificação
category: processo
phase: 4
depends_on: ["MCR-TASK-12", "MCR-TASK-13"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §9"
status: concluído
---

# MCR-TASK-14: Fechamento

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §0 (definição
  de pronto) e §9 (entregáveis).

---

## Critério de conclusão

- [x] Os seis itens da definição de pronto conferidos **um a um**, com o comando
      que reproduz cada um colado no Log.
- [x] **O item 5 da definição de pronto — "a UI abre, edita, grava, e o
      arquivo gravado passa no round-trip" — só é medido com
      `WE2002_MCR_CARD` apontado.** Desde a MCR-TASK-12 o `mcr_ui` dirige os
      widgets, grava dois cartões e confere o round-trip dos dois; **sem** a
      variável ele passa com a janela sozinha e imprime `note: no
      WE2002_MCR_CARD, so the write probe did not run`. O comando do Log é
      `WE2002_MCR_CARD=$PWD/work/entrada.mcr ctest --test-dir build -R mcr -V`,
      e o que se cola é a linha `probe:`, não o `Passed` — é a mesma armadilha
      que a receita de PES2 registra, onde `100% tests passed` convivia com o
      único gate que põe o jogo na tela pulando em 0,01 s.
- [x] O plano atualizado com o que a execução mediu — inclusive o que saiu
      diferente do previsto, que é o que vale registrar.
- [x] **A §5.4 do plano diz "os 30 campos" e são 29.** Medido na MCR-TASK-06
      contra o próprio `Player.cpp`, que é quem define o conjunto:
      `awk '/^void Player::Decode/,/^}/' src/core/Player.cpp | grep -oE '^\t[a-z_]+ =' | sed 's/[ \t=]//g' | sort -u | wc -l`
      devolve **29**, e `python3 tools/mcr/attributes.py --self-check` afirma o
      mesmo no primeiro check. O texto da MCR-TASK-06 já foi corrigido; o plano
      não.
- [x] **A §1.1 do plano remedida**, que a MCR-TASK-04 tocou e nenhuma outra
      task remede: ela cita a entrada 1 do diretório em bytes crus e **não diz
      que a cadeia tem dois blocos**. O comando é
      `python3 tools/mcr/card.py <cartão> --json`, e o que ele tem de dizer é
      `"blocos": [1, 2]`, `"tamanho_declarado": 16384` e um único bloco fora da
      cadeia (o 3, `0xA0`, 41 bytes não-zero). Se o plano continuar mudo sobre
      a cadeia, acrescente a frase.
- [x] **A §3.2 do plano nomeava `io.py` e o módulo é `mcrio.py`.** Corrigida na
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
- [x] **A §5.1 do plano diz "as duas formas" e não diz que a forma 2 precisa de
      companheira.** Medido na MCR-TASK-09: um `Save.write()` cujo laço não
      escreve ninguém deixa toda checagem de "não mudou byte" verde, porque
      escrever ninguém não muda nada. O `model.py` ganhou um check que prova
      que o escritor rodou; se o plano continuar mudo, acrescente a frase.
- [x] **A §3.5 do plano põe `tests/CMakeLists.txt` e o `Makefile` no mesmo
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
- [x] [`/docs/prompts/perfil-mcr.md`](/docs/prompts/perfil-mcr.md) com as
      decisões confirmadas, as armadilhas medidas, os gates e os arquivos
      quentes do ciclo.
- [x] `CLAUDE.md` com a seção do projeto, no formato da de PES2: o que é, onde
      mora, como se roda, e as três armadilhas que custam tempo.
- [x] `NOTICE.md` conferido: linhagem, SHA e a diferença de método.
- [x] `python3 tools/check_tasks.py` e `ctest -R 'tasks|mcr'` verdes.
- [x] Nada do upstream no repositório; `roms/` e o cartão do usuário intocados.

---

## Log de Execução

**Executado em:** 2026-09-08

### A definição de pronto, item por item

| # | item | comando | medido |
|---|---|---|---|
| 1 | round-trip nas duas formas | `python3 tools/mcr/mcrio.py work/pronto-14.mcr --roundtrip` | `form 1: 0 byte(s) differ` · `form 2: 0 byte(s) differ` |
| 2 | controle negativo 5/5 | `python3 tools/mcr/mcrio.py --negative` | `negative control: 5 of 5 guards fired` |
| 3 | `layout.py --check` 17/17 | `python3 tools/mcr/layout.py --check` | `17/17 destinations agree with wte/re/mcr.md` |
| 4 | codec com 0 divergências | `python3 tools/mcr/attributes.py --self-check` | `29 fields`; **100.000 blobs** nas quatro travessias, `0 failure(s)` |
| 5 | a UI abre, edita, grava, e o gravado passa no round-trip | `WE2002_MCR_CARD=$PWD/work/entrada.mcr ctest --test-dir build -R mcr -V` | `probe: one attribute moved 1 byte(s) at ['0x590d'], inside slot 0's record at 0x05904` · `probe: the gate asked for [14, 43] … and the drag landed on [14, 43], from [11, 32]` · `probe: both written cards round-trip` |
| 6 | máquina sem venv e sem fixture | `mv work/venv-mcr work/venv-mcr.oculto && env -u WE2002_MCR_CARD ctest --test-dir build -R mcr` | **1 passed, 2 skipped** (`mcr_card` e `mcr_ui`), e o venv de volta no lugar |

O item 5 traz também os quatro plantios que o próprio gate faz e exige
vermelhos: `to_card_x`, `to_card_y`, o alcance do capitão e a anotação do valor
fora do onze.

### O que estava errado no plano, e agora não está

- **§5.4 dizia "os 30 campos" e são 29.** Quem define o conjunto é o
  `Player::Decode`, e o `awk` da própria task devolve **29** — o mesmo que o
  primeiro check do `attributes.py` afirma.
- **§1.1 não dizia que a cadeia tem dois blocos.** Acrescentado, com o comando
  que o mede: `card.py --json` traz `"blocks": [1, 2]`,
  `"declared_size": 16384`, `"bad_checksums": []` e **um** bloco fora da cadeia
  (o 3, `0xa0`, 41 bytes não-zero).
- **§5.1 não dizia que a forma 2 precisa de companheira.** Acrescentado: um
  `Save.write()` que não escreve ninguém deixa toda checagem de "não mudou
  byte" verde, e o par é round-trip **mais** uma edição que reaparece.
- **§3.5 punha `Makefile` e `tests/CMakeLists.txt` no mesmo saco.** Corrigido
  com os dois números medidos: o `Makefile` é português inteiro, e as **74**
  linhas de comentário do `tests/CMakeLists.txt` são inglesas. E ficou escrito
  o que o episódio da CORR-MCR-019 mostrou — tolerar dois idiomas num arquivo
  custa o único critério que sobra, a consistência dele, e nenhuma varredura
  do ciclo o vigia.
- **§3.2 listava um `tactics.py` que nunca existiu, e não devia mesmo.** A §1.9
  e a §5.6 decidiram tática somente-leitura na v1; um módulo somente-leitura de
  seis bytes que ninguém lê não tem o que fazer. Os seis destinos moram em
  `layout.TACTICS`, e quem os defende é um check do `formation.py` que exige
  que gravar a formação não toque em nenhum. `ls tools/mcr/*.py` traz **15**
  módulos e nenhum é `tactics.py`.
- **§9 dizia "o núcleo (12 módulos)".** São **15** em `tools/mcr/` — os 12 que
  o `selftest` roda, mais o `cli.py`, o `selftest.py` e o `ui_check.py` — e
  **5** em `tools/mcr/ui/`. Acrescentado também o `tools/mcr/oracle/`, que a
  MCR-TASK-13 criou e o §9 não previa.
- **§3.2 e §3.3 sobre o `mcrio.py`** conferidas contra o disco e batendo:
  `ls tools/mcr/*.py` traz `mcrio.py` e não `io.py`, e
  `grep -n '^class \|^@dataclasses.dataclass'` confirma `Player` e `Save` no
  `model.py`, `Card` como classe comum no `card.py` e `Formation` no
  `formation.py` — que é o que a CORR-MCR-013 pôs no plano.

### Os quatro arquivos de fora

- **`docs/prompts/perfil-mcr.md`** — decisões confirmadas, as nove armadilhas
  medidas, as fontes binárias (com o `0x6500` já resolvido), os gates e os
  arquivos quentes. Ganhou a linha do `tools/mcr/oracle/`.
- **`CLAUDE.md`** — a seção existia com o que é, onde mora e as armadilhas, e
  faltava **como se roda**, que é metade do formato da seção de PES2.
  Acrescentada: a tabela de comandos, os três alvos de `ctest` e a ressalva de
  que o `mcr_ui` só mede gravação com `WE2002_MCR_CARD` apontado.
- **`NOTICE.md`** — conferido e correto: linhagem, o SHA `30af1fe5…37cc` (que
  bate com `git -C work/easy-mcr rev-parse HEAD`), a ausência de licença, a
  decisão do dono do repositório e a diferença de método para o ciclo `wte/`,
  lado a lado e com a razão de cada uma.
- **Nada do upstream versionado.** `git ls-files | grep -icE
  "easy-mcr|fifatomcr|\.vb$"` devolve **0**, e `work/easy-mcr`, `roms/` e
  `work/entrada.mcr` estão todos sob `git check-ignore`.

### Problemas encontrados

- **`chmod -x` no python do venv desliga o interpretador da máquina.** Foi a
  primeira tentativa de simular "máquina sem venv" para o item 6, e o `chmod`
  **segue symlink**: `work/venv-mcr/bin/python` → `python3` → o binário do mise,
  que é o mesmo que o `build/CMakeCache.txt` fixou. Os três alvos saíram
  `***Not Run` — nem falha, nem skip —, que é justamente o sintoma de o
  interpretador não poder ser executado. Restaurado com `chmod +x` e conferido
  (`python3 -c`, `ctest -R mcr_selftest` verde) antes de seguir. **A forma certa
  é `mv work/venv-mcr work/venv-mcr.oculto`**, e foi ela que produziu o
  `1 passed, 2 skipped` da tabela.
- **O item 6 pedia um número que só se mede desmontando o ambiente.** Vale
  registrar que ele **não** é medido por nenhum gate contínuo: é uma medição de
  fechamento, feita à mão, e quem a repetir tem de repor o venv.
- Nada mais. Os seis itens fecharam na primeira passagem.
