package com.deepseek.nosidebar;

import net.minecraftforge.fml.common.Mod;

/**
 * 魔女之泉 · 客户端计分板侧栏隐藏（NoSidebar）。
 *
 * <p>纯客户端 Mod：不添加任何物品/方块/网络包，只通过 Mixin 取消本地侧边栏渲染。
 * 装在客户端即可，服务端不需要也不应该装。</p>
 */
@Mod(NoSidebarMod.MODID)
public class NoSidebarMod {

    public static final String MODID = "nosidebar";

    public NoSidebarMod() {
        // 什么都不做：隐藏逻辑全在 Mixin，这里只是让 Forge 正常识别并加载这个 Mod。
        // 副作用是它能出现在 Mod 列表里，方便你确认装上了。
    }
}
