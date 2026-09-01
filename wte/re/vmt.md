# Chamada virtual da VCL — a rota escolhida e o teste que a decidiu

Produto da [WTE-TASK-24](../../docs/tasks/concluidos/24-ghidra-convencao-borland.md).
Referência: `PLAN-WTE-LAZARUS.md` §8.1, §8.2, §8.3.

Todo número deste arquivo saiu de `wte/tools/ghidra/vmt_probe.java` e de
`decompile_one.java`, rodando sobre o projeto que o `run_headless.sh` monta —
**inclusive os votos da âncora**, que até a
[CORR-WTE-054](../../docs/tasks/concluidos/CORR-WTE-054.md) eram os dois únicos calculados
fora. Nenhum veio de leitura de decompilado, e **nenhum trecho decompilado foi
colado aqui** — recuperação de especificação, não transcrição (§2, §8.10).

---

## Antes de tudo: a convenção pegou

A §8.1 chama a convenção Borland de "a pior armadilha do projeto, e ela aparece
na primeira função". Ela está resolvida, e mais barato do que o plano supunha —
ver [`../tools/ghidra/borland_cc.md`](../tools/ghidra/borland_cc.md).

Prova, medida:

```
decompile_one: MainForm__colorearClick @ 00410ea8
decompile_one: convencao  = __fastcall
decompile_one: assinatura = undefined MainForm__colorearClick(int param_1)
decompile_one: parametros = 1
```

**Um parâmetro, não zero.** É esse o teste: sem o compiler spec de Borland o
Ghidra reportaria `colorearClick(void)` lendo lixo de `EAX`, que é o ruído
convincente da §8.1.

---

## O padrão da §8.2

```asm
mov   ecx,DWORD PTR [eax]
call  DWORD PTR [ecx+0xcc]
```

`+0xcc` é slot de VMT da VCL, e o binário não diz de quem. As duas saídas do
plano:

1. **Reconstruir o VMT** a partir de `vcl60.bpl`, que está na pasta e exporta os
   nomes mangled. Trabalhoso, resolve de uma vez.
2. **Inferir pelo contexto** — o objeto veio de `[ebx+0x390]`, e o DFM diz qual
   componente é.

O plano recomenda começar por (2). O teste desta task foi feito para decidir.

---

## O teste

### Escala medida, nos 37 handlers do `MainForm`

| Medida | Valor |
|---|---|
| Chamadas virtuais nos handlers do `MainForm` | **217** |
| …com o campo de objeto recuperado do contexto | **189** (87%) |
| Campos distintos tocados | **41** |
| Extensão da corrida de campos | `+0x2f0` a `+0x4b0` = **113** slots de 4 bytes |
| Componentes do `MainForm` no DFM | **116** (o formulário + 115 filhos) |
| Slots de VMT distintos | **10** |

Os slots, por frequência:

| Slot | Vezes |
|---|---|
| `+0xc8` | 97 |
| `+0xe8` | 28 |
| `+0xcc` | 22 |
| `+0x64` | 39 |
| `+0x88` | 10 |
| `+0xc`, `+0x20` | 6 cada |
| `+0x3c` | 5 |
| `+0xc0` | 3 |
| `+0x80` | 1 |

**Dez slots cobrem 217 chamadas.** Isso é o que torna a rota (2) atraente: não é
preciso reconstruir um VMT inteiro, são dez perguntas.

### As cinco chamadas — `colorearClick`, que tem oito

| # | Endereço | Objeto vem de | Slot |
|---|---|---|---|
| 1 | `00410ecf` | `[0x00433dbc] + 0x394` | `+0xcc` |
| 2 | `00410ee9` | `[0x00433dbc] + 0x394` | `+0xcc` |
| 3 | `00410f03` | `[0x00433dbc] + 0x394` | `+0xcc` |
| 4 | `00410f11` | `[EBX + 0x390]` | `+0xc8` |
| 5 | `00410f2f` | `[0x00433dbc] + 0x398` | `+0xc8` |
| 6 | `00410f48` | `[0x00433dbc]` (o próprio formulário) | `+0xe8` |
| 7 | `00410f6d` | `[EBX + 0x384]` | `+0xc8` |
| 8 | `00410f7d` | `[EBX + 0x384]` | `+0xc8` |

`0x00433dbc` é o ponteiro global do formulário — a VCL declara um por form —, e
`EBX` é o mesmo objeto já em registrador. Os dois caminhos dão no mesmo campo.

**Resultado: 8 de 8 com campo e slot recuperados.** A metade mecânica da
inferência funciona, e funciona em escala (189 de 217).

---

## Onde a inferência **não** fecha, e isto é o achado

A rota (2) tem duas metades:

1. do disassembly, tirar **qual campo** do formulário guarda o objeto — ✅ 87%;
2. do campo, dizer **qual componente** ele é — ❌ **não fecha pela posição no
   DFM**.

