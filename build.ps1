# Build NoSidebar for Minecraft 1.20.1 / Forge 47.4.10.
# Target Java 17 via -source/-target (this Zulu build rejects single-dash -release).
# ASCII-only on purpose: Windows PowerShell 5.1 reads .ps1 as ANSI/GBK.
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$JAVA_HOME   = "D:\zulu21"
$FV          = "1.20.1-47.4.10"

# locate the .minecraft libraries dir.
# The pack folder name is non-ASCII ("归" = U+5F52); Windows PowerShell 5.1 reads this
# script as GBK, so the character is written as [char]0x5F52 to stay byte-safe.
$packDir = "D:\" + [char]0x6211 + [char]0x7684 + [char]0x4E16 + [char]0x754C + "\" + [char]0x9B54 + [char]0x5F52
$LibRoot = Join-Path $packDir ".minecraft\libraries"
if (-not (Test-Path (Join-Path $LibRoot "org\spongepowered\mixin\0.8.5\mixin-0.8.5.jar"))) {
    # fallback: search the filesystem for any valid libraries dir
    $LibRoot = $null
    $suffix = "\org\spongepowered\mixin\0.8.5\mixin-0.8.5.jar"
    $hits = Get-ChildItem -Path "D:\" -Recurse -Filter "mixin-0.8.5.jar" -ErrorAction SilentlyContinue -Force |
            Where-Object { $_.FullName -like "*$suffix" }
    foreach ($h in $hits) {
        $lib = $h.FullName.Substring(0, $h.FullName.Length - $suffix.Length)
        if (Test-Path (Join-Path $lib "net\minecraftforge\fmlloader\$FV\fmlloader-$FV.jar")) { $LibRoot = $lib; break }
    }
}
if (-not $LibRoot) { throw "libraries root not found" }
Write-Host "[libs] $LibRoot"

$CP_JARS = @(
    "$LibRoot\org\spongepowered\mixin\0.8.5\mixin-0.8.5.jar",
    "$LibRoot\net\minecraftforge\javafmllanguage\$FV\javafmllanguage-$FV.jar",
    "$LibRoot\net\minecraftforge\fmlloader\$FV\fmlloader-$FV.jar",
    "$LibRoot\net\minecraftforge\fmlcore\$FV\fmlcore-$FV.jar",
    "$LibRoot\net\minecraftforge\coremods\5.2.4\coremods-5.2.4.jar",
    "$LibRoot\net\minecraftforge\eventbus\6.0.5\eventbus-6.0.5.jar"
)
foreach ($p in $CP_JARS) { if (-not (Test-Path $p)) { throw "missing dependency: $p" } }
$CP = $CP_JARS -join ";"

$SrcDir   = Join-Path $ProjectRoot "src\main\java"
$ResDir   = Join-Path $ProjectRoot "src\main\resources"
$Manifest = Join-Path $ProjectRoot "src\main\MANIFEST.MF"
$BuildDir = Join-Path $ProjectRoot "build"
$ClassDir = Join-Path $BuildDir "classes"
$OutJar   = Join-Path $BuildDir "nosidebar-1.1.0-forge-1.20.1.jar"

if (Test-Path $ClassDir) { Remove-Item -Recurse -Force $ClassDir }
New-Item -ItemType Directory -Force -Path $ClassDir | Out-Null

$sources = Get-ChildItem -Path $SrcDir -Recurse -Filter *.java | ForEach-Object { $_.FullName }
if (-not $sources) { throw "no java sources" }
Write-Host "[1/4] javac: $($sources.Count) file(s)"

$javac = Join-Path $JAVA_HOME "bin\javac.exe"
& $javac -encoding UTF-8 -source 17 -target 17 -nowarn -proc:none -cp $CP -d $ClassDir $sources
if ($LASTEXITCODE -ne 0) { throw "javac failed (exit $LASTEXITCODE)" }

Write-Host "[2/4] copy resources"
Copy-Item -Path (Join-Path $ResDir "*") -Destination $ClassDir -Recurse -Force

Write-Host "[3/4] jar"
if (Test-Path $OutJar) { Remove-Item -Force $OutJar }
$jar = Join-Path $JAVA_HOME "bin\jar.exe"
& $jar --create --file $OutJar --manifest $Manifest -C $ClassDir .
if ($LASTEXITCODE -ne 0) { throw "jar failed (exit $LASTEXITCODE)" }

Write-Host "[4/4] done"
Get-Item $OutJar | Select-Object FullName, Length | Format-List
