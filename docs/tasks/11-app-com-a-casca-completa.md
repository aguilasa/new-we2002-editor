---
id: WTE-TASK-11
title: "App Lazarus abrindo os 18 formulários, com os 96 stubs logando"
type: implementação
category: ui
phase: 2
depends_on: ["WTE-TASK-10"]
status: pendente
---

# WTE-TASK-11: A casca completa

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §4.3 e Fase 2 item 2.
- A estratégia é **casca antes de recheio**: construir o app inteiro vazio e
  depois preencher handler a handler. O stub que loga transforma o app numa
  ferramenta de RE — clicar no original e no stub lado a lado mostra a **ordem
  real de disparo dos eventos**, que nenhuma análise estática dá.

**Nesta fase o app não toca a imagem de CD. Zero risco.**

---

## Objetivo

Aplicação que compila, abre, navega entre os 18 formulários, e registra cada
handler disparado.

### 1. Auto-create e navegação

O original cria as 18 instâncias globais no start (`_MainForm`, `_estrategia`,
`_jugador`, `_ficha_*`) — padrão auto-create do C++Builder. Reproduzir, e ligar
a navegação: qual botão abre qual formulário sai dos DFM.

Alguns formulários são modais de aviso (`ficha_error`, `ficha_warning`,
`ficha_info*`); outros são telas de trabalho (`estrategia`, `jugador`,
`ficha_color`). O DFM diz qual é qual pelo `BorderStyle` e `BorderIcons`.

### 2. `REStub` e o trace

```pascal
procedure REStub(const Nome: string);
```

Escreve em `wte/re/trace.log`: timestamp relativo, nome do handler, formulário.
Formato **estável e diffável** — a WTE-TASK-13 vai comparar duas execuções.

### 3. O que ainda não existe

Nenhum acesso a arquivo, nenhum `OpenDialog` funcional, nenhum desenho. Botão
que carregaria imagem só loga.

### Armadilha de plataforma

A regra do `:99` vale integralmente: `DISPLAY=:99`, `XAUTHORITY` resolvido pelo
`ps`, sem window manager, `xdotool windowactivate` não funciona — dirigir por
coordenada absoluta.

**O título da janela tem de ser diferente do original.** O `wte.exe` se chama
`W11 Team Editor...`; se o app Lazarus usar o mesmo, os scripts que acham janela
por título vão pegar o lado errado a partir da WTE-TASK-22.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/src/wtemain.pas` | criar — auto-create e navegação |
| `wte/src/restub.pas` | criar |
| `wte/wte.lpr` | modificar |

---

## Critério de conclusão

- [ ] `lazbuild` compila sem warning novo
- [ ] Os 18 formulários abrem e fecham no `:99`
- [ ] Os 96 stubs logam em `trace.log`, formato estável
- [ ] Título da janela distinto do original
- [ ] Nenhum acesso a arquivo de imagem de CD no código
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
