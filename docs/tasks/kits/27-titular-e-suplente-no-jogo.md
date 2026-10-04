---
id: KITS-TASK-27
---

# KITS-TASK-27 — §4.1 no emulador: suplente em campo e a VRAM lida

## Goal

A §4.1 respondida pelo jogo: com um time de pares diferentes jogando de suplente, os retângulos enviados à VRAM são o 2º par do TEX (ou não são), lido pelo `oracle.py --kit` do `looks` ou por opção versionada.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`
- `docs/PLAN-KITS-PY.md`

## Done criteria

- [ ] Comando versionado sobe o fork, chega à partida e compara retângulo por retângulo; saída colada
- [ ] Controle: o mesmo comando com o time de titular mostra o 1º par
- [ ] A §4.1 do plano tem veredito; se o par não for o 2º, uma CORR é aberta contra a fase 5

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.1). É a fase que não pode ser pulada (§7). Começa de save state, não da rota manual.

## Log de Execução

### 2026-10-04 — comparador pronto, partida ausente

**O comparador** é `tools/kits/oracle.py`. Diferente do `oracle.py --kit` do `looks`, ele **não** compara nos retângulos que o TEX declara: numa partida há dois times, e os dois não cabem em (576, 256). Ele despeja a VRAM inteira (1024×512, `dump_vram`), procura cada um dos 11 registros dos 105 TEX em **qualquer** posição, halfword a halfword nos 15 bits que o dump guarda, e diz o conjunto pelo índice do registro achado (0, 1, 2, 3 = conjunto 1; 4, 5, 6, 7 = conjunto 2). Controle embutido: dois dumps a um quadro de distância têm de dar os mesmos achados; registro com menos de 4 valores distintos é marcado como "não nomeia nada". `--png` faz a busca sobre um dump sem emulador.

Rodado sobre o slot 2 (a `LOOKS SET` do `looks`), onde a resposta é conhecida:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin \
  WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue \
  python3 tools/kits/oracle.py --slot 2 --out work/kits-oracle/looks-2
  control: two dumps a frame apart give the same 6 match(es)
  TEX_A4  record  1 sleeves            set 1  at (576,384)
  TEX_A4  record  2 player palette     set 1  at (0,486), (0,488)
  TEX_A4  record  3 goalkeeper palette set 1  at (0,486), (0,488)
  TEX_A4  record  5 sleeves            set 2  at (576,384)
  TEX_A4  record  6 player palette     set 2  at (0,486), (0,488)
  TEX_A4  record  7 goalkeeper palette set 2  at (0,486), (0,488)
  TEX_A4 wears set 1 and 2
```

Bate com o `looks` (`TEX_A4`, três retângulos enviados). E mostra por que a §4.1 não se responde com esta tela: no `TEX_A4` os dois conjuntos são os mesmos bytes, então todo registro de um aparece também como do outro.

**O que falta é a partida.** Não há save state de partida em lugar nenhum desta máquina: os de WE2002 (`~/.local/share/duckstation/savestates/SLPM-87056_*`, `work/looks-states/`) são as duas `LOOKS SET`, a tela de título e a de cartão de memória (`savestate.py shot` nos dois `.bak`). A task manda começar de save state, não da rota manual. A task fica bloqueada até existir um state de partida, num slot livre (o 3, por exemplo), com:

- um time de conjuntos diferentes (qualquer um das 103 tags do §1.1 cujas imagens diferem; qual time é qual tag não importa, a busca acha a tag) **jogando de suplente** — é o critério 2;
- e, como controle, um time de titular: o mandante da mesma partida serve.

Então, da raiz do repositório:

```
python3 tools/kits/oracle.py --slot 3
```

