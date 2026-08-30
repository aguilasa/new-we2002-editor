# PES2 — ajustes pendentes

> Revisão de [/docs/PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md), de
> [/docs/PES2-NOMES.md](/docs/PES2-NOMES.md) e dos três commits que os
> acompanham (`934ef1f`, `d345a0e`, `35a6d92`), feita em **2026-08-30**.
>
> **Executada no mesmo dia.** Todos os itens de §1 a §4 estão feitos, e
> dois dos quatro de §5. Os outros dois não são trabalho de código e
> viraram a §7 — que, enquanto PES2 estiver fora do `progresso.md`, **é o
> backlog do projeto**.
>
> **O que estava certo, e vale dizer antes:** a Fase 0 é real. O
> `roundtrip` do `iso.py` foi executado nesta revisão sobre o Track 1
> `(EsIt)` e saiu **`ROUND-TRIP OK: image is byte-identical`**, com
> 244 arquivos reescritos e 8 pulados na classificação prevista
> (1 `form2`, 7 `outside`). Os oito marcadores da §1.13 resolvem nas
> **duas** releases, cada um uma única vez, e os offsets batem com a
> tabela da §1.12 byte a byte. As contagens da §1.6 foram reconferidas
> contra o disco: **106** nomes de time, **95** abreviações, **463**
> registros de 10 B. Nada do que o plano afirma como medido saiu errado —
> com duas exceções que a execução encontrou e que estão em §6.

---

## O que ficou no repositório

| Arquivo | O que resolve |
|---|---|
| `tools/pes2/tables.py` | §2.1 — as onze tabelas de texto, com contagem, digest e regra de fim |
| `tools/pes2/diff_releases.py` | §2.2 — o diff entre releases, e `docs/samples/pes2-diff-releases.md` |
| `tools/pes2/memcard.py` | §2.3 — o alinhamento de cartão, as 54 fronteiras de elenco |
| `tools/pes2/faq_check.py` | §2.4 — `PES2-NOMES.md` contra o disco e contra os dois FAQs |
| `tools/pes2/iso.py negative` | §2.5 — o controle negativo, agora comando |
| `tools/pes2/selftest.py` | §2.6 — disco sintético de 24 setores; `ctest -R pes2_selftest` |
| `tools/pes2/check_image.py` | §2.6 — tudo que precisa de imagem; `ctest -R pes2_image` |
| `tools/pes2/boot_check.sh` | §2.7 — a evidência de boot, medida em vez de lembrada |

---

## 1. Defeitos de código

### 1.1 `run_duckstation.sh --kill` cria uma árvore fora do repositório

- [x] **Só resolver `DATA` e criar diretório depois de tratar `--kill`,
      e exigir `PES2_IMAGE` antes de qualquer `mkdir`.**

Medido. Com `PES2_IMAGE` vazio, a linha 18 faz
`DATA="$(dirname "")/../ds-data"` = `./../ds-data`, e as linhas 30–86
rodam **antes** do `if [ "$1" = "--kill" ]` da linha 136. Executando
`tools/pes2/run_duckstation.sh --kill` de dentro de `/tmp/killtest/sub`
apareceu:

```
/tmp/killtest/ds-data/duckstation/settings.ini
/tmp/killtest/ds-data/duckstation/bios -> ~/.local/share/duckstation/bios
/tmp/killtest/ds-data/duckstation/{memcards,savestates,screenshots,cache}
```

Isto é, o `--kill` — que só deveria matar processo — escreve uma
configuração inteira **no diretório-pai do CWD**. Rodado da raiz deste
repositório, ele cria `../ds-data` ao lado do repositório, em silêncio.

### 1.2 O default de `PES2_DATA` não é o que o cabeçalho promete

- [x] **Alinhar código e comentário, e usar caminho absoluto.**

O cabeçalho (linha 10) diz `default <scratch>/ds-data`; o código (linha
18) usa `$(dirname "$IMAGE")/../ds-data`, que é relativo ao **caminho da
imagem**, não ao scratchpad, e contém um `..` que muda de significado
conforme o `PES2_IMAGE` seja absoluto ou relativo.

