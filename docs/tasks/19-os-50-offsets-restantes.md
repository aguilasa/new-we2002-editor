---
id: WTE-TASK-19
title: "Descobrir os offsets que o Obocaman tem e nós não"
type: extração
category: dados
phase: 3
depends_on: ["WTE-TASK-06", "WTE-TASK-18"]
status: pendente
---

# WTE-TASK-19: Os offsets restantes

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §4.2 e Fase 3 item 4.
- **Onde o método do projeto se prova.** A §4.2 diz: *sempre tentar o diff antes
  do decompilador*. Esta task é a aplicação pura disso — cada offset custa dois
  minutos de tela, contra horas de disassembly.

O `wte.exe` edita coisa que o `ed.exe` não edita: camisa 2D, bandeira, dados que
vêm de `.mcr`. Os offsets dessas regiões, se existirem, **não estão em
`Offsets.hpp`** — este repositório nunca precisou deles.

---

## Objetivo

Fechar a lista de regiões que o app Lazarus precisa endereçar.

### Método: diff dirigido

Para cada campo editável do original que a WTE-TASK-06 não resolveu:

1. Cópia limpa da ROM (**sempre cópia** — o editor grava in-place, e são 474 MB).
2. Abrir no Wine, mudar **um** campo, gravar, fechar.
3. `cmp` contra a cópia limpa.
4. O offset que mudou é o offset do campo.

### Cuidado que evita falso positivo

O `Load`+`Save` do original **não é idempotente**: ele troca os dois primeiros
cobradores de cada clube de ML (`OFS_KICKER`), porque `Load` lê o par trocado e
`Save` grava na ordem declarada. E o `Save` reconstrói as all-star a partir dos
links.

**Então o diff de controle vem primeiro:** abrir e gravar **sem editar nada**, e
registrar as faixas que mudam de graça. Só o que aparecer *além* dessas faixas é
efeito da edição.

Sem esse controle, toda medição vem contaminada e parece que campos aleatórios
se movem.

### Campos a cobrir

| Área | Origem |
|---|---|
| os 50 `OFS_*` não confirmados | WTE-TASK-06 |
| cor de camisa (casa/fora, menu) | `ficha_color`, `grabar_camisetaClick` |
| bandeira e cor de radar | `colorearClick`, novidade da v0.99 |
| aparência (cabelo, barba, `careto`) | WTE-TASK-08 |
| preço do jogador | `etiqprecioClick` |
| slots de ML livres | `ficha_movertodos` |

### Saída

Os offsets confirmados entram na **entrada do gerador** (WTE-TASK-16), nunca no
arquivo gerado.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/diff_dirigido.sh` | criar — automatiza copiar, editar, gravar, `cmp` |
| `wte/re/offsets.md` | modificar |
| `wte/re/offsets-novos.md` | criar — os que o `newWe2002` não tem |

---

## Critério de conclusão

- [ ] Diff de controle (gravar sem editar) medido e registrado **antes** do resto
- [ ] Os 50 resolvidos ou declarados irrelevantes, um a um
- [ ] As seis áreas da tabela cobertas
- [ ] Offsets novos documentados com a região que endereçam
- [ ] Nenhuma medição feita sobre `roms/` diretamente
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
