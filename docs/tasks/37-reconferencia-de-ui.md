---
id: WTE-TASK-37
title: "Reconferência dos 18 formulários, com a lógica ligada"
type: verificação
category: ui
phase: 6
depends_on: ["WTE-TASK-34"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md Fase 6 item 4"
status: concluído
---

# WTE-TASK-37: Reconferência de UI

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 6 item 4.
- A WTE-TASK-12 conferiu os formulários **vazios**. Este confere com dado
  carregado e com a lógica ligada — que é quando os problemas de verdade
  aparecem.

Diferenças que só existem agora: rótulo que cabia vazio e não cabe com o nome de
um time real; combo populado com 63 entradas em vez de nenhuma; imagem de camisa
desenhada por cima do que era espaço reservado; controle habilitado ou
desabilitado por estado.

---

## Objetivo

Passar pelos 18 de novo, com imagem carregada, e comparar com o original no
mesmo estado.

### Método

Mesmo da WTE-TASK-12 — captura dos dois lados no `:98`, inspeção humana, sem
tolerância de pixel — com uma diferença: **mesmo estado dos dois lados**. Abrir
a mesma ROM, selecionar o mesmo time, o mesmo jogador.

*(O enunciado dizia `:99`, e era o certo quando foi escrito: o display mudou
para o `:98` em 2026-08-20, a pedido do usuário. Corrigido aqui porque isto é
enunciado, não registro histórico.)*

### O que procurar agora

| Achado | Onde volta |
|---|---|
| rótulo cortado por dado real | decisão: aceitar ou alargar |
| controle habilitado/desabilitado errado | spec do handler (Fase 4) |
| ordem de itens em combo | carga (WTE-TASK-25) |
| imagem não desenhada ou desenhada errada | render (WTE-TASK-29) |
| foco inicial e ordem de tabulação | DFM (`TabOrder`) — o gerador preservou? |

### `TabOrder` e o botão default

O `newWe2002` levou uma mordida aqui: `PUSHBUTTON` do `.rc` precisou sair com
`autoDefault=false`, senão `Return` clicaria um botão arbitrário — e um dos
candidatos aplicava formação predefinida sobre o time selecionado.

O risco equivalente existe: `lista_formacionesClick` é destrutivo. Conferir o
que `Return` faz em cada formulário, nos dois lados.

### As 37 `TStaticText`

Reconferir a decisão da WTE-TASK-12 com fundo real desenhado atrás.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/visual.md` | modificar — segunda passada |
| `wte/re/visual/carregado/*.png` | criar |
| `wte/tools/roteiro.sh` | modificar — o verbo `! foto` |
| `wte/tools/captura_ui.sh` | criar — dirige os dois lados e fotografa |
| `wte/tools/check_carregado.py` | criar — alcance, tamanho, cor de fundo, rótulos |
| `wte/tools/check_retorno.py` | criar — `Default`, `Cancel` e ordem de tabulação |
| `wte/re/carregado.md`, `carregado.tsv` | criar — gerados |
| `wte/re/retorno.md`, `retorno.tsv` | criar — gerados |
| `wte/tests/roteiros/ui-0{1,2,3}-*.txt` | criar — os três pares de captura |
| `wte/tests/roteiros/golden-25-retorno.txt` | criar — o `Return` medido em bytes |

*(A tabela original listava só os dois primeiros. As capturas não se tiram sem
ferramenta, e número em documento tem de vir de ferramenta — os sete itens
acima são isso.)*

---

## Critério de conclusão

- [x] Os 18 reconferidos com a mesma ROM e o mesmo estado dos dois lados —
      **15 pares fotografados**, 1 só do oráculo (`ficha_warning`, que o port
      não levanta) e 2 de nenhum (`ficha_enlaza`, sem chamador; `ficha_info4`,
      que exige uma gravação de ML). Os três casos são **achado**, não lacuna
      de método, e estão medidos
- [x] `TabOrder` e comportamento de `Return` conferidos por formulário —
      142 controles com `TabOrder`, **0 formulários** com ordem diferente entre
      DFM e LFM; 13 com `Default`, 7 com `Cancel`
- [x] Nenhuma ação destrutiva alcançável por `Return` — **com uma ressalva
      medida**: o `OK` do `ficha_color` é `Default = True` desde o DFM de 2002 e
      grava 383 bytes por time. Isso é do original, e os dois lados gravam os
      **mesmos** bytes por esse caminho (roteiro `golden-25-retorno`,
      byte-idêntico). O risco que o enunciado nomeava — `lista_formacionesClick`
      — não existe: o `estrategia` não tem botão `Default`
- [x] Decisão das `TStaticText` reconferida com fundo real — de pé para 36 dos
      37; o 37º (`help_team`, desabilitado) diverge, e a causa não é
      transparência
- [x] Achado que volta para outra fase registrado com a task de destino —
      linhas escritas nas tasks [10](/docs/tasks/10-conversor-dfm-para-lfm.md),
      [19](/docs/tasks/19-os-50-offsets-restantes.md),
      [25](/docs/tasks/25-handlers-de-carga.md) e
      [35](/docs/tasks/35-divergencias-deliberadas.md), e a decisão do
      `ComboBoxDrawItem` na spec dele
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-25

- **Resumo do que foi feito:**

  Os 18 formulários reconferidos **com dado na tela**, e o que se aprendeu é que
  a primeira passada não podia ter achado o principal: ela mediu os **37
  `TStaticText`** que a §8.9 nomeia, e o problema mora nos **151 `TLabel`** que
  declaram `Color` pelo mesmo DFM. Medidos nos 15 pares, **68 de 178 rótulos**
  têm cor de fundo diferente entre os dois lados — sempre no mesmo sentido, o
  rótulo somindo no fundo do formulário. A causa é um *default* de widgetset
  sobre uma propriedade que o DFM não declara (`Transparent` nasce `False` no
  VCL e `True` na LCL), e por isso ela não aparece em nenhuma comparação de
  propriedade: os dois arquivos são iguais.

  **O `Return` deixou de ser prosa.** 13 formulários têm botão `Default`, 7 têm
  `Cancel`, e a ordem de tabulação é idêntica entre DFM e LFM nos 18 — a mordida
  que o `newWe2002` levou com `autoDefault` não se repete, porque no DFM
  `Default` é propriedade explícita. O que existe é outro: o `OK` do
  `ficha_color` é `Default = True` desde 2002 e grava 383 bytes por time. Como
  isso é do original, a pergunta virou "os dois lados gravam o mesmo?", e a
  resposta veio em **bytes**, não em captura: o roteiro `golden-25-retorno` é o
  `golden-16-cor` fechando o editor por tecla, e passa byte-idêntico.

  **Três formulários não foram fotografados, e os três são achado.** O
  `ficha_warning` o port não levanta (aplica os remendos de arranque sem
  perguntar); o `ficha_enlaza` não tem chamador nenhum em `wte/src/`; o
  `ficha_info4` exige uma gravação de Master League que o roteiro não faz.

- **Arquivos criados/modificados:** conferido contra `git show --stat`.

  Criados: `wte/tools/check_retorno.py`, `wte/tools/check_carregado.py`,
  `wte/tools/test_check_retorno.py`, `wte/tools/captura_ui.sh`;
  `wte/re/retorno.{md,tsv}` e `wte/re/carregado.{md,tsv}` (gerados);
  os três pares `wte/tests/roteiros/ui-0{1,2,3}-*.txt` e o par
  `golden-25-retorno`; **37 PNG** em `wte/re/visual/carregado/`.

  Modificados: `wte/tools/roteiro.sh` (o verbo `! foto`), `wte/re/visual.md`
  (a segunda passada), `wte/re/spec/estrategia.ComboBoxDrawItem.md` (a
  decisão), `wte/re/golden.tsv` e `wte/re/golden.md` (as 4 corridas novas),
  `wte/re/fase-4.md` (regerado: o roteiro novo mudou a contagem de roteiros em
  disco), `docs/PLAN-WTE-LAZARUS.md`, `docs/tasks/progresso.md`, este arquivo, e
  **os quatro repasses**: `docs/tasks/10-conversor-dfm-para-lfm.md`,
  `19-os-50-offsets-restantes.md`, `25-handlers-de-carga.md` e
  `35-divergencias-deliberadas.md`.

- **Problemas encontrados:**

  **1. O `--roteiro` do `golden_suite.sh` TRUNCA o TSV.** Rodar
  `golden_suite.sh --roteiro golden-25-retorno` sem `--retomar` reescreveu o
  `wte/re/golden.tsv` inteiro com as 4 corridas novas — as 92 da WTE-TASK-34
  sumiram, e quem avisou foi o `check_golden.py --check`, que passou a acusar
  23 roteiros "com par em disco e ausentes da bateria". Recuperado do
  `git show HEAD:` e concatenado. **O `--retomar` não era conveniência: sem ele,
  `--roteiro` não era filtro, era substituição.**

  > **Consertado em 2026-08-25 pela
  > [CORR-WTE-113](/docs/tasks/CORR-WTE-113.md)** — o item que este parágrafo
  > dizia valer a pena abrir. O truncamento passou a valer só para a bateria
  > **inteira**; corrida parcial (`--roteiro`, ou `--rom` diferente de `ambas`)
  > preserva o registro e **substitui** a linha do trio em vez de acrescentar.
  > Medido: 97 linhas entram, 97 saem. A decisão ficou guardada por seis casos
  > no `test_check_golden.py`, que recortam o bloco do script e o rodam sem
  > levantar o Wine.

  **2. Quatro roteiros de captura falharam antes de dar certo, e cada falha
  ensinou o estado.** O `ficha_movertodos` não abria porque a
  `MoveTodosOsJogadores` sai antes do modal quando os combos do painel de baixo
  estão sem seleção — e com time **nacional** (índice < 95) metade da tela está
  desabilitada. `End` no combo tampouco serve: o último item da lista é
  **vazio**, e selecioná-lo desabilita a tela inteira (a foto
  `MainForm-clube` da segunda corrida mostra isso). O que resolveu foi 96
  `Down`, que é como o `compara_tela.sh` já chegava ao time-modelo.

  **3. A moldura do Wine é 6×32 e é preciso saber disso para medir qualquer
  coisa.** Formulário que declara `ClientWidth` no DFM aparece 6 px mais largo e
  32 px mais alto no oráculo, porque o Wine desenha a moldura **por dentro** da
  janela X; sem window manager, a LCL não desenha nenhuma. Todo retângulo de
  controle sobre a captura do oráculo precisa de `+3,+29`, e o
  `check_carregado.py` **aborta** se uma captura não for nem o cliente nem o
  cliente mais a moldura — a alternativa era medir 3 px à esquerda do lugar e
  publicar o resultado.

  **4. O enunciado dizia `:99`.** Corrigido para `:98` no corpo da task: isto é
  enunciado, não registro histórico, e o display mudou em 2026-08-20.
