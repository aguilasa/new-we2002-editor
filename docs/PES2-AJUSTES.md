# PES2 — ajustes pendentes

> Revisão de [/docs/PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md), de
> [/docs/PES2-NOMES.md](/docs/PES2-NOMES.md) e dos três commits que os
> acompanham (`934ef1f`, `d345a0e`, `35a6d92`), feita em **2026-08-30**.
>
> **O que está certo, e vale dizer antes:** a Fase 0 é real. O
> `roundtrip` do `iso.py` foi executado nesta revisão sobre o Track 1
> `(EsIt)` e saiu **`ROUND-TRIP OK: image is byte-identical`**, com
> 244 arquivos reescritos e 8 pulados na classificação prevista
> (1 `form2`, 7 `outside`). Os oito marcadores da §1.13 resolvem nas
> **duas** releases, cada um uma única vez, e os offsets batem com a
> tabela da §1.12 byte a byte. As contagens da §1.6 foram reconferidas
> contra o disco: **106** nomes de time, **95** abreviações, **463**
> registros de 10 B. Nada do que o plano afirma como medido saiu errado.
>
> O que segue é o que **falta**, o que está **inconsistente entre
> documento e medição**, e dois **defeitos de código** que se
> reproduzem.

---

## 1. Defeitos de código

### 1.1 `run_duckstation.sh --kill` cria uma árvore fora do repositório

- [ ] **Só resolver `DATA` e criar diretório depois de tratar `--kill`,
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

- [ ] **Alinhar código e comentário, e usar caminho absoluto.**

O cabeçalho (linha 10) diz `default <scratch>/ds-data`; o código (linha
18) usa `$(dirname "$IMAGE")/../ds-data`, que é relativo ao **caminho da
imagem**, não ao scratchpad, e contém um `..` que muda de significado
conforme o `PES2_IMAGE` seja absoluto ou relativo.

### 1.3 O link do BIOS pode ficar pendurado sem ninguém notar

- [ ] **Conferir `~/.local/share/duckstation/bios` antes do `ln -sfn`, e
      falhar alto se não existir.**

`ln -sfn` cria o link mesmo com alvo inexistente. O sintoma seria o
DuckStation não achar BIOS nenhuma e morrer na carga — longe da causa,
que é exatamente o tipo de armadilha que a §6.11 do plano cataloga.

### 1.4 `write_file` não é atômico

- [ ] **Validar `status(path) == "form1"` antes do primeiro
      `write_sector`, em vez de descobrir no meio.**

[`iso.py:224`](../tools/pes2/iso.py) grava setor a setor e confia no
`Form2Sector`/`OutsideTrack` que o `write_sector` levanta. Num arquivo
misto, os setores anteriores ao problemático **já foram gravados** quando
a exceção sobe, e o `inject` deixa o arquivo pela metade. Hoje nenhum dos
244 `form1` é misto, então o defeito é latente — mas o `inject` é a
ferramenta do ciclo de `poke`, e ela vai operar sobre cópia de 445 MiB.

### 1.5 Detalhes menores

- [ ] `Image.__init__` abre o arquivo e só depois chama
      `_read_filesystem()`; se este levantar, o descritor vaza.
- [ ] O docstring do `faq2md.py` documenta dois argumentos
      (`ENTRADA.txt SAIDA.md`), mas o `__main__` aceita um terceiro
      opcional (o título) — que é o que o `.gitignore` manda usar ao
      reconverter. Sem `argparse`, faltar argumento dá `IndexError`.

---

## 2. Lacunas de verificação

O `CLAUDE.md` deste repositório diz, sobre os golden: *"verde de golden é
asserção sobre um estímulo: sem o estímulo versionado a corrida não é
repetível, e o par verde+faixa vira lembrança."* A regra vale igual aqui,
e hoje **só o `roundtrip` a cumpre**.

- [ ] **Versionar a ferramenta que produziu as medições da §1.6.** As
      contagens (106 / 95 / 99 / 1.399 / 463) e a ordem canônica saíram de
      uma varredura que não está no repositório. Reconferi todas nesta
      revisão e batem — mas com script escrito na hora, que também se
      perdeu. Deveria ser um `tools/pes2/tables.py` que imprime a
      contagem, o offset e as primeiras/últimas entradas de cada tabela.
- [ ] **Versionar o diff entre releases da §1.12.** Os números (236 em
      comum, 204 idênticos, 32 diferem) não têm como ser reproduzidos.
- [ ] **Versionar a análise de memory card da §3.3.** É a medição mais
      valiosa do plano — as 54 fronteiras de elenco, 49 em `SELECTC.BIN`
      invertidos e 2 em `SLES_039.57` diretos — e é a que menos rastro
      deixou. A Fase 3 depende dela.
- [ ] **Versionar o alinhamento FAQ × disco** que sustenta o "30 dos 32"
      da [/docs/PES2-NOMES.md](/docs/PES2-NOMES.md). Os FAQs não entram no
      git, mas o **script** que os lê entra, e é ele que torna a
      verificação repetível quando o usuário baixá-los de novo.
- [ ] **Versionar o controle negativo da §5.1.** Trocar o `P` de
      `PIEMONTE` por `X` e conferir que muda exatamente um byte, no
      offset absoluto 2002800, é a prova de que a guarda sabe ficar
      vermelha. Hoje é prosa.
