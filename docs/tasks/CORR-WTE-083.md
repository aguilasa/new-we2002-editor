---
id: CORR-WTE-083
title: "Correção: dez times desenham bandeira preta — o ed.exe não lê a paleta deles, e o editor do Obocaman lê"
type: correção
category: comportamento
status: pendente
depends_on: []
---

# CORR-WTE-083: dez times desenham bandeira preta

## Problema identificado

Na conferência de tela da [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md)
(2026-08-22), o time **56 — `CLASSIC ENGLAND`** apareceu com a bandeira
**inteiramente preta** no port, e com a cruz de São Jorge no oráculo. As cinco
barras batem em pixel, o uniforme bate em pixel, e a bandeira diverge em
**3.840 de 3.840 pixels**, com desvio máximo de canal 232.

Não é um time: são **dez**, em duas famílias com mecanismos diferentes.

- **`teams[56]`…`teams[63]`** — os oito CLASSIC (`CLASSIC ENGLAND`,
  `CLASSIC FRANCE`, `CLASSIC NETHERLANDS`, `CLASSIC ITALY` e os quatro
  seguintes);
- **`ml_teams[5]` (`HIGHLANDS`) e `ml_teams[22]` (`EMILIA`)** — dois clubes de
  Master League.

Os dez carregam `flag_colours` como **dezesseis zeros**, e zero na paleta é
preto. Confirmado na tela em dois deles, um de cada família: o time 56 e o
combo 68, que é o `ml_teams[5]` — o oráculo desenha a cruz amarela em azul, o
port desenha preto, 3.840 de 3.840 pixels, desvio máximo de canal 248.

O `flag_shape` deles **não** é o problema: o time 56 traz `flag_shape = 4`, e
`bandera4.bmp` existe. O que falta é a cor.

## Evidência

Dump da camada de dados sobre a ROM japonesa, pelo
[`dump_estado.pas`](../../wte/tests/dump_estado.pas) — o mesmo que o
[`compara_tela.sh`](../../wte/tools/compara_tela.sh) gera como terceira ponta da
conferência:

```text
teams[56].flag_shape = 4
teams[56].flag_colours = 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```

Contados os 64 slots de `teams[]` e os 32 de `ml_teams[]`, **dez** têm a paleta
inteiramente zerada: `teams[56..63]`, `ml_teams[5]` e `ml_teams[22]`.

E a causa está no bloco de carga, que é **transpilado do `we2002_core`** e
portanto herdado do `ed.exe`. Nas duas famílias é a mesma coisa — endereço que
ninguém lê —, com forma diferente:

```text
wte/src/we2002_database.pas   for i := 0 to 55 do   ... image_file.Read(teams[i].flag_colours,32)
src/core/Database.cpp         for(i = 0;i < 56;i ++) ... image_file.Read(&teams[i].flag_colours,32)
```

O laço nacional para em 55, e os oito CLASSIC nunca são lidos. O bloco de
Master League não é laço: é uma lista de índices espalhados, e ela cobre
`{0-4, 7-21, 24-27}` — **`5`, `6`, `22` e `23` ficam de fora**. Desses quatro,
o `6` e o `23` aparecem com cor no dump (são lidos noutro ponto do arquivo); o
`5` e o `22` ficam com o zero da inicialização.

A montagem lado a lado ficou em `work/tela/time-56-lado-a-lado.png` durante a
medição — `work/` é rascunho e não é versionada; para refazer:

```sh
bash wte/tools/compara_tela.sh 56
```

## Causa raiz

**Os dois oráculos não cobrem a mesma coisa, e o port seguiu o de formato.**

- **Oráculo B, o `we2002_core`**, é byte-idêntico ao `ed.exe` e por isso
  reproduz o alcance do `ed.exe` — que **não carrega** a paleta de bandeira
  desses dez. Para o `ed.exe` isso nunca foi defeito: ele não desenha bandeira
  nenhuma, e paleta que ele não desenha ele também não precisa gravar;
