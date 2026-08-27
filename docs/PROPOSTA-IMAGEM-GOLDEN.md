# Proposta: adotar a `ptbr-remaster` como imagem golden

> **Documento de decisão.** Ele propõe **medir** se a `ptbr-remaster.bin` pode
> tomar o lugar da `golden-european-deluxe.bin`, define o protocolo que
> responde isso com evidência, e diz o que cada resultado licencia. Nada foi
> alterado: a europeia continua sendo a golden e as ferramentas continuam
> apontando para ela.
>
> **O protocolo roda na máquina Linux.** A bateria golden depende de Xvfb,
> `xdotool` e Wine — §5.4 de
> [/docs/PLAN-WTE-WINDOWS.md](/docs/PLAN-WTE-WINDOWS.md). O que a máquina
> Windows já mediu está na [§3](#3-o-que-já-está-medido).
>
> Diagnóstico do travamento em
> [../wte/re/crash-causa.md](../wte/re/crash-causa.md).

---

## 1. O que se propõe

Em uma frase:

> **Rodar os três portões da [§4](#4-o-protocolo-de-validação) sobre a
> `ptbr-remaster.bin` e, se os três passarem, promovê-la a imagem golden.**

A proposta **não** é trocar agora. É que a troca deixe de ser opinião: hoje
não se sabe se ela é possível, porque o oráculo do `newWe2002` — o
`Debug/ed.exe` — nunca foi rodado sobre essa imagem. O portão 1 existe para
responder exatamente isso.

E há uma segunda pergunta, que o protocolo responde de graça: **vale a pena?**
Se a `ptbr-remaster` passar nos três, ela vira a **única imagem que os dois
oráculos aceitam** — o `ed.exe` e o `we-team-editor.exe`. Nenhuma das duas
atuais é. Esse é o ganho concreto que justifica o trabalho; sem ele, a troca é
só troca.

---

## 2. De onde vem

Uma ROM nova entrou em `roms/` — uma ISO do WE2002 **traduzida para PT-BR** por
terceiros (o `.cue` original trazia *"WE2002 ISO limpa 100% Traduzida pt
GOKUWE11 & FABIO FJA"*), renomeada aqui para **`ptbr-remaster.bin`** pela
convenção do [../CLAUDE.md](../CLAUDE.md): minúsculas, sem espaço, dizendo o
que a imagem é.

Ela abre no **editor do Obocaman** e se deixa dirigir. A
`golden-european-deluxe.bin` **não**: ali o `wte.exe` morre com `0xc0000005` ao
trocar de time, e é por isso que 23 dos 24 roteiros da bateria golden do `wte/`
saem `SEM_ORACULO` naquela imagem — limite que o
[../wte/README.md](../wte/README.md) já registra como *"não é falha do port: é
ausência de régua"*.

---

## 3. O que já está medido

Em 2026-08-27, na máquina Windows, com as ferramentas do repositório.

### 3.1 O travamento é previsível, e a `ptbr-remaster` não o dispara

`wte/tools/conta_ml.py --medir` modela a rotina `0x004042d4` — a que conta os
blocos livres de Master League — e enumera os índices que ela escreve **fora**
da tabela de 462 palavras. É esse estouro que corrompe o ponteiro que o editor
desreferencia depois.

| imagem | próprios | distintos | livres | **fora do vetor** | maior `b0` |
|---|---:|---:|---:|---:|---:|
| `japanese-shift-jis` | 461 | 460 | 2 | **0** | 116 |
| `golden-european-deluxe` | 453 | 449 | 13 | **8** | 111 |
| **`ptbr-remaster`** | 461 | 461 | 1 | **0** | 116 |

**Confirmado ao vivo:** o editor do Obocaman abriu a `ptbr-remaster`, foi levado
a `20 Hungria`, desenhou a bandeira húngara e a camisa, mostrou `HUNGRIA`/`HUN`
e o goleiro `1 Kiraly`, e sobreviveu a quatro trocas de time. `SPC = 1`,
exatamente o `livres=1` previsto.

### 3.2 Ela cobre os mesmos ramos do codec que a europeia

Esta era **a** objeção séria, e ela caiu. O
[compare_dumps.py](../wte/tools/compare_dumps.py) registra em
[../wte/re/fase-3.tsv](../wte/re/fase-3.tsv) um achado da WTE-TASK-20: quem
exercita os ramos de mapeamento do `KanjiToAscii` **é a europeia** — a japonesa
guarda katakana (`0x83`), que o codec transforma em espaço.

| imagem | `kanji_duplo` | `kanji_decodificado` | `squad_numbers` ≠ 0 | nomes não-vazios |
|---|---:|---:|---:|---:|
| `golden-european-deluxe` | 95 | **95** | 64 | 95 |
| **`ptbr-remaster`** | 95 | **95** | 64 | 95 |
| `japanese-shift-jis` | 95 | **0** | 64 | 95 |

**A `ptbr-remaster` decodifica os mesmos 95.** A cobertura que só a europeia
dava não se perde.

### 3.3 Mesma estrutura, dados completamente outros

Dos 66.498 registros do dump, **43.556 diferem** da europeia:

```
eu  : players[0].name = 11:47616d61727261      ("Gamarra")
ptbr: players[0].name = 11:497277696e          ("Irwin")
```

Formato idêntico, elenco reescrito. Ela não é a europeia traduzida — é outra
base no mesmo molde. **Isso não é defeito**: o que a golden precisa é do
*layout*, e o layout está intacto. Mas é o motivo de os portões existirem: 43
mil registros diferentes são 43 mil chances de encostar num caminho que a
europeia nunca exercitou.

---

## 4. O protocolo de validação

Três portões, em ordem. **Cada um tem critério de aprovação escrito antes de
rodar** — é o que separa medir de torcer.

### Portão 1 — o `ed.exe` sobre a `ptbr-remaster` *(o que decide)*

É o oráculo do `newWe2002`. Sem ele não há golden nenhum, só um arquivo novo.

```sh
make golden     IMAGE=roms/ptbr-remaster.bin     # core headless vs ed.exe
make golden-gui IMAGE=roms/ptbr-remaster.bin     # a janela Qt no lugar do core
```

**O que prova:** que o `ed.exe` de 2002 carrega e grava essa imagem, e que o
port grava os mesmos bytes que ele.

**Critério:** passa se a **única** divergência for a faixa conhecida
`405724..405739` — os 16 bytes do slot 64 de um array de 63, que o original lê
e grava a partir da memória vizinha. Qualquer outra faixa reprova.

**Se reprovar:** a proposta morre aqui, e o resultado é informação boa — quer
dizer que a imagem tem algo que a europeia não tem, e o diff dirá o quê.

> **Atenção ao que "reprovar" significa.** Divergência nova pode ser defeito da
> imagem **ou** um caminho do `ed.exe` que a europeia nunca exercitou. Antes de
> condenar a ROM, ver de que offset é a faixa: se cair em região que os 43.556
> registros divergentes tocam, o achado é sobre o **editor**, não sobre ela.

### Portão 2 — a camada de dados, nos dois compiladores

```sh
python3 wte/tools/compare_dumps.py --medir
```

**O que prova:** que o Pascal do `wte/` e o C++ do `we2002_core` leem e gravam a
mesma coisa nessa imagem — o aceite da fase 3.

**Critério:** `divergencias_dump = 0` e `divergencias_rt_pascal_vs_cpp = 0`.

**Exige uma mudança de código** — ver a [§5](#5-as-mudanças-que-o-protocolo-exige).

### Portão 3 — a bateria do `wte/` com oráculo vivo

```sh
bash wte/tools/golden_suite.sh --rom ptbr
```

**O que prova:** o ganho que justifica a troca — que os 24 roteiros correm com
oráculo nessa imagem, o que na europeia não acontece.

**Critério:** zero `REPROVOU` e **zero `SEM_ORACULO`**. O segundo é o ponto:
`SEM_ORACULO` aqui significaria que ela trava como a europeia, e aí ela não
compra nada.

**Exige uma mudança de código** — ver a [§5](#5-as-mudanças-que-o-protocolo-exige).

---

## 5. As mudanças que o protocolo exige

Pequenas, nomeadas, e **reversíveis** — nenhuma troca a golden, só ensinam as
ferramentas a enxergar a terceira imagem:

| arquivo | o quê |
|---|---|
| [../wte/tools/golden_suite.sh](../wte/tools/golden_suite.sh) | o mapa de ROMs (`[japonesa]=`, `[europeia]=`) e o `case` que valida `--rom` ganham `ptbr` |
| [../wte/tools/compare_dumps.py](../wte/tools/compare_dumps.py) | a lista `ROMS` ganha uma terceira tupla |

O portão 1 **não exige nada**: `make golden IMAGE=` já aceita qualquer imagem.

---

## 6. Critério de decisão

O que cada resultado licencia — escrito antes, para a resposta não ser
negociada depois:

| P1 (`ed.exe`) | P2 (dados) | P3 (bateria `wte/`) | decisão |
|:-:|:-:|:-:|---|
| ✅ | ✅ | ✅ | **Adotar.** É a única imagem que os dois oráculos aceitam — ver a [§7](#7-adotar-como-trocar-ou-acrescentar) |
| ✅ | ✅ | ❌ | **Não trocar.** Passa como golden mas não compra nada: o ganho era o portão 3 |
| ✅ | ❌ | — | **Parar e investigar.** Divergência entre os dois compiladores na mesma imagem é achado sobre o *código*, não sobre a ROM |
| ❌ | — | — | **Arquivar a proposta**, com o diff do portão 1 registrado — ele é o resultado útil |

---

## 7. Adotar: como, trocar ou acrescentar

Mesmo com os três portões verdes, **substituir não é automático**, e a razão é
de custo, não de mérito:

| | ferramentas que a citam pelo nome | evidência versionada |
|---|---:|---|
| `golden-european-deluxe` | **8** | `fase-3.tsv`, `ml-slots-medido.tsv`, `ml-slots-fora.tsv`, `io-medido.tsv`, `cmp-medido.tsv`, `preco.tsv` |
| `japanese-shift-jis` | **12** | as mesmas |

São 30 arquivos que mencionam a europeia. Os seis TSVs guardam medições **feitas
nela, identificadas por nome**: trocada a imagem, cada um vira afirmação que
ninguém reconfere até ser remedido — e remedir é o trabalho, não o `sed`.

Há também o que a europeia é e a `ptbr-remaster` não: **dump de uma release
identificável**. A `ptbr-remaster` é modificação de fã, sem versão nem checksum
publicado. Régua que alguém pode reeditar e redistribuir com o mesmo nome é
régua mais fraca — mesmo passando nos três portões hoje.

Daí as duas formas de adotar:

**(a) Acrescentar** — as três ficam, a `ptbr-remaster` entra como a ROM em que a
bateria do `wte/` roda com oráculo. Custa ~450 MB e **nenhuma** reescrita de
evidência. A cadeia histórica de medições continua reconferível.

**(b) Substituir** — a europeia sai. Só faz sentido se o objetivo for reduzir o
conjunto mantido, e aí a ordem é: remedir e recommitar os seis TSVs, trocar o
nome nas 8 ferramentas, e **guardar a europeia mesmo assim** até que uma
corrida completa mostre a régua nova concordando com a antiga.

**A recomendação é (a)**, e ela não depende do resultado dos portões: acrescentar
entrega o mesmo ganho sem gastar a evidência acumulada. A (b) vira defensável no
dia em que manter três imagens de ~450 MB incomodar mais do que remedir tudo.

---

## 8. O que já mudou, e não depende desta decisão

- A imagem foi renomeada para `ptbr-remaster.bin`, e o `FILE` do `.cue`
  corrigido — apontava para um nome que não existia no disco.
- `roms/copadomundo2002.bin` **foi removida** (para a Lixeira). Ela não é
  WE2002 na região que importa: os nomes de time leem bem no offset certo, mas
  a região de vínculo de Master League traz `b0` até **252** numa tabela que
  define **120** times, e o editor do Obocaman morre com `0xc0000005` **na
  carga**, antes da janela principal. No port Lazarus, que não reproduz o
  estouro, ela abre e mostra o estrago: `20 Hungria` com `Nome1 GALES`, números
  de camisa repetidos, `SPC 410`. Nenhuma ferramenta a citava.
