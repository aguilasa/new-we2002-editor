---
id: WTE-TASK-19
title: "Descobrir os offsets que o Obocaman tem e nós não"
type: extração
category: dados
phase: 3
depends_on: ["WTE-TASK-06", "WTE-TASK-18"]
status: em andamento
---

# WTE-TASK-19: Os offsets restantes

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §4.2 e Fase 3 item 4.
- **Onde o método do projeto se prova.** A §4.2 diz: *sempre tentar o diff antes
  do decompilador*. Esta task é a aplicação pura disso — cada offset custa dois
  minutos de tela, contra horas de disassembly.

O `wte.exe` edita coisa que o `ed.exe` não edita: camisa 2D, bandeira, dados que
vêm de `.mcr`. Os offsets dessas regiões, se existirem, **não estão em
`Offsets.hpp`** — este repositório nunca precisou deles.

---

## Objetivo

Fechar a lista de regiões que o app Lazarus precisa endereçar.

### Método: diff dirigido

Para cada campo editável do original que a WTE-TASK-06 não resolveu:

1. Cópia limpa da ROM (**sempre cópia** — o editor grava in-place, e são 474 MB).
2. Abrir no Wine, mudar **um** campo, gravar, fechar.
3. `cmp` contra a cópia limpa.
4. O offset que mudou é o offset do campo.

### Cuidado que evita falso positivo

O `Load`+`Save` do original **não é idempotente**: ele troca os dois primeiros
cobradores de cada clube de ML (`OFS_KICKER`), porque `Load` lê o par trocado e
`Save` grava na ordem declarada. E o `Save` reconstrói as all-star a partir dos
links.

**Então o diff de controle vem primeiro:** abrir e gravar **sem editar nada**, e
registrar as faixas que mudam de graça. Só o que aparecer *além* dessas faixas é
efeito da edição.

Sem esse controle, toda medição vem contaminada e parece que campos aleatórios
se movem.

### Campos a cobrir

| Área | Origem |
|---|---|
| os 50 `OFS_*` não confirmados | WTE-TASK-06 |
| cor de camisa (casa/fora, menu) | `ficha_color`, `grabar_camisetaClick` |
| bandeira e cor de radar | `colorearClick`, novidade da v0.99 |
| aparência (cabelo, barba, `careto`) | WTE-TASK-08 |
| preço do jogador | `etiqprecioClick` |
| slots de ML livres | `ficha_movertodos` |

### Saída

