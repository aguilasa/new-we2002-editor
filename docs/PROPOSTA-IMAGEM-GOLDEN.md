# Proposta: adotar a `ptbr-remaster` como imagem golden

> **Documento de decisão.** Ele propõe **medir** se a `ptbr-remaster.bin` pode
> tomar o lugar da `golden-european-deluxe.bin`, define o protocolo que
> responde isso com evidência, e diz o que cada resultado licencia. Nada foi
> alterado: a europeia continua sendo a golden e as ferramentas continuam
> apontando para ela.
>
> **Dois dos três portões já correram, e passaram** — na máquina Windows, em
> 2026-08-27. O resultado está na [§8](#8-a-corrida-dos-portões). O portão 3
> continua sendo Linux: a bateria do `wte/` depende de Xvfb, `xdotool` e Wine
> — §5.4 de [/docs/PLAN-WTE-WINDOWS.md](/docs/PLAN-WTE-WINDOWS.md).
>
> Diagnóstico do travamento em
> [../wte/re/crash-causa.md](../wte/re/crash-causa.md).

---

## 1. O que se propõe

Em uma frase:

> **Rodar os três portões da [§4](#4-o-protocolo-de-validação) sobre a
> `ptbr-remaster.bin` e, se os três passarem, promovê-la a imagem golden.**

A proposta **não** é trocar agora. É que a troca deixe de ser opinião: quando
este documento foi escrito não se sabia se ela era possível, porque o oráculo
do `newWe2002` — o `Debug/ed.exe` — nunca tinha sido rodado sobre essa imagem.
**Foi rodado**, e passou; o mesmo vale para o portão 2. Falta o 3, e é ele que
responde se a troca *vale a pena*. Ver a [§8](#8-a-corrida-dos-portões).

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

**Resultado: ✅ passou** (2026-08-27, Windows). [§8.1](#81-portão-1--o-edexe-sobre-a-ptbr-remaster).

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

**Resultado: ✅ passou** (2026-08-27, Windows). [§8.2](#82-portão-2--a-camada-de-dados).

### Portão 3 — a bateria do `wte/` com oráculo vivo

```sh
bash wte/tools/golden_suite.sh --rom ptbr
```

**O que prova:** o ganho que justifica a troca — que os 24 roteiros correm com
oráculo nessa imagem, o que na europeia não acontece.

**Critério:** zero `REPROVOU` e **zero `SEM_ORACULO`**. O segundo é o ponto:
`SEM_ORACULO` aqui significaria que ela trava como a europeia, e aí ela não
compra nada.

**Resultado: pendente.** Só roda no Linux, e **exige uma mudança de código** —
ver a [§5](#5-as-mudanças-que-o-protocolo-exige).

---

## 5. As mudanças que o protocolo exige

Pequenas, nomeadas, e **reversíveis** — nenhuma troca a golden, só ensinam as
ferramentas a enxergar a terceira imagem:

| arquivo | o quê | estado |
|---|---|---|
| [../wte/tools/golden_suite.sh](../wte/tools/golden_suite.sh) | o mapa de ROMs (`[japonesa]=`, `[europeia]=`) e o `case` que valida `--rom` ganham `ptbr` | pendente (portão 3) |
| [../wte/tools/compare_dumps.py](../wte/tools/compare_dumps.py) | a lista `ROMS` ganha uma terceira tupla | **exercitada** no portão 2, e revertida depois — ver abaixo |

O portão 1 **não exige nada**: `make golden IMAGE=` já aceita qualquer imagem.

**A tupla do `compare_dumps.py` foi aplicada para medir e desfeita em seguida**,
de propósito: enquanto a decisão não está tomada, o `--medir` do Linux passaria a
escrever um `fase-3.tsv` de três linhas, e o `fase-3.md` versionado — que o
`ctest` confere — divergiria até alguém regerar. A tupla entra junto com a
decisão, não antes dela. O texto é o de cima; aplicar de novo é uma linha.

---

## 6. Critério de decisão

O que cada resultado licencia — escrito antes, para a resposta não ser
negociada depois:

| P1 (`ed.exe`) | P2 (dados) | P3 (bateria `wte/`) | decisão |
|:-:|:-:|:-:|---|
| ✅ | ✅ | *pendente* | **onde estamos hoje** — falta só o portão 3 |
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

## 8. A corrida dos portões

Em 2026-08-27, na máquina Windows. Os dois portões que não dependem de Xvfb
correram; os dois passaram.

Método comum aos dois: **`roms/` nunca é alvo**. Três cópias limpas em `work/`
— uma para o oráculo, uma para o port, uma para medir só a carga.

### 8.1 Portão 1 — o `ed.exe` sobre a `ptbr-remaster`

O `Debug\ed.exe` roda **nativo** aqui, sem Wine. Foi dirigido por mensagem de
janela, com a janela em `-32000,-32000` desde antes de nascer, como manda a
regra do [../CLAUDE.md](../CLAUDE.md).

O lado do port é o `we2002_golden_tool.exe` do preset `windows-release`
(MSVC 19.44), `roundtrip` sobre a outra cópia — Load+Save sem editar nada, que
é exatamente o que o clique em `Write into CD image` faz do outro lado.

```
tools/golden_compare.py work/g1-oracle.bin work/g1-port.bin
1 run(s), 15 byte(s) differ

     start        end    span    diff  sector      kind  region
---------------------------------------------------------------
    405724     405739      16      15     172      data  OFS_SQUAD_NUMBERS_NATIONAL+1008
```

**Passou.** A única divergência é a faixa conhecida — o slot 64 de um array de
63, que o original lê e grava a partir da memória vizinha. Nenhuma outra.

Duas medidas que saíram de brinde:

- **`ed.exe` carrega essa imagem sem reclamar de nada.** O `CMB_NSQUADRE` sai
  com **97 times**, e nenhum modal apareceu no caminho — nem o aviso de tamanho.
- **Abrir não altera a imagem.** Uma terceira cópia foi aberta e fechada **sem**
  clicar em gravar: `cmp` contra a original em `roms/` dá igual, byte a byte.

O segundo item encerra uma observação solta de uma corrida anterior não
controlada, que parecia dizer o contrário. O que ela via era a **gravação**: o
diff da cópia gravada hoje contra a original em `roms/` dá exatamente os mesmos
**56 bytes em 6 faixas** daquela observação — `OFS_PLAYER_NAME_7+471`,
a faixa conhecida, três em `OFS_PLAYER_ATTR_8` e `OFS_KICKER+384`. As duas
últimas são as duas não-idempotências que o
[../CLAUDE.md](../CLAUDE.md) já descreve: o `Save` reconstrói as all-star a
partir dos links, e troca os dois primeiros cobradores de cada clube de ML.

Fica de fora, e é registro honesto: o `golden_gui` — a metade que põe a janela
Qt no lugar do core — **não** correu no Windows. Ele dirige widget Qt por
`xdotool`, e widget Qt não é controle nativo: não há `GetDlgItem` para pegar.
Essa metade continua sendo do Linux.

### 8.2 Portão 2 — a camada de dados

```
python3 wte/tools/compare_dumps.py --medir
```

| rom | linhas_dump | divergencias_dump | faixas_rt_vs_original | divergencias_rt_pascal_vs_cpp |
|---|---:|---:|---:|---:|
| european-deluxe | 66.498 | 0 | 4 | **0** |
| japanese | 66.498 | 0 | 15 | **0** |
| **ptbr-remaster** | 66.498 | **0** | 9 | **0** |

**Passou.** O Pascal do `wte/` e o C++ do `we2002_core` leem a mesma coisa nessa
imagem e gravam os mesmos bytes.

As colunas de cobertura confirmam a [§3.2](#32-ela-cobre-os-mesmos-ramos-do-codec-que-a-europeia)
sobre dado medido de novo, não copiado: `kanji_duplo = 95`,
`kanji_decodificado = 95`, `squad_numbers_nao_zero = 64` — os mesmos da
europeia.

**O `fase-3.tsv` versionado não foi tocado.** A corrida foi do Windows, e o
sidecar `_url.txt` sai com CRLF aqui (3.822 bytes contra 1.911) — diferença de
plataforma registrada na §11 do [/docs/PLAN-WINDOWS.md](/docs/PLAN-WINDOWS.md),
e a §6 do [/docs/PLAN-WTE-WINDOWS.md](/docs/PLAN-WTE-WINDOWS.md) proíbe
commitar TSV medido aqui. A evidência versionada continua sendo a do Linux.

### 8.3 O que falta

O portão 3, no Linux, com a mudança de `--rom ptbr` no
[../wte/tools/golden_suite.sh](../wte/tools/golden_suite.sh). É ele que responde
a pergunta de valor: se os 24 roteiros correm com oráculo vivo nessa imagem, ela
compra o que nenhuma das duas atuais compra.

---

## 9. O que já mudou, e não depende desta decisão

- A imagem foi renomeada para `ptbr-remaster.bin`, e o `FILE` do `.cue`
  corrigido — apontava para um nome que não existia no disco.
- `roms/copadomundo2002.bin` **foi removida** (para a Lixeira). Ela não é
  WE2002 na região que importa: os nomes de time leem bem no offset certo, mas
  a região de vínculo de Master League traz `b0` até **252** numa tabela que
  define **120** times, e o editor do Obocaman morre com `0xc0000005` **na
  carga**, antes da janela principal. No port Lazarus, que não reproduz o
  estouro, ela abre e mostra o estrago: `20 Hungria` com `Nome1 GALES`, números
  de camisa repetidos, `SPC 410`. Nenhuma ferramenta a citava.
