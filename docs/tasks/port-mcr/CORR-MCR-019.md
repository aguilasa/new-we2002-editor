---
id: CORR-MCR-019
title: "Correção: o comentário do `mcr_ui` voltou ao português num arquivo que a MCR-TASK-10 mediu como inglês, e a pendência da MCR-TASK-14 ficou apoiada num fato que deixou de valer"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-MCR-019: uma decisão medida revertida em silêncio, e o item aberto que ela invalida

## Problema identificado

O commit desta task reescreveu o comentário do alvo `mcr_ui` em
`tests/CMakeLists.txt` **de inglês para português**:

```diff
-# The third mcr bracket needs the venv with PySide6 and an X display, which is
-# the same class of dependency as the golden tests -- so it is UNIX-only and
-# skips itself when the venv, the UI or the display is missing. Today it skips
-# on the UI: tools/mcr/ui/app.py is MCR-TASK-11.
+# O terceiro bracket de mcr precisa do venv com PySide6 e de um display X, que
+# e a mesma classe de dependencia dos golden -- entao e UNIX-only e se pula
+# sozinho quando falta o venv, a UI ou o display. Desde a MCR-TASK-11 ele
+# passa; desde a MCR-TASK-12 ele tambem dirige os widgets, grava dois cartoes e
+# confere o round-trip deles, mas so quando WE2002_MCR_CARD aponta um cartao --
+# sem ele o alvo continua passando com a janela sozinha.
```

**O conteúdo novo está certo** — o alvo faz exatamente isso, e a ressalva do
`WE2002_MCR_CARD` é bem-vinda. O que mudou junto, sem ser dito, foi o idioma —
e este arquivo tem história registrada sobre isso.

A **MCR-TASK-10** mediu e escreveu, no item 4 dos "Problemas encontrados":

> A §3.5 do plano diz que `tests/CMakeLists.txt` é português, e ele é inglês.
> Os comentários do arquivo são ingleses desde antes deste ciclo (o bloco de
> PES2 inteiro é), enquanto o `Makefile` é português de verdade. Segui o idioma
> **de cada arquivo**, que é o que a regra quer dizer.

E o bloco que esta task reescreveu é **o mesmo bloco** que a MCR-TASK-10
escreveu em inglês, sob essa decisão.

**A pendência da MCR-TASK-14 ficou apoiada num fato que deixou de valer.** O
item aberto lá diz:

> os comentários do `tests/CMakeLists.txt` são **ingleses** desde antes deste
> ciclo (o bloco de PES2 inteiro é) … `sed -n '1,20p' tests/CMakeLists.txt` e
> `sed -n '1,10p' Makefile` decidem em duas linhas.

O arquivo agora é **misto**, e o `sed` das vinte primeiras linhas — que é o que
o item manda rodar — nem alcança as seis linhas novas. Quem executar a
MCR-TASK-14 mede um arquivo que não é mais o que o item descreve, e decide a
favor da §3.5 por uma evidência que a MCR-TASK-12 produziu sem querer.

**A §3.5 não resolve.** Ela lista `tests/CMakeLists.txt` entre "o que a regra
**não** alcança", então os dois idiomas lhe são permitidos — o que torna a
consistência **do arquivo** o único critério que sobra, e é justamente o que se
perdeu.

## Evidência

```
$ grep -cE '^\s*#' tests/CMakeLists.txt
74

$ grep -nE "^\s*#" tests/CMakeLists.txt | grep -icE \
    "\b(precisa|entao|sozinho|falta|desde|grava|cartoes|confere|continua|passando|janela|quando|aponta|tambem|dirige)\b"
6
```

Seis das setenta e quatro linhas de comentário, todas as seis introduzidas
por `2c7ec25`, e todas no bloco que a MCR-TASK-10 escreveu em inglês. O resto
do arquivo — inclusive os blocos de PES2 e os dois alvos irmãos `mcr_selftest`
e `mcr_card`, escritos pela MCR-TASK-10 — continua inglês, o que deixa os três
alvos do mesmo projeto documentados em dois idiomas, lado a lado.

A varredura de idioma do ciclo não pega isto e **não deveria**: a
`glossary.sweep()` cobre `tools/mcr/**.py`, que é código do port. O
`tests/CMakeLists.txt` está fora dela por desenho.

## Causa raiz

O bloco foi reescrito para acrescentar a ressalva do `WE2002_MCR_CARD` e saiu
no idioma de quem escrevia a documentação da task, sem consultar o idioma do
arquivo.

## Correção

### Arquivo: `tests/CMakeLists.txt`

