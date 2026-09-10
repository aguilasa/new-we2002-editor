# Os desbloqueios no option file do WE2002

**Medido em 2026-09-10**, sobre a release japonesa `SLPM-87056` (as três
imagens de `roms/` declaram esse código). O que este arquivo diz é onde o
option file guarda os **nove times secretos** e a opção de **escolher os times
da Master League no modo exibição**, e como reescrever isso sem que o jogo
recuse o cartão.

É o papel que [`../wte/re/mcr.md`](../wte/re/mcr.md) faz para os 17 destinos do
editor do Obocaman: **fonte de endereços**, para a ferramenta citar. A medição
é da [MCR-TASK-17](/docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md), cujo
escopo é descoberta e mapeamento — **marcar e desmarcar na ferramenta é task
seguinte**, e ela cita este arquivo.

## O campo: `0x02184..0x02185`, dezesseis bits, little-endian

Endereço absoluto no cartão de 131.072 bytes. Cai no **bloco 1**, dentro da
cadeia declarada `[1, 2]` do save `BISLPM-87056WEW-OPT`.

| Bit | Máscara | O que liga |
|---:|---|---|
| 0 | `0x0001` | Euro A.S. |
| 1 | `0x0002` | Class. England |
| 2 | `0x0004` | Clas. France |
| 3 | `0x0008` | Clas. Nether |
| 4 | `0x0010` | Class. Italy |
| 5 | `0x0020` | C. Germany |
| 6 | `0x0040` | Clas. Brazil |
| 7 | `0x0080` | Cl. Argentina |
| 8 | `0x0100` | **times da Master League no modo exibição** |
| 10 | `0x0400` | World A.S. |

Os nomes são os que o jogo escreve na tela, e a ordem da tabela é a dos bits,
não a da tela.

**Três coisas que a forma do mapa não deixa adivinhar**, e cada uma custou um
teste:

- **O bit 8 não é time.** É a opção de Master League, no meio da faixa dos
  times. Foi ele que quebrou a leitura "bits 0..8 são os nove times".
- **O World A.S. não é vizinho do Euro A.S.** Ele está no bit **10**, com o
  bit 9 vazio entre os dois.
- **Bit 9 e bits 11..15 não fazem nada observável.** Ligados sozinhos, não
  acrescentam time nem opção. Não quer dizer que sejam livres — quer dizer que
  esta medição não os viu fazer nada.

## A verificação: sem recalcular, o jogo **recusa** o cartão

O save tem verificação própria, e ela **não** é a do diretório do cartão — o
`tools/mcr/cli.py info` dá `bad checksums none` num cartão que o jogo recusa,
porque os 16 checksums que ele confere são os dos quadros.

```
byte(0x02102) = ( soma de 0x02044..0x02186, exceto ele próprio ) + 0x8a   (mod 256)
```

`k = 0x8a` em **sete** cartões independentes, dois deles de terceiros. Gravar o
campo de flags sem refazer esse byte produz *ERROR* ao carregar o option file —
medido, e é o primeiro sintoma que aparece.

O campo de flags está **dentro** da faixa dessa soma, então quem escreve ali
sempre precisa refazê-la. Um segundo byte de soma, `0x02202`, cobre a faixa
seguinte, que começa em `0x02186`; o fim dela não foi determinado, e **não é
necessário** para escrever os flags.

### O campo `0x02035..0x02043`, 15 bytes

Alta entropia, muda por inteiro em toda gravação que mudou algo, e **é zero nos
três cartões de primeira execução — que o jogo aceita**. Não foi identificado.
Consequência prática: um cartão editado a partir de um `first-boot` pode
deixá-lo zerado, e é o que as sondas desta medição fizeram.

### O que **não** é verificação

`0x0216d` e `0x02205` mudam quando o save muda, e por isso entraram na lista de
candidatos. Foram **descartados**: a busca por faixa somada consistente com
todos os cartões dá **zero** soluções para os dois, enquanto dá soluções para
`0x02102` e `0x02202`. São dado — o `0x0216d` acompanha uma opção de jogo.

