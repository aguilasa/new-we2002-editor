---
id: WTE-TASK-40
title: "Verificação final — as três condições da definição de pronto"
type: fechamento
category: verificação
phase: 7
depends_on: ["WTE-TASK-36", "WTE-TASK-37", "WTE-TASK-39"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md §0, definição de pronto"
status: concluído
---

# WTE-TASK-40: Verificação final

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §0, definição de pronto.

> As três condições, **juntas**:
>
> 1. Os 96 handlers publicados têm equivalente funcional em Pascal.
> 2. Para cada operação que grava, `wte.exe` e o app Lazarus produzem imagem
>    byte-idêntica, nas duas ROMs.
> 3. O app roda em Linux x86-64 nativo, sem Wine, sem camada 32-bit.

---

## Objetivo

Provar as três, e escrever o que o projeto **pode** e **não pode** afirmar.

### Condição 1 — os 96

Já conferida na WTE-TASK-31. Reconferir que nada regrediu: o índice de
`re/spec/` continua com 96, sem `aberto`, e todo `não portado` com justificativa.

### Condição 2 — byte-idêntico

Já medida na WTE-TASK-34. Reconferir depois das mudanças das tasks 36 a 39 — em
especial a 36, que mexeu em comportamento de campo.

### Condição 3 — nativo

A que ninguém conferiu ainda, e a mais fácil de falhar por descuido:

- `ldd` no binário não mostra nada de Wine
- não há dependência de 32 bits
- roda num ambiente **sem** Wine instalado — testar de verdade, não presumir
- não lê nada de `work/wineprefix*`

### O vocabulário

Escrever o que o projeto pode afirmar, com a mesma disciplina que o
`newWe2002` usa. "Verificado" não é "correto":

- **Verificado:** as operações que a bateria cobre, nas duas ROMs testadas.
- **Não verificado:** operação fora da bateria; ROM fora das duas; combinação de
  edições não testada.
- **Divergente por decisão:** o que está em `re/divergencias.md`.

Uma frase honesta de resumo, para reusar em README e commit, vale mais que um
número.

### O que registrar como aberto

Todo item que ficou de fora, com a razão. O `newWe2002` fez isso — a Fase 7 dele
fechou com um item do checklist aberto (editar nome de time pela janela Qt e
comparar com o oráculo, bloqueado pela Citrix filtrando input sintético) e a
seção 11 do `PLAN-WINDOWS.md` diz isso em vez de omitir.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§11, registro de execução) |
| `wte/README.md` | modificar — o vocabulário e o que está aberto |
| `docs/tasks/progresso.md` | modificar |
| `wte/tools/sem_wine.sh` | **criar** — o ambiente sem Wine e sem 32 bits |
| `wte/tools/nativo_check.sh` | **criar** — as sete medidas da condição 3 |
| `wte/re/nativo.md`, `wte/re/nativo.tsv` | **criar** — a evidência da condição 3 |
| `wte/re/golden.{tsv,md}` | modificar — a bateria refeita |
| `wte/tools/README.md` | modificar — as duas ferramentas novas |

