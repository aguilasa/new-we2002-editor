---
id: PES2-TASK-13
title: "Uniforme e cores de time"
type: engenharia-reversa
category: formato
phase: 4
depends_on: ["PES2-TASK-11"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §5 (Fase 4)"
status: pendente
---

# PES2-TASK-13: Uniforme e cores

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §5, Fase 4, e §1.11.
- **A âncora do WE2002 é `BIN/DAT2D.BIN`**, LBA 5300 nos dois discos, onde
  quatro dos 69 `OFS_*` caem — a começar por `OFS_FLAG_COLOURS_SENEGAL`
  (§1.4). Cor de bandeira e cor de uniforme moram na mesma vizinhança no
  WE2002.
- **PES2 replica o `DAT2D` por idioma** (`DAT2D_*`, §1.12), o que dá uma
  segunda amostra de graça: o que for **igual** entre as variantes de idioma
  e não for código é candidato a dado de jogo (§4.2, alavanca 2).

---

## Objetivo

A estrutura de uniforme: cores (primária, secundária, detalhe), padrão da
camisa, e o que mais a tela de edição expuser.

### O caminho mais curto é a tela

Cor é o campo mais fácil de verificar que existe: **muda-se um byte e a
camisa muda de cor na tela**, sem ambiguidade nenhuma. É o oposto de um
atributo numérico, onde só o menu de edição conta a verdade.

Isso torna a busca por varredura viável mesmo sem rótulo: um valor RGB ou um
índice de paleta, `N` deles com `N` igual a uma contagem de time conhecida,
e um `poke` fecha em uma corrida.

### Paleta ou RGB direto

A PSX usa cor de 15 bits (`BGR555`) em VRAM. Duas hipóteses, e a segunda é a
mais provável para dado de time:

1. RGB direto de 2 bytes por cor — `BGR555`, bit 15 de transparência;
2. **índice numa paleta**, 1 byte, com a paleta em outro lugar do arquivo.

A segunda se reconhece pelo domínio estreito dos valores; a primeira, por
eles ocuparem os 16 bits inteiros. Medir antes de assumir.

---

## Critério de conclusão

- [ ] Tabela de cores localizada — arquivo, âncora, delta assinado, contagem
      — com a contagem batendo com uma contagem de time conhecida.
- [ ] Codificação decidida por medida: `BGR555` direto ou índice de paleta,
      com a paleta localizada no segundo caso.
- [ ] Verificado por `poke`: mudar a cor no disco muda a camisa na tela.
- [ ] O que mais o uniforme guarda (padrão, gola, número) mapeado ou listado
      como aberto, com a via.
- [ ] Ferramenta versionada, registrada no `check_image.py`.

---

## Log de Execução

*(a preencher)*