Os offsets confirmados entram na **entrada do gerador** (WTE-TASK-16), nunca no
arquivo gerado.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/diff_dirigido.sh` | criar — automatiza copiar, editar, gravar, `cmp` |
| `wte/re/offsets.md` | modificar |
| `wte/re/offsets-novos.md` | criar — os que o `newWe2002` não tem |

---

## Critério de conclusão

- [x] Diff de controle (gravar sem editar) medido e registrado **antes** do resto
      — duas vezes: na europeia (1ª passagem) e na japonesa, onde o `ARRANQUE`
      do roteiro 09 é o controle e vem antes de toda ação medida
- [ ] Os 50 resolvidos ou declarados irrelevantes, um a um
      — **15 dos 50** resolvidos por execução (era 14; a 4ª passagem
      acrescentou `OFS_PLAYER_ATTR`, lido em `CALCULA_PRECO`). Os 35 restantes
      **não esperam mais imagem nenhuma**: esperam tela que ninguém clicou
- [x] As seis áreas da tabela cobertas
      — as seis exercitadas com um time carregado, na 4ª passagem. Quatro
      delas **não tocam a imagem**, e isso é medida, não falha de clique
- [x] Offsets novos documentados com a região que endereçam
- [x] Nenhuma medição feita sobre `roms/` diretamente
- [x] Commit no formato conventional, em inglês

**A task ainda não fecha, e o que falta mudou de natureza.** Até 2026-08-10 os
dois critérios abertos dependiam de dirigir o `wte.exe` além da tela de carga, e
isso estava bloqueado. O bloqueio caiu com a
[CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) — e não era "a imagem certa" no
sentido que a 3ª passagem supunha: com `roms/japanese-shift-jis.bin`, que já
estava no repositório, o editor passa da troca de time com zero violação de
acesso contra 49.749 na europeia. A causa é ponteiro sobrescrito pela carga do
time, não release faltando.

Sobrou **um** critério, e ele agora é trabalho comum: 35 `OFS_*` sem veredito
dinâmico, cada um esperando um controle que nenhum roteiro clicou. Não há
bloqueio; há tela.

## Log de Execução

### 4ª passagem — 2026-08-10, o bloqueio caiu e as seis áreas foram medidas

- **Executado em:** 2026-08-10 — **ainda parcial**, mas por outro motivo

- **Resumo do que foi feito:**

  A [CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) tinha diagnosticado o
  travamento e achado o contorno; esta passagem **usa** o contorno. Roteiro
  novo, [`09-areas-com-time.txt`](../../wte/tests/roteiros/09-areas-com-time.txt),
  que troca de time **primeiro** e só então exercita cada área — a ordem que o
  06 não podia ter. Sobre cópia de `roms/japanese-shift-jis.bin`: **60 faixas**,
  as seis áreas cobertas, e as duas réguas fechando (19 faixas do `cmp` contidas
  na união de 31 faixas de escrita do trace).

  Ganho de offset: **um**. `OFS_PLAYER_ATTR`, lido em `CALCULA_PRECO` — de 14
  para 15 dos 50. O resto das áreas endereça região que o `Offsets.hpp` não
  nomeia: **27 faixas sem dono** nesta sessão, duas delas acima do maior offset
  que o `newWe2002` conhece.

  **Quatro das ações não tocam a imagem**, e isso é resultado medido:
  `GRAVA_BARRAS`, `IGUALA_NOMES`, `TIME_TITULAR` e `FIM`. O `boton_barras2iso`
  chega a anunciar "Barras inseridas no jogo!!!" e não emite uma syscall sobre
  o arquivo — as 11 linhas que caem na janela dele são a cauda da carga do time
  (8 ms depois da marca, todas `_llseek` sem `read`/`write`). A leitura mais
  provável, e que a fase 4 vai confirmar ou derrubar: ele só grava o que foi
  alterado, e nada foi.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/tests/roteiros/09-areas-com-time.txt` | criado — time primeiro, as seis áreas depois |
  | `wte/tools/analisar_io.py` | `unir_faixas()` nova; a conferência das réguas passou a ser contra a **união**; seção nova no `offsets-novos.md` |
  | `wte/tools/test_analisar_io.py` | +5 testes: a união e a conferência com faixa plantada |
  | `wte/tools/dump_offsets.py` | a prosa da coluna **medido** dizia que a sessão não passava da tela de carga |
  | `wte/re/io-medido.tsv` | +64 linhas, imagem `japanese-shift-jis.bin` |
  | `wte/re/offsets-novos.md`, `wte/re/offsets.md` | regerados |
  | `wte/tests/roteiros/README.md` | o 09, e as duas armadilhas de dirigir diálogo |

