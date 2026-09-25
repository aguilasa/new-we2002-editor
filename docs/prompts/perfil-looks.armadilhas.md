# Armadilhas do ciclo `looks` — da 70 em diante

As armadilhas 1 a 69 estão no
[`perfil-looks.md`](/docs/prompts/perfil-looks.md), na seção "Armadilhas
medidas neste ciclo". Este arquivo guarda da 70 em diante — da 80 desde a
[`LOOKS-TASK-36`](/docs/tasks/looks/36-os-sprites-estaticos.md) e da 70 desde a
[`LOOKS-TASK-40`](/docs/tasks/looks/40-a-camera-do-close-up.md), cada vez que o
perfil chegou ao limite de tamanho do rito (`[profile].max_kb`). O rito lê este
arquivo **por busca**, não por inteiro, então cada entrada nomeia os caminhos
e os termos que a disparam.

70. **O close-up GIRA o modelo, e a carga de câmera não traz o giro.** Com uma
    linha de cabeça sob o cursor, cada peça carrega um giro extra em `y` —
    +18,3°, −16,9° e +16,9° em três capturas, igual a 0,05° nas doze peças de
    cada uma — que a carga em `layout.POSE_MATRIX` não tem. Composta com ela, a
    translação espalha 29 unidades; derivada das peças
    (`oracle.camera_from_pieces`), menos de uma. No corpo inteiro as duas
    coincidem. **Câmera se deriva das peças que ela compôs**, e as doze têm de
    concordar — é a conferência. E foto e câmera saem da **mesma parada**: o
    giro muda de captura para captura.
71. **Resumo de uma lista ordenada não é o intervalo dela.** Conferindo se
    `T_peça − R·lugar` era constante no close-up, a primeira impressão mostrou
    os quatro primeiros valores ordenados, todos a ±1, e foi lida como
    "constante" — o intervalo inteiro era de **29** unidades. Conferência de
    constância imprime **mínimo e máximo**, nunca a cabeça da lista.
72. **`HEIG` e `BODY` moram na CÂMERA, não na pose.** O jogo guarda um vetor
    de escala da figura (`layout.FIGURE_SCALE`) e escala as **colunas** da
    rotação da figura antes de multiplicar a vista: `x = z = (h<<12)/(tabela
    [BODY]+10)`, `y = (h<<12)/180`, `h = HEIG+148`. Então `HEIG` escala os três
    eixos — o alto também é largo — e `BODY` só largura e profundidade. Palpite
    de "escala linear em altura" teria errado dois eixos de três. A regra se
    **lê do código** do `/SELECT8.BIN` (`stature.rule`), incluindo o `/180`,
    que não é `div`: é a multiplicação mágica `0xB60B60B7` com `sra 7`.
73. **Quadro contado igual não é quadro da caminhada igual depois de trocar um
    valor.** Acolchoar toda captura até o mesmo quadro contado desde o
    `load_state` devolveu passada **sem par** em 155 e 210 cm onde o estado,
    no mesmo quadro, tinha doze: a troca de valor desloca a fase da caminhada.
    E uma passada quase sempre desenha **dois** quadros do `ANIME.BIN` — a
    animação avança no meio dela —, cortados numa peça que muda com a fase:
    comparar os pares peça a peça gastou 80 passadas procurando um corte que
    não voltava. O que nomeia a pose é o **conjunto de quadros**
    (`oracle._stature_frames`).
74. **No goleiro, as peças do quadro 0 não são as do arquivo** — com os
    ângulos do scratchpad **iguais** aos do par. É a volta do ciclo, onde o jogo
    mistura com o quadro anterior (a média da visita que abre um lado, medida
    na task 32), e acontece na
    estatura do próprio estado. Controle que caísse ali cobraria da regra de
    estatura um erro do leitor de pose; o `--stature` exige que o controle seja
    uma passada que o leitor reproduz **inteira** e imprime as que recusa.
75. **Escalar linhas ou colunas dá os mesmos nove inteiros nesta tela.** Com
    `sx = sz` e a figura girada só em `y`, as duas leituras coincidem, e nenhum
    controle as separa — um controle plantado com a troca ficou **verde**, e
    saiu em vez de ficar fingindo. O `stature.camera` recusa qualquer outro
    giro, que é onde a diferença começaria a aparecer.
76. **Silhueta só ordena o que o próprio jogo separa.** `D TYPE` é 10% mais
    largo que o estado, e a foto do jogo em `D` difere da do estado em
    **menos** pixels do que a nossa melhor comparação já erra — então a nossa
    figura na estatura do estado pontuou *melhor* que a certa, nos dois slots,
    com todos os limiares da task 28 verdes. Não é defeito da regra (as peças
    batem inteiras): é resolução, a mesma da armadilha 68. O
    `--silhouette-stature` só afirma a ordem quando a mudança do jogo supera o
    resíduo, e imprime o resto como "abaixo da resolução".
