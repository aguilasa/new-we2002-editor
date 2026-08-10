# `re/crash-causa.md` — por que o `wte.exe` morre ao trocar de time

**Escrito à mão.** Produto da CORR-WTE-044. O [`crash.md`](crash.md) é gerado e
chega até *qual instrução faltou*; este arquivo responde *por quê*, e todo
endereço abaixo vem de comando, não de leitura do Ghidra transcrita.

As duas ferramentas que refazem tudo o que está aqui:

```sh
python3 wte/tools/sonda_dorsal.py --check        # os deslocamentos de campo
python3 wte/tools/sonda_dorsal.py wte/tests/roteiros/08-so-troca-de-time.txt \
        --vizinhanca                             # a corrida, sobre cópia
```

## A resposta

O controle **existe**. O ponteiro é que não é ponteiro.

A rotina privada de `0x0040b188` guarda em `0x004335e4` o `dorsalN` realçado
no momento, e ao entrar de novo devolve o anterior ao normal. Ela testa
`if (obj != nil)` antes de mexer — e o que está lá quando a imagem é a
`golden-european-deluxe.bin` é **`0x00010001`**, que passa no teste e não é
objeto nenhum. `[0x00010001 + 0x68]`, onde estaria o `TFont`, lê zero, e
`Graphics::TFont::SetSize(nil, 8)` morre em `[nil+0x1c]`.

Quem põe `0x00010001` ali não é a rotina: é a **carga do time**, que preenche
uma tabela de pares de 16 bits em `0x00433580..0x004335bf` e, com esta imagem,
escreve **além do fim dela**. Com a `japanese-shift-jis.bin` a mesma carga
escreve a mesma tabela, para no fim, e o `wte.exe` **não cai**.

## As quatro perguntas da correção

### 1. O campo em `+0x68` é mesmo `TControl.FFont` nesta VCL? — **sim**

Medido no `vcl60.bpl`, não de memória. `TControl::SetFont` lê `[this+0x68]` e
chama um método virtual do que achou ali:

```sh
objdump -d --start-address=$((0x400a0000+0x55efc)) \
           --stop-address=$((0x400a0000+0x55f08)) we-team-editor/vcl60.bpl
```

```text
400f5efc: 56              push %esi
400f5efd: 8b f0           mov  %eax,%esi
400f5eff: 8b 46 68        mov  0x68(%esi),%eax     <-- FFont
400f5f02: 8b 08           mov  (%eax),%ecx
400f5f04: ff 51 08        call *0x8(%ecx)
```

Os vizinhos confirmam a classe: `TControl::SetLeft` lê `+0x44`, `+0x48` e
`+0x4c` para remontar os limites, e `TControl::SetColor` grava `+0x70`. O mapa
que a rotina de realce usa é, então, `+0x40` `FLeft`, `+0x44` `FTop`, `+0x48`
`FWidth`, `+0x4c` `FHeight`, `+0x68` `FFont`, `+0x70` `FColor` — e é
exatamente esse o conjunto de campos que ela lê.

O `--check` da sonda refaz esta conferência sozinho, e refaz também as três de
`rtl60.bpl` que sustentam o censo da pergunta 2 (`TComponent.FName` `+0x08`,
`TComponent.FComponents` `+0x10`, `TList.FList` `+0x04`, `TList.FCount`
`+0x08`).

### 2. De onde vem o `N` de `"dorsal" + N`? — **não vem da imagem**

A rotina recebe `N` na pilha (`0x8(%ebp)`) e o formata com `%i` (o literal está
em `0x004324cf`) antes de concatenar com `'dorsal'` (`0x00424c7b`). Os quatro
chamadores, desmontados:

| chamador | como calcula o `N` |
|---|---|
| `lista_equiposChange` (`0x0040d339`) | `push $0x1` — **constante 1** |
| `lista_jugadores_1Change` (`0x0040f8cb`) | `ItemIndex + 1` da lista de jogadores |
| `dorsalClick` (`0x00410b2f`) | número extraído do **próprio nome** do controle |
| `dorsalMouseDown` (`0x00410e7b`) | idem |

O que trava é o primeiro, e ele pede sempre `dorsal1`. Nenhum dado da imagem
entra no nome procurado.

E o controle procurado está lá. O censo da lista de componentes do `MainForm`,
lido do processo vivo, fecha em **23 `dorsal*`, todos `TStaticText`, todos com
`Font` não nula**, e fica assim até o fim da sessão:

```text
   7.42s  MainForm=0x01644d2c  componentes=116  dorsal*=23  sem_Font=[]
```

Com isso cai a leitura que o `crash.md` tinha deixado em aberto — *por que este
controle não existe*. Ele existe; `FindComponent` teria achado. A pergunta
certa era outra.

### 3. Quem escreve no global `0x004335e4`? — **a carga do time, por engano**

No `.text` há **sete** referências ao endereço, e só uma delas é escrita: o
`mov %eax,(%ebx)` de `0x0040b241`, dentro da própria rotina de realce, com o
retorno de `FindComponent`. As outras seis são leitura (`0x00408aae`,
`0x00410ad4`, `0x00410b7e`, `0x00410bff`, `0x00410da3`, `0x00410e1f`).

Só que ao vivo **não é essa escrita que põe o valor lá**. O global sai de zero
direto para `0x00010001`, sem nunca passar por um ponteiro válido — e no mesmo
instante uma faixa inteira de `.data` muda junto:

