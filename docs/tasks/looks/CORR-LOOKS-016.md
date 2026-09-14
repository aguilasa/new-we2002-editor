---
id: CORR-LOOKS-016
title: "Correção: os dois alvos de `looks` são registrados fora do `if(Python3_FOUND)` que guarda os outros oito"
type: correção
category: verificação
status: concluído
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

- [x] os dois `add_test` de `looks` estão dentro de `if(Python3_FOUND)`
- [x] o mapa de profundidade não mostra mais nenhum teste Python em `depth=0`
      (o `pes2_boot` fica como está, é de outro ciclo)
- [x] cada `add_test` tem o comentário que o explica imediatamente acima
- [x] onde o build configurar, `ctest -R looks` continua listando os dois
- [x] `python tools/looks/selftest.py` continua saindo 0

## Log de Execução

**Executado em:** 2026-09-14

**Resumo do que foi feito:**

Os dois `add_test` entraram no `if(Python3_FOUND)`, como os oito irmãos, e os
comentários foram endireitados: o parágrafo de cada alvo agora fica
**imediatamente acima dele**. Antes a explicação do gate de imagem vinha antes
do `add_test` do gate obrigatório, e quem lesse o `looks_image` tinha de subir
por cima do `looks_selftest` para achar a dele.

O parágrafo de abertura do bloco passou a dizer **por que** a guarda importa
justamente aqui: sem Python, `${Python3_EXECUTABLE}` expande para nada, o
comando vira o caminho do `.py` sozinho, e o `looks_selftest` — o gate que o
perfil descreve como *"nunca pula"* — sai **Failed**, mandando quem o ler
procurar defeito em `tools/looks/` quando o que falta é o interpretador.

Mapa de profundidade depois, com os 15 `add_test` do arquivo:

```
  5: add_test(NAME core                 depth=0     <- teste C++, nao Python
 34: add_test(NAME golden               depth=1
 46: add_test(NAME golden_gui           depth=2
 64: add_test(NAME ui_forms             depth=1
 ...
173: add_test(NAME pes2_boot            depth=1
200: add_test(NAME looks_selftest       depth=1     <- era 0
221: add_test(NAME looks_image          depth=1     <- era 0
```

Nenhum teste Python em `depth=0`. O `pes2_boot` continua sob `if(UNIX)` sem
`Python3_FOUND`, como a CORR determina — é de outro ciclo.

Verificado num build fora da árvore, com a receita que a
[`CORR-LOOKS-015`](/docs/tasks/looks/CORR-LOOKS-015.md) acabou de registrar no
perfil:

```
$ ctest --test-dir <build> -R looks
1/2 Test #10: looks_selftest ...................   Passed    1.15 sec
2/2 Test #11: looks_image ......................***Skipped   0.06 sec
100% tests passed out of 2
```

Com `WE2002_LOOKS_IMAGE` apontada, os dois passam. Os onze alvos do projeto
continuam registrados, e os outros projetos sem regressão:

```
$ ctest --test-dir <build> -R "mcr|tasks|glossary"
glossary Passed | tasks Passed | mcr_selftest Passed | mcr_card Skipped |
mcr_container Passed                              100% tests passed out of 5
```

E o **controle**, que é o que prova a guarda: configurando com
`-DCMAKE_DISABLE_FIND_PACKAGE_Python3=TRUE`, os dois alvos **desaparecem** em
vez de aparecer vermelhos — `No tests were found!!!`, que é o mesmo
comportamento dos oito irmãos.

**Problemas encontrados:** nenhum.

`python tools/looks/selftest.py --quiet` continua saindo 0.

**Arquivos criados/modificados:**

- `tests/CMakeLists.txt` — o bloco de `looks` dentro de `if(Python3_FOUND)`,
  com os comentários na ordem dos alvos
- `docs/tasks/looks/CORR-LOOKS-016.md` — este Log
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
