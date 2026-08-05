---
description: Executa a proxima correcao pendente (CORR-WTE-XXX), seguindo docs/prompts/03-corrigir.md
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Skill, TodoWrite
---

Leia **agora** `docs/prompts/03-corrigir.md` e execute o que estiver escrito
nele.

**Releia o arquivo em toda invocação.** Ele é a fonte de verdade deste
comando e muda com o projeto — não trabalhe de memória nem do que ficou no
contexto de uma execução anterior.

Se `$ARGUMENTS` estiver preenchido, trate como a correção a executar (ex.:
`CORR-WTE-003`) e confira as dependências antes. Argumento vazio significa "a
primeira `[ ]` em `correcoes-progresso.md`".

## O que este comando garante

1. **Uma correção por invocação.** Concluída e commitada, **pare** — não
   avance para a próxima `[ ]` mesmo que seja no mesmo arquivo.

2. **Escopo de arquivo.** Abra **só** o `CORR-WTE-XXX.md` selecionado. Não
   leia os outros, mesmo apontando para o mesmo gerador ou o mesmo formulário.
   E nunca execute `WTE-TASK-XX` por aqui — isso é do `/executar`.

3. **Reproduzir a evidência antes de corrigir.** Rode o comando da seção
   "Evidência" e confira que o sintoma ainda existe. Se não bater, **pare e
   reporte**: a CORR pode ter envelhecido, e corrigir o que já não está
   quebrado é como se introduz regressão em código que estava certo.

4. **Correção no gerador, não no gerado.** Se o alvo sair de `dfm_extract.py`,
   `dfm2lfm.py`, `gen_tables_pas.py`, `port_database_pas.py` ou
   `spec_index.py`, o fix entra no gerador e a árvore é regenerada. Editar
   `wte/forms/*.lfm` ou `wte/src/we2002_*.pas` à mão não é correção — é a
   discrepância que a revisão deveria ter pegado.

5. **Nada de decompilado colado, nada de escrita no que é leitura pura.** Spec
   e Pascal se escrevem a partir de `wte/re/spec/`, com trecho parafraseado e
   nunca copiado. O `we-team-editor.exe` e `roms/` são leitura pura — trabalhe
   sobre cópia em `work/`.

6. **`[x]` só depois do commit.** Ele descreve estado já commitado, não
   intenção. Correção parcial não vira `[x]` — registre a pendência no Log de
   Execução. Junto do `[x]` vai a data do commit na coluna "Concluída em" da
   tabela de resumo, igual à do `Executado em` do Log, e o `status:` do
   frontmatter do `CORR-WTE-XXX.md` vira `concluído` — o `/revisar` abre toda
   correção com `pendente`, e o campo duplica a coluna Status.

7. **Discrepância achada no caminho se conserta, não se registra.** A lista de
   arquivos da CORR é o mínimo. Doc que o seu conserto tornou falso ou
   incompleto entra nesta mesma invocação, em commit próprio — `grep -rn` pelo
   termo que você mudou, em `docs`, `wte/re`, `.claude` e `CLAUDE.md`, antes de
   fechar. O `.claude/` está aí porque estes wrappers repetem o mesmo rito com
   outras palavras, e já ficaram para trás de uma mudança de processo uma vez.
   Registrar no Log e seguir não vale: quem lê o doc errado amanhã não lê o seu
   Log. O limite continua sendo `WTE-TASK` e implementação de handler, que não
   são deste comando.

8. **Se tocar `src/core/`, o projeto irmão tem de continuar verde.** O
   `newWe2002` está com escopo fechado e verificado: `ctest --preset debug` e o
   golden dele rodam depois, e o resultado vai na saída.

Ao terminar, entregue o formato de saída que o prompt pede — incluindo o SHA
do commit, `git status --short` limpo, e o número medido de cada gate
aplicável.
