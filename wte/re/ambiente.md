# Ambiente — versões medidas

Produto da [WTE-TASK-01](../../docs/tasks/01-ferramental.md). **Medido em
2026-08-05**, nesta máquina, com as ferramentas citadas em cada linha. Nenhum
número aqui foi digitado de memória.

Versão de compilador não é detalhe cosmético: ela decide layout de
`bitpacked record` (plano §8.11) e é o primeiro suspeito quando um número de
camisa sai embaralhado. Ao trocar qualquer uma destas versões, **reexecute os
gates da fase corrente e atualize esta tabela**.

## Host

| Eixo | Valor | Como foi medido |
|---|---|---|
| Distribuição | Zorin OS 18.1 (base `noble`) | `lsb_release -ds` |
| Kernel | 7.0.0-28-generic | `uname -r` |
| binutils (`objdump`) | 2.42 | `objdump --version` |

## O alvo — Lazarus/FPC

| Eixo | Valor | Como foi medido |
|---|---|---|
| `fpc` | 3.2.2+dfsg-32, build 2024/01/05 | `fpc -iV`, `fpc -iD`, `dpkg-query` |
| Alvo default do FPC | `linux` / `x86_64` | `fpc -iTO`, `fpc -iTP` |
| `lazbuild` | 3.0 (`/usr/bin/lazbuild`) | `lazbuild --version` |
| Pacote `lazarus` | 3.0+dfsg1-8build3 | `dpkg-query -W lazarus` |
| `lazarus-src-3.0` | instalado (puxado pelo metapacote) | `dpkg-query -W` |
| `fpc-source` | 3.2.2+dfsg-32 | `dpkg-query -W` |
| Widgetset default | **gtk2** | `lazbuild --help` (`default: gtk2`) |

Instalados por `apt install lazarus fpc fpc-source`, do `noble/universe`.

> **`fpc-src` não existe como pacote.** A WTE-TASK-01 pedia esse nome; o pacote
> real é **`fpc-source`** (o `fpc-src` do apt-cache é outra coisa: não há
> candidato). Divergência corrigida no markdown da task.

## Ghidra

| Eixo | Valor | Como foi medido |
|---|---|---|
| Versão | **12.1.2** (`PUBLIC`, build 2026-Jun-05) | `Ghidra/application.properties` |
| Instalado em | `~/.local/opt/ghidra_12.1.2_PUBLIC/` | — |
| Origem | release oficial do GitHub (NSA), zip de 572.803.866 B | `curl` + `ls -la` |
| SHA-256 do zip | `b62e81a0390618466c019c60d8c2f796ced2509c4c1aea4a37644a77272cf99d` | `sha256sum` |
| JDK exigido | **mínimo 21**, sem máximo | `application.java.min=21` |
| JDK usado | `temurin-21.0.11+10.0.LTS`, do `mise` | `java -version` no caminho fixado |

### O JDK 17 do `mise` **não** serve para o Ghidra 12

A WTE-TASK-01 registrava que o global `temurin-17` "atende o requisito do
Ghidra". Isso valia para o Ghidra 11; o **12.1.2 declara
`application.java.min=21`** e recusa o 17. O `temurin-21.0.11` já estava no
disco, então nada foi instalado.

**O global do `mise` continua `temurin-17` — de propósito.** Trocá-lo mexeria no
Java de todo o resto da máquina para agradar uma ferramenta só. Em vez disso o
caminho foi fixado dentro do próprio Ghidra:

```
~/.local/opt/ghidra_12.1.2_PUBLIC/support/launch.properties
JAVA_HOME_OVERRIDE=/home/ingmar/.local/share/mise/installs/java/temurin-21
```

O arquivo original ficou ao lado como `launch.properties.orig`. Essa rota tem a
vantagem de valer também fora de shell interativo — `.desktop`, cron, serviço —,
onde o shim do `mise` não está no `PATH`.

`mise ls java` em 2026-08-05:

```
java  temurin-17.0.19+10   ~/.config/mise/config.toml  temurin-17  (global)
java  temurin-21.0.11+10.0.LTS
java  temurin-8.0.492+9
java  corretto-8.422.05.1
java  17.0.2
java  25.0.2
```

