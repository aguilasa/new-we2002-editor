---
id: CORR-WTE-082
title: "Correção: a tela de tática não é enchida, e sem isso o ` Accept` do estrategia grava as coordenadas do .lfm"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-082: encher a tela de tática antes de deixar alguém gravá-la

## Problema identificado

A [CORR-WTE-081](/docs/tasks/CORR-WTE-081.md) fechou duas das três gravações
órfãs e parou na terceira, exatamente onde ela mesma previu que pararia. O
`estrategia.BitBtn3Click` — o ` Accept` da tela de tática, `0x0040a660` — **não
tem como ser implementado hoje**, e o motivo não é o handler: é que a tela de
onde ele lê nunca foi preenchida.

O bloco 3 do handler lê as posições dos componentes `bola`, `tirador` e
`simbolo` **da tela** e as converte de pixel para célula da malha
(`(Left - Left_do_campo + 2) div 8`). Num port cuja tela ninguém posicionou,
esses componentes estão onde o `.lfm` os deixou em tempo de projeto. Clicar
` Accept` gravaria as coordenadas do formulário na imagem de CD.

**Não é uma gravação que sai errada: é uma gravação que sai plausível.** Os
bytes teriam o formato certo, cairiam no offset certo, e o golden mediria a
diferença contra um oráculo que gravou a tática de verdade. O diagnóstico
apontaria para o escritor, e o defeito está no leitor que não existe.

## Evidência

A rotina que enche a tela é a `0x0040A0B4`, e ela continua sem port. Medido com
o decodificador do [`dump_auxiliares.py`](../../wte/tools/dump_auxiliares.py)
sobre o `.text`, em 2026-08-21:

```text
0x0040a0b4: 1443 bytes
0x0040a660: 1931 bytes

callers de 0x0040a0b4  ->  ['0x40a658', '0x4107a4']
    estrategia.BitBtn1Click
    MainForm.mostrar_estrategiaClick
```

Os dois chamadores estão `aberto`, e os dois pela mesma razão. O corpo do
`mostrar_estrategiaClick` no port diz isso com todas as letras:

```pascal
{ ESCOPO: navegacao, pela mesma divisao do irmao. Encher a tela de tatica
  (`0x0040a0b4`, 1.443 bytes) e da WTE-TASK-26, dona do formulario
  `estrategia`. }
```

Ele resolve o time em edição e chama `estrategia.ShowModal`. Nada mais.

**E há um segundo buraco, neste caso na spec.** A seção *Bytes tocados* do
[`estrategia.BitBtn3Click`](../../wte/re/spec/estrategia.BitBtn3Click.md) traz,
literalmente:

> Os tamanhos exatos da tática saem da segunda metade do corpo, que esta spec
> não percorreu instrução a instrução.
>
> **Evidência:** não medido

Ou seja: além de não haver o que ler na tela, não se sabe ainda **quantos
bytes** e **em que offsets** a metade de tática do handler grava. Implementar
com a spec assim seria escrever o escritor por adivinhação, que é o oposto do
que a [WTE-TASK-22](/docs/tasks/22-harness-golden.md) existe para permitir.

## Causa raiz

**Dívida herdada, e ela tem endereço.** A WTE-TASK-26 é dona do formulário
`estrategia` e fechou onze dos quinze handlers dele; a `0x0040A0B4` ficou de
fora, e a WTE-TASK-25 registrou a divisão no corpo do `mostrar_estrategiaClick`
em vez de abrir dono para ela. Ninguém errou uma medição: a rotina caiu na
fronteira entre duas tasks, que é o mesmo modo de falha que a CORR-WTE-081
descreveu para as três gravações órfãs — *"a divisão por formulário encontrando
a divisão por grupo de comportamento"*.

A diferença é o custo de deixar como está. Um `Original ` que não desfaz é uma
funcionalidade a menos; um ` Accept` que grava a tela não preenchida é uma
gravação errada na imagem do usuário.

## Correção

**Portar a `0x0040A0B4` e completar a spec do `BitBtn3Click`, nesta ordem.** A
gravação da tática continua sendo da CORR-WTE-081 e só deve ser tentada depois
das duas.

