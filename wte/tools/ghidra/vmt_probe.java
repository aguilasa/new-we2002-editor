// Mede o campo de objeto de cada chamada virtual -- WTE-TASK-24, §8.2.
//
// A rota 2 do plano diz: "o objeto veio de `[ebx+0x390]`, e o DFM diz qual
// componente e". Isso so fecha se os campos publicados do formulario formarem
// uma corrida CONTIGUA de ponteiros de 4 bytes, na ordem do DFM -- que e o que
// a VCL faz, mas que nao vale afirmar sem medir.
//
// Este script mede. Para todas as funcoes de um formulario (prefixo
// `<Form>__`), coleta os deslocamentos `[reg + 0xNNN]` que sao carregados e em
// seguida DEREFERENCIADOS (`MOV reg,[reg]`) -- o par que caracteriza "peguei o
// componente, agora pego o VMT dele". Imprime a corrida encontrada, o passo, e
// quantos slots ela tem, para cruzar com a contagem de componentes do
// `wte/re/dfm/censo.md`.
//
// Nao decompila e nao imprime corpo: e listagem, como o decompile_one.
//
// ## A votacao da ancora (segundo argumento, opcional)
//
//   -postScript vmt_probe.java MainForm /caminho/da/raiz
//
// Com a raiz do repositorio, o script tambem CALCULA a ancora em vez de so
// imprimir a entrada dela. Ele le o `published_methods.tsv` (de que componente
// e cada handler) e o `.dfm` do formulario (a posicao daquele componente na
// ordem plana do texto), e vota: `base = campo - 4*(posicao-1)`. A base
// verdadeira seria a que se repete entre handlers independentes.
//
// A votacao esta AQUI, e nao numa planilha de uma sessao, porque o resultado
// dela -- que ela NAO converge -- e o que decide a rota da §8.2 e o que o
// `wte/re/vmt.md` publica. Numero que decide metodo tem de ter ferramenta
// (CORR-WTE-054).
//
//@category WTE

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;

public class vmt_probe extends GhidraScript {

    // `  object colorear: TBitBtn` -- so o nome interessa, e a ordem em que
    // as linhas aparecem.
    private static final Pattern OBJETO = Pattern.compile(
            "^\\s*object (\\w+): \\w+\\s*$");

