---
id: CORR-WTE-044
title: "Correção: o oráculo comportamental está morto e a fase 4 é circular"
type: correção
category: comportamento
status: pendente
depends_on: ["WTE-TASK-24"]
---

# CORR-WTE-044: quebrar a circularidade do oráculo A

## Problema identificado

O `wte.exe` morre ao trocar de time com as duas ROMs deste repositório. Ele é o
**oráculo A** do projeto (plano §4.2), e a
[WTE-TASK-22](/docs/tasks/22-harness-golden.md) monta o gate golden em cima
dele. Sem gate, nenhum handler da fase 4 pode ser verificado.

A saída natural — entender por que ele morre — cai numa **circularidade**:

```text
22 (gate golden)          precisa do wte.exe vivo
wte.exe vivo              precisa entender lista_equiposChange
lista_equiposChange       é WTE-TASK-25
25                        depends_on 22
```

Nada nessa cadeia se resolve na ordem em que as fases foram escritas. O plano
supõe, sem dizer, que o oráculo A funciona; com estas ROMs, não funciona.

## Evidência

Medida na WTE-TASK-19, gerada por
[`wte/tools/analisar_crash.py`](../../wte/tools/analisar_crash.py) e escrita em
[`wte/re/crash.md`](../../wte/re/crash.md):

| | |
|---|---|
| exceção | `c0000005`, endereço que faltou `0x1c` |
| onde cai | `vcl60.bpl` realocado para `0x005f0000`, RVA `0x5ea0` |
| símbolo | `Graphics::TFont::SetSize` + 8, com `this` **nulo** |
| sítio de chamada | `0x0040b1ac`, identificado pelo `EDX` = 8 |
| rotina | privada, em `0x0040b188` — `FindComponent("dorsal" + N)` e reestiliza |
| chamadores | `lista_equiposChange`, `lista_jugadores_1Change`, `dorsalClick`, `dorsalMouseDown` (todos `MainForm`) |

A atribuição é medida, não lida da tela: os roteiros
[07](../../wte/tests/roteiros/07-controle-sem-time.txt) e
[08](../../wte/tests/roteiros/08-so-troca-de-time.txt) são iguais linha a linha
até `= ARRANQUE` e o 08 só acrescenta a troca de time — **0 violações de acesso
contra 309**.

**Duas hipóteses de causa já caíram, as duas por experimento:** o tamanho da
imagem (truncar para os 474.431.328 bytes exatos não muda uma faixa do mapa de
I/O e o app cai igual) e a região vazia em `14368636` (é a última leitura antes
da falha, mas a falha é de estado de interface — o `analisar_io.py` só enxerga
I/O e não tinha como distinguir vizinho de causa).

## Causa raiz

Duas, e é preciso separá-las:

1. **do defeito:** desconhecida — é o que esta correção manda descobrir;
2. **da circularidade:** a fase 4 foi escrita supondo o gate como pré-requisito
   de *toda* análise de handler. Isso é certo para **implementar** um handler e
   errado para **diagnosticar** um. Diagnóstico não grava byte nenhum, não
   precisa de comparação golden, e é justamente o que destrava o gate.

## Correção

**Só diagnóstico. Nada de implementação, nada de spec.** O produto é uma
resposta escrita; o Pascal continua sendo assunto da fase 4.

O ferramental já existe: a [WTE-TASK-24](/docs/tasks/24-ghidra-convencao-borland.md)
está concluída, com a convenção Borland (`EAX, EDX, ECX`) aplicada e os 96
nomes no Ghidra. O alvo é pequeno — uma rotina de ~340 bytes e quatro
chamadores.

### As quatro perguntas, em ordem de custo

1. **O campo em `+0x68` é mesmo `TControl.FFont` nesta VCL?** A rotina lê
   `[obj+0x68]` e passa direto para `TFont::SetSize`. Os vizinhos (`+0x40`,
   `+0x44`, `+0x48`, `+0x4c`) vão para `SetLeft`/`SetTop`/`SetWidth`/
   `SetHeight`, o que casa com `TControl`. Confirmar pelo `vcl60.bpl`, não por
   memória: se `+0x68` for outro campo para a classe que chega ali, o resto da
   análise muda de rumo.

2. **De onde vem o `N` de `"dorsal" + N`?** Se for derivado de dado da imagem,
   a região vazia em `14368636` volta a ser candidata — agora como *causa da
   causa*, com mecanismo. `dorsal1..dorsal23` existem no `MainForm` e são todos
   `TStaticText`; qualquer `N` fora disso faz `FindComponent` devolver `nil`.

3. **Quem escreve no global `0x004335e4`?** A rotina testa `if (obj != nil)`
   antes de mexer na fonte, então o objeto que chega ali **passou** no teste e
   mesmo assim tem `Font` nulo. As sete referências ao global no `.text` já
   estão localizadas. Duas leituras possíveis: `FindComponent` devolveu um
   componente que não é `TControl`, ou o global foi sobrescrito por estouro de
   buffer vizinho — e este repositório já pagou por um `strcpy` de um byte a
   mais (§8.10, e o `_FORTIFY_SOURCE` do `newWe2002`).

4. **Existe condição de entrada que evita o caminho?** Se sim, o oráculo volta
   a ser dirigível e a WTE-TASK-19 destrava sem depender de outro dump.

### Os dois desfechos, e os dois são legítimos

- **Achou condição de contorno** → registrar, ajustar os roteiros, e a
  WTE-TASK-19 e a 22 seguem.
- **Não achou** → o oráculo A é inutilizável com estas ROMs, e isso **muda a
  WTE-TASK-22**: o gate precisa ser redesenhado ou declarado dependente de uma
  release que ainda não temos. Resultado negativo é resultado (prompt de
  execução, §3).

**O que esta correção não autoriza:** editar o `.exe` (leitura pura — plano
§2), colar decompilado em spec ou em código (§2, §8.10), e implementar
`lista_equiposChange` (isso é WTE-TASK-25, e continua atrás do gate).

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/crash-causa.md` | criar — a resposta escrita, à mão, com todo endereço citado vindo de ferramenta |
| `wte/tools/ghidra/` | modificar, se o diagnóstico produzir script reaproveitável |
| `docs/tasks/22-harness-golden.md` | modificar **só no desfecho negativo** |
| `docs/tasks/progresso.md` | modificar — a pendência externa passa a ter veredito |

## Verificação

- [ ] As quatro perguntas com resposta escrita, ou com "não respondida" e a
      razão
- [ ] Todo endereço do `crash-causa.md` rastreável a saída de ferramenta —
      nenhum lido do Ghidra e transcrito à mão sem o comando ao lado
- [ ] Nenhum trecho de decompilado colado (`spec_index.py` recusa as oito
      marcas; aqui a regra vale por disciplina, já que o arquivo não é spec)
- [ ] `we-team-editor/` intocada — `git status` e `sha256sum` do `.exe` antes e
      depois
- [ ] `roms/` intocada; medição só sobre cópia em `work/`
- [ ] `make -C wte check` verde
- [ ] Desfecho declarado: condição de contorno **ou** veredito de oráculo
      inutilizável, com a consequência para a WTE-TASK-22 escrita
- [ ] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
