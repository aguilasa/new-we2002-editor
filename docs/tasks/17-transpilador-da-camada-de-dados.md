---
id: WTE-TASK-17
title: "tools/port_database_pas.py — transpilar o we2002_core"
type: ferramenta
category: dados
phase: 3
depends_on: ["WTE-TASK-15", "WTE-TASK-16"]
status: concluído
---

# WTE-TASK-17: Transpilador da camada de dados

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §4.5 e Fase 3 item 1.
- **A camada de dados não sai do binário do Obocaman.** Sai do `we2002_core`
  deste repositório, que já é byte-idêntico ao `ed.exe` nas duas ROMs.

Entrada, ~2.150 linhas:

```
src/core/Database.cpp    1704
src/core/Player.cpp       130
src/core/CdImage.cpp       89
src/core/TextCodec.cpp     77
src/core/include/we2002/Types.hpp   147
```

Subconjunto estreitíssimo de C++: laço de contagem fixa, `Seek`, `Read`,
`Write`, array, aritmética inteira. Sem template, sem STL além de array, sem
RAII, sem herança. **Transpila por regra.**

Precedente direto: `tools/port_database.py` já faz transpilação de C++ MFC para
C++ portável, extraindo `carica_dabin` e `OnWriteCD` verbatim e aplicando
substituições listadas.

---

## Objetivo

`wte/tools/port_database_pas.py`, decalcado do `port_database.py`, com **os dois
guards intactos**.

### Guard 1 — `FORBIDDEN`

Recusa emitir se sobrar construção que a tabela de substituição não reconhece,
em vez de produzir código quebrado. No `port_database.py` original ele pegou
dois erros na Fase 2 do port Qt.

Aqui a lista de proibidos muda: em vez de construção MFC, é construção C++ que
não tem tradução Pascal decidida — ponteiro aritmético, `reinterpret_cast`,
qualquer coisa de `<algorithm>`.

### Guard 2 — `check_seeks()`

Conta seeks absolutos e relativos na entrada e na saída e recusa se não baterem.

**Ele existe por um bug real:** uma regex com `[^,]` atravessou uma quebra de
linha e trocou um `Seek(begin)` por um `SeekCurrent`. Compilava, passava nos
testes, passava no ASan — só o confronto com o `ed.exe` mostrou.

**Fica mais valioso aqui, não menos.** `TFileStream.Seek(offset, soBeginning)` e
`Seek(offset, soCurrent)` têm a mesma cara, e o mesmo erro é igualmente
silencioso.

Lembrete que o `port_database.py` carrega e vale aqui: ao escrever regra nova em
`SUBS`, **`[^x]` casa `\n`**.

### Limite duro

O transpilador digere **código deste repositório**. Não estender para engolir
saída de decompilador (§8.10) — ali a entrada vira arbitrária, o `FORBIDDEN`
deixa de segurar, e o gerador passa a emitir Pascal quebrado com cara de certo.

Escrever esse limite no cabeçalho do próprio script, não só aqui.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/port_database_pas.py` | criar |
| `wte/re/transpilador.md` | criar — **gerado** pelo próprio script |
| `wte/tools/test_port_database_pas.py` | criar — a recusa com entrada plantada |

---

## Critério de conclusão

- [x] `FORBIDDEN` presente, com a lista adaptada ao C++ → Pascal
- [x] `check_seeks()` presente e batendo nas duas direções
- [x] O limite da §8.10 escrito no cabeçalho do script
- [x] Saída byte-estável; `--check` implementado
- [x] Recusa testada com entrada plantada, não só com a entrada boa
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-09

- **Resumo do que foi feito:**

  `port_database_pas.py` com os dois guards, a tabela de substituição (41
  regras, aplicadas em ordem) e `wte/re/transpilador.md` **gerado pelo próprio
  script** — a tabela, o que ela recusa, a contagem de seeks por arquivo e o
  worklist da WTE-TASK-18, nenhum número digitado à mão. 35 testes.

  **O achado que re-dimensiona a WTE-TASK-18, e é o que vale levar adiante:**

  > O `tools/port_database.py` pôde ser substituição textual pura porque a
  > **fonte e o alvo dele são a mesma linguagem** — C++ MFC para C++ portável.
  > C++ → Pascal não pode. Bloco, cabeçalho de laço, assinatura de função e
  > declaração de variável não têm forma comum, e nenhuma regex os alcança sem
  > uma passagem estrutural com casamento de chave.

  O enunciado desta task dizia "decalcado do `port_database.py`" e "transpila
  por regra"; isso vale para **statement e expressão**, e é o que foi entregue
  e testado. Não vale para estrutura. Em vez de deixar a estrutura "sair como
  está", ela entrou no `FORBIDDEN` — quatro entradas, todas apontando para a
  WTE-TASK-18. A alternativa seria emitir arquivo com extensão `.pas`,
  cabeçalho de unidade e corpo em C++: um artefato que **parece** camada de
  dados, não compila, e convida alguém a "só ajustar à mão" exatamente o que a
  §4.4 proíbe. Isso chegou a acontecer nesta execução — o `we2002_textcodec.pas`
  foi emitido antes de a estrutura virar recusa, e foi apagado.

  Estado medido no fim: **493 recusas em 13 motivos**, das quais 447 são o
  passe estrutural e 46 são construção C++ sem tradução decidida (STL,
  `std::function`, `sizeof`, `static_assert`, fallthrough de `switch`,
  `std::string`/`filesystem`/`ofstream`). Nenhuma unidade emitida — o
  transpilador não produz camada de dados parcial.

  `check_seeks()` foi conferido contra o `we2002_core` real: a direção dos
  seeks se preserva nas cinco unidades. E o teste que reproduz o bug histórico
  — a regra que atravessa a quebra de linha e troca absoluto por relativo —
  passa: o guard pega.

- **Arquivos criados/modificados:**

  - `wte/tools/port_database_pas.py` — criado
  - `wte/tools/test_port_database_pas.py` — criado (35 testes)
  - `wte/re/transpilador.md` — criado, gerado
  - `docs/tasks/18-camada-de-dados-gerada.md` — o passe estrutural entrou no
    escopo e nos critérios dela

- **Problemas encontrados:**

  1. **O gap estrutural**, acima. É o item a levar para a 18.
  2. **Recusa falsa por comentário.** O `FORBIDDEN` acusava o comentário
     `// the new national sides are elsewhere` (`Database.cpp:440`) como uso de
     `new`. Recusa falsa é pior que ruído: manda a task seguinte investigar
     trabalho que não existe, e ensina a ignorar o guard. Entrou uma máscara
     que apaga comentário e literal preservando o número da linha, com teste.
  3. **Sessão concorrente.** Durante esta execução outra sessão abriu a
     CORR-WTE-027 e a CORR-WTE-028 sobre o `check_fase2.py` — que esta leva de
     tarefas alterou na WTE-TASK-16. A 027 é sobre link `/docs/...` emitido de
     dentro de `wte/re/`; o `transpilador.md` foi escrito já com a forma
     relativa, para não repetir o defeito.
