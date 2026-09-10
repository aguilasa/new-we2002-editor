---
id: MCR-TASK-17
title: "Onde o option file guarda os times secretos e a opção de Master League no modo exibição"
type: verificação
category: engenharia-reversa
phase: 5
depends_on: ["MCR-TASK-09"]
fonte_de_verdade: "/docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md §Critério de conclusão"
status: pendente
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

---

## Objetivo

Dizer, com valor medido, **onde** cada uma das dez opções está gravada no
option file, e **qual valor** significa ligado.

---

## Critério de conclusão

- [ ] **O cartão inglês é mesmo o estado "travado".** Ele é chamado assim aqui
      por ser de primeira execução, e isso é inferência. Abrir a ROM inglesa
      com ele e olhar a lista de times fecha a questão — e se ele já vier com
      algo aberto, todo o resto muda de leitura.
- [ ] **O teste cruzado acima**, com as duas conclusões escritas. Se o
      desbloqueio for da ROM e não do cartão, a task fecha aí, com a evidência
      — e é resultado, não falha.
- [ ] **`0x02184..0x02185` confirmado ou derrubado.** Confirmar é mostrar o
      jogo lendo: gravar um valor intermediário num cartão de trabalho, abrir,
      e ver **um subconjunto** dos times na tela. `ff ff` contra `00 00` sozinho
      não distingue "flags" de "dois bytes que mudaram junto".
- [ ] **Um bit por opção, nomeado.** O experimento discriminante é
      diferencial e in-game: partir de um cartão sem nada aberto, ligar **uma**
      coisa, salvar, e comparar. Repetido, dá a tabela `bit → time`. Onde o
      jogo não deixar ligar uma sozinha, diga isso e mostre o que deu para
      isolar.
- [ ] **A opção de Master League no modo exibição** localizada com o mesmo
      método. Ela pode não estar no mesmo campo dos times, e não há motivo para
      supor que esteja.
- [ ] **O mapa vai para [`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md)**,
      arquivo novo: endereço, máscara, o nome de cada opção como o jogo a
      escreve na tela, e o comando que reproduz cada medição. É o papel que o
      [`wte/re/mcr.md`](../../../wte/re/mcr.md) faz para os 17 destinos — a
      task que for implementar isso cita esse arquivo, e não este.
- [ ] **Hipótese descartada fica registrada, com o motivo.** Os cinco bytes da
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