**Não instalar JDK pelo `apt`.** Sairia um segundo Java fora do gerenciador, e
quem manda no `PATH` é o shim do `mise`.

## Python

| Eixo | Valor | Como foi medido |
|---|---|---|
| `python3` no `PATH` | 3.13.13, do **`mise`** | `python3 -V`, `sys.executable` |
| `/usr/bin/python3` | 3.12.3, do sistema | `/usr/bin/python3 -V` |
| `pefile` no `mise` 3.13 | 2024.8.26 (via `pip`) | `import pefile` |
| `pefile` no sistema 3.12 | 2023.2.7 (`python3-pefile` do apt) | `import pefile` |

### A armadilha dos dois Pythons

`apt install python3-pefile` instala **no Python do sistema (3.12)**, mas o
`python3` que qualquer script deste projeto vai pegar é o **shim do `mise`
(3.13)** — e lá o módulo não existia. Um gerador com shebang `python3` teria
morrido com `ModuleNotFoundError` num ponto sem relação com a causa.

Resolvido instalando o `pefile` **também** no `mise` 3.13
(`python3 -m pip install pefile`), de modo que os dois interpretadores tenham o
módulo e nenhum script possa escolher errado. As versões diferem (2024.8.26 no
`mise`, 2023.2.7 no apt) — se algum dia isso importar, é sinal de que o
gerador deveria fixar o interpretador.

Mesma família da armadilha do JDK: **nesta máquina, o `mise` fica na frente do
`apt` no `PATH`.**

## Os dois oráculos

| Eixo | Valor | Como foi medido |
|---|---|---|
| `we-team-editor.exe` | 1.151.488 B, PE32 i386 | `stat -c %s` |
| SHA-256 do `.exe` | `9cebce645b8e320c77b82db5b4683613c8ccde5123e6b0b08a59f0f1b8697fff` | `sha256sum` |
| Wine (runner Bottles) | `wine-experimental.bleeding.edge.9.0.93696.20240429 (TkG Plain)` | `wine --version` |
| Xvfb `:99` | 1280x1024x24 | `ps -o args= -C Xvfb` |

O `.exe` é **leitura pura**. O hash está aqui para que qualquer medição futura
possa provar que mediu o mesmo binário.

## O que foi provado, não suposto

Os quatro critérios da WTE-TASK-01, com o resultado medido:

1. **`lazbuild` compila LCL vazio, GTK2.** Projeto de smoke test em
   `$SCRATCH/lclsmoke` (fora do repositório — a `wte/` só nasce na
   WTE-TASK-02). Linkou; `ldd` mostra `libgtk-x11-2.0.so.0`, o que confirma o
   widgetset pelo binário, não pela flag.
2. **A janela abre no `:99`.** Capturada por `import -window`, 417x208, com o
   rótulo legível. `DISPLAY=:99` + `XAUTHORITY` resolvido pelo `ps`, como manda
   o `CLAUDE.md`.
3. **`make wte-99` ainda abre o original.** O stack X i386 continua de pé — o
   oráculo A sobrevive. Ver o achado sobre os 18 formulários abaixo.
4. **Ghidra importa o `.exe`.** Headless (`analyzeHeadless -import`) e GUI
   (`ghidraRun` no `:99`, "Ghidra startup complete").

### Achado 1 — o Ghidra reconhece o C++Builder sozinho

O import sem análise já classifica o binário:

```
format=Portable Executable (PE)
lang=x86:LE:32:default
compiler=borlandcpp        <-- detectado, não configurado
imagebase=00400000
blocks=9
symbols=509
```

Reproduzir:

    $GHIDRA/support/analyzeHeadless <proj-dir> <proj> \
        -import we-team-editor/we-team-editor.exe \
        -scriptPath <dir do ShowInfo.java> -postScript ShowInfo.java \
        -noanalysis -overwrite

