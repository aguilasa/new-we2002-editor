# Progresso de Correções — mapeamento do Pro Evolution Soccer 2 (PSX)

Correções abertas pelo `/revisar` ([`../prompts/02-revisar.md`](/docs/prompts/02-revisar.md))
e fechadas pelo `/corrigir`. O andamento das **tarefas** fica em
[`progresso.md`](/docs/tasks/progresso.md); este arquivo só rastreia correção.

**"Concluída em" nasce `—`** e é preenchida por quem executa a correção, com a
data do commit — o `/revisar` abre a correção, não a fecha.

**A numeração deste pool começa em `CORR-PES2-001`.** O pool anterior, com a
numeração `CORR-WTE-XXX` contínua de 001 a 143, desceu inteiro para
[`concluidos/`](/docs/tasks/concluidos/correcoes-progresso.md) em 2026-09-01,
junto com as tasks que o geraram — a pasta é um conjunto fechado, e o
`tools/check_tasks.py` confere cada task contra o progresso que mora ao lado
dela. O prefixo muda porque o projeto muda; a convenção de que **o pool é
único dentro do ciclo** continua valendo.

**Nenhuma correção aberta ainda.** Este arquivo nasce com a estrutura pronta e
sem linha, junto com o pool de tasks de PES2, em 2026-09-01. A primeira entrada
virá de uma revisão, não de uma suposição.

## Resumo executivo

| ID | ID Task Origem | Título | Criticidade | Status | Concluída em |
|---|---|---|---|---|---|
| — | — | *(nenhuma correção aberta)* | — | — | — |

<!-- Criticidade: Alta · Média · Baixa.
     Status: `[ ] pendente` · `[x] concluída` · `[x] envelhecida`.
     A coluna de origem aceita uma task **ou outra CORR**, quando a correção
     nasceu de uma correção.

     Modelo de linha, para quando a primeira for aberta -- as duas primeiras
     celulas sao link em `/docs/`, como manda a .claude/rules/links.md; aqui
     estao sem colchete para nao virar link quebrado na conferencia:

| CORR-PES2-001 -> /docs/tasks/CORR-PES2-001.md | PES2-TASK-04 -> a task de origem | <o problema em uma frase, nao o fix> | Alta | [ ] pendente | — |
-->

## Checklist

*(vazio — sem correção aberta)*

## Detalhes por correção

*(vazio — sem correção aberta)*

<!-- Modelo de bloco, para quando a primeira for aberta:

### CORR-PES2-001

- **Arquivo com problema:** `<caminho>` (linha N) e/ou `<caminho do gerador, se
  o arquivo for gerado — o conserto vai no gerador, nunca na saída>`
- **Sintoma:** <o que se observa, com o número medido dos dois lados>
- **Como foi detectado:** <a régua que acusou, e em que corrida>
- **Fix:** <o gesto, e o que fazer se a medição apontar para outra causa>
-->

---

## O que este projeto tem de diferente, e que muda a forma da CORR

**Não há oráculo** (§4.1 do [plano](/docs/PLAN-PES2-PSX.md)). No `newWe2002` e
no `wte/` a evidência de uma correção era uma faixa de bytes contra um binário
que sabia a resposta; aqui o oráculo é **o jogo rodando**, e a evidência é uma
captura de tela mais o offset que a produziu.

Três consequências para a seção `## Evidência` de qualquer `CORR-PES2-*`:

- **O quadro não entra no git.** É jogo comercial, mesma regra de `roms/` e dos
  FAQs. O que entra é o comando que o produz e o número medido — como o
  `boot_check.sh` já faz com desvio-padrão e contagem de pixels.
- **Divergência fora do esperado vira CORR com a faixa e o marcador**, não com
  o offset absoluto: offset constante não sobrevive à troca de release (§6.6).
- **"Não reproduz" é resultado**, e fecha a correção como `[x] envelhecida`
  quando o sintoma deixou de existir entre a abertura e a execução. O Log dela
  traz as medidas que mostram isso.
