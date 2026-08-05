---
id: WTE-TASK-34
title: "Bateria golden completa — toda gravação, nas duas ROMs"
type: verificação
category: verificação
phase: 6
depends_on: ["WTE-TASK-29", "WTE-TASK-30", "WTE-TASK-31", "WTE-TASK-32", "WTE-TASK-33"]
status: pendente
---

# WTE-TASK-34: Bateria golden completa

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 6 item 1 e §0 (definição de
  pronto, item 2).

> Para cada operação que grava, `wte.exe` sob Wine e o app Lazarus produzem
> **imagem byte-idêntica** a partir da mesma imagem de entrada, nas duas ROMs.

As tasks 27, 31 e 32 rodaram golden **por operação**, isoladas. Esta roda a
bateria inteira, e é onde interação entre operações aparece.

---

## Objetivo

Uma bateria versionada, reproduzível, com resultado registrado.

### O que a bateria cobre

| Categoria | Origem |
|---|---|
| as seis gravações | WTE-TASK-27 |
| import de `.mcr` para a imagem | WTE-TASK-31 |
| gravação de camisa e bandeira | WTE-TASK-32 |
| edição + gravação combinadas | novo |
| gravar duas vezes seguidas | novo |

### As duas combinações que só aparecem aqui

**Edição múltipla antes de gravar.** Cada operação isolada passou; várias na
mesma sessão podem não passar, se o original recalcular algo ao trocar de
contexto. É a classe de bug que teste isolado não pega.

**Gravar duas vezes.** O `newWe2002` registra que o editor **não é idempotente**
— `Load`+`Save` troca os dois primeiros cobradores de cada clube de ML, e
gravar duas vezes volta ao início. Se o app Lazarus não reproduzir esse
vaivém, a segunda gravação diverge mesmo com a primeira idêntica.

### Custo

Cada rodada usa duas cópias de ~474 MB. A bateria inteira, com N operações e
duas ROMs, é 2N cópias — planejar espaço, e limpar entre rodadas. **Não roda em
CI**, e o plano já registra isso.

### Registro

Uma tabela: operação × ROM × resultado. Divergência vai para a WTE-TASK-35, não
fica na tabela como nota de rodapé.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/golden_suite.sh` | criar |
| `wte/re/golden.md` | criar — a tabela operação × ROM × resultado |

---

## Critério de conclusão

- [ ] Toda operação de gravação na bateria, nas duas ROMs
- [ ] Edição múltipla antes de gravar coberta
- [ ] Gravação dupla coberta, e o vaivém dos cobradores reproduzido
- [ ] Tabela de resultado completa, sem célula vazia
- [ ] Temporário limpo; `roms/` intocada
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
