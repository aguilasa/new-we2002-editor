---
id: CORR-WTE-023
title: "Correção: o critério de build da WTE-TASK-11 diz 2.482 linhas e atribui os 2 hints ao Lazarus; são 2.562 e vêm do /etc/fpc.cfg"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-023: os três números do critério de compilação não reproduzem

## Problema identificado

O primeiro critério de conclusão da WTE-TASK-11 é o que prova que a casca
compila limpa, e traz três medidas:

```markdown
- [x] `lazbuild` compila sem warning novo — 2.482 linhas, 0 warning, 2 hints
      (ambos do Lazarus sobre diretório de pacote do sistema, não do código)
```

Duas das três não batem com a ferramenta:

1. **São 2.562 linhas, não 2.482.** Diferença de 80. Não é deriva posterior:
   nenhum commit tocou `wte/src`, `wte/forms`, `wte/wte.lpr` ou `wte/wte.lpi`
   depois da task, e compilar a árvore **no próprio commit `af424c0`**, num
   worktree separado, dá 2.562.
2. **Os 2 hints não são "do Lazarus sobre diretório de pacote".** O contador
   `(1022) 2 hint(s) issued` é do FPC, e os dois hints que ele conta são
   `11030`/`11031` — abrir e fechar `/etc/fpc.cfg`. Os hints do Lazarus sobre
   diretório de pacote existem, mas são **sete**, saem antes do compilador e
   não entram nessa conta.

"0 warning" está certo, e é a parte que o critério existe para afirmar.

O dano é o de sempre com número que não reproduz: quem rodar `lazbuild` para
conferir vê 2.562 e 2 hints atribuídos a outra coisa, e tem de decidir sozinho
se a casca regrediu ou se o doc está velho — que é exatamente a dúvida que o
critério existe para não deixar acontecer. É a armadilha 11 do `progresso.md`
("todo número em doc vem de ferramenta").

## Evidência

Na árvore de hoje, nos dois modos:

```
$ rm -rf wte/build && lazbuild wte/wte.lpi
(1008) 2562 lines compiled, 0.9 sec
(1022) 2 hint(s) issued

$ lazbuild -B wte/wte.lpi
(1008) 2562 lines compiled, 1.0 sec
(1022) 2 hint(s) issued
```

No commit da própria task, para descartar deriva:

```
$ git log --oneline af424c0..HEAD -- wte/src wte/wte.lpr wte/wte.lpi wte/forms
(nenhuma saída)

$ git worktree add --detach /tmp/.../wt11 af424c0 && lazbuild /tmp/.../wt11/wte/wte.lpi
(1008) 2562 lines compiled, 1.0 sec
(1022) 2 hint(s) issued
```

Quais são os hints:

```
$ lazbuild -B wte/wte.lpi 2>&1 | grep -E '^Hint'
Hint: (lazarus) Missing state file of freetypelaz 1.0: ...
Hint: (lazarus) normal output directory of package freetypelaz 1.0 is not writable: ...
Hint: (lazarus) Compiler unit paths changed for LCLBase 3.0.0.3
Hint: (lazarus) normal output directory of package LCLBase 3.0.0.3 is not writable: ...
Hint: (lazarus) Compiler unit paths changed for LCL 3.0.0.3
Hint: (lazarus) normal output directory of package LCL 3.0.0.3 is not writable: ...
Hint: (lazarus) Build Project: nothing to do.
Hint: (11030) Start of reading config file /etc/fpc.cfg
Hint: (11031) End of reading config file /etc/fpc.cfg
```

Sete do Lazarus, dois do FPC. O `(1022) 2 hint(s) issued` conta os dois últimos.

## Causa raiz

Os três números foram escritos de memória depois da execução, em vez de colados
da saída — e a atribuição dos hints saiu de olhar as linhas `Hint:` do Lazarus,
que estão na mesma tela mas não são as que o contador soma.

## Correção

### Arquivo: `docs/tasks/concluidos/11-app-com-a-casca-completa.md`

Trocar o critério pelos valores medidos, dizendo de onde cada um sai:

```markdown
- [x] `lazbuild` compila sem warning novo — `lazbuild -B wte/wte.lpi` dá
      `(1008) 2562 lines compiled` e `(1022) 2 hint(s) issued`, com **0
      warning**. Os 2 hints do contador do FPC são `11030`/`11031`, abrir e
      fechar `/etc/fpc.cfg` — nada do código. Os hints do Lazarus sobre
      diretório de pacote do sistema não writable são outros sete, saem antes
      do compilador e não entram nessa conta.
```

Se `lazbuild` passar a relatar outro número de linhas depois de uma task de
fase 3 em diante, é porque unidades novas entraram — o número aqui é o da
casca da fase 2, e quem o mudar diz por quê no seu próprio Log.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/concluidos/11-app-com-a-casca-completa.md` | modificar (critério 1) |

## Verificação

- [ ] `lazbuild -B wte/wte.lpi 2>&1 | grep -E '1008|1022'` bate, dígito por
      dígito, com o que o critério passa a dizer
- [ ] `lazbuild -B wte/wte.lpi 2>&1 | grep -ci warning` continua 0
- [ ] `grep -n "2.482\|2482" docs/tasks/concluidos/11-app-com-a-casca-completa.md` sai vazio
- [ ] `make -C wte check` verde — nenhum número velho introduzido no perímetro
      do `check_fase1.py`
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-09

**Resumo do que foi feito:** O critério 1 da WTE-TASK-11 passou a trazer as
medidas coladas da saída, com o comando que as produz, e a dizer qual contador
é de quem: `(1022) 2 hint(s) issued` é do FPC e conta `11030`/`11031`
(`/etc/fpc.cfg`), enquanto os hints do Lazarus sobre diretório de pacote são
outros seis e saem antes do compilador.

**Problemas encontrados:** Dois, os dois relevantes para quem reconferir.

1. **O número escrito é 2.567, não 2.562.** A CORR-WTE-022, executada neste
   mesmo lote e imediatamente antes desta, acrescentou 5 linhas ao cabeçalho de
   `wtemain.pas` (`git show --numstat 55aec14` = +6 −1), e o FPC conta
   comentário em `lines compiled`. É a armadilha do lote: a correção *k+1*
   torna falso o número que a *k* mediu. O 2.562 do diagnóstico continua certo
   como história e está registrado como tal.
2. **A verificação `grep -ci warning` desta CORR é falso positivo.** Ela devolve
   **2** numa saída sem warning nenhum, porque casa
   `Compiling ./src/ep2002_warning.pas` e `ep2002_warning_2.pas`. O critério
   passou a dizer o que vale: `(1023) N warning(s) issued` ausente, ou
   `grep -cE '^Warning'` = 0 — medido, 0.

Terceiro detalhe menor: os hints do Lazarus são **seis** a partir de árvore
limpa (`rm -rf wte/build`), e sete quando a árvore já está construída, porque
entra o `Build Project: nothing to do.`. O critério diz os dois casos.

**Arquivos criados/modificados:**

- `docs/tasks/concluidos/11-app-com-a-casca-completa.md` (critério 1)
- `docs/tasks/concluidos/correcoes-progresso.md` (bloco de detalhe desta CORR — o
  2.562 do diagnóstico ganhou a nota do deslocamento)
