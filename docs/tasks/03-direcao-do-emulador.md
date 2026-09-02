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

`tools/pes2/drive.sh` (ou `drive.py`), que recebe um **roteiro nomeado** e
entrega um PNG por tela pedida.

```
tools/pes2/drive.sh <copia/track1.bin> --screen team-select --out /tmp/a.png
tools/pes2/drive.sh <copia/track1.bin> --screen replay,result --out-dir /tmp/
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

**Executado em:** 2026-09-01 / 2026-09-02 — **parcial.** A ferramenta e a
mecânica estão de pé e medidas; a navegação por menu **não** foi estabelecida,
e nenhuma das cinco telas do quadro foi alcançada. A task **não** está
concluída.

**O que existe.** `tools/pes2/drive.sh`: rotas nomeadas, passos
`wait / key / down / up / shot / until`, encerramento pelo
`run_duckstation.sh --kill` no `trap`, recusa de `roms/`, e captura por
`import -window root` recortada à geometria da janela. Mais quatro peças que
não existiam:

1. **`[Hotkeys]` no `run_duckstation.sh`.** Um `settings.ini` escrito à mão
   não vincula hotkey nenhuma — exatamente o que a armadilha 4 da §6.11 já
   dizia do `[Pad1]`. Sem isso, fast-forward, save state e load state não
   existiam. Entraram `FastForward = Tab`, `SaveSelectedSaveState = F2`,
   `LoadSelectedSaveState = F1`, `TogglePause = Space`.
2. **Tecla mantida.** `xdotool key` é press e release no mesmo instante e o
   jogo não vê o botão; `keydown` / **1 s** / `keyup` vê. Medido na tela de
   título: três formas de tocar deixaram o quadro idêntico até a sexta casa
   decimal, e 0,4 s de pressão ainda não bastam.
3. **`Tab` mantido corta o intro.** Os cerca de dois minutos de
   `MOVIE/WE2002.STR` viram **25 segundos** de fast-forward.
4. **O passo `until:`**, que espera a *assinatura do quadro* em vez de contar
   segundos. É o que torna a rota repetível: a duração do intro varia entre
   corridas, e todo `sleep` fixo ou passa do ponto ou para antes.

**O número que a rota existente entrega.** A rota `title` acertou a tela em
**5 de 5** corridas, com médias de 0,5502 a 0,5528 e desvios de 0,3397 a
0,3411 — a dispersão é a animação de brilhos do fundo, e é uma ordem de
grandeza menor que a tolerância de 0,02.

**O que não foi conseguido, e o que foi tentado.** Sair do título para o menu.
Seis corridas, e o comportamento não se reproduz: às vezes o `X` deixa o
título intacto, às vezes cai de volta no laço de atração, e **uma única
corrida** — a primeira sonda de input — chegou a um menu com o cabeçalho
`PRO EVOLUTION SOCCER 2`, sem que a sequência que a produziu se repetisse
depois. Tentados, um por corrida: toque simples; `windowfocus` antes;
`--clearmodifiers`; `keydown`/`keyup` de 0,4 s e de 1 s; um, dois e três `X`
com esperas de 5, 6, 10, 12 e 25 s; e fast-forward de 15, 20, 25, 30, 40 e
45 s antes do título.

**Três hipóteses derrubadas por medição**, que valem tanto quanto o que
funcionou e estão na §6.11 como armadilhas 10 a 13:

- *o input não chega* — chega; faltava manter a tecla;
- *a Citrix filtra o XTEST* — ela engancha `XNextEvent`, `xcb_poll_for_event`
  e `XRecordQueryVersion`, e **não** bloqueia. A frase do `CLAUDE.md` sobre
  input sintético é do Windows e não vale no `:98`. O `run-sanitized.sh` não
  é necessário aqui;
- *o `unexpected EOF` era erro de sintaxe* — era edição do `.sh` **durante a
  execução**; o bash relê o arquivo por offset.

**O save state não funcionou.** `F2` com a hotkey vinculada não escreveu nada
em `ds-data/duckstation/savestates`. Não foi diagnosticado — os nomes
`SaveSelectedSaveState` / `LoadSelectedSaveState` saíram do `settings.ini` do
próprio usuário, mas a versão do AppImage pode usar outros, ou a hotkey pode
exigir foco que o `press()` só passou a dar depois. **É a via mais promissora
para a próxima sessão**: com um estado salvo no menu, a navegação deixa de
custar dois minutos por tentativa e passa a ser carregar-e-navegar, que é
exatamente o que a seção "Save state como atalho" desta task previa.

**As telas não alcançadas, com a via proposta** — que é o terceiro critério:

| Tela | Estado | Via proposta |
|---|---|---|
| `team-select` | não alcançada | destravar o save state e navegar a partir de um estado no menu |
| `result` | não alcançada | idem, e depende de completar uma partida — candidata a save state próprio |
| `replay` | não alcançada | idem |
| `ending` | não alcançada | a própria task já previa que exigiria save state |
| `edit` | não alcançada | idem `team-select` |

E uma via que não depende de save state: **pedir a sequência de botões a quem
conhece o jogo**. Foi oferecido e recusado nesta sessão, com razão — a
descoberta autônoma é o método —, mas continua sendo o caminho de menor custo
se a próxima sessão também travar aqui.

**Arquivos criados/modificados**

- `tools/pes2/drive.sh` — novo
- `tools/pes2/run_duckstation.sh` — a seção `[Hotkeys]`
- `docs/PLAN-PES2-PSX.md` — a §6.11 passou de nove para treze armadilhas

**Problemas encontrados.** Os quatro acima. O de método que mais custou: mudar
mais de uma variável por corrida. Cada subida leva de um minuto e meio a dois,
e nas primeiras tentativas eu alterei espera e tecla ao mesmo tempo, o que
tornou dois resultados inúteis. Da quarta corrida em diante passei a mexer em
uma coisa por vez, e foi aí que as armadilhas 10 e 12 apareceram.
