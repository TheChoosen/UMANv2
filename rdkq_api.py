
from flask import Blueprint, request, jsonify, current_app, session
import os, json, sqlite3, hashlib, secrets

rdkq_api = Blueprint('rdkq_api', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'uman.db')

# --- Authentification et sessions ---

def hash_password(password):
    """Hasher un mot de passe avec un salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password, stored_hash):
    """Vérifier un mot de passe"""
    try:
        salt, hashed = stored_hash.split('$')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hashed
    except:
        return False

def ensure_password_column():
    """Ajouter la colonne password si elle n'existe pas"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('ALTER TABLE users ADD COLUMN password TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà
    conn.close()

@rdkq_api.route('/rdkq/api/session', methods=['GET'])
def get_session():
    """Vérifier la session active"""
    if 'member_id' in session:
        ensure_users_table()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, prenom, nom, email, organisation, telephone FROM users WHERE id=?', (session['member_id'],))
        row = c.fetchone()
        conn.close()
        
        if row:
            member = dict(zip(['id','prenom','nom','email','organisation','telephone'], row))
            return jsonify(success=True, member=member)
    
    return jsonify(success=False)

@rdkq_api.route('/rdkq/api/login', methods=['POST'])
def login():
    """Connexion membre"""
    ensure_users_table()
    ensure_password_column()
    
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    
    if not email or not password:
        return jsonify(success=False, error="Email et mot de passe requis")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, prenom, nom, email, organisation, telephone, password FROM users WHERE email=? AND active=1', (email,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return jsonify(success=False, error="Membre non trouvé ou inactif")
    
    # Si pas de mot de passe défini, utiliser "password123" par défaut
    stored_password = row[6] if row[6] else hash_password("password123")
    
    if verify_password(password, stored_password) or (not row[6] and password == "password123"):
        member = dict(zip(['id','prenom','nom','email','organisation','telephone'], row[:6]))
        session['member_id'] = member['id']
        return jsonify(success=True, member=member)
    else:
        return jsonify(success=False, error="Mot de passe incorrect")

@rdkq_api.route('/rdkq/api/logout', methods=['POST'])
def logout():
    """Déconnexion"""
    session.pop('member_id', None)
    return jsonify(success=True)

# Statistiques du membre
@rdkq_api.route('/rdkq/api/membres/<int:id>/stats', methods=['GET'])
def get_member_stats(id):
    """Obtenir les statistiques d'un membre"""
    ensure_users_table()
    ensure_cercles_table()
    ensure_decisions_table()
    ensure_publications_table()
    ensure_adhesions_table()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Compter les cercles
    c.execute('SELECT COUNT(*) FROM membre_cercles WHERE membre_id=?', (id,))
    cercles_count = c.fetchone()[0]
    
    # Compter les publications
    c.execute('SELECT prenom, nom FROM users WHERE id=?', (id,))
    membre = c.fetchone()
    if membre:
        auteur_name = f"{membre[0]} {membre[1]}"
        c.execute('SELECT COUNT(*) FROM publications WHERE auteur LIKE ?', (f'%{auteur_name}%',))
        publications_count = c.fetchone()[0]
    else:
        publications_count = 0
    
    # Compter les décisions votées
    c.execute('SELECT COUNT(*) FROM votes WHERE membre_id=?', (id,))
    decisions_count = c.fetchone()[0]
    
    # Compter les adhésions
    c.execute('SELECT COUNT(*) FROM adhesions WHERE membre_id=?', (id,))
    adhesions_count = c.fetchone()[0]
    
    conn.close()
    
    stats = {
        'cercles': cercles_count,
        'publications': publications_count,
        'decisions': decisions_count,
        'adhesions': adhesions_count
    }
    
    return jsonify(success=True, stats=stats)

# Cercles d'un membre
@rdkq_api.route('/rdkq/api/membres/<int:id>/cercles', methods=['GET'])
def get_member_cercles(id):
    """Obtenir les cercles d'un membre"""
    ensure_cercles_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT c.id, c.nom, c.description, c.statut
        FROM cercles c
        JOIN membre_cercles mc ON c.id = mc.cercle_id
        WHERE mc.membre_id = ?
    ''', (id,))
    
    rows = c.fetchall()
    cercles = [dict(zip(['id', 'nom', 'description', 'statut'], row)) for row in rows]
    
    conn.close()
    return jsonify(cercles)

# Rôles d'un membre
@rdkq_api.route('/rdkq/api/membres/<int:id>/roles', methods=['GET'])
def get_member_roles(id):
    """Obtenir les rôles d'un membre"""
    ensure_roles_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT r.id, r.nom, r.permissions, r.niveau
        FROM roles r
        JOIN membre_roles mr ON r.id = mr.role_id
        WHERE mr.membre_id = ?
    ''', (id,))
    
    rows = c.fetchall()
    roles = [dict(zip(['id', 'nom', 'permissions', 'niveau'], row)) for row in rows]
    
    conn.close()
    return jsonify(roles)

# Paramètres du membre
@rdkq_api.route('/rdkq/api/membres/<int:id>/settings', methods=['PUT'])
def update_member_settings(id):
    """Mettre à jour les paramètres d'un membre"""
    ensure_users_table()
    ensure_password_column()
    
    data = request.form
    prenom = data.get('prenom', '').strip()
    nom = data.get('nom', '').strip()
    email = data.get('email', '').strip().lower()
    telephone = data.get('telephone', '').strip()
    organisation = data.get('organisation', '').strip()
    password = data.get('password', '').strip()
    
    if not (prenom and nom and email):
        return jsonify(ok=False, error="Champs obligatoires manquants")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        if password:
            # Mettre à jour avec nouveau mot de passe
            hashed_password = hash_password(password)
            c.execute('''UPDATE users SET prenom=?, nom=?, email=?, telephone=?, organisation=?, password=? 
                        WHERE id=?''', (prenom, nom, email, telephone, organisation, hashed_password, id))
        else:
            # Mettre à jour sans changer le mot de passe
            c.execute('''UPDATE users SET prenom=?, nom=?, email=?, telephone=?, organisation=? 
                        WHERE id=?''', (prenom, nom, email, telephone, organisation, id))
        
        conn.commit()
        conn.close()
        
        member = {
            'id': id,
            'prenom': prenom,
            'nom': nom,
            'email': email,
            'telephone': telephone,
            'organisation': organisation
        }
        
        return jsonify(ok=True, member=member)
        
    except sqlite3.IntegrityError:
        return jsonify(ok=False, error="Email déjà utilisé")
    except Exception as e:
        return jsonify(ok=False, error=str(e))

