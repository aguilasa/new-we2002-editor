---
id: CORR-WTE-083
title: "Correção: dez times desenham bandeira preta — o ed.exe não lê a paleta deles, e o editor do Obocaman lê"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-083: dez times desenham bandeira preta

## Problema identificado

Na conferência de tela da [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md)
(2026-08-22), o time **56 — `CLASSIC ENGLAND`** apareceu com a bandeira
**inteiramente preta** no port, e com a cruz de São Jorge no oráculo. As cinco
barras batem em pixel, o uniforme bate em pixel, e a bandeira diverge em
**3.840 de 3.840 pixels**, com desvio máximo de canal 232.

Não é um time: são **dez**, em duas famílias com mecanismos diferentes.

- **`teams[56]`…`teams[63]`** — sete CLASSIC (`CLASSIC ENGLAND`,
  `CLASSIC FRANCE`, `CLASSIC NETHERLANDS`, `CLASSIC ITALY`, `CLASSIC GERMANY`,
  `CLASSIC BRAZIL`, `CLASSIC ARGENTINA`) mais o `teams[63]`, que **não é
  CLASSIC nem é alcançável**: o nome dele é vazio no dump, e o combo passa de
  `teams[62]` para `ml_teams[0]` porque `TEAMS_NATIONAL_ALLSTAR` vale 63. Esta
  linha dizia "os oito CLASSIC" até a execução medir os nomes;
- **`ml_teams[5]` (`HIGHLANDS`) e `ml_teams[22]` (`EMILIA`)** — dois clubes de
  Master League.

Os dez carregam `flag_colours` como **dezesseis zeros**, e zero na paleta é
preto. Confirmado na tela em dois deles, um de cada família: o time 56 e o
combo 68, que é o `ml_teams[5]` — o oráculo desenha a cruz amarela em azul, o
port desenha preto, 3.840 de 3.840 pixels, desvio máximo de canal 248.

O `flag_shape` deles **não** é o problema: o time 56 traz `flag_shape = 4`, e
`bandera4.bmp` existe. O que falta é a cor.

## Evidência

Dump da camada de dados sobre a ROM japonesa, pelo
[`dump_estado.pas`](../../wte/tests/dump_estado.pas) — o mesmo que o
[`compara_tela.sh`](../../wte/tools/compara_tela.sh) gera como terceira ponta da
conferência:

```text
teams[56].flag_shape = 4
teams[56].flag_colours = 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```

Contados os 64 slots de `teams[]` e os 32 de `ml_teams[]`, **dez** têm a paleta
inteiramente zerada: `teams[56..63]`, `ml_teams[5]` e `ml_teams[22]`.

E a causa está no bloco de carga, que é **transpilado do `we2002_core`** e
portanto herdado do `ed.exe`. Nas duas famílias é a mesma coisa — endereço que
ninguém lê —, com forma diferente:

```text
wte/src/we2002_database.pas   for i := 0 to 55 do   ... image_file.Read(teams[i].flag_colours,32)
src/core/Database.cpp         for(i = 0;i < 56;i ++) ... image_file.Read(&teams[i].flag_colours,32)
```

O laço nacional para em 55, e os oito CLASSIC nunca são lidos. O bloco de
Master League não é laço: é uma lista de índices espalhados, e ela cobre
`{0-4, 7-21, 24-27}` — **`5`, `6`, `22` e `23` ficam de fora**. Desses quatro,
o `6` e o `23` aparecem com cor no dump (são lidos noutro ponto do arquivo); o
`5` e o `22` ficam com o zero da inicialização.

A montagem lado a lado ficou em `work/tela/time-56-lado-a-lado.png` durante a
medição — `work/` é rascunho e não é versionada; para refazer:

```sh
bash wte/tools/compara_tela.sh 56
```

## Causa raiz

**Os dois oráculos não cobrem a mesma coisa, e o port seguiu o de formato.**

- **Oráculo B, o `we2002_core`**, é byte-idêntico ao `ed.exe` e por isso
  reproduz o alcance do `ed.exe` — que **não carrega** a paleta de bandeira
  desses dez. Para o `ed.exe` isso nunca foi defeito: ele não desenha bandeira
  nenhuma, e paleta que ele não desenha ele também não precisa gravar;
