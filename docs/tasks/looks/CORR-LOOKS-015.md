---
id: CORR-LOOKS-015
title: "Correção: o gate obrigatório não é alcançável por `ctest` nesta máquina, e pedir por ele continua saindo 0"
type: correção
category: verificação
status: done
depends_on: []
origin: LOOKS-TASK-06
severity: high
done_on: 2026-09-14
done_commit: db48d90
---

# CORR-LOOKS-015: o gate obrigatório não é alcançável por `ctest` nesta máquina

## Problema identificado

A task registrou o `looks_selftest` no `tests/CMakeLists.txt` — e o registro é
**textual**. Em nenhum diretório de build deste worktree o alvo existe, e o
comando que o pediria responde a frase que lê como verde:

```
$ ctest --test-dir build -R looks              ;  rc=0
$ ctest --test-dir build-mingw -R looks        ;  rc=0
$ ctest --test-dir build-windows-release -R looks ; rc=0
Test project ...
No tests were found!!!
```

Três builds, três "No tests were found!!!", três **exit 0**. É exatamente o
sintoma que a [`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md) abriu e
fechou como resolvido há poucas horas — e cujo Log transcreve corridas de
`ctest -R looks` com `10 - looks_image (Skipped)` e `1/1 Test #10 ... Passed`.
Nenhum build desta árvore produz isso hoje; nenhum `CTestTestfile.cmake` deste
worktree menciona `looks`.

**E o remédio que o Log desta task propõe não funciona nesta máquina.** Ele
diz: *"O `build/` do worktree foi gerado no Linux … quem reconfigurar o build
no Linux fecha o `ctest -R looks`."* O `build/` é mesmo de outra máquina
(`CMAKE_HOME_DIRECTORY:INTERNAL=/home/ingmar/...`), mas reconfigurar **aqui**
não fecha nada:

```
$ cmake -S . -B <scratchpad>/bld -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Debug
  Could NOT find CURL ...
  src/core/CMakeLists.txt:1 (find_package)
-- Configuring incomplete, errors occurred!          (rc=1)
```

O `tools/looks/` **não precisa de compilador, de libcurl, de Qt nem de venv** —
o próprio cabeçalho do alvo diz "It needs NOTHING". Mas o único jeito
declarado de rodá-lo passa por configurar um projeto C++ que não configura
nesta máquina, por uma dependência que nada tem a ver com ele.

O resultado é o pior dos três mundos:

1. o perfil do ciclo promete `looks_selftest` — *"nada — **nunca pula**"* — a
   partir desta task;
2. o comando que o materializa responde silêncio e **sucesso**;
3. e a ferramenta por baixo **funciona**: `python tools/looks/selftest.py` sai
   0 e mede tudo, como esta revisão confirmou.

O contrato que o próprio perfil escreve — *"mediu e passou, ou pulou com 77"* —
não está sendo cumprido pelo caminho que ele indica. E esta é a **segunda**
vez que o ciclo tropeça nisto pelo mesmo mecanismo; da primeira, a correção
registrou o alvo e deu a questão por encerrada sem que o `ctest` desta máquina
jamais o tivesse listado.

## Evidência

```
$ for d in build build-mingw build-windows-release; do
    ctest --test-dir $d -R looks 2>&1 | tail -1; done
No tests were found!!!
No tests were found!!!
No tests were found!!!

$ grep -rl "looks" --include=CTestTestfile.cmake .
(vazio)

$ grep -m2 -E "CMAKE_COMMAND|CMAKE_HOME_DIRECTORY" build/CMakeCache.txt
CMAKE_COMMAND:INTERNAL=/usr/bin/cmake
CMAKE_HOME_DIRECTORY:INTERNAL=/home/ingmar/desenvolvimento/github/new-we2002-editor
```

O registro existe no fonte (`tests/CMakeLists.txt:205` e `:210`), e a
ferramenta mede de verdade quando chamada direto:

```
$ python tools/looks/selftest.py
modules: 0 failure(s)
rules:   0 failure(s)       ..... rule 1 swept 7 file(s), 2206 line(s)
controls: 0 failure(s)      ..... 8 of 8 controls red
looks_selftest: 0 failure(s)                                      (rc=0)
```

E vermelha quando tem por que ficar — plantado `PLANTED = 0x8016E800` numa
**cópia** da árvore, no scratchpad, nada commitado:

```
FAIL  Rule 1: no address outside layout.py  [('section.py', 483, 'PLANTED = 0x8016E800')]
looks_selftest: 1 failure(s)                                      (rc=1)
```

O defeito não é a ferramenta nem o conteúdo do alvo. É que **o caminho
declarado até ele não existe nesta máquina, e falha em silêncio verde.**

## Causa raiz

O gate de um projeto que não depende de nada foi pendurado num `ctest` que só
existe depois de configurar um projeto C++ que não configura aqui, e a ausência
do alvo é indistinguível de sucesso.

## Correção

Escolher **um** caminho e escrevê-lo onde o rito olha. Em ordem de preferência:

### 1. O comando direto entra no perfil, ao lado do alvo

A tabela de gates de [`docs/prompts/perfil-looks.md`](/docs/prompts/perfil-looks.md)
ganha a coluna do que se roda de fato, e diz que nesta máquina (Windows, sem
libcurl) o `ctest` **não** alcança os alvos:

| alvo | como se roda aqui | como se roda onde o build configura |
| --- | --- | --- |
| `looks_selftest` | `python tools/looks/selftest.py` | `ctest -R looks_selftest` |
| `looks_image` | `python tools/looks/modelfile.py --check-image` | `ctest -R looks_image` |

Sem isso, toda task do ciclo vai continuar fechando com "o gate está verde"
apoiada num comando que ninguém pôde rodar.

### 2. A armadilha do `ctest -R` vazio fica registrada como armadilha

`ctest -R <padrão>` que não casa nada **sai 0**. Isso vale para os cinco
projetos do repositório e já enganou duas vezes aqui. Entra na lista de
armadilhas medidas do perfil, com a linha: conferir sempre `N tests passed` e
não só o código de saída.

### 3. Se a preferência for consertar o `ctest`

Então o caminho é tornar os alvos de `tools/looks/` alcançáveis sem o
`src/core` — eles não compartilham nada com ele. Isso é decisão de arquitetura
de build e **é conversa com o dono do repositório**, não escolha de execução:
hoje o `find_package(CURL)` do `src/core/CMakeLists.txt:1` derruba a
configuração inteira, e nenhum dos cinco projetos Python de `tests/` roda sem
ela.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/prompts/perfil-looks.md` | modificar |
| `docs/tasks/looks/19-alvos-de-ctest-e-cli.md` | modificar |

## Verificação

- [x] o perfil diz, para cada alvo, o comando que **roda nesta máquina**
- [x] a armadilha do `ctest -R` vazio saindo 0 está na lista do perfil
- [x] a LOOKS-TASK-19 fecha a conta com o comando que existe, e não com um
      `ctest -R looks` que responde "No tests were found"
- [x] `python tools/looks/selftest.py` continua saindo 0 e imprimindo as três
      linhas de contagem
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-14

**Resumo do que foi feito:**

O diagnóstico da CORR reproduz inteiro, e **uma das premissas dela não**: o
`ctest` *é* alcançável nesta máquina. Ver "Problemas encontrados". As três
partes pedidas foram feitas, e a terceira ficou melhor do que a CORR previa.

**1. A tabela de gates do perfil ganhou duas colunas** — *como se roda AQUI* e
*por `ctest`, onde o build configura*:

| alvo | como se roda aqui |
|---|---|
| `looks_selftest` | `python tools/looks/selftest.py` |
| `looks_image` | `python tools/looks/modelfile.py --check-image` |

A coluna do meio não depende de build nenhum, e é o caminho curto enquanto a
questão de arquitetura estiver aberta.

**2. A armadilha entrou na lista do perfil, como item 12:** `ctest -R <padrão>`
que não casa nada imprime `No tests were found!!!` e **sai 0**. Vale para os
cinco projetos, e enganou **duas vezes** neste ciclo — a
[`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md) sobre alvo inexistente,
esta sobre alvo que existe no fonte e em build nenhum. A regra escrita: conferir
`N tests passed`, e que o **nome** do alvo apareceu na listagem.