### 1.3 O link do BIOS pode ficar pendurado sem ninguém notar

- [x] **Conferir `~/.local/share/duckstation/bios` antes do `ln -sfn`, e
      falhar alto se não existir.**

`ln -sfn` cria o link mesmo com alvo inexistente. O sintoma seria o
DuckStation não achar BIOS nenhuma e morrer na carga — longe da causa,
que é exatamente o tipo de armadilha que a §6.11 do plano cataloga.

### 1.4 `write_file` não é atômico

- [x] **Validar `status(path) == "form1"` antes do primeiro
      `write_sector`, em vez de descobrir no meio.**

[`iso.py:224`](../tools/pes2/iso.py) grava setor a setor e confia no
`Form2Sector`/`OutsideTrack` que o `write_sector` levanta. Num arquivo
misto, os setores anteriores ao problemático **já foram gravados** quando
a exceção sobe, e o `inject` deixa o arquivo pela metade. Hoje nenhum dos
244 `form1` é misto, então o defeito é latente — mas o `inject` é a
ferramenta do ciclo de `poke`, e ela vai operar sobre cópia de 445 MiB.

### 1.5 Detalhes menores

- [x] `Image.__init__` abre o arquivo e só depois chama
      `_read_filesystem()`; se este levantar, o descritor vaza.
- [x] O docstring do `faq2md.py` documenta dois argumentos
      (`ENTRADA.txt SAIDA.md`), mas o `__main__` aceita um terceiro
      opcional (o título) — que é o que o `.gitignore` manda usar ao
      reconverter. Sem `argparse`, faltar argumento dá `IndexError`.

---

## 2. Lacunas de verificação

O `CLAUDE.md` deste repositório diz, sobre os golden: *"verde de golden é
asserção sobre um estímulo: sem o estímulo versionado a corrida não é
repetível, e o par verde+faixa vira lembrança."* A regra vale igual aqui,
e hoje **só o `roundtrip` a cumpre**.

- [x] **Versionar a ferramenta que produziu as medições da §1.6.** As
      contagens (106 / 95 / 99 / 1.399 / 463) e a ordem canônica saíram de
      uma varredura que não está no repositório. Reconferi todas nesta
      revisão e batem — mas com script escrito na hora, que também se
      perdeu. Deveria ser um `tools/pes2/tables.py` que imprime a
      contagem, o offset e as primeiras/últimas entradas de cada tabela.
- [x] **Versionar o diff entre releases da §1.12.** Os números (236 em
      comum, 204 idênticos, 32 diferem) não têm como ser reproduzidos.
- [x] **Versionar a análise de memory card da §3.3.** É a medição mais
      valiosa do plano — as 54 fronteiras de elenco, 49 em `SELECTC.BIN`
      invertidos e 2 em `SLES_039.57` diretos — e é a que menos rastro
      deixou. A Fase 3 depende dela.
- [x] **Versionar o alinhamento FAQ × disco** que sustenta o "30 dos 32"
      da [/docs/PES2-NOMES.md](/docs/PES2-NOMES.md). Os FAQs não entram no
      git, mas o **script** que os lê entra, e é ele que torna a
      verificação repetível quando o usuário baixá-los de novo.
- [x] **Versionar o controle negativo da §5.1.** Trocar o `P` de
      `PIEMONTE` por `X` e conferir que muda exatamente um byte, no
      offset absoluto 2002800, é a prova de que a guarda sabe ficar
      vermelha. Hoje é prosa.
- [x] **Registrar `iso.py` no `ctest`.** Nenhum teste do
      [tests/CMakeLists.txt](../tests/CMakeLists.txt) conhece `pes2`. Dois
      são viáveis: um sobre imagem **sintética** de poucos setores
      (aritmética de setor, Form 1 × Form 2, `outside`, recusa de mudar
      tamanho) que roda sempre; e um `pes2_anchors`, condicionado a uma
      variável `WE2002_PES2_IMAGE` e reportado como *skipped* sem ela,
      como já se faz com `WE2002_TEST_IMAGE`.
- [x] **Deixar evidência do boot da §3.4.** O commit `35a6d92` afirma que
      o jogo chega à tela-título no `:98`; não há screenshot nem log
      versionado, e não há script de direção — só as instruções que o
      `run_duckstation.sh` imprime no fim.

