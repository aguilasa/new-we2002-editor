---
id: CORR-DMCP-026
---

# CORR-DMCP-026 — A rota title do drive.py não reconhece mais o título e falha em 240 s

Origin: [DMCP-TASK-20](/docs/tasks/duckmcp/20-pes2-who-writes-e-drive.md)

## Problem

A rota `title` do `tools/pes2/drive.py` — a que dirige o **AppImage oficial** pelo
`run_duckstation.sh` — não chega mais ao título: espera 240 s pela assinatura `TITLE = (0.550, 0.341)`
(`tools/pes2/drive.py:167`) e sai com `DRIVE FAILED`. O quadro mais próximo que ela vê tem média 0,160,
longe da faixa medida (0,5502 a 0,5528). A janela é achada e capturada, então não é display nem
`XAUTHORITY`. O defeito é anterior à DMCP-TASK-20: falha igual na HEAD `e2dbefe2`, antes da migração, e
na árvore entregue por ela. Pelo código, as outras rotas do `drive.py`
(`main-menu`, `team-select`, `edit`) esperam a mesma assinatura (`drive.py:566`) e devem parar no
mesmo ponto — leitura, não medido.

## Evidência

Precisa do AppImage oficial em `~/Applications/`, do `:98` e de uma cópia do PES2. Medido pela
DMCP-TASK-20 (Log, "Resultado negativo, anterior a esta task"):

```text
$ DISPLAY=:98 XAUTHORITY= python3 tools/pes2/drive.py "work/pes2-EsIt/Pro Evolution Soccer 2 (Europe) (Es,It).cue" --screen title
DRIVE FAILED: no frame matched mean=0.55 sd=0.341 (+-0.02) within 240s; closest was mean=0.160099 sd=0.316763
```

Na HEAD `e2dbefe2` (`drive.py` antes da migração): `closest was mean=0.160117 sd=0.316803`. Nas duas
corridas o log mostra `window 2097159 on :98`.

## Root cause

Hipótese, a confirmar antes de mexer: a assinatura `TITLE` foi medida em 2026-09-02 com a
configuração do DuckStation de então, e o quadro que o AppImage entrega hoje é outro — resolução,
escala, ou uma tela anterior ao título (aviso, BIOS, menu do próprio emulador). Média 0,16 com
desvio 0,32 não é tela preta nem título. O primeiro passo é olhar o PNG capturado no prazo.

## Fix

Depende da causa. Se a tela é outra, a rota ganha o passo que falta; se é o mesmo título noutra
escala, a assinatura é remedida (cinco corridas, como o comentário de `TITLE` registra) e o comentário
recebe a data e os números novos. Não alargar a tolerância para caber 0,16.

## Arquivos a criar ou modificar

- `tools/pes2/drive.py`

## Verificação

- o comando da Evidência sai com o título capturado, e `--screen main-menu` também passa;
- controle: a assinatura nova continua recusando um quadro que não é o título (o do menu principal,
  valor colado);
- `python3 tools/pes2/selftest.py` sai 0.

## Log de Execução

**Reprodução (2026-10-23, HEAD `b0c0cc77`, `rite reproduce --all --cycle duckmcp`):** REPRODUCED.

```text
$ DISPLAY=:98 XAUTHORITY= python3 tools/pes2/drive.py "work/pes2-EsIt/Pro Evolution Soccer 2 (Europe) (Es,It).cue" --screen title
route: title -> /tmp/pes2-drive-a7qjigma
  window 2097159 on :98
DRIVE FAILED: no frame matched mean=0.55 sd=0.341 (+-0.02) within 240s; closest was mean=0.160111 sd=0.316799
```

**Causa, medida.** Uma sonda no scratchpad subiu o `Session` do `drive.py`, segurou o fast forward e
capturou a cada 2 s: os quadros traziam um retângulo preto no meio, e o quadro de média 0,160 era o
próprio título coberto por ele. Com o AppImage de pé, as janelas no `:98`:

```text
$ xwininfo -root -tree | grep -E '^\s+0x'
     0x200013 "Automatic Updater": ("DuckStation-x64.AppImage" "duckstation-qt")  651x474+65+50  +65+50
     0x200011 "DuckStation 0.1-11826": ("DuckStation-x64.AppImage" "duckstation-qt")  800x655+0+0  +0+0
     0x200007 "Pro Evolution Soccer 2": ("DuckStation-x64.AppImage" "duckstation-qt")  800x655+0+0  +0+0
```

O `Automatic Updater` do AppImage fica por cima da janela do jogo, e o `import -window` captura o que
está na tela dentro do retângulo dela. O `duckmcp.fork.launch` já dispensa esse diálogo (armadilha 29);
o `run_duckstation.sh` e o `drive.py` não. E o diálogo já está de pé quando o lançador retorna:

```text
launcher 33.354864626s
updater after launcher +.010051689s
```

Não era escala nem tela anterior ao título: a hipótese registrada caiu.

**Conserto.**

- `tools/duckmcp/fork.py`: `_dismiss_dialogs` virou `dismiss_dialogs`, público, com o docstring dizendo
  por quê (os dois chamadores internos seguem). `rite set` declarou o arquivo.
