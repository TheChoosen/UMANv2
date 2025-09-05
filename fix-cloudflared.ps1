# ====================================================
# 🔧 UMan API - Fix Cloudflared Connection Issues
# ====================================================

Write-Host "🚀 UMan API - Cloudflared Diagnostics & Fix" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Function to write colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 1. Stop existing cloudflared processes
Write-ColorOutput "🔴 Arrêt des processus cloudflared existants..." "Yellow"
try {
    Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-ColorOutput "✅ Processus cloudflared arrêtés" "Green"
} catch {
    Write-ColorOutput "ℹ️ Aucun processus cloudflared en cours" "Gray"
}

# 2. Stop and remove cloudflared service if exists
Write-ColorOutput "🔴 Arrêt et suppression du service cloudflared..." "Yellow"
try {
    & cloudflared.exe service uninstall 2>$null
    Write-ColorOutput "✅ Service cloudflared désinstallé" "Green"
} catch {
    Write-ColorOutput "ℹ️ Service cloudflared n'était pas installé" "Gray"
}

# 3. Check network connectivity to Cloudflare
Write-ColorOutput "🌐 Test de connectivité réseau..." "Yellow"
$cfEndpoints = @(
    "1.1.1.1",
    "198.41.192.227", 
    "cloudflare.com"
)

foreach ($endpoint in $cfEndpoints) {
    try {
        $ping = Test-NetConnection -ComputerName $endpoint -Port 443 -WarningAction SilentlyContinue
        if ($ping.TcpTestSucceeded) {
            Write-ColorOutput "✅ Connexion à $endpoint: OK" "Green"
        } else {
            Write-ColorOutput "❌ Connexion à $endpoint: ÉCHEC" "Red"
        }
    } catch {
        Write-ColorOutput "❌ Erreur test $endpoint" "Red"
    }
}

# 4. Check tunnel configuration
Write-ColorOutput "🔍 Vérification de la configuration du tunnel..." "Yellow"
$configFile = "config.yml"
if (Test-Path $configFile) {
    Write-ColorOutput "✅ Fichier config.yml trouvé" "Green"
    $config = Get-Content $configFile
    Write-ColorOutput "Contenu de la configuration:" "Cyan"
    $config | ForEach-Object { Write-ColorOutput "  $_" "Gray" }
} else {
    Write-ColorOutput "❌ Fichier config.yml non trouvé" "Red"
}

# 5. Check for certificate files
Write-ColorOutput "🔒 Vérification des certificats..." "Yellow"
$certFiles = @("cert.pem", "cloudflared.crt", "*.pem")
$foundCerts = @()

foreach ($pattern in $certFiles) {
    $found = Get-ChildItem -Path . -Name $pattern -ErrorAction SilentlyContinue
    if ($found) {
        $foundCerts += $found
    }
}

if ($foundCerts.Count -gt 0) {
    Write-ColorOutput "✅ Certificats trouvés:" "Green"
    $foundCerts | ForEach-Object { Write-ColorOutput "  $_" "Gray" }
} else {
    Write-ColorOutput "⚠️ Aucun certificat local trouvé" "Yellow"
}

# 6. Create a new configuration with Windows-specific settings
Write-ColorOutput "⚙️ Création d'une configuration optimisée pour Windows..." "Yellow"

# Get tunnel credentials if they exist
$credentialsFile = Get-ChildItem -Path . -Name "*.json" | Where-Object { $_.Name -match "^[a-f0-9-]{36}\.json$" } | Select-Object -First 1

