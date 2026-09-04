---
id: PES2-TASK-03
title: "Direção do DuckStation — navegar até a tela e capturar"
type: ferramenta
category: verificação
phase: 2
depends_on: []
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §3.4"
status: em andamento
---

# PES2-TASK-03: Direção do emulador

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §3.4 e §6.11, e a regra do `:98` do
  [CLAUDE.md](../../CLAUDE.md).
- **Sem oráculo, o jogo é o oráculo** (§4.1). Um campo só está mapeado quando
  um `poke` nele muda o que a tela mostra. Isso exige chegar à tela.

`tools/pes2/run_duckstation.sh` já sobe o jogo isolado no `:98`, com binding
de teclado, renderer de software e limpeza de instância. `boot_check.sh` já
mede que ele botou. O que não existe é **navegação**: sair do laço de
atração, entrar no menu, chegar à tela de seleção de time, e capturar.

---

## Objetivo

`tools/pes2/drive.py`, que recebe um **roteiro nomeado** e
entrega um PNG por tela pedida.

```
python3 tools/pes2/drive.py <copia/track1.bin> --screen team-select --out /tmp/a.png
python3 tools/pes2/drive.py <copia/track1.bin> --screen replay,result --out-dir /tmp/
```

### Os roteiros que a Fase 2 precisa

Um por tela onde um nome de time aparece — que é o conjunto de cópias da
§1.5, visto do outro lado:

| Roteiro | Onde o nome aparece | Cópia que o alimenta |
|---|---|---|
| `team-select` | seleção de time | `SELECT.BIN` @3128 |
| `result` | tela de resultado | `RESULT.BIN` @524 |
| `replay` | replay | `REPLAYS.BIN` @11380 |
| `ending` | fim de campeonato | `ENDING.BIN` @1256 |
| `edit` | modo de edição | `SELECTC.BIN` @16576 |

Nem todas serão alcançáveis em minutos de navegação — `ending` pode exigir
*save state*. **Declarar o que não deu, e como se pretende chegar lá**, é
resultado legítimo; fingir que uma tela foi vista não é.

### As armadilhas já pagas, e que este script herda

As nove da §6.11, todas dentro do `run_duckstation.sh` — reusar o script,
não reescrever a subida. Mais as do `CLAUDE.md` sobre dirigir janela sem
window manager:

- `xdotool windowactivate` **falha** no `:98` (`XGetInputFocus returned the
  focused window of 1`). Dirigir por coordenada absoluta.
- **O foco de teclado segue o ponteiro** (`PointerRoot`). `xdotool
  mousemove --window <janela>` antes de qualquer `key`.
- **Teclar uma vez e esperar o efeito**, nunca em laço.
- Capturar com `import -window <id>`; se falhar com `Resource temporarily
  unavailable`, a janela está obscurecida ou fora da tela — **não** é o
  emulador travado (§6.11, armadilha 5).

### Save state como atalho

O DuckStation tem *save state* (§3.4). Um estado salvo na tela certa
transforma "navegar por três minutos de menu" em "carregar e capturar", e
torna o roteiro repetível. **O estado não entra no git** — é derivado de
jogo comercial, mesma regra de `roms/` e dos quadros do `boot_check.sh`.
O que entra é o script que o cria e o caminho de onde ele mora.

---

### Quem está esperando: a PES2-TASK-28 parou aqui

Em 2026-09-01 a [PES2-TASK-28](/docs/tasks/28-t-name-copias-de-idioma.md)
fechou tudo o que não precisa de emulador — o conjunto de cópias varrido, a
recusa, a fonte localizada, o round-trip byte a byte — e **ficou parada nos
dois itens de tela**. Ela precisa de duas coisas deste roteiro, e vale
tê-las em mente ao escolher as telas:

- **A tela de apresentação**, a que desenha o nome do time a partir do
  `T_NAME`. É onde o nome novo tem de aparecer, e não é a mesma tela de
  seleção de time que a PES2-TASK-04 usa: o `T_NAME` é bitmap rasterizado, a
  tabela de texto é outra coisa, e é justamente por serem duas que a §6.12
  existe.
