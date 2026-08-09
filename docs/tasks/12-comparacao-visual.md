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
2. O app Lazarus no `:99`. **Ele não navega** — na fase 2 os handlers são stub
   ([WTE-TASK-11](/docs/tasks/11-app-com-a-casca-completa.md), problema 3). O
   andaime é `--show`: `./wte/build/wte --show all` abre os 18 de uma vez,
   `--show <nome>` abre um só, `--list` dá os nomes. Mesma captura.
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
| bitmap não aparece | **não é perda na conversão** — a preservação dos 118 blobs está medida (WTE-TASK-10). É defeito de exibição: LCL/GTK2 ou pai do componente |
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
- [ ] Os 118 blobs aparecem na janela — critério herdado da
      [WTE-TASK-10](/docs/tasks/10-conversor-dfm-para-lfm.md), que provou a
      preservação byte a byte e não podia provar a exibição
- [ ] O sufixo ` [Lazarus]` no `Caption` **não** foi contado como achado — é
      divergência deliberada da WTE-TASK-11, registrada na
      [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md). No `:99` não há
      window manager e a captura nem chega a mostrá-lo
- [ ] Nenhum controle faltando ou fora de lugar
- [ ] Comportamento das 37 `TStaticText` decidido
- [ ] Rótulos cortados listados, com a nota de que é esperado
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
