---
id: CORR-WTE-142
title: "Correção: os roteiros de ciclo de vida gravam captura em `/tmp/c09`, que ninguém cria — e o do oráculo anuncia a captura que não fez"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-142: a evidência dos itens 1, 2 e 5 da §8.10 não é reproduzível

## Problema identificado

Os itens 1, 2 e 5 da §8.10 **não têm veredito de `golden_compare.py`** — não
podem ter, porque são arranque e encerramento, e o harness já entra pelo
diálogo de abertura e já sai gravando. A evidência deles é **captura de tela**,
e é o que a §8.10 e a [PAR-TASK-09](/docs/tasks/PAR-TASK-09.md) descrevem
("combo sem itens, campos em branco, `Write into CD image` clicável").

As cinco chamadas de `import` dos dois roteiros escrevem em **`/tmp/c09/`**, um
diretório que **nenhum dos dois cria**:

```text
$ grep -n 'mkdir' tools/par/8.10-ciclo-port.sh tools/par/8.10-ciclo-oraculo.sh
tools/par/8.10-ciclo-oraculo.sh:24:[ -d "$WINEPREFIX" ] || { mkdir -p "$WINEPREFIX"; ... }
$ ls -d /tmp/c09
ls: cannot access '/tmp/c09': No such file or directory
```

Todo `import` sai com `2>/dev/null`, então a falha é silenciosa. Duas
consequências, e a segunda é a séria:

1. **Nenhuma captura é produzida** numa máquina limpa — nem hoje, aqui: o
   diretório não existe e as imagens não estão versionadas. A evidência dos
   três itens não se refaz rodando o roteiro.
2. **O `8.10-ciclo-oraculo.sh` afirma ter capturado.** Dois dos três `echo`
   estão **fora** do `&&` do `import`, então a linha é impressa mesmo quando o
   arquivo não foi escrito.

Isso também contraria a regra de arquivo temporário do `CLAUDE.md` — caminho
fixo em `/tmp`, fora do scratchpad, num script versionado.

## Evidência

Corrida desta revisão, oráculo, com `/tmp/c09` inexistente antes e depois:

```text
== item 1: cancelar o diálogo de abertura ==
  diálogo de abertura apareceu (id 14680085)
  aviso apareceu; captura em /tmp/c09/ora-cancelar.png     <-- mentira
  ed.exe ainda vivo? sim
  janela principal? 0xe00001

== item 2: abrir imagem com tamanho errado ==
  aviso de tamanho apareceu; captura em /tmp/c09/ora-tamanho.png   <-- mentira
  CARREGOU MESMO ASSIM -- janela principal 0xe00001

$ ls -l /tmp/c09
ls: cannot access '/tmp/c09': No such file or directory
```

A assimetria confirma o diagnóstico: a **terceira** captura do mesmo roteiro
(`ora-carregado.png`, linha 85) está guardada por `&&` e **não** imprimiu nada.
O `8.10-ciclo-port.sh` tem as duas guardadas, e por isso ficou calado — o que é
melhor, mas continua sem produzir a evidência:

```text
== item 1: cancelar o diálogo de abertura ==
  diálogo de abertura apareceu (id 4194313)
  janelas logo após cancelar:
    4194317 Geometry: 321x100 :: WE2002 Editor
  processo ainda vivo? NAO
```

**O comportamento medido bate com o que a task afirma** — o `ed.exe` fica de pé
com a janela principal e o port encerra; os dois carregam a imagem de tamanho
errado; `Escape` mata os dois. O que falta é a prova gráfica que os roteiros
dizem produzir.

## Causa raiz

Ninguém cria o diretório de destino, e dois `echo` de confirmação não estão
condicionados ao sucesso do `import`.

## Correção

### Arquivos: `tools/par/8.10-ciclo-port.sh` e `tools/par/8.10-ciclo-oraculo.sh`

1. **Destino parametrizado e criado**: `OUT="${PAR_OUT:-$PWD/work/par-8.10}"` e
   `mkdir -p "$OUT"` no topo dos dois. `work/` já está no `.gitignore`, é onde
   o resto do projeto põe saída de corrida, e não colide com outro usuário da
   máquina como um `/tmp` fixo colide.
