---
id: MCR-TASK-17
title: "Onde o option file guarda os times secretos e a opção de Master League no modo exibição"
type: verificação
category: engenharia-reversa
phase: 5
depends_on: ["MCR-TASK-09"]
fonte_de_verdade: "/docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md §Critério de conclusão"
status: concluído
---

# MCR-TASK-17: o mapa dos desbloqueios

## Contexto

- **Pedido do usuário em 2026-09-10**, depois do fechamento do ciclo. Como todo
  escopo da Fase 5, **a fonte de verdade é este arquivo** — o plano descreve a
  v1 sobre elenco, formação e dorsais, e não menciona opção de jogo nenhuma.
- **Escopo: descoberta e mapeamento, e nada além disso.** Nenhuma entrada em
  `layout.py`, nenhum campo na tela, nenhum caminho de gravação. Marcar e
  desmarcar essas opções na ferramenta é o objetivo *seguinte*, e vai ser task
  própria — esta entrega o endereço e o significado de cada bit, que é o que
  aquela vai precisar citar.

### O que se quer localizar

O `we2002-ptbr-first-boot.mcr` traz habilitados **nove times secretos**:

> Euro A.S., World A.S., Class. England, Clas. France, Clas. Nether,
> Class. Italy, C. Germany, Clas. Brazil e Cl. Argentina.

E traz habilitada a opção de **escolher os times da Master League no modo
exibição**.

São dez coisas ligáveis. Onde elas moram no option file é a pergunta.

### As fixtures, e por que elas bastam

Três cartões, os três versionados em [`../../../mcr/`](../../../mcr/README.md),
os três com `BISLPM-87056WEW-OPT` nos blocos 1–2:

| Cartão | Estado | md5 |
|---|---|---|
| `we2002-english-first-boot.mcr` | primeira execução, **nada desbloqueado** (a presumir — ver o critério) | `72626c3b…` |
| `we2002-ptbr-first-boot.mcr` | primeira execução, **os dez ligados** | `e2de493f…` |
| `pro-evolution-soccer-2.29939.gme` | de terceiro, *"All teams unlocked. All team names edited to english."* | `3fb86323…` |

O terceiro é o que dá o segundo eixo: ele foi desbloqueado por outra pessoa, em
outra máquina, a partir de outro caminho. O que os três concordarem não é
coincidência de build.

### O que já está medido, 2026-09-10

Três diferenças, todas restritas aos blocos 1–2 (a cadeia declarada; o resto do
cartão é `0xFF` de preenchimento do DuckStation):

| Confronto | Bytes diferentes |
|---|---|
| english × ptbr | **33** |
| english × 29939 | **817**, em 161 faixas |
| **english difere dos dois, e os dois concordam** | **7** |

Os sete:

```
0x02184  en=00  ptbr=ff  29939=ff
0x02185  en=00  ptbr=ff  29939=ff
0x043df  en=00  ptbr=ae  29939=ae
0x048ae  en=00  ptbr=b1  29939=b1
0x049da  en=00  ptbr=b0  29939=b0
0x049db  en=00  ptbr=c5  29939=c5
0x04ca0  en=00  ptbr=db  29939=db
```

**`0x02184..0x02185` é o candidato, e os outros cinco provavelmente não são.**
Dois motivos, e os dois são de forma:

1. `00 00` contra `ff ff` é a assinatura de um campo de flags que passou de
   nenhum para todos. Dezesseis bits acomodam as dez coisas da lista com folga.
2. Os outros cinco caem na **região da tabela de nomes**, e os valores (`ae`,
   `b1`, `b0 c5`, `db`) são exatamente os bytes que aparecem no confronto
   english × ptbr **deslocando nomes de um byte** — `Ylonen`, `Kovtun`,
   `De Anda`, medidos no [`README`](../../../mcr/README.md) de `mcr/`. Ali as
   duas builds não guardam a mesma lista, e isso não tem a ver com desbloqueio.

Candidato é candidato. O critério abaixo manda confirmar, não assumir.

