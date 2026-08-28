---
id: PAR-TASK-01
title: "Nomes e abreviações de time, pela tela"
type: verificação
category: ui
projeto: newWe2002
depends_on: []
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.1"
status: pendente
---

# PAR-TASK-01: Nomes e abreviações de time, pela tela

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.1.
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

- [ ] Editar os 6 slots de nome de uma seleção; conferir que o `(n)` de cada
      rótulo bate com o truncamento real
- [ ] Editar kanji e caixa mista
- [ ] Editar as 3 abreviações
- [ ] `CMD_COPY_TEAM_NAMES` numa seleção e num clube de ML — conferir o quirk do
      comprimento kanji (§3.3)
- [ ] Repetir num clube de ML, incluindo os dois nomes extras

### Por que esta é a primeira

Três razões que convergem:

1. **É onde bug já apareceu.** A [CORR-WTE-121](/docs/tasks/CORR-WTE-121.md)
   corrigiu, no port Lazarus, três faixas de gravação de nome de time
   (`OFS_TEAM_NAME_KANJI_A`, `OFS_TEAM_MIXED_CASE_NAME`, `OFS_TEAM_NAME_6_B`).
   Mesma família de campo, mesmos quirks de sobra de buffer — e no `newWe2002`
   essa área nunca foi conferida pela tela.
2. **Fecha o item aberto do Windows.** A [PAR-TASK-10](/docs/tasks/PAR-TASK-10.md)
   é o mesmo trabalho na outra plataforma, e lá está bloqueado; aqui não há
   Citrix filtrando input.
3. **A régua está pronta.** O `golden_gui` aceita `GOLDEN_EDIT` e rodou nas três
   imagens em 2026-08-27.

**Atenção ao `Ctrl+A`.** Ele **não** seleciona tudo num `CEdit` do Win32: limpe
o campo com `End`, `shift+Home`, `BackSpace` nos dois lados, senão os dois
recebem textos diferentes e o diff acusa divergência que não existe.

---

## Definição de pronto

- [ ] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.1
- [ ] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [ ] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*
