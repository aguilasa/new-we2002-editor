# Plano de engenharia reversa — WE2002 Team Editor → Lazarus

> **Objetivo final: o WE2002 Team Editor do Obocaman rodando 100% nativo no
> Linux, escrito em Object Pascal sobre Lazarus/LCL, sem Wine.**
>
> | Item | Valor |
> |---|---|
> | Alvo da engenharia reversa | `we-team-editor/we-team-editor.exe` (v0.99, tradução PT-BR) |
> | Toolchain original | **Borland C++Builder 6** (não Delphi — ver §1.1) |
> | Toolchain de destino | Lazarus 3.0 + FPC 3.2.2, LCL/GTK2, x86-64 |
> | Oráculo comportamental | o próprio `.exe` sob Wine 32-bit (`make wte`) |
> | Oráculo de formato | `we2002_core` deste repositório, já verificado contra o `ed.exe` |
>
> Data da análise inicial: 2026-08-05
> Estado: **plano; nenhuma fase executada.**
>
> Este é um projeto **separado** do `newWe2002`. Não mistura código, não
> compartilha build, não entra no `CMakeLists.txt`. O que compartilha é
> conhecimento: os offsets em [`Offsets.hpp`](../src/core/include/we2002/Offsets.hpp)
> são a âncora de toda a Fase 3.

---

## 0. Escopo

### Objetivo

Reimplementar o **WE2002 Team Editor v0.99** do Obocaman como aplicação
Lazarus nativa, com paridade de comportamento verificada byte a byte contra o
binário original.

Por que este editor e não só o `ed.exe`: ele tem quatro coisas que o `ed.exe`
não tem, todas já listadas no [CLAUDE.md](../CLAUDE.md) e todas dependentes de
lógica que só existe compilada —

1. **preço derivado dos atributos**, do jogador e do time inteiro;
2. **import de jogador de arquivo `.mcr`** (memory card do PSX);
3. **camisa e bandeira 2D em tempo real**, com colar-cores;
4. **contador de slots livres de Master League** na tela.

### Não-objetivos

- **Não** portar para Windows nem macOS nesta rodada. O código Lazarus não deve
  criar barreira gratuita ao Windows (nada de `/proc`, nada de caminho POSIX
  hardcoded), mas Windows não entra em matriz de teste.
- **Não** fundir com o `newWe2002`. São dois programas.
- **Não** manter a tradução PT-BR do `chagas_michel` como base de texto — ver §1.5.
- **Não** reproduzir bug do original *por padrão*. Divergência deliberada é
  permitida e vai num registro próprio (§7.3), diferente da política do
  `newWe2002`, onde o objetivo era clonar o `ed.exe` inclusive nos defeitos.

### Definição de pronto

As três condições, juntas:

1. Os **96 handlers publicados** (§1.4) têm equivalente funcional em Pascal.
2. Para cada operação que grava, `wte.exe` sob Wine e o app Lazarus produzem
   **imagem byte-idêntica** a partir da mesma imagem de entrada, nas duas ROMs
   de `roms/` (§6).
3. O app roda em Linux x86-64 nativo, sem Wine, sem camada 32-bit.

---

## 1. Diagnóstico do binário

Tudo nesta seção foi medido, não presumido. Reproduzível com `objdump`,
`strings` e Python puro.

### 1.1 Toolchain: C++Builder 6, não Delphi

Isto é o achado que dita o plano inteiro. Três provas independentes:

```
$ strings -n 6 we-team-editor.exe | grep -i borland
Borland C++ - Copyright 2002 Borland Corporation
c:\bcb\emuvcl\utilcls.h
```

```
$ objdump -x we-team-editor.exe | grep -oE '\] (_|@@)[A-Za-z0-9_@]+'
___CPPdebugHook
__GetExceptDLLinfo
```

E o *name mangling* dos 267 imports das duas BPLs — dos 322 do binário, os
outros 55 são das DLLs do Windows — é o do C++ da Borland, não o do Delphi:

```
@System@RegisterModule$qqrp17System@TLibModule
@Controls@TWinControl@CreateHandle$qqrv
@Forms@TApplication@CreateForm$qqrp17System@TMetaClasspv
```

O sufixo `$qqr` é `__fastcall` da Borland; `p17System@TLibModule` é ponteiro
para tipo de 17 caracteres. Delphi não emite nada disso.

**Consequência prática, e é a boa notícia:** a fonte original era C++ **usando
VCL**. A VCL é a mesma biblioteca do Delphi, com a mesma hierarquia de classes,
os mesmos nomes de propriedade e os mesmos `.dfm`. A LCL do Lazarus é uma
reimplementação da VCL com API deliberadamente compatível. Então a tradução
C++Builder → Lazarus é **VCL → LCL** (quase 1:1) mais **C++ → Object Pascal**
(mecânica), não uma reescrita de arquitetura.

**Consequência ruim:** o decompilador não vai devolver Pascal. Vai devolver C++
com convenção `__fastcall` da Borland, que nenhum decompilador reconhece por
padrão. Ver a armadilha §8.1.

### 1.2 Métricas

| Item | Valor |
|---|---|
| Tamanho do `.exe` | 1.151.488 bytes |
| Formato | PE32 i386, GUI, 8 seções, símbolos removidos |
| Timestamp do PE | 2002-11-30 14:39:08 |
| `.text` (código do autor) | 138.240 bytes (`0x21c00`) |
| `.data` | 65.024 bytes |
| `.rsrc` | 912.384 bytes — **79% do arquivo** |
| Imports | 322, sendo 267 de `rtl60.bpl`/`vcl60.bpl` |
| Imports de SO | só `KERNEL32.DLL`, `USER32.DLL`, `OLEAUT32.DLL` |
| Formulários DFM | 18 |
| Componentes nos formulários | 441 |
| Métodos publicados (handlers) | 96 |
| Unidades identificadas por nome | 13 |
| Bitmaps externos em `image/` | 198 |
| `data/dat.bin` | 145.408 bytes |

**Esta tabela foi remedida por ferramenta versionada na WTE-TASK-09** e traz os
valores reconciliados. Quatro números da primeira medição (2026-08-05, script
descartável) mudaram — componentes, imports de package, strings com enchimento e
bitmaps —, e o confronto linha a linha, com a causa de cada correção, está em
[`../wte/re/fase-1.md`](../wte/re/fase-1.md).

**A VCL está fora do executável.** O app usa runtime packages (`rtl60.bpl`,
1.324 KB; `vcl60.bpl`, 637 KB, ambos na pasta). Isso significa que os 138 KB de
`.text` são **quase inteiramente código do Obocaman** — não há runtime estático
para separar do que interessa. Para comparação, o `ed.exe` do MFC estático
carrega centenas de KB de framework misturados ao código do Moriero.

138 KB de código i386 sem otimização é da ordem de **6 a 8 mil linhas de C++**.
Escala comparável ao `edDlg.cpp` (8.456 linhas) que já foi portado neste repo.

### 1.3 Unidades originais

Os exports de finalização de unidade entregam os nomes dos arquivos-fonte:

```
@@Tep2002_about@Initialize          @@Tep2002_info3@Initialize
@@Tep2002_creditos_equipo@…         @@Tep2002_info4@…
@@Tep2002_dorsal@…                  @@Tep2002_movertodos@…
@@Tep2002_enlaza@…                  @@Tep2002_salida@…
@@Tep2002_error2@…                  @@Tep2002_warning@…
@@Tep2002_info@…                    @@Tep2002_warning_2@…
@@Tep2002_info2@…
```

O projeto se chamava **`ep2002`** (*editor de plantillas 2002*, provavelmente).
São 13 unidades exportadas; as unidades das telas grandes (`MainForm`,
`estrategia`, `jugador`, `ficha_color`, `ficha_error`) **não** aparecem aqui —
sem finalização a emitir, o linker não exportou. Elas existem, e os nomes das
instâncias globais confirmam:

```
_MainForm  _estrategia  _jugador  _ficha_color  _ficha_error  _ficha_about
_ficha_dorsal  _ficha_enlaza  _ficha_error2  _ficha_info  _ficha_info2
_ficha_info3  _ficha_info4  _ficha_movertodos  _ficha_salida  _ficha_warning
_ficha_warning_2  _ficha_creditos_equipo
```

18 instâncias globais, uma por formulário — o padrão auto-create do C++Builder.