77. **O uniforme é por time, e o contêiner se mede na VRAM.** São 105
    `TEX_*.BIN` com os mesmos retângulos; o nome não diz qual a tela usa. O
    `oracle.py --kit` compara cada retângulo declarado com o frame buffer do
    console, halfword a halfword: o `TEX_A4` reproduz **exatas** a página
    (576, 384) e as paletas (0, 486) e (0, 488) nos dois states, e nenhum
    outro reproduz nenhuma delas. **Somar os sete retângulos decide nada** —
    a tela sobe três, os outros quatro diferem em milhares para todos os 105
    (12.138 contra 13.274). E a página (576, 256) tem um bloco de 48 linhas
    que a tela sobrescreve, igual nos dois states: quem nomeia o kit é o
    retângulo exato, não a menor soma.
78. **O confronto de cor desenha só a cabeça, então não testa o uniforme.** O
    `--render`/`--score` usa `--piece head` por decisão medida; com o kit
    ligado os números dele não se movem **nem um milésimo** — as três
    pontuações saíram idênticas na primeira tentativa de controle. Quem cobra
    o kit é o `--kit-control`, que desenha a figura **inteira** com o
    contêiner de outros dois times e mede a distância até a foto do jogo.
79. **Dois contêineres guardam registros no mesmo offset.** A chave da textura
    era `(offset, profundidade, CLUT)` e passou a incluir o contêiner: sem
    isso a página do corpo e a da cabeça colidem na tabela do viewer, e o
    desenho morre com `KeyError` numa chave que parece legítima.

80. **As bandas guardam a lista da tela ANTERIOR junto com a desta.** Andar
    uma cadeia de nós bem formados na RAM dá 74 pacotes plausíveis que não são
    desta tela — as faixas de lá ficam a 9 pixels, as daqui a 12. O que separa
    é a **figura**: a cor que o pacote declara contra o pixel que o console
    mostrou dentro do retângulo dele (`oracle.py --scenery`). Geometria
    plausível não é evidência de que o pacote foi desenhado.
81. **O texto da tela não está em lista nenhuma da RAM.** Varrida inteira, com
    quads, triângulos e sprites: só aparecem o painel, a ajuda, as faixas e o
    boneco. E o `--repaint` mostra que **tudo** é redesenhado a cada quadro —
    então o caminho de impressão manda os comandos sem deixar nó. Procurar o
    título e os glifos na display list é procurar onde não está.
82. **O `gpu_dump` do fork sai em `.zst`, e esta máquina não lê zstd.** Nem
    `zstandard` no Python, nem `zstd` no `PATH` — a mesma armadilha que o
    `savestate.py` registra. O caminho que funciona aqui é ler a RAM e a VRAM
    por MCP.
83. **Diff de tela entre "antes" e "depois" mede a caminhada, não o dano.** A
    primeira versão do `--pages` estragava uma página, andava seis quadros e
    comparava com o quadro anterior: **48 ladrilhos mudavam para toda página**,
    inclusive as que nada amostra. O boneco anda. O controle certo é **duas
    corridas do mesmo comprimento** a partir do state — uma com dano e uma
    sem —, e as duas sem dano têm de dar a mesma tela.
84. **O que o GPU tem em vigor responde onde o pacote não existe.** A página da
    fonte saiu do `get_gpu_state` numa parada do `SCREEN_GLYPH`, não de pacote
    nenhum. Quando a lista não tem o desenho, pergunte ao hardware o estado em
    que ele está desenhando.
85. **A cor mais comum de um degradê é decidida por empate.** Comparando o chão
    das regiões, a "mais comum" da caixa de ajuda saiu (8,64,96) no jogo e
    (0,40,64) na janela — os dois degradês indo da mesma cor à mesma cor. O
    pontilhado do console e as faixas de 5 bits decidem o empate. A mediana de
    cada canal é o meio do degradê dos dois lados, e poucas letras não a
    movem. E pintar um degradê num viewer OpenGL não se faz com `glClearColor`:
    o painel ficou 24 longe do jogo até ser pintado por `QPainter` por trás do
    boneco.
86. **Filtro de cor contra o quadro descarta todo pacote semitransparente.** O
    quadro mostra a mistura, não a cor declarada: a barra de título são três
    degradês **aditivos** e sumiram da varredura da armadilha 80 inteiros, com
    a conclusão "não está em lista nenhuma da RAM". Quem diz o que o quadro
    desenhou é a **lista que ele entrega ao GPU**, andada da cabeça que o jogo
    grava no DMA (`layout.GPU_LIST_SUBMIT`), não a RAM varrida com filtro.
