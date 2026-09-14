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
