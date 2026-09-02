---
id: PES2-TASK-32
title: "Prova de conceito do MCP do DuckStation"
type: decisão
category: ferramental
phase: 0
depends_on: []
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §6.14"
status: pendente
---

# PES2-TASK-32: Prova de conceito do MCP do DuckStation

## Contexto

- **Referência:** [`/docs/PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md) §6.14, que
  registra a avaliação de 2026-09-02 e a decisão de **não adotar então**.
- Fase 0 pelo mesmo motivo da [PES2-TASK-01](/docs/tasks/01-ferramental-das-fases-3-e-4.md):
  é decisão sobre ferramental da máquina, não sobre o disco.

A §6.14 avaliou o
[`duckstation-claude-plugin`](https://github.com/sadnescity/duckstation-claude-plugin)
e recomendou esperar. Esta task **não revisita a recomendação**: o usuário
pediu a prova de conceito, e o que ela tem de decidir é se a ferramenta
funciona *nesta máquina* e se entrega o que promete. Recomendação e medição
são coisas diferentes, e a segunda ganha.

**O que ela resolveria, se funcionar.** O item 4 da §4.2 — a desmontagem do
MIPS, que o plano chama de "último recurso, e o mais caro". Quatro dos sete
fluxos dele batem no que o projeto não sabe fazer:

| fluxo | ferramentas | o que destravaria |
|---|---|---|
| C — busca de valor | `memory_scan`, `read_memory` | o endereço de RAM de um atributo pelo valor em tela |
| A — quem escreve | `breakpoint` de escrita, `read_registers`, `disassemble` | do endereço ao carregador, e dele ao offset no disco |
| D — diff de memória | `snapshot_memory`, `diff_memory` | "o que o Modo Editar muda?", que é a PES2-TASK-05 em RAM |
| E — verificar ASM | `read_memory`, `disassemble` | confirmar que um disco remendado carregou o que se esperava |

**O que ela custa, medido em 2026-09-02.** Um fork de terceiro do emulador —
`sadnescity/duckstation`, branch `mcp`, **3 estrelas e 0 forks**, sem binário
publicado. `EnableMCPServer` **não existe** no AppImage oficial: conferido por
`strings` sobre o binário extraído, onde as únicas ocorrências de `2346` são
número de linha de `fullscreenui_settings.cpp`.

---

## Objetivo

Decidir, **por medição e não por leitura**, se o MCP do DuckStation entra no
ferramental deste projeto.

A prova de conceito é pequena de propósito: um fluxo só, ponta a ponta, com um
número no fim. O escolhido é o **C**, busca de valor, porque é o mais barato de
julgar — ou o endereço aparece, ou não aparece — e porque é o que os outros
três pressupõem.

### O que a POC tem de mostrar

Achar, pela RAM, **onde vive o placar da partida**. É um bom alvo por três
razões: o valor está visível em tela, muda de forma controlada (um gol), e já
sabemos chegar nele — a rota `team-select` mais o laço do `pad.py run` põem uma
partida em campo em ~3 minutos, e há save state parkado.

Sequência: colocar uma partida em andamento, `memory_scan` pelo placar do
mandante, provocar um gol, filtrar por valor aumentado, e repetir até restar
um punhado de endereços. Depois `read_memory` neles e conferir contra a tela.

---

## Critério de conclusão

- [ ] O fork compila **ou** se decide, com o motivo escrito, que compilar não
      vale — e nesse caso a task fecha como decisão negativa, que é resultado
      legítimo. O tempo de compilação medido entra no registro.
- [ ] O servidor MCP responde: as ferramentas aparecem, e uma leitura trivial
      (`read_memory` num endereço qualquer da RAM) devolve bytes.
- [ ] O fluxo C completo: o endereço do placar isolado, e `read_memory` nele
      batendo com o número na tela **em duas leituras diferentes** — 0-1 e
      0-2, por exemplo. Uma leitura só não distingue acerto de coincidência.
- [ ] Medido quanto custa uma corrida com o fork **contra** o AppImage oficial:
      se as assinaturas de quadro do `drive.py` mudarem, está registrado quais
      e quanto, porque `TITLE`, `MAIN_MENU` e `TEAM_SELECT` são medidas do
      binário oficial (§6.11, armadilha 15).
- [ ] A recomendação da §6.14 **reescrita** com o que a POC mediu — adotar,
      não adotar, ou adotar só para uma fase. O texto atual diz "reavaliar
      quando o projeto chegar na fase de RAM/MIPS"; esta task é essa
      reavaliação e o parágrafo tem de deixar de ser previsão.
- [ ] Nada do fork entra no repositório. Ele é binário de terceiro sem
      licença nossa, mesma regra do `we-team-editor.exe` e de `roms/`. O que
      entra é o **procedimento** e os números.
- [ ] Roda sobre **cópia** da imagem, nunca `roms/`.

---

## O caminho mais barato, a medir antes

**Um save state contém a RAM inteira**, o `F2` funciona — provado em
2026-09-02 — e o `zstd` está na máquina (CLI 1.5.5). Os estados medidos têm
1,55 a 1,85 MB comprimidos contra os 2 MiB de RAM do PSX, o que bate.

Se o formato do arquivo for legível, os fluxos **C** e **D** saem em Python
puro, sem fork nenhum: dois estados antes e depois de um gol dão o diff de
memória, e vários estados com o placar mudando dão a busca de valor. Não dão
breakpoint nem disassembly — para esses o fork é insubstituível.

**Meça isso primeiro.** É uma corrida, contra dias de compilação, e se
funcionar muda o que a POC do fork precisa provar: ela passa a ter de
justificar só os fluxos A e E.

> O layout do save state **não foi lido**. O parágrafo acima é inferência a
> partir do tamanho, e está escrito como inferência de propósito.

---

## Armadilhas que esta task herda

- **`SaveStateCompression = ZstDefault`** no `settings.ini` da máquina. Trocar
  para `Uncompressed` na interface do DuckStation dispensa o descompressor —
  e lembrar que, desde 2026-09-02, **o lançador não escreve configuração**: a
  do emulador é a que vale (§6.11, armadilha 4).
- **Uma instância por vez.** O `--kill` do `run_duckstation.sh` não distingue
  display: rodar o gate `pes2_boot` fecha qualquer sessão aberta, inclusive
  uma no `:1`.
- **`pgrep -f` casa a linha de comando do próprio shell** (armadilha 25).
- O `:98` é o default; abrir no `:1` exige pedido explícito do usuário (§6.10).

---

## Log de Execução

*(a preencher)*
