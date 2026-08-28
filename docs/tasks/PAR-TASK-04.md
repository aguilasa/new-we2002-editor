---
id: PAR-TASK-04
title: "Atributos do jogador e os clamps"
type: verificação
category: core
projeto: newWe2002
depends_on: ["PAR-TASK-01"]
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.4"
status: pendente
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

- [x] Clampar habilidade abaixo de 12 e acima de 19
- [ ] Altura 100 e 999; idade 1 e 99; número 0 e 99
- [ ] Custo com mais de 2 dígitos — conferir que o original também trunca
- [ ] Trocar os 10 combos com mouse **e** com teclado
- [ ] Editar nome de jogador (é aqui que se edita, não no diálogo principal)

O terceiro item é o que mais engana: a suspeita natural é que o truncamento seja
defeito do port. **Meça o original antes de mexer** — os 198 `strcpy` em buffer
fixo herdados fazem truncamento que pode ser load-bearing no formato.

O quarto cobre mouse e teclado porque são caminhos de sinal diferentes no Qt, e
só um deles passa pelo `eventFilter` da PAR-TASK-03.

---

## Definição de pronto

- [ ] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.4
- [ ] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [ ] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-28 — **PARCIAL: 1 de 5 itens.**

**Resumo:**

O item 1 fechou: `golden_check.sh` em modo `gui` saiu
`OK: identico ao oraculo, exceto o slot 64 conhecido`, e o controle positivo
mostra `OFS_PLAYER_ATTR+7` com 2 bytes. O clamp foi medido **nos dois
extremos numa corrida só**: 25 digitado em `attack` grava 19, 3 digitado em
`defence` grava 12.

Os outros quatro itens **não foram executados** — o lote de três tarefas
(PAR-TASK-02, 03 e 04) consumiu o orçamento nas duas primeiras, que renderam
duas CORRs. Não há nada medido sobre eles; ficam abertos como estavam.

**O que se aprendeu, e vale para quem retomar:**

**O `PlayerSkillsDialog` é janela própria, de 493×323 px**, e as coordenadas
dos 21 campos do `controls.json` são relativas **a ele**, não ao `MainDialog` —
o roteiro precisa de `--window "$SKILLS"`, com a janela achada por tamanho, como
o `skills_win()` do roteiro faz. `CMD_SKILLS1` fica em dlu (392,36) no
`MainDialog` e `Escape` fecha o diálogo.

**Problemas encontrados:** nenhum no item executado.

**Arquivos criados/modificados:**

- `docs/PARIDADE-FUNCIONAL.md` — o item 1 da §8.4
- `docs/tasks/PAR-TASK-04.md` — este Log