1. **Medir a segunda metade do `0x0040a660`**, instrução a instrução, e trocar
   o `**Evidência:** não medido` da seção *Bytes tocados* por offsets e
   tamanhos. Enquanto ela disser "não medido", nenhum escritor pode ser
   escrito;
2. **Portar a `0x0040A0B4`** (1.443 bytes) — encher a tela de tática a partir
   da imagem. Ela **não grava**: é a leitora, e por isso fecha sem golden de
   gravação, pela régua de leitura do
   [`GABARITO.md`](../../wte/re/spec/GABARITO.md);
3. **Trocar o veredito dos dois chamadores** que ela destrava —
   [`estrategia.BitBtn1Click`](../../wte/re/spec/estrategia.BitBtn1Click.md) e
   [`MainForm.mostrar_estrategiaClick`](../../wte/re/spec/MainForm.mostrar_estrategiaClick.md)
   — e regerar o `INDICE.md`.

**Onde a rotina mora é decisão desta correção, e o precedente é fresco.** A
`0x0040A0B4` alcança os componentes do `estrategia` e é chamada de um handler
do `MainForm`; é o mesmo formato de problema que o `PreencheFicha` tem, e que a
CORR-WTE-081 resolveu criando a [`wte_ficha`](../../wte/src/wte_ficha.pas) —
uma unidade que nenhum dos dois formulários possui, com o `ep2002_estrategia`
usado só na implementação. Reaproveitar a forma poupa a discussão; inventar
outra exige justificar por que esta não serve.