87. **O estado do GPU numa parada não é o do próximo desenho.** A página em
    vigor na passada que desenha do `SCREEN_GLYPH` deu três valores em três
    corridas — (704,0), (704,256) e (832,256). Uma leitura só vira conclusão
    falsa com cara de medida; repita antes de escrever. **E os três estavam
    certos**: eram a seta, a fonte e a ajuda, três sprites diferentes, e a
    parada lia a página do último desenhado (quinta passada da LOOKS-TASK-31).
88. **Degradê de pacote não é vertical por definição.** A barra de título
    corre da esquerda para a direita. Pintar cada pacote como retângulo com
    gradiente de cima para baixo acerta o painel e a ajuda e erra o resto: o
    que o GPU faz é sombrear dois triângulos entre as cores dos cantos
    (`scene.furniture_picture`).
89. **Nó da lista não é comando.** A libgs põe o E1 que escolhe a página e o
    sprite no **mesmo** nó, e um leitor que classifica o nó pela primeira
    palavra vê uma troca de modo e nada mais. Foi assim que os 142 sprites da
    tela — texto, placa, setas, título — passaram quatro leituras como
    ausentes, com a conclusão "saem por escrita direta no GPU", que um
    watchpoint na porta de comando desmentiu: nada escreve nela. Parta o nó
    em comandos pelo comprimento que o código de cada um declara
    (`oracle.commands_of`) antes de perguntar o que ele desenha.
90. **Página sem registro no disco pode ser escrita pelo jogo — e a fonte
    pode ser do console.** O texto da ajuda são ladrilhos 16×16 da página
    (832,256), e nenhuma imagem de contêiner nenhum a cobre inteira — o
    `DATSEL3.BIN` tem um registro ali e bate só em parte. A CLUT é do disco;
    os texels o jogo os escreve na VRAM em tempo de execução, e **da ROM do
    console**: uma chamada de BIOS por caractere devolve um bitmap 16×15 em
    `0xBFC00000+0x80000` (LOOKS-TASK-39). "Não está no disco" é resultado,
    não falha do leitor, desde que o controle da comparação feche no resto —
    e aqui é mais que isso: **não está no disco porque não pode estar**, e
    procurar mais no disco era trabalho perdido.
100. **`attempt(nome, Exceção, lambda: ...)` não afirma nada.** No
    `harness`, quem exige recusa é `refuses(nome, fn, trecho, tipo)`; o
    `attempt(nome, fn, default)` **roda** `fn` e só reporta exceção
    inesperada. Escrito com a exceção no lugar do callable, ele constrói a
    exceção, devolve e passa verde: três controles do `anime.py` ficaram assim
    cinco dias sem poder ficar vermelhos (LOOKS-TASK-32). Controle que não
    pode falhar não é controle — a mesma lição da substituição que casa zero
    vezes (armadilha 90).
99. **Vigiar `ANIME_UNPACK` perde metade das passadas.** Dez variantes de
    desempacotamento dividem o dispatch `0x80011DA0`, e `0x80011D48` é uma
    delas: a passada que toma outra não para ali, e a captura volta **sem par
    em peça nenhuma** — é a razão das oito capturas postas de lado da
    LOOKS-TASK-26, não uma oscilação do emulador. Quem serve a todas é
    `layout.ANIME_BUILD` (o `jal` da `RotMatrix`), onde os ângulos já estão no
    scratchpad e `s0` ainda é o par: 520 de 520 cargas com par, contra 316 de
    520 na outra — e a falta tem forma, não é razão: **uma metade espelhada
    contígua**, 204 cargas seguidas, 17 das 34 passadas. Quem conta é
    `oracle.py --walk-watch [SLOT]`, igual nos dois slots
    (LOOKS-TASK-32, recontado na CORR-LOOKS-092).
98. **Contar a caminhada em quadros de vídeo dá um relógio que não repete.**
    A tela desenha a figura **uma vez a cada dois ou três quadros**, e o
    intervalo alterna sem período dentro de 500 quadros medidos (219 avanços
    de índice em 500, 0,438 por quadro). Em quadros, "o período" não existe;
    em **passadas de desenho** ele é exato: 34, e 77 quadros contados na
    corrida medida. Quem quiser um quadro nomeado conta passadas
    (`oracle.py --walk`, `anime.py --frame N`) e guarda o número de quadros
    como o que ele é — uma medição daquela corrida (LOOKS-TASK-32).