# Décisions disponibles pour vote
@rdkq_api.route('/rdkq/api/decisions/available', methods=['GET'])
def get_available_decisions():
    """Obtenir les décisions ouvertes au vote"""
    ensure_decisions_table()
    member_id = session.get('member_id')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if member_id:
        # Avec les votes du membre
        c.execute('''
            SELECT d.id, d.titre, d.type, d.description, d.date_vote, d.statut, v.vote as member_vote
            FROM decisions d
            LEFT JOIN votes v ON d.id = v.decision_id AND v.membre_id = ?
            WHERE d.statut = 'en_cours'
            ORDER BY d.date_vote DESC
        ''', (member_id,))
    else:
        # Sans les votes
        c.execute('''
            SELECT id, titre, type, description, date_vote, statut, NULL as member_vote
            FROM decisions
            WHERE statut = 'en_cours'
            ORDER BY date_vote DESC
        ''')
    
    rows = c.fetchall()
    decisions = [dict(zip(['id', 'titre', 'type', 'description', 'date_vote', 'statut', 'member_vote'], row)) for row in rows]
    
    conn.close()
    return jsonify(decisions)

# Enregistrer un vote
@rdkq_api.route('/rdkq/api/votes', methods=['POST'])
def submit_vote():
    """Enregistrer le vote d'un membre"""
    ensure_decisions_table()
    
    membre_id = request.form.get('membre_id')
    decision_id = request.form.get('decision_id')
    vote = request.form.get('vote')
    commentaire = request.form.get('commentaire', '')
    
    if not all([membre_id, decision_id, vote]):
        return jsonify(ok=False, error="Paramètres manquants")
    
    if vote not in ['pour', 'contre', 'abstention']:
        return jsonify(ok=False, error="Vote invalide")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Vérifier si le vote existe déjà
        c.execute('SELECT id FROM votes WHERE membre_id=? AND decision_id=?', (membre_id, decision_id))
        existing = c.fetchone()
        
        if existing:
            # Mettre à jour le vote existant
            c.execute('UPDATE votes SET vote=?, date_vote=CURRENT_TIMESTAMP WHERE membre_id=? AND decision_id=?', 
                     (vote, membre_id, decision_id))
        else:
            # Créer un nouveau vote
            c.execute('INSERT INTO votes (membre_id, decision_id, vote) VALUES (?, ?, ?)', 
                     (membre_id, decision_id, vote))
        
        conn.commit()
        conn.close()
        
        return jsonify(ok=True)
        
    except Exception as e:
        return jsonify(ok=False, error=str(e))

# --- CRUD Membres (users) ---
def ensure_users_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prenom TEXT,
        nom TEXT,
        email TEXT UNIQUE,
        organisation TEXT,
        telephone TEXT,
        cercles TEXT,
        roles TEXT,
        active INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Table de liaison membre-cercles
    c.execute('''CREATE TABLE IF NOT EXISTS membre_cercles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        membre_id INTEGER,
        cercle_id INTEGER,
        date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (membre_id) REFERENCES users (id),
        FOREIGN KEY (cercle_id) REFERENCES cercles (id)
    )''')
    
    # Table de liaison membre-rôles
    c.execute('''CREATE TABLE IF NOT EXISTS membre_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        membre_id INTEGER,
        role_id INTEGER,
        date_attribution TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (membre_id) REFERENCES users (id),
        FOREIGN KEY (role_id) REFERENCES roles (id)
    )''')
    
    # Table des votes sur les décisions
    c.execute('''CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        membre_id INTEGER,
        decision_id INTEGER,
        vote TEXT CHECK(vote IN ('pour', 'contre', 'abstention')),
        date_vote TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (membre_id) REFERENCES users (id),
        FOREIGN KEY (decision_id) REFERENCES decisions (id)
    )''')
    
    conn.commit()
    conn.close()

