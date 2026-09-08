---
id: CORR-MCR-015
title: "Correção: o bloco do `mcr_ui` entrou entre o comentário do `pes2_boot` e o teste dele"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-MCR-015: um comentário de DuckStation em cima de um teste de Qt

## Problema identificado

Em `tests/CMakeLists.txt`, o registro do `mcr_ui` foi inserido **entre** o
comentário do `pes2_boot` e o `add_test` dele. O resultado, hoje:

```
136 # Booting the game is a third cost bracket: it needs DuckStation, an X
137 # display and about ninety seconds of wall clock. Registered anyway, on the
138 # same terms as the golden tests -- it skips itself unless PES2_IMAGE names
139 # a working copy, so a machine without the emulator sees a skip and not a
140 # failure. Never runs in CI, for the same reason golden does not.
141 # The third mcr bracket needs the venv with PySide6 and an X display, which is
142 # the same class of dependency as the golden tests -- so it is UNIX-only and
143 # skips itself when the venv, the UI or the display is missing. Today it skips
144 # on the UI: tools/mcr/ui/app.py is MCR-TASK-11.
145 if(UNIX AND Python3_FOUND)
146     add_test(NAME mcr_ui
...
154 if(UNIX)
155     add_test(NAME pes2_boot
```

Duas leituras erradas de graça: quem lê o `mcr_ui` de cima para baixo atravessa
cinco linhas dizendo que ele precisa de **DuckStation**, de `PES2_IMAGE` e de
noventa segundos — nada disso é verdade sobre ele —, e o `pes2_boot`, que é o
teste que precisa dessas três coisas, fica **sem comentário nenhum**.

Os dois blocos de comentário também se contradizem sobre o mesmo assunto: o de
cima diz "third cost bracket" sobre o `pes2_boot` e o de baixo diz "the third
mcr bracket" sobre o `mcr_ui`.

`tests/CMakeLists.txt` é arquivo quente declarado do ciclo — o perfil diz "a
MCR-TASK-10 mexe; ninguém mais" —, e é o arquivo onde um comentário fora do
lugar sobrevive mais tempo, porque ninguém o lê fora de uma mudança de gate.

## Evidência

```
$ grep -n "^# \|add_test(NAME" tests/CMakeLists.txt | sed -n '/Booting the game/,$p'
136:# Booting the game is a third cost bracket: it needs DuckStation, an X
...
141:# The third mcr bracket needs the venv with PySide6 and an X display, which is
...
146:    add_test(NAME mcr_ui
155:    add_test(NAME pes2_boot
```

O comportamento dos dois testes está **certo** — `mcr_ui` pula com 77 dizendo
`tools/mcr/ui/app.py does not exist yet (MCR-TASK-11)`, `pes2_boot` pula sem
`PES2_IMAGE`, e `ctest -R mcr` dá 1 passed, 2 skipped. O defeito é só de
leitura.

## Causa raiz

O bloco novo foi acrescentado no fim da região dos testes de Python em vez de
depois do `endif()` do `pes2_boot`, e o comentário órfão ficou por cima dele.

## Correção

### Arquivo: `tests/CMakeLists.txt`

Mover o bloco `if(UNIX AND Python3_FOUND) … mcr_ui … endif()`, junto do seu
comentário (linhas 141-144), para **antes** do comentário do `pes2_boot`, ou o
bloco do `pes2_boot` para antes do do `mcr_ui`. Cada `add_test` volta a ficar
sob o comentário que o descreve.

Ao mover, reconciliar as duas frases "third … bracket": elas contam faixas de
projetos diferentes — a terceira do PES2 e a terceira do `mcr` —, e lado a lado
lêem-se como a mesma. Nomear o projeto em cada uma resolve.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tests/CMakeLists.txt` | modificar |

## Verificação

- [x] `grep -n "^# \|add_test(NAME" tests/CMakeLists.txt` mostra cada
      `add_test` imediatamente sob o comentário que o descreve
- [x] `cmake --preset debug` reconfigura sem aviso novo
- [x] `ctest -R mcr` sem cartão continua **1 passed, 2 skipped**
- [x] `make test` continua verde, com o mesmo número de testes
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-08

**Resumo do que foi feito:**

O bloco do `mcr_ui`, com o comentário dele, subiu para **antes** do comentário
do `pes2_boot`. Cada `add_test` do arquivo voltou a ficar imediatamente sob o
comentário que o descreve — conferido nos onze, não só nos dois.

As duas frases "third … bracket" ficaram: elas contam faixas de projetos
diferentes e agora dizem qual. A do PES2 passou a abrir com "Booting the PES2
game is **that project's** third cost bracket"; a do `mcr` já se identificava
("The third **mcr** bracket"), e o par de cima dela no mesmo `if` diz "The
mandatory one" e "The second", então a numeração fecha.

**Problemas encontrados:**

**A varredura achou, no mesmo arquivo, um número que a CORR-MCR-014 tinha
acabado de tornar falso.** O comentário do `mcr_selftest` dizia "It also plants
the **fourteen** negative controls", e são quinze desde o commit anterior deste
lote. É exatamente o caso que o `04-corrigir-tudo.md` prevê — a correção *k+1*
alcança o doc que a *k* escreveu. Corrigido aqui, junto com as duas ocorrências
gêmeas no `cli.py` (a docstring do módulo e o `help=` do `--negative`), que a
mesma varredura trouxe.

**Medições:**

| gate | número |
|---|---|
| `grep -n "^# \|add_test(NAME" tests/CMakeLists.txt` | cada `add_test` sob o seu comentário |
| `cmake --preset debug` | reconfigura, **0** avisos |
| `ctest -R mcr` sem cartão | **1 passed, 2 skipped** |
| `make test` | **10/10**, `100% tests passed` |
| `selftest.py` | `0 failure(s)` sobre 12 módulos |
| `grep -rn 'fourteen\|catorze' tools/mcr tests/CMakeLists.txt` | **vazio** |
| `roms/` | intocada |

**Arquivos criados/modificados:**

- `tests/CMakeLists.txt` — o bloco do `mcr_ui` movido, as duas frases "third
  bracket" nomeando o projeto, e a contagem de controles
- `tools/mcr/cli.py` — a mesma contagem, em dois lugares (varredura de
  discrepância)
