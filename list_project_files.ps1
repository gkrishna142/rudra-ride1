# Simple script to list project files
$projectRoot = "C:\Users\DELL\Desktop\Admin"
Set-Location $projectRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "YOUR PROJECT FILES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Current Git Status:" -ForegroundColor Green
git status --short
Write-Host ""

Write-Host "Files in your project:" -ForegroundColor Yellow
Write-Host ""

# List main directories and files
$items = Get-ChildItem -Path $projectRoot | Where-Object { $_.Name -ne '.git' }

foreach ($item in $items) {
    if ($item.PSIsContainer) {
        Write-Host "📁 $($item.Name)/" -ForegroundColor Cyan
        $subItems = Get-ChildItem -Path $item.FullName -Recurse -File -ErrorAction SilentlyContinue | 
            Where-Object { $_.FullName -notmatch '\\env\\' -and $_.FullName -notmatch '__pycache__' } |
            Select-Object -First 20
        foreach ($subItem in $subItems) {
            $relative = $subItem.FullName.Replace($projectRoot + "\", "")
            Write-Host "   - $relative" -ForegroundColor Gray
        }
        Write-Host ""
    } else {
        Write-Host "📄 $($item.Name)" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TO ADD ALL FILES:" -ForegroundColor Cyan
Write-Host "git add ." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

