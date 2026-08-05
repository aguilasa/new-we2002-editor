---
id: WTE-TASK-26
title: "Handlers de edição — nomes, números, atributos, mover jogador"
type: implementação
category: comportamento
phase: 4
depends_on: ["WTE-TASK-25"]
status: pendente
---

# WTE-TASK-26: Handlers de edição

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4.
- Editam o estado **em memória**. A gravação é a WTE-TASK-27. A separação é de
  propósito: assim o golden test da 27 mede gravação, não edição, e uma
  divergência aponta para um lado só.

---

## Objetivo

Implementar o grupo de edição, com spec por handler.

### Alvos

| Grupo | Handlers | Endereços |
|---|---|---|
| nomes | `edit_nombre1/2/3KeyPress`, `iguala_nombresClick`, `casilla_nombreKeyPress` | `0x0040d36c`, `0x0040d3c4`, `0x0040d41c`, `0x0040d43c`, `0x00408af8` |
| números | `dorsalClick`, `dorsalMouseDown`, `scroll_dorsalChange`, `casilla_dorsalKeyPress` | `0x00410a74`, `0x00410ddc`, `0x00402b58`, `0x00408b50` |
| atributos | `barrhabScroll`, `barrhab_bisScroll` | `0x00407a88`, `0x00407bb4` |
| barras | `sel_barraClick`, `track_barraChange` | `0x0040c9d0`, `0x0040ca10` |
| mover jogador | `paderechaClick`, `paizquierdaClick`, `parribaClick`, `pabajoClick`, `paderecha2Click`, `paizquierda2Click`, `paderechaeizquierdaClick`, `flechasapaClick` | `0x0040e5e8` … `0x00408088` |
| tática | `bolaMouseDown`, `bolaMouseMove`, `bolaEndDrag`, `campoMouseMove`, `rectanguloDragOver`, `rectanguloDragDrop`, `relojTimer` | `0x00408f00` … `0x00409ba4` |

`paderechaeizquierdaClick` é a novidade da v0.98 — "mover todos os jogadores de
cada time com um clique". `ficha_movertodos` é a tela dela.

### O que a spec tem de capturar aqui, e que a de carga não tinha

**Validação.** Estes handlers recusam entrada, e a regra da recusa é o que
importa. A WTE-TASK-05 já mapeou as mensagens de erro para os handlers que as
referenciam — a mensagem é o atalho para a regra. Exemplo já visto:

```
Numero do uniforme invalido ([33 ... 99] somente na Mastere
```

**Truncamento.** Todo campo de texto tem tamanho máximo no formato. O original
é C++Builder com buffer fixo; o comportamento de estouro (trunca? recusa?
corrompe o vizinho?) entra na spec, porque o Pascal não vai reproduzi-lo por
acidente. Isto alimenta a WTE-TASK-36.

**Ordem de evento.** `OnKeyPress` filtra caractere; a gravação no modelo
acontece onde? A WTE-TASK-13 mediu a ordem — usar a medição, não supor.

### Verificação

Estes não gravam. A verificação é: editar pela tela nos dois lados, **então**
gravar nos dois, e o golden test da WTE-TASK-22 compara. Uma edição por rodada,
para que a divergência tenha uma causa só.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar |
| `wte/src/ep2002_*.pas` | modificar |
| `wte/tools/roteiros/edicao-*.sh` | criar |

---

## Critério de conclusão

- [ ] Todo handler do grupo com spec, incluindo regra de validação
- [ ] Comportamento de truncamento documentado por campo
- [ ] Golden verde para cada edição, uma por rodada
- [ ] Limpeza de campo usando `End`/`shift+Home`/`BackSpace`, nunca `ctrl+a`
- [ ] Nenhuma medição sobre `roms/` diretamente
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
