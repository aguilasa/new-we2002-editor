---
id: CORR-PES2-029
title: "Correção: estado ausente despeja traceback no `savestate.py`, e o `except` do `selftest.py` vira NameError"
type: correção
category: ferramenta
status: pendente
depends_on: []
---

# CORR-PES2-029: dois caminhos de falha saem como traceback onde deviam sair como recusa

## Problema identificado

A lista de Fase 0 do [`perfil-pes2.md`](/docs/prompts/perfil-pes2.md) pergunta:

> - O caso de recurso ausente diz o que fazer, ou despeja traceback? "o fork
>   não está rodando" contra um `URLError` de `urllib`

No `savestate.py` a resposta é dividida, e é a divisão que incomoda: um
arquivo que **existe** e não é save state recebe recusa limpa; um arquivo que
**não existe** recebe traceback.

**Segundo caminho, no `selftest.py`.** O bloco que roda o leitor faz o import
dentro do `try` e escreve o `except` sobre o módulo importado:

```python
try:
    import savestate                                      # noqa: E402
    failures = savestate.self_check(verbose=False)
    ...
except savestate.Skip as why:                             # noqa: F821
    ...
except Exception as exc:                                  # noqa: BLE001
    bad += check("savestate.py reader, scan and guards", False, ...)
```

Se o **import** falhar — arquivo removido, erro de sintaxe, dependência que
some — o nome `savestate` não existe quando o interpretador avalia
`except savestate.Skip`, e isso levanta `NameError` **durante o tratamento**.
O `except Exception` irmão **não** o pega: a exceção escapa do `try` inteiro.
O resultado é o `pes2_selftest` morrendo com traceback em vez de reportar
`FAIL   savestate.py reader, scan and guards`, que é exatamente o que aquele
`except Exception` foi escrito para dar.

O `# noqa: F821` mostra que o problema foi visto pelo linter e silenciado.

## Evidência

O contraste dentro do próprio `savestate.py`:

```
$ python3 tools/pes2/savestate.py info CLAUDE.md
error: CLAUDE.md: magic 0x4c432023, not DUCC          (exit 2)

$ python3 tools/pes2/savestate.py info /nao/existe.sav
Traceback (most recent call last):
  ...
    with open(path, "rb") as fh:
         ~~~~^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/nao/existe.sav'   (exit 1)
```

O padrão do `selftest.py`, reproduzido isolado:

```python
try:
    import modulo_que_nao_existe as savestate
    savestate.self_check()
except savestate.Skip as why:
    print("skip:", why)
except Exception as exc:
    print("capturado limpo:", type(exc).__name__)
```

```
  File "nameerr.py", line 5, in <module>
    except savestate.Skip as why:
           ^^^^^^^^^
NameError: name 'savestate' is not defined
```

O `except Exception` logo abaixo não foi alcançado.

## Causa raiz

Nos dois casos a cerca foi escrita para o erro **esperado** — magic errado,
numpy ausente — e o caminho em que o próprio artefato não está lá ficou sem
cerca nenhuma.

## Correção

### Arquivo: `tools/pes2/savestate.py`

Recusar arquivo ausente ou ilegível com a mesma forma `error: …` das demais,
no ponto em que o caminho é aberto:

```python
try:
    with open(path, "rb") as fh:
        ...
except OSError as exc:
    raise Fail(f"{path}: {exc.strerror}") from None
```

Vale para `info`, `ram`, `shot`, `read`, `diff` e `scan` — o `scan` recebe
vários caminhos, e a mensagem tem de dizer **qual** deles falhou.

### Arquivo: `tools/pes2/selftest.py`

Tirar o import de dentro do bloco cujo `except` depende dele:

```python
try:
    import savestate                                      # noqa: E402
except Exception as exc:                                  # noqa: BLE001
    bad += check("savestate.py reader, scan and guards", False,
                 f"{type(exc).__name__}: {exc}")
else:
    try:
        failures = savestate.self_check(verbose=False)
        bad += check("savestate.py reader, scan and guards", not failures,
                     ", ".join(failures))
    except savestate.Skip as why:
        print(f"  ..   savestate.py skipped: {why}")
    except Exception as exc:                              # noqa: BLE001
        bad += check("savestate.py reader, scan and guards", False,
                     f"{type(exc).__name__}: {exc}")
```

O `# noqa: F821` sai junto — com o import fora do `try`, o nome existe.

**Conferir os blocos irmãos.** O laço que roda `mcp`, `fork` e `mcp_drive`
usa `__import__(name)` dentro do `try` com `except Exception`, que é seguro
porque não nomeia o módulo no `except`. O de `drive.py` merece a mesma
leitura antes de se dar por fechado.

### Verificação nova no `self_check`

Um caso vermelho para o caminho ausente, junto dos que já existem — o
`selftest` do leitor já vê "a truncated state is refused" e "a wrong RAM size
is refused"; falta "a missing state is refused".

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/savestate.py` | modificar |
| `tools/pes2/selftest.py` | modificar |

## Verificação

- [ ] `python3 tools/pes2/savestate.py info /nao/existe.sav` imprime
      `error: …` e sai não-zero, sem traceback
- [ ] o mesmo para `read`, `diff`, `ram`, `shot` e `scan`, e no `scan` a
      mensagem nomeia o estado que faltou
- [ ] `python3 tools/pes2/savestate.py selftest` verde, com o caso vermelho
      novo aparecendo na lista de recusas
- [ ] renomear `tools/pes2/savestate.py` temporariamente faz o
      `pes2_selftest` reportar `FAIL`, não um `NameError`
- [ ] `ctest --test-dir build -R pes2_selftest` verde com o arquivo no lugar

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
