---
id: CORR-WTE-079
title: "Correção: o compara_tela.sh ficou com dois blocos de --malha colados no lugar errado"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-079: o `compara_tela.sh` ficou com dois blocos de `--malha` colados no lugar errado

## Problema identificado

O modo `--malha` entrou no
[`wte/tools/compara_tela.sh`](../../wte/tools/compara_tela.sh) na sétima
passagem da [WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md), e a emenda
deixou **dois trechos mortos**, um em cada função de captura.

**1. `captura_oraculo`: o bloco `malha` aparece duas vezes seguidas.** O
primeiro termina em `return 0`, então o segundo — o que conta o disparo no
trace — é inalcançável:

```bash
  if [ "$MODO" = malha ]; then
    abre_estrategia "$destino" || { limpa; return 4; }
    limpa
    return 0
  fi
  if [ "$MODO" = malha ]; then          # <-- inalcançável
    abre_estrategia "$destino" || { limpa; return 4; }
    local mal
    mal=$(grep -c 'estrategia.malla1MouseDown' "$TRACE" 2>/dev/null || echo 0)
    ...
```

Do lado do oráculo o bloco morto é o **certo** de estar morto — não existe
trace ali, o `mal` daria 0 e o `return 5` reprovaria toda corrida. Mas ele está
morto por acidente, e quem ler vai concluir que o lado do oráculo confere o
disparo, quando não confere.

**2. `captura_port`: um `if [ "$MODO" = malha ]` aninhado dentro do ramo
`cor|grade`, com um `continue` fora de laço.** Nesse ramo o `$MODO` é
`cor` ou `grade` por construção, então a condição nunca é verdadeira:

```bash
  if [ "$MODO" = cor ] || [ "$MODO" = grade ]; then
    abre_editor_de_cor "$destino" || { limpa; return 4; }
    # ...
    if [ "$MODO" = malha ]; then        # <-- impossível aqui dentro
    python3 "$AQUI/compara_tela.py" --malha --indice "$indice" \
        ...
    continue                            # <-- `continue` sem laço nenhum
  fi
```

Essa chamada ao `compara_tela.py --malha` é **cópia** da que vive no laço
principal (a que de fato roda). O `continue` num corpo de função sem laço é
erro de tempo de execução em bash — hoje inerte porque a condição nunca fecha,
mas é a forma clássica de virar defeito no dia em que alguém mexer na condição.

**Nada disso invalida a medição da task.** O `--malha` roda pelo caminho
correto e foi reproduzido nesta revisão: `PASSOU: so a coluna clicada andou, e
andou 80 px nos dois lados`. O que está errado é o texto do instrumento, não o
resultado.

## Evidência

Rodado nesta revisão, com o `Xvfb :98` de pé:

```text
compara_tela: time 2 -- a malha de marcadores do estrategia (clique na coluna 2, linha 5)
  marcador    oraculo antes/depois   port antes/depois   delta
  simbolo1     None/None            316/316         None / 0
  simbolo2      316/396             316/396         80 / 80
  simbolo3      380/380             316/316         0 / 0
  simbolo4      460/460             316/316         0 / 0
  PASSOU: so a coluna clicada andou, e andou 80 px nos dois lados
```

As duplicatas, localizadas:

```bash
grep -n 'MODO" = malha' wte/tools/compara_tela.sh
grep -n 'compara_tela.py' wte/tools/compara_tela.sh
```

O segundo comando mostra a chamada `--malha` **duas vezes**: na linha 562,
dentro do ramo `cor|grade` do `captura_port`, e na linha 697, dentro do laço
`for indice in "$@"` — esta última é a que executa.

## Causa raiz

Emenda do modo novo aplicada em dois pontos por engano, e o `return 0` do
primeiro bloco escondeu o segundo.

## Correção

### Arquivo: `wte/tools/compara_tela.sh`

1. Em `captura_oraculo`, apagar **um** dos dois blocos `malha`. Qual fica
   depende do que se quer do lado do oráculo: ali não há trace, então o certo é
   ficar com o primeiro (o que só abre o `estrategia` e volta) e **dizer no
   comentário** que a confirmação de que o clique chegou é do lado do port e da
   comparação de delta, não daqui.
2. Em `captura_port`, apagar o `if [ "$MODO" = malha ]` aninhado, a chamada ao
   `compara_tela.py --malha` que ele embrulha e o `continue` solto. O bloco
   `malha` legítimo do `captura_port` já existe **antes**, no mesmo nível do
   ramo `cor|grade`, e é ele que faz a conferência de disparo.

Depois de cortar, o script deve passar por `bash -n` e o `--malha` continuar
dando o mesmo veredito.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/compara_tela.sh` | modificar |

## Verificação

- [x] `bash -n wte/tools/compara_tela.sh` sem erro
- [x] `grep -c 'MODO" = malha' wte/tools/compara_tela.sh` cai de **5** para
      **3** — o enunciado desta correção contou 4, e eram 5 (496, 501, 544,
      561, 696); os dois cortados são o 501 e o 561
- [x] `grep -c 'compara_tela.py" --malha' wte/tools/compara_tela.sh` cai para 1
- [x] `bash wte/tools/compara_tela.sh --malha` continua imprimindo
      `PASSOU: so a coluna clicada andou, e andou 80 px nos dois lados`
- [x] `bash wte/tools/compara_tela.sh --grade 2 9 63` continua verde — 16/16
      amostras nos dois lados, 5.168 px e 9.800 px com tolerância zero
- [x] `make -C wte check` verde — 695 testes, `OK (skipped=1)`, rc=0
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-21

**Resumo do que foi feito:**

Dois cortes, 20 linhas fora e 3 dentro:

1. `captura_oraculo` — apagado o **segundo** bloco `malha`, inalcançável desde
   o `return 0` do primeiro. Ficou o primeiro, que só abre o `estrategia` e
   volta, com o comentário que faltava: do lado do oráculo não há trace, e a
   confirmação de que o clique chegou vem do lado do port (que conta o
   `malla1MouseDown`) e da comparação de delta entre os dois;
2. `captura_port` — apagado o `if [ "$MODO" = malha ]` aninhado dentro do ramo
   `cor|grade`, com a chamada ao `compara_tela.py --malha` e o `continue` solto
   que ele embrulhava. O bloco `malha` legítimo já existe antes, no mesmo nível
   do ramo.

O `if [ "$MODO" = grade ]` que vinha logo depois estava indentado com 2 espaços
— resto da mesma emenda — e foi para 4, o nível do corpo do ramo.

**Problemas encontrados:**

A contagem do enunciado está errada por um: `grep -c 'MODO" = malha'` dá **5**
hoje, não 4, e cai para 3 e não para 2. As cinco ocorrências são as linhas 496,
501, 544, 561 e 696; as duas cortadas são a 501 e a 561. O sintoma descrito
está exato — o erro é só na régua do checklist.

**Arquivos criados/modificados:**

- `wte/tools/compara_tela.sh`
