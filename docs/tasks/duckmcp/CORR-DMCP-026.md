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
