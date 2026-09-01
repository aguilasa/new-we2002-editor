# `re/fase-1.md` — fechamento da fase 1

Produto da [WTE-TASK-09](../../docs/tasks/concluidos/09-fechamento-fase-1.md).
Gerado por [`../tools/check_fase1.py`](../tools/check_fase1.py).
**Não editar à mão** — correção entra no script e o arquivo é regerado:

```sh
python3 wte/tools/check_fase1.py
python3 wte/tools/check_fase1.py --check   # o que `make -C wte check` roda
```

Esta página **não mede o binário de novo**. Ela mede a coerência entre
os produtos que as WTE-TASK-03 a 08 deixaram versionados, e confronta os
sete números que a §1 do plano afirma contra o que essas ferramentas
dizem hoje. A exceção é a recontagem de componentes, que remede de
propósito — é a conferência que pegaria o [`censo.md`](dfm/censo.md)
errando, e o script aborta se os dois números discordarem.

## 1. DFM × handlers

A pergunta tem dois sentidos, e eles não valem a mesma coisa: `OnClick`
citado no DFM sem entrada no TSV significaria varredura de VMT
incompleta; entrada no TSV sem citação no DFM é normal — o método é
publicado e ligado em tempo de execução, ou simplesmente não é usado.

| Medida | Valor |
|---|---:|
| formulários em [`dfm/`](dfm/) | 18 |
| entradas em [`published_methods.tsv`](published_methods.tsv) | 96 |
| atribuições `OnX = handler` nos DFM | 219 |
| atribuições que o TSV registra | 219 |
| triplas `(formulário, handler, evento)` distintas no DFM | 95 |
| **no DFM e fora do TSV** | **0** |
| **no TSV e sem citação em DFM** | **1** |

**Zero no sentido que importaria.** Todo `OnX = handler` dos 18
formulários tem entrada no TSV, e as contagens de atribuição batem
nos dois lados (219). A varredura de VMT da WTE-TASK-04
não perdeu nenhum handler que o streaming de DFM precise resolver.

No outro sentido, o TSV tem entrada que nenhum DFM cita:

| Endereço | Handler | Formulário | Nota |
|---|---|---|---|
| `0x0040c9c4` | `Button2Click` | `MainForm` | sem referencia em DFM |

Isso **não** é defeito da extração: um método publicado sem
componente ligado é o que sobra quando o autor apaga o botão e
esquece o handler, ou quando a ligação é feita em código. A fase 4
decide o veredito de cada um; a fase 1 só registra que ele existe.

## 2. Strings × handlers

A pergunta da tarefa é se sobrou string demais sem dono — sinal de que
a heurística de referência estaria perdendo caso.

| População | Quantas |
|---|---:|
| strings em [`strings.tsv`](strings.tsv) | 765 |
| referenciadas por ponteiro de `.text` | 438 |
| referenciadas **de dentro** de um dos 96 | 122 |
| referenciadas, mas de código fora dos 96 | 316 |
| não referenciadas por ponteiro nenhum | 327 |

**Não é a heurística que está perdendo.** Os 96 corpos medidos cobrem
26.8% da `.text` ([`strings.md`](strings.md)), e a fração de string
com dono — 122 de 438 referenciadas,
27% — é da mesma ordem.
String referenciada de fora dos 96 vem de método não publicado, de
inicialização de unidade e da RTL estática, que são justamente os
73.2% restantes.

A consequência para a fase 4 é uma: **a mensagem que um handler exibe
nem sempre está no corpo dele.** O handler chama um auxiliar não
publicado, e a string mora lá. Procurar texto só dentro do corpo medido
acharia menos do que existe.

## 3. Offsets × `Offsets.hpp`

| Medida | Valor |
|---|---:|
| offsets em [`Offsets.hpp`](../../src/core/include/we2002/Offsets.hpp) | 69 |
| **confirmados no `.exe`** | **19** |
| ausentes do `.exe` | 50 |
| slots das duas tabelas de `.data` | 23 |
| slots preenchidos | 16 |
| cópias inteiras das tabelas em `.data` | 6 |
| candidatos ainda sem nome | 90 |

