---
id: CORR-WTE-104
title: "Correção: o golden-24 grava duas vezes num time cujos dois primeiros cobradores são iguais — o vaivém seria invisível"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-104: o `golden-24` é cego para o vaivém que ele existe para medir

## Problema identificado

O terceiro critério da [WTE-TASK-34](/docs/tasks/concluidos/34-bateria-golden-completa.md)
é *"gravação dupla coberta"*, e a razão de existir está escrita no enunciado da
fase 6: o `ed.exe` **não é idempotente** — `Load`+`Save` troca os dois primeiros
cobradores (`OFS_KICKER`) de cada clube de ML, e gravar duas vezes volta ao
início. O
[`golden-24-gravacao-dupla`](../../../wte/tests/roteiros/golden-24-gravacao-dupla.txt)
escolheu a tática justamente por ser a gravação que carrega cobrador.

**O roteiro grava no time 2, e os dois primeiros cobradores do time 2 são
iguais.** Na ROM japonesa virgem eles são `[7, 7, 8, 7, 7, 8]`: trocar o
primeiro pelo segundo devolve exatamente os mesmos bytes. Se o vaivém existisse
neste editor, este roteiro passaria igual — e se não existir, também. **O
roteiro não consegue distinguir os dois casos**, e é essa distinção que o
critério pede.

A task registra que falta o **terceiro ponto** — comparar uma gravação com
duas —, e encaminha para a
[WTE-TASK-35](/docs/tasks/concluidos/35-divergencias-deliberadas.md). Rodado nesta
revisão, ele fecha em zero; mas fecha em zero **pelo motivo errado**, porque o
time escolhido torna a pergunta indecidível.

## Evidência

O terceiro ponto, rodado em 2026-08-25 — `golden-17-tatica` (uma gravação) e
`golden-24-gravacao-dupla` (duas), os dois em `--modo controle --manter`, sobre
a mesma ROM japonesa:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
bash wte/tools/golden_check.sh wte/tests/roteiros/golden-17-tatica.txt \
     --modo controle --manter          # cp work/golden-a.bin uma-gravacao.bin
bash wte/tools/golden_check.sh wte/tests/roteiros/golden-24-gravacao-dupla.txt \
     --modo controle --manter          # cp work/golden-a.bin duas-gravacoes.bin
