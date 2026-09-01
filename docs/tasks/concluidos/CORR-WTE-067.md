---
id: CORR-WTE-067
title: "Correção: a nota nova da WTE-TASK-27 põe a AtualizaBlocosLivresDeMl na unidade errada e promete um mapa que não existe"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-067: o desbloqueio escrito na WTE-TASK-27 não corresponde à API entregue

## Problema identificado

O commit da WTE-TASK-33 acrescentou a `docs/tasks/concluidos/27-handlers-de-gravacao.md`
(linhas 178-181) a nota que declara o ramo de Master League desbloqueado:

```markdown
**A 33 fechou em 2026-08-19**, antecipada exatamente por isto: o contador
existe (`AtualizaBlocosLivresDeMl`, do `we2002_ml`), e com ele vem o mapa
de ocupação que diz **qual** bloco está livre.
```

Duas afirmações, as duas erradas contra o código entregue na mesma task:

1. **`AtualizaBlocosLivresDeMl` não é do `we2002_ml`.** Ela é um procedimento
   local do `wte/src/impl/ep2002_mainform.aux.inc` (linha 832), que junta a
   contagem com o `casilla_xmlibres.Caption`. Quem o `we2002_ml` exporta é
   `ContaBlocosLivresDeMl` e `MlPrefixoDoTime`.
2. **Não vem mapa de ocupação nenhum.** `ContaBlocosLivresDeMl` devolve um
   `Word` — quantos blocos estão livres — e, pela sobrecarga, um
   `fora_do_vetor: Integer`. O vetor `ocupacao` é **local** da função e morre
   com ela. Quem escrever o ramo de destino de ML precisa saber **qual** índice
   está livre, e essa informação não sai da unidade.

Quem executar a WTE-TASK-27 lendo essa nota vai procurar uma API que não
existe.

## Evidência

A interface publicada, de `wte/src/we2002_ml.pas`:

```pascal
function ContaBlocosLivresDeMl(const caminho: string;
                               out fora_do_vetor: Integer): Word; overload;
function ContaBlocosLivresDeMl(const caminho: string): Word; overload;
function MlPrefixoDoTime(time: Integer): Integer;
```

O `ocupacao` é local, e nada o devolve:

```pascal
var
  img: TCdImage;
  ocupacao: array[0..ML_INDICE_MAX] of Word;
```

Onde a `AtualizaBlocosLivresDeMl` mora de verdade:

```text
wte/src/impl/ep2002_mainform.aux.inc:832:procedure AtualizaBlocosLivresDeMl;
```

## Causa raiz

A nota foi escrita descrevendo a intenção do desbloqueio, não a assinatura que
ficou — e nenhum `--check` lê prosa de task.

## Correção

### Arquivo: `docs/tasks/concluidos/27-handlers-de-gravacao.md`

Reescrever as linhas 178-181 com o que existe:

- o contador é `ContaBlocosLivresDeMl`, do `we2002_ml`; a
  `AtualizaBlocosLivresDeMl` é o par contar-e-mostrar do
  `ep2002_mainform.aux.inc`;
- **o mapa de ocupação ainda não é exposto.** Escrever o ramo de ML exige ou
  devolver o vetor (um `out` a mais, ou uma função irmã que entregue o primeiro
  índice livre), ou refazer a varredura no chamador. Dizer qual dos dois é o
  caminho, para a 27 não redescobrir isso.

A referência à `0x0040427c` (o inverso do índice linear) está correta e fica.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/concluidos/27-handlers-de-gravacao.md` | modificar |

## Verificação

- [x] A nota da 27 nomeia `ContaBlocosLivresDeMl` como a função do `we2002_ml`
      e `AtualizaBlocosLivresDeMl` como do `ep2002_mainform.aux.inc`
- [x] A nota diz explicitamente que o mapa de ocupação não é exposto hoje, e
      qual é o caminho para obtê-lo
- [x] `grep -n 'AtualizaBlocosLivresDeMl' wte/src/we2002_ml.pas` continua sem
      resultado — a correção é no texto, não na unidade
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-19

**Resumo do que foi feito:**

A nota de desbloqueio da 27 foi reescrita contra a API que ficou: o contador é
a `ContaBlocosLivresDeMl`, do `we2002_ml`; a `AtualizaBlocosLivresDeMl` é o par
contar-e-mostrar e mora no `ep2002_mainform.aux.inc`, não na unidade. A nota
passou a dizer que **o mapa de ocupação não é exposto hoje** — a função devolve
quantos blocos estão livres, não quais, e o vetor `ocupacao` morre com ela — e
qual é o caminho: uma função irmã no `we2002_ml` que devolva o primeiro índice
livre, reaproveitando a varredura que já existe, em vez de o chamador reler a
imagem inteira uma segunda vez. A referência à `0x0040427c` estava certa e
ficou.

Correção de texto: a unidade não foi tocada, e a verificação exige justamente
isso.

**Problemas encontrados:**

Nenhum. A varredura por `AtualizaBlocosLivresDeMl` fora do `impl/` achou um
segundo sítio, `wte/re/spec/MainForm.FormShow.md:41` — mas ali a frase é
verdadeira: o `FormShow` do port chama mesmo o procedimento auxiliar, e o texto
não o atribui ao `we2002_ml`. Nada a reconciliar.

**Arquivos criados/modificados:**

- `docs/tasks/concluidos/27-handlers-de-gravacao.md`
