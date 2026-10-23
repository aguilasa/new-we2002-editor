---
id: CORR-DMCP-029
---

# CORR-DMCP-029 — O load_pad do drive.py cai em silêncio no DEFAULT_PAD quando o [Pad1] não é de teclado

Origin: [CORR-DMCP-026](/docs/tasks/duckmcp/CORR-DMCP-026.md)

## Problem

O `load_pad` do `tools/pes2/drive.py` lê o `[Pad1]` do `~/.local/share/duckstation/settings.ini` e
aceita só valores `Keyboard/…`; o que não for de teclado é pulado e o botão fica com o valor de
`DEFAULT_PAD`. Com o `[Pad1]` ligado a um controle (`SDL-0/…`, como está nesta máquina desde
2026-10-22 13:52), todo botão sai com a tecla default, que o emulador não liga a nada: as rotas
apertam teclas mortas sem aviso. `--screen title` passa porque só segura o `Tab` do fast forward
(hotkey, ainda de teclado); `--screen main-menu` para no passo 4 com uma mensagem que fala do jogo, não
do mapa. É a armadilha das "doze subidas apertando teclas ligadas a nada" (§6.11 do plano do PES2),
voltando por outro caminho.

## Evidência

```text
$ grep -E '^(Start|Cross) = ' ~/.local/share/duckstation/settings.ini
Cross = SDL-0/A
Start = SDL-0/Start
$ python3 -c "import sys;sys.path.insert(0,'tools/pes2');import drive;print('start ->', drive.PAD['start'], ' cross ->', drive.PAD['cross'])"
start -> Return  cross -> m
$ DISPLAY=:98 XAUTHORITY= python3 tools/pes2/drive.py "work/pes2-EsIt/Pro Evolution Soccer 2 (Europe) (Es,It).cue" --screen main-menu
...
DRIVE FAILED: Cross on the Si/No box did not leave the language screen
```

A última saída é da corrida medida na CORR-DMCP-026, com o `language.png` ainda mostrando o título.

## Root cause

Hipótese, a confirmar: o `continue` em `if not value.startswith("Keyboard/")` (`load_pad`) trata um
binding de controle como binding ausente. O fallback para `DEFAULT_PAD` existe para "não há arquivo
para ler", e passou a cobrir também "o arquivo liga o botão a outra coisa".

## Fix

O `load_pad` (ou o `preflight`) recusa com `Skip` — ou `Fail`, a decidir — quando um botão que as
rotas usam (`cross`, `start`, `up`, `down`) está ligado a algo que não é teclado, nomeando o botão, o
valor e o arquivo. O fallback para `DEFAULT_PAD` fica só para arquivo ausente ou chave ausente. Não
reescrever a configuração do usuário: é decisão de 2026-09-02 que os lançadores não a configuram.

## Arquivos a criar ou modificar

- `tools/pes2/drive.py`

## Verificação

- com o `[Pad1]` atual, `--screen main-menu` sai pela recusa nova, nomeando `SDL-0/Start`, em segundos
  e sem subir o emulador;
- `self_check` com um `settings.ini` sintético de `[Pad1]` em `SDL-0/…` exige a recusa, e um de
  `Keyboard/…` exige o mapa lido; controle plantado (o `continue` de volta) fica vermelho;
- `python3 tools/pes2/selftest.py` sai 0.

## Log de Execução

**Reprodução (2026-10-23, HEAD `30efe394`, `rite reproduce CORR-DMCP-029 --cycle duckmcp`):** REPRODUCED.

```text
$ grep -E '^(Start|Cross) = ' ~/.local/share/duckstation/settings.ini
Cross = SDL-0/A
Start = SDL-0/Start
$ python3 -c "import sys;sys.path.insert(0,'tools/pes2');import drive;print('start ->', drive.PAD['start'], ' cross ->', drive.PAD['cross'])"
start -> Return  cross -> m
$ DISPLAY=:98 XAUTHORITY= python3 tools/pes2/drive.py "work/pes2-EsIt/Pro Evolution Soccer 2 (Europe) (Es,It).cue" --screen main-menu
...
  shot confirm-chosen  mean=0.004135 sd=0.040906  /tmp/pes2-drive-r7_3ug8z/confirm-chosen.png
  press cross
  settled  mean=0.004098 sd=0.040332
DRIVE FAILED: Cross on the Si/No box did not leave the language screen
```

