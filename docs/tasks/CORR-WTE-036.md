---
id: CORR-WTE-036
title: "Correção: a regra `!` → `not` do `SUBS` atravessa a quebra de linha e engole seis statements para dentro de comentário"
type: correção
category: dados
status: pendente
depends_on: []
---

# CORR-WTE-036: a armadilha que o próprio cabeçalho documenta, cometida na regra 7

## Problema identificado

`wte/tools/port_database_pas.py`, regra 7 do `SUBS`:

```python
(r"!\s*(?=\w|\()", "not ", "! -> not"),
```

`\s*` casa `\n`. Onde um `!` termina a linha, a substituição **consome a quebra**
e cola a linha seguinte no fim da atual. Nas seis ocorrências do
`src/core/Database.cpp` a linha que termina em `!` é um **comentário `//`** — e o
statement da linha de baixo entra dentro dele.

Dois dos seis engolidos são `image_file.Seek(OFS_KIT_PREVIEW)`. Em Pascal, `//`
comenta até o fim da linha: um `Seek` absoluto **desapareceria** da unidade
emitida, e o ponteiro de arquivo ficaria onde a operação anterior o deixou.
É o mesmo desfecho do bug histórico que o `check_seeks()` existe para pegar,
por um caminho que ele não vê.

**O `check_seeks()` não pega**, e não é falha dele: ele conta ocorrências de
`Seek`/`SeekCurrent` no texto, e o texto continua tendo as duas — só que dentro
de um comentário. `test_a_direcao_dos_seeks_do_core_se_preserva` passa verde
sobre uma saída em que dois `Seek` já estão comentados.

**O guard que deveria ter pego olha só metade da classe.**
`test_nenhuma_regra_usa_classe_negada_sem_excluir_a_quebra` reprova regra com
`[^x]` sem `\n` — e o cabeçalho do script repete a lição
(«ao escrever regra nova em `SUBS`, `[^x]` casa `\n`»). Mas `\s*`, `\s+`,
`[\s\S]*` e `.` com `re.DOTALL` atravessam a quebra do mesmo jeito, e nenhum
deles é conferido.

Nada é emitido hoje (498 recusas em aberto), então o dano ainda não saiu do
transpilador. **A WTE-TASK-18 é justamente quem vai destravar a emissão**, e o
defeito está a montante dela.

## Evidência

A regra que muda a contagem de linhas, isolada rodando o `SUBS` em ordem sobre
`Database.cpp`:

```
regra 7: 1704 -> 1698   padrao='!\\s*(?=\\w|\\()' repl='not ' razao=! -> not
```

Os seis sítios, com o que cada um engole:

```
src/core/Database.cpp:497    '\t//kit preview !!!!!!!!!!!!!!!!'  <- 'image_file.Seek(OFS_KIT_PREVIEW);'
src/core/Database.cpp:1071   '\t//kit preview !!!!!!!!!!!!!!!!'  <- 'image_file.Seek(OFS_KIT_PREVIEW);'
src/core/Database.cpp:1492   '\t\t\t// i 9!!'                    <- 'if(db.players[i].acceleration == 19)'
src/core/Database.cpp:1547   '\t\t\t// i 9!!'                    <- 'if(db.players[i].acceleration == 19)'
src/core/Database.cpp:1607   '\t\t\t// i 9!!'                    <- 'if(db.players[i].acceleration == 19)'
src/core/Database.cpp:1665   '\t\t\t// i 9!!'                    <- 'if(db.players[i].acceleration == 19)'
```

A entrada e a saída lado a lado no primeiro sítio:

```
ENTRADA
  497: '\t//kit preview !!!!!!!!!!!!!!!!'
  498: '\timage_file.Seek(OFS_KIT_PREVIEW);'

SAÍDA
  497: '\t//kit preview !!!!!!!!!!!!!!!not image_file.Seek(OFS_KIT_PREVIEW, soBeginning);'
```

E o guard que passa verde por cima disso:

```
$ python3 -m unittest discover -s wte/tools -p 'test_port_database_pas.py'
Ran 38 tests ... OK
```

## Causa raiz

`\s*` casa `\n` — a mesma propriedade de `[^x]` que o cabeçalho do script já
adverte —, e o teste que fiscaliza isso reconhece só a forma `[^x]`.

## Correção

### Arquivo: `wte/tools/port_database_pas.py`

Ancorar a regra na mesma linha. Trocar `\s*` por `[^\S\n]*` (espaço horizontal,
nunca quebra):

```python
(r"!(?=[^\S\n]*[\w(])", "not ", "! -> not"),
```

ou aplicar o `SUBS` linha a linha para as regras que não têm razão para
atravessar. Qualquer das duas serve; o que não pode continuar é a regra
consumindo o `\n`.

### Arquivo: `wte/tools/test_port_database_pas.py`

1. Alargar `test_nenhuma_regra_usa_classe_negada_sem_excluir_a_quebra` para
   **toda** construção que atravessa quebra: `[^…]` sem `\n`, `\s`, `[\s\S]`,
   e `.` sob `re.DOTALL`. O nome do teste passa a valer o que ele promete.
2. Teste de invariante sobre a entrada real: `aplicar_subs` não pode reduzir a
   contagem de linhas de nenhum arquivo do `UNITS` — hoje reduz 6 em
   `Database.cpp`.
3. Teste com entrada plantada: `//x !\nimage_file.Seek(1);` tem de sair com o
   `Seek` **fora** do comentário.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/port_database_pas.py` | modificar |
| `wte/tools/test_port_database_pas.py` | modificar |
| `wte/re/transpilador.md` | modificar (regerado — a tabela publica o padrão da regra) |

## Verificação

- [ ] `python3 -c` sobre o `SUBS`: nenhuma regra casa `\n` nas seis unidades —
      a contagem de linhas de cada arquivo é idêntica antes e depois de
      `aplicar_subs`
- [ ] Os seis sítios do `Database.cpp` saem com o statement fora do comentário
- [ ] `python3 wte/tools/port_database_pas.py --check` verde; rodar duas vezes dá
      bytes iguais
- [ ] `python3 -m unittest discover -s wte/tools -p 'test_*.py'` verde, com os
      três testes novos
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
