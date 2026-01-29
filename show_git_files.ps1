# Script to show what files will be added to git

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FILES THAT WILL BE ADDED TO GIT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get current directory
$projectRoot = "C:\Users\DELL\Desktop\Admin"
Set-Location $projectRoot

Write-Host "Project Root: $projectRoot" -ForegroundColor Yellow
Write-Host ""

# Check git status
Write-Host "Git Status:" -ForegroundColor Green
git status --short

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DETAILED FILE LIST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Show files that would be added
$files = Get-ChildItem -Recurse -File | Where-Object {
    $_.FullName -notmatch '\\env\\' -and
    $_.FullName -notmatch '__pycache__' -and
    $_.FullName -notmatch '\\.git' -and
    $_.FullName -notmatch '\\.pyc$'
}

Write-Host "Total files to be tracked: $($files.Count)" -ForegroundColor Yellow
Write-Host ""

# Group by directory
$grouped = $files | Group-Object { Split-Path $_.DirectoryName -Leaf }

Write-Host "Files by Directory:" -ForegroundColor Green
Write-Host ""

foreach ($group in $grouped | Sort-Object Name) {
    Write-Host "📁 $($group.Name)" -ForegroundColor Cyan
    foreach ($file in $group.Group | Select-Object -First 10) {
        $relativePath = $file.FullName.Replace($projectRoot + "\", "")
        Write-Host "   - $relativePath" -ForegroundColor Gray
    }
    if ($group.Count -gt 10) {
        Write-Host "   ... and $($group.Count - 10) more files" -ForegroundColor DarkGray
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TO ADD ALL FILES, RUN:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "git add ." -ForegroundColor Yellow
Write-Host ""

