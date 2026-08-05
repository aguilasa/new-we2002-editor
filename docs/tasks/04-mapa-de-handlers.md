---
id: WTE-TASK-04
title: "published_methods.tsv — os 96 handlers, com dono"
type: extração
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-02"]
status: concluído
---

# WTE-TASK-04: Mapa de handlers

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §1.4 e Fase 1 item 2.
- A *published method table* do VMT sobreviveu ao `/STRIP`. Varrendo `.data`
  saem **96** pares nome↔endereço. Isso é o mapa de funções do projeto: em RE
  normal, descobrir 96 nomes de função custa dias.

Formato de cada entrada: `word` tamanho, `dword` endereço, `byte` tamanho do
nome, nome. O protótipo já achou os 96 e ordenou por endereço.

---

## Objetivo

`wte/re/published_methods.tsv` completo e **com a coluna que falta: a que
formulário cada handler pertence**.

### Por que o dono importa

Há colisão de nome — `FormCreate` aparece 17 vezes, `BitBtn1Click` duas,
`SpeedButton1Click` três. Sem o dono, "implementar `FormCreate`" é ambíguo, e a
Fase 2 precisa gerar o stub na unidade certa.

O dono sai do VMT que contém a tabela: cada tabela pertence a uma classe, e o
nome da classe está no próprio VMT. Alternativa, se o VMT resistir: cruzar com
o `OnClick = '<nome>'` dos DFM da WTE-TASK-03 — o DFM diz qual formulário
referencia qual handler.

**Cruzar as duas fontes e reportar discordância** é melhor que escolher uma: um
handler declarado no VMT e não referenciado por nenhum DFM é código morto ou
ligado em runtime, e vale saber qual.

### Colunas

| Coluna | Origem |
|---|---|
| `endereco` | tabela do VMT |
| `handler` | tabela do VMT |
| `formulario` | VMT, conferido contra o DFM |
| `componente` | DFM (`OnClick` de quem) |
| `evento` | DFM (`OnClick`, `OnChange`, `OnMouseDown`, …) |
| `grupo` | classificação manual: carga / edição / gravação / auxiliar |

A coluna `grupo` é o que ordena as tasks 25 a 28.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_published.py` | criar |
| `wte/re/published_methods.tsv` | criar |

---

## Critério de conclusão

- [x] Os 96 com endereço, ordenados
- [x] Coluna `formulario` preenchida para todos
- [x] VMT e DFM cruzados; discordância listada, não escondida
- [x] Handler sem referência em DFM identificado e anotado
- [x] `grupo` atribuído aos 96
- [x] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-05

- **Resumo do que foi feito:**

  `wte/tools/dump_published.py` percorre os VMTs de `.data` do
  `we-team-editor.exe`, lê a *published method table* de cada um e cruza o
  resultado com os 18 `.dfm` da WTE-TASK-03. Saída em
  `wte/re/published_methods.tsv` (96 registros) e
  `wte/re/published_methods.md` (a leitura). Python 3 stdlib pura, `--check`
  no contrato dos irmãos, determinístico.

  **Medido: 96 métodos publicados** em 17 dos 18 formulários — bate com a
  §1.4. Os VMTs são achados pelo auto-ponteiro (`vmtSelfPtr`, −76): a
  assinatura casa 19 vezes em `.data`, uma é rejeitada por ter `vmtClassName`
  nulo, e sobram 18 — um por `.dfm`, sem sobra dos dois lados. Essa bijeção é
  o fechamento que substitui confiar na varredura, e o script aborta se ela
  deixar de valer.

  **O dono sai do VMT** (`vmtClassName`, −44), que é fonte autoritativa e
  cobre inclusive o handler que nenhum DFM cita. O DFM entra como conferência
  e como origem de `componente`/`evento`: 219 ligações `On<Evento> = <handler>`
  que se reduzem a 95 pares (formulário, handler), todos entre os 96 do VMT.
  **Zero discordâncias de dono.** Um handler publicado sem referência em DFM:
  `Button2Click` (`MainForm`, `0x0040c9c4`), anotado na coluna `nota`.

  A coluna `grupo` saiu de **oito regras ordenadas mais uma tabela de nove
  exceções**, ambas no topo do script, com a regra que decidiu cada linha
  registrada na coluna `regra` — a tarefa a chamava de "classificação manual",
  mas saída de gerador tem de ser reproduzível e coberta pelo `--check`.
  Distribuição: carga 28, edição 44, gravação 6, auxiliar 18. Os dez handlers
  já interpretados na §1.4 caem todos onde a leitura dela manda.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/tools/dump_published.py` | criado |
  | `wte/re/published_methods.tsv` | criado (gerado) |
  | `wte/re/published_methods.md` | criado (gerado) |
  | `/docs/tasks/04-mapa-de-handlers.md` | este log |

  `wte/re/published_methods.md` não estava previsto na tabela da tarefa. Ele
  é gerado e coberto pelo `--check`, como o `censo.md` da WTE-TASK-03 e o
  `offsets.md` da WTE-TASK-06.

- **Problemas encontrados:**

  Nenhum bloqueio. Sete divergências entre texto já escrito e medida, todas
  detalhadas em `wte/re/published_methods.md`:

  1. §1.4 do plano e esta tarefa dizem `FormCreate` **17** vezes — são **16**
     (`ficha_error` e `ficha_error2` não têm).
  2. Esta tarefa diz `BitBtn1Click` **duas** — são **quatro**.
  3. A WTE-TASK-25 diz `FormCreate`/`FormShow` em **19 endereços** — são
     **18** (16 + 2).
  4. A §5.1 do plano dá `etiqprecioClick` ao formulário
     `ficha_creditos_equipo` — o dono é **`jugador`**, e
     `ficha_creditos_equipo` publica só `FormCreate`.
  5. A WTE-TASK-28 dá `malla1MouseDown`/`malla2MouseDown` a `ficha_color` e
     `ficha_creditos_equipo` — o dono é **`estrategia`**.
  6. A WTE-TASK-28 lista `botonClick` entre os "handlers repetidos por vários
     formulários" — ele aparece **uma vez**, em `ficha_color`.
  7. A WTE-TASK-28 se chama "os 13 diálogos" mas enumera **15** formulários
     `ficha_*`. Os 13 são as unidades exportadas (§1.3); `ficha_color` e
     `ficha_error` são telas grandes e ficam de fora delas. A regra R6 da
     classificação usa os 13, medidos da `.edata`.

  Duas observações que não são correção: `ficha_error2` não publica método
  nenhum (`vmtMethodTable` = 0) e o `.dfm` dele não tem uma ligação de evento
  sequer — é o único nessa situação; e a tabela de exportação do `.exe`
  repete nome (79 entradas, 46 distintas), o que obriga a deduplicar antes de
  contar as 13 unidades.

  Pendente para o thread principal: a tabela de `wte/tools/README.md` não tem
  linha para a WTE-TASK-04. Falta acrescentar
  `| dump_published.py ✅ | 04 | VMT + DFM → os 96 handlers, com dono |`
  entre as linhas da 03 e da 06.
