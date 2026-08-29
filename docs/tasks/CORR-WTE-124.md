---
id: CORR-WTE-124
title: "Correção: CMD_DEFAULT_NUMBERS grava 37 faixas no port contra 20 no ed.exe"
type: correção
category: paridade
status: concluído
depends_on: []
---

# CORR-WTE-124: `CMD_DEFAULT_NUMBERS` diverge do oráculo

## Problema identificado

O botão `CMD_DEFAULT_NUMBERS` (`CMD_NUMDEF` no `.rc`, rotulado *"pl. n° = team
n°"*) grava **mais** no port do que no `ed.exe`, com o mesmo estímulo:

| lado | faixas contra a imagem original | bytes |
|---|---:|---:|
| `Debug/ed.exe` | 20 | 118 |
| `newWe2002` | **37** | **151** |
| um contra o outro | **19** | 63 |

Medido em 2026-08-28 na `ptbr-remaster.bin`, pela
[PAR-TASK-02](/docs/tasks/PAR-TASK-02.md) item 3. O `golden_check.sh` em modo
`gui` reprova com **18 divergências** fora da faixa conhecida:

```text
FALHOU: 18 divergencia(s) nao esperada(s):
  1013316..1013319  4 byte(s)  data  OFS_TEAM_NAME_1+676
  1882648..1882651  4 byte(s)  data  OFS_TEAM_NAME_2+680
  1929016..1929016  1 byte(s)  data  OFS_FLAG_SHAPE_COPY_1+12
  2004888..2004890  3 byte(s)  data  OFS_TEAM_NAME_3+892
  2005424..2005424  1 byte(s)  data  OFS_FLAG_SHAPE_COPY_2+12
  2303730..2303730  1 byte(s)  data  OFS_FORMATIONS+30
  2305109..2305112  4 byte(s)  data  OFS_FORMATIONS_A+125
  2328072..2328072  1 byte(s)  data  OFS_FLAG_SHAPE_COPY_3+12
  2329064..2329067  3 byte(s)  data  OFS_KICKER+8
  2667758..2667761  4 byte(s)  data  OFS_KIT_PREVIEW+502
  2668258..2668261  4 byte(s)  data  OFS_KIT_PREVIEW+1002
  2668758..2668759  2 byte(s)  data  OFS_KIT_PREVIEW+1502
  2669562..2669565  4 byte(s)  data  OFS_KIT_PREVIEW_A+18
  4599304..4599307  4 byte(s)  data  OFS_TEAM_MIXED_CASE_NAME+708
  4904676..4904676  1 byte(s)  data  OFS_FLAG_SHAPE_COPY_4+12
  5711652..5711652  1 byte(s)  data  OFS_FLAG_SHAPE_COPY_5+12
  12549688..12549691  4 byte(s)  data  OFS_FLAG_COLOURS+170
  12549934..12549935  2 byte(s)  data  OFS_FLAG_COLOURS+416
```

O `region` é o offset conhecido mais próximo, **não** a estrutura: as faixas
caem em `+676`, `+502`, `+1002`, `+12` de cinco `FLAG_SHAPE_COPY` — o
espaçamento regular sugere um campo por time, não corrupção de nome ou bandeira.

## Evidência de que não é artefato do harness

Três descartes, todos medidos:

1. **Não depende de time selecionado.** O botão é global (percorre os 64 times),
   e a corrida **sem** nenhuma seleção dá as **mesmas 18 faixas**.
2. **Não é o modal.** O botão abre `"Operation done!"`, e a caixa é dispensada
   nos dois lados antes de gravar — com clique, não com `Return` (ver abaixo).
   Medido: depois da dispensa o modal não está mais em pé em nenhum dos dois.
3. **Não é clique perdido no lado Qt.** Depois do `Return` que fecha a
   `QMessageBox`, o port não tem nenhuma janela entre 100–900 × 60–400 px, então
   o ramo de clique do `dispensa_modal` não dispara ali.

## Causa raiz

**Não diagnosticada.** Os dois laços parecem equivalentes, e é isso que torna o
achado interessante. O legado (`legacy/mfc/edDlg.cpp`, `OnNumeriDefault`):

```cpp
for(i=0;i<64;i++) {
    gioc[462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_1+1;
    ...  // as 23 linhas, order_1 a order_23, escritas uma a uma
}
```

O port (`src/app/Commands.cpp`, `OnDefaultNumbers`):

```cpp
for (int t = 0; t < we2002::TEAMS_NATIONAL_ALLSTAR_SLOTS; ++t)
    for (int k = 0; k < 23; ++k)
        db_.players[PLAYERS_NC + (t * 23) + k].number =
            static_cast<int>(SquadNumberAt(db_.teams[t].squad_numbers, k)) + 1;
```

`TEAMS_NATIONAL_ALLSTAR_SLOTS` é 64 e `PLAYERS_NC` é 462 — os limites batem. A
suspeita a investigar primeiro é a **fonte da leitura**: o legado lê
`squad_nazall[i]` e o port lê `db_.teams[t]`. Se os dois arrays não forem a
mesma coisa para todo `i` — em particular nos slots de all-star —, os números
saem de times diferentes, e o `number` do jogador vai parar em registros que o
original não toca.

Confirmar exige comparar, para o mesmo `i`, o que cada lado lê antes de escrever.

## Correção

1. dumpar `squad_nazall[i]` e `db_.teams[i]` lado a lado para os 64 `i`, e achar
   onde divergem;
2. se forem arrays diferentes por construção, alinhar o port com a fonte que o
   original usa;
3. se forem iguais, o defeito está em `SquadNumberAt` contra a ordem
   `order_1..order_23` — e aí é o mapeamento de bitfield, com a armadilha 9 do
   `01-executar.md` (`DWORD`/ordem de bit) como primeira suspeita.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `src/app/Commands.cpp` | modificar — `OnDefaultNumbers`, depois do diagnóstico |
| `docs/PARIDADE-FUNCIONAL.md` | modificar — marcar o item 3 da §8.2 quando fechar |
| `docs/tasks/PAR-TASK-02.md` | modificar — o item 3 e o Log |

## Verificação

- [x] A divergência tem causa nomeada, com o array e o índice onde aparece
- [x] `golden_check.sh` em modo `gui` com o roteiro do item 3 sai `OK`
- [x] O `number` do jogador acompanha o número de camisa do time, medido no
      `dump_estado`
- [x] `ctest` do `newWe2002` continua verde — `Commands.cpp` é do app, mas o
      core não pode ter regredido
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-29

**Resumo do que foi feito:**

**A causa é estouro de array, e o original também estoura — só que num vizinho
que não vai para o disco.**

`GIOCATORI_TOT` é **1911** (`legacy/mfc/edDlg.cpp:29`), e `1911 = 462 + 63×23`:
o array de jogadores tem lugar para 63 times, não 64. O laço do original vai a
64 (`edDlg.cpp:7667`) e a 64ª volta escreve `gioc[1911..1933]`, fora do array.
Ali o vizinho é `gioc_fifa[]` (`edDlg.cpp:141`), que **não** é gravado na
imagem — a volta extra não tem efeito observável no disco.

No port `players[PLAYERS_TOTAL]` tem os mesmos 1911 lugares, mas em
`Database` o vizinho é `teams[64]`, que **é** gravado. Escrever
`players[1911..1933].number` caía em cima dos registros de time, e daí as 18
faixas de nome, camisa, bandeira, formação e cobrador que o oráculo não toca —
o `region` do `golden_compare.py` mostrava exatamente campos de `Team`.

O conserto é uma linha: o laço passa a ir a `TEAMS_NATIONAL_ALLSTAR` (63) em
vez de `TEAMS_NATIONAL_ALLSTAR_SLOTS` (64). Isso reproduz o que o original faz
**à imagem**, e larga o comportamento indefinido em vez de imitá-lo — a mesma
decisão que o 64º slot de números de camisa já tinha recebido.

O `Commands.cpp:85` era o **único** lugar do port que indexava `players[]` por
`TEAMS_NATIONAL_ALLSTAR_SLOTS`; nenhum outro laço precisou de mudança.

**Medições, todas na `ptbr-remaster.bin` com o roteiro versionado:**

| | faixas | bytes |
|---|---:|---:|
| controle do oráculo (original × `ed.exe`) | 20 | 118 |
| controle do port, **antes** | 37 | 151 |
| controle do port, **depois** | 19 | 103 |
| golden (oráculo × port), **antes** | 19 (18 fora da faixa conhecida) | 63 |
| golden (oráculo × port), **depois** | **1**, só `405724..405739` | 15 |

A diferença de uma faixa entre os dois controles é exatamente o slot 64
conhecido, que o oráculo escreve e o port preserva.

Pelo `dump_estado` (`wte/tests/dump_estado.cpp` compilado sobre `src/core`), o
número de slots em que `players[462 + t×23 + k].number` **não** bate com
`SquadNumberAt(teams[t], k) + 1`, para `t` em 0..62:

```text
oracle    divergencias t=0..62:    3  [(55, 7), (55, 14), (55, 21)]
port      divergencias t=0..62:    3  [(55, 7), (55, 14), (55, 21)]
original  divergencias t=0..62:   62
```

62 na imagem original, **3 idênticos nos dois lados** depois do botão. Os três
são do time 55, que é all-star — e o `Save` refaz all-star a partir dos links
(`OFS_PLAYER_ATTR_8`), nos dois editores.

**Problemas encontrados:**

**A §8.2 não tinha roteiro versionado**, e a `PAR-TASK-02` também não deixou o
seu — é a mesma lacuna que a [CORR-WTE-123](/docs/tasks/CORR-WTE-123.md) fechou
para a §8.1. O roteiro foi escrito em `tools/par/8.2-numeros-default.sh`, e a
reprodução da evidência já saiu dele.

**A dispensa da caixa "Operation done!" que a PAR-TASK-02 descreve só serve ao
oráculo.** O Log dela diz "o `OK` fica no centro horizontal a ~40% da altura",
que é a caixa do MFC (148×82). A `QMessageBox` do port mede **188×100** e tem o
`OK` a ~77% da largura e ~75% da altura — medido em captura nesta correção. Um
roteiro com só o primeiro ponto clica no texto do port, a caixa fica em pé,
engole o clique de gravar, e a corrida sai `IDENTICAL` dos dois lados: verde sem
ter medido nada, que foi o que aconteceu na primeira tentativa desta reprodução.
O roteiro versionado tenta os pontos em ordem e reconfere a caixa entre eles.

**Arquivos criados/modificados:**

- `src/app/Commands.cpp` — o limite do laço de `OnDefaultNumbers`, com o
  comentário que explica os dois vizinhos
- `tools/par/8.2-numeros-default.sh` — criado, o roteiro do item 3
- `docs/PARIDADE-FUNCIONAL.md` — §8.2: o item 3 marcado com as faixas
  remedidas, e a nota do modal com as duas geometrias
- `docs/tasks/PAR-TASK-02.md` — o item 3, a Definição de pronto, o `status` e o
  adendo no Log
- `docs/tasks/progresso.md` — a linha da PAR-TASK-02 no anexo