### 1.4 Os 96 handlers, com endereço

O VCL guarda a *published method table* no VMT, e ela sobreviveu ao
`/STRIP`: cada entrada tem `word tamanho`, `dword endereço`, `byte tamanho do
nome`, nome. Varrendo `.data` saem 96 pares nome↔endereço. Amostra dos que
importam:

| Endereço | Handler | O que provavelmente faz |
|---|---|---|
| `0x0040c2c8` | `boton_mcrClick` | abre o `.mcr` |
| `0x0040c46c` | `boton_mcr2isoClick` | grava o jogador do `.mcr` na imagem |
| `0x0040ee80` | `grabar_camisetaClick` | grava a camisa editada |
| `0x0040f69c` | `grabar_memoryClick` | grava para memory card |
| `0x00408bb8` | `etiqprecioClick` | calcula preço do jogador |
| `0x00410ea8` | `colorearClick` | pinta camisa/bandeira |
| `0x0040cd6c` | `lista_equiposChange` | carrega time selecionado |
| `0x00409aa0` | `lista_formacionesClick` | aplica formação |
| `0x0040adec` | `ComboBoxDrawItem` | owner-draw do combo |
| `0x0040a000` | `malla2MouseDown` | grade do editor de camisa |

A lista completa vai para `wte/re/published_methods.tsv` na Fase 1.

**Isso já é o mapa de funções.** Cada endereço acima é um ponto de entrada
nomeado — em RE normal, descobrir 96 nomes de função custa dias.

### 1.5 O binário é a tradução PT-BR, e isso não atrapalha

O caption diz `W11 Team Editor PT by chagas_michel!` e o `Leia - Me.txt`
confirma. O patch é **só string, in-place, com padding de espaço** — 13 strings
de `.data` e 80 literais dos DFM terminam em espaço de enchimento, sinal de
texto mais curto escrito por cima do original:

```
Uniforme inserido no jogo!!!.
A MCR foi salva!!!.
Numero do uniforme invalido ([33 ... 99] somente na Mastere
```

Aquele `Mastere` é `Master League` decepado — o PT ficou maior que o espanhol e
o tradutor cortou. Nada foi realocado: o timestamp do PE continua o de 2002 e
`.text` está intacto, então **todo endereço desta análise vale para o binário
autêntico do Obocaman**.

Os identificadores continuam em espanhol (`jugador`, `bandera`, `equipo`,
`estrategia`, `tirador`, `dorsal`, `careto`) porque são símbolos de compilação,
fora do alcance de um patch de string.

**Onde o enchimento está, e onde não está.** Esta seção afirmava um número
maior sem dizer onde contou. A WTE-TASK-05 mediu `.data` e achou **13**; o resto
está em `.rsrc`, isto é, em *caption* de formulário — pelo mesmo critério, os 18
DFM trazem **80** literais com enchimento. A conclusão desta seção continua de
pé; o que muda é onde procurar as outras, e a resposta é **nos `.dfm`**. Detalhe em
[`../wte/re/strings.md`](../wte/re/strings.md) e a reconciliação em
[`../wte/re/fase-1.md`](../wte/re/fase-1.md).

E não há acento errado: das 765 strings de `.data`, **zero** trazem byte acima
de `0x7E`. O tradutor **removeu** os acentos (`Numero`, `invalido`, `Preco`), em
vez de errar a codificação — não há encoding a consertar, há texto a reescrever.

**Decisão:** o app Lazarus nasce com strings em **pt-BR reescritas do zero**,
não copiadas do patch. As do patch estão truncadas, sem acento, e são trabalho
de terceiro sem licença. As mensagens originais em espanhol, quando
recuperáveis, servem de referência de *sentido*.

### 1.6 Os formulários saem inteiros

18 blocos `TPF0` em `.rsrc`. Um decodificador de DFM binário de ~90 linhas de
Python já extraiu **6.214 linhas** de definição legível:

```
object MainForm: TMainForm
  Caption = ' W11 Team Editor PT by chagas_michel!'
  ClientHeight = 475
  ClientWidth = 522
  Font.Name = 'MS Sans Serif'
  OnCreate = 'FormCreate'
  OnShow = 'FormShow'
  object SpeedButton1: TSpeedButton
    ...
```

Censo de componentes nos 18 formulários, **medido pelo `dfm_extract.py`** — o
censo por formulário está em
[`../wte/re/dfm/censo.md`](../wte/re/dfm/censo.md):

| Classe | Qtd | | Classe | Qtd |
|---|---:|---|---|---:|
| `TLabel` | 182 | | `TGroupBox` | 10 |
| `TImage` | 45 | | `TRadioButton` | 9 |
| `TStaticText` | 37 | | `TEdit` | 6 |
| `TBitBtn` | 32 | | `TOpenDialog` | 3 |
| `TShape` | 32 | | `TTrackBar` | 3 |
| `TSpeedButton` | 28 | | `TActionList` | 2 |
| `TScrollBar` | 20 | | `TBevel` | 2 |
| `TUpDown` | 12 | | `TBrowseURL` | 2 |
| `TComboBox` | 11 | | `TListBox` | 2 |
| | | | `TSaveDialog` | 2 |
| | | | `TTimer` | 1 |

Vinte classes distintas, **441 componentes**. Um deles não tem nome — um
`TStaticText` de 4×4 px no `MainForm`, que o DFM escreve como `object
TStaticText`, sem identificador. É o tipo de objeto que uma contagem apressada
perde, e por isso a WTE-TASK-09 reconta os `.dfm` e aborta se discordar do
censo.

**Dezenove das vinte classes têm equivalente direto na LCL** — ver §5.
`TBrowseURL` é a ação padrão da própria VCL (unidade `Extactns`), não
componente de terceiro, e é o único a substituir — medido na WTE-TASK-07.

Os `<bin N>` no dump são bitmaps embutidos, e são **118**: 18 ícones de
formulário, 41 `Picture.Data` (dos 45 `TImage`; as quatro bandeiras só existem
em runtime), 32 glyphs de `TBitBtn` e 27 de `TSpeedButton`. O decodificador da
Fase 1 tem que preservá-los, não descartar.

### 1.7 A tabela de offsets, e por que ela é o atalho

Dos 69 `OFS_*` que este repositório já conhece, **19 aparecem literalmente no
binário do Obocaman**. E não espalhados: quase todos num bloco contíguo de
`.data`, a partir de `0x004231a0`:

```
va 0x004231a0  =    2002316   OFS_TEAM_NAME_KANJI
va 0x004231a4  =    4598596   OFS_TEAM_MIXED_CASE_NAME
va 0x004231b8  =    2003996   OFS_TEAM_NAME_3
va 0x004231bc  =    1012640   OFS_TEAM_NAME_1
va 0x004231c0  =    2830160   OFS_TEAM_NAME_4
va 0x004231c4  =    2028267   OFS_ML_TEAM_NAME_7
va 0x004231c8  =    1881968   OFS_TEAM_NAME_2
va 0x004231cc  =    5651448   OFS_TEAM_NAME_6
va 0x004231d0  =    2004996   OFS_TEAM_ABBREV_1
va 0x004231d4  =    4234484   OFS_TEAM_ABBREV_3
va 0x004231d8  =    5651068   OFS_TEAM_ABBREV_2
```

Isso é um **array global de offsets**, e ele coincide com o nosso. Consequência:
qualquer instrução que indexe `0x004231a0` está mexendo em nome de time, e a
gente sabe disso **sem decompilar uma linha**. O mesmo vale para
`OFS_FLAG_SHAPE_COPY_1..5`, `OFS_COST_NATIONAL`, `OFS_COST_NC`, `OFS_LINK_ML`.

Os outros 50 offsets não batem porque o Obocaman ou usa aritmética (base +
constante) ou nomeia regiões que o Moriero não nomeou. Descobrir esses 50 é
trabalho da Fase 3 — mas partindo de 19 confirmados e de um formato **já
documentado e testado byte a byte** contra o `ed.exe`.

> **Medido depois, e corrige o parágrafo acima:** há um terceiro motivo, e ele
> responde por 17 dos 50. Esses não são endereço de campo nenhum — são artefato
> do jeito de **ler** do Moriero: ponto de retomada quando um registro cai em
> cima da fronteira de setor (14) e base de varredura sequencial (3). O
> Obocaman não varre; salta direto para o registro que a tela mostra, e por
> isso nunca passa por eles. Os outros 33 foram endereçados sob `strace`.
> Veredito linha a linha em [`../wte/re/offsets-novos.md`](../wte/re/offsets-novos.md)
> (WTE-TASK-19).

