# NoSidebar · 隐藏计分板侧栏

[English](README_EN.md) | **中文**

一个 **Minecraft 1.20.1 / Forge** 的纯客户端模组：不再绘制游戏右侧那条**计分板侧边栏**。

服务器上那条"死亡榜"（或任何挂在 sidebar 显示槽上的计分板）会从你屏幕上消失，
而聊天栏、Tab 玩家列表、物品栏、Boss 血条等其它 HUD **完全不受影响**。

> 为什么要做它：原版侧边栏只能由服务端用 `/scoreboard objectives setdisplay sidebar` 整条清掉，
> 而那会**对服务器上所有人一起生效**，玩家自己没有任何办法只隐藏自己屏幕上的那一栏。
> 这个模组补的正是这个缺口 —— 只改你本地渲染，服务端与其它玩家毫无感知。

---

## 功能

- 隐藏右侧计分板侧边栏（`sidebar` 显示槽）
- 纯客户端：**服务端不需要也不应该安装**
- 内置开关，可随时切回原版显示
- 不修改存档、不发送任何网络包、不改变计分板数据本身

## 安装

1. 确认你的游戏是 **Forge 1.20.1**（本模组针对 Forge `47.4.10` 编译验证）。
2. 把 `dist/nosidebar-1.0.2-forge-1.20.1.jar` 放进 `.minecraft/versions/<你的版本>/mods/`。
3. 重启游戏（模组不能热加载）。

## 开关

首次启动会在该版本的 `config` 目录生成 `nosidebar.toml`：

```toml
# true  = 隐藏右侧计分板侧栏（默认）
# false = 恢复原版计分板侧栏
hideScoreboardSidebar = true
```

改成 `false` 并重启即可恢复原版；删掉该文件同样按"隐藏"处理。
路径示例：`versions/xy/config/nosidebar.toml`。

## 卸载

删掉 jar 即可，完全恢复原版。本模组不写存档、不改服务端、不留任何残留。

## 工作原理

| 项目 | 内容 |
| --- | --- |
| 注入目标 | `net.minecraft.client.gui.Gui#m_280030_`，即官方名 `displayScoreboardSidebar(GuiGraphics, Objective)` |
| 描述符 | `(Lnet/minecraft/client/gui/GuiGraphics;Lnet/minecraft/world/scores/Objective;)V` |
| 注入方式 | `@Inject(at = @At("HEAD"), cancellable = true)`，命中即 `ci.cancel()` |
| 方法名怎么来的 | 直接从 Forge 47.4.10 运行期使用的 `client-1.20.1-20230612.114412-srg.jar` 中反汇编确认，且**全类唯一** |
| 为什么不用 refmap | 使用 **SRG 名 + `remap = false`**，不依赖混淆映射表，少一个出错环节，也不会因映射差异注入失败 |
| 失败时的行为 | `require = 1`：目标方法若不存在会明确报错，而不是静默失效 |

核心逻辑只有几行，见
[`MixinGuiSidebar.java`](src/main/java/com/deepseek/nosidebar/mixin/MixinGuiSidebar.java)。

### 一个值得记录的坑

模组 1.0.0 版把 `nosidebar.mixins.json` 的 `package` 写成了 `com.deepseek.nosidebar`，
于是 Mixin 把**整个包**都当成 mixin 包，而 `@Mod` 主类正好住在里面 —— FML 加载主类时直接抛：

```
IllegalClassLoadError: com.deepseek.nosidebar.NoSidebarMod is in a defined
mixin package com.deepseek.nosidebar.* owned by nosidebar.mixins.json
and cannot be referenced directly
```

**结论：mixin 配置里的 `package` 必须指向一个只放 mixin 类的专用子包。**
1.0.1 把 mixin 移入 `com.deepseek.nosidebar.mixin` 后修复，
并给 `verify_jar.py` 加了一条专门盯这个模式的结构回归检查。

## 构建与校验

本项目**不使用 Gradle**，直接 `javac` + `jar` 手搓（见
[`build.ps1`](build.ps1)），依赖全部取自本机已安装的 Forge 库。详见
[BUILDING.md](BUILDING.md)。

```powershell
./build.ps1                  # 产出 build/nosidebar-1.0.2-forge-1.20.1.jar
python verify_jar.py         # jar 结构 / 注解 / 目标方法 校验
python audit_injection.py    # 用 Mixin 自带 ASM 做注入装配审计
```

## 验证状态（如实说明）

| 项目 | 状态 |
| --- | --- |
| jar 结构 / 元数据 / 注解值 | ✅ 自动校验通过 |
| 注入目标在真实 SRG jar 中存在且唯一 | ✅ 自动校验通过 |
| 用 Mixin 自带 ASM 做的注入装配审计 | ✅ 通过 |
| **真实游戏内确认侧栏消失** | ✅ 由决策者在实际客户端确认 |

审计脚本只能证明"注入装配是正确的"，**不能替代真机测试**。本模组尚未覆盖所有模组组合。

## 许可与第三方

- 本项目采用 **MIT** 许可，见 [LICENSE](LICENSE)。
- 本项目**不包含** Minecraft、Forge 或任何第三方模组的代码，仅在 Mixin 注解中以字符串形式
  引用一个原版方法名。
- "Minecraft" 是 Mojang Studios 的商标。本项目是未获官方认可的非官方作品，与 Mojang Studios、
  Microsoft、Forge 团队均无隶属或背书关系。
- 本模组由 AI 构建，分工与免责条款见 [DISCLAIMER.md](DISCLAIMER.md)。
