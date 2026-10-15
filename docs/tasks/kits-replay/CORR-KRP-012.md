---
id: CORR-KRP-012
---

# CORR-KRP-012 — Log da KRP-TASK-06 traz resumo feito à mão e placeholder replay-<f> em vez da saída do confront --tab

Origin: [KRP-TASK-06](/docs/tasks/kits-replay/06-confront-tab-a-aba-contra-o-jogo-frente-com.md)

## Problem

O bloco de confronto do Log é uma linha `$` só, com o placeholder `<f>`, seguida de um resumo feito à
mão ("9-R1 kits-replay/1 tag 41 fig 1 … back<-back 7381 px 0.403/0.720 …"). Não é o que o comando
imprime: com `--json` ele imprime um documento JSON indentado. As flags de ambiente estão na prosa, não
na linha `$`.

Os números se reproduzem, mas a transcrição não é saída de ferramenta, o que fere a regra "número
colado da ferramenta" e a K3 da §9 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#9). O modo
sem `--json` do `confront --tab` já imprime esse resumo.

## Evidência

```text
$ sed -n '/O confronto, cada uma/,/^```$/p' docs/tasks/kits-replay/06-confront-tab-a-aba-contra-o-jogo-frente-com.md | head -4
$ python3 tools/kits/replay.py confront work/kits-replay/tab/replay-<f>.json --tab --json
(schema; tab: tag, figura, faixa, manga longa, número | lado da aba <- captura do jogo, px, interseção / sobre as cores da aba)
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-R1.json --tab --json | head -3
{
 "capture": {
```

## Root cause

(Hipótese.) Cinco documentos JSON foram condensados à mão para encurtar o Log.

## Fix

No Log da KRP-TASK-06, trocar o resumo por cinco linhas `$` completas, com as flags, e pela saída
literal do modo sem `--json` do comando (`  tab front (yaw …) against the game's … capture: …`),
recapturada na HEAD.

## Arquivos a criar ou modificar

- `docs/tasks/kits-replay/06-confront-tab-a-aba-contra-o-jogo-frente-com.md`

## Verificação

```sh
grep -c 'replay-<f>' docs/tasks/kits-replay/06-confront-tab-a-aba-contra-o-jogo-frente-com.md
```

Hoje dá 1. Depois do conserto tem de dar 0.

## Log de Execução

Reproduzido na HEAD `0a120f9a` (2026-10-15):

```text
$ grep -c 'replay-<f>' docs/tasks/kits-replay/06-confront-tab-a-aba-contra-o-jogo-frente-com.md
1
```

O bloco de confronto do Log da KRP-TASK-06 virou cinco linhas `$` completas, uma por captura de
`work/kits-replay/tab/`, cada uma com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`
na própria linha, seguidas da saída literal do modo sem `--json`, recapturada agora. O `--out` ficou no
default (`work/kits-replay/tab/`), o mesmo da corrida original; as cinco saem 0. A frase que trazia
as flags na prosa passou a só apresentar o bloco, e uma linha datada no Log da task diz que ele foi
refeito por esta correção.

Antigo contra novo, depois das CORR-KRP-011 (`--kit-set`) e CORR-KRP-013 (caminho do venv), que
mexeram no `confront_tab` depois do fechamento da task:

| Captura | Lado da aba <- jogo | Resumo à mão | Saída na HEAD |
|---|---|---|---|
| 9-R1 | back <- back | 7381 px 0.403/0.720 | 7381 px 0.403, 0.720 |
| 9-R1 | front <- front | 4440 px 0.501/0.670 | 4440 px 0.501, 0.670 |
| 10-R1 | back <- back | 4642 px 0.557/0.739 | 4642 px 0.557, 0.739 |
| 10-R1 | front <- front | 4746 px 0.499/0.677 | 4746 px 0.499, 0.677 |
| 9-3-R1 | back <- front | 3520 px 0.406/0.666 | 3520 px 0.406, 0.666 |
| 9-3-R1 | front <- back | 3200 px 0.439/0.612 | 3200 px 0.439, 0.612 |
| 10-3-R1 | back <- front | 3117 px 0.413/0.625 | 3117 px 0.413, 0.625 |
| 10-3-R1 | front <- back | 3538 px 0.362/0.556 | 3538 px 0.362, 0.556 |
| 10-2-R1 | back <- front | 2777 px 0.393/0.569 | 2777 px 0.393, 0.569 |
| 10-2-R1 | front <- back | 3401 px 0.326/0.476 | 3401 px 0.326, 0.476 |

Nenhum número mudou; a tabela da task contra o item 5 continua valendo sem edição. O que o resumo à
mão trazia e o modo sem `--json` não imprime — tag, figura, faixa, manga longa e número de cada aba —
saiu do Log junto com ele; continua no documento do `--json` de cada corrida.

Verificação, depois da edição:

```text
$ grep -c 'replay-<f>' docs/tasks/kits-replay/06-confront-tab-a-aba-contra-o-jogo-frente-com.md
0
```
