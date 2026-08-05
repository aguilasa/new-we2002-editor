---
id: WTE-TASK-08
title: "Convenção de nome dos 197 bitmaps e do dat.bin"
type: extração
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-05"]
status: pendente
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
camisa, ou por combinação. É a base da WTE-TASK-32.

### 3. Cabelo, barba e `careto_base`

Aparência de jogador. `careto` é "cara" em espanhol coloquial. Conferir se o
índice casa com algum campo de `Player`.

### 4. `dat.bin`

Começa com `MC` — cabeçalho de memory card do PSX. Confirmar se é memory card
de exemplo (e então é fixture da WTE-TASK-31) ou banco de dados próprio do
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

- [ ] Convenção das bandeiras resolvida, buracos explicados
- [ ] Convenção dos 105 uniformes resolvida
- [ ] Cabelo/barba/`careto_base` ligados ao campo de `Player` que os seleciona
- [ ] `dat.bin` classificado, e os 14.336 bytes de diferença explicados
- [ ] Nenhum teste rodado sobre a pasta original
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
