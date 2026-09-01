---
id: CORR-WTE-025
title: "Correção: a faixa `11797..26528` é numeração 1-based do `cmp`, e vai virar exceção declarada como se fosse offset"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-025: a faixa da gravação do aviso está deslocada em um byte

## Problema identificado

O achado 2 da WTE-TASK-12 mediu que aceitar o aviso de tamanho grava **11.952
bytes** na imagem, e registrou a faixa como `11797..26528` em três lugares:

| Arquivo | Linha |
|---|---|
| `wte/re/visual.md` | 98 — "Faixa `11797..26528`, **setores 5 a 11**" |
| `docs/tasks/concluidos/12-comparacao-visual.md` | 151 — mesma faixa no Log |
| `docs/tasks/concluidos/22-harness-golden.md` | 100 e **145** |

A linha 145 da WTE-TASK-22 é a que dói: é um critério de conclusão, e diz que a
faixa `11797..26528` **"vira exceção declarada"** no harness golden.

Esses dois números são a **numeração 1-based do `cmp -l`**, não offsets. A
contagem (11.952) e os setores (5 a 11) estão certos; os extremos estão ambos
deslocados em +1. Os offsets reais são `11796..26527`.

O repositório já tem convenção fixada, e é a oposta: a única exceção declarada
do `newWe2002` está em `tools/golden_check.sh:84-85` como
`KNOWN_START=405724` / `KNOWN_END=405739`, que é
`OFS_SQUAD_NUMBERS_NATIONAL (404716) + 1008` — **offset 0-based**. Um
`golden_check.sh` da fase 4 escrito a partir da linha 145 mascararia o byte
26528 (que não diverge) e acusaria o 11796 (que diverge) como divergência
inesperada — falha vermelha logo na primeira execução do gate, com a causa
escondida num deslocamento de um byte.

## Evidência

Reproduzido nesta revisão, no `:99`, sobre `work/wte-golden-european-deluxe.bin`
recém-copiado de `roms/golden-european-deluxe.bin` (`cmp` = 0 antes de clicar
"Sim" no aviso):

```
$ cmp -l roms/golden-european-deluxe.bin work/wte-golden-european-deluxe.bin | wc -l
11952
$ cmp -l ... | awk 'NR==1{f=$1} {l=$1} END{print f, l}'
11797 26528              # posições do cmp -- 1-based
```

O mesmo par de arquivos comparado por offset:

```
$ python3 -c '...'       # varredura byte a byte, índice 0-based
n: 11952 offsets 0-based: 11796 .. 26527 setores: 5 a 11
```

Os dois lados concordam na contagem e nos setores; divergem no extremo, que é
exatamente a diferença entre "posição do `cmp`" e "offset".

A convenção contrária, no projeto irmão:

```
$ grep -n 'KNOWN_' tools/golden_check.sh
84:KNOWN_START=405724
85:KNOWN_END=405739
$ grep -n 'SQUAD_NUMBERS_NATIONAL' src/core/include/we2002/Offsets.hpp
77:inline constexpr Offset OFS_SQUAD_NUMBERS_NATIONAL = 404716;
```

`404716 + 1008 = 405724` — offset, não posição de `cmp`.

## Causa raiz

A faixa foi copiada da saída do `cmp -l`, que numera bytes a partir de 1, e
escrita como se fosse offset.

## Correção

### Arquivo: `wte/re/visual.md`

Na linha 98, trocar a faixa por `11796..26527` e **dizer a base**, para o
próximo leitor não repetir a conversão de cabeça. Sugestão de redação:

```markdown
Faixa `11796..26527` (offsets 0-based; o `cmp -l` imprime `11797..26528`,
porque numera a partir de 1), **setores 5 a 11** — região de metadado ISO9660,
não de dado do jogo.
```

Acrescentar, ao lado do roteiro de reprodução, o comando que devolve offset em
vez de posição — para que a medida seja reproduzível na mesma base em que será
consumida.

### Arquivo: `docs/tasks/concluidos/12-comparacao-visual.md`

Linha 151, no Log de Execução: mesma faixa corrigida. O Log é história, mas
este número é o que a WTE-TASK-22 herdou.

### Arquivo: `docs/tasks/concluidos/22-harness-golden.md`

Linhas 100 e 145: faixa corrigida, e no critério da linha 145 dizer
explicitamente que os limites são **offsets 0-based, inclusivos**, como
`KNOWN_START`/`KNOWN_END` do `tools/golden_check.sh` do `newWe2002`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/visual.md` | modificar |
| `docs/tasks/concluidos/12-comparacao-visual.md` | modificar |
| `docs/tasks/concluidos/22-harness-golden.md` | modificar |

## Verificação

- [x] `grep -rn '11797\|26528' --include='*.md' .` não devolve mais nenhuma
      afirmação viva da faixa como offset (a menção à saída do `cmp`, se
      mantida, tem de estar rotulada como tal)
- [x] A faixa `11796..26527` aparece nos três arquivos, com a base declarada
- [x] `make -C wte check` continua verde
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-09

**Resumo do que foi feito:**

Faixa trocada para `11796..26527` nos três sítios, sempre com a base dita
(**offsets 0-based, inclusivos**) e com a posição do `cmp -l` mantida ao lado,
rotulada como tal — quem chegar pelo `cmp` reconhece o número que viu e sabe
por que ele não serve.

No `visual.md` foi acrescentado o comando que mede na base certa, colado com a
saída (`n: 11952 offsets 0-based: 11796 .. 26527 setores: 5 a 11`): a medida
passa a ser reproduzível na mesma base em que será consumida, que era o buraco
que abriu esta correção. O critério da linha 145 da WTE-TASK-22 agora aponta o
`KNOWN_START`/`KNOWN_END` do `tools/golden_check.sh` do `newWe2002` como a
convenção a seguir, e diz explicitamente que os `11797..26528` do `cmp -l` não
são ela.

**Problemas encontrados:**

Nenhum. A reprodução do `:99` **não** foi refeita — a contagem (11.952) e os
setores (5 a 11) não estavam em disputa, e o que a correção afirma é a base, que
a semântica do `cmp -l` decide sozinha: `cmp -l` sobre dois arquivos de 3 bytes
que diferem no offset 0-based `1` imprime `2`. Refazer a rodada custaria uma
cópia de ~474 MB e uma sessão de GUI no display serializado sem mudar o veredito.

Os setores foram reconferidos nos dois extremos, porque a correção afirma que
eles não mudam: `11796 // 2352 = 5`, `26527 // 2352 = 11`, e `26528 // 2352 = 11`
também — o deslocamento de um byte não atravessa fronteira de setor, que é
exatamente por que o erro sobreviveu a três arquivos.

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `wte/re/visual.md` | modificado — faixa, base e o comando de medida colado |
| `docs/tasks/concluidos/12-comparacao-visual.md` | modificado — faixa e base no Log |
| `docs/tasks/concluidos/22-harness-golden.md` | modificado — faixa e base na medida 2 e no critério |
| `docs/tasks/concluidos/correcoes-progresso.md` | modificado — `[x]`, data e status |
| `docs/tasks/concluidos/CORR-WTE-025.md` | modificado — `status:`, verificação e este Log |
