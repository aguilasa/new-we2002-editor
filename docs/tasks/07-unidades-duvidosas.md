---
id: WTE-TASK-07
title: "Veredito sobre Registry, Printers, Comobj e Winhelpviewer"
type: extração
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-02"]
status: pendente
---

# WTE-TASK-07: As quatro unidades duvidosas

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §5 e Fase 1 item 5.
- O binário importa 322 símbolos de `rtl60.bpl`/`vcl60.bpl`. Quatro unidades
  entre eles não têm par óbvio na LCL e podem ser dependência transitiva sem
  uso real — **ou** funcionalidade que o port precisa reproduzir.

| Unidade | Se for uso real | Se for transitiva |
|---|---|---|
| `Registry` | config no registry → vira INI em `~/.config/` | some |
| `Printers` | há impressão de verdade → decidir escopo | some |
| `Comobj` | OLE → provavelmente só o `ShellExecute` do `TBrowseURL` | some com a substituição |
| `Winhelpviewer` | ajuda `.hlp` → o texto vira janela própria | some |

Import de unidade em app C++Builder frequentemente é dependência transitiva. Mas
"frequentemente" não é veredito.

---

## Objetivo

Um veredito escrito por unidade: **usada** ou **transitiva**, com a evidência.

### Método

Para cada unidade, listar os símbolos importados dela (`objdump -x`, filtrando
por `@Registry@`, `@Printers@`, …) e procurar **chamada real** no
disassembly — `call ds:[...]` para o thunk correspondente.

Import sem nenhuma chamada = transitiva. Import com chamada = usada, e aí a
pergunta vira *onde*: qual dos 96 handlers contém a chamada.

### Duas armadilhas

1. **Chamada em código de inicialização não está em handler nenhum.** O
   `FormCreate` é handler, mas a inicialização de unidade
   (`@@Tep2002_*@Initialize`) não é. Procurar nos dois lugares.
2. **`Comobj` pode aparecer sem `TBrowseURL` estar envolvido.** Não concluir
   pela hipótese; conferir o sítio da chamada.

### Saída

Se alguma for **usada**, a task tem de propor a substituição em LCL, e ela vira
item da fase onde o handler dono for implementado — não trabalho perdido aqui.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/unidades-vcl.md` | criar |
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§5, fechando as quatro linhas de investigação) |

---

## Critério de conclusão

- [ ] As quatro com veredito e evidência (sítio da chamada, ou ausência dela)
- [ ] Inicialização de unidade conferida, além dos handlers
- [ ] Para cada "usada", substituição LCL proposta e task de destino apontada
- [ ] §5 do plano atualizado — sem linha de investigação em aberto
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