Descartados pelo mesmo tipo de evidência: os cinco bytes `0x043df`, `0x048ae`,
`0x049da`, `0x049db` e `0x04ca0`, que separam os dois cartões de primeira
execução. Eles caem na **tabela de nomes** e carregam os mesmos valores que
deslocam `Ylonen`, `Kovtun` e `De Anda` de um byte — as duas builds não guardam
a mesma lista de nomes, e isso não tem relação com desbloqueio.

## Como a medição foi feita

O jogo é a única fonte de cartão válido, então a série parte de um cartão que
ele mesmo gravou: [`../mcr/we2002-english-first-boot.mcr`](../mcr/README.md),
com o campo em `00 00` e nenhum extra na tela.

Cada sonda é esse cartão com **só** `0x02184..0x02185` trocado e `0x02102`
refeito. O jogo carrega, e o que aparece na tela é a resposta.

| Sonda | `0x02184..85` | Bits | O que apareceu |
|---|---|---|---|
| `v2-01` | `01 00` | 0 | Euro A.S. |
| `t0` | `aa 02` | 1,3,5,7,9 | England, Nether, Germany, Argentina |
| `t1` | `cc 00` | 2,3,6,7 | France, Nether, Brazil, Argentina |
| `t2` | `f0 00` | 4,5,6,7 | Italy, Germany, Brazil, Argentina |
| `t3` | `00 03` | 8,9 | **só a opção de Master League** |
| `t4` | `00 fc` | 10..15 | só o World A.S. |
| `u0` | `00 a8` | 11,13,15 | nada |
| `u1` | `00 30` | 12,13 | nada |
| `u2` | `00 c0` | 14,15 | nada |
| `mapa-completo` | `ff 05` | 0..8, 10 | **os nove times e a opção de Master League, e nada além** |

A última é a confirmação ponta a ponta: os dez bits da tabela ligados de uma
vez devolvem exatamente as dez opções da tabela. É ela que tira o
`bit 10 = World A.S.` da eliminação e o põe em observação direta.

As quatro primeiras são **teste em grupo**: o bit `i` entra na sonda `t` se o
bit `t` de `i` estiver ligado, então a assinatura de um nome — em quais sondas
ele apareceu — **é** o índice do bit dele. Dez bits em quatro boots, em vez de
dez. As três últimas são busca binária sobre os seis bits altos, que é o mínimo
possível quando há um só observável.

**Foi o controle que pegou a anomalia.** O World A.S. não apareceu em nenhuma
das quatro primeiras, o que daria assinatura `0000` — índice 0, já ocupado pelo
Euro A.S. medido direto. Sem essa contradição visível, o mapa teria sido lido
como "bits 0..8 são os nove times" e estaria errado em duas linhas.

### Reproduzir

```sh
# a sonda: campo trocado, soma refeita, nada mais
python3 - <<'EOF'
A,B,C = 0x02044, 0x02186, 0x02102
d = bytearray(open("mcr/we2002-english-first-boot.mcr","rb").read())
d[0x02184], d[0x02185] = 0xff, 0x05        # os dez bits do mapa
d[C] = 0
d[C] = (sum(d[i] for i in range(A,B)) + 0x8a) & 0xff
open("work/sonda.mcr","wb").write(bytes(d))
EOF

# guardar o cartao vivo antes de trocar, e por o da sonda no lugar
make we2002-card-snap LABEL=antes
cp work/sonda.mcr ~/.local/share/duckstation/memcards/"World Soccer Winning Eleven 2002 (Japan)_1.mcd"
make we2002-play          # a ROM inglesa, na tela do usuario
```

A gravação do jogo é **determinística** — salvar sem mudar nada devolve o mesmo
md5 —, então todo diff de uma série destas é sinal, sem relógio nem contador
para descontar.

## O que fica em aberto

- **Bit 9 e bits 11..15**: nada observável, causa desconhecida.
- **O fim da faixa do `0x02202`**: indeterminado com os cartões disponíveis.
- **Os 15 bytes de `0x02035`**: não identificados; zero é aceito.
- **Se a mesma verificação cobre a área de jogador**, que é onde o
  `tools/mcr/` e o editor do Obocaman escrevem. É a pergunta que a
  [MCR-TASK-13](/docs/tasks/port-mcr/13-oraculo-e-veredito.md) deixou como
  veredito do console, e agora é testável do mesmo jeito: gravar pela
  ferramenta e abrir no jogo.
