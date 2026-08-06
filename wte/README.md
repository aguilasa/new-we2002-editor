# `wte/` — o WE2002 Team Editor em Lazarus

Reimplementação do **WE2002 Team Editor v0.99** do Obocaman (C++Builder 6,
Win32) como aplicação **Lazarus/LCL nativa no Linux**, com paridade verificada
byte a byte contra o binário original.

- **Plano:** [`../docs/PLAN-WTE-LAZARUS.md`](../docs/PLAN-WTE-LAZARUS.md) — a
  fonte de verdade
- **Andamento:** [`../docs/tasks/progresso.md`](../docs/tasks/progresso.md)
- **Achados da engenharia reversa:** [`re/`](re/)
- **Ambiente medido:** [`re/ambiente.md`](re/ambiente.md)

> ## Projeto **separado** do `newWe2002`
>
> Apesar de morar no mesmo repositório, este diretório **não faz parte do build
> do `newWe2002`**: não é `add_subdirectory`, não aparece no `CMakeLists.txt` da
> raiz, não tem alvo no `Makefile` da raiz. São dois produtos, com dois ciclos
> de verificação.
>
> O que os dois compartilham é **conhecimento de formato**: `Offsets.hpp`,
> `Tables.cpp` e o `we2002_core` inteiro, que é a *entrada* do transpilador da
> fase 3 — nunca o alvo dele.

## Compilar e rodar

```sh
make -C wte build     # lazbuild wte.lpi -> wte/build/wte
make -C wte assets    # symlink para a pasta do Obocaman (uma vez)
make -C wte run-99    # roda no Xvfb :99
make -C wte check     # --check de todos os geradores de tools/
make -C wte           # lista os alvos
```

Sem `make`, direto:

```sh
lazbuild wte/wte.lpi
./wte/build/wte
```

> **Cuidado com os dois `wte`.** `make wte` **na raiz** abre o binário do
> Obocaman sob Wine — o oráculo A, que continua existindo e não mudou. Este
> projeto é `make -C wte <alvo>`. Nomes parecidos, coisas opostas: um é o
> original que estamos medindo, o outro é o que estamos escrevendo.

**Toda execução com GUI acontece no `DISPLAY=:99`** — o `:1` é a sessão real do
usuário. O `run-99` resolve o `XAUTHORITY` do Xvfb sozinho; à mão é preciso
fazer o que o [`../CLAUDE.md`](../CLAUDE.md) descreve, ou o GTK morre com
`Invalid MIT-MAGIC-COOKIE-1 key`.

## Layout

```text
wte/
  wte.lpi, wte.lpr    projeto e programa
  src/                unidades Pascal (.pas)
  forms/              os formulários (.lfm)
  assets/             symlink para ../we-team-editor/ -- NAO versionado
  re/                 produto da engenharia reversa -- VERSIONADO
    dfm/  spec/  ambiente.md
  tools/              geradores e scripts de golden test
  tests/              testes do lado Pascal
  build/              saída do lazbuild -- ignorada
```

---

## As três decisões da WTE-TASK-02

### 1. `assets/` é symlink de conveniência; quem manda é a resolução em runtime

A pasta `we-team-editor/` **é gitignored** — binário sem fonte e sem licença,
198 bitmaps, `dat.bin`. Um symlink versionado apontando para ela daria um link
quebrado em qualquer clone, então `wte/assets` também é ignorado e nasce de
`make -C wte assets`.

Isso resolve o **desenvolvimento**. Para o binário instalado a decisão é herdar
a ideia do `newWe2002` ([`../src/app/DataFiles.cpp`](../src/app/DataFiles.cpp)):
**resolver em runtime, relativo ao executável**, nunca por caminho absoluto
compilado. Ordem de busca acordada, na mesma forma do irmão:

1. `$WTE_ASSETS_DIR`
2. ao lado do executável
3. o prefixo instalado (`../share/<nome>/`)
4. a árvore de fonte (este `wte/assets`)

A implementação Pascal disso é da **WTE-TASK-39** (`datafiles.pas`), junto com o
empacotamento — antes disso não há prefixo instalado para procurar. O que a
fase 0 fixa é a **ordem**, para que nenhuma fase intermediária compile um
caminho absoluto e crie trabalho de desfazer.

O alvo `assets` **conta o que alcançou** em vez de dizer "ok": 198 bitmaps e o
`data/dat.bin`. Se a pasta faltar, ele falha dizendo o que colocar onde.

> **198, não 197.** A §1 do plano registra 197 `.bmp`; `find -iname '*.bmp'`
> acha **198**. A diferença provável é o `image/careto_base.bmp`, que está solto
> na raiz de `image/` em vez de num dos quatro subdiretórios
> (`banderas`, `barba`, `pelo`, `uniformes2d`). Não foi investigado aqui —
> a convenção dos assets é da **WTE-TASK-08** e a reconciliação dos números da
> §1 é da **WTE-TASK-09**. Registrado para que a divergência não se perca.

### 2. O `--check` mora num `Makefile` próprio, em `wte/`

Três rotas estavam abertas: `ctest` (não existe aqui — não há CMake), um alvo
novo no `Makefile` da raiz, ou coisa própria em `wte/`.

**Escolhido: `wte/Makefile` autônomo.** A razão é a mesma que separa os dois
projetos: um alvo na raiz faria o ciclo de verificação do `newWe2002` e o deste
compartilharem entrada, e o critério da WTE-TASK-02 é explícito em que nada de
`wte/` seja referenciado pelo build do `newWe2002`. O `Makefile` da raiz não foi
tocado.

`make -C wte check` roda `--check` em cada `tools/*.py`, enumerado por
`wildcard` — gerador novo entra na bateria sem editar o Makefile. Enquanto não
houver gerador nenhum, o alvo **diz que nada foi medido** em vez de sair verde:
alvo verde sem medição é pior do que alvo ausente.

A exceção é `tools/test_*.py`: teste de ferramenta não é gerador e não aceita
`--check`, então o `wildcard` o filtra. Esses rodam pelo alvo `test`, do qual
`check` depende — o comando a decorar continua sendo um só.

### 3. O binário se chama `wte` — provisoriamente

Nome definitivo é decisão da **WTE-TASK-38**, por causa da §2 do plano (o
produto tem de ser distinguível do original, que é software de terceiro sem
licença). Até lá, `wte` em toda parte: `wte.lpi`, `wte.lpr`, `build/wte`.

Trocar depois é barato — são três nomes de arquivo e o `Application.Title`.

---

## Armadilha já paga: o `.lfm` em `forms/`

`{$R *.lfm}` **não respeita o include path.** O FPC expande o curinga para o
nome da unidade e procura o arquivo **no diretório do `.pas`**, e só ali. Com
`src/` para código e `forms/` para formulário — que é o layout que o plano pede
— isso falha com:

```
WteMain.pas(33) Error: (9031) Can't open resource file ".../wte/src/WteMain.lfm"
```

mesmo com `forms/` em `IncludeFiles`. A saída é o caminho explícito:

```pascal
{$R ../forms/WteMain.lfm}
```

**O `dfm2lfm.py` da WTE-TASK-10 tem de emitir essa linha nos 18 esqueletos.**

## Estado

Fase 0. O que existe é esqueleto: um formulário vazio que prova que o build
fecha e que a janela abre no `:99`. Os 18 formulários do original chegam na
fase 2, gerados — [`src/WteMain.pas`](src/WteMain.pas) sai ou vira a casca do
`Tep2002_princ`. Não invista nele.
