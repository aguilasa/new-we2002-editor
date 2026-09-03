---
id: PES2-TASK-33
title: "Compilar o fork e validar o MCP de fato"
type: decisão
category: ferramental
phase: 0
depends_on: [PES2-TASK-32]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §6.14"
status: concluído
---

# PES2-TASK-33: Compilar o fork e validar o MCP de fato

## Contexto

- **Referência:** [`/docs/PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md) §6.14.
- **Existe porque a [PES2-TASK-32](/docs/tasks/32-poc-do-mcp-do-duckstation.md)
  não fez isto.** Ela se chamava "prova de conceito do MCP" e fechou **sem
  jamais baixar o fork, compilar ou falar com o servidor**. O que ela mediu foi
  o caminho alternativo — o save state —, concluiu que ele cobria os fluxos C e
  D, e daí decidiu que o fork não se justificava. É uma decisão defensável, mas
  ela responde a outra pergunta: *"preciso do MCP?"*, e não *"o MCP funciona?"*.
  A segunda continua sem resposta medida.

O usuário pediu a validação de fato. Esta task existe para não deixar a
diferença entre as duas perguntas enterrada num critério marcado.

**E o escopo encolheu, o que é bom.** Como a TASK-32 entregou C e D em Python
puro (`tools/pes2/savestate.py`), o MCP só precisa provar o que o save state
**não** dá:

| fluxo | ferramentas | por que só ele importa agora |
|---|---|---|
| **A — quem escreve** | `breakpoint` de escrita, `read_registers`, `disassemble` | do endereço de RAM ao **carregador**, e dele ao offset no disco. É o laço disco↔RAM, hoje feito só por cutucar e olhar |
| **E — verificar ASM** | `read_memory`, `disassemble`, `breakpoint` de execução | confirmar que um disco remendado carregou o que se esperava |

Um save state é uma foto: ele diz *o que* a RAM contém, nunca *quem* escreveu.
Só um breakpoint diz isso, e é por isso que A e E não têm substituto barato.

---

## Objetivo

Baixar `sadnescity/duckstation` na branch `mcp`, compilar, subir o servidor,
conectar, e **usar as ferramentas** para responder uma pergunta que este
projeto tem em aberto.

A pergunta escolhida: **quem escreve o placar da partida?** O endereço já é
conhecido e verificado — `0x0007151B` (u16) e `0x00137C12` (u8) — publicados pela
TASK-32 em oito leituras, de 0-1 a 0-6 mais um 0-17 de outra sessão. Ter o alvo
pronto é o que torna esta POC pequena: ela não gasta nada descobrindo *onde*
olhar, só mede se a ferramenta consegue dizer *quem* mexe ali.

---

## Critério de conclusão

- [x] **Compilou, e a premissa de custo da §6.14 estava errada.** Clone raso
      **8,16 s** / 180 MB; pack de dependências **2,43 s** / 44 MB → 204 MB;
      `cmake` **3,74 s**; **compilação 107 s**, 464 alvos em 16 núcleos;
      árvore de build 324 MB. Menos de três minutos do zero ao binário, não
      "dias". Uma falha no caminho, registrada verbatim no Log: faltava
      `clang-scan-deps`.
- [x] O servidor responde. `duckstation-mcp` 1.0.0 em `127.0.0.1:2346`,
      protocolo `2025-11-25`, Streamable HTTP com `MCP-Session-Id`, e
      `tools/list` devolvendo **95** ferramentas — o número que a §6.14
      citava do README, agora medido.
- [x] **Fluxo A completo.** `breakpoint` de escrita em `0x0007151B`, o jogo
      dirigido até uma partida nova, e ele disparou em `PC = 0x80083578`. O
      `disassemble` em volta dá `sb zero, 0x21a(v0)` com `addr=0x8007151b`,
      num bloco de `sb zero` em sequência, com `s0 = 0x80071300` e
      `ra = 0x800834C0`.
- [x] O que isso permite concluir: **o placar é o campo `+0x21B` de um
      registro baseado em `0x80071300`**, zerado pela rotina em `0x80083560`
      no reinício de partida. Um save state não dá isso — ele diz o que a
      memória contém, nunca quem escreveu.
- [x] Nenhuma assinatura de quadro se moveu, porque **nada correu sob o fork
      além do diagnóstico**: as rotas do `drive.py` seguem medidas contra o
      AppImage oficial, e o `pes2_boot` fechou verde depois.
- [x] §6.14 reescrita com os números medidos, e a decisão nova: **o fork
      entra como ferramenta de diagnóstico**, não como emulador de trabalho.
- [x] Nada do fork entrou no repositório. Entraram o procedimento, os
      números, e a correção do `savestate.py` que o confronto revelou.
- [x] Sobre cópia — `roms/` intocada.
- [x] O `settings.ini` do usuário mudou em **duas linhas**, com autorização
      explícita e `diff` mostrando só elas; digest `6791b8d4` → `c9588a68`.
      Os save states não foram alterados.

---

## O que medir antes de compilar

Compilar um emulador C++ é a parte cara, e três coisas podem matar a task
antes disso. Meça-as primeiro e, se alguma reprovar, a task fecha ali com o
motivo — que é resultado legítimo.

1. **O `ninja` não está instalado** nesta máquina (`cmake` 3.28.3 e `g++`
   13.3.0 estão). O DuckStation pede `ninja`; instalar é decisão do dono da
   máquina, como foi a do `numpy` na
   [PES2-TASK-01](/docs/tasks/01-ferramental-das-fases-3-e-4.md). **Pergunte.**
2. **As dependências do DuckStation** — Qt 6, SDL2, shaderc, SPIRV-Cross,
   libbacktrace. O projeto tem um script de dependências; ver o que ele quer
   antes de assumir que `apt` resolve.
3. **Espaço.** Há 973 GB livres em `/home`, então isto não deve travar nada,
   mas a árvore de build entra no scratchpad e não no repositório.

E uma quarta, que não é técnica: o fork tem **3 estrelas, 0 forks e um autor**.
Compilá-lo é rodar código de terceiro com acesso à memória do emulador. Não é
motivo para não fazer — é motivo para o usuário saber que está sendo feito.

---

## Armadilhas que esta task herda

- **Uma instância por vez.** O `--kill` do `run_duckstation.sh` não distingue
  display **nem binário**: ele casa `AppRun` e `DuckStation-x64`. Um build do
  fork provavelmente roda com **outro nome de processo**, e aí o `--kill` não o
  alcança — o que deixa instância órfã segurando o `:98` e faz a corrida
  seguinte dirigir a janela errada, que é a armadilha 6 da §6.11.
- **`pgrep -f` casa a linha de comando do próprio shell** (armadilha 25).
- **O lançador não escreve configuração** desde 2026-09-02 (armadilha 4): quem
  manda é o `settings.ini` da máquina. O fork precisa de
  `EnableMCPServer = true` **nesse** arquivo, e mexer nele é mexer na
  configuração do usuário — **pergunte antes**.
- O `:98` é o default; abrir no `:1` exige pedido explícito (§6.10).

---

## Log de Execução

**Executado em:** 2026-09-03
**Superada em:** 2026-09-03 — a decisão que fecha esta task, *"o fork entra
como ferramenta de diagnóstico, não como emulador de trabalho"*, foi
**revista pelo usuário no mesmo dia**: o fork passa a ser o emulador de
trabalho, pelo fluxo F — dirigir o jogo por MCP em vez de `xdotool`. O que
está escrito abaixo é o que esta task mediu e continua valendo como
evidência; o que a troca de binário arrasta está na §6.14 do plano e é a
[PES2-TASK-34](/docs/tasks/34-rotas-mcp-no-lugar-do-drive.md).

**Resumo.** O fork compila em **107 segundos**, o servidor MCP responde, e o
fluxo A entregou o que nenhum save state entrega. Mas o achado que mais vale
não foi sobre o MCP: **o confronto entre as duas ferramentas expôs um erro de
45 bytes no nosso `savestate.py`**, e foi o critério "duas ferramentas
independentes no mesmo número" que o pegou.

**A premissa de custo estava errada.** A §6.14 recusava o fork dando como
motivo "compilar 12.330 commits de C++". Medido: clone raso 8,16 s / 180 MB,
pack de dependências 2,43 s, `cmake` 3,74 s, **build 107 s** em 16 núcleos,
324 MB de árvore. O que faltava era um pacote — `clang-tools-18`, pelo
`clang-scan-deps` que o CMake usa para módulos C++20 —, e a primeira tentativa
morreu com `CMAKE_CXX_COMPILER_CLANG_SCAN_DEPS-NOTFOUND: not found`.

**O erro de 45 bytes, e por que ele sobreviveu.** O critério pedia que
`read_memory` e o `savestate.py` concordassem. Não concordaram: `12 13 14 15`
contra `11 00 00 00`. Despejando os 2 MiB pelos dois caminhos, a marca do
kernel caiu em **29236** no barramento e **29191** no leitor — 45 bytes. Com
o deslocamento aplicado, **99,95%** do primeiro MiB bate; sem ele, **13,17%**.

A causa é a derivação: `start = dma - size` supõe que a RAM é a última coisa
que a seção `Bus` escreve, e não é — `MEMCTRL.regs` e `RAM_SIZE.bits` vêm
depois. O certo conta **para frente** a partir da tag, e sai do
`Bus::DoState` do próprio DuckStation, que agora tenho em mãos: 4+3 da tag,
4 do `ram_size`, cinco `std::array<TickCount,3>` — **71 bytes**.

Duas coisas conspiraram para esconder isso por um dia:

1. **busca e leitura usavam a mesma base errada**, então as oito leituras da
   PES2-TASK-32 batiam com a tela. O valor estava certo; o endereço, não;
2. **a guarda perguntava se a marca existe, não onde ela está** — e a fixture
   do `selftest` plantava a marca em `0x7207` = 29191, o valor já deslocado.
   Guarda e defeito concordavam, então a guarda nunca podia ficar vermelha.

As duas foram corrigidas, e a guarda nova tem caso vermelho próprio: uma
marca 45 bytes fora é recusada com a conta na mensagem
(`the kernel marker is at 29281, not 29236`).

**O que o fluxo A entregou.** Breakpoint de escrita, o jogo dirigido até uma
partida nova, disparo em `PC = 0x80083578`. O `disassemble` mostra um bloco
de `sb zero` em sequência, com `sb zero, 0x21a(v0)` apontando exatamente para
`0x8007151b`, e os registradores dão `s0 = 0x80071300`. Ou seja: **o placar é
o campo `+0x21B` de uma estrutura de partida em `0x80071300`**, limpa pela
rotina em `0x80083560`. Isso é o laço que o projeto não fechava.

**Licença, e ela restringe o uso.** O binário avisa na abertura que o
DuckStation é **CC-BY-NC-ND-4.0** e que build modificado não pode ser
distribuído. Uso local não é distribuição, mas isso proíbe versionar ou
publicar o fork — mesma regra de `roms/` e do `we-team-editor.exe`.

**Isolação: impossível também com build nativo.** HOME próprio cai no
assistente de configuração mesmo com `SetupWizardIncomplete = false`, e a
página de BIOS recusa `Next` mesmo com `SearchDirectory` absoluto. Confirma a
armadilha 20 de forma independente — não era peculiaridade do AppImage. O
fork rodou sobre o diretório do usuário, que ganhou `[Debug] EnableMCPServer`
e `MCPServerPort` com autorização explícita.

**Arquivos criados/modificados**

- `tools/pes2/savestate.py` — a derivação corrigida, a guarda de índice e o
  caso vermelho dela; a fixture do `selftest` deixou de modelar o bug
- `docs/PLAN-PES2-PSX.md` — §6.14 reescrita com os números medidos e a
  decisão nova; os dois endereços corrigidos com o aviso do que diziam;
  armadilha **27** (o `windowkill`)
- `docs/tasks/32-poc-do-mcp-do-duckstation.md` — os endereços corrigidos e a
  nota de correção datada
- `docs/tasks/progresso.md` — esta task

**Problemas encontrados.** Quatro. O `clang-scan-deps` ausente, que parou o
primeiro build. O `xdotool windowkill` que matou o emulador inteiro em vez do
diálogo — virou a armadilha 27. Um teste meu invertido, em que
`grep '"running"'` nunca casava porque o JSON escapa as aspas, e eu li
"parou" onde estava escrito "rodando". E o de fundo: **eu publiquei na
PES2-TASK-32 dois endereços que estavam errados**, com uma guarda que não
podia reprová-los porque a fixture fora construída em torno do mesmo engano.

**Pendência encaminhada.** Nenhuma. As correções entraram aqui.
