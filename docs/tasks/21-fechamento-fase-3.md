---
id: WTE-TASK-21
title: "Fechamento da fase 3 — a camada de dados é 100% gerada?"
type: fechamento
category: dados
phase: 3
depends_on: ["WTE-TASK-20"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md Fase 3, critério de pronto"
status: concluído
---

# WTE-TASK-21: Fechamento da fase 3

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 3, critério de pronto.
- O critério é duplo e o segundo é fácil de deixar passar: os valores têm de
  bater **e** o código que os produz tem de ser 100% saída de gerador.

Se a camada acabar meio gerada e meio escrita à mão, a tese da §4.5 caiu, e o
plano precisa dizer isso em vez de fingir que não.

---

## Objetivo

Aceitar a fase, ou nomear o que falta.

### Conferências

1. **Fração gerada.** Quantas linhas da camada de dados são saída de gerador e
   quantas foram escritas à mão nas recusas da WTE-TASK-18? Número medido.
2. **`--check` verde** para os três geradores, sobre a árvore commitada.
3. **Os dois dumps idênticos** nas duas ROMs.
4. **Ghidra ainda não foi usado.** A Fase 3 fecha sem decompilador — é o cenário
   bom que o plano prevê. Se o Ghidra foi necessário, registrar em quê: é sinal
   de que a Fase 4 vai custar mais que o estimado.

### A pergunta que fecha a fase

**O app já lê o jogo?** Não a camada isolada — o app. Se a camada compila mas
nenhum formulário a consome, a Fase 4 começa integrando, e isso é trabalho que
esta fase deveria ter deixado pronto.

Decidir e escrever: a integração mínima (abrir imagem pelo `TOpenDialog` do
`MainForm` e popular o combo de times) entra aqui ou na WTE-TASK-25.

### O que ainda não foi provado

Que **gravar** pela janela funciona. A fase 3 prova leitura e prova gravação
headless. A gravação dirigida pela tela é a WTE-TASK-22 em diante.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/check_fase3.py` | criar — o medidor; `wte/re/fase-3.md` é **gerado por outro script** |
| `wte/re/fase-3-fechamento.md` | criar (gerado) |
| `wte/tools/compare_dumps.py` | modificar — a seção "o que isto não mede" trocava duas populações de offset |
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§4.5, a fração medida) |
| `docs/tasks/progresso.md` | modificar |

---

## Critério de conclusão

- [x] Fração gerada medida e comparada com a tese da §4.5
      — **91,8%** por regra (3.389 de 3.692 linhas), medido pelo
      `check_fase3.py`; as 303 à mão são as quatro peças da rota 3.
      Publicado como 92,5% / 3.415 / 277 até a
      [CORR-WTE-051](/docs/tasks/CORR-WTE-051.md), que pôs a mesma régua
      (linha física) nos dois lados da subtração
- [x] `--check` dos três geradores verde sobre a árvore commitada
      — `gen_tables_pas`, `port_database_pas` e `compare_dumps`, mais o
      `check_fase3` novo; 394 testes, `make -C wte check` inteiro
- [x] Dumps idênticos nas duas ROMs
      — remedido nesta execução: 66.498 linhas, **0** divergência em cada ROM,
      round-trip Pascal × C++ **0** byte, e o `fase-3.tsv` saiu byte a byte
      igual ao commitado
- [x] Registrado se o Ghidra foi ou não necessário, e em quê
      — **não foi.** Zero citação nos cinco artefatos de medida da fase; a
      única no conjunto é uma negação explícita no `crash-causa.md`
- [x] Decidido onde entra a integração mínima com o `MainForm`
      — **na WTE-TASK-25**, depois do gate da 22. Medido: 0 unidade da casca
      dá `uses we2002_database`
- [x] Escrito o que a fase **não** prova
      — seção 5 do `fase-3-fechamento.md`
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-10

- **Resumo do que foi feito:**

  O fechamento tem medidor próprio, o
  [`check_fase3.py`](../../wte/tools/check_fase3.py), irmão do `check_fase1` e
  do `check_fase2` — e a saída dele **não** é o `fase-3.md`, que já é de outra
  task: o `compare_dumps.py` da WTE-TASK-20 escreve aquele arquivo, e dois
  geradores no mesmo destino seriam a duplicação sem guarda que o `README.md`
  de `wte/tools/` manda evitar. Daí o nome novo,
  [`fase-3-fechamento.md`](../../wte/re/fase-3-fechamento.md), com os dois
  linkando um para o outro: um mede se **os valores batem**, o outro **quem
  escreveu o código que os produz**.

  **A fração é 91,8% por regra, e a ressalva é o que ela ensina.** Todos os
  oito `.pas` da camada são saída de gerador — nenhum editado à mão, e o
  `--check` prova. Mas arquivo gerado não é conteúdo transpilado: as 303 linhas
  da rota 3 são Pascal escrito à mão que mora nas constantes `MANUAIS` /
  `TRECHOS_MANUAIS` do gerador. Dizer "100% gerado" seria verdade de arquivo e
  mentira de conteúdo, e a tese da §4.5 fala de conteúdo.

  **O app ainda não lê o jogo, e isso virou número:** zero unidade da casca dá
  `uses we2002_database`; quem consome são dois programas de console de
  `wte/tests/`. A integração mínima fica para a WTE-TASK-25, **depois** do gate
  da 22 — fazê-la aqui seria implementar `boton_dialogo_weClick` e
  `lista_equiposChange` sem o gate que os julga.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/tools/check_fase3.py` | criado — o medidor do fechamento |
  | `wte/tools/test_check_fase3.py` | criado — 11 testes, guardas com entrada plantada |
  | `wte/re/fase-3-fechamento.md` | criado, **gerado** |
  | `wte/tools/compare_dumps.py` | a seção "o que isto não mede" trocava duas populações de offset; e agora aponta para o irmão |
  | `wte/re/fase-3.md` | regerado |
  | `docs/PLAN-WTE-LAZARUS.md` | §4.5 ganhou a fração medida |
  | `wte/tools/README.md`, `docs/tasks/progresso.md` | o script novo e o arquivo novo |

- **Problemas encontrados:**

  **Um erro de contagem que o dedupe pegou, e ele não era visível.** A primeira
  medição dizia 320 linhas à mão. O gerador **reusa** a constante em vez de
  copiar o texto — `MANUAL_TIPOS["we2002_types"]` **é**
  `MANUAL_TYPES.interface`, o mesmo objeto alcançado por dois caminhos —, e
  somar os dois contava o mesmo Pascal duas vezes. São 277, e a fração ia de
  91,3% para 92,5%. O teste que prende isso compara os textos por unidade.
  *(Os três números são de linha **útil**, que era a régua da contagem naquele
  momento; a [CORR-WTE-051](/docs/tasks/CORR-WTE-051.md) trocou a régua
  publicada para linha física, e os mesmos blocos passaram a somar 303 —
  fração 91,8%. O achado do dedupe não muda: a constante continua alcançada
  por dois caminhos.)*

  **Uma afirmação errada sobrevivendo num gerador.** A CORR-WTE-049 corrigiu,
  no `progresso.md`, a frase que trocava duas populações de offset — "os
  restantes são exatamente os que o `we2002_core` não tem". A **mesma** frase
  estava no `compare_dumps.py`, e de lá saía para o `fase-3.md` a cada
  regeração. Corrigir prosa de doc não alcança a cópia que mora dentro do
  gerador; a varredura de sítios da WTE-TASK-09 varre markdown, e esta cópia
  era Python.

  **A remedição dos dumps foi refeita de propósito**, e não reaproveitada: o
  critério é da fase, não da task 20. Saiu idêntica — mesmo TSV, byte a byte —,
  o que também prova que a medição é reprodutível.
