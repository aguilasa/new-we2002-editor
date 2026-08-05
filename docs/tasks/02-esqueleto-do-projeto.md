---
id: WTE-TASK-02
title: "Esqueleto de wte/ e build por linha de comando"
type: infra
category: infra
phase: 0
depends_on: ["WTE-TASK-01"]
status: pendente
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

- [ ] `lazbuild` compila e o binário abre no `:99`
- [ ] As três decisões acima escritas, com razão
- [ ] `wte/re/` versionado; saída de build ignorada
- [ ] Nada de `wte/` referenciado pelo build do `newWe2002`
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
