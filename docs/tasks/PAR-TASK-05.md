---
id: PAR-TASK-05
title: "Troca de jogador nos quatro tipos de slot"
type: verificação
category: core
projeto: newWe2002
depends_on: ["PAR-TASK-04"]
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.5"
status: concluído
---

# PAR-TASK-05: Troca de jogador nos quatro tipos de slot

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.5.
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

- [x] Slot de seleção nacional: "complete" e "incomplete"
- [x] Slot de clube de ML: link para contratado e para agente livre
- [x] Agente livre com nacionalidade padrão × escolhida no combo
- [x] Slot de all-star: conferir que os nomes se refazem depois

O último item toca uma não-idempotência conhecida: o `Save` reconstrói as
all-star a partir dos links (`OFS_PLAYER_ATTR_8`), então `Load`+`Save` sem
editar nada **não** devolve a imagem intacta — e não deveria. O oráculo faz o
mesmo. Conferir contra o `ed.exe`, nunca contra o arquivo original.

---

## Definição de pronto

- [x] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.5
- [x] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [x] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico — **nenhuma apareceu**
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-29 — **COMPLETA, 4 de 4.**

**Resumo:**

Sete corridas de `golden_check.sh` em modo `gui`, todas
`OK: identico ao oraculo, exceto o slot 64 conhecido (405724..405739)`, cada
uma com controle positivo. Nenhuma divergência nova, nenhuma CORR aberta.

Os quatro itens medidos são quatro caminhos distintos do mesmo botão, e o
controle positivo mostra que cada par realmente diverge do irmão — sem isso,
dois modos que gravassem o mesmo passariam os dois verdes sem medir nada:

| item | evidência |
|---|---|
| complete × incomplete | 1 registro de jogador contra **2** |
| ML contratado × agente livre | mesmo `OFS_LINK_ML2+1122`, valores diferentes |
| nacionalidade padrão × escolhida | **1 byte** no mesmo campo |
| all-star | `OFS_PLAYER_NAME_7+124` refeito junto com o link |

**O que se aprendeu:**

**Item de lista se escolhe por teclado.** A primeira versão do `sel_row`
calculava a linha como `topo + i*9` DLU, e isso erra: o Qt e o MFC não desenham
a mesma altura de linha, então o mesmo cálculo cai em jogadores diferentes de
cada lado — e o diff acusaria o port por uma divergência que é do roteiro.
Clicar na lista para dar-lhe foco, `Home` para ancorar e `Down` N vezes vale
nos dois. É a mesma lição do `CMB_TEAM` na §8.1, um controle adiante.

**Controle que não existe na tela não é controle que sumiu.** `CHK_ML`,
`CHK_LK_DEF`, `CHK_LK_NDEF` e `CMB_NATIONALITY` estão no `controls.json` e
**não aparecem** quando o slot é de seleção nacional — a §4.2 já dizia, e a
captura confirmou. Um roteiro que clicasse neles ali estaria clicando no vazio.

**O item 4 é o único da série que não pode ser medido contra a imagem
original.** O `Save` reconstrói as all-star a partir dos links, então
`Load`+`Save` sem editar nada já muda bytes. A conferência é contra o `ed.exe`,
que faz o mesmo — e é por isso que o controle positivo dele mostra as
não-idempotências conhecidas ao lado do estímulo, sem que isso seja defeito.

**Problemas encontrados:** nenhum.

**Arquivos criados/modificados:**

- `docs/PARIDADE-FUNCIONAL.md` — os quatro itens da §8.5 e as duas notas
- `docs/tasks/PAR-TASK-05.md` — este Log e o `status`
- `docs/tasks/progresso.md` — a linha da tabela do anexo
- `tools/par/8.5-prelude.sh` — o prelúdio (abre o `PlayerSelectDialog`; escolhe
  o time por `PAR_TIME=nacional|ml|allstar`)
- `tools/par/8.5-selecao-nacional.sh`, `8.5-clube-ml.sh`,
  `8.5-nacionalidade-livre.sh`, `8.5-allstar.sh` — um roteiro por item
