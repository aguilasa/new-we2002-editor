#!/usr/bin/env python3
"""Fechamento da fase 2: a casca esta fiel, e quanto dela e gerado.

Gera `wte/re/fase-2.md` -- o produto da WTE-TASK-14. Como o `check_fase1.py`,
ele nao remede o binario: mede a **coerencia entre os produtos** que as
WTE-TASK-10 a 13 deixaram versionados, e mede a fracao de codigo gerado, que e
o numero com que a §4.4 do plano se compromete.

## O que ele confere, e o que deliberadamente NAO confere

| Confere | Como |
|---|---|
| os 96 stubs, na unidade certa | cruza `published_methods.tsv` com os `REStub()` dos `.pas` gerados |
| os 18 formularios | os `.lfm` de `wte/forms/` contra os `.dfm` de `wte/re/dfm/` |
| os 18 vereditos visuais | a tabela de veredito do `re/visual.md` (WTE-TASK-12) |
| a fracao gerada | contagem de linha por arquivo, separando gerado de escrito a mao |

**Nao** confere se algum arquivo gerado foi editado a mao: quem faz isso e o
`dfm2lfm.py --check`, que roda na mesma bateria. Duplicar aqui criaria uma
segunda copia da medida -- a duplicacao sem guarda que o `README.md` deste
diretorio manda evitar.

## Por que a contagem do `.lfm` sai em duas colunas

118 blobs viraram hex inline nos 18 `.lfm` (decisao de 2026-08-06). Contados
junto, eles afogam tudo: a fracao "gerada" fica em 99% por causa de bitmap, e o
numero deixa de dizer o que a §4.4 quer saber. Entao o hex e contado a parte, e
a fracao que vale e a **sem** ele.

Uso:

    python3 wte/tools/check_fase2.py            # regenera
    python3 wte/tools/check_fase2.py --check    # confere contra o commitado
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "wte" / "src"
FORMS = ROOT / "wte" / "forms"
DFM = ROOT / "wte" / "re" / "dfm"
PUB = ROOT / "wte" / "re" / "published_methods.tsv"
VISUAL = ROOT / "wte" / "re" / "visual.md"
EVENTOS = ROOT / "wte" / "re" / "eventos.md"
LPR = ROOT / "wte" / "wte.lpr"
OUT = ROOT / "wte" / "re"

GENERATOR = "wte/tools/check_fase2.py"
MD_NAME = "fase-2.md"

# Marca que o dfm2lfm.py escreve no cabecalho de cada unidade que ele emite.
# E o que separa gerado de escrito a mao sem depender de lista fixa: unidade
# nova entra na conta sozinha, do lado certo.
MARCA_GERADO = "NAO EDITAR A MAO"


class CheckError(Exception):
    pass


# ------------------------------------------------------------------ leitura --

def ler_tsv() -> list[dict[str, str]]:
    if not PUB.exists():
        raise CheckError(f"{PUB} nao existe -- WTE-TASK-04 nao rodou")
    linhas = PUB.read_text(encoding="utf-8").splitlines()
    cab = linhas[0].split("\t")
    fora = [dict(zip(cab, l.split("\t"))) for l in linhas[1:] if l.strip()]
    if not fora:
        raise CheckError(f"{PUB} sem handler nenhum")
    return fora


def linhas_de(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def lfm_particionado(path: Path) -> tuple[int, int]:
    """(linhas de estrutura, linhas de hex de blob) de um `.lfm`.

    O hex mora entre `Data = {` e a linha que fecha com `}`. Nao classificar
    por "linha que so tem hexadecimal": `Left = 232` nao casa, mas uma linha de
    continuacao de string curta pode casar, e o erro seria silencioso. Uma
    variavel de estado custa menos que uma heuristica.
    """
    estrutura = hexa = 0
    dentro = False
    for linha in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if dentro:
            hexa += 1
            if linha.rstrip().endswith("}"):
                dentro = False
            continue
        estrutura += 1
        if re.search(r"\bData = \{\s*$", linha):
            dentro = True
    return estrutura, hexa


# ---------------------------------------------------------------- medidas --

def inventario() -> dict:
    """Linhas de Pascal, separadas por origem."""
    gerados, mao = [], []
    for pas in sorted(SRC.glob("*.pas")):
        texto = pas.read_text(encoding="utf-8", errors="replace")
        alvo = gerados if MARCA_GERADO in texto else mao
        alvo.append((f"src/{pas.name}", len(texto.splitlines())))
    if not gerados:
        raise CheckError(f"nenhum .pas em {SRC} com a marca {MARCA_GERADO!r} "
                         "-- o dfm2lfm.py nao rodou, ou mudou o cabecalho")
    if not LPR.exists():
        raise CheckError(f"{LPR} nao existe")
    mao.append(("wte.lpr", linhas_de(LPR)))

    lfm_estrutura = lfm_hex = 0
    lfms = sorted(FORMS.glob("*.lfm"))
    for lfm in lfms:
        e, h = lfm_particionado(lfm)
        lfm_estrutura += e
        lfm_hex += h

    return {
        "pas_gerados": gerados,
        "pas_mao": sorted(mao),
        "n_lfm": len(lfms),
        "lfm_estrutura": lfm_estrutura,
        "lfm_hex": lfm_hex,
    }


def conferir_stubs(handlers: list[dict]) -> dict[str, int]:
    """Cada linha do TSV tem um `REStub` seu, na unidade que declara a classe.

    Aborta na primeira falha. Stub que sumiu e casca errada, e casca errada faz
    a fase 4 inteira ser implementada contra o alvo errado.
    """
    fontes = {}
    for pas in sorted(SRC.glob("*.pas")):
        fontes[pas.name] = pas.read_text(encoding="utf-8", errors="replace")

    por_unidade: dict[str, int] = {}
    problemas: list[str] = []
    for h in handlers:
        chave = f"{h['formulario']}.{h['handler']}"
        marca = f"REStub('{chave}')"
        donos = [nome for nome, txt in fontes.items() if marca in txt]
        if len(donos) != 1:
            problemas.append(
                f"{chave}: {len(donos)} ocorrencia(s) de {marca} "
                f"({', '.join(donos) or 'nenhuma'})")
            continue
        dono = donos[0]
        classe = re.compile(rf"\bT{re.escape(h['formulario'])}\s*=\s*class\(",
                            re.I)
        if not classe.search(fontes[dono]):
            problemas.append(
                f"{chave}: o stub esta em {dono}, que nao declara "
                f"T{h['formulario']}")
            continue
        por_unidade[dono] = por_unidade.get(dono, 0) + 1

    if problemas:
        raise CheckError(
            "stubs fora do lugar (" + str(len(problemas)) + "):\n  " +
            "\n  ".join(problemas))

    total = sum(por_unidade.values())
    if total != len(handlers):
        raise CheckError(f"{total} stubs para {len(handlers)} handlers")
    return por_unidade


def conferir_formularios() -> list[str]:
    dfms = sorted(p.stem for p in DFM.glob("*.dfm"))
    lfms = sorted(p.stem for p in FORMS.glob("*.lfm"))
    if len(dfms) != len(lfms):
        raise CheckError(f"{len(dfms)} .dfm contra {len(lfms)} .lfm")
    # O nome muda de proposito -- MainForm.dfm vira ep2002_mainform.lfm --
    # entao o pareamento e pelo objeto raiz do .lfm, nao pelo nome do arquivo.
    raizes = []
    for lfm in sorted(FORMS.glob("*.lfm")):
        primeira = lfm.read_text(encoding="utf-8", errors="replace").splitlines()[0]
        m = re.match(r"object\s+(\S+)\s*:", primeira)
        if not m:
            raise CheckError(f"{lfm.name}: primeira linha nao declara objeto")
        raizes.append(m.group(1))
    faltando = sorted(set(dfms) - set(raizes))
    sobrando = sorted(set(raizes) - set(dfms))
    if faltando or sobrando:
        raise CheckError(
            f"formularios divergem -- sem .lfm: {faltando or 'nenhum'}; "
            f"sem .dfm: {sobrando or 'nenhum'}")
    return sorted(raizes)


def conferir_vereditos(formularios: list[str]) -> dict[str, str]:
    """Um veredito escrito por formulario, na tabela do `re/visual.md`."""
    if not VISUAL.exists():
        raise CheckError(f"{VISUAL} nao existe -- WTE-TASK-12 nao rodou")
    texto = VISUAL.read_text(encoding="utf-8")
    linhas = texto.splitlines()
    try:
        i = next(k for k, l in enumerate(linhas)
                 if l.startswith("## Veredito por formul"))
    except StopIteration:
        raise CheckError(f"{VISUAL.name}: sem secao 'Veredito por formulario'")

    achados: dict[str, str] = {}
    for linha in linhas[i:]:
        if linha.startswith("## ") and not linha.startswith("## Veredito"):
            break
        m = re.match(r"^\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|\s*$",
                     linha)
        if m and m.group(1) in formularios:
            achados[m.group(1)] = m.group(2).strip()
    faltando = sorted(set(formularios) - set(achados))
    if faltando:
        raise CheckError(
            f"{VISUAL.name}: sem veredito para {len(faltando)} formulario(s): "
            + ", ".join(faltando))
    return achados


def conferir_eventos() -> int:
    """`eventos.md` existe e traz achado, nao so roteiro."""
    if not EVENTOS.exists():
        raise CheckError(f"{EVENTOS} nao existe -- WTE-TASK-13 nao rodou")
    texto = EVENTOS.read_text(encoding="utf-8")
    achados = len(re.findall(r"^## Achado \d", texto, re.M))
    if achados == 0:
        raise CheckError(f"{EVENTOS.name}: nenhum '## Achado' -- a fase 4 "
                         "depende de diferenca de ordem registrada")
    return achados


# ----------------------------------------------------------------- saida --

def montar(inv: dict, por_unidade: dict, formularios: list[str],
           vereditos: dict, n_achados: int, n_handlers: int) -> str:
    pas_ger = sum(n for _, n in inv["pas_gerados"])
    pas_mao = sum(n for _, n in inv["pas_mao"])
    lfm_e = inv["lfm_estrutura"]
    lfm_h = inv["lfm_hex"]

    ger_sem_hex = pas_ger + lfm_e
    total_sem_hex = ger_sem_hex + pas_mao
    frac = 100.0 * ger_sem_hex / total_sem_hex
    com_original = 100.0 * (ger_sem_hex + lfm_h) / (total_sem_hex + lfm_h)

    L: list[str] = []
    w = L.append
    w(f"# `re/{MD_NAME}` — fechamento da fase 2")
    w("")
    w("Produto da [WTE-TASK-14](/docs/tasks/14-fechamento-fase-2.md). "
      "**Gerado** por")
    w("[`../tools/check_fase2.py`](../tools/check_fase2.py) — não editar à "
      "mão; correção")
    w("entra no script e o arquivo é regerado:")
    w("")
    w("```sh")
    w(f"python3 {GENERATOR}")
    w(f"python3 {GENERATOR} --check   # o que `make -C wte check` roda")
    w("```")
    w("")
    w("Ele não remede o binário: mede a **coerência entre os produtos** das "
      "WTE-TASK-10 a 13")
    w("e a fração de código gerado, que é o número com que a §4.4 do plano se "
      "compromete.")
    w("")
    w("---")
    w("")
    w("## Veredito da fase")
    w("")
    w("| Conferência | Resultado |")
    w("|---|---|")
    w(f"| Formulários com `.lfm` e `.dfm` pareados | **{len(formularios)}** |")
    w(f"| Handlers do `published_methods.tsv` com stub próprio | "
      f"**{n_handlers}** |")
    w("| Stub na unidade que declara a classe | **todos** |")
    w(f"| Formulários com veredito visual escrito | **{len(vereditos)}** |")
    w(f"| Achados registrados em `eventos.md` | **{n_achados}** |")
    w("")
    w("Qualquer uma dessas falhando **aborta** este script — não há tabela de "
      "resíduo.")
    w("Resíduo é falha, como no `FORBIDDEN` do `port_database.py`.")
    w("")
    w("A conferência que **não** está aqui é \"nenhum arquivo gerado foi "
      "editado à mão\":")
    w("quem prova isso é o `dfm2lfm.py --check`, na mesma bateria. Refazê-la "
      "aqui seria")
    w("uma segunda cópia da mesma medida.")
    w("")
    w("---")
    w("")
    w("## Fração de código gerado — a tese da §4.4")
    w("")
    w("A §4.4 diz que só um bloco vem de teclado: os corpos dos 96 handlers. "
      "Medido")
    w("hoje, com a fase 2 fechada e as fases 3 e 4 ainda por vir:")
    w("")
    w("| Origem | Arquivos | Linhas |")
    w("|---|---|---|")
    w(f"| Unidades Pascal geradas (`dfm2lfm.py`) | "
      f"{len(inv['pas_gerados'])} | {pas_ger} |")
    w(f"| Formulários `.lfm`, estrutura | {inv['n_lfm']} | {lfm_e} |")
    w(f"| **Gerado, subtotal** | | **{ger_sem_hex}** |")
    w(f"| Escrito à mão | {len(inv['pas_mao'])} | {pas_mao} |")
    w(f"| **Total** | | **{total_sem_hex}** |")
    w("")
    w(f"**{frac:.1f}% do Pascal da casca é saída de gerador.**")
    w("")
    w("Escrito à mão, linha por linha:")
    w("")
    w("| Arquivo | Linhas | O que é |")
    w("|---|---|---|")
    razao = {
        "wte.lpr": "programa principal (WTE-TASK-02)",
        "src/retrace.pas": "o registrador de disparo (WTE-TASK-11)",
        "src/wtemain.pas": "auto-create, `--show` e a marca de título "
                           "(WTE-TASK-11)",
    }
    for nome, n in inv["pas_mao"]:
        w(f"| `{nome}` | {n} | {razao.get(nome, '—')} |")
    w("")
    w("### O hex dos blobs fica fora da conta, e por quê")
    w("")
    w(f"Os 118 blobs viraram **{lfm_h} linhas** de hexadecimal inline nos 18 "
      "`.lfm`")
    w("(decisão de 2026-08-06, registrada no `re/dfm/README.md`). Contados "
      "junto, a")
    w(f"fração sobe para {com_original:.1f}% — e passa a medir bitmap, não "
      "geração de código.")
    w("O número que responde à §4.4 é o de cima.")
    w("")
    w("### O que este número **não** decide ainda")
    w("")
    w("A §4.3 afirma que a camada de UI é **60% do volume** do projeto. Isso "
      "não é")
    w("verificável hoje: a UI é a única camada que existe. Só dá para fechar "
      "depois")
    w("da fase 3 (camada de dados, gerada) e da fase 4 (os 96 corpos, à mão) — "
      "e é")
    w("nessa hora que a fração cai, porque os corpos são o único bloco manual "
      "grande.")
    w("")
    w("O que **está** verificado é o lado forte da tese: a casca inteira saiu "
      "de")
    w("gerador, e o que sobrou de teclado é andaime de projeto, não lógica do "
      "editor.")
    w("")
    w("---")
    w("")
    w("## Stubs por unidade")
    w("")
    w("| Unidade | Stubs |")
    w("|---|---|")
    for unidade in sorted(por_unidade, key=lambda u: (-por_unidade[u], u)):
        w(f"| `src/{unidade}` | {por_unidade[unidade]} |")
    w(f"| **total** | **{n_handlers}** |")
    w("")
    w("---")
    w("")
    w("## O que a fase 2 **não** prova")
    w("")
    w("Escrito de propósito, para o vocabulário não inflar.")
    w("")
    w("1. **A casca não toca a imagem de CD.** Nada aqui diz que o app "
      "*funciona* —")
    w("   só que ele *parece* e *reage*. Toda gravação é da fase 3 em diante.")
    w("2. **Os 18 formulários não são navegáveis, e não podiam ser.** O "
      "critério de")
    w("   pronto da fase 2 no plano pede navegação; quem abre formulário são "
      "os")
    w("   handlers, e nesta fase eles são stub. O que existe é `--show`, "
      "andaime")
    w("   explícito para a captura da WTE-TASK-12. Navegação de verdade chega "
      "com a")
    w("   WTE-TASK-25.")
    w("3. **A comparação visual cobriu os 18 do port e 4 do original.** Os "
      "outros 14")
    w("   não foram capturados porque o oráculo quebra ao selecionar um time — "
      "ver")
    w("   `re/visual.md`, achado 1. Geometria e presença de controle estão "
      "provadas")
    w("   contra o DFM, que é evidência mais forte que screenshot; **cor e "
      "render**")
    w("   dos 14 continuam sem confronto.")
    w("4. **Nenhum evento foi comparado com o original em execução.** O que a")
    w("   WTE-TASK-13 mediu do lado da LCL saiu do fonte da LCL e do trace do "
      "port;")
    w("   do lado do original saiu do DFM e da observação do arranque.")
    w("")
    w("---")
    w("")
    w("## Pendências que a fase 2 entrega para as seguintes")
    w("")
    w("| Pendência | Para quem |")
    w("|---|---|")
    w("| O oráculo quebra ao selecionar um time (310 `EXCEPTION_ACCESS_"
      "VIOLATION`) | [WTE-TASK-22](/docs/tasks/22-harness-golden.md), "
      "**bloqueante** |")
    w("| Aceitar o aviso de tamanho grava 11.952 bytes na imagem | "
      "[WTE-TASK-22](/docs/tasks/22-harness-golden.md) |")
    w("| Teclado não chega ao app LCL no `:99` | "
      "[WTE-TASK-22](/docs/tasks/22-harness-golden.md) |")
    w("| Cor de fundo posta em tempo de execução | "
      "[WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md) |")
    w("| As 14 capturas do original | "
      "[WTE-TASK-37](/docs/tasks/37-reconferencia-de-ui.md) |")
    w("")
    return "\n".join(L) + "\n"


def gerar() -> dict[str, str]:
    handlers = ler_tsv()
    inv = inventario()
    por_unidade = conferir_stubs(handlers)
    formularios = conferir_formularios()
    vereditos = conferir_vereditos(formularios)
    n_achados = conferir_eventos()
    return {MD_NAME: montar(inv, por_unidade, formularios, vereditos,
                            n_achados, len(handlers))}


def do_check(files: dict[str, str]) -> int:
    problemas: list[str] = []
    for nome, conteudo in sorted(files.items()):
        path = OUT / nome
        if not path.exists():
            problemas.append(f"{nome}: nao existe")
            continue
        disco = path.read_text(encoding="utf-8")
        if disco == conteudo:
            continue
        for i, (a, b) in enumerate(
                zip(disco.splitlines(), conteudo.splitlines()), 1):
            if a != b:
                problemas.append(f"{nome}: linha {i} diverge")
                break
        else:
            problemas.append(
                f"{nome}: {len(disco.splitlines())} linhas no disco contra "
                f"{len(conteudo.splitlines())} regeradas")
    if problemas:
        print("wte/re nao corresponde aos produtos da fase 2:", file=sys.stderr)
        for p in problemas:
            print("  " + p, file=sys.stderr)
        print(f"rode: python3 {GENERATOR}", file=sys.stderr)
        return 1
    print(f"{len(files)} arquivo em dia com os produtos da fase 2 "
          "(wte/src, wte/forms, published_methods.tsv, visual.md, eventos.md)")
    return 0


def do_write(files: dict[str, str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for nome, conteudo in sorted(files.items()):
        (OUT / nome).write_text(conteudo, encoding="utf-8", newline="\n")
        print(f"  {nome}: {conteudo.count(chr(10))} linhas, "
              f"{len(conteudo.encode('utf-8'))} bytes")
    return 0


def main(argv: list[str]) -> int:
    check = False
    for arg in argv:
        if arg == "--check":
            check = True
        else:
            print(f"uso: {GENERATOR} [--check]", file=sys.stderr)
            return 2
    try:
        files = gerar()
    except CheckError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return do_check(files) if check else do_write(files)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
