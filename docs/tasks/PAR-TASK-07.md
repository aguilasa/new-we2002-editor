---
id: PAR-TASK-07
title: "Bandeira, uniformes e os times sem bandeira própria"
type: verificação
category: ui
projeto: newWe2002
depends_on: ["PAR-TASK-01"]
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.8"
status: pendente
---

# PAR-TASK-07: Bandeira, uniformes e os times sem bandeira própria

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.8.
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

- [ ] Cores no teto (65535) e acima
- [ ] Time sem bandeira própria (57..63, 69, 86 e o 56) → caixas desabilitadas e
      import/export recusado
- [ ] `.b2002` e `.m2002`: exportar do port e importar no `ed.exe`, e vice-versa

O segundo item carrega uma **divergência deliberada** da Fase 5: o port usa teste
único de "tem bandeira própria" onde o original repetia a condição. Ela está na
lista de divergências aceitas do [/docs/PLAN-LINUX.md](/docs/PLAN-LINUX.md) e
não aparece nos golden tests — este item é onde ela finalmente se mede na tela.

O terceiro é ida e volta de arquivo, como o `.t2002` da PAR-TASK-06.

---

## Definição de pronto

- [ ] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.8
- [ ] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [ ] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*
