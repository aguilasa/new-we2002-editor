---
id: CORR-WTE-002
title: "Correção: dois números do `ambiente.md` só são reproduzíveis pelo scratchpad"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-002: evidência que mora no `/tmp` e comando que não está escrito

## Problema identificado

`wte/re/ambiente.md` abre afirmando "Nenhum número aqui foi digitado de
memória", e toda linha das tabelas traz a coluna **"Como foi medido"** com o
comando exato — `fpc -iV`, `sha256sum`, `dpkg-query -W`, `ps -o args= -C Xvfb`.
Reexecutei todos e batem (ver o relatório da revisão).

**Dois blocos do mesmo arquivo fogem dessa regra** — são os únicos números do
documento sem comando escrito, e a evidência de ambos está num diretório de
`/tmp` que some no próximo boot:

1. **Achado 1**, o bloco `blocks=9` / `symbols=509` / `compiler=borlandcpp`.
   Veio de um script Ghidra `ShowInfo.java` escrito no scratchpad da execução.
   O `.md` apresenta a saída, mas o script não está versionado e o documento
   não diz como regerá-la.
2. **Achado 2**, o censo de 24 janelas do qual saem os 18 formulários. O texto
   diz "A contagem saiu de `xdotool` + `grep -vc`" e aponta para
   "`wte-windows.tsv` no scratchpad da execução" — um caminho que não existe
   para ninguém além daquela sessão.

Os números **estão certos**: o scratchpad ainda não foi limpo e reproduzi os
dois lá (a `.tsv` tem 24 linhas; 24 − 3 `Default IME` − `Input` − `Abre` − a
oculta 1x1 = 18; o `ghidra-import2.log` traz `SMOKE blocks=9` e
`SMOKE symbols=509`). O defeito é de **reprodutibilidade**, não de valor: no
próximo boot a evidência some e o leitor fica sem rota para remedir.

Isso morde de verdade na **WTE-TASK-03**, que o próprio `ambiente.md` convida a
confrontar os tamanhos de janela contra os DFM extraídos.

## Evidência

Onde a evidência mora hoje:

```console
$ ls /tmp/claude-1000/-home-ingmar-.../scratchpad/
ShowInfo.java   wte-windows.tsv   ghidra-import2.log   lclsmoke/   ...

$ wc -l .../wte-windows.tsv
24 .../wte-windows.tsv

$ grep SMOKE .../ghidra-import2.log
INFO  ShowInfo.java> SMOKE blocks=9 (GhidraScript)
INFO  ShowInfo.java> SMOKE symbols=509 (GhidraScript)
```

Nada disso está sob `git ls-files`:

```console
$ git ls-files wte/
wte/re/ambiente.md
```

Contraste com o resto do documento, onde cada número tem comando ao lado:

| Linha do `ambiente.md` | "Como foi medido" |
|---|---|
| `fpc` 3.2.2 | `fpc -iV`, `fpc -iD`, `dpkg-query` |
| SHA-256 do `.exe` | `sha256sum` |
| Xvfb `:99` | `ps -o args= -C Xvfb` |
| **`blocks=9` / `symbols=509`** | **(ausente)** |
| **24 janelas → 18 formulários** | **(ausente)** |

## Causa raiz

Os dois números derivam de ferramenta ad-hoc criada durante a execução; o
documento registrou o resultado e não o caminho de volta.

## Correção

Não é para remedir nada — os valores estão conferidos. É para deixar escrito
como remedi-los.

### Arquivo: `wte/re/ambiente.md`

No **Achado 1**, acrescentar abaixo do bloco de saída a linha de comando e o
script inteiro (são 10 linhas — cabe inline, não precisa de arquivo novo):

```markdown
Reproduzir:

    $GHIDRA/support/analyzeHeadless <proj-dir> <proj> \
        -import we-team-editor/we-team-editor.exe \
        -scriptPath <dir do ShowInfo.java> -postScript ShowInfo.java \
        -noanalysis -overwrite

com `ShowInfo.java`:

    import ghidra.app.script.GhidraScript;
    public class ShowInfo extends GhidraScript {
      public void run() throws Exception {
        println("SMOKE format="   + currentProgram.getExecutableFormat());
        println("SMOKE lang="     + currentProgram.getLanguageID());
        println("SMOKE compiler=" + currentProgram.getCompilerSpec().getCompilerSpecID());
        println("SMOKE imagebase="+ currentProgram.getImageBase());
        println("SMOKE blocks="   + currentProgram.getMemory().getBlocks().length);
        println("SMOKE symbols="  + currentProgram.getSymbolTable().getNumSymbols());
      }
    }
```

No **Achado 2**, trocar a frase que aponta para o scratchpad pelo comando que
gera a lista, e apagar a referência ao caminho volátil:

```markdown
Reproduzir (com o `make wte-99` no ar, `DISPLAY`/`XAUTHORITY` como manda o
`CLAUDE.md`):

    xdotool search --name '.' 2>/dev/null | while read i; do
      n=$(xdotool getwindowname "$i" 2>/dev/null) || continue
      g=$(xdotool getwindowgeometry "$i" | sed -n 's/.*Geometry: //p')
      [ -n "$n" ] && printf '%s\t%s\n' "$n" "$g"
    done | sort

24 linhas; descontando as seis não-formulário citadas acima, sobram 18.
```

> O comando acima é o **roteiro do estado correto**, não transcrição: quem
> executar esta CORR deve rodá-lo, conferir que devolve as mesmas 24 linhas já
> tabuladas no documento e só então gravá-lo. Se devolver outra coisa, o achado
> é que muda — não o comando.

Se as duas linhas do TSV divergirem da tabela já publicada, **isso é um achado
novo**: registre no Log desta CORR em vez de ajustar a tabela em silêncio.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/ambiente.md` | modificar |

## Verificação

- [ ] Nenhuma menção a caminho de scratchpad sobrou:
      `grep -n 'scratchpad' wte/re/ambiente.md` não devolve nada
- [ ] Os dois comandos foram **rodados**, e a saída bate com a já publicada
      (24 linhas de janela; `blocks=9`, `symbols=509`)
- [ ] Todo número do arquivo tem comando ao lado ou logo abaixo
- [ ] `we-team-editor.exe` continua com o hash registrado:
      `sha256sum we-team-editor/we-team-editor.exe` → `9cebce64…`
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
