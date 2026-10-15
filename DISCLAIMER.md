# 免责声明 · AI 使用声明

# Disclaimer · AI Disclosure

---

## 中文

### ⚠️ 本模组由 AI 构建

**本项目 NoSidebar 的全部源代码、构建脚本与文档均由 AI（大语言模型编码代理）生成。**

| 项目 | 内容 |
| --- | --- |
| 生成工具 | DeepSeek Harness（模型：`deepseek-flash`） |
| 生成时间 | 2026 年 |
| 决策者 | **wdho** —— 提出需求、确定技术方向、选择目标环境、审核并决定最终产物 |

#### 具体分工

| 部分 | 由谁完成 |
| --- | --- |
| 全部 Java 源码（3 个文件，155 行） | **AI** |
| `nosidebar.mixins.json` / `mods.toml` / `pack.mcmeta` / `MANIFEST.MF` | **AI** |
| `build.ps1`（javac + jar 手工构建脚本） | **AI** |
| `verify_jar.py` / `audit_injection.py`（结构与注入校验脚本） | **AI** |
| `README.md` / `README_EN.md` / 本文件 | **AI** |
| 反汇编读取 SRG 方法名、字节码校验、注入装配审计、崩溃日志分析 | **AI 执行**，决策者确认结论 |
| 需求定义、目标版本选择、"做成模组"这一方案取舍 | **决策者** |
| **真机启动验证**（确认侧栏确实消失） | **决策者** |

#### 这意味着什么

- AI 生成的代码**可能包含错误、遗漏或与文档不符之处**。
- 在把它用到正式客户端 / 服务器之前，**请自行阅读并理解代码**。核心逻辑只有几行，见
  [`MixinGuiSidebar.java`](src/main/java/com/deepseek/nosidebar/mixin/MixinGuiSidebar.java)。
- AI 生成的代码**不附带任何质量保证**。
- 本项目确实经过验证（结构校验、注入装配审计，以及决策者在真实客户端上确认功能生效），
  但**验证只能说明被测的那一种情形可用**，不代表所有环境、所有模组组合下都没有问题。
- 本项目在开发过程中**真实导致过一次游戏启动崩溃**（1.0.0 版的 mixin 包边界问题，
  详见 README 的"一个值得记录的坑"）。该问题已修复，但它说明未经真机测试的产物是有风险的。

### 这个模组做什么

它让**你自己的客户端**不再绘制原版计分板侧边栏（也就是服务端常挂在右侧的"死亡榜"等榜单）。
实现方式是给 `Gui#displayScoreboardSidebar` 注入一个 `ci.cancel()`，可在配置里关闭。

它**只影响本地渲染**：不改计分板数据、不改服务端、不影响其它玩家、不发送任何网络包。

### 第三方与许可

- 本项目**不包含** Minecraft、Forge 或任何第三方模组的代码，仅在 Mixin 注解中以字符串形式
  引用一个原版方法名（SRG 名 `m_280030_`）。
- Minecraft 版权归 **Mojang Studios** 所有，"Minecraft" 是其商标。本项目是未获官方认可的非官方作品。
- 本项目与 Mojang Studios、Microsoft、Forge 团队、以及任何整合包作者**没有任何隶属或背书关系**。
- 请遵守你所使用整合包与服务端的规则；本模组会隐藏服务端展示的榜单，**服务器管理员应当知情**。

### 免责条款

本软件按「现状」提供，不附带任何明示或暗示的担保，包括但不限于对适销性、特定用途适用性及非侵权性的担保。
在任何情况下，作者或贡献者均不对因本软件或本软件的使用或其他交易而产生的任何索赔、损害或其他责任负责，
无论是在合同诉讼、侵权行为还是其他方面。

### 安全提示

1. **务必备份**你的整合包目录与存档再安装。
2. 本模组隐藏的是服务端下发的计分板显示，**不会**改变数据本身，也**不会**绕过任何权限 ——
   它只是"不看"，不是"不存在"。
