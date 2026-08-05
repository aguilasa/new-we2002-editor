---
id: CORR-WTE-003
title: "Correção: a seção `wte/` do `.gitignore` ignora `lib/` e `backup/` no repositório inteiro"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-003: dois padrões da seção do `wte/` vazam para o `newWe2002`

## Problema identificado

A WTE-TASK-02 acrescentou ao `.gitignore` uma seção rotulada
`# ---- Projeto Lazarus em wte/ (WTE-TASK-02) ----`. Cinco das suas regras são
**ancoradas ou específicas de Pascal** e ficam onde deviam:

```
wte/build/      <- ancorado
wte/assets      <- ancorado
*.lps *.ppu *.compiled   <- extensões que só o Lazarus/FPC produz
```

Duas não são nem uma coisa nem outra:

```
lib/
backup/
```

Nome de diretório genérico, **sem âncora**. Regra de `.gitignore` sem barra
inicial casa em qualquer profundidade, então essas duas passaram a valer para a
árvore inteira — inclusive a do `newWe2002`, que a task tinha o critério
explícito de não tocar ("Nada de `wte/` referenciado pelo build do
`newWe2002`").

Hoje nada é engolido: não existe `lib/` nem `backup/` rastreado no repositório.
O defeito é **latente**, e o modo de falha é o pior tipo — arquivo que não
aparece no `git status` e some sem aviso.

Some-se a isto que **este projeto nem usa esse layout**: o `wte.lpi` grava em
`build/units` (`<UnitOutputDirectory>`), não em `lib/`; `backup/` é da IDE
gráfica, e o faseamento inteiro assume `lazbuild` por linha de comando.

## Evidência

O que as duas regras alcançam hoje, fora do `wte/`:

```console
$ git check-ignore -v src/lib/x.cpp
.gitignore:69:lib/	src/lib/x.cpp

$ git check-ignore -v tools/lib/z.py
.gitignore:69:lib/	tools/lib/z.py

$ git check-ignore -v legacy/backup/y.txt
.gitignore:70:backup/	legacy/backup/y.txt
```

Contraste com as regras vizinhas da mesma seção, que se recusam a sair do
`wte/`:

```console
$ git check-ignore -v wte/build/wte wte/assets
.gitignore:59:wte/build/	wte/build/wte
.gitignore:63:wte/assets	wte/assets
```

E a saída de build que o projeto realmente produz — nenhum `lib/` à vista:

```console
$ grep UnitOutputDirectory wte/wte.lpi
        <UnitOutputDirectory Value="build/units"/>

$ find wte -type d -name lib -o -type d -name backup
(nada)
```

Impacto atual medido: **zero arquivo escondido**. O que existe é a armadilha.

## Causa raiz

As duas regras foram copiadas do `.gitignore` canônico de projeto Lazarus, que
assume o projeto na raiz do repositório; aqui o projeto está em `wte/` e o
prefixo não foi acrescentado.

## Correção

### Arquivo: `.gitignore`

Ancorar as duas no `wte/`, na seção onde já estão:

```diff
-lib/
-backup/
+wte/lib/
+wte/backup/
```

Manter `*.lps`, `*.ppu` e `*.compiled` como estão: são extensões que só o
toolchain Pascal emite, não colidem com nada do `newWe2002`, e ancorá-las
custaria alcance sem devolver segurança.

Vale acrescentar meia linha de comentário dizendo por que as duas estão
ancoradas e as três de extensão não — a seção já explica cada regra, e essa é a
única que ficaria sem razão escrita.

> Se quem executar preferir **remover** as duas em vez de ancorá-las, também
> resolve: o `wte.lpi` grava em `build/units` e o projeto não usa `lib/` nem
> `backup/`. Ancorar é a rota de menor surpresa para quem um dia abrir o
> projeto na IDE gráfica, que cria as duas pastas.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `.gitignore` | modificar |

## Verificação

- [x] As duas regras deixaram de alcançar o `newWe2002`:
      `git check-ignore -v src/lib/x.cpp tools/lib/z.py legacy/backup/y.txt`
      não devolve nada
- [x] Continuam alcançando o `wte/`:
      `git check-ignore -v wte/lib/x.o wte/backup/y.pas` devolve as duas linhas
- [x] Nada saiu do índice por engano: `git status --short` limpo e
      `git ls-files | wc -l` inalterado antes e depois
- [x] `wte/re/` segue **não** ignorado:
      `git check-ignore wte/re/ambiente.md` não devolve nada
- [x] `lazbuild wte/wte.lpi` continua compilando
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-05

**Resumo do que foi feito:**

Ancoradas as duas regras: `lib/` → `wte/lib/`, `backup/` → `wte/backup/`, na
mesma seção onde já estavam. As três de extensão (`*.lps`, `*.ppu`,
`*.compiled`) ficaram sem âncora, como a Correção manda. Escolhida a rota de
ancorar, não a de remover, pela razão registrada na CORR: a IDE gráfica cria as
duas pastas, e o `lazbuild` por linha de comando não.

Números medidos: `git ls-files` = **211 antes e depois**; `lazbuild` sai **0**,
com 0 linhas de `warning`/`error` e 2 hints (os mesmos de antes — expansão do
`{$R *.lfm}` e o `SetOutputDirectoryOverride`).

**Problemas encontrados:**

Nenhum. A varredura de discrepância (`grep -rn` em `docs`, `wte/re`, `.claude`,
`CLAUDE.md`) não achou doc que descrevesse as duas regras no estado antigo — só
esta CORR e o bloco de detalhe do `correcoes-progresso.md`, que narram o sintoma
e continuam corretos como registro histórico. O critério da WTE-TASK-02
(".gitignore cobrindo saída de build, e **não** cobrindo `wte/re/`") segue
verdadeiro: `git check-ignore wte/re/ambiente.md` não devolve nada.

Acrescentado o comentário que a Correção pedia, dizendo **por que** estas duas
são ancoradas e as três de extensão não — era a única regra da seção sem razão
escrita ao lado.

**Arquivos criados/modificados:**

- `.gitignore` (modificado)
- `docs/tasks/correcoes-progresso.md` (modificado)
- `docs/tasks/CORR-WTE-003.md` (modificado)