Os 19 continuam batendo depois de a tabela ter
limite medido, e **nenhum caiu fora do limite** — o que a pergunta da
tarefa queria saber. A distribuição explica por quê:

| Onde o valor aparece | Quantos |
|---|---:|
| dentro de uma das duas tabelas de `.data` | 16 |
| só como imediato de instrução, em `.text` | 3 |

- `OFS_COST_NATIONAL` — `0x0040448c|0x00404628`
- `OFS_COST_NC` — `0x004046b9|0x00404b66`
- `OFS_LINK_ML` — `0x004042fd`

Imediato de instrução nunca esteve sujeito ao limite da tabela: ele não
mora nela. Os outros são exatamente os slots preenchidos, e o critério
de limite do [`dump_offsets.py`](../tools/dump_offsets.py) já os contém
pelos dois testes independentes que ele confronta.

**Essa igualdade é asserção, não prosa.** O script aborta se
`19 − 3` deixar de dar `16`. O corte entre os dois grupos é por
**faixa de endereço** — `>= 0x00423000`, o início de `.data` —, e o
resultado é confrontado a cada rodada com a coluna `nota` do
[`offsets.tsv`](offsets.tsv), que o `dump_offsets.py` preenche lendo a
seção de cada ocorrência no PE. Até a
[CORR-WTE-017](../../docs/tasks/concluidos/CORR-WTE-017.md) o corte era
`"0x0042" not in va`, teste de faixa escrito como teste de substring:
os últimos 4 KiB de `.text` casam o prefixo e `.data` passa de
`0x0042ffff`, então ele errava nos dois sentidos — em silêncio.

As 6 cópias são as duas tabelas repetidas três vezes
cada em `.data` — o mesmo fenômeno do bloco de literais que o
[`strings.md`](strings.md) mediu, e não offsets novos.

## 4. Assets × formulários

A pergunta da tarefa era se parte dos bitmaps externos pode ser
irrelevante, caso os `TImage` já tragam a arte embutida.

| Medida | Valor |
|---|---:|
| `TImage` nos 18 formulários | 45 |
| com `Picture.Data` embutido | 41 |
| sem blob nenhum | 4 |
| `.bmp` em `we-team-editor/image/` | 198 |
| `data/dat.bin` | 145408 bytes |

| Pasta | `.bmp` |
|---|---:|
| `banderas` | 53 |
| `barba` | 7 |
| `pelo` | 32 |
| `uniformes2d` | 105 |
| `(raiz de image/)` | 1 |

**A resposta é não, e o motivo está medido na §7 do**
[`assets.md`](assets.md): embutido não quer dizer que o arquivo não é
lido. Cinco dos sete `TImage` que recebem `LoadFromFile` **têm** blob e
são sobrescritos na carga — o blob é *placeholder* de IDE. Nenhum dos
198 bitmaps é dispensável — cada um é alcançável por uma das
três tabelas de nome que a WTE-TASK-08 reconstruiu.

## 5. Recontagem dos sete números da §1 do plano

Divergência se resolve **a favor da medição**, e o plano é corrigido.

| Afirmação da §1 | Remedido | Valor | Veredito |
|---|---|---:|---|
| 18 formulários | recontagem dos `.dfm` | 18 | **bate** |
| ~430 componentes | recontagem dos `.dfm`, conferida com `censo.md` | 441 | **corrigido** |
| 20 classes distintas | idem | 20 | **bate** |
| 96 handlers | `published_methods.tsv` | 96 | **bate** |
| 19 de 69 offsets | `offsets.tsv` + `Offsets.hpp` | 19 de 69 | **bate** |
| 70 strings com padding | `strings.tsv` | 13 | **corrigido** |
| 13 unidades `Tep2002_*` | varredura do `.exe` | 13 | **bate** |
| 322 imports | `unidades-vcl.md` | 322 | **bate** |
| …sendo 300 de `rtl60`/`vcl60` | idem | 267 | **corrigido** |
| 197 bitmaps | `we-team-editor/image/` | 198 | **corrigido** |
| `dat.bin` de 145.408 B | `we-team-editor/data/` | 145408 | **bate** |