3. 若安装后游戏无法启动，**直接删除该 jar 即可完全恢复**，无任何残留。
   排错时看 `logs/latest.log` 里是否出现 `MixinGuiSidebar` 相关行。
4. 本模组通过 Mixin 修改原版渲染流程。若未来 Forge / Minecraft 版本变更导致该方法名改变，
   本模组会**明确报错**（`require = 1`）而不是静默失效；此模组仅针对 **1.20.1 / Forge 47.x** 编译。

---

## English

### ⚠️ This mod was built with AI

**Every line of source code, build script and documentation in this project (NoSidebar) was generated
by AI (a large language model coding agent).**

| Item | Detail |
| --- | --- |
| Tool | DeepSeek Harness (model: `deepseek-flash`) |
| Year | 2026 |
| Decision-maker | **wdho** — set the requirements, chose the technical approach and target environment, reviewed and decided the final artefacts |

#### Who did what

| Part | Author |
| --- | --- |
| All Java source (3 files, 155 lines) | **AI** |
| `nosidebar.mixins.json` / `mods.toml` / `pack.mcmeta` / `MANIFEST.MF` | **AI** |
| `build.ps1` (hand-rolled javac + jar build script) | **AI** |
| `verify_jar.py` / `audit_injection.py` (structure and injection checks) | **AI** |
| `README.md` / `README_EN.md` and this file | **AI** |
| Disassembling the SRG method name, bytecode checks, injection audit, crash-log analysis | **performed by AI**, conclusions confirmed by the decision-maker |
| Requirements, target version, the decision to build a mod at all | **Decision-maker** |
| **In-game verification** (confirming the sidebar is really gone) | **Decision-maker** |

#### What this means for you

- AI-generated code **may contain bugs, omissions, or claims that do not match the code**.
- **Read and understand the code yourself** before using it on a real client or server. The core logic is
  a few lines — see [`MixinGuiSidebar.java`](src/main/java/com/deepseek/nosidebar/mixin/MixinGuiSidebar.java).
- AI-generated code comes with **no quality guarantee whatsoever**.
- The project has been verified (structure checks, an injection audit, and the decision-maker confirming it
  works in the real client), but **verification only covers the scenarios that were tested** — not every
  environment or mod combination.
- During development this project **did cause a real game startup crash** (the 1.0.0 mixin package-boundary
  bug, described in the README). It is fixed, but it shows that untested artefacts carry risk.

### What this mod does

It stops **your own client** from drawing the vanilla scoreboard sidebar (the "death leaderboard" servers
often display on the right). It does so by injecting a `ci.cancel()` into `Gui#displayScoreboardSidebar`;
this can be turned off in the config.

It **only affects local rendering**: no scoreboard data is changed, no server changes, no effect on other
players, and no packets are sent.

### Third parties and licensing

- This project contains **no** Minecraft, Forge or third-party mod code. It only references one vanilla
  method name (the SRG name `m_280030_`) as a string inside a Mixin annotation.
- Minecraft is copyright **Mojang Studios**; "Minecraft" is their trademark. This is an unofficial,
  unendorsed work.
- This project is **not affiliated with or endorsed by** Mojang Studios, Microsoft, the Forge team, or any
  modpack author.
- Respect the rules of the modpack and server you play on: this mod hides a panel the server chose to show,
  so **server administrators should be aware of it**.

### Disclaimer of warranty

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### Safety notes

1. **Back up** your modpack directory and saves before installing.
2. This mod hides a server-provided scoreboard display. It does **not** change the data and does **not**
   bypass any permission — it is "not looking", not "not existing".
3. If the game fails to start after installing, **simply delete the jar** and everything is back to vanilla,
   with no leftovers. For troubleshooting, look for `MixinGuiSidebar` lines in `logs/latest.log`.
4. This mod alters vanilla rendering through Mixin. If a future Forge / Minecraft version changes that method
   name, the mod **fails loudly** (`require = 1`) rather than silently doing nothing. It is compiled for
   **1.20.1 / Forge 47.x** only.