97. **Comparação ajustada não julga close-up.** O `fit_centre` do
    `--silhouette` alinha as duas caixas de tinta, e é o certo no corpo
    inteiro (a mira é o offset de desenho do GPU, que este ciclo não mediu).
    No close-up o que se erra **é a mira**: com ajuste, a nossa figura na
    câmera de `HAIR` marcou 11.995 pixels contra 2.116 da câmera de corpo
    inteiro — o ajuste centra o corpo inteiro no painel e mostra a barriga
    onde o jogo mostra a cabeça. Sem ajuste, com o eixo medido
    (`scene.panel_axis`) e a translação reassentada (`scene.rebased`), a
    mesma câmera marca 15% e a errada 2,5x isso (LOOKS-TASK-40).
96. **O `pc` de um watchpoint de VRAM não é quem escreveu.** A cópia de
    memória para a VRAM é feita por DMA, então o programa já andou quando o
    GPU toca a memória de vídeo: o `last_hit` da tira da ajuda deu
    `0x8003A950` em duas corridas seguidas — estável o bastante para parecer
    medida — e `0x8003F2F4` e `0x8010A910` nas duas seguintes. O que o
    watchpoint afirma é o **retângulo** e que a tecla o causou; quem escreve
    se lê no código (LOOKS-TASK-39). E ele reporta **um** acerto por tecla, o
    último do lote, não um por ladrilho: contar ladrilhos por ali dá 1 de 15.
91. **Sprite na lista não é sprite que desenha.** A "barra vazia ao lado da
    placa" é um sprite de 96×12 do `EDT_2D.BIN` com os 1.152 texels
    transparentes; o verde que ocupa o lugar é a caixa da camisa, do
    `DAT2D.BIN`. Quem conta os sprites de uma tela pela lista conta um que o
    jogador nunca vê — e a amostra de pixel do `--scenery --write` sai vazia
    para ele, que é o sinal (LOOKS-TASK-36).
92. **A seta diz o que a tecla faria, e isso não é o mesmo que o valor estar
    na ponta.** O ◀ e o ▶ ao lado do valor aparecem enquanto `Left` e `Right`
    mexem em algo — e no `DEFAUL`, de valor único, o ◀ aparece, porque `Left`
    leva o cursor ao rótulo (`Undo`). O x do ◀ é fixo por linha e não
    acompanha o texto (302, 384, 416, 424): derivá-lo da largura do valor erra
    em toda linha. Medido no walk do `--screen` (LOOKS-TASK-36,
    [`CORR-LOOKS-067`](/docs/tasks/looks/CORR-LOOKS-067.md)).
93. **O texto provisório da janela cobre pixel de sprite.** A fonte do Qt é
    mais larga que a do jogo, e o "CB" e o "SHIRT N" caem sobre texels da placa
    e das caixas que o jogo deixa à mostra: 16 e 18 de 359 amostras erravam
    por isso, com o decode igual ao jogo. O `looks_ui` julga os sprites com
    `--no-stand-in-text`; quando a fonte do jogo chegar
    ([`LOOKS-TASK-37`](/docs/tasks/looks/37-a-tabela-de-glifos.md)), a opção
    perde o motivo. **Chegou, e o motivo mudou de nome:** a placa e a camisa
    agora saem nos glifos do jogo, mas do x do objeto, e não de onde o jogo as
    centra. A opção virou `--no-unplaced-text` e vale até a
    [`LOOKS-TASK-38`](/docs/tasks/looks/38-o-alinhamento-dos-valores.md).
95. **A caixa de um texto muda com o texto, e a cor vem de dentro da
    string.** O objeto do `NAT` fica em x −80 com `Unknown` e em −104 com uma
    nação: uma caixa medida na carga alinha errado todo valor depois da
    primeira tecla. E o código de controle 13 grava três bytes como a cor do
    objeto — o `O.K.` do `DEFAUL` é cinza num objeto lavanda —, e essa cor
    **persiste nas linhas abaixo**. Quem lê a cor do byte 16 do objeto e para
    aí escreve um valor na cor errada, com todo o resto no lugar: foram 514
    pixels de 23.472 na primeira corrida do `--outside` (LOOKS-TASK-38).
94. **A rotina de um endereço pode morar em outra overlay.** A de glifo
    (0x8010BB04) fica depois do fim do `/SELECT8.BIN` (0x800E98F8), no
    **`/SELECTC.BIN`**, carregado em 0x800FC000. Quem a procurar no arquivo
    que já tem a regra de estatura não acha, e pode ler isso como "não está no
    disco". Arquivo de código se acha **por conteúdo**: 64 bytes da RAM
    procurados em todos os arquivos dos dois discos (LOOKS-TASK-37).
