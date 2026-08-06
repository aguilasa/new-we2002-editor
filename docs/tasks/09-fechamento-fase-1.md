---
id: WTE-TASK-09
title: "Fechamento da fase 1 — a extração estática está completa?"
type: fechamento
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-03", "WTE-TASK-04", "WTE-TASK-05", "WTE-TASK-06", "WTE-TASK-07", "WTE-TASK-08"]
status: concluído
---

# WTE-TASK-09: Fechamento da fase 1

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 1, critério de pronto.
- A fase 1 é a única que **não usa decompilador**. Fechá-la mal significa entrar
  na Fase 4 lendo assembly para descobrir coisa que `strings` teria dado.

---

## Objetivo

Conferir que `wte/re/` está completo e que os números batem entre si.

### Conferências cruzadas

1. **DFM × handlers.** Todo `OnClick` citado nos 18 DFM tem entrada em
   `published_methods.tsv`? Todo handler do TSV é referenciado por algum DFM?
   Divergência nas duas direções é achado, não erro de ferramenta.
2. **Strings × handlers.** Quantas strings ficaram sem handler dono? Se for
   muito, a heurística de referência por imediato está perdendo caso.
3. **Offsets × `Offsets.hpp`.** Os 19 continuam batendo depois de a tabela ter
   limite medido? Algum caiu fora do limite?
4. **Assets × formulários.** Os `TImage` dos DFM carregam bitmap embutido ou
   arquivo externo? Se embutido, parte dos 197 pode ser irrelevante.

### Recontagem obrigatória

Todo número que o plano afirma na §1 foi medido em 2026-08-05 por script
descartável. Remedir com as ferramentas versionadas e **reconciliar**:

| Afirmação do plano | Onde remedir |
|---|---|
| 18 formulários, ~430 componentes | `dfm_extract.py` |
| 96 handlers | `dump_published.py` |
| 19 de 69 offsets | `dump_offsets.py` |
| 70 strings com padding | `dump_strings.py` |
| 13 unidades `Tep2002_*` | `objdump -x` |
| 322 imports, sendo 300 de `rtl60.bpl`/`vcl60.bpl` (§1.2) | `dump_units.py` |
| 197 bitmaps + `dat.bin` (§1.2 e §1.8) | `find -iname '*.bmp'` — ver [`assets.md`](../../wte/re/assets.md) |

A última linha não tem gerador: a WTE-TASK-08 decidiu rota inline para os
assets, com o comando ao lado de cada número. A coluna "onde remedir" aponta o
comando e o documento que o executa.

Divergência entre o plano e a medição versionada se resolve **a favor da
medição**, e o plano é corrigido.

### Varrer os sítios, não só a §1

Corrigir a §1 do plano não fecha um número errado — ele se espalha. O "197
bitmaps" está em **nove** lugares, dois deles no plano e dois em tarefas da fase
7 ainda por executar (a 38 vai pedir mensagem de erro sobre essa contagem, a 39
uma regra de empacotamento). Para cada número reconciliado:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rn "<o número velho>" docs/ wte/re/
```

O alvo é zerar a saída fora dos documentos que **narram** a correção
(`correcoes-progresso.md`, os `CORR-WTE-*.md`, os Logs de Execução), onde o
número velho é citação histórica e fica. Registrar em `wte/re/fase-1.md` o
`grep -rn "197" docs/ | wc -l` de antes e de depois.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/fase-1.md` | criar — as quatro conferências e a reconciliação |
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§1, se algum número mudar) |
| `docs/tasks/progresso.md` | modificar |

---

## Critério de conclusão

- [x] As quatro conferências cruzadas feitas, com o resultado escrito
- [x] Os sete números do plano remedidos por ferramenta versionada
- [x] Divergência corrigida no plano, não escondida
- [x] Cada número reconciliado varrido em `docs/` e `wte/re/`, e a contagem de
      antes e de depois registrada em `wte/re/fase-1.md` — a varredura virou
      guarda do `check_fase1.py`, não `grep` à mão; ver o Log
- [x] Nenhum item da Fase 1 em aberto sem justificativa
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-06