- **Oráculo A, o `wte.exe` do Obocaman**, desenha, e lê a cor de cada time pela
  tabela de offsets em `.data` que cobre os 95 slots —
  [`re/offsets.md`](../../wte/re/offsets.md), a rotina `0x004050D0`.

O port herdou a camada de dados do B e a tela do A. Onde os dois discordam de
**alcance**, a tela do port fica sem dado. É a mesma classe de achado da
[WTE-TASK-19](/docs/tasks/19-os-50-offsets-restantes.md) — *"os offsets que o
Obocaman tem e nós não"* —, e este passou por ela sem ser visto porque a
conferência de tela daquela época não olhou a bandeira desses dez.

## Correção

**O offset existe e está na tabela do `.exe`.** O trabalho é lê-lo e usá-lo,
não descobri-lo:

1. **Medir** onde a `0x004050D0` busca `flag_colours` para os dez —
   a global de offset é `[0x004331DC]`, preenchida pela varredura da tabela em
   `.data` (`0x0040CBC8`, seis colunas por linha). O
   [`dump_offsets.py`](../../wte/tools/dump_offsets.py) já lê essa tabela;
2. **Decidir onde o valor entra.** Duas rotas, e a escolha é do executor:
   - **rota A** — estender o laço do `we2002_database.pas`. Isso mexe em
     arquivo **gerado**, então a mudança entra no
     [`port_database_pas.py`](../../wte/tools/port_database_pas.py) e sai
     regerada. Mas ela faz o port divergir do `we2002_core` na carga, e o
     `compare_dumps.py` da WTE-TASK-20 reprova por construção: os dumps Pascal
     e C++ deixariam de ser idênticos;
   - **rota B** — carregar os dez à parte, fora da camada transpilada, como a
     [`wte_cor`](../../wte/src/wte_cor.pas) já faz com o que é do editor e não
     do formato. O dump continua idêntico e a tela ganha a cor.

   **A rota B é a recomendada**, e a razão é a regra da §4.5 do plano: a camada
   de dados é do `we2002_core`, e o que o Obocaman lê a mais é do Obocaman;
3. **Conferir com o `compara_tela.sh`** nos dez, não em dois. Dois é amostra;
   dez são as duas famílias inteiras — e são famílias diferentes, então passar
   numa não diz nada sobre a outra;
4. **Reler o veredito do `lista_equiposChange`** — este achado é hoje uma das
   razões de ele continuar `aberto`.

**Não mexer no `src/core/`.** O `newWe2002` está com escopo fechado e
verificado, e o `ed.exe` não desenha bandeira: estender o laço lá seria
divergir do oráculo que ele existe para reproduzir.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_offsets.py` ou gerador novo | consultar/estender |
| `wte/src/wte_cor.pas` (rota B) | modificar |
| `wte/tools/port_database_pas.py` (rota A, se escolhida) | modificar |
| `wte/re/spec/MainForm.lista_equiposChange.md` | modificar (veredito) |
| `wte/re/offsets-novos.md` | modificar |
| `docs/tasks/progresso.md` | modificar |

## Verificação

- [ ] `compara_tela.sh` verde nos **dez** — os oito CLASSIC (combo 56–63) e os
      dois de Master League (combo 68 e 85) —, com a bandeira batendo em pixel
      e tolerância zero
- [ ] `compara_tela.sh` continua verde nos times já conferidos (0, 2)
- [ ] `compare_dumps.py` continua idêntico entre Pascal e C++ nas **duas** ROMs
      — se a rota escolhida for a A, este critério cai e a divergência tem de
      ser registrada na
      [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md)
- [ ] `make -C wte check` e `lazbuild` verdes
- [ ] nenhum roteiro golden muda de veredito — este achado é de **tela**, e
      nenhum dos dois lados grava bandeira sem o usuário mandar
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
