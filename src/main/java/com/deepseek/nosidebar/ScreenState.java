package com.deepseek.nosidebar;

/**
 * 判断客户端当前是否打开了"可查看"的界面（背包、箱子、工作台等容器界面）。
 *
 * <p>用反射而不是直接引用，是为了让本 Mod 的源码编译时<b>完全不需要 Minecraft 类</b>
 * （编译期只用 javac + Mixin/FML 几个 jar，不反编译游戏）。方法名与字段名取自
 * Forge 47.4.10 运行期真实加载的 SRG jar，运行期不会被重映射：</p>
 *
 * <ul>
 *   <li>{@code net.minecraft.client.Minecraft#m_91087_} —— 即 {@code getInstance()}</li>
 *   <li>{@code net.minecraft.client.Minecraft#f_91080_} —— 即 {@code public Screen screen}</li>
 *   <li>{@code net.minecraft.client.gui.screens.inventory.AbstractContainerScreen} —— 容器界面基类（类名在运行期是官方名）</li>
 * </ul>
 *
 * <p>任何一步失败都返回 {@code false}（视为"没开界面"），从而退回隐藏侧栏的安全行为。</p>
 */
final class ScreenState {

    private static volatile boolean resolved = false;
    private static java.lang.reflect.Method getInstance;
    private static java.lang.reflect.Field screenField;
    private static Class<?> containerScreenClass;

    private ScreenState() {
    }

    /** 当前是否打开了背包 / 箱子 / 工作台这类容器界面。 */
    static boolean isContainerScreenOpen() {
        try {
            resolve();
            if (getInstance == null || screenField == null || containerScreenClass == null) {
                return false;
            }
            Object mc = getInstance.invoke(null);
            if (mc == null) {
                return false;
            }
            Object screen = screenField.get(mc);
            return screen != null && containerScreenClass.isInstance(screen);
        } catch (Throwable t) {
            return false;
        }
    }

    private static void resolve() {
        if (resolved) {
            return;
        }
        synchronized (ScreenState.class) {
            if (resolved) {
                return;
            }
            try {
                ClassLoader cl = ScreenState.class.getClassLoader();
                Class<?> mcClass = Class.forName("net.minecraft.client.Minecraft", false, cl);
                getInstance = mcClass.getMethod("m_91087_");
                screenField = mcClass.getField("f_91080_");
                containerScreenClass = Class.forName(
                        "net.minecraft.client.gui.screens.inventory.AbstractContainerScreen", false, cl);
            } catch (Throwable ignored) {
                // 保持 null，调用方按"未打开界面"处理
            }
            resolved = true;
        }
    }
}
