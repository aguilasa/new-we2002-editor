---
id: WTE-TASK-40
title: "Verificação final — as três condições da definição de pronto"
type: fechamento
category: verificação
phase: 7
depends_on: ["WTE-TASK-36", "WTE-TASK-37", "WTE-TASK-39"]
status: pendente
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

Já conferida na WTE-TASK-29. Reconferir que nada regrediu: o índice de
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

---

## Critério de conclusão

- [ ] Condição 1 reconferida, sem regressão
- [ ] Condição 2 reconferida depois das tasks 36 a 39
- [ ] Condição 3 testada em ambiente sem Wine, não presumida
- [ ] Vocabulário escrito: o que é verificado, o que não é, o que diverge
- [ ] Todo item aberto listado com a razão
- [ ] §11 do plano preenchido
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
