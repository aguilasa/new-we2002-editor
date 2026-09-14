---
id: CORR-LOOKS-016
title: "Correção: os dois alvos de `looks` são registrados fora do `if(Python3_FOUND)` que guarda os outros oito"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-LOOKS-016: os alvos de `looks` estão fora da guarda de Python

## Problema identificado

O `tests/CMakeLists.txt` procura o interpretador uma vez e põe **todos** os
testes Python atrás do resultado:

```cmake
62: find_package(Python3 COMPONENTS Interpreter)
63: if(Python3_FOUND)
64:     add_test(NAME ui_forms      ... ${Python3_EXECUTABLE} ...)
...
144:    add_test(NAME mcr_container ... ${Python3_EXECUTABLE} ...)
150: endif()
158: if(UNIX AND Python3_FOUND)
159:     add_test(NAME mcr_ui ...)
165: endif()
```

Os dois alvos deste ciclo, acrescentados pela
[`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md) e por esta task, ficaram
**no nível de cima**:

```
205: add_test(NAME looks_selftest   <<< depth=0
210: add_test(NAME looks_image      <<< depth=0
```

Oito irmãos dentro da guarda, dois fora. Numa máquina onde o CMake não acha um
Python 3, `${Python3_EXECUTABLE}` expande para **nada** e o comando do teste
vira o caminho do `.py` sozinho — que não é executável. O `ctest` então
reporta o `looks_selftest` como **Failed**, com uma mensagem sobre executável
não encontrado.

E é o pior alvo para isso acontecer. O `looks_selftest` é o gate que o perfil
descreve como *"nada — **nunca pula**"*: quem o vir vermelho vai procurar o
defeito em `tools/looks/`, e o defeito é que a máquina não tem Python. Os
outros oito simplesmente não aparecem, que é o comportamento certo — o
`ui_forms`, o `glossary` e o `tasks` não existem sem Python, e ninguém os
procura.

Vale notar o que **não** é o conserto: pôr os dois dentro da guarda não os faz
rodar nesta máquina, onde o problema é outro e está na
[`CORR-LOOKS-015`](/docs/tasks/looks/CORR-LOOKS-015.md). São duas coisas
diferentes — aqui, o alvo mente sobre a causa quando falta Python; lá, o alvo
não existe porque o build não configura.

## Evidência

O mapa de `if`/`endif` do arquivo, com a profundidade de cada `add_test`:

```
63: if(Python3_FOUND)                    (depth 1)
64:     add_test(NAME ui_forms           <<< depth=1
71:     add_test(NAME glossary           <<< depth=1
79:     add_test(NAME tasks              <<< depth=1
90:     add_test(NAME pes2_selftest      <<< depth=1
101:    add_test(NAME pes2_image         <<< depth=1
119:    add_test(NAME mcr_selftest       <<< depth=1
130:    add_test(NAME mcr_card           <<< depth=1
144:    add_test(NAME mcr_container      <<< depth=1
150: endif()
158: if(UNIX AND Python3_FOUND)          (depth 1)
159:    add_test(NAME mcr_ui             <<< depth=1
165: endif()
172: if(UNIX)                            (depth 1)
173:    add_test(NAME pes2_boot          <<< depth=1
178: endif()
205: add_test(NAME looks_selftest        <<< depth=0
210: add_test(NAME looks_image           <<< depth=0
```

Dez testes Python no arquivo; **oito** dentro de `if(Python3_FOUND)`, um dentro
de `if(UNIX AND Python3_FOUND)`, e os dois de `looks` fora de qualquer guarda.

*(O `pes2_boot` está sob `if(UNIX)` sem `Python3_FOUND` e tem a mesma fresta —
é anterior a este ciclo e não é desta correção.)*

## Causa raiz

Os dois alvos foram acrescentados no fim do arquivo, depois do `endif()` que
fecha a guarda dos demais.

## Correção

### Arquivo: `tests/CMakeLists.txt`

Envolver os dois `add_test` em `if(Python3_FOUND)` … `endif()`, como os oito
irmãos, mantendo os comentários onde estão.

Enquanto o bloco é mexido, vale endireitar a ordem dos comentários: hoje o
parágrafo que explica o **gate de imagem** ("It re-derives, against the real
disc…") vem antes do parágrafo do **gate obrigatório**, e os `add_test` vêm na
ordem inversa — quem lê o `add_test(looks_image)` tem de subir por cima do
`looks_selftest` para achar a explicação dele.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tests/CMakeLists.txt` | modificar |

## Verificação

- [ ] os dois `add_test` de `looks` estão dentro de `if(Python3_FOUND)`
- [ ] o mapa de profundidade não mostra mais nenhum teste Python em `depth=0`
      (o `pes2_boot` fica como está, é de outro ciclo)
- [ ] cada `add_test` tem o comentário que o explica imediatamente acima
- [ ] onde o build configurar, `ctest -R looks` continua listando os dois
- [ ] `python tools/looks/selftest.py` continua saindo 0

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
