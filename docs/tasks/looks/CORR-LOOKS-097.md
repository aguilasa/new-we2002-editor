---
id: CORR-LOOKS-097
title: "Versionar a sonda por trás dos números de posição no painel"
origin: LOOKS-TASK-34
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-097 — Versionar a sonda por trás dos números de posição no painel

Origin: [LOOKS-TASK-34](/docs/tasks/looks/34-o-goleiro-andando.md)

## Problem

O critério 4 do log da LOOKS-TASK-34 se apoia numa tabela de quatro linhas com
a caixa da tinta normalizada pelo painel (jogo slot 1 0,384/0,214/0,690/0,974,
janela slot 1 0,215/0,118/0,545/0,908, e o mesmo para o slot 2). O log diz que
ela foi medida "com um script de rascunho", e o script não está no log nem no
repositório; as entradas são PNGs de `work/looks-shots/`, fora do git. A
LOOKS-TASK-35 recebeu os mesmos números ("(0,215, 0,118) na janela contra
(0,384, 0,214) no jogo") como base de um veredito que ela tem de dar.

Refeitos por um script ad hoc do revisor, os números saem próximos (janela s1
0,214/0,118/0,547/0,911, s2 0,253/0,114/0,565/0,911; jogo s1
0,386/0,216/0,697/0,980, s2 0,378/0,216/0,697/0,988): a afirmação está certa
em substância, mas não se reproduz da HEAD, e o resultado depende da escolha da
borda do painel e do limiar — a primeira tentativa do revisor deu 0,004/0,006
do lado do jogo, porque pegou a moldura.

## Evidência

```text
$ grep -n "script de rascunho" docs/tasks/looks/34-o-goleiro-andando.md
(acha a frase no parágrafo do critério 4; nenhum comando nem corpo de script a segue)
$ git show 0d289714 -- docs/tasks/looks/35-fechamento-da-v2.md | grep "0,215"
+  caixa da tinta, em fração do painel, começa em (0,215, 0,118) na janela
$ python bbox3.py   # ad hoc do revisor, sobre work/looks-shots/walk-silhouette-{1,2}-60.png e task34/s{1,2}-f24.png
walk-silhouette-1-60.png (30, 172, 271, 515)  0.386 0.216 0.697 0.980
walk-silhouette-2-60.png (30, 172, 271, 515)  0.378 0.216 0.697 0.988
s1-f24.png (35, 133, 320, 370)  0.214 0.118 0.547 0.911
s2-f24.png (35, 133, 320, 370)  0.253 0.114 0.565 0.911
```

O log também não dá o comando que produziu `s1-f24.png`/`s2-f24.png`
(o `--frame 24` é inferido do nome).

## Root cause

Hipótese: a observação de posição surgiu de passagem, olhando as capturas; foi
medida com um script descartável e não virou sonda, porque o executor a julgou
fora do escopo e a encaminhou à task 35 — e os números viajaram como evidência
sem o método.

## Fix

Uma de duas: (a) uma sonda versionada, por exemplo `confront.py --placement
[SLOT]`, que toma a foto do jogo e a nossa captura `--frame N` e imprime a caixa
da tinta normalizada pelo painel, e trocar os números em
`docs/tasks/looks/34-o-goleiro-andando.md` e `35-fechamento-da-v2.md` pelo
comando e a saída dela; ou (b) colar o corpo exato do script num heredoc no log
da task 34, com os comandos que geraram `s1-f24.png`/`s2-f24.png`, e marcar a
tabela da task 35 como ad hoc, nomeando a sonda como ainda faltando.

## Arquivos a criar ou modificar

- docs/tasks/looks/34-o-goleiro-andando.md
- docs/tasks/looks/35-fechamento-da-v2.md
- tools/looks/confront.py

## Verificação

Hoje `grep -n "script de rascunho" docs/tasks/looks/34-o-goleiro-andando.md`
acha a frase sem comando reproduzível. Depois, os números de posição nos dois
arquivos saem de um comando que roda da HEAD (por exemplo
`python tools/looks/confront.py --placement 1`) e os imprime dentro de 0,01.

## Log de Execução