com `ShowInfo.java`:

    import ghidra.app.script.GhidraScript;
    public class ShowInfo extends GhidraScript {
      public void run() throws Exception {
        println("SMOKE format="   + currentProgram.getExecutableFormat());
        println("SMOKE lang="     + currentProgram.getLanguageID());
        println("SMOKE compiler=" + currentProgram.getCompilerSpec().getCompilerSpecID());
        println("SMOKE imagebase="+ currentProgram.getImageBase());
        println("SMOKE blocks="   + currentProgram.getMemory().getBlocks().length);
        println("SMOKE symbols="  + currentProgram.getSymbolTable().getNumSymbols());
      }
    }

O `-noanalysis` é o que torna o número reproduzível: com análise o Ghidra cria
símbolos e `symbols=509` vira outra coisa. O script é ad-hoc de propósito —
não é ferramenta do projeto, e por isso mora aqui e não em `wte/tools/`.

`compiler=borlandcpp` **não prova** que a convenção de chamada da §8.1 está
resolvida — a WTE-TASK-24 continua tendo de conferir `this` em `EAX` num
handler conhecido. Mas o ponto de partida é melhor do que o plano assumia.

O import também aplica símbolos de `rtl60.bpl` e `vcl60.bpl` a partir da própria
pasta `we-team-editor/`, sem os quais as chamadas à VCL ficariam anônimas.

### Achado 2 — o original instancia os 18 formulários no startup

Ao subir o `make wte-99`, antes de qualquer arquivo ser aberto, o `:99` já tem
**24 janelas X com título**. Descontando três `Default IME`, um `Input`, o
`TOpenDialog` "Abre" e a janela oculta de 1x1 da `TApplication`, sobram
**exatamente 18** — o mesmo número de DFM que a §1 do plano registra:

```
 W11 Team Editor PT by chagas_michel!  522x475     Cuidado                339x169
Estrategia                             529x498     Error                  335x121
Player characteristics                 707x273     Error                  382x122
Cor                                    542x225     W11TE PT!              414x189
W11 TE PT!                             284x158     Sobre...               319x274
W11 TE PT!                             282x113     Atalhos                264x196
Calcular precos                        285x124     Editar Jog.            257x188
Mover todos                            239x124     Fechar W11TE           231x122
Warning                                340x172     Number                 135x153
```

A contagem saiu de `xdotool`, não de contar na tela. Reproduzir (com o
`make wte-99` no ar, `DISPLAY`/`XAUTHORITY` como manda o `CLAUDE.md`):

    xdotool search --name '.' 2>/dev/null | while read i; do
      n=$(xdotool getwindowname "$i" 2>/dev/null) || continue
      g=$(xdotool getwindowgeometry "$i" | sed -n 's/.*Geometry: //p')
      [ -n "$n" ] && printf '%s\t%s\n' "$n" "$g"
    done | sort

24 linhas; descontando as seis não-formulário citadas acima, sobram 18.
Encerrar depois com `wineserver -k` no prefix `work/wineprefix-wte` — o `:99`
é recurso serializado, e janela esquecida ali é dirigida pelo teste seguinte.

Isto é `Application.CreateForm` para tudo no `.cpp` do projeto, o padrão do
C++Builder 6 — e é **material para a fase 2**: a casca pode reproduzir a mesma
estratégia, e os tamanhos aqui são um primeiro confronto contra os DFM que a
WTE-TASK-03 vai extrair.

Duas consequências para quem for dirigir a janela por `xdotool`:

- **A principal tem um homônimo de 1x1.** `W11 Team Editor PT` (1x1) é a janela
  oculta da `TApplication`; a de verdade é
  `_W11 Team Editor PT by chagas_michel!_` com 522x475 — note o **espaço
  inicial** no título. Procurar por nome exato sem isso não acha nada.
- **Há três pares de títulos repetidos** (`Error` ×2, `W11 TE PT!` ×2, e
  `W11TE PT!` que só difere por espaço). Igual ao `ed.exe`, achar janela por
  título aqui não é confiável — a WTE-TASK-22 vai precisar do `_NET_WM_PID`,
  como o `golden_gui.sh` do `newWe2002` já faz.

**Não é medição canônica.** São tamanhos de janela X sob Wine, não geometria de
DFM; a WTE-TASK-03 mede a fonte. Está aqui como pista, e para registrar que o
oráculo A subiu inteiro.
