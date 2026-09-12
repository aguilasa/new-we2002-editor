# Os desbloqueios no option file do WE2002

**Medido em 2026-09-10**, sobre a release japonesa `SLPM-87056`, nas duas
imagens que a medição usou: `roms/we2002-english/we2002-english.bin` e
`roms/we2002-pt-br.bin`, as duas declarando esse código. (Não são as únicas —
cinco `.bin` de `roms/` o declaram, a European Deluxe dos golden tests do
`newWe2002` entre elas.)

O que este arquivo diz é onde o option file guarda os **nove times secretos**,
o **estádio Club House** e a opção de **escolher os times da Master League no
modo exibição**, e como reescrever isso sem que o jogo recuse o cartão.

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
| 9 | `0x0200` | **estádio Club House** |
| 10 | `0x0400` | World A.S. |

Os nomes são os que o jogo escreve na tela, e a ordem da tabela é a dos bits,
não a da tela.

**Três coisas que a forma do mapa não deixa adivinhar**, e cada uma custou um
teste:

- **Nem todo bit é time, e os que não são estão no meio.** O bit 8 é a opção
  de Master League e o bit 9 é um **estádio**, os dois entre os times. Foi o 8
  que quebrou a leitura "bits 0..8 são os nove times".
- **O World A.S. não é vizinho do Euro A.S.** Ele está no bit **10**, com o
  Club House no 9 entre os dois.
- **Bits 11..15 não fazem nada observável.** Ligados sozinhos, não acrescentam
  time nem opção. Não quer dizer que sejam livres — quer dizer que esta medição
  não os viu fazer nada, e o bit 9 é a prova de que essa distinção importa
  (ver abaixo).

## A verificação: sem recalcular, o jogo **recusa** o cartão

O save tem verificação própria, e ela **não** é a do diretório do cartão — o
`tools/mcr/cli.py info` dá `bad checksums none` num cartão que o jogo recusa,
porque os 16 checksums que ele confere são os dos quadros.

```
byte(0x02102) = ( soma de 0x02044..0x02186, exceto ele próprio ) + 0x8a   (mod 256)
```

`k = 0x8a` em **seis cartões distintos**, um deles de terceiro — o
`pro-evolution-soccer-2.29939.gme`, descrito em
[`../mcr/README.md`](../mcr/README.md). Oito arquivos foram medidos, e três
deles são o mesmo cartão: `a1`, `a2` e o `we2002-ptbr-first-boot.mcr` têm o
mesmo md5, porque a gravação é determinística — é resultado desta medição, não
amostra perdida. (`work/cards/ptbr-original.mcr` e `ptbr-antes-do-v2.mcr` são
outras duas cópias, do PT-BR e do `c-opcao2`, e não entram na conta.) A forma
da regra reaparece em outra release: os cinco `BESLES-039xxPES-OPT` de PES2 em
`mcr/` dão `k = 0x89` na mesma faixa.

Gravar o campo de flags sem refazer esse byte produz *ERROR* ao carregar o
option file — medido, e é o primeiro sintoma que aparece.

O campo de flags está **dentro** da faixa dessa soma, então quem escreve ali
sempre precisa refazê-la.

### A mesma soma, descrita de outro jeito, em `tools/mcr/options.py`

O [`options.py`](../tools/mcr/options.py) chegou a esse byte por outro caminho,
medindo a câmera: para ele o `0x02102` é o **checksum do registro 0**, e a faixa
somada é o payload que o próprio registro declara — `0x02103..0x02189`, 134
bytes, com **`k = 0`**. Conferido sobre o mesmo cartão, as duas descrições dão o
byte idêntico:

```
gravado no cartão                                  0xd9
options.py        soma de 0x02103..0x02189, k=0    0xd9
este arquivo      soma de 0x02044..0x02186, k=0x8a 0xd9
```

Não é coincidência, e a explicação está na própria busca: ela devolve **23.875
faixas** consistentes, e a tabela acima registra o *início mínimo* de cada
bloco. A do `options.py` é outra dessas faixas — a que o cabeçalho do registro
nomeia, num formato `[u16 tamanho][u8 checksum][payload]` que se repete no
`0x02202`. As duas medições são a mesma regra vista de dois lados; a deste
arquivo é a que a busca acha sem saber do formato, e a do `options.py` é a que
o formato explica.