def ensure_membres_table():
    """Créer la table membres spécifique RDKQ avec champs étendus"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS membres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prenom TEXT NOT NULL,
        nom TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        organisation TEXT,
        telephone TEXT,
        password_hash TEXT,
        statut TEXT DEFAULT 'actif',
        niveau_acces INTEGER DEFAULT 1,
        date_adhesion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        derniere_connexion TIMESTAMP,
        bio TEXT,
        competences TEXT,
        localisation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def ensure_participations_table():
    """Créer la table participations pour les événements et activités"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS participations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        membre_id INTEGER NOT NULL,
        type_participation TEXT NOT NULL,
        titre TEXT NOT NULL,
        description TEXT,
        lieu TEXT,
        date_debut TIMESTAMP,
        date_fin TIMESTAMP,
        statut TEXT DEFAULT 'inscrit',
        points_gagne INTEGER DEFAULT 0,
        commentaire TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (membre_id) REFERENCES membres (id)
    )''')
    conn.commit()
    conn.close()

# Liste des membres avec leurs cercles et rôles
@rdkq_api.route('/rdkq/api/membres', methods=['GET'])
def api_get_membres():
    ensure_users_table()
    ensure_cercles_table()
    ensure_roles_table()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Récupérer les membres avec leurs cercles et rôles
    c.execute('''
        SELECT u.id, u.prenom, u.nom, u.email, u.organisation, u.telephone,
               GROUP_CONCAT(DISTINCT cc.nom) as cercles,
               GROUP_CONCAT(DISTINCT r.nom) as roles
        FROM users u
        LEFT JOIN membre_cercles mc ON u.id = mc.membre_id
        LEFT JOIN cercles cc ON mc.cercle_id = cc.id
        LEFT JOIN membre_roles mr ON u.id = mr.membre_id
        LEFT JOIN roles r ON mr.role_id = r.id
        GROUP BY u.id
        ORDER BY u.id DESC
    ''')
    
    rows = c.fetchall()
    membres = []
    for row in rows:
        membre = {
            'id': row[0],
            'prenom': row[1],
            'nom': row[2], 
            'email': row[3],
            'organisation': row[4],
            'telephone': row[5],
            'cercles': row[6] or '',
            'roles': row[7] or ''
        }
        membres.append(membre)
    
    conn.close()
    return jsonify(membres)

# Un membre avec ses cercles et rôles
@rdkq_api.route('/rdkq/api/membres/<int:id>', methods=['GET'])
def api_get_membre(id):
    ensure_users_table()
    ensure_cercles_table()
    ensure_roles_table()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Récupérer le membre
    c.execute('SELECT id, prenom, nom, email, organisation, telephone FROM users WHERE id=?', (id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({'ok': False, 'error': 'Not found'}), 404
    
    membre = dict(zip(['id','prenom','nom','email','organisation','telephone'], row))
    
    # Récupérer les cercles du membre
    c.execute('SELECT cercle_id FROM membre_cercles WHERE membre_id=?', (id,))
    cercles_ids = [str(row[0]) for row in c.fetchall()]
    membre['cercles'] = ','.join(cercles_ids)
    
    # Récupérer les rôles du membre
    c.execute('SELECT role_id FROM membre_roles WHERE membre_id=?', (id,))
    roles_ids = [str(row[0]) for row in c.fetchall()]
    membre['roles'] = ','.join(roles_ids)
    
    conn.close()
    return jsonify(membre)

# Créer membre avec cercles et rôles
@rdkq_api.route('/rdkq/api/membres', methods=['POST'])
def api_create_membre():
    ensure_users_table()
    ensure_password_column()
    data = request.form
    prenom = data.get('prenom','').strip()
    nom = data.get('nom','').strip()
    email = data.get('email','').strip().lower()
    organisation = data.get('organisation','').strip()
    telephone = data.get('telephone','').strip()
    password = data.get('password','').strip()
    cercles = data.get('cercles', '').strip()
    roles = data.get('roles', '').strip()
    
    if not (prenom and nom and email):
        return jsonify(ok=False, error="Champs obligatoires manquants"), 400
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Hacher le mot de passe si fourni
        hashed_password = hash_password(password) if password else None
        
        # Créer le membre
        c.execute('INSERT INTO users (prenom, nom, email, organisation, telephone, password, active) VALUES (?, ?, ?, ?, ?, ?, 1)',
                  (prenom, nom, email, organisation, telephone, hashed_password))
        membre_id = c.lastrowid
        
        # Ajouter les cercles
        if cercles:
            cercle_ids = [int(cid) for cid in cercles.split(',') if cid.strip().isdigit()]
            for cercle_id in cercle_ids:
                c.execute('INSERT INTO membre_cercles (membre_id, cercle_id) VALUES (?, ?)', (membre_id, cercle_id))
        
        # Ajouter les rôles
        if roles:
            role_ids = [int(rid) for rid in roles.split(',') if rid.strip().isdigit()]
            for role_id in role_ids:
                c.execute('INSERT INTO membre_roles (membre_id, role_id) VALUES (?, ?)', (membre_id, role_id))
        
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except sqlite3.IntegrityError:
        return jsonify(ok=False, error="Email déjà utilisé"), 400
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

# Modifier membre avec cercles et rôles
@rdkq_api.route('/rdkq/api/membres/<int:id>', methods=['PUT'])
def api_update_membre(id):
    ensure_users_table()
    ensure_password_column()
    data = request.form
    prenom = data.get('prenom','').strip()
    nom = data.get('nom','').strip()
    email = data.get('email','').strip().lower()
    organisation = data.get('organisation','').strip()
    telephone = data.get('telephone','').strip()
    password = data.get('password','').strip()
    cercles = data.get('cercles', '').strip()
    roles = data.get('roles', '').strip()
    
    if not (prenom and nom and email):
        return jsonify(ok=False, error="Champs obligatoires manquants"), 400
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Mettre à jour le membre
        if password:
            # Avec nouveau mot de passe
            hashed_password = hash_password(password)
            c.execute('UPDATE users SET prenom=?, nom=?, email=?, organisation=?, telephone=?, password=? WHERE id=?',
                      (prenom, nom, email, organisation, telephone, hashed_password, id))
        else:
            # Sans changer le mot de passe
            c.execute('UPDATE users SET prenom=?, nom=?, email=?, organisation=?, telephone=? WHERE id=?',
                      (prenom, nom, email, organisation, telephone, id))
        
        # Supprimer les anciennes associations
        c.execute('DELETE FROM membre_cercles WHERE membre_id=?', (id,))
        c.execute('DELETE FROM membre_roles WHERE membre_id=?', (id,))
        
        # Ajouter les nouveaux cercles
        if cercles:
            cercle_ids = [int(cid) for cid in cercles.split(',') if cid.strip().isdigit()]
            for cercle_id in cercle_ids:
                c.execute('INSERT INTO membre_cercles (membre_id, cercle_id) VALUES (?, ?)', (id, cercle_id))
        
        # Ajouter les nouveaux rôles
        if roles:
            role_ids = [int(rid) for rid in roles.split(',') if rid.strip().isdigit()]
            for role_id in role_ids:
                c.execute('INSERT INTO membre_roles (membre_id, role_id) VALUES (?, ?)', (id, role_id))
        
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except sqlite3.IntegrityError:
        return jsonify(ok=False, error="Email déjà utilisé"), 400
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

# Supprimer membre
@rdkq_api.route('/rdkq/api/membres/<int:id>', methods=['DELETE'])
def api_delete_membre(id):
    ensure_users_table()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Supprimer les associations
        c.execute('DELETE FROM membre_cercles WHERE membre_id=?', (id,))
        c.execute('DELETE FROM membre_roles WHERE membre_id=?', (id,))
        c.execute('DELETE FROM votes WHERE membre_id=?', (id,))
        
        # Supprimer le membre
        c.execute('DELETE FROM users WHERE id=?', (id,))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

# Historique des décisions d'un membre
@rdkq_api.route('/rdkq/api/membres/<int:id>/decisions', methods=['GET'])
def api_get_membre_decisions(id):
    ensure_decisions_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT d.id, d.titre, d.type, d.statut, d.date_vote, v.vote
        FROM decisions d
        LEFT JOIN votes v ON d.id = v.decision_id AND v.membre_id = ?
        ORDER BY d.date_vote DESC
    ''', (id,))
    
    rows = c.fetchall()
    decisions = []
    for row in rows:
        decision = {
            'id': row[0],
            'titre': row[1],
            'type': row[2],
            'statut': row[3],
            'date_vote': row[4],
            'vote': row[5] or 'abstention'
        }
        decisions.append(decision)
    
    conn.close()
    return jsonify(decisions)

