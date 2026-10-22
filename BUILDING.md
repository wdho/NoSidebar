# 构建与校验 · Building & Verification

[English](#english) | **中文**

---

## 中文

### 为什么不用 Gradle

常见的 Forge 模组用 ForgeGradle 构建，但那需要联网下载 Forge 的 userdev 产物、反编译整个 Minecraft
并跑完整条 MDK 管线，在离线环境下代价很高。本项目只依赖**编译期存在的少量 API**，于是选择直接
`javac` + `jar` 手工构建：依赖全部取自本机已安装好的 Forge 库，**不联网、不反编译、几秒出包**。

代价是：脚本依赖本机环境（见下），不像 Gradle 那样开箱可移植。

### 环境要求

| 项目 | 本机验证值 | 说明 |
| --- | --- | --- |
| JDK | Zulu 21（`D:\zulu21`） | 用 `-source 17 -target 17` 产出 Java 17 字节码，与 1.20.1 一致 |
| Forge | `47.4.10`（MC 1.20.1） | 编译期只需要它的几个 FML 类 |
| libraries 目录 | `<整合包>\.minecraft\libraries` | 脚本会自动定位 |

> 注：本机这个 Zulu 构建会把 `-release` 报成"非法标记"，因此脚本改用等价的
> `-source 17 -target 17`。

### 编译期依赖（全部来自 libraries）

| Jar | 用途 |
| --- | --- |
| `org/spongepowered/mixin/0.8.5/mixin-0.8.5.jar` | `@Mixin` / `@Inject` / `@At` / `CallbackInfo` |
| `net/minecraftforge/javafmllanguage/<ver>/...` | `net.minecraftforge.fml.common.Mod` |
| `net/minecraftforge/fmlloader/<ver>/...` | `net.minecraftforge.fml.loading.FMLPaths` |
| `net/minecraftforge/fmlcore/<ver>/...` | FML 相关 |
| `net/minecraftforge/coremods/5.2.4/...` | Forge coremod API |
| `net/minecraftforge/eventbus/6.0.5/...` | 事件总线 |

**注意：编译期完全不需要 Minecraft 本身。** 因为 Mixin 的目标类只用字符串
（`@Mixin(targets = "...")`）和方法名引用，源码里没有任何 `import net.minecraft.*`。
这也是它不需要 refmap 的原因。

### 构建

```powershell
./build.ps1
```

脚本做四件事：

1. 定位 `.minecraft\libraries`（先按包名硬编码尝试，失败则全盘搜索 `mixin-0.8.5.jar`）
2. `javac -encoding UTF-8 -source 17 -target 17 -nowarn -proc:none -cp <6 个 jar> -d build\classes <源码>`
3. 把 `src\main\resources` 拷进 classes 目录
4. `jar --create --file build\nosidebar-<版本>-forge-1.20.1.jar --manifest src\main\MANIFEST.MF -C build\classes .`

产物：`build/nosidebar-1.1.0-forge-1.20.1.jar`

**发布时**需要手动把它复制到 `dist/`（`build/` 已被 `.gitignore` 忽略，`dist/` 会被提交）。

### 校验

```powershell
$env:PYTHONIOENCODING = "utf-8"   # 控制台是 GBK，不设这个中文输出会乱码
python verify_jar.py
python audit_injection.py
```

`verify_jar.py` 检查：

- jar 条目、`MANIFEST.MF` 的 `MixinConfigs`、mixin 配置、`mods.toml`
- **mixin 包内只有 mixin 类**（1.0.1 崩溃的回归守卫）
- 编译后注解常量池里确实有 `@Mixin` / `@Inject` / 目标类名 / SRG 名
- 用 `javap` 交叉验证注解参数（`targets` / `method` / `at` / `cancellable` / `require` / `remap`）
- 目标方法在真实 SRG jar 中**存在且唯一**，签名匹配
- **反射用的 API 名在 SRG jar 中确实存在**：`Minecraft.m_91087_()`、字段 `f_91080_`、
  `AbstractContainerScreen` 类（这是 1.1.0 "按需查看"的依赖）

`audit_injection.py` 检查：

- 用 **Mixin 自带的 ASM** 读取编译后的注解（和 Mixin 运行期看到的一致）
- 按 `remap = false` 的规则在真实 `Gui` 类里解析注入点
- 校验 handler 签名对 void 目标是合法的
- 扫描其它模组是否也引用了同一个 SRG 名（潜在冲突）

**这两个脚本证明的是"装配正确"，不能替代真机测试。**

### 手工验证注入是否生效

启动游戏后看 `logs/latest.log`：

```
Mixing MixinGuiSidebar from nosidebar.mixins.json into net.minecraft.client.gui.Gui
```

有这行 = 注入成功。出现 `MixinApplyError` / `InjectionError` = 注入失败（删 jar 即可恢复）。

### 换机器 / 换整合包

`build.ps1` 里的 `$JAVA_HOME` 和 `$FV`（Forge 版本）是两个需要按环境修改的值；
libraries 目录会自动定位。如果目标环境的 Forge 版本不同，**必须重新确认 SRG 方法名**：
用 `javap` 从该环境运行期的 `client-*-srg.jar` 里反汇编 `net/minecraft/client/gui/Gui`，
找到入参为 `(GuiGraphics, Objective)` 的那个方法，取其 `m_xxxxxx_` 名字替换
`MixinGuiSidebar.java` 中的 `method` 值。

---

## English

### Why not Gradle

Forge mods normally build with ForgeGradle, which downloads Forge's userdev artefacts, decompiles all of
Minecraft and runs the full MDK pipeline — expensive and network-bound. This project only needs a handful of
compile-time APIs, so it is built directly with `javac` + `jar`: every dependency is taken from the locally
installed Forge libraries. **No network, no decompilation, a few seconds per build.**

The trade-off: the script depends on the local environment (below) instead of being portable out of the box.

### Requirements

| Item | Verified value here | Notes |
| --- | --- | --- |
| JDK | Zulu 21 (`D:\zulu21`) | Emits Java 17 bytecode via `-source 17 -target 17`, matching 1.20.1 |
| Forge | `47.4.10` (MC 1.20.1) | Only a few FML classes are needed at compile time |
| libraries dir | `<modpack>\.minecraft\libraries` | Located automatically by the script |

> Note: this particular Zulu build rejects `-release` as an invalid flag, hence the equivalent
> `-source 17 -target 17`.

### Compile-time dependencies (all from libraries)

| Jar | Used for |
| --- | --- |
| `org/spongepowered/mixin/0.8.5/mixin-0.8.5.jar` | `@Mixin` / `@Inject` / `@At` / `CallbackInfo` |
| `net/minecraftforge/javafmllanguage/<ver>/...` | `net.minecraftforge.fml.common.Mod` |
| `net/minecraftforge/fmlloader/<ver>/...` | `net.minecraftforge.fml.loading.FMLPaths` |
| `net/minecraftforge/fmlcore/<ver>/...` | FML |
| `net/minecraftforge/coremods/5.2.4/...` | Forge coremod API |
| `net/minecraftforge/eventbus/6.0.5/...` | event bus |

**Minecraft itself is not needed to compile.** The Mixin target is referenced purely as a string
(`@Mixin(targets = "...")`), and no source file imports `net.minecraft.*`. That is also why no refmap is
required.

### Build

```powershell
./build.ps1
```

The script (1) locates `.minecraft\libraries`, (2) runs `javac`, (3) copies `src\main\resources` into the
classes dir, and (4) packs the jar with `src\main\MANIFEST.MF`.

Output: `build/nosidebar-1.1.0-forge-1.20.1.jar`. For a release, copy it into `dist/` manually
(`build/` is git-ignored, `dist/` is committed).

### Verification

```powershell
$env:PYTHONIOENCODING = "utf-8"   # console is GBK here; without this, Chinese output is mangled
python verify_jar.py
python audit_injection.py
```

`verify_jar.py` checks the jar entries, the `MixinConfigs` manifest attribute, the mixin config, `mods.toml`,
that the **mixin package contains only mixin classes** (the 1.0.1 crash regression guard), the compiled
annotation constants, the annotation arguments via `javap`, that the target method exists uniquely with
a matching signature in the real SRG jar, and that the **reflected API names** exist there too
(`Minecraft.m_91087_()`, field `f_91080_`, `AbstractContainerScreen` — required by the 1.1.0 on-demand mode).

`audit_injection.py` reads the compiled annotations with **Mixin's own ASM** (exactly what Mixin sees at
runtime), resolves the injection point in the real `Gui` class under `remap = false` rules, validates the
handler signature for a void target, and scans for other mods referencing the same SRG name.

**These scripts prove the wiring is correct; they are not a substitute for running the game.**

### Verifying in game

After launching, look in `logs/latest.log` for:

```
Mixing MixinGuiSidebar from nosidebar.mixins.json into net.minecraft.client.gui.Gui
```

Present = the injection applied. `MixinApplyError` / `InjectionError` = it failed (delete the jar to recover).

### Porting to another machine / modpack

`$JAVA_HOME` and `$FV` (Forge version) in `build.ps1` are the two environment-specific values; the libraries
directory is discovered automatically. If the target Forge version differs you **must re-confirm the SRG
method name**: run `javap` on `net/minecraft/client/gui/Gui` from that environment's `client-*-srg.jar`, find
the method taking `(GuiGraphics, Objective)`, and replace the `method` value in `MixinGuiSidebar.java`.
