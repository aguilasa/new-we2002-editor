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

### A metade da WTE-TASK-26 que esta task herdou

*(decisão do usuário, 2026-08-12)*

A [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) edita **em memória** e não
grava; o critério dela dizia "editar pela tela nos dois lados, então gravar nos
dois, e o golden compara". O segundo verbo é desta task — as barras editadas lá
só chegam à imagem pelo `boton_barras2isoClick`, os nomes pelo
`boton_nombres2isoClick` —, e a 27 `depends_on` a 26. Circularidade da mesma
forma que a [CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) desfez para o gate.

**A 26 passou a fechar por conferência de tela e esta task herdou o byte.** Na
prática: cada uma das seis gravações roda o golden **duas** vezes —

1. **gravar sem editar** (o diff de controle da seção acima);
2. **editar pela tela, com um handler do grupo da 26, e então gravar.**

A segunda é a que julga a edição e a gravação juntas. Sem ela, a edição fica
verificada só por pixel, e pixel igual dos dois lados não prova que os dois
escreveram o **mesmo byte do modelo** — os dois poderiam desenhar a mesma
largura a partir de campos diferentes. É a lição da terceira ponta da
[WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md).

Par mínimo por gravação, quando existir handler de edição correspondente:

| gravação | edição que a exercita (WTE-TASK-26) |
|---|---|
| `boton_barras2isoClick` | `sel_barraClick` + `track_barraChange` |
| `boton_nombres2isoClick` | `edit_nombre1/2/3KeyPress`, `iguala_nombresClick` |
| `grabar_memoryClick` | os de número (`dorsalClick`, `scroll_dorsalChange`) |

`boton_tex2isoClick`, `boton_mcr2isoClick` e `grabar_camisetaClick` não têm par
na 26 — a origem dos bytes deles é das tasks 31 e 32, como já diz a seção de
alvos.

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
- [ ] **Cada gravação que tem par na WTE-TASK-26 rodada também com uma edição
      de tela antes** — herdado da 26 em 2026-08-12; ver a seção acima. É o
      único critério do projeto que julga edição e gravação juntas
- [ ] EDC/ECC preservados — provado, não presumido
- [ ] Nenhuma divergência sem veredito escrito
- [ ] `roms/` intocada em todas as rodadas
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
