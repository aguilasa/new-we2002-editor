---
id: MCR-TASK-16
title: "Abrir e gravar `.gme`: o contêiner do DexDrive, nos dois sentidos"
type: implementação
category: core
phase: 5
depends_on: ["MCR-TASK-15"]
fonte_de_verdade: "/docs/tasks/port-mcr/16-conteiner-gme.md §Critério de conclusão"
status: pendente
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

1. **Contêiner não é save.** Quatro dos oito `.gme` de `mcr/` são de **PES2**
   (`…PES-OPT`) e um de WE2002 **não tem option file** (só `WEW-D0A`). O
   leitor de contêiner tem de abrir os oito e entregar um cartão de 131.072 B;
   quem recusa cinco deles é o `check_card`, um nível acima, com a mensagem que
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

- [ ] **Um leitor de contêiner, por conteúdo.** Um módulo novo — sugerido
      `tools/mcr/gme.py`, separado do `card.py` porque este descreve *todo*
      cartão de PSX e aquele descreve uma embalagem em volta — devolve, de
      qualquer um dos três formatos, os 131.072 B do cartão **mais o cabeçalho
      quando havia um**. A decisão é `tamanho == 134.976 and dado[3904:3906] ==
      b"MC"`, nunca a extensão.
- [ ] **Os oito `.gme` de `mcr/` abrem como contêiner**, os três de cabeçalho
      zerado inclusive; e **cinco deles continuam sendo recusados** por
      `check_card`, com a mensagem de hoje, por não terem `WEW-OPT`.
- [ ] **`.gme` → `.gme` devolve o arquivo original, byte a byte**, nos oito —
      é o gate mais forte desta task, e o único que prova que o cabeçalho foi
      preservado em vez de regerado.
- [ ] **`.gme` → `.mcr`/`.mcd` → `.gme`** devolve o `.gme` original nos oito,
      desde que o cabeçalho viaje junto; e o cartão intermediário bate byte a
      byte com `tail -c 131072` do original.
- [ ] **`.mcr` → `.gme` sintetiza um cabeçalho válido**: assinatura em
      `0x00..0x0A`, os bytes fixos medidos acima, e `0x16..0x24` **espelhando
      os estados dos quadros 1..15 do cartão que vai junto**. Reabrir o
      resultado devolve o cartão de partida.
- [ ] **O espelho é conferido na gravação, não só escrito.** Gravar um `.gme`
      cujo espelho discorde do diretório do cartão é **recusado**, com a razão
      dita — um DexDrive listaria saves que não estão lá.
- [ ] **`copy_target` deixa de mentir na extensão.** Abrir `x.gme` e gravar a
      cópia padrão produz um `.gme` **de verdade** (134.976 B), não 131.072 B
      com nome errado. Gravar em outro formato é escolha explícita, não efeito
      colateral do nome.
- [ ] **O CLI ganha a conversão**, no mínimo `convert <entrada> <saída>`, com o
      formato saindo da extensão do destino e uma opção que a sobrepõe. As
      recusas de `mcrio` continuam no caminho.
- [ ] **`mcr/` entra na lista de diretórios que não se escreve**, ao lado de
      `roms/` e pelo mesmo motivo: são originais versionados com checksum
      registrado. `--force` não levanta essa, como não levanta a de `roms/`.
- [ ] **Os dois diálogos da UI nomeiam os três formatos** — abrir aceita
      `*.mcr *.mcd *.gme`, gravar oferece os três e o `.gme` sai `.gme`. O
      filtro é string na `ui/`; a decisão de formato é do núcleo.
- [ ] **Caso vermelho plantado**, com a disciplina do `controls.py`: **dois** —
      (a) o escritor que **regera** o cabeçalho em vez de preservá-lo, que tem
      de derrubar o round-trip dos três zerados; (b) o leitor que decide pela
      **extensão** em vez do conteúdo, que tem de derrubar um `.gme` renomeado
      para `.mcr`. Casar zero ou duas vezes é controle quebrado, não vermelho.
- [ ] **`self_check()` no módulo novo, com caso vermelho**, e ele entra na
      contagem do `selftest.py` (que hoje diz `12 modules`).
- [ ] **Gate sem fixture.** O passo novo do `ctest` roda **sem**
      `WE2002_MCR_CARD` — a entrada é `mcr/*.gme`, versionado. Se o alvo puder
      pular, ele imprime por quê, na convenção das duas linhas irmãs deste
      ciclo (`note: ...`): **leia a linha, não o `Passed`**.
- [ ] **Captura no `:98`** do diálogo de abrir mostrando os três formatos,
      anexada ao Log — e o probe **não** abre modal, como a MCR-TASK-15 fixou.
- [ ] **Documentação atualizada**: `tools/mcr/README.md` (os três formatos e o
      `convert`), `mcr/README.md` (a receita do `tail -c` passa a ser a
      alternativa manual, não a única) e o `CLAUDE.md`, cuja tabela do
      `tools/mcr/` diz hoje só `.mcr`.
- [ ] Strings de módulo e de UI em **en-US** (§3.5); esta task e o Log, em
      português.
- [ ] `python3 tools/mcr/selftest.py`, `python3 tools/mcr/controls.py` e
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

*(a preencher)*
