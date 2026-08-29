---
id: PAR-TASK-04
title: "Atributos do jogador e os clamps"
type: verificação
category: core
projeto: newWe2002
depends_on: ["PAR-TASK-01"]
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.4"
status: concluído
---

# PAR-TASK-04: Atributos do jogador e os clamps

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.4.
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

Cada um sobre o `tools/par/8.4-prelude.sh`, que abre o `PlayerSkillsDialog` e
não roda sozinho:

- [x] Clampar habilidade abaixo de 12 e acima de 19 — `tools/par/8.4-habilidade.sh`
- [x] Altura 100 e 999; idade 1 e 99; número 0 e 99 —
      `tools/par/8.4-limites-fisicos.sh`
- [x] Custo com mais de 2 dígitos — conferir que o original também trunca —
      `tools/par/8.4-custo.sh`
- [x] Trocar os 10 combos com mouse **e** com teclado — `tools/par/8.4-combos.sh`
- [x] Editar nome de jogador (é aqui que se edita, não no diálogo principal) —
      `tools/par/8.4-nome-jogador.sh`

O terceiro item é o que mais engana: a suspeita natural é que o truncamento seja
defeito do port. **Meça o original antes de mexer** — os 198 `strcpy` em buffer
fixo herdados fazem truncamento que pode ser load-bearing no formato.

O quarto cobre mouse e teclado porque são caminhos de sinal diferentes no Qt, e
só um deles passa pelo `eventFilter` da PAR-TASK-03.

---

## Definição de pronto

- [x] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.4
- [x] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [x] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico — **nenhuma apareceu nesta seção**
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-28 (item 1) e 2026-08-29 (itens 2 a 5) — **COMPLETA, 5 de 5.**

**Resumo:**

O item 1 fechou: `golden_check.sh` em modo `gui` saiu
`OK: identico ao oraculo, exceto o slot 64 conhecido`, e o controle positivo
mostra `OFS_PLAYER_ATTR+7` com 2 bytes. O clamp foi medido **nos dois
extremos numa corrida só**: 25 digitado em `attack` grava 19, 3 digitado em
`defence` grava 12.

Os outros quatro fecharam em 2026-08-29, cada um com golden verde e controle
positivo. **Nenhuma divergência nova nesta seção** — os cinco itens saem
idênticos ao oráculo.

Todo campo deste diálogo clampa, e os limites saíram medidos: altura
`155..210`, idade `15..46`, número com teto 32 (o mesmo da §8.2) e piso 1,
habilidade `12..19`, custo truncado em 2 dígitos, nome em 10 caracteres. Dos
dez combos, nove avançam exatamente uma posição com `Down`+`Return`; o décimo
(`out_of_position`) fica parado **nos dois lados**, por já estar no último item
de um combo YES/NO — parada idêntica é paridade, não item por medir.

**O que se aprendeu, e vale para quem retomar:**

**O `PlayerSkillsDialog` é janela própria, de 493×323 px**, e as coordenadas
dos 21 campos do `controls.json` são relativas **a ele**, não ao `MainDialog` —
o roteiro precisa de `--window "$SKILLS"`, com a janela achada por tamanho, como
o `skills_win()` do roteiro faz. `CMD_SKILLS1` fica em dlu (392,36) no
`MainDialog` e `Escape` fecha o diálogo.

**Problemas encontrados:** nenhum de paridade. Uma armadilha de ambiente, que
custou uma medição perdida: **o shell desta máquina é zsh**, e ali
`set -- $var` **não** faz word splitting como no bash. Um laço que montava três
cópias a partir de `"100 1 0 baixo"` produziu um único arquivo `p-.bin`, com
`$4` vazio. Em script de medição, passe os campos explicitamente.

**Arquivos criados/modificados:**

- `docs/PARIDADE-FUNCIONAL.md` — os cinco itens da §8.4 e a nota do diálogo
- `docs/tasks/PAR-TASK-04.md` — este Log e o `status`
- `docs/tasks/progresso.md` — a linha da tabela do anexo
- `tools/par/8.4-prelude.sh` — o prelúdio comum (abre o `PlayerSkillsDialog`)
- `tools/par/8.4-limites-fisicos.sh`, `8.4-custo.sh`, `8.4-combos.sh`,
  `8.4-nome-jogador.sh` — um roteiro por item

**Adendo da [CORR-WTE-128](/docs/tasks/CORR-WTE-128.md), 2026-08-29.** O item 1
tinha sido medido em 2026-08-28, no dia em que a
[CORR-WTE-123](/docs/tasks/CORR-WTE-123.md) criou o `tools/par/`, e ficou sem
roteiro — os outros quatro, do dia seguinte, já nasceram com o seu. A frase
"Roteiros em `tools/par/8.4-*.sh`" fazia a conta parecer fechada porque o
`8.4-prelude.sh` entrava no `ls`, e ele não é roteiro de item. O
`tools/par/8.4-habilidade.sh` foi escrito e o item **remedido**: `players[462]`
sai de `attack 13 / defence 17` para `19 / 12` nos dois lados, golden `OK`.
