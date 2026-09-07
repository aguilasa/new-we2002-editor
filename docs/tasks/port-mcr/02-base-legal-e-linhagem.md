---
id: MCR-TASK-02
title: "Base legal, linhagem e o SHA fixado do upstream"
type: documentação
category: processo
phase: 0
depends_on: ["MCR-TASK-01"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §2"
status: concluído
---

# MCR-TASK-02: Base legal e linhagem

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §2.
- O upstream **não tem licença** — sem `LICENSE`, sem cabeçalho de fonte,
  `"license": null` na API do GitHub, e um `<Copyright>Copyright © 2023</Copyright>`
  no `.vbproj`. O usuário decidiu portar literalmente, ciente disso, em
  2026-09-07.
- O repositório já vive nessa posição com `legacy/mfc/` (Moriero 2002,
  thyddralisk 2015), e por isso **não tem `LICENSE`**. A linhagem mora em
  [`NOTICE.md`](../../../NOTICE.md).

---

## Objetivo

Deixar a posição legível para quem chegar depois: de onde veio cada coisa, o
que é transcrição e o que é medição nossa, e por que o método aqui difere do
método do ciclo `wte/`.

---

## Critério de conclusão

- [x] `NOTICE.md` com a entrada do upstream: autor (Zetaprog), URL, **SHA
      `30af1fe59cf96beee3b066f6cdfcb1b6f3df37cc`**, data (2026-05-27), e a
      constatação de que não há licença.
- [x] O parágrafo que registra **a diferença de método**: no ciclo `wte/` o
      editor do Obocaman foi tratado como binário a medir, nunca a transcrever;
      aqui há fonte e o dono decidiu transcrever. As duas razões lado a lado —
      sem isso um leitor futuro conclui que a regra mudou sozinha.
- [x] O upstream clonado em `work/easy-mcr/` (gitignored), com o inventário de
      arquivos e tamanhos registrado no Log — o repo tem 5 commits num dia só e
      pode sumir.
- [x] Registrado o que **não entra**, e por quê: `BD.accdb`, as faces `.bmp`,
      os binários de `bin/`, o `.pfx` de assinatura e o cache do WebView2.
- [x] Conferido que `.gitignore` cobre `work/` (já cobre) e que nada do
      upstream entrou: `git status` limpo depois do clone.

---

## Log de Execução

**Executado em:** 2026-09-07

### Resumo do que foi feito

`NOTICE.md` ganhou a seção `## Lineage of the .mcr editor port (the tools/mcr/
tree)`, com a linha de crédito do Zetaprog (URL, SHA
`30af1fe59cf96beee3b066f6cdfcb1b6f3df37cc`, os cinco commits de 2026-05-27), a
constatação de que não há licença, e o parágrafo que põe **as duas razões lado
a lado**: contra o `.exe` do Obocaman não havia o que copiar senão saída de
decompilador, então medir era a única rota honesta; contra o repositório do
Zetaprog há fonte legível, e o que ele acrescenta é **semântica** — qual byte
significa "papel", como se chamam os vinte rótulos —, que não se mede na
fixture porque os bytes estão lá de qualquer jeito e só ele diz o que querem
dizer. A seção `## Copyright and license status` passou a nomear o Zetaprog
junto dos outros três.

**O que se aprendeu, e não estava no plano: o upstream tem duas árvores, e
nenhuma é subconjunto da outra.** `fifatomcr/` é .NET 8 e é a do
`<Copyright>Copyright ©  2023</Copyright>` que a §2 do plano cita;
`lite/fifatomcr/` é .NET Framework 4.7.2 e tem um `FrmFormation.vb` que a
principal não tem. A consequência é operacional e foi encaminhada por escrito:
**a tabela de cobradores e o `0x6500` existem só na `lite/`**.

### Inventário do upstream

Clone em `work/easy-mcr/` (gitignored), `HEAD` conferido igual ao SHA fixado.
Todos os números abaixo saem de `git ls-tree -r -l HEAD` **contra o SHA**, não
do disco — o comando reproduz em qualquer clone:

```sh
git -C work/easy-mcr rev-parse HEAD
# 30af1fe59cf96beee3b066f6cdfcb1b6f3df37cc

git -C work/easy-mcr log --format='%H %ad %an %s' --date=short
# 5 commits, todos 2026-05-27, todos de zetaprog

git -C work/easy-mcr ls-tree -r -l HEAD | awk '{s+=$4; n++} END {print n, s}'
# 2853 476688515
```

| diretório de topo | arquivos | bytes |
| --- | ---: | ---: |
| `lite/` | 2170 | 319.101.497 |
| `fifatomcr/` | 583 | 104.998.529 |
| `packages/` | 82 | 50.469.473 |
| `.vs/` | 13 | 1.928.312 |
| raiz | 5 | 190.704 |

**O que não entra, e por quê.** Categorias disjuntas, na ordem em que foram
descontadas (`git ls-tree -r -l HEAD` filtrado por prefixo e extensão; **o
prefixo casa em qualquer profundidade** — `.vs/` e `packages/` também
aparecem sob `lite/`, e é por isso que somam 20 e 164 contra os 13 e 82 do
topo). O cache do WebView2 **atravessa duas linhas** e por isso não é linha:
são 1.820 arquivos e 319.637.837 B ao todo, 1.656 / 218.698.891 sob
`bin/`+`obj/` e os outros 164 / 100.938.946 sob `packages/`, que é
inteiramente ele.

| categoria | arquivos | bytes | por quê |
| --- | ---: | ---: | --- |
| `.vs/` | 20 | 3.996.160 | cache do Visual Studio |
| `packages/` | 164 | 100.938.946 | NuGet restaurado — é **inteiramente** o WebView2 |
| `bin/` e `obj/` | 2586 | 363.366.917 | saída de build — inclui **1.656 arquivos e 218.698.891 B** do cache do WebView2, que é a maior parte dele mas não o todo |
| `BD.accdb` | 1 | 2.543.616 | banco Access privado dele (aparências e faces); não é dado de save |
| `.bmp` | 6 | 996.032 | faces e o `cancha.bmp` do editor de formação — arte |
| `.png` | 2 | 92.204 | arte |
| `.pfx` | 2 | 3.304 | `fifatomcr_TemporaryKey.pfx`, chave de assinatura — as duas cópias |
| **soma excluída** | **2781** | **471.937.179** | |
| **resto (o fonte que importa)** | **72** | **4.751.336** | |

Fora da conta por não ser arquivo: o raspador de Sofifa/Transfermarkt/FMInside/
PESMaster, que a §0 do plano já lista como não-objetivo, e as três cópias de
`PlayerStatsSkills.dll` (11.776 B cada), que é binário de terceiro sem fonte.

**O `.gitignore` já cobre `work/`** (linha 48), e `git status --short` depois do
clone não lista nada de `work/easy-mcr/`.

### As duas árvores, e onde cada fato mora

Medido por `grep` do valor decimal nos `.vb` das duas árvores:

| fato | valor | onde está |
| --- | --- | --- |
| base do registro de jogador | `22788` (`0x5904`) | `fifatomcr/Frmmcr.vb`, `lite/fifatomcr/Frmmcr.vb` |
| tabela de dorsais | `21508` (`0x5404`) | as duas `Frmmcr.vb` |
| `ListBoxMcrOffset`, `bufersizenum` | — | **só** `fifatomcr/` |
| `Regex.Replace(…, "[^a-zA-Z.]", "")` | — | **só** `fifatomcr/Form1.vb` |
| X, Y, papéis | `25256`, `25266`, `25557` | `fifatomcr/Frmmcr.vb` **e** `lite/fifatomcr/FrmFormation.vb` |
| cobradores | `24911, 24896, 24866, 24851, 24881` | **só** `lite/fifatomcr/FrmFormation.vb` |
| o byte em aberto | `25856` (`0x6500`) | **só** `lite/fifatomcr/FrmFormation.vb` |

Encaminhado **por escrito nos arquivos de destino**, não só aqui: a
[MCR-TASK-08](/docs/tasks/port-mcr/08-formacao-e-dominios.md) e a
[MCR-TASK-13](/docs/tasks/port-mcr/13-oraculo-e-veredito.md) ganharam cada uma
uma linha de Contexto dizendo qual arquivo ler. Sem isso, quem executar a 08
lendo só a árvore principal fica sem os cinco cobradores, e quem executar a 13
cita um "o upstream diz" que a árvore que ele abriu não diz.

### Arquivos criados/modificados

- `NOTICE.md` — a seção nova da linhagem do port, e o Zetaprog acrescentado à
  seção de status de licença
- `docs/tasks/port-mcr/08-formacao-e-dominios.md` — a linha de Contexto sobre
  a árvore `lite/`
- `docs/tasks/port-mcr/13-oraculo-e-veredito.md` — idem, para o `0x6500`
- `docs/tasks/port-mcr/progresso.md` — a linha desta task

Fora do git, por decisão: `work/easy-mcr/` (o clone).

### Problemas encontrados

Nenhum que bloqueasse. Duas coisas a registrar:

1. **O plano diz "o `.vbproj`" no singular, e há dois.** O
   `<Copyright>Copyright ©  2023</Copyright>` está só no
   `fifatomcr/fifatomcr.vbproj`; o da `lite/` é projeto clássico e não tem a
   tag. A afirmação da §2 continua verdadeira, mas era ambígua — o `NOTICE.md`
   agora nomeia o arquivo.
2. **`packages/` some do inventário se o WebView2 for descontado primeiro.**
   A primeira medição casou por `webview2` antes de casar por prefixo e
   devolveu `packages/ 0 arquivos`, o que é falso como leitura e verdadeiro
   como aritmética. A tabela acima desconta na ordem prefixo → extensão, e a
   legenda diz o que isso implica: o WebView2 **atravessa** `bin/`+`obj/` e
   `packages/`, então ele é descontado por prefixo, nunca por nome, e não
   pode ser atribuído a uma das duas linhas.

