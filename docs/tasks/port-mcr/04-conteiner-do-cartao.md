---
id: MCR-TASK-04
title: "`card.py` — diretório, blocos, quadros, checksum e as recusas"
type: implementação
category: núcleo
phase: 1
depends_on: ["MCR-TASK-03"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §1.1"
status: concluído
---

# MCR-TASK-04: O contêiner do cartão

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §1.1 e §1.10.
- **Não é engenharia reversa:** o contêiner do memory card PSX é documentação
  pública (nocash), e `wte/tools/dump_mcr.py` já o implementa em Python — com o
  dicionário **completo** de estados (`0x51/0x52/0x53`, `0xA0..0xA3`, `0xFF`).
  `tools/pes2/memcard.py` conhece só o `0x51`, e é leitura pura.
- **O upstream não conhece nada disso**, e é por isso que ele grava nos bytes
  `0..137` — que são, medido, o quadro `MC` inteiro mais `state`+`size`+`link`
  da entrada 1.

---

## Objetivo

`tools/mcr/card.py`: abrir um `.mcr`, enxergar o diretório, achar o save do
WE2002 pelo nome, e **recusar** o que não deve ser escrito.

---

## Critério de conclusão

- [x] Lê os 15 quadros de diretório, com os oito estados nomeados, o `link` e o
      tamanho declarado.
- [x] Acha o save por nome (`B?SLPM-86600WEW-OPT`, `B?SLES-…`, `B?SLUS-…`) e
      **diz em que bloco ele está** — o upstream assume o bloco e quebra em
      silêncio se ele mudar.
- [x] Calcula o checksum XOR de quadro e **relata** divergência sem consertar —
      preservar é o comportamento medido do original (§6 do plano).
- [x] **Recusa toda escrita abaixo de `0x800`**, com mensagem que diz o que há
      lá. É caso de controle negativo, não comentário.
- [x] Recusa arquivo cujo tamanho não seja 131.072 B, e arquivo sem `MC`.
- [x] `self_check()` importável, com as recusas exercitadas contra um cartão
      sintético montado em memória — sem depender da fixture.

---

## Log de Execução

**Executado em:** 2026-09-07

### Resumo do que foi feito

`tools/mcr/card.py` (563 linhas): diretório com os oito estados nomeados,
checksum XOR de quadro **relatado e nunca consertado**, busca do save por nome
com os blocos em que ele está, e as recusas. `self_check()` roda contra um
cartão sintético montado em memória — **27 checks, 0 falhas**, sem fixture,
sem disco e sem Qt.

Duas coisas que a execução mediu e que o plano não dizia: o `link` do
diretório é **0-based** e a cadeia da fixture tem **dois** blocos; e o
`self_check` original **morria de traceback** no primeiro defeito que
levantasse exceção, escondendo os vinte checks seguintes.

### O contêiner, medido na fixture

```
$ python3 tools/mcr/card.py work/mcr-entrada.mcr
work/mcr-entrada.mcr: 131072 bytes, magic MC
checksums de quadro: todos batem  (relatado, nunca consertado)
save WE2002: 'BISLPM-86600WEW-OPT' nos blocos [1, 2], 16384 bytes declarados,
             primeiro bloco em 0x02000
```

Os **16** checksums XOR (o quadro 0 mais os 15 de diretório) batem: a fixture é
um cartão formalmente íntegro.

**A cadeia tem dois blocos, e o `link` é 0-based.** O quadro 1 é `0x51` com
`link = 1`; o quadro 2 é `0x53` com `link = 0xFFFF`. Lido como *número de
quadro*, o link do quadro 1 aponta para ele mesmo — um leitor ingênuo entra em
laço ou conclui "cadeia de um bloco" para um save que declara 16.384 bytes. É o
**tamanho declarado que desempata**: 16.384 / 8.192 = 2 blocos, e só a leitura
0-based fecha essa conta. O `next_frame` devolve `link + 1`, com o porquê
escrito na docstring, e o `chain()` recusa cadeia circular nomeando justamente
essa causa.

**41 bytes de dado moram fora da cadeia declarada:**

```
$ python3 tools/mcr/card.py work/mcr-entrada.mcr --blocks
 bloco  estado  bytes nao-zero
    1   0x51     5844
    2   0x53     6253
    3   0xa0       41  <-- fora da cadeia declarada
    4..15 0xa0       0
```

É a §1.2 do plano vista pelo lado do contêiner: o bloco 3, onde caem 14 dos 17
destinos, o diretório declara **livre**. Virou o `--blocks` e o
`stray_blocks()` justamente para a afirmação não depender de script perdido.

### As recusas, e a prova de que elas ficam vermelhas

`self_check` cobre 27 asserções. As recusas não perguntam "o módulo aceita o
válido" — perguntam "recusa o inválido, **e pela razão certa**": cada uma exige
um trecho específico na mensagem, então trocar uma recusa por outra é falha.

Cinco controles negativos, cada um plantado numa cópia em `/tmp` (o
`tools/mcr/card.py` do repositório não foi tocado):

| defeito plantado | resultado | falhas |
|---|---|---|
| `if offset < HEADER_BYTES:` → `if False:` | 🔴 | 2 — "NAO recusou -- o guard esta verde a toa" |
| `return self.link + 1` → `return self.link` | 🔴 | 8, a primeira nomeando o laço na cadeia |
| `bad_checksums()` → `return []` | 🔴 | 1 — "checksum divergente e relatado ruins=[]" |
| `if len(data) != CARD_BYTES:` → `if False:` | 🔴 | 1 — recusou, mas pela mensagem de magic |
| `if data[:len(MAGIC)] != MAGIC:` → `if False:` | 🔴 | 1 |

> **Nota de 2026-09-07, posterior a esta corrida.** Os trechos de mensagem
> citados nesta tabela são os que o `self_check` imprimia **em português**, e
> ficam como estão — são a evidência da corrida. A §3.5 do plano passou a exigir
> **en-US em todo o código do port** no mesmo dia, e a retradução do `card.py` é
> a [CORR-MCR-007](/docs/tasks/port-mcr/CORR-MCR-007.md); depois dela os mesmos
> cinco casos continuam vermelhos, pelos trechos equivalentes em inglês.

**5/5 vermelhos, `rc=1` em todos.** O quarto merece nota: com a checagem de
tamanho desligada, o buffer truncado passa a falhar pelo **magic**, e o check
acusa exatamente isso ("recusou, mas sem dizer 'bytes, e um memory card'") —
que é o comportamento certo, porque a asserção é sobre *qual* recusa dispara,
não sobre haver alguma.

### As duas regras de desenho, conferidas mecanicamente

- **Regra 1 — só `layout.py` tem endereço.** `grep` dos 17 destinos (nas duas
  bases) em `card.py`: **nenhum**. O `0x800` do módulo **não é** um deles: ele é
  `FRAME_BYTES * (DIRECTORY_FRAMES + 1)`, calculado, com o porquê no comentário
  — escrito como constante viraria mais um número mágico, e quem mudasse
  `FRAME_BYTES` o deixaria para trás.
- **Regra 3 — o núcleo não conhece Qt.** `import card` e
  `assert "PySide6" not in sys.modules`: passa.

### O nome do save: um medido, dois por forma

`SAVE_NAME_RE` casa `B[A-Z]SL[A-Z]{2}-\d{5}WEW-OPT`. **Só uma variante foi
medida** — `BISLPM-86600WEW-OPT`, a japonesa da fixture. As variantes SLES e
SLUS estão no padrão **por forma**: nenhum cartão europeu ou americano passou
por aqui, e inventar o número de produto deles seria fabricar dado. O que
identifica o save é o sufixo `WEW-OPT`; o prefixo só confere que a coisa tem
cara de nome de save de PSX. Está dito no comentário, no lugar.

### Arquivos criados/modificados

- `tools/mcr/card.py` — **novo**, o módulo inteiro
- `docs/tasks/port-mcr/05-layout-e-cross-check.md` — a linha sobre a cadeia
  declarada e o `--blocks`
- `docs/tasks/port-mcr/13-oraculo-e-veredito.md` — o estado exato do cartão que
  o experimento do console tem de julgar
- `docs/tasks/port-mcr/14-verificacao-final.md` — a linha de recontagem da §1.1
- `docs/tasks/port-mcr/progresso.md` — duas linhas na tabela "Estado medido", e
  a linha desta task

Nenhum alvo de `ctest` foi criado: o perfil diz que **antes da MCR-TASK-10 não
há gate deste ciclo**, e `tests/CMakeLists.txt` é dela.

### Problemas encontrados

**1. O `self_check` morria de traceback em vez de reportar falha.** Descoberto
pelo controle 2: com o `+1` do `link` removido, o `find_save()` levanta
`CardError` no sexto check, o Python imprime traceback e **os vinte checks
seguintes nunca rodam**. O gate ficava vermelho — `rc=1` —, mas por acidente, e
o relatório não dizia o que mais estava quebrado. Um `tenta()` passou a
envolver as chamadas que um defeito pode fazer levantar: exceção inesperada
vira `FALHA` nomeada e a corrida continua. Depois do conserto o mesmo controle
reporta **8 falhas**, a primeira nomeando o laço na cadeia.

Vale para as tasks 05 a 10: **um harness que morre no primeiro susto mede o
primeiro defeito e esconde o resto.**

**2. A fixture não foi tocada.** Tudo que este módulo leu foi a cópia
`work/mcr-entrada.mcr`; o digest da fixture antes e depois é o mesmo
`e53f4895…c47546`. Escrita nenhuma tocou disco: os testes de `write()` são em
memória.

