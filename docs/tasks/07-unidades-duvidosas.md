---
id: WTE-TASK-07
title: "Veredito sobre Registry, Printers, Comobj e Winhelpviewer"
type: extração
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-02"]
status: concluído
---

# WTE-TASK-07: As quatro unidades duvidosas

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §5 e Fase 1 item 5.
- O binário importa 322 símbolos de `rtl60.bpl`/`vcl60.bpl`. Quatro unidades
  entre eles não têm par óbvio na LCL e podem ser dependência transitiva sem
  uso real — **ou** funcionalidade que o port precisa reproduzir.

| Unidade | Se for uso real | Se for transitiva |
|---|---|---|
| `Registry` | config no registry → vira INI em `~/.config/` | some |
| `Printers` | há impressão de verdade → decidir escopo | some |
| `Comobj` | OLE → provavelmente só o `ShellExecute` do `TBrowseURL` | some com a substituição |
| `Winhelpviewer` | ajuda `.hlp` → o texto vira janela própria | some |

Import de unidade em app C++Builder frequentemente é dependência transitiva. Mas
"frequentemente" não é veredito.

---

## Objetivo

Um veredito escrito por unidade: **usada** ou **transitiva**, com a evidência.

### Método

Para cada unidade, listar os símbolos importados dela (`objdump -x`, filtrando
por `@Registry@`, `@Printers@`, …) e procurar **chamada real** no
disassembly — `call ds:[...]` para o thunk correspondente.

Import sem nenhuma chamada = transitiva. Import com chamada = usada, e aí a
pergunta vira *onde*: qual dos 96 handlers contém a chamada.

### Duas armadilhas

1. **Chamada em código de inicialização não está em handler nenhum.** O
   `FormCreate` é handler, mas a inicialização de unidade
   (`@@Tep2002_*@Initialize`) não é. Procurar nos dois lugares.
2. **`Comobj` pode aparecer sem `TBrowseURL` estar envolvido.** Não concluir
   pela hipótese; conferir o sítio da chamada.

### Saída

Se alguma for **usada**, a task tem de propor a substituição em LCL, e ela vira
item da fase onde o handler dono for implementado — não trabalho perdido aqui.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/unidades-vcl.md` | criar |
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§5, fechando as quatro linhas de investigação) |

---

## Critério de conclusão

- [x] As quatro com veredito e evidência (sítio da chamada, ou ausência dela)
- [x] Inicialização de unidade conferida, além dos handlers
- [x] Para cada "usada", substituição LCL proposta e task de destino apontada
      *(vazio por construção: nenhuma é usada. A única chamada existente — a do
      `Comobj` — recebeu substituição e destino mesmo assim, para não ficar
      pendente.)*
- [x] §5 do plano atualizado — sem linha de investigação em aberto
- [x] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-05

- **Resumo do que foi feito:**

  **As quatro são transitivas.** `Registry`, `Printers` e `Winhelpviewer` não
  têm uma única referência de chamada em lugar nenhum do binário: importam
  apenas `@X@initialization$qqrv` e `@X@Finalization$qqrv`, e as duas únicas
  aparições de cada uma são o operando do próprio stub e uma entrada na tabela
  de módulos do executável. `Comobj` importa dois símbolos a mais e **tem uma
  chamada de verdade**, em `0x00421b5b` — mas fora dos 96 handlers, 3.141 bytes
  depois do fim do último, no caminho de falha de asserção da RTL da Borland
  (`VARIANT.CPP`, `vt == rhs.vt`, `_ASSERTE`), que levanta `EOleException` com
  `E_FAIL`. Nenhuma funcionalidade do aplicativo passa por ali.

  Três correções de método que o enunciado da tarefa não previa, e sem as quais
  a medida daria o resultado certo pelo motivo errado:

  1. **não existe `call ds:[...]` no binário.** O linker do C++Builder emite um
     stub `jmp *[IAT]` por import, no fim da `.text`, e o código chama o stub
     por `call rel32`. Procurar a forma indireta acha zero — nas quatro e nas
     outras 38. Medido: `call ds:[IAT]` em toda a `.text` = 0.
  2. **chamada não é a única forma de referência.** A referência de classe
     `@Comobj@EOleException@` chega ao código como *dado*, e os
     `initialization` chegam como *entrada de tabela*. Procurar só `call`
     acharia menos do que existe.
  3. **"sem import" não fecha sozinho.** O `Winhelpviewer` registra-se como
     visualizador na própria `initialization`, então poderia servir de dentro
     do package sem o `.exe` citar símbolo. A lacuna foi fechada com indício
     independente: nenhum dos 18 DFM tem `HelpFile`/`HelpContext`/`HelpType`/
     `HelpKeyword`, nenhuma string cita `.hlp`, e `ADVAPI32.DLL`/`SHELL32.DLL`
     não estão na tabela de import.

  A armadilha 2 da tarefa se confirmou ao contrário do esperado: a hipótese da
  §5 era que `Comobj` fosse *só* o `ShellExecute` do `TBrowseURL`. Não é —
  `SHELL32.DLL` não é importada, e o `TBrowseURL` não é componente de terceiro,
  é a ação padrão da VCL (`Extactns`), disparada por método dinâmico via VMT
  dentro do `vcl60.bpl`.

  **Rota escolhida: gerador com `--check`**, `wte/tools/dump_units.py`, como as
  quatro tasks irmãs. A medida não cabe em comando inline — precisa de leitor
  de PE, resolução de stub por `.reloc`, varredura do arquivo inteiro e do
  decodificador de comprimento x86-32 para delimitar os 96 handlers. Entrou
  sozinho no `make -C wte check` pelo `wildcard`.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/re/unidades-vcl.md` | criado (gerado) |
  | `wte/tools/dump_units.py` | criado |
  | `docs/PLAN-WTE-LAZARUS.md` | modificado (§5, as quatro linhas + o parágrafo) |
  | `docs/tasks/07-unidades-duvidosas.md` | modificado (este log) |

- **Problemas encontrados:**

  - **Duas afirmações da §1 do plano não batem com a medida**, e ficam para a
    WTE-TASK-09, que é quem reconcilia a §1: a §1.2 diz "322 imports, sendo
    **300** de `rtl60.bpl`/`vcl60.bpl`" — medido, são **267** (103 + 164); os
    outros 55 são de `KERNEL32` (51), `USER32` (3) e `OLEAUT32` (1).
  - **A §5 chama `TBrowseURL` de "componente de terceiro"**, na tabela de
    classes. É a ação padrão `Extactns::TBrowseURL` da própria VCL. A
    substituição proposta (`TLabel` + `OpenURL()` de `LCLIntf`) continua certa;
    só a justificativa está errada. Não corrigido aqui porque a instrução
    delimitava a edição às quatro linhas da tabela de *unidades*.
  - **`wte/tools/README.md` precisa de uma linha para o `dump_units.py`** (task
    07, "imports → veredito sobre as quatro unidades duvidosas"). Não editado
    aqui: está fora do escopo de arquivos desta tarefa.
  - O `dump_units.py` carrega uma cópia verbatim do decodificador x86-32 do
    `dump_strings.py`. A duplicação é a mesma escolha que já vale para o leitor
    de PE — cada gerador de `wte/tools/` roda sozinho —, mas os dois têm de
    andar juntos se um dia mudarem. *(Isto era só este parágrafo até a
    [CORR-WTE-013](/docs/tasks/CORR-WTE-013.md), que pôs a identidade entre as
    duas cópias sob teste.)*
