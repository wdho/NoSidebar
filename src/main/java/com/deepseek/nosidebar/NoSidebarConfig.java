package com.deepseek.nosidebar;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import net.minecraftforge.fml.loading.FMLPaths;

/**
 * 极简配置：只读 {@code config/nosidebar.toml} 里的一个开关。
 *
 * <pre>
 * # true  = 隐藏右侧计分板侧栏（默认）
 * # false = 恢复原版显示
 * hideScoreboardSidebar = true
 * </pre>
 *
 * 读取失败、文件不存在、值写错，一律按 <b>隐藏</b> 处理（这是本 Mod 的目的），
 * 并且绝不抛异常到渲染线程。
 *
 * <p>本类必须留在 mixin 包 <b>之外</b>（{@code com.deepseek.nosidebar}），
 * 否则会被 Mixin 当成 mixin 包内的普通类而拒绝加载。</p>
 */
public final class NoSidebarConfig {

    private static final String FILE_NAME = "nosidebar.toml";
    private static final String KEY = "hideScoreboardSidebar";

    private static volatile boolean resolved = false;
    private static volatile boolean hidden = true;

    private NoSidebarConfig() {
    }

    public static boolean isSidebarHidden() {
        if (!resolved) {
            synchronized (NoSidebarConfig.class) {
                if (!resolved) {
                    hidden = load();
                    resolved = true;
                }
            }
        }
        return hidden;
    }

    private static boolean load() {
        try {
            Path dir = FMLPaths.CONFIGDIR.get();
            if (dir == null) {
                return true;
            }
            Path file = dir.resolve(FILE_NAME);
            if (!Files.isRegularFile(file)) {
                writeDefault(file);
                return true;
            }
            List<String> lines = Files.readAllLines(file, StandardCharsets.UTF_8);
            for (String raw : lines) {
                String line = raw.trim();
                if (line.isEmpty() || line.startsWith("#") || line.startsWith("[")) {
                    continue;
                }
                int eq = line.indexOf('=');
                if (eq <= 0) {
                    continue;
                }
                String k = line.substring(0, eq).trim();
                if (!k.equalsIgnoreCase(KEY)) {
                    continue;
                }
                String v = line.substring(eq + 1).trim();
                // 去掉可能的行内注释
                int hash = v.indexOf('#');
                if (hash >= 0) {
                    v = v.substring(0, hash).trim();
                }
                v = v.replace("\"", "").replace("'", "").trim();
                if (v.equalsIgnoreCase("false") || v.equals("0") || v.equalsIgnoreCase("off")
                        || v.equalsIgnoreCase("no")) {
                    return false;
                }
                if (v.equalsIgnoreCase("true") || v.equals("1") || v.equalsIgnoreCase("on")
                        || v.equalsIgnoreCase("yes")) {
                    return true;
                }
                return true; // 值无法识别 -> 按隐藏
            }
            return true; // 没有这个键 -> 按隐藏
        } catch (Throwable t) {
            return true;
        }
    }

    private static void writeDefault(Path file) {
        String content = "# 魔女之泉 · 客户端计分板侧栏开关（由 NoSidebar 模组生成）\n"
                + "# true  = 隐藏右侧计分板侧栏\n"
                + "# false = 恢复原版计分板侧栏\n"
                + "# 改完保存即可，下次启动游戏生效。\n"
                + KEY + " = true\n";
        try {
            Path parent = file.getParent();
            if (parent != null) {
                Files.createDirectories(parent);
            }
            Files.write(file, content.getBytes(StandardCharsets.UTF_8));
        } catch (IOException ignored) {
            // 写不了就算了，不影响隐藏功能本身
        }
    }
}