- **Problemas encontrados:**

  **Um defeito do instrumento, e ele deu falso alarme.** A conferência das duas
  réguas exigia que cada faixa do `cmp` coubesse **numa** faixa de escrita do
  trace. O `wte.exe` grava nome **byte a byte**, e a marca do roteiro corta a
  sequência no meio: os 23 bytes de `3067404` saíram 22 em `CALCULA_PRECO` e 1
  em `ABRE_JOGADOR`. Duas faixas contíguas, cobertura completa — e o script
  acusou "o trace perdeu syscall; a atribuição por ação não vale", que é a
  mensagem que manda parar tudo. Agora a conferência é contra a **união**, com
  teste dos dois sentidos: faixa encostada junta, faixa com um byte de buraco
  não junta.

  É o **terceiro** defeito deste mesmo instrumento (os outros dois estão na 3ª
  passagem), e os três têm a mesma assinatura: número que muda em silêncio, ou
  alarme que soa sem causa. A lição é a mesma — a conferência entre as duas
  réguas é o que os pega, e ela precisa estar certa antes de qualquer número.

  **Dirigir diálogo modal custou três sessões exploratórias.** Cada botão de
  área abre uma janela diferente, e deixar qualquer uma aberta engole todos os
  cliques seguintes. Pior: `xdotool windowkill` numa delas **mata o processo
  inteiro** — a VCL não sobrevive à destruição da janela por fora. Fechar é
  clicando no botão, e as coordenadas de cada um estão no `README.md` dos
  roteiros.

  **O que ficou pendente:** os 35 `OFS_*` sem veredito dinâmico. Eles não
  esperam mais imagem — esperam controle clicado. Os candidatos naturais são as
  telas que este roteiro só abriu (a ficha do jogador, com cabelo/barba/
  `careto`) e as que ele não abriu (`ficha_movertodos`, `estrategia`, a
  gravação de camisa e de `.mcr`, que abrem diálogo de arquivo).

### 3ª passagem e anteriores — 2026-08-10

- **Executado em:** 2026-08-10 — **parcial, e o bloqueio continua**
  (três passagens no mesmo dia: a primeira mediu; a segunda refutou a hipótese
  do tamanho e consertou dois defeitos do instrumento; a terceira perguntou ao
  Wine **onde** o travamento cai, e a resposta mudou a natureza do bloqueio)

