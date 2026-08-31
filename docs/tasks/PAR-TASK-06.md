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

- [x] Clampar x em 0/48 e y em 0/112
- [x] Trocar papel e conferir a legenda do marcador
- [x] `Escape` depois de navegar um combo de papel — **já fechado** pela
      [CORR-WTE-127](/docs/tasks/CORR-WTE-127.md), fora desta task, porque a
      divergência apareceu na revisão da
      [PAR-TASK-03](/docs/tasks/PAR-TASK-03.md): os dez combos de papel gravam
      pelo mesmo `FocusOut` dos seis de cobrador, e o `Escape` divergia igual.
      Roteiros `tools/par/8.7-escape-papel.sh` e
      `tools/par/8.7-escape-papel-sem-navegar.sh`; medição na §8.7 do
      inventário. **Não precisa ser refeito aqui** — mas se o item 2 acima
      mexer no `OnRoleShown` ou no `eventFilter`, re-rode os dois roteiros
- [x] Aplicar os 16 presets num time
- [x] Editar e renomear um preset no `DefaultTacticsDialog` — reprovou aqui, e
      foi fechado pela [CORR-WTE-131](/docs/tasks/CORR-WTE-131.md); roteiro
      `tools/par/8.7-preset-renomear.sh`
- [ ] Exportar `.t2002`, importar de volta, e importar um `.t2002` do original
      — **destravado** pela [CORR-WTE-131](/docs/tasks/CORR-WTE-131.md), que
      deu saída ao diálogo onde `CMD_IMP` e `CMD_EXP` moram; falta medir

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

## Log de Execução

**Executado em:** 2026-08-29 (itens 1-3) e 2026-08-30 (itens 4 e 5) —
**PARCIAL: 4 de 5 itens fechados, 1 medido e reprovado** (o 6º da lista já
estava fechado pela CORR-WTE-127, fora desta task).

### Terceira passagem, 2026-08-30 — o item 5

**Ele destravou e reprovou.** Com o `DefaultTacticsDialog` confirmável pela
[CORR-WTE-131](/docs/tasks/CORR-WTE-131.md), o `CMD_EXP` pôde enfim ser
exercitado. Exportar a mesma tática dos dois lados dá **56 bytes no `ed.exe` e
52 no port**: assinatura e corpo batem, e o que diverge são os bytes entre eles
— oito no original (`18e3 5c40 0100 0000`) contra quatro zeros no port.

**Os oito bytes do original são determinísticos**, não lixo: duas exportações
seguidas deram o mesmo valor. Foi a primeira coisa que medi, porque "parece
ponteiro" convidava a descartá-los como memória não inicializada — e aí a
conclusão teria sido a oposta.

A causa está em duas constantes de `DefaultTacticsDialog.cpp`: `VPTR_BYTES` é 4
onde o oráculo — que é **x86-64** — usa 8, e `FILE_BYTES` não soma esse campo.
Como a **leitura** usa o mesmo `VPTR_BYTES`, o port exporta e importa o próprio
formato sem erro nenhum; é o que escondeu o defeito até a comparação com o
outro lado. **Formato só se confere contra o outro lado**, nunca contra si
mesmo. [CORR-WTE-132](/docs/tasks/CORR-WTE-132.md).

**Resumo:**

Cinco corridas de `golden_check.sh` em modo `gui`, todas
`OK: identico ao oraculo, exceto o slot 64 conhecido (405724..405739)`, cada
uma com controle positivo. Nenhuma divergência nova, nenhuma CORR aberta.

| item | evidência |
|---|---|
| clamp de x e y | 99 → `0x30` (48) e 999 → `0x70` (112) no `raw_formation` |
| trocar papel | `0x02` → `0x04`, e a legenda de `CB SX` a `SW` nos dois |
| 16 presets | sequência dos 16 ≠ preset 1 isolado, ambos iguais ao oráculo |

**O que se aprendeu:**

**O clamp tático não passa pelo `slot_x`/`slot_y` do dump.** Os dois campos
saem `0,0,0,...` para o time 0 antes **e** depois da edição, e olhar só para
eles diria que o estímulo não chegou. Quem guarda é o `raw_formation`, nos
bytes `10 + slot` e `20 + slot` — que é onde o `OnSlotXCommitted` escreve. O
`golden_compare.py` apontou o caminho ao mostrar `OFS_FORMATIONS+10`.

