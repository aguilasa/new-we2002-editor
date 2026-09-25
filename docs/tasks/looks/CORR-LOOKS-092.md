---
id: CORR-LOOKS-092
title: "Recontar o 132 de 480 do par: medido 316 de 520"
origin: LOOKS-TASK-32
severity: medium
files: [tools/looks/layout.py, tools/looks/oracle.py, docs/prompts/perfil-looks.md, docs/prompts/perfil-looks.armadilhas.md, docs/tasks/looks/32-o-ciclo-da-caminhada.md]
resources: [emulador, save-states]
status: blocked
depends_on: []
done_on: null
done_commit: null
unblocked_by: python tools/looks/oracle.py --check-live
---

# CORR-LOOKS-092 — Recontar o 132 de 480 do par: medido 316 de 520

Origin: [LOOKS-TASK-32](/docs/tasks/looks/32-o-ciclo-da-caminhada.md)

## Problema identificado

A task, a mensagem do commit `6a2c16fb`, os dois arquivos de perfil e o
docstring do `ANIME_BUILD` em `tools/looks/layout.py` afirmam que vigiar o
`ANIME_UNPACK` nomeia o par em **132 de 480** paradas, contra 480 de 480 no
`ANIME_BUILD`. Remedido na mesma máquina, com o mesmo laço de captura, o
watch antigo nomeia o par em **316 de 520** (60,8%), não 27,5%.

O denominador também está errado: o `_walk_stops(…, passes=40)` junta
`40 * (12 + 1) = 520` cargas de matriz, nunca 480.

A conclusão qualitativa sobrevive — e é mais nítida que a prosa: as faltas são
exatamente **uma metade espelhada contígua**, 17 passadas × 12 = 204 cargas.
Mas a razão publicada erra por um fator de 2,4 e já está na armadilha 99, que
as tasks seguintes são mandadas seguir.

**Segundo sintoma do mesmo hábito:** o docstring do `layout.WALK_CAMERA_GAP`
diz que "as matrizes da própria pose balançam 4362 unidades de 4096 ao longo
do ciclo". Nas duas leituras naturais o número é **4552** (as matrizes que o
jogo carregou, nos dois slots — que é o que esta mesma task publicou na sua
tabela de balanço) ou 5528 (a volta não composta). O 4362 não casa com nenhum
dos dois.

## Evidência

```text
$ # cópia de rascunho do HEAD, _walk_stops parametrizado no endereço do watch,
$ # slot 2, 40 passadas
$ python run.py
ANIME_BUILD    520 of 520 matrix loads carry a pair
ANIME_UNPACK   316 of 520 matrix loads carry a pair

$ python run2.py        # o mesmo, uma linha por passada (P = par, . = nenhum)
total 520 paired 316
  0..11  PPPPPPPPPPPP        (doze passadas inteiras)
  12     PPPPP.......
  13..28 ............        (204 cargas seguidas = 17 passadas, a metade espelhada)
  29     .....PPPPPPP
  30..43 PPPPPPPPPPPP

$ python - <<'EOF'   # o balanço, de work/looks-walk/slotN.json (escrito por oracle.py --walk)
import json
for n in (1, 2):
    by = {}
    for c in json.load(open(f"work/looks-walk/slot{n}.json"))["cycle"]:
        for p in c["pieces"]:
            by.setdefault(p["piece"], []).append(p["rotation"])
    spread = max(max(r[i] for r in rs) - min(r[i] for r in rs) for rs in by.values() for i in range(9))
    print(f"slot {n} max rotation spread {spread}")
EOF
slot 1 max rotation spread 4552
slot 2 max rotation spread 4552      # o docstring diz 4362

$ grep -rn "132 de 480\|132 of 480" --include='*.md' --include='*.py' .
./docs/prompts/perfil-looks.armadilhas.md:166
./docs/prompts/perfil-looks.md:512
./docs/tasks/looks/32-o-ciclo-da-caminhada.md:149
./tools/looks/layout.py:2067
```

## Causa raiz

(hipótese) Os dois números vêm de sondas avulsas rodadas durante a task, com
outro laço — 480 = 40 × 12 peças, contagem de **peça** e não das paradas que o
`_walk_stops` de fato junta —, e nunca foram recalculados contra o código que
foi entregue. Nenhum comando versionado imprime qualquer um dos dois, então
nada podia pegar a deriva. É a classe de defeito de que as armadilhas 98 e 99
avisam, aplicada aos números delas mesmas.

## Correção

- Corrigir os quatro lugares para um número que um comando reproduza, e dizer
  **a forma** da falta (uma metade espelhada contígua, 17 de cada 34 passadas)
  em vez de uma razão crua que depende de onde a corrida começa.
