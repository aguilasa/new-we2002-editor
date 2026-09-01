---
id: PES2-TASK-09
title: "Os 25 blocos de nome depois do pool, em `SELECTC.BIN`"
type: engenharia-reversa
category: formato
phase: 3
depends_on: []
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §1.5"
status: pendente
---

# PES2-TASK-09: Os blocos de nome depois do pool

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §1.5 e o achado da Fase 2 na §5;
  em `docs/PES2-AJUSTES.md`, a §6.5.
- **É o achado que abre a Fase 3**, nas palavras do próprio plano.

Depois do fim do pool de 1.399 nomes (offset 30853) vêm **mais 25 blocos**,
cerca de 2.000 trechos, de **31552** até por volta de **50000** —
`Tomazi`, `Navaji`, `Davinno`, `Beckenboer`, `Lupateli`. **Nenhum está entre
os 1.399.**

Duas coisas que a §1.7 já ensina e que valem de hipótese: nome fictício é
sinal de **clube**, e os 54 elencos de seleção já estão todos localizados no
pool. Se estes ~2.000 são os elencos de clube, a conta fecha na ordem certa:
32 clubes × 23 = 736, e sobra bastante para os *classic* e o resto.

---

## Objetivo

Dizer **o que são** esses blocos e **a que time pertencem**.

### Método

1. **Contar.** Quantos nomes, e o esquema de registro de cada bloco — o
   `strings_inventory.py` já os agrupou; falta a contagem exata por bloco e
   se o esquema é o mesmo do pool (string + terminador, alinhado a 4) ou o
   de largura fixa de `SELECT.BIN` @5320 (§1.10).
2. **Cruzar com `SELECT.BIN` @5320**, os 463 registros de 10 B rotulados como
   "jogador de clube" na §1.6. Se os dois conjuntos se intersectam, a
   pergunta vira "qual é o pool e qual é a lista por vaga", que é exatamente
   a relação que `player_map.py` já sabe medir entre as outras duas.
3. **Atribuir time.** Se os blocos são contíguos por elenco, a fronteira sai
   do tamanho; se não, sai do cruzamento com o índice canônico de time.
4. **Verificar por `poke`**: renomear um deles e ver em que elenco o nome
   novo aparece na tela.

### A armadilha que a §3.3 já custou uma vez

A ordem de armazenamento é **propriedade da tabela** — `SELECTC.BIN` guarda
elenco de trás para frente, o executável de frente para trás. **Não herdar
a ordem do pool para estes blocos.** Medir cada um.

---

## Critério de conclusão

- [ ] Contagem exata por bloco, e o esquema de registro de cada um.
- [ ] Relação com os 463 de `SELECT.BIN` @5320 medida — mesmo conjunto,
      disjunto, ou parcial, com os números.
- [ ] Pelo menos um elenco de clube com fronteira fechada e verificada.
- [ ] A ordem de cada bloco (direta ou reversa) **medida**, não assumida.
- [ ] Ferramenta versionada em `tools/pes2/`, registrada no `check_image.py`.
- [ ] Escrito na §1.5 do plano, substituindo "o que são … é trabalho da Fase 3".

---

## Log de Execução

*(a preencher)*