- **Oráculo A, o `wte.exe` do Obocaman**, desenha, e lê a cor de cada time pela
  tabela de offsets em `.data` que cobre os 95 slots —
  [`re/offsets.md`](../../wte/re/offsets.md), a rotina `0x004050D0`.

O port herdou a camada de dados do B e a tela do A. Onde os dois discordam de
**alcance**, a tela do port fica sem dado. É a mesma classe de achado da
[WTE-TASK-19](/docs/tasks/19-os-50-offsets-restantes.md) — *"os offsets que o
Obocaman tem e nós não"* —, e este passou por ela sem ser visto porque a
conferência de tela daquela época não olhou a bandeira desses dez.

## Correção

**O offset existe e está na tabela do `.exe`.** O trabalho é lê-lo e usá-lo,
não descobri-lo:

1. **Medir** onde a `0x004050D0` busca `flag_colours` para os dez —
   a global de offset é `[0x004331DC]`, preenchida pela varredura da tabela em
   `.data` (`0x0040CBC8`, seis colunas por linha). O
   [`dump_offsets.py`](../../wte/tools/dump_offsets.py) já lê essa tabela;
2. **Decidir onde o valor entra.** Duas rotas, e a escolha é do executor:
   - **rota A** — estender o laço do `we2002_database.pas`. Isso mexe em
     arquivo **gerado**, então a mudança entra no
     [`port_database_pas.py`](../../wte/tools/port_database_pas.py) e sai
     regerada. Mas ela faz o port divergir do `we2002_core` na carga, e o
     `compare_dumps.py` da WTE-TASK-20 reprova por construção: os dumps Pascal
     e C++ deixariam de ser idênticos;
   - **rota B** — carregar os dez à parte, fora da camada transpilada, como a
     [`wte_cor`](../../wte/src/wte_cor.pas) já faz com o que é do editor e não
     do formato. O dump continua idêntico e a tela ganha a cor.

   **A rota B é a recomendada**, e a razão é a regra da §4.5 do plano: a camada
   de dados é do `we2002_core`, e o que o Obocaman lê a mais é do Obocaman;
3. **Conferir com o `compara_tela.sh`** nos dez, não em dois. Dois é amostra;
   dez são as duas famílias inteiras — e são famílias diferentes, então passar
   numa não diz nada sobre a outra;
4. **Reler o veredito do `lista_equiposChange`** — este achado é hoje uma das
   razões de ele continuar `aberto`.

