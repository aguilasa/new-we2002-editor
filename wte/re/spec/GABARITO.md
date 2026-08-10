# Gabarito de `re/spec/<formulario>.<handler>.md`

Produto da [WTE-TASK-23](../../../docs/tasks/23-formato-da-spec.md). É o gabarito que
torna executável o método da §2 do
[`PLAN-WTE-LAZARUS.md`](../../../docs/PLAN-WTE-LAZARUS.md): **recuperação de
especificação, não transcrição.** O decompilador responde *perguntas*; a
resposta vem para um destes arquivos; o Pascal é escrito **a partir daqui**.

Sem formato definido, "escrever a spec" vira nota livre, e a fronteira entre
spec e transcrição some — que é exatamente o que a §2 existe para impedir.

- **Um arquivo por handler**, nomeado `<formulario>.<handler>.md`. Os 96 pares
  são únicos, mas os nomes soltos não: há 16 `FormCreate`, 2 `FormShow`, três
  nomes `BitBtnNClick` (`BitBtn1Click` em quatro formulários, `BitBtn3Click` em
  três, `BitBtn2Click` em dois) e `SpeedButton1Click` em três. Medido com
  `collections.Counter` sobre a coluna `handler` do
  [`../published_methods.tsv`](../published_methods.tsv).
- **O índice é gerado**, não escrito: `python3 wte/tools/spec_index.py`. Ele
  também **valida** cada arquivo, e `make -C wte check` o roda.

---

## O arquivo

````markdown
---
handler: lista_equiposChange
formulario: MainForm
endereco: 0x004120a4
veredito: aberto
---

# MainForm.lista_equiposChange

## Entrada

Que estado da tela e da imagem o handler lê.

**Evidência:** diff medido | disassembly lido | observação de tela | não medido

## Saída

Que estado ele muda — tela, memória, nada.

**Evidência:** …

## Bytes tocados

Offset e tamanho, ou **nenhum**. Um por linha, na forma
`0x0F7420 +16  numeros de camisa do time N`.

**Evidência:** …

## Pré-condições

O que o original checa antes de agir. Se não checa nada, escreva isso.

**Evidência:** …

## Comportamento de erro

O que faz com entrada inválida — índice fora de faixa, campo vazio, imagem
sem o time. "Não trata" é resposta.

**Evidência:** …

## Notas

Livre. Ordem de evento, divergência da LCL, armadilha. Opcional.
````

As seis seções são **obrigatórias e nesta ordem**; `## Notas` é opcional. Cada
uma das seis carrega sua própria linha `**Evidência:**`.

---

## O campo evidência é o que separa fato de suposição

Quatro valores, e só eles:

| Evidência | Quer dizer |
|---|---|
| `diff medido` | mudou na tela do original, gravou, `cmp` mostrou onde |
| `disassembly lido` | lido a partir do endereço, com a convenção Borland aplicada |
| `observação de tela` | inferido do efeito visível, sem confirmar nos bytes |
| `não medido` | ainda não se sabe; a seção é palpite declarado |

**Spec inteira marcada `observação de tela` é hipótese, não spec**, e o veredito
tem de refletir isso — não pode ser `implementado`. O `spec_index.py` recusa
essa combinação.

A ordem de força é a da §4.2 do plano: **diff antes de decompilador**. Pergunta
de *onde* se responde com `cmp` em dois minutos; o decompilador é para pergunta
de *fórmula*.

---

## Vocabulário de veredito — fechado

| Veredito | Significa |
|---|---|
| `implementado` | spec escrita, Pascal escrito, golden verde |
| `trivial` | só habilita/desabilita controle; **não toca a imagem** |
| `divergencia deliberada` | o port faz diferente, de propósito, e está registrado na [WTE-TASK-35](../../../docs/tasks/35-divergencias-deliberadas.md) |
| `nao portado` | fora de escopo, **com justificativa escrita** |
| `aberto` | ainda não estudado |

Sem acento e sem espaço no frontmatter (`divergencia deliberada` se escreve
assim mesmo) para não haver duas grafias do mesmo veredito.

**`nao portado` sem justificativa não é veredito.** O critério de pronto da
fase 4 depende disso, então a regra é mecânica: veredito `nao portado` exige a
seção `## Justificativa`, não vazia, e o índice recusa sem ela.

**`trivial` é reamostrado.** A fase 4 fecha reconferindo cinco dos `trivial`
(critério da fase 4 no `progresso.md`): é o veredito mais fácil de dar por
preguiça, e o único cuja consequência — "não toca a imagem" — o golden não
verifica sozinho, porque um handler que não deveria gravar nada e não grava
nada passa igual a um que não foi exercitado.

---

## O que a spec **não** pode conter

**Código C++ decompilado, colado.** Se a spec precisar de um trecho para ser
entendida, o trecho vai **parafraseado** — pseudocódigo ou prosa —, nunca
copiado. É a §2 do plano, e vale por dois motivos que não se substituem:
transcrever decompilado faz obra derivada de binário sem licença, e o
decompilado de C++Builder é ilegível o bastante para importar a estrutura de
2002 junto (§8.1).

Isto **não é honra**: o `spec_index.py` recusa o arquivo se achar

- bloco de código marcado ` ```c ` ou ` ```cpp `;
- os nomes que o Ghidra inventa — `undefined4`, `uVar1`, `iVar2`, `local_1c`,
  `param_1`, `DAT_00423…`, `FUN_00401…`, `__fastcall`, `(int)*(int *)`.

Pseudocódigo é bem-vindo; marque o bloco como ` ```text ` e escreva em
português. A diferença que interessa não é a linguagem do bloco, é se aquilo
foi **entendido e reescrito** ou **copiado**.

---

## Como o Pascal sai daqui

1. Ler o disassembly a partir do endereço, ou medir por diff.
2. Preencher as seis seções, cada uma com sua evidência.
3. Escrever o Pascal **a partir deste arquivo**, sem o decompilador aberto.
4. Golden test daquela operação.
5. Trocar o veredito e regerar o índice.

O passo 3 com o decompilador fechado é o ponto todo. Se a spec não bastar para
escrever o código, **a spec está incompleta** — e essa é a informação que ela
existe para dar.
