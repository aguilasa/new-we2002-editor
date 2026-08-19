---
id: WTE-TASK-33
title: "Contador de slots livres de Master League"
type: implementação
category: features
phase: 5
depends_on: ["WTE-TASK-20"]
status: concluído
---

# WTE-TASK-33: Slots livres de ML

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §5.4.
- **A menor das quatro features**, e a que depende só da Fase 3. Pode ser feita
  a qualquer momento depois da camada de dados.

O readme do original descreve a gestão de Master League como o carro-chefe da
v0.95: "as long as there is free space in the game, u can insert and edit new
Master League players". O contador na tela é o que torna isso utilizável.

---

## Objetivo

Varrer a região de ML, contar vagas, e mostrar.

### O que precisa ser respondido

1. **O que é um slot vazio.** Byte zero? Nome em branco? Marcador próprio?
   Descobrir e escrever — é a definição inteira da feature.
2. **Qual é a região.** `OFS_LINK_ML` está entre os 19 offsets confirmados, e
   `OFS_ML_TEAM_NAME_7`/`_8` também. A WTE-TASK-19 deve ter fechado o resto.
3. **Quantos slots existem no total.** Número fixo do formato.

### A armadilha herdada

O `newWe2002` documenta uma faixa de 16 bytes que o `ed.exe` lê e grava por
engano a partir de memória vizinha — **o slot 64 de um array de 63**
(`OFS_SQUAD_NUMBERS_NATIONAL+1008`, `405724..405739`). É a única divergência
aceita nos golden tests do port Qt.

Contar slots é exatamente a operação onde esse tipo de erro nasce. **Medir o
limite do array, não estimá-lo**, e conferir se o Obocaman comete o mesmo erro
que o Moriero — se cometer, é decisão registrada (reproduzir ou corrigir), não
descuido.

### Verificação

