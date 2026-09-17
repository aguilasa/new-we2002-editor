# Perfil de ciclo — visualizador 3D da aparência do jogador

**Este arquivo é o perfil do ciclo `looks`**, nomeado pelo campo `perfil:` do
[`docs/tasks/looks/progresso.md`](/docs/tasks/looks/progresso.md) e carregado
pelos prompts de `docs/prompts/`. Os prompts têm o **rito**; o que é deste ciclo
mora aqui.

Fonte: [`PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md). Onde este perfil e o plano
divergirem, **o plano ganha** — aqui só mora o resumo operacional, e o
`fonte_de_verdade` de cada task aponta para a seção que a mede.

**Este ciclo mora numa subpasta.** Os comandos o recebem por argumento:
`/executar looks`, `/revisar looks`, `/corrigir looks`. Sem argumento, os
comandos continuam no `docs/tasks/` raso, que é o ciclo de PES2. A regra está no
"Passo 0" de cada prompt.

---

## Contexto essencial — decisões já confirmadas

Não se revertem sem o usuário pedir.

- **v1 é só visualizador.** Não grava na imagem, não grava no cartão. Decisão do
  dono do repositório em 2026-09-13.
- **A v2 é a tela `LOOKS SET` animada, e continua só lendo.** Decisão do
  usuário em 2026-09-17: a janela é a própria tela do jogo — doze linhas
  trocáveis, como os save states dos slots 1 e 2 a mostram — com o boneco
  montado, vestido e caminhando, como uma gravação de tela dele mostra. **A
  gravação é referência só visual**: não entra no git, e número nenhum sai
  dela; quem mede é o emulador. O não-objetivo "não anima" da §0 do plano está
  revogado para a v2; os outros continuam. **A tela vem antes da pose** por
  pedido do usuário, não por risco: ela roda sobre a v1 como está.
- **Dois discos, com papéis separados** (§1.3 do plano). `roms/japanese-shift-jis.bin`
  é a fonte de verdade dos **bytes**; o `.cue` inglês em
  `C:\games\ps1\work\we2002-english.cue` é o de **dirigir o emulador**, porque
  tem os menus legíveis. A divisão é legítima porque `EDT_MOD.BIN` e
  `MODEL.BIN` são byte a byte idênticos nos dois.
- **`roms/japanese-shift-jis.bin` e `we-2002-original-japao.bin` são o mesmo
  dump** — `sha256 e853eb14f5bddd50…`. Nomes diferentes, arquivo igual.
- **Dois save states prontos, e é por eles que se começa.** Gravados pelo
  usuário em 2026-09-14, com o jogo na tela de edição do jogador:
  **slot 1 = goleiro, slot 2 = jogador de linha**, os dois sobre
  `we2002-english.cue`. O emulador sobe por `.\make.ps1 we2002-play`, que já
  tem a inglesa como default. **Toda medição de tela começa em `load_state`** —
  não pela rota manual, e não de onde a sessão anterior parou.
- **Render por `QOpenGLWidget`**, não Qt3D e não rasterizador em Python.
  `numpy` não está instalado e instalar é decisão do dono da máquina.
- **Não estende o `we2002_core`.** Nada em `src/` aprende o que é modelo 3D.
- **Nada do Superpack entra no git** — nem arquivo, nem transcrição longa.
- **O `we3d` é MIT** e entra com crédito; o fonte `en_we2000edit` é testemunha,
  não código a copiar.

---

## Armadilhas medidas neste ciclo

1. **Ler textura do disco inglês é erro silencioso.** O `DAT2D.BIN` difere entre
   as duas imagens; o offset existe nos dois e entrega gráfico diferente, sem
   nenhuma mensagem. É a razão de a LOOKS-TASK-02 plantar uma guarda por digest
   em vez de confiar em disciplina.
2. **A varredura contígua morre na seção 55 do `MODEL.BIN`.** Parece formato
   errado e é a **corrida de palavras zero** que separa grupos (§1.4). Foi o
   primeiro tropeço da sessão de investigação. Esta linha dizia *"o par de zeros"*
   até 2026-09-17, e o par é a leitura que quebra: a corrida tem 8 bytes no
   `MODEL.BIN` — onde a forma fixa funciona por coincidência — e **12** nas duas
   primeiras folgas do `EDT_MOD.BIN`. Um varredor que consome sempre 8 cai 4
   bytes dentro do cabeçalho seguinte e lê `nPrim` na casa dos bilhões — o mesmo
   sintoma da seção 55, pela regra oposta
   ([`LOOKS-TASK-04`](/docs/tasks/looks/04-formato-de-secao.md)).
3. **O `EDT_MOD.BIN` é contíguo do offset 216 ao EOF**, e a lista serve para
   outra coisa. Esta armadilha dizia *"não é contíguo — varrer do começo sem a
   lista pega uma seção e para"*, e foi remedida em 2026-09-14
   ([`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md)): varrer **do 216**
   acha as **20** seções e fecha no EOF. O que quebra é começar no offset 0 ou
   no 8, que são o cabeçalho e as listas — `BadSection`, com contagens na casa
   dos bilhões. A lista é necessária pela **ordem** e por dizer **qual peça
   pertence a qual dos dois modelos**, não por alcance.
   **E terminar no EOF não prova que a varredura leu o arquivo:** começar em
   15.704 também fecha em 36.072 exato, com 11/690/611, e é metade do arquivo.
   Contagem de seção sem o offset de partida não é medição.
4. **A ordem da lista não é a ordem do arquivo.** O registro do offset 24.136 vem
   antes do 22.984. Assumir a do arquivo embaralha peça sem sintoma visível.
