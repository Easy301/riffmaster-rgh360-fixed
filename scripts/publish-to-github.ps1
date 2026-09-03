# Publish to GitHub (release)
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

git branch -M main
git push -u origin main

$Notes = Get-Content "$Root\docs\RELEASE-NOTES.md" -Raw

gh release create "v1.04-stable" `
    "$Root\bin\riffmaster.xex" `
    --title "1.04 stable" `
    --notes $Notes

Write-Host ""
Write-Host "Release: https://github.com/$User/$RepoName/releases/tag/v1.04-stable"
