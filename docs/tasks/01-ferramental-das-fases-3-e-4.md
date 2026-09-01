---
id: PES2-TASK-01
title: "Ferramental das fases 3 e 4 — numpy e desmontador MIPS"
type: decisão
category: infra
phase: 0
depends_on: []
fonte_de_verdade: "/docs/PES2-AJUSTES.md §7.1"
status: concluído
---

# PES2-TASK-01: Ferramental das fases 3 e 4

## Contexto

- **Referência:** `docs/PES2-AJUSTES.md` §7.1, e `docs/PLAN-PES2-PSX.md` §3.2.
- **Não bloqueia nada das Fases 0–2.** As três estão fechadas ou a um item, e
  nenhuma delas precisa de varredura numérica nem de desmontador.
- **Instalar pacote na máquina é decisão do dono da máquina.** Esta task
  existe para dar dono à decisão, não para tomá-la.

Duas ausências confirmadas em 2026-08-30:

| Falta | Para quê | Bloqueia |
|---|---|---|
| `numpy` | varredura de padrão em 466 MB em tempo civilizado | conforto, não capacidade |
| Desmontador MIPS — `ghidra`, `radare2` ou `rizin`, os três ausentes | ler o código que consome a tabela, quando a estatística empacar | Fase 4, **se** ela empacar |

---

## Objetivo

Decidir, e registrar a decisão no plano:

1. instalar ou não `numpy` — e, se não, qual é o caminho lento aceito
   (`array`, `memoryview`, `mmap` + fatiamento) para as varreduras da Fase 3;
2. instalar ou não um desmontador MIPS, e **qual**.

### O que pesa em cada escolha

- **`numpy`** é conforto puro. As varreduras que a Fase 3 pede — achar `N`
  registros de largura constante numa faixa de 466 MB — rodam em Python
  puro, só que em minutos em vez de segundos. Um `mmap` com passo fixo já
  resolve a maior parte; o que dói é correlação de coluna.
- **Desmontador** só vale quando a estatística empacar (§4.2.4 do plano, a
  alavanca mais cara). Ghidra traz decompilador e reconhece MIPS de PSX;
  `radare2`/`rizin` são mais leves e bastam para ler uma rotina de acesso a
  tabela. **O overlay não é ELF** — é código realocado carregado em
  `0x800xxxxx`, e o desmontador precisa ser carregado com base explícita.

---

## Critério de conclusão

- [x] Decisão tomada e escrita na §3.2 do plano, com a razão em uma frase.
- [x] Se instalado: o comando que instalou, e a versão, registrados no Log.
- [x] Se recusado: qual é o plano B para a Fase 3, nomeado. *(Nada foi
      recusado para a Fase 3. O único recusado é o Ghidra, e o plano B dele
      está na §3.2: `radare2` para navegar e `objdump` para roteirizar; se a
      Fase 4 pedir decompilação, a decisão se retoma naquele momento.)*

Recusar é resultado legítimo desta task, desde que o plano B esteja escrito.

---

## Log de Execução

**Executado em:** 2026-09-01

**Resumo.** O dono da máquina autorizou instalar ("pode instalar tudo"), e o
que entrou foi `numpy` 2.5.2 (`pip3 install numpy`, no Python 3.13 do `mise` —
não há Python de sistema em uso aqui), `radare2` 5.5.0 e
`mipsel-linux-gnu-objdump` 2.42 (`apt-get install radare2
binutils-mipsel-linux-gnu`, com `sudo` sem senha).

**Ghidra ficou de fora, com razão escrita.** Não está nos repositórios do
Zorin 18.1 — `apt-cache policy ghidra` e `rizin` não devolvem nada —, o `.zip`
oficial pesa ~1,2 GB e exige JDK 21 contra o `openjdk 17.0.19` da máquina. O
que ele traz a mais é o decompilador, e o uso previsto na §4.2.4 é *ler uma
rotina de acesso a tabela*. Se a Fase 4 pedir decompilação de verdade, a
decisão se retoma ali.

**O que se aprendeu, e é o que vale para a Fase 4.** A instalação foi a parte
barata; o que custa é a base de carga. Os dois desmontadores foram exercitados
contra o executável de boot real (`/SLES_039.57`, extraído com `iso.py` para o
scratchpad — `roms/` intocada), e os dois desmontam o mesmo laço de zeragem de
BSS na entrada:

- O executável é `PS-X EXE`: cabeçalho de 2.048 B, `t_addr` em `+0x18` =
  `0x80010000` e `pc0` em `+0x10` = `0x80010008`. A base a passar é
  **`t_addr − 0x800`** = `0x8000f800`, senão o cabeçalho desloca tudo em 2 KiB
  e todo alvo de `jal` sai 2.048 bytes adiante — número plausível, endereço
  errado.
- `objdump` precisa de `-b binary -m mips:3000`. O `-EL` deste Log foi anotado
  pelo que se esperava dele: remedido na revisão desta task
  ([CORR-PES2-001](/docs/tasks/CORR-PES2-001.md)), **omiti-lo não muda uma
  instrução sequer** — o `mipsel-linux-gnu-objdump` 2.42 já tem alvo
  `elf32-tradlittlemips`, e 1.017 linhas com e sem ele dão mnemônicos
  idênticos. Quem **não** falha e só mente é o **`-EB`**: sobre o mesmo laço de
  BSS ele decodifica `j 0x8003800c` e `bltz s4,0x800108fc`, alvo de salto que
  parece endereço e não é. Manter o `-EL` explícito continua certo — muda a
  razão, não o comando.
- `radare2` reconhece o formato `PS-X EXE` sozinho e já rotula `entry0`; com
  `-m` ele avisa (`using oba to load the syminfo from different mapaddress`) e
  funciona.
- **Os demais overlays (`SELECT.BIN` e irmãos) não têm cabeçalho nenhum.** São
  código realocado — é o que a §7.3 do `PES2-AJUSTES.md` já media, com o
  deslocamento de `+3176` dominando entre as releases. A base deles sai de onde
  o carregador os põe, não do arquivo, e descobri-la é trabalho da Fase 4.

**Arquivos criados/modificados:**

- `docs/PLAN-PES2-PSX.md` — §3.2 reescrita com a decisão, as versões e os dois
  comandos medidos; uma linha na §3.1 apontando para ela
- `docs/PES2-AJUSTES.md` — o item da §7.1 marcado `[x]`, com o resultado
- `docs/tasks/progresso.md` — linha da task, quadro de fases, o parágrafo da
  Fase 0 e a "Pendência externa" correspondente
- este arquivo

**Problemas encontrados.** Nenhum que bloqueasse. Duas observações: `rizin` e
`ghidra` não existem nos repositórios do Zorin 18.1 (o `apt-cache policy` sai
vazio, sem erro — silêncio que parece "não perguntei"), e o `python3` desta
máquina é o do `mise`, não o do sistema, então `pip3 install` sem `--user` e
sem venv é o certo aqui e seria errado noutra.
