---
description: Executa todas as correcoes pendentes (CORR-WTE-XXX) em lote, seguindo docs/prompts/04-corrigir-tudo.md
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Skill, Agent, TodoWrite
---

Leia **agora** `docs/prompts/04-corrigir-tudo.md` e execute o que estiver
escrito nele.

**Releia o arquivo em toda invocação.** Ele é a fonte de verdade deste
comando e muda com o projeto — não trabalhe de memória nem do que ficou no
contexto de uma execução anterior.

`$ARGUMENTS` vazio significa "todas as `[ ]` de `correcoes-progresso.md`".
Com IDs (`CORR-WTE-013 CORR-WTE-016`), o lote é esse conjunto, ainda em ordem
de dependência. Com `--plano`, entregue só o plano da fase 0 e pare.

## O que este comando garante

1. **Lote inteiro, um commit por correção.** É a única regra do `/corrigir`
   que este comando relaxa. Todas as outras valem palavra por palavra — em
   dúvida, `docs/prompts/03-corrigir.md` é a fonte.

2. **Plano antes de editar.** Fase 0 sempre: ordem de dependência, matriz de
   conflito, ondas, e **por que** cada par ficou sequencial.

3. **Evidência do lote inteiro primeiro, em paralelo.** Reprodução é leitura
   pura. CORR cujo sintoma sumiu sai do lote e é reportada — corrigir o que já
   não está quebrado é como se introduz regressão. Ela não bloqueia as outras.
   **Exceção:** reprodução que precisa abrir o oráculo no `:98` **não** é
   paralelizável; ocupa o display e vai em série.

4. **O `:98` é o recurso mais serializado deste projeto.** Não há window
   manager, e os dois lados do golden acham a janela por heurística: duas
   sessões de GUI simultâneas dirigem a janela uma da outra, e o diff parece
   bug do port. Na prática, **toda CORR que abre o oráculo, roda o golden ou
   tira captura é sequencial**. Serializam junto: `work/` e as cópias de ~474 MB,
   o prefix do Wine, gerador em modo de escrita, `lazbuild`, o projeto do
   Ghidra, `git`, e o próprio `correcoes-progresso.md`.

5. **Doc quente presume conflito.** `CLAUDE.md`, `docs/PLAN-WTE-LAZARUS.md`,
   `docs/tasks/progresso.md`, `wte/re/*`, `.claude/commands/*` — a varredura de
   discrepância puxa doc que a lista da CORR não previa. Estes wrappers entram
   na lista porque reafirmam o mesmo rito dos prompts com outras palavras.
   **Na dúvida, sequencial.**

6. **Subagente edita; o thread principal commita.** Subagente não roda `git`,
   nem `lazbuild`, nem `golden_check.sh`, nem gerador em modo de escrita, e não
   abre janela no `:98`. Correção que precisa de um desses é sequencial por
   definição.

7. **Varredura de discrepância a cada CORR, não uma no fim.** Num lote a
   correção *k+1* torna falso o doc que a *k* acabou de escrever.

8. **`[x]` só depois do commit**, e escopo de arquivo por correção: ao
   corrigir a 013 você não abre a 016. A data da coluna "Concluída em" é **por
   CORR** — num lote que atravessa a meia-noite elas divergem, e a do lote não
   serve. O `status:` do frontmatter da CORR acompanha o `[x]`, também por CORR.

9. **Falha isolada não aborta o lote** — siga para quem não depende dela. Gate
   global quebrado **para o lote**: `lazbuild` não compila, `ctest` do
   `newWe2002` vermelho, ou — o caso mais provável aqui — o **controle do
   golden** não fechando, que indica problema do harness ou do `:98` e torna
   sem sentido qualquer resultado seguinte.

10. **Nunca execute `WTE-TASK-XX` por aqui** — isso é do `/executar`. E nunca
    cole decompilado, edite à mão o que um gerador produz, ou escreva no
    `we-team-editor.exe` / em `roms/`.

Ao terminar, entregue o formato de saída que o prompt pede — plano, veredito da
evidência por CORR, SHA de cada commit, o número medido de cada gate, as
correções que ficaram de fora com o motivo, e a confirmação de que `work/` não
ficou com cópia de imagem esquecida.
