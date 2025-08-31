# Script de démarrage automatique UMan API + Tunnel Cloudflare
# Ce script démarre l'application Flask et le tunnel multi-domaines

param(
    [switch]$SkipAppCheck,
    [switch]$OnlyTunnel,
    [switch]$OnlyApp
)

$TunnelName = "umanapi"
$Port = 8002

Write-Host "DEMARRAGE UMAN API MULTI-DOMAINES" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "=" * 50 -ForegroundColor Cyan

# Naviguer vers le dossier du projet
Set-Location "W:\UMANAPI"

if (-not $OnlyTunnel) {
    # 1. Vérifier si l'application Flask tourne déjà
    Write-Host "`nVerification de l'application Flask..." -ForegroundColor Yellow
    $portTest = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port -WarningAction SilentlyContinue

    if ($portTest.TcpTestSucceeded) {
    Write-Host "ATTENTION: Le port $Port est deja utilise" -ForegroundColor Yellow
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        foreach ($conn in $connections) {
            $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "   Processus actuel: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor Gray
            }
        }
    Write-Host "OK: Application Flask deja en cours d'execution" -ForegroundColor Green
    } else {
    Write-Host "Demarrage de l'application Flask..." -ForegroundColor Cyan
        
        # Activer l'environnement virtuel
        if (Test-Path ".\.venv\Scripts\Activate.ps1") {
            Write-Host "   Activation de l'environnement virtuel..." -ForegroundColor Gray
            & .\.venv\Scripts\Activate.ps1
        }
        
        # Variables d'environnement
        $env:FLASK_APP = "app.py"
        $env:FLASK_ENV = "production"
        $env:SECRET_KEY = "rdkq_secret_key_2024_change_in_production"
        
        if ($OnlyApp) {
            Write-Host "Demarrage en mode application uniquement..." -ForegroundColor Cyan
            Write-Host "   Accessible sur: http://127.0.0.1:$Port" -ForegroundColor White
            try {
                python app.py
            } catch {
                Write-Host "ERREUR: Demarrage: $($_.Exception.Message)" -ForegroundColor Red
            }
            return
        }
        
        # Démarrer l'application en arrière-plan pour le tunnel
        Write-Host "   Lancement de: python app.py" -ForegroundColor Gray
        $appJob = Start-Job -ScriptBlock {
            Set-Location "W:\UMANAPI"
            $env:FLASK_APP = "app.py"
            $env:FLASK_ENV = "production" 
            $env:SECRET_KEY = "rdkq_secret_key_2024_change_in_production"
            & python app.py
        }
        
        # Attendre que l'app démarre
        $attempts = 0
        $maxAttempts = 15
        Write-Host "   Attente du demarrage" -NoNewline -ForegroundColor Gray
        
        do {
            Start-Sleep -Seconds 2
            Write-Host "." -NoNewline -ForegroundColor Gray
            $portTest = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port -WarningAction SilentlyContinue
            $attempts++
        } while (-not $portTest.TcpTestSucceeded -and $attempts -lt $maxAttempts)
        
        Write-Host ""
        
        if ($portTest.TcpTestSucceeded) {
            Write-Host "OK: Application Flask demarree sur le port $Port" -ForegroundColor Green
        } else {
            Write-Host "ERREUR: Echec du demarrage de l'application apres $maxAttempts tentatives" -ForegroundColor Red
            Write-Host "Demarrez manuellement: python app.py" -ForegroundColor Yellow
            if ($appJob) { Stop-Job $appJob -Force }
            exit 1
        }
    }

    # 2. Test rapide de l'application
    if (-not $SkipAppCheck) {
    Write-Host "`nTest de l'application locale..." -ForegroundColor Yellow
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port" -UseBasicParsing -TimeoutSec 10
            Write-Host "OK: Application locale repond (Status: $($response.StatusCode))" -ForegroundColor Green
        } catch {
            Write-Host "ATTENTION: Application locale ne repond pas completement:" -ForegroundColor Yellow
            Write-Host "   $($_.Exception.Message)" -ForegroundColor Gray
            Write-Host "   Continuation du demarrage du tunnel..." -ForegroundColor Cyan
        }
    }
}

if (-not $OnlyApp) {
    # 3. Vérifier la configuration Cloudflare
    Write-Host "`nVerification de la configuration Cloudflare..." -ForegroundColor Yellow
    $configFile = "$env:USERPROFILE\.cloudflared\config.yml"
    if (-not (Test-Path $configFile)) {
    Write-Host "ERREUR: Configuration Cloudflare introuvable: $configFile" -ForegroundColor Red
    Write-Host "Executez d'abord: .\update-cloudflare-multi-domain.ps1" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "OK: Configuration Cloudflare trouvee" -ForegroundColor Green

    # 4. Afficher les informations avant le démarrage
    Write-Host "`nDOMAINES CONFIGURES:" -ForegroundColor Cyan
    Write-Host "   - https://uman-api.com" -ForegroundColor White
    Write-Host "   - https://peupleun.live" -ForegroundColor White
    Write-Host "   - https://*.uman-api.com" -ForegroundColor Gray
    Write-Host "   - https://*.peupleun.live" -ForegroundColor Gray

    # 5. Démarrer le tunnel Cloudflare
    Write-Host "`nDemarrage du tunnel Cloudflare..." -ForegroundColor Cyan
    Write-Host "   Tunnel: $TunnelName" -ForegroundColor Gray
    Write-Host "   Port local: $Port" -ForegroundColor Gray
    Write-Host "`nConnexion en cours (Ctrl+C pour arreter)..." -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Green

    try {
        & cloudflared tunnel run $TunnelName
    }
    catch {
    Write-Host "`nERREUR: Demarrage du tunnel echoue" -ForegroundColor Red
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Gray
    Write-Host "`nVERIFICATIONS:" -ForegroundColor Yellow
        Write-Host "   - cloudflared installe ?" -ForegroundColor White
        Write-Host "   - Tunnel '$TunnelName' existe ?" -ForegroundColor White
        Write-Host "   - Credentials valides ?" -ForegroundColor White
        exit 1
    }
    finally {
    Write-Host "`nArret du tunnel" -ForegroundColor Yellow
        if ($appJob) {
            Write-Host "Arret de l'application Flask..." -ForegroundColor Yellow
            Stop-Job $appJob -Force
            Remove-Job $appJob -Force
        }
    }
}
