# 7 — Times: criando-os

> Voltar ao [índice geral](/docs/biblia-we2002/README.md).
>
> *Tutorial by ][Unreal][, aperfeiçoado.*

**Programas usados nesse tutorial:** WE TEAM EDITOR (você poderá usar o 0.98 ou
o 0.99).

## Introdução

Obviamente um time é formado de jogadores, e primeiro você terá que usar o
[tutorial anterior](/docs/biblia-we2002/06-jogadores.md) e montar os jogadores do
time. Daí você se pergunta: e o que é montar um time, então?

Bem, montar o time em WE é **dar nome ao time** — o que antes originalmente era
BRAZIL agora você poderá renomear como CORINTHIANS ou FLAMENGO, etc. Aqui você
também irá indicar o potencial global do seu time (se ele é retranqueiro, ou vai
muito ao ataque). Tem também os esquemas táticos, as bandeiras, o uniforme, etc.

## Executando

Para fazer as mudanças em um time vamos usar o **WE TEAM EDITOR 0.98** do
Obocaman. Com a ISO já pronta, faça o que se pede:

**1º)** Execute o WE TEAM EDITOR.

**2º)** Nessa 2ª tela, clique em abrir ![ícone abrir](img/fig-010-012.png).
Selecione sua ISO no diretório como você fez antes.

![Janela principal do WE2002 Team Editor com o campo Game destacado](img/fig-010-013.png)

**3º)** No próximo passo, no menu **“Team”**, você escolherá o time no qual deseja
substituir ou editar.

![Lista suspensa Team com "41 Brazil" selecionado](img/fig-011-014.png)

### 4º) Editando o nome do time

Agora vamos à edição de fato: vamos dar nome ao time. No nosso caso inventamos o
time **IDEAL**. Para mudar o nome basta digitar nos campos **NAME 1**, **NAME 2**
e **NAME 3** o nome do seu time. Quando mudar, clique em
![ícone inserir](img/fig-011-015.png) para inserir o time na ISO. Uma janela
aparecerá informando que o nome do time foi alterado.

Lembrando que **existe limite na quantidade de caracteres, variando de time pra
time**.

| ANTES | DEPOIS |
| --- | --- |
| ![NAME1/2/3 antes](img/fig-011-016.png) | ![NAME1/2/3 depois](img/fig-011-017.png) |

![Mensagem "The team name has been modified"](img/fig-011-018.png)

### 5º) Editando potenciais do time

Pronto, já mudamos o nome do time. Agora vamos mudar as barras dos potenciais do
time (**Ataque, Defesa, Força, Velocidade e Técnica**), que também é muito
simples. Nos campos respectivos, selecione qual barra você deseja mudar,
clicando no *option box* ao lado, e aumente ou diminua no controle de barras.
Faça isso em todos os campos. Clique no ![ícone inserir](img/fig-012-019.png)
para inserir na ISO.

Só lembrando: isso aqui são informações **muito subjetivas** — vai depender
inteiramente do seu bom senso. Você é que dirá o quanto o time é ofensivo ou
defensivo, se tem poder em campo, se é veloz ou não, se joga com corre-corre ou
com técnica.

![Option box das barras OFFENSE/DEFENSE/POWER/SPEED/TECHNIQ e o controle de barras — clique e arraste para + ou −](img/fig-012-020.png)

### 6º) Inserindo uniforme do time

Agora vamos inserir uma camisa no seu time. Vá ao
[tutorial de uniformes](/docs/biblia-we2002/08-uniformes.md) para aprender a criar
uma **TEX** (uniforme), ou pegue uma já pronta. Clique no
![ícone abrir](img/fig-012-021.png), selecione a TEX (uniforme) e clique em
![ícone inserir](img/fig-012-022.png) para inserir na ISO.

![Campo "Shirt" com o arquivo ideal.bin — aqui você coloca a camisa que o time usa durante o jogo](img/fig-012-023.png)

### 7º) Editando esquemas táticos do time

Pronto. Agora vamos mudar a formação, táticas e batedores. Clique no botão
**“Team Edit”** como mostrado abaixo.

![Janela principal com o botão de Team Edit destacado, ao lado de BASE TEAM](img/fig-013-024.png)

**8º)** Aparecerá no **Team Editor** a tela abaixo (caso você tenha aplicado o
patch de relinkagem e tradução). Agora vamos começar mudando a formação do time.

Caso você queira personalizar a formação padrão, basta selecionar na lista a
formação **DEFAULT**; aí basta ir clicando em cada um dos pontinhos verdes, que
correspondem aos jogadores, e arrastá-los pra posição que desejar. Caso você
queira usar uma formação pré-existente — por exemplo, **4-4-2 - B** — basta
escolher na mesma lista.

Vamos para a prática: após escolher a formação que deseja mudar (aconselho a
DEFAULT), clique sobre o jogador (pontos verdes na figura do campo) e arraste
para o lugar desejado.

![Team Editor: campo com a formação, lista STOCK/DEFAULT, tabela de táticas e batedores](img/fig-014-025.png)

![Detalhe do campo, arrastando um jogador para a posição desejada](img/fig-014-026.png)

**9º)** Pronto. Ao finalizar a edição da formação, clique no botão **ACCEPT** pra
poder gravar na ISO.

**10º)** Após fazer sua formação, vamos fazer as **táticas** usadas no jogo. Para
isso, mude a posição dos quadrados de acordo com as cores referentes a cada
botão (quadrado, triângulo, X, círculo), clicando sobre as opções de tática
desejada. No nosso caso escolhemos: **NORMAL, CENTER ATTACK, RIGHT ATTACK e LEFT
ATTACK**, conforme abaixo.

![Grade de táticas: NO STRATEGY, NORMAL, CENTER ATTACK, RIGHT ATTACK, LEFT ATTACK, OTHER S. ATTACK, CHANGE SIDE, CB OVERLAP, PRESSING, COUNTR ATTACK, OFFSIDE TRAP](img/fig-015-027.png)

**11º)** Agora vamos para o último passo pra criar seu time: **os batedores**.

![Lista de titulares com as colunas SF, LF, RC, LC, PK e CP](img/fig-015-028.png)

**12º)** Esses nomes marcados por um círculo vermelho são a lista dos jogadores
titulares do seu time. Para aprender a mudar o jogador (criar, modificar, etc.)
vá ao tutorial [Editando os jogadores](/docs/biblia-we2002/06-jogadores.md). Ao
seu lado existe uma tabela com:

| Coluna | Significado |
| --- | --- |
| SF | falta perto |
| LF | falta longe |
| RC | escanteio direito |
| LC | escanteio esquerdo |
| PK | pênalti |
| CP | capitão |

Basta clicar no campo respectivo do jogador para dizer quem será o cobrador de
cada item.

**13º)** Para finalizar essas mudanças, clique no botão **ACCEPT** para gravar as
modificações.

---

Próxima seção: [8 — Uniformes: editando os 2D e 3D](/docs/biblia-we2002/08-uniformes.md)