Nenhum projeto de RE começa sabendo o formato do arquivo-alvo. Este começa.

### 1.8 Ativos externos: nada a reverter

```
data/dat.bin           145.408 bytes, começa com "MC" (cabeçalho de memory card PSX)
image/banderas/         53 .bmp
image/uniformes2d/     105 .bmp
image/pelo/             32 .bmp
image/barba/             7 .bmp
image/careto_base.bmp    1 .bmp
```

`53 + 105 + 32 + 7 + 1 =` **198** bitmaps e um blob, todos em formato aberto,
todos em disco. O app Lazarus lê os mesmos arquivos. **Zero trabalho de RE
aqui** — só descobrir a convenção de nome↔índice, que os handlers revelam, e
que a WTE-TASK-08 reconstruiu em
[`../wte/re/assets.md`](../wte/re/assets.md).

*(Esta prosa somava errado as cinco linhas acima; corrigido na WTE-TASK-09.)*

---

## 2. Ressalva legal — leia antes da Fase 0

O `we-team-editor.exe` é obra do **Obocaman (2002)**, sem licença concedida,
igual ao código herdado do Moriero e do thyddralisk que o
[NOTICE.md](../NOTICE.md) já registra. O `we-team-editor/` está no `.gitignore`
justamente por isso: binário de terceiro sem fonte e sem licença não entra no
repositório.

**Uma exceção, decidida em 2026-08-06.** Os 118 blobs de formulário
(`Icon.Data`, `Picture.Data`, `Glyph.Data` — 816.880 bytes) **estão**
versionados, como hex inline nos 18 `wte/forms/*.lfm`. O `.lfm` não é
documentação, é o formulário: sem o hex a janela abre sem ícone e sem glifo, e a
WTE-TASK-12 — o gate da fase 2 — compararia contra uma tela que não é a do port.
O registro completo da decisão está em
[`../wte/re/dfm/README.md`](../wte/re/dfm/README.md). O restante da arte (os 198
`.bmp` e o `dat.bin`) continua fora, e os blobs soltos de `wte/re/dfm/blobs/`
também.

Distinção que importa e que orienta o método deste plano:

| Atividade | Postura |
|---|---|
| Analisar o binário para **entender o formato do jogo** | Interoperabilidade. É o que o repo já faz com o `ed.exe`. |
| **Documentar comportamento** como especificação | Fato observável, não expressão autoral. |
| Reimplementar a partir da especificação | Trabalho novo. É o alvo. |
| Transcrever saída de decompilador para Pascal | **Evitar.** Vira obra derivada. |

**Método adotado: recuperação de especificação, não transcrição.** O
decompilador serve para *responder perguntas* — "que bytes esta rotina grava?",
"qual é a fórmula?" — e a resposta vai para um documento de especificação em
`wte/re/spec/`. O código Pascal é escrito **a partir do documento**, não a
partir do C++ decompilado. Além de mais defensável, dá código melhor: o
decompilado de C++Builder é ilegível (§8.1) e transcrevê-lo importaria a
estrutura de 2002 junto.

Se o app for publicado, o `NOTICE.md` ganha uma seção sobre a linhagem do
Obocaman, no mesmo tom das existentes. **Isso é decisão do usuário, não minha —
não publique sem confirmar.**

---

## 3. Ferramental

### 3.1 O que já existe na máquina

| Ferramenta | Uso |
|---|---|
| `objdump -d -M intel` | disassembly i386 (binutils) |
| `strings`, `xxd`, Python 3.13 | extração e scripts |
| Wine 32-bit via runner do Bottles | rodar o `.exe` (`make wte` já faz) |
| Xvfb `:98`, `xdotool`, `import` | dirigir e capturar a janela |
| `we2002_core` + `Offsets.hpp` | oráculo de formato |
| `roms/golden-european-deluxe.bin`, `roms/japanese-shift-jis.bin` | imagens de teste |

### 3.2 O que falta instalar

| Pacote | Para quê | Estado |
|---|---|---|
| `lazarus` 3.0, `fpc` 3.2.2 | o alvo | disponíveis no `noble/universe`, **não instalados** |
| Ghidra ≥ 11 (+ JDK 17/21) | decompilador | **não instalado**, não empacotado no Ubuntu |
| `python3-pefile` | parsing de PE em script | **não instalado** |

Nenhum decompilador está presente hoje: sem Ghidra, IDA, radare2, rizin ou
retdec. Ghidra é a escolha por ser gratuito, ter decompilador de x86-32 decente
e permitir convenção de chamada customizada — que é requisito duro aqui (§8.1).

Alternativa se Ghidra não for aceitável: **`objdump` + anotação manual**. Viável
para as quatro features-alvo, doloroso para os 96 handlers. Recomendo Ghidra.

### 3.3 Confirmar antes de começar

- `apt install lazarus fpc` puxa GTK2 e o `fpc-src`; conferir que
  `lazbuild` compila um projeto vazio para GTK2 no host.
- Ghidra precisa de JDK 17 ou 21. Conferir qual está instalado.
- O `make wte` **já funciona** e depende do stack X **i386** no host. Se ele
  quebrar, o oráculo comportamental morre junto — validar antes de tudo.

---

## 4. Estratégia

### 4.1 Três recuperações independentes, em paralelo

O trabalho se decompõe em três eixos que quase não se bloqueiam:

```
FORMA          DADOS                    COMPORTAMENTO
18 DFM         tabela de offsets        96 handlers
   ↓              ↓                        ↓
18 LFM         camada de I/O            lógica em Pascal
   ↓              ↓                        ↓
mecânico       ancorado no             decompilação
(script)       we2002_core             dirigida
```

**Forma** é mecânica: um conversor DFM→LFM resolve os 18 formulários de uma vez.
**Dados** parte de 19 offsets já confirmados e de um formato já testado.
**Comportamento** é o custo real, e é onde os 96 nomes de handler pagam.

Só o eixo comportamento é caro. Os outros dois são de dias, não semanas.

### 4.2 Dois oráculos, não um

O `newWe2002` tinha um oráculo (`ed.exe`). Aqui há dois, e o segundo é
incomum de se ter:

**Oráculo A — comportamental.** `we-team-editor.exe` sob Wine, dirigido por
`xdotool` no `:98`. Responde "que bytes esta operação grava?". É o mesmo padrão
do `tools/golden_check.sh` já existente, e o `make wte` já resolveu prefix,
arquitetura e mapeamento de unidade.

**Oráculo B — de formato.** O `we2002_core` deste repositório, cujo `Load`/`Save`
já é byte-idêntico ao `ed.exe` nas duas ROMs. Responde "o que significam estes
bytes?". Nenhum RE normal tem isto.

Combinados: quando o oráculo A mostra que `grabar_camisetaClick` mexeu nos bytes
X..Y, o oráculo B diz na hora que X..Y é a região de uniforme do time N. A
semântica sai sem decompilar.

**Corolário metodológico:** *sempre tentar o diff antes do decompilador.* Muita
pergunta ("onde fica a cor secundária da camisa?") se responde em minutos
alterando um controle na janela do Wine, gravando e fazendo `cmp` — e o
decompilador só entra quando a pergunta é sobre *fórmula*, não sobre *local*.

### 4.3 Ordem: casca antes de recheio

Construir o app Lazarus vazio primeiro — todos os 18 formulários, todos os ~430
controles, todos os 96 handlers como stub que só loga o próprio nome —, e
**depois** preencher handler a handler. Três razões:

1. Cada handler preenchido é testável no ato, contra o oráculo A.
2. A camada de UI, que é 60% do volume e 5% da dificuldade, sai do caminho cedo.
3. O stub que loga o nome transforma o app numa ferramenta de RE: clicar no
   original e no stub lado a lado mostra a ordem real de disparo dos eventos —
   que nenhuma análise estática dá.

### 4.4 O que é gerado e o que é escrito

