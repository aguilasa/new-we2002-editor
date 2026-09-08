---
id: MCR-TASK-13
title: "O oráculo do Obocaman: o `0x6500`, o nome cheio e o veredito do console"
type: verificação
category: engenharia-reversa
phase: 3
depends_on: ["MCR-TASK-09"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §5.5"
status: pendente
---

# MCR-TASK-13: O oráculo, e as três perguntas

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §5.5 e §1.8.
- **Pode ser antecipada** assim que a MCR-TASK-09 fechar: ela precisa do leitor,
  não da UI. E deve ser, porque o veredito muda a tela da MCR-TASK-12.
- O oráculo é o editor do Obocaman por `make wte` — Wine, prefix `win32`, no
  `:98`. Ele **não é oráculo de tudo**: é de três perguntas, e só.
- **O lado do upstream da discordância mora em `lite/fifatomcr/FrmFormation.vb`,
  e só ali.** Medido na MCR-TASK-02: o `25856` (= `0x6500`) não aparece em
  nenhum arquivo da árvore principal `fifatomcr/`, que é a do `<Copyright>`
  citado no plano. Ao citar o que "o upstream diz" sobre o sexto cobrador,
  a referência é esse arquivo — a árvore principal não opina sobre o byte.

---

## Objetivo

Responder com valor medido o que hoje é opinião.

---

## Critério de conclusão

- [ ] **A tela já está esperando o veredito, e sabe onde pô-lo.** A MCR-TASK-12
      deixou o `0x6500` em **leitura**, com o rótulo `_open_byte` do
      `tools/mcr/ui/formation_view.py` dizendo as duas leituras e que o byte é
      lido e nunca gravado. Fechado o veredito, o editor entra ali — um campo
      "capitão" (um índice de slot) ou um sexto cobrador ao lado dos cinco —, e
      **o `formation.write` precisa passar a gravar o byte**: hoje ele o pula
      de propósito, com o comentário dizendo por quê. São dois arquivos, e os
      dois estão nomeados aqui para não se descobrir isso relendo a tela.
- [ ] **O `0x6500`**: capitão ou sexto cobrador. Experimento discriminante — pôr
      o capitão num slot conhecido e os cinco cobradores em slots distintos,
      salvar, ler os seis bytes. Na fixture eles valem `[7,7,8,7,7]` e `8`, e
      **o valor sozinho não discrimina**.
- [ ] **O nome que enche os 10 bytes**: escrever nome de 10 caracteres com
      espaço no fim, salvar, ler de volta. Confirma (ou derruba) a leitura de
      que o campo não é cadeia terminada em NUL.
- [ ] **O veredito do console**, ou a razão escrita de ele não ter sido obtido:
      14 dos 17 destinos caem no bloco 3, que o diretório declara livre, e
      ninguém recalcula checksum. Um cartão gravado pelo port aberto no
      DuckStation responde se isso importa.

      **A MCR-TASK-04 já mediu o lado do contêiner**, e o comando que reproduz
      é `python3 tools/mcr/card.py <cartão> --blocks`: na fixture, os blocos
      1 e 2 são a cadeia declarada (16.384 B), o bloco 3 tem **41 bytes
      não-zero** e o diretório o marca `0xA0`, e **os 16 checksums de quadro
      batem** — o cartão está formalmente íntegro *exceto* por esse dado fora
      da cadeia. É esse o estado exato que o console tem de julgar; leve um
      cartão nessa condição ao experimento, não um recém-gravado sem conferir.
- [ ] O que for medido volta para a §1.8 e a §5.6 do plano; hipótese descartada
      fica, com o motivo.

---

## Armadilhas

- **Feche qualquer editor aberto no `:98` antes.** Os roteiros acham o diálogo
  pelo tamanho, e janela esquecida é dirigida no lugar da certa.
- **Cópia, sempre** — inclusive do cartão. O `work/entrada.mcr` é fixture.

---

## Log de Execução

*(a preencher)*
