---
id: CORR-PES2-016
title: "Correção: a profundidade é decidida por contêiner, e o `DAT2D.BIN` do PES2 tem 261 paletas de 16 contra 5 de 256"
type: correção
category: formato
status: pendente
depends_on: []
---

# CORR-PES2-016: `depth_of()` escolhe 8 bpp para um arquivo cujas paletas dizem 4

## Problema identificado

A §1.14(f) do plano enuncia a regra que a task descobriu:

> **A largura do CLUT é o que diz a profundidade da imagem.** … 256 cores ⇒
> **8 bpp**, 16 cores ⇒ **4 bpp**, e os dois aparecem no mesmo disco.

O `bin_archive.py` a implementa **por contêiner**:

```python
def depth_of(recs):
    widths = {e.colours for e in recs if e.is_clut}
    return 4 if widths and max(widths) <= 16 else 8
```

Medido: existe contêiner com as **duas** larguras, e é logo o mais importante.
`/BIN/DAT2D.BIN` das duas releases de PES2 tem **261 CLUTs de 16 cores e 5 de
256**, e `depth_of` devolve **8** para o arquivo inteiro, por causa do `max`.
Os 21 registros de imagem dele são, portanto, decodificados na profundidade
das 5 paletas mais raras, contra 261 que dizem o contrário.

E é **silencioso**: a contagem de bytes (`largura × altura × 2`) não muda com a
profundidade — a própria §1.14(f) diz isso —, então o `check` continua verde e
o `export` escreve PNG com o dobro da largura e metade dos pixels certos. É o
mesmo estrago do `LOGO.BIN` que o Log da task descreve ter custado uma corrida,
só que sem o sintoma que denunciou aquele (estourar o fim do arquivo).

`DAT2D.BIN` é o arquivo para o qual a §1.14(f) manda a
[PES2-TASK-14](/docs/tasks/14-bandeiras.md) olhar.

## Evidência

```
$ # larguras de CLUT por contêiner, os que têm mais de uma
PES2 (EsIt)     mixed: [('/BIN/DAT2D.BIN', {256: 5, 16: 261}, depth_of -> 8)]
PES2 (EnFrDe)   mixed: [('/BIN/DAT2D.BIN', {256: 5, 16: 261}, depth_of -> 8)]
japanese        mixed: []
```

Um contêiner, os dois discos de PES2, e é o que guarda as cores de bandeira.
Nos outros 138 contêineres com índice a regra por arquivo coincide com a
regra por imagem, e por isso ninguém tropeçou nela.

## Causa raiz

A regra foi medida em arquivos de paleta única (`TITLE` 8 bpp, `LOGO` 4 bpp) e
implementada como propriedade do contêiner. Ela é propriedade **do par
imagem-paleta**, e o `max()` faz a minoria decidir.

## Correção

### Arquivo: `tools/pes2/bin_archive.py`

- `depth_of` deixa de devolver um número para o arquivo inteiro. Onde a
  profundidade importa — `ls`, `export` — ela sai do **CLUT que se está
  usando**: `4 if clut.colours <= 16 else 8`. O `export` já recebe `--clut`, e
  é ele que decide.
- Onde não há CLUT escolhido, a saída **diz que não sabe**, em vez de assumir
  8 — a mesma disciplina do "não invento par de CLUT" que o módulo já adota.
- O `check` ganha o número: quantos contêineres têm mais de uma largura de
  CLUT. Um contêiner misto é fato do disco, e o gate deve contá-lo, não
  escondê-lo atrás de um `max`.

### Arquivo: `docs/PLAN-PES2-PSX.md`, §1.14(f)

A regra passa a dizer que a profundidade é **do par imagem-paleta**, com o
número que obriga a isso: 261 × 16 contra 5 × 256 no `DAT2D.BIN` do PES2. E
que, como o contêiner não diz qual CLUT vai com qual imagem (limite já
escrito), a profundidade de uma imagem de `DAT2D` **está em aberto** até esse
par ser resolvido.

### Arquivo: `docs/tasks/14-bandeiras.md`

O repasse ganha a consequência: as 261 paletas de 16 cores são a maioria, e a
bandeira quase certamente está entre elas — procurar por índice de CLUT, como
já está escrito, mas sabendo que a imagem correspondente é 4 bpp.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/bin_archive.py` | modificar |
| `docs/PLAN-PES2-PSX.md` | modificar |
| `docs/tasks/14-bandeiras.md` | modificar |

## Verificação

- [ ] `bin_archive.py ls <img> --file /BIN/DAT2D.BIN` mostra profundidade por
      CLUT, não uma só para o arquivo
- [ ] `bin_archive.py check` conta os contêineres de largura mista e o número
      é 1 nas duas releases de PES2, 0 na japonesa
- [ ] as contagens da tabela da §1.14(f) não mudam (918/798/105/15/804 na
      `(EsIt)` e as outras três linhas)
- [ ] um PNG de `DAT2D.BIN` exportado com CLUT de 16 cores sai legível — o
      critério "conferido a olho" da task, aplicado ao caso que faltava
- [ ] `roms/` intocada, e nenhum PNG versionado

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
