---
id: MCR-TASK-16
title: "Abrir e gravar `.gme`: o contêiner do DexDrive, nos dois sentidos"
type: implementação
category: core
phase: 5
depends_on: ["MCR-TASK-15"]
fonte_de_verdade: "/docs/tasks/port-mcr/16-conteiner-gme.md §Critério de conclusão"
status: concluído
---

# MCR-TASK-16: `.gme` como formato de entrada e de saída, e a conversão nos dois sentidos

## Contexto

- **Pedido do usuário em 2026-09-09**, depois do fechamento do ciclo: abrir
  `.gme` também, e poder gravar em `.mcr` ou `.mcd`. O sentido inverso —
  gravar `.gme` a partir de um cartão cru — **é possível**, e a medição abaixo
  diz por quê; entra no escopo.
- **Fonte de verdade:** este arquivo. O plano descreve a v1 sobre `.mcr` e não
  menciona contêiner nenhum, então o critério é o daqui, como
  `.claude/rules/tasks.md` autoriza.
- **A fixture já está no repositório.** Desde `cea0c31` há **oito `.gme`** em
  `mcr/`, com checksum registrado em [`../../../mcr/README.md`](../../../mcr/README.md).
  Um gate de contêiner não precisa de `WE2002_MCR_CARD` — roda em qualquer
  clone, o que nenhum outro gate deste ciclo faz.

### O que está medido do formato

Medido em 2026-09-09 sobre os oito arquivos de `mcr/`:

| Medido | Valor |
|---|---|
| tamanho | **134.976 B** nos oito = 3.904 de cabeçalho + os 131.072 do cartão |
| `MC` do cartão | em **3904** nos oito, sem exceção |
| assinatura | `123-456-STD` em `0x00..0x0A` — em **cinco** dos oito |
| cabeçalho zerado | **três** (`17738`, `18432`, `22507`) têm os 3.904 bytes **inteiramente nulos**, e o cartão dentro deles é válido |
| espelho do diretório | `0x16..0x24` são **15 bytes iguais aos estados dos quadros 1..15** do cartão, nos cinco assinados, byte a byte |
| resto | `0x12`, `0x14`, `0x15` fixos (`01`, `01`, `4D`); `0x25..0x26` = `00 01`; `0x27..0x34` quase todo `0xFF`; **de `0x35` a `0x0F3F`, zero nos oito** — a área de comentário do DexDrive não é usada por nenhum deles |

Duas conclusões que decidem o desenho, e não são palpite:

1. **`.gme` → cartão é corte, e é sem perda.** `tail -c 131072` basta, e
   funciona inclusive nos três de cabeçalho zerado — que um leitor que valide a
   assinatura antes de cortar recusaria.
2. **Cartão → `.gme` só é sem perda se o cabeçalho original for preservado.**
   Sintetizar um cabeçalho a partir de um `.mcr` produz a forma assinada, que
   **não** é o que os três zerados têm. Logo: quem abriu de `.gme` guarda os
   3.904 bytes e os devolve; quem abriu de `.mcr`/`.mcd` recebe um cabeçalho
   sintetizado, com o espelho de `0x16..0x24` batendo com o diretório do cartão
   que vai junto.

### O que hoje está errado, e é verificável

| Medido | Onde |
|---|---|
| `Card.from_file` faz `fh.read()` e o construtor exige 131.072 B — um `.gme` é recusado pelo **tamanho**, com mensagem que não menciona contêiner | `tools/mcr/card.py` |
| `copy_target` **preserva a extensão**: abrir `x.gme` e dar Ctrl+S grava `x-edited.gme` com **131.072 bytes crus dentro** — um `.gme` que nenhum DexDrive lê, e que o nosso próprio leitor recusaria | `tools/mcr/mcrio.py:120` |
| os dois diálogos filtram `Memory cards (*.mcr)` — `.mcd` do DuckStation e `.gme` não aparecem, embora o `.mcd` já **funcione** (a extensão não é olhada em lugar nenhum) | `tools/mcr/ui/main_window.py:183, 283` |
| `check_destination` protege `roms/` e a fixture de `WE2002_MCR_CARD`, e **não** protege `mcr/`, que desde `cea0c31` também guarda originais versionados | `tools/mcr/mcrio.py:97` |

### Três armadilhas para esta task

1. **Contêiner não é save.** **Cinco** dos oito `.gme` de `mcr/` são de
   **PES2** (`…PES-OPT`) e um de WE2002 **não tem option file** (só
   `WEW-D0A`) — a tabela de [`../../../mcr/README.md`](../../../mcr/README.md)
   é quem os separa. O leitor de contêiner tem de abrir os oito e entregar um
   cartão de 131.072 B; quem recusa **seis** deles — os cinco de PES2 mais o
   `34978` — é o `check_card`, um nível acima, com a mensagem que
   ele já tem. Misturar as duas camadas troca "não é um cartão" por "não é o
   cartão que eu queria", que é exatamente a confusão que a mensagem atual
   evita.