---

## 3. Inconsistências entre o plano e o que foi medido

- [x] **Cabeçalho do plano ainda diz "`plano. Nenhuma fase executada.`"**
      (linha 16). A Fase 0 está feita e verde. É a primeira linha que
      alguém lê.
- [x] **A §7 diz que a Fase 0 está "feito, **menos o emulador**"; a §5
      diz que o emulador está feito.** As duas se contradizem no mesmo
      documento.
- [x] **"Sete marcadores" (§1.13) × "os oito marcadores" (§5.1).** O
      código tem oito, e o oitavo — `Oranges001` em `SELECT.BIN` — **não
      aparece na tabela da §1.13**. Acrescentá-lo.
- [x] **A §1.5 põe a cópia em caixa mista de `RESULT.BIN` em `@~304`.**
      Medido agora, e coerente com a própria §1.12: é **524** em `(EsIt)`
      e **632** em `(EnFrDe)`. O `~304` está errado nas duas.
- [x] **A §1.5 diz que os nomes de jogador estão em `SELECTC.BIN`
      @20736; a §1.6 diz 17604.** Os dois números existem — 17604 é o
      início do bloco (os fictícios) e 20736 é onde começam os reais —,
      mas o texto não deixa isso claro, e um mapa construído a partir da
      §1.5 perde a primeira família inteira.
- [x] **A tabela de cópias da §1.5 omite a cópia em caixa mista de
      `SELECTC.BIN` @16576**, que a §1.6 lista com 99 entradas. Como a
      §6.1 é justamente "uma cópia gravada é pior que nenhuma", a lista de
      cópias é o pior lugar do documento para faltar uma linha.

---

## 4. Fatos medidos nesta revisão que ainda não estão escritos

- [x] **A âncora `Oranges001` não marca o início da tabela que ela
      ancora.** Ela resolve em **7060** nas duas releases, e a tabela de
      10 B começa em **5320** — é o registro de índice **174**, não o 0.
      O delta é **−1740**, e é constante entre as releases. O mapa da
      Fase 5 tem de guardar delta **assinado**, e este caso é o primeiro
      exemplo de que o marcador pode cair no meio.
- [x] **Não há folga nenhuma entre a tabela de nomes e a de
      abreviações.** Medido: os 106 nomes ocupam de 3128 a **4292**, e
      4292 é exatamente onde `PTA\0` começa. No disco lê-se
      `EURO ALLSTARS\0\0\0PTA\0` corrido. A §6.2 já manda truncar em vez
      de deslocar; vale registrar que a margem é **zero byte**, e que
      escrever um 107º nome invade a primeira abreviação.
- [x] **Nenhuma das tabelas tem sentinela de fim.** O que separa uma da
      seguinte é só a contagem. Consequência para a Fase 5: o mapa
      precisa declarar **contagem** por tabela, não apenas âncora e
      esquema de registro — hoje a §1.13 só prevê
      `(arquivo, marcador, deslocamento)`.

---

## 5. Integração com o resto do repositório

> `[x]` feito, `[→]` não é trabalho de código e segue vivo na §7.1.

- [x] **O `CLAUDE.md` não sabe que este projeto existe.** Não há menção a
      PES2, a `docs/PLAN-PES2-PSX.md` nem a `tools/pes2/`. Os outros três
      projetos (`newWe2002`, `wte/`, e os planos de Windows) todos têm
      parágrafo lá.
- [x] **O `CLAUDE.md` ainda diz, sem ressalva, `Pro Evolution Soccer 2
      (Europe) (EnFrDe) — NÃO USAR`** (linha 523). A §1.1 do plano
      explica que a proibição vale para o **`newWe2002`**, e que a
      release é justamente a segunda amostra deste projeto. Quem ler só o
      `CLAUDE.md` conclui o contrário.