**O item 4 saiu do bloqueio e virou medição — e o palpite de ontem estava
errado.** Ontem registrei que o `IDOK` "não é desenhado nos dois lados, logo é
paridade". A primeira metade é verdade e a conclusão não era: seguindo o quarto
caminho que eu mesmo tinha deixado escrito — ler o `.rc` —, o `ed.rc` linha 627
diz `DEFPUSHBUTTON "OK",IDOK,197,17,50,14,NOT WS_VISIBLE`. O botão é invisível
**por design**, e o `rc2ui.py` traduz certo.

O que diverge é o efeito, e só se vê medindo os dois lados **separadamente**:
com o mesmo roteiro, o `ed.exe` grava **7 faixas / 61 bytes** e o port sai
**`IDENTICAL`**. O diálogo era inutilizável no port — **e deixou de ser** em
2026-08-30, com a [CORR-WTE-131](/docs/tasks/CORR-WTE-131.md): o port agora
grava 7 faixas / 48 bytes, nos mesmos offsets, e o golden sai `OK`.

> **A explicação que escrevi aqui para esse `IDENTICAL` estava errada**, e a
> execução da CORR-WTE-131 a mediu em 2026-08-30. Eu disse que "no MFC o
> original aplica as edições enquanto se digita; no Qt o commit depende do
> `accept()`". A segunda metade é falsa: o port **também** aplica campo a
> campo, direto em `db_.preset_formations`, que o `OnPresetTactics` passa por
> ponteiro. Os dois são modais e os dois bloqueiam a gravação com o diálogo de
> pé; o que falta ao port é **fechá-lo** — no MFC o `DEFPUSHBUTTON` invisível
> segue sendo o default e o `Return` roda o `EndDialog`.
>
> O controle que desfaz o engano é rodar o oráculo **sem** o `Return` final:
> ele sai `a gravacao nao confirmou` e a cópia fica `IDENTICAL`. Sonda de
> janela não serve — o "Modify default tactics" aparece mapeado nos dois lados,
> porque o `dlg_tatt` do original é objeto membro e o Wine não destrói a janela
> X depois do `EndDialog`.

**A lição de método:** "os dois lados se comportam igual na tela" não é
paridade — paridade é o que sai no disco. Ontem parei na tela e concluí cedo
demais.

**Quatro caminhos de fechamento descartados por medição**, para não se
repetirem: `Return` sem foco, `Return` depois de `windowfocus`,
`xdotool key --window` (XSendEvent, que o Qt ignora) e clicar na posição do
botão invisível.

**O item 5 continua bloqueado** pela mesma causa: `CMD_IMP` e `CMD_EXP` moram
dentro desse diálogo, e sem caminho de confirmação não há como exercitá-los. Ele
destrava junto com a CORR-WTE-131.

**Uma armadilha do roteiro, medida:** abrir o `CMB_FORMATION` com o diálogo por
cima deixa a gravação do oráculo sem confirmar (`a gravacao nao confirmou`) e a
corrida morre antes de medir. E um `Return` ao fim é necessário: ele não fecha o
diálogo, mas confirma o campo em edição — sem ele, o oráculo também não grava.

**Problemas encontrados:** o bloqueio acima. A task fica aberta.

**Arquivos criados/modificados:**

- `docs/PARIDADE-FUNCIONAL.md` — os três itens da §8.7 e a nota do `IDOK`
- `docs/tasks/PAR-TASK-06.md` — este Log
- `tools/par/8.7-prelude.sh` — o prelúdio (o `8.7-escape-papel*.sh`, anterior a
  ele, traz o próprio `par_click` e não deve ser concatenado com este)
- `tools/par/8.7-clamp-xy.sh`, `8.7-troca-papel.sh`, `8.7-presets-16.sh` — um
  roteiro por item fechado
- `tools/par/8.7-preset-renomear.sh` — o roteiro do item 4. Deixou de ser
- `tools/par/8.7-t2002-exportar.sh` — o roteiro do item 5, que mediu a
  divergência do formato
- `docs/tasks/CORR-WTE-132.md` e `docs/tasks/correcoes-progresso.md` — o achado
  esqueleto: ele **mede**, e o veredito é a CORR-WTE-131. O cabeçalho explica
  por que não há clique de confirmação (o `IDOK` é `NOT WS_VISIBLE` no `.rc`)
- `docs/tasks/CORR-WTE-131.md` e `docs/tasks/correcoes-progresso.md` — o achado
