---
id: PES2-TASK-33
title: "Compilar o fork e validar o MCP de fato"
type: decisão
category: ferramental
phase: 0
depends_on: [PES2-TASK-32]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §6.14"
status: pendente
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
conhecido e verificado — `0x000714EE` (u16) e `0x00137BE5` (u8), medidos pela
TASK-32 em oito leituras, de 0-1 a 0-6 mais um 0-17 de outra sessão. Ter o alvo
pronto é o que torna esta POC pequena: ela não gasta nada descobrindo *onde*
olhar, só mede se a ferramenta consegue dizer *quem* mexe ali.

---

## Critério de conclusão

- [ ] O fork **clonado e compilado**, com o tempo de compilação e o espaço em
      disco medidos e escritos. Se não compilar, o erro entra no Log
      **verbatim** — "não compilou" sem a mensagem não é resultado.
- [ ] O servidor MCP responde: as ferramentas aparecem na lista, e
      `read_memory` em `0x000714EE` devolve o placar que está na tela.
      Conferir contra o `savestate.py`, que já sabe ler esse mesmo endereço —
      **duas ferramentas independentes no mesmo número** é o que separa
      "funcionou" de "parece que funcionou".
- [ ] **Fluxo A completo:** um `breakpoint` de escrita em `0x000714EE`, um gol
      provocado, e o endereço da instrução que disparou o breakpoint
      registrado, com o `disassemble` em volta dela. Um endereço de código, não
      "o breakpoint disparou".
- [ ] O que esse endereço de código **permite concluir** sobre o disco, ainda
      que a conclusão seja "nada por enquanto". A POC prova a ferramenta; se a
      ferramenta não leva a lugar nenhum útil aqui, isso é o resultado.
- [ ] O custo de uma corrida sob o fork medido **contra** o AppImage oficial, e
      as assinaturas de quadro do `drive.py` reconferidas: `TITLE`,
      `MAIN_MENU` e `TEAM_SELECT` são medidas do binário oficial, e a
      armadilha 15 da §6.11 diz que tecla funcionando não prova qual binário
      respondeu. Se mudarem, **quais e quanto**.
- [ ] A §6.14 reescrita outra vez, agora com o fork medido em vez de estimado.
      Ela hoje diz "não compilar o fork" e dá como motivo o custo **suposto**;
      depois desta task o motivo passa a ser um número, para um lado ou para o
      outro.
- [ ] Nada do fork entra no repositório — binário e fonte de terceiro, mesma
      regra do `we-team-editor.exe` e de `roms/`. Entram o procedimento, os
      números e, se houver, um wrapper em Python.
- [ ] Roda sobre **cópia** da imagem, nunca `roms/`.
- [ ] Os save states do usuário copiados antes e devolvidos byte a byte
      depois, com `cmp` limpo — como a TASK-32 fez.

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

*(a preencher)*
