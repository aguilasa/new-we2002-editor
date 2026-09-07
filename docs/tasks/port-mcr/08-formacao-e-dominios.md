---
id: MCR-TASK-08
title: "`formation.py` e `domains.py` — X/Y, papéis, cobradores e presets"
type: implementação
category: núcleo
phase: 1
depends_on: ["MCR-TASK-05"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §1.7"
status: pendente
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

- [ ] X, Y e papéis lidos e gravados, com o `+2` do papel simétrico.
- [ ] Os cinco cobradores pela **tabela** `0x614F, 0x6140, 0x6122, 0x6113,
      0x6131`, nunca por aritmética — ela não é crescente.
- [ ] O `0x6500` exposto como campo cru e **rotulado como em aberto**, com a
      referência à MCR-TASK-13.
- [ ] `domains.py` com as tabelas do upstream — 32 cabelos, 8 posições, 7
      barbas, 8 cores de cabelo, 4 tons de pele, 7 cores de barba, alturas,
      idades, 8 corpos, chuteiras A..H, pé R/L/B, os 20 papéis e os 17 presets
      — cada uma marcada como **rótulo de terceiro, não medição**.
- [ ] Os índices conferidos por faixa (valor fora da faixa recusa); os **nomes**
      não são asseridos, porque não têm oráculo.
- [ ] Round-trip da formação da fixture: ler e regravar não muda byte nenhum.

---

## Log de Execução

*(a preencher)*
