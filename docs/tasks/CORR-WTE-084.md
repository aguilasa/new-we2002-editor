---
id: CORR-WTE-084
title: "Correção: a bandeira do ml_teams[22] sai 2 px mais abaixo, e a barra `equipe` do oráculo sai fora da grade"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-084: o time 85 diverge por posição, não por cor

## Problema identificado

A [CORR-WTE-083](/docs/tasks/CORR-WTE-083.md) deu cor às dez paletas de
bandeira que o `we2002_core` não carrega, e **nove das dez fecharam em pixel**.
A décima — `ml_teams[22]` (`EMILIA`, combo **85**) — continua divergindo, e a
causa não é mais a paleta: as cores e o estêncil estão certos.

Sobraram **duas** diferenças no mesmo time, e elas parecem irmãs sem que se
tenha provado que são:

1. **A bandeira sai 2 px mais abaixo no port.** As faixas têm a mesma cor e a
   mesma espessura; o desenho inteiro está deslocado para baixo, com duas
   linhas pretas no topo e duas linhas de azul a menos embaixo;
2. **A barra `equipe` do oráculo mede 76 px, e 76 não está na grade.** A
   largura é `11 * v + 9`, que só produz `… 64, 75, 86 …`. O port desenha
   **75**, que é o `v = 6` do `ml_teams[22].bar_power` da camada de dados. Aqui
   quem está fora do formato é o **oráculo**.

## Evidência

Medido em 2026-08-22, ROM japonesa, com o
[`compara_tela.sh`](../../wte/tools/compara_tela.sh) — **duas corridas, mesmo
resultado nas duas**:

```text
compara_tela: time 85
  barras oraculo: [75, 86, 76, 75, 86]
  barras port   : [75, 86, 75, 75, 86]
  valores do jogo: ataque=6, defesa=7, equipe=?, velocidade=6, tecnica=7
  DIVERGE da camada de dados:
    equipe: dado 6 previa 75 px, oraculo 76, port 75
```

O `equipe=?` da terceira linha é o próprio medidor dizendo que não conseguiu
inverter os 76 px: não há `v` inteiro que os produza.

E o deslocamento da bandeira, alinhando o recorte de 80×48 quadro a quadro:

```text
port 0 px acima: 1500/3840 px diferentes
port 1 px acima:  796/3760
port 2 px acima:   92/3680     <- o mínimo
port 3 px acima:  714/3600
```

Antes da CORR-WTE-083 esse recorte divergia em **3.840 de 3.840** — a bandeira
era inteiramente preta. Depois dela, alinhado, divergem 92 de 3.680 (2,5%), e o
que sobra está nas bordas das faixas.

Os outros nove fecham em **0 de 3.840, tolerância zero** — inclusive o combo
**68** (`ml_teams[5]`), que é da mesma família de Master League. Não é um
problema da família: é deste time.

## Causa raiz

**Não medida.** As duas diferenças estão no mesmo time e nenhuma delas se
explica pelo que a CORR-WTE-083 consertou:

- o desenho da bandeira não tem nada por time além da forma e da paleta, e as
  duas batem — `ml_teams[22].flag_shape = 56` na camada de dados e `56` no byte
  que a tabela do Obocaman endereça, e `bandera56.bmp` tem os mesmos 20×16 dos
  outros;
- a barra sai da mesma rotina para os 95 times, e nos outros ela cai na grade.

Uma hipótese que **ainda não foi testada** é que as duas sejam a mesma coisa —
o painel deste time desenhado 1 a 2 px deslocado no oráculo —, mas nesse caso
as **cinco** barras estariam erradas, e quatro das cinco batem. Quem executar
esta correção começa por descartar ou confirmar isso.

## Correção

1. **Decidir de quem é o defeito antes de mexer em código.** A barra é o caso
   mais claro: 76 px não é uma largura que o formato produza, e o port
   concorda com a camada de dados. Se o oráculo estiver mesmo fora da grade,
   isto não é bug do port — é **divergência deliberada**, e o lugar dela é a
   [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md), não um conserto;
2. **Medir o deslocamento da bandeira** com a mesma régua: onde o `wte.exe`
   ancora o desenho, e onde a [`wte_render2d`](../../wte/src/wte_render2d.pas)
   o ancora. Dois pixels em 48 é 1/24 — pode ser origem do recorte, pode ser
   arredondamento de escala vertical (16 linhas de origem para 48 de destino);
