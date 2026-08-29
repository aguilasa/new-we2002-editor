---
id: PAR-TASK-03
title: "Cobradores, capitão e o foco de combo"
type: verificação
category: ui
projeto: newWe2002
depends_on: ["PAR-TASK-01"]
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.3"
status: concluído
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

- [x] Abrir o combo, **navegar com as setas sem sair do controle**, apertar
      ESC/clicar fora — conferir se grava ou não igual ao original — reprovou
      aqui, e foi fechado pela [CORR-WTE-125](/docs/tasks/CORR-WTE-125.md);
      roteiros em `tools/par/8.3-escape-cobrador.sh` e
      `tools/par/8.3-escape-sem-navegar.sh`
- [x] Escolher e sair com Tab; conferir os 6 campos —
      `tools/par/8.3-escolher-e-tab.sh`
- [x] Lembrar da troca do par de cobradores a cada gravação (é esperada)

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

- [x] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.3
- [x] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [x] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico — foi a [CORR-WTE-125](/docs/tasks/CORR-WTE-125.md)
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-28 — parcial, 2 de 3 itens. **Fechada em
2026-08-29**, quando a [CORR-WTE-125](/docs/tasks/CORR-WTE-125.md) corrigiu o
item 1.

**Resumo:**

Itens 2 e 3 fechados; o item 1 reprovou e virou
[CORR-WTE-125](/docs/tasks/CORR-WTE-125.md).

**O que se aprendeu:**

**O item 1 encontrou o que existia para encontrar, e o achado contradiz o
inventário.** A §3.5 diz que o original usa `CBN_KILLFOCUS` "justamente para
navegar a lista com as setas sem gravar". Medido: três `Down` e `Escape` levam
`kick_long_fk` de 3 a **6 no `ed.exe`** e o deixam em **3 no port**. Os dois
gravam em perda de foco — isso a §3.5 acerta —, mas o valor que chega lá é
outro, porque `Escape` mantém o item navegado no MFC e **reverte** no
`QComboBox`. A frase do inventário entra na CORR junto com o código.

**O irmão do item 1 passa, e isso delimita a correção.** Escolher com `Return` e
sair com `Tab` grava 3 → 5 **nos dois**, com os outros cinco campos intactos.
Quem diverge é só o caminho do `Escape`.

**Problemas encontrados:** o item 1, acima. A task fica aberta.

**Arquivos criados/modificados:**

- `docs/PARIDADE-FUNCIONAL.md` — os dois itens conferidos, o reprovado, e a
  nota sobre a frase errada da §3.5
- `docs/tasks/CORR-WTE-125.md` — o achado
- `docs/tasks/correcoes-progresso.md` — a linha e o checklist

**Adendo da [CORR-WTE-125](/docs/tasks/CORR-WTE-125.md), 2026-08-29.** O item 1
foi corrigido: o port passa a interceptar o `Escape` no popup dos seis combos de
cobrador e a manter o índice navegado, em vez de deixar o Qt desfazê-lo. Os três
roteiros da §8.3 ficaram versionados em `tools/par/`, e os três saem com o
golden em `OK`: `Escape` depois de três `Down` dá **6 nos dois lados**, `Escape`
sem navegar deixa **3 nos dois** e não escreve `OFS_KICKER+0`, e o irmão do item
2 continua em **3 → 5 nos dois**.
- `docs/tasks/PAR-TASK-03.md` — este Log
