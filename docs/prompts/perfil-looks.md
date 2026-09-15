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
   errado e é o par de zeros que separa grupos (§1.4). Foi o primeiro tropeço da
   sessão de investigação.
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
16. **Percentual de semelhança sem o nulo ao lado não se lê.** Na folha de 4
    bits deste arquivo um índice cobre um quinto dos texels, então chutar esse
    índice em toda parte já dá ~16%. Foi o que quase fez "9,2% igual" passar por
    "diferente" e "85,7%" por "parecido", quando os números diziam
    *não relacionado* e *é o mesmo arquivo editado*. O
    `atlas.py --compare` imprime o nulo em cada linha por isso.

---

## As fontes de verdade binárias

| o que | onde | quem é fiel |
| --- | --- | --- |
| geometria | `/BIN/EDT_MOD.BIN`, `/BIN/MODEL.BIN` | igual nos dois discos |
| textura e paleta | `/BIN/DAT2D.BIN` | **só o japonês** |
| registros de jogador | `/SELECT.BIN` +157.164, 1.242 × 12 B | japonês (a conferir na 13) |
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
| `looks_image` | `WE2002_LOOKS_IMAGE` (77 sem ela) | `python tools/looks/modelfile.py --check-image` | `ctest -R looks_image` | CORR-LOOKS-012 |
| `looks_ui` | venv + display (77 sem eles) | — (nasce na 16) | `ctest -R looks_ui` | LOOKS-TASK-16 |
| *(sem alvo ainda)* | `WE2002_LOOKS_IMAGE` (77 sem ela) | `python tools/looks/texture.py --check-image` | — | LOOKS-TASK-10 |
| *(sem alvo ainda)* | `WE2002_LOOKS_IMAGE` (77 sem ela) | `python tools/looks/atlas.py --check-image` | — | LOOKS-TASK-11 |
| *(sem alvo ainda)* | `WE2002_LOOKS_IMAGE` (77 sem ela) | `python tools/looks/skin.py --check-image` | — | LOOKS-TASK-12 |
| *(sem alvo ainda)* | as duas variáveis, os dois states e o emulador | `python tools/looks/oracle.py --palettes` | — | LOOKS-TASK-12 |

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

Hoje são **1 passed, 1 skipped**; depois da LOOKS-TASK-16, **1 passed,
2 skipped**.

**Antes da LOOKS-TASK-06 não há gate**, e isso é esperado: as tasks 01 a 05 se
verificam pela saída da ferramenta, copiada para o Log. Depois dela, toda task
fecha com o `selftest` verde.

**E nenhum alvo pode passar sem ter medido.** Alvo que passa imprimindo um
`note:` sobre o que não mediu é a armadilha que o `mcr_ui` pagou; aqui o
contrato é: mediu e passou, ou pulou com 77.

---

## Arquivos quentes deste ciclo

- `tools/looks/layout.py` — todo endereço passa por aqui. Duas tasks editando
  este arquivo ao mesmo tempo se atropelam.
- `tools/pes2/bin_archive.py` — **arquivo de outro projeto**. A LOOKS-TASK-10
  pode precisar mexer nele; se mexer, o `pes2_selftest` tem de continuar verde,
  e isso entra no critério de conclusão, não na esperança.
- `tests/CMakeLists.txt` — os três alvos entram aqui, junto com os dos outros
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
  prosa da task. Para a 14, a pergunta que decide: **cada linha da tabela de
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
