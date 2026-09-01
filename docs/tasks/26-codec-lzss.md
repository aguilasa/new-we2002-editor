---
id: PES2-TASK-26
title: "O codec LZSS dos contêineres `BIN/*.BIN`"
type: engenharia-reversa
category: formato
phase: 7
depends_on: []
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §1.14"
status: concluído
---

# PES2-TASK-26: O codec LZSS dos contêineres

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §1.14, e a §5 Fase 9 do
  [PLAN-FEATURES](/docs/PLAN-FEATURES.md), que descreve o mesmo codec do lado
  do WE2002.
- **É leitura pura.** Não precisa de emulador, de cartão nem de cópia gravável
  — como a PES2-TASK-08 e a 09, é o trabalho barato que continua se a Fase 2
  travar.

Os arquivos `form1` de `/BIN/` do PES2 são contêineres comprimidos com o
LZSS que o `WECompressor` do CARP descomprime — 208 em `(EsIt)` e 210 em
`(EnFrDe)`; a contagem é do disco, não do jogo. A §1.14 mede a evidência: os
2.070 primeiros bytes do fluxo de `DAT2D.BIN` são **idênticos** entre o
PES2 `(EsIt)` e o WE2002 japonês, e o histograma de largura de cabeçalho é o
mesmo nos dois discos.

O que **não** está medido é o fluxo inteiro: prefixo idêntico prova que o
mesmo decodificador consome os dois, não que ele chega ao fim de todos eles.
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
3. **Rodar nas duas releases + nas duas imagens de WE2002**, e classificar
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

- [x] `tools/pes2/lzss.py` versionado, com `--check` que roda sobre uma imagem.
- [x] Os contêineres de cada release classificados, com a conta dos três
      números: descomprimiu inteiro, parou no meio, não é LZSS.
- [x] `decompress(compress(x)) == x` em 100% dos blocos descomprimidos.
- [x] O início do fluxo de `TEX_00.BIN` decidido por medição, e a fonte errada
      corrigida (§1.14 aqui, ou §5c do `PLAN-FEATURES.md`).
- [x] Alvo `pes2_image` do `ctest` cobrindo a varredura; *skipped* sem imagem.
- [x] Escrito na §1.14 do plano, com a contagem final.
- [x] `NOTICE.md` com a seção de crédito da §9 do `PLAN-FEATURES.md` — **é
      bloqueante**, e sai no mesmo commit do primeiro arquivo derivado.

---

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito.** `tools/pes2/lzss.py` porta o codec do
`WECompress.cpp` da WECompressor do CARP — baixado do repositório público que
o `PLAN-FEATURES` §1 nomeia, porque nada dele existia nesta máquina. Os dois
pontos que o plano marcou para revisão são os que a leitura confirma e o
código comenta no lugar: `while (k3-- >= 0)` com `k3` **assinado** dá bloco de
`k3 + 1` literais, e o opcode `0xC0..0xFE` é lido e nunca emitido. Um terceiro
detalhe que um porte apressado perde: `i = k | 0xFF00` não é dado — o `0xFF00`
é contador de deslocamento, e é o `(i & 0x100) == 0` que recarrega o byte de
flags a cada oito tokens.

**A busca de casamento não foi portada, de propósito.** O anel de 1.024 bytes
com cadeia de hash virou índice de chave de três bytes, o que é legítimo aqui
porque o codificador pode escolher qualquer casamento válido — e a §5c do
`PLAN-FEATURES` já media que a saída recomprimida nunca é a da Konami. Por
isso a invariante afirmada é `decompress(compress(x)) == x`, e só ela.

**Resultado medido**, `python3 tools/pes2/lzss.py <a> <b> <c> <d> --check`:

| Disco | contêineres | inteiro | parcial | não é LZSS | blocos |
|---|---:|---:|---:|---:|---:|
| PES2 `(EsIt)` | 208 | 172 | 3 | 33 | 2.153 |
| PES2 `(EnFrDe)` | 210 | 174 | 3 | 33 | 2.195 |
| WE2002 European Deluxe | 177 | 141 | 3 | 33 | 1.842 |
| WE2002 japonês | 195 | 159 | 3 | 33 | 2.027 |
| **total** | **790** | **646** | **12** | **132** | **8.217** |

Round-trip **8.217 de 8.217** blocos, nos quatro discos. `CHECK OK` nos
quatro. `ctest -R pes2` verde em 12,45 s.