Repor o comentário em inglês, **preservando o conteúdo novo**, que é o que
importa:

```cmake
# The third mcr bracket needs the venv with PySide6 and an X display, which is
# the same class of dependency as the golden tests -- so it is UNIX-only and
# skips itself when the venv, the UI or the display is missing. Since
# MCR-TASK-11 it passes; since MCR-TASK-12 it also drives the widgets, writes
# two cards and checks their round-trip -- but only when WE2002_MCR_CARD names
# a card. Without it the target still passes on the window alone, and says so.
```

### Arquivo: `docs/tasks/port-mcr/14-verificacao-final.md`

O item continua valendo — a §3.5 realmente junta dois arquivos que não estão
juntos —, mas a evidência precisa dizer o que se mede hoje: o arquivo é inglês
**salvo o bloco do `mcr_ui`, que a MCR-TASK-12 reescreveu em português e a
CORR-MCR-019 repôs**, e o `sed` de vinte linhas não alcança o bloco. Trocar por
`grep -nE '^\s*#' tests/CMakeLists.txt | head -30` e a linha do `Makefile`.

Se a correção for executada antes da MCR-TASK-14, basta registrar que o
episódio aconteceu — é ele que mostra por que a frase da §3.5 precisa ser
consertada em vez de tolerada.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tests/CMakeLists.txt` | modificar |
| `docs/tasks/port-mcr/14-verificacao-final.md` | modificar |

## Verificação

- [x] o bloco do `mcr_ui` está em inglês e mantém a ressalva do
      `WE2002_MCR_CARD`, inclusive a frase que diz que sem ela o alvo passa
      com a janela sozinha **e avisa**
- [x] `grep -nE '^\s*#' tests/CMakeLists.txt` não mostra português em nenhuma
      das linhas de comentário: as 74 continuam 74, e a contagem da Evidência
      caiu de **6 para 0**
- [x] o item da MCR-TASK-14 descreve o que se mede hoje, com
      `grep -nE '^\s*#' tests/CMakeLists.txt` — o arquivo inteiro — no lugar
      do `sed` de vinte linhas, e registra o episódio como o argumento a favor
      de consertar a §3.5 em vez de tolerá-la
- [x] `cmake --preset debug` reconfigura sem aviso novo
- [x] `ctest -R mcr` = **3 de 3** com `WE2002_MCR_CARD`; `make test` **10 de 10**
- [x] `python3 tools/check_tasks.py` (100 ok) e `ctest -R tasks` (1 de 1) verdes
- [x] `roms/` intocada — esta correção não abre cartão nenhum

## Log de Execução

**Executado em:** 2026-09-08

**Resumo do que foi feito:**

Reproduzido antes de mexer: 74 linhas de comentário no arquivo, **6** delas
portuguesas, todas introduzidas por `2c7ec25` e todas no bloco que a
MCR-TASK-10 escreveu em inglês depois de medir o idioma do arquivo. Reposto o
bloco em inglês **com o conteúdo novo intacto** — a ressalva do
`WE2002_MCR_CARD` é o que a MCR-TASK-12 acrescentou de útil ali, e ela
sobreviveu à volta. A contagem caiu de 6 para 0; as 74 continuam 74.

O item da MCR-TASK-14 foi reancorado num comando que alcança o **arquivo
inteiro**. O `sed -n '1,20p'` que ele mandava rodar não alcançava nenhuma das
seis linhas novas — quem executasse a task mediria um arquivo diferente do que
o item descreve e decidiria a favor da §3.5 por uma evidência produzida sem
querer. O episódio ficou registrado no próprio item, porque é ele que mostra
por que a frase da §3.5 precisa ser consertada e não tolerada: enquanto os dois
idiomas forem permitidos neste arquivo, a consistência **dele** é o único
critério que sobra, e nenhuma varredura do ciclo o vigia — a `glossary.sweep()`
cobre `tools/mcr/**.py` e para ali, por desenho.

**Problemas encontrados:**

Nenhum. A correção é de idioma e de âncora; nada de comportamento mudou, e os
quatro gates confirmam: `ctest -R mcr` 3 de 3 com a fixture apontada,
`make test` 10 de 10, `ctest -R tasks` 1 de 1, `check_tasks` 100 ok.

**Arquivos criados/modificados:**

- `tests/CMakeLists.txt` — o bloco do `mcr_ui` de volta ao inglês
- `docs/tasks/port-mcr/14-verificacao-final.md` — o item reancorado
- `docs/tasks/port-mcr/correcoes-progresso.md`
