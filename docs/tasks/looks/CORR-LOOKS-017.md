---
id: CORR-LOOKS-017
title: "Correção: sem `WE2002_LOOKS_IMAGE` o `--check-live` sobe o emulador e morre num traceback, em vez de pular com 77"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-LOOKS-017: o quarto pré-requisito do `--check-live` não tem caminho de skip

## Problema identificado

O critério da task diz: *"Sem emulador, ou sem os states, **pula** (77) com a
mensagem dizendo o que falta."* O `--check-live` faz isso para **três**
pré-requisitos, e o Log os confere um a um. Ele precisa de **quatro**.

O quarto é a `WE2002_LOOKS_IMAGE` — a trilha japonesa, que o `verify_load()`
abre para comparar a RAM contra o disco. Ela não está na preflight, então o
comando **sobe o emulador**, esconde a janela, roda cinco verificações, e só aí
morre:

```
  window moved off the visible desktop
  ok    a reloaded state is the same picture to the last bit
  ok    the two slots show different players
  ok    slot 2's picture is refused as slot 1
  slot 1 restored: the goalkeeper, on LOOKS SET
Traceback (most recent call last):
  File "...\oracle.py", line 882, in main
    return check_live()
  File "...\oracle.py", line 662, in check_live
    report = game.verify_load()
  File "...\iso_source.py", line 103, in image_from_env
    raise RuntimeError(
RuntimeError: WE2002_LOOKS_IMAGE is not set: ...
                                                                      (rc=1)
```

**Exit 1, com traceback.** Pelo contrato que o perfil escreve — *"mediu e
passou, ou pulou com 77"* — isso não é nenhum dos dois. E quem vir a saída lê
`oracle.py, line 882` no topo e vai procurar defeito no oráculo; o que falta é
uma variável de ambiente que o comando poderia ter conferido antes de ligar o
emulador.

Três agravantes pequenos, todos medidos:

- **O custo já foi pago quando a falha aparece.** O fork sobe, a janela vai
  para −32000, três save states são restaurados. Uns 30 segundos e o emulador —
  que este ciclo trata como **recurso serializado**, uma instância por vez —
  ocupado à toa. (A boa notícia: ele **não** fica para trás; conferido com
  `Get-Process` depois do estouro, nenhum processo sobrou.)
- **A mensagem certa já existe e não é usada.** O
  `iso_source.image_from_env()` levanta exatamente o texto que um skip deveria
  imprimir — ele nomeia as **duas** variáveis, que é a confusão que os dois
  nomes existem para evitar. Falta capturá-lo.
- **O módulo irmão já resolveu isso.** O `modelfile.py --check-image` sem a
  variável imprime `skipped -- WE2002_LOOKS_IMAGE is not set: ...` e sai **77**
  ([`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md)). O padrão está na
  casa; o `--check-live` não o herdou.

O Log da task afirma *"Os três caminhos de skip, conferidos um a um e todos
saindo 77"*, e é verdade — esta revisão reproduziu os três. O defeito é que são
quatro pré-requisitos e três caminhos.

## Evidência

Os três que funcionam, reproduzidos:

```
$ python tools/looks/oracle.py --check-states
oracle: skipped -- WE2002_LOOKS_DRIVE_IMAGE is not set: it names the English
.cue the emulator boots. ...                                        (rc=77)

$ WE2002_LOOKS_DRIVE_IMAGE=<cue> WE2002_LOOKS_STATES=C:/nope-not-here \
    python tools/looks/oracle.py --check-live
oracle: skipped -- no project copy of slot 1 at C:/nope-not-here\SLPM-87056_1.sav
-- run --adopt-states                                               (rc=77)

$ WE2002_LOOKS_DRIVE_IMAGE=<cue> WE2002_LOOKS_IMAGE=<bin> PES2_FORK=C:/nowhere-fork \
    python tools/looks/oracle.py --check-live
oracle: skipped -- no DuckStation fork at C:/nowhere-fork\duckstation-qt-x64-ReleaseLTCG.exe
-- run `tools/pes2/fork.py recipe` for how to build it              (rc=77)
      (e nenhum diretorio deixado para tras)
```

O quarto, que não funciona: o bloco de traceback acima, com apenas
`WE2002_LOOKS_DRIVE_IMAGE` posta.

Com as duas variáveis, o mesmo comando fecha verde e mede tudo — esta revisão
reproduziu **cada número** do Log:

```
  shot slot1-goalkeeper  mean=0.182425 sd=0.189376
  shot slot2-outfield    mean=0.183158 sd=0.190350
  ok    a reloaded state is the same picture to the last bit
  ok    the two slots show different players
        the plate differs by 0.119963 between the slots
  ok    slot 2's picture is refused as slot 1
        the position plate reads 0.299999 and slot 1 reads 0.291686 (+-0.004000)
  /BIN/EDT_MOD.BIN at 0x8011c000: 203 of 36072 byte(s) differ ... section(s) 0, 3, 4, 5, 6, 7, 8, 9, 10
  /BIN/MODEL.BIN   at 0x8016e800:  20 of 64800 byte(s) differ ... section(s) 24, 32
  ok    both model files are loaded where layout.py says
  Right moved it by 0.108086
oracle --check-live: 0 failure(s)                                    (rc=0)
```

**O oráculo está certo. O que falta é a porta de entrada dele.**

## Causa raiz

A preflight do `--check-live` confere o disco de dirigir, os states e o fork, e
não confere a imagem japonesa, que só é exigida lá dentro pelo
`verify_load()`.

## Correção

### Arquivo: `tools/looks/oracle.py`

Na preflight do `check_live()`, antes de qualquer `launch`, conferir também a
`WE2002_LOOKS_IMAGE` — chamando o `iso_source.image_from_env()` e convertendo o
`RuntimeError` em skip 77 com a mesma mensagem, que é a forma que o
`modelfile.py --check-image` já usa. Ordem importa: **tudo que pode faltar se
confere antes de subir o emulador.**

Vale a asserção estrutural junto, para o quinto pré-requisito não repetir a
história: o `check_live()` lista o que precisa num só lugar, e a preflight
percorre essa lista.

### Caso vermelho

O `self_check()` sintético não alcança isto — é o `main()` que decide skip
contra falha. Então o caso vermelho é o do próprio comando, e pode ficar como
está nos outros três: uma corrida com a variável ausente, exigindo **77** e
nenhuma linha de traceback. Se houver um jeito barato de exercitá-lo no
`selftest` (chamar `check_live()` com o ambiente limpo e exigir 77 antes de
qualquer `launch`), melhor — é o que torna a regra permanente.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/oracle.py` | modificar |

## Verificação

- [ ] `WE2002_LOOKS_DRIVE_IMAGE` posta e `WE2002_LOOKS_IMAGE` ausente:
      `--check-live` sai **77**, com a mensagem que nomeia as duas variáveis
- [ ] e **não** sobe o emulador nesse caminho (nenhuma linha `fork ... on this
      desktop`, e `Get-Process` sem DuckStation depois)
- [ ] os outros três caminhos de skip continuam saindo 77
- [ ] com as duas variáveis, `--check-live` continua dando `0 failure(s)` e as
      mesmas contagens de RAM
- [ ] `python tools/looks/selftest.py` verde, com os 9 controles vermelhos
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