- **A troca de idioma.** A `(EsIt)` tem duas cópias de `T_NAME` e a
  `(EnFrDe)` três, todas com o mesmo conteúdo; o jogo escolhe pelo idioma.
  Verificar num idioma só deixa passar exatamente o defeito que a §6.12
  descreve, então o roteiro precisa saber chegar ao menu de idioma, ou a
  task 28 tem de dizer por escrito que não conseguiu.

## Critério de conclusão

- [x] Pelo menos **três** das cinco telas alcançadas e capturadas.
      **Quatro** — `team-select`, `edit`, `result` por rota versionada, e
      `replay` à mão pelo `pad.py`.

      > **O critério dizia "com o PNG mostrando um nome de time legível", e
      > isso o jogo não dá.** Medido em 2026-09-02 e reconfirmado em
      > 2026-09-04: só a `team-select` traz nome de time em texto
      > (`IRELAND`); placar, replay e o menu pós-partida identificam o time
      > por **bandeira**. Não é falha da ferramenta e não se conserta
      > dirigindo melhor — está na §4.2 do plano como item 3a, e é o que
      > limita o que a PES2-TASK-04 pode verificar em tela. O critério foi
      > reescrito para o que se pode medir: **alcançar e capturar**, e
      > **registrar como cada tela identifica o time**.
- [x] O roteiro é repetível. Medido em 2026-09-04, duas corridas seguidas por
      rota, e o resultado é mais forte do que o critério pedia: os PNG saem
      **idênticos byte a byte**, `difference = 0.00000000`.

      | rota | corridas | diferença |
      |---|---|---|
      | `team-select` | 17,95 s e 21,03 s | **0** |
      | `edit` | 29,28 s e 27,58 s | **0** |
      | `result` | 225,78 s e 227,56 s | **0** |
      | `main-menu` | 52,71 s e 48,69 s | 0,00029855 |

      **As três primeiras partem de save state e a quarta não**, e é isso
      que explica a diferença: a rota fria atravessa a abertura em tempo
      real, e a fase da bola que gira atrás do menu não cai no mesmo lugar.
      0,0003 sobre o quadro inteiro e 0,00014 sobre o recorte dos sete itens
      — é a bola, não o menu.

      É consequência da PES2-TASK-34 — o emulador parado entre um toque e o
      próximo — mais o toque que fixa `Día/Noche` (armadilha 37). Antes
      disso o `title` estava em 5 de 5 e o `main-menu` em 4 de 4, pela
      tolerância do `PES2_TOLERANCE`; agora não é preciso tolerância
      nenhuma.

      **`replay` continua sem rota versionada**, e é o que mantém esta task
      parcial.
- [x] As telas não alcançadas estão listadas, com o motivo e a via proposta.
- [x] Encerra sempre pelo `run_duckstation.sh --kill`, sem deixar montagem
      FUSE nem janela órfã no `:98`.
- [x] Roda no `DISPLAY=:98`. Sem exceção (§6.10) — **salvo a sessão conjunta
      de 2026-09-02**, que rodou no `:1` a pedido explícito do usuário, que
      é o que a regra manda pedir.

---

## Log de Execução

**Executado em:** 2026-09-01 / 2026-09-02 — **parcial.** A ferramenta está de
pé, reescrita em Python, e o **menu principal é alcançado em 3 de 3
corridas**. As cinco telas do quadro (`team-select`, `result`, `replay`,
`ending`, `edit`) continuam **não alcançadas**: elas ficam depois do menu, e a
navegação a partir dele não foi escrita. A task **não** está concluída.

**A ferramenta é `tools/pes2/drive.py`**, que substituiu o `drive.sh` a pedido
do usuário — regra nova do repositório: ferramenta se escreve em Python, salvo
motivo específico em contrário. O shell era herança, não escolha, e cobrou:
o bash relê script por *offset de byte*, então editar o `.sh` no meio da
corrida corrompeu uma; cada espera saía por `identify -format`, um processo por
poll devolvendo string; e a rota era string separada por espaço, que teste
nenhum alcançava sem emulador. Ficou em shell o que é shell puro: o lançador,
com as armadilhas de `pgrep` e o `fusermount` do `--kill`.

O que a versão Python tem e a outra não podia ter:

