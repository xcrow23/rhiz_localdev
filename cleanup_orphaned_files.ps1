# Rhiz Codebase Cleanup Script
# Purpose: Archive orphaned files and create manifests for large directories
# Generated: 2026-01-10
# Based on: COMPREHENSIVE_ALIGNMENT_AUDIT_20260110.md

param(
    [switch]$DryRun = $false,
    [switch]$Force = $false
)

$RhizRoot = "C:\Users\dread\documents\rhiz_localdev"
$ArchiveDir = "$RhizRoot\external\archive"
$BackupDir = "$RhizRoot\.cleanup_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Rhiz Codebase Cleanup Script" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN MODE] No changes will be made" -ForegroundColor Yellow
    Write-Host ""
}

# Function to get directory size
function Get-DirectorySize {
    param([string]$Path)
    if (Test-Path $Path) {
        $size = (Get-ChildItem -Path $Path -Recurse -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum
        return [math]::Round($size / 1MB, 2)
    }
    return 0
}

# Function to archive directory
function Archive-Directory {
    param(
        [string]$SourcePath,
        [string]$DestPath,
        [string]$Reason
    )

    $sizeMB = Get-DirectorySize -Path $SourcePath
    Write-Host "[ARCHIVE] $SourcePath ($sizeMB MB) - $Reason" -ForegroundColor Yellow

    if (-not $DryRun) {
        if (-not (Test-Path $ArchiveDir)) {
            New-Item -ItemType Directory -Path $ArchiveDir -Force | Out-Null
        }
        Move-Item -Path $SourcePath -Destination $DestPath -Force
        Write-Host "  → Moved to $DestPath" -ForegroundColor Green
    } else {
        Write-Host "  → Would move to $DestPath" -ForegroundColor Gray
    }
}

# 1. Archive large unused repos from external/
Write-Host "Step 1: Archive Large Unused Repositories" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

$repos_to_archive = @(
    @{Path = "$RhizRoot\external\pytorch-main"; Reason = "Use pip package instead (211 MB)"},
    @{Path = "$RhizRoot\external\tensorflow-master"; Reason = "Not using TensorFlow (451 MB)"},
    @{Path = "$RhizRoot\external\langflow-main"; Reason = "Not aligned with architecture (170 MB)"}
)

foreach ($repo in $repos_to_archive) {
    if (Test-Path $repo.Path) {
        $destPath = "$ArchiveDir\$(Split-Path $repo.Path -Leaf)"
        Archive-Directory -SourcePath $repo.Path -DestPath $destPath -Reason $repo.Reason
    } else {
        Write-Host "[SKIP] $($repo.Path) - Not found" -ForegroundColor Gray
    }
}

# 2. Handle ai-through-symbiosis (2.1 GB)
Write-Host ""
Write-Host "Step 2: Extract ai-through-symbiosis Summary" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

$symbiosis_path = "$RhizRoot\external\ai-through-symbiosis-master"
if (Test-Path $symbiosis_path) {
    $sizeMB = Get-DirectorySize -Path $symbiosis_path
    Write-Host "[LARGE REPO] $symbiosis_path ($sizeMB MB)" -ForegroundColor Yellow

    $readme_path = "$symbiosis_path\README.md"
    if (Test-Path $readme_path) {
        $summary_dest = "$RhizRoot\docs\research\ai_through_symbiosis_summary.md"
        Write-Host "  → Extracting README to docs/research/" -ForegroundColor Yellow

        if (-not $DryRun) {
            Copy-Item -Path $readme_path -Destination $summary_dest -Force
            Write-Host "  → Summary saved to $summary_dest" -ForegroundColor Green

            # Archive the full repo
            Archive-Directory -SourcePath $symbiosis_path -DestPath "$ArchiveDir\ai-through-symbiosis-master" -Reason "Summary extracted"
        } else {
            Write-Host "  → Would extract summary and archive" -ForegroundColor Gray
        }
    } else {
        Write-Host "  → README.md not found, skipping extraction" -ForegroundColor Red
    }
} else {
    Write-Host "[SKIP] ai-through-symbiosis not found" -ForegroundColor Gray
}

# 3. Create Gifts_From_Alex manifest
Write-Host ""
Write-Host "Step 3: Create Gifts_From_Alex Manifest" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

$gifts_path = "$RhizRoot\Gifts_From_Alex"
if (Test-Path $gifts_path) {
    $sizeMB = Get-DirectorySize -Path $gifts_path
    Write-Host "[MANIFEST] Gifts_From_Alex ($sizeMB MB)" -ForegroundColor Yellow

    $manifest_path = "$gifts_path\README.md"

    if (-not $DryRun) {
        $items = Get-ChildItem -Path $gifts_path -Recurse | Where-Object { $_.PSIsContainer -eq $false }
        $manifest_content = @"
# Gifts From Alex

## Overview
Collection of resources, documentation, and reference materials gifted from Alex.

**Total Size**: $sizeMB MB
**Last Updated**: $(Get-Date -Format 'yyyy-MM-dd')

## Contents

"@

        $grouped = $items | Group-Object { $_.Directory.Name }
        foreach ($group in $grouped) {
            $manifest_content += "`n### $($group.Name)`n"
            foreach ($file in $group.Group) {
                $fileSize = [math]::Round($file.Length / 1KB, 2)
                $manifest_content += "- $($file.Name) ($fileSize KB)`n"
            }
        }

        $manifest_content | Out-File -FilePath $manifest_path -Encoding UTF8 -Force
        Write-Host "  → Manifest created at $manifest_path" -ForegroundColor Green
    } else {
        Write-Host "  → Would create manifest at $manifest_path" -ForegroundColor Gray
    }
} else {
    Write-Host "[SKIP] Gifts_From_Alex directory not found" -ForegroundColor Gray
}

# 4. Create external/ manifest
Write-Host ""
Write-Host "Step 4: Create external/ Manifest" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

$external_path = "$RhizRoot\external"
if (Test-Path $external_path) {
    $manifest_path = "$external_path\README.md"

    if (-not $DryRun) {
        $repos = Get-ChildItem -Path $external_path -Directory | Where-Object { $_.Name -ne "archive" }

        $manifest_content = @"
# External Reference Repositories

## Overview
Collection of external codebases used as reference and research material.

**Last Updated**: $(Get-Date -Format 'yyyy-MM-dd')

## Active Repositories

"@

        foreach ($repo in $repos) {
            $repoSize = Get-DirectorySize -Path $repo.FullName
            $manifest_content += "- **$($repo.Name)** ($repoSize MB)`n"
        }

        $manifest_content += "`n## Archived Repositories`n`n"
        $manifest_content += "See ``archive/`` directory for repositories no longer actively referenced.`n"

        $manifest_content | Out-File -FilePath $manifest_path -Encoding UTF8 -Force
        Write-Host "  → Manifest created at $manifest_path" -ForegroundColor Green
    } else {
        Write-Host "  → Would create manifest at $manifest_path" -ForegroundColor Gray
    }
} else {
    Write-Host "[SKIP] external/ directory not found" -ForegroundColor Gray
}

# 5. Check for orphaned temp files
Write-Host ""
Write-Host "Step 5: Check for Orphaned Temp Files" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

$temp_patterns = @("UsersdreadAppDataLocalTemp*.json", "memory_export.json")
foreach ($pattern in $temp_patterns) {
    $files = Get-ChildItem -Path $RhizRoot -Filter $pattern -ErrorAction SilentlyContinue
    if ($files) {
        foreach ($file in $files) {
            Write-Host "[TEMP] $($file.Name)" -ForegroundColor Yellow

            if ($Force) {
                if (-not $DryRun) {
                    Remove-Item -Path $file.FullName -Force
                    Write-Host "  → Deleted" -ForegroundColor Green
                } else {
                    Write-Host "  → Would delete" -ForegroundColor Gray
                }
            } else {
                Write-Host "  → Use -Force flag to delete" -ForegroundColor Gray
            }
        }
    }
}

# Summary
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Cleanup Summary" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host ""
    Write-Host "This was a dry run. No changes were made." -ForegroundColor Yellow
    Write-Host "Run without -DryRun flag to apply changes." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "Cleanup complete!" -ForegroundColor Green
    if (Test-Path $ArchiveDir) {
        $archiveSize = Get-DirectorySize -Path $ArchiveDir
        Write-Host "Archived $archiveSize MB to external/archive/" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "  .\cleanup_orphaned_files.ps1            # Dry run (preview changes)" -ForegroundColor Gray
Write-Host "  .\cleanup_orphaned_files.ps1 -DryRun    # Explicit dry run" -ForegroundColor Gray
Write-Host "  .\cleanup_orphaned_files.ps1 -Force     # Execute cleanup (archive repos, delete temp files)" -ForegroundColor Gray
