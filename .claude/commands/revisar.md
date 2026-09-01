---
description: Revisa a ultima tarefa concluida e cria CORRs, seguindo docs/prompts/02-revisar.md
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Skill, TodoWrite
---

Leia **agora** `docs/prompts/02-revisar.md` e execute o que estiver escrito
nele.

**Releia o arquivo em toda invocação.** Ele é a fonte de verdade deste
comando e muda com o projeto — não trabalhe de memória nem do que ficou no
contexto de uma execução anterior.

Se `$ARGUMENTS` estiver preenchido, trate como a tarefa a revisar (ex.:
`WTE-TASK-04`). Argumento vazio significa "a última `✅ Concluído` do
`progresso.md` com a coluna **"Revisado em"** ainda em `⬜ pendente`".

## O que este comando garante

1. **Revisão, nunca implementação.** Não execute task nem CORR aqui, não
   marque nada como concluído no `progresso.md` — a única célula que este
   comando escreve lá é a **"Revisado em"** da tarefa revisada. **Não rode
   gerador em modo de escrita**: `--check` é obrigatório, gerador sem `--check`
   reescreve a árvore e é implementação. E nada de escrever no
   `we-team-editor.exe` nem em `roms/`.

2. **Uma revisão por invocação.** Só a última tarefa concluída. Criadas as
   CORRs e feito o commit, **pare**.

3. **Medir, não ler.** Metade dos artefatos é **gerada** e a outra metade é
   verificada contra um binário de 2002 rodando sob Wine — ler o código não
   basta nos dois casos. No gerado, o que prova é o `--check` (e rodar duas
   vezes dando bytes iguais); no comportamento, o que prova é o
   `golden_check.sh` com o controle fechando antes. Compare com o que o Log de
   Execução afirma; o Log é pista, não verdade.

4. **Recontar o que a task afirma.** Os números do plano vieram de script
   descartável em 2026-08-05 — 18 formulários, ~430 componentes, 96 handlers,
   19 de 69 offsets, 70 strings com padding, 197 bitmaps. Se a task afirma
   algum, remede com a ferramenta versionada.

5. **Saída em `docs/tasks/`:** um `CORR-<PREFIXO>-XXX.md` por discrepância, no
   formato do prompt, mais `correcoes-progresso.md` atualizado sem alterar as
   entradas anteriores. Linha nova na tabela nasce com o ID **linkado**
   (`[CORR-<PREFIXO>-XXX](/docs/tasks/CORR-<PREFIXO>-XXX.md)`, sempre `/docs/` + caminho do
   arquivo — ver `.claude/rules/links.md`), a coluna **"ID Task
   Origem"** com a tarefa revisada, também linkada, e a "Concluída em" em `—` —
   quem preenche a data é quem executa a correção. Sem discrepância, diga isso
   **explicitamente e diga quais gates você mediu** para poder afirmar.

6. **A coluna "Revisado em" é preenchida sempre**, com a data do commit desta
   revisão — inclusive quando nada foi achado. Nesse caso o commit tem só o
   `progresso.md`, e sem ele a revisão não deixa rastro: a próxima invocação
   reviveria a mesma tarefa.

7. **Resultado negativo não é discrepância.** Task que conclui "`Printers` é
   dependência transitiva" ou "os 105 uniformes são índice direto, sem tabela"
   entregou o que devia. Registre no relatório e siga.

Ao terminar, entregue os 9 itens do formato de saída que o prompt pede.