A premissa da metade 2 é que os campos publicados formam uma corrida contígua de
ponteiros de 4 bytes na ordem do DFM. **A corrida existe:** `+0x2f0` a `+0x4b0`
são 113 slots de 4 bytes contra 115 componentes filhos — bate, com folga de dois.
O que falta é a **âncora**: o deslocamento do primeiro campo.

Tentou-se ancorar pelo dono de cada handler — o `published_methods.tsv` diz de
que componente cada handler é, o DFM dá a posição daquele componente, e
`base = campo − 4·(posição−1)` deveria convergir. **Não convergiu**, e quem
mede isso é o próprio `vmt_probe.java`, com a raiz do repositório no segundo
argumento:

```
vmt_probe: ANCORA: 115 componente(s) no MainForm.dfm, 37 handler(s) com dono no TSV
vmt_probe: ANCORA: 108 referencia(s) de campo dentro da corrida votaram (9 sem posicao no DFM)
vmt_probe: ANCORA: 69 candidato(s) a base; os cinco mais votados:
  base +0x260  4 voto(s)
  base +0x264  4 voto(s)
  base +0x290  4 voto(s)
  base +0x268  3 voto(s)
  base +0x26c  3 voto(s)
vmt_probe: ANCORA: 1o e 2o colocados a 4 byte(s) um do outro
```

**69 candidatos para 108 votos, e o mais votado tem 4.** Uma âncora que fechasse
teria um candidato com dezenas. Os "9 sem posição no DFM" são handlers cujo dono
não é componente filho — `FormCreate` e `FormShow` são do próprio formulário.

Três causas, as três visíveis nos dados:

- **Handler não toca necessariamente o próprio componente.** `colorearClick` é o
  `OnClick` de `colorear`, e não lê `colorear`: lê os quatro campos que ele vai
  pintar. A hipótese que a âncora assume é falsa na maioria dos casos.
- **Aninhamento.** A ordem plana do texto do DFM não é obrigada a ser a ordem de
  declaração dos campos quando há `TGroupBox` com filhos, e o `MainForm` tem 10
  group boxes. O empate a 4 bytes entre os dois primeiros candidatos tem
  exatamente essa cara.
- **Componente sem `Name`.** O `MainForm.dfm` tem 117 linhas `object` e **115**
  componentes nomeados: uma é o formulário e outra é um `object TStaticText`
  sem nome (linha 330). Componente anônimo entra na contagem de componentes e
  **não** ganha campo publicado, então qualquer posição contada por linha de
  `object` erra em 1 dali para a frente. O script conta os nomeados, por isso.

Sinal de que a corrida é real, apesar disso: `paderecha`, `paderechaeizquierda`
e `paizquierda` são componentes **vizinhos** no DFM, e os campos que os
respectivos handlers tocam são `+0x384`, `+0x388` e `+0x38c` — vizinhos também,
com passo 4.

---

## A rota escolhida

**Rota 2, inferência pelo contexto** — mas com a âncora vinda de outro lugar que
não a posição no DFM.

Por quê, e não a rota 1: reconstruir o VMT do `vcl60.bpl` resolveria a
identidade da **classe**, e não é a identidade da classe que falta. O que falta
é *qual dos 115 componentes* é o campo `+0x390`, e isso o VMT não diz —
componentes da mesma classe compartilham VMT. A rota 1 custaria o trabalho todo
e não responderia a pergunta que sobrou.

E, principalmente, porque a §4.2 já manda **diff antes de decompilador**: para o
que a fase 4 precisa saber — *que bytes esta operação grava* — o par (campo,
slot) mais o diff dirigido responde sem identificar componente nenhum.

### A âncora, quando for precisa

O caminho barato, e ele não é decompilação: a VCL grava o **`Name`** de cada
componente, e o construtor do formulário registra os componentes em ordem. Um
único par (campo, nome) fixa a base e resolve os 115 de uma vez. Fica para a
WTE-TASK-25, que é quem primeiro precisa nomear componente em spec de handler.

**Até lá, spec de handler cita `campo +0xNNN` e `slot +0xNN`, não nome de
componente inferido.** Nome inferido sem âncora seria exatamente o "ruído
convincente" que a §8.1 manda evitar, só que uma camada acima.

---

## Como refazer

```sh
bash wte/tools/ghidra/run_headless.sh                        # importa e nomeia
bash wte/tools/ghidra/run_headless.sh --decompile colorearClick
```

O `vmt_probe.java` roda pelo `analyzeHeadless`; ele imprime a tabela de campos,
a de slots, os campos por handler — a entrada da tentativa de âncora — e, com a
raiz do repositório no **segundo argumento**, a votação da âncora em si:

```sh
GHIDRA=$HOME/.local/opt/ghidra_12.1.2_PUBLIC
"$GHIDRA/support/analyzeHeadless" work/ghidra wte \
  -process we-team-editor.exe -noanalysis \
  -scriptPath "$PWD/wte/tools/ghidra" \
  -postScript vmt_probe.java MainForm "$PWD" \
  -readOnly
```

Sem o segundo argumento ele avisa que a votação não rodou, em vez de calar.
