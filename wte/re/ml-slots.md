# Os blocos livres de Master League
**GERADO** por [`conta_ml.py`](../tools/conta_ml.py) a partir de
`we-team-editor/we-team-editor.exe` e de [`src/core/Tables.cpp`](../../src/core/Tables.cpp).
Nao edite a mao.
```sh
python3 wte/tools/conta_ml.py --check
```
## O que e um bloco livre
O original responde sozinho. O `Hint` do controle que mostra o numero
diz **`Free blocks for new Master League players`**
([`dfm/MainForm.dfm`](dfm/MainForm.dfm), `casilla_xmlibres`), e o
`we2002_core` nomeia o pool: `PLAYERS_NC = 462`, os jogadores
*non-contract* que ocupam `players[0..461]` antes dos 1449 de selecao.
> **Bloco livre e um indice de NC que nenhum par de vinculo de Master
> League reivindica.**
Nao e byte zero nem nome em branco: e ausencia de referencia. Um bloco
com nome preenchido mas sem vinculo apontando para ele conta como
livre, e e assim que o original o oferece para jogador novo.
## A rotina, e os dois lugares que a chamam
| endereco | papel |
|---|---|
| `0x004042d4` | conta os blocos livres e deixa o numero em `0x004335c0` |
| `0x0040423c` | `prefixo[time] + slot - 23` -- o indice linear do bloco |
| `0x0040427c` | o inverso: do indice linear de volta ao par `(time, slot)` |
As duas chamadas a `0x004042d4` sao `MainForm.FormShow` (em
`0x004116df`) e `MainForm.boton_dialogo_weClick` (em `0x0040c241`), e
as duas seguem com
`casilla_xmlibres.Caption := IntToStr(WORD[0x004335c0])` -- o campo
`+0x434` do `MainForm`, pelo [`campos.tsv`](campos.tsv).
```text
memset(0x00433224, 0, 462)
WORD[0x004335c0] = 462
fseek(arquivo, 2012680, SEEK_SET)          # OFS_LINK_ML
para par = 0 ate 759:
    salta_fronteira_de_setor()
    b0 = fgetc(); b1 = fgetc()
    se par = 23: segue
    se b1 < 23: segue
    i = prefixo[b0] + b1 - 23
    se WORD[0x00433224 + 2*i] = 0: WORD[0x004335c0] -= 1
    WORD[0x00433224 + 2*i] += 1
```
### Os 760 pares, e por que 760
A regiao de vinculo e um vetor unico para quem le pelo fluxo: 23 pares
do `ml_default`, **um par de enchimento**, e 32 clubes de 23. Sao
23 + 1 + 736 = 760. O enchimento aparece no `we2002_core` como a
distancia entre `OFS_LINK_ML` (2012680) e `OFS_LINK_ML1` (2012728):
48 bytes para 46 de conteudo. O `wte.exe` nao tem os dois offsets --
tem o `je` de `0x0040432f`, que pula o par 23.
A fronteira de setor cai **entre** pares, e nao dentro de um: de
`OFS_LINK_ML` ate o fim do payload do setor 855 vao 352 bytes, 176
pares exatos. Importa porque a rotina salta uma vez por iteracao e le
os dois bytes seguidos -- um par impar-alinhado leria EDC/ECC no
segundo byte.
## A tabela de `0x00423424`, e o mesmo dado no outro oraculo
120 DWORDs, um por time: quantos jogadores NC ele tem. **A soma dos
120 da 462**, que fecha com o `PLAYERS_NC` do
`we2002_core`. 50 times tem algum; o resto tem zero.
O `ed.exe` guarda a mesma tabela ja somada, no `START_LINK[]` do
[`src/core/Tables.cpp`](../../src/core/Tables.cpp), e o `ResolveMlLink` dele calcula
`slot + START_LINK[team] - 23` -- letra por letra a `0x0040423c`.
**Os dois concordam em todos os times que tem NC.** O gerador recusa se
isso deixar de valer.
Divergem em 70 times, todos com zero NC: o `START_LINK`
escreve `0` (e `-1` nos 32 clubes de ML) onde a tabela nao esta
definida, enquanto o `wte.exe` soma o prefixo de verdade. Vinculo
valido nao endereca time sem NC -- ver a secao seguinte, que e o caso
em que endereca.
A tabela inteira esta em [`ml-slots.tsv`](ml-slots.tsv).
## O que isso quebra: o `memset` limpa metade
A tabela de ocupacao vai de `0x00433224` a
`0x004335bf` -- 462 palavras, 924 bytes --
e o contador mora em `0x004335c0`, que e **o indice 462**.
O `memset` de `0x004042dd` limpa 462 **bytes**: as 231
primeiras palavras, metade da tabela.
Na primeira chamada isso nao aparece -- a regiao esta alem do fim dos
dados brutos da secao `.data`, entao o carregador a entrega zerada. Na
**segunda** (abrir outra imagem, ou o `FormShow` seguido do botao) a
metade de cima guarda a contagem da imagem anterior, o `dec` nao
dispara para aqueles blocos, e o contador sai **alto demais**.
Nada disso e teoria: e a mesma classe de erro que o `newWe2002`
documenta no `ed.exe` (o slot 64 de um vetor de 63), e a que a
WTE-TASK-33 mandou medir em vez de estimar.
## Escrita fora do vetor, e a causa do travamento da ROM europeia
Quando `prefixo[b0] + b1 - 23` passa de 461, o `inc` escreve depois do
fim da tabela, em dados vivos. **A tabela abaixo e MEDIDA**, uma linha
por indice que as imagens de fato alcancam -- sai de
[`ml-slots-fora.tsv`](ml-slots-fora.tsv), que o `--medir` escreve junto
com a contagem.
| indice | endereco | par (time, slot) | imagem | o que mora la |
|---:|---|---|---|---|
| 480 | `0x004335e4` | 20, 189 | `ml-eu.bin` | o ponteiro de time da rotina de realce |
| 481 | `0x004335e6` | 21, 190 | `ml-eu.bin` | a metade alta do mesmo DWORD |
| 488 | `0x004335f4` | 43, 121 | `ml-eu.bin` | nao identificado |
| 489 | `0x004335f6` | 43, 122 | `ml-eu.bin` | nao identificado |
| 512 | `0x00433624` | 21, 221 | `ml-eu.bin` | vizinho do mesmo bloco |
| 513 | `0x00433626` | 21, 222 | `ml-eu.bin` | vizinho do mesmo bloco |
| 514 | `0x00433628` | 21, 223 | `ml-eu.bin` | vizinho do mesmo bloco |
| 515 | `0x0043362a` | 21, 224 | `ml-eu.bin` | vizinho do mesmo bloco |
Sao 4 DWORDs, que e a granularidade em que o
[`crash-causa.md`](crash-causa.md) le a `.data`: `0x004335e4`,
`0x004335f4`, `0x00433624`, `0x00433628`.
O indice 462 -- `0x004335c0`, o proprio contador -- e o
primeiro endereco depois do vetor, e por isso o alvo mais obvio. **Ele
nao aparece acima**: e alcancavel em tese, e nao alcancado por nenhuma
das duas imagens. A diferenca importa, porque atropelar o contador
falsearia o proprio numero na tela, e nao e o que acontece.
[`crash-causa.md`](crash-causa.md) mediu, ao vivo e com a ROM europeia,
`0x004335e4`, `0x004335f4`, `0x00433624`, `0x00433628` mudando de `0x0`
para `0x00010001`, e nao mudando com a japonesa, e encerrou dizendo que
nomear a instrucao exigiria um watchpoint de hardware. **A instrucao e o
`inc WORD PTR [eax*2+0x433224]` de `0x0040435d`**, aqui, e a condicao e
vinculo apontando para time sem NC nenhum.
**Os 4 DWORDs previstos sao os 4 medidos ao vivo.** O confronto e feito
por este gerador, entre a lista de `ml-slots-fora.tsv` e a que o
`crash-causa.md` registrou -- e ja recusou concordar uma vez: a
transcricao de 2026-08-11 tinha tres linhas, esta ferramenta apontou a
quarta, e a sessao refeita em 2026-08-20 mostrou `0x004335f4` mudando no
mesmo instante que as outras. Modelo que enumera o conjunto acha a linha
que o olho perde no meio de vinte.
A mesma medicao traz a confirmacao numerica de graca: ela leu
`0x004335c0` indo a `0x0000000d` com a ROM europeia, e `0x0d` e **13**
-- o mesmo que esta ferramenta calcula e o mesmo que o rotulo mostra. Um
numero lido da memoria do processo em 2026-08-11, sem saber de quem era,
batendo com a conta escrita aqui; a sessao de 2026-08-20 leu o mesmo 13,
de outro valor anterior (`0x154` contra `0xf5`), que e o `memset` de
meia tabela deixando lixo diferente a cada corrida.
## Medido
| imagem | proprios | distintos | livres | fora do vetor | maior `b0` | tela do oraculo | tela do port |
|---|---:|---:|---:|---:|---:|:-:|:-:|
| `ml-jp.bin` | 461 | 460 | **2** | 0 | 116 | - | 2 |
| `ml-jp-pos-oraculo.bin` | 461 | 461 | **1** | 0 | 116 | 1 | 1 |
| `ml-eu.bin` | 453 | 449 | **13** | 8 | 111 | 13 | 13 |
As colunas de numero, ate `maior b0`, saem de
`python3 wte/tools/conta_ml.py --medir <copia>`, que escreve
[`ml-slots-medido.tsv`](ml-slots-medido.tsv). **Copia** -- `roms/`
nao e alvo de ferramenta nenhuma.
As duas ultimas sao o que o rotulo `casilla_xmlibres` mostrou no
`:99`, lido da captura: evidencia de **observacao de tela**, e a
unica que fecha o circuito entre a conta e o que o usuario ve.
### O ramo `b0 >= 120`, que nenhuma das duas alcanca
A `0x0040423c` soma `[0x00423424 + 4*t]` para todo `t < b0`. Com `b0 >=
120` ela le alem do fim da tabela de 120, e a soma passa a depender do
que a `.data` guarda depois dela -- lixo. **O port nao modela esse
ramo**, e a justificativa e medida, nao afirmada: o maior `b0` visto e
**116** (116 em `ml-jp.bin`, 116 em `ml-jp-pos-oraculo.bin`, 111 em
`ml-eu.bin`), o que deixa 4 de folga ate o teto de 120.
O numero sai da coluna `maior b0` da tabela acima, escrita pelo
`--medir` sobre as mesmas copias -- entra no perimetro do
`--check` e nao pode envelhecer sozinho. Ele conta so os pares
que CHEGAM a formula: o enchimento e os de `b1 < 23`
sao descartados antes, e `b0` alto num deles nao diria nada
sobre este ramo.
### O `-` da japonesa limpa, e o que ele revelou
**O oraculo altera a imagem ao abri-la**, e a alteracao muda a
propria conta. Duas corridas com copia nova da japonesa deixaram o
arquivo com DOIS bytes trocados em `2012984` -- o par de vinculo do
clube de ML 5, slot 13, de `(102, 23)` para `(0, 27)`. O time 102
nao tem NC nenhum, entao `(102, 23)` e referencia pendurada; a
troca a aponta para um bloco que ja estava ocupado, e por isso o
numero de distintos sobe de 460 para 461 e o de livres cai de 2
para 1.
Nao ha como o oraculo mostrar o numero da imagem limpa: quando o
rotulo aparece, o arquivo dele ja mudou. O confronto direto esta na
linha `ml-jp-pos-oraculo.bin`, que e a copia do arquivo QUE O
ORACULO PRODUZIU dada ao port -- os dois mostram `1`.
**Essa escrita ja estava registrada, sem significado.** A spec do
[`boton_dialogo_weClick`](spec/MainForm.boton_dialogo_weClick.md)
a lista desde a WTE-TASK-25 entre as *duas faixas do arranque que
continuam sem explicacao* -- `1921862..1921862` e
`2012984..2012985` --, declaradas `conhecida:` no roteiro do gate
porque o oraculo as grava e o port nao. O que esta medicao
acrescenta e o SIGNIFICADO da segunda: sao os dois bytes de um par
de vinculo, e trocar `(102, 23)` por `(0, 27)` custa um bloco
livre.
Continua sem dono a pergunta de QUEM escreve: a unica referencia
absoluta a `OFS_LINK_ML` em toda a `.text` e o `push 0x1eb608` de
`0x004042fc`, desta rotina, que so LE. O endereco sai calculado de
outro ponto do caminho de abertura, e na europeia a mesma sequencia
nao o toca.
## O port
[`we2002_ml.pas`](../src/we2002_ml.pas), com a tabela em
[`we2002_ml_tabela.inc`](../src/we2002_ml_tabela.inc), tambem gerado
daqui. Ele reproduz a conta, **e nao reproduz o estouro**: o indice
fora de `0..461` e contado num dicionario a parte, entao o
numero na tela e o mesmo do original e nenhuma variavel vizinha e
atingida. Divergencia deliberada, para a
[WTE-TASK-35](../../docs/tasks/35-divergencias-deliberadas.md).
