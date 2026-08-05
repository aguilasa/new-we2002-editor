---
id: WTE-TASK-33
title: "Contador de slots livres de Master League"
type: implementação
category: features
phase: 5
depends_on: ["WTE-TASK-20"]
status: pendente
---

# WTE-TASK-33: Slots livres de ML

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §5.4.
- **A menor das quatro features**, e a que depende só da Fase 3. Pode ser feita
  a qualquer momento depois da camada de dados.

O readme do original descreve a gestão de Master League como o carro-chefe da
v0.95: "as long as there is free space in the game, u can insert and edit new
Master League players". O contador na tela é o que torna isso utilizável.

---

## Objetivo

Varrer a região de ML, contar vagas, e mostrar.

### O que precisa ser respondido

1. **O que é um slot vazio.** Byte zero? Nome em branco? Marcador próprio?
   Descobrir e escrever — é a definição inteira da feature.
2. **Qual é a região.** `OFS_LINK_ML` está entre os 19 offsets confirmados, e
   `OFS_ML_TEAM_NAME_7`/`_8` também. A WTE-TASK-19 deve ter fechado o resto.
3. **Quantos slots existem no total.** Número fixo do formato.

### A armadilha herdada

O `newWe2002` documenta uma faixa de 16 bytes que o `ed.exe` lê e grava por
engano a partir de memória vizinha — **o slot 64 de um array de 63**
(`OFS_SQUAD_NUMBERS_NATIONAL+1008`, `405724..405739`). É a única divergência
aceita nos golden tests do port Qt.

Contar slots é exatamente a operação onde esse tipo de erro nasce. **Medir o
limite do array, não estimá-lo**, e conferir se o Obocaman comete o mesmo erro
que o Moriero — se cometer, é decisão registrada (reproduzir ou corrigir), não
descuido.

### Verificação

Contar nas duas ROMs e conferir contra o número que o original mostra na tela.
Depois inserir um jogador pelo original, recontar dos dois lados, e ver se
decrementam junto.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/ml-slots.md` | criar |
| `wte/src/we2002_ml.pas` | criar |
| `wte/tests/test_ml.pas` | criar |

---

## Critério de conclusão

- [ ] Definição de "slot vazio" escrita, com evidência
- [ ] Região e total de slots medidos, não estimados
- [ ] Contagem batendo com a tela do original nas duas ROMs
- [ ] Decrementa junto com o original após inserção
- [ ] Conferido se há leitura fora do array, e a decisão registrada
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
