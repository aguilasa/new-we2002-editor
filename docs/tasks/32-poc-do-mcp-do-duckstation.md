---
id: PES2-TASK-32
title: "Prova de conceito do MCP do DuckStation"
type: decisão
category: ferramental
phase: 0
depends_on: []
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §6.14"
status: concluído
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

- [x] **Decisão negativa, com o motivo escrito: o fork não foi compilado.**
      O caminho barato que a própria task mandava medir primeiro entregou os
      fluxos C e D em Python puro, e com isso a POC do fork passaria a ter de
      justificar só A e E — que este projeto não precisa hoje. O custo que
      ela evita está reconferido, não relembrado: `sadnescity/duckstation`
      tem 3 estrelas, 0 forks, 12.330 commits na branch `mcp`, e **nenhuma
      release própria** — a página que o README aponta é a do upstream
      `stenzek/duckstation`, que é justamente o build sem o servidor.

      *Corrigido em 2026-09-03 pela
      [CORR-PES2-028](/docs/tasks/CORR-PES2-028.md):* três dos quatro números
      continuam certos, e **"nenhuma release própria" é falso**. O fork
      publica quatorze ativos na release `latest`, de 2026-08-29, e o
      `DuckStation-x64.AppImage` dela **traz o servidor MCP**. A frase sobre
      o README continua verdadeira e foi justamente o que enganou: o README é
      o do upstream, e a aba de releases do próprio fork nunca foi aberta. A
      decisão desta task não muda por isso — ela se sustentava no caminho
      barato ter entregado os fluxos C e D —, mas a conta de custo estava
      errada duas vezes: nem dias, nem os 107 s que a PES2-TASK-33 mediu, e
      sim um download.
- [x] Sem servidor MCP para responder, a leitura trivial de RAM foi feita
      pelo outro caminho: `savestate.py read` devolve bytes de qualquer
      endereço, e a extração passa por uma guarda de kernel que a faz falhar
      alto quando o deslocamento está errado.
- [x] **Fluxo C completo, e com oito leituras em vez de duas.** O placar
      visitante caiu de 130 candidatos (2 leituras) para 2 (8 leituras), e os
      dois sobreviventes — `0x0007151B` u16 e `0x00137C12` u8 — batem com o
      número na tela em 0-1, 0-2, 0-3, 0-4, 0-5, 0-6 e, numa partida de
      **outra sessão**, 0-17. Não são candidato e ruído: são duas cópias
      vivas do placar, que é o mesmo padrão que a §6.1 cobra do texto.
- [x] Não se aplica na forma escrita, e o motivo é o resultado: **o binário
      não mudou**. Toda a POC correu sobre o AppImage oficial, então nenhuma
      assinatura de quadro do `drive.py` se moveu — o `pes2_boot` fechou
      verde depois da corrida, em 91,54 s.
- [x] §6.14 reescrita. Ela deixou de dizer "reavaliar quando o projeto chegar
      na fase de RAM/MIPS" e passou a registrar o formato do save state, o
      funil da varredura, os números do fluxo D e a decisão datada. A §4.2,
      item 4, que apontava para a previsão, aponta agora para o caminho que
      funciona.
- [x] Nada do fork entrou no repositório, e nada dele foi baixado. Entraram
      o procedimento, os números e `tools/pes2/savestate.py`.
- [x] Correu sobre a cópia de `(EsIt)` no scratchpad — `roms/` intocada. Os
      três save states do usuário foram copiados antes e devolvidos byte a
      byte depois (`cmp` limpo nos três).

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

> *"Dias de compilação" não se sustentou* — a PES2-TASK-33 mediu **107 s** de
> build, e a CORR-PES2-028 achou o binário pronto que o CI do fork publica. O
> resultado desta task não muda; a premissa de custo do parágrafo acima, sim.

> O layout do save state **não foi lido**. O parágrafo acima é inferência a
> partir do tamanho, e está escrito como inferência de propósito.
>
> **Lido em 2026-09-02, e a inferência estava certa.** A RAM está inteira lá,
> e os fluxos C e D saíram em Python puro. O formato, o funil da varredura e
> os números estão na §6.14 do plano; o leitor é `tools/pes2/savestate.py`.

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

**Executado em:** 2026-09-02
**Corrigido em:** 2026-09-03 — os dois endereços publicados aqui estavam
deslocados 45 bytes, porque o `savestate.py` derivava o início da RAM
contando para trás a partir da tag `DMA`. A
[PES2-TASK-33](/docs/tasks/33-compilar-e-validar-o-mcp.md) achou o erro ao
confrontar o leitor com o servidor MCP, e os números acima já são os certos.
As leituras desta task continuam válidas — o que estava errado era o
endereço, nunca o valor.