### A pergunta que vem antes de todas

**O desbloqueio está no cartão ou na ROM?** A PT-BR pode ser um romhack que já
nasce com os times abertos, e nesse caso o option file não guarda flag nenhuma
e o mapa não existe. O confronto acima **não** decide isso: ele mostra que os
bytes diferem, não que o jogo os lê.

O teste que decide é cruzado, e é barato:

- ROM PT-BR **com o cartão inglês** — se os times somem, quem manda é o cartão;
- ROM inglesa **com o cartão PT-BR** — se os times aparecem, quem manda é o
  cartão.

Concordando, está respondido. Discordando, o achado é esse, e vale mais que o
mapa.

#### Respondida em 2026-09-10, pelo usuário: **está no cartão**

A ROM **inglesa** aberta com o `we2002-ptbr-first-boot.mcr` mostrou **todas** as
opções extras. O jogo lê os desbloqueios do option file, e o campo existe.

O que isso ainda **não** diz: se a ROM PT-BR também os liga por conta própria — a
outra metade do cruzado, que ficou por fazer e não bloqueia o mapa. Nem qual
byte é: a prova é de que o cartão manda, e não de onde no cartão.

#### E o save tem verificação de integridade — medido no mesmo dia

O cartão inglês com **só** `0x02184..0x02185` trocado de `00 00` para `01 00`,
e mais nada, foi **recusado pelo jogo** ao carregar o option file. O
`cli.py info` o dá por íntegro (`bad checksums none`) porque os 16 checksums
que ele confere são os **do diretório**, e a escrita foi no bloco 1, dentro do
save.

Três consequências, e elas mudam o método desta task:

1. **Editar o campo à mão e ver o resultado na tela não funciona.** O critério
   que dizia "gravar um valor intermediário e ver um subconjunto dos times"
   está morto como escrito; o que resta dele é a intenção.
2. **O caminho que resta é deixar o jogo recalcular.** Partir de um cartão que
   carrega, mudar **uma** opção dentro do jogo, salvar, e comparar. O
   diferencial entrega duas coisas de uma vez: qual bit é a opção, e **quais
   bytes são a verificação**, porque estes se mexem em toda gravação.
3. **A verificação também precisa ser mapeada**, ou o objetivo seguinte —
   marcar e desmarcar na ferramenta — é inalcançável: gravar o bit sem
   recalcular produz exatamente o erro acima.

Três bytes avulsos são os primeiros candidatos a ser a verificação, por não
terem forma de dado e por diferirem entre os três cartões:

```
0x02102  en=d9  ptbr=8f  29939=84
0x0216d  en=e8  ptbr=a0  29939=a8
0x02202  en=8b  ptbr=4d  29939=ed
```

**Não é soma de bytes de uma faixa contígua simples** — medido: os deltas entre
inglês e PT-BR são `b6`, `b8` e `c2`, e nenhuma das faixas plausíveis
(`0x2000..0x2102`, `0x2103..0x216d`, `0x2186..0x2202`, e as duas maiores)
reproduz nenhum deles. Ou a faixa é outra, ou não é soma.

**E isto toca a MCR-TASK-13.** O veredito do console ficou "não obtido", e a
pergunta dele era se um cartão com dado gravado fora da cadeia declarada é
válido para o jogo. Agora se sabe que dado gravado **dentro** da cadeia, sem
recalcular a verificação, é recusado. Se a mesma verificação cobre a área de
jogador — que é onde o port e o editor do Obocaman escrevem — é pergunta
aberta, e agora testável: gravar pela ferramenta e abrir no jogo.

#### A verificação: **um byte de soma por bloco**, medido em 2026-09-10

Cinco arquivos novos, todos gravados **pelo jogo** e portanto válidos, a
partir do cartão PT-BR — `a1`, `a2` (salvar sem mudar nada, duas vezes),
`b-nome` (uma letra de um nome), `c-opcao` (várias opções) e `c-opcao2`
(`c-opcao` **mais** a câmera, e só ela). São **três padrões distintos**: `a1` e
`a2` saíram idênticos ao PT-BR de partida, que é o achado do parágrafo
seguinte. Ficam em `$(WORK)/cards/`, pelo alvo
`make we2002-card-snap LABEL=<nome>`.