**A divergência do critério, resolvida: é 48.** Nas quatro imagens, 24, 28, 32
e 44 falham no `TEX_00.BIN`, e falham cedo — na primeira distância que aponta
para antes do começo da saída. A §5c do `PLAN-FEATURES` foi corrigida no
arquivo dela, e com o provável motivo de a medição antiga não se reproduzir:
**na imagem golden European Deluxe 18 dos 105 `TEX_*.BIN` são Form 2**, o
`TEX_00.BIN` entre eles, e o `iso.py` recusa lê-los, então quem mediu em
2026-08-02 leu com outro fatiamento de setor — o que casa com o
`16.400 = 16.384 + 16` da linha velha. (Este Log dizia "os 105" até a
[CORR-PES2-014](/docs/tasks/CORR-PES2-014.md); os outros 87 são Form 1.)
As outras cinco linhas daquela tabela **se reproduzem exatamente** pelo
`lzss.py`: `DAT2D` 8/7.447/16.345, `LOGO` 8/3.186/8.192, `TITLE`
8/3.015/8.192, `T_NAME` 4/1.890/8.192 e `DATSEL3` 8/2.973/8.192. Essa
concordância é a melhor evidência de que o porte está certo, porque nenhum dos
cinco números foi olhado antes de a ferramenta os imprimir.

**Os três verdictos precisaram ser redefinidos, e o markdown desta task foi
adaptado.** Ele pedia "descomprimiu inteiro / parou no meio / não é fluxo
LZSS", supondo que um contêiner é fluxo comprimido de ponta a ponta. Não é:
depois do último bloco vem uma **tabela de entradas** de registros de 16 bytes
— 15.538 bytes dela em `DAT2D.BIN` do PES2 `(EsIt)` —, e contar isso como
"parou no meio" reportaria defeito onde não há. Os verdictos passaram a ser
*inteiro* (fluxo no offset que o cabeçalho nomeia), *parcial* (há fluxo, mas
não ali) e *não é LZSS* (nada decodifica), com os bytes fora de qualquer fluxo
medidos e reportados, nunca julgados. A tabela de entradas é assunto da
PES2-TASK-27, e a linha está escrita no arquivo dela.

**O achado que vale repassar: onze `CG*.BIN` não são LZSS.** Nem no offset do
cabeçalho, nem em lugar nenhum do arquivo — depois dos ponteiros de RAM vem
`00000041 00000000 00000001`. A §5 Fase 10 do `PLAN-FEATURES` conta com eles
como contêiner gráfico, e o critério de conclusão da PES2-TASK-27 mandava
extrair "todas as entradas de … `CG*`". Os dois foram anotados: a task 27
ganhou o item e o critério dela foi corrigido.

**Arquivos criados/modificados**

- `tools/pes2/lzss.py` — novo
- `tools/pes2/check_image.py` — o `--check` do codec no `pes2_image`
- `tests/CMakeLists.txt` — o comentário do que o `pes2_image` cobre
- `NOTICE.md` — a seção de crédito ao CARP, **bloqueante**, no mesmo commit
- `docs/PLAN-PES2-PSX.md` — a §1.14(e), com a tabela dos quatro discos, e a
  divergência fechada
- `docs/PLAN-FEATURES.md` — a linha do `TEX_00` da §5c corrigida, a lista de
  offsets de início `(4, 8, 48)`, e o item da §11 fechado
- `docs/tasks/27-conteiner-e-tim.md` — o repasse dos três achados e a correção
  do critério
- `docs/tasks/progresso.md`, `docs/prompts/perfil-pes2.md`, `CLAUDE.md` — o
  gate novo e a ferramenta nova

**Problemas encontrados.** Nenhum bloqueante. Três coisas custaram tempo e
ficam registradas: a fonte do CARP **não existe nesta máquina** e teve de ser
baixada do GitHub; o encadeamento dos blocos **não é contíguo** — há folga de
0 a 3 bytes de alinhamento e, entre alguns, mais de mil bytes de metadados, o
que obrigou a varredura a ressincronizar de quatro em quatro bytes; e a
primeira definição de "inteiro" (cauda menor que 2.048 bytes) reprovava
arquivos sadios, porque a cauda é a tabela de entradas e o tamanho dela é
proporcional ao número de blocos.
