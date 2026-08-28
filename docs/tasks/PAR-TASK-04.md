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

- [ ] Clampar habilidade abaixo de 12 e acima de 19
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

## Log de Execução *(preenchido após execução)*
