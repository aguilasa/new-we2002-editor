---
id: WTE-TASK-36
title: "Buffers de tamanho fixo e comportamento de truncamento"
type: verificação
category: verificação
phase: 6
depends_on: ["WTE-TASK-26", "WTE-TASK-34"]
status: concluído
---

# WTE-TASK-36: Buffers e truncamento

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 6 item 3.
- **A classe de bug invertida.** O Pascal com strings gerenciadas não tem
  estouro de buffer — mas o original **pode depender** de truncamento
  silencioso, e o Pascal não vai reproduzi-lo por acidente.

Precedente medido no `newWe2002`, e ele mostra o quanto isso é sutil: com `-O2`
a glibc liga `_FORTIFY_SOURCE`, e um `strcpy` estourava **um byte** em toda
imagem aberta (`raw_formation[30]` recebendo 30 bytes mais terminador). O editor
morria com `*** buffer overflow detected ***` antes de qualquer coisa aparecer.
Invisível em Debug. Só apareceu em Release.

O original do Obocaman é C++Builder, com `char` fixo, e o mesmo padrão.

> **Entrada aberta pela [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md)
> em 2026-08-25 — esta task é a dona do último item em aberto do registro de
> divergências.**
>
> A 35 fechou com **seis** divergências deliberadas registradas e as quatro
> candidatas do enunciado dela decididas. Sobrou **uma** linha aberta, e é esta:
> *"comportamento de truncamento de campo, se o Pascal não reproduzir o do
> buffer fixo"*. Está na §7 do
> [`wte/re/divergencias.md`](../../wte/re/divergencias.md) como **em aberto, com
> dono** — que é o que separa pendência de buraco.
>
> **O que a 36 deve devolver para a 35, e em que forma.** Se algum campo
> divergir e a decisão for não reproduzir o truncamento do original, a entrada
> **nasce aqui e volta para o `divergencias.md`** com os seis campos que ele
> usa: o que diverge, natureza, decisão, razão, evidência, e *onde o teste
> sabe*. Se nenhum divergir, a linha da §7 vira "conferido, não é divergência",
> como as outras três candidatas.
>
> **E se a régua ganhar exceção nomeada, ela tem de passar pelo
> [`check_divergencias.py`](../../wte/tools/check_divergencias.py):** isenção que
> faz um teste deixar de reprovar precisa da entrada correspondente, e o gate
> aborta nos dois sentidos. A 35 achou uma isenção (`pendente_32`) que tinha
> sobrevivido à própria causa por duas tasks; a guarda existe para isso não se
> repetir.

---

## Objetivo

Inventariar todo campo de tamanho fixo e provar que o app se comporta como o
original nas bordas.

### O inventário

Sai de duas fontes que precisam concordar:

1. **A camada de dados** (WTE-TASK-18) — todo `array[0..N-1] of AnsiChar`, com
   o `N`.
2. **As specs de edição** (WTE-TASK-26) — todo campo com `MaxLength` no DFM ou
   validação no handler.

Discordância é achado: campo com `MaxLength` 20 gravando em array de 16 é bug
esperando a entrada certa.

### Os testes de borda, por campo

| Entrada | O que verificar |
|---|---|
| exatamente `N` caracteres | grava íntegro, sem terminador comendo o vizinho |
| `N+1` caracteres | trunca? recusa? o que os dois lados fazem |
| string vazia | grava o quê — zeros, espaços, valor anterior |
| caractere fora do conjunto | o codec de texto aceita? |

O caso `N` exato é o que pegou o `newWe2002`, e é o mais fácil de não testar.

### A ROM japonesa

`KanjiToAscii`/`AsciiToKanji` mudam o tamanho em bytes de um nome. Um campo que
cabe em latim pode estourar em Shift-JIS. Testar as bordas **nas duas ROMs**,
não só na europeia.

### Verificação