**Não mexer no `src/core/`.** O `newWe2002` está com escopo fechado e
verificado, e o `ed.exe` não desenha bandeira: estender o laço lá seria
divergir do oráculo que ele existe para reproduzir.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_offsets.py` ou gerador novo | consultar/estender |
| `wte/src/wte_cor.pas` (rota B) | modificar |
| `wte/tools/port_database_pas.py` (rota A, se escolhida) | modificar |
| `wte/re/spec/MainForm.lista_equiposChange.md` | modificar (veredito) |
| `wte/re/offsets-novos.md` | modificar |
| `docs/tasks/progresso.md` | modificar |

## Verificação

- [x] `compara_tela.sh` verde nos **nove alcançáveis** — os sete CLASSIC
      (combo 56–62) e os dois de Master League (combo 68 e 85), com a bandeira
      batendo em pixel e tolerância zero. **Os nove fecharam**: o combo 85
      fechou em 2026-08-23, quando a
      [CORR-WTE-084](/docs/tasks/CORR-WTE-084.md) mostrou que o desvio dele era
      da régua e não da tela. O décimo slot zerado, `teams[63]`, não tem item de
      combo e não há tela para conferir
- [x] `compara_tela.sh` continua verde nos times já conferidos (0, 2)
- [x] `compare_dumps.py` continua idêntico entre Pascal e C++ nas **duas** ROMs
      — 66.498 linhas, 0 divergência, round-trip 0 byte nas duas. A rota
      escolhida foi a **B**, e é por isso que este critério continua de pé
- [x] `make -C wte check` e `lazbuild` verdes
- [x] nenhum roteiro golden muda de veredito — o `golden-16-cor`, que é o que
      grava bloco de cor, continua byte-idêntico
- [x] `roms/` intocada

## Log de Execução

**CONCLUÍDA.** A carga está implementada e conferida, e os **nove
alcançáveis** fecham em pixel com tolerância zero.

O nono (combo 85) ficou pendente por um dia. A paleta dele foi corrigida junto
com as outras — as cores e o estêncil batiam desde 2026-08-22 —, mas sobrou o
que na época se leu como diferença de POSIÇÃO, e virou a
[CORR-WTE-084](/docs/tasks/CORR-WTE-084.md). Em **2026-08-23** aquela correção
mediu os dois desvios e nenhum era da tela: a bandeira do 85 bate em 0 de
3.840 px com a mesma calibração dos outros dez times, e os 76 px da barra
`equipe` eram a camisa remanejada entrando na faixa de medição do
`compara_tela.py`. Com a régua consertada, esta correção fecha sem código novo.

**Executado em:** 2026-08-22 (a carga) e 2026-08-23 (o fechamento)

**Resumo do que foi feito:**

Escolhida a **rota B**, como a própria correção recomendava. A
`CarregaBandeirasQueOCoreNaoLe`, na [`wte_cor`](../../wte/src/wte_cor.pas),
percorre os 95 slots e, para cada um cuja paleta o `Database.Load` deixou
inteiramente zerada, lê os 32 bytes da imagem pelo offset da tabela do Obocaman
e os põe no `Jogo`. Ela é chamada pelos **dois** caminhos que abrem imagem —
`MainForm.FormShow` e `boton_dialogo_weClick` —, depois do `AbreImagem` e fora
dele: o `dump_estado.pas` chama o `Load` direto e não passa por aqui, e é por
isso que o `compare_dumps.py` continua comparando duas cargas idênticas.

**O offset não precisou ser medido: já estava extraído.** A
[`dump_blococor.py`](../../wte/tools/dump_blococor.py), da
[CORR-WTE-081](/docs/tasks/CORR-WTE-081.md), lê do `.exe` a tabela de 95 bytes
de `0x00423247` e a converte com a mesma aritmética do `0x00404E70`, com oito
âncoras conferidas contra `OFS_*` do `we2002_core`.

**Problemas encontrados:**

1. **O critério "o core deixou zerado" foi medido antes de virar código, e a
   medição mudou o desenho.** Comparando os 95 slots entre a carga do core e a
   tabela do Obocaman na ROM japonesa: **85 batem exatamente**, 10 estão
   zerados, e **um diverge de propósito** — o `teams[39]`, que o core lê de
   outro ponto do arquivo (o caso `36, 39, 47` do laço). Ler os 95 pela tabela
   do Obocaman, que era a rota mais simples, teria passado por cima do 39.
   Preencher só o que está zerado nunca sobrescreve o que o core leu.
2. **São sete CLASSIC, não oito, e nove alcançáveis, não dez.** O `teams[63]`
   tem nome vazio no dump e nenhum item do combo o alcança: com
   `TEAMS_NATIONAL_ALLSTAR = 63`, o combo salta de `teams[62]` para
   `ml_teams[0]`. O texto desta correção e o critério de verificação foram
   corrigidos.
3. **O combo 85 não fechou no dia, e o que sobrou não era cor.** A bandeira
   dele ficou com as cores e as faixas certas, e o que sobrou foi lido como
   deslocamento de 2 px mais uma barra de 76 px fora da grade. Virou a
   CORR-WTE-084, e ela mediu no dia seguinte que **nenhum dos dois existia**:
   os 2 px vinham de um recorte alinhado à mão, e os 76 px de a `bandas()` do
   `compara_tela.py` somar pixel por linha em vez de medir trecho contíguo,
   contando a camisa que o `lista_equiposChange` remaneja para dentro da faixa
   quando `indice > 62`. A régua foi consertada lá; aqui nada mudou.

**Arquivos criados/modificados:**

- criados: `docs/tasks/CORR-WTE-084.md`
- modificados: `wte/src/wte_cor.pas` (a `CarregaBandeirasQueOCoreNaoLe`),
  `wte/src/impl/ep2002_mainform.FormShow.inc`,
  `wte/src/impl/ep2002_mainform.boton_dialogo_weClick.inc`,
  `docs/PLAN-WTE-LAZARUS.md` §4.4, `wte/re/fase-2.md`
