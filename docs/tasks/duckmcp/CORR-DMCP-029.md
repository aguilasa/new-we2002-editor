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
