---
id: PAR-TASK-09
title: "Ciclo de vida da janela"
type: verificação
category: ui
projeto: newWe2002
depends_on: []
status: pendente
---

# PAR-TASK-09: Ciclo de vida da janela

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.10.
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

- [ ] Cancelar o diálogo de abertura
- [ ] Abrir arquivo com tamanho errado → aviso, e carrega
- [ ] `CMB_RELOAD` depois de editar → descarta as edições
- [ ] `Return` na janela principal não pode disparar nada
- [ ] `Escape` fecha

O quarto item é guarda de regressão com história: dentro de um `QDialog` o Qt
torna todo botão auto-default, e num diálogo com 86 botões e nenhum
`DEFPUSHBUTTON` o `Return` clicaria o primeiro da ordem de tabulação — um dos
candidatos aplica formação predefinida sobre o time selecionado. O `rc2ui.py`
emite `autoDefault=false` por isso. **Este item é o que impede a emenda de
apodrecer em silêncio.**

O segundo confirma que o aviso de "não tem 474.431.328 bytes" é só aviso: o
original carrega assim mesmo, e o port tem de carregar também.

---

## Definição de pronto

- [ ] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.10
- [ ] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [ ] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*