# Historique des adhésions d'un membre
@rdkq_api.route('/rdkq/api/membres/<int:id>/adhesions', methods=['GET'])
def api_get_membre_adhesions(id):
    ensure_adhesions_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT type, date_debut, date_fin, statut FROM adhesions WHERE membre_id = ? ORDER BY date_debut DESC', (id,))
    rows = c.fetchall()
    adhesions = [dict(zip(['type', 'date_debut', 'date_fin', 'statut'], row)) for row in rows]
    
    conn.close()
    return jsonify(adhesions)

# Historique des publications d'un membre
@rdkq_api.route('/rdkq/api/membres/<int:id>/publications', methods=['GET'])
def api_get_membre_publications(id):
    ensure_publications_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Nous recherchons par auteur (nom du membre)
    c.execute('SELECT prenom, nom FROM users WHERE id = ?', (id,))
    membre = c.fetchone()
    if not membre:
        return jsonify([])
    
    auteur_name = f"{membre[0]} {membre[1]}"
    
    c.execute('''
        SELECT titre, type, created_at, statut, 
               CASE WHEN LENGTH(contenu) > 100 THEN LENGTH(contenu)/50 ELSE 10 END as vues
        FROM publications 
        WHERE auteur LIKE ? 
        ORDER BY created_at DESC
    ''', (f'%{auteur_name}%',))
    
    rows = c.fetchall()
    publications = [dict(zip(['titre', 'type', 'created_at', 'statut', 'vues'], row)) for row in rows]
    
    conn.close()
    return jsonify(publications)

# Participation form submission
@rdkq_api.route('/rdkq/submit-form', methods=['POST'])
def submit_form():
    nom = request.form.get('nom', '').strip()
    email = request.form.get('email', '').strip()
    sujet = request.form.get('sujet', '').strip()
    message = request.form.get('message', '').strip()
    rgpd = request.form.get('rgpd', '')
    if not (nom and email and sujet and message and rgpd):
        return jsonify(success=False, message="Champs obligatoires manquants"), 400
    # Save to DB (simple)
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS participations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT, email TEXT, sujet TEXT, message TEXT, rgpd INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('INSERT INTO participations (nom, email, sujet, message, rgpd) VALUES (?, ?, ?, ?, ?)',
                  (nom, email, sujet, message, int(bool(rgpd))))
        conn.commit()
        conn.close()
    except Exception as e:
        return jsonify(success=False, message=f"Erreur serveur: {e}"), 500
    return jsonify(success=True, message="Participation enregistrée. Merci !")

# Profile search (dummy)
@rdkq_api.route('/rdkq/profile-search', methods=['GET'])
def search_profile():
    query = request.args.get('q', '').strip().lower()
    # Demo: always return a fake profile
    if query == 'paul':
        return jsonify(results=[{"nom": "Paul Lynes", "proprietes": ["Maison", "Voiture"]}])
    return jsonify(results=[])

# Mediatheque (from static JSON)
@rdkq_api.route('/rdkq/media', methods=['GET'])
def get_media():
    path = os.path.join(current_app.root_path, 'static', 'RepubliqueduKwebec', 'mediaContent.json')
    if not os.path.exists(path):
        return jsonify([])
    with open(path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    return jsonify(content)

# --- CRUD CERCLES ---
def ensure_cercles_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cercles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        description TEXT,
        statut TEXT DEFAULT 'actif',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

@rdkq_api.route('/rdkq/api/cercles', methods=['GET'])
def api_get_cercles():
    ensure_cercles_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, nom, description, statut FROM cercles ORDER BY id DESC')
    rows = c.fetchall()
    cercles = [dict(zip(['id','nom','description','statut'], row)) for row in rows]
    # Ajouter nb_membres simulé
    for cercle in cercles:
        cercle['nb_membres'] = 0  # À implémenter avec une vraie relation
    conn.close()
    return jsonify(cercles)

@rdkq_api.route('/rdkq/api/cercles/<int:id>', methods=['GET'])
def api_get_cercle(id):
    ensure_cercles_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, nom, description, statut FROM cercles WHERE id=?', (id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'ok': False, 'error': 'Not found'}), 404
    cercle = dict(zip(['id','nom','description','statut'], row))
    return jsonify(cercle)

@rdkq_api.route('/rdkq/api/cercles', methods=['POST'])
def api_create_cercle():
    ensure_cercles_table()
    data = request.form
    nom = data.get('nom','').strip()
    description = data.get('description','').strip()
    statut = data.get('statut','actif')
    if not nom:
        return jsonify(ok=False, error="Nom requis"), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO cercles (nom, description, statut) VALUES (?, ?, ?)',
                  (nom, description, statut))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@rdkq_api.route('/rdkq/api/cercles/<int:id>', methods=['PUT'])
def api_update_cercle(id):
    ensure_cercles_table()
    data = request.form
    nom = data.get('nom','').strip()
    description = data.get('description','').strip()
    statut = data.get('statut','actif')
    if not nom:
        return jsonify(ok=False, error="Nom requis"), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE cercles SET nom=?, description=?, statut=? WHERE id=?',
                  (nom, description, statut, id))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@rdkq_api.route('/rdkq/api/cercles/<int:id>', methods=['DELETE'])
def api_delete_cercle(id):
    ensure_cercles_table()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM cercles WHERE id=?', (id,))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

# --- CRUD ROLES ---
def ensure_roles_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        permissions TEXT,
        niveau INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

@rdkq_api.route('/rdkq/api/roles', methods=['GET'])
def api_get_roles():
    ensure_roles_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, nom, permissions, niveau FROM roles ORDER BY niveau DESC, id DESC')
    rows = c.fetchall()
    roles = [dict(zip(['id','nom','permissions','niveau'], row)) for row in rows]
    conn.close()
    return jsonify(roles)