Consequência prática: **a sonda do bit 9 foi montada pelo módulo**, sem
reimplementar soma nenhuma — o campo de flags cai dentro do payload do registro
0, então a mesma função que conserta a soma ao gravar a câmera a conserta aqui. Um segundo byte de soma, `0x02202`, cobre a faixa
seguinte, que começa em `0x02186`; o fim dela não foi determinado ao byte, mas
está medido em **`b >= 0x04e30`** — a segunda soma cobre a área de jogador. Não
é necessário para escrever os flags.

A busca é por faixa consistente com todos os cartões ao mesmo tempo, e ela
devolve **milhares** de faixas, não uma: o que se mede é o início mínimo de
cada bloco. **Uma busca que pare em `0x02400` acha zero faixas para o
`0x02202`** e conclui, errado, que ele não é soma.

### O campo `0x02035..0x02043`, 15 bytes

Alta entropia, muda por inteiro em toda gravação que mudou algo, e **é zero nos
dois cartões de primeira execução — o inglês e o PT-BR —, que o jogo aceita**.
O `29939` entra aqui só como o caso oposto, o de campo preenchido: ele não é de
primeira execução. Não foi identificado.
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
| `sonda-bit9` | `00 02` | 9 | **o estádio Club House** — 2026-09-12, na tela de estádios |

A última é a confirmação ponta a ponta: os dez bits da tabela ligados de uma
vez devolvem exatamente as dez opções da tabela. É ela que tira o
`bit 10 = World A.S.` da eliminação e o põe em observação direta.

**A coluna "O que apareceu" é observação direta, não capturada.** Ela saiu das
nove corridas de `make we2002-play` de 2026-09-10 — sessão na tela do usuário,
a exceção com nome próprio da regra do `:98` —, e esse caminho não tem gate que
capture quadro. Os artefatos versionados provam a **regra da soma** e o
conteúdo de cada sonda; o que a tela mostrou é testemunho de quem estava
olhando. Quem quiser a imagem tem o caminho escrito no bloco "Reproduzir"
abaixo: montar a sonda, guardar o cartão vivo, pôr a sonda no lugar, e capturar
com `python3 tools/pes2/pad.py shot` sobre a instância viva ou com
`DISPLAY=:98 import -window root` se o boot for por `make we2002-98`.

As quatro primeiras são **teste em grupo**: o bit `i` entra na sonda `t` se o
bit `t` de `i` estiver ligado, então a assinatura de um nome — em quais sondas
ele apareceu — **é** o índice do bit dele. Dez bits em quatro boots, em vez de
dez. As três últimas são busca binária sobre os seis bits altos, que é o mínimo
possível quando há um só observável.

**Foi o controle que pegou a anomalia.** O World A.S. não apareceu em nenhuma
das quatro primeiras, o que daria assinatura `0000` — índice 0, já ocupado pelo
Euro A.S. medido direto. Sem essa contradição visível, o mapa teria sido lido
como "bits 0..8 são os nove times" e estaria errado em duas linhas.

### O bit 9: o método tinha a resposta, faltava olhar

O bit 9 ficou dois dias como "nada observável, causa desconhecida", e a
causa do buraco **não foi o método** — foi a escolha do observável.

O teste em grupo põe o bit `i` na sonda `t` quando o bit `t` de `i` está
ligado. `9 = 1001b`, então o bit 9 entrou em **`t0` e `t3`**, e as duas
corridas aconteceram. A assinatura `1001` estava lá para ser lida; ninguém a
leu porque a coluna "O que apareceu" registra **a tela de seleção de times**, e
um estádio não aparece nela. As duas linhas dizem "England, Nether, Germany,
Argentina" e "só a opção de Master League" — e as duas estavam certas e
incompletas ao mesmo tempo.

Em 2026-09-12 a sonda isolada `00 02` foi montada sobre o cartão limpo, cujo
campo estava em `0x0000`, e o **Club House** apareceu na tela de estádios. Dois
bytes: `0x02185` e a soma.

**A lição é sobre o custo de um observável a menos, não sobre o desenho do
teste.** Quatro boots teriam bastado para os onze bits; foram nove, e um
décimo dois dias depois, porque a pergunta feita à tela era "que times
apareceram" e não "o que mudou". Vale para os bits 11..15, que continuam em
aberto pela mesma razão possível: podem estar ligando algo que ninguém olhou.

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

