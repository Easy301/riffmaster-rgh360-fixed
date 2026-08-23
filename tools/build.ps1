<#
    build.ps1 - build riffmaster.xex from source.

        powershell -ExecutionPolicy Bypass -File tools\build.ps1

    Three steps, all of which are required for a plugin that will actually load on a
    RETAIL RGH console from Hdd:\ :

      1. msbuild, using the .NET Framework v4.0 MSBuild. The Xbox 360 platform toolset
         installs under "C:\Program Files (x86)\MSBuild\Microsoft.Cpp\v4.0\Platforms\
         Xbox 360", which modern MSBuild (VS2019/2022) cannot consume - so the v4.0
         MSBuild is not a preference, it is the only one that works.

      2. xextool -r a -m r. Raw XDK output is marked DEVKIT with "Allowed Media: System
         Flash" and will silently refuse to load from the HDD. This flips it to retail
         and clears the media restriction. The .vcxproj has a post-build event that
         would do this, but it ships disabled and points at a path that does not exist.

      3. Verify. The build is rejected unless xextool reports both "Retail" and
         "All Media Types", so a plugin that cannot load is never produced quietly.

    Parameters
      -Out <path>   where to write the finished xex (default: bin\riffmaster.xex)
      -Clean        full rebuild
#>
param(
    [string]$Out = "",
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$sln  = Join-Path $root "src\riffmaster.sln"
$built = Join-Path $root "src\riffmaster\Release Retail\riffmaster.xex"
if (-not $Out) { $Out = Join-Path $root "bin\riffmaster.xex" }

# xextool: shipped in XeXGUI, Velocity, and most 360 homebrew toolkits. Point XEXTOOL at
# it if it is not on PATH or next to this script.
$xextool = $env:XEXTOOL
if (-not $xextool) {
    $c = Join-Path $PSScriptRoot "xextool.exe"
    if (Test-Path $c) { $xextool = (Resolve-Path $c).Path }
}
if (-not $xextool) {
    $cmd = Get-Command xextool.exe -ErrorAction SilentlyContinue
    if ($cmd) { $xextool = $cmd.Source }
}

$msbuild = "C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe"
if (-not (Test-Path $msbuild)) { throw "MSBuild v4.0 not found at $msbuild" }
if (-not (Test-Path $sln))     { throw "Solution not found: $sln" }
if (-not $xextool) {
    throw "xextool.exe not found. Put it in tools\, or set the XEXTOOL environment variable. See docs/BUILDING.md."
}

# The XDK's targets read %XEDK%. The installer sets it at machine scope, but it is not
# always present in a non-login shell.
if (-not $env:XEDK) {
    $env:XEDK = [Environment]::GetEnvironmentVariable("XEDK", "Machine")
    if (-not $env:XEDK) {
        throw "XEDK is not set - the Xbox 360 SDK does not appear to be installed. See docs/BUILDING.md."
    }
}

$targets = if ($Clean) { "/t:Rebuild" } else { "/t:Build" }
Write-Host "[1/3] msbuild $targets ..." -ForegroundColor Cyan
& $msbuild $sln /p:Configuration="Release Retail" /p:Platform="Xbox 360" $targets /v:minimal /nologo
if ($LASTEXITCODE -ne 0) { throw "Build failed (exit $LASTEXITCODE)" }
if (-not (Test-Path $built)) { throw "Build reported success but $built is missing" }

Write-Host "[2/3] xextool -r a -m r (force retail, clear media restriction) ..." -ForegroundColor Cyan
& $xextool -r a -m r $built | Out-Null
if ($LASTEXITCODE -ne 0) { throw "xextool failed (exit $LASTEXITCODE)" }

# NB: on an array, -match returns matching ELEMENTS, not a boolean. Count instead.
$info     = & $xextool -l $built
$isRetail = @($info | Where-Object { $_ -match '^\s*Retail\s*$' }).Count -gt 0
$allMedia = @($info | Where-Object { $_ -match 'All Media Types' }).Count -gt 0
if (-not $isRetail -or -not $allMedia) {
    $info | Write-Host
    throw "Post-processing check failed (Retail=$isRetail, AllMedia=$allMedia) - refusing to ship a xex that will not load."
}
Write-Host "      verified: Retail + All Media Types" -ForegroundColor DarkGray

Write-Host "[3/3] -> $Out" -ForegroundColor Cyan
$outDir = Split-Path -Parent $Out
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
Copy-Item $built $Out -Force

$size = (Get-Item $Out).Length
$md5  = (Get-FileHash $Out -Algorithm MD5).Hash
Write-Host ""
Write-Host ("DONE  {0}  ({1:N0} bytes, MD5 {2})" -f $Out, $size, $md5) -ForegroundColor Green
Write-Host "Copy it to Hdd:\ and add a pluginN line to launch.ini - see docs/INSTALL.md."
