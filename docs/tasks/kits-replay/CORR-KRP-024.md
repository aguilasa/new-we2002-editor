---
id: CORR-KRP-024
---

# CORR-KRP-024 — head_judge não pega painel de cabeça largo demais, e o exit 2 de --player-looks inválido não tem gate

Origin: [KRP-TASK-22](/docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md)

## Problem

A §3.3 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#3.3) diz que a largura é reajustada "para
o rótulo mais longo não cortar nem o painel sobrar". O `head_judge` afirma só duas coisas: que nenhum
rótulo é mais estreito que o próprio texto, e que as larguras das duas línguas diferem. Um painel
ajustado mais largo que o necessário nas duas línguas passa.

O commit também acrescenta a recusa de um `--player-looks` inválido (frase no stderr, exit 2), e
nenhum gate a confere. Medido: `--player-looks X-Y` dá "--player-looks: 'X-Y' is not a looks tuple
like A-A1-A-A-A: …", com exit 2.

## Evidência

```text
$ grep -n "did not refit\|width < needs" tools/kits/ui_check.py
1101:                if width < needs:
1107:        bad.append("the head panel is %d px in both languages: the switch did not refit it"
$ grep -n "player-looks" tools/kits/ui_check.py tools/kits/selftest.py
```

O último `grep` acha 5 ocorrências, e nenhuma é caso de tupla inválida.

## Root cause

O juiz cobre a redação do critério de pronto ("muda a largura … nenhum rótulo corta"), mas não o "nem
o painel sobrar" do plano. O caminho do exit 2 entrou sem sonda.

## Fix

- No `head_judge` de `tools/kits/ui_check.py`, afirmar que a largura do painel é igual à largura
  ajustada. Por exemplo: imprimir o `sizeHint` ao lado de `width` na linha de painel de cabeça do
  `--list-combos` em `tools/kits/ui/app.py`, e exigir igualdade.
- Plantar algo como `setFixedWidth(self.head_panel.sizeHint().width() + 60)` e vê-lo vermelho.
- Acrescentar uma corrida com `--player-looks` inválido que exija exit 2 e a frase.

## Arquivos a criar ou modificar

- `tools/kits/ui_check.py`
- `tools/kits/ui/app.py`

## Verificação

```sh
DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py | grep "head panel width oversized"
```

Hoje esse plant não existe. Depois do conserto tem de aparecer
`ok    plant 'head panel width oversized' fails the head panel judge`.

## Log de Execução
