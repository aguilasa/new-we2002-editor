# A convenção Borland no Ghidra — o procedimento, para refazer

Produto da [WTE-TASK-24](../../../docs/tasks/24-ghidra-convencao-borland.md).

**Por que isto está escrito.** O projeto do Ghidra é um banco binário local, não
versionado (`work/ghidra/`, coberto pelo `.gitignore`). Ele **vai** se perder —
numa troca de máquina, num `make distclean`, num reimport. O que sobrevive é
este documento mais os três scripts ao lado, e juntos eles refazem tudo em um
comando.

---

## A armadilha, em uma frase

**O C++Builder passa `this`/1º argumento em `EAX`, 2º em `EDX`, 3º em `ECX`.** O
Ghidra, com qualquer compiler spec que não seja o de Borland, assume `__cdecl` e
reporta **função sem argumento** que misteriosamente lê lixo, com as três
primeiras variáveis fora da assinatura.

Sintoma no disassembly real de `colorearClick` (`0x00410ea8`):

```asm
00410ea8:  push  ebx
00410ea9:  push  esi
00410eaa:  mov   ebx,eax        ; <-- 'this' chegando em EAX
```

Sem a correção a saída do decompilador é **ruído convincente** — o pior tipo de
erro, porque parece certo.

---

## O achado desta task: não é preciso construir convenção nenhuma

A §8.1 do plano descreve criar uma convenção customizada (`EAX, EDX, ECX`,
retorno em `EAX`) e aplicá-la a todas as funções. **Isso não é necessário no
Ghidra 12.1.2.** Ele já traz o compiler spec de Borland:

```
Ghidra/Processors/x86/data/languages/x86.ldefs
  <compiler name="Borland C++" spec="x86borland.cspec" id="borlandcpp"/>
  <compiler name="Delphi"      spec="x86delphi.cspec"  id="borlanddelphi"/>
```

E dentro do `x86borland.cspec` o modelo é o **`<default_proto>`**:

```xml
<default_proto>
  <prototype name="__fastcall" extrapop="unknown" stackshift="4">
    <input>
      <pentry minsize="1" maxsize="4"><register name="EAX"/></pentry>
      <pentry minsize="1" maxsize="4"><register name="EDX"/></pentry>
      <pentry minsize="1" maxsize="4"><register name="ECX"/></pentry>
      ...
```

Ser `default_proto` é o ponto: a convenção vale para **todas** as funções, sem
aplicar nada função a função — que é literalmente o critério da task. Construir
uma convenção à mão daria o mesmo resultado com mais superfície para errar.

**`borlandcpp`, não `borlanddelphi`.** Os dois existem e o engano é fácil: os
dois produtos são de 2002, usam a mesma VCL, os mesmos `rtl60.bpl`/`vcl60.bpl` e
o mesmo `.dfm`. O binário é **C++Builder 6** — o mangling `$qqr`, os símbolos
`___CPPdebugHook`/`__GetExceptDLLinfo` e a string `c:\bcb\emuvcl\utilcls.h`
decidem. Ver a §1.1 do plano.

---

## O procedimento

### Headless — a rota normal

```sh
bash wte/tools/ghidra/run_headless.sh
```

Faz importação, análise e aplicação dos nomes num passo. O que ele fixa, e que
é a parte que não pode variar:

```
-processor x86:LE:32:default  -cspec borlandcpp
```

### GUI — quando for preciso olhar

1. `~/.local/opt/ghidra_12.1.2_PUBLIC/ghidraRun`
2. **File → Import File**, escolher `we-team-editor/we-team-editor.exe`
3. Na caixa de importação, clicar nos **três pontos** ao lado de *Language* e
   escolher **`x86:LE:32:default:borlandcpp`** — a coluna *Compiler* tem de
   dizer `borlandcpp`. **Este é o passo que não pode ser pulado.** O Ghidra
   detecta `windows` sozinho e ficaria em `__cdecl`.
4. Analisar com os padrões.
5. **Window → Script Manager**, adicionar `wte/tools/ghidra/` ao *Script
   Directories*, e rodar `apply_names.py` com a raiz do repositório como
   argumento.

### Se o projeto já existe com o cspec errado

Não há conserto barato: `Set Language` reanalisa tudo e deixa resíduo da
inferência antiga. **Reimporte.** É por isso que o banco não é versionado e o
`run_headless.sh` usa `-overwrite`.

---

## A guarda que impede o erro silencioso

O `apply_names.py` **aborta** se o cspec não for `borlandcpp`:

```
apply_names: ABORTADO: cspec e 'windows', nao 'borlandcpp'.
```

Isso não é zelo. Aplicar os 96 nomes sobre assinaturas inferidas como `__cdecl`
seria o pior resultado possível: nome bonito em cima de ruído, e quem ler
depois confia. Errar alto é melhor do que produzir um projeto que **parece**
anotado.

---

## Verificar que pegou

```sh
bash wte/tools/ghidra/run_headless.sh --decompile colorearClick
```

A convenção tem de sair `__fastcall`, e a função tem de ter parâmetro — não
zero. Zero parâmetro em `colorearClick` significa que o cspec não pegou.
