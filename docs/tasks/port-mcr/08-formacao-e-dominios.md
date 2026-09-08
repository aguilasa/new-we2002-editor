---
id: MCR-TASK-08
title: "`formation.py` e `domains.py` — X/Y, papéis, cobradores e presets"
type: implementação
category: núcleo
phase: 1
depends_on: ["MCR-TASK-05"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §1.7"
status: concluído
---

# MCR-TASK-08: Formação e domínios

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §1.7 e §1.8.
- **É aqui que o upstream acrescenta de fato.** Nossa RE tinha `0x62A8` (20 B) e
  `0x63D5` (10 B) como faixas opacas; ele diz que são X[10], Y[10] e papel
  posicional. Medido na fixture: X `0b 0b 0b 0f 0f 14 1f 1f 2c 29`,
  Y `20 34 48 11 57 32 1e 3e 2a 3e`, papéis `02 03 06 07 08 0a 0e 10 11 13`.
- O papel é gravado como **índice + 2** sobre 20 rótulos. Os fatores `X*7` e
  `Y*2` do upstream são **de tela**, não de formato — não entram no núcleo.
- **X e Y são uma vista derivada, não um endereço novo.** A medição de
  `wte/re/mcr.md` tem **um** destino de 20 bytes em `0x62A8`; a leitura do
  upstream o parte em X[10] e Y[10]. A MCR-TASK-05 deixou isso pronto em
  `layout.py` como `FORMATION_X_ADDRESS` e `FORMATION_Y_ADDRESS` (= `0x62B2`),
  derivados do destino de 20 bytes. **Não acrescente `0x62B2` a
  `DESTINATIONS`** — isso faria a contagem virar 18 e derrubaria o
  `layout.py --check`, que é 17/17 contra a medição. E não escreva endereço
  nenhum aqui: `layout.py --rule1` varre `formation.py` atrás de hex em
  `0x4000..0x8000` e de decimal como `25256`.
- **O `0x6500` está em aberto** (§1.8): capitão pela nossa RE, sexto cobrador
  pelo upstream. Até a MCR-TASK-13 responder, o byte **passa intacto** e não
  aparece na UI.
- **O upstream tem duas árvores, e o que esta task precisa está na menos
  óbvia.** Medido na MCR-TASK-02: `work/easy-mcr/` traz `fifatomcr/` (.NET 8, a
  do `<Copyright>` que o plano cita) e `lite/fifatomcr/` (.NET Framework
  4.7.2), e **nenhuma é subconjunto da outra**. A tabela de cobradores
  (`24911, 24896, 24866, 24851, 24881` = `0x614F, 0x6140, 0x6122, 0x6113,
  0x6131`) e o `25856` = `0x6500` existem **só** em
  `lite/fifatomcr/FrmFormation.vb`, que a árvore principal não tem — lá o
  editor de formação está dobrado dentro do `Frmmcr.vb`, que guarda apenas
  X/Y/papéis (`25256`, `25266`, `25557`). Ler só a árvore principal deixa esta
  task sem os cinco cobradores e sem o byte em aberto.

---

## Objetivo

`formation.py` (X, Y, papéis, os cinco cobradores, o byte em aberto) e
`domains.py` (as tabelas de rótulo).

---

## Critério de conclusão

*(Precedente da MCR-TASK-07, que vale para os cobradores e os papéis: gravar
por **read-modify-write** e nunca montar o campo do zero. Na tabela de dorsais
sobram 2 bits em cada grupo de 32 e o slot 24 não é jogador; montar do zero os
apaga, e o controle negativo que planta isso fica vermelho em dois checks.)*

- [x] X, Y e papéis lidos e gravados, com o `+2` do papel simétrico.
- [x] Os cinco cobradores pela **tabela** `0x614F, 0x6140, 0x6122, 0x6113,
      0x6131`, nunca por aritmética — ela não é crescente.
- [x] O `0x6500` exposto como campo cru e **rotulado como em aberto**, com a
      referência à MCR-TASK-13.
- [x] `domains.py` com as tabelas do upstream — 32 cabelos, 8 posições, 7
      barbas, 8 cores de cabelo, 4 tons de pele, 7 cores de barba, alturas,
      idades, 8 corpos, chuteiras A..H, pé R/L/B, os 20 papéis e os 17 presets
      — cada uma marcada como **rótulo de terceiro, não medição**.
- [x] Os índices conferidos por faixa (valor fora da faixa recusa); os **nomes**
      não são asseridos, porque não têm oráculo.
- [x] Round-trip da formação da fixture: ler e regravar não muda byte nenhum.

---

## Log de Execução

**Executado em:** 2026-09-07

### Resumo do que foi feito

`tools/mcr/formation.py` (330 linhas) e `tools/mcr/domains.py` (329 linhas),
en-US. A formação da fixture lê exatamente o que a §1.7 mediu, e **ler e
regravar não muda um byte**. As 14 tabelas de rótulo são reconferidas contra o
fonte VB por comando: **14/14**.

Três coisas que a execução mediu: o upstream **não nomeia** todos os valores de
três campos; um controle negativo saiu **verde por skip**, não por acerto; e a
varredura da Regra 1 acusava onze endereços que eram **prosa**.

### A formação, medida

```
$ python3 tools/mcr/formation.py work/mcr-entrada.mcr
 slot   X    Y   role
   0    11   32    0 CB-L
   1    11   52    1 CB-R
   2    11   72    4 CB-C
   3    15   17    5 LB
   4    15   87    6 RB
   5    20   50    8 DH-C
   6    31   30   12 OH-L
   7    31   62   14 OH-R
   8    44   42   15 CF-L
   9    41   62   17 CF-R

kickers (kicker order): [7, 7, 8, 7, 7]
0x6500 = 8  -- captain or sixth kicker, OPEN until MCR-TASK-13; read, never written
```

X, Y e papéis batem byte a byte com a §1.7. **E os rótulos formam um time**:
três zagueiros centrais, laterais esquerdo e direito, um volante central, dois
meias e dois atacantes. Isso não *prova* a semântica do upstream — não há
oráculo —, mas é a corroboração mais barata que havia, e ela não contradiz.

**O papel vai para o cartão como índice + 2**, e o controle F1 (gravar sem o
`+2`) derruba quatro checks, incluindo os rótulos, que passam a mostrar `?` nos
dois primeiros.

**Os cobradores saem da tabela, nunca de aritmética.** O controle F2 troca
`layout.kicker_address(k)` por `min(KICKER_ADDRESSES) + k` e o resultado é
`[0, 0, 0, 1, 0]` — plausível numa tela, errado no cartão.

**Os fatores `X*7` e `Y*2` não entraram.** Asserido por comportamento: escrever
`x=[7]*10` põe **7** no cartão, não 49. A primeira versão desse check greppeava
o próprio fonte atrás de `* 7` e ficou vermelha na aritmética do próprio
self-check — *lint contra o próprio arquivo mede o arquivo, não o
comportamento.*

**O `0x6500` é lido e nunca gravado.** O `write()` não o toca, e há check para
isso; o controle F4 (gravar zero ali) fica vermelho em dois. Na fixture ele vale
8 e **8 também está entre os cobradores** — o valor sozinho não discrimina, que
é exatamente o que a §1.8 diz e o que a MCR-TASK-13 vai resolver.

### As tabelas de rótulo

```
$ python3 tools/mcr/domains.py --check work/easy-mcr
domains.py --check: 14/14 label tables match the upstream source
```

O `--check` relê as listas do `Frmmcr.designer.vb` e do
`FrmFormation.Designer.vb` e exige igualdade item a item. Ele prova que a
**transcrição** é fiel; **não prova, e não pode provar, que os nomes estão
certos** — são rótulos de terceiro, e a §5.6 já os lista como sem oráculo. O
módulo afere **faixas** e nunca **nomes**.

Confirmados por medição: 32 cabelos, 8 posições, 8 cores de cabelo, 4 tons de
pele, 8 corpos, chuteiras A..H, alturas 148..211 (64), idades 15..46 (32), os
**20 papéis** da §1.7 e os **17 presets** (`Stock`, `4-5-1A`, …, `5-3-2B`).

**Três campos têm mais valores do que o upstream nomeia** — achado desta task:

| campo | bits | valores | rótulos |
|---|---|---|---|
| `beard_style` | 3 | 8 | **7** |
| `beard_colour` | 3 | 8 | **7** |
| `foot` | 2 | 4 | **3** |

O índice extra não é ilegal, é anônimo. O `label()` devolve `"?"` nesse caso e
**levanta** só fora da faixa do campo — duas condições diferentes que precisam
continuar diferentes, senão um cartão legítimo vira erro. Encaminhado para a
MCR-TASK-11.

Altura, idade e a faixa de perícia são **construídas a partir do bias do
`attributes.py`**, não coladas — assim as duas não podem divergir.

### Os controles negativos

Seis defeitos plantados, cada um pela substituição literal, com a função onde
ela mora, rodados com `PYTHONPATH` apontando para a cópia:

| # | função | de → para | resultado |
|---|---|---|---|
| F1 | `formation.write` | `bytes(r + ROLE_BIAS for r in f.role)` → `bytes(r for r in f.role)` | 🔴 4 falhas |
| F2 | `formation.write` | `layout.kicker_address(k)` → `min(layout.KICKER_ADDRESSES) + k` | 🔴 3 falhas |
| F3 | `formation.write` | `bytes(f.x)` → `bytes(v * 7 % 256 for v in f.x)` | 🔴 3 falhas |
| F4 | `formation.write` | acrescentar `card.write(CAPTAIN_OR_SIXTH_KICKER.address, b"\0")` | 🔴 2 falhas |
| D1 | tabela `HAIR_STYLE` | `"o1", "p1")` → `"o1", "q9")` | 🔴 1 falha *(ver Problemas)* |
| D2 | `domains.label` | `table[offset] if offset < len(table) else UNNAMED` → `table[offset % len(table)]` | 🔴 1 falha |

**6/6 vermelhos, `rc=1` em todos**, e a substituição casou 1× em cada.

### Arquivos criados/modificados

- `tools/mcr/formation.py` — **novo**
- `tools/mcr/domains.py` — **novo**
- `tools/mcr/layout.py` — `find_upward()` hasteado, e a varredura da Regra 1
  passou a tokenizar
- `tools/mcr/attributes.py` — usa o `find_upward()`
- `docs/prompts/perfil-mcr.md` — a lição do controle que sai verde por skip
- `docs/tasks/port-mcr/10-selftest-cli-e-gate.md` — os dois utilitários
  compartilhados
- `docs/tasks/port-mcr/11-ui-leitura.md` — os três índices sem rótulo
- `docs/tasks/port-mcr/progresso.md` — a linha desta task

### Problemas encontrados

**1. Um controle negativo saiu verde por `skip`, não por acerto.** O D1 — um
rótulo inventado no fim da lista de cabelos — passou com "0 failure(s)" na
primeira corrida. A substituição tinha casado; o que não rodou foi o check.
A cópia em `/tmp` não enxergava `work/easy-mcr`, então o cross-check contra o
upstream **pulou**, e a linha de `skip` estava fora do `grep` que eu lia.

A causa raiz é a mesma que a MCR-TASK-05 já tinha consertado no `layout.py` e
que **estava repetida em dois módulos**: o clone era localizado contando saltos
de `dirname` a partir de `__file__`. Um módulo um diretório mais raso aponta
para lugar nenhum — e o efeito não é erro, é ausência. O `find_upward()` subiu
para o `layout.py` e os dois passaram a usá-lo; com isso o D1 fica vermelho.

A convenção de controle do perfil ganhou a frase: **casar a substituição não
basta, o check que o defeito deveria acender tem de ter rodado.**

**2. A varredura da Regra 1 acusou onze endereços que eram prosa.** O
`formation.py` nomeia `0x62A8`, os cinco cobradores e o `0x6500` no docstring e
nos comentários — de propósito: "o `0x6500` rotulado como em aberto" é critério
desta task. A varredura era textual e não distinguia código de comentário, o
que deixava duas saídas ruins: mutilar a documentação, ou desligar a guarda.

Ela passou a **tokenizar**, ignorando comentários, literais de string e os
tokens de f-string. Estes últimos foram a parte não óbvia: o Python 3.12
partiu f-string em `FSTRING_START`/`MIDDLE`/`END`, então o texto dentro de uma
não é `STRING` — sem tratá-los, um `print` que menciona `0x6500` na mensagem
continuava sendo lido como código. Replantado `SNEAKY = 0x62A8` no
`formation.py`: **continua vermelha**.

**3. A lista de cabelos não é uma sequência regular.** Escrevi
`c1,c2,c3,c4,c5,c6,d1,…` por analogia e passou em toda checagem de faixa; só o
`--check` contra o fonte VB pegou. A real é `a1,a2,a3,b1..b6,c1,c2,d1,d2,e1,e2,f1..f3,g1,h1,i1..i3,j1,k1,l1..l3,m1,n1,o1,p1`
— 16 letras com contagens irregulares. **Tabela de terceiro se copia, não se
deduz**, e o comentário no lugar diz isso.

**4. A fixture não foi tocada.** O round-trip roda sobre uma cópia em memória
(`Card(real.to_bytes())`); o digest continua `e53f4895…c47546`.