- **Resumo do que foi feito:**

  As quatro conferências cruzadas fecharam, e três delas **sem achado novo** —
  o que é resultado: as WTE-TASK-04 a 08 já tinham antecipado a pergunta. A
  quarta achou. A recontagem dos 18 `.dfm` dá **441** componentes contra os
  "~430" do plano, e a diferença não é só o `~`: um dos 441 **não tem nome** —
  um `TStaticText` de 4×4 px no `MainForm`, que o DFM escreve como `object
  TStaticText`, sem identificador. Um regex que exija `nome: Classe` devolve
  440 e não avisa. O `dfm2lfm.py` já o tratava.

  Quatro dos sete números do plano estavam errados, e as quatro causas são
  diferentes — só uma é erro de medição (os imports de package, 300 → 267). Os
  bitmaps eram **erro de soma na prosa** (a §1.8 lista as cinco pastas certas e
  soma 197); as strings com enchimento eram **população diferente** (13 em
  `.data`, 80 nos DFM, e a §1.5 contou o binário inteiro); os componentes eram
  estimativa declarada. Registrar a causa importa mais que o número: só a de
  imports pede desconfiar da ferramenta.

  A varredura de sítios virou **guarda de build**, não `grep` à mão. Eram 18
  afirmações vivas dos quatro números; hoje são 0, e o `check_fase1.py` aborta
  se alguma voltar. O perímetro é a parte que exigiu decisão: fica de fora o
  documento que **narra** a correção, o Log de Execução de qualquer tarefa, e o
  **enunciado de tarefa já concluída** — este último medido pelo `status:` do
  frontmatter. Enunciado executado é história; enunciado **pendente** é
  instrução, e foi essa distinção que trouxe a WTE-TASK-38 e a 39 para dentro
  da correção antes de serem executadas contra uma contagem inexistente.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/tools/check_fase1.py` | criado — gerador com `--check`, entra sozinho no `make -C wte check` |
  | `wte/tools/test_check_fase1.py` | criado — 11 testes do perímetro e do corte por contexto, sem abrir o `.exe` |
  | `wte/re/fase-1.md` | criado (gerado) |
  | `wte/tools/README.md` | modificado — as duas tabelas |
  | `docs/PLAN-WTE-LAZARUS.md` | modificado — §1.2, §1.5, §1.6, §1.8, §5, §8.8 |
  | `docs/tasks/progresso.md` | modificado — marcação, tabela de estado, censo, três seções de prosa, estrutura de pastas, nota de execução |
  | `docs/tasks/08-convencao-dos-assets.md` | modificado — o título dizia 197 |
  | `docs/tasks/38-nome-e-linhagem.md`, `39-empacotamento.md` | modificados — pendentes, iam pedir mensagem de erro e regra de empacotamento sobre 197 |

- **Problemas encontrados:**

  **O documento gerado é ponto fixo da própria varredura.** A primeira versão
  do `fase-1.md` listava os sítios residuais numa tabela; como o arquivo mora
  no perímetro varrido, publicar o número velho ali mudava a contagem que ele
  mesmo publicava. A saída foi tirar a tabela e fazer resíduo **abortar**, como
  o `FORBIDDEN` do `port_database.py` — resíduo é falha, não linha de relatório.
  O mesmo pegou duas vezes na prosa do plano: a frase que eu escrevi para
  explicar a correção citava `"70 strings"` e virou resíduo dela mesma. Quem
  narra a correção é o `fase-1.md`, não o documento corrigido.

  **A coluna "sítios antes" não é remedível.** Ela é constante no script, com a
  data e o perímetro escritos ao lado. Não há como medi-la depois de corrigir,
  e fingir que sai de ferramenta seria pior do que dizer que é constante.

  **Dois números vêm de uma frase, não de um TSV.** A cobertura de `.text` e os
  literais com enchimento dos DFM são casados por regex no `strings.md`, e os
  imports no `unidades-vcl.md`. Os três abortam se a frase mudar de forma —
  desfecho certo, e ainda assim acoplamento a registrar. A alternativa era um
  quinto leitor de PE nesta árvore, sem o teste que a cópia do `dump_units.py`
  tem.
