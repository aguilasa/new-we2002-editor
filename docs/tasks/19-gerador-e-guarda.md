---
id: PES2-TASK-19
title: "O gerador — do mapa ao código, com `--check`"
type: ferramenta
category: build
phase: 5
depends_on: ["PES2-TASK-18"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §4.4"
status: pendente
---

# PES2-TASK-19: O gerador e a guarda

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §4.4 e §5, Fase 5, segundo item.
- **É a mesma disciplina do `newWe2002`**, e ela já pagou por si: os
  geradores de lá (`extract_legacy_data.py`, `port_database.py`, `rc2ui.py`)
  têm `--check` no `ctest`, e **editar o gerado falha em teste**.

---

## Objetivo

Um gerador que produz, a partir do `pes2_map.json`, o código de leitura e
gravação — e uma guarda que impede o gerado de divergir do gerador.

### As três lições do `newWe2002` que este gerador herda

1. **Falhar em vez de emitir código quebrado.** O `port_database.py` tem uma
   lista `FORBIDDEN` e recusa se sobrar construção que ele não reconhece.
   Pegou dois erros na Fase 2 daquele projeto.
2. **Contar invariantes, não só compilar.** O `check_seeks()` conta seeks
   absolutos e relativos no legado e na saída e recusa se não baterem —
   porque uma regex com `[^,]` atravessou uma quebra de linha e **trocou** um
   `Seek(begin)` por um `SeekCurrent`. Compilava, passava nos testes,
   passava no ASan; só o oráculo mostrou. **Aqui não há oráculo**, o que
   torna a contagem de invariantes mais importante, não menos.
3. **`--check` no `ctest`.** Sem ele o gerado envelhece em silêncio.

O invariante desta família é o **conjunto de cópias**: para cada entidade, o
número de gravações que o código gerado emite tem de ser igual ao número de
cópias que o mapa declara. É o `check_seeks()` deste projeto.

### O que gerar

Decidir na task, e registrar a razão. O mínimo: uma tabela de constantes
(âncora, delta, contagem, esquema) e as rotinas de leitura e gravação por
entidade. A linguagem sai da PES2-TASK-22, se ela já tiver corrido; senão,
gerar Python e deixar o alvo definitivo para depois é resultado legítimo.

---

## Critério de conclusão

- [ ] Gerador em `tools/pes2/`, com `--check`.
- [ ] `--check` registrado no `ctest` e falhando quando o gerado é editado à
      mão (exercitado, não só escrito).
- [ ] Guarda de invariante de cópias, exercitada com um caso negativo.
- [ ] O gerador **recusa** o que não reconhece, em vez de emitir código
      incompleto — exercitado.

---

## Log de Execução

*(a preencher)*