**A gravação é determinística.** `a1`, `a2` e o `we2002-ptbr-first-boot.mcr`
são o mesmo md5 — salvar sem mudar nada não move um bit. Não há relógio nem
contador no save, então todo diff daqui em diante é sinal.

A regra, que reproduz **seis cartões distintos** — os três padrões novos
(`b-nome`, `c-opcao`, `c-opcao2`), os dois `first-boot` e o `29939`, o único de
terceiro:

```
byte(0x02102) = ( soma de 0x02044..0x02186, exceto ele próprio ) + 0x8a   (mod 256)
```

`k = 0x8a` nos seis. A busca que a achou é de faixa consistente com
todos os cartões ao mesmo tempo, com `a` no bloco 1 e `b` até o fim do bloco 2.
Ela não devolve uma faixa: devolve **milhares** — 23.875 para `0x02102` e
27.250 para `0x02202` —, e o que se mede é o **limite inferior** de cada uma:

| candidato | faixas consistentes | início mínimo | fim mínimo |
|---|---:|---|---|
| `0x02102` | 23.875 | `0x02044` | `0x02186` |
| `0x02202` | 27.250 | `0x02186` | `0x04e30` |

**Nenhuma faixa consistente começa antes de `0x02044`** — o byte logo depois do
campo de alta entropia —, e nenhuma das de `0x02202` começa antes de `0x02186`,
onde a anterior termina. São blocos encadeados, cada um com seu byte de soma
dentro. É esse limite inferior que fixa o achado que interessa: **o campo de
alta entropia fica fora da soma**, e é o que permite deixá-lo zerado.

E a janela da busca é parte do resultado: com `b < 0x02400` o `0x02202` dá
**zero** faixas, e só aparece quando `b` alcança o fim do bloco 2. Uma busca
curta conclui, errado, que o segundo byte não é soma.

E o inverso vale registrar: `0x0216d` e `0x02205` dão **zero** faixas
consistentes. Não são verificação — são dado. O `0x0216d` muda quando uma opção
muda, o que é o que se espera de um byte de opção.

#### O campo de alta entropia `0x02035..0x02043`, 15 bytes

Zero nos dois cartões de primeira execução — o inglês e o PT-BR — e o jogo
**aceita** os dois. (`a1`, `a2` e `ptbr-original` também estão zerados, e são
esse mesmo cartão PT-BR.)
Preenchido com valor de alta entropia em toda gravação posterior que mudou
algo (`b-nome`, `c-opcao`, `c-opcao2`, `29939`). Não foi identificado. O que
importa para o objetivo é que **zero é aceito**, então um cartão editado a
partir de um `first-boot` pode deixá-lo zerado.

#### O que o `c-opcao2` isolou de brinde

Ele foi gravado **sobre** o `c-opcao`, não a partir do zero, e **no jogo mudou
só a câmera**. No cartão mudaram **17 bytes**:

```
0x02104   c-opcao=03   c-opcao2=02      <- a câmera
0x02102   c-opcao=ad   c-opcao2=ac      <- a soma, acompanhando
0x02035..0x02043   15 bytes             <- o campo de alta entropia
```

Um byte de enum e a soma andando junto — é a mesma forma que o campo de flags
tem de ter, e é o que faz deste par o isolamento útil. Os outros 15 são o campo
de `0x02035`, que muda por inteiro em **toda** gravação que mudou algo; o par é
também a segunda amostra desse comportamento, e é por isso que "só a câmera"
vale para a tela e não para os bytes. Quem for escrever o gravador precisa
saber que trocar um enum move dois bytes **que se sabe reproduzir** e quinze
**que não** — e que zero é aceito num cartão de primeira execução.

