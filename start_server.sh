#!/bin/bash

# Script pour démarrer le serveur UMANv2 sur le port 8020
# Auteur: Assistant IA
# Date: $(date)

set -e  # Arrêter le script en cas d'erreur

# Configuration
PROJECT_DIR="/home/amenard/UMANv2/UMANv2"
PYTHON_APP="app.py"
PORT=8020
HOST="127.0.0.1"
VENV_DIR="$PROJECT_DIR/venv"

echo "=========================================="
echo "  Démarrage du serveur UMANv2"
echo "=========================================="
echo "Port: $PORT"
echo "Host: $HOST"
echo "Répertoire: $PROJECT_DIR"
echo "=========================================="

# Vérifier si le port est déjà utilisé
check_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  ATTENTION: Le port $PORT est déjà utilisé!"
        echo "Processus utilisant le port:"
        lsof -Pi :$PORT -sTCP:LISTEN
        echo ""
        read -p "Voulez-vous tuer le processus existant? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🔄 Arrêt du processus sur le port $PORT..."
            lsof -ti:$PORT | xargs kill -9
            echo "✅ Processus arrêté."
        else
            echo "❌ Abandon du démarrage."
            exit 1
        fi
    fi
}

# Aller dans le répertoire du projet
cd "$PROJECT_DIR" || {
    echo "❌ Erreur: Impossible d'accéder au répertoire $PROJECT_DIR"
    exit 1
}

# Vérifier que le fichier app.py existe
if [ ! -f "$PYTHON_APP" ]; then
    echo "❌ Erreur: Le fichier $PYTHON_APP n'existe pas dans $PROJECT_DIR"
    exit 1
fi

# Vérifier le port
check_port

# Créer et activer l'environnement virtuel Python
setup_venv() {
    echo "🐍 Configuration de l'environnement virtuel Python..."
    
    # Vérifier si python3-venv est installé
    if ! python3 -m venv --help >/dev/null 2>&1; then
        echo "⚠️  python3-venv n'est pas installé. Installation..."
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y python3-venv python3-full
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-venv
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-venv
        else
            echo "❌ Impossible d'installer python3-venv automatiquement."
            echo "Veuillez l'installer manuellement: sudo apt install python3-venv python3-full"
            exit 1
        fi
    fi
    
    # Créer l'environnement virtuel s'il n'existe pas
    if [ ! -d "$VENV_DIR" ]; then
        echo "📦 Création de l'environnement virtuel..."
        python3 -m venv "$VENV_DIR"
        echo "✅ Environnement virtuel créé dans $VENV_DIR"
    else
        echo "✅ Environnement virtuel trouvé dans $VENV_DIR"
    fi
    
    # Activer l'environnement virtuel
    source "$VENV_DIR/bin/activate"
    echo "🔄 Environnement virtuel activé"
    
    # Mettre à jour pip dans l'environnement virtuel
    echo "📦 Mise à jour de pip..."
    pip install --upgrade pip --quiet
}

# Configurer l'environnement virtuel
setup_venv

# Configurer l'environnement Python si nécessaire
if [ -f "requirements.txt" ]; then
    echo "📦 Installation des dépendances Python..."
    
    # Installer les requirements avec verbose pour debug
    if pip install -r requirements.txt --quiet; then
        echo "✅ Dépendances installées avec succès"
    else
        echo "⚠️  Erreur lors de l'installation des dépendances, tentative individuellement..."
        
        # Installer les dépendances critiques une par une
        critical_packages=("Flask>=2.0" "mysql-connector-python>=8.0.0" "python-dotenv>=0.21.0")
        
        for package in "${critical_packages[@]}"; do
            echo "📦 Installation de $package..."
            if pip install "$package" --quiet; then
                echo "✅ $package installé"
            else
                echo "❌ Échec de l'installation de $package"
                echo "🔄 Tentative avec --upgrade..."
                pip install "$package" --upgrade --quiet || echo "⚠️  $package toujours en échec"
            fi
        done
        
        # Installer le reste
        echo "📦 Installation des autres dépendances..."
        pip install -r requirements.txt --quiet || echo "⚠️  Certaines dépendances optionnelles ont échoué"
    fi
else
    echo "⚠️  Aucun fichier requirements.txt trouvé"
    echo "📦 Installation des dépendances essentielles..."
    pip install Flask mysql-connector-python python-dotenv --quiet
fi

# Vérifier que les modules critiques sont disponibles
echo "🔍 Vérification des modules critiques..."
$PYTHON_EXEC -c "
try:
    import flask
    print('✅ Flask disponible')
except ImportError:
    print('❌ Flask manquant')

try:
    import mysql.connector
    print('✅ MySQL Connector disponible')
except ImportError:
    print('❌ MySQL Connector manquant')
    
try:
    import os
    print('✅ OS module disponible')
except ImportError:
    print('❌ OS module manquant')
" || echo "⚠️  Problème lors de la vérification des modules"

# Configurer les variables d'environnement
export FLASK_APP="$PYTHON_APP"
export FLASK_DEBUG="1"
export FLASK_ENV="development"

# Fonction pour nettoyer à la sortie
cleanup() {
    echo ""
    echo "🛑 Arrêt du serveur..."
    if [ ! -z "$VIRTUAL_ENV" ]; then
        echo "🔄 Désactivation de l'environnement virtuel..."
        deactivate 2>/dev/null || true
    fi
    echo "✅ Nettoyage terminé"
    exit 0
}

# Capturer Ctrl+C pour nettoyer proprement
trap cleanup SIGINT SIGTERM

echo "🚀 Démarrage du serveur Flask..."
echo "📍 URL d'accès: http://$HOST:$PORT"
echo "🔧 Mode debug activé"
echo "⏹️  Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

# Démarrer le serveur avec le port personnalisé
# On utilise l'environnement virtuel activé
export UMAN_PORT="$PORT"
export UMAN_HOST="$HOST"

# Utiliser Python de l'environnement virtuel
PYTHON_EXEC="$VENV_DIR/bin/python"

echo "🔧 Utilisation de Python: $PYTHON_EXEC"

# Vérifier que l'application peut être importée
echo "🔍 Test d'import de l'application..."
if ! $PYTHON_EXEC -c "
import sys
sys.path.insert(0, '.')
try:
    from app import app
    print('✅ Application importée avec succès')
except Exception as e:
    print(f'❌ Erreur d\\'import: {e}')
    sys.exit(1)
"; then
    echo "❌ Impossible d'importer l'application. Vérifiez les dépendances."
    exit 1
fi

# Démarrer le serveur Flask
echo "🚀 Lancement du serveur Flask..."
$PYTHON_EXEC -c "
import os
import sys
sys.path.insert(0, '.')

try:
    # Importer l'app
    from app import app

    # Configurer le port et host depuis les variables d'environnement
    port = int(os.environ.get('UMAN_PORT', '8020'))
    host = os.environ.get('UMAN_HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'

    print(f'🌐 Serveur démarré sur http://{host}:{port}')
    print('📝 Logs du serveur:')
    print('=' * 50)
    app.run(host=host, port=port, debug=debug)

except KeyboardInterrupt:
    print('\\n🛑 Serveur arrêté par l\\'utilisateur')
except Exception as e:
    print(f'❌ Erreur lors du démarrage: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"
