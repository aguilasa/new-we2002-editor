---
id: CORR-WTE-007
title: "Correção: a tabela \"onde o plano envelheceu\" atribui ao plano uma frase que só existe na task, e não registra três divergências medidas"
type: correção
category: engenharia-reversa
status: pendente
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
| `docs/tasks/30-preco-do-jogador.md:37` | `formulário ficha_creditos_equipo` na tabela de entrada da tarefa | o dono de `etiqprecioClick` é **`jugador`** — a mesma correção que a linha da §5.1 já faz, no outro arquivo que a repete |
| `docs/tasks/28-handlers-auxiliares.md:35` | `BitBtn1Click` (**3×**) | **4×** — a mesma contagem que a tabela de homônimos do próprio `.md` já traz |
| `docs/tasks/28-handlers-auxiliares.md:36-38` | `SpeedButton2Click`, `Button2Click`, `Image3Click`, `base_teamClick`, `imagen_urlClick` entre os "repetidos por vários formulários" | **uma vez cada** — o `.md` registra só o sexto da mesma lista, `botonClick` |

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
2. Acrescentar a linha de `docs/tasks/30-preco-do-jogador.md`, ao lado da que
   já existe para a §5.1 — o dono sai de `m.rows`, como a da §5.1 já faz.
3. Generalizar a linha de `botonClick`: em vez de um nome fixo, varrer a lista
   que a WTE-TASK-28 chama de "repetidos" e emitir uma linha com **todos** os
   que a contagem medida dá 1, mais `BitBtn1Click` com a contagem real. A lista
   da 28 é literal escrita à mão (é citação de outro documento), mas o veredito
   de cada nome vem de `count_by_name(m)`.

O padrão a seguir é o de `EXCEPTIONS` e `FORMULA_OWNERS`, que já abortam quando
uma chave escrita à mão não casa com handler medido: se um nome citado da 28
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

- [ ] `python3 wte/tools/dump_published.py --check` verde depois de regerar
- [ ] Rodar o gerador duas vezes dá bytes iguais (determinismo preservado)
- [ ] Toda citação da tabela nomeia um arquivo que contém a frase citada:
      `grep -n "<frase>" <arquivo>` acha
- [ ] Nome citado da WTE-TASK-28 que não exista entre os 96 faz o script
      **abortar**, testado com uma entrada plantada
- [ ] A tabela lista os seis handlers de contagem 1 e o `BitBtn1Click` com 4
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
