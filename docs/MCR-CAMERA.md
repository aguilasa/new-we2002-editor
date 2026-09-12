# A câmera no option file do WE2002

**Medido entre 2026-09-11 e 2026-09-12**, sobre a release japonesa
`SLPM-87056`, num cartão do usuário gravado pelo jogo rodando sob o fork do
DuckStation.

O que este arquivo diz é onde o option file guarda a **câmera** — a vista de
jogo, uma entre nove —, como reescrevê-la sem que o jogo recuse o cartão, e o
que a série de testes provou em cada sentido.

É o papel que [`../wte/re/mcr.md`](../wte/re/mcr.md) faz para os 17 destinos do
editor do Obocaman: **fonte de endereços**, para a ferramenta citar. Ao
contrário daquele, aqui a ferramenta existe e roda: quem lê e grava é o
[`../tools/mcr/options.py`](../tools/mcr/options.py), e o `--check` dele repete
esta medição.

## O campo: **um byte**, no offset 1 do registro 0

**Não é um endereço absoluto, e isso é medido, não cautela.** O save
`BISLPM-87056WEW-OPT` pode morar em qualquer bloco — ver
[Onde o save mora](#onde-o-save-mora) —, então o que vale é o offset:

```
byte 1 do payload do registro 0
```

Nos cartões desta máquina, com o save no bloco 1, isso cai em **`0x02104`**. Com
o save no bloco 3 cai em `0x06104`. Um leitor que crave `0x02104` acerta todo
cartão deste repositório e erra o primeiro que vier de fora.

| Valor | Câmera | Como se sabe |
|---:|---|---|
| 0 | `normal-near` | o jogo gravou, nós lemos |
| 1 | `normal-mid` | o jogo gravou, nós lemos — é o default do cartão limpo |
| 2 | `normal-far` | o jogo gravou, nós lemos |
| 3 | `wide` | **nós gravamos, o jogo mostrou** |
| 4 | `tv` | o jogo gravou **depois** de nós editarmos o cartão |
| 5 | `zoom` | **nós gravamos, o jogo mostrou** |
| 6 | `ov-near` | **nós gravamos, o jogo mostrou** |
| 7 | `ov-mid` | **nós gravamos, o jogo mostrou** |
| 8 | `ov-far` | o jogo gravou, nós lemos |

Os nomes são os que o jogo escreve na tela.

**As nove foram vistas, e não são a mesma evidência**, que é a razão de a
tabela ter essa coluna. São três rotas:

| rota | valores | o que prova |
|---|---|---|
| o jogo gravou, nós lemos | 0, 1, 2, 8 | o decodificador |
| nós gravamos, o jogo mostrou | 3, 5, 6, 7 | a gravação — a direção para a qual a ferramenta existe |
| o jogo gravou sobre o nosso | 4 | os dois lados de uma vez: ele pôs o byte onde lemos, com a soma que calculamos |

Cartão que o jogo salvou é cartão que o jogo **já aceitou**: relê-lo não diz
nada sobre gravar, e é por isso que a primeira rota sozinha não bastava.

Até 2026-09-12 o 6 e o 7 estavam aqui por **cerco** — cada um entre dois
vizinhos provados —, o que é argumento e não observação. Duas corridas os
tiraram dessa condição. Nenhum valor da tabela depende mais de inferência, e um
check do módulo exige que as três rotas cubram as nove e não reivindiquem
nenhuma duas vezes.

## A verificação: sem refazer a soma, o jogo dá `ERROR`

O byte da câmera cai dentro do payload do registro 0, e todo registro carrega o
próprio checksum na frente. A regra, e a busca de faixa que a sustenta, estão em
[`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md#a-verificação-sem-recalcular-o-jogo-recusa-o-cartão);
aqui basta a forma que o módulo usa:

```
byte(header + 2) = ( soma do payload que o header declara ) mod 256
```

**Medido em 2026-09-12, e desmentiu uma dedução.** Um byte foi trocado no
cartão do DuckStation, de `wide` para `tv`, deixando a soma no `0xdb` da wide em
vez do `0xdc` da tv. O jogo **não** aceitou o registro, **não** caiu para um
default e **não** ignorou a edição em silêncio: pôs **`ERROR`** na tela ao
carregar o option file e parou ali.

A documentação dizia que uma soma velha "parecia que a edição não pegou". Era
dedução de nunca ter visto uma recusa, e estava errada na direção que importa —
quem fosse depurar por aquela frase procuraria uma gravação que não pegou,
quando o jogo já tinha nomeado o problema na tela.

**E não encostou no cartão.** O digest depois da recusa era o de antes, byte a
byte. Uma soma velha custa uma carga que falha, e nada mais: os 12.420 bytes de
nomes do registro 1 nunca correram risco.

### A soma que o jogo **produz** é a nossa

Rejeitar soma errada não é o mesmo que gerar a soma certa — um validador pode
aceitar um byte por coincidência e emitir outro. Não é o caso. Com o save nos
blocos 3-4, a câmera foi trocada para `tv` **pela tela do próprio jogo** e o
option file salvo: ele escreveu `0xdc`, que é exatamente o que o
`options.checksum()` calcula para aquele payload, aceito sem ajuste nenhum.

Mesmo algoritmo, nos dois sentidos.

## Onde o save mora

**O bloco não é o endereço do save**, e o console segue o diretório — na leitura
e na gravação.

Em 2026-09-12 o save foi movido dos blocos **1-2 para os 3-4**, diretório junto:
as duas entradas antigas liberadas, duas novas escritas com a cadeia religada e
o XOR de cada quadro refeito, e os 16 KiB de dados copiados.

| o que se mediu | resultado |
|---|---|
| o jogo carrega do bloco 3? | **sim**, com a câmera certa, e sem regravar nada |
| ao gravar, onde ele põe o save? | **de volta nos blocos 3-4** — grava na cadeia que achou, não normaliza para os primeiros livres |
| a câmera cai onde a ferramenta lê? | **sim**, offset 1 do registro 0, num cartão que a ferramenta já tinha editado |

Dezesseis bytes se moveram nessa gravação: o byte da câmera, a soma, e treze no
padding do título.

Consequência para quem escreve código: cartão de terceiro pode ter este save em
**qualquer** bloco. Os cartões desta máquina já o têm no **1**, e não no 2, que
é onde os 17 destinos absolutos do editor do Obocaman o esperam.

## O padding do título, que não é dado

Os bytes entre o fim do título do save e o fim do campo de 64 — nos cartões
desta máquina, `0x02034..0x02043` — mudam a cada gravação. É memória não
inicializada que o jogo deixa no cabeçalho do save PSX.

Isso apareceu como ruído no primeiro diff e voltou em todos os outros. O
`--check` do módulo **conta e nomeia** esses bytes em vez de os varrer para
debaixo do tapete: diferença que passe dessa faixa é diferença de verdade.

**A prova de que nunca foram dado veio do próprio jogo.** O `radar-dow.mcr` — o
cartão com o radar devolvido ao valor original — é idêntico ao limpo em tudo,
menos 12 bytes, todos aí dentro. E entre duas gravações do jogo sem mudança
nenhuma de conteúdo, a faixa varia.

> Isto aperta uma frase do [`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md):
> "a gravação do jogo é determinística — salvar sem mudar nada devolve o mesmo
> md5". Vale **quando o padding está zerado**, que é o caso dos cartões de
> primeira execução daquela medição. Com lixo no padding, o md5 muda sem que
> nenhum dado mude.

## O mapa do registro 0

A câmera não está sozinha. O registro 0 tem **134 bytes** e é onde caem todos os
campos que este repositório mapeou até agora. Nos **dezenove cartões** medidos,
**oito** offsets variam: seis já têm nome, dois não.

| offset | addr (save no bloco 1) | o que é | onde está descrito |
|---:|---|---|---|
| 0 | `0x02103` | `00` em todos os cartões | — |
| **1** | `0x02104` | **a câmera** | este arquivo |
| 2..101 | `0x02105..0x02168` | 50 × `u16` LE, constantes em todos os cartões; têm cara de máscaras de pad | não identificado |
| **106..107** | `0x0216D..6E` | **a velocidade do jogo**, `u16` | [`/docs/MCR-OPCOES-JOGO.md`](/docs/MCR-OPCOES-JOGO.md) |
| 109 | `0x02170` | varia: `0x00`, `0x10` | não identificado |
| **115** | `0x02176` | **as cinco opções de tela** | [`/docs/MCR-OPCOES-JOGO.md`](/docs/MCR-OPCOES-JOGO.md) |
| 126 | `0x02181` | varia: `0x00`, `0x02` | não identificado |
| **129..130** | `0x02184..85` | **os desbloqueios**, 16 bits | [`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md) |

Os outros **126 bytes** são iguais nos dezenove cartões — o que não quer dizer
que sejam fixos, e sim que nenhuma sonda os moveu ainda. O offset 107 é a
lembrança de que isso muda: ele ficou constante até uma sonda mudar a
velocidade para zero barras, que é o único valor medido em que o `u16`
transborda para o byte de cima.

## Como a medição foi feita

O jogo é a única fonte de cartão válido, então a série parte de cartões que ele
gravou. Quatro option files salvos numa sessão, sem mexer em nada além da
câmera:

| câmera | byte | checksum |
|---|---|---|
| `normal-near` | `00` | `d8` |
| `normal-mid` (o limpo) | `01` | `d9` |
| `normal-far` | `02` | `da` |
| `ov-far` | `08` | `e0` |

Gravar esses dois bytes no cartão limpo reproduz cada um dos outros três **byte
a byte**, fora o padding do título. É o que o `--check` refaz.

Daí em diante, cada pergunta virou uma corrida na tela: escrever `zoom` e ver
`Zoom`; depois `wide`, `ov-near` e `ov-mid`, e ver os três; deixar a soma velha
e ver `ERROR`; mover o save de bloco e ver se carrega; mudar pela tela do jogo e
medir o que ele gravou.

**Dez corridas ao todo**, cada uma respondendo uma pergunta que os cartões
sozinhos não respondiam.

### Reproduzir

```sh
# ler
python3 tools/mcr/options.py <cartão.mcr>

# gravar, numa cópia -- dois bytes, o valor e a soma
python3 tools/mcr/options.py <cartão.mcr> --set zoom --out work/sonda.mcr

# a medição inteira, contra os cartões de origem
WE2002_MCR_CAMERA_CARDS=<dir> python3 tools/mcr/options.py --check
```

E a troca no emulador, que é o que fecha o ciclo:

```sh
cp work/sonda.mcr "<memcards>/World Soccer Winning Eleven 2002 (Japan)_1.mcd"
```

**Feche o emulador antes de trocar o arquivo** — ele reescreve o cartão ao
sair, e a sonda vai junto.

## O que fica em aberto

- **Os offsets 109 e 126** do registro 0: variam entre os cartões e não foram
  identificados. O `0x0216D`, que estava nesta lista, era a **velocidade do
  jogo** — e o [`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md) já o
  tinha descartado da lista de verificações dizendo que "acompanha uma opção de
  jogo", o que estava certo e agora tem nome.
- **Os 15 bytes do padding do título**: não identificados; zero é aceito pelo
  jogo.
- **O registro 1**, de 12.420 bytes: são os nomes editados, e nada além disso
  foi mapeado.
