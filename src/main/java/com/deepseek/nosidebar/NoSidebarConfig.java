package com.deepseek.nosidebar;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import net.minecraftforge.fml.loading.FMLPaths;

/**
 * 极简配置：读取 {@code config/nosidebar.toml} 里的隐藏模式。
 *
 * <pre>
 * # "always"  = 一直隐藏右侧计分板侧栏
 * # "screens" = 平时隐藏，打开背包/箱子等界面时显示   ← 默认（按需查看）
 * # "never"   = 从不隐藏（原版行为）
 * hideMode = "screens"
 * </pre>
 *
 * <p>兼容旧版配置：如果只有布尔键 {@code hideScoreboardSidebar}，
 * {@code true} 视为 {@code always}，{@code false} 视为 {@code never}。</p>
 *
 * <p>读取失败、文件不存在、值写错，一律按 {@code screens}（默认）处理，
 * 并且绝不抛异常到渲染线程。</p>
 *
 * <p>本类必须留在 mixin 包 <b>之外</b>（{@code com.deepseek.nosidebar}），
 * 否则会被 Mixin 当成 mixin 包内的普通类而拒绝加载。</p>
 */
public final class NoSidebarConfig {

    private static final String FILE_NAME = "nosidebar.toml";
    private static final String KEY_MODE = "hideMode";
    private static final String KEY_LEGACY = "hideScoreboardSidebar";

    /** 侧栏隐藏策略。 */
    public enum Mode {
        /** 一直隐藏。 */
        ALWAYS,
        /** 平时隐藏，打开容器界面（背包/箱子等）时显示。 */
        SCREENS,
        /** 从不隐藏（原版行为）。 */
        NEVER
    }

    private static volatile boolean resolved = false;
    private static volatile Mode mode = Mode.SCREENS;

    private NoSidebarConfig() {
    }

    /**
     * 本帧是否应该隐藏侧栏。
     *
     * <p>只剩"要不要画"这一个判断：{@code screens} 模式下打开背包等界面时返回 {@code false}，
     * 于是 Mixin 不取消原版渲染，侧栏就显示出来了。</p>
     */
    public static boolean shouldHideSidebar() {
        Mode m = currentMode();
        switch (m) {
            case ALWAYS:
                return true;
            case NEVER:
                return false;
            case SCREENS:
            default:
                return !ScreenState.isContainerScreenOpen();
        }
    }

    private static Mode currentMode() {
        if (!resolved) {
            synchronized (NoSidebarConfig.class) {
                if (!resolved) {
                    mode = load();
                    resolved = true;
                }
            }
        }
        return mode;
    }

    private static Mode load() {
        try {
            Path dir = FMLPaths.CONFIGDIR.get();
            if (dir == null) {
                return Mode.SCREENS;
            }
            Path file = dir.resolve(FILE_NAME);
            if (!Files.isRegularFile(file)) {
                writeDefault(file);
                return Mode.SCREENS;
            }
            List<String> lines = Files.readAllLines(file, StandardCharsets.UTF_8);
            String legacyValue = null;
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
                String v = cleanValue(line.substring(eq + 1));
                if (k.equalsIgnoreCase(KEY_MODE)) {
                    return parseMode(v);
                }
                if (k.equalsIgnoreCase(KEY_LEGACY)) {
                    legacyValue = v;
                }
            }
            if (legacyValue != null) {
                return parseLegacy(legacyValue);
            }
            return Mode.SCREENS;
        } catch (Throwable t) {
            return Mode.SCREENS;
        }
    }

    /** 去掉行内注释、引号与首尾空白。 */
    private static String cleanValue(String rawValue) {
        String v = rawValue;
        int hash = v.indexOf('#');
        if (hash >= 0) {
            v = v.substring(0, hash);
        }
        v = v.replace("\"", "").replace("'", "").trim();
        return v;
    }

    private static Mode parseMode(String v) {
        if (v.equalsIgnoreCase("always") || v.equalsIgnoreCase("hide") || v.equalsIgnoreCase("hidden")) {
            return Mode.ALWAYS;
        }
        if (v.equalsIgnoreCase("never") || v.equalsIgnoreCase("off") || v.equalsIgnoreCase("show")
                || v.equalsIgnoreCase("vanilla")) {
            return Mode.NEVER;
        }
        if (v.equalsIgnoreCase("screens") || v.equalsIgnoreCase("menus") || v.equalsIgnoreCase("on_demand")
                || v.equalsIgnoreCase("ondemand")) {
            return Mode.SCREENS;
        }
        return Mode.SCREENS; // 值无法识别 -> 默认按需查看
    }

    private static Mode parseLegacy(String v) {
        if (v.equalsIgnoreCase("false") || v.equals("0") || v.equalsIgnoreCase("off") || v.equalsIgnoreCase("no")) {
            return Mode.NEVER;
        }
        return Mode.ALWAYS;
    }

    private static void writeDefault(Path file) {
        String content = "# 魔女之泉 · 客户端计分板侧栏开关（由 NoSidebar 模组生成）\n"
                + "#\n"
                + "# hideMode 可选值：\n"
                + "#   \"always\"  = 一直隐藏右侧计分板侧栏\n"
                + "#   \"screens\" = 平时隐藏，打开背包/箱子等界面时显示（按需查看，默认）\n"
                + "#   \"never\"   = 从不隐藏，保持原版样子\n"
                + "#\n"
                + "# 改完保存，重启游戏生效。\n"
                + KEY_MODE + " = \"screens\"\n";
        try {
            Path parent = file.getParent();
            if (parent != null) {
                Files.createDirectories(parent);
            }
            Files.write(file, content.getBytes(StandardCharsets.UTF_8));
        } catch (IOException ignored) {
            // 写不了就算了，不影响默认行为
        }
    }
}
