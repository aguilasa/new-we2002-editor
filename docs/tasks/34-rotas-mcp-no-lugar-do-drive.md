---
id: PES2-TASK-34
title: "Rotas MCP no lugar do `drive.py`"
type: ferramenta
category: ferramental
phase: 0
depends_on: [PES2-TASK-33]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §6.14 (fluxo F)"
status: concluído
---

# PES2-TASK-34: Rotas MCP no lugar do `drive.py`

## Contexto

- **Referência:** [`/docs/PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md) §6.14, o
  **fluxo F** — o único dos sete que a seção descartou dizendo *"as
  ferramentas dele seriam melhores … mas é a parte que já está de pé e
  medida"*.
- Fase 0 pelo mesmo motivo das [PES2-TASK-32](/docs/tasks/32-poc-do-mcp-do-duckstation.md)
  e [33](/docs/tasks/33-compilar-e-validar-o-mcp.md): é decisão sobre o
  ferramental da máquina, não sobre o disco.

A frase do plano continua verdadeira quanto ao *estar de pé*, e falsa quanto
ao **custo de mantê-lo de pé**. O `drive.py` dirige o jogo por `xdotool` num
`:98` sem window manager, e quase toda armadilha da §6.11 existe por causa
disso: o foco que segue o ponteiro, `TAP=0.15` contra `HOLD=1.0` calibrados na
tentativa, o auto-repeat que dá volta num menu de sete itens e se parece com
tecla perdida, o `menu_pick` que conta quantas linhas registraram porque
**não dá para confiar** que cinco teclas movam cinco linhas, e as assinaturas
de quadro que decidem se a tela chegou. Cada uma dessas é um contorno para a
mesma falta: **não há como parar o jogo entre uma tecla e a próxima**.

Com o MCP há. `frame_step` avança **um quadro exato** e pausa; `press_button`
recebe `duration_frames`. Com o emulador pausado, cinco `Down` são cinco
linhas, e não uma aposta.

### O que já foi medido, e por qual ferramenta

Em **2026-09-03**, depois da PES2-TASK-33, o caminho feliz inteiro foi
percorrido **sem uma chamada de `xdotool`**: do vídeo de abertura ao menu
principal, e do menu até o cursor em `Modo Editar`.

| passo | chamada | resultado |
|---|---|---|
| vídeo de abertura | `press_button Cross` ×2 | `PRESS ANY BUTTON` |
| idioma | `Down` + `Cross` | Español |
| ¿Estás seguro? | `Up` + `Cross` | Sí |
| MEMORY CARD | `Cross` | slot 1, checagem |
| menu principal | — | as sete linhas |
| **navegação exata** | `pause` + 5 × (`Down` + 12 × `frame_step`) | cursor em `Modo Editar`, quinta linha |

> **Isso não é resultado versionado, e a task existe por isso.** A corrida
> acima usou um cliente MCP descartável no scratchpad. O que ela prova é que
> o caminho funciona; o que falta é a ferramenta que o torna repetível — que
> é o entregável desta task. Nenhum número acima deve ser copiado para outro
> documento antes de sair de script versionado.

Contagem de ferramentas: **95**, e o número da §6.14 está certo. Vale saber
por quê, porque o fonte engana: o `TOOLS_JSON` estático do `mcp_server.cpp`
declara **99** nomes, e quatro deles — `analyze_memory`, `debug_crash`,
`inspect_gpu`, `trace_function` — **não aparecem** no `tools/list`. Contar
pelo fonte dá 99 e está errado; quem manda é o servidor. As de entrada são
seis — `press_button`,
`release_button`, `set_analog`, `input_sequence`, `get_controller_state`,
`list_controllers` — mais `frame_step`, `take_screenshot`, `set_speed`
(inclui `rewind`), `save_state`/`load_state` por slot, `boot_game`,
`shutdown_system` e `trigger_hotkey`.

---

## Objetivo

Substituir a direção por `xdotool` por direção por MCP nas rotas do
`tools/pes2/drive.py` e nos comandos do `tools/pes2/pad.py`, **sem perder
nenhuma capacidade que os dois têm hoje** e sem quebrar o gate `pes2_boot`.

O ganho a comprovar não é velocidade: é **determinismo**. Uma rota que hoje
espera por assinatura de quadro passa a contar quadros, e o que era heurística
vira asserção.

---

## A decisão já está tomada

**2026-09-03, pelo usuário: o fork é o emulador de trabalho.** Isto não é
mais escolha desta task — ela executa. A §6.14 do plano guarda as três
decisões em ordem e o que esta arrasta; o `progresso.md` guarda o resumo.

O que **continua sendo medição** desta task, e não pode ser presumido:

- **As assinaturas de quadro batem entre os dois binários?** A da tela de
  título (0,550 / 0,341) e a do menu (0,1405 / 0,2124) saíram do renderer e
  da versão do AppImage. Duas capturas e uma subtração respondem. Se
  baterem, as rotas atuais funcionam sob o fork sem tocar em número; se não
  baterem, há duas saídas e a boa é a segunda:
  1. remedir as assinaturas sob o fork — mantém a heurística viva, e com ela
     o motivo de ela existir;
  2. **aposentá-las como critério.** Se `frame_step` decide quando a tela
     chegou, média e desvio do quadro viram evidência, não julgamento — que
     é o ganho inteiro desta task. Um número que ninguém usa para decidir
     não precisa ser remedido.
- **Onde o binário passa a morar.** Ele foi compilado no scratchpad da
  sessão, que se apaga. Emulador de trabalho não mora em diretório
  temporário, e a licença CC-BY-NC-ND proíbe versioná-lo — então é um lugar
  fora do repositório e fora do scratchpad, e **a escolha é do dono da
  máquina**: pergunte, não invente. Junto com ela vem a receita de
  reconstruí-lo (clone raso, pack de dependências, `clang-tools-18`,
  `cmake`, 107 s), que hoje só existe no Log da PES2-TASK-33.
- **O que fazer com o AppImage oficial.** Ele continua instalado e continua
  sendo o que um terceiro reproduz. A pergunta é se alguma ferramenta ainda
  aponta para ele de propósito ao fim desta task — e a resposta tem de estar
  escrita, não implícita no código.

---

## O que precisa existir antes das rotas

**O fork não sobe sozinho, e isso não é detalhe.** Medido em 2026-09-03:

- ele abre um diálogo **"You are not using an official release!"** cujo botão
  default é `Yes`, e `Yes` significa *sair e abrir duckstation.org*. Um
  `Return` reflexo — o gesto que o resto do projeto usa — **mata o
  processo**, sem janela e sem porta, parecendo build quebrado;
- **a porta 2346 só abre depois que esse diálogo é dispensado.** Enquanto ele
  estiver na tela, `initialize` recebe `Connection refused`;
- o `run_duckstation.sh` **não serve**: ele lança o AppImage oficial, que não
  tem servidor. O `--kill` dele também não alcança o fork — ele casa `AppRun`
  e `DuckStation-x64`, e o processo do fork se chama `duckstation-qt`
  (armadilha 6 da §6.11, agora com um binário a mais para escapar dela).

Portanto a task entrega, **antes** de qualquer rota, um lançador: sobe o fork,
dispensa o aviso, espera a porta responder `initialize`, e falha alto com o
motivo se algum dos três não acontecer. Python, pela regra do ferramental.

E entrega o cliente MCP como módulo versionado — `initialize`, sessão por
`MCP-Session-Id`, `tools/call` — que hoje só existe como rascunho no
scratchpad.

---

## `.mcp.json`

O servidor foi registrado no projeto em 2026-09-03 a pedido do usuário:

```json
{ "mcpServers": { "duckstation": { "type": "http",
    "url": "http://127.0.0.1:2346/mcp" } } }
```

**Decidido em 2026-09-03 pelo usuário: entra, em escopo `project`.** Os dois
pontos que pesavam contra e a favor ficam registrados, porque o segundo é um
efeito real que quem clonar vai ver:

- ele publica um endereço de `localhost`, **não** o fork — dentro da regra de
  licença da §6.14, que proíbe versionar ou publicar o binário;
- mas ele descreve um servidor que **só existe nesta máquina**: num clone
  sem o fork compilado, a entrada aparece como servidor quebrado. Escopo
  `local` evitaria isso ao custo de o repositório não documentar nada — e
  documentar ganhou.

Resta desta seção uma coisa só, e é de execução: a entrada exige **aprovação
manual** na primeira sessão (`claude mcp list` mostra `⏸ Pending approval`),
o que é uma pegadinha a registrar junto das do lançador.

---

## Critério de conclusão

- [x] Um cliente MCP versionado em `tools/pes2/`, com `initialize`, sessão e
      `tools/call`, e um caso vermelho para servidor ausente que diga
      "o fork não está rodando" em vez de despejar um traceback de `urllib`.
- [x] Um lançador do fork que dispensa o aviso de build não-oficial e espera
      a porta, com as três falhas acima distinguidas na mensagem.
- [x] As quatro rotas do `drive.py` — `title`, `main-menu`, `team-select`,
      `edit` — reproduzidas por MCP, **e a comparação medida** contra as
      atuais: tempo de relógio e número de tentativas até a tela.
- [x] Pelo menos uma rota que hoje espera por assinatura de quadro passando a
      contar quadros, com a asserção que isso permite escrita como caso
      vermelho: uma tecla a mais deve **falhar**, não passar despercebida.
- [x] As assinaturas de quadro do fork medidas contra as do AppImage, e o
      resultado escrito na §6.14 — remedidas, ou aposentadas como critério
      com o motivo.
- [x] O lugar definitivo do binário do fork combinado com o usuário, e a
      receita de reconstruí-lo fora do Log de uma task concluída.
- [x] O `pes2_boot` continua verde, e o log diz **contra qual binário** ele
      correu. Se a decisão for o fork, ele foi remedido; se for conviver, o
      gate diz qual dos dois julga.
- [x] O `pad.py` — que é a ferramenta de trabalhar **junto com o usuário**,
      no `:1` — decidido: portado, mantido em `xdotool` ou aposentado. Ele
      tem um caso que as rotas não têm, o `run` que dá `Cross` em cada saque,
      e esse caso tem de continuar existindo em alguma forma.
- [x] As armadilhas novas na §6.11, com a contagem da seção **recontada**, não
      incrementada de cabeça — ela já envelheceu duas vezes (§6.14 dizia
      "vinte", o perfil dizia "treze", e o `awk` contava 26).
- [x] `.mcp.json` decidido: commitado com o escopo justificado, ou removido em
      favor de escopo local, com o motivo escrito.
- [x] Nada do fork no repositório. Sobre cópia, sempre — `roms/` intocada.

---

## Armadilhas que esta task herda

- **Uma instância por vez, e agora são dois binários.** O `--kill` do
  `run_duckstation.sh` casa `AppRun` e `DuckStation-x64`; o fork é
  `duckstation-qt` e escapa. Instância órfã segurando o `:98` é a armadilha 6
  da §6.11, e o custo dela é dirigir a janela errada.
- **`pgrep -f` casa a linha de comando do próprio shell** (armadilha 25), e
  `pkill -f` sobre ela **mata o próprio shell** — aconteceu duas vezes.
- **`xdotool windowkill` mata o processo inteiro**, não a janela (armadilha
  27): ele encerra o cliente X.
- **O lançador não escreve configuração** desde 2026-09-02 (armadilha 4). O
  `EnableMCPServer` mora no `settings.ini` do usuário e já está lá, com
  autorização; **não o reescreva**, e confira com `diff` contra
  o estado anterior se mexer.
- **O emulador roda no `:98`.** Abrir no `:1` exige pedido explícito do
  usuário (§6.10) — o `pad.py` existe justamente para o caso em que ele pede.

---

## Log de Execução

**Executado em:** 2026-09-03

## Resumo do que foi feito

As quatro rotas passaram a ser dirigidas por MCP, e o que a task esperava
provar sobre as assinaturas de quadro **saiu diferente do previsto**. A
premissa era "trocar de binário invalida as assinaturas"; o que se mediu é
que **toda média sobreviveu** — à troca de binário, a uma troca de
configuração e à virada do dia — e que o **desvio da tela de título não
reproduz em binário nenhum**: o AppImage é o mesmo arquivo de 29 de agosto,
intocado, e hoje dá 0,3587 onde deu 0,341 anteontem. Quatro hipóteses foram
medidas e descartadas (o fork, o caminho de captura, a escala de resolução, o
recorte), e a causa continua não identificada. O par saiu de critério não
porque mudou com o fork, mas porque **não se reproduz nem se explica um dia
depois no mesmo binário** — o que é um argumento melhor do que o que a task
tinha.

No lugar dele entrou a asserção que contar quadro permite. Com o emulador
parado entre um toque e o próximo, a mesma linha de menu difere de si mesma
por 0,0002..0,0005 e de outra por 0,0082..0,0125 — vinte vezes de distância —,
e sobre isso o `menu_pick` assere que **todo toque moveu** e que **nenhum caiu
numa linha já visitada**. A segunda é o caso vermelho pedido: a lista dá a
volta, então uma tecla a mais falha em vez de confirmar o item errado. O
`--measure-menu` mede as sete linhas do menu e depois pede sete, o que tem de
falhar, e falha.

Cinco defeitos foram encontrados **por rodar**, não por ler, e cada um virou
armadilha na §6.11: o `RUNPATH` absoluto que impedia o binário de achar as
próprias bibliotecas fora da árvore de build; o filtro de `kill_leftovers`
sensível a maiúsculas, que descartava o fork logo depois de a lista de nomes
passar a encontrá-lo; a imobilidade exata, que só serve em tela realmente
parada e "funciona por sorte de fatia" nas outras quatro; o teste de preto,
que parava no splash e deixou a rota devolver `mean=0.000000` declarando
sucesso; e o custo de 57 ms por `frame_step`, que obriga a dividir quadro para
precisão e relógio para distância.

E duas coisas que a §6.14 afirmava foram medidas e estão erradas: o diálogo
que o fork abre é o `Automatic Updater`, não o de build não-oficial, e
`Escape` não o fecha; e a **porta 2346 abre antes** de ele ser dispensado.

## Arquivos criados/modificados

- `tools/pes2/mcp.py` — **novo.** O cliente MCP, stdlib pura: `initialize`,
  sessão por `MCP-Session-Id`, `tools/call`, decodificação de JSON e de SSE
  de um evento, e o caso vermelho de servidor ausente.
- `tools/pes2/fork.py` — **novo.** O lançador: acha o fork em
  `~/Applications/duckstation-mcp/`, monta `LD_LIBRARY_PATH` e
  `QT_PLUGIN_PATH`, dispensa o modal, espera o `initialize`, e distingue as
  quatro falhas. `kill` alcança os três nomes de processo; `recipe` imprime
  como reconstruí-lo; `status` diz qual binário está rodando.
- `tools/pes2/mcp_drive.py` — **novo.** As quatro rotas por MCP, o
  `menu_pick` que conta linhas e o `--measure-menu` que exercita o caso
  vermelho contra o jogo vivo.
- `tools/pes2/pad.py` — portado para MCP. Mesmos cinco comandos, incluindo o
  `run` que dá `Cross` em cada saque.
- `tools/pes2/boot_check.sh` — prefere o fork, cai para o AppImage, e a linha
  final diz contra qual dos dois correu. `PES2_BINARY` força.
- `tools/pes2/run_duckstation.sh` — o `--kill` alcança `duckstation-qt`, e o
  filtro de `/proc/*/cmdline` ficou insensível a maiúsculas.
- `tools/pes2/selftest.py` — os três `self_check` novos entraram no
  `pes2_selftest`.
- `docs/PLAN-PES2-PSX.md` — a §6.11 foi de 27 para **34** armadilhas
  (recontadas, não incrementadas), e a §6.14 ganhou a seção de resultado
  desta task: onde o binário mora, as assinaturas medidas, a asserção, a
  comparação e o que ficou decidido. As duas afirmações erradas da seção
  ficaram no lugar, com a correção medida ao lado.
- `docs/prompts/perfil-pes2.md` — a armadilha 12, o quadro de gates e o
  parágrafo do emulador, que agora descreve **dois** binários e diz qual
  ferramenta usa qual.
- `CLAUDE.md` — a tabela de ferramentas de PES2 e a nota do emulador.
- `docs/tasks/progresso.md`, `docs/tasks/34-rotas-mcp-no-lugar-do-drive.md`.

Fora do repositório, por licença: o binário do fork foi instalado em
`~/Applications/duckstation-mcp/` (249 MB), escolhido pelo usuário.

## Problemas encontrados

- **A comparação de tempo exigiu as duas séries inteiras.** As quatro rotas
  foram corridas dos dois lados na mesma máquina e no mesmo `:98`:
  274,54 s por `xdotool` contra 116,93 s por MCP. Mas nesta corrida o
  `drive.py` **não precisou de nenhuma repetição**, o que é sorte e é
  justamente o ponto: uma tentativa que nem sempre é necessária não pode ser
  assegurada. O ganho a registrar é que a coluna "tentativas" deixou de
  existir.
- **`pgrep -f`/`pkill -f` casou a linha de comando do próprio shell de novo**
  — armadilha 25, agora contra `mcp_drive.py` — e matou a tarefa de fundo
  junto. É o motivo de o `fork.running_pids()` usar `pgrep -x`.
- **Três rotas falharam antes de fechar**, e as três por presumir imobilidade:
  o menu principal (bola girando), a atribuição de controle (pisca entre duas
  imagens) e a grade de bandeiras (cursor piscando). Cada uma custou uma
  corrida.

