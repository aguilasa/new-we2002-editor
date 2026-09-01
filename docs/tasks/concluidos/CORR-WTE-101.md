---
id: CORR-WTE-101
title: "Correção: \"seis seções obrigatórias\" onde o gabarito e a ferramenta têm cinco, e a conta de 481 é só delas"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-101: são cinco seções obrigatórias, não seis

## Problema identificado

O contrato da spec diz **seis** seções obrigatórias em três lugares; a
ferramenta que o cobra reconhece **cinco**:

```python
SECOES = ("Entrada", "Saida", "Bytes tocados",
          "Pre-condicoes", "Comportamento de erro")   # spec_index.py:41
```

O próprio [`GABARITO.md`](../../../wte/re/spec/GABARITO.md) se contradiz na mesma
página: o modelo mostra cinco seções com `**Evidência:**` mais uma `## Notas`
declarada **opcional**, e o parágrafo logo abaixo diz *"As seis seções são
obrigatórias e nesta ordem; `## Notas` é opcional. Cada uma das seis carrega
sua própria linha `**Evidência:**`"* — o que soma sete títulos e não fecha de
nenhum jeito.

A [WTE-TASK-31](/docs/tasks/concluidos/31-fechamento-fase-4.md) herdou a frase e a
republicou: o cabeçalho do `check_fase4.py` e a prosa que ele **gera** no
`wte/re/fase-4.md` repetem "seis seções obrigatórias".

**E a frase gerada erra duas vezes, não uma.** Ela apresenta o 481 como se
fosse o total de linhas `**Evidência:**` das specs:

> Cada uma das seis seções obrigatórias de cada spec carrega a sua linha
> `**Evidência:**`. A distribuição das 481 linhas:

São 481 nas cinco seções cobradas — e **525** no total, porque 44 linhas de
evidência moram em seções que o vocabulário não cobra (`## Notas`,
`## Justificativa`, `## Como o veredito fechou`). O número está certo para o
que foi contado; a frase é que promete outra coisa.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rn "seis seç\|seis secoes" wte/re/spec/GABARITO.md wte/tools/check_fase4.py wte/re/fase-4.md
python3 -c "
import sys; sys.path.insert(0,'wte/tools')
import spec_index as S
print(len(S.SECOES), S.SECOES)"
```

```text
wte/re/spec/GABARITO.md:72:As seis seções são **obrigatórias e nesta ordem**; `## Notas` é opcional. Cada
wte/re/spec/GABARITO.md:170:2. Preencher as seis seções, cada uma com sua evidência.
wte/tools/check_fase4.py:15:| forca da evidencia | as linhas `**Evidencia:**` das seis secoes obrigatorias |
wte/tools/check_fase4.py:781:    a("Cada uma das seis seções obrigatórias de cada spec carrega a sua linha")
wte/re/fase-4.md:145:Cada uma das seis seções obrigatórias de cada spec carrega a sua linha

5 ('Entrada', 'Saida', 'Bytes tocados', 'Pre-condicoes', 'Comportamento de erro')
```

E a conta das linhas, separando o que é contado do que existe:

```bash
python3 - <<'PY'
import sys, csv
from pathlib import Path
sys.path.insert(0,'wte/tools')
import spec_index as S
dentro = fora = 0
with open('wte/re/published_methods.tsv', encoding='utf-8') as f:
    for h in csv.DictReader(f, delimiter='\t'):
        p = Path('wte/re/spec') / f"{h['formulario']}.{h['handler']}.md"
        texto = p.read_text(encoding='utf-8')
        secs = S.secoes_de(texto)
        n = sum(len(S.CABECALHO_EVIDENCIA.findall(secs.get(s, '')))
                for s in S.SECOES)
        dentro += n
        fora += len(S.CABECALHO_EVIDENCIA.findall(texto)) - n
print(dentro, fora, dentro + fora)
PY
```

```text
481 44 525
```

| Afirmado | Medido | Fonte |
|---|---|---|
| seis seções obrigatórias | **cinco** | `spec_index.SECOES` |
| "a distribuição das 481 linhas" `**Evidência:**` | 481 nas cinco cobradas, **525** no arquivo | o script acima |

A distribuição em si está correta e não muda: 468 `disassembly lido`, 10
`diff medido`, 2 `observação de tela`, 1 `não medido`.

## Causa raiz

O `GABARITO.md` contou a `## Notas` opcional junto com as cinco obrigatórias, e
o número saiu de lá para o cabeçalho do `check_fase4.py` e para a prosa que ele
gera.

