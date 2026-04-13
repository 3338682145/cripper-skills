[CmdletBinding()]
param(
    [string]$InstallRoot,
    [string]$SkillName = "source-intake",
    [switch]$FromGitHub,
    [string]$GitHubOwner = "3338682145",
    [string]$GitHubRepo = "cripper-skills",
    [string]$GitHubBranch = "main"
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
    Write-Host "[source-intake] $Message" -ForegroundColor Cyan
}

function Resolve-InstallRoot([string]$RequestedRoot) {
    if ($RequestedRoot) {
        return $RequestedRoot
    }
    if ($env:CODEX_HOME) {
        return (Join-Path $env:CODEX_HOME "skills")
    }
    $codexRoot = Join-Path $env:USERPROFILE ".codex\skills"
    if (Test-Path -LiteralPath (Split-Path -Parent $codexRoot)) {
        return $codexRoot
    }
    throw "No default skill directory was detected. Re-run with -InstallRoot '<your-agent-skill-dir>'."
}

function Initialize-Directory([string]$PathValue) {
    if (-not (Test-Path -LiteralPath $PathValue)) {
        New-Item -ItemType Directory -Path $PathValue -Force | Out-Null
    }
    return (Resolve-Path -LiteralPath $PathValue).Path
}

function Reset-Destination([string]$Destination) {
    if (Test-Path -LiteralPath $Destination) {
        Remove-Item -LiteralPath $Destination -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
}

function Copy-LocalSkill([string]$SourceDir, [string]$Destination) {
    Write-Step "Installing local skill files from $SourceDir"
    Reset-Destination -Destination $Destination
    Copy-Item -Path (Join-Path $SourceDir "*") -Destination $Destination -Recurse -Force
}

function Download-File([string]$Url, [string]$Destination) {
    $parent = Split-Path -Parent $Destination
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    Invoke-WebRequest -Uri $Url -OutFile $Destination
}

function Install-FromGitHub([string]$Destination, [string]$Owner, [string]$Repo, [string]$Branch) {
    $baseUrl = "https://raw.githubusercontent.com/$Owner/$Repo/$Branch/optional-skills/research/source-intake"
    $files = @(
        "SKILL.md",
        "README.md",
        "README.zh-CN.md",
        "install-skill.ps1",
        "install-to-codex.ps1",
        "install-to-codex.cmd",
        "references/backend-matrix.md",
        "references/packet-contract.md",
        "references/verifier-rubric.md",
        "references/examples.md"
    )

    Write-Step "Downloading skill files from $baseUrl"
    Reset-Destination -Destination $Destination
    foreach ($file in $files) {
        $relativeUrl = $file.Replace("\", "/")
        $destinationFile = Join-Path $Destination $file
        Download-File -Url "$baseUrl/$relativeUrl" -Destination $destinationFile
    }
}

$resolvedInstallRoot = Initialize-Directory -PathValue (Resolve-InstallRoot -RequestedRoot $InstallRoot)
$destinationDir = Join-Path $resolvedInstallRoot $SkillName
$sourceDir = $null

if ($PSScriptRoot) {
    $candidateSkillFile = Join-Path $PSScriptRoot "SKILL.md"
    if (Test-Path -LiteralPath $candidateSkillFile) {
        $sourceDir = (Resolve-Path -LiteralPath $PSScriptRoot).Path
    }
}

if (-not $FromGitHub -and $sourceDir) {
    Copy-LocalSkill -SourceDir $sourceDir -Destination $destinationDir
} else {
    Install-FromGitHub -Destination $destinationDir -Owner $GitHubOwner -Repo $GitHubRepo -Branch $GitHubBranch
}

Write-Step "Installed to $destinationDir"
Write-Step "Skill manifest: $(Join-Path $destinationDir 'SKILL.md')"
Write-Step "This installs the skill files only. Install the cliper package separately if you also want source-intake CLI commands."
