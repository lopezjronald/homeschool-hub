Write-Host "Setting up developer environment..." -ForegroundColor Cyan

git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not inside a git repository." -ForegroundColor Red
    exit 1
}

git config core.hooksPath .githooks
$hooksPath = git config --get core.hooksPath
if ($hooksPath -ne ".githooks") {
    Write-Host "Failed to set core.hooksPath to .githooks" -ForegroundColor Red
    exit 1
}

Write-Host "Git hooks enabled (core.hooksPath = .githooks)" -ForegroundColor Green

gh --version *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Host "GitHub CLI (gh) installed" -ForegroundColor Green
} else {
    Write-Host "GitHub CLI (gh) not found. Install if you want CLI PR workflow." -ForegroundColor Yellow
}

Write-Host "Done." -ForegroundColor Cyan