## Correção

### Arquivo: `wte/re/spec/GABARITO.md`

Trocar as duas frases por **cinco**, dizendo o que cada número é:

> As **cinco** seções acima são obrigatórias e nesta ordem, cada uma com sua
> linha `**Evidência:**`; `## Notas` é opcional e **não** é cobrada.

A linha 170 (*"Preencher as seis seções"*) idem.

### Arquivo: `wte/tools/check_fase4.py`

Linha 15 (cabeçalho) e linha 781 (a prosa gerada): `seis` → `cinco`. E a frase
do total passa a dizer o que conta:

```python
a("Cada uma das cinco seções obrigatórias de cada spec carrega a sua linha")
a("`**Evidência:**`, e é essa a população contada — evidência escrita em")
a("`## Notas`, `## Justificativa` ou `## Como o veredito fechou` fica de fora.")
a(f"A distribuição das {sum(m['evidencias'].values())} linhas cobradas:")
```

Se sair barato, imprimir também quantas ficaram de fora — é uma subtração e
tira a pergunta de quem recontar por `grep`.

### Arquivo: `wte/re/fase-4.md`

**Não editar.** É gerado; sai certo com o gerador corrigido e reexecutado.

### Guarda

O `test_check_fase4.py` ganha um caso que amarra a prosa ao vocabulário:
o texto gerado tem de citar `len(S.SECOES)` por extenso, e não um literal — se
alguém acrescentar uma seção obrigatória, a frase acompanha em vez de virar a
próxima "seis".

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/GABARITO.md` | modificar |
| `wte/tools/check_fase4.py` | modificar |
| `wte/tools/test_check_fase4.py` | modificar — a guarda |
| `wte/re/fase-4.md` | regerar |

## Verificação

- [x] `grep -rn "seis seç\|seis secoes" wte/ docs/` não devolve afirmação viva
- [x] `grep -n "cinco seções" wte/re/fase-4.md` mostra a frase regerada
- [x] O caso novo do `test_check_fase4.py` reprova se a frase voltar a ser literal
- [x] `make -C wte check` verde
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-24

**Resumo do que foi feito:**

Trocado `seis` por `cinco` nos três sítios do contrato — as duas frases do
`GABARITO.md` e o cabeçalho do `check_fase4.py` — e a prosa gerada passou a
dizer **o que conta**: a linha nasce de `por_extenso(len(S.SECOES))`, e o
parágrafo declara que evidência em `## Notas`, `## Justificativa` e `## Como o
veredito fechou` fica de fora, com o número medido (44) ao lado das 481
cobradas. O `medir()` ganhou `evidencias_fora`, que é a subtração entre as
linhas do arquivo e as das seções cobradas.

A guarda (`TestProsaDaEvidencia`, cinco casos) amarra três coisas: o cardinal
sai de `len(S.SECOES)`, a linha viva do `fase-4.md` cita o cardinal de hoje, e a
linha do gerador tem de conter `por_extenso(len(S.SECOES))` — plantar o literal
`"cinco"` de volta a reprova, medido. O 44 também é conferido contra a medida
independente, não contra um literal.

**Problemas encontrados:**

A varredura achou dois sítios que a CORR não previa, os dois em **Log de
Execução**: `23-formato-da-spec.md:103` (*"O gabarito tem as seis seções
obrigatórias"*) e `26-handlers-de-edicao.md:383` (*"`disassembly lido` nas seis
seções"*). Log costuma ser registro histórico e fica de fora — foi o critério
da CORR-WTE-102 para o `94`. Aqui não vale: `94` era verdade no dia em que foi
medido, e `seis` nunca foi. As duas specs citadas têm cinco linhas
`**Evidência:**` e cinco seções obrigatórias mais `## Notas`; era o mesmo
engano herdado do gabarito, repetido. Corrigidos os dois.

**Arquivos criados/modificados:**

- `wte/re/spec/GABARITO.md` — as duas frases
- `wte/tools/check_fase4.py` — cabeçalho, `por_extenso()`, `evidencias_fora`, a prosa
- `wte/tools/test_check_fase4.py` — `TestProsaDaEvidencia`, cinco casos
- `wte/re/fase-4.md` — regerado
- `docs/tasks/concluidos/23-formato-da-spec.md`, `docs/tasks/concluidos/26-handlers-de-edicao.md` — a varredura