**Nenhum decompilador emite Object Pascal.** Ghidra, IDA e retdec devolvem
pseudo-C; não existe backend Pascal em nenhum deles. O mais próximo é o
**IDR (Interactive Delphi Reconstructor)**, que entende binário Delphi/BCB e
devolve esqueleto Pascal — mas é Windows-only, a saída não compila, e o que ele
recuperaria aqui (formulários e nomes de rotina) **já foi recuperado com ~90
linhas de Python**. Não paga o custo de adotar.

Isso não significa escrever tudo à mão. A maior parte do fonte final sai de
gerador, e só um bloco vem de teclado:

| Bloco | Origem | Como |
|---|---|---|
| 18 formulários `.lfm` | os DFM de `.rsrc` | conversão de formato — `dfm2lfm.py` |
| Esqueleto das 18 unidades | DFM × tabela de métodos publicados | campos dos componentes, as 96 assinaturas, o `var` global |
| Bloco de offsets | `Offsets.hpp` + a tabela em `0x004231a0` | dado puro |
| Tabelas estáticas | `src/core/Tables.cpp` (704 linhas) | dado puro |
| **Camada de dados** | `we2002_core` deste repo | transpilação — ver §4.5 |
| **Corpos dos 96 handlers** | `re/spec/*.md` | **escrito à mão** |

Só a última linha é trabalho manual de verdade. E ela é a única que **tem** de
ser manual, pelos dois motivos que já ficaram registrados: a lógica só existe
compilada (§1.2) e transcrever decompilado vira obra derivada (§2).

**Medido com a fase 4 em curso: 55,6% do Pascal da casca é saída de gerador** —
9.449 linhas geradas contra 7.546 escritas à mão. Dessas 7.546, 352 são andaime de
projeto (`wte.lpr` 31, `retrace.pas` 125, `wtemain.pas` 196) e o resto é corpo escrito à
mão em `src/impl/` e nas unidades de formato, que é exatamente a última linha da
tabela acima: a parte que tem de ser manual. São de duas formas — `<unidade>.<handler>.inc`, um corpo de
handler, e `<unidade>.aux.inc`, as rotinas internas que o original chama de mais
de um handler e que por isso não são método publicado. (Eram 353 e 96,2% no
fechamento da fase 2; a WTE-TASK-22
acrescentou ao `wtemain.pas` o argumento posicional de imagem e levou a 95,9%.
A fração é medida, então ela se move — e daqui em diante ela **cai** a cada
handler implementado, que é o sinal certo: o denominador da §4.4 é o Pascal da
casca, e o que sobra de manual é o que a §2 diz que não tem gerador possível.
Ela cai pelas **duas** pontas, e a segunda surpreende: implementar um handler
tira linhas do numerador também, porque o stub `REStub` que ele substitui era
saída de gerador — cinco linhas com o `{$PUSH}`/`{$POP}` viram duas com o
`{$I}`. Foi o que a WTE-TASK-30 mediu ao escrever doze corpos de uma vez: 9.416 →
9.374 geradas, 6.476 → 6.816 à mão. A CORR-WTE-081 mediu o mesmo movimento por
outra causa: 6.816 → 7.233 à mão sem que um só corpo novo explicasse o salto,
porque o que entrou foi uma **unidade** — o `wte_ficha.pas`, para onde desceu o
buffer de jogador quando o `Comple.` da ficha passou a precisar dele de fora do
`ep2002_mainform`. Mudança de estrutura conta no denominador como corpo conta,
e é bom que conte: unidade escrita à mão é exatamente o que a §4.4 mede. A
segunda passagem dela — o `OK` do editor de cor — moveu as **duas** pontas de
uma vez, e é o único caso até aqui: 7.233 → 7.546 à mão pelo escritor do bloco
de cor, e 9.372 → 9.449 geradas porque a tabela de 95 bytes de
`0x00423247` entrou por gerador novo, o `dump_blococor.py`. Numerador e
denominador crescendo juntos é o sinal de que a fronteira entre dado e lógica
foi respeitada.)
O número sai do
[`check_fase2.py`](../wte/tools/check_fase2.py) e a conta inteira está em
[`../wte/re/fase-2.md`](../wte/re/fase-2.md), inclusive por que as 25.712
linhas de hex dos blobs ficam fora dela. **A fração da §4.3 — "a UI é 60% do
volume" — continua sem verificação**, e só fecha depois das fases 3 e 4: hoje a
UI é a única camada que existe.

**Disciplina de código gerado — a mesma do resto do repositório.** Nada de
editar `.lfm` ou unidade gerada à mão; mexe-se no gerador e reexecuta. Cada
gerador tem `--check` que compara com o commitado, e o `--check` entra na
bateria de testes, exatamente como `ui_forms` e `glossary` fazem hoje para o
`newWe2002`.

### 4.5 Transpilar o `we2002_core`, não o `wte.exe`

O `Load`/`Save` do app Lazarus **não precisa sair do binário do Obocaman**.
Sai daqui:

```
src/core/Database.cpp                1704
src/core/Player.cpp                   130
src/core/CdImage.cpp                   89
src/core/TextCodec.cpp                 77
src/core/Team.cpp                      16
src/core/include/we2002/Types.hpp     147
src/core/include/we2002/Player.hpp     95
src/core/include/we2002/Team.hpp       91
src/core/include/we2002/CdImage.hpp    77
src/core/include/we2002/Database.hpp   60
src/core/include/we2002/TextCodec.hpp  18
                                     ----
                                     2504 linhas
```

**Os cabeçalhos entram, e o número já foi menor por causa disso.** A primeira
versão desta lista tinha só os cinco arquivos de cima até `Types.hpp` — "~2.150
linhas" — e deixava de fora justamente onde os registros são declarados. Sem
`Team.hpp` não há `Team`, `MlTeam` nem `Formation`, que `Database.hpp:44-48`
usa como campo. O `UNITS` do `wte/tools/port_database_pas.py` lê os 11, e o
`test_nenhuma_entrada_do_core_fica_de_fora` reprova arquivo de `src/core/` que
ninguém reivindicou.

Código deste repositório, já verificado byte a byte contra o `ed.exe` nas duas
ROMs, e escrito num subconjunto estreitíssimo de C++: laço de contagem fixa,
`Seek`, `Read`, `Write`, array, aritmética inteira. Sem template, sem STL além
de array, sem RAII, sem herança. **Esse subconjunto transpila para Pascal por
regra.**

Precedente direto, no mesmo repositório: `tools/port_database.py` já faz
transpilação de C++ MFC para C++ portável, extraindo `carica_dabin` e
`OnWriteCD` verbatim do legado e aplicando substituições listadas. O
`port_database_pas.py` herda dele **os dois guards sem alteração**:

- **`FORBIDDEN`** — recusa emitir se sobrar construção que a tabela não
  reconhece, em vez de produzir código quebrado. Pegou dois erros na Fase 2 do
  port Qt.
- **`check_seeks()`** — conta seeks absolutos e relativos na entrada e na saída
  e recusa se não baterem. Existe porque uma regex com `[^,]` atravessou uma
  quebra de linha e **trocou** um `Seek(begin)` por um `SeekCurrent`; compilava,
  passava nos testes e passava no ASan, e só o confronto com o `ed.exe` mostrou.

> **Onde o decalque para, e isso foi medido na WTE-TASK-17.** O que ele **não**
> herda é a técnica: o `port_database.py` pode ser substituição textual pura
> porque a fonte e o alvo dele são a **mesma linguagem**. C++ → Pascal não pode.
> Statement e expressão transpilam por regra, como esta seção diz; **estrutura
> não** — bloco, cabeçalho de laço, assinatura de função e declaração de
> variável não têm forma comum, e nenhuma regex os alcança sem casamento de
> chave. O `port_database_pas.py` entrega a camada de statement e põe a
> estrutura no `FORBIDDEN`; o passe estrutural é da WTE-TASK-18. Ver
> [`../wte/re/transpilador.md`](../wte/re/transpilador.md).

O segundo guard fica **mais** valioso na travessia para Pascal, não menos: o
`TFileStream` do FPC tem `Seek(offset, soBeginning)` e `Seek(offset, soCurrent)`
com a mesma cara, e o mesmo erro é igualmente silencioso.

**Consequência para o cronograma:** a Fase 3 deixa de ser porte manual e vira
execução de gerador mais conferência. O que sobra de manual nela é decidir o
mapeamento de tipo (§8.6) e escrever a tabela de substituição.

