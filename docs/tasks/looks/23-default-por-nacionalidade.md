---
id: LOOKS-TASK-23
title: "Incógnita (r) — `DEFAUL` e `NAT`: a nação escolhida e o default que ela aplica"
type: implementação
category: montagem
phase: 8
depends_on: ["LOOKS-TASK-22"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (r)"
status: concluído
---

# LOOKS-TASK-23: O default por nacionalidade

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (r), e a armadilha 17 do perfil.
- **`DEFAUL` e `NAT` não guardam nada**: são as duas metades do default por
  nacionalidade, a tabela que o repositório já tem em `data/defaultlook.txt` —
  95 nações por cinco colunas, as cinco da tupla do corpus
  ([`LOOKS-TASK-13`](/docs/tasks/looks/13-campos-e-dominios-de-looks.md)).
- **Duas cópias do arquivo, e elas têm de bater** (`CLAUDE.md`): o
  `Debug/defaultlook.txt` do `ed.exe` é gitignored e já divergiu. Quem lê aqui
  é o `data/`, versionado.
- **O que a [`LOOKS-TASK-21`](/docs/tasks/looks/21-a-tela-medida.md) mediu da linha, e deixa para cá** (em
  `tools/looks/screen.json`): `NAT` anda **80** valores, de `Unknown` a
  `New Zeland`, com os nomes truncados que o jogo escreve (`Swi`, `Cze`,
  `Portuga`) — contra **95** linhas do `data/defaultlook.txt`, então a
  correspondência não é de um para um e pelo menos quinze linhas do arquivo não
  têm valor na tela. Andar `NAT` **não muda nenhuma outra linha**: o default não
  se aplica sozinho. `DEFAUL` tem um valor só, `O.K.`, trava nas duas pontas com
  `Left`/`Right`, e a ajuda dele é `Confirm` — o que o aplica é outra tecla,
  não medida. E nenhum dos dois está nos 12 bytes do registro
  (`layout.PLAYER_RAM`): onde o jogo guarda a nação escolhida é pergunta desta
  task.
- **Que a ordem da linha `NAT` é a ordem do arquivo é suposição.** O índice de
  nação do arquivo é o do `ed.exe`; o jogo pode ordenar de outro jeito, e casar
  por índice aplica o default da nação errada com cara de certo.

---

## Objetivo

Fazer a linha `NAT` escolher a nação que o jogo escolhe e a linha `DEFAUL`
aplicar o mesmo default que o jogo aplica, medido contra o jogo.

---

## Critério de conclusão

**Dois critérios foram reescritos durante a execução, e a razão é o resultado
da medição**: eles pressupunham que `DEFAUL` aplica a linha do arquivo, e o
jogo não aplica — `DEFAUL` é o botão de **confirmar** da tela. O texto
original de cada um está citado abaixo dele. A regra do prompt é essa:
divergência entre doc e ferramenta é achado, e o markdown se corrige.

- [x] A correspondência valor de `NAT` → linha do `data/defaultlook.txt`,
      medida no jogo em pelo menos cinco nações espalhadas, incluindo uma cujo
      default não é todo `A`. **Seis**, e a correspondência é **por nome**: as
      duas listas não são a mesma lista.
- [x] **O que `DEFAUL O.K.` faz, medido em cada uma dessas nações** — e o que
      ele faz é sair da tela sem aplicar nada: as doze linhas e os doze bytes
      do registro saem da tecla iguais, em 6 de 6.
      *(Dizia: "`DEFAUL O.K.` no jogo, depois de escolher cada uma dessas
      nações: os cinco valores que a tela passa a mostrar iguais aos da linha
      do arquivo." Nenhum valor muda, então não há o que comparar com o
      arquivo — o veredito é esse.)*
- [x] Na janela, a mesma sequência dá os mesmos cinco valores **e o mesmo valor
      de `NAT`**; sem default aplicado, o boneco não tem por que se redesenhar,
      e não se redesenha nos dois lados.
- [x] Controle negativo: **a regra ingênua do código de nação** (`código =
      índice − 1` até o fim) plantada numa cópia da árvore fica vermelha, com
      25 problemas, um por valor depois do salto.
      *(Dizia: "aplicar a linha vizinha do arquivo fica vermelho" — não há
      aplicação a plantar; o que se planta é a correspondência.)*
- [x] O que o jogo faz e o arquivo não diz — 36 valores da tela sem linha, 51
      linhas sem valor, e o código que salta 41 — escrito, e `Unknown` recusado
      em vez de receber um código.
- [x] §10.3 (r) com o veredito e a data.

---

## Log de Execução

**Executado em:** 2026-09-17

### O que se aprendeu

**A premissa da task era falsa, e desmentí-la é o resultado.** `DEFAUL` não
aplica default nenhum: é o **botão de confirmar** da tela — um valor (`O.K.`),
ajuda `Confirm`, e `Circle` sobre ele sai do `LOOKS SET` para o menu de edição
do jogador. Medido em seis nações espalhadas, três delas com linha no arquivo
que não é toda `A`: as doze linhas e os doze bytes do registro saem da tecla
**iguais**, 6 de 6.

**`NAT` guarda, e guarda fora dos doze bytes.** A nacionalidade escolhida cai
em `layout.PLAYER_NATION` e sobrevive à saída da tela — o menu passa a mostrar
`NAT. BRA`. Um dos dois endereços é `0x800E9450 + 27`, o que diz de quebra que
o registro de 12 bytes deste ciclo mora **dentro de uma estrutura maior**.

**E o código da nação não é a posição na linha.** Andando os 80 valores e lendo
o byte em cada um: 1 a 54 guardam 0 a 53, e aí o código **salta 41** —
`Iceland` (valor 55) guarda 95, e a linha acaba em 119. Os códigos 54 a 94
nomeiam algo que a tela não oferece. `Algeria` é o valor 65 e guarda 105 — foi
ele que derrubou a primeira versão desta medição, que tinha concluído
"código = índice − 1" a partir de cinco amostras.

**O `data/defaultlook.txt` é a tabela do editor, e o cabeçalho dela diz.**
`TEAM;NAME;…`: são 95 **times**, nações e clubes juntos (`Inter`, `Bayern`,
`Clas. Brazil`, `Euro All Stars`), enquanto a linha `NAT` é a lista de
nacionalidades do jogo. Casadas por nome: **44** dos 80 valores da tela têm
linha (12 por truncamento — `Portuga`, `Swi`, `Cze`), **36** não têm, e **51**
linhas do arquivo não têm valor. Pareando por índice — pulando `Unknown` — a
coisa **vale até o valor 16** (`Sweden`) e depois desanda: no 17 o jogo diz
`Finland` e a linha é `Islanda`, e `Algeria` receberia a linha do **Arsenal**.

### Gates, na árvore de `SHA_DA_TASK`

*(transcritos abaixo, depois do commit)*

### Arquivos criados/modificados

*(conferidos contra `git show --stat --format= HEAD`)*

### Problemas encontrados

1. **O primeiro filtro para achar a nação achou o relógio.** Andar até três
   nações com três números de teclas diferentes e guardar o que "andou com o
   índice" devolveu **21 bytes**, todos contadores de tempo — continuaram
   subindo com a tela parada. O jeito que funciona é duas corridas com o
   **mesmo** número de teclas terminando em nações diferentes: o que conta
   tempo anda igual nas duas e sai sozinho. Virou a armadilha 40 do perfil.
2. **Cinco amostras concordaram com uma regra errada.** `código = índice − 1`
   vale para 54 dos 80 valores, e as cinco primeiras nações que escolhi caem
   todas nessa faixa. Quem apanhou foi `Algeria`, que só entrou na lista porque
   o pareamento por índice lhe daria a linha de um clube. Desde então o comando
   **anda a linha inteira**, e não uma amostra.
3. **O controle vermelho ficou vermelho pela causa errada, duas vezes.** A
   cópia da árvore não leva o `data/defaultlook.txt` (o caminho é relativo à
   raiz), e a linha de resumo que eu tinha escrito indexava
   `NATION_CODES[1]` — com a regra ingênua plantada, de um trecho só, ela
   estourava antes de comparar coisa alguma. As duas coisas foram consertadas:
   a cópia leva o `data/`, e o resumo se escreve sobre os trechos que a regra
   declarar. É a armadilha 27 do perfil, pela terceira vez no ciclo.
