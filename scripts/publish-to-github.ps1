# Publish to GitHub (private repo + release)
# Run from repo root AFTER: gh auth login

$ErrorActionPreference = "Stop"
$RepoName = "riffmaster-rgh360-fixed"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

gh auth status | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in. Run: gh auth login -h github.com -p https -w"
    exit 1
}

$User = (gh api user -q .login)
Write-Host "GitHub user: $User"

# Create private repo if remote missing
if (-not (git remote get-url origin 2>$null)) {
    gh repo create $RepoName --private --source=. --remote=origin --description "Patched riffmaster-rgh360: RiffMaster auth fix for Xbox 360"
}

git branch -M main
git push -u origin main

# Release with patched xex
$Notes = Get-Content "$Root\docs\RELEASE-NOTES-v1.0.0-fixed.md" -Raw
$Notes = $Notes -replace "PLACEHOLDER", $User

gh release create "v1.0.0-fixed" `
    "$Root\bin\riffmaster.xex" `
    --title "v1.0.0-fixed — Patched RiffMaster driver" `
    --notes $Notes

Write-Host ""
Write-Host "Private repo: https://github.com/$User/$RepoName"
Write-Host "Release:      https://github.com/$User/$RepoName/releases/tag/v1.0.0-fixed"