#### O campo confirmado: `0x02184..0x02185`, um bit por opção

Medido em 2026-09-10. Cartão inglês de primeira execução, `0x02184..85` posto
em `01 00` e `0x02102` recalculado pela regra acima (`d9` → `da`), mais nada:
o jogo **carregou** e mostrou **um** time extra, o **Euro A.S.**

Duas coisas de uma vez, e é por isso que este era o teste a fazer:

1. **A regra da soma está certa.** Carregar é a prova — o mesmo cartão sem o
   recálculo tinha sido recusado.
2. **`0x02184..0x02185` é o campo, e é bitmap.** `bit 0 = Euro A.S.`, que é o
   primeiro da lista do enunciado. Não é enum nem contador.

O resto do mapa sai por **teste em grupo**: com dez bits e o nome de cada opção
visível na tela, quatro cartões bastam. O teste `t` liga os bits cujo índice
tem o bit `t` — `t0 = 0x02aa`, `t1 = 0x00cc`, `t2 = 0x00f0`, `t3 = 0x0300` —, e
a assinatura de um nome (em quais testes ele apareceu) **é** o índice do bit
dele. O Euro A.S. não deve aparecer em nenhum dos quatro, que é o controle:
índice 0 não tem bit ligado em assinatura nenhuma.

---

## Objetivo

Dizer, com valor medido, **onde** cada uma das dez opções está gravada no
option file, e **qual valor** significa ligado.

---

## Critério de conclusão

- [x] **O cartão inglês é mesmo o estado "travado".** Ele é chamado assim aqui
      por ser de primeira execução, e isso é inferência. Abrir a ROM inglesa
      com ele e olhar a lista de times fecha a questão — e se ele já vier com
      algo aberto, todo o resto muda de leitura.
- [x] **O teste cruzado acima**, com as duas conclusões escritas. Se o
      desbloqueio for da ROM e não do cartão, a task fecha aí, com a evidência
      — e é resultado, não falha.
- [x] **`0x02184..0x02185` confirmado ou derrubado.** Confirmar é mostrar o
      jogo lendo: gravar um valor intermediário num cartão de trabalho, abrir,
      e ver **um subconjunto** dos times na tela. `ff ff` contra `00 00` sozinho
      não distingue "flags" de "dois bytes que mudaram junto".
- [x] **Um bit por opção, nomeado.** O experimento discriminante é
      diferencial e in-game: partir de um cartão sem nada aberto, ligar **uma**
      coisa, salvar, e comparar. Repetido, dá a tabela `bit → time`. Onde o
      jogo não deixar ligar uma sozinha, diga isso e mostre o que deu para
      isolar.
- [x] **A opção de Master League no modo exibição** localizada com o mesmo
      método. Ela pode não estar no mesmo campo dos times, e não há motivo para
      supor que esteja.
