---
id: PAR-TASK-03
title: "Cobradores, capitão e o foco de combo"
type: verificação
category: ui
projeto: newWe2002
depends_on: ["PAR-TASK-01"]
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.3"
status: pendente
---

# PAR-TASK-03: Cobradores, capitão e o foco de combo

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.3.
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

- [ ] Abrir o combo, **navegar com as setas sem sair do controle**, apertar
      ESC/clicar fora — conferir se grava ou não igual ao original
- [ ] Escolher e sair com Tab; conferir os 6 campos
- [ ] Lembrar da troca do par de cobradores a cada gravação (é esperada)

**É o bloco mais sensível a diferença de framework.** `QComboBox` não tem
`killFocus`; os combos gravavam em `CBN_KILLFOCUS` e um `eventFilter` de
`FocusOut` no `MainWindow` reproduz. E `setCurrentIndex` **dispara**
`currentIndexChanged`, enquanto `SetCurSel` não disparava `CBN_SELCHANGE` — daí
os `QSignalBlocker` nas cargas de time. O primeiro item existe para medir
exatamente essa emenda.

A troca do par de cobradores a cada gravação **é bug do original, reproduzido de
propósito**: `Load` lê o par trocado e `Save` grava na ordem declarada. Gravar
duas vezes volta ao início. Não acuse como divergência.

---

## Definição de pronto

- [ ] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.3
- [ ] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [ ] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*
