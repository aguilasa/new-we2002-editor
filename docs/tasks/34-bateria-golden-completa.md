---
id: WTE-TASK-34
title: "Bateria golden completa — toda gravação, nas duas ROMs"
type: verificação
category: verificação
phase: 6
depends_on: ["WTE-TASK-31", "WTE-TASK-32", "WTE-TASK-33"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md Fase 6 item 1 e §0 (definição de pronto, item 2)"
status: concluído
---

# WTE-TASK-34: Bateria golden completa

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 6 item 1 e §0 (definição de
  pronto, item 2).

> Para cada operação que grava, `wte.exe` sob Wine e o app Lazarus produzem
> **imagem byte-idêntica** a partir da mesma imagem de entrada, nas duas ROMs.

As tasks 27, 31 e 32 rodaram golden **por operação**, isoladas. Esta roda a
bateria inteira, e é onde interação entre operações aparece.

---

## Objetivo

Uma bateria versionada, reproduzível, com resultado registrado.

### O que a bateria cobre

| Categoria | Origem |
|---|---|
| as quatro gravações sem fórmula | WTE-TASK-27 |
| import de `.mcr` para a imagem | WTE-TASK-28 |
| gravação de camisa e bandeira | WTE-TASK-29 |
| edição + gravação combinadas | novo |
| gravar duas vezes seguidas | novo |

### As duas combinações que só aparecem aqui

**Edição múltipla antes de gravar.** Cada operação isolada passou; várias na
mesma sessão podem não passar, se o original recalcular algo ao trocar de
contexto. É a classe de bug que teste isolado não pega.

**Gravar duas vezes.** O `newWe2002` registra que o **`ed.exe`** não é
idempotente — `Load`+`Save` troca os dois primeiros cobradores de cada clube de
ML, e gravar duas vezes volta ao início. Se o app Lazarus não reproduzir esse
vaivém, a segunda gravação diverge mesmo com a primeira idêntica.

> **Medido depois, e a resposta é não.** A [CORR-WTE-104](/docs/tasks/CORR-WTE-104.md)
> mediu o terceiro ponto num time onde a troca seria visível: uma gravação e
> duas dão a **mesma** imagem, e os cobradores saem intactos. O `wte.exe` não
> tem o vaivém — é resultado negativo, registrado em
> [`golden.md`](../../wte/re/golden.md).

### Custo

Cada rodada usa duas cópias de ~474 MB. A bateria inteira, com N operações e
duas ROMs, é 2N cópias — planejar espaço, e limpar entre rodadas. **Não roda em
CI**, e o plano já registra isso.

### Registro

Uma tabela: operação × ROM × resultado. Divergência vai para a WTE-TASK-35, não
fica na tabela como nota de rodapé.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/golden_suite.sh` | criar — a bateria versionada |
| `wte/tools/check_golden.py` | criar — o gerador do `golden.md`, com `--check` |
| `wte/re/golden.tsv` | criar — o registro cru, escrito pela bateria |
| `wte/re/golden.md` | criar — a tabela operação × ROM × resultado |
| `wte/tests/roteiros/golden-23-multiplas-edicoes{,.port}.txt` | criar |
| `wte/tests/roteiros/golden-24-gravacao-dupla{,.port}.txt` | criar |
| `wte/tools/roteiro.sh` | modificar — pular as três chaves novas de cabeçalho |
| os seis roteiros com receita em comentário | modificar — a receita vira chave |

*Adaptado na execução (2026-08-24).* O enunciado listava dois arquivos, e a
regra do repositório pede três por saída gerada — **o gerador, o `--check` e a
saída**. Daí o `check_golden.py` e a separação `golden.tsv` (cru, escrito pela
corrida) / `golden.md` (gerado, conferido pelo `make -C wte check`).

Os dois roteiros novos são as duas combinações que o próprio enunciado nomeia e
que não existiam em disco; sem eles não haveria o que rodar. E as chaves de
cabeçalho vieram da lição que a WTE-TASK-31 deixou escrita: a receita de
invocação de cada roteiro — que fixture criar, que artefato comparar, que
variável exportar — morava em **comentário**, e comentário não é lido por
ferramenta nenhuma.

---

## Critério de conclusão

- [x] Toda operação de gravação na bateria, nas duas ROMs — **92 corridas,
      23 roteiros × 2 ROMs × 2 modos**, registro em
      [`wte/re/golden.tsv`](../../wte/re/golden.tsv). Na japonesa, **46 de 46
      `PASSOU`**. Na europeia, **2 `PASSOU`, 22 `SEM_ORACULO`, 22
      `NAO_APLICAVEL`, e zero `REPROVOU`** — ver o critério seguinte e a
      ressalva abaixo
- [x] Edição múltipla antes de gravar coberta —
      [`golden-23-multiplas-edicoes`](../../wte/tests/roteiros/golden-23-multiplas-edicoes.txt),
      controle 143 s / golden 134 s na japonesa
- [x] Gravação dupla coberta —
      [`golden-24-gravacao-dupla`](../../wte/tests/roteiros/golden-24-gravacao-dupla.txt),
      controle 157 s / golden 145 s. **A segunda metade do critério não foi
      provada, e está registrada como pendência abaixo:** o roteiro prova que
      os dois lados chegam ao mesmo byte depois de duas gravações de tática —
      que é a gravação que carrega `OFS_KICKER` —, mas **não** prova que existe
      vaivém de cobradores neste editor. A não-idempotência de que o enunciado
      fala é do `ed.exe` (`Load`+`Save` em clubes de ML), e o `wte.exe` do
      Obocaman é outro binário e outro caminho de código
- [x] Tabela de resultado completa, sem célula vazia —
      [`wte/re/golden.md`](../../wte/re/golden.md), 23 linhas × 2 ROMs. A
      guarda 2 do `check_golden.py` **aborta** se um roteiro com par em disco
      ficar fora do TSV
- [x] Temporário limpo; `roms/` intocada — cada corrida faz duas cópias em
      `work/` e as apaga; 6.448 s de relógio no total
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-24 *(a bateria fechou na madrugada de 25)*

- **Resumo do que foi feito:**

  A bateria virou ferramenta: [`golden_suite.sh`](../../wte/tools/golden_suite.sh)
  roda a lista inteira, e [`check_golden.py`](../../wte/tools/check_golden.py)
  publica [`golden.md`](../../wte/re/golden.md) a partir do
  [`golden.tsv`](../../wte/re/golden.tsv) que ela escreve. Até aqui a bateria
  era o `golden_check.sh` mais um operador — 42 invocações à mão e o resultado
  transcrito depois. Duas coisas não sobrevivem a esse arranjo: a reprodução (a
  próxima pessoa não sabe a lista nem a ordem) e a fixture (o operador aponta
  para o que estiver em `work/`).

  **Resultado: 92 corridas, 48 `PASSOU`, 22 `SEM_ORACULO`, 22 `NAO_APLICAVEL`,
  e zero `REPROVOU`.** A japonesa fechou 46 de 46, incluindo os dois roteiros
  novos que a fase 6 acrescenta.

  **O achado que muda uma leitura do projeto: a europeia hospeda o oráculo — só
  não para quem troca de time.** O `golden-01-arranque` passou controle **e**
  golden ali, byte-idêntico. A leitura em bloco que o projeto carregava desde
  2026-08-18 — *"a europeia não hospeda o oráculo"* — tinha sido medida sobre
  **um** roteiro, e aquele roteiro trocava de time. O recorte certo é mecânico e
  já estava no [`crash-causa.md`](../../wte/re/crash-causa.md): sem a troca, a
  carga não escreve além do fim da tabela de `0x00433580`, o ponteiro de
  `dorsal1` não vira `0x00010001`, e o `wte.exe` não cai. Vinte e dois dos vinte
  e três roteiros trocam de time, então a conclusão prática não muda — mas ela
  passou a ser **medida roteiro a roteiro** em vez de dispensada em atacado, e é
  isso que o critério "nas duas ROMs" pedia.

- **Problemas encontrados:**

  **O gate classificava travamento do oráculo como divergência do port, e a
  correção é da fase 4 achada pela fase 6.** O
  [`golden_run_wte.sh`](../../wte/tools/golden_run_wte.sh) varre o log do Wine
  atrás de `c0000005` **depois** de executar o roteiro. Sob `set -e`, um roteiro
  que não consegue dirigir devolve 1 e aborta o script **antes** da varredura —
  e na europeia é exatamente o que acontece: o oráculo trava ao trocar de time e
  o diálogo do passo seguinte nunca aparece.

  O efeito é uma **inversão de acusação**. O gate saía com código genérico, a
  bateria classificava `REPROVOU` — a única palavra do vocabulário que acusa o
  **port** —, e o port sequer tinha sido comparado. Parei a bateria em 50/92
  para não acumular mais 44 linhas afirmando divergência onde não houve medição.

  A causa foi confirmada com número antes de qualquer correção: reproduzida a
  corrida com `--manter`, o log tinha **49.749 violações de acesso**, o valor
  exato que o `crash-causa.md` registra. A falha de condução é sintoma.

  A correção inverte a ordem das duas conferências, e a razão cabe numa frase:
  **é justamente quando o roteiro falha que a pergunta "o oráculo morreu?" mais
  importa.** Log sujo → `exit 4` → `SEM_ORACULO`. Log limpo → propaga a falha,
  dizendo explicitamente que *não* é o travamento conhecido, então é coordenada,
  tempo ou janela. Recusa vista nos dois sentidos: a mesma corrida que dava
  `REPROVOU` passou a dar `codigo=4`.

  **Nenhum verde já registrado depende do defeito.** Com a japonesa o roteiro
  sempre dirige até o fim, então a varredura sempre foi alcançada; o ponto cego
  só existia no caminho em que o oráculo morre, e nesse caminho nunca houve
  verde.

  **Duas armadilhas menores, as duas da família "estado achado em vez de
  declarado".** As variáveis de `ambiente:` vazavam entre roteiros — a bateria
  roda todos no mesmo shell, e um `WTE_MCR_ENTRADA` esquecido faria o port
  importar um cartão no arranque de um roteiro que não pediu nenhum, produzindo
  um `REPROVOU` que acusaria o port por um estímulo que o roteiro não tem. E o
  guarda de cobertura do `check_fase4.py` supunha **uma** bateria: exigir os
  roteiros da fase 6 no registro da fase 4 faria aquele registro crescer toda
  vez que uma fase posterior escrevesse um roteiro, e a data daquela corrida
  passaria a mentir.

- **O que ficou pendente:** *(resolvido em 2026-08-25 — ver abaixo)*

  **O vaivém dos cobradores não foi provado, só coberto.** Encaminhado para a
  [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md), que é quem registra
  divergência deliberada com evidência. O que falta é o terceiro ponto da lição 1
  da quarta passagem da [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md):
  comparar a imagem depois de **uma** gravação de tática com a de **duas**. Se
  não diferirem, o `wte.exe` é idempotente nesse caminho e não há vaivém que
  reproduzir — resultado negativo legítimo, e que precisa ficar escrito, porque
  hoje o enunciado da fase 6 afirma um comportamento herdado de outro binário.

  > **Resolvido pela [CORR-WTE-104](/docs/tasks/CORR-WTE-104.md), em
  > 2026-08-25.** E a pendência estava pior do que este parágrafo sabia: o
  > roteiro gravava no time 2, cujos dois primeiros cobradores são iguais, de
  > modo que a comparação **não podia** dar resposta. Movido para o time 5 e
  > medido, o terceiro ponto fecha em **0 bytes** entre uma gravação e duas,
  > com os cobradores intactos nos três estados — **resultado negativo**. Está
  > escrito em [`golden.md`](../../wte/re/golden.md), como este parágrafo pedia.

- **Arquivos criados/modificados:** ver `git show --stat`. Criados:
  `wte/tools/golden_suite.sh`, `wte/tools/check_golden.py`,
  `wte/tools/test_check_golden.py`, `wte/re/golden.tsv`, `wte/re/golden.md`, e
  os dois pares de roteiro `golden-23`/`golden-24`. Modificados:
  `wte/tools/golden_run_wte.sh` (a ordem das conferências),
  `wte/tools/roteiro.sh` (as três chaves novas de cabeçalho),
  `wte/tools/check_fase4.py` e o gerado `wte/re/fase-4.md` (o guarda de
  cobertura e a contagem de roteiros), os seis roteiros que ganharam chave de
  cabeçalho, `docs/PLAN-WTE-LAZARUS.md`, `docs/tasks/progresso.md`; este
  arquivo.