Quatro correções, e as quatro têm causa diferente — vale registrar,
porque só uma delas é erro de medição:

- **componentes: ~430 → 441.** O `~` do plano era estimativa
  declarada. O valor exato inclui um componente **sem nome** — um
  `TStaticText` de 4×4 px no `MainForm` —, que é justamente o tipo de
  objeto que uma contagem apressada perde: o DFM escreve `object
  TStaticText`, sem identificador, e um regex que exija `nome: Classe`
  devolve 440. O [`dfm2lfm.py`](../tools/dfm2lfm.py) já o trata
  — não vira campo da classe, porque inventar identificador que o
  original não tem seria inventar;
- **strings com enchimento: 70 → 13.** Não é erro de
  ninguém: são populações diferentes. Os 13 são de `.data`; o número da
  §1.5 sai de contar o binário inteiro, e o que aparece a mais é `.rsrc`,
  isto é, *caption* de formulário. Pelo mesmo critério os 18 DFM trazem
  80 literais com enchimento. A conclusão da §1.5 continua de
  pé; o que muda é **onde procurar as outras** — nos `.dfm`, não aqui;
- **imports de `rtl60`/`vcl60`: 300 → 267.** Erro de medição
  do script descartável de 2026-08-05, corrigido pela
  [CORR-WTE-012](../../docs/tasks/concluidos/CORR-WTE-012.md). O total de
  322 imports sempre esteve certo;
- **bitmaps: 197 → 198.** Erro de **soma na prosa**: a §1.8 do
  plano lista as cinco pastas com os números certos e soma errado.

## 6. A varredura dos sítios

Corrigir a §1 não fecha um número errado — ele se espalha. Cada número
reconciliado foi varrido nos markdowns de `docs/` e de `wte/`, e o
script **aborta** se sobrar afirmação viva. Não há tabela de resíduo
aqui porque resíduo é falha, como o `FORBIDDEN` do `port_database.py`.

| Número velho | Sítios antes | Sítios agora |
|---|---:|---:|
| 197 bitmaps | 10 | 0 |
| ~430 componentes | 5 | 0 |
| 300 imports de rtl60/vcl60 | 2 | 0 |
| 70 strings com enchimento | 5 | 0 |

**22 → 0.** Os 22 de antes foram medidos com o
perímetro corrente, sobre a árvore anterior à correção
(`git archive 65cc4be docs wte`); estão fixos na tabela `SITIOS` do
script, porque não há como remedi-los sobre a árvore de hoje. Cada vez
que o perímetro cresce eles são **remedidos**, não ajustados: a
[CORR-WTE-016](../../docs/tasks/concluidos/CORR-WTE-016.md) levou bitmaps de 8 para
9 ao trazer `wte/README.md` para dentro, e a
[CORR-WTE-018](../../docs/tasks/concluidos/CORR-WTE-018.md) somou os três sítios de
`docs/prompts/`. Os sítios
corrigidos foram a §1.2, a §1.5, a §1.6, a §1.8, a §5 e a §8.8 do plano,
a tabela de estado e três seções do `progresso.md`, os enunciados ainda
**pendentes** da WTE-TASK-38 e da WTE-TASK-39 — que iriam pedir mensagem
de erro e regra de empacotamento sobre uma contagem inexistente — e o
[`README.md`](../README.md) do `wte/`.

**O perímetro nasceu menor.** Ele parava em `docs/` e `wte/re/`, que foi
o que o enunciado da WTE-TASK-09 pediu, e ali fechou em zero — mas o
`wte/README.md` continuava afirmando 197 fora do alcance da guarda, que
é exatamente o espalhamento que esta seção diz combater. A
[CORR-WTE-016](../../docs/tasks/concluidos/CORR-WTE-016.md) trocou as duas bases
por `docs/` e `wte/`; o `rglob` sobre `wte` já cobre `wte/re/`.