@rdkq_api.route('/rdkq/api/roles/<int:id>', methods=['GET'])
def api_get_role(id):
    ensure_roles_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, nom, permissions, niveau FROM roles WHERE id=?', (id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'ok': False, 'error': 'Not found'}), 404
    role = dict(zip(['id','nom','permissions','niveau'], row))
    return jsonify(role)

@rdkq_api.route('/rdkq/api/roles', methods=['POST'])
def api_create_role():
    ensure_roles_table()
    data = request.form
    nom = data.get('nom','').strip()
    permissions = data.get('permissions','').strip()
    niveau = int(data.get('niveau', 1))
    if not nom:
        return jsonify(ok=False, error="Nom requis"), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO roles (nom, permissions, niveau) VALUES (?, ?, ?)',
                  (nom, permissions, niveau))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@rdkq_api.route('/rdkq/api/roles/<int:id>', methods=['PUT'])
def api_update_role(id):
    ensure_roles_table()
    data = request.form
    nom = data.get('nom','').strip()
    permissions = data.get('permissions','').strip()
    niveau = int(data.get('niveau', 1))
    if not nom:
        return jsonify(ok=False, error="Nom requis"), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE roles SET nom=?, permissions=?, niveau=? WHERE id=?',
                  (nom, permissions, niveau, id))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@rdkq_api.route('/rdkq/api/roles/<int:id>', methods=['DELETE'])
def api_delete_role(id):
    ensure_roles_table()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM roles WHERE id=?', (id,))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

# --- CRUD DECISIONS ---
def ensure_decisions_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        description TEXT,
        type TEXT DEFAULT 'vote_simple',
        statut TEXT DEFAULT 'en_cours',
        date_vote TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

@rdkq_api.route('/rdkq/api/decisions', methods=['GET'])
def api_get_decisions():
    ensure_decisions_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, titre, description, type, statut, date_vote FROM decisions ORDER BY id DESC')
    rows = c.fetchall()
    decisions = [dict(zip(['id','titre','description','type','statut','date_vote'], row)) for row in rows]
    conn.close()
    return jsonify(decisions)

@rdkq_api.route('/rdkq/api/decisions/<int:id>', methods=['GET'])
def api_get_decision(id):
    ensure_decisions_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, titre, description, type, statut, date_vote FROM decisions WHERE id=?', (id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'ok': False, 'error': 'Not found'}), 404
    decision = dict(zip(['id','titre','description','type','statut','date_vote'], row))
    return jsonify(decision)

@rdkq_api.route('/rdkq/api/decisions', methods=['POST'])
def api_create_decision():
    ensure_decisions_table()
    data = request.form
    titre = data.get('titre','').strip()
    description = data.get('description','').strip()
    type_decision = data.get('type','vote_simple')
    statut = data.get('statut','en_cours')
    date_vote = data.get('date_vote','')
    if not titre:
        return jsonify(ok=False, error="Titre requis"), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO decisions (titre, description, type, statut, date_vote) VALUES (?, ?, ?, ?, ?)',
                  (titre, description, type_decision, statut, date_vote))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@rdkq_api.route('/rdkq/api/decisions/<int:id>', methods=['PUT'])
def api_update_decision(id):
    ensure_decisions_table()
    data = request.form
    titre = data.get('titre','').strip()
    description = data.get('description','').strip()
    type_decision = data.get('type','vote_simple')
    statut = data.get('statut','en_cours')
    date_vote = data.get('date_vote','')
    if not titre:
        return jsonify(ok=False, error="Titre requis"), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE decisions SET titre=?, description=?, type=?, statut=?, date_vote=? WHERE id=?',
                  (titre, description, type_decision, statut, date_vote, id))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@rdkq_api.route('/rdkq/api/decisions/<int:id>', methods=['DELETE'])
def api_delete_decision(id):
    ensure_decisions_table()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM decisions WHERE id=?', (id,))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

# --- CRUD ADHESIONS ---
def ensure_adhesions_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS adhesions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        membre_id INTEGER NOT NULL,
        type TEXT DEFAULT 'standard',
        date_debut TEXT,
        date_fin TEXT,
        statut TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

@rdkq_api.route('/rdkq/api/adhesions', methods=['GET'])
def api_get_adhesions():
    ensure_adhesions_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT a.id, a.membre_id, a.type, a.date_debut, a.date_fin, a.statut,
                        u.prenom || ' ' || u.nom as membre_nom
                 FROM adhesions a 
                 LEFT JOIN users u ON a.membre_id = u.id
                 ORDER BY a.id DESC''')
    rows = c.fetchall()
    adhesions = [dict(zip(['id','membre_id','type','date_debut','date_fin','statut','membre_nom'], row)) for row in rows]
    conn.close()
    return jsonify(adhesions)

@rdkq_api.route('/rdkq/api/adhesions/<int:id>', methods=['GET'])
def api_get_adhesion(id):
    ensure_adhesions_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, membre_id, type, date_debut, date_fin, statut FROM adhesions WHERE id=?', (id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'ok': False, 'error': 'Not found'}), 404
    adhesion = dict(zip(['id','membre_id','type','date_debut','date_fin','statut'], row))
    return jsonify(adhesion)

@rdkq_api.route('/rdkq/api/adhesions', methods=['POST'])
def api_create_adhesion():
    ensure_adhesions_table()
    data = request.form
    membre_id = data.get('membre_id','')
    type_adhesion = data.get('type','standard')
    date_debut = data.get('date_debut','')
    date_fin = data.get('date_fin','')
    statut = data.get('statut','active')
    if not membre_id or not date_debut:
        return jsonify(ok=False, error="Membre et date de début requis"), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO adhesions (membre_id, type, date_debut, date_fin, statut) VALUES (?, ?, ?, ?, ?)',
                  (int(membre_id), type_adhesion, date_debut, date_fin, statut))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@rdkq_api.route('/rdkq/api/adhesions/<int:id>', methods=['PUT'])
def api_update_adhesion(id):
    ensure_adhesions_table()
    data = request.form
    membre_id = data.get('membre_id','')
    type_adhesion = data.get('type','standard')
    date_debut = data.get('date_debut','')
    date_fin = data.get('date_fin','')
    statut = data.get('statut','active')
    if not membre_id or not date_debut:
        return jsonify(ok=False, error="Membre et date de début requis"), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE adhesions SET membre_id=?, type=?, date_debut=?, date_fin=?, statut=? WHERE id=?',
                  (int(membre_id), type_adhesion, date_debut, date_fin, statut, id))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@rdkq_api.route('/rdkq/api/adhesions/<int:id>', methods=['DELETE'])
def api_delete_adhesion(id):
    ensure_adhesions_table()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM adhesions WHERE id=?', (id,))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

# --- CRUD PUBLICATIONS ---
def ensure_publications_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS publications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        contenu TEXT,
        type TEXT DEFAULT 'article',
        auteur TEXT,
        auteur_id INTEGER,
        cercle_id INTEGER,
        statut TEXT DEFAULT 'brouillon',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(auteur_id) REFERENCES users(id),
        FOREIGN KEY(cercle_id) REFERENCES cercles(id)
    )''')
    
    # Ajouter les colonnes manquantes si elles n'existent pas
    try:
        c.execute('ALTER TABLE publications ADD COLUMN auteur_id INTEGER')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    
    try:
        c.execute('ALTER TABLE publications ADD COLUMN cercle_id INTEGER')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    
    conn.close()

