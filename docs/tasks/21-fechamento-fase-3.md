---
id: WTE-TASK-21
title: "Fechamento da fase 3 — a camada de dados é 100% gerada?"
type: fechamento
category: dados
phase: 3
depends_on: ["WTE-TASK-20"]
status: pendente
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
| `wte/re/fase-3.md` | modificar |
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§4.5, se a fração gerada divergir da tese) |
| `docs/tasks/progresso.md` | modificar |

---

## Critério de conclusão

- [ ] Fração gerada medida e comparada com a tese da §4.5
- [ ] `--check` dos três geradores verde sobre a árvore commitada
- [ ] Dumps idênticos nas duas ROMs
- [ ] Registrado se o Ghidra foi ou não necessário, e em quê
- [ ] Decidido onde entra a integração mínima com o `MainForm`
- [ ] Escrito o que a fase **não** prova
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
