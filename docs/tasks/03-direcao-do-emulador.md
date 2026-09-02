---
id: PES2-TASK-03
title: "Direção do DuckStation — navegar até a tela e capturar"
type: ferramenta
category: verificação
phase: 2
depends_on: []
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §3.4"
status: pendente
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

- [ ] Pelo menos **três** das cinco telas alcançadas e capturadas, com o PNG
      mostrando um nome de time legível. **Uma** — `team-select`, com
      `IRELAND` legível. O `edit` foi alcançado e capturado, mas o Modo
      Editar do PES2 só edita jogador **criado**, então nenhum nome de time
      aparece nele sem criar um antes. Ver o Log.
- [ ] O roteiro é repetível: duas corridas seguidas produzem a mesma tela
      — medido para `title` (5 de 5) e `main-menu` (4 de 4, médias 0,140546
      a 0,140682). `team-select` e `edit` foram alcançadas, mas cada uma numa
      corrida só; falta a segunda.
      (dentro da tolerância do `PES2_TOLERANCE`, pela mesma razão do
      `boot_check.sh` — emulação não é exata quadro a quadro).
- [x] As telas não alcançadas estão listadas, com o motivo e a via proposta.
- [x] Encerra sempre pelo `run_duckstation.sh --kill`, sem deixar montagem
      FUSE nem janela órfã no `:98`.
- [x] Roda no `DISPLAY=:98`. Sem exceção (§6.10).

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

**As três que faltam, e por quê.** `result`, `replay` e `ending` estão atrás
de uma partida terminada. Medido: **onze minutos de fast-forward não
terminaram** uma partida de exibição na duração padrão — a média do quadro
ficou em 0,30 o tempo todo. E `Opciones de Partido` **não** tem duração de
partida: tem `MEMORY CARD`, `Repetición de la moviola`, botões, som e tela.
A duração mora na configuração de cada modo — a tela do `Modo Copa` mostra
`Duración del partido  10 min.`

Via proposta, agora medida em vez de suposta:

| Tela | Via |
|---|---|
| `result` | `Modo Copa` ou `Modo Liga` com a menor duração, e **save state antes do apito final** — daí vira carregar-e-capturar |
| `replay` | idem; `Opciones de Partido → Repetición de la moviola` controla o replay |
| `ending` | campeonato completo; save state é o único caminho sensato |
| `edit` com nome de time | criar um jogador primeiro, e então `Registrar jugador` pede o time |

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
