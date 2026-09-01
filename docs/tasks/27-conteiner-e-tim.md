---
id: PES2-TASK-27
title: "Cabeçalho de contêiner e entradas TIM — 4 e 8 bpp com CLUT"
type: engenharia-reversa
category: formato
phase: 7
depends_on: [PES2-TASK-26]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §1.14"
status: pendente
---

# PES2-TASK-27: Contêiner e TIM

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §1.14 e §6.13; a §5 Fase 10 do
  [PLAN-FEATURES](/docs/PLAN-FEATURES.md).
- **É a task de risco mais alto da Fase 7**, pelo mesmo motivo que a Fase 10 é
  a de risco mais alto do PLAN-FEATURES: é o único ponto onde o formato ainda
  é hipótese.

O cabeçalho já está medido como **array de ponteiros de 32 bits para a RAM da
PSX** (`0x800xxxxx`), de largura variável — 16 larguras distintas em `/BIN/`,
de 0 a 204 palavras, **com o mesmo histograma nos dois jogos** (§1.14). O que
não está medido é o que vem depois de descomprimir: a lista de entradas e o
`DATA_HEADER` de 32 bytes (`ID`, `VramX`, `VramY`, `width`, `height`,
`offset`, …) que o PLAN-FEATURES descreve.

---

## Objetivo

Extrair **toda** entrada gráfica dos contêineres, com dimensão e paleta, e
exportá-la como PNG.

### Método

1. **Parsear a lista de entradas** do bloco descomprimido: `DATA_HEADER` de
   32 B, contagem, deslocamento de cada entrada.
2. **Decodificar 4 bpp e 8 bpp com CLUT.** Paleta e imagem são entradas
   distintas do mesmo contêiner — é o que faz o Image Manager do BAT_WE
   mostrar grade × grade em vez de uma lista só.
3. **Exportar PNG indexado**, preservando a paleta (o caminho de volta da
   PES2-TASK-29 depende de a paleta sobreviver ao round-trip).
4. **Conferir a invariante de formato**: `width × height × bpp / 8` bate com o
   tamanho da entrada descomprimida, em 100% dos casos. Entrada que não bate é
   entrada mal parseada, não exceção.
5. **Comparar contra o WE2002.** Os `TEX_*`, `CG*` e `GRDM_*` têm a mesma
   largura de cabeçalho nos dois jogos; se o parser lê os dois, o formato é da
   engine e não da release. Se lê só um, a hipótese da §1.4 tem limite, e o
   limite tem de ser escrito.

### O que a §1.14 já entrega de graça

`/BIN/DAT2D.BIN` no WE2002 guarda as **cores de bandeira** — é onde caem
quatro dos 69 `OFS_*` (§1.4), entre eles `OFS_FLAG_COLOURS_SENEGAL`. O mesmo
arquivo existe no PES2, no **mesmo LBA 5300**. Esta task é, portanto, a via de
entrada mais provável para a PES2-TASK-14 (bandeiras), e as duas devem trocar
achado antes de qualquer uma escrever no mapa.

---

## Critério de conclusão

- [ ] `tools/pes2/bin_archive.py` versionado, com `ls` e `export`.
- [ ] Todas as entradas de `DAT2D*`, `DATSEL*`, `LOGO`, `TITLE`, `CG*` e
      `TEX_*` das **duas** releases extraídas, sem entrada órfã e sem estouro.
- [ ] `w × h × bpp / 8 == tamanho descomprimido` em 100% das entradas, com a
      contagem escrita.
- [ ] O parser rodando também nas duas imagens de WE2002, ou o limite da
      hipótese da §1.4 escrito com os números.
- [ ] Um punhado de PNGs conferido a olho — nenhum quadro do jogo entra no
      git (§2 do plano; vale para asset extraído como vale para screenshot).
- [ ] A relação com `OFS_FLAG_COLOURS_*` avaliada e registrada na §1.14.
- [ ] Escrito na §1.14 do plano.

---

## Log de Execução

*(a preencher)*
