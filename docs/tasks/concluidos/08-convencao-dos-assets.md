---
id: WTE-TASK-08
title: "Convenção de nome dos 198 bitmaps e do dat.bin"
type: extração
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-05"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md §1.8 e Fase 1 item 6"
status: concluído
---

# WTE-TASK-08: Convenção dos assets

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §1.8 e Fase 1 item 6.
- Os assets **não precisam ser revertidos** — são BMP em formato aberto, já no
  disco. O que falta é a convenção que liga nome de arquivo a índice de jogo.

```
image/banderas/       53 .bmp    bandera0..bandera60, com buracos
image/uniformes2d/   105 .bmp
image/pelo/           32 .bmp    cabelo
image/barba/           7 .bmp
image/careto_base.bmp  1 .bmp    base do rosto
data/dat.bin     145.408 B       comeca com "MC"
```

**Os números têm buracos.** `banderas/` vai de `bandera0` a `bandera60` mas tem
53 arquivos — faltam sete. Se o app indexa direto, ele tem de lidar com ausência;
se indexa por tabela, a tabela está no `.exe`.

---

## Objetivo

Responder, com evidência, como cada família é endereçada.

### 1. Bandeiras

Índice direto (`bandera<N>.bmp` para o time N) ou tabela? Os buracos sugerem que
alguns times compartilham bandeira ou usam a bandeira própria da imagem de CD —
o plano já registra que o `newWe2002` tem um teste de "tem bandeira própria".
Cruzar com `OFS_FLAG_SHAPE_COPY_1..5`, que estão entre os 19 offsets
confirmados.

### 2. Uniformes 2D

105 arquivos para quantos times? Descobrir se o índice é por time, por modelo de
camisa, ou por combinação. É a base da WTE-TASK-29.

### 3. Cabelo, barba e `careto_base`

Aparência de jogador. `careto` é "cara" em espanhol coloquial. Conferir se o
índice casa com algum campo de `Player`.

### 4. `dat.bin`

Começa com `MC` — cabeçalho de memory card do PSX. Confirmar se é memory card
de exemplo (e então é fixture da WTE-TASK-28) ou banco de dados próprio do
editor. 145.408 bytes contra os 131.072 de um memory card padrão: os 14.336 de
diferença precisam de explicação.

### Método

Preferir **observação** a leitura de assembly: abrir o original no Wine, trocar
de time, e ver qual bitmap aparece. Renomear um arquivo e ver o que quebra é
teste destrutivo barato — em cópia da pasta, nunca na original.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/assets.md` | criar |

---

## Critério de conclusão

- [x] Convenção das bandeiras resolvida, buracos explicados
- [x] Convenção dos 105 uniformes resolvida
- [x] Cabelo/barba/`careto_base` ligados ao campo de `Player` que os seleciona
- [x] `dat.bin` classificado, e os 14.336 bytes de diferença explicados
- [x] Nenhum teste rodado sobre a pasta original
- [x] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-06

- **Resumo do que foi feito:**

  Criado [`wte/re/assets.md`](../../../wte/re/assets.md). **Rota escolhida: comando
  inline, sem gerador** — o produto são ~15 medidas e um texto que as amarra, não
  uma enumeração; cada número traz o comando que o reproduz, como a CORR-WTE-002
  exigiu do `ambiente.md`. As três tabelas de 95 entradas, que *são* enumeráveis,
  ficam com o comando de extração no `.md` para a WTE-TASK-29 decidir se viram
  TSV.

  Achados principais:

  - **Bandeira é forma, não país.** `bandera<n>.bmp` é um estêncil de 20×16 com
    16 cores úteis; a cor sai da imagem de CD. Agrupar a tabela de 95 bytes em
    `0x004231e8` por valor mostra tricolor vertical, tricolor horizontal, cruz
    nórdica. Casa com o nome `OFS_FLAG_SHAPE_COPY_*` que o `newWe2002` já usa.
  - **Os buracos são oito (44..51), não sete** — 61 − 53 = 8. E não são buracos:
    o conjunto usado pela tabela é exatamente o conjunto em disco, e o combo
    `ficha_color.lista_col0` indexa a tabela, então índice ausente é
    inalcançável.
  - **Uniformes por tabela**, `0x004232a6`, 95 × 4 bytes = 2 jogos ×
    {camiseta, pantalon}. Cobre as 99 camisas e os 6 calções sem sobra. Times
    0..62 usam `camiseta0..49` (40 px), 63..94 usam `camiseta50..98` (51 px).
  - **Cabelo/barba/rosto** vêm de `Player::hair_style` / `beard_style` /
    `skin_colour` / `hair_colour` / `beard_colour`, que o `we2002_core` já
    decodifica, pela via dos `TUpDown` `flechasapa2..6`.
  - **O app grava dentro dos `.bmp`** (`fopen` em `"r+b"`, reescrita da paleta).
    Confirmado pelo `mtime`: três arquivos da pasta do usuário datam da sessão de
    `make wte` de 2026-08-05, com tamanho intacto; os outros 195 são de 2006.
  - **`dat.bin` são dois blobs**: `[0..0x1FFFF]` é molde de memory card copiado
    por `grabar_memoryClick`; os 14.336 bytes restantes são 7 setores injetados
    **na imagem de CD** em `0x2e08` ao abri-la, com sentinela `0xfc` em `0x2e14`.
  - **Resolução de caminho por `GetCurrentDir()`**, não pelo diretório do
    executável — a ordem acordada na decisão 1 do `wte/README.md` é divergência
    deliberada.
  - **198 é o número certo**; a §1.8 do plano lista as cinco linhas corretas e
    erra a soma na prosa ("197 bitmaps"). Reconciliação é da WTE-TASK-09.
  - **41 dos 45 `TImage`** dos DFM trazem bitmap embutido, mas isso não dispensa
    nenhum dos 198 arquivos: os blobs de `imagen_base`, `imagen_pelo`,
    `imagen_barba`, `home1` e `home2` são placeholder de IDE, sobrescritos em
    runtime.

  Nenhuma ferramenta criada, logo nenhum `tools/test_*.py` novo. `make -C wte
  check` rodado assim mesmo, como guarda de regressão: 76 testes e os cinco
  `--check` verdes.

- **Arquivos criados/modificados:**
  - `wte/re/assets.md` — criado
  - `docs/tasks/concluidos/08-convencao-dos-assets.md` — critérios e este log

- **Problemas encontrados:**
  - A coluna `handler` do `strings.tsv` está vazia para as seis strings de asset.
    **Não é falha**: os sítios estão em auxiliares não publicados
    (`sub_405270`, `sub_4056c8`, …), fora dos 96 corpos delimitados pela
    WTE-TASK-04. O dono publicado é o chamador, e o `assets.md` o nomeia.
  - A ordem dos campos publicados do C++Builder **não** é a ordem do DFM quando
    há aninhamento — calibrar por ela produz contradição. Os nomes de `TImage`
    alvo foram amarrados por dimensão (as alturas 42 e 22 de `home1`/`home2`
    batem exatamente com `camiseta`/`pantalon`) e por vizinhança de campo.
  - `beard_style` cabe 0..7 no disco e só existem `barba_0..6`; o original
    satura em 6 via `TUpDown::Position`. Anotado para a WTE-TASK-29.
