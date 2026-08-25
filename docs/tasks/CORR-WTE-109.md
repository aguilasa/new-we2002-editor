---
id: CORR-WTE-109
title: "Correção: quatro sítios do lado WTE atribuem a não-idempotência ao \"editor original\", que aqui é o wte.exe — e o único caminho medido não a tem"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-109: "o editor original não é idempotente" — qual editor?

## Problema identificado

A [CORR-WTE-104](/docs/tasks/CORR-WTE-104.md) mediu, em 2026-08-25, que o
`wte.exe` **não** troca os cobradores ao gravar tática duas vezes: uma gravação
e duas dão a mesma imagem, e os seis bytes de `OFS_KICKER` saem intactos dos
três estados.

A [CORR-WTE-108](/docs/tasks/CORR-WTE-108.md) conferiu o plano e o achou limpo.
**A varredura dela achou outra coisa:** quatro sítios vivos do lado WTE
afirmam a não-idempotência falando de *"o original"* ou *"o editor original"*
— e **neste projeto "o original" é o `wte.exe`**, não o `ed.exe`. O port é o app
Lazarus; o original é o binário do Obocaman.

A frase é herdada do `newWe2002`, onde ela é **verdadeira e medida** — lá o
oráculo é o `ed.exe`. Ao migrar para as tasks do WTE ela trocou de sujeito sem
trocar de palavras.

| Sítio | O que diz | Qual editor o leitor entende |
|---|---|---|
| [`wte/tools/gravacao_controle.py:197`](../../wte/tools/gravacao_controle.py) | *"o `Load`+`Save` do editor original não é idempotente"* | `wte.exe` |
| [`wte/re/gravacao-controle.md:19`](../../wte/re/gravacao-controle.md) | idem — **é gerado pelo de cima** | `wte.exe` |
| [`docs/tasks/19-os-50-offsets-restantes.md:41`](/docs/tasks/19-os-50-offsets-restantes.md) | *"O `Load`+`Save` do original **não é idempotente**"* | `wte.exe` |
| [`docs/tasks/27-handlers-de-gravacao.md:91`](/docs/tasks/27-handlers-de-gravacao.md) | *"o `Load`+`Save` do original não é idempotente"* | `wte.exe` |