    // `MOV EAX,dword ptr [EBX + 0x390]`
    private static final Pattern CAMPO = Pattern.compile(
            "^MOV (\\w+),(?:dword ptr )?\\[(\\w+) \\+ (0x[0-9a-f]+)\\]$");
    // `MOV EDX,dword ptr [EAX]`  -- o carregamento do VMT
    private static final Pattern DEREF = Pattern.compile(
            "^MOV (\\w+),(?:dword ptr )?\\[(\\w+)\\]$");
    // `CALL dword ptr [ECX + 0xcc]`
    private static final Pattern VCALL = Pattern.compile(
            "^CALL (?:dword ptr )?\\[(\\w+) \\+ (0x[0-9a-f]+)\\]$");

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            println("vmt_probe: uso: vmt_probe.java <PrefixoDoFormulario>");
            throw new IllegalArgumentException("sem formulario");
        }
        String forma = args[0];
        String raiz = args.length >= 2 ? args[1] : null;

        // deslocamento do campo -> quantas vezes apareceu
        Map<Long, Integer> campos = new TreeMap<>();
        // slot de VMT -> quantas vezes
        Map<Long, Integer> slots = new TreeMap<>();
        int vcalls = 0, resolvidas = 0;
        List<String> exemplos = new ArrayList<>();

        for (Function fn : currentProgram.getFunctionManager()
                .getFunctions(true)) {
            if (!fn.getName().startsWith(forma + "__")) {
                continue;
            }
            List<Instruction> corpo = new ArrayList<>();
            for (Instruction ins : currentProgram.getListing()
                    .getInstructions(fn.getBody(), true)) {
                corpo.add(ins);
            }
            for (int i = 0; i < corpo.size(); i++) {
                Matcher mc = VCALL.matcher(corpo.get(i).toString());
                if (!mc.matches()) {
                    continue;
                }
                vcalls++;
                long slot = Long.decode(mc.group(2));
                slots.merge(slot, 1, Integer::sum);

                // Andar para tras atras do par campo/deref que produziu o
                // registrador usado na chamada.
                String vmtReg = mc.group(1);
                Long campo = null;
                String objReg = null;
                for (int k = i - 1; k >= Math.max(0, i - 8); k--) {
                    String t = corpo.get(k).toString();
                    Matcher md = DEREF.matcher(t);
                    if (objReg == null && md.matches()
                            && md.group(1).equals(vmtReg)) {
                        objReg = md.group(2);
                        continue;
                    }
                    if (objReg != null) {
                        Matcher mf = CAMPO.matcher(t);
                        if (mf.matches() && mf.group(1).equals(objReg)) {
                            campo = Long.decode(mf.group(3));
                            break;
                        }
                    }
                }
                if (campo != null) {
                    campos.merge(campo, 1, Integer::sum);
                    resolvidas++;
                    if (exemplos.size() < 8) {
                        exemplos.add(String.format(
                                "%s  %s  campo +0x%x  slot +0x%x",
                                corpo.get(i).getAddress(), fn.getName(),
                                campo, slot));
                    }
                }
            }
        }

        println("vmt_probe: formulario " + forma);
        println("vmt_probe: " + vcalls + " chamada(s) virtual(is), "
                + resolvidas + " com campo de objeto recuperado");
        for (String e : exemplos) {
            println("  " + e);
        }

        println("vmt_probe: " + campos.size() + " campo(s) distinto(s):");
        Long ant = null;
        int passo4 = 0;
        for (Map.Entry<Long, Integer> e : campos.entrySet()) {
            String d = "";
            if (ant != null) {
                long delta = e.getKey() - ant;
                d = " (+" + delta + ")";
                if (delta == 4) {
                    passo4++;
                }
            }
            println(String.format("  +0x%03x  %dx%s", e.getKey(),
                    e.getValue(), d));
            ant = e.getKey();
        }
        long lo = 0, hi = -1;
        if (!campos.isEmpty()) {
            lo = ((TreeMap<Long, Integer>) campos).firstKey();
            hi = ((TreeMap<Long, Integer>) campos).lastKey();
            println(String.format(
                    "vmt_probe: corrida de +0x%x a +0x%x = %d slot(s) de 4 "
                    + "bytes; %d par(es) consecutivo(s) com passo 4",
                    lo, hi, (hi - lo) / 4 + 1, passo4));
        }

        println("vmt_probe: slots de VMT usados:");
        for (Map.Entry<Long, Integer> e : slots.entrySet()) {
            println(String.format("  +0x%x  %dx", e.getKey(), e.getValue()));
        }

        // Por handler, os campos que ele toca. E o que permite ANCORAR a
        // corrida: o `published_methods.tsv` diz de que componente cada handler
        // e, e o DFM da a posicao daquele componente. Com base = campo - 4*pos,
        // a base verdadeira e a que se repete entre handlers independentes.
        println("vmt_probe: CAMPOS-POR-HANDLER (handler<TAB>0xNNN,...)");
        Map<String, List<Long>> porHandler = new TreeMap<>();
        for (Function fn : currentProgram.getFunctionManager()
                .getFunctions(true)) {
            if (!fn.getName().startsWith(forma + "__")) {
                continue;
            }
            Map<Long, Integer> meus = new TreeMap<>();
            for (Instruction ins : currentProgram.getListing()
                    .getInstructions(fn.getBody(), true)) {
                Matcher mf = CAMPO.matcher(ins.toString());
                if (mf.matches()) {
                    meus.merge(Long.decode(mf.group(3)), 1, Integer::sum);
                }
            }
            StringBuilder sb = new StringBuilder();
            for (Long k : meus.keySet()) {
                if (sb.length() > 0) {
                    sb.append(",");
                }
                sb.append(String.format("0x%x", k));
            }
            println("CAMPOS\t" + fn.getName() + "\t" + sb);
            porHandler.put(fn.getName().substring(forma.length() + 2),
                    new ArrayList<>(meus.keySet()));
        }

        if (raiz != null) {
            votar(raiz, forma, porHandler, lo, hi);
        } else {
            println("vmt_probe: sem a raiz do repositorio no 2o argumento, a "
                    + "votacao da ancora nao roda (ver o cabecalho).");
        }
    }

    /**
     * A tentativa de ancora, e o motivo de ela estar aqui: o numero que ela
     * produz -- quantos votos o candidato mais votado tem -- e o que decide
     * a rota da §8.2. Ele nao pode sair de conta feita fora.
     */
    private void votar(String raiz, String forma,
            Map<String, List<Long>> porHandler, long lo, long hi)
            throws Exception {

        File tsv = new File(raiz, "wte/re/published_methods.tsv");
        File dfm = new File(raiz, "wte/re/dfm/" + forma + ".dfm");
        if (!tsv.isFile() || !dfm.isFile()) {
            println("vmt_probe: ANCORA: nao achei " + tsv + " ou " + dfm);
            return;
        }

        // handler -> componente dono, so deste formulario.
        Map<String, String> dono = new HashMap<>();
        for (String linha : Files.readAllLines(tsv.toPath(),
                StandardCharsets.UTF_8)) {
            String[] c = linha.split("\t", -1);
            if (c.length < 4 || !c[2].equals(forma)) {
                continue;
            }
            dono.put(c[1], c[3]);
        }

        // A ordem PLANA do texto do .dfm -- que e exatamente a premissa sob
        // teste. O primeiro `object` e o proprio formulario; os filhos comecam
        // na posicao 1.
        Map<String, Integer> posicao = new HashMap<>();
        int n = 0;
        for (String linha : Files.readAllLines(dfm.toPath(),
                StandardCharsets.ISO_8859_1)) {
            Matcher m = OBJETO.matcher(linha);
            if (m.matches()) {
                if (n > 0 || !m.group(1).equals(forma)) {
                    posicao.putIfAbsent(m.group(1), ++n);
                }
            }
        }

        // Voto: base = campo - 4*(posicao-1), so para campo dentro da corrida
        // medida acima -- fora dela o campo nao e ponteiro de componente.
        Map<Long, Integer> votos = new TreeMap<>();
        int referencias = 0, semDono = 0, semPosicao = 0;
        for (Map.Entry<String, List<Long>> e : porHandler.entrySet()) {
            String comp = dono.get(e.getKey());
            if (comp == null) {
                semDono++;
                continue;
            }
            Integer pos = posicao.get(comp);
            if (pos == null) {
                semPosicao++;
                continue;
            }
            for (Long campo : e.getValue()) {
                if (campo < lo || campo > hi) {
                    continue;
                }
                referencias++;
                votos.merge(campo - 4L * (pos - 1), 1, Integer::sum);
            }
        }

        println("vmt_probe: ANCORA: " + posicao.size() + " componente(s) no "
                + dfm.getName() + ", " + dono.size() + " handler(s) com dono "
                + "no TSV");
        println("vmt_probe: ANCORA: " + referencias + " referencia(s) de campo "
                + "dentro da corrida votaram" + (semDono > 0
                        ? " (" + semDono + " handler(s) sem dono no TSV)" : "")
                + (semPosicao > 0
                        ? " (" + semPosicao + " sem posicao no DFM)" : ""));

        List<Map.Entry<Long, Integer>> rank = new ArrayList<>(votos.entrySet());
        rank.sort((a, b) -> b.getValue() - a.getValue());
        println("vmt_probe: ANCORA: " + votos.size() + " candidato(s) a base; "
                + "os cinco mais votados:");
        for (int i = 0; i < Math.min(5, rank.size()); i++) {
            println(String.format("  base +0x%03x  %d voto(s)",
                    rank.get(i).getKey(), rank.get(i).getValue()));
        }
        if (rank.size() >= 2) {
            long d = Math.abs(rank.get(0).getKey() - rank.get(1).getKey());
            println("vmt_probe: ANCORA: 1o e 2o colocados a " + d
                    + " byte(s) um do outro");
        }
    }
}