A causa confere: o `continue` em `if not value.startswith("Keyboard/")` deixava o botão com o valor
de `DEFAULT_PAD`. O `[Pad1]` em `SDL-0/…` desta máquina foi ligado por acidente, segundo o usuário; a
CORR fica de pé porque o `drive.py` aceitou a ligação sem dizer nada.

**Conserto** (`tools/pes2/drive.py`):

- a leitura do `[Pad1]` virou `_pad1(path)`, que devolve o valor cru de cada botão; o `load_pad` lê
  dele, igual a antes;
- `foreign_bindings(path, buttons=ROUTE_BUTTONS)` devolve os botões das rotas (`cross`, `start`,
  `up`, `down`) ligados a algo que não é teclado; arquivo ausente continua sendo "os defaults";
- o `preflight` recusa com `Fail`, nomeando arquivo, botões e valores, antes de subir o emulador.
  A configuração do usuário não é tocada.
- o `self_check` escreve dois `settings.ini` sintéticos: o de `SDL-0/…` tem de dar os quatro botões
  (e o `[Pad2]` e o `L3` não entram), o de `Keyboard/…` tem de dar `{}` e ser lido (`Return`, `m`), e
  o arquivo ausente tem de dar `{}`.

Consequência: `--screen title`, que só segura o `Tab`, também passa a ser recusado com esse `[Pad1]`.
É deliberado: o `preflight` não conhece a rota, e toda rota além do título aperta esses botões.

**Controles**, plantados numa cópia de `tools/pes2` + `tools/duckmcp` no scratchpad:

```text
== s/if b in pad1 and pad1\[b\] and not pad1\[b\].startswith("Keyboard\/")}/if False}/
AssertionError: a controller [Pad1] read as {}
exit 1
== s/if b in pad1 and pad1\[b\] and not pad1\[b\].startswith("Keyboard\/")}/if b in pad1 and pad1[b]}/
AssertionError: a keyboard [Pad1] refused: {'cross': 'Keyboard/M', 'start': 'Keyboard/Enter', 'up': 'Keyboard/UpArrow', 'down': 'Keyboard/DownArrow'}
exit 1
```

**Verificação** na árvore entregue, com o `[Pad1]` atual:

```text
$ time (DISPLAY=:98 XAUTHORITY= python3 tools/pes2/drive.py "work/pes2-EsIt/Pro Evolution Soccer 2 (Europe) (Es,It).cue" --screen main-menu; echo "exit $?")
DRIVE FAILED: [Pad1] of /home/ingmar/.local/share/duckstation/settings.ini binds Cross = SDL-0/A, Start = SDL-0/Start, Up = SDL-0/DPadUp, Down = SDL-0/DPadDown, not the keyboard; xdotool can only press keys -- rebind them in DuckStation
exit 1
... 0,058 total
$ pgrep -af -i duckstation | grep -v pgrep        # nada: o emulador não subiu
$ python3 tools/pes2/drive.py --self-check; echo "exit $?"
SELF-CHECK OK: frame comparison, regions, routes, pad map
exit 0
$ python3 tools/pes2/selftest.py 2>&1 | tail -1
OK
$ python3 tools/duckmcp/selftest.py 2>&1 | tail -1
duckmcp_selftest: 435 check(s) ran, 0 failure(s)
```

`--screen main-menu` até o menu só se mede depois de o `[Pad1]` voltar ao teclado, decisão do
usuário (pela interface do DuckStation ou restaurando os catorze botões do
`settings (Copy).ini` de 2026-09-02).
