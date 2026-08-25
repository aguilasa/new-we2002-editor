#!/usr/bin/env python3
"""O registro de divergencias deliberadas confere com o que as ferramentas isentam?

Produto da [WTE-TASK-35](../../docs/tasks/35-divergencias-deliberadas.md).

    python3 wte/tools/check_divergencias.py           # relata
    python3 wte/tools/check_divergencias.py --check   # o que `make -C wte check` roda

## Por que este script nao gera o markdown

Porque `wte/re/divergencias.md` NAO e gerado, e nao deve ser: as entradas dele
sao *decisao* -- por que reproduzir um bug e nao outro, por que nao implementar
uma tela. Prosa nao se gera, e um gerador que a produzisse estaria inventando
razao a partir de numero.

O que da para mecanizar e a outra metade, e e a que o enunciado da task nomeia
numa frase: **"uma excecao no golden sem entrada aqui e buraco"**. Entao este
script casa os dois lados, e so isso:

| lado | o que e |
|---|---|
| ferramenta | excecao NOMEADA que faz uma regua deixar de reprovar |
| documento | secao de `divergencias.md` que a explica |

Falta de qualquer um dos lados aborta.

## O inventario de excecoes, e por que ele e escrito a mao

`EXCECOES` lista onde cada isencao mora hoje. Ele nao e descoberto por
varredura: varrer o codigo atras de "coisas que parecem excecao" acharia
`conteudo` e `fora_da_faixa` do `compara_tela.py`, que nao sao divergencia entre
os dois lados -- sao regiao que a regua de pixel nao sabe medir. Confundir as
duas encheria o registro de entradas falsas, que e o defeito que a secao 9 do
proprio documento descreve.

A lista e curta de proposito e cada linha diz o predicado que a torna
verdadeira, para o script poder conferi-la em vez de acreditar nela.

## A conferencia que pegou algo de verdade

O grupo `pendente_32` isentava `bandera`, `home1` e `home2` de reprovar
enquanto o 2D nao estivesse desenhado. A WTE-TASK-29 desenhou, as
CORR-WTE-083/-084 consertaram a bandeira preta de dez times, e a isencao ficou
-- medido, os tres batem com numeros identicos dos dois lados. Uma isencao que
sobreviveu a propria causa nao protege nada: ela esconde a regressao seguinte.

Por isso a checagem e nos DOIS sentidos. Excecao sem entrada e buraco; entrada
sem excecao e prosa vencida.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WTE = ROOT / "wte"
DOC = WTE / "re" / "divergencias.md"
TOOLS = WTE / "tools"
ROTEIROS = WTE / "tests" / "roteiros"


class DivergError(Exception):
    pass


# Cada excecao nomeada: o titulo da secao que a explica no documento, e um
# predicado que confirma que ela AINDA existe na ferramenta.
#
# `secao` e casado pelo numero do cabecalho `## N.`, nao pelo texto inteiro --
# reescrever o titulo de uma secao nao deve derrubar o gate; remover a secao
# deve.
EXCECOES = [
    {
        "nome": "glifo_cinza",
        "secao": 2,
        "arquivo": "compara_tela.py",
        "predicado": r'"glifo_cinza"',
        "o_que_isenta": "os botoes cujo glifo e invariante sob `gdeDisabled`",
    },
    {
        "nome": "INVARIANTES",
        "secao": 2,
        "arquivo": "check_glifos_disabled.py",
        "predicado": r"^INVARIANTES = \{",
        "o_que_isenta": "os 5 glifos declarados que nao acinzentam",
    },
    {
        "nome": "ULTIMO_SLOT_PRECADO",
        "secao": 5,
        "arquivo": "check_preco.py",
        "predicado": r"ULTIMO_SLOT_PRECADO",
        "o_que_isenta": "o slot 22, que o original calcula e nao grava",
    },
]

# Excecoes RETIRADAS, e a secao que registra a retirada. Elas nao podem voltar
# a existir na ferramenta sem passar por aqui: e o segundo sentido da
# conferencia, e o unico que pega prosa vencida.
RETIRADAS = [
    {
        "nome": "pendente_32",
        "secao": 9,
        "arquivo": "compara_tela.py",
        "por_que": "os tres controles passaram a bater; a isencao sobreviveu "
                   "a propria causa",
    },
]


# A DIRECAO QUE FALTAVA -- CORR-WTE-114.
#
# As tabelas acima conferem EXCECAO DE FERRAMENTA contra entrada. A outra
# direcao -- achado de divergencia escrito numa task e sem entrada no registro
# -- passava batida, e o gate ficava verde. Foi o que aconteceu com as tres
# candidatas da WTE-TASK-37: a primeira delas se declarava *"ainda sem entrada
# aqui"* no markdown de uma task ja `concluido`, que ninguem executaria de novo.
#
# Prosa que se declara pendente e exatamente o que uma guarda consegue ler.
#
# O ALCANCE E ESTREITO DE PROPOSITO, e a palavra que o define e `ainda`. O
# enunciado da REGRA -- *"uma excecao no golden sem entrada aqui e buraco"* --
# aparece em cinco lugares vivos e nao e pendencia nenhuma; ele nunca diz
# "ainda". Alargar para `sem entrada aqui` cru marcaria os cinco, e guarda que
# erra e guarda que se desliga. E a mesma escolha do `BLOQUEIO_VENCIDO` do
# `check_fase4.py`, que restringe o verbo a "portar" pela mesma razao.
PENDENCIA_DECLARADA = [
    re.compile(r"ainda\s+sem\s+entrada\s+aqui", re.I),
    re.compile(r"ainda\s+sem\s+entrada\s+n[oa]\s+registro", re.I),
]

# Onde ela e procurada. Sao os documentos que descrevem divergencia e que nao
# sao o proprio registro -- o `divergencias.md` fica de fora porque uma frase
# assim DENTRO dele seria outra coisa (uma entrada incompleta, que os seis
# campos ja cobram).
ONDE_PROCURAR = ("docs/tasks", "wte/re")


def pendencias_declaradas() -> list[str]:
    """Frase que se declara sem entrada no registro, fora do registro."""
    achados: list[str] = []
    for pasta in ONDE_PROCURAR:
        raiz = ROOT / pasta
        if not raiz.is_dir():
            continue
        for arq in sorted(raiz.rglob("*.md")):
            if arq == DOC:
                continue
            # Os arquivos que CITAM a frase para a descrever, em vez de a
            # declarar: o markdown de cada correcao e o indice delas. Excluir
            # por nome, e nao por heuristica de contexto, porque a diferenca
            # entre citar e declarar nao se le de uma regex -- se le de onde a
            # frase esta.
            if arq.name.startswith("CORR-WTE-"):
                continue
            if arq.name == "correcoes-progresso.md":
                continue
            texto = arq.read_text(encoding="utf-8")
            for padrao in PENDENCIA_DECLARADA:
                for m in padrao.finditer(texto):
                    linha = texto.count("\n", 0, m.start()) + 1
                    achados.append(
                        f"{arq.relative_to(ROOT)}:{linha}: diz "
                        f"{m.group(0)!r} -- divergencia que se declara sem "
                        f"entrada no registro tem de TER a entrada, ou deixar "
                        f"de se dizer divergencia. Ver a CORR-WTE-114.")
    return achados


def secoes(texto: str) -> dict[int, str]:
    """Numero da secao -> titulo, dos cabecalhos `## N. ...`."""
    return {int(m.group(1)): m.group(2).strip()
            for m in re.finditer(r"^## (\d+)\. (.+)$", texto, re.M)}


def mede() -> dict:
    if not DOC.exists():
        raise DivergError(f"falta {DOC.relative_to(ROOT)}")
    texto = DOC.read_text(encoding="utf-8")
    tem = secoes(texto)
    problemas: list[str] = []

    for e in EXCECOES:
        alvo = TOOLS / e["arquivo"]
        if not alvo.exists():
            problemas.append(f"{e['arquivo']} nao existe, e {e['nome']} o cita")
            continue
        corpo = alvo.read_text(encoding="utf-8")
        vivo = re.search(e["predicado"], corpo, re.M) is not None
        if not vivo:
            problemas.append(
                f"a excecao `{e['nome']}` sumiu de {e['arquivo']}, e a secao "
                f"{e['secao']} de divergencias.md continua a explicando. "
                f"Excecao que some sem a entrada sair e PROSA VENCIDA -- o "
                f"documento passa a mandar procurar um problema que nao existe.")
        if e["secao"] not in tem:
            problemas.append(
                f"a excecao `{e['nome']}` (em {e['arquivo']}) nao tem secao "
                f"{e['secao']} em divergencias.md. Excecao no golden sem "
                f"entrada aqui e BURACO -- e o que o enunciado da WTE-TASK-35 "
                f"manda impedir.")

    for r in RETIRADAS:
        alvo = TOOLS / r["arquivo"]
        if alvo.exists() and re.search(rf'"{r["nome"]}"', alvo.read_text(encoding="utf-8")):
            problemas.append(
                f"a excecao `{r['nome']}` VOLTOU a {r['arquivo']}, e a secao "
                f"{r['secao']} de divergencias.md diz que ela foi retirada "
                f"({r['por_que']}). Ou a retirada esta errada, ou alguem a "
                f"desfez sem passar por aqui.")
        if r["secao"] not in tem:
            problemas.append(
                f"a retirada de `{r['nome']}` nao tem secao {r['secao']} em "
                f"divergencias.md")

    problemas.extend(pendencias_declaradas())

    # As faixas `conhecida:` da bateria de bytes. Hoje sao zero, e a secao 8 do
    # documento AFIRMA isso -- entao uma faixa nova sem entrada tem de abortar,
    # senao a afirmacao envelhece sozinha.
    com_faixa = sorted(
        p.stem for p in ROTEIROS.glob("golden-*.txt")
        if re.search(r"^conhecida:", p.read_text(encoding="utf-8"), re.M))
    if com_faixa:
        problemas.append(
            "roteiro declarando faixa `conhecida:` sem entrada em "
            f"divergencias.md: {', '.join(com_faixa)}. A secao 8 afirma que a "
            "bateria de bytes nao tem excecao nenhuma; uma faixa nova torna "
            "essa afirmacao falsa.")

    return {
        "excecoes": EXCECOES,
        "retiradas": RETIRADAS,
        "com_faixa": com_faixa,
        "secoes": tem,
        "problemas": problemas,
    }


def main(argv: list[str]) -> int:
    try:
        m = mede()
    except DivergError as e:
        print(f"check_divergencias: {e}", file=sys.stderr)
        return 2
    if m["problemas"]:
        for p in m["problemas"]:
            print(f"check_divergencias: {p}", file=sys.stderr)
        return 2
    rel = DOC.relative_to(ROOT)
    print(f"check_divergencias: {rel}: ok -- {len(m['excecoes'])} excecao(oes) "
          f"nomeada(s) com entrada, {len(m['retiradas'])} retirada(s) que nao "
          f"voltou(aram), {len(m['com_faixa'])} faixa(s) `conhecida:` na "
          f"bateria de bytes, {len(m['secoes'])} secao(oes) no documento")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
