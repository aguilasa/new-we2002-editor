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
- [ ] Editar e renomear um preset no `DefaultTacticsDialog`  ← **bloqueado, ver o Log**
- [ ] Exportar `.t2002`, importar de volta, e importar um `.t2002` do original  ← **bloqueado pelo mesmo**

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

**Executado em:** 2026-08-29 — **PARCIAL: 3 de 5 itens** (o 6º da lista já
estava fechado pela CORR-WTE-127, fora desta task).

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

**Os itens 4 e 5 estão bloqueados, e o bloqueio é o mesmo.** O `IDOK` do
`DefaultTacticsDialog` **não é desenhado em nenhum dos dois lados** — o
manifesto o põe em dlu `[197,17,50,14]`, dentro dos 481×297 px do diálogo, e a
captura do topo mostra ali só `Selection` e `Name`, no port e no `ed.exe`. As
duas telas concordam, então isto é paridade, não defeito.

**Três caminhos foram medidos e descartados**, e ficam registrados para quem
retomar não repetir:

1. `Return` — não fecha o diálogo em nenhum dos dois;
2. clicar na posição do `IDOK` do manifesto — também não fecha;
3. deixar o diálogo aberto e gravar — a imagem sai `IDENTICAL` à original, ou
   seja, **sem confirmação as edições do diálogo não são aplicadas**.

O quarto caminho a tentar é o `.rc` do `IDOK` (por que ele não aparece) ou o
handler que o `DefaultTacticsDialog` liga ao fechamento. O item do `.t2002` cai
junto porque `CMD_IMP` e `CMD_EXP` moram **dentro** desse diálogo.

**Problemas encontrados:** o bloqueio acima. A task fica aberta.

**Arquivos criados/modificados:**

- `docs/PARIDADE-FUNCIONAL.md` — os três itens da §8.7 e a nota do `IDOK`
- `docs/tasks/PAR-TASK-06.md` — este Log
- `tools/par/8.7-prelude.sh` — o prelúdio (o `8.7-escape-papel*.sh`, anterior a
  ele, traz o próprio `par_click` e não deve ser concatenado com este)
- `tools/par/8.7-clamp-xy.sh`, `8.7-troca-papel.sh`, `8.7-presets-16.sh` — um
  roteiro por item fechado
- `tools/par/8.7-preset-renomear.sh` — o esqueleto do item 4, versionado **com
  aviso no cabeçalho de que não fecha o diálogo e portanto não mede nada**:
  abrir, escolher, renomear e editar funcionam; falta só o caminho de confirmar
