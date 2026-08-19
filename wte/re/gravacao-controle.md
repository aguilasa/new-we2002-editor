# Diff de controle da gravação — gravar sem editar nada

**Arquivo gerado.** Não edite à mão: mexa em
[`../tools/gravacao_controle.py`](../tools/gravacao_controle.py) e
reexecute. `make -C wte check` roda o `--check`.

Produto da [WTE-TASK-27](../../docs/tasks/27-handlers-de-gravacao.md).
A medição é a sessão `27-gravacao-controle` de
[`../tools/diff_dirigido.sh`](../tools/diff_dirigido.sh) sobre
`roms/japanese-shift-jis.bin`, com o roteiro
[`../tests/roteiros/golden-02-gravacao.txt`](../tests/roteiros/golden-02-gravacao.txt).

## Por que ele vem antes de implementar qualquer coisa

Carregar um time e mandar gravar **sem tocar em campo nenhum** já muda
bytes. Sem essa linha de base, toda divergência medida depois vem
contaminada — e as duas armadilhas conhecidas são de naturezas
diferentes: o `Save` do formato reconstrói dado a partir de link, e o
`Load`+`Save` do editor original não é idempotente.

## O que cada ação endereçou, e o que de fato mudou

As duas colunas de contagem não medem a mesma coisa. `escreveu` é
syscall — o que o app mandou para o arquivo. `mudou` é `cmp` — o que
ficou diferente do que já estava lá. A diferença entre elas é gravação
de valor igual, que nenhum `cmp` enxerga.

| ação | faixas de escrita | bytes escritos | bytes que mudaram |
| --- | ---: | ---: | ---: |
| `ARRANQUE` | 9 | 14339 | 12911 |
| `SELECIONA_TIME` | 0 | 0 | 0 |
| `GRAVA_BARRAS` | 1 | 5 | 0 |
| `GRAVA_NOMES` | 8 | 64 | 22 |
| `FIM` | 0 | 0 | 0 |

### `GRAVA_BARRAS`

| offset | tamanho | setor | região | mudou |
| ---: | ---: | ---: | --- | ---: |
| 2328184 | 5 | 989 | `OFS_TEAM_BARS` | 0 |

### `GRAVA_NOMES`

| offset | tamanho | setor | região | mudou |
| ---: | ---: | ---: | --- | ---: |
| 1013924 | 12 | 431 | `OFS_TEAM_NAME_1_A+188` | 0 |
| 1882884 | 12 | 800 | `OFS_TEAM_NAME_2+916` | 8 |
| 2004976 | 12 | 852 | `OFS_TEAM_NAME_3+980` | 0 |
| 2005368 | 4 | 852 | `OFS_TEAM_ABBREV_1+372` | 0 |
| 2830932 | 8 | 1203 | `OFS_TEAM_NAME_4+772` | 7 |
| 4234856 | 4 | 1800 | `OFS_TEAM_ABBREV_3+372` | 0 |
| 5651440 | 4 | 2402 | `OFS_TEAM_ABBREV_2+372` | 0 |
| 5652636 | 8 | 2403 | `OFS_TEAM_NAME_6_B+272` | 7 |

## O clique não grava: quem grava é o `fseek` seguinte

O `wte.exe` escreve pela saída **bufferizada** do runtime C. Clicar o
botão não produz syscall nenhuma: os bytes ficam no buffer, e só vão ao
arquivo quando algo depois procura noutro ponto do mesmo arquivo —
`fseek` esvazia a saída pendente antes de mover.

O par de sondas abaixo mede isso com **uma** variável de diferença. Os
dois roteiros são iguais linha a linha; o `-com` tem quatro linhas a
mais, que trocam de time depois do clique.

| sonda | roteiro | escritas na imagem |
| --- | --- | ---: |
| `27-descarga-sem` | [`../tests/roteiros/27-descarga-sem.txt`](../tests/roteiros/27-descarga-sem.txt) | 0 |
| `27-descarga-com` | [`../tests/roteiros/27-descarga-com.txt`](../tests/roteiros/27-descarga-com.txt) | 1 |

Duas consequências, e as duas doem:

- **roteiro que termina numa gravação mede um oráculo truncado.** O
  harness encerra com `wineserver -k`, e o que estiver no buffer se
  perde. Se o port gravar direto, o gate acusaria o *port* por bytes
  que o oráculo nunca chegou a escrever;
