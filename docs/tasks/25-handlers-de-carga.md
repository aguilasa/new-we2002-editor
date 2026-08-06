---
id: WTE-TASK-25
title: "Handlers de carga — abrir a imagem e popular as telas"
type: implementação
category: comportamento
phase: 4
depends_on: ["WTE-TASK-22", "WTE-TASK-23", "WTE-TASK-24"]
status: pendente
---

# WTE-TASK-25: Handlers de carga

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4.
- **Ordem por dependência, não por endereço.** Estes vêm primeiro porque tudo
  depende deles: sem carga, nenhum handler de edição tem estado para editar.

Estes handlers **leem** a imagem e **não gravam**. O golden test não os mede
diretamente — o que os mede é a tela. Por isso a verificação aqui é dupla:
comparar o que aparece na janela dos dois lados, e comparar o estado interno
contra o dump da WTE-TASK-20.

---

## Objetivo

Implementar o grupo de carga, com spec e verificação por handler.

### Alvos

| Handler | Endereço | Papel |
|---|---|---|
| `boton_dialogo_weClick` | `0x0040bd60` | abre a imagem de CD |
| `lista_equiposChange` | `0x0040cd6c` | carrega o time selecionado |
| `lista_equipos_2Change` | `0x0040e1a8` | segunda lista de times |
| `lista_jugadores_1Change` | `0x0040f8b8` | seleção de jogador |
| `mostrar_jugadorClick` | `0x0040f8d4` | abre a ficha do jogador |
| `mostrar_estrategiaClick` | `0x00410220` | abre a tela de tática |
| `lista_formacionesClick` | `0x00409aa0` | aplica formação predefinida |
| `ComboBoxDrawItem` | `0x0040adec` | owner-draw do combo |
| `FormCreate` / `FormShow` | 18 endereços | inicialização de cada formulário |

São **16 `FormCreate` mais 2 `FormShow`** — não um por formulário:
`ficha_error` e `ficha_error2` não publicam nenhum dos dois. A coluna
`formulario` do `published_methods.tsv` diz qual é qual.

### Duas armadilhas de framework

**`ItemIndex` dispara `OnChange` na LCL.** Se o original dependia de não
disparar (o `SetCurSel` do Win32 não dispara `CBN_SELCHANGE`), a carga de time
entra em recursão ou recarrega duas vezes. A WTE-TASK-13 já deve ter respondido
isso; se não respondeu, responder aqui antes de escrever código.

**`lista_formacionesClick` aplica formação sobre o time selecionado** — é ação
destrutiva disparada por clique em lista. Conferir que ela não roda durante a
carga.

### Verificação

1. **Estado interno** — depois de carregar o time N, o dump da WTE-TASK-20 do
   app tem de bater com o do `we2002_core`.
2. **Tela** — captura dos dois lados, mesmo time selecionado, comparação humana
   dos campos preenchidos (não de pixel).
3. **Sem gravação** — provar que nenhum destes escreve na imagem: rodar todos,
   fechar sem salvar, e `cmp` contra a cópia limpa tem de dar zero.

O item 3 é barato e pega a classe de bug mais cara desta fase.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar (um por handler do grupo) |
| `wte/src/ep2002_*.pas` | modificar (corpo dos stubs) |
| `wte/re/spec/INDICE.md` | regenerar |

---

## Critério de conclusão

- [ ] Todo handler do grupo com spec no gabarito da WTE-TASK-23
- [ ] Estado interno batendo com o `we2002_core` após carga
- [ ] Tela conferida contra o original para pelo menos 3 times distintos
- [ ] Provado que o grupo não escreve na imagem (`cmp` = zero)
- [ ] Comportamento de `OnChange` na carga decidido e testado
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
