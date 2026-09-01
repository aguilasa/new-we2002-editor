---
id: CORR-PES2-010
title: "Correção: as duas constantes do `scan` do `lzss.py` — uma decide todo verdicto com 128 B de margem, a outra é justificada por um número errado"
type: correção
category: formato
status: concluído
depends_on: []
---

# CORR-PES2-010: os dois limiares do `scan`, e o que o plano afirma por causa deles

## Problema identificado

`scan()` tem dois números cravados, e os dois carregam mais peso do que
aparentam.

**1. `minimum=1024` decide o verdicto de todo contêiner.** Um arquivo é
`none` quando nada decodifica para 1 KiB ou mais — não quando "nada
decodifica". A §1.14(e) do plano, porém, define o verdicto como *"**não é
LZSS** — nada decodifica em lugar nenhum"*, que é mais forte do que se mediu.
O limiar nunca foi justificado por medição, e a margem é fina.

**2. O comentário do `PROBE_CAP` afirma um fato medido, e ele é falso:**

```python
# The largest block any container on these discs decompresses to is 16 KiB.
PROBE_CAP = 1 << 18
```

Medido em `(EsIt)`: o maior bloco tem **16.676 bytes**, e **cinco** blocos
passam de 16 KiB. O `PROBE_CAP` de 256 KiB continua folgado — não há defeito
funcional —, mas a frase que o justifica está errada, e é o tipo de número que
a próxima task herda sem remedir.

## Evidência

O limiar, e o quanto ele segura:

```
$ # os mesmos contêineres, com minimum=64 em vez de 1024
/BIN/ANIME.BIN         none     blocks(min1024)=  0 blocks(min64)=322
/BIN/DEMODATA.BIN      none     blocks(min1024)=  0 blocks(min64)=274
/BIN/CGAF.BIN          none     blocks(min1024)=  0 blocks(min64)= 21
/BIN/GRDM_GJ.BIN       none     blocks(min1024)=  0 blocks(min64)=  1
/BIN/GDC_AD.BIN        partial  blocks(min1024)= 30 blocks(min64)= 37
                                        (os 36 não-`whole` de `(EsIt)`)
```

Ou seja: com 64, **todo** arquivo `none` produz blocos. O `none` do plano é
"nada decodifica **para 1 KiB ou mais**", e a distinção é o limiar, não o
formato.

A margem, medida agora pela primeira vez:

```
min raw among whole-container blocks: 1152
most common sizes: [(8192, 1129), (16384, 881), (7678, 3), (2688, 3),
                    (16381, 3), (1412, 2)]
max raw 16676   over 16 KiB: 5
```

O menor bloco real do disco tem **1.152 bytes**. Entre ele e o limiar há
**128 bytes**. Um bloco real de 1 KiB num quinto disco sairia da conta em
silêncio, e o arquivo dele viraria `none`.

## Causa raiz

Os dois números foram escolhidos por plausibilidade durante a varredura e
ficaram no código como se fossem medidos. O comentário do `PROBE_CAP` chegou a
afirmar a medição; o `minimum` nem isso.

## Correção

### Arquivo: `tools/pes2/lzss.py`

- `minimum` vira constante nomeada, com o número que a justifica no comentário
  — menor bloco real medido **1.152 B**, margem 128 B — e um modo que reporta a
  distribuição (`--sizes`, ou uma linha no `-v`), para que a próxima medição
  não precise de script descartável.
- O comentário do `PROBE_CAP` passa a dizer o valor medido: maior bloco
  **16.676 B**, cinco acima de 16 KiB em `(EsIt)`; o teto de 256 KiB é a folga
  deliberada sobre isso.
- Opcional, e é o que fecha o buraco de verdade: um bloco abaixo do `minimum`
  encontrado **no offset que o cabeçalho nomeia** deixa de ser descartado —
  ali o offset não é palpite.

### Arquivo: `docs/PLAN-PES2-PSX.md`

A definição do verdicto `none` na §1.14(e) passa a dizer o que se mediu:
*"nada decodifica para um bloco de 1 KiB ou mais, em offset nenhum"*, com a
margem de 128 B registrada — é ela que diz quanto o número aguenta.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/lzss.py` | modificar |
| `docs/PLAN-PES2-PSX.md` | modificar |

## Verificação

- [x] as quatro contagens da §1.14(e) continuam idênticas depois da mudança
      (208/172/3/33/2.153 e as outras três linhas)
- [x] a ferramenta imprime o menor e o maior bloco medidos, e os dois batem
      com 1.152 e 16.676 em `(EsIt)`
- [x] `lzss.py --check` verde nos quatro discos
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito.** O `1024` virou `MIN_BLOCK`, com o número que o
justifica no comentário e a consequência escrita: é ele que **define** o
verdicto `none`, e a margem sob ele é de 128 B. O comentário do `PROBE_CAP`
passou a dizer o valor medido e a admitir, em uma linha, o que afirmava
antes. Entrou `--sizes`, que reimprime a distribuição por disco — o ponto é
que a próxima medição não precise de script descartável:

```
block sizes: min 1152  max 16676  over 16 KiB 5  (MIN_BLOCK 1024, margin 128 B; PROBE_CAP 262144)
```

**As quatro contagens não mudaram:** 208/172/3/33/2.153, 210/174/3/33/2.195,
177/141/3/33/1.842, 195/159/3/33/2.027, `CHECK OK` nos quatro.

**Problemas encontrados.** Dois, os dois por medir o que a CORR afirmava de
um disco só:

1. **O maior bloco do conjunto não é 16.676 — é 16.725**, na
   `japanese-shift-jis`, que também tem **sete** blocos acima de 16 KiB
   contra cinco das outras três (a European Deluxe vai a 16.501). A CORR mediu
   só `(EsIt)`. O comentário do `PROBE_CAP` traz os quatro; o teto de 256 KiB
   continua folgado por qualquer um deles.
2. **O item opcional não tem instância nos quatro discos, e por isso ficou de
   fora.** Ele propõe aceitar um bloco abaixo do limiar quando ele está no
   offset que o cabeçalho nomeia. Medido: dos 36 contêineres não-`whole` de
   `(EsIt)`, **zero** decodificam qualquer coisa no offset do cabeçalho — eles
   levantam `LzssError` ali, não um bloco curto. O ramo não teria caso em
   disco nenhum que temos, e um ramo sem caso é o que a CORR-PES2-005 acabou
   de consertar noutro lugar. O buraco que ele mira — bloco real de 1 KiB num
   quinto disco — fica coberto pela outra metade da correção: a margem de
   128 B agora está escrita nos dois lugares, e o `--sizes` a reimprime.

O menor bloco, esse sim, é **1.152 nos quatro discos** — a margem de 128 B
não é de uma amostra.

**Gates.** `lzss.py --check --sizes` nos quatro discos: `CHECK OK` × 4,
exit 0, contagens idênticas às da §1.14(e). `--roundtrip` no disco tocado:
**2153/2153 OK**. `check_tasks.py` 82 tasks ok. Todos os números do doc saíram
da ferramenta. `roms/` intocada.

**Arquivos criados/modificados:**

- `tools/pes2/lzss.py`
- `docs/PLAN-PES2-PSX.md`