- O durável é uma sonda pequena no `tools/looks/oracle.py` — parametrizar o
  endereço do watch no `_walk_stops` são três linhas —, para a afirmação ter
  gerador. Sem isso, marcar os números como avulsos, com a corrida de onde
  saíram.
- O mesmo para o `4362` do `layout.WALK_CAMERA_GAP`: usar o 4552 que a tabela
  de balanço da própria task mede, ou nomear a métrica que dá 4362.

## Arquivos

- tools/looks/layout.py (linhas ~2050-2070 e o docstring do `WALK_CAMERA_GAP`)
- tools/looks/oracle.py (`_walk_stops`)
- docs/prompts/perfil-looks.md:512
- docs/prompts/perfil-looks.armadilhas.md:166
- docs/tasks/looks/32-o-ciclo-da-caminhada.md:149

## Verificação

Rodar a sonda que parametriza o endereço do watch sobre 40 passadas no slot 2 e
exigir que as contagens impressas sejam as que os quatro documentos citam. Hoje
ela imprime `520 of 520` e `316 of 520` contra os documentados `480 of 480` e
`132 of 480`.

## Log de Execução

### 2026-09-25 — triagem inline (`/rite:fix-all looks --plan`, Rite 0.8.0)

**REPRODUCED**, decidido inline por `rite reproduce --all --cycle looks --json` na HEAD `de066fd5`.

Decide pelo `grep`: `132 de 480` continua em `perfil-looks.md:512` e `layout.py:2067`. Dois dos quatro lugares da Evidência (`perfil-looks.armadilhas.md:166`, `32-o-ciclo-da-caminhada.md:149`) não saem do `grep` porque lá o número quebra linha (`132 de` / `480`) — conferido com `sed -n 166p` e `sed -n 149p`: o texto continua lá. O balanço dá 4552 nos dois slots, como registrado, e o `4362` continua em `tools/looks/oracle.py:7412` (o `WALK_CAMERA_GAP` mora no `oracle.py`, não no `layout.py` que a Correção nomeia). `run.py` e `run2.py` eram cópias de rascunho fora do repositório: o 316 de 520 só se remede com o emulador, e fica para quem corrigir.

```text
$ # cópia de rascunho do HEAD, _walk_stops parametrizado no endereço do watch,
$ # slot 2, 40 passadas
$ python run.py
C:\Users\ingcvs\AppData\Local\Programs\Python\Python313\python.exe: can't open file 'C:\\github\\new-we2002-editor\\run.py': [Errno 2] No such file or directory
[exit 2]
$ python run2.py        # o mesmo, uma linha por passada (P = par, . = nenhum)
C:\Users\ingcvs\AppData\Local\Programs\Python\Python313\python.exe: can't open file 'C:\\github\\new-we2002-editor\\run2.py': [Errno 2] No such file or directory
[exit 2]
$ python - <<'EOF'   # o balanço, de work/looks-walk/slotN.json (escrito por oracle.py --walk)  # (heredoc)
slot 1 max rotation spread 4552
slot 2 max rotation spread 4552
$ grep -rn "132 de 480\|132 of 480" --include='*.md' --include='*.py' .
./docs/prompts/perfil-looks.md:512:    outra variante, e ali são 480 de 480 paradas com par contra 132 de 480
./docs/tasks/looks/CORR-LOOKS-092.md:3:title: "Recontar o 132 de 480 do par: medido 316 de 520"
./docs/tasks/looks/CORR-LOOKS-092.md:14:# CORR-LOOKS-092 — Recontar o 132 de 480 do par: medido 316 de 520
./docs/tasks/looks/CORR-LOOKS-092.md:22:`ANIME_UNPACK` nomeia o par em **132 de 480** paradas, contra 480 de 480 no
./docs/tasks/looks/CORR-LOOKS-092.md:71:$ grep -rn "132 de 480\|132 of 480" --include='*.md' --include='*.py' .
./docs/tasks/looks/CORR-LOOKS-092.md:112:`132 of 480`.
./docs/tasks/looks/correcoes-progresso.md:111:| [CORR-LOOKS-092](/docs/tasks/looks/CORR-LOOKS-092.md) | Recontar o 132 de 480 do par: medido 316 de 520 | LOOKS-TASK-32 | medium | pending | — |
./tools/looks/layout.py:2067:pieces of every pass -- 480 of 480 stops over forty passes, against 132 of 480
```
- **blocked** (2026-09-25): the pair counts (316 of 520 against the documented 132 of 480) can only be re-measured over forty passes in the running game, and the probe that parametrizes _walk_stops is part of the fix, not yet versioned; no work started — unblocked by `python tools/looks/oracle.py --check-live`
