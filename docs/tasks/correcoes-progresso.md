# Progresso de Correções — WE2002 Team Editor → Lazarus

Correções abertas pelo `/revisar` ([`../prompts/02-revisar.md`](../prompts/02-revisar.md))
e fechadas pelo `/corrigir`. O andamento das **tarefas** fica em
[`progresso.md`](progresso.md); este arquivo só rastreia correção.

**"Concluída em" nasce `—`** e é preenchida por quem executa a correção, com a
data do commit — o `/revisar` abre a correção, não a fecha.

## Resumo executivo

| ID | ID Task Origem | Título | Criticidade | Status | Concluída em |
|---|---|---|---|---|---|
| [CORR-WTE-001](CORR-WTE-001.md) | [WTE-TASK-01](01-ferramental.md) | Frontmatter da task diz `pendente` numa tarefa concluída | Baixa | [ ] pendente | — |
| [CORR-WTE-002](CORR-WTE-002.md) | [WTE-TASK-01](01-ferramental.md) | Dois números do `ambiente.md` só são reproduzíveis pelo scratchpad | Baixa | [ ] pendente | — |

## Checklist

- [ ] CORR-WTE-001 — sincronizar `status:` do frontmatter, e citá-lo no `01-executar.md`
- [ ] CORR-WTE-002 — escrever no `ambiente.md` como remedir os dois números derivados

## Detalhes por correção

### CORR-WTE-001

- **Arquivo com problema:** `docs/tasks/01-ferramental.md` (frontmatter), com a
  causa em `docs/prompts/01-executar.md`
- **Sintoma:** `status: pendente` numa tarefa que o `progresso.md` registra como
  `✅ Concluído` em 2026-08-05, com os seis critérios `[x]`
- **Como foi detectado:** `grep '^status:' docs/tasks/*.md` confrontado com a
  tabela de resumo do `progresso.md`
- **Fix:** trocar para `concluído` no arquivo da task e acrescentar o passo à
  seção "4) Atualizar progresso" do `01-executar.md`, para não repetir nas 39
  tarefas restantes

### CORR-WTE-002

- **Arquivo com problema:** `wte/re/ambiente.md`
- **Sintoma:** os dois blocos de "Achado" citam evidência que mora no scratchpad
  da execução (`ShowInfo.java`, `wte-windows.tsv`) e não trazem o comando que a
  regera — os únicos números do arquivo sem a coluna "Como foi medido"
- **Como foi detectado:** `git ls-files wte/` devolve só o `.md`; os números
  foram reproduzidos a partir do scratchpad ainda não limpo, que some no próximo
  boot
- **Fix:** inlinar no `ambiente.md` o `analyzeHeadless` + `ShowInfo.java` e o
  laço `xdotool` do censo de janelas, e remover a referência ao caminho volátil.
  Os valores estão certos; o que falta é a rota de volta
