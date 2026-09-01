# PES2 — ajustes pendentes

> Revisão de [/docs/PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md), de
> [/docs/PES2-NOMES.md](/docs/PES2-NOMES.md) e dos três commits que os
> acompanham (`934ef1f`, `d345a0e`, `35a6d92`), feita em **2026-08-30**.
>
> **Executada no mesmo dia**, e a §7 depois dela. Estão feitos: §1 a §4
> inteiras, dois dos quatro de §5, e **oito dos dez** da §7. Os dois que
> sobram não são trabalho de código — criar as tasks e instalar pacote —
> e continuam esperando decisão.
>
> Com isso a **Fase 1 fecha** e a **Fase 2 fica a um item**: o `poke` de
> validação, que precisa do emulador e não da varredura.
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
- [x] **Nenhuma task de PES2 no `progresso.md`.** Era uma decisão a tomar,
      não um erro: as seis fases do plano poderiam virar tasks com
      `fonte_de_verdade` apontando para as seções dele, como manda a
      [.claude/rules/tasks.md](../.claude/rules/tasks.md), ou o projeto podia
      ficar fora do pool enquanto exploratório. **Adiado em 2026-08-30** para
      não misturar criação de tarefa com aquela rodada, e **decidido em
      2026-09-01**: o projeto entra no pool, com 25 tasks em
      [/docs/tasks/progresso.md](/docs/tasks/progresso.md). Enquanto esteve
      adiado, o backlog foi a §7 deste arquivo; agora não é mais.
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

### 6.3 As duas tabelas de jogador são o mesmo pool, uma delas deduplicada

Perseguir as "50 entradas a mais" do executável (§7.4) devolveu o
contrário da pergunta. As duas guardam **os mesmos 1.399 nomes
distintos** — nenhuma tem um que a outra não tenha. `SELECTC.BIN` guarda
cada nome **uma vez**; o executável **repete 50**; e `SELECTC.BIN` é
**subsequência exata** do executável lido de trás para frente.

Ou seja, `SELECTC.BIN` é um **pool de string deduplicado** e o executável
é **ordenado por vaga**. Jogador em dois elencos ganha dois registros lá e
um aqui.

Isso explica a §3.3 sem apelar a dado faltante: os cinco elencos que só
casam no executável são exatamente os cinco que contêm um jogador de nome
repetido — `Petit`, `Butt`, `Sorensen`, `Zanetti`, `Moore` — de modo que
no pool suas 23 vagas viram 22 e deixam de ser um trecho contíguo. E 45
das 50 repetições ficam numa janela de 46 vagas, que é 2 × 23: os dois
elencos *elite*.

### 6.4 Os oito arquivos de tamanho fixo são código realocado, não dado

99,6% a 100% das palavras que diferem em `GAME.BIN`, `SELECT4.BIN`,
`ENTER.BIN`, `PKMATCH.BIN`, `TRAINING.BIN` e `MOVIE.BIN` são a mesma
rotina MIPS deslocada — e o deslocamento dominante é o mesmo **+3176** em
arquivos diferentes. **Nenhum dos oito guarda dado de jogo diferente**, o
que fecha a Fase 1 com resposta em vez de com uma lista de suspeitos.

### 6.5 Há mais nome em `SELECTC.BIN` do que o pool

Depois do fim do pool (30853) vêm mais 25 blocos de nome, cerca de 2.000
trechos, de 31552 a por volta de 50000 — `Tomazi`, `Navaji`, `Davinno`,
`Beckenboer`, `Lupateli`. Nenhum está entre os 1.399. É achado da
varredura da §7.4 e é onde a Fase 3 começa.

### 6.6 Três fatos novos que mudam o formato do mapa

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

## 7. Pendências — o backlog de PES2 **morava** aqui

Esta seção fez as vezes do `progresso.md` enquanto o projeto estava fora do
pool. **Deixou de estar em 2026-09-01**, e desde então o backlog é
[/docs/tasks/progresso.md](/docs/tasks/progresso.md) — 25 tasks nas seis
fases, cada uma com `fonte_de_verdade` apontando para a seção do plano que a
mede. O que aparecer para fazer entra **lá**, não aqui.

O que sobrou desta seção é registro do que a revisão de 2026-08-30 apontou, e
de onde cada item foi parar. Um único item continua vivo, e por não ser
trabalho de código: a instalação de pacote da §7.1.

### 7.1 Decisões do usuário, não de código

- [x] **Criar as tasks das seis fases** — feito em 2026-09-01, em
      [/docs/tasks/progresso.md](/docs/tasks/progresso.md), com
      `fonte_de_verdade` apontando para as seções do plano como manda a
      [.claude/rules/tasks.md](../.claude/rules/tasks.md). São **25 tasks**:
      uma de decisão de ferramental, três que fecham a Fase 2 pelo `poke` de
      validação, seis na Fase 3, seis na Fase 4, cinco na Fase 5 e quatro na
      Fase 6. O `correcoes-progresso.md` do ciclo nasceu junto, vazio, com a
      numeração `CORR-PES2-XXX`.
- [x] **`numpy`** para varredura de padrão em 466 MB em tempo civilizado,
      e um **desmontador MIPS** — resolvido em 2026-09-01 (PES2-TASK-01), a
      pedido do dono da máquina: `numpy` 2.5.2, `radare2` 5.5.0 e
      `mipsel-linux-gnu-objdump` 2.42. **Ghidra ficou de fora** — fora dos
      repositórios do Zorin 18.1, ~1,2 GB, e exige JDK 21 contra o 17 da
      máquina; o que ele traz a mais é o decompilador, e a §4.2.4 pede leitura
      de rotina, não decompilação. Detalhe e os comandos com base explícita na
      §3.2 do plano.

