---
description: Executa a proxima tarefa pendente do backlog, seguindo docs/prompts/01-executar.md
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Skill, TodoWrite
---

Leia **agora** `docs/prompts/01-executar.md` e execute o que estiver escrito
nele.

**Releia o arquivo em toda invocação.** Ele é a fonte de verdade deste
comando e muda com o projeto — não trabalhe de memória nem do que ficou no
contexto de uma execução anterior.

Se `$ARGUMENTS` estiver preenchido, trate como pedido de tarefa específica
(ex.: `WTE-TASK-32`) e confira contra as regras de seleção do prompt antes de
executar — a antecipação da WTE-TASK-32 (preço) exige pedido
explícito do usuário. Argumento vazio significa "a próxima pendente na ordem".

## O que este comando garante

1. **Uma tarefa por invocação.** O prompt tem uma exclusão obrigatória nesse
   sentido: concluída e commitada a tarefa selecionada, **pare**. Não avance
   para a próxima pendente mesmo que a primeira tenha sido rápida. Quando várias
   ficam prontas ao mesmo tempo — as 03 a 07 só dependem da 02 —, executa-se a
   de menor ID.

2. **Ao final, `docs/tasks/progresso.md` fica atualizado** com o progresso da
   tarefa:
   - tabela de resumo E checklist da fase trocados de `⬜ Pendente` para
     `✅ Concluído`
   - coluna **"Concluída em"** da tabela de resumo com a data do commit
     (`AAAA-MM-DD`), e a célula do ID como link para o markdown da tarefa
     (`[WTE-TASK-XX](/docs/tasks/XX-nome.md)` — sempre `/docs/` + caminho do
     arquivo, ver `.claude/rules/links.md`)
   - coluna **"Revisado em"** de `—` para `⬜ pendente`, que é o marcador pelo
     qual o `/revisar` escolhe a próxima. A data ali é do `/revisar`, nunca
     deste comando
   - `status: pendente` → `status: concluído` no **frontmatter do markdown da
     tarefa**. Ele duplica a coluna Status da tabela; as 40 tasks nascem
     `pendente` e o campo é fácil de esquecer, porque nenhum consumidor o lê
     ainda — foi assim que a WTE-TASK-01 fechou afirmando o contrário do índice
   - o **Log de Execução** preenchido no markdown da tarefa em `docs/tasks/`:
     data, resumo do que se aprendeu, arquivos tocados, problemas encontrados.
     A lista de arquivos se confere contra `git show --stat --format= HEAD`,
     não contra a memória — ela já ficou devendo um item quatro vezes, sempre o
     que entrou no meio da execução por motivo lateral

   Tarefa parcial **não** vira `✅ Concluído` — registre no Log o que ficou
   pendente e diga isso na saída.

   E **pendência encaminhada para outra task precisa da linha escrita na task
   de destino**, não só no seu Log: quem executar a NN lê o arquivo dela. Já
   falhou duas vezes ([CORR-WTE-086](../../docs/tasks/CORR-WTE-086.md),
   [CORR-WTE-105](../../docs/tasks/CORR-WTE-105.md)).

3. **`✅ Concluído` só depois do commit.** Ele descreve estado já commitado,
   não intenção. O passo 5 do prompt (commit, `git status --short` limpo)
   fecha antes de a marcação ser escrita.

4. **O gate da fase, medido.** `--check` dos geradores nas fases 1 a 3;
   `lazbuild` a partir da 2; `golden_check.sh` **com o controle fechando
   antes** a partir da 4. Controle é original contra original dando zero
   divergência — sem ele, verde e vermelho não significam nada.

5. **Nada de escrita no que é leitura pura.** O `we-team-editor.exe` não se
   edita; `roms/` nunca é alvo de ferramenta — cópia em `work/`, sempre.
   Arquivo que um gerador produz não se edita à mão: mexe-se no gerador.

6. **Todo número novo em doc veio de ferramenta.** Contagem à mão em mensagem
   de commit já se propagou para doc neste repositório; se a task produzir
   número, ele sai de script versionado.

Ao terminar, entregue o formato de saída que o prompt pede — incluindo o SHA
do commit e o resultado medido de cada gate da fase.