3. **Não generalizar a partir de um time.** Nove fecham em zero. Qualquer
   mudança na âncora tem de manter os nove.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/src/wte_render2d.pas` | investigar; modificar só se o defeito for do port |
| `wte/re/render2d.md` ou o gerador dele | modificar (o que for medido) |
| `docs/tasks/35-divergencias-deliberadas.md` | modificar, se a barra for do oráculo |
| `wte/re/spec/MainForm.lista_equiposChange.md` | modificar (veredito) |

## Verificação

- [x] `compara_tela.sh 85` verde — as cinco barras em `[75, 86, 75, 75, 86]`
      nos dois lados, e bandeira + uniforme em **0 de 9.800 px, tolerância
      zero**. Não houve divergência deliberada a registrar: não havia
      divergência
- [x] os nove que já fecham continuam em **0 de 3.840** — 56, 57, 58, 59, 60,
      61, 62, 68, e os times 0 e 2. Onze times medidos numa corrida só
- [x] `make -C wte check` e `lazbuild` verdes
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-23

**Resumo do que foi feito:**

**Nenhum dos dois desvios existia. Quem estava errada era a régua.**

O passo 1 da Correção mandava decidir de quem é o defeito antes de mexer em
código, e a medição respondeu por um terceiro caminho que a correção não
previa: o defeito é do
[`compara_tela.py`](../../wte/tools/compara_tela.py).

**A barra `equipe`.** O oráculo desenha 75 px contíguos, de `x = 92` a
`x = 166` — exatamente `11 * 6 + 9`, e portanto dentro da grade. Os 76 vinham
da `bandas()`, que **somava pixels de preenchimento por linha** em vez de medir
o trecho contíguo. Para `indice > 62` o `lista_equiposChange` remaneja o
`home1` para `Left = 7, Width = 100`, e o controle passa a começar em
`x = 223` — sete pixels dentro da `FAIXA_X`, que termina em 230. No `EMILIA` a
faixa diagonal laranja da camisa toca `x = 229` nas linhas 131–133, que caem
dentro da banda da barra `equipe`; a soma dava 76. O port escapava por um pixel
de deslocamento horizontal: a mesma camisa chega só a `x = 231` do lado dele.

Medido na captura dos dois lados:

```text
oraculo  y=130  n=75  x92..166  gaps=[]
oraculo  y=131  n=76  x92..229  gaps=[(166, 229)]   <- o buraco de 63 px
port     y=131  n=75  x94..168  gaps=[]
```

A `bandas()` passou a medir o trecho contíguo mais longo por linha, pela
`corrida_mais_longa()` nova. Onde não há intruso, contar e medir dão o mesmo
número, e as outras dez telas não mudaram de valor.

**A bandeira.** Não sai deslocada: `bandera`, `home1` e `home2` do combo 85
batem em **0 de 3.840, 0 de 4.200 e 0 de 1.760 px**, com desvio máximo de canal
**0**, em duas corridas independentes do `compara_tela.sh`. A `calibra()`
devolve `(0, 0)` no oráculo e `(2, 2)` no port, e a janela dos dois sai nos
522×475 que o `.lfm` declara — sem a escala de 1,0421 que a docstring da
`calibra()` registra de uma medição antiga. Os 92/3.680 do enunciado foram
medidos à mão, alinhando recorte, e não sobrevivem à medição pela mesma
calibração que os outros dez times usam.

**Problemas encontrados:**

1. **O `compara_tela.sh` aborta na primeira falha, e por isso a bandeira nunca
   foi medida pela ferramenta.** O passo das barras reprovava e o script saía
   com 1 antes de chegar ao render — foi o que fez a medição da bandeira ser
   feita à mão, e foi a medição à mão que trouxe os 2 px. Deixado como está: a
   ordem é deliberada, e o que faltava era a barra estar certa.
2. **Nada a registrar na
   [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md).** O passo 1 previa
   que a barra pudesse ser divergência deliberada do oráculo; ela não é, e
   inventar uma linha de divergência para um desvio que não existe seria pior
   do que o defeito.
3. **`wte/re/render2d.md` não muda.** O port ancora certo; não houve medida
   nova sobre ele.

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `wte/tools/compara_tela.py` | modificado — `corrida_mais_longa()` nova, usada pela `bandas()` |
| `wte/tools/test_compara_tela.py` | modificado — caso de regressão da camisa encostando na faixa |
| `wte/re/spec/MainForm.lista_equiposChange.md` | modificado — o registro do que a medição mostrou |
