---
id: CORR-MCR-001
title: "Correção: `.claude/rules/tasks.md` ainda afirma que os prompts apontam para `docs/tasks/progresso.md`"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-MCR-001: a regra ficou com a afirmação que a MCR-TASK-01 tornou falsa

## Problema identificado

A MCR-TASK-01 fez os cinco prompts **resolverem** a pasta do ciclo no Passo 0 e
trabalharem com `<CICLO>/progresso.md`. O `CLAUDE.md` foi atualizado na mesma
passagem — o bullet de lá hoje diz *"Até 2026-09-07 eles cravavam
`docs/tasks/progresso.md`; desde então resolvem a pasta do ciclo no Passo 0"*.

O gêmeo dele em `.claude/rules/tasks.md` **não** foi, e continua afirmando o
contrário em dois sítios:

```
$ grep -n 'docs/tasks/progresso.md' .claude/rules/tasks.md
29:1. ler `docs/tasks/progresso.md` e `docs/tasks/correcoes-progresso.md`;
176:**Os prompts continuam apontando para `docs/tasks/progresso.md`** — o vivo, o
```

A linha 29 está na lista *"Os prompts sabem:"* da seção
`## A task declara a própria fonte de verdade`; a 176, na seção
`## Projeto encerrado vai para docs/tasks/concluidos/`.

As duas eram verdadeiras até 2026-09-07 e deixaram de ser nesse dia. Não são
citação datada de ciclo fechado — são afirmação em tempo presente sobre o rito,
no arquivo que o repositório carrega como instrução de projeto em toda sessão.

## Evidência

| afirmação | onde | o que o rito faz hoje |
|---|---|---|
| "ler `docs/tasks/progresso.md` …" | `.claude/rules/tasks.md:29` | `docs/prompts/01-executar.md` Passo 0: resolve `<CICLO>` e lê `<CICLO>/progresso.md` |
| "Os prompts continuam apontando para `docs/tasks/progresso.md`" | `.claude/rules/tasks.md:176` | idem, nos cinco prompts — bloco `Passo 0` idêntico, `md5 aa2ef72d…` nos cinco |

```
$ for f in docs/prompts/0*.md; do awk '/^## Passo 0/,/^---$/' "$f" | md5sum; done
aa2ef72d1b019815d93fb9fbb68ddfd0  -   (x5)
```

E o `CLAUDE.md`, atualizado pela mesma task:

> **Os prompts nunca apontam para o arquivo.** Até 2026-09-07 eles cravavam
> `docs/tasks/progresso.md`, o vivo; desde então resolvem a **pasta do ciclo**
> no Passo 0 e trabalham com `<CICLO>`.

## Causa raiz

A varredura da MCR-TASK-01 alcançou o `CLAUDE.md` e a seção nova de
`.claude/rules/tasks.md`, mas não reconciliou as duas seções **antigas** do
mesmo arquivo de regra, que falavam do mesmo caminho.

## Correção

### Arquivo: `.claude/rules/tasks.md`

- **linha 29** — trocar o caminho cravado pela pasta resolvida:

  ```markdown
  1. ler o `progresso.md` e o `correcoes-progresso.md` da **pasta do ciclo**
     (`docs/tasks/`, ou a subpasta que o argumento nomear — ver
     "O ciclo pode morar numa subpasta");
  ```

- **linha 176** — a intenção do parágrafo (`concluidos/` é história, e prompt
  que aponta para história executa task já feita) **continua valendo**; o que
  envelheceu é o caminho. Reescrever no mesmo espírito do `CLAUDE.md`:

  ```markdown
  **Os prompts nunca apontam para esta pasta.** Até 2026-09-07 eles cravavam
  `docs/tasks/progresso.md`, o vivo; desde então resolvem a **pasta do ciclo**
  no Passo 0 e trabalham com `<CICLO>`. Em nenhuma das duas formas
  `concluidos/` é alcançável — é história, e prompt que aponta para história
  executa task já feita.
  ```

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `.claude/rules/tasks.md` | modificar |

## Verificação

- [ ] `grep -n 'docs/tasks/progresso.md' .claude/rules/tasks.md` não devolve
      afirmação em tempo presente sobre para onde os prompts apontam
- [ ] a seção `## Projeto encerrado vai para docs/tasks/concluidos/` continua
      dizendo que `concluidos/` não é alcançável pelos prompts
- [ ] `python3 tools/check_tasks.py` verde e `ctest -R tasks` verde
- [ ] a conferência de forma de link de `.claude/rules/links.md` sem sítio novo
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-07

**Resumo do que foi feito:**

A linha 29 de `.claude/rules/tasks.md` deixou de cravar o caminho e passou a
falar da **pasta do ciclo**, remetendo à seção "O ciclo pode morar numa
subpasta" do mesmo arquivo. A linha 176 foi reescrita no espírito do
`CLAUDE.md`: registra que os prompts cravavam `docs/tasks/progresso.md` até
2026-09-07 e que desde então resolvem `<CICLO>` no Passo 0, e mantém a
conclusão do parágrafo — `concluidos/` não é alcançável em nenhuma das duas
formas.

A varredura do termo puxou um sítio irmão que a CORR não previa:
`docs/prompts/perfil-wte.md:15` dizia, em tempo presente, que o perfil em vigor
é o que o `/docs/tasks/progresso.md` nomeia — singular e raso, falso desde que
o ciclo vivo pode morar numa subpasta. Corrigido na mesma passagem, pela regra
"discrepância achada no caminho".

**Problemas encontrados:**

O sítio irmão do `perfil-wte.md` acima. O restante dos 30 acertos do termo é
legítimo: o ciclo de PES2 **é** o raso, e as tasks dele citam o próprio
`progresso.md` com razão; as citações dentro dos `CORR-MCR-*` descrevem o
sintoma.

**Arquivos criados/modificados:**

- `.claude/rules/tasks.md` — linhas 29 e 176
- `docs/prompts/perfil-wte.md` — linha 15 (discrepância revelada pela varredura)
