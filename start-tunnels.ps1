# Script de démarrage complet pour les tunnels Cloudflare et l'application Flask
# Auteur: Assistant
# Date: $(Get-Date)

param(
    [switch]$ConfigureOnly,  # Seulement configurer sans démarrer
    [switch]$StartOnly       # Seulement démarrer sans reconfigurer
)

# Configuration
$TunnelID = "28561e3a-b70d-47e4-84ea-e86ffd20e358"
$TunnelName = "umanapi"
$Port = 8002
$UserProfile = "C:\Users\amena"
$CloudflaredDir = Join-Path $UserProfile ".cloudflared"
$CredFile = Join-Path $CloudflaredDir ("$TunnelID.json")
$ConfigFile = Join-Path $CloudflaredDir "config.yml"
$AppPath = "W:\UMANAPI"

Write-Host "🚀 DÉMARRAGE DES TUNNELS CLOUDFLARE" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "=" * 60 -ForegroundColor Cyan

# Fonction pour vérifier si un processus fonctionne
function Test-ProcessRunning {
    param([string]$ProcessName)
    return (Get-Process -Name $ProcessName -ErrorAction SilentlyContinue) -ne $null
}

# Fonction pour vérifier si un port est utilisé
function Test-PortInUse {
    param([int]$Port)
    $connection = netstat -an | Select-String ":$Port "
    return $connection -ne $null
}

# Étape 1: Vérifier l'état actuel
Write-Host "`n📊 VÉRIFICATION DE L'ÉTAT ACTUEL" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow

# Vérifier le service Cloudflared
$CloudflaredService = Get-Service -Name "cloudflared" -ErrorAction SilentlyContinue
if ($CloudflaredService) {
    Write-Host "✅ Service Cloudflared: $($CloudflaredService.Status)" -ForegroundColor Green
} else {
    Write-Host "❌ Service Cloudflared: Non installé" -ForegroundColor Red
    exit 1
}

# Vérifier si l'application Flask fonctionne
if (Test-PortInUse -Port $Port) {
    Write-Host "✅ Application Flask: En cours d'exécution sur le port $Port" -ForegroundColor Green
    $FlaskRunning = $true
} else {
    Write-Host "⚠️  Application Flask: Non démarrée" -ForegroundColor Yellow
    $FlaskRunning = $false
}

# Vérifier les tunnels Cloudflare
if (Test-ProcessRunning -ProcessName "cloudflared") {
    Write-Host "✅ Tunnels Cloudflare: En cours d'exécution" -ForegroundColor Green
    $TunnelsRunning = $true
} else {
    Write-Host "⚠️  Tunnels Cloudflare: Non démarrés" -ForegroundColor Yellow
    $TunnelsRunning = $false
}

# Étape 2: Configuration (si nécessaire)
if (-not $StartOnly) {
    Write-Host "`n⚙️  CONFIGURATION DES TUNNELS" -ForegroundColor Yellow
    Write-Host "-" * 40 -ForegroundColor Yellow
    
    # Créer le répertoire s'il n'existe pas
    if (-not (Test-Path $CloudflaredDir)) {
        New-Item -ItemType Directory -Path $CloudflaredDir -Force | Out-Null
        Write-Host "📁 Répertoire Cloudflare créé: $CloudflaredDir" -ForegroundColor Green
    }
    
    # Configuration YAML multi-domaines
    $configYaml = @"
# Configuration Cloudflare Tunnel multi-domaines
# Tunnel: $TunnelID
# Domaines: uman-api.com et peupleun.live
# Généré le: $(Get-Date)

tunnel: $TunnelID
credentials-file: $CredFile

ingress:
  - hostname: uman-api.com
    service: http://127.0.0.1:$Port
  - hostname: www.uman-api.com
    service: http://127.0.0.1:$Port
  - hostname: peupleun.live
    service: http://127.0.0.1:$Port
  - hostname: www.peupleun.live
    service: http://127.0.0.1:$Port
  - hostname: "*.peupleun.live"
    service: http://127.0.0.1:$Port
  - hostname: "*.uman-api.com"
    service: http://127.0.0.1:$Port
  - service: http_status:404

loglevel: info
"@

    # Écrire la configuration
    Set-Content -Path $ConfigFile -Value $configYaml -Encoding UTF8
    Write-Host "✅ Configuration mise à jour: $ConfigFile" -ForegroundColor Green
    
    # Afficher la configuration
    Write-Host "`n📄 Configuration active:" -ForegroundColor Cyan
    Write-Host "-" * 30 -ForegroundColor Gray
    Get-Content $ConfigFile | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
}

