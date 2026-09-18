# VisoMaster-Modern auto-installer (Windows / PowerShell)
#
# Usage (from the repo root):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
#   .\install.ps1 -SkipModels -SkipDeps     # only set up the Python environment
#   .\install.ps1 -Launch                   # start the app when done
#
# It will: locate/install Python 3.11, create .venv, install requirements_cu129.txt,
# download models, and fetch ffmpeg into dependencies/ if missing.

[CmdletBinding()]
param(
    [switch]$SkipModels,
    [switch]$SkipDeps,
    [switch]$Launch
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Write-Step($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "  [ok] $msg" -ForegroundColor Green }
function Write-Warn2($msg) { Write-Host "  [!] $msg" -ForegroundColor Yellow }

$VenvDir = Join-Path $Root ".venv"
$VenvPy = Join-Path $VenvDir "Scripts\python.exe"
$DepsDir = Join-Path $Root "dependencies"

# --- 1. Locate Python 3.11 -----------------------------------------------------
Write-Step "Locating Python 3.11"

$pythonCmd = $null
$candidates = @(
    @{ Exe = "py"; Args = @("-3.11") },
    @{ Exe = "python"; Args = @() },
    @{ Exe = (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"); Args = @() },
    @{ Exe = "C:\Python311\python.exe"; Args = @() }
)

foreach ($cand in $candidates) {
    if ($cand.Exe -match '\\' -and -not (Test-Path -LiteralPath $cand.Exe)) { continue }
    if (-not ($cand.Exe -match '\\') -and -not (Get-Command $cand.Exe -ErrorAction SilentlyContinue)) { continue }
    try {
        $ver = & $cand.Exe @($cand.Args) -c "import sys;print('%d.%d'%sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and $ver -eq "3.11") {
            $pythonCmd = $cand
            Write-Ok "found $($cand.Exe) $($cand.Args -join ' ')"
            break
        }
    } catch { }
}

if (-not $pythonCmd) {
    Write-Warn2 "Python 3.11 not found."
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "  Trying to install Python 3.11 via winget..."
        try {
            winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
        } catch {
            Write-Warn2 "winget install failed: $($_.Exception.Message)"
        }
        $installed = Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"
        if (Test-Path -LiteralPath $installed) {
            $pythonCmd = @{ Exe = $installed; Args = @() }
            Write-Ok "installed to $installed"
        }
    }
}

if (-not $pythonCmd) {
    throw "Python 3.11 is required. Install it from https://www.python.org/downloads/ (do NOT use 3.14), then re-run this script."
}

# --- 2. Create the virtual environment ----------------------------------------
Write-Step "Creating virtual environment (.venv)"
if (Test-Path -LiteralPath $VenvPy) {
    Write-Ok ".venv already exists"
} else {
    $exe = $pythonCmd.Exe
    $args = @($pythonCmd.Args) + @("-m", "venv", $VenvDir)
    & $exe @args
    if (-not (Test-Path -LiteralPath $VenvPy)) { throw "Failed to create .venv" }
    Write-Ok "created .venv"
}

# --- 3. Install dependencies ---------------------------------------------------
Write-Step "Installing Python dependencies (this downloads several GB)"
& $VenvPy -m pip install --upgrade pip wheel
& $VenvPy -m pip install -r (Join-Path $Root "requirements_cu129.txt") --default-timeout 120
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
Write-Ok "dependencies installed"

# --- 4. Download models --------------------------------------------------------
if ($SkipModels) {
    Write-Warn2 "skipping model download (-SkipModels)"
} else {
    Write-Step "Downloading models into model_assets/ (large)"
    & $VenvPy (Join-Path $Root "download_models.py")
    Write-Ok "models downloaded"
}

# --- 5. ffmpeg -----------------------------------------------------------------
if ($SkipDeps) {
    Write-Warn2 "skipping ffmpeg download (-SkipDeps)"
} else {
    Write-Step "Checking ffmpeg"
    $ffmpeg = Join-Path $DepsDir "ffmpeg.exe"
    if (Test-Path -LiteralPath $ffmpeg) {
        Write-Ok "dependencies\ffmpeg.exe already present"
    } else {
        New-Item -ItemType Directory -Path $DepsDir -Force | Out-Null
        $tmp = Join-Path $env:TEMP "visomaster_ffmpeg"
        $zip = Join-Path $tmp "ffmpeg.zip"
        Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
        New-Item -ItemType Directory -Path $tmp -Force | Out-Null
        try {
            Write-Host "  Downloading ffmpeg (essentials build)..."
            Invoke-WebRequest -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" -OutFile $zip -UseBasicParsing
            Expand-Archive -Path $zip -DestinationPath $tmp -Force
            $found = Get-ChildItem -Path $tmp -Recurse -Filter "ffmpeg.exe" | Select-Object -First 1
            if ($found) {
                Copy-Item -LiteralPath $found.FullName -Destination $ffmpeg -Force
                Write-Ok "fetched dependencies\ffmpeg.exe"
            } else {
                Write-Warn2 "ffmpeg.exe not found in the archive; recording will be unavailable."
            }
        } catch {
            Write-Warn2 "could not download ffmpeg ($($_.Exception.Message)). Recording will be unavailable; copy ffmpeg.exe into dependencies\\ manually."
        } finally {
            Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

# --- 6. Done -------------------------------------------------------------------
Write-Step "Done"
Write-Host "Start the app with:  .venv\Scripts\python.exe main.py   (or Start.bat)"
if ($Launch) {
    Write-Host "Launching..."
    & $VenvPy (Join-Path $Root "main.py")
}