**Medido no fechamento da fase 3 (WTE-TASK-21): 91,8% da camada de dados é
transpilação por regra** — 3.389 linhas contra 303 escritas à mão, sobre 3.692
emitidas, contando linha física dos dois lados (a fração já foi 92,5%, quando o
total contava branco e o manual não). A razão entrada × saída é **por
gerador**, e não sobre a soma: o
transpilador infla (2.504 → 2.984, 1,19) e o `gen_tables_pas.py` encolhe
(852 → 708, 0,83). Os oito `.pas` são saída de gerador sem
exceção; as 303 não são porte de lógica do editor, e sim as quatro peças que o
[`../wte/re/tipos.md`](../wte/re/tipos.md) já tinha decidido que **não**
transpilam — `CdImage` (`std::fstream`), `SquadNumbers` (bitfield), o sidecar
`_url.txt` e o `Reporter` (`std::function`) —, e elas moram nas constantes do
próprio gerador, nunca no arquivo de saída. O número sai do
[`check_fase3.py`](../wte/tools/check_fase3.py) e a conta inteira está em
[`../wte/re/fase-3-fechamento.md`](../wte/re/fase-3-fechamento.md).

**Limite, e é duro:** o transpilador digere **código nosso**, estável e testado.
Não estender para engolir saída de decompilador. Ali a entrada vira arbitrária,
o `FORBIDDEN` deixa de segurar, e o gerador passa a emitir Pascal quebrado com
cara de certo — que é o modo de falha mais caro que este projeto pode ter.

---

## 5. Mapeamento VCL → LCL

Dezenove das vinte classes são diretas. A LCL foi feita para isso.

| VCL (C++Builder 6) | LCL (Lazarus 3.0) | Observação |
|---|---|---|
| `TForm`, `TLabel`, `TEdit`, `TListBox`, `TComboBox`, `TGroupBox`, `TRadioButton`, `TBevel`, `TTimer`, `TShape`, `TImage`, `TScrollBar`, `TTrackBar`, `TUpDown`, `TSpeedButton`, `TBitBtn`, `TOpenDialog`, `TSaveDialog` | mesmo nome | 1:1 |
| `TStaticText` | `TStaticText` | existe, mas com quirks de fundo transparente no GTK2 — 37 instâncias, conferir cedo |
| `TActionList` | `TActionList` | existe; checar se as ações padrão (`Stdactns`) usadas têm par |
| **`TBrowseURL`** | **sem par** | ação padrão da VCL (unidade `Extactns`), não componente de terceiro — medido na WTE-TASK-07. A LCL não a tem; substituir por `TLabel` + `OpenURL()` de `LCLIntf`. 2 instâncias. |

Unidades VCL vistas nos imports e o que fazer com cada uma:

| Unidade | Situação |
|---|---|
| `Forms`, `Controls`, `Stdctrls`, `Extctrls`, `Buttons`, `Graphics`, `Classes`, `Dialogs`, `Comctrls` | par direto na LCL |
| `Sysutils`, `Strutils`, `Types`, `Variants`, `Typinfo` | FPC tem todas |
| `Registry` | **transitiva.** Nenhum símbolo além do par de ciclo de vida, nenhuma chamada. Nada a portar. |
| `Printers` | **transitiva.** Idem: o app não imprime, e nenhum formulário tem diálogo de impressão. |
| `Comobj` | **transitiva.** Tem uma chamada — o `EOleException` do caminho de asserção da RTL —, e ela não está em handler nenhum. Não é o `TBrowseURL`. |
| `Winhelpviewer` | **transitiva.** Não há ajuda `.hlp`, nem `HelpFile`/`HelpContext` em formulário nenhum. |

Essas quatro linhas eram itens de investigação da Fase 1 e foram **fechadas
pela WTE-TASK-07**, com a medida em
[`wte/re/unidades-vcl.md`](../wte/re/unidades-vcl.md). O palpite que as
enquadrava — "import de unidade em app C++Builder frequentemente é dependência
transitiva sem uso real" — se confirmou nas quatro, e o motivo é estrutural:
**27 das 42 unidades Borland importadas trazem apenas
`@X@initialization$qqrv` e `@X@Finalization$qqrv`**, que não são API, e sim o
par que a tabela de módulos do executável percorre no arranque.

Duas hipóteses desta seção morreram junto, e vale registrar por quê:

- **não há configuração nenhuma a migrar.** `Inifiles` também é só ciclo de
  vida, e nenhuma string do binário cita chave de registry ou `.ini`. O
  `~/.config/` não ganha arquivo.
- **`Comobj` não é o `ShellExecute` do `TBrowseURL`.** O `.exe` não importa
  `SHELL32.DLL`; o `TBrowseURL` é a ação padrão da VCL (unidade `Extactns`,
  não componente de terceiro) e é disparado por método dinâmico através do
  VMT, resolvido dentro do `vcl60.bpl`.

Nenhuma das quatro gera item para fase alguma.

### Duas diferenças de plataforma já conhecidas

- **`MS Sans Serif` não existe no host.** O `newWe2002` já sofreu isso: o Qt
  substitui e rótulo apertado corta. Mesmo problema aqui, mesma resposta —
  aceitar, e conferir os rótulos apertados na comparação visual da Fase 2.
- **Geometria absoluta.** Os 441 controles têm `Left`/`Top` fixos, como os 434
  do `ed.rc`. **Não** introduzir layout automático: a fidelidade é o critério, e
  o `newWe2002` já provou que geometria absoluta funciona.

---

## 6. Testes: o golden test, adaptado

O repo já tem a máquina toda. `tools/golden_check.sh` faz duas cópias da imagem,
passa uma pelo oráculo sob Wine e a outra pelo port, e compara. Aqui a estrutura
é idêntica, trocando o oráculo:

```
copia_A.bin ──▶ we-team-editor.exe (Wine 32-bit, :99, xdotool) ──┐
                                                                  ├─▶ cmp
copia_B.bin ──▶ app Lazarus (nativo, :99, xdotool) ──────────────┘
```

**Herdar as guardas, sem exceção.** O `golden_check.sh` acumulou proteções que
custaram bugs para descobrir, e todas se aplicam:

- Fixar `DISPLAY=:98` dentro do script; não confiar no que o `ctest` repassa.
- Recusar-se a começar se houver janela grande já aberta no `:98` — dirigir a
  janela errada produz diff que parece bug do app.
- Restringir os candidatos de janela ao `_NET_WM_PID` do processo lançado.
- Nunca apontar para `roms/` diretamente. Cópia, sempre.

**Diferença relevante:** o `wte.exe` **tem título de janela**
(`W11 Team Editor…`), ao contrário do `IDD_ED_DIALOG` do `ed.exe`, que só se
acha pelo tamanho. Isso simplifica a busca — mas o app Lazarus deve então ter
título **diferente** do original, senão os dois lados se confundem.

### Níveis de teste

| Nível | O que cobre | Depende de |
|---|---|---|
| Unitário (FPCUnit) | codificação de atributo, fórmula de preço, parser de `.mcr` | nada |
| Round-trip headless | abrir + gravar sem editar reproduz o que o original reproduz | 1 ROM |
| Golden por operação | uma operação de tela por vez, byte a byte | Wine + `:98` |
| Visual | screenshot do formulário Lazarus vs do original | Wine + `:98` |

O visual não deve ser automatizado com tolerância de pixel — fonte diferente
garante divergência. É inspeção humana, uma vez por formulário, na Fase 2.

---

## 7. Fases

### Fase 0 — Infra

Instalar `lazarus`, `fpc`, Ghidra + JDK, `python3-pefile`. Confirmar que
`lazbuild` produz binário GTK2 e que `make wte` ainda abre a janela.

Criar o esqueleto:

```
wte/
  src/            unidades Pascal
  forms/          os .lfm
  assets/         symlink ou cópia de image/ e data/
  re/             produto da engenharia reversa
    dfm/          os 18 DFM em texto
    spec/         a especificação recuperada, por handler
    published_methods.tsv
    offsets.md
  tools/          geradores e scripts de golden test
    dfm_extract.py        .rsrc  -> os 18 DFM em texto          (Fase 1)
    dfm2lfm.py            DFM    -> .lfm + esqueleto das units  (Fase 2)
    port_database_pas.py  we2002_core -> camada de dados        (Fase 3)
    gen_tables_pas.py     Tables.cpp + Offsets.hpp -> const     (Fase 3)
    golden_check.sh       wte.exe vs app Lazarus                (Fase 4+)
  tests/
```

