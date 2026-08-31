---
id: PAR-TASK-08
title: "Operações em massa"
type: verificação
category: core
projeto: newWe2002
depends_on: ["PAR-TASK-04", "PAR-TASK-07"]
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.9"
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

- [ ] `CMD_SORT_RESERVES`  ← **não medido: exige MSVC** numa seleção e num clube (a ordem torta é a certa).
      **O botão é invisível nos dois** — exige build de teste com o controle
      visível dos dois lados; não commitar
- [ ] Clube com 1 goleiro na reserva × com 2  ← **não medido: mesmo handler**
- [x] `CMD_UPDATE_COSTS`
- [ ] `CMB_EDITALLLOOK`  ← **reprovou, CORR-WTE-133**
- [x] `CMB_EDITALLBARS` — conferir que 57..63 ficaram intactos

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

## Log de Execução

**Executado em:** 2026-09-01 — **PARCIAL: 2 de 5 fechados, 1 reprovado, 2 não
mensuráveis nesta máquina.**

**Resumo:**

| item | resultado |
|---|---|
| `CMD_SORT_RESERVES` | **não medido** — botão `NOT WS_VISIBLE` nos dois; exige MSVC |
| 1 goleiro × 2 | **não medido** — mesmo handler do anterior |
| `CMD_UPDATE_COSTS` | golden `OK` |
| `CMB_EDITALLLOOK` | **reprovou** — 92 bytes, [CORR-WTE-133](/docs/tasks/CORR-WTE-133.md) |
| `CMB_EDITALLBARS` | golden `OK`, e 57..63 intactos |

**Os dois não medidos, e por que não se inventou caminho.** O enunciado é
explícito: *"se isso não for viável, o item fica registrado como não-medido,
com a razão. Não invente medição por outro caminho."* O `.rc` confirma o
`NOT WS_VISIBLE` (`CMD_CALCFORZA2`), e tornar o controle visível **no lado do
`ed.exe`** exigiria editar o `.rc` e recompilar com MSVC + MFC estático, o que
o `CLAUDE.md` registra como impossível aqui. O item 2 cai junto porque é o
mesmo `OnSortReserves` — o comentário do handler descreve exatamente o caso de
um goleiro só.

**O que se aprendeu, e custou três corridas erradas:**

**Nem toda operação em massa abre a caixa `"Operation done!"`, e os dois lados
discordam sobre quais.** O `CMD_UPDATE_COSTS` abre nos dois; o
`CMB_EDITALLBARS` abre **só no port** e não no `ed.exe`. Isso quebra as duas
soluções óbvias: sem dispensar, o port não grava; dispensando com o
`dispensa_modal` da §8.2, o **oráculo** deixa de gravar. Um `Return` seco
resolve os dois.

**E o `dispensa_modal` é ativamente perigoso no lado do Wine.** Os controles do
MFC ali são janelas X de verdade, e vários caem na faixa que o `acha_modal`
procura (206×80, 148×82). Sem caixa na tela, ele acha um **controle**, clica
nele, e a gravação não acontece: a cópia sai `IDENTICAL` enquanto o port grava,
e o golden acusa o port por uma divergência que é do roteiro. Foi o que
produziu, em sequência, um vermelho falso e depois um **verde vazio** — os dois
lados sem gravar, saindo iguais.

**Problemas encontrados:** o item 4, acima. A task fica aberta.

**Arquivos criados/modificados:**

- `docs/PARIDADE-FUNCIONAL.md` — os cinco itens da §8.9 e a nota dos modais
- `docs/tasks/CORR-WTE-133.md` e `docs/tasks/correcoes-progresso.md` — o achado
- `docs/tasks/PAR-TASK-08.md` — este Log
- `tools/par/8.9-prelude.sh` — o prelúdio, com `acha_modal`/`dispensa_modal` e
  a nota de quando **não** usá-los
- `tools/par/8.9-update-costs.sh`, `8.9-reset-look.sh`, `8.9-update-bars.sh`
