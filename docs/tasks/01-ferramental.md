---
id: WTE-TASK-01
title: "Instalar e verificar o ferramental (Lazarus, FPC, Ghidra)"
type: infra
category: infra
phase: 0
depends_on: []
status: pendente
---

# WTE-TASK-01: Ferramental

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §3 e Fase 0.
- Esta task **abre o projeto**. Nada mais pode começar sem ela.

Medido em 2026-08-05: **nada do que o projeto precisa está instalado**. Não há
Lazarus, FPC, Ghidra, IDA, radare2, rizin, retdec nem `pefile`. O que existe é
`objdump`, `strings`, Python 3.13, Wine 32-bit via runner do Bottles, o Xvfb
`:99` com `xdotool`/`import`, e o `we2002_core` deste repositório.

`lazarus` 3.0+dfsg1-8build3 e `fpc` 3.2.2+dfsg-32 estão no `noble/universe`.
Ghidra **não** é empacotado pelo Ubuntu — instalação manual, e precisa de JDK.

---

## Objetivo

Deixar a máquina pronta, e **provar** que está, em vez de supor.

### 1. Instalar

| Pacote | Origem | Para quê |
|---|---|---|
| `lazarus`, `fpc`, `fpc-src` | `apt` | o alvo |
| `python3-pefile` | `apt` | parsing de PE em script |
| Ghidra ≥ 11 | download manual | decompilador (Fase 4 e 5) |
| JDK 17 ou 21 | **já instalado — via `mise`, não `apt`** | requisito do Ghidra |

**O Java desta máquina é gerenciado pelo [`mise`](https://mise.jdx.dev/).** Não
instalar JDK pelo `apt`: sairia um segundo Java fora do gerenciador, e o que
manda no `PATH` é o shim do `mise`. Medido em 2026-08-05:

```
$ mise ls java
java  temurin-17.0.19+10   ~/.config/mise/config.toml  temurin-17   (ativo)
java  temurin-21.0.11+10.0.LTS
java  temurin-8.0.492+9
java  corretto-8.422.05.1
java  17.0.2
java  25.0.2
```

O global já é `temurin-17`, que **atende o requisito do Ghidra**; o 21 também
está no disco se for preciso. `java` resolve para
`~/.local/share/mise/installs/java/temurin-17/bin/java`.

Duas consequências práticas:

- O `ghidraRun` procura o JDK pelo `PATH` ou pelo `JAVA_HOME`. O shim do `mise`
  está no `PATH` de shell interativo, mas **não** necessariamente no ambiente de
  um `.desktop` ou de um serviço. Se o Ghidra reclamar de Java, apontar
  `JAVA_HOME=$(mise where java)` — ou gravar o caminho no
  `support/launch.properties` do Ghidra.
- Para fixar a versão só neste projeto, `mise use java@temurin-21` escreve num
  `mise.toml` local em vez de mexer no global. Não fazer isso sem necessidade —
  o `temurin-17` já serve.

Conferir com `mise ls java` antes de mexer em qualquer coisa de Java; **não**
usar `apt install openjdk-*`.

### 2. Provar que o Lazarus funciona no alvo real

Compilar um projeto LCL vazio por **linha de comando** (`lazbuild`, não a IDE) e
abrir a janela no `:99`, seguindo a regra do `CLAUDE.md`: `DISPLAY=:99` e
`XAUTHORITY` resolvido pelo `ps`.

A IDE gráfica é opcional para o projeto; `lazbuild` **não** é — todo o
faseamento assume build reproduzível por linha de comando.

### 3. Provar que o oráculo A continua de pé

`make wte` tem de abrir a janela do editor do Obocaman. Ele depende do stack X
**i386** no host; se quebrar, a Fase 4 inteira perde o oráculo comportamental e
o plano muda. Descobrir isso agora, não na Fase 4.

### 4. Registrar as versões

Versão exata de `fpc`, `lazbuild`, widgetset padrão, Ghidra e JDK, num arquivo
que as tasks seguintes possam citar. No JDK, registrar também que veio do
`mise` e qual é o global ativo — trocar de versão pelo `mise` muda o Java que o
Ghidra pega, sem nada mudar no `apt`. Versão de compilador muda layout de
`bitpacked record` (§8.11) — não é detalhe cosmético.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/progresso.md` | modificar (status) |
| `wte/re/ambiente.md` | criar — versões medidas, com a data |

---

## Critério de conclusão

- [ ] `lazbuild` compila projeto LCL vazio sem erro, widgetset GTK2 confirmado
- [ ] A janela desse projeto abre no `:99` e é capturada por `import`
- [ ] `make wte` abre a janela do editor original
- [ ] Ghidra abre e importa o `we-team-editor.exe` sem erro
- [ ] `wte/re/ambiente.md` com as versões medidas
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
