---
id: PAR-TASK-02
title: "Números de camisa e o clamp em 32"
type: verificação
category: core
projeto: newWe2002
depends_on: ["PAR-TASK-01"]
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.2"
status: concluído
---

# PAR-TASK-02: Números de camisa e o clamp em 32

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.2.
- **Projeto:** `newWe2002` (port Qt do `ed.exe`), **não** o `wte/` Lazarus.

---

## Método

O mesmo para toda a série, e é o que a §8 do inventário já fixa: **fazer a
mesma coisa no `ed.exe` sob Wine e no port, gravar as duas cópias e comparar
com `tools/golden_compare.py`.**

```sh
cp roms/ptbr-remaster.bin  "$SCRATCH/v.bin"
DISPLAY=:98 ./build/src/app/newWe2002 "$SCRATCH/v.bin"
```

**Critério de aprovação:** a única divergência é `405724..405739`, o slot 64 do
array de 63. Qualquer outra faixa é achado, e vira CORR.

**Sempre sobre cópia, sempre no `:98`.** O `roms/` nunca é alvo. Feche qualquer
editor aberto no display antes: os dois lados acham o diálogo principal pelo
tamanho, e uma janela esquecida é dirigida no lugar da que está sob teste.

**A imagem preferida desta série é a `ptbr-remaster.bin`.** Ela é a única com
oráculo vivo nos dois editores e com os ramos do codec exercitados — medido na
[PROPOSTA-IMAGEM-GOLDEN](/docs/PROPOSTA-IMAGEM-GOLDEN.md) §8.4. Onde o item
pedir nome latino legível, é ela; onde pedir kanji, a `japanese-shift-jis.bin`.

---

## Itens a conferir

- [x] Digitar 33 numa seleção → tem que virar 32 na tela e no disco —
      `tools/par/8.2-clamp-selecao.sh`
- [x] Digitar num clube de ML (sem clamp) e conferir —
      `tools/par/8.2-clamp-clube-ml.sh`
- [x] `CMD_DEFAULT_NUMBERS` e conferir que o `number` do jogador seguiu —
      reprovou aqui, e foi fechado pela
      [CORR-WTE-124](/docs/tasks/CORR-WTE-124.md);
      roteiro em `tools/par/8.2-numeros-default.sh`

O clamp existe só na seleção nacional; no clube de ML não há. A assimetria é do
original e tem de ser reproduzida, não corrigida.

`SquadNumbers` usa bitfields `std::uint32_t` — **não** `DWORD`. No Linux LP64 um
`DWORD` teria 64 bits e embaralharia todos os números. Se algo sair torto aqui,
é a primeira suspeita.

---

## Definição de pronto

- [x] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.2
- [x] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [x] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico — foi a [CORR-WTE-124](/docs/tasks/CORR-WTE-124.md)
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-28 — parcial, 2 de 3 itens. **Fechada em
2026-08-29**, quando a [CORR-WTE-124](/docs/tasks/CORR-WTE-124.md) corrigiu o
terceiro.

**Resumo:**

Itens 1 e 2 fechados, com `golden_check.sh` em modo `gui` saindo
`OK: identico ao oraculo, exceto o slot 64 conhecido` e controle positivo
mostrando o estímulo no disco. O item 3 **reprovou** e virou
[CORR-WTE-124](/docs/tasks/CORR-WTE-124.md).

**O que se aprendeu:**

**O campo guarda `número − 1`.** Digitar 33 numa seleção mostra 32 na tela e
grava 31 — que é o teto, logo o clamp existe. No clube de ML o mesmo 33 grava
32. A assimetria que o item pede está medida nos dois sentidos, e sem o
`dump_estado` ela não apareceria: byte cru não decodifica bitfield empacotado, e
lê-lo à mão dava 63, um número que não significa nada.

**Botão que abre modal precisa de dispensa explícita no roteiro**, e essa é a
lição que vale para toda a série. Sem ela a caixa fica na frente do `CMB_WRITE`,
o clique de gravar não chega, e o `wait_for_window` do `golden_gui.sh` toma a
caixa pela confirmação: imprime "gravado" e o arquivo sai **intacto**. Os dois
lados fazem isso, então o golden fica verde sem ter medido nada — a mesma
família do verde vazio da [PAR-TASK-01](/docs/tasks/PAR-TASK-01.md), por outra
causa.

**`Return` não dispensa modal do MFC sob Wine.** Fecha a `QMessageBox` do port e
deixa a do oráculo em pé — medido em captura. O efeito é pior que não dispensar:
o port grava e o oráculo não, e o golden acusa faixas que parecem bug do port.
O que funciona nos dois é clicar no botão; a caixa do oráculo mede 148×82 e o
`OK` fica no centro horizontal a **~40% da altura**, não junto à base — a
primeira tentativa mirou a base e errou o alvo.

> **Isto vale só para o oráculo.** A `QMessageBox` do port mede **188×100** e
> tem o `OK` a ~77% da largura e ~75% da altura — medido na
> [CORR-WTE-124](/docs/tasks/CORR-WTE-124.md). Um roteiro que use só o ponto
> acima clica no texto do port, a caixa fica em pé e engole o clique de gravar.
> O `tools/par/8.2-numeros-default.sh` tenta os dois pontos em ordem.

**Problemas encontrados:**

O item 3 reprovou de verdade: 18 divergências, reprodutíveis **sem** seleção de
time, com o modal comprovadamente dispensado nos dois lados e sem clique perdido
no lado Qt. Os três descartes estão na CORR. Como a causa não foi diagnosticada
dentro do escopo desta task, ela fica pendente e a task **não** é marcada como
concluída.

**Arquivos criados/modificados:**

- `docs/PARIDADE-FUNCIONAL.md` — os dois itens conferidos e a nota do modal
- `docs/tasks/CORR-WTE-124.md` — o achado do item 3
- `docs/tasks/correcoes-progresso.md` — a linha e o checklist da CORR
- `docs/tasks/PAR-TASK-02.md` — este Log

**Adendo da [CORR-WTE-124](/docs/tasks/CORR-WTE-124.md), 2026-08-29.** O item 3
foi diagnosticado e corrigido: o `OnDefaultNumbers` do port ia aos 64 slots do
array de times em vez dos 63 times reais, e a 64ª volta escrevia
`players[1911..1933]` — fora de `players[]`, em cima de `teams[]`, que **é**
gravado na imagem. O original faz o mesmo estouro, mas ali o vizinho é
`gioc_fifa[]`, que não vai para o disco: a 64ª volta não tem efeito observável.
Com o laço em 63 o golden sai `OK`. O roteiro do item ficou versionado em
`tools/par/8.2-numeros-default.sh`, com a dispensa da caixa que funciona nos
dois lados — o `OK` fica em lugar diferente em cada um.

**Adendo da [CORR-WTE-126](/docs/tasks/CORR-WTE-126.md), 2026-08-29.** Os itens
1 e 2 tinham sido medidos em 2026-08-28, no mesmo dia em que a
[CORR-WTE-123](/docs/tasks/CORR-WTE-123.md) criou o `tools/par/`, e ficaram sem
roteiro versionado — a §8.2 era a única seção fora da convenção. Os dois foram
escritos e **remedidos**: seleção `0 → 31` no `squad_numbers[0]` e `1 → 32` no
`players[462].number`, clube de ML `0 → 32` no `raw_numbers[0]`, iguais nos
dois lados, com o golden `OK` nos dois. A §8.2 passou a trazer também a
invocação do `dump_estado` que decodifica o bitfield — sem ela os dois números
não têm fonte re-executável, porque byte cru ali dá 63.
