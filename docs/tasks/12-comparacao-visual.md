---
id: WTE-TASK-12
title: "Comparação visual dos 18 formulários contra o original"
type: verificação
category: ui
phase: 2
depends_on: ["WTE-TASK-11"]
status: pendente
---

# WTE-TASK-12: Comparação visual

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §6 e Fase 2 item 3.
- **Não automatizar com tolerância de pixel.** `MS Sans Serif` não está
  instalada no host, o Qt e o GTK2 substituem por fontes diferentes, e o próprio
  `wte.exe` sob Wine já renderiza com fonte substituta. Diferença de pixel é
  garantida e não informa nada. É inspeção humana, uma vez por formulário.

O `newWe2002` já passou por isto: rótulo apertado corta ("Position" vira
"Positior") tanto no port quanto no `ed.exe` sob Wine, pelo mesmo motivo.

---

## Objetivo

Capturar os 18 formulários dos dois lados e conferir, um a um, que a diferença é
só de fonte — não de posição, tamanho, cor, ordem ou controle faltando.

### Método

1. `make wte` no `:99`, navegar até cada formulário, `import -window <id>`.
2. O app Lazarus no `:99`, mesmo formulário, mesma captura.
3. Lado a lado em `wte/re/visual/<formulario>/`.

**`import -window` falha com janela obscurecida por modal** — o aviso de
tamanho aparece na carga dos dois lados. Dispensar o modal antes, ou capturar
`-window root`.

### O que procurar, em ordem de gravidade

| Achado | Gravidade |
|---|---|
| controle faltando ou sobrando | bug do gerador — volta para a WTE-TASK-10 |
| posição ou tamanho errado | bug do gerador |
| cor de fundo diferente | provável `TStaticText` (§8.9) — 37 candidatos |
| bitmap não aparece | blob perdido na conversão |
| rótulo cortado | **esperado**, registrar e seguir |

### As 37 instâncias de `TStaticText`

A §8.9 manda conferir agora, não na Fase 6. Corrigir 37 controles no fim é
retrabalho.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/visual/*.png` | criar (36 capturas) |
| `wte/re/visual.md` | criar — um veredito por formulário |

---

## Critério de conclusão

- [ ] Os 18 capturados dos dois lados
- [ ] Um veredito escrito por formulário
- [ ] Nenhum controle faltando ou fora de lugar
- [ ] Comportamento das 37 `TStaticText` decidido
- [ ] Rótulos cortados listados, com a nota de que é esperado
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
