---
id: CORR-WTE-059
title: "Correção: a spec do `lista_equiposChange` dá para o veredito `aberto` uma razão que a seção seguinte desmente"
type: correção
category: engenharia-reversa
status: concluído
depends_on: []
---

# CORR-WTE-059: a razão escrita do `aberto` já não é a razão verdadeira

## Problema identificado

Em [`wte/re/spec/MainForm.lista_equiposChange.md`](../../wte/re/spec/MainForm.lista_equiposChange.md),
o bloco que justifica o veredito termina assim:

> É o custo de ainda não ter conferido contra a tela, e a razão de o veredito
> continuar `aberto`.

A linha **seguinte** do mesmo arquivo abre a seção:

> ## A conferência de tela — três times, e os dois erros que ela achou

A frase foi escrita na sexta passagem, quando a conferência de tela ainda não
existia; a seção que a contradiz entrou na oitava. O arquivo ficou afirmando
como pendente exatamente aquilo que o parágrafo de baixo documenta como feito —
e feito com resultado, já que foi ali que apareceram os dois erros de mapeamento
de nome.

O veredito `aberto` **está certo**, e o problema é só a razão escrita. A razão
verdadeira está três parágrafos acima, e é outra: `TControl::SetEnabled` tem zero
`call rel32` na `.text`, a seção **Saída** foi rebaixada para `nao medido`, e o
Pascal reproduz ~20 `.Enabled :=` que ninguém confirmou. Quem ler de baixo para
cima leva a impressão de que falta uma conferência que já aconteceu, e para de
procurar a que falta de verdade.

## Evidência

```
$ grep -n 'razão de o veredito\|^## A conferência de tela' \
    wte/re/spec/MainForm.lista_equiposChange.md
160:É o custo de ainda não ter conferido contra a tela, e a razão de o veredito
161:continuar `aberto`.
163:## A conferência de tela — três times, e os dois erros que ela achou
```

A conferência aconteceu, e foi refeita nesta revisão com o mesmo resultado:

```
$ bash wte/tools/compara_tela.sh 2 9 63
compara_tela: time 2   barras oraculo/port [64, 53, 75, 75, 75]  PASSOU
compara_tela: time 9   barras oraculo/port [75, 64, 75, 75, 75]  PASSOU
compara_tela: time 63  barras oraculo/port [104, 75, 97, 97, 97] PASSOU
```

A razão que continua de pé:

```
$ awk '/^## Saída/,/^## Bytes/' wte/re/spec/MainForm.lista_equiposChange.md \
    | grep 'Evidência'
**Evidência:** nao medido
```

## Causa raiz

A oitava passagem acrescentou a seção nova ao fim do arquivo sem reler o
parágrafo que ela tornava falso.

## Correção

### Arquivo: `wte/re/spec/MainForm.lista_equiposChange.md`

Trocar a frase de fecho do bloco por uma que nomeie a razão que sobrou: o
veredito segue `aberto` porque a seção **Saída** está `nao medido` — o caminho
pelo qual o original habilita controle não foi encontrado —, e **não** por falta
de conferência de tela, que está logo abaixo.

Se a [CORR-WTE-057](/docs/tasks/CORR-WTE-057.md) for executada antes desta e a
conferência do estado de habilitação subir a seção Saída para
`observação de tela`, a razão muda de novo; nesse caso escreva a que valer no
dia, e não as duas.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/MainForm.lista_equiposChange.md` | modificar |

## Verificação

- [x] O arquivo não afirma em nenhum ponto que a conferência de tela está por
      fazer — a única ocorrência da frase antiga é a citação dela dentro do
      bloco que a aposenta
- [x] A razão escrita do `aberto` é a mesma que a seção Saída sustenta
- [x] `python3 wte/tools/spec_index.py --check` verde
- [x] `make -C wte check` verde
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-11

**Resumo do que foi feito:**

A [CORR-WTE-057](/docs/tasks/CORR-WTE-057.md) foi executada antes desta, no
mesmo lote, e mudou o terreno: a seção **Saída** subiu de `nao medido` para
`observacao de tela`. Então a razão escrita não é nenhuma das duas que esta
correção previa — nem "falta conferir a tela" (falso desde a 8ª passagem) nem
"a Saída está `nao medido`" (falso desde a 057). A que valia no dia, e que
ficou escrita:

- o **efeito** foi visto e o **mecanismo** não: `observacao de tela` diz que a
  tela mostrou o que liga e o que desliga, não por onde o original liga, e o
  Pascal reproduz 27 `.Enabled :=` apoiado nisso;
- e a conferência achou dois defeitos de comportamento — os `dorsal1..23` um a
  menos e o `iguala_nombres` que o port não desabilita — que continuam sem
  conserto.

O parágrafo ganhou junto o registro de que **já esteve errado uma vez**, com o
ponteiro para esta correção. Frase de fecho é lida como veredito, e essa é a
segunda vez que a seção seguinte muda debaixo dela.

**Problemas encontrados:**

Nenhum. A ordem do lote resolveu o único risco que a correção nomeava: se ela
tivesse rodado antes da 057, a razão escrita teria envelhecido em uma hora.

**Arquivos criados/modificados:**

- `wte/re/spec/MainForm.lista_equiposChange.md` — o parágrafo de fecho do bloco
  do veredito