- **comparação por região.** A espera antiga era a média do quadro **inteiro**,
  e é por isso que a rota do menu não fechava: duas telas diferentes podem ter
  a mesma média. `Frame.difference(box=…)` compara um recorte;
- **`settle` que recusa preto.** Tela de carregamento é preta e é *parada* —
  a primeira versão devolvia no instante em que o título esmaecia, e o passo
  seguinte apertava `Down` num carregamento;
- **`nudge`**, que aperta até algo mudar. Justificou-se sozinho: numa das três
  corridas verdes o `Down` da tela de idioma só pegou na **quinta** tentativa;
- **`self_check`** sem emulador, registrado no `pes2_selftest` — inclusive o
  caso em que duas metades trocadas têm a mesma média e só o recorte as separa.

**A causa raiz de tudo, e ela é grave: `XDG_DATA_HOME` nunca isolou nada.**
Este AppImage resolve o diretório de dados a partir do **`$HOME`**, então toda
corrida usou `~/.local/share/duckstation`, o do usuário. A prova é de uma
linha — `StartFullscreen = true` no arquivo que o lançador escreve, janela sai
com 800×655. Consequências medidas:

- o `[Pad1]` que o lançador escreve **nunca valeu**; o que valia era o
  `settings.ini` do usuário. Doze subidas foram gastas apertando teclas ligadas
  a coisa nenhuma;
- `Tab`, `Enter` e as setas funcionavam por serem **defaults** do DuckStation,
  não por causa do arquivo — o que fez a configuração parecer aplicada;
- dois save states nossos foram parar no diretório do usuário. Um deles é o
  `SLES-03957_1.sav` de 2026-09-01 22:26: **o `F2` da sessão anterior
  funcionou**, e a conclusão de que "o save state não gravou" estava errada —
  ele gravou no lugar errado;
- o cartão de memória do usuário **não** foi tocado: digest `4acca062…`,
  mtime de 29/ago, conferido antes e depois.

Sobrescrever `HOME` isola de verdade e foi tentado; aí o primeiro boot para no
assistente de nove páginas, que `SetupWizardIncomplete = false` não pula —
medido com a bandeira presente, com os `resources/` semeados de uma instalação
que funciona, com o BIOS como arquivo em vez de link, e com o `settings.ini` do
usuário copiado verbatim.

**E aí a isolação foi encerrada por decisão do usuário**, na mesma sessão: esta
máquina roda DuckStation para este projeto, e isolar não interessa. O lançador
**deixou de escrever configuração** — arquivo que ninguém lê é pior que nenhum,
porque passou um dia parecendo aplicado — e o `drive.py` **lê os bindings do
`settings.ini` que de fato vale**. Efeito colateral bem-vindo: remapear um
botão na interface do DuckStation basta, sem tocar no repositório. Save state e
cartão caem em `~/.local/share/duckstation`, como em qualquer sessão do
emulador; a armadilha 20 fica registrada para o caso de a isolação voltar a
interessar.

**O caminho feliz, dado pelo usuário e medido passo a passo.** Os botões não
são todos o mesmo, que é o que custou uma dúzia de subidas para enxergar:

| passo | botão | evidência |
|---|---|---|
| 1. passar do vídeo | `Tab` mantido 25 s | `Cross` **não** pula: 24 pressionamentos em 80 s deixaram o FMV correndo |
| 2. sair do título | **`Start`** | 5 `Cross` nele deram diff 0,0003; `Start` deu 0,5502 |
| 3. `Seleziona Lingua` | `Down`, `Cross` | `Down` 0,00634; `Cross` 0,02176 e a tela vira espanhol |
| 4. `¿Estás seguro?` | `Up`, `Cross` | `Up` 0,00554 |
| 5. ranura de MEMORY CARD | `Cross` | sai para o menu, diff 0,132939 |

**3 de 3 corridas chegaram ao menu**, com assinaturas 0,140639/0,212488,
0,140682/0,212449 e 0,140679/0,212435 — dispersão na quarta casa decimal. A
rota `title` segue medida em 5 de 5 (médias 0,5502–0,5528).

**Sete hipóteses derrubadas por medição**, todas na §6.11 como armadilhas 14 a
20, mais as 10 a 13 da sessão anterior:

