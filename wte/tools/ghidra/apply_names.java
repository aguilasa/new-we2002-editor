// Aplica ao projeto Ghidra o que a fase 1 ja mediu -- WTE-TASK-24.
//
// Le dois TSV versionados e devolve nome e rotulo ao banco do Ghidra. Nao
// decompila nada, e nao escreve em `we-team-editor.exe` -- leitura pura, como
// manda a tabela das fontes binarias.
//
//   wte/re/published_methods.tsv   os 96 handlers, com endereco e formulario
//   wte/re/offsets.tsv             a tabela de offsets em .data (WTE-TASK-06)
//
// 96 renomeacoes a mao nao sobrevivem a reimportar o binario -- e o binario
// SERA reimportado, porque o banco do Ghidra e local e nao entra no
// versionamento. Por isso script.
//
// ## Por que Java e nao Python
//
// O Ghidra 12 largou o Jython, e script `.py` agora exige PyGhidra, que por sua
// vez exige `pip install pyghidra` mais JPype no Python da maquina. O
// `analyzeHeadless` compila GhidraScript em Java sozinho, com o JDK que ja
// esta fixado no `launch.properties` -- zero dependencia nova, e roda igual no
// headless e na GUI. A troca esta registrada no Log da WTE-TASK-24.
//
//@category WTE

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;

public class apply_names extends GhidraScript {

    // A pior armadilha do projeto (§8.1). O C++Builder passa `this`/1o
    // argumento em EAX, 2o em EDX, 3o em ECX; com qualquer cspec que nao seja o
    // de Borland o Ghidra assume __cdecl e reporta FUNCAO SEM ARGUMENTO que
    // misteriosamente le lixo. A saida do decompilador vira ruido convincente.
    //
    // Aplicar os 96 nomes por cima disso e pior que nao aplicar: da nome bonito
    // a assinatura errada, e quem ler depois confia.
    private static final String CSPEC_EXIGIDO = "borlandcpp";

