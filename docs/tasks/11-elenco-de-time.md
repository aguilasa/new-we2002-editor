---
id: PES2-TASK-11
title: "Elenco por time — que jogador pertence a que clube"
type: engenharia-reversa
category: formato
phase: 4
depends_on: ["PES2-TASK-10"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §5 (Fase 4)"
status: pendente
---

# PES2-TASK-11: Elenco por time

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §5, Fase 4, e §1.11 (o que ainda
  não foi localizado).
- **Metade já está feita, de graça.** A §3.3 fechou as **54 fronteiras de
  elenco de seleção** contra o memory card: 49 em `SELECTC.BIN` em ordem
  reversa, 5 no executável em ordem direta. O que falta são os **clubes** — e
  a PES2-TASK-09 é quem deve ter chegado perto deles.

Mas fronteira de nome não é elenco. A §1.7 avisa: *"o tamanho de elenco tem
de sair da tabela numérica de elenco, não da contagem de nomes"* — o corte
por 23 bate aproximadamente (1.399 = 60 × 23 + 19) e **não fecha**, e por
isso não serve de prova.

---

## Objetivo

A **tabela numérica de elenco**: para cada time, os índices dos jogadores que
o compõem.

### Como ela se parece

`N` registros de tamanho constante, `N` igual a uma contagem de time já
conhecida (95, 104, 106), cada um com 23 valores que são índices na tabela de
jogador. É o padrão que a §4.3 descreve: *"toda tabela numérica paralela vai
estar nessa mesma ordem, e é assim que se identifica uma"*.

### Duas verificações que a tornam certa em vez de plausível

1. **Os 54 elencos de seleção já são conhecidos.** Se a tabela candidata
   reproduz esses 54 exatamente, ela é a certa — 54 × 23 = 1.242 asserções
   que nenhuma coincidência satisfaz.
2. **Os cinco elencos do executável** (França, Alemanha, Noruega, Argentina,
   Austrália) são o caso difícil, porque no pool suas 23 vagas viram 22
   (§3.3). Uma tabela de índice que aponte para o **pool** vai errar nesses
   cinco; uma que aponte para a tabela de 1.449 do executável, não. **Qual
   das duas ela indexa é a pergunta**, e os cinco são o teste que a responde.

### Depois disso, o bônus da §1.8

Com elenco ligado a time, reconhecer um plantel identifica o clube fictício
sem depender de FAQ. A `docs/PES2-NOMES.md` mapeia os 32 clubes pela via dos
FAQs; esta é a via **verificável** que a §1.8 preferia, e vale confrontar as
duas.

---

## Critério de conclusão

- [ ] Tabela localizada: arquivo, marcador, delta assinado, contagem, largura
      do registro, e **qual** tabela de jogador ela indexa.
- [ ] Os 54 elencos de seleção reproduzidos por ela, 23 de 23.
- [ ] Pelo menos um elenco de clube verificado por `poke` — trocar um índice
      e ver o jogador certo entrar no time certo na tela.
- [ ] O confronto com `docs/PES2-NOMES.md`: quantos dos 32 clubes a via
      medida confirma, e onde as duas divergem.
- [ ] Ferramenta versionada, registrada no `check_image.py`.

---

## Log de Execução

*(a preencher)*