O `golden-02-gravacao.txt:16` diz o mesmo, e o
`golden-24-gravacao-dupla.txt:9` também — mas este atribui (*"o `newWe2002`
registra que…"`*), o que o salva. Os de `docs/PLAN-LINUX.md` e do `CLAUDE.md`
estão **certos**: são do outro projeto, onde o oráculo é o `ed.exe`.

## Por que isto não foi consertado junto

**Porque a medição não cobre a afirmação inteira.** A CORR-WTE-104 mediu **um**
caminho de gravação — o ` Accept` da tela de tática
(`estrategia.BitBtn3Click`), que é a gravação que carrega `OFS_KICKER`. A frase
dos quatro sítios é sobre o ciclo `Load`+`Save` em geral.

Trocar "o original" por "o `ed.exe`" nos quatro seria provavelmente certo e
**não está medido**: se algum outro caminho do `wte.exe` reproduzir o vaivém, a
troca teria criado a mentira simétrica. Redimensionar isso dentro da
CORR-WTE-108 — cujo escopo é uma frase sobre o plano — seria o que o
`03-corrigir.md` chama de resolver de afogadilho.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rn "não é idempotente\|nao e idempotente" docs wte CLAUDE.md
```

```text
docs/tasks/19-os-50-offsets-restantes.md:41:O `Load`+`Save` do original **não é idempotente**: ele troca os dois primeiros
docs/tasks/27-handlers-de-gravacao.md:91:`Load`+`Save` do original não é idempotente (troca os dois primeiros cobradores
wte/tools/gravacao_controle.py:197:    w("`Load`+`Save` do editor original não é idempotente.")
wte/re/gravacao-controle.md:19:`Load`+`Save` do editor original não é idempotente.
```

E o que está medido contra isso, do `wte/re/golden.md` (gerado):

| Medida | Bytes |
|---|---:|
| uma gravação × duas gravações (tática, time 5) | **0** |
| ROM virgem × uma gravação | 11.962 |

`OFS_KICKER` do time 5: `[9, 5, 5, 5, 7, 5]` na ROM virgem, depois de uma
gravação e depois de duas.

## Causa raiz

Frase verdadeira sobre o `ed.exe`, migrada do `newWe2002` para as tasks do WTE
sem trocar o sujeito. É a mesma família da
[CORR-WTE-101](/docs/tasks/CORR-WTE-101.md) — número que migra de um documento
para outro e envelhece no destino —, com sujeito no lugar de número.

## Correção

### Primeiro medir, depois escrever

O que falta é saber se **algum** caminho de gravação do `wte.exe` troca o par.
O barato é o `gravacao-controle`: ele já grava sem editar nada e mede o que
muda de graça, nas duas ROMs. Rodá-lo **duas vezes seguidas** sobre a mesma
cópia e comparar as duas saídas responde a pergunta geral pelo mesmo preço da
resposta particular que a CORR-WTE-104 pagou.

- **Nenhum caminho troca** → os quatro sítios trocam *"o original"* por *"o
  `ed.exe`"*, com o número ao lado; o `gravacao_controle.py` é gerador, então
  a correção entra nele e o `.md` é regerado.
- **Algum troca** → a frase fica, ganha o caminho nomeado, e vira entrada da
  [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md) com o offset.

### Guarda

O `check_divergencias.py` não alcança isto — não é isenção. O lugar natural é o
próprio `gravacao_controle.py`, que já publica número medido: se ele passar a
comparar as duas gravações, a afirmação do `.md` deixa de ser herdada e passa a
sair da corrida.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/gravacao_controle.py` | modificar — a medida e a frase |
| `wte/re/gravacao-controle.md` | regerar |
| `docs/tasks/19-os-50-offsets-restantes.md` | modificar |
| `docs/tasks/27-handlers-de-gravacao.md` | modificar |
| `wte/tests/roteiros/golden-02-gravacao.txt` | modificar |

## Verificação

- [x] A segunda gravação foi medida, e o número está escrito — **0 bytes** nos
      dois caminhos, com 41 times onde a troca apareceria e **0** trocados
- [x] `grep -rn "do original não é idempotente" docs wte` não devolve
      afirmação sem sujeito — só o teste, que cita a forma velha para a recusar
- [x] `make -C wte check` verde (815 testes, era 809)
- [x] `roms/` intocada; trabalhou sobre cópia

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-25

**Resumo do que foi feito:**

Medido e depois escrito, nessa ordem. Dos 17 caminhos de gravação, **dois**
tocam `OFS_KICKER` — lido da seção `## Bytes tocados` das 96 specs, não de
memória: o ` Accept` da tática e o import de `.mcr`. Os dois gravam duas vezes
seguidas sem trocar o par:

| Caminho | uma × duas | a gravação aconteceu |
|---|---:|---:|
| tática (CORR-WTE-104, time 5) | **0** B | 11.962 B contra a virgem |
| import de `.mcr` (esta CORR, time 3) | **0** B | 12.419 B contra a virgem |

O segundo foi medido aqui, encadeando duas importações da mesma fixture sobre a
mesma cópia. **E o zero não é cego:** depois da importação, **41** dos 96 times
têm `cobrador[0] != cobrador[1]` — é neles que uma troca apareceria —, e
**zero** mudaram na segunda gravação. Também zero em toda a imagem, nos 307 MB.

O achado que fecha a pergunta geral: **o `wte.exe` não tem ciclo `Load`+`Save`
de banco inteiro.** Ele grava por área, e a frase herdada descreve uma
propriedade de carga-e-gravação do banco todo, que é o que o `ed.exe` faz.

Corrigidos seis sítios, mais o gerador. A guarda
(`TestIdempotencia`, 6 casos) mora no `test_gravacao_controle.py` e cobra a
coerência entre a tabela medida e a prosa gerada — plantando a frase velha de
volta, ela reprova.

**Problemas encontrados:**

**A receita da CORR não se aplicava à ferramenta que ela nomeia.** Ela mandava
rodar o `gravacao-controle` "duas vezes seguidas sobre a mesma cópia". O
`gravacao_controle.py` é gerador **offline**: lê `io-medido.tsv` e
`cmp-medido.tsv` e escreve prosa; não roda o oráculo, então rodá-lo duas vezes
não mede nada. A medição foi feita onde ela existe — `golden_check.sh` com o
`golden-12-mcr2iso`, encadeado. O gerador continua sendo o lugar certo do
*registro*, que é a outra metade do que a CORR pedia.

**A lista de sítios da CORR estava incompleta: são seis, não quatro.** A
varredura achou `docs/tasks/20-round-trip-headless.md:95` e — o que mais
importa — `docs/prompts/02-revisar.md:167`, que é **prompt vivo**: ele mandava
o revisor cobrar gravação dupla porque *"o editor não é idempotente"*. Item de
checklist com premissa falsa é pior que doc velho, porque dirige trabalho
futuro. Reescrito: a gravação dupla continua valendo — o que só aparece na
segunda gravação não aparece em lugar nenhum —, e o motivo agora é manter
verdadeiro o que foi medido, não reproduzir um vaivém que não existe.

**A própria task 19 já acertava em outro lugar.** A linha 41 dizia *"o
`Load`+`Save` do original não é idempotente"*, e a linha 286 do mesmo arquivo
diz *"não é o `Load`+`Save` não idempotente **do `ed.exe`**"*. O sujeito certo
estava escrito duzentas linhas abaixo do errado, no mesmo documento — o que
mostra que a confusão não foi ignorância e sim uma frase copiada sem reler.

Os sítios que **não** foram tocados, e por quê: `docs/PLAN-LINUX.md` e o
`CLAUDE.md` são do outro projeto, onde o oráculo é o `ed.exe` e a frase é
verdadeira e medida; `analisar_io.py`, `offsets-novos.md` e a linha 286 da task
19 já nomeavam o `ed.exe`; `conta_ml.py`, `ml-slots.md`,
`boton_dialogo_weClick.md` e `we2002_estado.pas` falam de outra idempotência —
a da sentinela de arranque.

**Arquivos criados/modificados:**

- `wte/tools/gravacao_controle.py` — a tabela `IDEMPOTENCIA` e a prosa
- `wte/re/gravacao-controle.md` — regerado
- `wte/tools/test_gravacao_controle.py` — `TestIdempotencia`, 6 casos
- `docs/tasks/19-os-50-offsets-restantes.md`, `20-round-trip-headless.md`,
  `27-handlers-de-gravacao.md` — o sujeito, com a medida
- `docs/prompts/02-revisar.md` — o item de checklist (varredura)
- `wte/tests/roteiros/golden-02-gravacao.txt`,
  `golden-24-gravacao-dupla.txt` — os cabeçalhos