def is_member_of_circle(user_id, circle_id):
    """Vérifier si un utilisateur est membre d'un cercle"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT 1 FROM membre_cercles WHERE membre_id=? AND cercle_id=?', (user_id, circle_id))
    result = c.fetchone()
    conn.close()
    return bool(result)

def get_current_user():
    """Obtenir l'utilisateur connecté"""
    if 'member_id' not in session:
        return None
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, prenom, nom, email FROM users WHERE id=?', (session['member_id'],))
    row = c.fetchone()
    conn.close()
    
    if row:
        return dict(zip(['id', 'prenom', 'nom', 'email'], row))
    return None

@rdkq_api.route('/rdkq/api/publications', methods=['GET'])
def api_get_publications():
    ensure_publications_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT p.id, p.titre, p.contenu, p.type, p.auteur, p.auteur_id, p.cercle_id, 
                        p.statut, p.created_at, c.nom as cercle_nom 
                 FROM publications p 
                 LEFT JOIN cercles c ON p.cercle_id = c.id 
                 ORDER BY p.id DESC''')
    rows = c.fetchall()
    publications = [dict(zip(['id','titre','contenu','type','auteur','auteur_id','cercle_id',
                             'statut','created_at','cercle_nom'], row)) for row in rows]
    conn.close()
    return jsonify(publications)

@rdkq_api.route('/rdkq/api/publications', methods=['POST'])
def api_create_publication():
    ensure_publications_table()
    
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Authentification requise'}), 401
    
    data = request.get_json() or {}
    titre = (data.get('titre') or '').strip()
    contenu = (data.get('contenu') or '').strip()
    type_pub = data.get('type', 'article')
    cercle_id = data.get('cercle_id')
    
    if not titre or not contenu:
        return jsonify({'message': 'Titre et contenu requis'}), 400
    
    # Vérifier que l'utilisateur est membre du cercle si spécifié
    if cercle_id:
        try:
            cercle_id = int(cercle_id)
            if not is_member_of_circle(user['id'], cercle_id):
                return jsonify({'message': 'Vous n\'êtes pas membre de ce cercle'}), 403
        except (ValueError, TypeError):
            return jsonify({'message': 'ID de cercle invalide'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    auteur_nom = f"{user['prenom']} {user['nom']}"
    
    c.execute('''INSERT INTO publications (titre, contenu, type, auteur, auteur_id, cercle_id, statut) 
                 VALUES (?, ?, ?, ?, ?, ?, 'publie')''',
              (titre, contenu, type_pub, auteur_nom, user['id'], cercle_id))
    
    conn.commit()
    publication_id = c.lastrowid
    conn.close()
    
    return jsonify({'id': publication_id, 'message': 'Publication créée avec succès'}), 201

@rdkq_api.route('/rdkq/api/publications/<int:id>', methods=['GET'])
def api_get_publication(id):
    ensure_publications_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, titre, contenu, type, auteur, statut FROM publications WHERE id=?', (id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'ok': False, 'error': 'Not found'}), 404
    publication = dict(zip(['id','titre','contenu','type','auteur','statut'], row))
    return jsonify(publication)

@rdkq_api.route('/rdkq/api/publications/<int:id>', methods=['PUT'])
def api_update_publication(id):
    ensure_publications_table()
    
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Authentification requise'}), 401
    
    data = request.get_json() or {}
    titre = (data.get('titre') or '').strip()
    contenu = (data.get('contenu') or '').strip()
    type_pub = data.get('type', 'article')
    cercle_id = data.get('cercle_id')
    
    if not titre or not contenu:
        return jsonify({'message': 'Titre et contenu requis'}), 400
    
    # Vérifier que l'utilisateur est membre du cercle si spécifié
    if cercle_id:
        try:
            cercle_id = int(cercle_id)
            if not is_member_of_circle(user['id'], cercle_id):
                return jsonify({'message': 'Vous n\'êtes pas membre de ce cercle'}), 403
        except (ValueError, TypeError):
            return jsonify({'message': 'ID de cercle invalide'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Vérifier que la publication appartient à l'utilisateur
    c.execute('SELECT auteur_id FROM publications WHERE id=?', (id,))
    row = c.fetchone()
    if not row or row[0] != user['id']:
        conn.close()
        return jsonify({'message': 'Publication non trouvée ou accès non autorisé'}), 404
    
    c.execute('''UPDATE publications SET titre=?, contenu=?, type=?, cercle_id=? WHERE id=?''',
              (titre, contenu, type_pub, cercle_id, id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'ok': True, 'message': 'Publication mise à jour'})

@rdkq_api.route('/rdkq/api/publications/<int:id>', methods=['DELETE'])
def api_delete_publication(id):
    ensure_publications_table()
    
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Authentification requise'}), 401
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Vérifier que la publication appartient à l'utilisateur
    c.execute('SELECT auteur_id FROM publications WHERE id=?', (id,))
    row = c.fetchone()
    if not row or row[0] != user['id']:
        conn.close()
        return jsonify({'message': 'Publication non trouvée ou accès non autorisé'}), 404
    
    c.execute('DELETE FROM publications WHERE id=?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'ok': True, 'message': 'Publication supprimée'})

def init_demo_data():
    """Initialiser des données de démonstration riches pour Adam Menard"""
    ensure_all_tables()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Créer Adam Menard avec un profil riche et mot de passe
    adam_password = hash_password("demo123")
    c.execute('''INSERT OR REPLACE INTO users (id, prenom, nom, email, organisation, telephone, password) 
                 VALUES (1, "Adam", "Menard", "adam@rdkq.org", "République du Kwébec", "514-555-0101", ?)''', (adam_password,))
    
    # Ajouter plus de cercles
    cercles_demo = [
        (1, "Conseil Exécutif", "Organe décisionnel principal de la République"),
        (2, "Commission Économique", "Développement économique durable et innovation"),
        (3, "Commission Sociale", "Politique sociale, santé et éducation"),
        (4, "Commission Environnementale", "Protection environnementale et transition écologique"),
        (5, "Commission Technologique", "Innovation numérique et transformation digitale"),
        (6, "Commission Culturelle", "Promotion de la culture kwébécoise"),
        (7, "Commission Internationale", "Relations diplomatiques et coopération")
    ]
    for cercle in cercles_demo:
        c.execute('INSERT OR REPLACE INTO cercles (id, nom, description) VALUES (?, ?, ?)', cercle)
    
    # Ajouter plus de rôles
    roles_demo = [
        (1, "Président", "Chef de l'exécutif de la République"),
        (2, "Vice-Président", "Assistant du président et suppléant"),
        (3, "Commissaire Principal", "Chef de commission spécialisée"),
        (4, "Commissaire", "Membre actif de commission"),
        (5, "Délégué Régional", "Représentant territorial"),
        (6, "Conseiller Expert", "Expert consultatif spécialisé"),
        (7, "Ambassadeur", "Représentant diplomatique")
    ]
    for role in roles_demo:
        c.execute('INSERT OR REPLACE INTO roles (id, nom, description) VALUES (?, ?, ?)', role)
    
    # Assigner Adam à plusieurs cercles et rôles
    membre_cercles = [
        (1, 1),  # Adam dans Conseil Exécutif
        (1, 2),  # Adam dans Commission Économique
        (1, 4),  # Adam dans Commission Environnementale
        (1, 5),  # Adam dans Commission Technologique
        (1, 7),  # Adam dans Commission Internationale
    ]
    for mc in membre_cercles:
        c.execute('INSERT OR REPLACE INTO membre_cercles (membre_id, cercle_id) VALUES (?, ?)', mc)
    
    membre_roles = [
        (1, 1),  # Adam est Président
        (1, 3),  # Adam est Commissaire Principal
        (1, 6),  # Adam est Conseiller Expert
    ]
    for mr in membre_roles:
        c.execute('INSERT OR REPLACE INTO membre_roles (membre_id, role_id) VALUES (?, ?)', mr)
    
    # Ajouter des décisions avec votes d'Adam
    decisions_demo = [
        (1, "Adoption de la Constitution", "Adopter la nouvelle constitution démocratique de la République du Kwébec", "politique", "approuvée", "2025-01-15"),
        (2, "Budget National 2025", "Approuver le budget national pour l'exercice 2025", "économique", "en_discussion", "2025-02-01"),
        (3, "Transition Énergétique", "Stratégie nationale de transition énergétique verte", "environnement", "en_discussion", "2025-02-15"),
        (4, "Réforme Fiscale Progressive", "Modernisation équitable du système fiscal", "économique", "approuvée", "2025-03-01"),
        (5, "Programme Social Universel", "Extension des programmes de protection sociale", "social", "en_discussion", "2025-03-10"),
        (6, "Charte Numérique", "Droits et devoirs dans l'espace numérique", "technologie", "approuvée", "2025-03-20"),
        (7, "Accords Commerciaux", "Nouveaux partenariats commerciaux internationaux", "international", "en_discussion", "2025-04-01")
    ]
    for decision in decisions_demo:
        c.execute('INSERT OR REPLACE INTO decisions (id, titre, description, categorie, statut, date_creation) VALUES (?, ?, ?, ?, ?, ?)', decision)
    
    # Adam a voté sur plusieurs décisions
    votes_demo = [
        (1, 1, "pour", "2025-01-15"),
        (1, 2, "pour", "2025-02-20"),
        (1, 4, "pour", "2025-03-10"),
        (1, 6, "pour", "2025-03-25"),
    ]
    for vote in votes_demo:
        c.execute('INSERT OR REPLACE INTO votes (membre_id, decision_id, vote, date_vote) VALUES (?, ?, ?, ?)', vote)
    
    # Ajouter des publications riches d'Adam
    publications_demo = [
        (1, 1, "Vision 2030 pour la République", "Notre vision d'une République moderne, démocratique et prospère qui place le citoyen au centre de toutes les décisions. Un projet ambitieux pour bâtir ensemble l'avenir du Kwébec.", "politique", "2025-01-10"),
        (2, 1, "Économie Circulaire et Innovation", "Proposition détaillée pour une transition complète vers une économie circulaire et durable au Kwébec, créant des emplois verts et de la prospérité partagée.", "économique", "2025-02-05"),
        (3, 1, "Révolution Technologique Responsable", "L'importance cruciale de l'innovation technologique dans notre développement national, tout en préservant nos valeurs humaines et notre souveraineté numérique.", "technologie", "2025-02-28"),
        (4, 1, "Diplomatie Progressive", "Stratégie de développement de partenariats avec d'autres nations progressistes pour un monde plus juste et durable.", "international", "2025-03-15"),
        (5, 1, "Éducation du Futur", "Réforme éducative complète pour préparer nos citoyens aux défis du 21e siècle tout en préservant notre identité culturelle.", "éducation", "2025-03-22"),
        (6, 1, "Transition Écologique Juste", "Plan national pour une transition écologique qui ne laisse personne derrière et crée de nouvelles opportunités pour tous.", "environnement", "2025-04-02"),
        (7, 1, "Démocratie Participative 2.0", "Modernisation de nos institutions démocratiques avec les outils numériques pour une participation citoyenne renforcée.", "politique", "2025-04-10")
    ]
    for pub in publications_demo:
        c.execute('INSERT OR REPLACE INTO publications (id, membre_id, titre, contenu, categorie, date_publication) VALUES (?, ?, ?, ?, ?, ?)', pub)
    
    # Ajouter des adhésions d'Adam avec historique
    adhesions_demo = [
        (1, 1, 1, "2024-06-15"),  # Adam a adhéré au Conseil Exécutif
        (2, 1, 2, "2024-07-01"),  # Adam a adhéré à la Commission Économique
        (3, 1, 4, "2024-08-15"),  # Adam a adhéré à la Commission Environnementale
        (4, 1, 5, "2025-01-10"),  # Adam a adhéré à la Commission Technologique
        (5, 1, 7, "2025-02-20"),  # Adam a adhéré à la Commission Internationale
    ]
    for adhesion in adhesions_demo:
        c.execute('INSERT OR REPLACE INTO adhesions (id, membre_id, cercle_id, date_adhesion) VALUES (?, ?, ?, ?)', adhesion)
    
    # Ajouter des participations d'Adam
    participations_demo = [
        (1, 1, "conférence", "Sommet de la Démocratie Numérique", "Participation au sommet international sur la démocratie numérique", "Montréal", "2025-01-20", "2025-01-22", "complété", 50, "Excellente participation, présentation remarquée"),
        (2, 1, "atelier", "Atelier Innovation Économique", "Animation d'un atelier sur l'économie circulaire", "Québec", "2025-02-10", "2025-02-10", "complété", 30, "Animation très appréciée des participants"),
        (3, 1, "formation", "Formation Leadership Démocratique", "Formation avancée sur le leadership dans les institutions démocratiques", "En ligne", "2025-03-01", "2025-03-05", "complété", 40, "Certification obtenue avec distinction"),
        (4, 1, "mission", "Mission Diplomatique", "Rencontre avec délégations internationales", "Ottawa", "2025-03-25", "2025-03-27", "complété", 60, "Négociations fructueuses, accords signés"),
        (5, 1, "événement", "Forum Citoyen", "Organisation du forum citoyen annuel", "Sherbrooke", "2025-04-15", "2025-04-16", "planifié", 0, "En préparation, forte participation attendue")
    ]
    for participation in participations_demo:
        c.execute('INSERT OR REPLACE INTO participations (id, membre_id, type_participation, titre, description, lieu, date_debut, date_fin, statut, points_gagne, commentaire) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', participation)
    
    conn.commit()
    conn.close()
    print("✅ Données de démonstration initialisées pour Adam Menard")

# --- CRUD Participations ---

@rdkq_api.route('/rdkq/api/participations', methods=['GET'])
def api_get_participations():
    ensure_participations_table()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''SELECT p.*, u.prenom, u.nom 
                     FROM participations p 
                     LEFT JOIN users u ON p.membre_id = u.id 
                     ORDER BY p.date_debut DESC''')
        rows = c.fetchall()
        conn.close()
        
        participations = []
        for row in rows:
            participations.append({
                'id': row[0],
                'membre_id': row[1],
                'type_participation': row[2],
                'titre': row[3],
                'description': row[4],
                'lieu': row[5],
                'date_debut': row[6],
                'date_fin': row[7],
                'statut': row[8],
                'points_gagne': row[9],
                'commentaire': row[10],
                'created_at': row[11],
                'membre_nom': f"{row[12]} {row[13]}" if row[12] and row[13] else "Inconnu"
            })
        
        return jsonify(participations)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@rdkq_api.route('/rdkq/api/participations', methods=['POST'])
