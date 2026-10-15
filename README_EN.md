# NoSidebar · Hide the scoreboard sidebar

**中文** | [English](README_EN.md)

A **client-only Minecraft 1.20.1 / Forge** mod that stops the game from drawing the
**scoreboard sidebar** on the right side of the screen.

The server's death leaderboard — or anything else bound to the `sidebar` display slot —
simply disappears from *your* screen. Chat, the tab player list, the hotbar and boss bars
are **completely unaffected**.

> Why it exists: the vanilla sidebar can only be taken down by the server with
> `/scoreboard objectives setdisplay sidebar`, which affects **every player at once**.
> A player has no vanilla way to hide that panel just for themselves. This mod fills that
> gap — it only touches your local rendering, and the server never knows.

---

## Features

- Hides the scoreboard sidebar (`sidebar` display slot)
- Client-only: the server **does not need it and should not install it**
- Built-in toggle to restore vanilla behaviour
- Does not touch saves, sends no packets, does not alter scoreboard data

## Installation

1. Make sure you run **Forge 1.20.1** (compiled and verified against Forge `47.4.10`).
2. Drop `dist/nosidebar-1.0.2-forge-1.20.1.jar` into `.minecraft/versions/<your profile>/mods/`.
3. Restart the game (mods cannot be hot-loaded).

## Toggle

On first launch a `nosidebar.toml` is generated in that profile's `config` directory:

```toml
# true  = hide the sidebar (default)
# false = restore the vanilla sidebar
hideScoreboardSidebar = true
```

Set it to `false` and restart to get the vanilla panel back; deleting the file also means "hide".
Example path: `versions/xy/config/nosidebar.toml`.

## Uninstalling

Delete the jar. That's it — no save edits, no server changes, no leftovers.

## How it works

| Item | Detail |
| --- | --- |
| Injection target | `net.minecraft.client.gui.Gui#m_280030_`, i.e. the official `displayScoreboardSidebar(GuiGraphics, Objective)` |
| Descriptor | `(Lnet/minecraft/client/gui/GuiGraphics;Lnet/minecraft/world/scores/Objective;)V` |
| Injection | `@Inject(at = @At("HEAD"), cancellable = true)` → `ci.cancel()` |
| How the name was determined | Disassembled out of the very `client-1.20.1-20230612.114412-srg.jar` that Forge 47.4.10 loads at runtime, and confirmed **unique** in that class |
| Why no refmap | The mod uses the **SRG name with `remap = false`**, so no obfuscation mappings are needed — one less thing to break |
| Failure mode | `require = 1`: if the target method is missing, it fails loudly instead of silently doing nothing |

The core logic is a handful of lines — see
[`MixinGuiSidebar.java`](src/main/java/com/deepseek/nosidebar/mixin/MixinGuiSidebar.java).

### A pitfall worth recording

Version 1.0.0 set `nosidebar.mixins.json`'s `package` to `com.deepseek.nosidebar`, so Mixin
treated the **whole package** as a mixin package — and the `@Mod` entry class lived inside it.
FML then threw while loading the main class:

```
IllegalClassLoadError: com.deepseek.nosidebar.NoSidebarMod is in a defined
mixin package com.deepseek.nosidebar.* owned by nosidebar.mixins.json
and cannot be referenced directly
```

**Lesson: the mixin config `package` must point at a subpackage that contains only mixin
classes.** 1.0.1 moved the mixin into `com.deepseek.nosidebar.mixin`, and `verify_jar.py`
gained a structural regression check aimed specifically at this pattern.

## Building and verification

This project deliberately **does not use Gradle** — it is built directly with `javac` + `jar`
(see [`build.ps1`](build.ps1)), taking every dependency from the locally installed Forge
libraries. See [BUILDING.md](BUILDING.md).

```powershell
./build.ps1                  # produces build/nosidebar-1.0.2-forge-1.20.1.jar
python verify_jar.py         # jar structure / annotations / target method
python audit_injection.py    # injection audit using Mixin's own ASM
```

## Verification status (honest account)

| Item | Status |
| --- | --- |
| Jar structure / metadata / annotation values | ✅ automated check passes |
| Injection target exists and is unique in the real SRG jar | ✅ automated check passes |
| Injection audit with Mixin's own ASM | ✅ passes |
| **Sidebar confirmed gone in the real game** | ✅ confirmed by the decision-maker on an actual client |

The audit scripts prove that the *injection is wired correctly*; they are **not a substitute
for running the game**. Not every mod combination has been covered.

## Licensing and third parties

- Licensed under **MIT**, see [LICENSE](LICENSE).
- This project contains **no** Minecraft, Forge or third-party mod code. It only references one
  vanilla method name as a string inside a Mixin annotation.
- "Minecraft" is a trademark of Mojang Studios. This is an unofficial, unendorsed work, not
  affiliated with or endorsed by Mojang Studios, Microsoft or the Forge team.
- Built with AI — see [DISCLAIMER.md](DISCLAIMER.md) for the division of labour and disclaimers.
