#!/usr/bin/env python3
"""Fechamento da fase 4: os 96 tem veredito, e toda gravacao tem gate?

Gera `wte/re/fase-4.md` -- o produto da WTE-TASK-31. Irmao do `check_fase1.py`,
do `check_fase2.py` e do `check_fase3.py`, e pela mesma razao: fechamento de
fase so vale se os numeros dele sairem de ferramenta versionada. Contagem a mao
em doc ja se propagou neste repositorio (CORR-WTE-012, -014, -023).

## O que ele mede

| Mede | Como |
|---|---|
| cobertura | os 96 do `published_methods.tsv` contra os `.md` de `re/spec/` |
| distribuicao de veredito | o frontmatter de cada spec, pelo validador do `spec_index.py` |
| forca da evidencia | as linhas `**Evidencia:**` das cinco secoes obrigatorias |
| `nao portado` justificado | secao `## Justificativa` nao vazia |
| decompilado colado | as marcas do `spec_index.py` sobre specs, `.inc` e `.pas` |
| bloqueio vencido | rotina que a spec `aberto` diz nao portada e o Pascal tem |
| quem grava | a secao `## Bytes tocados` de cada spec |
| gate por gravacao | a tabela `GOLDEN_DE` abaixo, contra os roteiros em disco |
| resultado da bateria | `wte/re/fase-4-golden.tsv`, escrito pela corrida da task |

## Duas medidas que so aparecem aqui, e que mudam o numero de gravacoes

**As tasks nomearam nove gravacoes; medido, sao dezessete.** Nove e a conta de
quem alguem CHAMOU de gravacao: seis na WTE-TASK-27, uma na 28, uma na 29 e as
tres orfas da 30, menos o `grabar_memoryClick`. Lendo a secao
`## Bytes tocados` das 96 specs, a diferenca aparece nos dois sentidos:

- **entram** os sete de mover jogador e numero de camisa -- grupo `edicao`, que
  gravam dentro da `0x00404820` --, mais o `FormShow` e o
  `boton_dialogo_weClick`, que gravam no arranque;
- **saem** o `grabar_memoryClick` e o `grabar_camisetaClick`, que apesar do nome
  nao tocam a ROM: leem dela e emitem um arquivo.

Nao e preciosismo de contagem. Um handler que grava e nao esta na tabela de
gates deste gerador aborta o fechamento -- e era justamente por nao ter essa
conta que tres gravacoes ficaram sem dono ate a WTE-TASK-30.

## Como a leitura de "quem grava" e mecanica, e nao interpretacao

A primeira linha nao vazia de `## Bytes tocados` decide, depois de tirar a
enfase markdown e baixar a caixa:

- comeca com uma das formas de `NAO_GRAVA` -> nao toca a imagem;
- **contem** `nenhum` sem casar com nenhuma delas -> **aborta**. Frase nova de
  "nao grava" e a maneira barata de esta conta passar a mentir em silencio, e
  a saida e escolher uma das formas existentes ou acrescentar a sua aqui;
- qualquer outra coisa -> grava.

## A varredura de decompilado e mais estreita que a do `spec_index.py`, de proposito

O `spec_index.py` recusa `undefined` com digito OPCIONAL, e faz bem: ele varre
so as specs, que sao escritas em portugues, e ali `undefined` sozinho nao tem o
que fazer. Esta varredura tambem alcanca `.pas` e `.inc`, onde a palavra
aparece como adjetivo ingles -- o `we2002_types.pas` tem
`undefined behaviour, not a behaviour` num comentario, herdado da decisao de
nao reproduzir comportamento indefinido. Entao aqui o digito e OBRIGATORIO.

O custo esta escrito para nao ser esquecido: um `undefined` de Ghidra sem
digito passaria por esta varredura. As outras seis marcas continuam iguais, e
sao as que nao tem homonimo em prosa.

Uso:

    python3 wte/tools/check_fase4.py            # regenera
    python3 wte/tools/check_fase4.py --check    # confere contra o commitado
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_fase1 as F1  # noqa: E402  (o perimetro de doc vivo, ja escrito la)
import dfm2lfm as D  # noqa: E402  (o nome da unidade de cada formulario)
import spec_index as S  # noqa: E402  (o validador e o vocabulario)

ROOT = Path(__file__).resolve().parents[2]
WTE = ROOT / "wte"
IMPL = WTE / "src" / "impl"
SRC = WTE / "src"
ROTEIROS = WTE / "tests" / "roteiros"
OUT = WTE / "re" / "fase-4.md"
BATERIA = WTE / "re" / "fase-4-golden.tsv"
# A bateria completa da WTE-TASK-34. Este gerador NAO a publica -- quem
# faz isso e o `check_golden.py`. Ela e lida so para o guarda de
# cobertura, e a ausencia do arquivo nao e erro: ate a fase 6 ele nao
# existia, e a fase 4 fechou sem ele.
COMPLETA = WTE / "re" / "golden.tsv"
REAMOSTRA = WTE / "re" / "fase-4-trivial.tsv"

GENERATOR = "wte/tools/check_fase4.py"

# As formas aceitas de "nao toca a imagem", na primeira linha de
# `## Bytes tocados`. Sao as que as specs usam hoje -- a populacao nao entra
# na frase de proposito: ela cresce a cada spec nova e o numero envelheceria
# sozinho aqui, que foi o defeito da CORR-WTE-102.
#
# A CLASSIFICACAO E BINARIA DE PROPOSITO -- toca a imagem, ou nao toca. Uma
# terceira classe ("nao toca, mas emite um arquivo") seria util e NAO se le
# daqui: `Nenhum na imagem` abre tanto a spec do `grabar_memoryClick`, que
# emite um `.mcr`, quanto a do `gradienteClick`, que so mexe na paleta em
# memoria. A mesma frase, dois fatos. Quem sabe a diferenca e o roteiro, pelo
# `--artefato`, e e de la que o numero sai.
NAO_GRAVA = (
    "nenhum",
    "na imagem de cd: nenhum",
    "na imagem: nenhum",
)

# Marcas de decompilado colado. Sao as do `spec_index.py` com UMA diferenca,
# explicada no cabecalho: aqui `undefined` exige digito.
_TIPO_C = (r"(?:(?:un)?signed +)?"
           r"(?:int|uint|short|ushort|byte|char|long|ulong|undefined[0-9])")
MARCAS = (
    (re.compile(r"^```\s*(c|cpp|c\+\+)\s*$", re.M | re.I), "bloco marcado c/cpp"),
    (re.compile(r"\bundefined[0-9]\b"), "tipo undefined<n> do Ghidra"),
    (re.compile(r"\b[iuf]Var[0-9]+\b"), "variavel uVar<n>/iVar<n>"),
    (re.compile(r"\blocal_[0-9a-f]+\b"), "local_<hex>"),
    (re.compile(r"\bparam_[0-9]+\b"), "param_<n>"),
    (re.compile(r"\b(DAT|FUN|LAB|PTR)_[0-9a-f]{6,}\b"), "simbolo DAT_/FUN_"),
    (re.compile(r"__fastcall\b"), "__fastcall"),
    (re.compile(rf"\({_TIPO_C}\)\s*\*\s*\(\s*{_TIPO_C}\s*\*\s*\)"), "cast de deref"),
)

# --------------------------------------------------------------------------
# A guarda de BLOQUEIO VENCIDO -- terceira passagem da WTE-TASK-31, 2026-08-23.
#
# Um veredito `aberto` e sustentado por prosa: "aberto porque a `0x…` nao esta
# portada". A prosa envelhece e o veredito nao: a rotina e portada por outra
# task, ninguem volta na spec, e o `aberto` continua la afirmando um bloqueio
# que caiu. Aconteceu com o `0x0040a0b4` (portada pela CORR-WTE-082 em
# 2026-08-21) segurando DOIS vereditos do `estrategia` por dois dias, e com o
# `0x00404820` segurando o `mostrar_jugadorClick`.
#
# A guarda e mecanica: numa spec `aberto`, endereco citado como "nao portada"
# que APARECA em `src/*.pas` ou `src/impl/*.inc` aborta o fechamento. Nao ha
# julgamento -- ou o endereco esta no Pascal, ou nao esta.
#
# O ALCANCE, escrito para nao ser esquecido: ela pega a forma "nao (esta)
# portad[ao]" e mais nenhuma. "0x… nao lida", "nao existe" e "falta a 0x…"
# passam por ela -- foram medidas e produzem falso positivo, porque as specs
# usam esses verbos para dado e para campo de imagem, nao so para rotina
# ("o campo nao existe na imagem", "a tabela nao existe no arquivo: e .bss").
# Estreitar o verbo foi a escolha: guarda que erra e desligada, guarda que
# cala em um caso continua servindo nos outros.
#
# A JANELA para por quebra de paragrafo, nao por ponto. `[^.]` seria o
# instinto e esta errado duas vezes: casa `\n` (a armadilha 2 do prompt) e
# nao atravessa `MainForm.mostrar_estrategiaClick` -- nome qualificado tem
# ponto, e era exatamente essa a frase do `bolaMouseDown`.
_ENDERECO = r"0x[0-9a-fA-F]{6,8}"
_NAO_PORTADA = "n[ãa]o\\s+(?:est[áa]\\s+)?portad[ao]"
# vao de ate 200 caracteres sem OUTRO endereco pelo meio (para o par ser o
# mais proximo) e sem linha em branco (para nao atravessar paragrafo)
_VAO = rf"(?:(?!{_ENDERECO})(?!\n[ \t]*\n).){{0,200}}?"
BLOQUEIO_VENCIDO = (
    re.compile(rf"({_ENDERECO}){_VAO}{_NAO_PORTADA}", re.S),
    re.compile(rf"{_NAO_PORTADA}{_VAO}({_ENDERECO})", re.S),
)


def enderecos_no_pascal() -> set[str]:
    """Todo `0x…` citado no Pascal escrito a mao ou gerado, em minuscula."""
    achados: set[str] = set()
    for arq in sorted(SRC.glob("*.pas"), key=lambda p: p.as_posix()) + sorted(IMPL.glob("*.inc"), key=lambda p: p.as_posix()):
        achados |= {e.lower() for e in
                    re.findall(_ENDERECO, arq.read_text(encoding="utf-8"))}
    return achados


# Os arquivos de `re/spec/` que documentam as marcas em vez de as conterem.
# Sao os mesmos que o `spec_index.py` reserva.
RESERVADOS = {"GABARITO.md", "INDICE.md", "README.md"}

# Qual roteiro golden julga cada handler que grava.
#
# TABELA A MAO, E COM GUARDA. O dialeto de roteiro do `roteiro.sh` nao tem
# campo para o handler -- o cabecalho aceita `alvo:`, `estado:`, `operacao:`,
# `conhecida:` e `espera:`, e linha desconhecida vira `AVISO: linha ignorada`.
# Inventar um campo mexeria no contrato do harness por causa de um documento.
#
# A guarda e o que impede a tabela de envelhecer em silencio: todo handler que
# a secao `## Bytes tocados` diz que grava TEM de aparecer aqui, e todo roteiro
# citado tem de existir em disco. Gravacao nova sem gate aborta o fechamento.
#
# **E as duas guardas abaixo existem porque a tabela ja envelheceu em silencio
# uma vez.** A CORR-WTE-096 achou `"MainForm.base_teamClick"` escrito DUAS
# vezes aqui: a entrada boa, com o `golden-22-precos`, e a velha da epoca em que
# o handler estava `aberto`, com a tupla vazia. Em Python a ultima ganha, e
# nenhuma das guardas de cima reclama -- a chave EXISTE, e as duas se perguntam
# sobre chave, nao sobre valor. O `fase-4.md` passou a publicar `**nenhum**` na
# linha do unico escritor cujo gate estava verde, tres linhas abaixo da frase
# que promete abortar nesse caso.
GOLDEN_DE: dict[str, tuple[str, ...]] = {
    # as seis da WTE-TASK-27
    "MainForm.boton_barras2isoClick": ("golden-03-barras", "golden-04-barras-editada"),
    "MainForm.boton_nombres2isoClick": ("golden-05-nomes",),
    "MainForm.boton_tex2isoClick": ("golden-06-textura",),
    "MainForm.dorsalClick": ("golden-08-dorsal-mcr",),
    # WTE-TASK-32 -- o preco do time inteiro, a nona rota de escrita.
    "MainForm.base_teamClick": ("golden-22-precos",),
    "MainForm.paderechaClick": ("golden-09-mover",),
    "MainForm.paizquierdaClick": ("golden-09-mover",),
    "MainForm.paderechaeizquierdaClick": ("golden-09-mover",),
    "MainForm.paderecha2Click": ("golden-10-mover-ml",),
    "MainForm.paizquierda2Click": ("golden-10-mover-ml",),
    "MainForm.pabajoClick": ("golden-11-descarte-ml",),
    # a da WTE-TASK-28
    "MainForm.boton_mcr2isoClick": ("golden-12-mcr2iso", "golden-13-roundtrip"),
    # as tres orfas da WTE-TASK-30, fechadas pela CORR-WTE-081
    "jugador.BitBtn3Click": ("golden-15-ficha", "golden-18-ficha-edicao",
                             "golden-19-ficha-original",
                             "golden-20-ficha-reserva"),
    "ficha_color.BitBtn3Click": ("golden-16-cor",),
    "estrategia.BitBtn3Click": ("golden-17-tatica", "golden-21-arrasto"),
    # as duas que gravam sem ser botao de gravar
    "MainForm.FormShow": ("golden-01-arranque",),
    "MainForm.boton_dialogo_weClick": ("golden-01-arranque",),
}


# A decisao sobre cada ponto de evidencia fraca -- criterio 3 da task, que
# pede "listar, e decidir quais precisam de disassembly antes da Fase 6".
#
# TABELA A MAO, E COM GUARDA, pela mesma razao do `GOLDEN_DE`: ponto fraco novo
# sem decisao aborta o fechamento, e decisao orfa tambem. O que ela NAO faz e
# julgar sozinha -- "observacao de tela" as vezes e a evidencia certa, e dizer
# qual e o caso e trabalho de quem le.
DECISAO_FRACA: dict[tuple[str, str], str] = {
    ("MainForm.boton_dialogo_weClick", "Comportamento de erro"):
        "**Fica.** A afirmação é sobre **ausência** de tratamento — o original "
        "não confere nada além do tamanho, e a checagem de tamanho é só aviso. "
        "Ausência não tem endereço para ler: o disassembly já mostrou que não "
        "há ramo de erro, e a tela mostrou o que acontece sem ele.",
    ("MainForm.FormShow", "Comportamento de erro"):
        "**Fica, e tem dono.** O original encerra e o port não — é divergência "
        "deliberada, registrada para a "
        "[WTE-TASK-35](../../docs/tasks/concluidos/35-divergencias-deliberadas.md). "
        "Para *\"o original encerra\"*, tela é a evidência certa: o que se mede é "
        "o efeito observável, não a instrução.",
    ("MainForm.mostrar_jugadorClick", "Bytes tocados"):
        "**Fica.** A seção diz `Nenhum gravado`, e o que ficou por medir são as "
        "faixas **lidas**. O golden do grupo prova a metade que importa para a "
        "fase 4 — ele não grava —, e o mapa de leitura só faz falta a quem for "
        "otimizar carga, que não é desta fase.",
}


class Fase4Error(Exception):
    pass


# Quantos `trivial` a task manda reconferir, e como eles sao escolhidos.
#
# A REGRA E DECLARADA, E NAO "ao acaso". O enunciado pede cinco ao acaso, e
# sorteio de verdade quebraria o `--check`: cada corrida escolheria outros
# cinco e o arquivo gerado nunca casaria com o commitado. Cinco ESPACADOS
# uniformemente pela lista ordenada por endereco dao a mesma propriedade que o
# sorteio existe para dar -- ninguem escolhe quais depois de ver o resultado --
# e sao reproduziveis.
#
# A amostra sai proporcional a populacao, e isso importa: 14 dos 19 `trivial`
# sao `FormCreate` da forma "cor", entao uma amostra que os evitasse estaria
# medindo outra coisa que nao o grupo.
REAMOSTRA_N = 5


def cinco_trivial(triviais: list[dict]) -> list[dict]:
    ordenados = sorted(triviais, key=lambda d: d["endereco"])
    n = len(ordenados)
    if n < REAMOSTRA_N:
        raise Fase4Error(
            f"so ha {n} handlers `trivial` -- a task pede {REAMOSTRA_N}")
    indices = sorted({round(i * (n - 1) / (REAMOSTRA_N - 1))
                      for i in range(REAMOSTRA_N)})
    return [ordenados[i] for i in indices]


def le_reamostra() -> dict[str, dict]:
    if not REAMOSTRA.exists():
        raise Fase4Error(
            f"{REAMOSTRA.relative_to(ROOT)} nao existe. Ele e o registro da "
            f"reconferencia dos cinco `trivial`, e sem ele o criterio 6 da "
            f"WTE-TASK-31 nao tem evidencia.")
    linhas = [l for l in REAMOSTRA.read_text(encoding="utf-8").splitlines()
              if l.strip()]
    cab = linhas[0].split("\t")
    esperado = ["handler", "endereco", "bytes", "confirmado",
                "o_que_o_corpo_faz"]
    if cab != esperado:
        raise Fase4Error(f"{REAMOSTRA.name}: cabecalho {cab} -- esperava {esperado}")
    return {d["handler"]: d
            for d in (dict(zip(cab, l.split("\t"))) for l in linhas[1:])}


# ---------------------------------------------------------------- vocabulario ---
# O numero de secoes obrigatorias SAI do `spec_index.SECOES`, nunca de literal.
#
# A CORR-WTE-101 nasceu de "seis secoes obrigatorias" escrito em tres lugares
# contra as cinco que o `spec_index.py` cobra -- o `GABARITO.md` tinha contado a
# `## Notas` opcional junto, e o numero migrou dali para o cabecalho deste
# gerador e para a prosa que ele emite. Escrever a palavra por extenso a partir
# de `len(S.SECOES)` faz a frase acompanhar o vocabulario: acrescentar uma secao
# obrigatoria muda a prosa gerada em vez de produzir a proxima "seis".
_EXTENSO = {1: "uma", 2: "duas", 3: "tres", 4: "quatro", 5: "cinco",
            6: "seis", 7: "sete", 8: "oito", 9: "nove", 10: "dez"}


def por_extenso(n: int) -> str:
    """O cardinal em palavra, ou o algarismo se sair da faixa util."""
    return _EXTENSO.get(n, str(n))


# ------------------------------------------------------------------ leitura ---
# Uma cerca de bloco de codigo sozinha na linha. A `boton_tex2isoClick` abre a
# secao com um bloco `text` -- a cerca nao e a resposta, e a linha seguinte e.
_CERCA = re.compile(r"^\s*`{3,}\s*\w*\s*$")


def normaliza_primeira_linha(corpo: str) -> str:
    """A primeira linha que diz alguma coisa, sem enfase e em caixa baixa."""
    for linha in corpo.splitlines():
        if not linha.strip() or _CERCA.match(linha):
            continue
        # A enfase markdown some das PONTAS, e so delas: `replace` global
        # comeria o `*` de multiplicacao da `boton_tex2isoClick`.
        return linha.strip().strip("*`").strip().lower()
    return ""


def grava_na_imagem(chave: str, corpo: str) -> bool:
    """A spec diz que este handler escreve na imagem de CD?"""
    linha = normaliza_primeira_linha(corpo)
    if not linha:
        raise Fase4Error(
            f"{chave}: a secao '## Bytes tocados' esta vazia. Ela e obrigatoria "
            f"e 'nenhum' e resposta -- vazia nao e.")
    for forma in NAO_GRAVA:
        if linha.startswith(forma):
            return False
    if "nenhum" in linha:
        raise Fase4Error(
            f"{chave}: '## Bytes tocados' comeca com {linha[:60]!r}, que contem "
            f"'nenhum' e nao casa com nenhuma das formas conhecidas "
            f"({', '.join(NAO_GRAVA)}). Frase nova de 'nao grava' faria esta "
            f"conta mentir em silencio: escolha uma das formas ou acrescente a "
            f"sua a NAO_GRAVA em {GENERATOR}.")
    return True


def le_bateria() -> list[dict]:
    if not BATERIA.exists():
        raise Fase4Error(
            f"{BATERIA.relative_to(ROOT)} nao existe. Ele e o registro da corrida "
            f"da bateria golden deste fechamento, e sem ele o criterio 4 da "
            f"WTE-TASK-31 nao tem evidencia.")
    linhas = [l for l in BATERIA.read_text(encoding="utf-8").splitlines() if l.strip()]
    cab = linhas[0].split("\t")
    esperado = ["roteiro", "modo", "veredito", "segundos", "tentativas", "data"]
    if cab != esperado:
        raise Fase4Error(
            f"{BATERIA.name}: cabecalho {cab} -- esperava {esperado}")
    return [dict(zip(cab, l.split("\t"))) for l in linhas[1:]]


def le_bateria_completa() -> set[str]:
    """Os roteiros cobertos nos DOIS modos pela bateria da WTE-TASK-34.

    Ausencia do arquivo devolve conjunto vazio, e isso e deliberado: a fase 4
    fechou antes de a bateria completa existir, e este gerador precisa
    continuar rodando num estado em que ela nao existe. O que ele NAO pode e
    aceitar um arquivo malformado em silencio -- ai o guarda de cobertura
    passaria a nao guardar nada.
    """
    if not COMPLETA.exists():
        return set()
    linhas = [l for l in COMPLETA.read_text(encoding="utf-8").splitlines()
              if l.strip()]
    if not linhas:
        return set()
    cab = linhas[0].split("\t")
    esperado = ["roteiro", "rom", "modo", "veredito", "segundos", "data"]
    if cab != esperado:
        raise Fase4Error(
            f"{COMPLETA.name}: cabecalho {cab} -- esperava {esperado}")
    modos: dict[str, set[str]] = {}
    for l in linhas[1:]:
        d = dict(zip(cab, l.split("\t")))
        modos.setdefault(d["roteiro"], set()).add(d["modo"])
    return {n for n, m in modos.items() if m == {"controle", "golden"}}


def roteiros_em_disco() -> dict[str, dict]:
    fora: dict[str, dict] = {}
    for arq in sorted(ROTEIROS.glob("golden-*.txt"), key=lambda p: p.as_posix()):
        if arq.name.endswith(".port.txt"):
            continue
        nome = arq.stem
        texto = arq.read_text(encoding="utf-8")
        def campo(chave: str) -> str:
            m = re.search(rf"^{chave}: *(.+)$", texto, re.M)
            return m.group(1).strip() if m else ""
        fora[nome] = {
            "operacao": campo("operacao"),
            "par": (ROTEIROS / f"{nome}.port.txt").exists(),
            "artefato": "--artefato" in texto,
        }
    return fora


# ------------------------------------------------------------------ medicao ---
def chaves_repetidas_no_fonte(nome: str = "GOLDEN_DE") -> list[str]:
    """As chaves escritas mais de uma vez no literal de `nome`, lidas da FONTE.

    Quando este modulo roda, o interpretador ja colapsou o literal: o
    `dict` em memoria tem uma entrada so, e a duplicata e invisivel. Por isso a
    conferencia e sobre o texto do arquivo, com `ast` -- o mesmo desenho do
    `check_seeks()` do `port_database_pas.py`, que confere o legado e nao a
    saida.
    """
    arvore = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    for no in ast.walk(arvore):
        alvo = getattr(no, "target", None)
        if not isinstance(no, ast.AnnAssign) or getattr(alvo, "id", "") != nome:
            continue
        chaves = [c.value for c in no.value.keys]
        return sorted({c for c in chaves if chaves.count(c) > 1})
    raise Fase4Error(f"nao achei o literal de {nome} em {GENERATOR}")


def gates_vazios(escritores: list[dict]) -> list[str]:
    """Escritor `implementado` cuja tupla de gate esta vazia.

    A tupla vazia so faz sentido para handler `aberto`, onde ela quer dizer
    "o gate vem com o dono". Num escritor `implementado` ela vira `**nenhum**`
    na tabela publicada, e `**nenhum**` num handler que grava e exatamente o
    buraco que a WTE-TASK-30 pagou para descobrir.
    """
    return sorted(e["handler"] for e in escritores
                  if e["veredito"] == "implementado"
                  and not GOLDEN_DE.get(e["handler"]))


def medir() -> dict:
    handlers = S.le_handlers()
    if len(handlers) != 96:
        raise Fase4Error(
            f"published_methods.tsv tem {len(handlers)} handlers, esperava 96")

    vereditos: dict[str, int] = {v: 0 for v in S.VEREDITOS}
    evidencias: dict[str, int] = {e: 0 for e in S.EVIDENCIAS}
    evidencias_fora = 0   # linhas `**Evidencia:**` em secao que nao e cobrada
    sem_spec: list[str] = []
    fracas: list[dict] = []
    pontos_fracos: list[dict] = []
    abertos: list[dict] = []
    triviais: list[dict] = []
    escritores: list[dict] = []
    nao_portados: list[str] = []
    citados_como_ausentes: list[tuple[str, str]] = []

    for h in handlers:
        chave = f"{h['formulario']}.{h['handler']}"
        arq = S.SPEC / f"{chave}.md"
        if not arq.exists():
            sem_spec.append(chave)
            continue
        veredito, evid = S.valida(arq, h)
        vereditos[veredito] += 1
        for e in evid:
            evidencias[e] += 1

        texto = arq.read_text(encoding="utf-8")
        secs = S.secoes_de(texto)

        # A conta acima e das SECOES COBRADAS. Uma spec pode escrever evidencia
        # em `## Notas`, `## Justificativa` ou `## Como o veredito fechou`, e
        # essas linhas existem no arquivo sem entrar na distribuicao -- medir a
        # diferenca e o que impede a prosa de prometer "todas as linhas".
        evidencias_fora += (
            len(S.CABECALHO_EVIDENCIA.findall(texto))
            - sum(len(S.CABECALHO_EVIDENCIA.findall(secs.get(nome, "")))
                  for nome in S.SECOES))

        # spec cuja evidencia INTEIRA e fraca -- o `spec_index.py` ja recusa a
        # combinacao com `implementado`; aqui a pergunta e mais larga.
        if set(evid) <= {"observacao de tela", "nao medido"}:
            fracas.append({"handler": chave, "veredito": veredito})
        # e as secoes soltas que se apoiam em evidencia fraca
        for nome in S.SECOES:
            for bruto in S.CABECALHO_EVIDENCIA.findall(secs.get(nome, "")):
                valor = S.sem_acento(bruto.strip().lower())
                if valor in ("observacao de tela", "nao medido"):
                    pontos_fracos.append({"handler": chave, "secao": nome,
                                          "evidencia": valor})

        if veredito == "trivial":
            triviais.append({"endereco": h["endereco"], "handler": chave})

        if veredito == "nao portado":
            nao_portados.append(chave)

        if veredito == "aberto":
            unidade = D.nome_da_unidade(h["formulario"])
            inc = IMPL / f"{unidade}.{h['handler']}.inc"
            abertos.append({"endereco": h["endereco"], "handler": chave,
                            "grupo": h["grupo"], "corpo": inc.exists()})
            for padrao in BLOQUEIO_VENCIDO:
                for citado in padrao.findall(texto):
                    citados_como_ausentes.append((chave, citado.lower()))

        if grava_na_imagem(chave, secs["Bytes tocados"]):
            escritores.append({"endereco": h["endereco"], "handler": chave,
                               "grupo": h["grupo"], "veredito": veredito})

    # --- as guardas da tabela de gate ------------------------------------
    repetidas = chaves_repetidas_no_fonte()
    if repetidas:
        raise Fase4Error(
            f"GOLDEN_DE tem chave repetida: {', '.join(repetidas)}. Em Python a "
            f"ultima ocorrencia ganha, e as guardas de nome nao veem a "
            f"diferenca -- apague a sobra em {GENERATOR}.")
    nomes_escritores = {e["handler"] for e in escritores}
    fora_da_tabela = sorted(nomes_escritores - set(GOLDEN_DE))
    if fora_da_tabela:
        raise Fase4Error(
            "handler que grava e nao esta em GOLDEN_DE: "
            f"{', '.join(fora_da_tabela)}. Gravacao nova sem gate declarado e "
            f"exatamente o que este fechamento existe para nao deixar passar -- "
            f"acrescente o roteiro (ou a tupla vazia, com dono nomeado) em "
            f"{GENERATOR}.")
    sobrando = sorted(set(GOLDEN_DE) - nomes_escritores)
    if sobrando:
        raise Fase4Error(
            "GOLDEN_DE cita handler que a spec nao diz que grava: "
            f"{', '.join(sobrando)}")
    vazios = gates_vazios(escritores)
    if vazios:
        raise Fase4Error(
            f"escritor `implementado` sem roteiro em GOLDEN_DE: "
            f"{', '.join(vazios)}. Tupla vazia so vale para handler `aberto`, "
            f"onde o gate vem com o dono; aqui ela publica `**nenhum**` na "
            f"linha de quem grava.")

    # --- a guarda de bloqueio vencido ------------------------------------
    no_pascal = enderecos_no_pascal()
    vencidos = sorted({(h, e) for h, e in citados_como_ausentes
                       if e in no_pascal})
    if vencidos:
        raise Fase4Error(
            "spec `aberto` diz que uma rotina nao esta portada e ela esta: "
            + ", ".join(f"{h} cita {e}" for h, e in vencidos)
            + ". Veredito preso por prosa vencida e o modo como o `aberto` "
              "mente sem que ninguem minta -- reconfira o veredito contra a "
              "regua e reescreva a razao, ou promova.")

    disco = roteiros_em_disco()
    citados = {r for rs in GOLDEN_DE.values() for r in rs}
    faltando = sorted(citados - set(disco))
    if faltando:
        raise Fase4Error(
            f"GOLDEN_DE cita roteiro que nao existe: {', '.join(faltando)}")

    # --- varredura de decompilado ----------------------------------------
    alvos = [a for a in sorted(S.SPEC.glob("*.md"), key=lambda p: p.as_posix()) if a.name not in RESERVADOS]
    alvos += sorted(IMPL.glob("*.inc"), key=lambda p: p.as_posix())
    alvos += sorted(SRC.glob("*.pas"), key=lambda p: p.as_posix())
    suspeitos = []
    for arq in alvos:
        texto = arq.read_text(encoding="utf-8")
        for marca, rotulo in MARCAS:
            achado = marca.search(texto)
            if achado:
                suspeitos.append({"arquivo": str(arq.relative_to(ROOT)),
                                  "marca": rotulo,
                                  "trecho": achado.group(0)[:40]})

    # --- os cinco `trivial` reconferidos ---------------------------------
    amostra = cinco_trivial(triviais)
    registro = le_reamostra()
    faltando_amostra = [x["handler"] for x in amostra
                        if x["handler"] not in registro]
    if faltando_amostra:
        raise Fase4Error(
            "a amostra de `trivial` mudou e o registro nao acompanhou: "
            f"{', '.join(faltando_amostra)} nao esta em {REAMOSTRA.name}. "
            "Handler que entra ou sai do veredito `trivial` desloca a amostra, "
            "e reconferencia velha nao vale para handler novo.")
    sobrando_amostra = sorted(set(registro) - {x["handler"] for x in amostra})
    if sobrando_amostra:
        raise Fase4Error(
            f"{REAMOSTRA.name} traz handler fora da amostra de hoje: "
            f"{', '.join(sobrando_amostra)}")
    nao_confirmados = [h for h, d in registro.items() if d["confirmado"] != "sim"]

    # --- a guarda das decisoes sobre evidencia fraca ---------------------
    chaves_fracas = {(x["handler"], x["secao"]) for x in pontos_fracos}
    sem_decisao = sorted(chaves_fracas - set(DECISAO_FRACA))
    if sem_decisao:
        raise Fase4Error(
            "ponto de evidencia fraca sem decisao escrita: "
            + ", ".join(f"{h} [{s}]" for h, s in sem_decisao)
            + f". O criterio 3 da WTE-TASK-31 pede a decisao, nao so a lista -- "
              f"acrescente-a a DECISAO_FRACA em {GENERATOR}.")
    decisao_orfa = sorted(set(DECISAO_FRACA) - chaves_fracas)
    if decisao_orfa:
        raise Fase4Error(
            "DECISAO_FRACA decide sobre ponto que nao existe mais: "
            + ", ".join(f"{h} [{s}]" for h, s in decisao_orfa))

    bateria = le_bateria()
    por_roteiro: dict[str, dict[str, str]] = {}
    for linha in bateria:
        por_roteiro.setdefault(linha["roteiro"], {})[linha["modo"]] = linha["veredito"]

    # Todo roteiro com par `.port` tem de ter as duas corridas registradas --
    # em UMA das duas baterias.
    #
    # Ate a WTE-TASK-34 havia uma so, e este guarda exigia o registro AQUI. A
    # fase 6 acrescentou a bateria completa (`re/golden.tsv`, operacao x ROM) e
    # com ela dois roteiros que sao dela e nao desta fase: o de edicao multipla
    # e o de gravacao dupla. Exigi-los no `fase-4-golden.tsv` obrigaria o
    # registro da fase 4 a crescer toda vez que uma fase POSTERIOR escrevesse
    # um roteiro -- e a data daquela corrida passaria a mentir.
    #
    # O que o guarda quer dizer nao mudou: roteiro que existe com par foi
    # rodado nos dois modos, e o resultado esta escrito em algum lugar
    # versionado. So a lista de lugares e que passou a ser duas.
    cobertos = {n for n, d in por_roteiro.items()
                if set(d) == {"controle", "golden"}}
    cobertos |= le_bateria_completa()
    sem_registro = sorted(
        n for n, d in disco.items() if d["par"] and n not in cobertos)
    if sem_registro:
        raise Fase4Error(
            "roteiro com par de port e sem as duas corridas em "
            f"{BATERIA.name} nem em {COMPLETA.name}: "
            f"{', '.join(sem_registro)}. O criterio 4 diz "
            "'golden verde', e o controle vem antes do teste.")

    return {
        "handlers": len(handlers),
        "vereditos": vereditos,
        "sem_spec": sem_spec,
        "evidencias": evidencias,
        "evidencias_fora": evidencias_fora,
        "fracas": fracas,
        "pontos_fracos": pontos_fracos,
        "abertos": abertos,
        "nao_portados": nao_portados,
        "escritores": escritores,
        "amostra": [registro[x["handler"]] for x in amostra],
        "nao_confirmados": nao_confirmados,
        "roteiros": disco,
        "bateria": bateria,
        "por_roteiro": por_roteiro,
        "suspeitos": suspeitos,
        "varridos": len(alvos),
    }


# -------------------------------------------------------------------- saida ---
def gera_md(m: dict) -> str:
    linhas: list[str] = []
    a = linhas.append

    total = m["handlers"]
    com_spec = total - len(m["sem_spec"])
    v = m["vereditos"]
    fechados = v["implementado"] + v["trivial"] + v["divergencia deliberada"] \
        + v["nao portado"]
    pendentes = v["aberto"] + len(m["sem_spec"])

    a("# `re/fase-4.md` — o fechamento da fase 4")
    a("")
    a("**GERADO — não editar à mão.** Correção entra no gerador e o arquivo")
    a("é regerado:")
    a("")
    a("```sh")
    a(f"python3 {GENERATOR}")
    a(f"python3 {GENERATOR} --check   # o que `make -C wte check` roda")
    a("```")
    a("")
    a("Produto da [WTE-TASK-31](../../docs/tasks/concluidos/31-fechamento-fase-4.md).")
    a("Fonte: [`published_methods.tsv`](published_methods.tsv), os `.md` de")
    a("[`spec/`](spec/), os `.inc` de [`../src/impl/`](../src/impl/), os")
    a("roteiros de [`../tests/roteiros/`](../tests/roteiros/) e o registro da")
    a(f"bateria em [`{BATERIA.name}`]({BATERIA.name}).")
    a("**Todo número daqui saiu do script.**")
    a("")
    a("## O critério, e onde ele está")
    a("")
    a("> **Pronto quando:** os 96 têm veredito e nenhum é \"não portado\" sem")
    a("> justificativa escrita.")
    a("")
    a(f"**{fechados} dos {total} têm veredito fechado; {pendentes} não.**")
    # As duas metades do criterio sao independentes, e a prosa era escrita
    # como se a primeira nunca fechasse -- ela dizia "e a primeira nao" com
    # `pendentes` ja em 0, na quinta passagem de 2026-08-24. Numero e frase
    # discordando no MESMO paragrafo e a forma mais barata de um gerado
    # passar a mentir: quem le a frase nao confere o numero ao lado.
    a("A segunda metade do critério está cumprida — ver a seção do")
    if pendentes:
        a("`nao portado` abaixo —, e a primeira não.")
    else:
        a("`nao portado` abaixo —, e a primeira também: nenhum handler ficou")
        a("`aberto`, e nenhum ficou sem arquivo de spec.")
    a("")

    a("## Cobertura e vereditos")
    a("")
    a("| Veredito | Handlers |")
    a("|---|---:|")
    for nome in S.VEREDITOS:
        a(f"| `{nome}` | {v[nome]} |")
    a(f"| *(sem arquivo de spec)* | {len(m['sem_spec'])} |")
    a(f"| **total** | **{total}** |")
    a("")
    a(f"{com_spec} dos {total} têm arquivo de spec.")
    if m["sem_spec"]:
        a("Os que não têm:")
        a("")
        for chave in m["sem_spec"]:
            a(f"- `{chave}`")
    # A linha em branco fecha o bloco NOS DOIS ESTADOS. Dentro do `if` ela so
    # existia quando havia handler sem spec -- e o estado de fechamento, que e
    # o que este arquivo tem de agora em diante, e justamente `sem_spec` vazio.
    # Ver a CORR-WTE-103: o titulo seguinte saia colado no paragrafo.
    a("")

    a("## Os que continuam `aberto`")
    a("")
    com_corpo = sum(1 for x in m["abertos"] if x["corpo"])
    # A concordancia quebra em 1, e o numero chegou a 1 em 2026-08-24. O
    # `740` abaixo ja tratava o caso; este nao tratava.
    #
    # E quebra de novo em 0, que chegou na quinta passagem: "Sao 0, e 0 deles
    # ja tem corpo Pascal escrito" seguido de uma tabela com cabecalho e
    # nenhuma linha. Tabela vazia num gerado nao se le como "nenhum" -- se le
    # como ferramenta quebrada, e manda alguem procurar o defeito que nao ha.
    n = len(m['abertos'])
    if n == 0:
        a("**Nenhum.** Todos os 96 fecharam veredito, e a seção fica no lugar")
        a("porque o número que importa é o zero: se um handler voltar a")
        a("`aberto` — spec nova, veredito revisto —, ele aparece aqui.")
        a("")
    else:
        a(f"{'É um só' if n == 1 else f'São {n}'}, e "
          + ("**ele já tem corpo Pascal escrito**."
             if n == 1 and com_corpo == 1 else
             "**ele não tem corpo Pascal**." if n == 1 else
             f"**{com_corpo} deles já têm corpo Pascal escrito**."))
        a("A coluna `corpo` diz se existe `src/impl/<unidade>.<handler>.inc`;")
        a("onde ela diz `sim`, o que segura o veredito não é código ausente, é")
        a("régua — a spec de cada um nomeia o que falta e quem é o dono.")
        a("")
        a("| Endereço | Handler | Grupo | Corpo |")
        a("|---|---|---|---|")
        for x in sorted(m["abertos"], key=lambda d: d["endereco"]):
            a(f"| `{x['endereco']}` | [{x['handler']}](spec/{x['handler']}.md) "
              f"| {x['grupo']} | {'sim' if x['corpo'] else '**não**'} |")
        a("")

    a("## Quem grava na imagem, e o gate de cada um")
    a("")
    a(f"São **{len(m['escritores'])}**, e o número não é o que as tasks")
    a("contavam. **Nove** é a conta de quem alguém *chamou* de gravação: seis na")
    a("WTE-TASK-27, uma na 28, uma na 29 e as três órfãs da 30. A leitura aqui é")
    a("da seção `## Bytes tocados` de cada spec, e a diferença aparece nos dois")
    a("sentidos — **entram** os sete de mover jogador e número de camisa (grupo")
    a("`edicao`, que gravam dentro da `0x00404820`), mais o `FormShow` e o")
    a("`boton_dialogo_weClick`, que gravam no arranque; **saem** o")
    a("`grabar_memoryClick` e o `grabar_camisetaClick`, que apesar do nome não")
    a("tocam a ROM — leem dela e emitem um arquivo.")
    a("")
    a("A tabela abaixo é guardada: handler que a spec diz que grava e não tem")
    a("linha aqui **aborta** o fechamento. Era justamente por não existir essa")
    a("conta que três gravações ficaram sem dono até a WTE-TASK-30.")
    a("")
    a("| Endereço | Handler | Grupo | Veredito | Gate |")
    a("|---|---|---|---|---|")
    for x in sorted(m["escritores"], key=lambda d: d["endereco"]):
        gates = GOLDEN_DE[x["handler"]]
        celula = ", ".join(f"[{g}](../tests/roteiros/{g}.txt)" for g in gates) \
            or "**nenhum**"
        a(f"| `{x['endereco']}` | [{x['handler']}](spec/{x['handler']}.md) "
          f"| {x['grupo']} | {x['veredito']} | {celula} |")
    a("")

    a("## A bateria golden desta corrida")
    a("")
    disco = m["roteiros"]
    com_par = sum(1 for d in disco.values() if d["par"])
    sem_par = sorted(n for n, d in disco.items() if not d["par"])
    # A conta e de DUAS listas, e confundi-las faz este paragrafo mentir. O que
    # esta em disco cresce quando uma fase POSTERIOR escreve roteiro -- a fase 6
    # acrescentou o de edicao multipla e o de gravacao dupla --, e esta secao
    # descreve a corrida DESTA fase, que aconteceu antes deles existirem.
    aqui = sorted(m["por_roteiro"])
    noutra = [n for n, d in disco.items() if d["par"] and n not in m["por_roteiro"]]
    a(f"São {len(disco)} roteiros em disco, {com_par} com par do lado port, e")
    a(f"**{len(aqui)} deles rodaram nesta bateria**. Cada um desses rodou")
    a("**duas vezes**: `controle` (oráculo contra oráculo, que prova que o par")
    a("roteiro+imagem é determinístico) e `golden` (oráculo contra o app")
    a("Lazarus). **O controle vem antes do teste** — sem ele, verde e vermelho")
    a("não significam nada.")
    a("")
    if noutra:
        a("Com par e fora desta bateria: "
          + ", ".join(f"`{n}`" for n in sorted(noutra)) + ". "
          + ("Ele é" if len(noutra) == 1 else "Eles são")
          + " da [WTE-TASK-34](../../docs/tasks/concluidos/34-bateria-golden-completa.md),")
        a("que roda a bateria completa (operação × ROM) e registra em")
        a("[`golden.tsv`](golden.tsv). O guarda de cobertura aceita as **duas**")
        a("listas: o que ele exige é que roteiro com par tenha rodado nos dois")
        a("modos e esteja escrito em lugar versionado, não que esteja escrito")
        a("*aqui* — senão o registro da fase 4 cresceria toda vez que uma fase")
        a("posterior escrevesse um roteiro, e a data desta corrida passaria a")
        a("mentir.")
        a("")
    if sem_par:
        a("Fora da bateria por não ter lado port: "
          + ", ".join(f"`{n}`" for n in sem_par)
          + ". Roteiro sem par julga o oráculo contra ele mesmo e mais nada; o")
        a("gerador **aborta** se um roteiro **com** par ficar sem as duas")
        a("corridas registradas.")
        a("")
    com_artefato = sorted(n for n, d in disco.items() if d["artefato"])
    a(f"**{len(com_artefato)} deles comparam um artefato além das imagens.** Nem")
    a("toda gravação é na ROM: o `grabar_memoryClick` emite um `.mcr` e o")
    a("`grabar_camisetaClick` um `.bin` de uniforme, e nos dois a imagem sai")
    a("intacta dos dois lados. Comparar só as imagens aprovaria um port que não")
    a("fizesse absolutamente nada, e é para isso que o `golden_check.sh` tem")
    a("`--artefato`. São eles: " + ", ".join(f"`{n}`" for n in com_artefato) + ".")
    a("")
    a("| Roteiro | Controle | Golden | s | Tentativas |")
    a("|---|---|---|---:|---|")
    seg: dict[str, int] = {}
    tent: dict[str, int] = {}
    for linha in m["bateria"]:
        seg[linha["roteiro"]] = seg.get(linha["roteiro"], 0) + int(linha["segundos"])
        tent[linha["roteiro"]] = max(tent.get(linha["roteiro"], 1),
                                     int(linha["tentativas"]))
    for nome in sorted(m["por_roteiro"]):
        d = m["por_roteiro"][nome]
        n = tent[nome]
        a(f"| [{nome}](../tests/roteiros/{nome}.txt) | {d.get('controle','—')} "
          f"| {d.get('golden','—')} | {seg[nome]} "
          f"| {'1' if n == 1 else f'**{n}**'} |")
    a("")
    verdes = sum(1 for l in m["bateria"] if l["veredito"] == "PASSOU")
    repetidos = sorted(n for n, x in tent.items() if x > 1)
    a(f"**{verdes} de {len(m['bateria'])} corridas verdes**, "
      f"{sum(seg.values())} segundos de relógio no total.")
    a("")
    if repetidos:
        a("**E a coluna de tentativas não é enfeite.** "
          + ", ".join(f"`{n}`" for n in repetidos)
          + " precisou de mais de uma corrida; a causa de cada")
        a("caso está no Log da task que rodou a bateria. Gate que precisa de")
        a("repetição para ficar verde deixa de separar *\"o port diverge\"* de")
        a("*\"a corrida não estava pronta\"*, e essa é a classe de problema que a")
        a("[CORR-WTE-080](../../docs/tasks/concluidos/CORR-WTE-080.md) nomeou — a causa não")
        a("precisa ser a mesma para o custo ser.")
        a("")
    a("**As duas ROMs, e por que a conta é de uma só.** O critério da task diz")
    a("\"nas duas ROMs\". Com a europeia o `wte.exe` morre ao trocar de time —")
    a("49.749 violações de acesso contra 0 — e a gravação nunca acontece, então")
    a("o oráculo não existe daquele lado. Está medido e registrado em")
    a("[`gravacao-controle.md`](gravacao-controle.md); a bateria roda sobre a")
    a("japonesa, e a cobertura da europeia é da")
    a("[WTE-TASK-34](../../docs/tasks/concluidos/34-bateria-golden-completa.md).")
    a("")

    a("## Força da evidência")
    a("")
    a(f"Cada uma das {por_extenso(len(S.SECOES))} seções obrigatórias de cada spec")
    a("carrega a sua linha `**Evidência:**`, e é essa a população contada:")
    a("evidência escrita em `## Notas`, `## Justificativa` ou `## Como o veredito")
    a("fechou` fica de fora, e são")
    a(f"{m['evidencias_fora']} linhas. A distribuição das")
    a(f"{sum(m['evidencias'].values())} cobradas:")
    a("")
    a("| Evidência | Linhas |")
    a("|---|---:|")
    for nome in S.EVIDENCIAS:
        a(f"| `{nome}` | {m['evidencias'][nome]} |")
    a("")
    if m["fracas"]:
        a("**Specs cuja evidência inteira é fraca:**")
        a("")
        for x in m["fracas"]:
            a(f"- `{x['handler']}` ({x['veredito']})")
    else:
        a("**Nenhuma spec se apoia só em `observação de tela` ou `não medido`.**")
        a("Era a pergunta 3 da task — *\"quantas são hipóteses vestidas de")
        a("spec?\"* — e a resposta é zero. O `spec_index.py` já recusava essa")
        a("combinação para o veredito `implementado`; medido agora sobre os")
        a("cinco vereditos, ela não aparece em nenhum.")
    a("")
    a(f"Os {len(m['pontos_fracos'])} pontos soltos de evidência fraca, um a um —")
    a("são seções isoladas dentro de specs cujo resto está medido:")
    a("")
    a("| Handler | Seção | Evidência | Decisão |")
    a("|---|---|---|---|")
    for x in m["pontos_fracos"]:
        a(f"| [{x['handler']}](spec/{x['handler']}.md) | {x['secao']} "
          f"| `{x['evidencia']}` "
          f"| {DECISAO_FRACA[(x['handler'], x['secao'])]} |")
    a("")
    a("**Nenhum dos três pede disassembly antes da Fase 6**, e a tabela acima")
    a("diz por quê, um a um. O gerador **aborta** se aparecer ponto fraco sem")
    a("decisão escrita — ou decisão sobrando, que é o sintoma de um ponto que")
    a("foi medido e a tabela não acompanhou.")
    a("")

    a("## `nao portado`, e a justificativa de cada um")
    a("")
    if m["nao_portados"]:
        quantos = len(m["nao_portados"])
        a(f"{'É um só' if quantos == 1 else f'São {quantos}'}. O `spec_index.py` "
          "**recusa** o veredito")
        a("sem uma seção `## Justificativa` não vazia, então a existência dela é")
        a("mecânica; o que a task pede a mais é que a razão seja de escopo, e")
        a("não de dificuldade.")
        a("")
        for chave in m["nao_portados"]:
            a(f"- [`{chave}`](spec/{chave}.md)")
    else:
        a("Nenhum.")
    a("")

    a("## Os cinco `trivial` reconferidos")
    a("")
    a("`trivial` é o veredito mais fácil de dar por preguiça, e o único cuja")
    a("consequência — *\"não toca a imagem\"* — o golden não verifica sozinho:")
    a("um handler que não deveria gravar e não grava passa igual a um que não")
    a("foi exercitado. Por isso o critério da fase manda reamostrar cinco.")
    a("")
    a("**A escolha é declarada, e não sorteada.** Cinco espaçados uniformemente")
    a("pela lista ordenada por endereço dão a propriedade que o sorteio existe")
    a("para dar — ninguém escolhe quais depois de ver o resultado — e são")
    a("reproduzíveis, que é o que o `--check` exige. A amostra sai proporcional")
    a("à população, e isso importa: 14 dos 19 `trivial` são `FormCreate` da")
    a("forma \"cor\".")
    a("")
    a("| Handler | Endereço | Bytes | Confirmado | O que o corpo faz |")
    a("|---|---|---:|---|---|")
    for x in m["amostra"]:
        a(f"| [{x['handler']}](spec/{x['handler']}.md) | `{x['endereco']}` "
          f"| {x['bytes']} | {x['confirmado']} | {x['o_que_o_corpo_faz']} |")
    a("")
    if m["nao_confirmados"]:
        a("**Nem todos confirmaram:** "
          + ", ".join(f"`{h}`" for h in m["nao_confirmados"]))
    else:
        a("**Os cinco confirmaram.** Nenhum toca a imagem, e nos três")
        a("`FormCreate` o valor de cor que o original passa a")
        a("`TControl::SetColor` é o mesmo que o `.inc` do port escreve.")
    a("")
    a("Registro em [`fase-4-trivial.tsv`](fase-4-trivial.tsv); a amostra é")
    a("recalculada a cada corrida, e o gerador **aborta** se ela se deslocar sem")
    a("o registro acompanhar — handler que entra ou sai de `trivial` muda quais")
    a("são os cinco, e reconferência velha não vale para handler novo.")
    a("")

    a("## Varredura por decompilado colado")
    a("")
    a(f"{m['varridos']} arquivos varridos — as specs, os `.inc` de corpo escrito")
    a("à mão e as unidades de `src/`.")
    a("")
    if m["suspeitos"]:
        a("| Arquivo | Marca | Trecho |")
        a("|---|---|---|")
        for x in m["suspeitos"]:
            a(f"| `{x['arquivo']}` | {x['marca']} | `{x['trecho']}` |")
    else:
        a("**Nada.** É a §2 do plano sustentada por medida em vez de honra.")
    a("")

    return "\n".join(linhas) + "\n"


# ------------------------------------------- a guarda do numero de gravacoes --
#
# **A conta subiu duas vezes e o texto ficou para tras nas duas.** Seis virou
# nove na WTE-TASK-30 e nove virou dezessete na WTE-TASK-31; a
# CORR-WTE-085 achou o `seis` ainda vivo no preambulo da Fase 5 do plano e na
# copia dele no `progresso.md`, a dezesseis linhas de uma linha que ja dizia
# dezessete. Nenhum gate pegava: o `--check` daqui so compara o `fase-4.md`
# com o disco, e o perimetro do `check_fase1.py` varre outros quatro numeros.
#
# O alvo e a FORMA POR EXTENSO (`seis gravacoes`, `nove gravacoes`), nao o
# digito: `6` e `9` soltos dariam falso positivo em qualquer pagina. E o numero
# corrente nao e constante escrita aqui -- sai de `len(m['escritores'])`, a
# mesma medida que imprime o `São **17**` do `fase-4.md`.
#
# O perimetro e importado do `check_fase1.py`, nao copiado: ele ja sabe deixar
# de fora a narracao (`correcoes-progresso.md`), as `CORR-WTE-*.md`, as tasks
# `NN-*.md` concluidas e tudo o que vem depois do `## Log de Execução`. Duas
# copias de perimetro divergiriam, que e o que o `wte/tools/README.md` manda
# evitar.
FORMAS_APOSENTADAS = (r"\bseis\s+gravaç", r"\bnove\s+gravaç")

# A linha que escreve `velho -> corrente` esta ensinando, nao mentindo. Como o
# total corrente aparece por extenso e em digito, os dois valem como perdao.
def _diz_o_corrente(linha: str, corrente: int) -> bool:
    return "dezessete" in linha.lower() or re.search(rf"\b{corrente}\b", linha)


def confere_forma_aposentada(corrente: int) -> list[str]:
    """Os sitios vivos que ainda escrevem a conta velha por extenso."""
    achados: list[str] = []
    for caminho in F1._markdowns():
        if not F1._no_perimetro(caminho):
            continue
        for i, linha in F1._linhas_vivas(caminho):
            if any(re.search(f, linha, re.I) for f in FORMAS_APOSENTADAS) \
                    and not _diz_o_corrente(linha, corrente):
                rel = caminho.relative_to(ROOT).as_posix()
                achados.append(f"{rel}:{i}: {linha.strip()}")
    return achados


# ------------------------------------------------------------------- driver ---
def generate() -> dict[str, str]:
    m = medir()
    residuo = confere_forma_aposentada(len(m["escritores"]))
    if residuo:
        raise Fase4Error(
            "a conta de gravacoes corrente e "
            f"{len(m['escritores'])}, e estes sitios vivos ainda escrevem a "
            "velha por extenso:\n  " + "\n  ".join(residuo))
    return {str(OUT): gera_md(m)}


def do_check(files: dict[str, str]) -> int:
    rc = 0
    for caminho, conteudo in files.items():
        p = Path(caminho)
        if not p.exists():
            print(f"ERRO: {p.relative_to(ROOT)} nao existe -- rode "
                  f"`python3 {GENERATOR}`", file=sys.stderr)
            rc = 2
            continue
        if p.read_text(encoding="utf-8") != conteudo:
            print(f"ERRO: {p.relative_to(ROOT)} diverge do medido hoje -- rode "
                  f"`python3 {GENERATOR}`", file=sys.stderr)
            rc = 2
    if rc == 0:
        print(f"check_fase4: {OUT.relative_to(ROOT)}: ok")
    return rc


def do_write(files: dict[str, str]) -> int:
    for caminho, conteudo in files.items():
        p = Path(caminho)
        p.write_text(conteudo, encoding="utf-8")
        print(f"  {p.name}: {len(conteudo.splitlines())} linhas, "
              f"{len(conteudo.encode('utf-8'))} bytes")
    return 0


def main(argv: list[str]) -> int:
    try:
        files = generate()
    except (Fase4Error, S.SpecError) as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        return 2
    if "--check" in argv:
        return do_check(files)
    return do_write(files)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
