---
id: PAR-TASK-10
title: "O item aberto do Windows: nome de time pela janela Qt"
type: verificação
category: verificação
projeto: newWe2002
depends_on: ["PAR-TASK-01"]
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.11"
status: bloqueado
---

# PAR-TASK-10: O item aberto do Windows: nome de time pela janela Qt

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.11.
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

- [ ] Editar nome de time pela janela Qt no Windows e comparar com o
      `Debug\ed.exe` nativo

**Está bloqueado, e o bloqueio é da máquina, não do código.** A Citrix filtra
input sintético e a UIA do Qt não expõe os itens do combo de forma estável — §5.3
e §11 do [/docs/PLAN-WINDOWS.md](/docs/PLAN-WINDOWS.md).

O que a [PAR-TASK-01](/docs/tasks/concluidos/PAR-TASK-01.md) entrega no Linux é a mesma
medição sem esse filtro. Esta task existe para decidir uma de três, **depois**
que a 01 fechar:

1. dirigir por **mensagem de janela** em vez de input sintético — é o que o
   `CLAUDE.md` recomenda para o Windows, e o que funcionou com o `ed.exe`;
2. aceitar a medição do Linux como suficiente e registrar o porquê, já que o
   `.exe` do MSVC já grava os mesmos bytes que o do GCC nas duas imagens;
3. mantê-la aberta com o bloqueio nomeado.

**Não** vale forçar `SendInput`, `SetCursorPos` ou `click_input`: os três já
foram medidos como filtrados nesta máquina.

---

## Definição de pronto

- [ ] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.11
- [ ] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [ ] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*