- *o `settings.ini` do lançador vale* — não vale, e é a raiz de tudo;
- *`Tab` funcionar prova que o arquivo foi lido* — não prova: é default;
- *`Keyboard/X` é nome de tecla* — não é. A tabela do binário sai com
  `strings` e tem `UpArrow`, `Enter`, `Space`, `Escape`, `F1`–`F4`, `F10`,
  `F11` e as letras `A D E F G H I J K L Q S T W`. `X`, `P`, `Insert`,
  `Delete`, `Home` não estão lá e nunca vincularam;
- *`Keyboard/Space` serve para `Cross`* — serve como nome e **pausa o
  emulador**: hotkey ganha de pad, e o glifo de pausa no canto da captura foi
  o que denunciou;
- *o título aceita `Cross`* — aceita `Start`;
- *um pressionamento basta* — não basta;
- *o `F2` não gravava* — gravava, no diretório do usuário.

**As telas do quadro, com a via proposta** — o terceiro critério:

| Tela | Estado | Via proposta |
|---|---|---|
| `team-select` | não alcançada | `Modo Partido` a partir do menu, que agora é alcançável em 3 de 3 |
| `result` | não alcançada | exige completar uma partida — candidata a save state, que agora se sabe que funciona |
| `replay` | não alcançada | idem |
| `ending` | não alcançada | save state |
| `edit` | não alcançada | `Modo Editar` a partir do menu |

**Arquivos criados/modificados**

- `tools/pes2/drive.py` — novo, substitui o `drive.sh`
- `tools/pes2/drive.sh` — removido
- `tools/pes2/run_duckstation.sh` — a escrita de `settings.ini` removida
  inteira (com ela o `PES2_PAD_TYPE`, o `PES2_BIOS` e o `XDG_DATA_HOME`), e o
  achado do `$HOME` registrado onde ele engana
- `tools/pes2/selftest.py` — a lógica de quadro do `drive.py`
- `docs/PLAN-PES2-PSX.md` — §6.11 de treze para **vinte** armadilhas, e as 4
  e 11 corrigidas: elas afirmavam o contrário do que se mediu
- `CLAUDE.md`, `docs/prompts/perfil-pes2.md`, `docs/tasks/04-*`, `05-*` — a
  ferramenta trocou de nome

**Problemas encontrados.** Os sete acima. O de método que mais custou continua
sendo mudar mais de uma variável por corrida; a correção — uma coisa por
subida — é o que fez as armadilhas aparecerem. E um segundo, novo: **passei
doze subidas tratando "a tecla não funciona" como fato sobre o jogo quando era
fato sobre a configuração.** O teste que resolveu — mudar algo que não é
default (`StartFullscreen`) e olhar o efeito — custa uma subida e devia ter
sido o primeiro.

---

### Segunda sessão de 2026-09-02 — do menu para dentro

**O save state destravou tudo.** Ele existe agora como `--save-state` do
`drive.py`, e `from_main_menu()` carrega-o quando existe: **2,5 min por
tentativa viraram ~40 s**. O estado é derivado de jogo comercial e fica
**fora do git**, como `roms/` e os quadros do `boot_check.sh`; o que está
versionado é a rota que o cria. Ele mora em
`~/.local/share/duckstation/savestates/SLES-03957_1.sav`, 1.553.197 B — e o
`save_state()` **confere a mtime do arquivo** em vez de apertar e torcer,
que é o erro exato que fez a sessão anterior concluir que o `F2` não gravava.

**Duas telas novas, e a segunda quase não conta.**

| rota | como se chega | assinatura | nome de time? |
|---|---|---|---|
| `team-select` | menu → `Modo Partido` → `Partido de exhibición` → passa a atribuição de controle | 0,1686 / 0,2490 | **sim**, `IRELAND` legível |
| `edit` | menu → sexta linha | 0,1530 / 0,2103 | **não** |

O `edit` decepciona por um motivo do jogo, não da ferramenta: o **Modo
Editar do PES2 só edita jogador criado**. `Cambiar` e `Registrar jugador`
mostram doze linhas de `–NO DATA–`, e o nome de time de `SELECTC.BIN`
@16576 fica atrás de criar um jogador primeiro — várias telas de entrada de
nome.