2. **Detecção por conteúdo, não por extensão.** Ninguém garante que um `.gme`
   se chame `.gme`. O que decide a leitura é o **par tamanho + `MC` em 3904**;
   a extensão decide só o que se **escreve**, e mesmo isso com uma opção
   explícita por cima.
3. **A Regra 3 continua valendo.** Nada em `tools/mcr/ui/**.py` importa
   `layout`, `card` ou `mcrio` — os filtros de diálogo não são exceção, e o
   `selftest` varre.

---

## Objetivo

`.gme`, `.mcr` e `.mcd` viram **três embalagens do mesmo cartão**: qualquer uma
abre, qualquer uma grava, e a conversão entre elas não perde byte. O que já
está medido sobre o cartão em si — round-trip, recusas, gravação pela tela —
não muda de valor por causa disso.

---

## Critério de conclusão

- [x] **Um leitor de contêiner, por conteúdo.** Um módulo novo — sugerido
      `tools/mcr/gme.py`, separado do `card.py` porque este descreve *todo*
      cartão de PSX e aquele descreve uma embalagem em volta — devolve, de
      qualquer um dos três formatos, os 131.072 B do cartão **mais o cabeçalho
      quando havia um**. A decisão é `tamanho == 134.976 and dado[3904:3906] ==
      b"MC"`, nunca a extensão.
- [x] **Os oito `.gme` de `mcr/` abrem como contêiner**, os três de cabeçalho
      zerado inclusive; e **seis deles continuam sendo recusados** por
      `check_card`, com a mensagem de hoje, por não terem `WEW-OPT` — os
      **cinco** de PES2 mais o `34978`, que só tem cup data. Sobram
      **dois** aceitos, o `29939` e o `34218`.
- [x] **`.gme` → `.gme` devolve o arquivo original, byte a byte**, nos oito —
      é o gate mais forte desta task, e o único que prova que o cabeçalho foi
      preservado em vez de regerado.
- [x] **`.gme` → `.mcr`/`.mcd` → `.gme`** devolve o `.gme` original nos oito,
      desde que o cabeçalho viaje junto; e o cartão intermediário bate byte a
      byte com `tail -c 131072` do original.
- [x] **`.mcr` → `.gme` sintetiza um cabeçalho válido**: assinatura em
      `0x00..0x0A`, os bytes fixos medidos acima, e `0x16..0x24` **espelhando
      os estados dos quadros 1..15 do cartão que vai junto**. Reabrir o
      resultado devolve o cartão de partida.
- [x] **O espelho é conferido na gravação, não só escrito.** Gravar um `.gme`
      cujo espelho discorde do diretório do cartão é **recusado**, com a razão
      dita — um DexDrive listaria saves que não estão lá.
- [x] **`copy_target` deixa de mentir na extensão.** Abrir `x.gme` e gravar a
      cópia padrão produz um `.gme` **de verdade** (134.976 B), não 131.072 B
      com nome errado. Gravar em outro formato é escolha explícita, não efeito
      colateral do nome.
- [x] **O CLI ganha a conversão**, no mínimo `convert <entrada> <saída>`, com o
      formato saindo da extensão do destino e uma opção que a sobrepõe. As
      recusas de `mcrio` continuam no caminho.
- [x] **`mcr/` entra na lista de diretórios que não se escreve**, ao lado de
      `roms/` e pelo mesmo motivo: são originais versionados com checksum
      registrado. `--force` não levanta essa, como não levanta a de `roms/`.
- [x] **Os dois diálogos da UI nomeiam os três formatos** — abrir aceita
      `*.mcr *.mcd *.gme`, gravar oferece os três e o `.gme` sai `.gme`. O
      filtro é string na `ui/`; a decisão de formato é do núcleo.
- [x] **Caso vermelho plantado**, com a disciplina do `controls.py`: **dois** —
      (a) o escritor que **regera** o cabeçalho em vez de preservá-lo, que tem
      de derrubar o round-trip dos três zerados; (b) o leitor que decide pela
      **extensão** em vez do conteúdo, que tem de derrubar um `.gme` renomeado
      para `.mcr`. Casar zero ou duas vezes é controle quebrado, não vermelho.
- [x] **`self_check()` no módulo novo, com caso vermelho**, e ele entra na
      contagem do `selftest.py` (que hoje diz `12 modules`).