Os quatro primeiros são **geradores**: a saída deles não se edita à mão, cada um
tem `--check` e o `--check` entra na bateria de testes. Mesma regra que vale
hoje para `src/core/Database.cpp` e `src/app/ui/` no `newWe2002`.

`wte/re/` é **documentação**, versionável. `wte/assets/` aponta para
`we-team-editor/`, que é gitignored.

> **Pronto quando:** `lazbuild` compila um projeto vazio e abre janela no `:98`.

---

### Fase 1 — Extração estática total

Sem decompilador ainda. Tudo que sai de `objdump`, `strings` e Python.

1. **`tools/dfm_extract.py`** — os 18 `TPF0` para texto DFM. O protótipo já
   existe e decodificou 15 de 18 limpos; falta acertar o byte de flags de
   objeto nos 3 restantes (`ficha_creditos_equipo`, `ficha_movertodos`,
   `ficha_warning_2`) e **preservar os blobs binários** em vez de resumir como
   `<bin N>`.
2. **`published_methods.tsv`** — os 96, com endereço, ordenados, e a qual
   formulário pertencem (dá para inferir pelo VMT que contém a tabela).
3. **Inventário de strings** — todas as strings do `.data`, com endereço e
   quem as referencia (`objdump -d` + grep de endereço). Vira `re/strings.tsv`.
4. **Mapa de offsets** — os 19 confirmados, a tabela em `0x004231a0`, e uma
   varredura por outros valores plausíveis (dword entre 1.000.000 e 8.000.000
   em `.data` ou como imediato em `.text`). Vira `re/offsets.md`.
5. **Resolver as quatro dúvidas de unidade** — `Registry`, `Printers`,
   `Comobj`, `Winhelpviewer`: procurar chamada real no disassembly.
6. **Convenção de nome dos assets** — quais dos 105 `uniformes2d/*.bmp`
   correspondem a que time; idem para as 53 bandeiras. Provavelmente índice
   direto, confirmável pela tela.

> **Pronto quando:** `re/` tem os 18 DFM completos, os 96 métodos, o mapa de
> strings e o mapa de offsets, e as quatro unidades duvidosas têm veredito.

---

### Fase 2 — Casca: a UI inteira, sem lógica

1. **`tools/dfm2lfm.py`** — conversor DFM → LFM. O LFM é sintaticamente quase
   o DFM textual; o trabalho está em (a) blobs binários no formato hex da LCL,
   (b) `TBrowseURL` → `TLabel`, (c) propriedades que a LCL não tem, que viram
   comentário em vez de sumir calado.
2. **18 unidades Pascal**, uma por formulário, nomes fiéis aos originais
   (`ep2002_about.pas`, …), com os 96 handlers como stub:
   ```pascal
   procedure TMainForm.colorearClick(Sender: TObject);
   begin
     REStub('colorearClick');   // registra em wte/re/trace.log
   end;
   ```
3. **Comparação visual** dos 18 formulários contra o original sob Wine.
4. **Trace de eventos** — clicar as mesmas coisas nos dois e comparar a ordem
   de disparo. Isso alimenta a Fase 4.

> **Pronto quando:** o app abre, os 18 formulários **aparecem**, os 96 stubs
> logam, e a comparação visual foi conferida formulário a formulário.

> **"Navegáveis" era impossível, e a WTE-TASK-14 corrigiu o critério.** Quem
> abre formulário são os handlers, e nesta fase eles são stub por definição —
> pedir navegação aqui é pedir a fase 4. O que existe é `--show`, andaime
> explícito da WTE-TASK-11, e foi com ele que os 18 foram capturados. Navegação
> de verdade chega com a WTE-TASK-25. Medido no fechamento: 18 de 18 abrem no
> `:98`, 96 de 96 stubs logam, 16 `FormCreate` no arranque (os dois `ficha_error`
> não têm `OnCreate`). Ver [`../wte/re/fase-2.md`](../wte/re/fase-2.md).

Nesta fase o app não toca a imagem de CD. Zero risco.

---

### Fase 3 — Camada de dados, **gerada**

Onde o oráculo B paga. E, pela §4.5, isto é execução de gerador mais
conferência — não porte manual.

1. **Escrever `tools/port_database_pas.py`**, decalcado do `port_database.py`
   existente: mesma extração verbatim da entrada, outra tabela de substituição,
   **os dois guards intactos** (`FORBIDDEN` e `check_seeks()`). O decalque
   cobre statement e expressão; o **passe estrutural** (bloco, laço, assinatura,
   `record`) é trabalho próprio, e é da WTE-TASK-18 — ver a ressalva na §4.5.
2. **Definir o mapeamento de tipo antes de rodar qualquer coisa.** É a única
   decisão de projeto real desta fase, e é onde mora a mordida da §8.6:

   | C++ (`we2002_core`) | Pascal (FPC) | Motivo |
   |---|---|---|
   | `std::uint8_t` | `Byte` | |
   | `std::uint32_t` | `LongWord` | **nunca** `Cardinal` sem checar, nunca tipo dependente de plataforma |
   | bitfield de `SquadNumbers` | registro empacotado + acessor | FPC tem bitpacked record, mas a ordem de bit difere entre compiladores — gerar acessor explícito e testar |
   | `char[N]` | `array[0..N-1] of AnsiChar` | **não** `string`; o truncamento é load-bearing (§6, nível unitário) |
   | `char` numérico | `ShortInt` | **com sinal**, como o `char` do x86: a UI o alarga com `static_cast<int>`, e `Byte` mostraria 200 onde a referência mostra −56 |
   | `CdImage` | wrapper sobre `TFileStream` | ponteiro único, leitura curta não é erro (`Read`, **nunca** `ReadBuffer`), **nunca** recalcular EDC/ECC |

   **Fechado pela WTE-TASK-15**, com a tabela completa — os 16 tipos que a
   entrada real usa —, as cinco decisões difíceis escritas e o teste que prova
   cada uma, em [`../wte/re/tipos.md`](../wte/re/tipos.md). A tabela acima é o
   resumo; o `tipos.md` é a fonte para os geradores.

3. **Gerar** o equivalente Pascal de `Database`, `Player`, `Team`, `CdImage`,
   `TextCodec` e `Types` — **2.504 linhas** de entrada, medidas, contando os
   cabeçalhos que declaram os registros (ver a §4.5). `Tables.cpp` (704 linhas) e
   os 69 `OFS_*` saem por gerador separado, mais simples, por serem dado puro.
4. **Descobrir os 50 offsets restantes** por diff dirigido: mudar um campo na
   janela do Wine, gravar, `cmp`. Cada campo custa dois minutos. Os que
   aparecerem entram na entrada do gerador, não no arquivo gerado.
5. **Round-trip headless** contra as duas ROMs, comparando com o
   `we2002_core` campo a campo.
6. **Registrar o `--check`** do gerador na bateria de testes.

> **Pronto quando:** um programa de console em Pascal abre a ROM, lista os times
> e os jogadores com os mesmos valores que o `we2002_core` reporta, e o código
> que faz isso é 100% saída de gerador.

**Ainda sem decompilador.** Se a Fase 3 fechar assim, o Ghidra fica só para as
fórmulas da Fase 5 — que é o cenário bom.

---

### Fase 4 — Comportamento: os 96 handlers

Aqui entra o decompilador, e só aqui.

**Ordem por dependência, não por endereço.** Primeiro os que carregam estado
(`lista_equiposChange`, `mostrar_jugadorClick`, `FormCreate` de cada
formulário), porque tudo depende deles. Depois os de edição. Por último os de
gravação.

Ciclo por handler:

1. Ler o disassembly a partir do endereço conhecido.
2. Cruzar com as referências a `0x004231a0` e às strings mapeadas na Fase 1.
3. Quando a lógica for local, **testar em vez de ler**: exercitar no Wine e
   diffar a imagem.
4. Escrever `re/spec/<handler>.md` — o que entra, o que sai, que bytes muda.
5. Implementar em Pascal **a partir do `.md`**.
6. Golden test daquela operação.

Fica em `re/spec/` o registro de cada handler com o veredito: *implementado*,
*trivial* (só habilita/desabilita controle), *divergência deliberada*, ou
*não portado*.