- [→] **Nenhuma task de PES2 em
      [/docs/tasks/progresso.md](/docs/tasks/progresso.md).** É uma
      decisão a tomar, não necessariamente um erro: as seis fases do plano
      poderiam virar tasks com `fonte_de_verdade` apontando para as seções
      dele, como manda [.claude/rules/tasks.md](../.claude/rules/tasks.md),
      ou o projeto pode ficar fora do pool enquanto for exploratório.
      **Adiado por decisão do usuário em 2026-08-30**, para não misturar
      criação de tarefa com esta rodada. O `CLAUDE.md` já diz, em uma
      linha, que o projeto está fora do pool *por escolha* — o que remove
      o "sem ninguém ter decidido". Enquanto isso, **o backlog de PES2 é
      a §7 deste arquivo**, não o `progresso.md`. Item vivo na **§7.1**.
- [→] **Preparo para as Fases 3 e 4:** `numpy` não está instalado
      (confirmado), e não há desmontador MIPS — `ghidra`, `radare2` e
      `rizin` todos ausentes. **Não instalado nesta execução**: instalar
      pacote na máquina do usuário é decisão dele, e nada das Fases 0–2
      precisa dos dois. Item vivo na **§7.1**.

---

## 6. O que a execução encontrou, e que a revisão não previa

Versionar uma medição é diferente de repeti-la: a ferramenta discorda, e
neste caso discordou duas vezes. As duas correções estão escritas no
plano, nas seções que as afirmavam.

### 6.1 O diff entre releases era 202 / 27 / 7, não 204 / 32

`tools/pes2/diff_releases.py` mede 236 arquivos em comum, **202** byte a
byte idênticos, **27** diferentes e **7** que o Track 1 não permite
comparar — os `/SD/DA/*.DA`, que moram nas trilhas de áudio. O par
204 / 32 da §1.12 foi contado à mão e não fecha com nenhuma leitura que
se consiga reproduzir. De brinde, duas respostas que faltavam:

- o único arquivo Form 2, `/MOVIE/ISS_2002.STR`, **é idêntico** nas duas —
  a comparação dele é de setor cru, porque ele não tem área de 2.048 B;
- dos 27, **19 mudam de tamanho** (texto localizado) e **8 mantêm o
  tamanho e mudam conteúdo**. Estes oito são a lista de suspeitos da
  Fase 1, e agora ela está fechada.

### 6.2 Os 54 elencos casam todos; não havia parcial nenhum

A §3.3 dizia 49 exatos em `SELECTC.BIN`, 2 no executável e **3 parciais**
— Noruega, Argentina e Austrália, com "19, 15 e 21 dos 23 nomes". O
`memcard.py` acha os **54 exatos**: 49 em `SELECTC.BIN` em ordem reversa
e **5** no executável em ordem direta.

A causa do engano é interessante e vira conhecimento: a busca original no
executável olhava só onde França e Alemanha já haviam aparecido. A tabela
de lá tem **1.449 registros de 10 B** — a mesma faixa dos 1.399 de
`SELECTC.BIN`, guardada de trás para frente e 50 entradas mais longa — e
os três "parciais" estavam nela inteiros.

Isso custa uma alavanca: os três pares editado/original que a §4.2.3
esperava colher de graça não existem, porque não havia divergência.

### 6.3 Três fatos novos que mudam o formato do mapa

- **"Cópia" de tabela não quer dizer mesma lista.** As cinco listas de
  nome de time têm 106, 99, 95, 94 e 123 entradas, e diferem em conteúdo,
  não só em recorte: onde `SELECT.BIN` tem as 7 seleções temáticas e as 2
  *elite*, o `RESULT.BIN` tem 6 *classic* e as 2 *allstars*. Casar duas
  por índice grava no time errado. Está na §6.1 do plano.
- **`REPLAYS.BIN` carrega uma nona cópia**, em caixa mista, logo depois
  das abreviações (`PTA\0MRA\0BZA\0` + 380). Nenhuma versão da §1.5 a
  listava.
- **O executável guarda a tabela de jogador inteira**, 1.449 registros de
  10 B, invertida em relação a `SELECTC.BIN`.

---

## 7. Pendências — o backlog de PES2 mora aqui

Enquanto o projeto estiver fora do `progresso.md` (§5), **é esta seção que
faz as vezes dele.** O que aparecer para fazer entra aqui, não lá.

### 7.1 Decisões do usuário, não de código

