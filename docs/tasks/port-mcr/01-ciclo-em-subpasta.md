---
id: MCR-TASK-01
title: "O ciclo em subpasta — o Passo 0 agnóstico nos prompts e wrappers"
type: infraestrutura
category: processo
phase: 0
depends_on: []
fonte_de_verdade: "/docs/tasks/port-mcr/01-ciclo-em-subpasta.md §Critério de conclusão"
status: concluído
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

- [x] O Passo 0 nos cinco prompts de `docs/prompts/`, com o **mesmo texto**, e
      os literais `docs/tasks/…` do corpo resolvidos para `<CICLO>/…`.
- [x] **As citações datadas de ciclo fechado ficam intactas.** As linhas que
      citam `docs/tasks/concluidos/CORR-WTE-*` são evidência do que aconteceu;
      reindexá-las falsifica o registro, e `.claude/rules/tasks.md` diz isso em
      letras. `git diff` não pode tocá-las.
- [x] O parágrafo do argumento nos cinco wrappers de `.claude/commands/`, com o
      caso torto do `executar-lote` explicitado: `<ciclo> 3` é pasta + tamanho,
      `<ciclo>` sozinho é pasta + o padrão, `3` sozinho é raso + 3.
- [x] `docs/prompts/geral.md` sem o caminho absoluto cravado, e com o bloco do
      ciclo em subpasta.
- [x] Os dois `*.template.md` com o segmento de ciclo nos links de exemplo, e o
      `progresso.template.md` com a linha "**Pasta deste ciclo:**" e o campo
      `perfil:`, que hoje falta nele.
- [x] `.claude/rules/tasks.md` com a seção `## O ciclo pode morar numa subpasta`
      e as quatro afirmações: pasta é ciclo se tem `progresso.md`;
      `correcoes-progresso.md` sozinho **não** qualifica; link de dentro continua
      `/docs/` + caminho completo; `depends_on` não atravessa pasta.
- [x] `.claude/rules/links.md` com a conferência de existência alcançando a
      subpasta e excluindo `docs/tasks/concluidos/` — e registrando que, quando
      os `CORR-MCR-*.md` tiverem transcrição de `grep`, a exclusão certa passa a
      ser por `CORR-*.md` e não por pasta.
- [x] `tools/check_tasks.py` recusando pasta que tem `correcoes-progresso.md` e
      **não** tem `progresso.md` — o buraco conhecido vira vermelho.
- [x] `CLAUDE.md` com o parágrafo do projeto novo e a nota de que ciclo **vivo**
      pode morar em subpasta (hoje o único enquadramento é `concluidos/`, que é
      história).
- [x] `grep -rn 'port-mcr' docs/prompts/0*.md docs/prompts/geral.md .claude/commands`
      sai **vazio** — o rito não conhece ciclo pelo nome. As duas regras de
      `.claude/rules/` **podem** citá-lo como exemplo, e citam: elas já nomeiam
      `PES2` e `WTE` do mesmo jeito, e o que descreve uma convenção precisa de
      um caso concreto para não virar prosa.
- [x] `python3 tools/check_tasks.py` verde, e `ctest -R tasks` verde.
- [x] `/executar` sem argumento escolhe **a mesma** task de antes.

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

**Executado em:** 2026-09-07

## Resumo do que foi feito

O rito deixou de conhecer a pasta. Os cinco prompts ganharam o **Passo 0** —
texto idêntico nos cinco — e os literais do corpo viraram `<CICLO>/…`: 7 sítios
no `01`, 11 no `02`, 9 no `03`, 5 no `04` e 5 no `05`. Os cinco wrappers de
`.claude/commands/` ganharam o parágrafo do argumento antes da frase do
`perfil:`, e o `executar-lote` ganhou os três formatos explicitados
(`<ciclo> 3`, `<ciclo>`, `3`).

**A varredura pulou toda linha que cita `concluidos`**, e o `git diff` prova:
zero linhas com `concluidos` no diff dos prompts. São citação datada de ciclo
fechado, e reindexá-las falsificaria o registro.

Duas coisas saíram diferentes do previsto, as duas por medição:

- **O `grep` de "nenhum prompt cita o ciclo" precisou de escopo.** As duas
  regras de `.claude/rules/` **citam** `port-mcr` — e devem: elas já nomeiam
  `PES2` e `WTE` do mesmo jeito, e convenção sem caso concreto vira prosa. O
  critério passou a ser sobre `docs/prompts/0*.md`, `geral.md` e
  `.claude/commands/`, que é onde a regra tem efeito. O `geral.md`, que é folha
  de colar, usa `<subpasta>`.
- **A conferência de *forma* de link de `.claude/rules/links.md` ficou vermelha**
  com os modelos dos prompts: `](/<CICLO>/XX-nome.md)` não casa `](/docs/`. É
  placeholder, como o `<PREFIXO>`, e entrou na exclusão junto com eles, com o
  parágrafo que explica.

O caso vermelho do `check_tasks.py` foi exercitado de verdade: uma pasta com
`correcoes-progresso.md` e sem `progresso.md` faz o gate sair 1 dizendo
`_teste_orfao/: tem correcoes-progresso.md e nao tem progresso.md`. Antes desta
task esse caso passava calado — a pasta ficava invisível para a varredura.

## Arquivos criados/modificados

- `docs/prompts/01-executar.md` … `05-executar-lote.md` — o Passo 0 e os 37
  sítios resolvidos.
- `docs/prompts/geral.md` — sem o caminho absoluto do progresso; com o bloco do
  ciclo em subpasta.
- `.claude/commands/{executar,revisar,corrigir,corrigir-tudo,executar-lote}.md`
  — o parágrafo do argumento e os caminhos por `<CICLO>`.
- `docs/tasks/progresso.template.md` — "Pasta deste ciclo", o campo `perfil:`
  (que faltava) e o prefixo declarado; links de exemplo com `<CICLO>/`.
- `docs/tasks/correcoes-progresso.template.md` — idem, e o `progresso.md` do
  link é o **ao lado deste arquivo**.
- `.claude/rules/tasks.md` — a seção `## O ciclo pode morar numa subpasta`.
- `.claude/rules/links.md` — a conferência de existência alcança subpasta viva e
  exclui `concluidos/`; a de forma aceita `/<CICLO>/`.
- `tools/check_tasks.py` — a quinta conferência, com o caso vermelho.
- `CLAUDE.md` — o parágrafo do ciclo vivo em subpasta, e o bullet que dizia "os
  prompts continuam apontando para `docs/tasks/progresso.md`", que envelheceu
  nesta data.

## Verificação

| item | resultado |
|---|---|
| `grep -rn 'port-mcr' docs/prompts/0*.md docs/prompts/geral.md .claude/commands` | vazio |
| `git diff docs/prompts \| grep -c concluidos` | **0** |
| conferência de forma de link | só o arquivo histórico, que já era assim |
| conferência de existência de link | vazia |
| `python3 tools/check_tasks.py` | `100 task(s), ok` |
| `ctest -R tasks` | 1/1 passed |
| caso vermelho do gate | sai 1, com a pasta nomeada |
| `/executar` sem argumento | `<CICLO>` = `docs/tasks`, e a seleção é a mesma de antes — a `PES2-TASK-03`, que está `🔄 Em andamento` |