- [x] **Gate sem fixture.** O passo novo do `ctest` roda **sem**
      `WE2002_MCR_CARD` — a entrada é `mcr/*.gme`, versionado. Se o alvo puder
      pular, ele imprime por quê, na convenção das duas linhas irmãs deste
      ciclo (`note: ...`): **leia a linha, não o `Passed`**.
- [x] **Captura no `:98`** do diálogo de abrir mostrando os três formatos,
      anexada ao Log — e o probe **não** abre modal, como a MCR-TASK-15 fixou.
- [x] **Documentação atualizada**: `tools/mcr/README.md` (os três formatos e o
      `convert`), `mcr/README.md` (a receita do `tail -c` passa a ser a
      alternativa manual, não a única) e o `CLAUDE.md`, cuja tabela do
      `tools/mcr/` diz hoje só `.mcr`.
- [x] Strings de módulo e de UI em **en-US** (§3.5); esta task e o Log, em
      português.
- [x] `python3 tools/mcr/selftest.py`, `python3 tools/mcr/controls.py` e
      `ctest -R mcr` com `WE2002_MCR_CARD` apontado — os três verdes, com o
      número medido de cada um no Log.

---

## Fora de escopo

- **Escrever o que o DexDrive real lê.** Nenhum DexDrive passou por aqui, e o
  critério acima é *round-trip mais espelho coerente*, não "o hardware aceita".
  Se um dia um aceitar ou recusar, isso é medição nova, e vira task.
- **A área de comentário** (`0x35..0x0F3F`). Zero nos oito arquivos; preservada
  quando vem, nunca preenchida por nós.
- **Outros contêineres** — `.mcs`, `.psv`, `.vgs`, `.vmp`. Mesma família de
  problema, nenhum pedido e nenhuma amostra no disco.

---

## Log de Execução

**Executado em:** 2026-09-09

### Resumo do que foi feito

O contêiner virou uma **camada**, não um ramo escondido: `tools/mcr/gme.py`
sabe desembrulhar e embrulhar, e nada mais no port sabe que existe um
cabeçalho. As três embalagens passaram a ser a mesma coisa vista de fora —
`.mcr` e `.mcd` são o dump cru, `.gme` é o dump com 3.904 bytes na frente —, e
**quem decide o que um arquivo é são os bytes dele**: o tamanho, e o `MC` em
3904. A extensão decide só o que se **escreve**.

O que a execução ensinou, e não estava na task:

1. **A assimetria é mais funda do que "preservar o cabeçalho".** O cabeçalho
   viaja com o **cartão em memória**, não com o arquivo: um `.mcr` no disco não
   tem onde guardá-lo. Então `gme → mcr → gme` em duas invocações de CLI **não
   pode** devolver o original, e o critério da task ("desde que o cabeçalho
   viaje junto") é sobre o objeto, não sobre o par de arquivos. Medido nos oito:
   **8/8 idênticos** preservando, **2/8** sintetizando. O `convert` imprime uma
   nota quando sintetiza, em vez de fingir simetria.
2. **Dois números que a task não previa.** Só `0x27..0x34` — 14 bytes, quase
   todos `0xFF` — separam a síntese do original nos cinco assinados; os dois que
   ela reproduz são os que calham de ser `0xFF` inteiros. É a medição que
   sustenta o desenho, e virou asserção: `synthesis reproduces two of those five
   exactly`.
3. **O `edit_probe` comparava maçã com laranja.** Ele lia o arquivo cru e
   comparava com `card.to_bytes()`; com um `.gme` na entrada, todo offset sairia
   deslocado em 3.904 e as diferenças **pareceriam edições que não houve**.
   Entrou `mcrio.card_bytes_of()`, que tira o embrulho antes de comparar. O
   mesmo valia para o `roundtrip`, que escrevia a cópia como `.mcr` e batia num
   erro de **tamanho** em vez de medir byte.

### Os dois controles, e as duas armadilhas que eles cobraram

Os dois novos foram plantados na forma literal do `controls.py`, e **nenhum dos
dois funcionou de primeira** — exatamente pelos dois motivos que o perfil
registra:

- **`gme-detect-by-extension` casou 2×.** `    if looks_wrapped(data):`
  aparece em `read_card` e em `main()`. Controle quebrado, não vermelho. O
  literal passou a levar a linha seguinte junto, que difere (`str(path)` contra
  `a.path`).
- **`gme-header-regenerated` ficou verde no `mcrio`.** O `.gme` plantado ali
  era construído com `gme.wrap(raw)` — e um escritor que **sempre** regenera
  produz o mesmo arquivo, então a comparação concordava consigo mesma. O
  conserto foi montar o arquivo **à mão**, `bytes(HEADER_BYTES) + raw`: um
  cabeçalho de zeros é a única forma que a regeneração não sabe inventar,
  porque ela assina o que faz. É a mesma família do `model-write-nobody`.

Total: `controls: 22 of 22 red (21 substitutions, 1 new file)`.

**Um controle existente teve de ser reescrito**: `mcrio-readonly-guard` citava
`    if READ_ONLY_DIR in parts:`, e a linha mudou de forma quando `mcr/` entrou
ao lado de `roms/`. Sem isso, ele passaria a casar zero vezes — verde pelo
motivo errado.

### O que ficou medido

| medição | valor |
|---|---|
| `gme.py --check` | `8/8 containers round-trip byte-identical` |
| `.gme` → cartão → `.gme` preservando | **8 de 8** idênticos |
| o mesmo, sintetizando o cabeçalho | **2 de 8** |
| cartões assinados em `mcr/` | 5 de 8; os outros três, 3.904 bytes nulos |
| `selftest.py` | `0 failure(s) over 13 modules plus the design rules` |
| `controls.py` | `22 of 22 red (21 substitutions, 1 new file)` |
| `ctest -R mcr` com fixture e `:98` | 4/4 passed |
| `ctest -R mcr` sem fixture | `mcr_container` **passa**; só o `mcr_card` pula |

### A tela

A janela abre um `.gme` direto — `work/mcr-ui-gme.png`, uma cópia do
`29939` aberta no `:98`, com a barra de estado dizendo
`BISLPM-87056WEW-OPT  blocks [1, 2]  23 players  22 shirt number(s) DISAGREE`.
**O `DISAGREE` não é defeito desta task**: é o que o `mcr/README.md` já
registra — esses cartões têm nome trocado e time desbloqueado, e a área de
jogador criado que os 17 destinos endereçam está vazia. A tripwire dos dorsais
está certa ao acusar.

O diálogo de abrir, em `work/mcr-ui-filtros.png`, mostra
`Memory cards (*.mcr *.mcd *.gme)` e os oito arquivos de `mcr/`. Ele foi
capturado **fora do gate**, num script descartável que constrói o
`QFileDialog` direto: a regra da MCR-TASK-15 continua valendo, e nenhum probe
abre modal. Quem julga o filtro é o `ui_check.py`, sobre a string que o
`--open-probe` relata — e a asserção foi conferida à mão, plantando um filtro
só de `.mcr` numa cópia da árvore: `FAIL: the file dialogs do not offer .mcd,
.gme`.

> **Conferência à mão não fica no repositório.** A
> [CORR-MCR-025](/docs/tasks/port-mcr/CORR-MCR-025.md) plantou o caso vermelho
> no `OPEN_BREAKS`, e ao plantá-lo mediu que a asserção era mais fraca do que
> esta corrida à mão fez parecer: ela varria a string inteira do filtro, e os
> grupos estreitos do fim a satisfaziam com o grupo default oferecendo `.mcr`
> sozinho.

### Arquivos criados/modificados

Conferido contra `git show --stat --format= HEAD`:

- **`tools/mcr/gme.py`** — novo, o contêiner
- `tools/mcr/card.py` — `Card.container`, e a mensagem de tamanho que dizia que
  `.gme` "não serve aqui"
- `tools/mcr/mcrio.py` — `read_card`, `card_bytes_of`, formato na gravação,
  `READ_ONLY_DIRS`, e os checks do contêiner
- `tools/mcr/cli.py` — o `convert`
- `tools/mcr/controls.py` — dois controles novos, um reescrito
- `tools/mcr/selftest.py` — `gme` na lista de módulos
- `tools/mcr/ui/main_window.py` — `CARD_FILTER`, usado pelos dois diálogos
- `tools/mcr/ui/app.py` — o probe relata o filtro
- `tools/mcr/ui_check.py` — e o gate o julga
- `tests/CMakeLists.txt` — o alvo `mcr_container`
- `tools/mcr/README.md`, `mcr/README.md`, `CLAUDE.md`, `docs/PLAN-MCR-PY.md`,
  `docs/prompts/perfil-mcr.md` — os três formatos, o `convert`, o gate novo, e
  as contagens de módulo e de controle que a varredura do `controls.py` cobra
- `docs/tasks/port-mcr/progresso.md` — a linha da task e o total de controles

### Problemas encontrados

Os três acima — o literal que casou duas vezes, o controle que se comparava
consigo mesmo, e o `edit_probe`/`roundtrip` comparando arquivo embrulhado com
cartão cru. Nenhum bloqueio.

Uma decisão vale registrar: o `convert` **não** passa pelo `check_card`.
Contêiner não é save, cinco dos oito `.gme` são de PES2 e um não tem option
file; recusar a conversão deles seria responder a pergunta errada. Quem
responde se o save serve a este editor é o `info`, com a mensagem que ele já
tinha.
