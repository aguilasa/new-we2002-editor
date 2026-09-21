# Armadilhas do ciclo `looks` — da 86 em diante

As armadilhas 1 a 85 estão no
[`perfil-looks.md`](/docs/prompts/perfil-looks.md), na seção "Armadilhas
medidas neste ciclo". Este arquivo guarda da 86 em diante, desde a
[`LOOKS-TASK-36`](/docs/tasks/looks/36-os-sprites-estaticos.md), quando o perfil
chegou ao limite de tamanho do rito (`[profile].max_kb`). O rito lê este
arquivo **por busca**, não por inteiro, então cada entrada nomeia os caminhos
e os termos que a disparam.

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
90. **Página sem registro no disco pode ser escrita pelo jogo.** O texto da
    ajuda são seis ladrilhos 16×16 da página (832,256), e nenhuma imagem de
    contêiner nenhum a cobre inteira — o `DATSEL3.BIN` tem um registro ali e
    bate só em parte. A CLUT é do disco; os texels, o jogo os escreve na VRAM
    em tempo de execução. "Não está no disco" é resultado, não falha do
    leitor, desde que o controle da comparação feche no resto.
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
    perde o motivo.
