---
id: CORR-KRP-009
---

# CORR-KRP-009 — kits_selftest leva 260-275 s contra TIMEOUT 300 e estoura sob carga

Origin: [KRP-TASK-07](/docs/tasks/kits-replay/07-replay-py-capture-com-as-guardas-medidas-e-o.md)

## Problem

O `kits_selftest` leva 259,5 s rodando sozinho, e 274,65 s no Log da KRP-TASK-07, contra
`TIMEOUT 300`: de 86% a 92% do orçamento.

Os tempos registrados ao longo do ciclo foram 221,9, 222,8, 227,6, 235,1, 248,8 e 274,65 s. Rodando o
gate com o `controls.py` em paralelo, o teste estourou o tempo. O gate fica sensível à carga da
máquina e pode ficar vermelho sem defeito nenhum no código.

## Evidência

```text
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits   # com tools/kits/controls.py rodando em paralelo
18 - kits_selftest (Timeout)
$ # o mesmo comando, com -R kits_selftest, sozinho
1/1 Test #18: kits_selftest ....................   Passed  259.51 sec
$ grep -n "kits_selftest PROPERTIES TIMEOUT" tests/CMakeLists.txt
303:    set_tests_properties(kits_selftest PROPERTIES TIMEOUT 300)
$ grep -rhn "kits_selftest .*Passed" docs/tasks/kits-replay/
(222.75, 227.58, 235.06, 248.77, 221.92, 274.65 sec)
```

## Root cause

(Hipótese.) Cada task do ciclo acrescenta casos ao selftest que rodam os leitores de replay inteiros,
e o timeout nunca acompanhou. Os casos novos desta task são pequenos (sem emulador): o crescimento é
cumulativo, não específico da KRP-TASK-07.

## Fix

Em `tests/CMakeLists.txt:303`, subir o timeout com uma margem declarada, ou separar as asserções
lentas de replay num teste à parte.

## Arquivos a criar ou modificar

- `tests/CMakeLists.txt`
- `tools/kits/selftest.py` (se as asserções forem separadas)

## Verificação

Rodar o gate `ctest -R kits` com `python3 tools/kits/controls.py` em paralelo: o `kits_selftest` não
pode estourar o tempo.

## Log de Execução