def api_create_participation():
    ensure_participations_table()
    data = request.get_json()
    
    membre_id = data.get('membre_id')
    type_participation = data.get('type_participation', '').strip()
    titre = data.get('titre', '').strip()
    description = data.get('description', '').strip()
    lieu = data.get('lieu', '').strip()
    date_debut = data.get('date_debut')
    date_fin = data.get('date_fin')
    statut = data.get('statut', 'inscrit')
    points_gagne = data.get('points_gagne', 0)
    commentaire = data.get('commentaire', '').strip()
    
    if not (membre_id and type_participation and titre):
        return jsonify(ok=False, error="Membre ID, type et titre requis"), 400
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO participations 
                     (membre_id, type_participation, titre, description, lieu, date_debut, date_fin, statut, points_gagne, commentaire)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (membre_id, type_participation, titre, description, lieu, date_debut, date_fin, statut, points_gagne, commentaire))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@rdkq_api.route('/rdkq/api/participations/<int:id>', methods=['DELETE'])
def api_delete_participation(id):
    ensure_participations_table()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM participations WHERE id=?', (id,))
        conn.commit()
        conn.close()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@rdkq_api.route('/rdkq/api/membres/<int:membre_id>/participations', methods=['GET'])
def api_get_membre_participations(membre_id):
    """Récupérer les participations d'un membre spécifique"""
    ensure_participations_table()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''SELECT * FROM participations 
                     WHERE membre_id = ? 
                     ORDER BY date_debut DESC''', (membre_id,))
        rows = c.fetchall()
        conn.close()
        
        participations = []
        for row in rows:
            participations.append({
                'id': row[0],
                'membre_id': row[1],
                'type_participation': row[2],
                'titre': row[3],
                'description': row[4],
                'lieu': row[5],
                'date_debut': row[6],
                'date_fin': row[7],
                'statut': row[8],
                'points_gagne': row[9],
                'commentaire': row[10],
                'created_at': row[11]
            })
        
        return jsonify(participations)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@rdkq_api.route('/rdkq/api/init-demo', methods=['POST'])
def init_demo_route():
    """Route pour initialiser les données de démonstration"""
    try:
        init_demo_data()
        return jsonify(success=True, message="Données de démonstration initialisées avec succès")
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

# Fonction utilitaire pour s'assurer que toutes les tables existent
def ensure_all_tables():
    ensure_users_table()
    ensure_membres_table()
    ensure_cercles_table()
    ensure_roles_table()
    ensure_decisions_table()
    ensure_adhesions_table()
    ensure_publications_table()
    ensure_participations_table()
    ensure_password_column()
