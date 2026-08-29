---
id: PAR-TASK-06
title: "Táticas, presets e o formato `.t2002`"
type: verificação
category: ui
projeto: newWe2002
depends_on: ["PAR-TASK-03"]
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.7"
status: pendente
---

# PAR-TASK-06: Táticas, presets e o formato `.t2002`

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.7.
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

- [ ] Clampar x em 0/48 e y em 0/112
- [ ] Trocar papel e conferir a legenda do marcador
- [x] `Escape` depois de navegar um combo de papel — **já fechado** pela
      [CORR-WTE-127](/docs/tasks/CORR-WTE-127.md), fora desta task, porque a
      divergência apareceu na revisão da
      [PAR-TASK-03](/docs/tasks/PAR-TASK-03.md): os dez combos de papel gravam
      pelo mesmo `FocusOut` dos seis de cobrador, e o `Escape` divergia igual.
      Roteiros `tools/par/8.7-escape-papel.sh` e
      `tools/par/8.7-escape-papel-sem-navegar.sh`; medição na §8.7 do
      inventário. **Não precisa ser refeito aqui** — mas se o item 2 acima
      mexer no `OnRoleShown` ou no `eventFilter`, re-rode os dois roteiros
- [ ] Aplicar os 16 presets num time
- [ ] Editar e renomear um preset no `DefaultTacticsDialog`
- [ ] Exportar `.t2002`, importar de volta, e importar um `.t2002` do original

O quinto item é o mais valioso da série inteira: **troca de arquivo nos dois
sentidos** entre port e original é a prova de formato mais forte que existe
fora do golden test.

Os `TXT_TATX/TATY` usam `textChanged`, não `textEdited`, porque `EN_CHANGE`
disparava em `SetWindowText` e é o que move os marcadores do campinho ao trocar
de time. Não "otimize" isso ao mexer aqui.

Cuidado ao aplicar preset: num diálogo com 86 botões e nenhum `DEFPUSHBUTTON`,
`Return` já foi capaz de disparar ação arbitrária — daí `autoDefault=false` nos
`PUSHBUTTON`. A PAR-TASK-09 mede isso de propósito.

---

## Definição de pronto

- [ ] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.7
- [ ] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [ ] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*
