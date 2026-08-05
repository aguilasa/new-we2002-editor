---
id: WTE-TASK-13
title: "Trace de eventos — a ordem de disparo dos dois lados"
type: verificação
category: comportamento
phase: 2
depends_on: ["WTE-TASK-11"]
status: pendente
---

# WTE-TASK-13: Trace de eventos

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §4.3 item 3 e Fase 2 item 4.
- **Isto é RE dinâmica barata, e alimenta a Fase 4 inteira.** A ordem em que os
  eventos disparam não sai de análise estática, e ela decide o resultado: se o
  original recalcula o preço no `OnChange` antes do `OnKillFocus` gravar, a
  ordem invertida grava valor velho.

O `newWe2002` já pagou por diferença de sinal entre frameworks — `setText` não
dispara `editingFinished`, mas `EN_CHANGE` **dispara** em `SetWindowText`, e é o
que move os marcadores do campinho. Descobrir o equivalente aqui, antes de
implementar handler, é o ponto desta task.

---

## Objetivo

Comparar a sequência de eventos entre o original e a casca, para um conjunto
fixo de interações.

### 1. Instrumentar o lado do original

O `wte.exe` não loga nada. Duas opções, escolher e escrever a razão:

- **Ghidra + breakpoint** nos 96 endereços, com o Wine sob depurador. Preciso,
  caro de montar.
- **Inferência por efeito** — clicar e observar o que muda na tela, cruzando com
  os DFM. Barato, e suficiente para ordem relativa na maioria dos casos.

### 2. O roteiro de interações

Fixo, versionado, reproduzível por `xdotool` — **não** driver que reage à tela.
Roteiro que reage muda o estímulo quando um lado diverge, e aí os dois param de
receber a mesma entrada.

Candidatos de partida, cobrindo os pontos onde a ordem importa:

| Interação | Por que interessa |
|---|---|
| trocar de time no combo | `lista_equiposChange` — carga em cascata |
| clicar num jogador | `mostrar_jugadorClick` |
| editar nome e sair do campo | `OnKeyPress` × `OnExit` |
| mexer num `TScrollBar` de atributo | `OnChange` contínuo × final |
| abrir e fechar `ficha_color` | ordem de `FormShow`/`FormCreate` |

### 3. O que registrar

Diferenças de ordem entre LCL e VCL, com a consequência. Cada uma vira nota na
spec do handler afetado, na Fase 4.

**`setCurrentIndex`/`ItemIndex` dispara `OnChange` na LCL.** Se o original
dependia de não disparar, a carga de time precisa de bloqueio de sinal — o
`newWe2002` resolveu com `QSignalBlocker`; o equivalente aqui é um contador de
"estou carregando" ou desligar o handler temporariamente.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tests/roteiros/*.txt` | criar |
| `wte/re/eventos.md` | criar — diferenças de ordem e consequência |

---

## Critério de conclusão

- [ ] Método de instrumentação do original escolhido, com razão
- [ ] Roteiro fixo versionado, não driver reativo
- [ ] As cinco interações da tabela cobertas
- [ ] Cada diferença de ordem com a consequência escrita
- [ ] Decidido se a carga de time precisa de bloqueio de sinal
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
