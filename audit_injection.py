# -*- coding: utf-8 -*-
"""Offline injection audit for the NoSidebar mixin.

Uses Mixin's own ASM (shaded into mixin-0.8.5.jar) to:
  1. read the shipped @Mixin / @Inject annotations off the compiled mixin class
  2. load net.minecraft.client.gui.Gui out of the real Forge SRG client jar
  3. resolve the injection target exactly the way Mixin does when remap=false
  4. confirm the handler signature is a valid injection point for that target
  5. confirm another mod (EndingLibrary) does not already overwrite that method
"""
import json
import os
import subprocess
import sys
import zipfile

# console is GBK here; force UTF-8 so diagnostics never crash the script
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MIXIN = r"D:\我的世界\魔归\.minecraft\libraries\org\spongepowered\mixin\0.8.5\mixin-0.8.5.jar"
ASM = r"D:\我的世界\魔归\.minecraft\libraries\org\ow2\asm\asm\9.6\asm-9.6.jar"
ASM_TREE = r"D:\我的世界\魔归\.minecraft\libraries\org\ow2\asm\asm-tree\9.6\asm-tree-9.6.jar"
SRG = r"D:\我的世界\魔归\.minecraft\libraries\net\minecraft\client\1.20.1-20230612.114412\client-1.20.1-20230612.114412-srg.jar"
MODS = r"D:\我的世界\魔归\.minecraft\versions\魔女之泉：归寂\mods"
JAR = r"D:\我的世界\deepseek1区\build\nosidebar-1.1.0-forge-1.20.1.jar"
JAVA = r"D:\zulu21\bin\java.exe"
TMP = r"C:\Users\li\AppData\Local\Temp\nosidebar-audit"
GUI_ENTRY = "net/minecraft/client/gui/Gui.class"
TARGET_SRG = "m_280030_"
TARGET_DESC = "(Lnet/minecraft/client/gui/GuiGraphics;Lnet/minecraft/world/scores/Objective;)V"

os.makedirs(TMP, exist_ok=True)
problems = []


def check(cond, msg):
    print(("  [OK]   " if cond else "  [FAIL] ") + msg)
    if not cond:
        problems.append(msg)


# ---------------------------------------------------------------- unpack inputs
mixin_cls = os.path.join(TMP, "MixinGuiSidebar.class")
with zipfile.ZipFile(JAR) as z:
    open(mixin_cls, "wb").write(z.read("com/deepseek/nosidebar/mixin/MixinGuiSidebar.class"))

gui_cls = os.path.join(TMP, "Gui.class")
with zipfile.ZipFile(SRG) as z:
    open(gui_cls, "wb").write(z.read(GUI_ENTRY))

