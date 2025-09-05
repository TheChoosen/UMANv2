# ====================================================
# UMan API - Fix Cloudflared Connection Issues
# ====================================================

Write-Host "UMan API - Cloudflared Diagnostics & Fix" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Function to write colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 1. Stop existing cloudflared processes
Write-ColorOutput "Arret des processus cloudflared existants..." "Yellow"
try {
    Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-ColorOutput "Processus cloudflared arretes" "Green"
} catch {
    Write-ColorOutput "Aucun processus cloudflared en cours" "Gray"
}

# 2. Stop and remove cloudflared service if exists
Write-ColorOutput "Arret et suppression du service cloudflared..." "Yellow"
try {
    & cloudflared.exe service uninstall 2>$null
    Write-ColorOutput "Service cloudflared desinstalle" "Green"
} catch {
    Write-ColorOutput "Service cloudflared n'etait pas installe" "Gray"
}

# 3. Check network connectivity to Cloudflare
Write-ColorOutput "Test de connectivite reseau..." "Yellow"
$cfEndpoints = @(
    "1.1.1.1",
    "198.41.192.227", 
    "cloudflare.com"
)

foreach ($endpoint in $cfEndpoints) {
    try {
        $ping = Test-NetConnection -ComputerName $endpoint -Port 443 -WarningAction SilentlyContinue
        if ($ping.TcpTestSucceeded) {
            Write-ColorOutput "Connexion a ${endpoint} - OK" "Green"
        } else {
            Write-ColorOutput "Connexion a ${endpoint} - ECHEC" "Red"
        }
    } catch {
        Write-ColorOutput "Erreur test ${endpoint}" "Red"
    }
}

# 4. Check tunnel configuration in user profile
Write-ColorOutput "Verification de la configuration du tunnel..." "Yellow"
$UserProfile = $env:USERPROFILE
$CloudflaredDir = Join-Path $UserProfile ".cloudflared"
$ConfigFile = Join-Path $CloudflaredDir "config.yml"

if (Test-Path $ConfigFile) {
    Write-ColorOutput "Fichier config.yml trouve dans ${CloudflaredDir}" "Green"
    $config = Get-Content $ConfigFile
    Write-ColorOutput "Contenu de la configuration:" "Cyan"
    $config | ForEach-Object { Write-ColorOutput "  $_" "Gray" }
} else {
    Write-ColorOutput "Fichier config.yml non trouve dans ${CloudflaredDir}" "Red"
}

# 5. Check for certificate files
Write-ColorOutput "Verification des certificats..." "Yellow"
$credFiles = Get-ChildItem -Path $CloudflaredDir -Name "*.json" -ErrorAction SilentlyContinue

if ($credFiles) {
    Write-ColorOutput "Certificats trouves:" "Green"
    $credFiles | ForEach-Object { Write-ColorOutput "  $_" "Gray" }
} else {
    Write-ColorOutput "Aucun certificat local trouve" "Yellow"
}

# 6. Create a new optimized configuration
Write-ColorOutput "Creation d'une configuration optimisee pour Windows..." "Yellow"

# Get tunnel credentials if they exist
$credentialsFile = Get-ChildItem -Path $CloudflaredDir -Name "*.json" -ErrorAction SilentlyContinue | Select-Object -First 1

if ($credentialsFile) {
    $tunnelId = $credentialsFile.BaseName
    $credPath = Join-Path $CloudflaredDir $credentialsFile.Name
    Write-ColorOutput "Tunnel ID trouve: $tunnelId" "Green"
    
    # Create optimized config
    $configContent = @"
tunnel: $tunnelId
credentials-file: $credPath

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
  - hostname: www.uman-api.com
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
  - hostname: peupleun.live
    service: http://localhost:5000
  - hostname: www.peupleun.live
    service: http://localhost:5000
  - hostname: republiqueduquebec.quebec
    service: http://localhost:5000
  - hostname: www.republiqueduquebec.quebec
    service: http://localhost:5000
  - service: http_status:404
"@
    
    $newConfigFile = Join-Path $CloudflaredDir "config-fixed.yml"
    $configContent | Out-File -FilePath $newConfigFile -Encoding UTF8
    Write-ColorOutput "Configuration optimisee creee: config-fixed.yml" "Green"
    
} else {
    Write-ColorOutput "Aucun fichier de credentials trouve (*.json)" "Red"
}

