---
id: LOOKS-TASK-03
title: "`iso_source.py` e `layout.py` — a fachada de disco e o monopólio de endereço"
type: implementação
category: núcleo
phase: 1
depends_on: ["LOOKS-TASK-02"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §3.1"
status: concluído
---

# LOOKS-TASK-03: A fachada de disco e o monopólio de endereço

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §3.1, §3.2
  e §3.3 (regra 1).
- **Nada de leitor de ISO é escrito aqui.** `tools/pes2/iso.py` já lê a imagem
  japonesa nesta máquina, inclusive no Windows; esta task o **embrulha**, não o
  duplica.
- A regra 1 do ciclo — só `layout.py` carrega endereço — é o que permite mover
  um offset depois sem caçá-lo pela árvore.
- **`tools/looks/layout.py` já existe, e esta task o estende — não o cria.** A
  [`LOOKS-TASK-02`](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md) o abriu
  em 2026-09-14 para plantar a guarda dos dois discos, porque a regra da §4.5
  do plano precisava existir como código antes de qualquer leitura de textura.
  O que está lá hoje: os nomes das duas variáveis de ambiente, os quatro
  caminhos de dentro do ISO como constante, o sha256 de cada um como lido do
  disco japonês, a exceção `WrongDisc`, `require()`, o `_hint_for()` que dá
  a cada família de arquivo a sua mensagem, e um `self_check()` com **quatro**
  casos vermelhos — o quarto varre o `DIGEST` inteiro e exige dica para todo
  caminho medido ([`CORR-LOOKS-006`](/docs/tasks/looks/CORR-LOOKS-006.md)). **Nenhum LBA, nenhum `BASE`, nenhum 157.164** — esses
  são desta task.
- **O `_check_discs()` do `layout.py` é dívida desta task.** Ele importa
  `tools/pes2/iso.py` direto, com um comentário dizendo que é temporário,
  porque a fachada de disco é justamente o `iso_source.py` que esta task
  escreve. Ao criar o `iso_source.py`, **mova a leitura para trás dele** e
  deixe o `layout.py` sem I/O nenhum, que é o contrato dele (ele não sabe
  formato, e o `self_check()` roda sem imagem).

---

## Objetivo

`tools/looks/iso_source.py` entrega bytes de arquivo do disco;
`tools/looks/layout.py` é o **único** módulo que sabe LBA, `BASE` e offset.

---

## Critério de conclusão

- [x] `iso_source.py` abre a imagem por `tools/pes2/iso.py` e entrega
      `/BIN/EDT_MOD.BIN`, `/BIN/MODEL.BIN` e `/BIN/DAT2D.BIN`.
- [x] **Toda leitura de arquivo do disco no `iso_source.py` passa por
      `layout.require()`** — não é opção do chamador. Um arquivo cujo digest
      não bate não chega a virar bytes na mão de ninguém. Sem este item a 03
      fecha deixando a guarda da LOOKS-TASK-02 completa, testada e
      **inalcançável** — o único chamador dela hoje é o `_check_discs()`, que
      esta mesma task manda mover.
- [x] **Caso vermelho vivo:** ler `/BIN/DAT2D.BIN` do disco **inglês** pelo
      `iso_source.py` levanta `WrongDisc`, e o teste exige isso. É o mesmo
      estímulo do `--check-discs`, agora pelo caminho que o resto do projeto
      usa.
- [x] Se algum ponto legítimo precisar dos bytes sem conferência — comparar
      dois discos, que é o que o `--check-discs` faz —, que seja função
      **nomeada e separada** (`read_unchecked()` ou equivalente), para o
      desvio aparecer no `grep`.
- [x] `layout.py` carrega, e é o único a carregar: os LBAs (5000, 8100, 5300),
      os dois `BASE` (`0x8011C000`, `0x8016E800`), o início de geometria do
      `MODEL.BIN` (1816) e o offset dos registros de jogador (157.164).
      **Acrescentados ao que a LOOKS-TASK-02 já pôs lá**, sem apagar a guarda
      dos discos nem os quatro casos vermelhos dela.
- [x] O `layout.py` fica **sem I/O**: o `_check_discs()` que hoje importa
      `tools/pes2/iso.py` direto passa a ler pelo `iso_source.py`. **A
      ressalva do docstring de topo sai junto com a função** — ele hoje diz
      "no I/O com uma exceção, e a exceção é datada"; movida a leitura, a
      afirmação volta a valer para o arquivo inteiro
      ([`CORR-LOOKS-007`](/docs/tasks/looks/CORR-LOOKS-007.md)).
- [x] Os dois `BASE` são **derivados do cabeçalho e conferidos** contra a
      constante, não apenas cravados — é o método que a §1.2 usa.
- [x] Varredura mecânica: nenhum endereço fora de `layout.py`.
- [x] `self_check()` em cada um, com caso vermelho.

---

## Log de Execução

**Executado em:** 2026-09-14

### Resumo do que foi feito

`tools/looks/iso_source.py` nasceu como a **única porta de leitura de disco** do
projeto, e o `layout.py` ganhou os endereços mais a derivação do `BASE`. As duas
dívidas que a LOOKS-TASK-02 deixou escritas aqui foram quitadas: o
`_check_discs()` saiu do `layout.py`, e o docstring voltou a poder afirmar
"nenhum I/O" sobre o arquivo inteiro.

Quatro coisas que a execução ensinou.

**1. A guarda ficou obrigatória por construção, não por disciplina.** O `Disc`
**não herda** de `iso.Image` de propósito: herdar exporia o `read_file()` sem
conferência sob o nome que a leitura conferida quer, e a única coisa que esta
classe existe para tornar impossível é a leitura desatenta. Quem precisa dos
bytes crus chama `read_unchecked()`, e o nome é o ponto — `grep -rn
read_unchecked tools/looks` lista todo desvio, o que um argumento opcional do
`read()` não daria.

**2. O par verde/vermelho precisa das duas metades.** O caso vermelho do
`iso_source.py --check` é a leitura conferida recusando; o caso **verde** que o
acompanha é a `read_unchecked()` **devolvendo** os mesmos bytes. Sem o segundo,
o dia em que as duas passarem a recusar — por um bug de leitura, não de guarda —
o vermelho continua vermelho e deixa de medir o que diz medir. O
`--check-discs` faz o mesmo contra disco real: a cada recusa, exige que a
`read_unchecked()` entregue o arquivo (81.124 B no `DAT2D.BIN`), que é o que
torna a recusa uma **decisão** e não uma falha de leitura disfarçada.

**3. O `BASE` sai de uma regra só, e ela vale para os dois arquivos apesar de
cabeçalhos de tamanhos muito diferentes.** Os dois abrem com uma corrida de
ponteiros KSEG0, que termina no primeiro word que não é ponteiro (uma contagem,
ou o `0x000000FF`). O menor ponteiro dessa corrida aponta para o primeiro byte
**depois** dela, que é onde a lista de registros começa. Logo:

```
base = min(ponteiros do cabeçalho) - 4 * (palavras de cabeçalho)
```

Medido:

```
/BIN/EDT_MOD.BIN     header= 2 palavras  derivado=0x8011C000  constante=0x8011C000  bate
/BIN/MODEL.BIN       header=18 palavras  derivado=0x8016E800  constante=0x8016E800  bate
```

O 2 e o 18 não são chute: o `lzss.py -v` reporta os mesmos comprimentos de
cabeçalho para estes arquivos, por leitura própria — **segunda testemunha** de
onde a corrida termina.

Os dois blocos acima são saída de um script desta execução, que **não ficou** — e
era esse o defeito. Desde a
[`CORR-LOOKS-008`](/docs/tasks/looks/CORR-LOOKS-008.md) quem deriva as duas
bases sobre os arquivos reais, nos dois discos e a cada corrida, é o
`iso_source.py --check-discs`, junto com os números do item 4 abaixo.

**4. E a armadilha desse método: não rodar a derivação sobre o arquivo inteiro.**
Dado de vértice e de cor está cheio de word com o bit alto ligado. Medido nesta
corrida: **642** deles no `EDT_MOD.BIN` e **1.703** no `MODEL.BIN`, dos quais só
24 e 240 caem dentro do arquivo sob o `BASE` certo — os alvos dos demais chegam a
2,1 bilhões. Ler isso como tabela de endereço dá um `BASE` que não quer dizer
nada. A corrida do cabeçalho é segura justamente porque **para** no primeiro
não-ponteiro. O `derive_base()` carrega essa advertência no próprio docstring, e
faz o cross-check que fecha a resposta: sob o `BASE` derivado, **todo** ponteiro
do cabeçalho tem de cair dentro do arquivo — e cai, nos dois (alvos de 8 a 112
no `EDT_MOD.BIN`, de 72 a 1.712 no `MODEL.BIN`).

### A varredura da regra 1, e o marcador que se lia ao contrário

O `layout.py --sweep` confere a regra 1 em vez de prometê-la: varre
`tools/looks/` por literal hexadecimal e por decimal de quatro dígitos ou mais
fora do `layout.py`. Rodou vermelho de primeira, com três linhas — e as três
eram **falso positivo legítimo** do `superpack_count.py`: dois tamanhos de
arquivo sintético num teste e o divisor `1024 ** 3`.

Isso obrigou a escolher entre excluir o arquivo por nome e dar-lhe um escape.
Excluir por nome é como regra decai, então o escape: uma linha com
`# not-an-address: <razão>` sai da conta. **A primeira grafia era
`# address:`** — e ela se lê como *"isto é um endereço"*, que é o contrário do
que o anotador quer dizer. Escape que se lê ao contrário é escape usado errado,
então virou `# not-an-address:` antes de qualquer linha o usar.

Segunda lição do mesmo lugar: **o escape é por linha**. A anotação escrita na
linha **de cima** não isentou nada, e o `--sweep` continuou vermelho até ela
virar comentário de fim de linha.

### Medições

```
$ python tools/looks/layout.py --check
layout: self_check ok
$ python tools/looks/iso_source.py --check
iso_source: self_check ok
$ python tools/looks/layout.py --sweep
layout --sweep: no address outside layout.py

$ python tools/looks/iso_source.py --check-discs roms/japanese-shift-jis.bin C:/games/ps1/work/we2002-english.bin
Japanese disc -- everything must be accepted
  accepted /BIN/DAT2D.BIN
  accepted /BIN/EDT_MOD.BIN
  accepted /BIN/MODEL.BIN
  accepted /SELECT.BIN
English disc -- geometry accepted, the Japanese-only files refused
  refused  /BIN/DAT2D.BIN       (wanted refused) ok
  accepted /BIN/EDT_MOD.BIN     (wanted accepted) ok
  accepted /BIN/MODEL.BIN       (wanted accepted) ok
  refused  /SELECT.BIN          (wanted refused) ok
iso_source --check-discs: ok
```

O caso vermelho vivo que o critério pede, pelo caminho que o resto do projeto
usa — `Disc.read()` sobre o disco inglês:

```
/BIN/DAT2D.BIN: read 4a4d6a4f… from …we2002-english.bin, expected 0e914e58….
  /BIN/DAT2D.BIN differs between the Japanese original and the English
  translation patch, and textures and palettes may only be read from the
  Japanese one.  Point WE2002_LOOKS_IMAGE at it; WE2002_LOOKS_DRIVE_IMAGE is
  the disc you drive, not the disc you read.
--- read_unchecked devolve 81124 bytes, o que torna a recusa uma decisao
```

Os endereços que entraram no `layout.py`, todos remedidos nesta corrida contra
`roms/japanese-shift-jis.bin`:

| o quê | valor |
| --- | --- |
| LBA / tamanho | `EDT_MOD` 5000/36.072 · `MODEL` 8100/64.800 · `DAT2D` 5300/81.124 · `SELECT` 850/300.648 |
| `BASE` | `EDT_MOD` `0x8011C000` · `MODEL` `0x8016E800` |
| início da geometria do `MODEL.BIN` | 1.816 — e lá se lê `nVert=107 nPrim=88`, que é o que o `we3d` reporta para a seção 0 |
| registros de jogador | `/SELECT.BIN` +157.164, 1.242 × 12 B = 14.904 B, terminando em 172.068, dentro dos 300.648 |

O `self_check()` do `layout.py` foi de quatro para **sete** casos vermelhos, e
ganhou também uma varredura de coerência entre as tabelas: todo caminho com
digest tem de ter LBA e tamanho, e `set(BASE)` tem de ser exatamente os arquivos
de geometria. É a mesma forma da varredura de dicas da
[`CORR-LOOKS-006`](/docs/tasks/looks/CORR-LOOKS-006.md) — a falha que ela fecha é
por **omissão**, e omissão nenhum caso de propriedade pega.

### Arquivos criados/modificados

- `tools/looks/iso_source.py` — **novo**. `Disc` (com `read()` conferido e
  `read_unchecked()` nomeado), `open_disc()`, `read_file()`, `image_from_env()`,
  `self_check()` com leitor de mentira e o `--check-discs` vivo
- `tools/looks/layout.py` — `LBA`, `SIZE`, `BASE`, `MODEL_GEOMETRY_START`, os
  três `PLAYER_RECORD_*`, `WrongBase`, `derive_base()`, `require_base()`,
  `sweep_addresses()` + `--sweep`; saiu o `_check_discs()` e com ele a ressalva
  de I/O do docstring
- `tools/looks/superpack_count.py` — três `# not-an-address:` nas linhas que o
  `--sweep` acusou
- `docs/PLAN-LOOKS-PY.md` — §1.3 e §4.5 (o `--check-discs` mudou de módulo; o
  `--sweep` e o `iso_source.py --check` entraram na lista de comandos; o nome
  real da saída é `Disc.read_unchecked()`)
- `docs/tasks/looks/03-fonte-de-disco-e-layout.md` — este arquivo

### Problemas encontrados

Dois, e nenhum bloqueou.

**Os vetores sintéticos do `derive_base()` nasceram curtos demais.** O caso
**verde** tinha 72 bytes e um ponteiro mirando o offset 112, então ele tropeçava
na conferência de alcance que o caso vermelho 5 existe para demonstrar — teste
verde falhando pelo motivo do vermelho. Alargados para 520 bytes. E o vermelho 7
partia de `outside[:4]`, que deriva **o mesmo** `BASE` da constante e portanto
nunca levantaria: virou um cabeçalho que declara outra base (`0x80200000`), com
um `assert` provando que ele de fato deriva outra coisa antes de exigir a
recusa.

**O `tools/pes2/selftest.py` não roda nesta máquina**, e é anterior a esta task:
ele lê `/proc/self/fd` para caçar descritor vazado, e isso não existe no Windows
(`FileNotFoundError: [WinError 3] … '/proc/self/fd'`). `git diff HEAD --
tools/pes2/` sai vazio — nada aqui tocou aquele projeto. Fica **registrado como
achado**, não consertado: é do ciclo de PES2, e o perfil deste ciclo só exige o
`pes2_selftest` verde se a task mexer no `bin_archive.py`, o que não é o caso.
