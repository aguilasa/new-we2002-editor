---
id: CORR-PES2-010
title: "Correção: as duas constantes do `scan` do `lzss.py` — uma decide todo verdicto com 128 B de margem, a outra é justificada por um número errado"
type: correção
category: formato
status: pendente
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

- [ ] as quatro contagens da §1.14(e) continuam idênticas depois da mudança
      (208/172/3/33/2.153 e as outras três linhas)
- [ ] a ferramenta imprime o menor e o maior bloco medidos, e os dois batem
      com 1.152 e 16.676 em `(EsIt)`
- [ ] `lzss.py --check` verde nos quatro discos
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
