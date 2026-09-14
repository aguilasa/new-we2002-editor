---
id: CORR-LOOKS-012
title: "Correção: o perfil promete o `looks_image` a partir desta task, e `ctest -R looks` sai 0 dizendo que não achou teste"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-LOOKS-012: o `looks_image` não existe, e pedir por ele sai verde

## Problema identificado

A tabela de gates do perfil do ciclo diz:

| alvo | precisa | a partir de |
| --- | --- | --- |
| `looks_image` | `WE2002_LOOKS_IMAGE` (77 sem ela) | **LOOKS-TASK-05** |

A LOOKS-TASK-05 fechou, e o alvo **não existe**. Não há uma linha sequer sobre
`looks` no `tests/CMakeLists.txt`, e o efeito é o pior possível:

```
$ ctest --test-dir build -R looks
Test project C:/github/new-we2002-editor/build
No tests were found!!!
$ echo $?
0
```

**Sai zero.** Quem rodar `ctest -R looks` numa corrida de conferência recebe
silêncio e código de sucesso — a definição exata do que o próprio perfil proíbe
duas linhas abaixo daquela tabela: *"nenhum alvo pode passar sem ter medido …
o contrato é: mediu e passou, ou pulou com 77."* Um alvo que não existe não
pula com 77; ele não aparece, e a ausência é indistinguível de verde.

A verificação **existe** — o `modelfile.py --check-image` afirma as contagens
dos dois arquivos contra o disco real, e esta revisão o rodou verde. O que
falta é o fio que faz alguém rodá-lo sem se lembrar dele. Enquanto isso, as
contagens da Fase 1 só são conferidas quando uma pessoa digita o comando, que
é o estado em que a
[`CORR-LOOKS-008`](/docs/tasks/looks/CORR-LOOKS-008.md) já pegou o `BASE`.

**Há uma divergência de dono por trás disso**, e ela precisa ser resolvida e
não contornada: o perfil diz que o `looks_image` nasce na 05, e a
[`LOOKS-TASK-19`](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md) se chama
*"`cli.py` e os três alvos de `ctest`"*. Os dois não podem estar certos. Se a
19 é quem cria os alvos, o perfil está prometendo por catorze tasks um gate que
não existe — e a Fase 1 inteira fecha sem nenhum gate automático, o que
contradiz o próprio perfil (*"depois dela, toda task fecha com o `selftest`
verde"*).

## Evidência

```
$ grep -rn "looks" tests/CMakeLists.txt
(vazio)

$ ctest --test-dir build -R looks
Test project C:/github/new-we2002-editor/build
No tests were found!!!
rc=0
```

E a verificação que deveria estar por trás do alvo, rodada à mão nesta revisão:

```
$ MSYS_NO_PATHCONV=1 python tools/looks/modelfile.py --check-image roms/japanese-shift-jis.bin
  /BIN/MODEL.BIN from 1816: 106 sections, 2461 vertices, 1767 primitives, end 64800 = EOF
  /BIN/EDT_MOD.BIN from 216: 20 sections, 1218 vertices, 1074 primitives, end 36072 = EOF
  ...
modelfile --check-image: ok
```

Verde, correto, e invisível para o `ctest`.

Para comparação, é assim que os outros quatro projetos deste repositório se
comportam: `ctest -R mcr` numa máquina sem fixture dá **2 passed, 2 skipped**,
e o skip é 77 — nunca "no tests were found".

## Causa raiz

O alvo de `ctest` não foi criado, e a tabela de gates do perfil o dá como
existente desde esta task.

## Correção

### Arquivo: `tests/CMakeLists.txt`

Registrar o `looks_image` agora, no molde dos alvos de `mcr` e `pes2` que já
moram ali:

- roda `python tools/looks/modelfile.py --check-image "$WE2002_LOOKS_IMAGE"`;
- **pula com 77** quando a variável não está no ambiente, com uma linha
  dizendo qual variável falta — nunca passa sem medir;
- o `WE2002_LOOKS_IMAGE` é o nome que o `layout.ENV_IMAGE` já declara, e ele
  aponta para a **trilha japonesa**, não para o `.cue` inglês
  (`WE2002_LOOKS_DRIVE_IMAGE`).

Vale registrar junto o `looks_selftest`, mesmo que a
[`LOOKS-TASK-06`](/docs/tasks/looks/06-harness-controles-e-selftest.md) ainda
vá escrever o agregador: hoje já há cinco módulos com `self_check()` e nenhum
deles roda sem alguém digitar. Se a preferência for esperar a 06, então **a
tabela de gates do perfil tem de dizer isso**, que é a outra metade desta
correção.

### Arquivo: `docs/prompts/perfil-looks.md`

A coluna "a partir de" passa a dizer a verdade — o alvo criado aqui, ou a task
que de fato o cria. E a
[`LOOKS-TASK-19`](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md) deixa de
prometer "os três alvos" se dois já existirem: ela passa a fechar a conta
(`ctest -R looks` = 1 passed, 2 skipped numa máquina limpa) em vez de criar do
zero.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tests/CMakeLists.txt` | modificar |
| `docs/prompts/perfil-looks.md` | modificar |
| `docs/tasks/looks/19-alvos-de-ctest-e-cli.md` | modificar |

## Verificação

- [ ] `ctest --test-dir build -R looks` **acha** o alvo e não imprime
      "No tests were found"
- [ ] sem `WE2002_LOOKS_IMAGE`, o alvo reporta **skipped (77)** e diz qual
      variável falta
- [ ] com a variável apontando `roms/japanese-shift-jis.bin`, o alvo passa e a
      saída traz as duas linhas de contagem com o offset de início
- [ ] apontar a variável para o disco **inglês** faz o alvo falhar pela guarda
      dos dois discos, e não passar em silêncio
- [ ] a tabela de gates do perfil e a 19 concordam sobre quem cria cada alvo
- [ ] `roms/` intocada — o alvo lê a imagem, não escreve

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
