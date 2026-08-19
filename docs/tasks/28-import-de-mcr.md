---
id: WTE-TASK-28
title: "Import e export de .mcr — memory card do PSX"
type: implementação
category: features
phase: 4
depends_on: ["WTE-TASK-08", "WTE-TASK-24", "WTE-TASK-27"]
status: pendente
---

# WTE-TASK-28: Import de `.mcr`

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §5.2.
- Segunda das quatro features. Permite trazer jogador de memory card para a
  imagem de CD — o `ed.exe` não faz.
- **Fase 4, não 5**, e a task carrega a gravação `boton_mcr2isoClick` — ver
  "A gravação mora aqui" abaixo.

| Handler | Endereço | Papel |
|---|---|---|
| `boton_mcrClick` | `0x0040c2c8` | abre o `.mcr` |
| `boton_mcr2isoClick` | `0x0040c46c` | **grava o jogador na imagem** — desta task desde 2026-08-19 |
| `grabar_memoryClick` | `0x0040f69c` | escreve `.mcr` — **já implementado** na [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md), e o layout de saída dele é insumo daqui |

### A gravação mora aqui, e o que veio com ela

*(decisão do usuário, 2026-08-19)*

Até 2026-08-19 o `boton_mcr2isoClick` era da
[WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) — a gravação lá, a origem
dos bytes aqui. A divisão criava **ciclo**: a 27 não fechava sem esta task, e
esta declarava `depends_on` a 27. Agora a task que produz os bytes é a mesma que
os grava, e as duas features que estavam nessa situação subiram para a fase 4.

Com a gravação vieram as regras, e nenhuma delas é sobre o handler — são sobre
gravar **nesta imagem**:

- **Nunca recalcular EDC/ECC.** O editor original não recalcula; preservar é o
  comportamento correto.
- **Fronteira de setor.** `2352 = 24 + 2048 + 280`, e os offsets pulam cabeçalho
  de setor à mão. Round-trip que falha: é a primeira suspeita.
- **Cópia, sempre.** Cada rodada de golden usa duas cópias de ~474 MB, e `roms/`
  nunca é alvo.
- **O diff de controle já está medido** e vale aqui igual:
  [`wte/re/gravacao-controle.md`](../../wte/re/gravacao-controle.md). Gravar sem
  editar nada **muda** 22 bytes nesta ROM — katakana virando ASCII. Sem esse
  desconto, toda medição vem contaminada.
- **O clique não grava; quem grava é o `fseek` seguinte.** O `wte.exe` escreve
  pela saída bufferizada do runtime C, e um roteiro que **termina** numa
  gravação mede um oráculo truncado: o harness encerra com `wineserver -k` e o
  buffer se perde. Todo roteiro de gravação tem de terminar com uma troca de
  time — a descarga — e só então a marca de corte. Medido com o par
  [`27-descarga-sem.txt`](../../wte/tests/roteiros/27-descarga-sem.txt) /
  [`27-descarga-com.txt`](../../wte/tests/roteiros/27-descarga-com.txt); sem
  repetir isso aqui, o golden desta task nasceria com o defeito que a primeira
  passagem da 27 levou oito dias para achar.

O readme do original registra que a v0.98 corrigiu "the problem with the captain
and kickers when loading from .mcr files" e "the problem with the Eire's
goalkeeper" — sinal de que o mapeamento `.mcr` → imagem tem casos especiais.

---

## Objetivo

Ler, escrever e converter, com fixture reproduzível.

### O risco declarado, e a mitigação

**Pode faltar `.mcr` de teste variado.** Mitigação prevista no plano: o
`grabar_memoryClick` do próprio original **escreve** `.mcr`. Então dá para gerar
fixture — editar um jogador conhecido no original, exportar, e usar o arquivo
como entrada do teste de import.

`data/dat.bin` começa com `MC` e tem 145.408 bytes contra os 131.072 de um
memory card padrão. A WTE-TASK-08 já deve ter classificado o arquivo e explicado
os 14.336 de diferença; se não explicou, explicar aqui antes de usá-lo como
fixture.

### O formato

Memory card do PSX é parcialmente documentado publicamente — cabeçalho, tabela
de blocos, diretório. Usar a documentação pública para o **contêiner**, e
engenharia reversa só para o **conteúdo** do bloco do WE2002, que é específico
do jogo.

Essa divisão poupa a maior parte do trabalho.

### Os casos especiais

O readme aponta três, e cada um vira teste:

1. **Capitão e cobradores** ao carregar de `.mcr`
2. **Goleiro da Eire** — provável caso de índice fora do padrão
3. **Espaços no nome do jogador**

Um bug corrigido pelo autor é um caso que o formato tem; reproduzir a *correção*,
não o bug.

### Round-trip

Exportar do app e importar de volta tem de dar o mesmo estado. E exportar do app
vs. exportar do original, a partir do mesmo jogador, tem de dar o **mesmo
arquivo** — é o golden test desta feature.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/boton_mcr*.md` | criar |
| `wte/re/mcr.md` | criar — contêiner (público) e conteúdo (revertido) |
| `wte/src/we2002_mcr.pas` | criar |
| `wte/tests/fixtures/*.mcr` | criar — geradas pelo próprio original |
| `wte/tests/test_mcr.pas` | criar |

---

## Critério de conclusão

- [ ] Contêiner lido conforme documentação pública, com a fonte citada
- [ ] Conteúdo do bloco do WE2002 mapeado
- [ ] Fixtures geradas pelo original, não à mão
- [ ] Os três casos especiais do readme cobertos por teste
- [ ] Round-trip export/import estável
- [ ] Export do app byte-idêntico ao export do original
- [ ] `boton_mcr2isoClick` com spec em
      `wte/re/spec/MainForm.boton_mcr2isoClick.md` e golden verde na ROM
      japonesa — gravação e origem dos bytes fecham na mesma task
- [ ] **EDC/ECC preservados na escrita de setor inteiro — provado, não
      presumido.** É a única gravação do projeto que escreve setor completo, e a
      única em que preservar EDC/ECC é decisão e não consequência: as quatro da
      WTE-TASK-27 escrevem dentro do payload de 2048 B e não alcançam os 280
      bytes de correção
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
