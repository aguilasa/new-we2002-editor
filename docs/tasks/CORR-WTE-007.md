---
id: CORR-WTE-007
title: "Correção: a tabela \"onde o plano envelheceu\" atribui ao plano uma frase que só existe na task, e não registra três divergências medidas"
type: correção
category: engenharia-reversa
status: concluído
depends_on: []
---

# CORR-WTE-007: a tabela de envelhecimento do `published_methods.md` está incompleta e erra uma atribuição

## Problema identificado

`wte/re/published_methods.md`, seção "Onde o plano e as tarefas envelheceram",
é a lista de divergências entre o medido e o texto já escrito — a entrega do
critério "discordância listada, não escondida" da
[WTE-TASK-04](/docs/tasks/04-mapa-de-handlers.md). Ela tem sete linhas. Duas
coisas estão erradas nela.

**1. Atribui ao plano uma frase que o plano não tem.** A primeira linha diz
"§1.4 do plano e WTE-TASK-04 | `FormCreate` aparece **17** vezes". O plano não
diz isso em lugar nenhum:

```
$ grep -rn "FormCreate" docs/PLAN-WTE-LAZARUS.md
228:  OnCreate = 'FormCreate'
741:(`lista_equiposChange`, `mostrar_jugadorClick`, `FormCreate` de cada
```

O "17" está em `docs/tasks/04-mapa-de-handlers.md:32` e em
`docs/prompts/02-revisar.md:113`. Mandar alguém corrigir a §1.4 faz procurar o
que não existe, e deixa de fora o arquivo que realmente carrega o número — o
prompt de revisão, que reprovaria um `dfm2lfm.py` correto na fase 2.

**2. Três divergências medidas ficaram de fora**, todas do mesmo tipo das sete
que entraram:

| Onde | Diz | Medido |
|---|---|---|
| `docs/tasks/32-preco-do-jogador.md:37` | `formulário ficha_creditos_equipo` na tabela de entrada da tarefa | o dono de `etiqprecioClick` é **`jugador`** — a mesma correção que a linha da §5.1 já faz, no outro arquivo que a repete |
| `docs/tasks/30-handlers-auxiliares.md:35` | `BitBtn1Click` (**3×**) | **4×** — a mesma contagem que a tabela de homônimos do próprio `.md` já traz |
| `docs/tasks/30-handlers-auxiliares.md:36-38` | `SpeedButton2Click`, `Button2Click`, `Image3Click`, `base_teamClick`, `imagen_urlClick` entre os "repetidos por vários formulários" | **uma vez cada** — o `.md` registra só o sexto da mesma lista, `botonClick` |

A terceira é a que mostra o padrão: a linha de `botonClick` foi escrita à mão
para um caso, quando a mesma consulta responde pelos seis.

## Evidência

Contagem por nome, do `wte/re/published_methods.tsv` gerado:

```
BitBtn1Click         4  ficha_dorsal ficha_color jugador estrategia
SpeedButton2Click    1  MainForm
Button2Click         1  MainForm
Image3Click          1  MainForm
botonClick           1  ficha_color
base_teamClick       1  MainForm
imagen_urlClick      1  ficha_about
```

O `.md` já sabe disso — a seção "Homônimos" dele lista `BitBtn1Click | 4`. A
tabela de envelhecimento, três seções abaixo, continua confrontando o texto da
28 só onde alguém digitou o confronto.

Origem do "17", que a tabela dá ao plano:

```
$ grep -rn "17 vezes" docs/
docs/tasks/04-mapa-de-handlers.md:32:...`FormCreate` aparece 17 vezes...
docs/prompts/02-revisar.md:113:  usada? `FormCreate` aparece 17 vezes
```

## Causa raiz

A tabela é meia-gerada: o lado "Medido" é calculado, o lado "Diz" é literal
escrito à mão em `render_md()`, e nada confere que a citação existe no arquivo
citado nem que a lista de confrontos está completa.

## Correção

`wte/re/published_methods.md` é **gerado** — a correção entra no gerador.

### Arquivo: `wte/tools/dump_published.py`

Em `render_md()`, na tabela "Onde o plano e as tarefas envelheceram"
(linhas 1166-1196):

1. Trocar a atribuição da primeira linha: de `§1.4 do plano e WTE-TASK-04` para
   `WTE-TASK-04 e docs/prompts/02-revisar.md`, que são os arquivos onde o "17"
   está escrito.
2. Acrescentar a linha de `docs/tasks/32-preco-do-jogador.md`, ao lado da que
   já existe para a §5.1 — o dono sai de `m.rows`, como a da §5.1 já faz.
3. Generalizar a linha de `botonClick`: em vez de um nome fixo, varrer a lista
   que a WTE-TASK-30 chama de "repetidos" e emitir uma linha com **todos** os
   que a contagem medida dá 1, mais `BitBtn1Click` com a contagem real. A lista
   da 30 é literal escrita à mão (é citação de outro documento), mas o veredito
   de cada nome vem de `count_by_name(m)`.

