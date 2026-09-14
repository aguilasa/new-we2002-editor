---
id: LOOKS-TASK-08
title: "Incógnita (a) — de onde vem o boneco: `EDT_MOD.BIN` ou os TMDs de `0x00168xxx`"
type: engenharia-reversa
category: formato
phase: 2
depends_on: ["LOOKS-TASK-07"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §6"
status: pendente
---

# LOOKS-TASK-08: De onde vem o boneco da tela

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §6,
  incógnita (a), e §1.6.
- **São três candidatos, não dois.** O `EDT_MOD.BIN` traz **dois** modelos de
  onze peças — duas listas de ponteiros, compartilhando duas peças, sobre o
  mesmo esqueleto (§1.5, medido pela
  [`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md) em 2026-09-14).
  A pergunta "de onde vem o boneco" tem de escolher entre **lista A, lista
  B e os TMDs de `0x00168xxx`**, e os dois save states — goleiro e jogador
  de linha — são o estímulo óbvio para decidir se as duas listas são esses
  dois bonecos.
- **É a incógnita de maior risco do plano.** Quatro TMDs Sony de verdade —
  `id=0x41`, `flags=1`, texturizados, modos `0x2d` e `0x3d`, com 92, 261, 30 e
  18 vértices — vivem em `0x0016821C`, `0x00168C0C`, `0x0016A2C4` e
  `0x0016A650`, e **não pertencem a nenhum dos dois arquivos de modelo**.
- A GPU desenha em **4-bit CLUT** com textura ligada; a primitiva de 24 bytes
  das seções **não tem UV**. Os dois não podem estar certos para a mesma
  geometria.
- **Nada de geometria deve ser escrito antes de responder isto** — é a ordem
  obrigatória da §7 do plano.
- **Comece por `load_state`.** Os dois states de 2026-09-14 põem o jogo na tela
  de edição: **slot 1 goleiro, slot 2 jogador de linha**, os dois no disco
  inglês. Recarregar entre medições dá baseline byte a byte idêntico, e é o que
  faz o diff medir só o que você mudou.
- **A RAM se lê por MCP vivo.** O `savestate.py` não alcança a RAM nesta
  máquina: sem CLI `zstd` e sem o módulo `zstandard`, ele lê cabeçalho e para.
- **Os dois states são um controle de graça.** Goleiro e jogador de linha usam
  uniformes diferentes e, possivelmente, peças diferentes. O que diferir entre
  os dois é **posição ou uniforme**, não LOOKS — e isso separa dois eixos sem
  custo nenhum.

- **O `MODEL.BIN` guarda uma terceira forma de ponteiro, ainda não lida, e são
  DUAS corridas dela** — candidatas junto com as outras. Medido em 2026-09-14
  pela [`LOOKS-TASK-05`](/docs/tasks/looks/05-arquivos-de-modelo.md) e
  remedido pela
  [`CORR-LOOKS-013`](/docs/tasks/looks/CORR-LOOKS-013.md), que achou esta
  linha falando de uma só: 16 das 18 listas do cabeçalho abrem com tag `0x80`,
  e **12** miram o offset **104** enquanto **4** miram o **232**. Nenhum dos
  dois é seção — são corridas de ponteiros KSEG0 crus, sem tag e sem
  terminador, de **64** e de **32** ponteiros, apontando para dentro da região
  de geometria (104: 15.152, 15.768, 16.384, 17.200, …; 232: 49.856, 49.856,
  50.240, 50.240, … — e os pares repetidos ali são achado por si só). O
  `read_pointer_list()` não as lê, e ninguém mediu o que agrupam nem por que
  são duas. Se a resposta da incógnita (a) for "o boneco vem do `MODEL.BIN`",
  **são essas corridas que dizem qual dos modelos dele**, e a hipótese do
  `we3d` — 14 jogadores de 11 peças — se confere ali. **Procure duas tabelas,
  não uma**, e a segunda pode ser justamente o que distingue os agrupamentos.
- **E as duas listas de uma entrada do `MODEL.BIN` nomeiam seção**: tag `0x02`,
  mirando 1816 e 4792, que são as duas primeiras seções do arquivo.

---

## Objetivo

Decidir, por medição, qual dado o jogo está desenhando na tela `LOOKS SET`.

---

## Critério de conclusão

- [ ] Carregar o state, tirar `snapshot_memory`, trocar `HAIR`, e rodar
      `diff_memory`: as regiões que mudam ficam listadas, com endereço e
      tamanho.
- [ ] A medição é **repetida a partir do state recarregado**, e dá o mesmo
      resultado. Diff que não reproduz depois de `load_state` é ruído, não
      achado.
- [ ] O mesmo diff é feito no **slot 1 e no slot 2**, e a comparação entre os
      dois diz o que é do boneco e o que é do uniforme.
- [ ] Fica decidido, com a evidência ao lado, se o boneco vem do
      `EDT_MOD.BIN`, dos quatro TMDs, ou de uma combinação — e o que os quatro
      TMDs são, se não forem o boneco.
- [ ] Se forem os TMDs: de onde eles vêm (qual arquivo, qual carga) fica
      medido, e o plano ganha a seção nova.
- [ ] Se for o `EDT_MOD.BIN`: fica explicado **como a textura entra** numa
      geometria cuja primitiva não tem UV.
- [ ] O resultado é escrito no plano **na seção que muda**, não num apêndice.

---

## Log de Execução

*(preencher ao executar)*
