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
      mostrando um nome de time legível. **Nenhuma das cinco** — a rota até o
      menu não foi estabelecida. Ver o Log.
- [ ] O roteiro é repetível: duas corridas seguidas produzem a mesma tela
      — **medido para a única rota que existe** (`title`): 5 corridas, 5
      acertos. Fica aberto porque o critério fala das telas do quadro, e
      nenhuma delas foi alcançada.
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
usuário copiado verbatim. **Fica em aberto** (armadilha 20 da §6.11). Enquanto
isso o `drive.py` **lê os bindings do `settings.ini` que de fato vale**, em vez
de declarar os seus — o que é honesto e sobrevive a o usuário remapear.

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
- `tools/pes2/run_duckstation.sh` — `PES2_PAD_TYPE`, os nomes de tecla
  corrigidos, e o achado do `$HOME` registrado onde ele engana
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

**Pendência encaminhada.** A isolação por `HOME` esbarra no assistente de
configuração; enquanto não for resolvida, as corridas leem o `settings.ini` do
usuário e escrevem save state no diretório dele.
