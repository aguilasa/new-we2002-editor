---
id: PAR-TASK-01
title: "Nomes e abreviações de time, pela tela"
type: verificação
category: ui
projeto: newWe2002
depends_on: []
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.1"
status: concluído
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

Cada um tem o seu roteiro versionado em `tools/par/`, e é ele o "comando" da
Definição de pronto:

- [x] Editar os 6 slots de nome de uma seleção; conferir que o `(n)` de cada
      rótulo bate com o truncamento real — `tools/par/8.1-nomes-6-slots.sh`
- [x] Editar kanji e caixa mista — `tools/par/8.1-kanji-e-mista.sh`
- [x] Editar as 3 abreviações — `tools/par/8.1-abreviacoes.sh`
- [x] `CMD_COPY_TEAM_NAMES` numa seleção e num clube de ML — conferir o quirk do
      comprimento kanji (§3.3) — `tools/par/8.1-copy-selecao.sh` e
      `tools/par/8.1-copy-clube-ml.sh`
- [x] Repetir num clube de ML, incluindo os dois nomes extras —
      `tools/par/8.1-clube-ml-extras.sh`

### Por que esta é a primeira

Três razões que convergem:

1. **É onde bug já apareceu.** A [CORR-WTE-121](/docs/tasks/concluidos/CORR-WTE-121.md)
   corrigiu, no port Lazarus, três faixas de gravação de nome de time
   (`OFS_TEAM_NAME_KANJI_A`, `OFS_TEAM_MIXED_CASE_NAME`, `OFS_TEAM_NAME_6_B`).
   Mesma família de campo, mesmos quirks de sobra de buffer — e no `newWe2002`
   essa área nunca foi conferida pela tela.
2. **Fecha o item aberto do Windows.** A [PAR-TASK-10](/docs/tasks/concluidos/PAR-TASK-10.md)
   é o mesmo trabalho na outra plataforma, e lá está bloqueado; aqui não há
   Citrix filtrando input.
3. **A régua está pronta.** Ela rodou nas três imagens em 2026-08-27. Os dois
   lados têm hook de edição, e **os nomes são diferentes**: `GOLDEN_EDIT` no
   `golden_run.sh` (o `ed.exe`) e **`GOLDEN_GUI_EDIT`** no `golden_gui.sh` (o
   port). Os dois recebem `$MAIN` em escopo e definem `dlu_x`/`dlu_y` com a
   mesma conversão, então **o mesmo trecho de shell serve aos dois** — é assim
   que esta série mede.

**Atenção ao `Ctrl+A`.** Ele **não** seleciona tudo num `CEdit` do Win32: limpe
o campo com `End`, `shift+Home`, `BackSpace` nos dois lados, senão os dois
recebem textos diferentes e o diff acusa divergência que não existe.

---

## Definição de pronto

- [x] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.1
- [x] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [x] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico — **nenhuma apareceu**, então nenhuma CORR foi aberta
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-28

**Resumo do que foi feito:**

Os cinco itens da §8.1 medidos na `ptbr-remaster.bin`, cada um com um par de
corridas: `golden_check.sh` em modo `gui` (port contra `ed.exe`) e um
**controle positivo** (a cópia gravada contra a imagem original, para provar
que o estímulo chegou ao disco). Seis corridas de golden, todas
`OK: identico ao oraculo, exceto o slot 64 conhecido (405724..405739)`.
Nenhuma divergência nova, nenhuma CORR aberta.

**O que se aprendeu, e vale para as PAR-TASK seguintes:**