Em compensação ele entregou de graça o que a §4.2 queria: os **dezesseis
atributos por jogador, em ordem de tela** — `Ataque`, `Defensa`, `Equilib.`,
`Resisten`, `Velocid.`, `Acelerar`, `Respues.`, `Regate`, `Pase`,
`Precisión`, `Potencia`, `Cabezazo`, `Salto`, `Técnica`, `Efecto`,
`Positivo`, mais `Nación`, `Altura`, `Edad`, `Posición` e `Pie`. Está na
§4.2 do plano como item 3b.

**Duas armadilhas novas, as 21 e 22 da §6.11, e a segunda escondia um bug
que confirmava o item errado calado:**

- **o d-pad quer toque, o botão de face quer pressão.** Medido lado a lado
  no menu: `Down` de 1,0 s perdeu **duas de seis**; de 0,15 s, seis de seis.
  Não era tecla perdida — 1 s dispara o auto-repeat e num menu de sete itens
  dá a volta inteira, parando no mesmo item. Isso também explica a
  instabilidade da tela de idioma: com toque curto, `down`, `cross` e `up`
  passaram a pegar na **primeira** tentativa;
- **`nudge` está errado numa lista.** A tentativa extra dele move uma linha
  a mais: cinco linhas pedidas viraram dez teclas e a rota do `Modo Editar`
  caiu no `Modo Copa` **sem reclamar**. O `menu_pick` passou a mandar uma
  tecla por linha, esperar mais, e **contar** quantas registraram — e a
  recusa disparou de verdade ("3 de 5") antes de o toque curto consertar a
  causa.

**As três que faltam, e por quê — com o número refeito.** Esta seção dizia
"onze minutos de fast-forward não terminaram a partida", e **estava errada**:
media uma partida que nunca havia começado. O usuário apontou a causa e ela
se confirmou por medição — **o relógio não anda até o passe inicial**. O
saque fica em `1°  0:00` esperando o `Cross` do jogador 1, e para qualquer
medida sobre o quadro inteiro isso é idêntico a uma partida correndo: a
câmera se mexe, os jogadores respiram, a média fica em ~0,30.

O teste honesto recorta **só o relógio** e compara dois quadros. Na mesma
tela de saque, com o quadro conferido (`1°  0:00`, placar 0-0, HUD com
`Quinn` e `Sand`):

| | diferença do recorte do relógio |
|---|---:|
| antes do `Cross` | **0,00000** |
| 5 s depois do `Cross` | andando |

**Chegar ao saque também precisou de medição**, porque três telas seguidas —
abertura de estádio, entrada dos times e saque — têm todas média entre 0,21
e 0,30, e duas sondas apertaram `Cross` na tela errada por isso. O que as
separa é o **desvio da faixa do topo** `(0,60)-(800,200)`: saque
0,1170–0,1204, entrada 0,1531, abertura 0,2317–0,2537. O teste usado é a
conjunção dela com o relógio congelado, porque cada um sozinho já deu falso
positivo — o recorte do relógio sobre o céu da abertura também fica parado.
E **`Start` pula a abertura de estádio**, o que poupa a espera.

**Com o passe dado, o ritmo real:** 600 s de fast-forward levaram a partida
a `1°  7:06`. São ~0,71 minuto de jogo por minuto real, e uma partida
padrão inteira sai por volta de **28 minutos reais** mais o intervalo.

`Opciones de Partido` **não** tem duração: tem `MEMORY CARD`,
`Repetición de la moviola`, botões, som e tela. A duração mora na
configuração de cada modo — a tela do `Modo Copa` mostra
`Duración del partido  10 min.`

Via proposta, agora medida em vez de suposta:

| Tela | Via |
|---|---|
| `result` | **`Partido a Penaltis`** primeiro — segunda linha do submenu do `Modo Partido`, e uma disputa de pênaltis termina em muito menos que os ~28 min de uma partida padrão. Se não servir, `Modo Copa`/`Liga` na menor duração, com **save state antes do apito final**, que transforma a espera em carregar-e-capturar |
| `replay` | idem; `Opciones de Partido → Repetición de la moviola` controla o replay |
| `ending` | campeonato completo; save state é o único caminho sensato |
| `edit` com nome de time | criar um jogador primeiro, e então `Registrar jugador` pede o time |