- [ ] **Criar as tasks das seis fases** em
      [/docs/tasks/progresso.md](/docs/tasks/progresso.md), com
      `fonte_de_verdade` apontando para as seções do plano — ou decidir
      que o projeto segue fora do pool. Adiado em 2026-08-30.
- [ ] **`numpy`** para varredura de padrão em 466 MB em tempo civilizado,
      e um **desmontador MIPS** (`ghidra`, `radare2` ou `rizin` — os três
      ausentes). Nada das Fases 0–2 precisa deles; a Fase 4 precisa, se
      empacar. Instalar pacote é decisão do dono da máquina.

### 7.2 Dívida das ferramentas novas

- [ ] **O teste de descritor vazado do `selftest.py` é fraco.** Ele fica
      verde mesmo sem o `except BaseException` do `Image.__init__`, porque
      o CPython coleta o objeto de arquivo assim que a exceção desenrola.
      Está dito no próprio teste; se um dia importar de verdade, o jeito é
      segurar uma referência à exceção e conferir `/proc/self/fd` com ela
      viva.
- [ ] **A evidência de boot é número, não imagem** — desvio-padrão e
      contagem de pixels diferentes. Os quadros são de jogo comercial e
      ficam fora do git, como `roms/` e os FAQs. Quem quiser rever roda
      `tools/pes2/boot_check.sh`. Se algum dia for preciso comparar
      *contra* um quadro de referência, o lugar dele é fora do
      repositório, e o caminho vira variável de ambiente.
- [ ] **`boot_check.sh` não entra no `ctest`.** Ele precisa do `:98`, do
      DuckStation e de ~90 s; é o mesmo motivo pelo qual os golden do
      `newWe2002` também não rodam em CI. Fica como comando à mão.

### 7.3 Fase 1, o que a execução deixou apontado

- [ ] **Olhar os oito arquivos que diferem sem mudar de tamanho** entre as
      releases — `GAME.BIN` (38.213 B de diferença), `SELECT4.BIN`
      (6.884), `ENTER.BIN` (3.272), `PKMATCH.BIN` (242), `TRAINING.BIN`
      (126), `FNOTE_G.BIN` (105), `MOVIE.BIN` (79), `SYSTEM.CNF` (2). A
      lista está fechada em
      [/docs/samples/pes2-diff-releases.md](/docs/samples/pes2-diff-releases.md);
      falta o que há dentro. É ali que pode haver dado de jogo em vez de
      texto localizado.
- [ ] **Mapear os 69 `OFS_*` do WE2002** para `(arquivo, offset
      relativo)` no PES2. A §1.4 do plano tem o esqueleto; falta o offset
      relativo de cada um.

### 7.4 Fase 2, idem

- [ ] **Varrer os 252 arquivos restantes** por string, classificando em
      nome de time / abreviação / nome de jogador / interface / lixo. As
      onze tabelas da §1.6 estão fechadas; o resto do disco não.
- [ ] **Fechar a correspondência entre as cinco listas de nome de time.**
      Elas têm 106, 99, 95, 94 e 123 entradas e **não são a mesma lista**
      (§6.3). O mapa da Fase 5 precisa da correspondência entrada a
      entrada, tirada de comparação de conteúdo — nunca de índice. Sem
      isso, gravar "todas as cópias" grava no time errado em pelo menos
      duas delas.
- [ ] **Classificar a segunda massa de nomes do executável.** São 1.449
      registros de 10 B contra os 1.399 de `SELECTC.BIN` (§1.5): faltam
      dizer quais são as 50 entradas a mais e por que só elas moram lá.

---

## Ordem sugerida

*(§1 a §4 cumpridas em 2026-08-30, nesta ordem. A §5 ficou pelas duas
decisões acima; a §7 é o que sobrou.)*

Os itens da §1.1 e da §3 custam minutos e removem armadilha ativa —
`--kill` escrevendo fora do repositório, e o cabeçalho do plano dizendo
que nada foi feito. A §2 é o investimento que decide se a Fase 2 vai
poder ser reconferida daqui a um mês. A §4 é conhecimento medido que só
precisa ser escrito antes de esfriar.