Fica fora do perímetro o documento que **narra** a correção: os
`CORR-WTE-*.md` e o `correcoes-progresso.md`, o [`assets.md`](assets.md)
e o [`strings.md`](strings.md) — que registram, cada um, a divergência
que mediram —, o [`README.md`](../tools/README.md) de `wte/tools/`, que
narra esta guarda e cita `430` para explicar o corte por contexto, o
enunciado da própria WTE-TASK-09 e o Log de Execução de qualquer
tarefa. Fica fora também o **enunciado de tarefa já
concluída**: é história, não instrução. Tarefa pendente continua dentro,
e é o que fez a 38 e a 39 entrarem.

**`docs/prompts/` esteve fora e voltou.** A exclusão valia para o
*destino de link* — `/docs/tasks/CORR-WTE-XXX.md` e afins são
placeholder e não dá para conferir —, mas destino de link não é o que
esta guarda mede, e número de referência afirmado em prosa entrou de
carona. O `02-revisar.md` citava três números aposentados como “o que já
está no plano”, e quem revisasse leria o valor velho como gabarito. A
[CORR-WTE-018](../../docs/tasks/concluidos/CORR-WTE-018.md) trouxe a pasta para
dentro.

O corte exige o número **e** uma palavra de contexto na mesma linha.
Sem isso, `430` casaria o setor 430 do `PLAN-LINUX.md` e `300` casaria
os 300 setores de ECC amostrados — outro projeto, outro assunto, mesmo
dígito.

**Número velho em forma de história não conta**, e isso é regra: uma
linha que escreve `197 → 198` diz o que mudou, não afirma o valor. Antes
da CORR-WTE-018 essa forma passava por acidente de quebra de linha — o
bloco que a CORR-WTE-016 escreveu no `wte/README.md` tem o número numa
linha e a palavra de contexto noutra, e reflowar o parágrafo deixaria o
`--check` vermelho sem nada ter piorado.

## 7. O que fica em aberto ao sair da fase 1

| Item | Situação |
|---|---|
| binário original em espanhol | **desejável, não bloqueante** — as três mensagens em que importa têm cópia legível dentro do próprio `.exe` ([`strings.md`](strings.md)) |
| 90 candidatos a offset sem nome | **WTE-TASK-19** — são os offsets que o Obocaman tem e o `newWe2002` não |
| 1 handler sem componente ligado | **fase 4** — `published_methods.tsv` o registra com a nota; o veredito é da 25-28 |
| a arte do original | **não versionada, por decisão** — os 198 `.bmp`, o `dat.bin` e os 118 blobs dos DFM ficam com o usuário, como `roms/` |

Nenhum desses é resultado negativo por falta de medição. Os quatro são
decisão registrada ou trabalho de fase seguinte.

## Ressalvas

- **Esta página consome produto, não binário.** Se um dos geradores da
  fase 1 estiver errado, ela repete o erro com ar de conferência. O que
  a protege é o `--check` de cada um, que roda antes dela em
  `make -C wte check`, e a recontagem de componentes, que é a única
  medida independente aqui — e é a que aborta se discordar do censo;
- **os dois números de import vêm de uma frase.** O
  [`unidades-vcl.md`](unidades-vcl.md) é gerado, mas o que se lê dele
  aqui é texto corrido casado por regex. Se a frase mudar de forma, o
  script aborta em vez de emitir número inventado — é o desfecho certo,
  e ainda assim é acoplamento a registrar;
- **a coluna “sítios antes” não é remedível.** Ela é constante no
  script, com a data e o perímetro escritos. Quem duvidar dela tem de
  voltar no `git log`, e é por isso que o commit desta tarefa cita os
  arquivos que tocou.
