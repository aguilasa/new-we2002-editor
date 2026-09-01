---
id: PES2-TASK-06
title: "Estrutura do registro de jogador, pelo cartão"
type: engenharia-reversa
category: formato
phase: 3
depends_on: ["PES2-TASK-05"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §5 (Fase 3)"
status: pendente
---

# PES2-TASK-06: Estrutura do registro de jogador, pelo cartão

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §5, Fase 3, e §4.2 alavanca 3.
- **O cartão é o lado fácil**, e é por onde a fase começa: 1.242 registros de
  10 B em @516 do `PES-OPT`, e 1.242 = 54 × 23 exato (§3.3). Cada bloco de 23
  é um elenco **rotulado**, porque o nome está ali.

Mas 10 bytes é o **nome**. Os atributos moram em outro lugar do save, e achar
onde é metade desta task: o `PES-OPT` tem 16 KiB e os nomes ocupam 12.420 B.

---

## Objetivo

A estrutura do registro de jogador **no cartão**: campo, deslocamento,
largura em bits, domínio.

### Método

1. **Enquadrar o registro.** Editar o mesmo atributo em dois jogadores
   consecutivos e medir a distância entre os dois bytes que mudaram: é o
   passo do registro. Repetir com jogadores distantes para confirmar que o
   passo é constante.
2. **Preencher os campos** pelo ciclo da PES2-TASK-05, um atributo por vez.
3. **Fechar o domínio** de cada um: valor mínimo e máximo aceitos na tela, e
   o que a codificação faz nos extremos.
4. **Achar a origem**: o offset onde o registro do jogador 0 começa, e a
   relação dele com os 1.242 nomes de @516.

### O que o WE2002 sugere procurar

Não como resposta — como **lista de perguntas**, na ordem em que
`Player::Decode` do core as desempacota: posição, pé preferido, altura,
atributos numéricos, e a máscara de habilidades especiais. Se a engine é a
mesma, a **ordem** dos campos dentro do registro tende a ser a mesma, mesmo
que as larguras mudem. Confirmar cada um; não herdar nenhum.

### O que esta task não entrega

O registro **no disco**. O layout do cartão não é o do disco (§4.2.3), e
casar os dois é a PES2-TASK-07. Aqui fecha-se só o lado do cartão, que é o
que tem rótulo.

---

## Critério de conclusão

- [ ] Passo do registro medido, não inferido, com duas medições
      independentes que concordam.
- [ ] Pelo menos os campos que a tela de edição expõe, cada um com offset,
      máscara e domínio.
- [ ] Cada campo **verificado nos dois sentidos**: editar na tela muda o byte
      previsto, e escrever o byte muda o que a tela mostra.
- [ ] Escrito numa seção nova do plano (Fase 3), com a tabela de campos.
- [ ] Nenhum campo entra "por analogia com o WE2002" — a §4 do plano
      proíbe, e a §6.9 diz por quê.

---

## Log de Execução

*(a preencher)*
