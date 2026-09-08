---
id: CORR-MCR-015
title: "Correção: o bloco do `mcr_ui` entrou entre o comentário do `pes2_boot` e o teste dele"
type: correção
category: processo
status: pendente
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

- [ ] `grep -n "^# \|add_test(NAME" tests/CMakeLists.txt` mostra cada
      `add_test` imediatamente sob o comentário que o descreve
- [ ] `cmake --preset debug` reconfigura sem aviso novo
- [ ] `ctest -R mcr` sem cartão continua **1 passed, 2 skipped**
- [ ] `make test` continua verde, com o mesmo número de testes
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
