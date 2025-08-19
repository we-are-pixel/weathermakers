# PowerShell script to fix Git repository with invalid Windows filenames
# This script creates a cleaned version of the repository

param(
    [string]$SourceRepo = "https://github.com/we-are-pixel/weathermakers.git",
    [string]$CleanRepoPath = "weathermakers-clean"
)

Write-Host "🔧 Git Repository Filename Fixer for Windows" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Function to sanitize filenames
function Sanitize-Filename {
    param([string]$filename)
    
    # Replace invalid Windows characters
    $sanitized = $filename -replace '[<>:"|?*="&"]', '_'
    
    # Handle URL encoding
    if ($sanitized -match '%[0-9A-Fa-f]{2}') {
        try {
            $sanitized = [System.Web.HttpUtility]::UrlDecode($sanitized)
            $sanitized = $sanitized -replace '[<>:"|?*="&"]', '_'
        }
        catch {
            # If URL decode fails, keep the original replacement
        }
    }
    
    # Clean up multiple underscores and trim
    $sanitized = $sanitized -replace '_+', '_'
    $sanitized = $sanitized.Trim('. ')
    
    # Truncate if too long
    if ($sanitized.Length -gt 200) {
        $extension = [System.IO.Path]::GetExtension($sanitized)
        $nameWithoutExt = [System.IO.Path]::GetFileNameWithoutExtension($sanitized)
        $sanitized = $nameWithoutExt.Substring(0, 200 - $extension.Length) + $extension
    }
    
    return $sanitized
}

# Check if git-filter-repo is available
$filterRepoAvailable = $false
try {
    git filter-repo --help | Out-Null
    $filterRepoAvailable = $true
    Write-Host "✅ git-filter-repo is available" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  git-filter-repo not found. Using alternative method." -ForegroundColor Yellow
    Write-Host "   Install with: pip install git-filter-repo" -ForegroundColor Yellow
}

Write-Host "`n📥 Step 1: Clone repository..." -ForegroundColor Cyan

# Create a bare clone
$tempRepo = "temp-weathermakers-bare"
if (Test-Path $tempRepo) {
    Remove-Item $tempRepo -Recurse -Force
}

