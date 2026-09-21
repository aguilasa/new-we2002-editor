# Convenções de task

Desde a migração para o plugin **Rite** (branch `adopt-rite`), quem conduz as tasks é o rito do
plugin, e quem guarda as convenções é o `rite.toml` na raiz. Esta página diz o que vale **neste
repositório**; o rito em si está na documentação do plugin
(<https://github.com/aguilasa/rite>: `docs/CONCEPTS.md`, `docs/CONFIG.md`).

## Comandos

| Antes | Agora |
| --- | --- |
| `/executar [ciclo]` | `/rite:execute [ciclo] [ID]` |
| `/executar-lote [ciclo] N` | `/rite:execute-batch [ciclo] [N]` |
| `/revisar [ciclo]` | `/rite:review [ciclo] [ID]` |
| `/corrigir [ciclo]` | `/rite:fix [ciclo] [ID]` |
| `/corrigir-tudo [ciclo]` | `/rite:fix-all [ciclo]` |
| — | `/rite:status`, `/rite:new-cycle`, `/rite:plan-to-tasks`, `/rite:close-cycle`, `/rite:retro` |

Os ciclos continuam onde estavam e têm nome: `pes2` (`docs/tasks/`), `looks` (`docs/tasks/looks/`),
`port-mcr` (`docs/tasks/port-mcr/`) e `wte`, arquivado em `docs/tasks/concluidos/`.

## O que mudou, e o que não mudou

- **O estado mora no frontmatter de cada item** — `status`, `done_on`, `done_commit`,
  `reviewed_on`. As tabelas do `progresso.md` e do `correcoes-progresso.md` são **geradas** entre
  `<!-- rite:begin … -->` e `<!-- rite:end -->`; nunca edite dentro da região nem marque estado à
  mão. Quem escreve é o CLI (`rite close`, `rite mark*`), o que acaba com a classe inteira de CORRs
  de escrituração (coluna errada, `status:` esquecido).
- **A task continua declarando contra o que se mede**, agora em `source_of_truth`, com âncora:
  `/docs/PLAN-X.md#4.2`. `rite anchors <plano>` lista as âncoras válidas.
- **A CORR continua autocontida** (Problema, Evidência, Causa raiz, Correção) e agora traz `origin`
  e `severity` no frontmatter. O ID de uma CORR nova sai sempre do `rite new-fix` — nunca "o maior
  + 1" contado à mão.
- **A ordem de execução** de um ciclo é a numérica, a menos que o `progresso.md` liste `order:` no
  frontmatter — é o caso do `looks`, que roda 36–40 antes de 32.
- **Um ciclo é uma pasta com `progresso.md`**, `depends_on` não atravessa pasta, e projeto
  encerrado desce para `docs/tasks/concluidos/`. Isso não mudou.
- **Os perfis** (`docs/prompts/perfil-<ciclo>.md`) continuam sendo a camada do ciclo, lidos por todo
  comando do rito. Os prompts antigos (`docs/prompts/0*.md`, `geral.md`) e os wrappers de
  `.claude/commands/` foram removidos; a versão final deles está no histórico
  (`git show bcb5aee:docs/prompts/01-executar.md`).

## Conferência

```bash
ctest -R tasks          # roda tools/check_tasks.py, que chama `rite.py check`; pula se o plugin não estiver instalado
```

O `rite.py check` confere frontmatter e vocabulário, `source_of_truth` (arquivo e âncora),
`depends_on`, links, tabelas geradas em dia, a entrada da fase no perfil do ciclo e o tamanho do
perfil. Rode antes de commitar task nova.