2. **Nenhum `echo` de captura fora do `&&`** — nos dois roteiros, a linha que
   anuncia o arquivo só sai se ele foi escrito. Melhor ainda: `|| echo
   "  captura FALHOU"`, porque silêncio também esconde.
3. Não engolir o erro do `import` sem dizer nada: trocar `2>/dev/null` por uma
   mensagem quando falhar.

### Arquivo: `docs/PARIDADE-FUNCIONAL.md` e `docs/tasks/PAR-TASK-09.md`

Refazer as capturas com os roteiros consertados e dizer onde elas caem, para o
próximo leitor conseguir refazer os três itens.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/par/8.10-ciclo-port.sh` | modificar |
| `tools/par/8.10-ciclo-oraculo.sh` | modificar |
| `docs/PARIDADE-FUNCIONAL.md` | modificar — §8.10, onde ficam as capturas |
| `docs/tasks/PAR-TASK-09.md` | modificar — o Log |

## Verificação

- [ ] Numa árvore sem o diretório de saída, os dois roteiros o criam e as cinco
      capturas existem ao fim
- [ ] Nenhuma linha de "captura em ..." é impressa sem o arquivo correspondente
      (testar renomeando o destino para um caminho sem permissão)
- [ ] Os vereditos de tela continuam os mesmos: `ed.exe` vivo com janela
      principal depois do cancelamento, port encerrado; os dois carregam a
      imagem de tamanho errado; `Escape` encerra os dois
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-31

**Resumo do que foi feito:**

Destino das capturas passou a ser `${PAR_OUT:-$REPO/work/par-8.10}`, criado
pelos dois roteiros com `mkdir -p`. As cinco chamadas soltas de `import` viraram
um `capturar()` que imprime a linha de confirmação **só** com o arquivo escrito
e, quando falha, mostra a mensagem do próprio `import` em vez de engoli-la.

**Problemas encontrados:**

**Eram dois defeitos, e o segundo estava escondido atrás do primeiro.** Com o
erro visível, a primeira corrida acusou:

```text
  captura FALHOU (.../port-cancelar.png): import-im6.q16: unable to read
  X window image `4194310': Resource temporarily unavailable
```

Ou seja: mesmo com o diretório existindo, `import -window <id>` não lia a
janela. Duas causas, as duas consertadas aqui:

1. **A janela estava obscurecida pelo modal** — a armadilha que o `CLAUDE.md`
   já registra na seção do `:98`. O `capturar()` tenta a janela e cai para
   `-window root`, que sempre funciona e, sem gerente de janelas, mostra a
   mesma tela; a mensagem diz qual das duas produziu o arquivo.
2. **A busca de janela por título não filtrava por visibilidade.** O
   `xdotool search --name` devolvia uma janela **não mapeada** de mesmo nome
   (o `4194310` do erro, contra o `4194317` que a listagem mostrava), que não
   se captura nem se dirige. Passou a usar `--onlyvisible` nos dois roteiros.

**Uma captura faltava**, e o item 1 é justamente quem precisava dela: o roteiro
do oráculo reportava `janela principal? 0xe00001` e nunca a fotografava — a
janela vazia que o `ed.exe` mantém de pé é a evidência do item. Agora sai como
`ora-cancelar-janela.png`, depois de um `sleep` que deixa o MFC terminar de
pintar (sem ele a captura pega meia tela de rótulos, medido).

**Arquivos criados/modificados:**

- `tools/par/8.10-ciclo-port.sh` — destino, `capturar()`, `--onlyvisible`
- `tools/par/8.10-ciclo-oraculo.sh` — idem, mais a captura da janela que sobra
  e o `sleep` de pintura
- `docs/PARIDADE-FUNCIONAL.md` — §8.10 diz onde as capturas caem e como refazê-las
- `docs/tasks/PAR-TASK-09.md` — nota posterior
- `docs/tasks/CORR-WTE-140.md` — a linha que anunciava a captura inexistente
  ganhou a nota do que realmente aconteceu
