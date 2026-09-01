---
id: CORR-WTE-063
title: "Correção: cara, cabelo e barba da ficha não têm dono em nenhuma das 40 tasks"
type: correção
category: escopo
status: concluído
depends_on: []
---

# CORR-WTE-063: uma exclusão de escopo sem dono nomeado

## Problema identificado

O `jugador.flechasapaClick` redesenha três bitmaps ao mexer nas setas de
aparência — `image/careto_base.bmp`, `image/pelo/pelo_<n>.bmp` e
`image/barba/barba_<n>.bmp`, pelas rotinas `0x00406fe0`, `0x00407110` e
`0x00407338` (1.414 bytes somados).

A [WTE-TASK-26](/docs/tasks/concluidos/26-handlers-de-edicao.md) as deixou de fora e
escreveu que elas **"não têm dono"**. A
[WTE-TASK-29](/docs/tasks/concluidos/29-camisa-e-bandeira-2d.md) cobre **uniforme e
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

$ grep -ciE "careto|pelo|barba" docs/tasks/29-camisa-e-bandeira-2d.md
0
```

O que elas fazem já está medido, na §5 e na §6 do
[`wte/re/assets.md`](../../../wte/re/assets.md): as três abrem o `.bmp` em `"r+b"` e
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

1. **Estender a WTE-TASK-29** para incluir os três renderizadores da ficha. O
   trabalho é do mesmo tipo que ela já prevê (escrever paleta em `.bmp` e
   recarregar), as tabelas de cor já estão localizadas — pele em `0x00423998`,
   cabelo em `0x00423a98`, barba em `0x00423b38` — e a saturação em `7` do
   `beard_style` já está registrada na §5.1 do `assets.md`;
2. **Registrar a exclusão como deliberada** na
   [WTE-TASK-35](/docs/tasks/concluidos/35-divergencias-deliberadas.md), com o efeito
   escrito: o port mostra a cara de um jogador só, e as setas de cabelo e barba
   não redesenham.

O que **não** fecha é o estado de hoje: uma exclusão que só existe como frase
dentro do log de uma task concluída.

### Arquivos

- [`docs/tasks/concluidos/29-camisa-e-bandeira-2d.md`](/docs/tasks/concluidos/29-camisa-e-bandeira-2d.md)
  ou [`docs/tasks/concluidos/35-divergencias-deliberadas.md`](/docs/tasks/concluidos/35-divergencias-deliberadas.md),
  conforme a decisão
- [`wte/re/spec/jugador.flechasapaClick.md`](../../../wte/re/spec/jugador.flechasapaClick.md)
  — a nota "sem dono" passa a apontar para o dono

---

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-18

**Resumo do que foi feito:**

**A decisão foi pedida ao usuário, como esta correção manda, e ele escolheu
registrar a exclusão na
[WTE-TASK-35](/docs/tasks/concluidos/35-divergencias-deliberadas.md)** — não estender a
WTE-TASK-29. Nenhuma das duas saídas foi tomada por conta própria.

A entrada nova traz os seis campos que a task exige. O que ela acrescenta ao
que a correção já dizia é a **razão medida**, e ela é mais forte do que "não
tem dono": as três abrem o `.bmp` em `"r+b"` (cadeia de modo em `0x004249cd`),
dão `fseek` para a entrada 10 da paleta (`0x5e` = 54 + 10 × 4) e **regravam a
paleta dentro do arquivo de asset**. Como `pelo_<n>.bmp` e `barba_<n>.bmp` são
compartilhados por todos os jogadores e o `make -C wte assets` liga a pasta do
`we-team-editor/` do usuário, reproduzir isso poria o porte gravando na pasta
de dados dele a cada clique numa seta.

Que a gravação acontece de verdade não precisou de teste destrutivo: a §6.1 do
`assets.md` lê o `mtime` dos 198 `.bmp` — 176 de 2002, 19 de 2006 — e acha
**três** reescritos no mesmo segundo de 2026-08-05, a primeira sessão de
`make wte` nesta máquina, com o tamanho intacto.

**O campo "onde o teste sabe" saiu honesto:** nenhuma régua alcança o
formulário `jugador`, então esta entrada **não** pede exceção nomeada em lugar
nenhum. O `compara_tela.py` mede a janela do `MainForm` e os três modos do
`compara_tela.sh` partem dali; o `check_edicao.py` já registra, para os
handlers da ficha, *"sub-dialogo que nenhuma regua de tela alcanca"*. Inventar
ferramenta aqui seria pior do que dizer que não há.

**Duas coisas que a decisão tornou falsas foram consertadas na mesma
passagem**, e as duas atribuíam à WTE-TASK-29 trabalho que ela não vai mais
ter:

- o título da seção da spec (*"A saturação em `7` que a WTE-TASK-29 vai
  herdar"*) e a §5.1 do `assets.md`. **A saturação sobrevive à decisão** e
  muda de dono, não some: ela mora no `TUpDown`, que o port já tem, e o 7 que
  vira 6 chega ao disco pela gravação — logo é da **WTE-TASK-27**. Não
  desenhar a barba não faz o 7 parar de virar 6;
- a §6.2 recomendava recolorir em memória "para a WTE-TASK-29". A
  recomendação continua valendo para os **dois** renderizadores do `MainForm`
  e caducou para os **três** da ficha, que não serão implementados.

**Problemas encontrados:**

O `veredito: aberto` da spec do `flechasapaClick` ficou como estava, de
propósito: quem o revisa é a passagem de veredito, e mudá-lo aqui seria decidir
coisa que esta correção não decide. O que mudou é que a razão escrita ali —
*falta de dono* — deixou de valer, e isso está dito no arquivo.

**Arquivos criados/modificados:**

- `docs/tasks/concluidos/35-divergencias-deliberadas.md` — a candidata, com os seis campos
- `wte/re/spec/jugador.flechasapaClick.md` — a nota "sem dono" vira nota com
  dono, mais o título da seção da saturação
- `wte/re/assets.md` — §5.1 e §6.2, as duas atribuições que caducaram
- `docs/tasks/concluidos/26-handlers-de-edicao.md` — a pendência encaminhada, fechada