- [ ] **Registrar `iso.py` no `ctest`.** Nenhum teste do
      [tests/CMakeLists.txt](../tests/CMakeLists.txt) conhece `pes2`. Dois
      são viáveis: um sobre imagem **sintética** de poucos setores
      (aritmética de setor, Form 1 × Form 2, `outside`, recusa de mudar
      tamanho) que roda sempre; e um `pes2_anchors`, condicionado a uma
      variável `WE2002_PES2_IMAGE` e reportado como *skipped* sem ela,
      como já se faz com `WE2002_TEST_IMAGE`.
- [ ] **Deixar evidência do boot da §3.4.** O commit `35a6d92` afirma que
      o jogo chega à tela-título no `:98`; não há screenshot nem log
      versionado, e não há script de direção — só as instruções que o
      `run_duckstation.sh` imprime no fim.

---

## 3. Inconsistências entre o plano e o que foi medido

- [ ] **Cabeçalho do plano ainda diz "`plano. Nenhuma fase executada.`"**
      (linha 16). A Fase 0 está feita e verde. É a primeira linha que
      alguém lê.
- [ ] **A §7 diz que a Fase 0 está "feito, **menos o emulador**"; a §5
      diz que o emulador está feito.** As duas se contradizem no mesmo
      documento.
- [ ] **"Sete marcadores" (§1.13) × "os oito marcadores" (§5.1).** O
      código tem oito, e o oitavo — `Oranges001` em `SELECT.BIN` — **não
      aparece na tabela da §1.13**. Acrescentá-lo.
- [ ] **A §1.5 põe a cópia em caixa mista de `RESULT.BIN` em `@~304`.**
      Medido agora, e coerente com a própria §1.12: é **524** em `(EsIt)`
      e **632** em `(EnFrDe)`. O `~304` está errado nas duas.
- [ ] **A §1.5 diz que os nomes de jogador estão em `SELECTC.BIN`
      @20736; a §1.6 diz 17604.** Os dois números existem — 17604 é o
      início do bloco (os fictícios) e 20736 é onde começam os reais —,
      mas o texto não deixa isso claro, e um mapa construído a partir da
      §1.5 perde a primeira família inteira.
- [ ] **A tabela de cópias da §1.5 omite a cópia em caixa mista de
      `SELECTC.BIN` @16576**, que a §1.6 lista com 99 entradas. Como a
      §6.1 é justamente "uma cópia gravada é pior que nenhuma", a lista de
      cópias é o pior lugar do documento para faltar uma linha.

---

## 4. Fatos medidos nesta revisão que ainda não estão escritos

- [ ] **A âncora `Oranges001` não marca o início da tabela que ela
      ancora.** Ela resolve em **7060** nas duas releases, e a tabela de
      10 B começa em **5320** — é o registro de índice **174**, não o 0.
      O delta é **−1740**, e é constante entre as releases. O mapa da
      Fase 5 tem de guardar delta **assinado**, e este caso é o primeiro
      exemplo de que o marcador pode cair no meio.
- [ ] **Não há folga nenhuma entre a tabela de nomes e a de
      abreviações.** Medido: os 106 nomes ocupam de 3128 a **4292**, e
      4292 é exatamente onde `PTA\0` começa. No disco lê-se
      `EURO ALLSTARS\0\0\0PTA\0` corrido. A §6.2 já manda truncar em vez
      de deslocar; vale registrar que a margem é **zero byte**, e que
      escrever um 107º nome invade a primeira abreviação.
- [ ] **Nenhuma das tabelas tem sentinela de fim.** O que separa uma da
      seguinte é só a contagem. Consequência para a Fase 5: o mapa
      precisa declarar **contagem** por tabela, não apenas âncora e
      esquema de registro — hoje a §1.13 só prevê
      `(arquivo, marcador, deslocamento)`.

---

## 5. Integração com o resto do repositório

- [ ] **O `CLAUDE.md` não sabe que este projeto existe.** Não há menção a
      PES2, a `docs/PLAN-PES2-PSX.md` nem a `tools/pes2/`. Os outros três
      projetos (`newWe2002`, `wte/`, e os planos de Windows) todos têm
      parágrafo lá.
- [ ] **O `CLAUDE.md` ainda diz, sem ressalva, `Pro Evolution Soccer 2
      (Europe) (EnFrDe) — NÃO USAR`** (linha 523). A §1.1 do plano
      explica que a proibição vale para o **`newWe2002`**, e que a
      release é justamente a segunda amostra deste projeto. Quem ler só o
      `CLAUDE.md` conclui o contrário.
- [ ] **Nenhuma task de PES2 em
      [/docs/tasks/progresso.md](/docs/tasks/progresso.md).** É uma
      decisão a tomar, não necessariamente um erro: as seis fases do plano
      poderiam virar tasks com `fonte_de_verdade` apontando para as seções
      dele, como manda [.claude/rules/tasks.md](../.claude/rules/tasks.md),
      ou o projeto pode ficar fora do pool enquanto for exploratório.
      Hoje está implicitamente fora, sem ninguém ter decidido.
- [ ] **Preparo para as Fases 3 e 4:** `numpy` não está instalado
      (confirmado), e não há desmontador MIPS — `ghidra`, `radare2` e
      `rizin` todos ausentes. O plano já lista os dois como faltantes; o
      item aqui é só não descobrir isso no meio da fase.

---

## Ordem sugerida

Os itens da §1.1 e da §3 custam minutos e removem armadilha ativa —
`--kill` escrevendo fora do repositório, e o cabeçalho do plano dizendo
que nada foi feito. A §2 é o investimento que decide se a Fase 2 vai
poder ser reconferida daqui a um mês. A §4 é conhecimento medido que só
precisa ser escrito antes de esfriar.
