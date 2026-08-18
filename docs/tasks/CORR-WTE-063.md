---
id: CORR-WTE-063
title: "Correção: cara, cabelo e barba da ficha não têm dono em nenhuma das 40 tasks"
type: correção
category: escopo
status: pendente
depends_on: []
---

# CORR-WTE-063: uma exclusão de escopo sem dono nomeado

## Problema identificado

O `jugador.flechasapaClick` redesenha três bitmaps ao mexer nas setas de
aparência — `image/careto_base.bmp`, `image/pelo/pelo_<n>.bmp` e
`image/barba/barba_<n>.bmp`, pelas rotinas `0x00406fe0`, `0x00407110` e
`0x00407338` (1.414 bytes somados).

A [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) as deixou de fora e
escreveu que elas **"não têm dono"**. A
[WTE-TASK-32](/docs/tasks/32-camisa-e-bandeira-2d.md) cobre **uniforme e
bandeira do `MainForm`** — e não menciona cara, cabelo nem barba em nenhuma
linha.

O enunciado da própria 26 diz, sobre outra exclusão: *"Exclusão sem dono nomeado
é buraco, e este projeto já pagou por isso na 25."* Esta é uma, e ela atravessou
o fechamento da task.

## Evidência

Nenhuma task além da que as excluiu menciona os três endereços:

```
$ grep -rl "0x00406fe0\|0x00407110\|0x00407338" docs/tasks/*.md
docs/tasks/26-handlers-de-edicao.md

$ grep -ciE "careto|pelo|barba" docs/tasks/32-camisa-e-bandeira-2d.md
0
```

O que elas fazem já está medido, na §5 e na §6 do
[`wte/re/assets.md`](../../wte/re/assets.md): as três abrem o `.bmp` em `"r+b"` e
**regravam a paleta dentro do arquivo de asset** antes de recarregá-lo. Mexer
numa seta de cabelo altera o arquivo que todos os jogadores compartilham — e a
marca disso está no `mtime` da pasta do usuário.

O efeito visível hoje: as setas de aparência **mudam o rótulo e não mudam o
desenho**, o que é diferente de "não implementado" e não se anuncia.

## Causa raiz

A 26 é dona de **handler**, não de **asset**. A 32 é dona de asset, mas foi
escrita para os dois do `MainForm`. Cara, cabelo e barba caem entre as duas
definições, e nenhuma das duas errou ao não os pegar.

## Correção

**A decisão é do usuário, e esta correção existe para pedi-la** — não para
tomá-la. Duas saídas, e as duas fecham:

1. **Estender a WTE-TASK-32** para incluir os três renderizadores da ficha. O
   trabalho é do mesmo tipo que ela já prevê (escrever paleta em `.bmp` e
   recarregar), as tabelas de cor já estão localizadas — pele em `0x00423998`,
   cabelo em `0x00423a98`, barba em `0x00423b38` — e a saturação em `7` do
   `beard_style` já está registrada na §5.1 do `assets.md`;
2. **Registrar a exclusão como deliberada** na
   [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md), com o efeito
   escrito: o port mostra a cara de um jogador só, e as setas de cabelo e barba
   não redesenham.

O que **não** fecha é o estado de hoje: uma exclusão que só existe como frase
dentro do log de uma task concluída.

### Arquivos

- [`docs/tasks/32-camisa-e-bandeira-2d.md`](/docs/tasks/32-camisa-e-bandeira-2d.md)
  ou [`docs/tasks/35-divergencias-deliberadas.md`](/docs/tasks/35-divergencias-deliberadas.md),
  conforme a decisão
- [`wte/re/spec/jugador.flechasapaClick.md`](../../wte/re/spec/jugador.flechasapaClick.md)
  — a nota "sem dono" passa a apontar para o dono
