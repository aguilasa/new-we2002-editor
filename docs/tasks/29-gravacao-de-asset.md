---
id: PES2-TASK-29
title: "Gravação de asset — fit-or-fail, recompressão só do editado"
type: ferramenta
category: formato
phase: 7
depends_on: [PES2-TASK-27]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §1.14"
status: pendente
---

# PES2-TASK-29: Gravação de asset

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §1.14, §6.7 e §6.13; a §5(a) e a
  §5(c) do [PLAN-FEATURES](/docs/PLAN-FEATURES.md), que são as duas decisões
  estruturais que esta task herda.
- **É a primeira vez que o projeto escreve fora do banco de texto.** O
  `iso.py inject` já sabe reinjetar arquivo preservando setor e cauda; o que
  falta é remontar o **conteúdo** do arquivo.

### As duas decisões que vêm prontas

**Fit-or-fail.** Orçamento = tamanho original arredondado para cima até o fim
do último setor. Não coube, **recusa e diz quantos bytes faltaram**. Rebuild
de ISO e realocação de extent ficam **fora do projeto** — não "para depois".
O motivo é medido no WE2002 e vale igual aqui: o jogo não acha arquivo por
nome, as LBAs estão cravadas no código MIPS, e o buffer de destino continua do
tamanho antigo mesmo que o diretório ISO seja corrigido.

**Entrada não editada nunca recomprime.** O arquivo guarda os bytes
comprimidos originais de cada entrada e regenera só as que o usuário tocou.
É isso que dá a invariante que serve de teste: *abrir e salvar sem editar
devolve a imagem byte a byte idêntica* — a mesma condição 3 da §0.

### A divergência que esta task tem de resolver, não herdar

A §5(b) do `PLAN-FEATURES` decidiu **recalcular EDC/ECC** no caminho de
assets. A §6.7 deste plano decide **preservar**. As duas não podem valer no
mesmo comando.

A reconciliação proposta, e que a task deve confirmar por medição: **preservar
por padrão** — é o que mantém o round-trip da §0 e o controle negativo do
`iso.py` honestos — e oferecer o recálculo como **comando avulso opt-in**,
que é exatamente o escape hatch `fixecc` que o próprio PLAN-FEATURES prevê.
Nunca ligado à gravação.

---

## Objetivo

Escrever um asset editado de volta na imagem, sem crescer o extent e sem
mexer no que não foi tocado.

### Método

1. **Importar PNG indexado**, validando dimensão, profundidade e paleta contra
   a entrada de destino. Divergência é recusa, não conversão silenciosa.
2. **Recomprimir só a entrada tocada**, remontar o contêiner e conferir o
   orçamento **antes** de escrever.
3. **Descomprimir de volta e comparar antes de ir para o disco** — sem
   exceção, sem flag para desligar.
4. **Escrever pelo `iso.py inject`**, que já preserva setor e cauda.
5. **Controle negativo**, como o do `iso.py`: uma edição de um pixel tem de
   produzir diferença **localizada e contável**, senão a guarda não sabe ficar
   vermelha.

---

## Critério de conclusão

- [ ] Abrir e salvar sem editar devolve a imagem **byte a byte idêntica**, nas
      duas releases.
- [ ] Trocar uma cor de paleta altera **exatamente** os setores daquele
      arquivo, com a conta.
- [ ] Estouro de orçamento **recusa**, dizendo quantos bytes faltaram.
- [ ] Toda entrada regravada é descomprimida e comparada antes de ir ao disco.
- [ ] Política de EDC/ECC decidida por medição e escrita na §6.7 — com o
      recálculo, se entrar, como comando avulso e nunca no caminho de gravação.
- [ ] Controle negativo versionado, provando que a guarda fica vermelha.
- [ ] A tela alterada vista no emulador (§4.1 — o oráculo é o jogo).
- [ ] Alvo de `ctest` cobrindo o round-trip; *skipped* sem imagem.

---

## Log de Execução

*(a preencher)*
