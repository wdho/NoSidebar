# -*- coding: utf-8 -*-
"""Verify the built NoSidebar jar.

Robust on purpose: it scans the compiled class constant pool for the annotation
strings and cross-checks the injection target with javap against the real Forge
SRG client jar, instead of hand-decoding the whole class-file layout.
"""
import json
import os
import re
import struct
import subprocess
import sys
import zipfile

JAR = r"D:\我的世界\deepseek1区\build\nosidebar-1.0.2-forge-1.20.1.jar"
LIB = r"D:\我的世界\魔归\.minecraft\libraries"
SRG = os.path.join(LIB, r"net\minecraft\client\1.20.1-20230612.114412\client-1.20.1-20230612.114412-srg.jar")
JAVAP = r"D:\zulu21\bin\javap.exe"
TMP = r"C:\Users\li\AppData\Local\Temp\nosidebar-verify"

problems = []


def check(cond, msg):
    print(("     [OK]   " if cond else "     [FAIL] ") + msg)
    if not cond:
        problems.append(msg)


def cp_strings(data):
    """Return every Utf8 constant in a class file (constant pool only)."""
    assert data[:4] == b"\xca\xfe\xba\xbe", "not a class file"
    count = struct.unpack_from(">H", data, 8)[0]
    pos = 10
    out = []
    i = 1
    while i < count:
        tag = data[pos]
        pos += 1
        if tag == 1:
            ln = struct.unpack_from(">H", data, pos)[0]
            pos += 2
            out.append(data[pos:pos + ln].decode("utf-8", "replace"))
            pos += ln
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            pos += 4
        elif tag in (5, 6):
            pos += 8
            i += 1
        elif tag in (7, 8, 16, 19, 20):
            pos += 2
        elif tag == 15:
            pos += 3
        else:
            raise ValueError("bad constant pool tag %d at index %d" % (tag, i))
        i += 1
    return out


print("=" * 78)
print("NoSidebar jar verification")
print("=" * 78)

print("\n[1] archive entries")
with zipfile.ZipFile(JAR) as z:
    names = z.namelist()
    for n in sorted(names):
        print("     " + n)
    for need in ("com/deepseek/nosidebar/mixin/MixinGuiSidebar.class",
                 "com/deepseek/nosidebar/NoSidebarConfig.class",
                 "com/deepseek/nosidebar/NoSidebarMod.class",
                 "nosidebar.mixins.json", "META-INF/mods.toml", "META-INF/MANIFEST.MF"):
        check(need in names, "entry present: %s" % need)

    # regression guard for the crash of 2026-10-16: the mixin package must not contain
    # any non-mixin class, otherwise FML throws IllegalClassLoadError when loading the mod.
    print("\n[1b] mixin package contents (crash regression guard)")
    pkg_prefix = "com/deepseek/nosidebar/mixin/"
    pkg_classes = sorted(n for n in names if n.startswith(pkg_prefix) and n.endswith(".class"))
    for n in pkg_classes:
        print("     " + n)
    check(pkg_classes == ["com/deepseek/nosidebar/mixin/MixinGuiSidebar.class"],
          "mixin package holds exactly the one mixin class (no mod entry / config classes)")
    mod_prefix = "com/deepseek/nosidebar/"
    strays = [n for n in names
              if n.startswith(mod_prefix) and not n.startswith(pkg_prefix)
              and n.endswith(".class")]
    print("     outside mixin package: " + ", ".join(sorted(strays)))
    check(len(strays) == 2, "mod entry + config classes live outside the mixin package")

print("\n[2] manifest")
with zipfile.ZipFile(JAR) as z:
    mf = z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace")
print("     " + mf.replace("\r\n", "\n").replace("\n ", "").replace("\n", "\n     ").strip())
check("MixinConfigs: nosidebar.mixins.json" in mf, "MixinConfigs attribute points at the mixin config")

print("\n[3] mixin config")
with zipfile.ZipFile(JAR) as z:
    cfg = json.loads(z.read("nosidebar.mixins.json").decode("utf-8"))
print("     " + json.dumps(cfg, ensure_ascii=False))
check(cfg.get("package") == "com.deepseek.nosidebar.mixin", "mixin package == com.deepseek.nosidebar.mixin")
check(cfg.get("client") == ["MixinGuiSidebar"], "mixin declared in the client list")
check("refmap" not in cfg, "no refmap required (SRG names used directly)")

print("\n[4] mods.toml")
with zipfile.ZipFile(JAR) as z:
    toml = z.read("META-INF/mods.toml").decode("utf-8")
check('modLoader="javafml"' in toml, "modLoader is javafml (Forge)")
check('modId="nosidebar"' in toml, "modId declared")
check('versionRange="[1.20.1,1.20.2)"' in toml, "constrains minecraft 1.20.1")

print("\n[5] compiled mixin annotations (constant pool)")
with zipfile.ZipFile(JAR) as z:
    cls = z.read("com/deepseek/nosidebar/mixin/MixinGuiSidebar.class")
    z.extract("com/deepseek/nosidebar/mixin/MixinGuiSidebar.class", TMP)
strs = cp_strings(cls)
# annotation types are stored as type descriptors (L...;), so match on the descriptor form
for want in ("Lorg/spongepowered/asm/mixin/Mixin;",
             "Lorg/spongepowered/asm/mixin/injection/Inject;",
             "net.minecraft.client.gui.Gui",
             "m_280030_",
             "HEAD"):
    check(want in strs, "class references %s" % want)

print("\n[6] javap cross-check on the shipped class")
out = subprocess.run([JAVAP, "-v", "-p", "-classpath", TMP,
                      "com.deepseek.nosidebar.mixin.MixinGuiSidebar"],
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
txt = out.stdout
for pat, label in (
        (r'targets=\["net\.minecraft\.client\.gui\.Gui"\]', "@Mixin targets Gui"),
        (r'method=\["m_280030_"\]', "@Inject targets m_280030_"),
        (r'value="HEAD"', "@Inject at HEAD"),
        (r'cancellable=true', "@Inject cancellable"),
        (r'require=1', "@Inject require=1"),
        (r'remap=false', "remap=false (no refmap needed)"),
):
    check(re.search(pat, txt) is not None, "javap shows " + label)

print("\n[7] injection target exists in Forge 47.4.10 SRG jar")
os.makedirs(os.path.join(TMP, "srg", "net", "minecraft", "client", "gui"), exist_ok=True)
with zipfile.ZipFile(SRG) as z:
    open(os.path.join(TMP, "srg", "net", "minecraft", "client", "gui", "Gui.class"), "wb").write(
        z.read("net/minecraft/client/gui/Gui.class"))
out2 = subprocess.run([JAVAP, "-p", "-classpath", os.path.join(TMP, "srg"),
                       "net.minecraft.client.gui.Gui"],
                      capture_output=True, text=True, encoding="utf-8", errors="replace")
hits = [l.strip() for l in out2.stdout.splitlines() if "m_280030_" in l]
for h in hits:
    print("     " + h)
check(len(hits) == 1, "exactly one method named m_280030_")
check(any("(net.minecraft.client.gui.GuiGraphics, net.minecraft.world.scores.Objective)" in h
          for h in hits), "signature matches displayScoreboardSidebar")

print("\n" + "=" * 78)
if problems:
    print("RESULT: FAIL (%d)" % len(problems))
    for p in problems:
        print("  - " + p)
    sys.exit(1)
print("RESULT: PASS")
