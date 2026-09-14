---
id: CORR-LOOKS-019
title: "Correção: o `--tmds` promete dizer se algum campo move um TMD, e não pergunta — a metade negativa do veredito não sai de comando nenhum"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-LOOKS-019: a metade negativa do veredito não é medida por comando

## Problema identificado

O veredito da task tem dois lados, e o perfil deste ciclo faz disso a pergunta
obrigatória da Fase 2: *"o veredito distingue **medi e é isto** de **não achei o
contrário**?"*. O lado positivo está medido com endereço, seção e posição dentro
da primitiva, e reproduz. O lado negativo — **"e de TMD nenhum"** — não sai de
nenhum comando versionado.

O `check_tmds()` promete exatamente isso no próprio docstring:

```python
def check_tmds(verbose=True):
    """Are the four TMDs of plan section 1.6 in RAM, and does any field move one?

    The answer decides unknown (a) as much as the field diffs do, and it has to
    come from a command: "I looked and they were zero" is exactly the kind of
    claim this cycle keeps turning into a script.
    """
```

A função **não pergunta a segunda metade**. Ela restaura os dois slots, imprime
os quatro endereços da §1.6 (zerados), varre a RAM atrás de cabeçalho TMD e
imprime *"TMDs actually in RAM: 29"*. Não aperta tecla nenhuma, não chama
`field_diff()`, e não tem o que comparar com o quê.

E o `--fields`, que é quem move campo, **não conhece TMD**: o `report_field()`
atribui cada byte a arquivo/seção/primitiva e joga o resto num contador único —

```python
print("      in no model file: %d byte(s)" % elsewhere)
```

— 124 bytes para `HAIR`, 202 para `SKIN` no slot 2, 304 e 237 para `BODY`.
"Fora dos dois arquivos de modelo" e "fora dos TMDs" são afirmações diferentes,
e só a primeira é impressa. A frase do Log e do plano — *"e **nenhum campo de
LOOKS toca um deles**"* — é, hoje, leitura de dois relatórios que não se cruzam.

**A conclusão está certa.** Esta revisão mediu o cruzamento que falta, e deu
zero nos dois casos (abaixo). Por isso a criticidade é Média e não Alta: o que
não se sustenta é a evidência, não o resultado. Mas é exatamente a forma de
afirmação que este ciclo transforma em script — e o docstring da função já diz
isso, sobre si mesma.

## Evidência

O que o comando entrega hoje, reproduzido inteiro nesta revisão (idêntico nos
dois slots):

```text
$ python tools/looks/oracle.py --tmds
  slot 1 (goalkeeper):
      0x8016821c  000000000000000000000000   ALL ZERO
      0x80168c0c  000000000000000000000000   ALL ZERO
      0x8016a2c4  000000000000000000000000   ALL ZERO
      0x8016a650  000000000000000000000000   ALL ZERO
      TMDs actually in RAM: 29
          from 0x800c1678 to 0x800c4948, 4..54 vertices
```

Nenhuma linha sobre campo. E o que o `--fields` entrega, do outro lado:

```text
  SKIN, slot 2 (outfield player): 326 byte(s)
      /BIN/EDT_MOD.BIN section 0: 4 byte(s), at byte [2] of the primitive
      ...
      in no model file: 202 byte(s)
```

O cruzamento, medido nesta revisão com script descartável sobre a mesma API
(`field_diff()` + `attribute()` + `_tmd_headers()`):

```text
TMDs in RAM: 29, from 0x800c1678 to 0x800c4948
SKIN slot 2: 326 byte(s), 202 in no model file, 0 inside the TMD region
   residue by 4 KiB page: 0x8007d000:1, 0x800e7000:2, 0x800e9000:2,
     0x8010e000:1, 0x80153000:3, 0x80154000:59, 0x80155000:19, 0x80157000:25,
     0x80162000:34, 0x80163000:32, 0x80164000:1, 0x80165000:22, 0x801ff000:1
HAIR slot 1: 132 byte(s), 124 in no model file, 0 inside the TMD region
   residue by 4 KiB page: 0x8007d000:1, 0x800e7000:2, 0x800e9000:2,
     0x8010e000:1, 0x80153000:4, 0x80156000:1, 0x80157000:88, 0x80162000:4,
     0x80164000:1, 0x80165000:7, 0x80166000:13
```

Zero em região de TMD, com folga de 4 KiB depois do último cabeçalho. **É a
medição que o veredito precisava e que nenhum comando do repositório faz** — a
próxima pessoa que perguntar "e os TMDs?" vai reescrever este script.

O resíduo, de quebra, tem forma: ele se concentra entre `0x80153000` e
`0x80166000`, logo **abaixo** do endereço de carga do `MODEL.BIN`
(`0x8016E800`) e bem acima do fim do `EDT_MOD.BIN` (`0x80124CE8`). São as
faixas de buffer que a
[`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md) já tem
escrito para nomear.

## Causa raiz

As duas metades do veredito foram medidas por dois comandos que não se falam, e
o que cruzaria os dois — atribuir o resíduo do `field_diff()` ao mapa de TMDs —
não existe, apesar de o `check_tmds()` prometê-lo no docstring.

## Correção

### Arquivo: `tools/looks/oracle.py`

Fazer o comando cumprir o docstring. O caminho mais barato reusa o que já
existe, sem uma segunda corrida do emulador:

1. `_tmd_headers()` passa a devolver também a **extensão** de cada TMD (o
   cabeçalho já traz as contagens), e o módulo ganha um `tmd_spans(data)` no
   feitio do `spans()` que já mapeia os dois arquivos de modelo;
2. o `report_field()` recebe esse mapa e imprime **três** baldes em vez de dois
   — arquivo de modelo, **TMD** (com o índice do TMD) e "em nenhum dos dois" —,
   porque "nada fora" e "nada medido" continuam imprimindo igual enquanto só os
   acertos aparecem;
3. o `check_fields()` monta o mapa de TMD do mesmo snapshot em que já carrega o
   state, e o `--tmds` imprime a linha do cruzamento ou deixa de prometê-la.

### Caso vermelho

Sem um, a terceira coluna passa a imprimir `0` para sempre e ninguém percebe.
Um controle do catálogo — no feitio dos onze que já existem — que faça o
`attribute()`/`tmd_spans()` **não reconhecer** a região e exija que a contagem
de TMD deixe de bater é o que torna a asserção permanente. Serve também a
verificação sintética: uma faixa de TMD forjada num buffer de teste, com um
offset dentro dela, tem de cair no balde de TMD e não no de resíduo.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/oracle.py` | modificar |
| `tools/looks/controls.py` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |

## Verificação

- [ ] `python tools/looks/oracle.py --fields SKIN` imprime, por slot, quantos
      bytes caíram **em TMD** — e o número é zero por medição, não por omissão
- [ ] `--tmds` cumpre o que o docstring promete, ou o docstring deixa de
      prometer
- [ ] há caso vermelho: com o mapa de TMD estragado, a contagem muda
- [ ] a §1.6 do plano cita o comando que sustenta *"nenhum campo de LOOKS toca
      um deles"*, e não só o `--tmds` de hoje
- [ ] `python tools/looks/selftest.py` verde, com os controles todos vermelhos
- [ ] `python tools/looks/oracle.py --check` continua `0 failure(s)`
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
