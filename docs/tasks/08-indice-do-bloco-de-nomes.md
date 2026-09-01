---
id: PES2-TASK-08
title: "Os 624 candidatos de 16 bits — existe índice para o bloco de nomes?"
type: engenharia-reversa
category: formato
phase: 3
depends_on: []
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §1.10"
status: pendente
---

# PES2-TASK-08: O índice do bloco de nomes

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §1.10, e a regra conservadora da
  §6.2 que depende desta resposta.
- **É a pergunta que decide se o editor pode renomear com liberdade.**

Os registros de nome são de tamanho variável — string, terminador,
alinhamento a 4. A varredura da §1.10 procurou tabela de ponteiros de 32
bits apontando para o bloco e achou **três candidatos isolados, ruído**. Há
**624 candidatos de 16 bits**, não investigados.

Enquanto isso não estiver resolvido, a regra é: **um nome novo só pode
ocupar até o tamanho do slot alinhado que já existe** (§6.2). Se houver
índice reconstruível, a regra afrouxa; se o jogo percorre linearmente, ela
fica para sempre.

---

## Objetivo

Responder, com medida: **existe índice para o bloco de nomes, ou o jogo o
percorre linearmente?**

### Como um índice se pareceria

Uma sequência de `N` valores de 16 bits, monotonicamente crescente, com
`N` igual a uma contagem já conhecida (1.399, 1.242, 463, 106, 95) e
diferenças que batem com os comprimentos alinhados dos nomes.

**Este último teste é o forte**, e é barato: os comprimentos das 1.399
entradas de `SELECTC.BIN` já são conhecidos. Se algum dos 624 candidatos
tiver deltas que reproduzam essa sequência de comprimentos, é o índice — e
a chance de coincidência é nula.

### Se não houver

Duas verificações antes de declarar "linear":

1. procurar índice de **offset relativo ao bloco**, não absoluto — 16 bits
   cobrem 65 KiB e o pool tem ~13 KiB, então cabe;
2. procurar índice **por elenco** em vez de por jogador — 54 × 23 sugere que
   o jogo pode indexar o time e contar 23 dali.

E, ainda assim, a resposta negativa é resultado: escrevê-la no plano fecha a
§6.2 como decisão medida em vez de precaução.

---

## Critério de conclusão

- [ ] Os 624 candidatos classificados, com o critério de classificação
      escrito e a ferramenta versionada em `tools/pes2/`.
- [ ] Resposta escrita na §1.10 do plano: índice localizado (arquivo, offset,
      largura, base) **ou** "linear", com as duas verificações acima feitas.
- [ ] Se houver índice: um `poke` que escreve um nome **mais longo** e o
      índice ajustado, verificado na tela.
- [ ] Se não houver: a §6.2 passa de precaução a decisão, com esta task
      citada como a medida.

---

## Log de Execução

*(a preencher)*