    private final List<String> problemas = new ArrayList<>();

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            fail("uso: apply_names.java <raiz do repositorio>");
        }
        File raiz = new File(args[0]);
        File pub = new File(raiz, "wte/re/published_methods.tsv");
        File ofs = new File(raiz, "wte/re/offsets.tsv");
        for (File f : new File[] { pub, ofs }) {
            if (!f.isFile()) {
                fail(f + " nao existe -- a fase 1 nao rodou?");
            }
        }

        conferirCspec();

        List<Map<String, String>> handlers = lerTsv(pub);
        println("apply_names: " + handlers.size() + " handler(s) no TSV");
        aplicarHandlers(handlers);

        aplicarOffsets(lerTsv(ofs));
        medirImports();

        if (!problemas.isEmpty()) {
            println("apply_names: " + problemas.size() + " PROBLEMA(S):");
            for (String p : problemas) {
                println("  " + p);
            }
            // Nome nao aplicado e nome que a fase 4 vai procurar e nao achar.
            // Falhar alto -- silencio aqui vira "esse handler nao existe".
            fail(problemas.size() + " nome(s) nao aplicado(s)");
        }
        println("apply_names: ok");
    }

    private void fail(String msg) throws Exception {
        println("apply_names: ABORTADO: " + msg);
        throw new IllegalStateException(msg);
    }

    // ---------------------------------------------------------- guarda 1 ---

    private void conferirCspec() throws Exception {
        String got = currentProgram.getCompilerSpec().getCompilerSpecID()
                .getIdAsString();
        if (!CSPEC_EXIGIDO.equals(got)) {
            fail("cspec e '" + got + "', nao '" + CSPEC_EXIGIDO + "'.\n"
                + "  Com outro cspec o Ghidra assume __cdecl, e o C++Builder\n"
                + "  passa this em EAX: toda assinatura sai errada, e aplicar\n"
                + "  os 96 nomes por cima so daria nome bonito a ruido.\n"
                + "  Reimporte com: -processor x86:LE:32:default"
                + " -cspec borlandcpp");
        }
        String conv = "?";
        if (currentProgram.getCompilerSpec().getDefaultCallingConvention()
                != null) {
            conv = currentProgram.getCompilerSpec()
                    .getDefaultCallingConvention().getName();
        }
        println("apply_names: cspec=" + got + ", convencao default=" + conv);
    }

    // ------------------------------------------------------------- TSV -----

    private List<Map<String, String>> lerTsv(File path) throws Exception {
        List<Map<String, String>> fora = new ArrayList<>();
        try (BufferedReader in = new BufferedReader(new FileReader(path))) {
            String cabLinha = in.readLine();
            if (cabLinha == null) {
                fail(path + " esta vazio");
            }
            String[] cab = cabLinha.split("\t", -1);
            String linha;
            while ((linha = in.readLine()) != null) {
                if (linha.trim().isEmpty()) {
                    continue;
                }
                String[] campos = linha.split("\t", -1);
                Map<String, String> reg = new HashMap<>();
                for (int i = 0; i < cab.length && i < campos.length; i++) {
                    reg.put(cab[i], campos[i]);
                }
                fora.add(reg);
            }
        }
        return fora;
    }

    // -------------------------------------------------------- handlers -----

    private void aplicarHandlers(List<Map<String, String>> linhas)
            throws Exception {
        int criadas = 0, renomeadas = 0, jaOk = 0;
        for (Map<String, String> reg : linhas) {
            Address addr = toAddr(reg.get("endereco"));
            // `Formulario__handler`: o mesmo par que o REStub() da casca usa
            // (WTE-TASK-11), para que grepar um nome atravesse Ghidra, TSV e
            // Pascal.
            String nome = reg.get("formulario") + "__" + reg.get("handler");
            Function fn = getFunctionAt(addr);
            if (fn == null) {
                fn = createFunction(addr, nome);
                if (fn == null) {
                    problemas.add(nome + ": nao foi possivel criar funcao em "
                                  + reg.get("endereco"));
                    continue;
                }
                criadas++;
            } else if (nome.equals(fn.getName())) {
                jaOk++;
                continue;
            } else {
                fn.setName(nome, SourceType.USER_DEFINED);
                renomeadas++;
            }
            fn.setComment("WTE-TASK-04: " + reg.get("formulario") + "."
                          + reg.get("handler") + " (" + reg.get("evento")
                          + " de " + reg.get("componente") + "), grupo "
                          + reg.get("grupo"));
        }
        println("apply_names: handlers -- " + criadas + " criada(s), "
                + renomeadas + " renomeada(s), " + jaOk + " ja ok");
    }

    // --------------------------------------------------------- offsets -----

    // Rotular aqui e o atalho da §1.7 aplicado DENTRO da ferramenta: toda
    // referencia a tabela passa a aparecer legivel no decompilador, e o
    // analista deixa de cruzar endereco com o offsets.tsv de olho.
    private void aplicarOffsets(List<Map<String, String>> linhas)
            throws Exception {
        SymbolTable st = currentProgram.getSymbolTable();
        int rotulos = 0, comentarios = 0;
        for (Map<String, String> reg : linhas) {
            String registro = reg.get("registro");
            // `tabela_slot` e o slot dentro da tabela; `confirmado` traz TODAS
            // as ocorrencias do mesmo offset, e sao varias: a tabela aparece
            // QUATRO vezes na .data, e alguns offsets ainda aparecem como
            // imediato dentro da .text. Rotular so a primeira copia deixaria
            // tres quartos das referencias ilegiveis, que e o oposto do que o
            // atalho da §1.7 quer.
            if (!"tabela_slot".equals(registro)
                    && !"confirmado".equals(registro)) {
                continue;
            }
            String nome = reg.get("nome");
            String va = reg.get("va");
            if (nome == null || nome.trim().isEmpty()
                    || va == null || va.trim().isEmpty()) {
                continue;
            }
            nome = nome.trim();
            for (String um : va.split("\\|")) {
                um = um.trim();
                if (um.isEmpty()) {
                    continue;
                }
                Address addr = toAddr(um);
                if (addr == null) {
                    problemas.add(nome + ": VA " + um + " nao resolve");
                    continue;
                }
                String nota = "WTE-TASK-06: " + nome + " = " + reg.get("valor");
                // Endereco em bloco executavel e o imediato DENTRO de uma
                // instrucao. Rotulo ali criaria simbolo no meio do codigo;
                // comentario diz a mesma coisa sem sujar a listagem.
                if (getMemoryBlock(addr) != null
                        && getMemoryBlock(addr).isExecute()) {
                    setEOLComment(addr, nota);
                    comentarios++;
                } else {
                    st.createLabel(addr, nome, SourceType.USER_DEFINED);
                    setEOLComment(addr, nota);
                    rotulos++;
                }
            }
        }
        println("apply_names: tabela de offsets -- " + rotulos
                + " rotulo(s) em dados, " + comentarios
                + " comentario(s) em codigo");
    }

    // --------------------------------------------------------- imports -----

    // Vantagem que compensa a §8.2: os imports de rtl60.bpl/vcl60.bpl chegam
    // com nome mangled, entao `@Controls@TWinControl@CreateHandle$qqrv` se le
    // direto -- centenas de pontos de referencia de graca. Mas so se o Ghidra
    // os resolveu POR NOME, e nao deixou endereco cru. Isto mede isso.
    private void medirImports() {
        Map<String, Integer> porLib = new TreeMap<>();
        int semNome = 0;
        for (Symbol sym : currentProgram.getSymbolTable().getExternalSymbols()) {
            String lib = sym.getParentNamespace() == null
                    ? "?" : sym.getParentNamespace().getName();
            porLib.merge(lib, 1, Integer::sum);
            String n = sym.getName();
            if (n == null || n.startsWith("Ordinal_") || n.startsWith("FUN_")) {
                semNome++;
            }
        }
        for (Map.Entry<String, Integer> e : porLib.entrySet()) {
            println("apply_names: imports de " + e.getKey() + ": "
                    + e.getValue());
        }
        println("apply_names: imports sem nome legivel: " + semNome);
    }
}