- **Resumo do que foi feito:**

  A régua trocou, e essa é a decisão da execução. O enunciado pede `cmp` depois
  de editar um campo; `cmp` só enxerga **escrita de valor diferente**, e o
  editor do Obocaman grava, na maior parte das áreas, exatamente o que leu —
  ali um `cmp` limpo não distingue *não gravou* de *gravou igual*. Pior: `cmp`
  não vê **leitura** nenhuma, que é a metade da resposta que diz onde os 50
  `OFS_*` ausentes moram. Então o `wte.exe` passou a rodar sob `strace`, e cada
  `_llseek` + `read`/`write` virou uma faixa `(offset, tamanho)`. O `cmp`
  continua, como segunda régua independente.

  **O diff de controle veio primeiro, e ele é maior do que a task supunha.**
  Abrir a imagem, sem tocar em nada, já grava **14.337 bytes em 8 faixas** —
  sete setores inteiros (5 a 11, byte 24 ao 2071) mais um byte solto em
  1.921.862. Não é o `Load`+`Save` não idempotente do `ed.exe`: aqui não há
  `Save` nenhum, o `wte.exe` escreve **durante a carga**, antes de a janela
  principal aparecer. As duas réguas concordam byte a byte: as sete faixas do
  `cmp` estão contidas nas oito do trace.

  Resultado: **28 `OFS_*` confirmados por execução**, dos quais **14 eram
  `ausente`** na classificação estática da WTE-TASK-06 — inclusive dois `H3`,
  a classe que a WTE-TASK-06 marcou como "sem base derivável"
  (`OFS_KIT_PREVIEW` e `OFS_FLAG_COLOURS`). E **13 faixas que nenhum `OFS_*`
  explica**, três delas casando com candidatos que a WTE-TASK-06 extraiu do
  `.text` (`2736694`, `1921862`, `12544268`), e uma em **14.368.636** — 1,8 MB
  **acima** do maior offset que o `newWe2002` conhece.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/tools/diff_dirigido.sh` | criado — copia a ROM, dirige o `wte.exe` sob `strace` por roteiro, `cmp` contra a cópia limpa |
  | `wte/tools/analisar_io.py` | criado — trace → faixas, e faixas → `offsets-novos.md` |
  | `wte/tools/test_analisar_io.py` | criado — 15 testes, parser com linha plantada |
  | `wte/tests/roteiros/06-diff-dirigido.txt` | criado |
  | `wte/re/io-medido.tsv` | criado — a evidência |
  | `wte/re/offsets-novos.md` | criado, **gerado** |
  | `wte/re/offsets.md`, `wte/tools/dump_offsets.py` | coluna **medido** na tabela dos 50 |
  | `wte/re/io-conteudo.tsv` | criado — amostra do conteúdo de cada faixa lida |
  | `wte/tools/analisar_crash.py` | criado — log de exceção do Wine → `re/crash.md`; resolve o endereço de falha contra a tabela de exportação do módulo e acha os sítios de chamada no `.exe` |
  | `wte/tools/test_analisar_crash.py` | criado — 14 testes: parser com linha plantada, e o par de roteiros |
  | `wte/re/crash.md` | criado, **gerado** |
  | `wte/re/crash-sessoes.tsv`, `crash-seh.tsv`, `crash-modulos.tsv` | criados — a evidência |
  | `wte/tests/roteiros/07-controle-sem-time.txt`, `08-so-troca-de-time.txt` | criados — o par que torna a atribuição uma medida |
  | `wte/tools/README.md`, `wte/tests/roteiros/README.md` | atualizados |

- **Problemas encontrados:**

  **O bloqueio, e ele não é desta task só: o `wte.exe` morre ao carregar um
  time.** `SIGSEGV`/`SEGV_MAPERR` em `NULL`, logo depois de ler os dados do
  primeiro time selecionado, com as duas ROMs deste repositório — e com
  qualquer time, não só o primeiro.

  **A primeira hipótese estava errada, e a correção é o achado da retomada.**
  O editor avisa na abertura que o tamanho não corresponde — quer 474.431.328
  bytes exatos, e a European Deluxe tem 474.784.128. A diferença é
  **352.800 = exatamente 150 setores** de 2352, toda ela na cauda, muito depois
  do maior offset conhecido. Truncar a cópia para o tamanho exato e repetir o
  roteiro: **o aviso some, e mais nada muda** — o mapa de I/O sai idêntico
  faixa a faixa, e o app cai no mesmo ponto. Tamanho não era a causa; o que a
  hipótese explicava era o aviso, e o aviso nunca foi o problema.

  O que sobrou como pista foi **conteúdo**: a última leitura antes do
  `SIGSEGV` são 512 bytes em `14368636`, e amostrando 64 bytes ali esta release
  tem **4 não-zero** — contra 32 a 64 em toda outra faixa que o editor lê. Isso
  parecia diagnóstico e não era: **leitura vizinha de uma falha é
  correlação**, e o `analisar_io.py` não tem como distinguir as duas coisas
  porque só enxerga I/O.

  **A causa foi medida na terceira passagem, e não é a imagem.** Basta rodar a
  mesma corrida com `WINEDEBUG=+seh,+loaddll`: o Wine diz qual instrução
  faltou e onde cada módulo foi carregado. Resultado, em
  [`crash.md`](../../wte/re/crash.md):

  - a violação de acesso cai em `0x005f5ea0`, que é o `vcl60.bpl`
    **realocado** para `0x005f0000` — sem a linha do `+loaddll` o endereço não
    cai em módulo nenhum e a pista morre ali;
  - RVA `0x5ea0` = `Graphics::TFont::SetSize` + 8, com `eax` zero e o endereço
    que faltou em `0x1c`: o `this` chegou **nulo**;
  - o sítio de chamada é `0x0040b1ac` — identificado pelo argumento, porque o
    C++Builder passa o primeiro parâmetro em `EDX` (§8.1) e ali `EDX` valia 8,
    o imediato que só um dos dois sítios carrega;
  - os dois sítios estão numa rotina privada em `0x0040b188` que procura um
    controle por `FindComponent("dorsal" + N)` e mexe na fonte dele. Quem a
    chama: `lista_equiposChange`, `lista_jugadores_1Change`, `dorsalClick` e
    `dorsalMouseDown`, todos do `MainForm`.

  **A falha é de estado de interface, não de leitura da imagem.** Falta o
  objeto, não o byte.

  A atribuição "quem mata é a troca de time" também deixou de ser leitura de
  tela: os roteiros **07** e **08** são iguais linha a linha até `= ARRANQUE` e
  o 08 tem duas linhas a mais, que trocam o time. Medido: **0 violações de
  acesso no 07, 309 no 08**. O roteiro 06 não serve de par — ele clica as oito
  áreas antes, o que são oito variáveis a mais.

  O pedido, então, deixou de ser "a release de 474.431.328 bytes" e passou a
  ter **dois caminhos**: uma release cuja região em `14368636` seja populada,
  ou descobrir por que o controle não existe — e este segundo é pergunta da
  fase 4 sobre um handler que já tem nome, endereço e formulário.

  O custo maior não é aqui. O `wte.exe` é o **oráculo comportamental** do
  projeto (§4.2 do plano), e a WTE-TASK-22 monta o gate golden em cima dele.
  Um oráculo que não passa da tela de carga não sustenta gate nenhum. Ficou
  registrado nas Pendências externas do `progresso.md`.

  **Dois defeitos do próprio instrumento, que mudavam número em silêncio.** Os
  dois só apareceram porque a segunda régua passou a ser conferida de verdade
  (`analisar_io.py --conferir`), e o script prometia essa conferência desde o
  primeiro commit sem executá-la:

  1. **a marca era número de linha**, e o `strace` bufferiza o log — `wc -l` no
     instante da marca fica atrás das syscalls que já aconteceram, e a faixa ia
     para a ação errada. Virou relógio (`strace -tt`);
  2. **o parser ignorava syscall partida** em `<unfinished ...>` +
     `<... resumed>`, que sobre a imagem é a **maioria** delas — 1.529 numa
     sessão só. Duas faixas mudavam no arquivo sem aparecer no trace.

  Com os dois consertados, as duas réguas fecham: as 7 faixas do `cmp` cabem
  nas 8 faixas de escrita do trace, nas duas sessões.

  **Três diagnósticos custaram tempo e viraram nota escrita**, porque os três
  se disfarçam de "o clique parou de funcionar":

  1. a janela **sobrevive** ao processo — o `wineserver` a mantém mapeada —,
     então a tela continua parecendo viva depois do `SIGSEGV`. Confira
     `ps -o stat` procurando `Z`;
  2. a lista suspensa de um `TComboBox` fica **mapeada** depois do clique no
     item e segura o ponteiro; todo clique seguinte morre nela, mesmo num botão
     do outro lado da janela. Trocar de item pelo teclado (`Down`) evita;
  3. um terceiro método tentado — encher a cópia com `0xA5` depois do Load e
     ver o que sobrevive à gravação — **derruba o app**: ele não lê tudo no
     Load, lê sob demanda. Está registrado no `offsets-novos.md` para que
     ninguém repita.

  **Medida negativa que também é resultado:** os botões de gravação por área
  (`boton_barras2iso`, `boton_nombres2iso`, `colorear`, `grabar_camiseta`,
  `grabar_memory`) não escrevem byte nenhum enquanto não houver time
  selecionado. Isso não é "o clique não chegou": o mesmo roteiro reabre o
  splash `Sobre...` por clique, com a janela mapeando.

  **O que ficou pendente**, e volta quando o oráculo passar da tela de carga
  por qualquer dos dois caminhos: as seis áreas da tabela, os 36 `OFS_*`
  restantes, e o diff dirigido *stricto sensu* — editar um campo e gravar. A
  ferramenta e o roteiro já estão prontos para isso.

  **Lição que vale para o resto do projeto:** hipótese barata deve ser testada
  antes de virar bloqueio publicado. Foram duas seguidas — o tamanho da imagem
  e a região vazia —, as duas escritas como causa no `progresso.md`, as duas
  derrubadas por um experimento de minutos. A terceira só apareceu porque a
  pergunta mudou de "que dado falta" para "que instrução faltou", e essa o Wine
  responde de graça.