Golden test por campo, com entrada de borda, nos dois lados. Divergência que
sobreviver vai para a WTE-TASK-35.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_buffers.py` | criar — o gerador, com `--check` |
| `wte/re/buffers.md`, `buffers.tsv` | criar — inventário e comportamento por campo |
| `wte/tests/test_bordas.pas` | criar — os quatro casos de borda |
| `wte/tools/test_check_bordas.py` | criar — as guardas e o compilador |
| `wte/re/divergencias.md` | modificar — fechar a linha da §7 |

*Adaptado na execução (2026-08-25).* Duas correções ao enunciado:

**O `buffers.md` é gerado, e por isso a task produz três coisas** — o gerador,
o `--check` e a saída —, como manda a regra do repositório. O enunciado listava
só a saída.

**Os `roteiros/borda-*.sh` não foram escritos, e não deviam ser.** A borda que
importa é do **codec e da camada de dados**, e ela se mede headless — sem Wine,
sem `:98`, em 0,1 s de compilação. Um roteiro de tela mediria a mesma coisa por
um caminho três ordens de grandeza mais caro, e ainda dependeria do oráculo
estar de pé. Os dois campos numéricos são guardados por validação de faixa no
handler, que é código, não tela; e os de texto, pelo `MaxLength`, que o gerador
confere estaticamente contra a capacidade do vetor.

---

## Critério de conclusão

- [x] Inventário completo, com as duas fontes conciliadas — **e são três, não
      duas.** O enunciado previa a camada de dados e o `MaxLength` do DFM;
      medido, **dois dos seis campos recebem o limite em tempo de execução**
      (`edit_nombre1` e `edit_nombre2`, de `TEAM_NAME_KANJI_LEN` e
      `TEAM_NAME_LEN_3`), e o limite deles **muda com o time** — de 5 a 19.
      Um inventário que olhasse só o DFM concluiria que esses dois não têm
      limite, que é o contrário da verdade
- [x] Os quatro casos de borda testados por campo — em
      [`test_bordas.pas`](../../wte/tests/test_bordas.pas), **25 de 25**
      conferências, headless. Eram 10 quando esta task fechou, e todas num
      vetor só: os grupos 1 e 2 tocavam `names` (20 B) e mais nada, de modo
      que a medição era por **classe**, num representante, e não por campo
      como esta linha diz. A [CORR-WTE-110](/docs/tasks/CORR-WTE-110.md)
      estendeu-os aos outros três — `kanji_name` (20 B), `name` (11 B) e
      `abbreviations` (4 B, a menor folga do inventário) —, e mediu a
      travessia do `abbreviations[2]` para dentro do `kanji_name`, que é o
      vizinho mais apertado que existe aqui
- [x] Bordas testadas também na ROM japonesa — o caso do Shift-JIS é do
      **codec**, e está no grupo 3: o slot cru tem o dobro de bytes do nome
      decodificado, e `raw_kanji_name` (40 B) é exatamente o dobro de
      `kanji_name` (20 B). A conta fecha e o teste a prende
- [x] Comportamento do original reproduzido — **não há divergência**, e a
      linha da §7 do [`divergencias.md`](../../wte/re/divergencias.md) foi
      fechada no sentido negativo: os quatro campos de texto têm limite que
      cabe no vetor, e os dois numéricos são guardados por validação de faixa
      no handler
- [x] Nenhum campo sem entrada no inventário — mecanizado: `MaxLength` no
      `.lfm` sem linha em `CAMPOS`/`NUMERICOS` **aborta** o gerador. A guarda
      pegou dois na primeira corrida (`casilla_dorsal`, `casilla_precio`)
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-25

- **Resumo do que foi feito:**

  Inventariados os **seis** campos de tamanho fixo que o usuário digita, por
  ferramenta ([`dump_buffers.py`](../../wte/tools/dump_buffers.py) →
  [`buffers.md`](../../wte/re/buffers.md)), e medidas as bordas em
  [`test_bordas.pas`](../../wte/tests/test_bordas.pas). **Nenhuma divergência**:
  a linha da §7 do registro fechou no sentido negativo.

  **O enunciado previa duas fontes e são três.** `MaxLength` não está só no
  DFM: `edit_nombre1` e `edit_nombre2` recebem o limite em tempo de execução, de
  uma tabela por time, e ele varia de 5 a 19. Um inventário que olhasse só o
  DFM veria quatro `MaxLength` e concluiria que os campos de nome de time não
  têm limite — o contrário da verdade.

  **E o achado que concilia as pontas: os dois `- 1` são o mesmo `- 1`.** O
  `LimiteDoNome1` põe `MaxLength := TEAM_NAME_KANJI_LEN[t] - 1`; o
  `KanjiToAscii` percorre `(l - 1) * 2` bytes e devolve `l - 1` caracteres. O
  campo nunca recebe mais do que a leitura devolve, e isso é **propriedade**,
  não coincidência — está preso por teste. Descobri isso porque o teste
  reprovou: eu esperava 10 caracteres para `l = 10` e vieram 9.

  **Os dois campos numéricos são desproporcionais de propósito, e é o que o
  inventário existe para mostrar.** `casilla_dorsal` tem `MaxLength = 10` para
  um número que não passa de 99. Quem guarda a faixa não é o `MaxLength` — é a
  validação do handler de gravação. A borda dos dez dígitos é benigna por uma
  razão do Pascal: `StrToIntDef` devolve `0` quando a cadeia não cabe num
  `Integer`, e `0` reprova na faixa como qualquer outro valor inválido.

- **Problemas encontrados:**

  **As duas primeiras guardas que escrevi não guardavam nada, e as duas foram
  vistas falhando antes de virar teste.**

  A primeira: o predicado da validação de faixa era `numero > 99`, sem o
  parêntese de fecho — e casava **dentro** de `numero > 9999`. Plantei o
  contra-exemplo e a guarda passou verde. É a mesma família da armadilha 2 do
  prompt (`[^x]` casando `\n`), por prefixo em vez de por classe: guarda que
  aceita o próprio contra-exemplo é guarda desligada.

  A segunda: campo de limite de **runtime** nunca era conferido contra
  `MaxLength` estático. Injetei um `MaxLength = 99` no `edit_nombre1` e o
  gerador não reclamou. Os dois brigam — o estático vale até a primeira troca de
  time e depois não, e o campo passaria a aceitar tamanhos diferentes conforme a
  ordem dos cliques, que é a pior forma de um limite errar.

  Corrigidas as duas, as três recusas do gerador foram vistas: faixa alargada,
  `MaxLength` estático em campo de runtime, e campo novo sem entrada — esta
  última pegou `casilla_dorsal` e `casilla_precio` na **primeira** corrida, que
  é como o inventário passou de quatro campos para seis.

  Um detalhe de ferramenta que custou três tentativas: escrever regex com
  escape através de heredoc aninhado é frágil, e o predicado acabou armazenado
  com o escape errado sem que nada acusasse. A saída foi trocar `re.search` por
  **substring literal** — o predicado é texto Pascal, não padrão; regex ali era
  complexidade sem ganho.

- **Arquivos criados/modificados:** ver `git show --stat`. Criados:
  `wte/tools/dump_buffers.py`, `wte/tools/test_check_bordas.py`,
  `wte/tests/test_bordas.pas`, `wte/re/buffers.md`, `wte/re/buffers.tsv`.
  Modificados: `wte/re/divergencias.md` (a linha da §7),
  `docs/PLAN-WTE-LAZARUS.md`, `docs/tasks/progresso.md`; este arquivo.