O padrão a seguir é o de `EXCEPTIONS` e `FORMULA_OWNERS`, que já abortam quando
uma chave escrita à mão não casa com handler medido: se um nome citado da 30
deixar de existir no binário, o script deve **falhar**, não emitir uma linha
sobre um handler que não existe.

### Arquivo: `wte/re/published_methods.md`

Regerado, não editado — `python3 wte/tools/dump_published.py`.

**Relação com a [CORR-WTE-006](/docs/tasks/CORR-WTE-006.md):** a 006 conserta os
documentos citados; esta conserta a lista que os cita. Ordem indiferente, mas
depois das duas a tabela passa a registrar divergência que **não existe mais** —
é o mesmo destino das outras sete, e a WTE-TASK-09 é quem decide se a seção
inteira vira histórico ao fechar a fase 1.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_published.py` | modificar |
| `wte/re/published_methods.md` | regerar (nunca editar à mão) |

## Verificação

- [x] `python3 wte/tools/dump_published.py --check` verde depois de regerar
- [x] Rodar o gerador duas vezes dá bytes iguais (determinismo preservado)
- [~] Toda citação da tabela nomeia um arquivo que contém a frase citada:
      `grep -n "<frase>" <arquivo>` acha — **não é mais satisfazível**, e a
      razão está no Log: a CORR-WTE-006 corrigiu os arquivos citados antes
      desta correção rodar. A coluna **Diz** virou registro do que foi
      consertado, e a seção passou a dizer isso em vez de fingir que a citação
      ainda se lê lá. A atribuição, que era o defeito de verdade, aponta agora
      para os arquivos que **carregavam** a frase
- [x] Nome citado da WTE-TASK-30 que não exista entre os 96 faz o script
      **abortar**, testado com uma entrada plantada
- [x] A tabela lista os seis handlers de contagem 1 e o `BitBtn1Click` com 4
- [x] `make -C wte check` verde
- [x] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-06

**Resumo do que foi feito:**

Três mudanças em `render_md()`, nenhuma no `.md` à mão:

1. A atribuição da primeira linha saiu de `§1.4 do plano e WTE-TASK-04` para
   `WTE-TASK-04 e docs/prompts/02-revisar.md` — os dois arquivos que de fato
   carregavam o "17". O plano não contém a frase.
2. A linha da `WTE-TASK-32` entrou ao lado da da §5.1: os dois documentos
   repetem o mesmo erro de dono, e o valor sai de `m.rows` nas duas.
3. A linha escrita à mão para `botonClick` virou uma varredura sobre
   `TASK30_REPEATED`, os dez nomes que a WTE-TASK-30 chama de "repetidos". A
   lista é literal (é citação de outro documento), mas o veredito de cada nome
   vem de `count_by_name()`: seis dão 1 e saem numa linha só, com o formulário
   de cada um, e o `BitBtn1Click` ganhou linha própria com a contagem real.

Como em `EXCEPTIONS` e `FORMULA_OWNERS`, um nome citado que não exista entre os
96 **aborta** em vez de gerar linha sobre handler inexistente. Testado com
`NaoExisteClick` plantado: `rc=2` e a mensagem nomeando o nome morto.

**Problemas encontrados:**

O critério "toda citação nomeia um arquivo que contém a frase citada" deixou de
ser satisfazível no meio do lote, e não por defeito desta correção: a
[CORR-WTE-006](/docs/tasks/CORR-WTE-006.md) rodou antes e consertou os seis
arquivos citados. Qualquer ordem daria o mesmo — as duas correções tratam os
dois lados da mesma citação. A saída foi enquadrar a seção em vez de fingir: um
parágrafo novo diz que a coluna **Diz** cita o texto como ele estava quando a
WTE-TASK-04 mediu, que a CORR-WTE-006 propagou as linhas, e que a WTE-TASK-09 é
quem decide se a seção inteira vira histórico ao fechar a fase 1. O defeito real
que a CORR aponta — a atribuição a um arquivo que nunca teve a frase — está
consertado, e é o que sobrevive à propagação.

A varredura achou a mesma má-atribuição fora do gerador: o Log da WTE-TASK-04
dizia "§1.4 do plano e esta tarefa dizem `FormCreate` 17 vezes". A CORR-WTE-006
deixou o Log de fora por ser histórico, mas histórico errado sobre qual arquivo
dizia o quê continua mandando alguém procurar o que não existe — a linha passou
a nomear os arquivos certos, marcando a atribuição original como corrigida.

O link que escrevi no parágrafo novo saiu como `/docs/tasks/...`. Errado:
`.claude/rules/links.md` restringe essa forma a markdown **dentro** de `docs/`,
e `wte/re/published_methods.md` está fora — os vizinhos dele usam
`../../docs/tasks/`. Corrigido no gerador antes do commit.

**Arquivos criados/modificados:**

- `wte/tools/dump_published.py` — `TASK30_REPEATED`, a guarda de nome morto e a
  tabela de envelhecimento em `render_md()`
- `wte/re/published_methods.md` — regerado
- `docs/tasks/04-mapa-de-handlers.md` — a mesma má-atribuição no Log
- `docs/tasks/correcoes-progresso.md`