Contar nas duas ROMs e conferir contra o número que o original mostra na tela.
Depois inserir um jogador pelo original, recontar dos dois lados, e ver se
decrementam junto.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/ml-slots.md` | criar — **gerado** |
| `wte/re/ml-slots.tsv`, `wte/re/ml-slots-medido.tsv` | criar — gerado / medido |
| `wte/tools/conta_ml.py`, `wte/tools/test_conta_ml.py` | criar |
| `wte/src/we2002_ml.pas` | criar |
| `wte/src/we2002_ml_tabela.inc` | criar — **gerado** |
| `wte/tests/test_ml.pas` | criar |

*(2026-08-19)* O enunciado pedia `wte/re/spec/ml-slots.md`. **Não pode ser
ali:** o `spec_index.py` da WTE-TASK-23 reprova como órfão qualquer `.md` de
`wte/re/spec/` que não case com um dos 96 handlers publicados, e `ml-slots` não
é handler. Foi para `wte/re/`, ao lado de `zonas.md` e `formacoes.md`, que é
onde moram os achados que não são de handler.

---

## Critério de conclusão

- [x] **Definição de "slot vazio" escrita, com evidência.** Bloco livre é um
      índice de jogador *non-contract* que nenhum par de vínculo de Master
      League reivindica — **não** é byte zero nem nome em branco. Duas fontes
      independentes: o `Hint` do próprio controle (`Free blocks for new Master
      League players`, no DFM) e o `PLAYERS_NC = 462` do `we2002_core`
- [x] **Região e total de slots medidos, não estimados.** Região: 760 pares a
      partir de `OFS_LINK_ML`, lidos pelo fluxo. Total: **462**, que é o
      imediato de `0x004042f1` **e** a soma dos 120 valores da tabela de
      `0x00423424` — as duas leituras fecham, e o gerador recusa se pararem de
      fechar
- [x] **Contagem batendo com a tela do original nas duas ROMs.** Europeia:
      `13` no oráculo, `13` no port, `13` na ferramenta. Japonesa: `1` nos dois
      lados **com o mesmo conteúdo de arquivo** — ver a ressalva abaixo, que é
      achado, não falha
- [ ] ~~Decrementa junto com o original após inserção~~ — **não medido, e o
      motivo é de outra task.** Inserir jogador em clube de ML é o ramo de
      destino de ML da `0x00404820`, que a
      [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) declarou lacuna
      **esperando esta task**. Agora que o contador existe, o ramo pode ser
      escrito, e é lá que este critério fecha: o par inserir-e-recontar exercita
      código que ainda não existe nos dois lados
- [x] **Conferido se há leitura fora do array, e a decisão registrada.** Há, e
      é grave: o vetor de ocupação tem 462 palavras e o `memset` de
      `0x004042dd` limpa 462 **bytes** — 231 palavras, metade. E o índice pode
      passar de 461, e aí o `inc` de `0x0040435d` escreve em variável vizinha.
      **Decisão: não reproduzir.** O port dimensiona o vetor para toda a faixa
      alcançável e o zera inteiro; o número na tela sai igual e nada vizinho é
      atingido. Divergência deliberada, para a WTE-TASK-35
- [x] Commit no formato conventional, em inglês

### O que a conferência de tela revelou de quebra

O oráculo mostra `1` e o port mostra `2` na japonesa — e **não é a contagem**.
O oráculo **altera a imagem ao abri-la**: troca o par de vínculo em `2012984`
de `(102, 23)` para `(0, 27)`, e essa troca custa um bloco livre. Dado ao port
o arquivo que o oráculo produziu, os dois mostram `1`.

Essa escrita já estava registrada — a spec do `boton_dialogo_weClick` a lista
desde a WTE-TASK-25 entre as *duas faixas do arranque sem explicação*
(`1921862..1921862` e `2012984..2012985`), declaradas `conhecida:` no roteiro
do gate. O que esta task acrescenta é o **significado** da segunda. Quem a
escreve continua sem nome: a única referência absoluta a `OFS_LINK_ML` em toda
a `.text` é o `push 0x1eb608` desta rotina, que só lê.

### E a causa do travamento da ROM europeia, que estava em aberto

O [`crash-causa.md`](../../wte/re/crash-causa.md) mediu `0x004335e4`,
`0x00433624` e `0x00433628` mudando de `0x0` para `0x00010001` com a europeia e
não com a japonesa, e encerrou dizendo que nomear a instrução exigiria um
watchpoint de hardware que esta máquina não permite. **A instrução é o
`inc WORD PTR [eax*2+0x433224]` de `0x0040435d`**, desta rotina, e a condição é
vínculo apontando para time sem NC nenhum: os índices 480, 512 e 514 caem
exatamente naqueles três endereços. A mesma medição traz a confirmação
numérica de graça — ela leu o contador em `0x0000000d`, que é **13**, o mesmo
que esta task calcula e o mesmo que o rótulo mostra.

## Log de Execução

- **Executado em:** 2026-08-19

- **Resumo do que foi feito:**
  - Recuperada a `0x004042d4` inteira do disassembly, com as duas auxiliares
    (`0x0040423c`, o índice linear; `0x0040427c`, o inverso) e os dois
    chamadores (`MainForm.FormShow` em `0x004116df` e
    `MainForm.boton_dialogo_weClick` em `0x0040c241`, os dois seguidos de
    `casilla_xmlibres.Caption := IntToStr(WORD[0x004335c0])`).
  - **A tabela de `0x00423424` é a mesma do `we2002_core`, noutra
    codificação.** O `wte.exe` guarda quantos NC cada time tem e soma o prefixo
    a cada chamada; o `ed.exe` guarda o prefixo pronto em `START_LINK[]`, e a
    fórmula do `ResolveMlLink` (`slot + START_LINK[team] - 23`) é letra por
    letra a `0x0040423c`. Concordam em todos os 50 times que têm algum NC; onde
    divergem, a contagem é zero e nenhum vínculo válido endereça. Isso é
    checagem cruzada entre os dois oráculos de graça, e o gerador a executa.
  - Port em `we2002_ml.pas`, com a tabela num include gerado; ligado nos dois
    lugares em que o original conta.
  - Conferência de tela nos dois lados, nas duas ROMs — e foi ela que expôs a
    escrita de `2012984` (ver acima).

- **Arquivos criados/modificados:**
  - criados: `wte/tools/conta_ml.py`, `wte/tools/test_conta_ml.py`,
    `wte/src/we2002_ml.pas`, `wte/src/we2002_ml_tabela.inc` (gerado),
    `wte/tests/test_ml.pas`, `wte/re/ml-slots.md` (gerado),
    `wte/re/ml-slots.tsv` (gerado), `wte/re/ml-slots-medido.tsv` (medido)
  - modificados: `wte/src/impl/ep2002_mainform.aux.inc`,
    `ep2002_mainform.FormShow.inc`, `ep2002_mainform.boton_dialogo_weClick.inc`,
    `ep2002_mainform.uses`, `wte/src/ep2002_mainform.pas` (regerado),
    `wte/re/spec/MainForm.FormShow.md`,
    `wte/re/spec/MainForm.boton_dialogo_weClick.md`, `wte/re/fase-2.md`
    (regerado), `docs/PLAN-WTE-LAZARUS.md` §4.4 (fração medida),
    `wte/tools/README.md`, `wte/tests/README.md`, `docs/prompts/01-executar.md`

- **Problemas encontrados:**
  - **A primeira contagem deu 23 e estava errada**, por uma razão que não
    apareceu em nenhum teste: o rascunho leu só 63 entradas da tabela, e o
    `TAB[:b0]` do Python devolve a lista inteira para `b0 >= 63` em vez de
    estourar. Todos os clubes de ML colapsavam num prefixo só, e blocos
    distintos viravam o mesmo. São **120** entradas, e a soma delas é que fecha
    em 462. Fatiamento de lista fora do fim é silencioso em Python, como
    `[^x]` casa `\n` em regex.
  - **`b0 >= 120` não é modelado, e ficou escrito assim.** Ali o original soma
    além do fim da tabela e o resultado depende do que a `.data` guarda depois
    dela. Nenhuma das duas ROMs chega lá — o maior `b0` medido é 43 —, e
    inventar uma regra produziria número plausível sem nada que o sustente.
  - **A conferência de tela quase virou "bug do port".** Oráculo `1`, port `2`,
    mesma ROM de origem: parecia erro de contagem. Era o oráculo escrevendo na
    própria cópia ao abrir. O que desfez foi dar ao port o **arquivo que o
    oráculo produziu** — regra velha deste repositório, e continua valendo:
    comparar número, não procedência.
  - `spec_index.py` reprova `.md` órfão em `wte/re/spec/`; o enunciado pedia o
    documento ali. Corrigido no enunciado, com o motivo.