cmp -l uma-gravacao.bin duas-gravacoes.bin | wc -l
cmp -l roms/japanese-shift-jis.bin duas-gravacoes.bin | wc -l
```

```text
0            <- uma gravacao e duas dao a MESMA imagem
11966        <- e as duas gravaram: 11.966 bytes mudam contra a ROM virgem
```

**E o que torna o zero indecidível** — os seis bytes de cobrador do time 2, no
endereço que o `GravaTaticaNaImagem` calcula (`TATICA_COBRADOR_LOGICO +
6·time`, setor base 850, = **2329068**):

```text
virgem  [7, 7, 8, 7, 7, 8]
uma     [7, 7, 8, 7, 7, 8]
duas    [7, 7, 8, 7, 7, 8]
```

`cobrador[0] == cobrador[1] == 7`. A troca que o critério procura é a
identidade neste time.

**Há 41 times onde ela não seria:**

```bash
python3 - <<'PY'
SETOR_BYTES, INICIO, DADOS = 2352, 24, 2048
end = lambda b, l: b*SETOR_BYTES + INICIO + (l//DADOS)*SETOR_BYTES + l % DADOS
with open('roms/japanese-shift-jis.bin', 'rb') as f:
    for t in range(96):
        f.seek(end(850, 0x46228 + 6*t + 2*(t//95)))
        b = list(f.read(6))
        if b[0] != b[1]:
            print(t, b)
PY
```

```text
5 [9, 5, 5, 5, 7, 5]
7 [6, 4, 6, 6, 8, 8]
10 [9, 8, 9, 9, 9, 1]
...                      (41 times ao todo)
```

| O que o critério pede | O que o roteiro mede |
|---|---|
| a segunda gravação reproduz (ou não) a troca de `cobrador[0]`/`[1]` | que os dois lados chegam ao mesmo byte gravando duas vezes num time onde `cobrador[0] == cobrador[1]` |

**O irmão dele está bem.** O terceiro ponto do
`golden-23-multiplas-edicoes` foi rodado na mesma revisão e **passa**: contra a
ROM virgem a imagem muda em 20 blocos, com o byte de barra em `2328195`
(`OFS_TEAM_BARS + 11`) **e** os dez blocos de nome (`1013916`, `1882876`,
`2003952`, `2004968`, `2005364`, `2830924`, `4234852`, `4599396`, `5651436`,
`5652628`). As duas edições acontecem mesmo; a correção abaixo é só do
`golden-24`.

## Causa raiz

O time do roteiro foi herdado do `golden-17-tatica` — de onde vieram todas as
coordenadas, de propósito — sem conferir se naquele time os dois cobradores
diferem, que é a única condição em que a troca é observável.

## Correção

### Arquivo: `wte/tests/roteiros/golden-24-gravacao-dupla{,.port}.txt`

Trocar o time por um em que `cobrador[0] != cobrador[1]`. O **5** é o primeiro
da lista (`[9, 5, 5, 5, 7, 5]`) e custa só mudar a contagem de `Down` — o
roteiro chega ao time 2 com três, e ao 5 com seis; nenhuma outra coordenada
muda, porque a tela de tática é a mesma.

**Vale escrever no cabeçalho por que aquele time**, com os seis bytes e o
endereço, senão a próxima pessoa "simplifica" de volta para o 2:

```text
# O TIME 5 NAO E ESCOLHA LIVRE. Os cobradores dele sao [9, 5, ...] em 2329086:
# `cobrador[0] != cobrador[1]`, que e a UNICA condicao em que a troca do
# `Load`+`Save` e observavel. No time 2 eles sao [7, 7, ...] e a troca e a
# identidade -- o roteiro passaria com vaivem e sem ele.
```

### O terceiro ponto vira registro, não recado

Depois da troca, rodar o par `golden-17` × `golden-24` como acima e **escrever
o resultado**, que é decisivo nos dois sentidos:

- **imagens iguais** → o `wte.exe` é idempotente nesse caminho, não há vaivém a
  reproduzir, e é resultado negativo legítimo — o enunciado da fase 6 afirma um
  comportamento do **`ed.exe`**, que é outro binário e outro caminho de código;
- **imagens diferentes** → há vaivém, e ele já está reproduzido (o par golden
  fecha byte-idêntico), o que o transforma em entrada da
  [WTE-TASK-35](/docs/tasks/concluidos/35-divergencias-deliberadas.md) com o offset medido.

O lugar do registro é o gerador do
[`golden.md`](../../../wte/re/golden.md) — hoje ele descreve o terceiro ponto
como coisa a fazer (*"o terceiro ponto de cada um é o par que grava uma vez
pelo mesmo caminho"*) e não carrega resultado nenhum.

### Guarda

O `check_golden.py` já recusa roteiro com par ausente do TSV. O que ele não
sabe é se um roteiro **pode** medir o que diz medir, e isso não se mecaniza em
geral — mas este caso sim: um teste que leia os seis bytes de cobrador do time
que o `golden-24` usa e reprove se os dois primeiros forem iguais custa cinco
linhas e amarra o roteiro à sua própria premissa.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tests/roteiros/golden-24-gravacao-dupla.txt` | modificar |
| `wte/tests/roteiros/golden-24-gravacao-dupla.port.txt` | modificar |
| `wte/tools/check_golden.py` | modificar — o resultado do terceiro ponto |
| `wte/tools/test_check_golden.py` | modificar — a guarda dos dois cobradores |
| `wte/re/golden.tsv` | regerar as linhas do `golden-24` (as duas ROMs, os dois modos) |
| `wte/re/golden.md` | regerar |

## Verificação

- [x] Os cobradores do time do roteiro diferem:
      time 5, `[9, 5, 5, 5, 7, 5]` em 2329086
- [x] `golden-24` verde nos dois modos na japonesa, com o controle antes
      (controle 158 s, golden 144 s)
- [x] `cmp -l` entre a imagem de uma gravação e a de duas está **escrito** no
      `golden.md`, com o número — é **0**
- [x] `python3 wte/tools/check_golden.py --check` verde
- [x] `make -C wte check` verde (789 testes)
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-25

**Resumo do que foi feito:**

O `golden-24` passou do time 2 para o **5** (`[9, 5, 5, 5, 7, 5]` em 2329086),
nos dois lados do par — só a contagem de `Down` muda, de três para seis, porque
a tela de tática é a mesma. O cabeçalho diz por que aquele time, com os seis
bytes e o endereço, para a próxima pessoa não "simplificar" de volta.

**O terceiro ponto foi medido, e o resultado é negativo e decisivo:**

| Medida | Bytes |
|---|---:|
| uma gravação × duas gravações | **0** |
| ROM virgem × uma gravação | 11.962 |

Os cobradores do time 5 saem **intactos** dos três estados —
`[9, 5, 5, 5, 7, 5]` na virgem, depois de uma gravação e depois de duas. Num
time onde a troca *seria* visível, ela não acontece: **o `wte.exe` não tem o
vaivém**. A não-idempotência do enunciado da fase 6 é do `ed.exe`, outro
binário e outro caminho de código. E as duas gravações aconteceram, o que
impede o zero de ser trivial.

O registro entrou no gerador do `golden.md` como tabela medida com guarda — o
padrão do `GOLDEN_DE` do `check_fase4.py` —, e as quatro linhas do `golden-24`
no `golden.tsv` foram remedidas pela bateria (japonesa `PASSOU`/`PASSOU`,
158 s e 144 s; europeia `SEM_ORACULO`/`NAO_APLICAVEL`, que é o esperado ali).

**Problemas encontrados:**

**O instrumento que a CORR mandava usar deixou de servir por causa da própria
correção.** A seção "O terceiro ponto vira registro" manda rodar o par
`golden-17-tatica` × `golden-24` — que era o par certo enquanto os dois
gravavam no time 2. Com o `golden-24` no time 5 e o `golden-17` no 2, o `cmp`
entre as duas imagens mede a diferença entre **dois times**, não entre uma
gravação e duas: daria um número grande e sem significado.

O lado "uma gravação" passou a ser o **próprio `golden-24` truncado depois da
descarga** — mesmas coordenadas, mesmo time, mesmo caminho, uma gravação a
menos. É instrumento melhor que o `golden-17` era, e não custa gate novo: o
roteiro truncado é aparelho de medição, não entra no repositório. Mover o
`golden-17` para o time 5 seria a outra saída e foi recusada — ele é um gate
verde com história própria, e a CORR diz que a correção é só do `golden-24`.

A guarda lê o time **do próprio roteiro**, pela contagem de `Down` até
`= SELECIONA_TIME`, e não de um literal: plantando o time 2 de volta, dois
casos reprovam, um deles com a mensagem que nomeia os cobradores iguais.

**Arquivos criados/modificados:**

- `wte/tests/roteiros/golden-24-gravacao-dupla.txt`, `.port.txt` — o time 5
- `wte/tools/check_golden.py` — `TERCEIRO_PONTO` e a seção que ele gera
- `wte/tools/test_check_golden.py` — `TestPremissaDaGravacaoDupla`, 5 casos
- `wte/re/golden.tsv` — as quatro linhas do `golden-24`, remedidas
- `wte/re/golden.md` — regerado