- **a marca de corte tem de vir depois da descarga.** Na primeira
  medição desta passagem ela não vinha, e os 5 bytes das barras
  apareceram creditados à ação seguinte, a dos nomes — atribuição
  errada, em silêncio, num TSV que parecia medido.

Por isso cada bloco do roteiro termina com uma troca de time, e só
então a marca.

## A gravação sem edição **não** é neutra

Ela é destrutiva nesta imagem, e o motivo é o alfabeto. A ROM japonesa
guarda o nome do time em duas escritas: latina no primeiro bloco e
katakana de meia largura nos demais. O editor lê o campo da tela — que
veio do bloco latino — e o grava em **todos** os blocos. Os três
trechos que mudam de graça são katakana sendo substituído por ASCII.

Consequência para o port: reproduzir isso é obrigação, não escolha. Um
port que "preservasse" o katakana passaria a divergir do oráculo em
toda gravação de nomes, e o golden acusaria a gravação por um defeito
que seria de fidelidade.

## O mesmo ordinal em blocos de ordenação diferente

Os blocos de nome não estão todos na mesma ordem, e o editor escreve o
time selecionado no **mesmo ordinal** de todos. Medido nesta corrida,
com dois ordinais consecutivos:

| bloco | ordinal *k* | ordinal *k*+1 |
| --- | --- | --- |
| `OFS_TEAM_NAME_1_A` (12 B) | `SCOTLAND` | `IRELAND` |
| `OFS_TEAM_NAME_6_B` (8 B) | `ｶﾒﾙｰﾝ` | `ﾆｲｼﾞｪﾘｱ` |

Gravar "Scotland" substituiu, no último bloco, o registro que
guardava "Camarões". Isso é o comportamento do original e o port o
reproduz — o que **não** se pode é descobrir isso depois, olhando um
diff, e chamar de bug do port.

## A ROM europeia não hospeda este controle

Rodado nesta mesma passagem, o roteiro acima sobre
`roms/golden-european-deluxe.bin` morre na troca de time: a caixa de
confirmação da gravação nunca aparece, e o log do Wine traz **49.749**
violações de acesso — o mesmo número que a
[CORR-WTE-044](../../docs/tasks/CORR-WTE-044.md) já tinha medido, e
reproduzido aqui com
`grep -cE 'code=c0000005' <log>`. O `golden_run_wte.sh` reprova com
código 4 exatamente por isso: oráculo que morreu no meio grava menos,
e o diff sairia menor.

O critério "nas duas ROMs" da task herda esse limite. Ele não é
omissão desta passagem — é a mesma restrição que já vale para o gate
desde a WTE-TASK-22.

## EDC/ECC preservado, e a conta que prova isso

Setor MODE2/2352 são 24 bytes de cabeçalho, 2048 de dados e 280 de
EDC/ECC. O editor original **não recalcula** EDC/ECC, então preservar
é o comportamento correto — e preservar sai de graça enquanto toda
escrita cair dentro dos 2048. O que transforma isso de presumido em
medido não é corrida nova: é uma conta sobre as faixas que as corridas
já versionaram.

Conferidas **114** faixas do `cmp`, em 8 sessões desta
task:

- `27-barras-editada` — 10 faixa(s)
- `27-descarga-com` — 9 faixa(s)
- `27-descarga-sem` — 9 faixa(s)
- `27-dorsal-editado` — 10 faixa(s)
- `27-gravacao-controle` — 12 faixa(s)
- `27-mcr` — 9 faixa(s)
- `27-nomes-editados` — 19 faixa(s)
- `27-textura` — 36 faixa(s)

**Nenhuma toca byte de EDC/ECC nem de cabeçalho.** Cada extremo cai
entre 24 e 2071 do próprio setor, que é a
região de dados de usuário. Os 280 bytes de correção saem intactos
das quatro gravações desta task.

A conta enumera as sessões pelo prefixo `27-` em vez de listá-las: sonda
nova entra sozinha, e listar à mão seria a forma conhecida de o número
envelhecer calado.

**O que ela não alcança:** gravação que escreva **setor inteiro**. Não
existe nenhuma nesta task — a única do projeto é o `boton_mcr2isoClick`,
da [WTE-TASK-28](../../docs/tasks/28-import-de-mcr.md), e é lá que
preservar EDC/ECC deixa de ser consequência e vira decisão.
