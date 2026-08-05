---
id: WTE-TASK-17
title: "tools/port_database_pas.py — transpilar o we2002_core"
type: ferramenta
category: dados
phase: 3
depends_on: ["WTE-TASK-15", "WTE-TASK-16"]
status: pendente
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
| `wte/re/transpilador.md` | criar — a tabela de substituição e o que ela recusa |

---

## Critério de conclusão

- [ ] `FORBIDDEN` presente, com a lista adaptada ao C++ → Pascal
- [ ] `check_seeks()` presente e batendo nas duas direções
- [ ] O limite da §8.10 escrito no cabeçalho do script
- [ ] Saída byte-estável; `--check` implementado
- [ ] Recusa testada com entrada plantada, não só com a entrada boa
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