O **deslocamento** ficou para trás naquela reconciliação e só foi corrigido em
2026-09-03 pela [CORR-PES2-026](/docs/tasks/CORR-PES2-026.md): o Resumo abaixo
dizia 6799, e o leitor mede **6754**. Os dois números se movem em sentidos
opostos — a base desce 45, os endereços sobem 45 —, então procurar pelo
endereço publicado não encontra o deslocamento que o produziu.

**Resumo.** O caminho barato funciona, e por isso o fork não foi compilado.
Um save state do DuckStation (formato versão 86) é um cabeçalho fixo, um
screenshot e **um frame zstd** cujo conteúdo é uma sequência de seções com
nome prefixado por tamanho; os 2 MiB de RAM principal são a cauda de `Bus`,
encostados na marca `DMA`. O deslocamento **se deriva** — `Bus` abre com o
tamanho da RAM, e a RAM termina onde `DMA` começa — e nos estados desta
máquina cai em **6754**, que é resultado e não constante. (Este Resumo dizia
6799 até 2026-09-03 — ver o bloco **Corrigido em** acima.)

O fluxo C fechou com oito leituras: 130 candidatos com duas, 2 com oito. Os
dois sobreviventes são placar de verdade, e é isso que ensina — **o motor
guarda o placar em mais de um lugar**, exatamente como guarda o nome de time
em oito tabelas (§6.1). Um editor de RAM que gravasse uma cópia só repetiria
o modo de falha do `poke`.

Três coisas medidas que valem para a PES2-TASK-05 e adiante:

- a leitura 4 repetiu o valor 0-3 e **cortou quase nada** (8 para 6): o que
  filtra é valor *diferente*, não estado a mais;
- o fluxo D entre dois estados a um gol de distância mexe em **7,11% da
  RAM**, porque a partida é viva. Diff de memória só é barato em tela
  estática — que é o cenário do Modo Editar;
- o placar **só aparece na tela em parada de jogo**, então o instante de
  salvar é o congelamento do relógio, não um momento qualquer. O laço de
  coleta é o do `pad.py run` com um save no meio.

**Arquivos criados/modificados** (conferidos contra `git show --stat`):

- `tools/pes2/savestate.py` — novo. Leitor do save state, `scan` (fluxo C),
  `diff` (fluxo D), `read`, `ram`, `shot`, `info` e `selftest`.
- `tools/pes2/selftest.py` — chama o `self_check()` do leitor, para o
  `pes2_selftest` cobri-lo numa máquina sem emulador, sem disco e sem zstd.
- `docs/PLAN-PES2-PSX.md` — §6.14 reescrita; §4.2 item 4 reapontado.
- `CLAUDE.md` — a linha do `savestate.py` na tabela de ferramentas de PES2.
- `docs/prompts/perfil-pes2.md` — o gate novo, e a contagem de armadilhas do
  §6.11 corrigida (ver abaixo).
- `docs/tasks/progresso.md` e este arquivo.

**Problemas encontrados.**

1. **O thumbnail do save state não serve para ler placar.** São 256×192, e a
   1 vira 7 no aumento. A tela viva de 800×655 lê; o embutido documenta.
   Registrado na §6.14 para ninguém tentar de novo.
2. **Duas contagens vencidas, corrigidas de passagem.** A §6.14 dizia "as
   vinte armadilhas da §6.11" e o perfil do ciclo dizia "Treze armadilhas";
   o `awk` sobre a seção conta **26**. Os dois textos foram corrigidos, o do
   perfil dizendo desde quando envelheceu.
3. **O `pes2_boot` do `ctest` se reporta *skipped* com `WE2002_PES2_IMAGE`
   sozinho** — ele quer `PES2_IMAGE` apontando para o `.cue`. Foi rodado à
   parte com as duas, e passou.

   *Corrigido em 2026-09-03 pela
   [CORR-PES2-027](/docs/tasks/CORR-PES2-027.md):* este item concluía "não é
   defeito, é uma variável a mais que a linha do perfil não mostra", e **era
   defeito**. A linha do perfil era a única instrução que existia, então o
   gate nunca corria pela receita escrita — e pulava com o mesmo `Skipped`
   de uma máquina sem emulador, o que fazia a corrida imprimir
   `100% tests passed` sem ter julgado o boot. A receita ganhou o
   `PES2_IMAGE` e o `boot_check.sh` ganhou três recusas distintas.
