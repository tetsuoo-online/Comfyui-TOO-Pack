# Lecture du fichier
$content = Get-Content "pyproject.toml"

# Extraction de la version (ligne du type: version = "1.2.3")
$versionLine = $content | Where-Object { $_ -match 'version\s*=' }
if ($versionLine -match 'version\s*=\s*"([^"]+)"') {
    $currentVersion = $matches[1]
} else {
    Write-Host "Impossible de trouver la version dans pyproject.toml"
    exit 1
}

Write-Host "Version actuelle : $currentVersion"

# Demande nouvelle version
$newVersion = Read-Host "Nouvelle version (laisser vide pour garder $currentVersion)"
if ([string]::IsNullOrWhiteSpace($newVersion)) {
    $newVersion = $currentVersion
}

Write-Host "Nouvelle version retenue : $newVersion"

# Remplacement dans le fichier
$newContent = $content -replace 'version\s*=\s*"[^"]+"', "version = `"$newVersion`""
$newContent | Set-Content "pyproject.toml"

Write-Host "Version mise à jour dans pyproject.toml"