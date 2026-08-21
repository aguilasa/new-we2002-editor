---
handler: imagen_urlClick
formulario: ficha_about
endereco: 0x00402de8
veredito: implementado
---

# ficha_about.imagen_urlClick

Clicar no banner da W11 Online abre o site no navegador. O handler não sabe a
URL: ele **encaminha para a ação do botão vizinho**.

**Evidência:** disassembly lido

## Entrada

O campo `+0x2F8` da instância, que o [`campos.tsv`](../campos.tsv) nomeia
`SpeedButton1` (`TSpeedButton`). O `Sender` não é olhado.

**Evidência:** disassembly lido

## Saída

```text
acao := SpeedButton1.Action          ' TControl::GetAction, VMT +0x3C
metodo := FindDynaInst(acao, -17)    ' TContainedAction::Execute
metodo(acao)
```

Os três nomes saem do `vcl60.bpl`, não de leitura: o `+0x3C` do VMT de
`TSpeedButton` é `@Controls@TControl@GetAction$qqrv`, o `0x004219ac` do `.exe`
é um `jmp` para `@System@@FindDynaInst$qqrv`, e o índice dinâmico `-17` está na
tabela de métodos dinâmicos de `TContainedAction` apontando para
`@Actnlist@TContainedAction@Execute$qqrv`.

A ação é a `lanza_url`, um `TBrowseURL` do `ActionList1` cujo `.dfm` traz
`URL = 'http://www.w11.com.br         '` — com os nove espaços à direita.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Nenhuma chamada de escrita, e o handler nem abre a imagem.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma conferência. Se o `SpeedButton1` não tivesse ação, o `GetAction`
devolveria nulo e o `FindDynaInst` estouraria — mas o `.dfm` amarra
`Action = lanza_url` em tempo de projeto.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. O `TBrowseURL` da VCL entrega a URL ao `ShellExecute`, e o que o
navegador faz com ela não volta para o app.

**Evidência:** disassembly lido

## Notas

**A LCL não tem `TBrowseURL`**, e a
[WTE-TASK-10](../../../docs/tasks/10-conversor-dfm-para-lfm.md) já tinha
resolvido metade disto: o `dfm2lfm.py` converte a ação num `TLabel` inerte e
guarda o valor na constante `LANZA_URL_URL` da unidade, com um `TODO` pedindo
`OpenURL()` no handler que dispara. Este é o handler que dispara, e o `TODO`
fecha aqui.

**O port passa a URL por `Trim`.** Os nove espaços à direita são inofensivos
para o `ShellExecute` do Windows e não são para o `xdg-open`, que os leva para
dentro do argumento. Aparar preserva o *efeito* — abrir
`http://www.w11.com.br` — em vez da forma do argumento, e não toca a imagem de
CD nem nada que o golden meça.
