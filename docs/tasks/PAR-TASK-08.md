---
id: PAR-TASK-08
title: "Operações em massa"
type: verificação
category: core
projeto: newWe2002
depends_on: ["PAR-TASK-04", "PAR-TASK-07"]
status: pendente
---

# PAR-TASK-08: Operações em massa

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.9.
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

- [ ] `CMD_SORT_RESERVES` numa seleção e num clube (a ordem torta é a certa).
      **O botão é invisível nos dois** — exige build de teste com o controle
      visível dos dois lados; não commitar
- [ ] Clube com 1 goleiro na reserva × com 2
- [ ] `CMD_UPDATE_COSTS`
- [ ] `CMB_EDITALLLOOK`
- [ ] `CMB_EDITALLBARS` — conferir que 57..63 ficaram intactos

**O primeiro item exige build descartável dos dois lados**, e o enunciado é
explícito: não commitar. O `ed.exe` precisa do controle visível também, o que
significa editar o `.rc` e recompilar com MSVC — se isso não for viável, o item
fica registrado como não-medido, com a razão. Não invente medição por outro
caminho.

`CMD_SORT_RESERVES` tem uma **divergência deliberada** da Fase 5: o swap fora do
array. A "ordem torta é a certa" do enunciado se refere a isso — conferir contra
o oráculo, não contra o que parece ordenado.

---

## Definição de pronto

- [ ] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.9
- [ ] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [ ] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*