# ou, pelo modulo, que ja sabe refazer a soma desse registro:
python3 - <<'EOF'
import sys; sys.path.insert(0, "tools/mcr")
import options, layout
from card import Card
c = Card.from_file("mcr/we2002-english-first-boot.mcr")
rec = options.record(c, layout.CAMERA.record)
c.write(0x02184, (0x0200).to_bytes(2, "little"))          # so o bit 9
c.write(rec.header + 2,
        bytes([options.checksum(bytes(c.data[rec.payload:rec.payload + rec.size]))]))
open("work/sonda.mcr", "wb").write(c.to_bytes())
EOF

# guardar o cartao vivo antes de trocar, e por o da sonda no lugar
make we2002-card-snap LABEL=antes
cp work/sonda.mcr ~/.local/share/duckstation/memcards/"World Soccer Winning Eleven 2002 (Japan)_1.mcd"
make we2002-play          # a ROM inglesa, na tela do usuario
```

A gravação do jogo é **determinística** — salvar sem mudar nada devolve o mesmo
md5 —, então todo diff de uma série destas é sinal, sem relógio nem contador
para descontar.

A busca de faixa, que é o que sustenta os limites acima. `k` de uma faixa
`[a, b)` é `2*byte[C] - (P[b] - P[a])`, então duas cartas concordam quando a
diferença dos prefixos delas é constante — o que torna a varredura de
8.192 × 16.384 pares uma busca em dicionário:

```sh
python3 - <<'EOF'
from collections import defaultdict
HDR = 3904
def load(p):
    d = open(p, "rb").read()
    return d[HDR:] if len(d) == 131072 + HDR else d
CARDS = ["mcr/we2002-english-first-boot.mcr", "mcr/we2002-ptbr-first-boot.mcr",
         "work/cards/b-nome.mcr", "work/cards/c-opcao.mcr",
         "work/cards/c-opcao2.mcr", "mcr/pro-evolution-soccer-2.29939.gme"]
D = [load(p) for p in CARDS]
P = []
for d in D:
    p, s = [0] * (len(d) + 1), 0
    for i, v in enumerate(d):
        s = (s + v) & 0xff
        p[i + 1] = s
    P.append(p)
LO, HI_A, HI_B = 0x2000, 0x4000, 0x6000            # bloco 1, bloco 2
for C in (0x02102, 0x02202, 0x0216d, 0x02205):
    V = {j: tuple((P[i][j] - P[0][j]) & 0xff for i in range(1, len(D)))
         for j in range(LO, HI_B + 1)}
    T = tuple((2 * (D[i][C] - D[0][C])) & 0xff for i in range(1, len(D)))
    by = defaultdict(list)
    for b in range(LO + 1, HI_B + 1):
        by[V[b]].append(b)
    hits = [(a, b) for a in range(LO, HI_A)
            for b in by.get(tuple((V[a][i] + T[i]) & 0xff
                                  for i in range(len(T))), ()) if b > a]
    print(f"0x{C:05x}: {len(hits)} faixas", 
          f"inicio_min=0x{min(a for a,_ in hits):05x}" if hits else "",
          f"fim_min=0x{min(b for _,b in hits):05x}" if hits else "")
EOF
```

```
0x02102: 23875 faixas inicio_min=0x02044 fim_min=0x02186
0x02202: 27250 faixas inicio_min=0x02186 fim_min=0x04e30
0x0216d: 0 faixas
0x02205: 0 faixas
```

## O que fica em aberto

- **Bits 11..15**: nada observável, causa desconhecida. O bit 9 esteve nesta
  linha até 2026-09-12 e saiu dela quando se olhou **outra tela** — o que é
  motivo para tratar estes cinco como "não procurados o bastante", e não como
  "vazios".
- **O fim da faixa do `0x02202`**: indeterminado ao byte com os cartões
  disponíveis; medido `b >= 0x04e30`.
- **Os 15 bytes de `0x02035`**: não identificados; zero é aceito.
- **Se a mesma verificação cobre a área de jogador**, que é onde o
  `tools/mcr/` e o editor do Obocaman escrevem. É a pergunta que a
  [MCR-TASK-13](/docs/tasks/port-mcr/13-oraculo-e-veredito.md) deixou como
  veredito do console, e agora é testável do mesmo jeito: gravar pela
  ferramenta e abrir no jogo.