**3. A LOOKS-TASK-19** passou a fechar a conta com um número que sai de corrida
que listou os alvos, e ganhou o ponteiro para a receita. De quebra, dois itens
do critério dela estavam desatualizados: o `looks_selftest` já está registrado
(pela LOOKS-TASK-06), e a conta "até esta task" era **0 passed, 1 skipped** e é
**1 passed, 1 skipped**.

Evidência reproduzida antes de editar:

```
$ for d in build build-mingw build-windows-release; do
    ctest --test-dir $d -R looks 2>&1 | tail -1; done
No tests were found!!!      rc=0
No tests were found!!!      rc=0
No tests were found!!!      rc=0

$ grep -rl "looks" --include=CTestTestfile.cmake .
(vazio)

$ python tools/looks/selftest.py
  ..... rule 1 swept 7 file(s), 2206 line(s)
  ..... 8 of 8 controls red
looks_selftest: 0 failure(s)                                        (rc=0)
```

**Problemas encontrados:**

**O `ctest` é alcançável nesta máquina, e a CORR conclui que não é.** A
evidência dela mostra um `cmake -G "MinGW Makefiles"` sem toolchain falhando em
`Could NOT find CURL`, e disso tira que *"reconfigurar aqui não fecha nada"*.
Fecha, com o toolchain do vcpkg — que é exatamente o que a
[`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md) usou algumas horas
antes e **não escreveu em lugar nenhum**, que é o defeito de fundo. Medido
agora, com o `tests/CMakeLists.txt` de hoje:

```
$ cmake -S . -B <fora da arvore> -G Ninja     -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake
-- Configuring done (3.7s)

$ ctest --test-dir <fora da arvore> -R looks
1/2 Test #10: looks_selftest ...................   Passed    1.13 sec
2/2 Test #11: looks_image ......................***Skipped   0.06 sec
100% tests passed out of 2
```

Com `WE2002_LOOKS_IMAGE` apontada, os dois passam. A receita está agora na
tabela de gates do perfil, junto com o aviso de **usar build fora da árvore** —
reconfigurar o `build/` do worktree destruiria o cache da outra máquina.

Isso **não invalida** a CORR: o caminho declarado continua respondendo verde
sem medir nada, que é o achado. O que muda é o remédio — a opção 3 dela
("conversa com o dono do repositório") deixa de ser a única saída e vira o
conserto de fundo, registrado como **aberto** no perfil: `tools/looks/` não
precisa de compilador, libcurl, Qt nem venv, e ainda assim depende de um
toolchain de C++ para ser **listado**. Isso alcança os cinco projetos, não só
este.

**Segundo achado, de graça:** a §4.4 do plano dizia *"Hoje são 0 passed, 1
skipped: só o `looks_image` está registrado"*, escrito antes de a LOOKS-TASK-06
registrar o `looks_selftest`. Corrigido no mesmo commit, com a armadilha do
`ctest -R` vazio ao lado.

**Arquivos criados/modificados:**

- `docs/prompts/perfil-looks.md` — a tabela de gates (duas colunas novas, a
  receita medida) e a armadilha 12
- `docs/tasks/looks/19-alvos-de-ctest-e-cli.md` — o critério
- `docs/PLAN-LOOKS-PY.md` — §4.4
- `docs/tasks/looks/CORR-LOOKS-015.md` — este Log
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
