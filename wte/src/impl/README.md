# `src/impl/` — os corpos de handler escritos à mão

Da [WTE-TASK-25](../../../docs/tasks/25-handlers-de-carga.md) em diante. É o
**único** conteúdo escrito à mão que entra nas 18 unidades `ep2002_*.pas`.

O problema que esta pasta resolve: os `ep2002_*.pas` são saída do
[`dfm2lfm.py`](../../tools/dfm2lfm.py) e o cabeçalho de cada um diz **NÃO
EDITAR À MÃO**; `make -C wte check` prova isso a cada rodada. Mas corpo de
handler não é coisa que gerador saiba escrever — ele sai da spec de
[`../../re/spec/`](../../re/spec/), uma a uma, como manda a §2 do plano. Editar
o `.pas` gerado para pô-los ali quebraria a regra que o próprio arquivo
anuncia.

Então o corpo mora fora, e o gerador só o **referencia**:

| Arquivo | O que é |
|---|---|
| `<unidade>.<handler>.inc` | o corpo, do `var`/`begin` até o `end;` |
| `<unidade>.uses` | uma unidade por linha, acrescentada ao `uses` da unidade; `#` comenta |

O gerador emite a assinatura — que é mecânica, vem da tabela `ASSINATURAS` e do
DFM — e logo abaixo `{$I impl/<arquivo>.inc}`. O `.inc` começa no `var` (ou
direto no `begin`) porque `{$I}` **dentro** de um `begin..end` não poderia
declarar local.

Handler sem `.inc` continua saindo como stub `REStub`, e é assim que o índice
de `re/spec/` e o gerador contam a mesma coisa por caminhos diferentes.

**Nome errado aborta o gerador.** `.inc` que não corresponde a handler
publicado nenhum viraria stub em silêncio, e o sintoma seria "o handler não faz
nada" — diagnóstico que manda procurar no lugar errado.
