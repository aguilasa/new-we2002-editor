---
id: CORR-WTE-001
title: "Correção: frontmatter da task diz `pendente` numa tarefa concluída"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-001: o campo `status` do frontmatter não acompanha o `progresso.md`

## Problema identificado

`docs/tasks/01-ferramental.md` fechou no commit `2aec9cb`: os seis itens do
"Critério de conclusão" estão `[x]`, o Log de Execução está preenchido, e o
`progresso.md` registra `✅ Concluído` com "Concluída em" `2026-08-05`.

O frontmatter do mesmo arquivo continua dizendo o contrário:

```console
$ sed -n '1,9p' docs/tasks/01-ferramental.md | grep status:
status: pendente
```

São duas afirmações de estado sobre a mesma tarefa, dentro do repositório, que
se contradizem. Quem ler o arquivo da task — ou qualquer script que um dia
filtre as 40 tasks por `status:` — vê "pendente" numa tarefa fechada.

A causa não é descuido do executor: o `docs/prompts/01-executar.md` §4
("Atualizar progresso") enumera o que atualizar — tabela do `progresso.md`,
checklist da fase, "Concluída em", "Revisado em", Log de Execução — e **não
menciona o frontmatter**. O executor fez exatamente o que o prompt pede.

Sem correção o defeito se repete nas 39 tarefas restantes.

## Evidência

| Fonte | O que afirma |
|---|---|
| `docs/tasks/01-ferramental.md` linha 8 | `status: pendente` |
| `docs/tasks/progresso.md` linha 16 | `✅ Concluído` · `2026-08-05` |
| `docs/tasks/01-ferramental.md` linhas 115-120 | os seis critérios em `[x]` |
| `git show --stat 2aec9cb` | o commit que fechou a tarefa |

Os 40 arquivos de task nascem com `status: pendente`, então hoje o campo é
inerte — nenhum consumidor o lê. É justamente por isso que ele passou:

```console
$ grep -c "^status: pendente" docs/tasks/[0-4][0-9]-*.md | grep -c ':1'
40
```

## Causa raiz

O `01-executar.md` define o rito de fechamento sem citar o frontmatter, e o
frontmatter guarda um estado que o `progresso.md` já guarda — duplicação sem
dono.

## Correção

Rota escolhida: **manter o campo e sincronizá-lo**, acrescentando o passo ao
prompt para que valha das 39 tarefas seguintes.

### Arquivo: `docs/prompts/01-executar.md`

Na seção "### 4) Atualizar progresso", acrescentar um item à lista de "Se
concluída:", antes do item do Log de Execução:

```markdown
- Trocar `status: pendente` por `status: concluído` no **frontmatter do arquivo
  da tarefa**. O campo duplica a coluna Status do `progresso.md`; os dois têm de
  concordar, senão o arquivo da task afirma o contrário do índice
```

### Arquivo: `docs/tasks/01-ferramental.md`

Trocar a linha 8 do frontmatter:

```yaml
status: concluído
```

**Não** varrer as outras 39: elas estão pendentes de verdade, e o valor está
correto nelas.

### Rota alternativa, se o usuário preferir

Remover o campo `status:` dos 40 frontmatters e deixar o `progresso.md` como
fonte única. Elimina a duplicação em vez de sincronizá-la, mas mexe em 40
arquivos e tira metadado de um formato que ainda pode ganhar consumidor. Fica
registrada; a rota escolhida acima é a de menor toque.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/prompts/01-executar.md` | modificar |
| `docs/tasks/01-ferramental.md` | modificar |

## Verificação

- [x] `grep '^status:' docs/tasks/01-ferramental.md` devolve `concluído`
- [x] O `01-executar.md` §4 cita o frontmatter na lista de "Se concluída"
- [x] Nenhuma outra task teve o `status:` alterado:
      `git diff --stat` mostra só os dois arquivos acima
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-05

**Resumo do que foi feito:**

Trocado `status: pendente` por `status: concluído` no frontmatter do
`01-ferramental.md`, e acrescentado o passo correspondente à seção "4) Atualizar
progresso" do `01-executar.md`, antes do item do Log de Execução — é o que
impede o defeito de se repetir nas 39 tarefas restantes. As outras 39 não foram
tocadas: nelas o valor está certo.

**Problemas encontrados:**

A varredura de discrepância mostrou que o buraco não é só das tasks. O
`02-revisar.md` emite todo `CORR-WTE-XXX.md` com `status: pendente` no
frontmatter, e nem o `03-corrigir.md` §4 nem o `04-corrigir-tudo.md` fase 2
mandam sincronizá-lo ao fechar. Consertar só o lado das tasks deixaria o
repositório com duas regras para o mesmo campo — foi reconciliado em commit
próprio, junto com o `status:` deste arquivo.

**Arquivos criados/modificados:**

- `docs/prompts/01-executar.md` (modificado)
- `docs/tasks/01-ferramental.md` (modificado)
- `docs/tasks/correcoes-progresso.md` (modificado)
- `docs/tasks/CORR-WTE-001.md` (modificado)