*(As cinco últimas linhas foram acrescentadas na execução: o enunciado previa
só documento, e a condição 3 exigia ferramenta — "testar de verdade, não
presumir" não se cumpre escrevendo prosa.)*

---

## Critério de conclusão

- [x] Condição 1 reconferida, sem regressão
- [x] Condição 2 reconferida depois das tasks 36 a 39
- [x] Condição 3 testada em ambiente sem Wine, não presumida
- [x] Vocabulário escrito: o que é verificado, o que não é, o que diverge
- [x] Todo item aberto listado com a razão
- [x] §11 do plano preenchido
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-26

- **Resumo do que foi feito:**

  As três condições da §0 foram medidas, e **nenhuma por prosa**. A 1
  (`spec_index.py --check`) e a 2 (`golden_suite.sh --rom ambas`) já tinham
  ferramenta; a 3 não tinha nada, e é onde estava o trabalho.

  **O que se aprendeu, e vale além desta task:** *"o app não usa Wine"* e *"o
  app roda onde Wine não existe"* são afirmações diferentes, e a primeira é
  fácil de entregar no lugar da segunda — um `ldd` limpo responde a errada. Esta
  máquina **tem** Wine e não pode deixar de ter (o oráculo A depende dele),
  então a única saída honesta era fabricar a ausência: um user+mount namespace
  sem privilégio (`bwrap`) com `tmpfs` vazio por cima de tudo que é Wine aqui.
  E "tudo que é Wine aqui" não é `/usr/bin/wine` — **não há pacote `wine` no
  apt desta máquina**; o Wine é o runner `soda-9.0-1` do Bottles, em
  `~/.var/app/`. Mascarar o caminho óbvio não teria escondido nada, e o teste
  passaria sem medir. Por isso o `sem_wine.sh` tem guarda: ambiente que só
  *parece* limpo mede tão pouco quanto não medir.

  **E a guarda tem duas cláusulas, das quais só uma trabalha aqui** — medido
  pela [CORR-WTE-120](/docs/tasks/CORR-WTE-120.md), porque este parágrafo
  creditava a inerte. A primeira recusa se `wine`/`wine64`/`wineserver`/
  `winecfg` responderem no `PATH`; ela pega a máquina com o pacote do apt, e
  **aqui é verdadeira antes de mascarar qualquer coisa** — é o que as três
  linhas acima acabaram de dizer, sem notar que isso a desarma. Quem recusa de
  verdade é a segunda: cada alvo mascarado tem de ficar **vazio** dentro do
  namespace. Apagar a segunda desliga a conferência mesmo com a primeira
  intacta, e isso está medido em `test_check_nativo.py`.

  A segunda lição é a medida `carga` do `nativo_check.sh`. Janela vazia abre
  igual à janela boa, e um teste que só espera a janela aprova um app inerte —
  o mesmo defeito que a bateria golden evita com o `controle`. A régua é o log
  de trace que o **próprio app** escreve: 3 teclas `Down` têm de virar 3
  `MainForm.lista_equiposChange`. E o alvo é a árvore **instalada**, não o
  `wte/build/wte` — medir o `build/` mediria justamente o caso especial que a
  WTE-TASK-39 acabou de consertar.

  A condição 2 saiu mais forte do que o enunciado pedia: em vez de um
  subconjunto, a bateria **inteira** foi refeita (96 corridas, 1,9 h), e os 96
  vereditos vieram **idênticos** aos da WTE-TASK-34 — só data e segundos
  mudaram. Isso é a resposta medida à pergunta que a task fazia (*as tasks 36 a
  39 regrediram alguma coisa?*): a 36 não tocou em Pascal nenhum (foi
  inventário e medição), e a 39 tocou em arranque e resolução de caminho, que é
  exatamente o que uma bateria completa exercita 96 vezes.

- **Arquivos criados/modificados:**
  - `wte/tools/sem_wine.sh` — **novo**; o ambiente sem Wine e sem 32 bits
  - `wte/tools/nativo_check.sh` — **novo**; as sete medidas da condição 3
  - `wte/re/nativo.md`, `wte/re/nativo.tsv` — **novos**; a evidência da condição 3
  - `wte/re/golden.tsv` — as 96 corridas refeitas (vereditos idênticos)
  - `wte/re/golden.md` — regerado pelo `check_golden.py`
  - `wte/tools/README.md` — as duas ferramentas novas na tabela
  - `wte/README.md` — a seção *"O que este projeto pode afirmar"* e o `Estado`
  - `docs/PLAN-WTE-LAZARUS.md` — a §11 inteira, e a linha de estado do
    cabeçalho, que ainda dizia *"plano; nenhuma fase executada"* com 39 tasks
    concluídas
  - `docs/tasks/progresso.md` — a linha da tabela e os cinco itens da fase 7
  - este arquivo

- **Problemas encontrados:**

  1. **A linha de estado do plano era prosa vencida.** O cabeçalho do
     `PLAN-WTE-LAZARUS.md` dizia *"Estado: plano; nenhuma fase executada"* —
     escrito em 2026-08-05 e nunca tocado, com 39 tasks fechadas desde então.
     É o defeito que a WTE-TASK-31 batizou, no documento que é a fonte de
     verdade do projeto. Corrigido com a nota do que ele dizia antes.
  2. **A numeração das correções tem um buraco, e ele é declarado.** São
     **117** correções, não 118: o `CORR-WTE-033` foi pulado na numeração (a
     revisão da WTE-TASK-15 abriu 030, 032, 034 e 035). O primeiro rascunho
     desta task escreveu 118 lendo o número mais alto; a contagem correta veio
     de `ls docs/tasks/CORR-WTE-*.md | wc -l`, que é o hábito que o prompt
     cobra — todo número vem de ferramenta, inclusive os que parecem óbvios.
  3. **Nada mais.** A bateria não teve uma corrida vermelha, e os dois scripts
     novos funcionaram na primeira medição.

---

## Achado que já espera a condição 3 (WTE-TASK-38, 2026-08-25)

**A condição 3 reprova hoje, e a causa não é Wine nem 32 bits.** O binário
copiado para fora de `wte/build/` não abre: morre num diálogo da LCL — `File
not found. / Press OK to ignore and risk data corruption. / Press Abort to kill
the program.` — antes de qualquer janela.

A causa medida é o log de trace: `ResolveArquivo` em
[`wte/src/retrace.pas`](../../wte/src/retrace.pas) resolve
`<dir do executável>/../re/trace.log` quando `WTE_TRACE_FILE` não está
definida, e o `Rewrite` levanta `EInOutError` porque o diretório não existe.
Controle: com o binário em `<algum>/sub/wte`, criar `<algum>/re/` — o `re/` é
irmão **do diretório** do binário, não do arquivo —, e o mesmo binário abre a
janela principal (522×475). Ou, sem diretório nenhum,
`WTE_TRACE_FILE=/tmp/trace.log ./wte`. *(Corrigido pela
[CORR-WTE-116](/docs/tasks/CORR-WTE-116.md) em 2026-08-25; a receita anterior
punha o `re/` irmão do **arquivo**, e assim não reproduz.)*

Quem conserta é a [WTE-TASK-39](/docs/tasks/39-empacotamento.md), que é dona da
resolução em runtime — a linha está lá. Aqui fica o registro de que **"roda num
ambiente sem Wine" e "funciona depois de movida" são conferências diferentes**,
e a segunda tem um defeito conhecido esperando por ela: reconferir a de mover
com o binário *instalado*, não com o de `build/`.

**Consertado em 2026-08-26 pela WTE-TASK-39**, e a metade de "movida" está
medida: `make -C wte install PREFIX=<p>`, `mv <p> <outro>`, e o binário
instalado abriu, achou os assets no caminho novo e carregou um time da imagem
japonesa. A regra passou a viver no
[`wte/src/wte_datafiles.pas`](../../wte/src/wte_datafiles.pas), e ela cobre
assets **e** trace.

**O que esta task ainda deve, e é a outra metade:** rodar num ambiente **sem
Wine**. A conferência de 2026-08-26 foi nesta máquina, que tem Wine instalado
para o oráculo — ela prova que o app **não usa** Wine (é ELF nativo, e o `ldd`
não mostra nada de Wine), não que ele rode onde Wine não existe. As duas
afirmações são diferentes, e só a segunda fecha a condição 3.

> **Resolvido nesta task, em 2026-08-26.** A ausência de Wine foi **fabricada**
> em vez de esperada: o [`sem_wine.sh`](../../wte/tools/sem_wine.sh) cobre com
> `tmpfs` vazio o runner do Bottles — que **é** o Wine desta máquina, já que
> não há pacote no apt —, o `/var/lib/flatpak`, os dois `work/wineprefix*` e o
> stack `i386`, e **recusa** se algum desses alvos não ficar vazio lá dentro
> (a cláusula que trabalha nesta máquina) ou se `wine`/`wine64`/`wineserver`/
> `winecfg` responderem no `PATH`. As
> sete medidas do [`nativo_check.sh`](../../wte/tools/nativo_check.sh) deram
> `ok` sobre a árvore **instalada**; o registro está em
> [`wte/re/nativo.md`](../../wte/re/nativo.md).
