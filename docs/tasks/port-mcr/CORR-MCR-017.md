---
id: CORR-MCR-017
title: "Correção: o perfil promete 15 controles vermelhos e o `mcr_selftest` exige 16, do décimo sexto o perfil não conhece nem a forma"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-MCR-017: o número do gate obrigatório envelheceu no arquivo onde se lê o gate

## Problema identificado

O `perfil-mcr.md` é onde o `/executar` e o `/revisar` leem **o que cada gate
exige** antes de rodar qualquer coisa. Ele diz 15 em dois lugares, e a
ferramenta mede 16:

| onde | o que diz |
|---|---|
| `perfil-mcr.md:141`, a linha do `mcr_selftest` na tabela de gates | "…**e as 15 substituições literais, exigidas vermelhas**" |
| `perfil-mcr.md:149` | "As **quinze** substituições moram em `tools/mcr/controls.py` — arquivo, função, linha exata, e o que ela vira" |
| `python3 tools/mcr/controls.py` | `controls: 16 of 16 red` |

A MCR-TASK-11 criou o décimo sexto — `ui-imports-an-address` — e **editou a
linha 143 e a linha 124** do mesmo arquivo (a do `mcr_ui`, que passou a verde,
e a da estrutura). A linha 141 ficou.

**E não é só o número.** A frase da linha 149 descreve o conteúdo de
`controls.py` como "arquivo, função, linha exata, e o que ela vira" — o que
não descreve o `ui-below-the-sweep`, que a
[CORR-MCR-014](/docs/tasks/port-mcr/CORR-MCR-014.md) abriu e que **cria um
arquivo** (`creates=True`) em vez de substituir uma linha. Hoje o motor tem
dois tipos e o perfil só conhece um; um leitor que confira `controls.py`
contra o perfil conclui que sobrou um controle a explicar.

O `progresso.md` do mesmo ciclo, atualizado pela **mesma task**, já diz certo:

> Controles negativos | **16/16 vermelhos**, com e sem fixture: quinze por
> substituição literal, um que cria um arquivo uma pasta abaixo.

Os dois documentos do ciclo discordam, e o que os comandos leem primeiro é o
que está errado.

## Evidência

```
$ python3 tools/mcr/controls.py | tail -3
  RED    ui-imports-an-address      ui/main_window.py :: module scope  (skips: {'selftest': 6})
  RED    ui-below-the-sweep         ui/_probe.py :: a new file, one directory down
controls: 16 of 16 red

$ PYTHONPATH=tools/mcr python3 -c \
    "import controls; print(len(controls.CONTROLS), \
     sum(1 for k in controls.CONTROLS if not k.creates), \
     sum(1 for k in controls.CONTROLS if k.creates))"
16 15 1

$ grep -n "15 substitui\|quinze substitui" docs/prompts/perfil-mcr.md
141:| `mcr_selftest` | ... **e as 15 substituições literais, exigidas vermelhas** ...
149:**Controle negativo se roda, não se descreve.** As quinze substituições moram
```

E o diff da task mostra que o arquivo foi editado com a linha errada à vista:

```
$ git show 7901d36 -- docs/prompts/perfil-mcr.md
-tools/mcr/ui/         a UI PySide6 -- não importa layout/card/io
+tools/mcr/ui/         a UI PySide6 -- só importa `model` e `domains`, ...
 | `mcr_selftest` | ... **e as 15 substituições literais, ...** |     <- intacta
-| `mcr_ui` | ... Registrado já; pula com 77 até a MCR-TASK-11 ...
+| `mcr_ui` | ... **Passa desde a MCR-TASK-11**; ...
```

Os 16 são vermelhos de verdade — replantados nesta revisão, com e sem fixture,
e o `ui-imports-an-address` acusa pelo nome:

```
FAIL  Rule 3: the UI imports no core module that knows an address
      ['ui/main_window.py:26: mcrio']
```

O defeito é do **número no perfil**, não do gate.

## Causa raiz

O total de controles é afirmado em prosa em dois documentos e medido em um
terceiro lugar; toda task que acrescenta um controle tem de lembrar dos dois.

## Correção

### Arquivo: `docs/prompts/perfil-mcr.md`

Duas linhas, e a segunda ganha o tipo que falta:

```markdown
| `mcr_selftest` | MCR-TASK-10 | os 12 `self_check()`, as três regras, a
varredura de idioma **e os 16 controles negativos, exigidos vermelhos** — sem
fixture e sem Qt, ~13 s. **Obrigatório** |
```

```markdown
**Controle negativo se roda, não se descreve.** Os dezesseis controles moram em
`tools/mcr/controls.py`, em dois tipos: **quinze substituições literais** —
arquivo, função, linha exata e o que ela vira — e **um que cria um arquivo**
uma pasta abaixo (`creates=True`), que é como se prova que uma varredura
**desce**. `python3 tools/mcr/controls.py` planta cada um numa cópia da árvore
e exige o vermelho; substituição que casa zero ou duas vezes é reportada como
**controle quebrado**, não como vermelho.
```

### E o que impede a próxima

O número vai envelhecer de novo. O barato é o `controls.py` **imprimir** o
resumo por tipo na última linha — `controls: 16 of 16 red (15 substitutions,
1 new file)` —, e o perfil dizer "o total que `controls.py` imprime" em vez de
repetir o número. É a mesma escolha que o `--edit-probe` já fez na MCR-TASK-09:
reportar em vez de afirmar.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/prompts/perfil-mcr.md` | modificar |
| `tools/mcr/controls.py` | modificar (o resumo por tipo na última linha) |

## Verificação

- [ ] `grep -n "quinze substitui\|15 substitui" docs/prompts/perfil-mcr.md` sai
      vazio
- [ ] o número que o perfil cita é o que `python3 tools/mcr/controls.py`
      imprime, e os dois tipos estão descritos
- [ ] `python3 tools/mcr/controls.py` continua **16 de 16 vermelhos**, com e
      sem fixture, e o `self_check` do `controls.py` continua com 5 checks
- [ ] `ctest -R mcr` = **3 de 3**, e `make test` verde
- [ ] `python3 tools/check_tasks.py` e `ctest -R tasks` verdes
- [ ] `roms/` intocada; a fixture com o mesmo `sha256sum`

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
