[CmdletBinding()]
param(
    [switch]$FromGitHub,
    [string]$GitHubOwner = "3338682145",
    [string]$GitHubRepo = "cripper-skills",
    [string]$GitHubBranch = "main"
)

$installRoot = if ($env:CODEX_HOME) {
    Join-Path $env:CODEX_HOME "skills"
} else {
    Join-Path $env:USERPROFILE ".codex\skills"
}

& (Join-Path $PSScriptRoot "install-skill.ps1") `
    -InstallRoot $installRoot `
    -SkillName "source-intake" `
    -FromGitHub:$FromGitHub `
    -GitHubOwner $GitHubOwner `
    -GitHubRepo $GitHubRepo `
    -GitHubBranch $GitHubBranch