### 7.2 Dívida das ferramentas novas

- [x] **O teste de descritor vazado do `selftest.py` era fraco.**
      Consertado, e o conserto precisou de duas tentativas — que é o
      próprio motivo do item. Segurar o traceback mantém o frame de
      `__init__` vivo, e com ele o `self`, então o descritor continua
      aberto se ninguém o fechou de propósito. **Mas a primeira versão
      continuava verde**: ela comparava o *conjunto de números* de
      `/proc/self/fd` antes e depois, e o descritor vazado caía num
      número baixo que já estava em uso antes, então a diferença de
      conjuntos dava vazia. Varrer por **caminho de destino** pega. Com o
      `except BaseException` removido à mão, o teste agora acusa
      `still open: ['4']`.
- [x] **A evidência de boot é número, não imagem** — e continua sendo, por
      escolha: os quadros são de jogo comercial e ficam fora do git, como
      `roms/` e os FAQs. O que faltava era o caminho de comparação, e ele
      existe: `PES2_REFERENCE` aponta um PNG de fora do repositório e
      `PES2_TOLERANCE` diz quanto pode diferir (35% por padrão — emulação
      não é exata quadro a quadro e a partida de demonstração nunca se
      repete, então é teste de "mesma tela", não golden).

      **Exercitado nos dois sentidos em 2026-08-30**, porque escrever o
      caminho não é o mesmo que rodá-lo: contra o quadro de uma corrida
      anterior no mesmo instante do vídeo de abertura, **8.178 de 76.800
      pixels diferem (10,6%)** e passa; contra o quadro da partida de
      demonstração, **58.451 (76,1%)** e falha com *"frame 2 is not the
      same screen as the reference"*. A tolerância de 35% fica com folga
      entre os dois.
- [x] **`boot_check.sh` não entrava no `ctest`.** Entra agora, como
      **`pes2_boot`**, nos mesmos termos dos golden: sai 77 e se reporta
      *skipped* se faltar imagem, DuckStation, ImageMagick, `xdotool` ou
      servidor X. Continua fora do CI, pelo mesmo motivo que o `golden`.

### 7.3 Fase 1, o que a execução deixou apontado

- [x] **Olhar os oito arquivos que diferem sem mudar de tamanho.** Feito
      com `diff_releases.py --explain`, **e a resposta é não**: 99,6% a
      100% das palavras que diferem nos seis overlays são a mesma rotina
      MIPS **realocada** — alvo de `j`/`jal`, imediato de `lui`/`addiu`,
      ponteiro `0x800xxxxx` —, deslocada por um punhado de constantes com
      **+3176** dominando. O resíduo é de dezenas de palavras e o pouco
      que significa algo é constante de código, não banco. Os outros dois
      são o que aparentavam: `FNOTE_G.BIN` é alemão reescrito no mesmo
      tamanho e `SYSTEM.CNF` é o nome do executável.
- [x] **Mapear os 69 `OFS_*`.** Feito — `tools/pes2/ofs_map.py`, tabela em
      [/docs/samples/pes2-ofs-map.md](/docs/samples/pes2-ofs-map.md).
      **69 de 69 localizados**, em 13 arquivos, e os 13 existem no PES2
      (o executável com outro nome). Cinco pares já se pode afirmar, e um
      deles é a confirmação mais forte da §1.4: `OFS_TEAM_NAME_1` está no
      **mesmo offset relativo (1256) nos dois jogos**.

### 7.4 Fase 2, idem

- [x] **Varrer o disco por string.** Feito — `strings_inventory.py`,
      saída em [/docs/samples/pes2-strings.md](/docs/samples/pes2-strings.md).
      171.161 trechos em 217 arquivos, agrupados em **281 blocos densos**,
      que é a forma que uma tabela tem vista de fora. Ranquear arquivo não
      servia: `SELECT.BIN` são 216 kB de código com 6 kB de tabela dentro.
- [x] **Fechar a correspondência entre as cinco listas.** Feito —
      `team_map.py`, saída em
      [/docs/samples/pes2-team-lists.md](/docs/samples/pes2-team-lists.md).
      Cada cópia é uma sequência de **trechos** da lista canônica, e o
      `--team N` diz onde um time está em cada uma. Exemplo do perigo que
      isso fecha: o time canônico 34 fica no índice 34, 36, 32 e 60 de
      quatro listas e **não existe** na quinta.
- [x] **Classificar a segunda massa do executável.** Feito —
      `player_map.py`. As duas guardam os **mesmos 1.399 nomes
      distintos**; `SELECTC.BIN` é um pool deduplicado e o executável é
      ordenado por vaga, repetindo 50. Ver a §6.3.

---

## Ordem sugerida

*(§1 a §4 cumpridas em 2026-08-30, nesta ordem. A §5 ficou pelas duas
decisões acima; a §7 é o que sobrou.)*

Os itens da §1.1 e da §3 custam minutos e removem armadilha ativa —
`--kill` escrevendo fora do repositório, e o cabeçalho do plano dizendo
que nada foi feito. A §2 é o investimento que decide se a Fase 2 vai
poder ser reconferida daqui a um mês. A §4 é conhecimento medido que só
precisa ser escrito antes de esfriar.
