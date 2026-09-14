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

---

## Objetivo

Decidir, por medição, qual dado o jogo está desenhando na tela `LOOKS SET`.

---

## Critério de conclusão

- [ ] Trocar `HAIR` na tela e rodar `diff_memory` (ou `snapshot_memory` +
      diff): as regiões que mudam ficam listadas, com endereço e tamanho.
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
