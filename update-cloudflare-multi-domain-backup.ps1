# Script pour configurer le tunnel avec plusieurs domaines

$TunnelID = "28561e3a-b70d-47e4-84ea-e86ffd20e358"
$TunnelName = "umanapi"
$Port = 8002
$UserProfile = "C:\Users\amena"
$CloudflaredDir = Join-Path $UserProfile ".cloudflared"
$CredFile = Join-Path $CloudflaredDir ("$TunnelID.json")
$ConfigFile = Join-Path $CloudflaredDir "config.yml"

Write-Host "Configuration multi-domaines pour le tunnel..." -ForegroundColor Cyan

# Nouvelle configuration avec les deux domaines
$configYaml = @"
# Configuration Cloudflare Tunnel multi-domaines
# Tunnel: $TunnelID
# Domaines: uman-api.com et peupleun.live

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

Set-Content -Path $ConfigFile -Value $configYaml -Encoding UTF8
Write-Host "Configuration multi-domaines mise a jour" -ForegroundColor Green

# Afficher la configuration
Write-Host "`nConfiguration active:" -ForegroundColor Yellow
Get-Content $ConfigFile

Write-Host "`nAjout des routes DNS..." -ForegroundColor Cyan

# Ajouter les routes DNS pour les deux domaines
try {
    Write-Host "Ajout de la route pour peupleun.live..." -ForegroundColor Yellow
    cloudflared tunnel route dns $TunnelName peupleun.live
    Write-Host "Route DNS ajoutee pour peupleun.live" -ForegroundColor Green
} catch {
    Write-Warning "Echec de l'ajout de la route peupleun.live : $($_.Exception.Message)"
}

try {
    Write-Host "Ajout de la route pour *.peupleun.live..." -ForegroundColor Yellow
    cloudflared tunnel route dns $TunnelName "*.peupleun.live"
    Write-Host "Route DNS ajoutee pour *.peupleun.live" -ForegroundColor Green
} catch {
    Write-Warning "Echec de l'ajout de la route *.peupleun.live : $($_.Exception.Message)"
}

# Vérifier que uman-api.com existe déjà
try {
    Write-Host "Verification de la route pour uman-api.com..." -ForegroundColor Yellow
    cloudflared tunnel route dns $TunnelName uman-api.com
    Write-Host "Route DNS confirmee pour uman-api.com" -ForegroundColor Green
} catch {
    Write-Host "Route uman-api.com deja configuree" -ForegroundColor Blue
}

try {
    Write-Host "Ajout de la route pour www.uman-api.com..." -ForegroundColor Yellow
    cloudflared tunnel route dns $TunnelName "www.uman-api.com"
    Write-Host "Route DNS ajoutee pour www.uman-api.com" -ForegroundColor Green
} catch {
    Write-Warning "Echec de l'ajout de la route www.uman-api.com : $($_.Exception.Message)"
}

try {
    Write-Host "Ajout de la route pour www.peupleun.live..." -ForegroundColor Yellow
    cloudflared tunnel route dns $TunnelName "www.peupleun.live"
    Write-Host "Route DNS ajoutee pour www.peupleun.live" -ForegroundColor Green
} catch {
    Write-Warning "Echec de l'ajout de la route www.peupleun.live : $($_.Exception.Message)"
}

try {
    Write-Host "Ajout de la route pour *.uman-api.com..." -ForegroundColor Yellow
    cloudflared tunnel route dns $TunnelName "*.uman-api.com"
    Write-Host "Route DNS ajoutee pour *.uman-api.com" -ForegroundColor Green
} catch {
    Write-Warning "Echec de l'ajout de la route *.uman-api.com : $($_.Exception.Message)"
}

# Afficher les routes configurées
Write-Host "`nVerification des routes DNS..." -ForegroundColor Cyan
try {
    cloudflared tunnel route ip show
} catch {
    Write-Host "Impossible d'afficher les routes" -ForegroundColor Yellow
}

Write-Host "`nConfiguration terminee!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green

Write-Host "`nPROCHAINES ETAPES:" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "`n1. 🚀 Demarrer l'application Flask:" -ForegroundColor Yellow
Write-Host "   cd W:\UMANAPI" -ForegroundColor White
Write-Host "   python app.py" -ForegroundColor Cyan

Write-Host "`n2. 🌐 Demarrer le tunnel Cloudflare:" -ForegroundColor Yellow
Write-Host "   cloudflared tunnel run $TunnelName" -ForegroundColor Cyan

Write-Host "`n3. 🧪 Tester vos sites:" -ForegroundColor Yellow
Write-Host "   - https://uman-api.com" -ForegroundColor Cyan
Write-Host "   - https://www.uman-api.com" -ForegroundColor Cyan
Write-Host "   - https://peupleun.live" -ForegroundColor Cyan
Write-Host "   - https://www.peupleun.live" -ForegroundColor Cyan
Write-Host "   - https://admin.uman-api.com" -ForegroundColor Cyan
Write-Host "   - https://rdkq.peupleun.live" -ForegroundColor Cyan

Write-Host "`n4. 🔧 Demarrage automatique (optionnel):" -ForegroundColor Yellow
Write-Host "   Executez le script: .\start-app.ps1" -ForegroundColor Cyan

Write-Host "`nDOMAINES CONFIGURES:" -ForegroundColor Green
Write-Host "- uman-api.com (principal + sous-domaines)" -ForegroundColor White
Write-Host "- peupleun.live (principal + sous-domaines)" -ForegroundColor White