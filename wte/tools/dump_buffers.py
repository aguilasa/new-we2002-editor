#!/usr/bin/env python3
"""Inventario dos campos de tamanho fixo, e as duas fontes conciliadas.

Gera `wte/re/buffers.md` e `wte/re/buffers.tsv` -- produto da
[WTE-TASK-36](../../docs/tasks/36-buffers-e-truncamento.md).

    python3 wte/tools/dump_buffers.py           # regera as duas saidas
    python3 wte/tools/dump_buffers.py --check   # o que `make -C wte check` roda

## A pergunta que este script existe para responder

O enunciado da task manda conciliar DUAS fontes que precisam concordar:

1. **a camada de dados** -- todo `array[0..N-1] of AnsiChar`, com o `N`;
2. **as specs de edicao** -- todo campo com `MaxLength` no DFM ou validacao no
   handler.

E diz o que fazer com a diferenca: *"campo com `MaxLength` 20 gravando em array
de 16 e bug esperando a entrada certa"*. Entao o script nao descreve os dois
lados -- ele **compara** e aborta quando um cabe no outro pelo avesso.

## A terceira fonte, que o enunciado nao previa

`MaxLength` nao esta so no DFM. Dos cinco campos de texto que gravam, **dois
recebem o limite em tempo de execucao**: `edit_nombre1` e `edit_nombre2` sao
carregados por `lista_equiposChange`, que le a largura do registro de uma
tabela por time (`TEAM_NAME_KANJI_LEN` e `TEAM_NAME_LEN_3`) e poe
`largura - 1`. Ou seja: o limite deles **muda com o time selecionado**, de 5 a
19 caracteres.

Um inventario que olhasse so o DFM veria quatro `MaxLength` e concluiria que os
campos de nome de time nao tem limite -- que e o contrario da verdade. Por isso
a coluna `origem` diz de onde cada numero vem, e o `--check` conferiria os dois
tipos com a mesma regra.

## O que NAO entra

Vetor que nao e campo de texto editavel: `link` (46 bytes de indice),
`raw_formation` (30 bytes de posicao), `quadro` do `.mcr`. Eles tem tamanho
fixo e nao tem borda de digitacao -- a pergunta da task e sobre o que o
**usuario digita** e o que chega ao disco. Vetor de dado binario entra no
inventario com `editavel = nao`, para a conta fechar, e fica fora dos testes de
borda.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WTE = ROOT / "wte"
SRC = WTE / "src"
FORMS = WTE / "forms"
OUT_MD = WTE / "re" / "buffers.md"
OUT_TSV = WTE / "re" / "buffers.tsv"

GERADOR = "wte/tools/dump_buffers.py"


class BufferError(Exception):
    pass


# Os campos de texto que o usuario edita e que chegam ao disco. Cada um diz o
# controle, o vetor de destino, e de onde sai o limite.
#
# A lista e escrita a mao de proposito, e a razao e a mesma do
# `check_glifos_disabled.py`: varrer o codigo atras de "coisas que parecem
# campo" acharia os vetores binarios junto, e a conferencia perderia o sentido.
# Cada linha carrega o predicado que o script confere -- o vetor tem de existir
# com aquele tamanho, e o limite tem de sair de onde a linha diz.
CAMPOS = [
    {
        "controle": "edit_nombre1",
        "formulario": "MainForm",
        "vetor": ("we2002_team.pas", "kanji_name"),
        "origem": "runtime",
        "limite": "TEAM_NAME_KANJI_LEN[time] - 1",
        "faixa": (5, 19),
        "modo": "dois bytes",
        "filtro": "[A-Za-z0-9 .]",
    },
    {
        "controle": "edit_nombre2",
        "formulario": "MainForm",
        "vetor": ("we2002_team.pas", "names"),
        "origem": "runtime",
        "limite": "TEAM_NAME_LEN_3[time] - 1",
        "faixa": (5, 19),
        "modo": "um byte",
        "filtro": "[A-Za-z0-9 .]",
    },
    {
        "controle": "edit_nombre3",
        "formulario": "MainForm",
        "vetor": ("we2002_team.pas", "abbreviations"),
        "origem": "dfm",
        "limite": "3",
        "faixa": (3, 3),
        "modo": "um byte",
        "filtro": "[A-Za-z0-9]",
    },
    {
        "controle": "casilla_nombre",
        "formulario": "jugador",
        "vetor": ("we2002_player.pas", "name"),
        "origem": "dfm",
        "limite": "10",
        "faixa": (10, 10),
        "modo": "um byte",
        "filtro": "[A-Za-z0-9 .]",
    },
]

# Campos NUMERICOS, e eles quebram o modelo dos de texto.
#
# O destino nao e um vetor com capacidade -- e uma FAIXA, e quem a guarda nao e
# o `MaxLength`, e a validacao do handler de gravacao. Os dois casos aqui sao
# desproporcionais de proposito, e e o que este inventario existe para mostrar:
#
#   casilla_precio   MaxLength 3  -> aceita ate "999", faixa valida 1..250
#   casilla_dorsal   MaxLength 10 -> aceita ate "9999999999", faixa valida 1..99
#
# O `casilla_dorsal` e o extremo: dez digitos para um numero que nao passa de
# 99. Se a validacao do handler sumisse, `MaxLength` nao seguraria nada -- e a
# conferencia abaixo e exatamente essa, o predicado tem de existir no `.inc`.
NUMERICOS = [
    {
        "controle": "casilla_precio",
        "formulario": "jugador",
        "handler": "ep2002_jugador.BitBtn3Click.inc",
        "predicado": "(creditos < 1) or (creditos > 250)",
        "faixa": "1..250",
        "maxlength": 3,
        "filtro": "[0-9]",
        "destino": "o byte de credito de `OFS_COST_*`",
    },
    {
        "controle": "casilla_dorsal",
        "formulario": "jugador",
        "handler": "ep2002_jugador.BitBtn3Click.inc",
        "predicado": "(numero < 1) or (numero > 99)",
        "faixa": "1..99 (1..32 fora de Master League)",
        "maxlength": 10,
        "filtro": "[0-9]",
        "destino": "o campo de numero de camisa (`SquadNumbers`)",
    },
]

# Vetor de tamanho fixo que NAO e campo de digitacao. Entra para a conta
# fechar; fica fora dos testes de borda.
NAO_EDITAVEIS = [
    ("we2002_team.pas", "raw_formation", "30 bytes de posicao de jogador"),
    ("we2002_team.pas", "raw_kanji_name", "o slot cru, antes do decodificador"),
    ("we2002_team.pas", "mixed_case_name", "nome em caixa mista, so leitura"),
    ("we2002_team.pas", "link", "46 indices de jogador"),
    ("we2002_player.pas", "url", "sidecar do SoFIFA, nao vai para a imagem"),
]

DECL = re.compile(
    r"^\s*(\w+)\s*:\s*array\[0\s*\.\.\s*(\d+)\]\s*of\s+"
    r"(?:array\[0\s*\.\.\s*(\d+)\]\s*of\s+)?(AnsiChar|Char|Byte)\s*;", re.M)


def vetores() -> dict[tuple[str, str], dict]:
    """Todo `array[0..N] of AnsiChar/Byte` declarado na camada de dados."""
    achados: dict[tuple[str, str], dict] = {}
    for arq in sorted(SRC.glob("we2002_*.pas")):
        texto = arq.read_text(encoding="utf-8")
        for m in DECL.finditer(texto):
            nome, n1, n2, tipo = m.group(1), int(m.group(2)), m.group(3), m.group(4)
            # `array[0..5] of array[0..19]` -- o interno e a capacidade do campo
            capacidade = (int(n2) + 1) if n2 else (n1 + 1)
            quantos = (n1 + 1) if n2 else 1
            achados[(arq.name, nome)] = {
                "arquivo": arq.name, "nome": nome, "capacidade": capacidade,
                "quantos": quantos, "tipo": tipo,
            }
    return achados


def tabela_limites(nome: str) -> list[int]:
    """Os valores de `TEAM_NAME_KANJI_LEN` / `TEAM_NAME_LEN_3`."""
    texto = (SRC / "we2002_tables.pas").read_text(encoding="utf-8")
    m = re.search(rf"{nome}: array\[0\.\.(\d+)\] of ShortInt = \((.*?)\);",
                  texto, re.S)
    if not m:
        raise BufferError(f"{nome} nao achada em we2002_tables.pas")
    valores = [int(v) for v in re.findall(r"-?\d+", m.group(2))]
    esperado = int(m.group(1)) + 1
    if len(valores) != esperado:
        raise BufferError(
            f"{nome}: {len(valores)} valores para array[0..{esperado - 1}]")
    return valores


def maxlength_dos_forms() -> dict[str, int]:
    """Os `MaxLength` estaticos, por nome de objeto, dos `.lfm` gerados."""
    achados: dict[str, int] = {}
    for arq in sorted(FORMS.glob("*.lfm")):
        objeto = None
        for linha in arq.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"\s*object (\w+):", linha)
            if m:
                objeto = m.group(1)
            m = re.match(r"\s*MaxLength = (\d+)", linha)
            if m and objeto:
                achados[objeto] = int(m.group(1))
    return achados


def mede() -> dict:
    vet = vetores()
    est = maxlength_dos_forms()
    kanji = tabela_limites("TEAM_NAME_KANJI_LEN")
    len3 = tabela_limites("TEAM_NAME_LEN_3")

    problemas: list[str] = []
    linhas = []

    for c in CAMPOS:
        chave = c["vetor"]
        if chave not in vet:
            problemas.append(
                f"{c['controle']}: o vetor {chave[1]} nao existe em {chave[0]}")
            continue
        cap = vet[chave]["capacidade"]

        if c["origem"] == "dfm":
            if c["controle"] not in est:
                problemas.append(
                    f"{c['controle']}: a linha diz que o MaxLength vem do DFM, "
                    f"e nenhum .lfm o declara. Ou o gerador o perdeu, ou a "
                    f"origem desta linha esta errada.")
                continue
            lim_min = lim_max = est[c["controle"]]
            if str(lim_max) != c["limite"]:
                problemas.append(
                    f"{c['controle']}: o .lfm diz MaxLength = {lim_max} e a "
                    f"linha diz {c['limite']}")
        else:
            tab = kanji if "KANJI" in c["limite"] else len3
            lim_min, lim_max = min(tab) - 1, max(tab) - 1
            # Limite de runtime e `MaxLength` estatico brigam: o `.lfm` venceria
            # ate a primeira troca de time, e depois nao -- o campo passaria a
            # aceitar tamanhos diferentes conforme a ordem dos cliques, que e a
            # pior forma de um limite errar. O DFM do original NAO declara
            # `MaxLength` nestes dois, e o `.lfm` gerado tem de continuar assim.
            if c["controle"] in est:
                problemas.append(
                    f"{c['controle']}: o limite vem de `{c['limite']}` em tempo "
                    f"de execucao, e o .lfm declara MaxLength = "
                    f"{est[c['controle']]}. Os dois brigam -- o estatico vale "
                    f"ate a primeira troca de time e depois nao. O DFM do "
                    f"original nao declara MaxLength aqui.")

        # A conferencia que o enunciado pede, e a que aborta.
        #
        # No modo de dois bytes cada caractere ocupa DOIS bytes no disco, e a
        # capacidade do vetor e em caracteres decodificados -- por isso a
        # comparacao e contra `capacidade - 1` nos dois modos: o `- 1` e o
        # terminador que o `Cadeia()` espera.
        cabe = lim_max <= cap - 1
        if not cabe:
            problemas.append(
                f"{c['controle']}: MaxLength maximo {lim_max} contra vetor "
                f"{chave[1]} de {cap} bytes ({cap - 1} uteis mais terminador). "
                f"E o caso que o enunciado da WTE-TASK-36 nomeia: campo "
                f"gravando em array menor e bug esperando a entrada certa.")

        linhas.append({
            "controle": c["controle"], "formulario": c["formulario"],
            "vetor": f"{chave[1]}", "arquivo": chave[0],
            "capacidade": cap, "origem": c["origem"], "limite": c["limite"],
            "lim_min": lim_min, "lim_max": lim_max,
            "modo": c["modo"], "filtro": c["filtro"], "cabe": cabe,
        })

    # Os numericos: quem guarda a faixa e a validacao do handler, nao o
    # `MaxLength`. Entao o predicado dela TEM de existir -- se sumir, o campo
    # fica com dez digitos livres para um numero que nao passa de 99.
    numericos = []
    for n in NUMERICOS:
        alvo = SRC / "impl" / n["handler"]
        if not alvo.exists():
            problemas.append(f"{n['controle']}: falta {n['handler']}")
            continue
        corpo = alvo.read_text(encoding="utf-8")
        if n["predicado"] not in corpo:
            problemas.append(
                f"{n['controle']}: a validacao de faixa ({n['faixa']}) sumiu de "
                f"{n['handler']}. O `MaxLength = {n['maxlength']}` NAO guarda "
                f"essa faixa -- ele deixa passar "
                f"{'9' * n['maxlength']}. Sem a validacao o campo fica aberto.")
        if est.get(n["controle"]) != n["maxlength"]:
            problemas.append(
                f"{n['controle']}: o .lfm diz MaxLength = "
                f"{est.get(n['controle'])} e a linha diz {n['maxlength']}")
        numericos.append(dict(n))

    # `MaxLength` no .lfm que nenhuma linha reivindica: campo novo sem entrada.
    reivindicados = ({c["controle"] for c in CAMPOS}
                     | {n["controle"] for n in NUMERICOS})
    orfaos = sorted(set(est) - reivindicados)
    if orfaos:
        problemas.append(
            "MaxLength declarado no .lfm e sem linha em CAMPOS: "
            + ", ".join(orfaos)
            + ". Campo sem entrada no inventario e o quinto criterio da task.")

    if problemas:
        raise BufferError("; ".join(problemas))

    return {
        "linhas": linhas, "vetores": vet, "kanji": kanji, "len3": len3,
        "nao_editaveis": NAO_EDITAVEIS, "estaticos": est,
        "numericos": numericos,
    }


def tsv(m: dict) -> str:
    cab = ("controle\tformulario\tvetor\tcapacidade\torigem\tlimite_min\t"
           "limite_max\tmodo\tfiltro\n")
    corpo = "".join(
        f"{l['controle']}\t{l['formulario']}\t{l['vetor']}\t{l['capacidade']}\t"
        f"{l['origem']}\t{l['lim_min']}\t{l['lim_max']}\t{l['modo']}\t"
        f"{l['filtro']}\n"
        for l in m["linhas"])
    return cab + corpo


def md(m: dict) -> str:
    L: list[str] = []
    a = L.append
    a("# `re/buffers.md` — campos de tamanho fixo, e o que acontece na borda")
    a("")
    a("**GERADO — não editar à mão.** A correção entra no gerador:")
    a("")
    a("```sh")
    a(f"python3 {GERADOR}")
    a(f"python3 {GERADOR} --check   # o que `make -C wte check` roda")
    a("```")
    a("")
    a("Produto da [WTE-TASK-36](../../docs/tasks/36-buffers-e-truncamento.md).")
    a("**Todo número daqui saiu do script.**")
    a("")
    a("## As duas fontes, conciliadas")
    a("")
    a("O enunciado manda conciliar a **camada de dados** (todo")
    a("`array[0..N-1] of AnsiChar`) com as **specs de edição** (todo campo com")
    a("`MaxLength`), e diz o que fazer com a diferença: *campo com `MaxLength`")
    a("20 gravando em array de 16 é bug esperando a entrada certa*. O gerador")
    a("**aborta** nesse caso — não relata, aborta.")
    a("")
    a(f"São **{len(m['linhas'])} campos de digitação**, e nos "
      f"{len(m['linhas'])} o limite cabe no vetor.")
    a("")
    a("| Controle | Formulário | Vetor | Capacidade | Limite | Origem | Modo |")
    a("|---|---|---|---:|---|---|---|")
    for l in m["linhas"]:
        lim = (f"{l['lim_min']}..{l['lim_max']}"
               if l["lim_min"] != l["lim_max"] else str(l["lim_max"]))
        a(f"| `{l['controle']}` | {l['formulario']} | `{l['vetor']}` "
          f"| {l['capacidade']} B | {lim} | {l['origem']} | {l['modo']} |")
    a("")

    a("## A terceira fonte, que o enunciado não previa")
    a("")
    a("`MaxLength` não está só no DFM. Dos quatro campos, **dois recebem o")
    a("limite em tempo de execução**: `edit_nombre1` e `edit_nombre2` são")
    a("carregados por `lista_equiposChange`, que lê a largura do registro de")
    a("uma tabela por time e põe `largura - 1`. O limite deles **muda com o")
    a("time selecionado**.")
    a("")
    k, l3 = m["kanji"], m["len3"]
    a(f"| Tabela | Times | Mínimo | Máximo | `MaxLength` resultante |")
    a(f"|---|---:|---:|---:|---|")
    a(f"| `TEAM_NAME_KANJI_LEN` | {len(k)} | {min(k)} | {max(k)} "
      f"| {min(k) - 1}..{max(k) - 1} |")
    a(f"| `TEAM_NAME_LEN_3` | {len(l3)} | {min(l3)} | {max(l3)} "
      f"| {min(l3) - 1}..{max(l3) - 1} |")
    a("")
    a("Um inventário que olhasse só o DFM veria os `MaxLength` estáticos e")
    a("concluiria que os campos de nome de time **não têm limite** — que é o")
    a("contrário da verdade. É por isso que a coluna `origem` existe.")
    a("")

    a("## Os campos numéricos, e por que `MaxLength` não guarda nada neles")
    a("")
    a("O destino deles não é vetor com capacidade — é uma **faixa**, e quem a")
    a("guarda é a validação do handler de gravação. Os dois são")
    a("desproporcionais, e é o que o inventário existe para mostrar:")
    a("")
    a("| Controle | `MaxLength` | Aceita digitar até | Faixa válida | Destino |")
    a("|---|---:|---|---|---|")
    for n in m["numericos"]:
        a(f"| `{n['controle']}` | {n['maxlength']} | "
          f"`{'9' * n['maxlength']}` | {n['faixa']} | {n['destino']} |")
    a("")
    a("O `casilla_dorsal` é o extremo: **dez dígitos** para um número que não")
    a("passa de 99. Se a validação do handler sumisse, o `MaxLength` não")
    a("seguraria coisa nenhuma — e é exatamente esse o predicado que o gerador")
    a("confere no `.inc`, um por campo. Ele **aborta** se a faixa sair do")
    a("handler, porque aí o campo fica aberto e nada na tela diz isso.")
    a("")
    a("**A borda dos dez dígitos é benigna, e a razão é do Pascal:**")
    a("`StrToIntDef` devolve o padrão `0` quando a cadeia não cabe num")
    a("`Integer`, e `0` reprova na faixa `1..99` como qualquer outro valor")
    a("inválido. Não há estouro silencioso — há recusa, que é o que o original")
    a("também faz.")
    a("")
    a("## Os vetores que não são campo de digitação")
    a("")
    a("Entram no inventário para a conta fechar, e ficam fora dos testes de")
    a("borda: têm tamanho fixo, mas ninguém digita neles.")
    a("")
    a("| Vetor | Arquivo | O que é |")
    a("|---|---|---|")
    for arq, nome, oque in m["nao_editaveis"]:
        cap = m["vetores"].get((arq, nome), {}).get("capacidade", "?")
        a(f"| `{nome}` ({cap} B) | `{arq}` | {oque} |")
    a("")
    a(f"A camada de dados declara **{len(m['vetores'])}** vetores de tamanho")
    a("fixo ao todo; os demais são tabelas constantes e buffers locais.")
    a("")
    return "\n".join(L) + "\n"


def main(argv: list[str]) -> int:
    checando = "--check" in argv
    try:
        m = mede()
        texto_md, texto_tsv = md(m), tsv(m)
    except BufferError as e:
        print(f"dump_buffers: {e}", file=sys.stderr)
        return 2
    for alvo, texto in ((OUT_MD, texto_md), (OUT_TSV, texto_tsv)):
        rel = alvo.relative_to(ROOT)
        if checando:
            if not alvo.exists() or alvo.read_text(encoding="utf-8") != texto:
                print(f"dump_buffers: {rel}: DIVERGE do gerador", file=sys.stderr)
                return 2
            print(f"dump_buffers: {rel}: ok")
        else:
            alvo.write_text(texto, encoding="utf-8")
            print(f"dump_buffers: {rel}: {len(texto)} B")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
