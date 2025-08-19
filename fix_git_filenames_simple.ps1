# Simple PowerShell script to fix Git repository with invalid Windows filenames

Write-Host "🔧 Git Repository Filename Fixer for Windows" -ForegroundColor Green

# Function to sanitize filenames
function Sanitize-Filename {
    param([string]$filename)
    
    # Replace invalid Windows characters one by one
    $sanitized = $filename
    $sanitized = $sanitized -replace '\?', '_'
    $sanitized = $sanitized -replace '=', '_'
    $sanitized = $sanitized -replace '&', '_and_'
    $sanitized = $sanitized -replace '<', '_'
    $sanitized = $sanitized -replace '>', '_'
    $sanitized = $sanitized -replace ':', '_'
    $sanitized = $sanitized -replace '"', '_'
    $sanitized = $sanitized -replace '\|', '_'
    $sanitized = $sanitized -replace '\*', '_'
    
    # Handle URL encoding
    if ($sanitized -match '%[0-9A-Fa-f]{2}') {
        try {
            Add-Type -AssemblyName System.Web
            $sanitized = [System.Web.HttpUtility]::UrlDecode($sanitized)
            # Re-sanitize after decoding
            $sanitized = $sanitized -replace '\?', '_'
            $sanitized = $sanitized -replace '=', '_'
            $sanitized = $sanitized -replace '&', '_and_'
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

Write-Host "📥 Analyzing the repository..." -ForegroundColor Cyan

# Get list of problematic files from the remote
try {
    $allFiles = git ls-tree -r --name-only origin/main 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Could not get file list from origin/main" -ForegroundColor Red
        Write-Host "Make sure you have the remote configured: git remote add origin https://github.com/we-are-pixel/weathermakers.git" -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host "❌ Error getting file list: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Find problematic files
$problematicFiles = @()
$invalidPatterns = @('\?', '=', '&', '<', '>', ':', '"', '\|', '\*')

foreach ($file in $allFiles) {
    $hasInvalidChar = $false
    foreach ($pattern in $invalidPatterns) {
        if ($file -match $pattern) {
            $hasInvalidChar = $true
            break
        }
    }
    if ($hasInvalidChar) {
        $problematicFiles += $file
    }
}

Write-Host "Found $($problematicFiles.Count) problematic files" -ForegroundColor Yellow

if ($problematicFiles.Count -eq 0) {
    Write-Host "✅ No problematic files found!" -ForegroundColor Green
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
Write-Host "`n🔄 Creating rename mapping..." -ForegroundColor Cyan
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
"Original -> Sanitized" | Out-File -FilePath "rename_mapping.txt" -Encoding UTF8
"=" * 50 | Out-File -FilePath "rename_mapping.txt" -Append -Encoding UTF8
$renameMapping.GetEnumerator() | ForEach-Object {
    "$($_.Key) -> $($_.Value)"
} | Out-File -FilePath "rename_mapping.txt" -Append -Encoding UTF8

Write-Host "💾 Saved rename mapping to: rename_mapping.txt" -ForegroundColor Green

# Show examples
Write-Host "`n📝 Example renames:" -ForegroundColor Yellow
$count = 0
$renameMapping.GetEnumerator() | ForEach-Object {
    if ($count -lt 5) {
        Write-Host "  $($_.Key) -> $($_.Value)" -ForegroundColor Cyan
        $count++
    }
}

# Create instructions
$instructions = @"
🚀 INSTRUCTIONS FOR FIXING THE REPOSITORY
=========================================

Problem: The repository contains $($problematicFiles.Count) files with characters (?, =, &) that are invalid on Windows.

RECOMMENDED SOLUTION - Using git-filter-repo:

1. Install git-filter-repo:
   pip install git-filter-repo

2. Clone the repository bare:
   git clone --bare https://github.com/we-are-pixel/weathermakers.git weathermakers-temp

3. Navigate to the repository:
   cd weathermakers-temp

4. Apply the renames using filter-repo (create this script):

#!/bin/bash
"@

# Add filter-repo commands to instructions
foreach ($mapping in $renameMapping.GetEnumerator()) {
    $original = $mapping.Key -replace "'", "'\'''"
    $sanitized = $mapping.Value -replace "'", "'\'''"
    $instructions += "git filter-repo --path-rename '$original':'$sanitized' --force`n"
}

$instructions += @"

5. Clone the cleaned repository:
   git clone weathermakers-temp weathermakers-clean

ALTERNATIVE SOLUTIONS:

Option 2 - Use WSL/Linux:
- Clone and work with the repository in WSL where these characters are valid
- Use standard git operations there

Option 3 - Sparse checkout:
- Clone with --no-checkout
- Use sparse-checkout to only include directories without problematic files

Files that need renaming:
See rename_mapping.txt for the complete list of $($problematicFiles.Count) files.
"@

$instructions | Out-File -FilePath "INSTRUCTIONS.txt" -Encoding UTF8

Write-Host "`n✅ Analysis complete!" -ForegroundColor Green
Write-Host "📖 See INSTRUCTIONS.txt for detailed steps" -ForegroundColor Yellow
Write-Host "📋 See rename_mapping.txt for all file renames" -ForegroundColor Yellow
Write-Host "`n💡 Quick start:" -ForegroundColor Cyan
Write-Host "   1. pip install git-filter-repo" -ForegroundColor White
Write-Host "   2. Follow the bash script in INSTRUCTIONS.txt" -ForegroundColor White