# 7. Test with basic configuration first
Write-ColorOutput "Test de connexion avec configuration de base..." "Yellow"
$basicConfigFile = Join-Path $CloudflaredDir "config-basic.yml"
$basicConfig = @"
# Configuration basique pour test
protocol: quic
grace-period: 30s
retries: 3
loglevel: debug
"@

$basicConfig | Out-File -FilePath $basicConfigFile -Encoding UTF8
Write-ColorOutput "Configuration basique creee pour test" "Green"

# 8. Create startup scripts
Write-ColorOutput "Creation des scripts de demarrage..." "Yellow"

# Script de test rapide
$testScript = @"
# UMan API - Test Cloudflared Rapide
Write-Host "Test de connexion Cloudflared..." -ForegroundColor Cyan

# Arreter les processus existants
Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force

# Test avec configuration basique
Write-Host "Demarrage avec configuration basique..." -ForegroundColor Yellow
& cloudflared.exe tunnel --config `"$basicConfigFile`" run
"@

$testScript | Out-File -FilePath "test-cloudflared-basic.ps1" -Encoding UTF8

# Script de production
$prodScript = @"
# UMan API - Cloudflared Production
Write-Host "Demarrage du tunnel Cloudflared optimise..." -ForegroundColor Cyan

# Arreter les processus existants
Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force

# Demarrer avec configuration optimisee
if (Test-Path `"$newConfigFile`") {
    Write-Host "Utilisation de la configuration optimisee..." -ForegroundColor Green
    & cloudflared.exe tunnel --config `"$newConfigFile`" run
} else {
    Write-Host "Configuration optimisee non trouvee, utilisation de la configuration par defaut..." -ForegroundColor Yellow
    & cloudflared.exe tunnel run umanapi
}
"@

$prodScript | Out-File -FilePath "start-cloudflared-optimized.ps1" -Encoding UTF8

Write-ColorOutput "Scripts de demarrage crees:" "Green"
Write-ColorOutput "  - test-cloudflared-basic.ps1 (test)" "Gray"
Write-ColorOutput "  - start-cloudflared-optimized.ps1 (production)" "Gray"

# 9. System diagnostics
Write-ColorOutput "Diagnostics systeme..." "Yellow"
Write-ColorOutput "OS: $((Get-WmiObject Win32_OperatingSystem).Caption)" "Gray"
Write-ColorOutput "PowerShell: $($PSVersionTable.PSVersion)" "Gray"
Write-ColorOutput "Date/Heure: $(Get-Date)" "Gray"

# 10. DNS flush
Write-ColorOutput "Nettoyage du cache DNS..." "Yellow"
try {
    & ipconfig /flushdns | Out-Null
    Write-ColorOutput "Cache DNS nettoye" "Green"
} catch {
    Write-ColorOutput "Impossible de nettoyer le cache DNS" "Yellow"
}

Write-ColorOutput "" "White"
Write-ColorOutput "RESUME DES ACTIONS:" "Cyan"
Write-ColorOutput "1. Processus cloudflared arretes" "White"
Write-ColorOutput "2. Service desinstalle" "White"
Write-ColorOutput "3. Connectivite reseau testee" "White"
Write-ColorOutput "4. Configuration optimisee creee" "White"
Write-ColorOutput "5. Scripts de demarrage generes" "White"
Write-ColorOutput "" "White"
Write-ColorOutput "PROCHAINES ETAPES:" "Yellow"
Write-ColorOutput "1. Test rapide: .\test-cloudflared-basic.ps1" "Green"
Write-ColorOutput "2. Si le test fonctionne: .\start-cloudflared-optimized.ps1" "Green"
Write-ColorOutput "3. Testez vos domaines: https://uman-api.com" "Green"
Write-ColorOutput "" "White"
Write-ColorOutput "Diagnostic termine!" "Cyan"