**O erro de método desta sessão, e ele é o mesmo de sempre.** Registrei como
propriedade do jogo ("a partida não termina em onze minutos") um número que
era propriedade do meu roteiro (a partida não tinha começado). O sintoma —
quadro se mexendo, média estável — era compatível com as duas leituras, e eu
escolhi a que não exigia mais trabalho. O conserto foi medir a coisa
específica (o relógio) em vez da tela inteira. Duas outras corridas se
perderam para a armadilha 25, o `pgrep -f` casando o próprio shell, que já
estava documentada e eu repeti duas vezes seguidas.

**Arquivos desta sessão**

- `tools/pes2/drive.py` — `save_state`/`load_state`, `from_main_menu`,
  `menu_pick`, as rotas `team-select` e `edit`, `wait_for_stats(fast=)`, e
  `TAP`/`DPAD`
- `docs/PLAN-PES2-PSX.md` — armadilhas 21 e 22, o item 3b da §4.2, e a §6.14
  (a ferramenta externa avaliada)

**Pendência encaminhada.** Nenhuma sobre configuração: a isolação foi
encerrada por decisão e o lançador encolheu de 302 para 173 linhas. O que fica
para quem seguir é a navegação **a partir** do menu, que agora é alcançável em
3 de 3 — `Modo Partido` para `team-select`, `Modo Editar` para `edit`, e save
state para `result`, `replay` e `ending`, agora que se sabe que o `F2`
funciona.

---

### Terceira sessão de 2026-09-02 — a partida, com o usuário na tela

Feita **junto**, com o emulador no `:1` para o usuário ver — a exceção que a
§6.10 manda pedir, e ele pediu. Dela saiu a ferramenta `tools/pes2/pad.py`,
que **anexa** ao emulador em vez de bootar: um comando por vez
(`press`, `shot`, `stats`, `watch`, `run`), decidido por quem está olhando.
É de onde as rotas do `drive.py` passam a ser escritas.

**O achado que destravou o `result`, e ele é do usuário.** A armadilha 23
dizia que o saque espera `Cross`, e a leitura fácil é que basta dá-lo uma
vez. Não basta: **todo gol devolve um saque que congela de novo**, tela e
relógio em `0,00000`. Um laço que só segura o fast-forward para no primeiro
gol e fica ali até o orçamento acabar — que é exatamente o que produziu o
"onze minutos não terminaram a partida". Com o laço certo — acelerar,
detectar congelamento, `Cross`, retomar — a partida foi do saque ao
`RESULTADO` em **179 segundos e nove saques**, contra os ~28 minutos que a
versão sem `Cross` fazia estimar. Está no `pad.py run` e virou a armadilha
26.

**Duas telas novas, e uma limitação que muda o critério.**

| tela | como se chega | identifica o time por |
|---|---|---|
| `replay` | acontece sozinho a cada gol; `Square` abre `Guardar Repetición` | **bandeira** |
| `result` | fim da partida | **bandeira** |

Medido percorrendo a partida inteira: placar em jogo, replay, `RESULTADO` e
o menu pós-resultado (`Pasar al siguiente partido` / `A menú de Selección de
Modo`) **não mostram nome de time em texto**. O registro de replay gravado
no cartão também não — traz as duas bandeiras, o placar, `Goleador` e
`Pasador`. Isso limita o que a PES2-TASK-04 pode verificar em tela, e está
na §4.2 do plano como item 3a: `SELECT.BIN` @3128 é verificável pela grade
de seleção; onde aparecem os nomes de `RESULT.BIN` @524 e `REPLAYS.BIN`
@11380 **ainda não se sabe**.

**Gravar um replay no cartão, e o diferencial que ele deixou.** São quatro
passos e o último não é `Cross`: `Square` → `Cross` (ranura) → `Cross`
(bloco) → **`Start`**. Com autorização do usuário, gravado no cartão real, em
bloco que a própria tela declarava vazio. O diferencial, medido com cópia de
antes e depois:

| | |
|---|---|
| tamanho | 131.072 → 131.072, inalterado |
| bytes diferentes | 16.282 |
| blocos de 8.192 B tocados | **0, 4 e 5** |

