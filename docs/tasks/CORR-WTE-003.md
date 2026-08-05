---
id: CORR-WTE-003
title: "Correção: a seção `wte/` do `.gitignore` ignora `lib/` e `backup/` no repositório inteiro"
type: correção
category: processo
status: pendente
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

- [ ] As duas regras deixaram de alcançar o `newWe2002`:
      `git check-ignore -v src/lib/x.cpp tools/lib/z.py legacy/backup/y.txt`
      não devolve nada
- [ ] Continuam alcançando o `wte/`:
      `git check-ignore -v wte/lib/x.o wte/backup/y.pas` devolve as duas linhas
- [ ] Nada saiu do índice por engano: `git status --short` limpo e
      `git ls-files | wc -l` inalterado antes e depois
- [ ] `wte/re/` segue **não** ignorado:
      `git check-ignore wte/re/ambiente.md` não devolve nada
- [ ] `lazbuild wte/wte.lpi` continua compilando
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
