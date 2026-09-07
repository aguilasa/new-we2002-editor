---
id: MCR-TASK-01
title: "O ciclo em subpasta — o Passo 0 agnóstico nos prompts e wrappers"
type: infraestrutura
category: processo
phase: 0
depends_on: []
fonte_de_verdade: "/docs/tasks/port-mcr/01-ciclo-em-subpasta.md §Critério de conclusão"
status: pendente
---

# MCR-TASK-01: O ciclo em subpasta

## Contexto

- **Referência:** esta task. O critério mora aqui porque o que ela muda é o
  **rito**, e o rito não tem plano — ele tem
  [`.claude/rules/tasks.md`](../../../.claude/rules/tasks.md), que esta task
  também altera.
- **Ovo e galinha:** enquanto o Passo 0 não existir, `/executar port-mcr` não
  resolve pasta nenhuma. Esta task é feita no **bootstrap**, junto com a
  criação da pasta, e só depois o ciclo anda por comando.

O que hoje presume `docs/tasks/` raso, medido em 2026-09-07: **35 pontos** — os
5 wrappers de `.claude/commands/`, os 5 prompts de `docs/prompts/`, o
`geral.md`, os 2 perfis, os 2 templates, a conferência de existência de link de
`.claude/rules/links.md` (escopo raso) e as duas regras.

O que **já funciona sem tocar em nada**: `tools/check_tasks.py` varre
`docs/tasks/` e cada subpasta com `progresso.md` próprio, e a ligação
task↔progresso já aceita a marca `/docs/tasks/port-mcr/<arquivo>.md)`.

---

## Objetivo

Fazer os cinco comandos aceitarem, como primeira palavra do argumento, o nome
de uma subpasta de `docs/tasks/` que tenha `progresso.md` próprio — e resolver
**todo** caminho a partir dela. Sem argumento, nada muda.

---

## O Passo 0 — texto idêntico nos cinco prompts

Entra logo depois do cabeçalho de cada prompt:

> Resolva a pasta do ciclo **antes** de qualquer leitura. Se o primeiro termo do
> argumento nomear uma subpasta de `docs/tasks/` que contenha `progresso.md`, a
> pasta do ciclo é essa; senão, é `docs/tasks/`. **Um argumento é nome de ciclo
> se, e só se, `docs/tasks/<arg>/progresso.md` existe** — confira com `ls`,
> nunca pelo formato do texto. Argumento que não resolve para pasta continua
> sendo o que este prompt já dizia; dois termos são `<ciclo> <item>`, nessa
> ordem; **sem argumento, nada muda.** Daí em diante `<CICLO>` é o caminho da
> pasta a partir da raiz, e todo caminho sai dele — inclusive os links, que são
> `/<CICLO>/<arquivo>.md`. O `perfil:` e o prefixo saem do `progresso.md` **da
> pasta resolvida**. `depends_on` não atravessa pasta, e o pool de correções é
> único **dentro** do ciclo.

---

## Critério de conclusão

- [ ] O Passo 0 nos cinco prompts de `docs/prompts/`, com o **mesmo texto**, e
      os literais `docs/tasks/…` do corpo resolvidos para `<CICLO>/…`.
- [ ] **As citações datadas de ciclo fechado ficam intactas.** As linhas que
      citam `docs/tasks/concluidos/CORR-WTE-*` são evidência do que aconteceu;
      reindexá-las falsifica o registro, e `.claude/rules/tasks.md` diz isso em
      letras. `git diff` não pode tocá-las.
- [ ] O parágrafo do argumento nos cinco wrappers de `.claude/commands/`, com o
      caso torto do `executar-lote` explicitado: `<ciclo> 3` é pasta + tamanho,
      `<ciclo>` sozinho é pasta + o padrão, `3` sozinho é raso + 3.
- [ ] `docs/prompts/geral.md` sem o caminho absoluto cravado, e com o bloco do
      ciclo em subpasta.
- [ ] Os dois `*.template.md` com o segmento de ciclo nos links de exemplo, e o
      `progresso.template.md` com a linha "**Pasta deste ciclo:**" e o campo
      `perfil:`, que hoje falta nele.
- [ ] `.claude/rules/tasks.md` com a seção `## O ciclo pode morar numa subpasta`
      e as quatro afirmações: pasta é ciclo se tem `progresso.md`;
      `correcoes-progresso.md` sozinho **não** qualifica; link de dentro continua
      `/docs/` + caminho completo; `depends_on` não atravessa pasta.
- [ ] `.claude/rules/links.md` com a conferência de existência alcançando a
      subpasta e excluindo `docs/tasks/concluidos/` — e registrando que, quando
      os `CORR-MCR-*.md` tiverem transcrição de `grep`, a exclusão certa passa a
      ser por `CORR-*.md` e não por pasta.
- [ ] `tools/check_tasks.py` recusando pasta que tem `correcoes-progresso.md` e
      **não** tem `progresso.md` — o buraco conhecido vira vermelho.
- [ ] `CLAUDE.md` com o parágrafo do projeto novo e a nota de que ciclo **vivo**
      pode morar em subpasta (hoje o único enquadramento é `concluidos/`, que é
      história).
- [ ] `grep -rn 'port-mcr' docs/prompts .claude` sai **vazio**.
- [ ] `python3 tools/check_tasks.py` verde, e `ctest -R tasks` verde.
- [ ] `/executar` sem argumento escolhe **a mesma** task de antes.

---

## Armadilhas

- **Reindexar não é generalizar.** Trocar um caminho dentro de uma citação
  histórica produz uma afirmação falsa sobre o que aconteceu. Texto que descreve
  um ciclo **se move** para o perfil; só o rito se generaliza.
- **`depends_on` não atravessa pasta**, e não deve passar a atravessar: a pasta
  é conjunto fechado, e é isso que faz a convenção continuar valendo quando o
  projeto desce para `concluidos/`.
- **Nenhum prompt pode citar `port-mcr`.** Três CORRs do ciclo anterior
  custaram a firmar essa regra.

---

## Log de Execução

*(a preencher)*
