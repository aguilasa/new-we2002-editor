---
id: WTE-TASK-27
title: "Handlers de gravação — escrever na imagem de CD"
type: implementação
category: comportamento
phase: 4
depends_on: ["WTE-TASK-26"]
status: pendente
---

# WTE-TASK-27: Handlers de gravação

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4 e §6.
- **O grupo mais arriscado do projeto.** É onde o app toca 474 MB de imagem
  in-place, e é o único grupo que o golden test mede diretamente e sem
  ambiguidade.

Vêm por último de propósito: dependem de carga e edição estarem certas.

---

## Objetivo

Implementar as seis gravações, cada uma com golden verde antes de passar para a
seguinte.

### Alvos

| Handler | Endereço | O que grava |
|---|---|---|
| `boton_nombres2isoClick` | `0x0040d534` | nomes na imagem |
| `boton_barras2isoClick` | `0x0040cab8` | barras/atributos |
| `boton_tex2isoClick` | `0x0040de18` | textura |
| `boton_mcr2isoClick` | `0x0040c46c` | dados vindos de `.mcr` — **ver WTE-TASK-31** |
| `grabar_camisetaClick` | `0x0040ee80` | camisa — **ver WTE-TASK-32** |
| `grabar_memoryClick` | `0x0040f69c` | escreve `.mcr` (saída, não a imagem) |

Dois deles são **compartilhados com a Fase 5**: `boton_mcr2isoClick` depende do
parser de `.mcr` e `grabar_camisetaClick` do render 2D. Aqui se implementa a
**gravação** — onde e como os bytes vão para a imagem; a *origem* dos bytes é
das tasks 31 e 32. Se a ordem incomodar, inverta: nada impede fazer a 31/32
antes, desde que o golden desta task rode depois.

### Regras que não podem ser violadas

- **Nunca recalcular EDC/ECC.** O editor original não recalcula; preservar é o
  comportamento correto.
- **Fronteira de setor.** Os offsets pulam cabeçalho de setor manualmente
  (2352 = 24 + 2048 + 280). Se um round-trip falhar, é a primeira suspeita.
- **Cópia, sempre.** Cada rodada de golden usa duas cópias de ~474 MB.

### O diff de controle vem antes

Como na WTE-TASK-19: gravar **sem editar nada** nos dois lados e registrar o que
muda de graça. O `Save` reconstrói as all-star a partir dos links, e o
`Load`+`Save` do original não é idempotente (troca os dois primeiros cobradores
de cada clube de ML). Sem esse controle, toda medição vem contaminada.

### Critério

**Byte-idêntico** entre `wte.exe` e o app Lazarus, nas duas ROMs, para cada
operação. Divergência que sobreviver à análise vira **divergência deliberada**
com registro (WTE-TASK-35) — nunca "aceita e esquecida".

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar (6) |
| `wte/src/ep2002_*.pas` | modificar |
| `wte/tools/roteiros/gravacao-*.sh` | criar (6) |

---

## Critério de conclusão

- [ ] Diff de controle medido e registrado antes de qualquer edição
- [ ] As seis com spec e com golden verde nas duas ROMs
- [ ] EDC/ECC preservados — provado, não presumido
- [ ] Nenhuma divergência sem veredito escrito
- [ ] `roms/` intocada em todas as rodadas
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
