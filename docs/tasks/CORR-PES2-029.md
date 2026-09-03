---
id: CORR-PES2-029
title: "Correção: estado ausente despeja traceback no `savestate.py`, e o `except` do `selftest.py` vira NameError"
type: correção
category: ferramenta
status: concluído
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

- [x] `python3 tools/pes2/savestate.py info /nao/existe.sav` imprime
      `error: …` e sai não-zero, sem traceback
- [x] o mesmo para `read`, `diff`, `ram`, `shot` e `scan`, e no `scan` a
      mensagem nomeia o estado que faltou
- [x] `python3 tools/pes2/savestate.py selftest` verde, com o caso vermelho
      novo aparecendo na lista de recusas
- [x] renomear `tools/pes2/savestate.py` temporariamente faz o
      `pes2_selftest` reportar `FAIL`, não um `NameError`
- [x] `ctest --test-dir build -R pes2_selftest` verde com o arquivo no lugar

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-09-03

**Resumo do que foi feito:** os dois caminhos, mais um terceiro que a leitura
que a CORR mandava fazer revelou.

1. **`savestate.py`.** O `open` do `SaveState.__init__` recusa `OSError` como
   `BadState`, que o `main` já imprime como `error: …` com saída 2. Como
   **todo** comando constrói um `SaveState`, um ponto só cobre os seis — e a
   mensagem leva o caminho, que é o que o `scan` precisa por receber vários.
   Um caso vermelho novo no `self_check`: os três que existiam são arquivos
   que **existem e mentem**; este é o que não está lá.
2. **`selftest.py`, bloco do `savestate`.** O import saiu do `try` cujo
   `except` nomeia o módulo, com o padrão `try/except/else`. O
   `# noqa: F821` saiu junto — o linter tinha visto e alguém o calou.
3. **`selftest.py`, bloco do `drive`** — a CORR mandava "merece a mesma
   leitura antes de se dar por fechado", e ele tinha **o mesmo defeito**:
   `import drive` dentro do `try`, `except drive.Skip` fora de alcance, e o
   mesmo `# noqa: F821`. Corrigido igual. O laço que roda `mcp`, `fork` e
   `mcp_drive` usa `__import__(name)` e não nomeia o módulo no `except`, então
   é seguro e ficou como está — foi conferido, não presumido.

**Problemas encontrados:** nenhum, e nenhum doc vivo ficou falso.

**Gates, com o número medido.** Os seis comandos com estado ausente, todos
`exit=2` e sem traceback:

```
info   /nao/existe.sav              error: /nao/existe.sav: No such file or directory
ram    /nao/existe.sav --out …      error: /nao/existe.sav: No such file or directory
shot   /nao/existe.sav --out …      error: /nao/existe.sav: No such file or directory
read   /nao/existe.sav 0x80000000   error: /nao/existe.sav: No such file or directory
diff   /nao/a.sav /nao/b.sav        error: /nao/a.sav: No such file or directory
scan   <bom>=1 /nao/existe.sav=2    error: /nao/existe.sav: No such file or directory
```

O `scan` **nomeia** o que faltou, e não o primeiro da lista. De brinde, um
diretório em vez de arquivo: `error: /tmp: Is a directory`.

O caso vermelho novo, na lista de recusas do `selftest`:

```
  [ok] a missing state is refused -- …/there-is-no-such-state.sav: No such file or directory
all checks passed, and every guard was seen refusing
```

E os dois `NameError` fechados, medidos por remoção do módulo:

```
$ mv tools/pes2/savestate.py … && python3 tools/pes2/selftest.py
  FAIL savestate.py reader, scan and guards  -- ModuleNotFoundError: No module named 'savestate'
FAILED                                                             exit 1
$ mv tools/pes2/drive.py … && python3 tools/pes2/selftest.py
  FAIL drive.py frame logic  -- ModuleNotFoundError: No module named 'drive'
  FAIL mcp_drive.py routes and thresholds  -- ModuleNotFoundError: No module named 'drive'
```

Antes, os dois saíam com `NameError: name 'savestate' is not defined` levantado
**durante o tratamento**, que o `except Exception` irmão não pega. Com os
arquivos no lugar, `pes2_selftest` **Passed 0,34 s**.

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `tools/pes2/savestate.py` | modificado (`SaveState.__init__`, caso vermelho no `self_check`) |
| `tools/pes2/selftest.py` | modificado (os blocos do `savestate` e do `drive`) |
