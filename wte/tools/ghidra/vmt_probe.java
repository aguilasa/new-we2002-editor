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
//@category WTE

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;

public class vmt_probe extends GhidraScript {

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
        if (!campos.isEmpty()) {
            long lo = ((TreeMap<Long, Integer>) campos).firstKey();
            long hi = ((TreeMap<Long, Integer>) campos).lastKey();
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
        }
    }
}
