---
id: WTE-TASK-01
title: "Instalar e verificar o ferramental (Lazarus, FPC, Ghidra)"
type: infra
category: infra
phase: 0
depends_on: []
status: concluído
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
| `lazarus`, `fpc`, `fpc-source` | `apt` | o alvo |
| `python3-pefile` | `apt` | parsing de PE em script |
| Ghidra ≥ 11 | download manual | decompilador (Fase 4 e 5) |
| JDK 21 | **já instalado — via `mise`, não `apt`** | requisito do Ghidra |

> **Duas correções feitas na execução** (ver o Log no fim do arquivo):
> o pacote é **`fpc-source`**, não `fpc-src` — este último não tem candidato no
> apt; e o Ghidra 12 declara `application.java.min=21`, então o **`temurin-17`
> global não serve**, ao contrário do que a seção abaixo dizia.

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

O global é `temurin-17` e `java` resolve para
`~/.local/share/mise/installs/java/temurin-17/bin/java`. **Isso não atende o
Ghidra 12**, que exige 21 no mínimo; o `temurin-21.0.11` já está no disco e é o
que foi usado, sem mexer no global.

Duas consequências práticas:

- O `ghidraRun` procura o JDK pelo `PATH` ou pelo `JAVA_HOME`. O shim do `mise`
  está no `PATH` de shell interativo, mas **não** necessariamente no ambiente de
  um `.desktop` ou de um serviço. **Rota escolhida:** gravar o caminho do
  `temurin-21` em `support/launch.properties` (`JAVA_HOME_OVERRIDE=`), que vale
  também fora de shell interativo.
- A alternativa `mise use java@temurin-21` escreveria um `mise.toml` local. Foi
  descartada: o override do próprio Ghidra resolve sem acrescentar arquivo de
  configuração ao repositório.

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

- [x] `lazbuild` compila projeto LCL vazio sem erro, widgetset GTK2 confirmado
- [x] A janela desse projeto abre no `:99` e é capturada por `import`
- [x] `make wte` abre a janela do editor original
- [x] Ghidra abre e importa o `we-team-editor.exe` sem erro
- [x] `wte/re/ambiente.md` com as versões medidas
- [x] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-05

- **Resumo do que foi feito:**

  Instalado `lazarus` 3.0 / `fpc` 3.2.2 / `fpc-source` do `noble/universe` e o
  Ghidra 12.1.2 em `~/.local/opt/`. Os quatro critérios foram **medidos**, não
  supostos: um projeto LCL de smoke test linkou contra `libgtk-x11-2.0.so.0`
  (widgetset provado pelo binário, não pela flag) e abriu no `:99`; o
  `make wte-99` subiu o oráculo A inteiro; o Ghidra importou o `.exe` headless e
  abriu a GUI no `:99`.

  Os dois achados que mudam trabalho futuro: o Ghidra classifica o binário como
  **`compiler=borlandcpp` sozinho**, sem configuração — o que não dispensa a
  conferência de `this` em `EAX` da WTE-TASK-24, mas melhora o ponto de partida
  —, e o original **instancia os 18 formulários no startup**, o que dá à fase 2
  uma primeira lista de tamanhos para confrontar com os DFM.

  O que a task ensinou de mais reaproveitável: **nesta máquina o `mise` fica na
  frente do `apt` no `PATH`**, e isso mordeu duas vezes na mesma execução (JDK e
  Python). Registrado em `wte/re/ambiente.md` como armadilha, não como nota de
  rodapé.

- **Arquivos criados/modificados:**
  - `wte/re/ambiente.md` — criado; versões medidas, as duas armadilhas do
    `mise`, e os dois achados acima
  - `docs/tasks/01-ferramental.md` — corrigido (`fpc-src` → `fpc-source`,
    JDK 21) + este log
  - `docs/tasks/progresso.md` — status, "Concluída em", "Revisado em"
  - Fora do repositório: `~/.local/opt/ghidra_12.1.2_PUBLIC/` e o
    `launch.properties` fixando o `temurin-21`

- **Problemas encontrados:**

  1. **`fpc-src` não existe.** `apt-cache policy fpc-src` devolve
     "Candidate: (none)". O pacote é **`fpc-source`**. Task corrigida.
  2. **O `temurin-17` não serve para o Ghidra 12.** A task afirmava que o global
     do `mise` atendia; o `application.properties` do 12.1.2 declara
     `application.java.min=21`. Resolvido com `JAVA_HOME_OVERRIDE` apontando
     para o `temurin-21` que já estava no disco — **sem mexer no global do
     `mise`**, que continua `temurin-17` para o resto da máquina.
  3. **`python3-pefile` foi para o Python errado.** O apt instala no Python do
     sistema (3.12), mas o `python3` do `PATH` é o do `mise` (3.13), onde o
     módulo não existia. Um gerador com shebang `python3` teria morrido com
     `ModuleNotFoundError` longe da causa. Instalado o `pefile` também no 3.13,
     de modo que nenhum interpretador possa escolher errado.
  4. **A `wte/` ainda não existe** — quem a cria é a WTE-TASK-02. O projeto de
     smoke test do `lazbuild` foi montado no scratchpad, fora do repositório, e
     não foi versionado. Só o `wte/re/ambiente.md` entrou.
