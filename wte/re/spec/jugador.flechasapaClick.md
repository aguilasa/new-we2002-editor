---
handler: flechasapaClick
formulario: jugador
endereco: 0x00408088
veredito: divergencia deliberada
---

# jugador.flechasapaClick

O despachante das doze setas de **aparência** da ficha do jogador — posição,
tom de pele, cabelo, barba, altura, idade, pé, e mais quatro. **981 bytes**,
mais a `0x00408460` (143 B), que é a única auxiliar dele ainda não lida antes
desta passagem; as outras três são as carregadoras de bitmap da
[§5 de `assets.md`](../assets.md).

Ligado aos doze `flechasapa1..12`, todos `TUpDown`, todos por `OnClick`.

## Entrada

- **`Sender.Name`**, cortado em `SubString(11, 2)` — `flechasapa` tem dez
  letras, então a posição 11 é o primeiro dígito e o corte de dois pega tanto
  `1`..`9` quanto `10`..`12`. É o mesmo desenho dos dois `barrhab*Scroll`,
  onde o corte é de um dígito num e de dois no outro; aqui um só corte serve
  os doze porque o despacho compara **cadeia**, não número.
- **`Sender.Position`**, e nos três casos especiais o campo do formulário
  (`jugador+0x434`, `+0x43c`, `+0x424`) em vez do `Sender` — o mesmo objeto.

**Evidência:** disassembly lido

## Saída

**São dois despachantes em fila, não um.** O primeiro escreve o rótulo, o
segundo redesenha os bitmaps, e todo caminho do primeiro cai no segundo.

```text
sufixo := SubString(Sender.Name, 11, 2)

' --- primeiro: o rotulo ---
se sufixo = '7'  entao valorapa7.Caption := IntToStr(flechasapa7.Position + 148)
senao se '9'     entao valorapa9.Caption := IntToStr(flechasapa9.Position + 15)
senao se '3'     entao valorapa3.Caption := TABELA_CABELO[flechasapa3.Position]
senao
    alvo := FindComponent('valorapa' + sufixo)
    linha := Variant(sufixo) - 1                 ' a 0x00408460
    alvo.Caption := TABELA_FICHA[linha][Sender.Position]

' --- segundo: os bitmaps ---
se sufixo = '2' entao 0x406fe0 ; 0x407110 ; 0x407338   ' careto, pelo, barba
se sufixo = '3' ou '4' entao 0x407110                  ' pelo
se sufixo = '5' ou '6' entao 0x407338                  ' barba
```

**`0x00408460` é a conversão do sufixo em índice de linha.** Ela monta dois
`Variant` — um da cadeia, um do literal `1` —, subtrai e devolve; o chamador
extrai o inteiro e multiplica por `0x20`, que é o passo da tabela. Escrito
assim, e não como um `StrToInt`, porque o C++Builder resolve
`Variant("10") - 1` sem o autor precisar decidir o tipo.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum na imagem de CD.** O inventário de chamadas dos 1.124 bytes não
alcança nenhuma das duas escritoras (`0x00403400`, a de bytes, e
`0x00404048`, a de número de camisa). O que a seta muda fica no formulário
até alguém gravar.

**Mas ele escreve em disco assim mesmo, e isso não é detalhe.** As três
carregadoras de bitmap abrem o `.bmp` em `"r+b"` e **regravam a paleta dentro
do arquivo de asset** antes de recarregá-lo — `image/careto_base.bmp`,
`image/pelo/pelo_<n>.bmp`, `image/barba/barba_<n>.bmp`. Mexer numa seta de
cabelo altera o arquivo compartilhado por todos os jogadores. Medido na
[§6 de `assets.md`](../assets.md), com a marca de `mtime` da pasta do usuário
como prova.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma. Não confere se há jogador carregado.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Sufixo que não case com nenhum literal cai no ramo genérico, e um
`FindComponent` que devolva `nil` estouraria ali — não acontece porque os doze
`valorapa` existem no formulário.

**Evidência:** disassembly lido

## Notas

### As duas tabelas de legenda, e por que elas precisaram de ferramenta

Nove dos doze controles não mostram número: mostram palavra, buscada em
`0x00423798` — um `AnsiString[12][8]` indexado por `[sufixo − 1][Position]`.
**Essa tabela é zero no disco**, montada em tempo de execução pelo
inicializador da unidade. `flechasapa3` tem faixa de 32 e não cabe numa linha
de 8, então tem tabela própria logo depois, em `0x00423918`.

As duas saem do
[`dump_legendas.py`](../../tools/dump_legendas.py) → [`legendas.md`](../legendas.md).
O que a ferramenta acrescenta sobre transcrever à mão é a **posição**: as
cadeias apareceriam num `strings`, mas qual vai em qual slot só está na ordem
das chamadas ao construtor.