try {
    git clone --bare $SourceRepo $tempRepo
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to clone repository"
    }
}
catch {
    Write-Host "❌ Failed to clone repository: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Push-Location $tempRepo

Write-Host "📋 Step 2: Analyzing problematic files..." -ForegroundColor Cyan

# Get list of all files
$allFiles = git ls-tree -r --name-only HEAD

# Find problematic files
$problematicFiles = @()
$invalidChars = '[<>:"|?*="&"]'

foreach ($file in $allFiles) {
    if ($file -match $invalidChars) {
        $problematicFiles += $file
    }
}

Write-Host "Found $($problematicFiles.Count) problematic files" -ForegroundColor Yellow

if ($problematicFiles.Count -eq 0) {
    Write-Host "✅ No problematic files found!" -ForegroundColor Green
    Pop-Location
    Remove-Item $tempRepo -Recurse -Force
    exit 0
}

# Show examples
Write-Host "`n📄 Examples of problematic files:" -ForegroundColor Yellow
$problematicFiles | Select-Object -First 10 | ForEach-Object {
    Write-Host "  $_" -ForegroundColor Red
}
if ($problematicFiles.Count -gt 10) {
    Write-Host "  ... and $($problematicFiles.Count - 10) more" -ForegroundColor Red
}

# Create rename mapping
Write-Host "`n🔄 Step 3: Creating rename mapping..." -ForegroundColor Cyan
$renameMapping = @{}
$usedNames = @{}

foreach ($originalPath in $problematicFiles) {
    $pathParts = $originalPath -split '/'
    $sanitizedParts = @()
    
    foreach ($part in $pathParts) {
        $sanitizedParts += Sanitize-Filename $part
    }
    
    $sanitizedPath = $sanitizedParts -join '/'
    
    # Ensure unique names
    $baseSanitized = $sanitizedPath
    $counter = 1
    while ($usedNames.ContainsKey($sanitizedPath)) {
        $extension = [System.IO.Path]::GetExtension($baseSanitized)
        $nameWithoutExt = $baseSanitized -replace [regex]::Escape($extension) + '$', ''
        $sanitizedPath = "${nameWithoutExt}_${counter}${extension}"
        $counter++
    }
    
    $renameMapping[$originalPath] = $sanitizedPath
    $usedNames[$sanitizedPath] = $true
}

# Save mapping
$mappingFile = Join-Path (Get-Location).Path "rename_mapping.txt"
$renameMapping.GetEnumerator() | ForEach-Object {
    "$($_.Key) -> $($_.Value)"
} | Out-File -FilePath $mappingFile -Encoding UTF8

Write-Host "💾 Saved rename mapping to: $mappingFile" -ForegroundColor Green

# Show examples
Write-Host "`n📝 Example renames:" -ForegroundColor Yellow
$count = 0
$renameMapping.GetEnumerator() | ForEach-Object {
    if ($count -lt 5) {
        Write-Host "  $($_.Key) -> $($_.Value)" -ForegroundColor Cyan
        $count++
    }
}

Pop-Location

Write-Host "`n🎯 Step 4: Creating solution scripts..." -ForegroundColor Cyan

# Create a git-filter-repo script if available
if ($filterRepoAvailable) {
    $filterScript = @"
#!/bin/bash
# Script to clean repository using git-filter-repo

cd $tempRepo

echo "Applying filename fixes with git-filter-repo..."

"@

    foreach ($mapping in $renameMapping.GetEnumerator()) {
        $original = $mapping.Key -replace "'", "'\'''"
        $sanitized = $mapping.Value -replace "'", "'\'''"
        $filterScript += "git filter-repo --path-rename '$original':'$sanitized' --force`n"
    }
    
    $filterScript += @"

echo "Repository cleaned successfully!"
echo "You can now clone from this local repository:"
echo "git clone $tempRepo $CleanRepoPath"
"@

    $filterScript | Out-File -FilePath "clean_with_filter_repo.sh" -Encoding UTF8
    Write-Host "📄 Created clean_with_filter_repo.sh" -ForegroundColor Green
}

# Create manual cleanup instructions
$instructions = @"
🚀 INSTRUCTIONS FOR FIXING THE REPOSITORY
=========================================

Problem: The repository contains files with characters (?, =, &) that are invalid on Windows.

Solution Options:

OPTION 1 - Using git-filter-repo (RECOMMENDED):
1. Install git-filter-repo: pip install git-filter-repo
2. Run: bash clean_with_filter_repo.sh
3. Clone the cleaned repo: git clone $tempRepo $CleanRepoPath

OPTION 2 - Manual approach:
1. Use Linux/WSL environment where these characters are valid
2. Clone repository there: git clone $SourceRepo
3. Use the Python script fix_filenames.py to rename files
4. Push to a new repository

OPTION 3 - Sparse checkout (partial solution):
1. git clone --no-checkout $SourceRepo
2. git sparse-checkout init --cone
3. git sparse-checkout set [directories without problematic files]
4. git checkout

Files that will be renamed:
$($problematicFiles.Count) files total
See rename_mapping.txt for complete list

The cleaned repository will be fully functional on Windows systems.
"@

$instructions | Out-File -FilePath "INSTRUCTIONS.txt" -Encoding UTF8

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "📖 See INSTRUCTIONS.txt for next steps" -ForegroundColor Yellow
Write-Host "📋 See rename_mapping.txt for all file renames" -ForegroundColor Yellow

if ($filterRepoAvailable) {
    Write-Host "`n🎯 Quick start: Run 'bash clean_with_filter_repo.sh'" -ForegroundColor Cyan
} else {
    Write-Host "`n💡 Tip: Install git-filter-repo for easier cleanup: pip install git-filter-repo" -ForegroundColor Yellow
}