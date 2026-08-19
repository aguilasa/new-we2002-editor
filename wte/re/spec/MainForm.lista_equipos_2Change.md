---
handler: lista_equipos_2Change
formulario: MainForm
endereco: 0x0040e1a8
veredito: aberto
---

# MainForm.lista_equipos_2Change

O irmão de [`lista_equiposChange`](MainForm.lista_equiposChange.md) para a
**segunda** lista de times — o time reserva, de onde saem os jogadores que a
tela move para o titular. 348 bytes contra 1.536: ele faz bem menos.

## Entrada

- `lista_equipos_2.ItemIndex`, e `lista_equipos.ItemIndex` para comparar os
  dois;
- a imagem, através da rotina de preenchimento de lista em `0x0040b2d8`, a
  mesma que o `lista_equiposChange` usa.

**Evidência:** disassembly lido

## Saída

```text
se lista_equipos_2.ItemIndex = -1: sai
help_team.Enabled := verdadeiro
0x0040b2d8(lista_equipos_2, lista_jugadores_2)   ' enche a lista do reserva
lista_jugadores_2.Enabled := verdadeiro ; ItemIndex := 0
mostrar_jugador_2, mostrar_estrategia_2, pabajo  .Enabled := verdadeiro
se lista_equipos_1.ItemIndex >= 0:
    os cinco botões de troca (paderecha, paderecha2, paizquierda,
    paizquierda2, paderechaeizquierda) .Enabled := verdadeiro
se lista_equipos_2.ItemIndex < 95:
    se lista_equipos_2.ItemIndex <> lista_equipos_1.ItemIndex:
        0x00405468(...)                    ' desenha a bandeira do reserva
    senão:
        banderita2.Picture := bandera.Picture
    banderita2.Visible := verdadeiro
senão:
    banderita2.Visible := falso
```

**Os controles sem nome foram resolvidos na oitava passagem**, cruzando os
deslocamentos do corpo com o [`../campos.tsv`](../campos.tsv): `help_team`,
`lista_jugadores_2`, `mostrar_jugador_2`, `mostrar_estrategia_2` e `pabajo`.

**E uma correção veio junto:** o teste é contra **`lista_equipos_1`**, não
contra `lista_equipos`. Os dois andam juntos — o `lista_equiposChange` espelha
a seleção de um no outro —, então o efeito é o mesmo, mas quem o corpo lê é o
`_1`. A redação anterior era leitura de intenção, não de campo.

O `<>` entre as duas listas é o detalhe que vale registrar: quando os dois
lados são o **mesmo** time, o original não redesenha — copia a bandeira já
pronta do `bandera`. É otimização, não comportamento diferente, e o port pode
fazer os dois caminhos iguais sem divergir na tela.

O `95` tem o mesmo significado do handler irmão: é o índice do modelo de Master
League, não o número de times.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum** neste corpo, e nenhuma **escrita** em `0x0040b2d8` — a rotina
compartilhada só lê. A forma dela está medida em
[`../auxiliares.md`](../auxiliares.md): recebe a lista de times e a lista de
jogadores, esvazia a segunda e a preenche com 23 nomes lidos da imagem,
atravessando fronteira de setor por `0x00403388`. A aritmética que localiza
cada nome passa por `0x00404374`, 881 bytes, ainda não lida.

**Evidência:** disassembly lido

## Pré-condições

`ItemIndex = -1` sai imediatamente. Os cinco botões de troca só são habilitados
se a **outra** lista também tiver seleção — é o par simétrico do teste que o
`lista_equiposChange` faz sobre esta.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**Veredito `aberto` pela mesma razão do irmão:** o corpo depende de
`0x0040b2d8` (preencher lista de jogadores) e de `0x00405468` (desenhar
bandeira, que é da
[WTE-TASK-29](../../../docs/tasks/29-camisa-e-bandeira-2d.md)).

**Os dois argumentos de `0x0040b2d8` são combos, e é isso que explica os dois
chamadores.** O primeiro é a lista de times de onde sai o índice, o segundo é a
lista de jogadores que ele esvazia e enche — este handler passa o par reserva,
o `lista_equiposChange` passa o par titular. Uma rotina, duas metades da tela.

**O Pascal está escrito**, em
[`../../src/impl/ep2002_mainform.lista_equipos_2Change.inc`](../../src/impl/ep2002_mainform.lista_equipos_2Change.inc),
e reusa os auxiliares do lado titular — é a mesma `PreencheJogadores`, com a
outra lista, exatamente como no original, onde `0x0040b2d8` recebe as duas
listas como argumento e por isso tem dois chamadores.

**Veredito `aberto` até a conferência de tela alcançar o lado reserva.** O
[`compara_tela.sh`](../../tools/compara_tela.sh) dirige hoje só o combo
titular; para julgar este handler ele precisa dirigir também o
`lista_equipos_2`. O recorte já não é obstáculo: desde a
[CORR-WTE-057](../../../docs/tasks/CORR-WTE-057.md) a montagem sai da janela
inteira, e a metade de baixo — a `lista_jugadores_1` e os 23 dorsais — está
nela. Falta a navegação. Enquanto ela não existir, o corpo está escrito a
partir de spec medida e **não** verificado
contra o original — e foi justamente a conferência de tela que achou os dois
erros de mapeamento do handler irmão.
