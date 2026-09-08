---
id: MCR-TASK-09
title: "`model.py`, `mcrio.py` e o round-trip byte-idêntico"
type: implementação
category: núcleo
phase: 1
depends_on: ["MCR-TASK-06", "MCR-TASK-07", "MCR-TASK-08"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §5.1"
status: concluído
---

# MCR-TASK-09: O modelo e o round-trip

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §5.1 e §3.3
  (Regra 2).
- **Os bytes crus são normativos.** `model.Card` guarda os 131.072 bytes e edita
  por read-modify-write no campo; nada mais é tocado. É o que faz os 10 bytes
  finais de cada registro, a folga do bloco, o diretório e os seis campos de
  tática atravessarem intactos.
- O contraexemplo é o upstream, que remonta o arquivo — e é por isso que ele
  consegue escrever no cabeçalho.

---

## Objetivo

O modelo em `dataclasses` sem Qt e sem endereço, o I/O que valida e recusa, e o
round-trip que prova os dois.

---

## Critério de conclusão

- [x] `Player`, `Save` e `Formation` como `dataclasses`; nenhum endereço fora de
      `layout.py`; nenhum `import` de Qt. O contêiner `card.Card` **continua
      classe comum** — ele guarda um `bytearray` mutável e valida no construtor,
      e `@dataclass` ali não acrescentaria nada. A **§3.2** escrevia "`Card`,
      `Player` e `Formation`"; o que a execução entregou é o nível do modelo:
      `Player` e `Save` novos em `model.py`, `Formation` já era `dataclass`.
- [x] **Round-trip forma 1** — ler → gravar: `cmp` = **0 bytes**.
- [x] **Round-trip forma 2** — ler → decodificar os 23 → re-codificar todos →
      gravar: `cmp` = **0 bytes**. É esta que pega bug de encoder.
- [x] O **controle negativo** completo, 5/5 vermelhos (§5.2 do plano) — mais
      sete controles de substituição literal, 7/7 vermelhos.
- [x] Gravação **sempre sobre cópia**; a ferramenta recusa escrever no arquivo
      apontado por `WE2002_MCR_CARD` sem `--force`, e recusa `roms/` mesmo
      **com** `--force`.
- [x] Uma edição de ponta a ponta medida no Log: mudar um atributo de um
      jogador muda **exatamente** os bytes esperados, e nada mais.

---

## Log de Execução

**Executado em:** 2026-09-08

### Resumo do que foi feito

`tools/mcr/model.py` (366 linhas) e `tools/mcr/mcrio.py` (491 linhas): o modelo
em `dataclasses` sobre os bytes crus, o I/O que valida e recusa, e as duas
formas do round-trip — **0 bytes de diferença** nas duas, contra a fixture e
contra um cartão sintético. O controle negativo da §5.2 roda por comando
(`mcrio.py --negative`, **5/5 vermelhos**).

Três coisas que a execução mediu e o plano não dizia: **o módulo não pode se
chamar `io.py`**; **um cartão zerado não tem formação para preservar**; e
**"não mudou byte" fica verde quando o escritor não escreve ninguém**.

### O nome `io.py` é inutilizável, e o plano dizia `io.py`

A §3.2 nomeava `io.py`. Todo módulo deste ciclo põe `tools/mcr` na frente do
`sys.path`, e `io` é módulo da biblioteca padrão que o CPython **já importou e
cacheou** antes de qualquer linha nossa rodar — a máquina de import precisa
dele. Medido:

```
$ python3 -c "import sys; sys.path.insert(0, '/tmp/shadowtest'); import io; \
              print(io.__file__, hasattr(io, 'MARK'))"
/home/ingmar/.local/share/mise/installs/python/3.13.13/lib/python3.13/io.py False
```

O arquivo local existe, tem `MARK`, e `import io` não o alcança. Um `io.py`
aqui rodaria como script e seria **importável por ninguém** — fatal para o
`selftest.py` da MCR-TASK-10, que agrega os `self_check()` por import. O módulo
chama-se `mcrio.py`; o plano foi corrigido na §3.2 e na Regra 3 da §3.3, a
MCR-TASK-10 ganhou a linha, e a asserção que prova o motivo mora no próprio
`self_check` — ela compara o diretório de onde `io` veio com o diretório deste
módulo, em vez de afirmar isso em prosa.

### As duas formas do round-trip, medidas

```
$ python3 tools/mcr/mcrio.py <cópia da fixture> --roundtrip
form 1: 0 byte(s) differ
form 2: 0 byte(s) differ
```

Forma 1 prova o I/O; forma 2 decodifica os 23 registros para o modelo,
**re-codifica todos** e grava — é a que põe o encoder sob teste. As duas passam
por arquivo de verdade, porque "o I/O" é justamente o que a forma 1 mede;
comparar dois buffers em memória pularia a parte testada.

### A edição de ponta a ponta: exatamente os bytes nomeados

```
$ python3 tools/mcr/mcrio.py <cópia> --edit-probe 0 technique 12
technique=12 on slot 0: 1 byte(s) moved
  0x0590d

$ python3 tools/mcr/mcrio.py <cópia> --edit-probe 0 number 30
number=30 on slot 0: 2 byte(s) moved
  0x05404
  0x05907
```

Um atributo comum move **um byte**, dentro dos 12 do registro do jogador 0
(`0x5904 + 9`). O dorsal move **dois**, e são exatamente os dois que a §1.5
prevê: a tabela de 5 bits em `0x5404` e o byte 3 do registro (`0x5904 + 3`, o
`1 + ((raw[3]>>2)&0x1f)`). Os dez bytes finais do registro, a folga do bloco, o
diretório e os seis campos de tática não se mexem — é a Regra 2 medida em vez
de afirmada.

`--edit-probe` **reporta** os offsets em vez de afirmá-los, para que o número
deste log saia de ferramenta versionada e não de contagem à mão.

### O controle negativo da §5.2, por comando

```
$ python3 tools/mcr/mcrio.py --negative
  RED   swap speed and dribbling in the encoder  ->  form 2 of the round-trip
  RED   drop the -1 from the shirt-number write  ->  the cross-check of the two encoders
  RED   write 138 bytes at offset 0  ->  the refusal below the directory
  RED   flip the state of frame 1 to free  ->  the directory validation
  RED   truncate the card by one byte  ->  the size validation
negative control: 5 of 5 guards fired
```

As cinco injeções são aplicadas a **dado e comportamento**, não editando fonte:
cada uma reproduz o que o defeito faria e pergunta ao guard que a possui. A
injeção 2 é literal — gravar `n + STORED_BIAS` armazena `n`, que é exatamente o
que a falta do `−1` faz.

### E os sete controles de substituição literal, 7/7 vermelhos

Estes provam o outro lado: que os guards **sabem** ficar vermelhos. Cada um
numa cópia da árvore em `/tmp`, com `wte/re/mcr.md` levado junto e
`WE2002_MCR_CARD` apontando para a fixture — senão o check pula e o controle
sai verde à toa, que foi o que a MCR-TASK-08 mediu. A substituição casou **1×**
em todos.

| # | arquivo :: função | de | para | resultado |
|---|---|---|---|---|
| 1 | `mcrio.py` :: `check_destination` | `if READ_ONLY_DIR in parts:` | `if False:` | 🔴 mcrio, 2 falhas |
| 2 | `mcrio.py` :: `check_destination` | `if not force:` | `if False:` | 🔴 mcrio, 1 falha |
| 3 | `mcrio.py` :: `check_card` | `if found is None:` | `if False:` | 🔴 mcrio, 2 falhas |
| 4 | `model.py` :: `Save.write_player` | `if not 0 <= index < SQUAD_SIZE:` | `if False:` | 🔴 model, 2 falhas |
| 5 | `model.py` :: `Save.set_number` | `p.shirt_number = number` | `pass` | 🔴 model **e** mcrio — 4 e 1 falhas (era 3 e 1; a quarta é o conjunto fechado da [CORR-MCR-012](/docs/tasks/port-mcr/CORR-MCR-012.md), e o 1 do `mcrio` já era vermelho e não estava anotado) |
| 6 | `model.py` :: `Save.write` | `for i in range(SQUAD_SIZE):` | `for i in range(0):` | 🔴 model **e** mcrio, 1 falha cada |
| 7 | `model.py` :: `Save._write_number` | `table[index] = number` | `if table[index] != number:`⏎`    self.card.write(layout.player_attribute_address(5) + 22, b"\x7f")`⏎`table[index] = number` | 🔴 model **e** mcrio, 1 falha cada |

O 4 merece nota: com a guarda de índice desligada, o que sobe é `IndexError` e
`LayoutError`, não `ModelError` — e o `refuses()` reporta isso como falha
("raised X, expected ModelError"), que é o comportamento certo. A asserção é
sobre *qual* recusa dispara, não sobre haver alguma.

O 7 é o que a [CORR-MCR-012](/docs/tasks/port-mcr/CORR-MCR-012.md) plantou, e
existe porque nenhum dos outros seis alcança o conjunto de bytes que uma
gravação de dorsal toca. Ele escreve um byte nos **dez intocados** do jogador 5
e só quando o dorsal **muda**, o que o faz sobreviver ao round-trip — este
regrava os mesmos valores e não dispara o ramo. Antes do conserto os dois
`--self-check` saíam `rc=0`, `0 failure(s)`, com o check nomeado dizendo `ok`;
depois dele saem `rc=1`, e o `moved=` de cada um imprime o `0x059ba` plantado.

### Os gates da fase

| gate | resultado |
|---|---|
| `model.py --self-check` | 19 checks, `rc=0` |
| `mcrio.py --self-check` | 17 checks, `rc=0` |
| os nove módulos | card 27, layout 29, attributes 22, numbers 17, text 23, domains 15, formation 25, model 19, mcrio 17 — todos `rc=0` |
| `layout.py --check` | 17/17 destinos batem com `wte/re/mcr.md` |
| `layout.py --rule1` | **0** endereços fora de `layout.py` |
| `domains.py --check work/easy-mcr` | 14/14 tabelas de rótulo |
| `attributes.py --upstream-weights work/easy-mcr` | 21/21 |
| Regra 3 | `PySide6` ausente de `sys.modules` após importar os nove |
| `tools/check_tasks.py` | 100 task(s), ok |
| fixture | `sha256 e53f4895affe075bced499a32ba736d10a20f72b010c9c8c05c1269e77c47546`, intocada antes e depois |

### Arquivos criados/modificados

- `tools/mcr/model.py` — **novo**, o modelo
- `tools/mcr/mcrio.py` — **novo**, o I/O, as recusas e o controle negativo
- `tools/mcr/formation.py` — uma cláusula na mensagem de recusa de papel
  negativo (ver "Problemas encontrados", item 2)
- `docs/PLAN-MCR-PY.md` — §3.2 (`io.py` → `mcrio.py`, com o motivo) e a Regra 3
  da §3.3
- `docs/prompts/perfil-mcr.md` — duas linhas na Fase 1: a companheira que o
  round-trip precisa, e o nome do módulo de I/O
- `docs/tasks/port-mcr/10-selftest-cli-e-gate.md` — duas linhas: o nome do
  módulo de I/O e os **nove** módulos com `self_check()`
- `docs/tasks/port-mcr/14-verificacao-final.md` — duas linhas no quadro de
  recontagem: a §3.2 corrigida e o silêncio da §5.1 sobre a companheira da
  forma 2
- `docs/tasks/port-mcr/progresso.md` — a linha desta task e o checklist

Nenhum alvo de `ctest` foi criado: o perfil diz que **antes da MCR-TASK-10 não
há gate deste ciclo**, e `tests/CMakeLists.txt` é dela.

### Problemas encontrados

**1. O nome `io.py` do plano é inutilizável.** Detalhado acima. É o primeiro
achado deste ciclo que corrige o **plano** e não uma task, e o custo de
descobri-lo dentro da MCR-TASK-10 seria bem maior: lá o sintoma seria "o
agregador não vê o módulo", com um `import io` que funciona e traz outra coisa.

**2. Um cartão zerado não tem formação para preservar.** O primeiro
`model.py --self-check` morreu com `role[0]=-2 is outside 0..19`: o papel é
gravado como índice + 2, então uma região de zeros — cartão sintético, save
recém-criado — lê de volta como −2, e o `formation.write` recusa. A recusa está
**certa**; a mensagem é que não dizia por que o número era negativo. Ganhou uma
cláusula que nomeia o byte armazenado e o caso da região zerada, e o
`self_check` planta uma formação antes de medir round-trip — o que ele mede
passou a ser o round-trip, não o cartão em branco. O caso virou check próprio.

**3. "Não mudou byte" fica verde quando o escritor não escreve ninguém.** O
controle 6 trocou o laço de `Save.write` por `range(0)` e o `model.py` saiu
**verde**: todas as checagens de round-trip são satisfeitas por um escritor que
não escreve. Só o `mcrio.py` pegou, pela injeção 1. O conserto foi um check
companheiro no `model.py` — editar o último jogador, gravar, reler e exigir o
valor de volta —, e depois dele o controle 6 fica vermelho nos dois. **Toda
checagem de round-trip precisa de uma companheira que prove que o escritor
rodou**; encaminhado para a §5.1 do plano pela linha nova na MCR-TASK-14.