**A atribuição "linha `n` = `flechasapa n+1`" não está escrita no binário** —
sai dessa ordem. O que a sustenta é uma segunda medida, de outra fonte: para
cada uma das doze linhas, a contagem de células com texto bate exatamente com
`Max + 1` do controle no `.dfm`, e as três linhas vazias são exatamente os três
controles de faixa maior que 8. O gerador **aborta** se isso deixar de valer.

### O veredito passou a `divergencia deliberada` em 2026-08-24

**A decisão que ele esperava foi tomada em 2026-08-18, e o veredito não
acompanhou.** A [CORR-WTE-063](../../../docs/tasks/concluidos/CORR-WTE-063.md) levou as
três carregadoras de bitmap para a
[WTE-TASK-35](../../../docs/tasks/concluidos/35-divergencias-deliberadas.md) como
**exclusão deliberada** — elas abrem o `.bmp` em `"r+b"` e regravam a paleta
dentro do arquivo de asset compartilhado, e reproduzir isso poria o port
gravando na pasta de dados do usuário toda vez que alguém encostasse numa seta.

Não falta medida nem código: o despachante está portado, os doze rótulos estão
certos, a exclusão está escrita com a razão, e o efeito no port está descrito
abaixo. `aberto` afirmaria que ainda há pergunta em aberto, e não há —
`divergencia deliberada` é o que o vocabulário tem para "portado, com desvio
consciente e registrado".

O texto abaixo é o registro de quando o veredito era `aberto`, e continua
valendo inteiro como descrição da exclusão.

### O que segurava o veredito

Não é a régua de bytes — este handler não grava na imagem, e a
[WTE-TASK-27](../../../docs/tasks/concluidos/27-handlers-de-gravacao.md) não o alcança.
É a **metade dos bitmaps**: o segundo despachante está portado como estrutura,
mas as três carregadoras (`0x00406fe0`, 301 B; `0x00407110`, 552 B;
`0x00407338`, 561 B — 1.414 somados) ficaram fora da
[WTE-TASK-26](../../../docs/tasks/concluidos/26-handlers-de-edicao.md), que é dona de
handler, e fora da
[WTE-TASK-29](../../../docs/tasks/concluidos/29-camisa-e-bandeira-2d.md), que é dona de
asset mas dos dois do `MainForm` — uniforme e bandeira.

**Elas têm dono desde 2026-08-18, e o dono é uma decisão, não uma
implementação.** A
[CORR-WTE-063](../../../docs/tasks/concluidos/CORR-WTE-063.md) levou as três para a
[WTE-TASK-35](../../../docs/tasks/concluidos/35-divergencias-deliberadas.md) como
**exclusão deliberada**: não serão portadas. A razão é a mesma medida da
[§6 de `assets.md`](../assets.md) — as três abrem o `.bmp` em `"r+b"` e
regravam a paleta dentro do arquivo de asset compartilhado —, e reproduzir isso
poria o porte gravando na pasta de dados do usuário toda vez que alguém
encostasse numa seta.

**O efeito no port, escrito:** as setas de aparência mudam o rótulo e **não**
mudam o desenho. `imagen_base`, `imagen_pelo` e `imagen_barba` mostram o que o
`.bmp` trouxer do disco — inclusive a paleta que a última execução do original
deixou lá, que é o item 2 da §6.2 —, sem o tom de pele, a cor de cabelo nem a
cor de barba do jogador carregado. Os doze rótulos continuam certos, porque
saem das tabelas de legenda e não dos bitmaps.

O campo `veredito` do cabeçalho continua `aberto`: quem o revisa é a passagem de
veredito, não esta correção. O que mudou aqui é que a razão antes escrita —
*falta de dono* — deixou de valer.

### A saturação em `7`, e de quem ela é depois da CORR-WTE-063

`beard_style` e `beard_colour` guardam 3 bits no disco (0..7), o `Max` dos
controles é 6 e só existem `barba_0..6`. O `TUpDown` do original satura em
`Max`, então um 7 vindo do disco vira 6 na tela — e, gravando de volta, vira 6
no disco. Já registrado na §5.1 da [`assets.md`](../assets.md); aparece aqui
porque é este handler que fecha o ciclo.

**Não é da WTE-TASK-29, e deixou de poder ser.** A
[CORR-WTE-063](../../../docs/tasks/concluidos/CORR-WTE-063.md) tirou cara, cabelo e barba
do escopo dela — a 29 continua sendo dona de uniforme e bandeira do `MainForm`
e não ganha nada da ficha. A saturação, porém, **não morre com o desenho**: ela
acontece no `TUpDown`, que o port já tem, e o 7 que vira 6 chega ao disco pela
gravação. O dono é a
[WTE-TASK-27](../../../docs/tasks/concluidos/27-handlers-de-gravacao.md).

**Evidência:** disassembly lido