**Duas gravações fecham fora do grupo de gravação.** `boton_mcr2isoClick` e
`grabar_camisetaClick` dependem de fórmula — o parser de `.mcr` e o render 2D —,
e por isso fecham nas tasks que produzem essa fórmula (§5.2 e §5.3), junto com a
origem dos bytes. Cada uma leva consigo as regras de gravar nesta imagem: nunca
recalcular EDC/ECC, o salto de fronteira de setor, cópia sempre, o diff de
controle já medido, e a descarga bufferizada que faz o `fseek` seguinte ser quem
grava.

> **Pronto quando:** os 96 têm veredito e nenhum é "não portado" sem
> justificativa escrita.

---

### Fase 5 — As features que motivaram tudo (duas executam na Fase 4)

Estas quatro são as únicas que exigem **fórmula**, não só posição de byte, e
são a única parte onde o decompilador é insubstituível.

**Duas delas executam dentro da Fase 4**, e isso não é desvio de rota. O `.mcr`
(§5.2) e a camisa 2D (§5.3) são a *origem dos bytes* de duas das seis gravações
do editor, e enquanto a gravação morava numa task e a origem noutra havia
**ciclo**: a task de gravação não fechava sem elas, e elas declaravam
`depends_on` a task de gravação. Cada uma passou a carregar a gravação que
viabiliza, e por isso subiu de fase. As quatro continuam sendo o motivo do
projeto; muda só quando duas delas acontecem.

A numeração `§5.x` abaixo é **endereço de seção, não fase de execução** — as
tasks citam essas sub-seções pelo número, e ela fica estável:

| § | task | fase de execução |
|---|---|---|
| 5.1 preço | WTE-TASK-32 | 5 |
| 5.2 `.mcr` | WTE-TASK-28 | **4** |
| 5.3 camisa 2D | WTE-TASK-29 | **4** |
| 5.4 slots de ML | WTE-TASK-33 | 5 |

**5.1 Preço derivado dos atributos.** `etiqprecioClick` (`0x00408bb8`) e o
formulário `jugador`. É aritmética pura sobre os atributos já
decodificados — testável de forma exaustiva: variar um atributo por vez no
original, ler o preço na tela, tabelar, e conferir a fórmula recuperada contra
a tabela. **Não precisa de golden test de imagem**, precisa de tabela de
verdade. Alvo: acerto em 100% de uma amostra grande.

**5.2 Import de `.mcr`.** `boton_mcrClick` (`0x0040c2c8`) e
`boton_mcr2isoClick` (`0x0040c46c`). Formato de memory card do PSX —
parcialmente documentado publicamente, o que ajuda. `data/dat.bin` começa com
`MC`, então provavelmente é um memory card de exemplo e serve de fixture.
**Risco: pode faltar `.mcr` de teste variado.** Mitigação: o
`grabar_memoryClick` (`0x0040f69c`) escreve `.mcr` — dá para gerar fixture com
o próprio original.

**5.3 Camisa e bandeira 2D.** `colorearClick`, `grabar_camisetaClick`,
`malla1/2MouseDown`, `gradienteClick`, `oscurecerClick`, `aclararClick`,
`lista_col0..3Change`, e o formulário `ficha_color` (866 linhas de DFM,
medidas em `wte/re/dfm/ficha_color.dfm`).
A renderização usa os 105 `uniformes2d/*.bmp` como base e aplica cor **na
paleta**: as três rotinas de desenho posicionam o arquivo em `0x36`, que é a
primeira entrada, e reescrevem as primeiras — 16 na bandeira, 15 no uniforme, e
o uniforme roda o bloco duas vezes, uma para `camiseta<n>.bmp` e outra para
`pantalon<n>.bmp`. **Nenhuma varre pixel.** (Esta seção supunha `TBitmap` +
varredura de pixel até 2026-08-20, quando a WTE-TASK-29 mediu; o disassembly
está em [`wte/re/render2d.md`](../wte/re/render2d.md).) O `TLazIntfImage`
continua sendo o certo no port, por outro motivo: ele precisa do **índice** de
cada pixel, e o leitor de BMP da LCL entrega o bitmap já convertido para 32
bpp, com a paleta consumida — daí a `wte/src/we2002_bmp.pas`.
**Fidelidade de cor exige atenção**: paleta e arredondamento de gradiente têm
que bater, e a verificação é diff de bitmap contra captura do original.

**5.4 Slots livres de Master League.** O menor dos quatro: varre a região de ML
e conta vagos. Depende só da Fase 3.

> **Pronto quando:** cada uma das quatro tem teste próprio verde — tabela de
> preço, round-trip de `.mcr`, diff de bitmap, contagem conferida. Duas delas
> são gateadas dentro da Fase 4, junto com a gravação que carregam.

---

### Fase 6 — Paridade e endurecimento

1. **Bateria golden completa**, todas as operações de gravação, nas duas ROMs.
2. **Registro de divergências deliberadas** — no formato que o
   [PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) já usa: o que diverge, por
   que, e que evidência sustenta.
3. **Robustez que o original não tem** — o `newWe2002` aprendeu em Release que
   `strcpy` sem terminador derruba o app em toda imagem aberta. O Pascal com
   strings gerenciadas não tem essa classe de bug, mas *tem* a inversa: o
   original pode depender de truncamento silencioso. Toda vez que a Fase 4
   encontrar buffer de tamanho fixo, o comportamento de estouro entra na spec.
4. **Sem regressão de UI** — reconferir os 18 formulários.

---

### Fase 7 — Acabamento

Ícone, `.desktop`, AppStream, `install` — copiar o padrão que o `newWe2002` já
tem em `packaging/`. Decidir nome do produto (**não** reusar
"WE2002 Team Editor" tal e qual, por causa da §2). Empacotamento
(AppImage/Flatpak) fica **fora**, igual à decisão do plano Linux.

---

## 8. Armadilhas conhecidas

Todas verificadas ou herdadas de dor já paga neste repositório.

### 8.1 O decompilador não conhece `__fastcall` da Borland

**A pior armadilha do projeto, e ela aparece na primeira função.**

C++Builder usa registradores: `this`/1º argumento em `EAX`, 2º em `EDX`, 3º em
`ECX`, resto na pilha. Ghidra assume `__cdecl` por padrão e vai reportar
**funções sem argumentos** que misteriosamente leem lixo — e as três primeiras
variáveis vão sumir da assinatura.

Sintoma no disassembly real, já observado em `colorearClick`:

```asm
00410ea8:  push  ebx
00410ea9:  push  esi
00410eaa:  mov   ebx,eax        ; <-- 'this' chegando em EAX
```

**Correção obrigatória antes de decompilar qualquer coisa:** definir no Ghidra
uma convenção customizada (`EAX, EDX, ECX`, retorno em `EAX`, *caller-cleanup*
para os que sobram na pilha) e aplicá-la a todas as funções. Sem isso, a saída
do decompilador é ruído convincente — o pior tipo de erro, porque parece certo.

### 8.2 Chamada virtual não diz o nome do método

```asm
mov   ecx,DWORD PTR [eax]
call  DWORD PTR [ecx+0xcc]
```

`+0xcc` é um slot de VMT da VCL, e o binário não diz de quem. Duas saídas:

1. **Reconstruir o VMT** a partir de `vcl60.bpl`, que está na pasta e exporta os
   nomes mangled. Trabalhoso, mas resolve de uma vez para todas as classes.
2. **Inferir pelo contexto** — o objeto veio de `[ebx+0x390]`, que o DFM diz ser
   qual componente; `+0xcc` num `TLabel` é quase certamente `SetCaption`.

Começar por (2), que resolve a maioria, e só investir em (1) se travar.

### 8.3 Chamada direta à VCL **já vem nomeada**

O contrário da anterior, e é vantagem: import por nome mangled significa que
`call ds:[@Controls@TWinControl@CreateHandle$qqrv]` se lê direto. Os **267**
imports de `rtl60.bpl`/`vcl60.bpl` são 267 pontos de referência gratuitos —
322 é o total do binário, e os outros 55 são das DLLs do Windows, sem mangling
da VCL (§1.2). Aproveitar.

### 8.4 O app grava in-place — cópia, sempre

