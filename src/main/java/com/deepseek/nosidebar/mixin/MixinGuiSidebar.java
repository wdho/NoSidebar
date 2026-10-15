package com.deepseek.nosidebar.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import com.deepseek.nosidebar.NoSidebarConfig;

/**
 * 客户端隐藏右侧计分板侧边栏。
 *
 * <p>目标方法：{@code net.minecraft.client.gui.Gui#m_280030_}，
 * 即官方名 {@code displayScoreboardSidebar(GuiGraphics, Objective)}。
 * 该方法在 Forge 47.4.10 运行期的 SRG jar 中确认存在且唯一（描述符
 * {@code (Lnet/minecraft/client/gui/GuiGraphics;Lnet/minecraft/world/scores/Objective;)V}）。</p>
 *
 * <p>刻意使用 <b>SRG 名</b> + {@code remap = false}，因此不需要 refmap，
 * 也不会因混淆映射差异而注入失败。取消注入只影响本地渲染，纯客户端行为。</p>
 *
 * <p>注意：本类必须待在 mixin 专用子包（{@code ...nosidebar.mixin}）里。
 * 一旦 mixin 配置的 package 覆盖到 {@code NoSidebarMod}，FML 加载主类时就会抛
 * {@code IllegalClassLoadError: ... is in a defined mixin package ...}。</p>
 */
@Mixin(targets = "net.minecraft.client.gui.Gui", priority = 500, remap = false)
public class MixinGuiSidebar {

    /** 只在方法开头注入；侧栏要不要画完全由这里决定，方法体原样保留。 */
    @Inject(method = "m_280030_", at = @At("HEAD"), cancellable = true, require = 1, remap = false)
    private void nosidebar$cancelSidebarRendering(CallbackInfo ci) {
        try {
            if (NoSidebarConfig.isSidebarHidden()) {
                ci.cancel();
            }
        } catch (Throwable ignored) {
            // 配置读取出任何问题都不应该影响游戏：静默放行，保持原版行为。
        }
    }
}