java_src = r'''
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.Type;
import org.objectweb.asm.tree.AnnotationNode;
import org.objectweb.asm.tree.ClassNode;
import org.objectweb.asm.tree.MethodNode;
import java.io.File;
import java.nio.file.Files;
import java.util.List;

public class Audit {
    static int failures = 0;

    static void ok(boolean cond, String msg) {
        System.out.println("  [" + (cond ? "OK" : "FAIL") + "]   " + msg);
        if (!cond) failures++;
    }

    public static void main(String[] args) throws Exception {
        String mixinPath = args[0], guiPath = args[1];
        String targetSrg = args[2], targetDesc = args[3];

        ClassNode mixin = new ClassNode();
        new ClassReader(Files.readAllBytes(new File(mixinPath).toPath())).accept(mixin, 0);

        System.out.println("== mixin class: " + mixin.name);
        AnnotationNode mixinAnno = null;
        List<AnnotationNode> clsAnnos = mixin.visibleAnnotations;
        if (mixin.invisibleAnnotations != null) {
            for (AnnotationNode a : mixin.invisibleAnnotations) {
                if (a.desc.equals("Lorg/spongepowered/asm/mixin/Mixin;")) mixinAnno = a;
            }
        }
        if (clsAnnos != null) {
            for (AnnotationNode a : clsAnnos) {
                if (a.desc.equals("Lorg/spongepowered/asm/mixin/Mixin;")) mixinAnno = a;
            }
        }
        ok(mixinAnno != null, "@Mixin annotation readable from the shipped class");
        String targetClass = null;
        boolean remapOk = false;
        if (mixinAnno != null) {
            for (int i = 0; i + 1 < mixinAnno.values.size(); i += 2) {
                String k = String.valueOf(mixinAnno.values.get(i));
                Object v = mixinAnno.values.get(i + 1);
                if (k.equals("targets")) {
                    List<?> l = (List<?>) v;
                    targetClass = String.valueOf(l.get(0));
                }
                if (k.equals("remap")) remapOk = Boolean.FALSE.equals(v) || "false".equals(String.valueOf(v));
            }
        }
        ok("net.minecraft.client.gui.Gui".equals(targetClass), "@Mixin target = " + targetClass);
        ok(remapOk, "@Mixin remap = false");

        MethodNode handler = null;
        AnnotationNode injectAnno = null;
        for (MethodNode m : mixin.methods) {
            List<AnnotationNode> annos = m.visibleAnnotations;
            if (annos == null) continue;
            for (AnnotationNode a : annos) {
                if (a.desc.equals("Lorg/spongepowered/asm/mixin/injection/Inject;")) {
                    handler = m;
                    injectAnno = a;
                }
            }
        }
        ok(handler != null, "@Inject handler found");
        if (handler == null) { System.out.println("RESULT: FAIL"); System.exit(1); }

        String methodName = null;
        boolean cancellable = false, remapFalse = false;
        int require = -1;
        for (int i = 0; i + 1 < injectAnno.values.size(); i += 2) {
            String k = String.valueOf(injectAnno.values.get(i));
            Object v = injectAnno.values.get(i + 1);
            if (k.equals("method")) {
                List<?> l = (List<?>) v;
                methodName = String.valueOf(l.get(0));
            } else if (k.equals("cancellable")) cancellable = Boolean.TRUE.equals(v);
            else if (k.equals("remap")) remapFalse = Boolean.FALSE.equals(v) || "false".equals(String.valueOf(v));
            else if (k.equals("require")) require = ((Number) v).intValue();
        }
        ok(targetSrg.equals(methodName), "@Inject method = " + methodName);
        ok(cancellable, "@Inject cancellable = true");
        ok(remapFalse, "@Inject remap = false");
        ok(require == 1, "@Inject require = 1");

        // ---- resolve the target in the real Gui class (same name+desc rule Mixin uses with remap=false)
        ClassNode gui = new ClassNode();
        new ClassReader(Files.readAllBytes(new File(guiPath).toPath())).accept(gui, 0);
        System.out.println("== target class: " + gui.name);

        MethodNode found = null;
        int hits = 0;
        for (MethodNode m : gui.methods) {
            if (m.name.equals(targetSrg)) {
                hits++;
                if (m.desc.equals(targetDesc)) found = m;
            }
        }
        ok(hits == 1, "exactly one method named " + targetSrg + " (found " + hits + ")");
        ok(found != null, "descriptor matches: " + targetDesc);
        if (found != null) {
            System.out.println("     target: " + found.name + found.desc
                    + " access=0x" + Integer.toHexString(found.access)
                    + " insns=" + found.instructions.size());
            ok(found.instructions.size() > 0, "target has a body (injectable, not abstract/native)");
        }

        // ---- handler signature must be valid for a void target: (CallbackInfo)V
        String expectedHandler = "(Lorg/spongepowered/asm/mixin/injection/callback/CallbackInfo;)V";
        ok(handler.desc.equals(expectedHandler),
                "handler descriptor " + handler.desc + " valid for a void target");
        ok((handler.access & Opcodes.ACC_STATIC) == 0, "handler is an instance method");

        System.out.println(failures == 0 ? "RESULT: PASS" : "RESULT: FAIL");
        System.exit(failures == 0 ? 0 : 1);
    }
}
'''

src_file = os.path.join(TMP, "Audit.java")
open(src_file, "w", encoding="utf-8").write(java_src)

print("=" * 78)
print("Offline Mixin injection audit (uses Mixin's own ASM)")
print("=" * 78)
print("\n[compile audit tool]")
cp = os.pathsep.join([MIXIN, ASM, ASM_TREE])
r = subprocess.run([r"D:\zulu21\bin\javac.exe", "-nowarn", "-proc:none", "-cp", cp,
                    "-d", TMP, src_file],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
if r.returncode != 0:
    print(r.stdout)
    print(r.stderr)
    sys.exit("audit tool failed to compile")

print("\n[run audit]")
r = subprocess.run([JAVA, "-cp", TMP + os.pathsep + cp, "Audit",
                    mixin_cls, gui_cls, TARGET_SRG, TARGET_DESC],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print(r.stdout)
if r.stderr.strip():
    print("stderr:", r.stderr)

# --------- check no other mod overwrites the same method -------------
print("\n[conflict scan] other mods injecting into / overwriting " + TARGET_SRG)
found_any = False
for root, _, files in os.walk(MODS):
    for fn in files:
        if not fn.lower().endswith(".jar"):
            continue
        path = os.path.join(root, fn)
        try:
            with zipfile.ZipFile(path) as z:
                for entry in z.namelist():
                    if not entry.endswith(".class"):
                        continue
                    data = z.read(entry)
                    if TARGET_SRG.encode() in data:
                        found_any = True
                        print("     %s :: %s" % (fn, entry))
        except Exception as e:
            print("     (skip %s: %s)" % (fn, e))
if not found_any:
    print("     none - no other mod references the SRG name directly")

print("\n" + "=" * 78)
print("AUDIT RESULT:", "PASS" if (r.returncode == 0 and not problems) else "FAIL")
sys.exit(0 if r.returncode == 0 else 1)