**A conferência é de tela, não de byte.** A régua natural é o
[`compara_tela.sh`](../../wte/tools/compara_tela.sh) sobre o formulário
`estrategia` — as onze posições em campo e a lista de formações, nos dois
lados, para pelo menos três times distintos. O `wte/re/malhas.tsv` e a
[`wte_zonas`](../../wte/src/wte_zonas.pas) já descrevem a malha.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/estrategia.BitBtn3Click.md` | modificar (a seção *Bytes tocados*) |
| `wte/src/wte_tatica.pas` (ou onde a rotina for morar) | criar |
| `wte/src/impl/ep2002_mainform.mostrar_estrategiaClick.inc` | modificar |
| `wte/src/impl/ep2002_estrategia.BitBtn1Click.inc` | criar |
| `wte/src/impl/*.uses` | modificar |
| `wte/re/spec/estrategia.BitBtn1Click.md` | modificar (veredito) |
| `wte/re/spec/MainForm.mostrar_estrategiaClick.md` | modificar (veredito) |
| `wte/re/spec/INDICE.md` | regenerar |
| `docs/tasks/progresso.md` | modificar |

## Verificação

- [x] a seção *Bytes tocados* do `estrategia.BitBtn3Click` sem `não medido` —
      cinco regiões, 45 bytes por time, com `OFS_FORMATIONS` e `OFS_KICKER`
      fechando as duas âncoras que têm nome
- [x] a tela de tática do port conferida contra o oráculo em **três** times
      distintos, com o `compara_tela.sh --malha`: `0`, `2` e `63`, os três
      `PASSOU`, com as quatro posições de marcador batendo com o oráculo antes
      e depois do clique
- [x] `estrategia.BitBtn1Click` e `MainForm.mostrar_estrategiaClick` com
      veredito trocado, e `spec_index.py --check` verde — 19 `aberto`
- [x] `make -C wte check` verde e `lazbuild wte/wte.lpi` sem warning novo
- [x] `golden-15-ficha` e `golden-16-cor` continuam verdes
- [x] `roms/` intocada; toda corrida sobre cópia

## Log de Execução

**CONCLUÍDA**, em duas passagens. A primeira mediu a segunda metade do
`0x0040a660`; a segunda portou a `0x0040A0B4` e fechou os dois vereditos.

**Executado em:** 2026-08-21 (primeira passagem)

**Resumo do que foi feito:**

Lida instrução a instrução a faixa `0x0040A7C0`..`0x0040ADCD` do
`estrategia.BitBtn3Click`, e a seção *Bytes tocados* da spec dele trocou o
`**Evidência:** não medido` por **cinco regiões e 45 bytes por time**:

| região | índice lógico | bytes |
|---|---:|---:|
| cor de radar 1 | `2*t + 0x3F534` | 2 |
| cor de radar 2 | `2*t + 0x3F634` | 2 |
| formação | `30*t + 2*(t div 95) + 0x40C2C` | 30 |
| cobrador | `6*t + 2*(t div 95) + 0x46228` | 6 |
| tática | `5*t + 0x408A8` | 5 |

Duas âncoras fecham contra o `we2002_core` — para o time 0 a formação dá
**2303700** (`OFS_FORMATIONS`) e o cobrador **2329056** (`OFS_KICKER`) —, e as
três constantes já estavam versionadas no `.aux.inc` do `MainForm` desde a
WTE-TASK-25, medidas por outro caminho e batendo uma a uma.

**Problemas encontrados:**

1. **O `spec_index.py` tem vocabulário fechado no campo evidência**, e ele
   recusa qualificação: `disassembly lido (0x0040A7C0..0x0040ADCD)` reprova, só
   `disassembly lido` passa. A faixa foi para a prosa acima da linha. A guarda
   está certa — evidência qualificada deixa de ser comparável entre specs.
2. **Os três últimos blocos não passam pela `0x00403400`.** Chamam `fseek` e
   `fputc` da RTL direto, um byte por vez, e resolvem a fronteira de setor no
   próprio laço: comparam o índice com `0x800` e dão `fseek(+0x130,
   SEEK_CUR)`. Procurar a escritora comum aqui não a encontraria — é a segunda
   vez que este handler mistura o caminho incremental com o fechado.
3. **Os 30 bytes da formação saem de três laços de dez, não de um de trinta**,
   e o primeiro copia a partir do índice **1** de `[0x00434224]` — o elemento
   zero fica de fora.

**O que a medição mudou no tamanho do passo 2 — e o que ela poupou:**

O passo 2 é maior do que esta correção estimou ao ser aberta, e agora se sabe
por quê. A `0x0040A0B4` **não faz I/O de imagem nenhum** — sem `0x004033BC`,
sem `0x00403388`, sem `fseek`. Ela lê de globais e posiciona componentes; quem
enche as globais é o `MainForm.mostrar_estrategiaClick` (`0x00410220`), que é
um dos chamadores da leitora comum. Portar a tela de tática é portar **os
dois**, mais as duas auxiliares que a `0x0040A0B4` chama (`0x004099BC`, 227 B, e
`0x004097D4`, 474 B) — cerca de 2.100 bytes somados, além da leitura da imagem
no handler de navegação.

E há um terceiro beneficiário já nomeado: o
[`lista_formacionesClick`](../../wte/re/spec/estrategia.lista_formacionesClick.md)
está `implementado` **com divergência nomeada** — o item `DEFAULT` não faz nada
porque o buffer vivo do time (`0x00432E88`) é justamente o que a `0x0040A0B4`
preenche. Fechar o passo 2 fecha aquela divergência também.

**Arquivos criados/modificados:**

- modificados: `wte/re/spec/estrategia.BitBtn3Click.md` (a seção *Bytes
  tocados* e a justificativa), `docs/tasks/CORR-WTE-081.md` (a linha que dizia
  que a spec ainda estava `não medido`)

---

**Executado em:** 2026-08-21 (segunda passagem — o port)

**Resumo do que foi feito:**

Portada a `0x0040A0B4` como `PreencheTelaDeTatica`, e com ela a metade de
LEITURA do `MainForm.mostrar_estrategiaClick` que ninguém tinha visto: sete
chamadas a `0x004033BC` para cinco regiões. As duas moram na
`wte/src/wte_tatica.pas`, a terceira unidade neutra deste port — o
preenchimento precisa do `ep2002_estrategia` e do `ep2002_mainform` ao mesmo
tempo, e nenhum dos dois pode usar o outro na interface.

Os vereditos do `estrategia.BitBtn1Click` (que virou uma chamada só, como no
original) e do `MainForm.mostrar_estrategiaClick` passaram a `implementado`;
o índice foi de 21 para **19** `aberto`.

**A conferência:** `compara_tela.sh --malha` nos times `0`, `2` e `63`, os três
`PASSOU`. As quatro posições de marcador batem com o oráculo **antes** do
clique, que é justamente o que o preenchimento produz — e elas diferem entre
times (316/380/460 no time 2 contra 348/316/348/396 nos outros dois), o que
mostra que o valor vem do dado e não de constante.

**Problemas encontrados:**

1. **A rotina de preenchimento escreve `Top`, não `Left`.** Na primeira
   corrida os dez marcadores foram parar amontoados no canto superior direito.
   O `MoveMarcadorDaMalha` já dizia por quê desde a WTE-TASK-29 — *"o `Left` do
   marcador não é tocado: ele já está na coluna certa desde o `.dfm`"* —, e os
   dois números da conta (passo 16, folga 3) são os mesmos `MALHA_PASSO_Y` e
   `MALHA_FOLGA` do clique, que estavam em `wte_zonas` o tempo todo.
2. **O corte do nome é 1 no port e 4 ou 5 no original**, e a diferença apareceu
   na tela: onde o oráculo mostrava `?I???` o port mostrava `?`. A lista do
   original traz um prefixo numérico antes do nome; a do port, não. Isso é uma
   inconsistência **herdada** e ela tem um segundo sintoma, fora desta
   correção: o `NomeDoItemSelecionado` do `MainForm` corta 4 ou 5 de um item
   que não tem o que cortar.
3. **As duas auxiliares pesadas já estavam portadas** — `PreparaAnimacao`
   (`0x004097D4`, 474 B) e `PintaPosicoes` (`0x004099BC`, 227 B) —, o que tirou
   701 dos ~2.100 bytes que esta correção estimava. O que elas precisavam era
   deixar de receber um ÍNDICE na tabela predefinida e passar a receber o
   REGISTRO: é o que o original sempre teve, um ponteiro em `0x00434230` que
   ora aponta para a tabela, ora para o buffer vivo.
4. **A tabela de zona é a mesma tabela de formações, deslocada de dois.** Os
   dois endereços imediatos do binário (`0x00433F2D` e `0x00433F85 + 44*n`) são
   o campo `zona` dos registros 0 e n+2 da tabela de 18 × 44 que a
   `wte_formacoes` já trazia — não havia tabela nova para extrair.
5. `docs/PLAN-WTE-LAZARUS.md` §4.4 moveu de novo: 7.546 → 8.027 à mão e 9.449 →
   9.456 geradas. O `check_fase2.py` pegou.

**O que fechou de brinde, e estava escrito como divergência:**

O item `DEFAULT` da lista de formações não fazia nada, e a tela de tática abria
com as bolas nas posições de projeto do `.lfm` e toda bola na zona 0. As duas
estavam registradas na spec do `lista_formacionesClick` como divergências com
dono nomeado — `0x0040a0b4` —, e as duas caíram junto.

**O que continua vazio na tela, e não é deste handler:** os itens dos dois
combos de cor de radar e a bandeira do canto. Os dois saem do
`estrategia.FormCreate`, que segue `aberto`.

**Arquivos criados/modificados (segunda passagem):**

- criados: `wte/src/wte_tatica.pas`,
  `wte/src/impl/ep2002_estrategia.BitBtn1Click.inc`
- modificados: `wte/src/impl/ep2002_estrategia.aux.inc` (o corte),
  `wte/src/impl/ep2002_estrategia.lista_formacionesClick.inc`,
  `wte/src/impl/ep2002_mainform.mostrar_estrategiaClick.inc`, os dois `.uses`,
  `wte/tools/dump_formacoes.py` (as oito cores de radar) e
  `wte/src/wte_formacoes.pas`, `wte/re/spec/estrategia.BitBtn1Click.md`,
  `wte/re/spec/MainForm.mostrar_estrategiaClick.md`,
  `wte/re/spec/estrategia.lista_formacionesClick.md`, `wte/re/spec/INDICE.md`,
  `docs/PLAN-WTE-LAZARUS.md` §4.4, `wte/re/fase-2.md`
- reconciliação de doc, em commit próprio: `wte/tools/dump_zonas.py` e
  `wte/re/zonas.md`, `wte/re/formacoes.md`, `docs/tasks/progresso.md`
