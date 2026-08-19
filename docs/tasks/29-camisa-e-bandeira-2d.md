---
id: WTE-TASK-29
title: "Camisa e bandeira 2D em tempo real, com colar-cores"
type: implementação
category: features
phase: 4
depends_on: ["WTE-TASK-08", "WTE-TASK-24", "WTE-TASK-27"]
status: pendente
---

# WTE-TASK-29: Render 2D

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §5.3 e §9.
- Terceira das quatro, e **a de maior risco do projeto**. A tabela de riscos do
  plano dá probabilidade **média** para "render 2D não bate pixel a pixel", e a
  causa nomeada é arredondamento de gradiente.

É também a feature mais visível: o readme do original a vende como "an
improvement over WE2002 Painter features".

---

## Objetivo

Reproduzir o editor de cor com fidelidade medida.

### Alvos

| Handler | Endereço |
|---|---|
| `colorearClick` | `0x00410ea8` |
| `gradienteClick` | `0x004063b0` |
| `oscurecerClick` | `0x004065fc` |
| `aclararClick` | `0x00406744` |
| `lista_col0Change` … `lista_col3Change` | `0x0040688c` … `0x0040690c` |
| `colorMouseDown` | `0x00406a0c` |
| `barraChange`, `barra1Change`, `barra2Change` | `0x00405e40`, `0x00406358`, `0x00406384` |
| `malla1MouseDown`, `malla2MouseDown` | `0x00409f4c`, `0x0040a000` |
| `grabar_camisetaClick` | `0x0040ee80` |

Formulário `ficha_color`: 758 linhas de DFM.

### A base

Os 105 `image/uniformes2d/*.bmp` e as 53 `image/banderas/*.bmp` são a base, e a
cor é aplicada sobre eles. A convenção de índice vem da WTE-TASK-08.

Em Pascal isso é `TBitmap` mais varredura de pixel; a LCL dá `TLazIntfImage`
para acesso rápido — `Canvas.Pixels` num loop é ordens de grandeza mais lento e
não serve para tempo real.

### Onde a fidelidade some

1. **Arredondamento de gradiente.** Se o original faz aritmética inteira com
   truncamento e o Pascal faz com arredondamento, o degradê inteiro desloca de 1.
   É o risco nomeado.
2. **Paleta.** BMP de 8 bits tem paleta; aplicar cor pode ser troca de entrada de
   paleta, não varredura de pixel. Descobrir qual antes de escrever código —
   muda o algoritmo inteiro.
3. **Espaço de cor.** "Escurecer" e "clarear" podem ser multiplicação em RGB ou
   ajuste em HSL. Resultado parecido, valores diferentes.

### Verificação

**Diff de bitmap contra captura do original**, não inspeção. Para uma grade de
cores de entrada, capturar a camisa renderizada dos dois lados e comparar pixel
a pixel.

**Aceitar tolerância documentada** se a igualdade exata não sair — a §9 já prevê
isso. O que não é aceitável é tolerância não medida: se houver diferença, ela
tem de ter máximo conhecido e causa nomeada.

### A gravação é outra coisa, e desde 2026-08-19 ela mora aqui

`grabar_camisetaClick` (`0x0040ee80`) grava na imagem, e aí o critério é
byte-idêntico, sem tolerância. Render é tela; gravação é dado. Não confundir os
dois critérios.

*(decisão do usuário, 2026-08-19)* Até essa data o handler era da
[WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) — a gravação lá, o render
aqui. A divisão criava **ciclo**: a 27 não fechava sem esta task, e esta
declarava `depends_on` a 27. Agora a task que produz os pixels é a mesma que os
grava, e por isso esta subiu para a fase 4.

Com a gravação vieram as regras, e nenhuma delas é sobre o handler — são sobre
gravar **nesta imagem**:

- **Nunca recalcular EDC/ECC.** O original não recalcula; preservar é o correto.
- **Fronteira de setor.** `2352 = 24 + 2048 + 280`, com os saltos à mão.
- **Cópia, sempre**; `roms/` nunca é alvo.
- **O diff de controle** já medido em
  [`wte/re/gravacao-controle.md`](../../wte/re/gravacao-controle.md) vale aqui
  igual: gravar sem editar **muda** 22 bytes nesta ROM.
- **O clique não grava; quem grava é o `fseek` seguinte.** Saída bufferizada do
  runtime C — roteiro que termina numa gravação mede um oráculo truncado, porque
  o harness encerra com `wineserver -k`. Todo roteiro de gravação termina com
  uma troca de time e só então a marca de corte. Medido com o par
  [`27-descarga-sem.txt`](../../wte/tests/roteiros/27-descarga-sem.txt) /
  [`27-descarga-com.txt`](../../wte/tests/roteiros/27-descarga-com.txt).

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar |
| `wte/re/render2d.md` | criar — algoritmo, espaço de cor, tolerância medida |
| `wte/src/we2002_render.pas` | criar |
| `wte/tests/test_render.pas` | criar |

---

## Critério de conclusão

- [ ] Decidido paleta vs. varredura de pixel, com evidência
- [ ] Espaço de cor de escurecer/clarear identificado
- [ ] `TLazIntfImage` usado; render em tempo real sem travar a janela
- [ ] Diff de bitmap sobre grade de cores, com tolerância **medida** e causa nomeada
- [ ] `grabar_camisetaClick` byte-idêntico, sem tolerância, com spec em
      `wte/re/spec/MainForm.grabar_camisetaClick.md` e golden verde
- [ ] **Determinado se `grabar_camisetaClick` escreve setor inteiro ou só
      payload.** A camisa lê 16 setores contíguos em `21168024`..`21203815`
      (achado da fase 3), e a resposta muda o critério: se for setor completo,
      herda o EDC/ECC provado da
      [WTE-TASK-28](/docs/tasks/28-import-de-mcr.md); se for payload, não se
      aplica. Barato de responder agora, caro de descobrir tarde
- [ ] **Bandeira e uniforme conferidos na tela contra o original, para os mesmos
      3 times da [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md)** — herdado
      dela em 2026-08-11, ver abaixo
- [ ] Commit no formato conventional, em inglês

### O critério de tela que veio da WTE-TASK-25

*(2026-08-11)*

A 25 pedia comparar a janela carregada contra o original para 3 times. A janela
carregada tem bandeira e uniforme, que são desta task — e esta task depende da
27, que depende da 26, que depende da 25. Ciclo. A 25 cortou o nó restringindo
a conferência dela aos campos que o grupo de carga produz (nomes, barras,
números de camisa, lista de jogadores, habilitação), e **a metade excluída caiu
aqui**.

O ciclo que restava — esta task esperando a gravação da 27, e a 27 esperando o
render daqui — morreu em 2026-08-19, quando `grabar_camisetaClick` passou a ser
desta task. `depends_on` continua `[08, 24, 27]`, e agora todos apontam para
número **menor**: a ordem numérica virou a ordem de execução.

Sem esta linha a exclusão de lá viraria buraco: os dois lados diriam "é da
outra" e ninguém conferiria. As três rotinas envolvidas são `0x00405270`
(bandeira do titular), `0x00405468` (bandeira do reserva) e `0x004056c8`
(uniforme); as duas primeiras estão inventariadas em
[`auxiliares.md`](../../wte/re/auxiliares.md), com tamanho e chamadores.

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