- [x] **O mapa vai para [`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md)**,
      arquivo novo: endereço, máscara, o nome de cada opção como o jogo a
      escreve na tela, e o comando que reproduz cada medição. É o papel que o
      [`wte/re/mcr.md`](../../../wte/re/mcr.md) faz para os 17 destinos — a
      task que for implementar isso cita esse arquivo, e não este.
- [x] **Hipótese descartada fica registrada, com o motivo.** Os cinco bytes da
      tabela de nomes são a primeira candidata a cair; se caírem, o arquivo diz
      por quê, para ninguém refazer a conta.

---

## Armadilhas

- **As duas ROMs escrevem o MESMO arquivo de cartão.** Ambas declaram
  `BOOT = cdrom:SLPM_870.56`, e o DuckStation nomeia o cartão pelo título:
  `World Soccer Winning Eleven 2002 (Japan)_1.mcd`. Uma corrida sobrescreve o
  cartão da outra. `make we2002-play-fresh` e `make we2002-ptbr-play-fresh`
  arquivam o anterior em `$(WORK)/optionfiles-<data>/` antes — use-os, e
  guarde cada cartão intermediário com nome próprio assim que ele nascer.
- **`mcr/` é diretório de originais.** O `mcrio.check_destination` o recusa
  como alvo de escrita, ao lado de `roms/`. Todo experimento é sobre cópia.
- **Cartão de experimento não se versiona por reflexo.** Os três de `mcr/` são
  exceção medida, e a seção "Versionamento" do README de lá diz o critério. Um
  cartão a mais entra se ele for estímulo de uma medição que os três não
  conseguem ser.
- **O jogo roda fora da tela do usuário** — `:98`, regra do repositório. A
  exceção com nome próprio é `we2002-play`/`we2002-ptbr-play`, que existem para
  as sessões em que o usuário joga. Um experimento que precise de partida é
  dele, não do gate.
- **Ler nome de entrada sem olhar o estado inventa save que não existe** — a
  mesma armadilha que o README de `mcr/` registra para `N.Kanu` e
  `BASCUS-94254PRO-00`.

---

## Log de Execução

**Executado em:** 2026-09-10

### O mapa

Está em [`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md), que é o
entregável. Resumo: `0x02184..0x02185`, dezesseis bits little-endian, bits 0–7
para o Euro A.S. e as sete seleções *Classic*, **bit 8 para os times da Master
League no modo exibição** e **bit 10 para o World A.S.** Bit 9 e bits 11–15 não
fazem nada observável.

### Duas linhas que a forma do mapa não deixava adivinhar

O bit 8 **não é time**, e mora no meio da faixa deles; o World A.S. **não é
vizinho** do Euro A.S. Quem as pegou foi o **controle** do teste em grupo: o
World A.S. não apareceu em nenhuma das quatro sondas, o que daria assinatura
`0000` — índice 0, já medido como Euro A.S. A contradição era visível, e sem
ela o mapa teria sido lido como "bits 0..8 são os nove times", errado em duas
linhas.

Dez bits em **nove boots**: quatro de teste em grupo, três de busca binária
sobre os bits altos, um de âncora (`01 00`) e um de confirmação ponta a ponta
(`ff 05`, que devolveu as dez opções e nada além).

### O achado que não estava no escopo, e sem o qual a task seguinte não anda

O save tem verificação própria — um byte de soma por bloco encadeado —, e sem
refazê-la o jogo **recusa** o option file. A regra vale para seis cartões
distintos, um deles de terceiro:

```
byte(0x02102) = ( soma de 0x02044..0x02186, exceto ele próprio ) + 0x8a
```

Ela custou a primeira sonda, que foi recusada, e mudou o método desta task no
meio do caminho — o registro de como isso aconteceu ficou no Contexto, acima.

### O que ficou por fazer, e por que não muda a conclusão

**A segunda metade do teste cruzado** — ROM PT-BR com o cartão inglês — não
rodou. A primeira metade respondeu a pergunta (ROM inglesa com o cartão PT-BR
mostrou tudo), e as nove sondas a responderam de novo por outro caminho: se o
desbloqueio fosse da ROM, trocar bits num cartão não mudaria a tela, e mudou
nove vezes seguidas.

Fica em aberto, e está listado no fim do mapa: bit 9 e bits 11–15; o fim da
faixa do segundo byte de soma; os 15 bytes de `0x02035`; e se a mesma
verificação cobre a área de jogador, que é a pergunta que a
[MCR-TASK-13](/docs/tasks/port-mcr/13-oraculo-e-veredito.md) deixou como
veredito do console e que agora é testável do mesmo jeito.

### As amostras

`work/cards/` guarda a série gravada pelo jogo (`a1`, `a2`, `b-nome`,
`c-opcao`, `c-opcao2`), pelo alvo `make we2002-card-snap LABEL=<nome>`. As
sondas construídas ficam em `work/` (`v2-*`, `t0..t4`, `u0..u2`,
`mapa-completo`). **Nenhuma entra no git**: são derivadas do
`we2002-english-first-boot.mcr`, que está versionado, e o bloco "Reproduzir" do
mapa as reconstrói em quatro linhas.
