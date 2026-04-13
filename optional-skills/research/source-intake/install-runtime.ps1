[CmdletBinding()]
param(
    [string]$InstallRoot,
    [string]$SkillName = "source-intake",
    [switch]$FromGitHub,
    [switch]$SkipSkill,
    [switch]$SkipRuntime,
    [string]$GitHubOwner = "3338682145",
    [string]$GitHubRepo = "cripper-skills",
    [string]$GitHubBranch = "main"
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
    Write-Host "[source-intake] $Message" -ForegroundColor Cyan
}

function Resolve-LocalRepoRoot() {
    if (-not $PSScriptRoot) {
        return $null
    }
    $candidate = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..") -ErrorAction SilentlyContinue
    if ($candidate -and (Test-Path -LiteralPath (Join-Path $candidate.Path "pyproject.toml"))) {
        return $candidate.Path
    }
    return $null
}

function Find-PythonCommand() {
    foreach ($name in @("python", "py")) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) {
            return $command.Source
        }
    }
    throw "Python was not found. Install Python first, then rerun this script."
}

function Invoke-SkillInstaller(
    [string]$RequestedInstallRoot,
    [string]$RequestedSkillName,
    [bool]$UseGitHub,
    [string]$Owner,
    [string]$Repo,
    [string]$Branch
) {
    $localInstaller = Join-Path $PSScriptRoot "install-skill.ps1"
    if (Test-Path -LiteralPath $localInstaller) {
        & $localInstaller `
            -InstallRoot $RequestedInstallRoot `
            -SkillName $RequestedSkillName `
            -FromGitHub:$UseGitHub `
            -GitHubOwner $Owner `
            -GitHubRepo $Repo `
            -GitHubBranch $Branch
        return
    }

    $tempInstaller = Join-Path $env:TEMP "source-intake-install-skill.ps1"
    $installerUrl = "https://raw.githubusercontent.com/$Owner/$Repo/$Branch/optional-skills/research/source-intake/install-skill.ps1"
    Write-Step "Downloading $installerUrl"
    Invoke-WebRequest -Uri $installerUrl -OutFile $tempInstaller
    & $tempInstaller `
        -InstallRoot $RequestedInstallRoot `
        -SkillName $RequestedSkillName `
        -FromGitHub `
        -GitHubOwner $Owner `
        -GitHubRepo $Repo `
        -GitHubBranch $Branch
}

function Install-Runtime([string]$PythonCommand, [string]$RepoRoot, [bool]$UseGitHub, [string]$Owner, [string]$Repo, [string]$Branch) {
    if ($UseGitHub -or -not $RepoRoot) {
        $packageRef = "git+https://github.com/$Owner/$Repo.git@$Branch"
        Write-Step "Installing runtime from $packageRef"
        & $PythonCommand -m pip install --upgrade --force-reinstall $packageRef
        return
    }

    Write-Step "Installing runtime from local repo $RepoRoot"
    & $PythonCommand -m pip install --upgrade --force-reinstall $RepoRoot
}

$localRepoRoot = Resolve-LocalRepoRoot
$useGitHub = $FromGitHub -or -not $localRepoRoot

if (-not $SkipSkill) {
    Invoke-SkillInstaller `
        -RequestedInstallRoot $InstallRoot `
        -RequestedSkillName $SkillName `
        -UseGitHub $useGitHub `
        -Owner $GitHubOwner `
        -Repo $GitHubRepo `
        -Branch $GitHubBranch
}

if (-not $SkipRuntime) {
    $pythonCommand = Find-PythonCommand
    Install-Runtime `
        -PythonCommand $pythonCommand `
        -RepoRoot $localRepoRoot `
        -UseGitHub $useGitHub `
        -Owner $GitHubOwner `
        -Repo $GitHubRepo `
        -Branch $GitHubBranch
}

if ($SkipSkill -and $SkipRuntime) {
    Write-Step "Nothing was installed because both -SkipSkill and -SkipRuntime were set."
} elseif ($SkipRuntime) {
    Write-Step "Done. Skill files are ready. Runtime installation was skipped."
} elseif ($SkipSkill) {
    Write-Step "Done. Runtime is ready. Skill installation was skipped."
} else {
    Write-Step "Done. Skill files and runtime are ready."
}