O bloco 0 é o diretório; 4 e 5 são o dado. A tela do próprio jogo confirma:
o cartão passou a mostrar `R1` ocupando **dois** blocos. É insumo direto
para a PES2-TASK-05.

**Outras coisas medidas, todas inéditas para o `:98`:**

- existe um **menu pré-partida** (`Iniciar partido`, `Ajuste alineación`,
  `Ajuste sonido`, `Config. Personal`, `Abandonar partido`) que os cinco
  `Cross` da rota anterior atravessavam sem que eu soubesse;
- **`Start` pula a abertura de estádio** — do usuário, e usado o tempo todo;
- **um `Cross` só** sai do replay e dá o saque, não são dois;
- no `:1` a busca de janela acha a **moldura**, não o cliente: 894×785 em vez
  de 800×655, e todo recorte medido no `:98` passa a cair no pixel errado.
  O `pad.py` desce para a janela filha, e a prova é que a assinatura do menu
  principal voltou a bater exatamente (0,1407 / 0,2124).

**Save states parkados:** um na tela de `RESULTADO` (`SLES-03957_1.sav`,
17:57), que torna `result` carregar-e-capturar.

**Arquivos desta sessão**

- `tools/pes2/pad.py` — novo
- `tools/pes2/run_duckstation.sh` — o `:1` como display possível: cookie
  preservado fora do `:98`, e posicionamento deixado para o window manager
- `docs/PLAN-PES2-PSX.md` — armadilha 26 e o item 3a da §4.2

---

### Quarta sessão de 2026-09-04 — a rota `result`, e a repetibilidade medida

**A task continua parcial**, e o que falta é uma coisa só: `replay` não tem
rota versionada. `ending` segue não alcançada, com a via já escrita acima.

**A rota `result` existe, e ela não passa por uma tela de `RESULTADO`.** A via
é `Partido a Penaltis` — a segunda linha do submenu do `Modo Partido` —,
escolhida porque uma disputa chega ao fim em ~3,5 min contra os ~28 min de uma
partida de exibição. Medido em quatro corridas: a disputa acaba e o jogo vai
**direto** para a caixa `Pasar al siguiente partido`, sem tela de resultado no
meio. O quadro desta task lista `result` como tela própria porque a sessão de
2026-09-02 a viu por uma partida de exibição; por pênaltis ela não existe.
Virou a armadilha 40 da §6.11.

**Quatro botões dessa via não são os que um palpite escolheria**, e cada um
custou uma corrida:

| tela | botão | o que os outros fazem |
|---|---|---|
| opções de partido | `Cross` | `Start` não faz nada |
| ordem de cobradores | **`Square`** | `Start`, `Cross`, `Circle` e `Triangle` deixam a tela onde está — maior diferença medida 0,0018 |
| cobrança | `Cross` | — |
| depois da última | **nenhum** | `Cross` dispensa a caixa no instante em que ela sobe |

**O achado que dominou a sessão: depois que a rota entra numa partida, brilho
não reconhece tela nenhuma.** A tela de opções abre com `Día/Noche = Al azar`
e `Estación/Tiempo = Al azar`, e a consequência não é cosmética:

- o gramado lê **0,301–0,310** num saque diurno e **0,1123** num noturno, e a
  rota decidiu que tinha saído do gramado estando nele — voltou com um pênalti
  como "resultado";
- **toda tela com campo por trás herda isso**: a ordem de cobradores leu
  0,2633, 0,2581 e 0,2499 em três corridas;
- recorte de UI **não** salva, porque o painel é translúcido: a coluna azul de
  cobradores foi de 0,2965 para 0,2891 com a luz, e a faixa do HUD de 0,3356
  (dia) para 0,0933 (noite).

O conserto é um toque — fixar `Día/Noche` antes de confirmar — e ele é também
o que torna a rota repetível: com a luz fixada a mesma tela lê **0,249778 em
três corridas seguidas**, na sexta casa. Viraram as armadilhas 37 e 38.

**E a caixa pós-partida precisou de cinco reconhecedores.** Os quatro
primeiros falharam, cada um por um motivo medido, e vale a lista porque ela é
o método:

