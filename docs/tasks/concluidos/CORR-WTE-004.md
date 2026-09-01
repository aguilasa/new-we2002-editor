---
id: CORR-WTE-004
title: "Correção: `--check` fica vermelho num clone limpo, porque `blobs/` é gitignored e o modo de conferência nunca o materializa"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-004: `--check` não distingue "gerado editado à mão" de "blob ainda não materializado"

## Problema identificado

`wte/tools/dfm_extract.py --check` exige que os 118 `.bin` estejam no disco:

```python
    for name, data in sorted(blob_files.items()):
        path = BLOBS / name
        if not path.exists():
            problems.append(f"blobs/{name}: nao existe")
```

Mas `wte/re/dfm/blobs/` é **ignorado pelo git** (`.gitignore:99`, decisão da
própria WTE-TASK-03) e só nasce no modo de escrita. Num clone limpo, com o
`we-team-editor.exe` presente e a árvore versionada intacta, o gate
`make -C wte check` sai **vermelho com 118 linhas de `nao existe`**.

O que a WTE-TASK-02 declara que esse alvo mede é outra coisa:

> `# Gate das fases 1 a 3: nenhum arquivo gerado foi editado a mao.`
> (`wte/Makefile`, alvo `check`)

Blob ausente não é arquivo editado à mão — é o estado normal de quem acabou de
clonar. O gate hoje não separa os dois, e o vermelho de rotina é o que ensina a
ignorar vermelho.

O `.dfm` versionado **já** ancora os bytes: a referência
`{blob <arquivo> <tamanho> sha256:<hash>}` é regerada do `.exe` a cada
`--check` e comparada com a commitada, então um `.exe` trocado ou um blob
diferente derruba a conferência pelo texto, sem depender do `.bin` no disco. A
checagem de existência não acrescenta garantia; acrescenta um falso vermelho.

Some-se a isso que o `dfm_extract.py` e o `wte/re/dfm/README.md` afirmam que
`blobs/` "renasce do `.exe` a cada execução" — o que não vale para a execução
com `--check`, que é justamente a que o Makefile roda.

## Evidência

Conferência com a árvore versionada correta e `blobs/` ausente (o estado de um
clone limpo), simulada sem tocar na árvore real — `OUT`/`BLOBS` apontados para
uma cópia em sandbox:

```
wte/re/dfm nao corresponde a we-team-editor/we-team-editor.exe:
  blobs/MainForm/Image1.Picture.Data.bin: nao existe
  blobs/MainForm/Image2.Picture.Data.bin: nao existe
  ... (118 linhas)
rode: python3 wte/tools/dfm_extract.py
B) clone limpo (sem blobs/): 1
```

Para contraste, a mesma sandbox com **uma linha editada à mão** — o que o gate
existe para pegar — devolve o mesmo código de saída 1:

```
wte/re/dfm nao corresponde a we-team-editor/we-team-editor.exe:
  ficha_about.dfm: linha 4 diverge
A) edicao a mao: 1
```

Os dois estados são indistinguíveis pelo código de saída, e o segundo é o que
importa.

Na máquina do usuário o alvo está verde, porque a WTE-TASK-03 rodou o gerador
em modo de escrita:

```
$ python3 wte/tools/dfm_extract.py --check
19 arquivos e 118 blobs em dia com we-team-editor/we-team-editor.exe
```

Impacto atual: **zero**. O defeito é latente, como o da CORR-WTE-003.

## Causa raiz

`do_check()` trata `blobs/` como saída versionada, mas ela é cache regenerável
— o `.gitignore` diz isso e o `.dfm` já carrega o hash que a substitui.

## Correção

### Arquivo: `wte/tools/dfm_extract.py`

Em `do_check()`, separar as duas condições:

- **blob ausente** — cache não materializado. Não é falha de conferência:
  reportar como aviso na saída padrão (`118 blobs ainda nao materializados --
  rode sem --check para gera-los`) e **não** somar a `problems`.
- **blob presente e divergente** — continua falha, com a linha atual
  (`conteudo diverge do .exe`).
- **blob sobrando** (`rglob("*.bin")` sem par no `.exe`) — continua falha.

A garantia byte a byte não muda: ela vem do SHA-256 dentro do `.dfm`
versionado, que a comparação de texto já cobre. O que a mudança tira é o
vermelho por um estado que o próprio `.gitignore` declara normal.

### Arquivo: `wte/re/dfm/README.md`

A frase "`blobs/` é ignorado pelo git e renasce do `.exe` a cada execução" vale
só para o modo de escrita. Dizer isso: uma linha registrando que `--check` não
materializa nada, e que um clone limpo roda `python3 wte/tools/dfm_extract.py`
uma vez antes de consumir os blobs (a WTE-TASK-10 precisa deles no disco).

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dfm_extract.py` | modificar |
| `wte/re/dfm/README.md` | modificar |

## Verificação

- [x] `python3 wte/tools/dfm_extract.py --check` continua verde na árvore atual,
      com os 118 blobs materializados
- [x] Com `BLOBS` apontado para diretório vazio (sandbox, sem mexer na árvore),
      o comando sai **0** e imprime o aviso de blobs não materializados
- [x] Com um `.bin` alterado na sandbox, o comando sai **1** com
      `conteudo diverge do .exe`
- [x] Com uma linha de `.dfm` alterada na sandbox, o comando sai **1** com
      `linha N diverge`
- [x] `make -C wte check` verde
- [x] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-05

**Resumo do que foi feito:**

`do_check()` passou a contar blob ausente num `missing_blobs` que **não** entra
em `problems`: sai como `AVISO: N blobs ainda nao materializados`, na saída
padrão, e o código de retorno continua 0. Blob presente e divergente, blob
sobrando, `.dfm` divergente e `.dfm` ausente continuam falha. A linha final
passou a contar os blobs **presentes** (`19 arquivos e 0 blobs em dia` no clone
limpo), para não afirmar conferência de arquivo que não foi lido.

Os cinco estados foram medidos em sandbox, com `OUT`/`BLOBS` redirecionados —
a árvore real nunca foi tocada: árvore íntegra → 0; sem `blobs/` → 0 com aviso;
`.bin` alterado → 1; linha de `.dfm` alterada → 1; blob sobrando → 1.

**Problemas encontrados:**

A varredura de discrepância pegou um terceiro arquivo, que a lista da CORR não
previa: `wte/re/dfm/censo.md` repetia a mesma frase obsoleta ("`blobs/` renasce
do `.exe` a cada execução"). Ele é **gerado** por `render_census()`, então a
correção entrou no gerador e o `censo.md` foi regerado — não editado à mão.

**Arquivos criados/modificados:**

- `wte/tools/dfm_extract.py` — `do_check()`, o docstring do módulo e o texto de
  `render_census()`
- `wte/re/dfm/README.md`
- `wte/re/dfm/censo.md` — regerado
- `docs/tasks/concluidos/correcoes-progresso.md`
