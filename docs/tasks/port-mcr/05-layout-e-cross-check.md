---
id: MCR-TASK-05
title: "`layout.py` e o cross-check dos 17 destinos"
type: implementação
category: núcleo
phase: 1
depends_on: ["MCR-TASK-04"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §1.2"
status: concluído
---

# MCR-TASK-05: Os endereços, e a única fonte deles

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §1.2 e §3.3
  (Regra 1).
- Os 17 destinos estão medidos em [`../wte/re/mcr.md`](../../../wte/re/mcr.md),
  do `we-team-editor.exe`. O upstream chega **independentemente** aos mesmos
  números onde as duas listas se tocam — 21508, 22788 passo 32, os cinco
  cobradores, 25256/25266/25557.
- **Esta task trava a 06, a 07 e a 08.** Decodificador escrito contra endereço
  não conferido produz campo plausível e errado, e o sintoma só aparece no jogo.
- **O contêiner já responde em que bloco cada endereço cai**, e a MCR-TASK-04
  mediu: o save declarado ocupa os blocos **1 e 2** (16.384 B), e o bloco 3 —
  onde caem 14 dos 17 destinos — está **fora da cadeia declarada**, com 41
  bytes não-zero num quadro que o diretório marca `0xA0`. Use
  `card.Card.find_save()` e `python3 tools/mcr/card.py <cartão> --blocks` em vez
  de dividir endereço por 8192 na mão; e note que a divisão simples continua
  certa para o **número** do bloco, mas não diz se ele é declarado.

---

## Objetivo

`tools/mcr/layout.py` como **fonte única de endereço**, com um `--check` que se
mede contra o nosso RE.

---

## Critério de conclusão

- [x] Nenhum outro módulo de `tools/mcr/` tem constante de endereço — guarda
      mecânica no `selftest`.
- [x] `layout.py --check` compara com a tabela de `wte/re/mcr.md`: **17/17**,
      `(endereço, bytes)` iguais, e **conjunto idêntico nos dois sentidos** —
      destino presente de um lado e ausente do outro é falha.
- [x] Duas asserções que a `mcr.md` já cobra: a tabela de cobradores **não é
      crescente**, e os deslocamentos de bit do dorsal são `[0,5,2,7,4,1]` =
      `(5·(j mod 6)) mod 8`.
- [x] Um caso vermelho: mudar um endereço na mão faz o `--check` falhar dizendo
      qual.

---

## Log de Execução

**Executado em:** 2026-09-07

### Resumo do que foi feito

`tools/mcr/layout.py` (566 linhas, **en-US** pela decisão de 2026-09-07): os 17
destinos como fonte única, `--check` contra `wte/re/mcr.md` dando **17/17**,
`--rule1` varrendo os demais módulos atrás de endereço, e `--self-check` com
**29 asserções, 0 falhas** — incluindo quatro casos vermelhos embutidos.

O que a execução ensinou não veio da tabela, veio dos controles: **dois
defeitos do próprio módulo só apareceram porque as plantações foram rodadas de
verdade**, e os dois eram do tipo que só dói meses depois.

### O cross-check, medido

```
$ python3 tools/mcr/layout.py --check
layout.py --check: 17/17 destinations agree with wte/re/mcr.md
$ python3 tools/mcr/layout.py --rule1
layout.py --rule1: 0 address(es) outside layout.py
```

**O `--check` lê o markdown commitado, não o `dump_mcr.py`.** Duas razões, e
as duas contam: o `wte/re/mcr.md` é versionado enquanto o
`we-team-editor.exe` **não é**, então o check roda num clone limpo; e a tabela
do `layout.py` foi escrita independentemente da ferramenta que emite o
markdown, então as duas concordarem quer dizer alguma coisa. Importar o gerador
seria conferi-lo contra ele mesmo.

**`total_bytes` não é o span, e o registro de jogador é o caso que faz isso
doer.** A medição conta 276 bytes de atributos, que são 23 pedaços de 12 a
passo 32 — o span é 23×32. Ler `0x5904..0x5904+276` atravessa nomes e bytes
intocados e produz jogador plausível e errado. O `Destination` guarda
`item_size`/`count`/`stride` e o `item_address()` recusa índice fora de 0..22.

**X e Y são vista derivada, não o 18º destino.** A medição tem **um** destino
de 20 bytes em `0x62A8`; a leitura do upstream o parte em X[10] e Y[10]
(`0x62B2`). Acrescentar `0x62B2` a `DESTINATIONS` faria a contagem virar 18 e
derrubaria o próprio check. Ficou derivado, com o porquê no comentário, e a
MCR-TASK-08 recebeu a linha.

As duas asserções que a `mcr.md` já cobra passam: a tabela de cobradores
`0x614F, 0x6140, 0x6122, 0x6113, 0x6131` **não é crescente** (por isso é tabela
e não aritmética), e os deslocamentos são `(0,5,2,7,4,1) = (5·(j mod 6)) mod 8`.

### A guarda da Regra 1, que é o que faz a regra existir

"Só `layout.py` tem endereço" não vale nada como prosa. `address_monopoly()`
varre `tools/mcr/*.py` — menos o próprio `layout.py` — atrás de literal
hexadecimal dentro de `0x4000..0x8000` **e dos mesmos endereços em decimal**. O
decimal não é zelo: o upstream escreve `22788` e `21508`, que passariam batido
por varredura só de hex.

A faixa é estreita de propósito. Uma varredura que acusasse "qualquer
hexadecimal" acenderia no `0x20000`, no `8192` e no `0x800` do `card.py` — que
são o contêiner, não endereço de save — e uma varredura que grita no legítimo é
desligada em uma semana. Testada nos dois sentidos: pega `0x5904` e `21508`
plantados, e deixa `0x20000` em paz.

### Os controles negativos

Seis defeitos plantados numa cópia em `/tmp` (o módulo do repositório não foi
tocado):

| defeito plantado | resultado |
|---|---|
| apagar o destino `0x63D5` (16 em vez de 17) | 🔴 `LayoutError` nomeando `FORMATION_ROLES` e o `0x63d5` |
| inventar um 18º destino `0x6600` | 🔴 3 falhas, uma delas "is in layout.py and NOT in the measurement" |
| mover `0x5404` para `0x5405` | 🔴 `LayoutError` nomeando o destino que sumiu |
| tabela de cobradores em ordem crescente | 🔴 1 falha, imprimindo a tabela |
| deslocamentos `(0,1,2,3,4,5)` | 🔴 1 falha, imprimindo os deslocamentos |
| `PLAYER_STRIDE = 22` | 🔴 3 falhas: passo, endereço do jogador 0/22, e o do nome |

**6/6 vermelhos, `rc=1` em todos.** Mais quatro casos vermelhos que rodam
*dentro* do `--self-check` a cada corrida — endereço movido, tamanho errado,
tabela que não parseia nada, e o par de plantações da varredura da Regra 1.

### Os dois defeitos que os controles acharam

**1. O caminho do `mcr.md` era contado em saltos de `dirname`.** Copiar o
módulo para qualquer lugar — que é exatamente o que os controles dele fazem —
apontava para um diretório inexistente, e o `--check` morria com erro de
caminho em vez de rodar. Efeito prático: **toda corrida de controle reportava
três falhas que nada tinham a ver com o defeito plantado**, e o controle deixa
de ser legível quando isso acontece. Passou a subir a árvore procurando
`wte/re/mcr.md`, com fallback que ainda deixa um caminho nomeável na mensagem
de erro.

**2. Apagar uma linha da tabela dava `KeyError: 25557`.** Um número decimal,
sem arquivo, sem dizer que um destino sumiu — e no *import*, então nem o
self-check chegava a começar. Virou `_required()`, que levanta `LayoutError`
dizendo qual vista precisa de qual endereço e manda rodar o `--check` para ver
quem discorda. Todas as vistas nomeadas passaram por ele; o único
`BY_ADDRESS[...]` cru que sobrou é o de dentro do próprio helper.

Os dois são da mesma família: **código que só é exercitado quando algo dá
errado, e que por isso nunca foi exercitado**. Rodar os controles de verdade —
em vez de afirmar que eles existem — foi o que os expôs.

### Arquivos criados/modificados

- `tools/mcr/layout.py` — **novo**, o módulo inteiro
- `docs/tasks/port-mcr/08-formacao-e-dominios.md` — X/Y como vista derivada, e
  o aviso de que a `--rule1` varre o `formation.py`
- `docs/tasks/port-mcr/10-selftest-cli-e-gate.md` — agregar a
  `address_monopoly()` em vez de reimplementá-la, e escolher uma casa só para o
  `attempt()`, hoje duplicado
- `docs/tasks/port-mcr/progresso.md` — a linha desta task

Nenhum alvo de `ctest`: gate deste ciclo começa na MCR-TASK-10.

### Problemas encontrados

Os dois de cima, os dois consertados. Fora isso:

- **O `attempt()` do `card.py` foi copiado para cá**, e é a segunda cópia. Não
  foi fatorado agora porque não há onde — o módulo comum é o `selftest.py`, da
  MCR-TASK-10 —, e a linha foi escrita **no arquivo daquela task**, não só
  aqui.
- **`mcr.md` diz 6243 bytes não-zero no bloco 2 e a MCR-TASK-04 mediu 6253.**
  Não é divergência: aquela medição é sobre o **molde** (`we-team-editor/data/dat.bin`)
  e esta sobre a **fixture**. Registrado para ninguém tratar os dois números
  como o mesmo depois.
- A fixture não foi tocada — este módulo não abre cartão nenhum.