# Étape 3: Démarrage de l'application Flask
if (-not $ConfigureOnly -and -not $FlaskRunning) {
    Write-Host "`n🐍 DÉMARRAGE DE L'APPLICATION FLASK" -ForegroundColor Yellow
    Write-Host "-" * 40 -ForegroundColor Yellow
    
    # Aller dans le répertoire de l'application
    Set-Location $AppPath
    
    # Démarrer l'application Flask en arrière-plan
    Write-Host "⚡ Démarrage de l'application Flask..." -ForegroundColor Cyan
    $FlaskJob = Start-Job -ScriptBlock {
        param($AppPath)
        Set-Location $AppPath
        & "W:\UMANAPI\.venv\Scripts\Activate.ps1"
        python app.py
    } -ArgumentList $AppPath
    
    # Attendre que l'application démarre
    $attempts = 0
    $maxAttempts = 10
    do {
        Start-Sleep -Seconds 2
        $attempts++
        Write-Host "   Tentative $attempts/$maxAttempts..." -ForegroundColor Gray
    } while (-not (Test-PortInUse -Port $Port) -and $attempts -lt $maxAttempts)
    
    if (Test-PortInUse -Port $Port) {
        Write-Host "✅ Application Flask démarrée sur http://127.0.0.1:$Port" -ForegroundColor Green
    } else {
        Write-Host "❌ Échec du démarrage de l'application Flask" -ForegroundColor Red
        exit 1
    }
}

# Étape 4: Démarrage des tunnels Cloudflare
if (-not $ConfigureOnly) {
    Write-Host "`n🌐 DÉMARRAGE DES TUNNELS CLOUDFLARE" -ForegroundColor Yellow
    Write-Host "-" * 40 -ForegroundColor Yellow
    
    if ($TunnelsRunning) {
        Write-Host "⚠️  Arrêt des tunnels existants..." -ForegroundColor Yellow
        Stop-Process -Name "cloudflared" -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
    }
    
    # Démarrer le tunnel
    Write-Host "🚀 Démarrage du tunnel '$TunnelName'..." -ForegroundColor Cyan
    $TunnelJob = Start-Job -ScriptBlock {
        param($TunnelName)
        cloudflared tunnel run $TunnelName
    } -ArgumentList $TunnelName
    
    # Attendre un peu pour que le tunnel se connecte
    Start-Sleep -Seconds 5
    
    if (Test-ProcessRunning -ProcessName "cloudflared") {
        Write-Host "✅ Tunnel Cloudflare démarré avec succès" -ForegroundColor Green
    } else {
        Write-Host "❌ Échec du démarrage du tunnel" -ForegroundColor Red
    }
}

# Étape 5: Affichage du statut final
Write-Host "`n📈 STATUT FINAL" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow

if (Test-PortInUse -Port $Port) {
    Write-Host "✅ Application Flask: http://127.0.0.1:$Port" -ForegroundColor Green
} else {
    Write-Host "❌ Application Flask: Non accessible" -ForegroundColor Red
}

if (Test-ProcessRunning -ProcessName "cloudflared") {
    Write-Host "✅ Tunnels Cloudflare: Actifs" -ForegroundColor Green
} else {
    Write-Host "❌ Tunnels Cloudflare: Non actifs" -ForegroundColor Red
}

# Étape 6: URLs de test
Write-Host "`n🌍 URLS DE TEST" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
Write-Host "Local:      http://127.0.0.1:$Port" -ForegroundColor Cyan
Write-Host "Domaine 1:  https://uman-api.com" -ForegroundColor Cyan
Write-Host "Domaine 2:  https://peupleun.live" -ForegroundColor Cyan
Write-Host "WWW 1:      https://www.uman-api.com" -ForegroundColor Cyan
Write-Host "WWW 2:      https://www.peupleun.live" -ForegroundColor Cyan

Write-Host "`n🎯 COMMANDES UTILES" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
Write-Host "Voir les logs Flask:     Get-Job | Receive-Job" -ForegroundColor White
Write-Host "Arrêter Flask:           Get-Job | Stop-Job" -ForegroundColor White
Write-Host "Arrêter les tunnels:     Stop-Process -Name cloudflared" -ForegroundColor White
Write-Host "Redémarrer service:      Restart-Service cloudflared" -ForegroundColor White

Write-Host "`n🎉 DÉMARRAGE TERMINÉ!" -ForegroundColor Green -BackgroundColor Black
Write-Host "=" * 60 -ForegroundColor Green
