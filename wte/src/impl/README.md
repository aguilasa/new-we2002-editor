# `src/impl/` — os corpos de handler escritos à mão

Da [WTE-TASK-25](../../../docs/tasks/concluidos/25-handlers-de-carga.md) em diante. É o
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
| `<unidade>.aux.inc` | rotinas internas compartilhadas, com assinatura própria |
| `<unidade>.uses` | uma unidade por linha, acrescentada ao `uses` da unidade; `#` comenta |

O gerador emite a assinatura — que é mecânica, vem da tabela `ASSINATURAS` e do
DFM — e logo abaixo `{$I impl/<arquivo>.inc}`. O `.inc` começa no `var` (ou
direto no `begin`) porque `{$I}` **dentro** de um `begin..end` não poderia
declarar local.

Handler sem `.inc` continua saindo como stub `REStub`, e é assim que o índice
de `re/spec/` e o gerador contam a mesma coisa por caminhos diferentes.

## `<unidade>.aux.inc` — o que não é handler

Decidido na WTE-TASK-25, quinta passagem. O original chama rotinas internas que
**não são método publicado**, e algumas de mais de um handler: a `0x0040b188`,
que marca a camisa, é chamada pelo `lista_jugadores_1Change` e pelo
`lista_equiposChange`. Um `.inc` por handler não tem onde guardar isso — o
corpo teria de ser duplicado, ou um dos dois handlers viraria dono de uma
rotina que não é dele.

Duas diferenças para o `.inc` de handler, e as duas têm razão:

- ele traz **procedimento inteiro**, com assinatura, e pode declarar `var` de
  unidade — o `.inc` de handler começa no `var`/`begin` porque a assinatura é
  gerada;
- o `{$I}` dele sai **uma vez por unidade, antes de todos os handlers**. Em
  Pascal a ordem de declaração é o que autoriza a chamada, e um handler não
  alcança o que vem depois dele sem `forward`.

As linhas dele contam como escritas à mão no `check_fase2.py`, junto com os
demais `.inc`. Sem isso a fração da §4.4 do plano **subiria** a cada auxiliar
escrito, que é o defeito da
[CORR-WTE-051](../../../docs/tasks/concluidos/CORR-WTE-051.md).

Alternativa descartada: unidade `we2002_*` nova. Esse prefixo é a camada de
dados gerada, e auxiliar que mexe em controle de formulário não é dado.

**Nome errado aborta o gerador.** `.inc` que não corresponde a handler
publicado nenhum viraria stub em silêncio, e o sintoma seria "o handler não faz
nada" — diagnóstico que manda procurar no lugar errado.