Os **três** editores (`ed.exe`, `wte.exe`, o app novo) gravam direto na imagem
de 474 MB. O `make wte` já mantém cópia própria em `work/`. Todo script de
teste faz cópia. Nunca apontar nada para `roms/`.

### 8.5 O `:98` e as regras já escritas

Vale integralmente a seção do topo do [CLAUDE.md](../CLAUDE.md): `DISPLAY=:98`,
`XAUTHORITY` resolvido pelo `ps`, sem window manager, `xdotool windowactivate`
não funciona, `xdotool type --window` embaralha string longa. E:

**`Ctrl+A` não seleciona tudo num `CEdit` do Win32** — nem num `TEdit` da VCL.
Ao escrever teste que digita no original e no app Lazarus, limpar campo com
`End`, `shift+Home`, `BackSpace`.

### 8.6 O original tem 32 bits; o alvo tem 64

O `wte.exe` roda sob `wine` 32-bit e depende do stack X **i386** no host. O app
Lazarus é x86-64 nativo. Consequência sutil: **todo tipo inteiro do modelo de
dados precisa de tamanho explícito**. `Integer` em FPC é 32-bit em ambos, mas
`PtrUInt` e ponteiro não são. O `newWe2002` levou exatamente essa mordida com
`DWORD` virando 64-bit no Linux LP64 e embaralhando número de camisa.

### 8.7 O limite da tabela tem de ser medido dos dois lados

A varredura da §1.7 mostra que o bloco em `0x004231a0` tem buracos (`= 0`) e é
cercado de não-offset. Os dois lados caem por motivos diferentes, e é isso que
obriga a medir cada um com seu critério:

- **abaixo**, em `0x00423190`, está `1869507948` — little-endian `6c 6d 6e 6f`,
  ASCII **`lmno`**, pedaço da tabela de alfabeto vizinha. É o ASCII que fixa o
  limite inferior;
- **acima**, logo após o fim em `0x004231e8`, está `67305984` (`0x04030200`),
  que não passa no filtro por conteúdo, não por ser texto.

Confirmar limite da tabela antes de tratá-la como array — indexar além do fim
foi exatamente o bug do slot 64 num array de 63 que o `newWe2002` documentou.
O critério escrito e as duas medidas independentes do limite superior estão em
[`../wte/re/offsets.md`](../wte/re/offsets.md) (WTE-TASK-06).

### 8.8 O tradutor truncou mensagens

13 strings de `.data` — e 80 literais dos DFM, que são outra população, ver
§1.5 — estão com padding, e pelo menos uma perdeu conteúdo
(`somente na Mastere`). Se a spec de um handler depender de ler a mensagem de
erro para entender a regra de validação, a mensagem pode estar incompleta.

**A recuperação não depende do binário espanhol.** A WTE-TASK-05 mediu que o
bloco de literais do app aparece **três vezes** na `.data`, e as duas cópias
altas não são referenciadas por ponteiro nenhum — são mortas, e por isso o
tradutor não as sobrescreveu. Elas preservam o texto que a viva perdeu:
`somente na Mastere`, referenciada de dentro de `jugador.BitBtn3Click`, tem
gêmea legível com o parêntese fechado e `Master` inteiro. São **três** as
mensagens nessa situação, e o `wte/re/strings.tsv` as marca com
`gemea_difere` na coluna `suspeita_patch` — um `grep` no arquivo que já está
no disco.

O binário original em espanhol continua sendo bom ter e continua **não sendo
bloqueante**; deixou de ser a única rota. Registrado em §1.5.

### 8.9 `TStaticText` no GTK2

37 instâncias. `TStaticText` é o par LCL de `TStaticText`, mas transparência e
cor de fundo se comportam diferente no GTK2 do que no Win32. Conferir na Fase 2,
não na Fase 6 — corrigir 37 controles no fim é retrabalho.

### 8.10 Não alimentar o transpilador com decompilado

O `port_database_pas.py` da Fase 3 funciona porque a entrada é **código deste
repositório**: subconjunto estreito de C++, estável, testado, e com o
`FORBIDDEN` cobrindo o que ele não reconhece.

A tentação, quando a Fase 4 estiver cara, é apontar o mesmo transpilador para a
saída do Ghidra. **Não fazer.** Decompilado é entrada arbitrária: o `FORBIDDEN`
deixa de segurar porque não há vocabulário fechado a proibir, e o resultado é
Pascal sintaticamente válido, que compila, que passa em teste unitário — e que
grava bytes errados. Foi assim que o `SeekCurrent` trocado passou por tudo no
`newWe2002` menos pelo confronto com o `ed.exe`.

Os corpos dos 96 handlers vêm de `re/spec/*.md`, escritos à mão. Esse limite é
de projeto, não de esforço.

### 8.11 Bitfield em FPC não tem ordem garantida

`SquadNumbers` é bitfield, e o `newWe2002` já levou uma mordida ali quando
`DWORD` virou 64-bit no Linux LP64 e embaralhou todo número de camisa. Em FPC o
risco é outro e igualmente silencioso: `bitpacked record` tem ordem de bit
definida pelo compilador e pelo endianness, e não é obrigada a casar com o que o
MSVC fez com `struct NUMERI` em 2002.

**Gerar acessor explícito** — máscara e deslocamento escritos à mão — em vez de
confiar no layout do `bitpacked record`. E testar contra a imagem real na Fase 3,
não na Fase 6.

---

## 9. Riscos ao "100%"

Honestidade sobre o que pode não fechar.

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Fórmula de preço não sai do disassembly | baixa | é aritmética simples; e dá para recuperar por tabela de verdade exaustiva, sem decompilar |
| Render 2D não bate pixel a pixel | **média** | arredondamento de gradiente é onde some. Aceitar tolerância documentada em vez de exigir igualdade exata |
| Formato `.mcr` mais complexo que o esperado | média | gerar fixture com o `grabar_memoryClick` do próprio original |
| `Registry`/`Printers` serem uso real | baixa | quase certo que é dependência transitiva; verificado na Fase 1 |
| Wine 32-bit quebrar e matar o oráculo A | baixa | o oráculo B (`we2002_core`) cobre formato; só a verificação comportamental sofre |
| Handler depender de comportamento não documentado do Win32 | média | é o caso clássico de divergência deliberada — documentar e seguir |
| Transpilador da Fase 3 não cobrir todo o subconjunto | baixa–média | o `FORBIDDEN` **falha alto** em vez de emitir código quebrado; o trecho recusado vira porte manual daquele trecho, não do módulo |
| Layout de bitfield do FPC divergir do MSVC de 2002 | média | acessor explícito por máscara e deslocamento (§8.11), testado na Fase 3 |

**"100%" aqui significa: todo handler com veredito escrito e toda gravação
byte-idêntica.** Não significa que nenhuma divergência é aceita — significa que
nenhuma é *desconhecida*. É o mesmo critério que fechou o escopo Linux do
`newWe2002`, onde a única divergência aceita é uma faixa de 16 bytes,
documentada e explicada.

---

## 10. Ordem sugerida de ataque

Se o objetivo for ver resultado cedo em vez de seguir as fases em bloco:

1. **Fase 0** inteira. Sem ferramenta não há projeto.
2. **Fase 1, itens 1 e 2** — os DFM e os 96 métodos. Meio dia, e destrava a
   Fase 2 inteira.
3. **Fase 2 inteira.** O app abre e mostra os 18. Marco visível. (Navegar
   entre eles é da fase 4 — ver o critério de pronto da fase 2.)
4. **Fase 3** até o round-trip headless. Agora o app *lê* o jogo.
5. **§5.1** (preço, WTE-TASK-32) antecipada, porque é a feature mais desejada, é
   isolada e não depende de gravação.
6. **Fase 4** no ritmo, handler a handler — **incluindo §5.2 e §5.3**, que
   fecham as duas gravações que dependem de fórmula.
7. **§5.4**, **6**, **7**.

O passo 5 é antecipação deliberada: entrega valor antes de a Fase 4 terminar, e
valida o ferramental de decompilação num alvo pequeno e conferível. Até a
renumeração de 2026-08-19 ele era também *fora de ordem*, o que deixou de ser
verdade — preço virou a 32 e o fechamento da Fase 4 virou a 31.

---

## 11. Registro de execução

*(vazio — preencher ao concluir cada fase, no formato da seção 11 do
[PLAN-WINDOWS.md](/docs/PLAN-WINDOWS.md))*
