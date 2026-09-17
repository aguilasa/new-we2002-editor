---
id: LOOKS-TASK-23
title: "Incógnita (r) — `DEFAUL` e `NAT`: a nação escolhida e o default que ela aplica"
type: implementação
category: montagem
phase: 8
depends_on: ["LOOKS-TASK-22"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (r)"
status: pendente
---

# LOOKS-TASK-23: O default por nacionalidade

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (r), e a armadilha 17 do perfil.
- **`DEFAUL` e `NAT` não guardam nada**: são as duas metades do default por
  nacionalidade, a tabela que o repositório já tem em `data/defaultlook.txt` —
  95 nações por cinco colunas, as cinco da tupla do corpus
  ([`LOOKS-TASK-13`](/docs/tasks/looks/13-campos-e-dominios-de-looks.md)).
- **Duas cópias do arquivo, e elas têm de bater** (`CLAUDE.md`): o
  `Debug/defaultlook.txt` do `ed.exe` é gitignored e já divergiu. Quem lê aqui
  é o `data/`, versionado.
- **Que a ordem da linha `NAT` é a ordem do arquivo é suposição.** O índice de
  nação do arquivo é o do `ed.exe`; o jogo pode ordenar de outro jeito, e casar
  por índice aplica o default da nação errada com cara de certo.

---

## Objetivo

Fazer a linha `NAT` escolher a nação que o jogo escolhe e a linha `DEFAUL`
aplicar o mesmo default que o jogo aplica, medido contra o jogo.

---

## Critério de conclusão

- [ ] A correspondência valor de `NAT` → linha do `data/defaultlook.txt`,
      medida no jogo em pelo menos cinco nações espalhadas, incluindo uma cujo
      default não é todo `A`.
- [ ] `DEFAUL O.K.` no jogo, depois de escolher cada uma dessas nações: os
      cinco valores que a tela passa a mostrar iguais aos da linha do arquivo.
- [ ] Na janela, a mesma sequência dá os mesmos cinco valores, e o boneco se
      redesenha.
- [ ] Controle negativo: aplicar a linha vizinha do arquivo fica vermelho.
- [ ] O que o jogo faz e o arquivo não diz — nação sem linha, estilo recusado
      no default — escrito, com a recusa visível.
- [ ] §10.3 (r) com o veredito e a data.

---

## Log de Execução

*(preencher ao executar)*