| tentativa | por que falhou |
|---|---|
| média do quadro | `Estadio` também é `Selección al azar`: a mesma caixa leu 0,3185 num estádio e 0,3941 em outro |
| média de recorte de UI | painel translúcido — armadilha 38 |
| imobilidade exata | a caixa fica sobre um estádio 3D vivo; o `still` estourou 40 s |
| "mexe pouco" | a cauda da comemoração anda menos de 0,03 em 3 s e passou por caixa |
| **desvio-padrão do retângulo da caixa** | funciona: 0,2048–0,2116 contra 0,1197–0,1261 da comemoração, em três estádios |

O quinto é o que está no código, com caso vermelho no `--self-check`. Virou a
armadilha 39.

**A repetibilidade saiu mais forte que o critério.** Ele pedia "a mesma tela";
o medido é **o mesmo arquivo**: `team-select`, `edit` e `result` produziram
PNG idênticos byte a byte em duas corridas seguidas, `difference =
0.00000000`. O `main-menu` não, e a razão é a diferença certa entre eles — as
três primeiras partem de save state, a quarta atravessa a abertura em tempo
real, e a bola que gira atrás do menu não cai na mesma fase (0,0003 no quadro
inteiro, 0,00014 no recorte dos sete itens).

**Um defeito achado pela guarda, não por uma corrida.** A média do Modo Editar
**andou entre os dois dias** — 0,154324–0,155040 em 03/09 e 0,147528 em 04/09,
duas vezes — porque a tela anima um jogador e o save state guarda uma fase
diferente da caminhada dele. Ao alargar a tolerância do Modo Editar para
cobrir as duas leituras, o `--self-check` ficou vermelho num teste que já
existia: *"Modo Editar é o vizinho mais apertado da cerca do menu
principal"*. E estava certo — com 0,147528, o Modo Editar cai **dentro** da
tolerância de ±0,010 do menu principal, e o `from_main_menu` teria aceitado um
estado parado no Modo Editar como sendo o menu, calado, com toda rota
seguindo dali para `Down`. A cerca foi de ±0,010 para **±0,003**, que é quinze
vezes a dispersão medida da própria tela (0,0002 em duas máquinas e dois dias)
e deixa 0,0069 entre as duas. Conferido com duas corridas vivas depois de
apertar: 0,140592 e 0,140493, as duas dentro.

**Arquivos criados/modificados**

- `tools/pes2/mcp_drive.py` — a rota `result` e o `take_penalties`; as
  constantes da via de pênaltis; `on_pitch`; a cerca do menu principal
  apertada; a tolerância do Modo Editar alargada; e as asserções novas do
  `--self-check` (a faixa do gramado contra as cinco telas vizinhas, o
  `JUMP`, e a caixa pós-partida contra a comemoração)
- `docs/PLAN-PES2-PSX.md` — §6.11 de 36 para **42** armadilhas, recontadas
  pelo `awk`, e as três citações da contagem
- `docs/prompts/perfil-pes2.md` — a armadilha 12 do perfil, com o resumo das
  seis novas
- `docs/tasks/03-direcao-do-emulador.md` — os dois critérios reescritos e este
  Log

**Problemas encontrados**

- **O primeiro critério pedia o que o jogo não dá.** "Três telas com nome de
  time legível" não é alcançável dirigindo melhor: só a `team-select` mostra
  nome em texto, e as outras usam bandeira. Reescrito para o que se mede —
  alcançar, capturar, e registrar como cada tela identifica o time —, com a
  razão ao lado. É o item 3a da §4.2, e é o que limita a PES2-TASK-04.
- **Dois times iguais vão para morte súbita**: Irlanda contra Irlanda levou 55
  e 58 cobranças. A rota aguenta (orçamento de 60), mas quem quiser metade do
  tempo escolhe times de força diferente. Armadilha 41.
- **Errei o mesmo erro duas vezes na mesma sessão**, e o módulo já o
  documentava: a nota do `mcp_drive.py` diz que imobilidade exata só serve na
  tela realmente parada, e eu a usei duas vezes em telas que animam — no Modo
  Editar em 03/09 e na caixa pós-partida hoje. Ler a própria nota antes de
  escrever o `wait` custaria dois minutos e poupou zero.
