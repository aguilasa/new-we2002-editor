---
id: WTE-TASK-02
title: "Esqueleto de wte/ e build por linha de comando"
type: infra
category: infra
phase: 0
depends_on: ["WTE-TASK-01"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md Fase 0"
status: concluído
---

# WTE-TASK-02: Esqueleto do projeto

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 0.
- É **projeto separado** do `newWe2002`: não entra no `CMakeLists.txt`, não
  compartilha alvo de build, não é adicionado por `add_subdirectory`. O que
  compartilha é conhecimento de formato.

---

## Objetivo

Criar a árvore e o build, vazios mas funcionando.

```
wte/
  src/            unidades Pascal
  forms/          os .lfm
  assets/         aponta para we-team-editor/ (gitignored)
  re/             produto da engenharia reversa -- versionado
    dfm/
    spec/
  tools/          geradores e scripts de golden test
  tests/
```

### Decisões a tomar e escrever

1. **Como `assets/` aponta para `we-team-editor/`.** Symlink versionado, ou
   resolução em runtime por variável de ambiente? O `newWe2002` resolve dados
   relativo ao executável (`DataFiles.cpp`); vale herdar a ideia em vez de
   caminho absoluto compilado.
2. **Onde entra o `--check` dos geradores.** O `newWe2002` registra no `ctest`.
   Aqui não há CMake — decidir entre um `Makefile` próprio em `wte/`, um alvo
   novo no `Makefile` da raiz, ou script em `wte/tools/`.
3. **Nome do binário.** Provisório é aceitável; o nome definitivo é decisão da
   WTE-TASK-38, por causa da §2 do plano.

### O que tem de funcionar no fim

- `lazbuild wte/wte.lpi` produz binário
- o binário abre janela vazia no `:99`
- `wte/assets/` alcança os 197 `.bmp` e o `data/dat.bin`
- `.gitignore` cobrindo saída de build, e **não** cobrindo `wte/re/`

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/wte.lpi`, `wte/wte.lpr` | criar |
| `wte/` (árvore acima) | criar |
| `wte/README.md` | criar — como compilar e rodar, e o aviso de projeto separado |
| `.gitignore` | modificar |
| `docs/PLAN-WTE-LAZARUS.md` | modificar, se alguma decisão acima mudar a Fase 0 |

---

## Critério de conclusão

- [x] `lazbuild` compila e o binário abre no `:99`
- [x] As três decisões acima escritas, com razão
- [x] `wte/re/` versionado; saída de build ignorada
- [x] Nada de `wte/` referenciado pelo build do `newWe2002`
- [x] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-05

- **Resumo do que foi feito:**

  Árvore `wte/` criada com projeto Lazarus compilando por linha de comando
  (`lazbuild wte/wte.lpi` → `wte/build/wte`, 27 MB, GTK2 confirmado por `ldd`) e
  um formulário vazio que abre no `:99`. As três decisões estão escritas com a
  razão em `wte/README.md`, que é onde quem chegar depois vai procurar.

  As decisões: **(1)** `wte/assets` é symlink **não versionado** criado por
  `make -C wte assets` — versioná-lo daria link quebrado em todo clone, já que
  `we-team-editor/` é gitignored; o que vale para o binário instalado é a ordem
  de resolução em runtime herdada do `DataFiles.cpp` do `newWe2002`
  (`$WTE_ASSETS_DIR` → ao lado do executável → prefixo instalado → árvore de
  fonte), implementada só na WTE-TASK-39. **(2)** O `--check` mora num
  `wte/Makefile` autônomo, não num alvo da raiz — o critério desta task pede
  separação, e um alvo na raiz a desfaria. **(3)** O binário se chama `wte`,
  provisório até a WTE-TASK-38.

  O que se aprendeu e muda trabalho futuro: **`{$R *.lfm}` não respeita o
  include path**. Com `src/` e `forms/` separados — que é o layout que o plano
  pede — a compilação falha, e a saída é caminho relativo explícito. Isso vira
  requisito do `dfm2lfm.py` da WTE-TASK-10, que precisa emitir essa linha nos 18
  esqueletos.

- **Arquivos criados/modificados:**
  - `wte/wte.lpi`, `wte/wte.lpr` — projeto e programa
  - `wte/src/WteMain.pas`, `wte/forms/WteMain.lfm` — formulário provisório
  - `wte/Makefile` — `build`, `run`, `run-98`, `assets`, `check`, `clean`,
    `distclean`
  - `wte/README.md` — as três decisões, a armadilha do `.lfm`, o aviso de
    projeto separado
  - `wte/re/dfm/README.md`, `wte/re/spec/README.md`, `wte/tools/README.md`,
    `wte/tests/README.md` — dizem o que chega em cada pasta e em que task
  - `.gitignore` — seção do `wte/`
  - `docs/tasks/concluidos/progresso.md`, este arquivo

- **Problemas encontrados:**

  1. **`{$R *.lfm}` não acha o `.lfm` em `forms/`.** O FPC expande o curinga
     para o nome da unidade e procura **só** no diretório do `.pas`;
     `IncludeFiles` não é consultado. Erro:
     `(9031) Can't open resource file .../wte/src/WteMain.lfm`. Resolvido com
     `{$R ../forms/WteMain.lfm}`, mantendo o layout do plano. Registrado no
     `README.md` como requisito da WTE-TASK-10.
  2. **Comentário Pascal não aninha.** A primeira versão do comentário que
     explica o item 1 continha uma chave de abertura no meio do texto e saiu
     `Warning: (2005) Comment level 2 found`. Reescrito com `//`.
  3. **São 198 bitmaps, não 197.** `find -iname '*.bmp'` acha 198 onde a §1 do
     plano registra 197 — provavelmente o `image/careto_base.bmp`, que está
     solto na raiz de `image/` em vez de num dos quatro subdiretórios. **Não
     investigado**: a convenção dos assets é da WTE-TASK-08 e a reconciliação
     dos números é da WTE-TASK-09. Registrado no `README.md` para não se perder.
  4. **Dois `wte` com nomes colidindo.** `make wte` na raiz abre o **original**
     sob Wine (oráculo A); `make -C wte` é este projeto. Nada quebrou, mas o
     risco de confusão é real e ficou avisado no `README.md`.