**Verde de gravação sem controle positivo não mede nada.** A primeira corrida
passou com o roteiro editando os seis campos — e o controle mostrou que nada
de nome havia sido gravado: só as não-idempotências conhecidas
(`OFS_PLAYER_ATTR_8`, `OFS_KICKER`, `OFS_PLAYER_NAME_7+471`) apareciam. A causa
é que **o port abre com o combo de time em `---` e os campos vazios**; digitar
ali não grava em time nenhum, e os dois lados fizeram `Load`+`Save` idêntico.
Selecionar um time é a primeira linha do roteiro, não preâmbulo. A armadilha 4
do `01-executar.md` descreve exatamente esta família, e ela pegou assim mesmo
— porque aqui o controle que faltava não era o `Load`+`Save`, era a prova de
que o **estímulo** chegou.

**A seleção de time precisa de `Home` antes do `Down`.** Sem ele a sequência
significa "o próximo", que depende do estado inicial; com ele, "o primeiro".
Medido idêntico nos dois lados: os dois chegam a `Nation 1 - Ireland`, com
`IRLANDA` nos campos e `(7)` nos rótulos.

**E precisa de um `Return` no fim.** O clique no `CMB_TEAM` abre o popup, e
`Home`/`End`/`Down`/`Up` só movem o item destacado — a seleção **não é
confirmada** sem o `Return`. Sem ele o popup fica aberto, o formulário não
troca de time, e tudo o que vem depois no roteiro digita no time errado (ou em
time nenhum): é a mesma família do verde-sem-controle-positivo acima, e dá o
mesmo sintoma. Este terceiro fato faltava no Log original e foi medido de novo
pela [CORR-WTE-123](/docs/tasks/concluidos/CORR-WTE-123.md).

**`End` no combo cai em `Master League (default)`**, que é um item especial de
campos desabilitados e não serve de clube. Um `Up` a partir dele dá o último
clube real (`Master League 32`), sem depender de contar quantos são.

**O truncamento segue o rótulo em todos os limites medidos** — `(7)`, `(8)` e
`(11)`, quatro deles na mesma tela do clube de ML. É a resposta afirmativa ao
item 1, e ela vale para os oito campos, não só os seis.

**Problemas encontrados:**

**O markdown desta task afirmava que o `golden_gui` aceita `GOLDEN_EDIT`.**
Não aceita: o hook do lado do port chama-se **`GOLDEN_GUI_EDIT`**
(`tools/golden_gui.sh`), e `GOLDEN_EDIT` é o do `golden_run.sh`, do lado do
`ed.exe`. Corrigido no texto da task. Os dois recebem `$MAIN` e definem
`dlu_x`/`dlu_y` igual, então o mesmo trecho serve aos dois — o que a correção
registra, porque é o que faz a série funcionar.

**Dois tiros no pé de shell, registrados porque custam tempo a quem repetir:**
`pkill -f 'build/src/app/newWe2002'` casa o **próprio** processo do shell que
contém essa string no comando e o mata (`exit 144`); e `break` dentro de um
`for` em `$(...)` não escapa do subshell, o que fez a busca de janela devolver
vazio e travar até o timeout.

**Arquivos criados/modificados:**

- `docs/PARIDADE-FUNCIONAL.md` — os cinco itens da §8.1 marcados, cada um com a
  faixa medida, mais a nota sobre o controle positivo
- `docs/tasks/concluidos/PAR-TASK-01.md` — este Log, o `status`, e a correção do nome do
  hook
- `docs/tasks/concluidos/progresso.md` — a linha da PAR-TASK-01 no anexo

**Adendo da [CORR-WTE-123](/docs/tasks/concluidos/CORR-WTE-123.md), 2026-08-28.** Os seis
roteiros desta task foram shell avulso e não ficaram em lugar nenhum, o que
tornava as seis corridas verdes não repetíveis. Foram **reconstruídos e
remedidos**, e agora vivem em `tools/par/`, um arquivo por corrida, cada um
rodando nos dois hooks sem alteração. As faixas do controle positivo de cada um
estão na §8.1 do inventário. A remedição confirmou os cinco itens e corrigiu
uma frase: o `span 9 / diff 4` do kanji é do **clube de ML**; na seleção, para
a mesma fonte de 6 caracteres, o mesmo `copy` dá `span 13 / diff 7`.