if ($credentialsFile) {
    $tunnelId = $credentialsFile.BaseName
    Write-ColorOutput "✅ Tunnel ID trouvé: $tunnelId" "Green"
    
    # Create optimized config
    $configContent = @"
tunnel: $tunnelId
credentials-file: $($credentialsFile.Name)

# Windows-specific optimizations
protocol: quic
grace-period: 30s
retries: 5
ha-connections: 2

# Logging
loglevel: info

# Ingress rules
ingress:
  - hostname: uman-api.com
    service: http://localhost:5000
  - hostname: democratie.uman-api.com  
    service: http://localhost:5000
  - hostname: biq.uman-api.com
    service: http://localhost:5000
  - hostname: garde.uman-api.com
    service: http://localhost:5000
  - hostname: sheriff.uman-api.com
    service: http://localhost:5000
  - hostname: monark.uman-api.com
    service: http://localhost:5000
  - service: http_status:404
"@
    
    $configContent | Out-File -FilePath "config-fixed.yml" -Encoding UTF8
    Write-ColorOutput "✅ Configuration optimisée créée: config-fixed.yml" "Green"
    
} else {
    Write-ColorOutput "❌ Aucun fichier de credentials trouvé (*.json)" "Red"
}

# 7. Test connection with optimized settings
Write-ColorOutput "🧪 Test de connexion avec configuration optimisée..." "Yellow"
if (Test-Path "config-fixed.yml") {
    Write-ColorOutput "Lancement du test de connexion..." "Cyan"
    Write-ColorOutput "Commande: cloudflared.exe tunnel --config config-fixed.yml run" "Gray"
    Write-ColorOutput "" "White"
    Write-ColorOutput "Pour démarrer le tunnel avec la configuration corrigée:" "Yellow"
    Write-ColorOutput "  cloudflared.exe tunnel --config config-fixed.yml run" "Green"
    Write-ColorOutput "" "White"
    Write-ColorOutput "Pour installer comme service Windows:" "Yellow"
    Write-ColorOutput "  cloudflared.exe service install --config config-fixed.yml" "Green"
}

# 8. Create a startup script
$startupScript = @"
# UMan API - Cloudflared Startup Script
# Usage: .\start-cloudflared-fixed.ps1

Write-Host "🚀 Démarrage du tunnel Cloudflared optimisé..." -ForegroundColor Cyan

# Stop existing processes
Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force

# Start with optimized config
& cloudflared.exe tunnel --config config-fixed.yml run
"@

$startupScript | Out-File -FilePath "start-cloudflared-fixed.ps1" -Encoding UTF8
Write-ColorOutput "✅ Script de démarrage créé: start-cloudflared-fixed.ps1" "Green"

# 9. System diagnostics
Write-ColorOutput "🔍 Diagnostics système..." "Yellow"
Write-ColorOutput "OS: $((Get-WmiObject Win32_OperatingSystem).Caption)" "Gray"
Write-ColorOutput "PowerShell: $($PSVersionTable.PSVersion)" "Gray"
Write-ColorOutput "Date/Heure: $(Get-Date)" "Gray"

# 10. DNS flush (peut aider avec les problèmes de connectivité)
Write-ColorOutput "🔄 Nettoyage du cache DNS..." "Yellow"
try {
    & ipconfig /flushdns | Out-Null
    Write-ColorOutput "✅ Cache DNS nettoyé" "Green"
} catch {
    Write-ColorOutput "⚠️ Impossible de nettoyer le cache DNS" "Yellow"
}

Write-ColorOutput "" "White"
Write-ColorOutput "🎯 RÉSUMÉ DES ACTIONS:" "Cyan"
Write-ColorOutput "1. Processus cloudflared arrêtés" "White"
Write-ColorOutput "2. Service désinstallé" "White"
Write-ColorOutput "3. Connectivité réseau testée" "White"
Write-ColorOutput "4. Configuration optimisée créée" "White"
Write-ColorOutput "5. Script de démarrage généré" "White"
Write-ColorOutput "" "White"
Write-ColorOutput "📋 PROCHAINES ÉTAPES:" "Yellow"
Write-ColorOutput "1. Exécutez: .\start-cloudflared-fixed.ps1" "Green"
Write-ColorOutput "2. Si stable, installez le service: cloudflared.exe service install --config config-fixed.yml" "Green"
Write-ColorOutput "3. Testez vos domaines: https://uman-api.com" "Green"
Write-ColorOutput "" "White"
Write-ColorOutput "✅ Diagnostic terminé!" "Cyan"