5. **`bin_archive.py` responde `0 clut(s)` sem reclamar**, e ler isso como "não
   tem paleta" continua sendo erro — mas o motivo não era o que esta linha
   dizia. Ela dizia *"a lista existe e o varredor não a acha"*, como se fosse
   falha de varredura. **Remedido em 2026-09-15**
   ([`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md)): a lista
   existe — 267 registros a partir de 76.836 — e o que a esconde é o **campo 7**
   do registro, que o `bin_archive.py` documenta como a tag constante `0x800f` e
   que é, medido, o **banco de 64 KiB do offset de 16 bits do campo 6**. O
   varredor está certo para os quatro discos que ele mede, onde nenhum payload
   passa dos primeiros 64 KiB. Quem lê paleta neste ciclo é o
   `tools/looks/texture.py`; `bin_archive.py` **não foi tocado, e a razão é de
   escopo**: ele é o varredor de outro projeto, cujo gate não é medido aqui.
   Esta linha dizia que generalizar o `entries()` faz aparecerem *"2.151
   registros a mais em 40 outros contêineres, os estádios incluídos"*, e esse
   número não reproduz por leitura nenhuma
   ([`CORR-LOOKS-022`](/docs/tasks/looks/CORR-LOOKS-022.md)): medido pelo
   `texture.py --survey`, o custo é de **80 registros em cinco contêineres, e
   nenhum deles é estádio**. §1.8 do plano.
6. **`MSYS_NO_PATHCONV=1`** em toda chamada do Git Bash que passe caminho de
   dentro do ISO. Sem ele `/BIN/EDT_MOD.BIN` vira `C:/Program Files/Git/BIN/…` e
   a mensagem de erro acusa "not a Form 1", que culpa a coisa errada.
7. **Círculo confirma, e precisa de pelo menos 8 frames.** Com 3 o jogo não
   registra: a tela fica igual e parece botão errado. Cruz abre `Exit?` com
   `CANCEL` já selecionado.
8. **Uma tecla de cada vez.** Confirmação em laço fecha a caixa seguinte junto —
   regra do [CLAUDE.md](../../CLAUDE.md), que custou uma corrida no ciclo `wte/`.
9. **O nome do save state não diz de que disco ele veio.** O arquivo se chama
   `SLPM-87056_N.sav` — serial **japonês** — mesmo quando o state foi feito na
   imagem inglesa. Um state da japonesa teria exatamente o mesmo nome e traria
   os menus ilegíveis. Quem decide é o campo `media` **de dentro** do arquivo.
10. **`savestate.py` não alcança a RAM nesta máquina.** Ele chama o CLI `zstd`,
    que não está no `PATH`, e o módulo `zstandard` também não está instalado.
    Ele imprime o cabeçalho e **depois** estoura com
    `FileNotFoundError [WinError 2]`, que não menciona `zstd` em lugar nenhum.
    Consequência: **RAM se lê por MCP vivo** (`read_memory`, `search_memory`,
    `snapshot_memory` + `diff_memory`), e o state serve como ponto de partida,
    não como fonte de memória.
11. **O diretório de save states é compartilhado com o trabalho de PES2.**
    Slot nu é sobrescrevível por acidente; os dois `.sav` do ciclo se copiam
    para um caminho do projeto e se apontam por variável.
12. **`ctest -R <padrao>` que não casa nada SAI 0.** Ele imprime
    `No tests were found!!!` e devolve sucesso, e isso vale para os cinco
    projetos do repositório. Já enganou **duas vezes** neste ciclo: a
    [`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md) sobre um alvo que
    não existia, e a
    [`CORR-LOOKS-015`](/docs/tasks/looks/CORR-LOOKS-015.md) sobre um alvo que
    existe no fonte e em build nenhum. **Confira `N tests passed`, nunca só o
    código de saída** — e, num alvo que deveria rodar, confira que o nome dele
    aparece na listagem.
13. **Os documentos da cena se contradizem, e o vencedor foi o tutorial.**
    O CARP rotula o offset 8 do `DAT2D.BIN` como "Pelos" e o 3.568 como
    "Caras"; o tutorial do `zeta` manda abrir o 3.568 para achar cabelo.
    **Medido em 2026-09-15**
    ([`LOOKS-TASK-11`](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md)): o
    cabelo é o **3.568** — as primitivas que `HAIR` e `FACE` movem têm `u`
    152..199, e numa página de 4 bits isso é a segunda metade. O `zeta` acertou;
    o *"Pelos"* do CARP está errado. O que fica de armadilha é outra coisa, e
    mais geral: **nome de arquivo de terceiro é rótulo como qualquer outro.**
    O `cabellowe2002.bmp` que vem ao lado do tutorial — "cabelo" no nome — é
    byte a byte o registro em **8**, e não o cabelo.
14. **Os campos da tela travam nas pontas; não dão a volta.** Medido em
    2026-09-15 ([`LOOKS-TASK-12`](/docs/tasks/looks/12-pele-paleta-ou-vertice.md)):
    o quarto `Right` no `SKIN` deixa o CLUT id exatamente onde o terceiro o
    pôs. Quem anda um campo esperando o ciclo voltar ao início lê esse valor
    repetido como **pressão que o jogo ignorou** e acusa falha — foi o que a
    primeira corrida do `--palettes` fez. O jeito de medir o alcance de um campo
    é andar até a ponta de baixo, depois até a de cima, e contar.
15. **Registro largo e registro estreito se sobrepõem na VRAM, e o estreito
    ganha.** Na linha 484 do `DAT2D.BIN` seis paletas de 16 entradas ficam por
    cima de uma de 256. Comparar a VRAM contra o registro largo dá **71**
    entradas diferentes e parece defeito de leitura; resolver cada `x` pelo
    `texture.covering` dá **zero** nas 21 linhas de CLUT do arquivo. O desempate
    "mais estreito ganha" não é convenção nossa: é o que o console faz.
16. **Número de terceiro vem em par, e só uma metade costuma estar certa.**
    O `Offsets We2002.txt` do Superpack dá *"157.164, 1.242 jogadores"* para os
    registros do `/SELECT.BIN`. Medido em 2026-09-15
    ([`LOOKS-TASK-13`](/docs/tasks/looks/13-campos-e-dominios-de-looks.md)): o
    **offset está certo** — o `OFS_PLAYER_ATTR` do próprio repositório cai no
    mesmo byte — e a **contagem está 207 curta**, são 1.449. Conferir a metade
    fácil e herdar a outra é o jeito de escrever um número errado com ar de
    medido; e aqui as duas metades se medem de graça, uma pelo `ofs_map.py` e a
    outra pela altura que deixa de ser plausível.
17. **Rótulo de tela não é nome de campo, e campo de tela nem sempre é campo.**
    A linha `FACE` é o `beard_style` e a `H.F.COL.` é o `beard_colour`; e
    `DEFAUL` e `NAT`, das doze linhas da tela, **não guardam nada** — são as duas
    metades do default por nacionalidade do `data/defaultlook.txt`. Contar doze
    campos porque a tela tem doze linhas erra por dois.
18. **O jogo reescreve o bloco de primitivas ao longo de MAIS DE UM QUADRO.**
    Medido em 2026-09-15
    ([`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md)): uma
    leitura logo depois da tecla trouxe 34 das 42 primitivas do `BOOTS` no CLUT
    novo e 8 ainda no velho — um estado que nunca existiu. E uma amostra tirada
    **antes** de a escrita começar é igual à anterior, o que uma varredura lê
    como fim do alcance: foi assim que 32 valores de `HAIR` viraram três e 8 de
    `BOOTS` viraram nove. Leia até **duas leituras seguidas concordarem**
    (`oracle.steady`), e recuse se nunca concordarem. **E duas leituras 20
    quadros separadas não bastam para uma cabeça inteira:** as listas de
    primitivas de `SKIN` (8) e `H.COL` (7) da seção 24 saíram assim, e das duas
    pontas assentadas, 300 quadros entre as leituras, são 14 e 12
    ([`CORR-LOOKS-049`](/docs/tasks/looks/CORR-LOOKS-049.md)). Quem mede **o que
    um campo move** compara as pontas (`oracle.py --colour`), não passo a passo.
19. **Alcance de tela não é domínio de campo — e "a tela alcança três" pode
    ser a JANELA, não a tela.** `beard_style` guarda oito, os rótulos nomeiam
    sete e a tela anda **sete** — esta linha dizia **cinco**, e era a mesma
    armadilha: cinco é a faixa dos dois quads da seção 24, e `F` e `G` desenham
    **outra seção**, o gêmeo da cabeça
    ([`CORR-LOOKS-044`](/docs/tasks/looks/CORR-LOOKS-044.md),
    [`CORR-LOOKS-048`](/docs/tasks/looks/CORR-LOOKS-048.md)). Já o `HAIR` guarda 32
    e a varredura leu **três**, e isso estava **errado** — corrigido em
    2026-09-16 ([`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md)):
    a célula de valor da linha se mexe em **32 de 32** teclas; o que assenta em
    três estados é a **seção 24**, que é uma família de cabelo só. Quem anda um
    campo observando **uma** seção mede aquela seção, e uma linha que escolhe
    entre treze delas fica parecendo uma linha que trava. A pergunta que separa
    os dois casos custa uma captura: **a tela mudou nessa tecla?**
20. **Byte parado não é byte não escrito, e byte não escrito é medição.** O `v`
    do quad de cabelo da seção 24 é reescrito pelo jogo com o **mesmo valor**
    sempre que a família A está selecionada, e não é escrito nenhuma vez nos
    valores das outras famílias — 90 s de execução livre sem um toque. Um
    watchpoint de escrita distingue as duas coisas; um diff de memória, não.
    Por isso o `oracle.catch_write` devolve `None` em vez de estourar quando
    ninguém escreve: "este valor não escreve" é resultado.
21. **Breakpoint de execução vê o que diff de memória não vê, e é assim que
    se mede escrita de valor igual.** O jogo reescreve o quad de cabelo com o
    **mesmo** byte quando o estilo não muda de família, e `--patched` (diff
    contra o disco) lê isso como "nada aconteceu". Um breakpoint na instrução
    do store — `layout.HAIR_QUAD_STORE` — dá a primitiva em `a0` e a faixa em
    `a2` a cada escrita. **E um store não serve o arquivo inteiro:** aquela
    instrução escreve os quads de quatro das treze cabeças, e as outras nove
    têm outro dono, que ninguém achou ainda. Medido em 2026-09-16
    ([`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md)).
22. **Tecla dada com a CPU parada num breakpoint pode não registrar.** Na
    varredura do `--writes`, **5 de 31** teclas não moveram a célula de valor —
    e sem a captura ao lado, cada uma delas poria as escritas seguintes sob o
    rótulo errado. Quem anda um campo em execução livre **confere a tela a cada
    passo** e diz quantas não pegaram, em vez de assumir que pegaram.
23. **Display list de cena animada não é observação.** As duas faixas de
    buffer da §6(a) se reescrevem a **cada quadro**, porque o boneco anima:
    andar um campo lendo-as morre no `steady()` com *"never settled"*, e está
    certo que morra. Medido em 2026-09-16
    ([`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md)). Quem
    precisar do que o campo escreve lá usa o filtro de churn do `field_diff`,
    ou breakpoint de escrita — que o fork oferece e este ciclo ainda não usou.
24. **Nenhum dos dois arquivos de modelo diz ONDE uma peça fica.** Cada seção
    é modelada em torno da própria origem, então desenhar as doze nas
    coordenadas do arquivo empilha o boneco num ponto só — e cada peça, isolada,
    parece perfeita. Quem posiciona é o jogo, na display list. Medido em
    2026-09-16
    ([`LOOKS-TASK-15`](/docs/tasks/looks/15-visualizador-opengl.md)); o
    visualizador desenha uma **prateleira** (`scene.shelf`) e diz que é uma.
25. **Uniforme int do PySide6 se escreve com `setUniformValue1i`.** Passar um
    `int` para o `setUniformValue` geral chega no shader como zero, sem erro
    nenhum: o primeiro render saiu com o boneco inteiro na cor de espaço
    reservado, o que parece textura que não carregou. O mesmo vale para o
    sampler. E a segunda armadilha da mesma família: o modelo olha para **-z**,
    então a câmera em yaw 0 fotografa a nuca — um crânio preto que também
    parece falha de textura.
26. **Percentual de semelhança sem o nulo ao lado não se lê.** Na folha de 4
    bits deste arquivo um índice cobre um quinto dos texels, então chutar esse
    índice em toda parte já dá ~16%. Foi o que quase fez "9,2% igual" passar por
    "diferente" e "85,7%" por "parecido", quando os números diziam
    *não relacionado* e *é o mesmo arquivo editado*. O
    `atlas.py --compare` imprime o nulo em cada linha por isso.
27. **Árvore plantada que nem importa fica vermelha, e vermelho pela causa
    errada não prova nada.** Medido em 2026-09-16
    ([`LOOKS-TASK-16`](/docs/tasks/looks/16-contratos-da-ui.md)): a primeira
    corrida do `ui_check.py` anunciou **3 de 3** controles vermelhos, e os três
    tinham morrido em `ModuleNotFoundError: No module named 'lzss'` — o
    `atlas.py` alcança `tools/pes2/` de lado, e a cópia levava só
    `tools/looks/`. O `controls.py` já copiava as duas pastas, com a razão
    escrita. Duas consequências: **copie o que a árvore alcança**, e faça o
    plantio **distinguir "não rodou" de "rodou e o juiz reprovou"** — sem essa
    separação, um controle que quebra o import passa por guarda exercitada para
    sempre.
28. **A célula de valor não conta valores.** A caixa do `oracle.row_value`
    contém a seta de fim de curso — que some na ponta do alcance — e o cursor
    amarelo que **pisca** entre dois brilhos. Contando por diferença crua da
    célula, o `FACE` deu **8** valores num slot e 7 no outro, numa linha que
    mostra sete rótulos nos dois. A letra não pisca: o `confront.glyph_mask`
    lê só os pixels lavanda do rótulo, com controle ocioso antes. Medido em
    2026-09-16 ([`LOOKS-TASK-17`](/docs/tasks/looks/17-confronto-com-o-emulador.md)).
29. **Um quadro do jogo e um render nosso não se comparam por pixel.** A pose e
    a câmera mudam quase todo pixel sem que a tupla mude; o que a tupla muda é
    o **histograma de cor**, e as cores dos quads saem exatas, sem modulação.
    E vitória por pouco não é derrota: uma interseção não pode liderar por mais
    do que os **nossos** dois renders distam entre si, e o `confront.verdict`
    imprime esse teto ao lado. **Mas só onde o teto explica:** liderança abaixo
    da margem passa como `ranked` quando o teto é menor que `2 × MARGIN`, e
    falha sob teto largo — até a
    [`CORR-LOOKS-045`](/docs/tasks/looks/CORR-LOOKS-045.md) passava sempre.
30. **Histograma de cor resolve cor e não resolve forma — e quem prova é o
    controle, não o corpus.** Contra os 47 renders do corpus, 35 JPEGs não ficam
    em primeiro; lido sozinho, isso parece render errado. Os quadros do
    **emulador**, com a verdade conhecida, ficam em 3º e 4º na mesma matriz.
    Pele, cor de cabelo e cor de barba o argmax acerta sempre; estilo e barba,
    metade. Medido em 2026-09-16
    ([`LOOKS-TASK-18`](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md)).
    **Métrica sobre dado de terceiro sem controle de verdade conhecida ao lado
    não diz de quem é a falha.**
31. **Exceção dentro do `__enter__` não passa pelo `__exit__`.** O `Oracle`
    sobe o emulador no `__enter__` e o derruba no `__exit__`; quando o primeiro
    `pause` falhou, na primeira corrida do `looks_live` pelo `ctest`, o
    emulador **ficou de pé** depois de o teste terminar — e o DuckStation tem
    um diretório de dados só, então a sobra derruba a próxima corrida de
    qualquer projeto. Todo recurso adquirido no `__enter__` se solta ali mesmo
    se o resto dele falhar. Medido em 2026-09-17
    ([`LOOKS-TASK-19`](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md)).
32. **O servidor MCP do fork guarda UMA sessão, e o editor é um segundo
    cliente.** O `.mcp.json` registra o fork na porta 2346 no escopo do projeto;
    um `initialize` de qualquer outro cliente invalida a sessão de quem a tinha,
    e a próxima chamada volta `HTTP 400 ... missing or invalid MCP-Session-Id`.
    Medido em 2026-09-17, **3 de 3** com um segundo cliente de propósito
    ([`CORR-LOOKS-051`](/docs/tasks/looks/CORR-LOOKS-051.md)) — é o vermelho
    sem causa que o `looks_live` deu uma vez em catorze. O `oracle.OneSession`
    refaz o `initialize` **uma vez** e imprime `MCP session taken by another
    client`; ver essa linha num Log é sinal de dois clientes na porta, e perder
    de novo logo depois do novo handshake falha — não é caso de rodar até passar.

---

## As fontes de verdade binárias

| o que | onde | quem é fiel |
| --- | --- | --- |
| geometria | `/BIN/EDT_MOD.BIN`, `/BIN/MODEL.BIN` | igual nos dois discos |
| textura e paleta | `/BIN/DAT2D.BIN` | **só o japonês** |
| registros de jogador | `/SELECT.BIN` +157.164, **1.449** × 12 B — dizia 1.242, o número do Superpack, até a LOOKS-TASK-13 medir (armadilha 16) | japonês |
| corpus de render | 50 JPGs do Superpack | terceiro, fora do git |

Leitura pura em todas. **Nenhuma task deste ciclo escreve em imagem de CD** —
se alguma precisar, o escopo mudou e isso é conversa com o usuário, não decisão
de execução.

---

## Estrutura

```text
tools/looks/        núcleo Python puro — ZERO Qt, ZERO endereço fora de layout.py
tools/looks/ui/     PySide6 — ZERO endereço, ZERO leitura de disco
work/venv-looks/    fora do git
docs/tasks/looks/   este ciclo
```

As três regras de desenho (§3.3 do plano) são varridas mecanicamente pelo
`selftest.py`, e a varredura usa `os.walk` — `os.listdir` não enxerga `ui/`, e
foi assim que o ciclo do `.mcr` deixou uma pasta inteira fora da regra.

---

## Gates deste ciclo

| alvo | precisa | **como se roda AQUI** | por `ctest`, onde o build configura | existe desde |
| --- | --- | --- | --- | --- |
| `looks_selftest` | nada — **nunca pula** | `python tools/looks/selftest.py` | `ctest -R looks_selftest` | LOOKS-TASK-06 |
| `looks_image` | `WE2002_LOOKS_IMAGE` (77 sem ela) | `python tools/looks/cli.py check` — os oito `--check-image`, todos até o fim (a ordem é de leitura, não guarda — [`CORR-LOOKS-052`](/docs/tasks/looks/CORR-LOOKS-052.md)); até a LOOKS-TASK-19 era só o `modelfile.py --check-image` | `ctest -R looks_image` | CORR-LOOKS-012 |
| `looks_ui` | venv + display + `WE2002_LOOKS_IMAGE` (77 sem eles) | `python tools/looks/ui_check.py` | `ctest -R looks_ui` | LOOKS-TASK-16 |
| `looks_live` | as duas variáveis, os dois states e o fork (77 sem eles, antes de subir processo) | `python tools/looks/oracle.py --check-live` | `ctest -R looks_live` | LOOKS-TASK-19 (o comando, da LOOKS-TASK-07) |
| *(dentro do `looks_image`)* | `WE2002_LOOKS_IMAGE` (77 sem ela) | `python tools/looks/texture.py --check-image` | — | LOOKS-TASK-10 |
| *(dentro do `looks_image`)* | `WE2002_LOOKS_IMAGE` (77 sem ela) | `python tools/looks/atlas.py --check-image` | — | LOOKS-TASK-11 |
| *(dentro do `looks_image`)* | `WE2002_LOOKS_IMAGE` (77 sem ela) | `python tools/looks/skin.py --check-image` | — | LOOKS-TASK-12 |
| *(sem alvo ainda)* | as duas variáveis, os dois states e o emulador | `python tools/looks/oracle.py --palettes` | — | LOOKS-TASK-12 |
| *(dentro do `looks_image`)* | `WE2002_LOOKS_IMAGE` (77 sem ela) | `python tools/looks/looks.py --check-image` | — | LOOKS-TASK-13 |
| *(dentro do `looks_image`)* | `WE2002_LOOKS_IMAGE` (77 sem ela) | `python tools/looks/assembly.py --check-image` | — | LOOKS-TASK-14 |
| *(sem alvo ainda)* | as duas variáveis, os dois states e o emulador; ~1 min, e ~30 s por tupla | `python tools/looks/oracle.py --patched <LINHA> [<SLOT> [<TUPLA> ...]]` — o slot desde a CORR-LOOKS-047 (sem ele é o 2); as tuplas desde a CORR-LOOKS-048, uma caminhada por tupla a partir de `load_state`, com as primitivas mudadas impressas | — | LOOKS-TASK-14 |
| *(sem alvo ainda)* | idem, e leva ~15 min | `python tools/looks/oracle.py --hair` | — | LOOKS-TASK-14 |
| *(sem alvo ainda)* | idem, e leva ~3 a 12 min | `python tools/looks/oracle.py --writes HAIR [<SLOT>]` | — | LOOKS-TASK-14 |
| *(sem alvo ainda)* | idem; ~45 s por tupla | `python tools/looks/oracle.py --colour <LINHA> [<SLOT> [<TUPLA> ...]]` — as primitivas que uma linha de cor move em cada cabeça, pelas duas pontas assentadas | — | CORR-LOOKS-049 |
| *(sem alvo ainda)* | `WE2002_LOOKS_IMAGE` + `WE2002_LOOKS_CORPUS` (77 sem elas) | `python tools/looks/assembly.py --corpus` | — | LOOKS-TASK-14 |
| *(sem alvo ainda)* | `WE2002_LOOKS_CORPUS`, ou a pasta por argumento (77 sem ela) | `python tools/looks/looks.py --corpus` | — | CORR-LOOKS-027 |
| *(dentro do `looks_image`)* | `WE2002_LOOKS_IMAGE` (77 sem ela) | `python tools/looks/scene.py --check-image` | — | LOOKS-TASK-15 |
| *(sem alvo ainda)* | as duas variáveis (77 sem elas) | `python tools/looks/scene.py --corpus` | — | LOOKS-TASK-15 |
| *(o que o `looks_ui` dirige)* | venv + a imagem; **nada aparece na tela** | `work/venv-looks/Scripts/python tools/looks/ui/app.py --smoke` | — | LOOKS-TASK-15 |
| *(sem alvo ainda)* | idem | `… tools/looks/ui/app.py --looks <tupla> --screenshot <png>` | — | LOOKS-TASK-15 |
| *(sem alvo ainda)* | só o venv | `… tools/looks/ui/app.py --compare <png> <png>` | — | LOOKS-TASK-15 |
| *(sem alvo ainda)* | as duas variáveis, os dois states, o emulador e o venv; ~40 min | `python tools/looks/confront.py --run` | — | LOOKS-TASK-17 |
| *(sem alvo ainda)* | venv + `WE2002_LOOKS_IMAGE`; **sem emulador**, ~15 s | `python tools/looks/confront.py --render` — refaz só o **nosso** lado, apagando PNG **e** `.refused` de cada tupla | — | CORR-LOOKS-046 |
| *(sem alvo ainda)* | `WE2002_LOOKS_IMAGE` e as capturas de um `--run` | `python tools/looks/confront.py --score` — **falha** se uma tupla tiver PNG e `.refused` ao mesmo tempo | — | LOOKS-TASK-17 |
| *(sem alvo ainda)* | as duas variáveis, os dois states e o emulador | `python tools/looks/confront.py --reach <LINHA>` | — | LOOKS-TASK-17 |
| *(sem alvo ainda)* | `WE2002_LOOKS_IMAGE`, `WE2002_LOOKS_CORPUS` (77 sem ela), o venv e o PIL | `python tools/looks/corpus.py --run` | — | LOOKS-TASK-18 |
| *(sem alvo ainda)* | idem, sem venv; o controle roda se houver capturas da 17 | `python tools/looks/corpus.py --score` | — | LOOKS-TASK-18 |

**Nenhum diretório de build do worktree alcança alvo nenhum**, e por isso a
coluna do meio existe. Medido em 2026-09-14
([`CORR-LOOKS-015`](/docs/tasks/looks/CORR-LOOKS-015.md)): `build`,
`build-mingw` e `build-windows-release` respondem `No tests were found!!!` e
**saem 0**, e nenhum `CTestTestfile.cmake` deles cita `looks`. O `build/` foi
gerado noutra máquina (`CMAKE_HOME_DIRECTORY:INTERNAL=/home/ingmar/...`).

**Mas o `ctest` é alcançável aqui — com o toolchain do vcpkg**, e a receita
estava só na cabeça de quem a usou. Sem ela o `find_package(CURL REQUIRED)` do
`src/core/CMakeLists.txt:1` derruba a configuração inteira, e com ela os dez
testes Python de `tests/`, que não têm nada a ver com o CURL:

```sh
cmake -S . -B <build> -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake
ctest --test-dir <build> -R looks
```

```text
1/2 Test #10: looks_selftest ...................   Passed
2/2 Test #11: looks_image ......................***Skipped   (sem a variavel)
100% tests passed out of 2
```

Com `WE2002_LOOKS_IMAGE` apontada, os dois passam. **Use um diretório de build
fora da árvore** — reconfigurar o `build/` do worktree destruiria o cache da
outra máquina.

`tools/looks/` **não precisa de compilador, libcurl, Qt nem venv** — o
comentário do próprio alvo diz "It needs NOTHING", e ainda assim depende de um
toolchain de C++ para ser listado. Tornar os alvos Python alcançáveis sem o
`src/core` seria o conserto de verdade; alcança os **cinco** projetos e é
**decisão de arquitetura de build, do dono do repositório** — não escolha de
execução. Fica **aberta**, e enquanto estiver, a coluna do meio é o caminho
curto: ela não depende de build nenhum.

Hoje são **1 passed, 3 skipped** numa máquina limpa — medido em 2026-09-17,
com os quatro alvos listados pelo nome —, e **4 passed** com as duas variáveis
apontadas, o venv e o fork no lugar. Eram *1 passed, 2 skipped* e *3 passed*
até a [`LOOKS-TASK-19`](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md), que
registrou o `looks_live`.

**Antes da LOOKS-TASK-06 não há gate**, e isso é esperado: as tasks 01 a 05 se
verificam pela saída da ferramenta, copiada para o Log. Depois dela, toda task
fecha com o `selftest` verde.

**E nenhum alvo pode passar sem ter medido.** Alvo que passa imprimindo um
`note:` sobre o que não mediu é a armadilha que o `mcr_ui` pagou; aqui o
contrato é: mediu e passou, ou pulou com 77.

**A transcrição do gate se tira DEPOIS do último commit da task, e nomeia o
commit.** Não é zelo: a árvore anda a cada edição da própria task, e o número
copiado no meio da execução descreve uma árvore que não existe mais. Três vezes
neste ciclo, em três tasks seguidas — 8.916 contra 10.182 na
[`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md)
([`CORR-LOOKS-032`](/docs/tasks/looks/CORR-LOOKS-032.md)), 11.789 contra 11.831
na [`LOOKS-TASK-15`](/docs/tasks/looks/15-visualizador-opengl.md)
([`CORR-LOOKS-036`](/docs/tasks/looks/CORR-LOOKS-036.md)) e 12.609 contra
12.613 na [`LOOKS-TASK-16`](/docs/tasks/looks/16-contratos-da-ui.md)
([`CORR-LOOKS-041`](/docs/tasks/looks/CORR-LOOKS-041.md)). A forma que
sobrevive é `# na arvore de <sha>` ao lado do comando; remedir depois é
`git worktree add --detach <tmp> <sha>` e rodar o gate lá.

---

## Arquivos quentes deste ciclo

- `tools/looks/layout.py` — todo endereço passa por aqui. Duas tasks editando
  este arquivo ao mesmo tempo se atropelam.
- `tools/pes2/bin_archive.py` — **arquivo de outro projeto**, e o ciclo **não o
  tocou**: a LOOKS-TASK-10 leu as paletas pelo `texture.py`, e a dívida do campo
  7 ficou registrada no plano de PES2 pela LOOKS-TASK-20. Se alguém mexer nele
  por aqui, o `pes2_selftest` tem de continuar verde,
  e isso entra no critério de conclusão, não na esperança.
- `tests/CMakeLists.txt` — os quatro alvos entram aqui, junto com os dos outros
  quatro projetos.
- `NOTICE.md` — tocado pela 01 e reconferido pela 20.
- `docs/PLAN-LOOKS-PY.md` — **o plano se corrige na seção que muda**, nunca num
  apêndice de erratas.

---

## Recursos serializados

- **O emulador é um só.** DuckStation usa um único diretório de dados, então
  roda **uma instância por vez**. Task que precisa do emulador não corre em
  paralelo com outra que precisa. E `.\make.ps1 pes2` **derruba** um
  `we2002-play` em curso.
- **Os dois save states são fixture compartilhada.** Não se sobrescrevem sem o
  usuário pedir: refazê-los custa uma navegação manual que nenhuma ferramenta
  do ciclo sabe reproduzir hoje.
- **A tela do usuário.** Nada abre janela visível: `:98` no Linux, janela em
  −32000 no Windows.

---

## Antecipação

**A LOOKS-TASK-13 pode ser antecipada** assim que a 09 fechar, e provavelmente
deve: ela depende só da 09, é a task mais barata do ciclo — transcrição
conferida contra quatro implementações que já concordam — e tanto o `--looks` da
UI quanto o parser de tupla do corpus dependem dela. É o padrão que o
`01-executar.md` já autoriza: tarefa de fase adiante de que uma tarefa da fase
corrente precisa.

**O que não se antecipa:** nada que dependa da LOOKS-TASK-08. Enquanto a
incógnita (a) estiver aberta, escrever montagem ou caçar paleta é trabalhar
sobre dado que pode não ser o que a tela desenha.

---

## Verificações específicas por fase

- **Fase 0** — o `NOTICE.md` distingue os **três** materiais de terceiro e as
  três situações legais, sem fundir as duas que não têm licença com a que tem.
  O venv existe e o `pip freeze` dele vai para o Log. E a pergunta que decide a
  fase: **a guarda dos dois discos existe como código, com caso vermelho?** Uma
  regra que só vive na prosa não impede ninguém de ler paleta no disco errado,
  e esse erro não tem sintoma.
- **Fase 1** — todo módulo novo traz `self_check()` com **caso vermelho**;
  nenhum endereço fora de `layout.py`, conferido por varredura e não por
  leitura; e nada em português no código (§3.5). As contagens são **asserção**,
  não comentário: `MODEL.BIN` 106/2.461/1.767 **a partir de 1816** terminando
  em 64.800, e `EDT_MOD.BIN` 20/1.218/1.074 **a partir de 216** terminando em
  36.072. **Toda contagem vem com o offset de onde a varredura começou**, e
  isso não é zelo: começar em 15.704 dá 11/690/611 fechando no mesmo EOF
  exato, o que passou por leitura completa do arquivo e era metade dele
  ([`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md)). **Uma varredura que não chega
  ao EOF não é "quase certa", é errada** — foi exatamente assim que o formato
  revelou o separador de zeros. E o controle negativo do tamanho de primitiva
  (24 → 20) tem de ficar vermelho; se ficar verde, a varredura não está
  medindo o que diz medir.
- **Fase 2** — a tela é alcançada por **`load_state`**, e o Log traz a captura
  e o `media` conferido de dentro do state. **Toda medição recarrega o state
  antes**, e a revisão pergunta por isso: um diff tirado de uma sessão que já
  andou mede também tudo que o jogo mexeu no caminho, e parece achado. Diff que
  não reproduz a partir do state recarregado é ruído. As duas medições valem
  nos **dois slots** — o que diferir entre goleiro e jogador de linha é
  uniforme ou posição, não LOOKS, e essa separação sai de graça. A
  incógnita (a) tem veredito **com a evidência ao lado**, não com uma
  conclusão. Pergunta obrigatória da revisão: **o veredito distingue "medi e é
  isto" de "não achei o contrário"?** Os quatro TMDs de `0x00168xxx` não
  pertencem a nenhum dos dois arquivos, e "o boneco deve vir do `EDT_MOD.BIN`"
  sem medição é a hipótese confortável, não a medida. Para a 09, cada peça
  nomeada traz **como se soube** — trocar a opção e ver o que muda, nunca
  deduzir do número de vértices.
- **Fase 3** — toda leitura de textura sai do **disco japonês**, e a revisão
  confere isso explicitamente em cada comando do Log. **E toda paleta tem
  largura de registro, nunca de arquivo:** o `DAT2D.BIN` guarda 262 de 16
  entradas e 5 de 256, e um id de 4 bits pode apontar para dentro de uma de 256
  — ler a largura errada devolve dezesseis entradas que desenham perfeitamente e
  são as cores erradas. **E toda imagem tem página, não só offset:** uma página
  de 4 bits cobre 256 texels e as imagens deste arquivo têm 128, então `u` acima
  de 127 amostra a imagem **seguinte** — foi disso que saiu o veredito da §1.8,
  e é o que um mapa campo → imagem erra sem sintoma. A lista de CLUTs é achada
  **por marcador**, não por offset constante — é a regra que o
  `bin_archive.entries()` já segue e a razão de o mapa de PES2 nunca ancorar em
  constante. A contradição 8 × 3.568 tem veredito com o documento errado
  nomeado. **E paleta larga não é paleta: é grade** — um registro de 256
  entradas são dezesseis CLUTs de 4 bits lado a lado, e um campo que "troca a
  paleta" pode estar andando a linha (a pele) ou a coluna (o cabelo, a barba);
  a revisão pergunta **qual das duas**, porque as duas se escrevem no mesmo
  byte do CLUT id. Alcance de campo é **andado até as duas pontas**, nunca
  deduzido do número de bits que o `Player.cpp` reserva: `beard_colour` tem três
  bits e a tela oferece sete valores. E se o conserto tocou
  `tools/pes2/bin_archive.py`, o `pes2_selftest` verde aparece no Log.
- **Fase 4** — os domínios conferidos **campo a campo** contra
  `src/core/Player.cpp`, com o cross-check dentro do `self_check()` e não só na
  prosa da task — e **mecanicamente**: o `looks.py` lê as expressões daquele
  arquivo e roda as duas lado a lado sobre blobs, que é o que separa "conferido"
  de "redigitado". A revisão pergunta também **quantos valores o campo guarda e
  quantos alguém nomeou**: três campos têm menos rótulo do que bits, e um
  índice sem rótulo é lacuna de terceiro, não defeito — recusar nele faz a
  ferramenta rejeitar um disco que o jogo roda. Para a 14, a pergunta que decide: **cada linha da tabela de
  montagem diz de onde veio?** Tabela derivada de medição e tabela plausível
  são indistinguíveis depois de escritas, e a armadilha das oito listas de nome
  de time do PES2 é o precedente. Buraco nomeado vale mais que mapeamento
  inventado.
- **Fase 5** — captura de tela no Log, e **nenhuma janela apareceu para o
  usuário** (`:98` no Linux, −32000 no Windows). O gate julga o PNG, não a
  saída do processo: duas tuplas visivelmente diferentes têm de produzir
  imagens diferentes, senão o alvo passa desenhando sempre o mesmo boneco. E a
  regra 3 varrida: nenhum `import layout` em `ui/`, e `PySide6` fora de
  `sys.modules` depois de importar o núcleo.
- **Fase 6** — **três tuplas, não uma**, e a métrica nomeada. A captura sai do
  **mesmo quadro** em toda corrida — `pause` mais `frame_step` contado a partir
  do `load_state`, nunca "depois de uns segundos"; senão o número muda entre
  corridas sem que nada tenha mudado, e a variação vira falso achado. Cada fonte de
  diferença atribuída a pose, câmera, resolução ou filtro; o que sobrar sem
  explicação é achado e vira CORR. A §5.6 já avisa que a comparação **nunca**
  bate pixel a pixel — então a revisão pergunta o contrário do usual: **o
  número foi olhado, ou só registrado?** E os piores casos do corpus são
  examinados um a um, que é onde erro sistemático aparece.
- **Fase 7** — `ctest -R looks` com o número copiado da saída, e os alvos dos
  outros quatro projetos sem regressão. Cada incógnita da §6 com veredito
  escrito: respondida com a medição, ou aberta com a razão e o que a
  destravaria. Cada afirmação da §1 que a execução desmentiu **corrigida no
  lugar**, com a data e o que ela dizia antes — o plano não ganha apêndice de
  erratas. E o `check_tasks.py` verde.
- **Fase 8** — **todo texto que a janela mostra veio do jogo, lido por
  ferramenta** — da tabela de texto em RAM ou das células capturadas —, nunca
  do rótulo do `looks.py` nem de transcrição à mão (armadilha 17). O cursor foi
  andado até as duas pontas nas **doze** linhas, não só nas de cor. A recusa é
  **visível**: valor que o `assembly` recusa aparece na ajuda e não desenha a
  cabeça de outro estilo. O gate dirige a janela por tecla, fora da tela, e a
  comparação com o jogo é a mesma sequência de teclas a partir do
  `load_state`, com a sequência repetida no jogo como controle. E `NAT` →
  linha do `defaultlook.txt` é medido no jogo — casar por índice aplica o
  default da nação errada com cara de certo.
- **Fase 9** — a pergunta que decide a fase é a da Fase 2, um nível acima:
  **o veredito sobre a fonte da pose distingue "medi e é isto" de "não achei o
  contrário"?** Um `ANIME.BIN` que carrega na RAM não prova que a pose sai dele.
  Toda captura de matriz sai de **quadro contado** a partir do `load_state`, e
  duas capturas do mesmo quadro são idênticas número a número — e dois quadros
  diferentes, diferentes, senão a captura lê uma constante. Matriz é ponto
  fixo: a comparação do leitor contra o jogo é **exata**, e "quase igual" é
  achado, não tolerância. Contagem do `ANIME.BIN` sempre com o offset de
  partida, e a varredura até o EOF (Fase 1). Silhueta só se compara com a
  câmera do jogo, e o limiar sai do controle — emulador contra emulador no
  mesmo quadro dá zero, em quadro deslocado dá diferença —, escrito depois de
  medido e dito que foi. `HEIG` e `BODY` se medem pela pose, nunca pela
  suposição de escala linear.
- **Fase 10** — toda leitura de `TEX_*.BIN` sai do **disco japonês**, pela
  guarda, com o digest escrito antes do primeiro byte lido; a forma de cada
  arquivo (form1 ou form2) **medida** no japonês, não herdada da
  `golden-european-deluxe.bin`. Qual arquivo a tela veste se mede na VRAM, não
  pelo nome nem pelo time. Cenário que é imagem sai do disco; cenário que é
  polígono se desenha — e qual é qual, pela display list. E a revisão pergunta:
  **o confronto de cor da Fase 6 foi re-rodado com o uniforme**, e as tuplas
  continuam em primeiro?
- **Fase 11** — o ritmo sai de `frame_step` contado, **nunca** da gravação do
  usuário, que tem a cadência do gravador. Interpolação é medida contra quadros
  que não são quadro-chave. A animação se confere em **vários** quadros do
  ciclo, nos dois slots — um quadro certo é pose. Os gates desenham `--frame N`
  determinístico; o timer é só para quem olha. Nenhuma janela aparece nos
  gates; só o `.\make.ps1 looks` abre visível.