- `tools/pes2/drive.py`: o `Session.__enter__` chama `fork.dismiss_dialogs` por até `DIALOG_WAIT = 5` s
  depois de achar a janela, e para assim que um diálogo some.
- A assinatura `TITLE` foi remedida com o diálogo fora, porque o desvio tinha andado para perto da
  borda da tolerância (sd 0,357 contra 0,341 ± 0,02, margem 0,004). Cinco corridas de `--screen title`,
  linhas `shot title`:

```text
  shot title  mean=0.554962 sd=0.357246
  shot title  mean=0.552372 sd=0.357453
  shot title  mean=0.552391 sd=0.357414
  shot title  mean=0.555067 sd=0.357224
  shot title  mean=0.552336 sd=0.357433
```

  `TITLE = (0.553, 0.357)`, comentário com a data e a faixa; a tolerância continua 0,02. A
  comparação virou `matches(signature, mean, sd, tol)`, usada pelo `wait_for_stats`, e o `self_check`
  exige que ela aceite as duas pontas medidas e recuse o menu principal (`MAIN_MENU`, 0,1407/0,2124) e
  o título sob o updater (0,160111/0,316799).

**Controles**, plantados numa cópia de `tools/pes2` + `tools/duckmcp` no scratchpad:

```text
== s/^TITLE = (0.553, 0.357)/TITLE = (0.160, 0.317)/
AssertionError: title (0.552336, 0.357433) refused
exit 1
== s/return abs(mean - signature\[0\]) <= tol and abs(sd - signature\[1\]) <= tol/return abs(mean - signature[0]) <= tol or abs(sd - signature[1]) <= 1/
AssertionError: the title signature took the main menu (0.1407, 0.2124)
exit 1
```

O vermelho do conserto do diálogo é a própria reprodução acima, na HEAD sem ele. A primeira corrida
depois do conserto imprimiu a dispensa:

```text
route: title -> /tmp/pes2-drive-aoc9b8i9
  window 2097159 on :98
  dismissed the Automatic Updater dialog
  recognised  mean=0.554964 sd=0.357231
```

(a ordem das duas linhas do meio é a da árvore entregue; nessa corrida a dispensa saía antes do
`window`, e foi movida depois.)

**Verificação** na árvore entregue:

```text
$ DISPLAY=:98 XAUTHORITY= python3 tools/pes2/drive.py "work/pes2-EsIt/Pro Evolution Soccer 2 (Europe) (Es,It).cue" --screen title; echo "exit $?"
route: title -> /tmp/pes2-drive-s9xygxuf
  window 2097159 on :98
  recognised  mean=0.554880 sd=0.357227
  shot title  mean=0.554953 sd=0.357224  /tmp/pes2-drive-s9xygxuf/title.png
DRIVE OK: /tmp/pes2-drive-s9xygxuf
exit 0
$ python3 tools/pes2/drive.py --self-check
SELF-CHECK OK: frame comparison, regions, routes, pad map
$ python3 tools/pes2/selftest.py 2>&1 | tail -1
OK
$ python3 tools/duckmcp/selftest.py 2>&1 | tail -1
duckmcp_selftest: 435 check(s) ran, 0 failure(s)
$ python3 tools/duckmcp/controls.py 2>&1 | tail -1
duckmcp_controls: 41 control(s), 41 red as required; 22/22 cover rules (a) to (d); per rule (a) 2/2, (b) 8/8, (c) 8/8, (client) 2/2, (d) 4/4, (debug) 2/2, (fork) 3/3, (gpu) 2/2, (live) 6/6, (png) 1/1, (psx) 1/1, (session) 1/1, (vram) 1/1
```

Na última corrida o updater não subiu — o "Remind Me Later" da corrida anterior o adia —, e a rota
passou assim mesmo: a espera de `DIALOG_WAIT` cobre os dois casos.

**Resultado negativo: `--screen main-menu` não passa, por outra causa.** Ele passa do título e para
no passo 4:

```text
  shot confirm-chosen  mean=0.004135 sd=0.040906  /tmp/pes2-drive-oemy09im/confirm-chosen.png
  press cross
  settled  mean=0.004098 sd=0.040332
DRIVE FAILED: Cross on the Si/No box did not leave the language screen
```

O `language.png` dessa corrida ainda é o título: o Start não pegou. O `[Pad1]` do
`~/.local/share/duckstation/settings.ini` (alterado em 2026-10-22 13:52) liga todo botão a `SDL-0/…`,
e o `load_pad` ignora o que não é `Keyboard/` e cai em silêncio no `DEFAULT_PAD` — teclas ligadas a
nada, a armadilha da §6.11. Não é o defeito desta CORR; vira CORR nova, com essa saída como Evidência.
- **Closed** — commit `049cb6a6` (2026-10-23): fix(pes2): drive.py dismisses the AppImage's Automatic Updater before capturing
  - Files (`git show --name-status 049cb6a6`):
    - `M docs/tasks/duckmcp/CORR-DMCP-026.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
    - `M tools/duckmcp/fork.py`
    - `M tools/pes2/drive.py`
