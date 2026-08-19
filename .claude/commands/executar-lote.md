---
description: Executa N tarefas pendentes do backlog em lote (padrao 2), seguindo docs/prompts/05-executar-lote.md
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Skill, Agent, TodoWrite
---

Leia **agora** `docs/prompts/05-executar-lote.md` e execute o que estiver
escrito nele.

**Releia o arquivo em toda invocação.** Ele é a fonte de verdade deste
comando e muda com o projeto — não trabalhe de memória nem do que ficou no
contexto de uma execução anterior.

`$ARGUMENTS` vazio significa **2 tarefas**. Só dígitos (`3`) é o tamanho do
lote. Com IDs (`WTE-TASK-03 WTE-TASK-05`), o lote é esse conjunto, ainda em
ordem de dependência. Com `--plano`, entregue só o plano da fase 0 e pare.
Número **e** IDs juntos é erro — pergunte qual dos dois vale.

## O que este comando garante

1. **N tarefas por invocação, um commit por tarefa.** É a única regra do
   `/executar` que este comando relaxa. Todas as outras valem palavra por
   palavra — em dúvida, `docs/prompts/01-executar.md` é a fonte. Ordem de fase,
   `depends_on`, e a antecipação da WTE-TASK-32 (preço, só com
   pedido explícito do usuário) continuam de pé.

2. **Não existe "executar tudo".** O padrão é 2 e o usuário pode pedir outro
   número. Lote que atravessa uma fase inteira entrega um `progresso.md` que
   ninguém audita depois.

3. **Plano antes de editar.** Fase 0 sempre: inventário das pendentes na tabela
   **e** no checklist, ordem de dependência, matriz de conflito, ondas, e **por
   que** cada par ficou sequencial. Menos tarefas prontas que `N` significa
   executar menos e dizer isso — nunca trocar a ordem para caber mais.

4. **"Em lote" não é "em paralelo".** Lote é quantas a invocação fecha;
   paralelo é quantas rodam ao mesmo tempo, que às vezes é uma. Um lote de 2
   que serializa no `:99` roda em sequência e está correto — a economia ali é
   de rito, não de tempo de máquina. O paralelismo paga na **fase 1** (03 a
   07): extração estática, leitura pura sobre o `.exe`, cada uma escrevendo seu
   arquivo em `wte/re/`.

5. **O `:99` é o recurso mais serializado deste projeto.** Não há window
   manager, e os dois lados do golden acham a janela por heurística: duas
   sessões de GUI simultâneas dirigem a janela uma da outra. **Toda tarefa que
   abre o oráculo, roda o golden ou tira captura é sequencial.** Serializam
   junto: `work/` e as cópias de ~474 MB, o prefix do Wine, gerador em modo de
   escrita, `lazbuild`, o projeto do Ghidra, `git`, o `progresso.md` e o
   `wte/Makefile` — onde mora a bateria de `--check`, e onde as tarefas 03 a 06
   **todas** querem acrescentar um alvo.

6. **Grafo e matriz divergem, e a matriz manda.** O `progresso.md` diz que 12 e
   13 vão em paralelo, e diz certo: nenhuma depende da outra. Mas as duas
   dirigem janela no `:99`, então vão em série. O grafo fala de dependência
   lógica; a matriz, de recurso físico.

7. **Tarefa de fechamento (09, 14, 21, 29, 34, 40) não divide lote com
   dependência sua.** O filtro de `depends_on` já segura, mas o erro é
   tentador: fechar a fase junto com a última tarefa dela mede um estado que
   ainda ia mudar.

8. **Subagente edita; o thread principal commita.** Subagente não roda `git`,
   nem `lazbuild`, nem `golden_check.sh`, nem gerador em modo de escrita, não
   abre janela no `:99`, e não escreve no `progresso.md` nem no `wte/Makefile`.

9. **Varredura de discrepância a cada tarefa, não uma no fim.** Num lote a
   tarefa *k+1* torna falso o doc que a *k* acabou de escrever.

10. **`✅ Concluído` só depois do commit**, e escopo de arquivo por tarefa: ao
    executar a 03 você não abre a 05. A data de "Concluída em" é **por tarefa** —
    num lote que atravessa a meia-noite elas divergem, e a do lote não serve.
    "Revisado em" vai para `⬜ pendente`, nunca uma data. O `status:` do
    frontmatter da tarefa acompanha o `✅`, também por tarefa.

11. **Falha isolada não aborta o lote** — siga para quem não depende dela. Gate
    global quebrado **para o lote**: `lazbuild` não compila, `ctest` do
    `newWe2002` vermelho, ou — o caso mais provável aqui — o **controle do
    golden** não fechando, que indica problema do harness ou do `:99` e torna
    sem sentido qualquer resultado seguinte.

12. **Nunca execute `CORR-WTE-XXX` por aqui** — isso é do `/corrigir` e do
    `/corrigir-tudo`. E nunca cole decompilado, edite à mão o que um gerador
    produz, ou escreva no `we-team-editor.exe` / em `roms/`.

O lote deixa **mais de uma tarefa esperando revisão**, e isso é esperado: o
`/revisar` pega a de menor ID entre as `⬜ pendente`, uma por invocação. Não
revise nada por aqui.

Ao terminar, entregue o formato de saída que o prompt pede — plano, o que o
contexto de cada tarefa mostrou, SHA de cada commit, o resultado medido de cada
gate, as tarefas que ficaram de fora com o motivo, e a confirmação de que
`work/` não ficou com cópia de imagem esquecida.