```text
  18.14s  .data mudou:
    0x00433580  0x0 -> 0x00010001
    ...                                (16 palavras contíguas)
    0x004335bc  0x1 -> 0x00010001
    0x004335c0  0xf5 -> 0x0000000d
    0x004335e4  0x0 -> 0x00010001  <== o global
    0x00433624  0x0 -> 0x00010001
    0x00433628  0x0 -> 0x00010001
```

`0x00433580..0x004335bf` são 16 palavras de pares de 16 bits (`0x00010001`,
`0x00010002`, `0x00020001` — valores 1 e 2), e `0x004335c0` é o contador que
anda junto. Nenhum desses endereços tem referência absoluta no `.text`: a
tabela só é alcançada por índice, o que é o que se espera de vetor global.

**As duas leituras que a correção pôs lado a lado se resolvem aqui.**
`FindComponent` devolvendo componente que não é `TControl` está **refutada** —
os 23 estão vivos e são `TStaticText`. Sobra a segunda: escrita além do fim de
um vetor vizinho. E ela deixou de ser hipótese, porque a mesma medição contra a
outra imagem mostra a tabela parando onde deve.

### 4. Existe condição de entrada que evita o caminho? — **existe: a imagem**

Mesmo roteiro, mesma condução, mesmas marcas (`ARRANQUE`, `SELECIONA_TIME`,
`FIM`), só a imagem muda:

| imagem | `[0x004335e4]` depois da troca | violações de acesso |
|---|---|---:|
| `roms/golden-european-deluxe.bin` | `0x00010001`, `classe=None`, `Font=0` | **49 749** |
| `roms/japanese-shift-jis.bin` | `0x01659dac`, `classe=TStaticText`, `Font=0x1659fc8` | **0** |

A linha da japonesa é a rotina funcionando: `FindComponent("dorsal1")` achou,
`0x0040b241` guardou, e o realce seguiu sem exceção. Refeito duas vezes, com o
mesmo resultado.

E na japonesa a tabela **para no fim**: a faixa escrita vai de `0x00433580` a
`0x004335c0` e não toca `0x004335e4`, `0x00433624` nem `0x00433628` — os três
endereços que a europeia atropela.

Duas coisas que **não** explicam a diferença, as duas medidas:

- **Não é a região vazia em `14368636`.** As duas imagens leem exatamente as
  mesmas faixas durante `SELECIONA_TIME`, essa inclusive (`io.tsv` das duas
  corridas; a única diferença é uma leitura que a japonesa parte em duas na
  fronteira de setor). A candidata que a WTE-TASK-19 deixou aberta e o
  `crash.md` promoveu a *causa da causa* cai por aqui: mesmo endereço lido,
  travamento num caso só.
- **Não é o tamanho do arquivo.** Já tinha caído na WTE-TASK-19, por
  experimento.

## O desfecho

**Condição de contorno achada.** O oráculo A é dirigível — com
`roms/japanese-shift-jis.bin`. É o desfecho positivo dos dois que a
CORR-WTE-044 previu, e ele desfaz a circularidade: a
[WTE-TASK-22](../../docs/tasks/22-harness-golden.md) não precisa mais do
`lista_equiposChange` entendido para montar o gate, e a
[WTE-TASK-19](../../docs/tasks/19-os-50-offsets-restantes.md) volta a poder
levar o editor além da tela de carga.

Três ressalvas que vão junto, e nenhuma é pequena:

1. **A imagem golden do `newWe2002` não serve de golden aqui.** Quem montar o
   gate da 22 tem de fixar a japonesa, e dizer no arquivo por quê — senão o
   próximo a rodar troca a imagem por hábito e recebe 49 mil violações de
   acesso achando que quebrou o harness.
2. **A japonesa não tem `.cue` e não é de jogar** (ver `CLAUDE.md`). Para o
   gate isso é indiferente: ele compara bytes.
3. **Não está provado que a japonesa é imune, só que este caminho é.** O
   estouro é de tabela preenchida com dado do time; outro time, outra tela,
   outro contador podem alcançar o mesmo endereço. O gate da 22 deve tratar
   violação de acesso no `wine.log` como falha do lado do oráculo, e não
   silenciá-la.

## O que não foi respondido

**Qual instrução escreve `0x004335e4`.** Sei *de onde* vem (a carga do time,
por índice, junto com a tabela de `0x00433580`) e sei que **não** é a rotina de
realce. Nomear a instrução pede um watchpoint de hardware, e o
`ptrace_scope=1` desta máquina só deixa tracear descendente: o `gdb` teria de
lançar o Wine, e o endereço só existe depois do PE mapeado, quando já não dá
para pôr o watchpoint pela linha de comando. Não foi tentado porque o desfecho
não depende disso — o contorno da pergunta 4 já destrava a fase 4.

**Fica registrado como o próximo passo natural**, para quem for implementar a
carga do time (WTE-TASK-25): a tabela de `0x00433580` e o contador de
`0x004335c0` são estrutura de dados do handler, e o port não deve reproduzir o
estouro.

## Uma nota sobre a contagem de violações

O [`crash.md`](crash.md) registra **309** violações na sessão
`so-troca-de-time`. As corridas desta correção deram **49 749** com o mesmo
roteiro e a mesma imagem. Não há contradição: a primeira exceção é a única que
localiza, e o manipulador do próprio app reentra em laço depois dela, então o
número mede **quanto tempo o processo ficou vivo**, não o defeito. O que separa
as sessões é zero contra não-zero — e é assim que o `sonda_dorsal.py` avisa ao
terminar.
