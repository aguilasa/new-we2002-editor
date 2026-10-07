---
id: CORR-KITS-026
---

# CORR-KITS-026 — Correct why golden_tool exits 127 under Git Bash

Origin: [KITS-TASK-13](/docs/tasks/concluidos/kits/13-nomes-dos-times.md)

## Problem

As Notas da KITS-TASK-13 dizem que "pelo Git Bash o mesmo `.exe` sai 127 sem imprimir nada". O 127 só acontece quando o diretório do runtime MinGW não está no `PATH`. Com o `bin` do compilador no `PATH`, o mesmo `.exe` roda pelo Git Bash e imprime as 95 linhas (saída 0). A causa é a busca de DLL, não o shell, e quem for reproduzir o Log é mandado ao PowerShell sem necessidade.

## Evidência

```text
$ grep -n "sai 127 sem imprimir nada" docs/tasks/kits/13-nomes-dos-times.md
37:- O `golden_tool` roda pelo PowerShell; pelo Git Bash o mesmo `.exe` sai 127 sem imprimir nada.
$ cd $TEMP && ./build-kits08/tests/we2002_golden_tool.exe names /c/github/new-we2002-editor/roms/golden-european-deluxe.bin; echo exit $?
exit 127
$ PATH="/c/Users/ingcvs/AppData/Local/Microsoft/WinGet/Packages/BrechtSanders.WinLibs.POSIX.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe/mingw64/bin:$PATH" $TEMP/build-kits08/tests/we2002_golden_tool.exe names roms/golden-european-deluxe.bin | wc -l; echo exit ${PIPESTATUS[0]}
95
exit 0
```

## Root cause

O `.exe` compilado pelo MinGW precisa das DLLs `libstdc++`/`libgcc` do `bin` do compilador. A sessão de PowerShell tinha esse diretório no `PATH` e a de Git Bash não — hipótese sobre o `PATH` do PowerShell do usuário.

## Fix

Nas Notas de `docs/tasks/kits/13-nomes-dos-times.md`, dizer que saída 127 significa que as DLLs do runtime MinGW não estão no `PATH`, e dar o prefixo de `PATH` que faz o Git Bash funcionar.

## Arquivos a criar ou modificar

- `docs/tasks/kits/13-nomes-dos-times.md`

## Verificação

```text
$ grep -n "sai 127 sem imprimir nada" docs/tasks/kits/13-nomes-dos-times.md
```

Hoje imprime a linha 37; depois tem de dar lugar à explicação de DLL/`PATH`.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `eee0e6fd`)

```text
$ $TEMP/build-kits08/tests/we2002_golden_tool.exe names roms/golden-european-deluxe.bin | wc -l; echo exit ${PIPESTATUS[0]}
0
exit 127
$ PATH="$M:$PATH" $TEMP/build-kits08/tests/we2002_golden_tool.exe names roms/golden-european-deluxe.bin | wc -l; echo exit ${PIPESTATUS[0]}
95
exit 0
$ ls "$M" | grep -iE "libstdc|libgcc|winpthread"
libgcc_s_seh-1.dll
libstdc++-6.dll
libwinpthread-1.dll
```

(`$M` = `.../WinGet/Packages/BrechtSanders.WinLibs.POSIX.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe/mingw64/bin`.) REPRODUCED: o mesmo Git Bash roda o `.exe` com o `bin` do MinGW no `PATH`.

### O que foi feito

Notas da KITS-TASK-13: a linha do "pelo Git Bash sai 127" virou a explicação — o 127 é a busca das três DLLs do runtime MinGW, não o shell —, com o prefixo de `PATH` que faz o Git Bash funcionar.

### Verificação

```text
$ grep -n "sai 127 sem imprimir nada" docs/tasks/kits/13-nomes-dos-times.md
(sem saída, exit 1)
$ grep -c "libstdc++-6.dll" docs/tasks/kits/13-nomes-dos-times.md
1
```
- **Closed** — commit `025e1073` (2026-10-01): docs(kits): say the golden_tool's 127 is the MinGW runtime DLLs, not the shell
  - Files (`git show --name-status 025e1073`):
    - `M docs/tasks/kits/13-nomes-dos-times.md`
    - `M docs/tasks/kits/CORR-KITS-026.md`
