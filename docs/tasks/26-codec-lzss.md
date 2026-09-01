---
id: PES2-TASK-26
title: "O codec LZSS dos contêineres `BIN/*.BIN`"
type: engenharia-reversa
category: formato
phase: 7
depends_on: []
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §1.14"
status: pendente
---

# PES2-TASK-26: O codec LZSS dos contêineres

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §1.14, e a §5 Fase 9 do
  [PLAN-FEATURES](/docs/PLAN-FEATURES.md), que descreve o mesmo codec do lado
  do WE2002.
- **É leitura pura.** Não precisa de emulador, de cartão nem de cópia gravável
  — como a PES2-TASK-08 e a 09, é o trabalho barato que continua se a Fase 2
  travar.

Os 208 arquivos `form1` de `/BIN/` do PES2 são contêineres comprimidos com o
LZSS que o `WECompressor` do CARP descomprime. A §1.14 mede a evidência: os
2.070 primeiros bytes do fluxo de `DAT2D.BIN` são **idênticos** entre o
PES2 `(EsIt)` e o WE2002 japonês, e o histograma de largura de cabeçalho é o
mesmo nos dois discos.

O que **não** está medido é o fluxo inteiro: prefixo idêntico prova que o
mesmo decodificador consome os dois, não que ele chega ao fim de todos os 208.
É isso que esta task fecha.

---

## Objetivo

Um `tools/pes2/lzss.py` que descomprima **todo** contêiner de `/BIN/` das duas
releases, com round-trip provado.

### Método

1. **Portar o decodificador** a partir da descrição do `WECompress.cpp`
   (Python 3, `bytes`/`bytearray`, nada de dependência nova). Os dois pontos
   que a §5 Fase 9 do PLAN-FEATURES marca para revisão valem aqui inteiros:
   - `while (k3-- >= 0)` usa `k3` **assinado**; tratar como não-assinado muda
     o teto do laço e o erro só aparece em blocos específicos;
   - o opcode `0xC0..0xFE` (cópia literal em bloco) é **lido** pelo
     descompressor e **não emitido** pelo compressor do CARP. Manter a
     assimetria; não "completar por simetria" sem medir.
2. **Achar o início do fluxo** pelo cabeçalho de ponteiros (§1.14) — não por
   constante. A largura varia de 0 a 204 palavras entre os arquivos.
3. **Rodar nos 208 × 2 releases + nas duas imagens de WE2002**, e classificar
   cada arquivo em: descomprimiu inteiro / parou no meio / não é fluxo LZSS.
4. **Round-trip**: `decompress(compress(x)) == x` para cada bloco
   descomprimido. **Não** se exige `compress(decompress(y)) == y` — o
   compressor do CARP nunca reproduz os bytes da Konami, e a §5c do
   PLAN-FEATURES já mediu por quê.

### A pergunta aberta que esta task tem de responder

A §5c do PLAN-FEATURES afirma que o fluxo de `TEX_00.BIN` começa em **28**.
A varredura de cabeçalho da §1.14 diz **48** — 12 palavras, uma delas nula no
índice 6, nos **dois** jogos. As duas leituras não podem estar certas. Medir
qual descomprime, e corrigir a que estiver errada, **no arquivo em que ela
está escrita**.

---

## Critério de conclusão

- [ ] `tools/pes2/lzss.py` versionado, com `--check` que roda sobre uma imagem.
- [ ] Os 208 contêineres de cada release classificados, com a conta dos três
      números: descomprimiu inteiro, parou no meio, não é LZSS.
- [ ] `decompress(compress(x)) == x` em 100% dos blocos descomprimidos.
- [ ] O início do fluxo de `TEX_00.BIN` decidido por medição, e a fonte errada
      corrigida (§1.14 aqui, ou §5c do `PLAN-FEATURES.md`).
- [ ] Alvo `pes2_image` do `ctest` cobrindo a varredura; *skipped* sem imagem.
- [ ] Escrito na §1.14 do plano, com a contagem final.
- [ ] `NOTICE.md` com a seção de crédito da §9 do `PLAN-FEATURES.md` — **é
      bloqueante**, e sai no mesmo commit do primeiro arquivo derivado.

---

## Log de Execução

*(a preencher)*
