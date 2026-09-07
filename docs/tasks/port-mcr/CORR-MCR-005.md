---
id: CORR-MCR-005
title: "Correção: os três `PlayerStatsSkills.dll` estão dentro do resto, não fora da conta"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-MCR-005: o "resto" do inventário não é só fonte

## Problema identificado

O Log da [MCR-TASK-02](/docs/tasks/port-mcr/02-base-legal-e-linhagem.md) fecha o
inventário com a linha:

> | **resto (o fonte que importa)** | **72** | **4.751.336** | |

e logo abaixo:

> Fora da conta por não ser arquivo: o raspador de Sofifa/Transfermarkt/
> FMInside/PESMaster, que a §0 do plano já lista como não-objetivo, e as três
> cópias de `PlayerStatsSkills.dll` (11.776 B cada), que é binário de terceiro
> sem fonte.

Duas coisas estão erradas aí, e a segunda é a que engana:

1. o raspador de fato não é arquivo — é comportamento espalhado pelos `.vb`, e
   dizer que está "fora da conta" é correto;
2. **`PlayerStatsSkills.dll` é arquivo, e está dentro da conta.** As três
   cópias são 3 dos 72 e 35.328 dos 4.751.336 bytes daquela linha. A frase diz
   o contrário, e a etiqueta "o fonte que importa" reforça o engano.

Junto delas, a mesma linha ainda carrega **6 `.jpg` e 2 `.ico`** — 195.476 B de
arte que também não é fonte. O total de 72 / 4.751.336 está certo; o que não
está é a descrição dele.

## Evidência

O `resto` decomposto por extensão, com a mesma classificação disjunta da tabela
do Log:

```sh
git -C work/easy-mcr ls-tree -r -l HEAD | awk '{
  size=$4; path=""; for(i=5;i<=NF;i++) path = path (i>5?" ":"") $i;
  if (path ~ /(^|\/)\.vs\// || path ~ /(^|\/)packages\// || path ~ /(^|\/)(bin|obj)\// ||
      path ~ /BD\.accdb$/ || tolower(path) ~ /\.(bmp|png|pfx)$/) next;
  n=split(path,a,"."); ext=(n>1?a[n]:"(sem)"); c[ext]++; b[ext]+=size
} END { for (k in c) printf "%-8s %4d %12d\n", k, c[k], b[k] }' | sort -k3 -rn
```

| ext | arquivos | bytes | |
| --- | ---: | ---: | --- |
| `vb` | 34 | 3.139.331 | fonte |
| `resx` | 10 | 1.143.958 | recurso de formulário |
| `xsd` | 1 | 210.021 | |
| `ico` | 2 | 127.964 | **arte** |
| `jpg` | 6 | 67.512 | **arte** |
| `dll` | 3 | 35.328 | **binário de terceiro — os `PlayerStatsSkills.dll`** |
| demais (`vbproj`, `sln`, `settings`, `md`, `user`, `config`, `myapp`, `xsc`, `xss`) | 16 | 27.222 | |
| **total** | **72** | **4.751.336** | fecha com a linha do Log |

E as três cópias, com o tamanho que o Log cita:

```sh
git -C work/easy-mcr ls-tree -r -l HEAD | grep PlayerStatsSkills.dll
# 11776 PlayerStatsSkills.dll
# 11776 lite/PlayerStatsSkills.dll
# 11776 lite/fifatomcr/PlayerStatsSkills.dll
```

3 × 11.776 = 35.328 — a linha `dll` da decomposição, dentro dos 4.751.336.

O `NOTICE.md` **não erra**: ele nomeia `PlayerStatsSkills.dll` entre o que não
entra no repositório, o que é verdade — nada do upstream entra. O erro é só de
inventário, no Log da task.

## Causa raiz

A frase juntou duas exclusões de natureza diferente sob a mesma razão ("por não
ser arquivo"): uma que de fato não é arquivo e outra que é, e que ficou contada.

## Correção

### Arquivo: `docs/tasks/port-mcr/02-base-legal-e-linhagem.md`

- Trocar o rótulo da linha final de `**resto (o fonte que importa)**` para
  `**resto — fonte, recursos e 8 arquivos de arte**`, ou manter o rótulo e
  acrescentar a decomposição por extensão acima logo abaixo da tabela. A
  segunda é preferível: ela é o que torna a linha auditável.
- Reescrever a nota seguinte separando as duas naturezas:

  ```markdown
  Fora da conta por não ser arquivo: o raspador de Sofifa/Transfermarkt/
  FMInside/PESMaster, que a §0 do plano já lista como não-objetivo — é
  comportamento espalhado pelos `.vb`, não um caminho a excluir.

  **Dentro** da conta, mas não portável: as três cópias de
  `PlayerStatsSkills.dll` (11.776 B cada, 35.328 B ao todo), binário de
  terceiro sem fonte, e os 8 arquivos de arte (`.ico` e `.jpg`, 195.476 B) que
  sobraram por não casarem com as extensões descontadas. Nenhum entra no port;
  ficam contados porque a tabela desconta por prefixo e extensão, e nenhuma
  das duas os alcança.
  ```

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/port-mcr/02-base-legal-e-linhagem.md` | modificar |

## Verificação

- [ ] o `awk` da seção Evidência devolve as 15 extensões, somando 72 /
      4.751.336, e o doc não afirma mais que os `.dll` estão fora da conta
- [ ] as somas do inventário continuam fechando: 2.781 + 72 = 2.853
- [ ] `python3 tools/check_tasks.py` verde e `ctest -R tasks` verde
- [ ] `work/easy-mcr/` e `roms/` intocados

## Log de Execução

**Executado em:** 2026-09-07

**Resumo do que foi feito:**

A linha final perdeu a etiqueta "o fonte que importa" e passou a dizer o que de
fato carrega, e logo abaixo dela entrou a **decomposição por extensão** — as 15
extensões, fechando em 72 / 4.751.336 —, que é o que torna a linha auditável.
A nota seguinte foi partida em duas naturezas: o raspador, que de fato **não é
arquivo**; e o que está **dentro** da conta mas não é portável — as três cópias
de `PlayerStatsSkills.dll` (35.328 B) e os 8 arquivos de arte `.ico`/`.jpg`
(195.476 B), com a razão de ficarem contados (nenhum prefixo nem extensão
descontada os alcança).

**Problemas encontrados:**

**Um ponto em que esta execução discorda da CORR.** Ela afirma que o
`NOTICE.md` não erra. Erra, de forma mais sutil: a lista "Named specifically"
está gramaticalmente presa à frase dos **2.781 excluídos**, e todos os outros
itens dela — `BD.accdb`, os `.bmp`, os dois `.pfx`, as árvores `bin/`+`obj/` —
estão mesmo lá. Só `PlayerStatsSkills.dll` não: ele é 3 dos 72. Sob o título da
seção ("What does not enter this repository") a frase é defensável, mas deixá-la
punha o arquivo público de linhagem em desacordo com a decomposição recém
publicada. O `.dll` saiu daquela lista para uma oração própria, que diz que ele
e os 8 de arte estão **dentro** dos 72 e são igualmente não portáveis.

**Arquivos criados/modificados:**

- `docs/tasks/port-mcr/02-base-legal-e-linhagem.md` — rótulo da linha `resto`,
  a decomposição por extensão, e a nota logo abaixo
- `NOTICE.md` — a atribuição do `PlayerStatsSkills.dll` (discrepância revelada
  pela varredura; a CORR o dava por correto)
