# --- RDKQ (République du Kwébec) minimal site ---
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g, send_from_directory, session
from functools import wraps
import hashlib
import secrets
import os
import smtplib

# Import the API blueprint
from rdkq_api import rdkq_api
from werkzeug.utils import secure_filename

# Import MySQL configuration
from config_mysql import get_mysql_db, close_mysql_db

# create app early so decorators below can reference it

app = Flask(__name__)
app.register_blueprint(rdkq_api)


def is_admin_session():
    return session.get('is_admin')


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not is_admin_session():
            flash('Accès admin requis', 'warning')
            return redirect(url_for('index'))
        return fn(*args, **kwargs)
    return wrapper

@app.route('/rdkq')
def rdkq_index():
    return render_template('RepubliqueduKwebec/index.html')

@app.route('/rdkq/profil')
def rdkq_profil():
    return render_template('RepubliqueduKwebec/profil.html')

@app.route('/rdkq/admin')
def rdkq_admin():
    # Vérifier que l'utilisateur est connecté et admin
    if not session.get('user_id') or not session.get('is_admin'):
        flash('Accès refusé. Vous devez être administrateur pour accéder à cette page.', 'danger')
        return redirect(url_for('rdkq_index'))
    return render_template('RepubliqueduKwebec/admin.html')


@app.route('/rdkq/registre')
def rdkq_registre():
    return render_template('RepubliqueduKwebec/registre.html')


@app.route('/rdkq/login', methods=['GET', 'POST'])
def rdkq_login():
    """Route de connexion spécifique pour RDKQ"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Email et mot de passe requis.', 'danger')
            return render_template('RepubliqueduKwebec/login.html')
        
        # Vérifier si l'utilisateur existe dans la table membres
        db = get_mysql_db()
        cur = db.cursor(dictionary=True)
        cur.execute('SELECT * FROM membres WHERE email = %s', (email,))
        user = cur.fetchone()
        
        if user:
            # Vérifier le mot de passe (hash ou mot de passe temporaire admin)
            password_hash = hash_code(password)
            if (password_hash == user['password']) or (password == 'admin123' and user['is_admin']):
                session['user_id'] = user['id']
                session['user_email'] = user['email']
                session['username'] = user['username']
                session['is_admin'] = bool(user['is_admin'])
                flash('Connexion réussie! Bienvenue dans l\'espace membre RDKQ.', 'success')
                return redirect(url_for('rdkq_index'))
            else:
                flash('Mot de passe incorrect.', 'danger')
        else:
            flash('Aucun compte trouvé avec cette adresse email.', 'danger')
    
    return render_template('RepubliqueduKwebec/login.html')


@app.route('/rdkq/register', methods=['GET', 'POST'])
def rdkq_register():
    """Page d'inscription RDKQ"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        prenom = request.form.get('prenom', '').strip()
        nom = request.form.get('nom', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        password_confirm = request.form.get('password_confirm', '').strip()
        cercle_local = request.form.get('cercle_local', '').strip()
        terms = request.form.get('terms')
        
        # Validation des données
        if not all([prenom, nom, email, password, password_confirm]):
            flash('Tous les champs obligatoires doivent être remplis.', 'danger')
            return render_template('RepubliqueduKwebec/register.html')
        
        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return render_template('RepubliqueduKwebec/register.html')
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères.', 'danger')
            return render_template('RepubliqueduKwebec/register.html')
        
        if not terms:
            flash('Vous devez accepter les conditions d\'utilisation.', 'danger')
            return render_template('RepubliqueduKwebec/register.html')
        
        # Vérifier si l'email existe déjà
        db = get_mysql_db()
        cur = db.cursor(dictionary=True)
        cur.execute('SELECT id FROM membres WHERE email = %s', (email,))
        existing_user = cur.fetchone()
        
        if existing_user:
            flash('Un compte existe déjà avec cette adresse email.', 'danger')
            return render_template('RepubliqueduKwebec/register.html')
        
        # Créer le nouveau membre
        try:
            username = f"{prenom} {nom}"
            # Hash simple du mot de passe (à améliorer en production)
            password_hash = hash_code(password)
            now = datetime.now(timezone.utc).isoformat()
            
            cur.execute('''
                INSERT INTO membres (username, email, password, nom, cercle_local, is_admin, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (username, email, password_hash, nom, cercle_local, 0, now))
            
            db.commit()
            
            flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('rdkq_login'))
            
        except Exception as e:
            flash('Erreur lors de l\'inscription. Veuillez réessayer.', 'danger')
            print(f"Erreur d'inscription: {e}")
            return render_template('RepubliqueduKwebec/register.html')
    
    return render_template('RepubliqueduKwebec/register.html')


# --- BIQ (Bureau Indépendance Québec) skeleton routes ---
@app.route('/biq')
def biq_index():
    return render_template('BIQ/index.html')


@app.route('/biq/prd')
def biq_prd():
    return render_template('BIQ/prd.html')


@app.route('/biq/login', methods=['GET', 'POST'])
def biq_login():
    """Route de connexion pour BIQ"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Email et mot de passe requis.', 'danger')
            return render_template('BIQ/login.html')
        
        # Vérifier si l'utilisateur existe dans la table membres
        db = get_mysql_db()
        cur = db.cursor(dictionary=True)
        cur.execute('SELECT * FROM membres WHERE email = %s', (email,))
        user = cur.fetchone()
        
        if user and verify_password(password, user['password']):
            # Utilisateur authentifié - connexion réussie
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['username'] = user['username'] or user['nom']
            session['is_admin'] = bool(user['is_admin'])
            flash(f'Connexion réussie. Bienvenue {user["nom"]}!', 'success')
            return redirect(url_for('biq_profile'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
    
    return render_template('BIQ/login.html')


@app.route('/biq/register', methods=['GET', 'POST'])
def biq_register():
    """Route d'inscription pour BIQ"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        # Validation des données
        if not all([username, email, password]):
            flash('Tous les champs sont requis.', 'danger')
            return render_template('BIQ/register.html')
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères.', 'danger')
            return render_template('BIQ/register.html')
        
        # Vérifier si l'email ou username existe déjà
        db = get_mysql_db()
        cur = db.cursor(dictionary=True)
        cur.execute('SELECT id FROM membres WHERE email = %s OR username = %s', (email, username))
        existing_user = cur.fetchone()
        
        if existing_user:
            flash('Cet email ou nom d\'utilisateur est déjà utilisé.', 'danger')
            return render_template('BIQ/register.html')
        
        # Créer le nouveau membre
        try:
            # Hacher le mot de passe
            hashed_password = hash_password(password)
            
            cur.execute('''INSERT INTO membres (username, email, password, created_at)
                           VALUES (%s, %s, %s, NOW())''', 
                       (username, email, hashed_password))
            db.commit()
            
            flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('biq_login'))
            
        except Exception as e:
            flash('Erreur lors de l\'inscription. Veuillez réessayer.', 'danger')
            return render_template('BIQ/register.html')
    
    return render_template('BIQ/register.html')


@app.route('/biq/profile')
def biq_profile():
    """Page de profil BIQ - nécessite une connexion"""
    if not session.get('user_id'):
        flash('Vous devez être connecté pour accéder à cette page.', 'warning')
        return redirect(url_for('biq_login'))
    
    # Récupérer les informations utilisateur
    db = get_mysql_db()
    cur = db.cursor(dictionary=True)
    cur.execute('SELECT * FROM membres WHERE id = %s', (session.get('user_id'),))
    user = cur.fetchone()
    
    if not user:
        session.clear()
        flash('Session expirée. Veuillez vous reconnecter.', 'warning')
        return redirect(url_for('biq_login'))
    
    # Statistiques de l'utilisateur
    cur.execute('SELECT COUNT(*) as count FROM signalements WHERE created_by = %s', (user['id'],))
    signalements_count = cur.fetchone()['count']
    
    return render_template('BIQ/profile.html', user=user, signalements_count=signalements_count)


@app.route('/biq/signalement', methods=['GET', 'POST'])
def biq_signalement():
    """Route pour les signalements BIQ - réservée aux membres connectés"""
    if not session.get('user_id'):
        flash('Vous devez être connecté pour déposer un signalement.', 'warning')
        return redirect(url_for('biq_login'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        type_signalement = request.form.get('type', '').strip()
        description = request.form.get('description', '').strip()
        contact = request.form.get('contact', '').strip()
        
        # Validation
        if not all([title, type_signalement, description]):
            flash('Titre, type et description sont requis.', 'danger')
            return render_template('BIQ/signalement.html')
        
        # Enregistrer le signalement
        try:
            db = get_mysql_db()
            cur = db.cursor()
            cur.execute('''INSERT INTO signalements 
                           (title, type, description, contact, created_by, created_at)
                           VALUES (%s, %s, %s, %s, %s, NOW())''', 
                       (title, type_signalement, description, contact, session.get('user_id')))
            db.commit()
            
            flash('Signalement déposé avec succès. Il sera traité par notre équipe.', 'success')
            return redirect(url_for('biq_profile'))
            
        except Exception as e:
            flash('Erreur lors de l\'enregistrement du signalement.', 'danger')
    
    return render_template('BIQ/signalement.html')


@app.route('/biq/mediatheque')
def biq_mediatheque():
    return render_template('BIQ/mediatheque.html')


@app.route('/biq/admin')
@admin_required
def biq_admin_index():
    """Dashboard administrateur BIQ"""
    db = get_mysql_db()
    cur = db.cursor(dictionary=True)
    
    # Statistiques générales
    cur.execute('SELECT COUNT(*) as count FROM membres')
    total_membres = cur.fetchone()['count']
    
    cur.execute('SELECT COUNT(*) as count FROM signalements')
    total_signalements = cur.fetchone()['count']
    
    cur.execute('SELECT COUNT(*) as count FROM signalements WHERE status = "nouveau"')
    nouveaux_signalements = cur.fetchone()['count']
    
    cur.execute('SELECT COUNT(*) as count FROM mediatheque WHERE is_public = 1')
    medias_publics = cur.fetchone()['count']
    
    stats = {
        'total_membres': total_membres,
        'total_signalements': total_signalements,
        'nouveaux_signalements': nouveaux_signalements,
        'medias_publics': medias_publics
    }
    
    return render_template('BIQ/admin_index.html', stats=stats)


@app.route('/biq/admin/users')
@admin_required
def biq_admin_users():
    """Gestion des utilisateurs BIQ"""
    db = get_mysql_db()
    cur = db.cursor(dictionary=True)
    
    # Récupérer tous les membres
    cur.execute('''SELECT id, username, email, nom, is_admin, created_at 
                   FROM membres ORDER BY created_at DESC''')
    users = cur.fetchall()
    
    return render_template('BIQ/admin_users.html', users=users)


@app.route('/biq/admin/signalements')
@admin_required
def biq_admin_signalements():
    """Gestion des signalements BIQ"""
    db = get_mysql_db()
    cur = db.cursor(dictionary=True)
    
    # Récupérer tous les signalements avec info utilisateur
    cur.execute('''SELECT s.*, m.username, m.email, m.nom
                   FROM signalements s
                   LEFT JOIN membres m ON s.created_by = m.id
                   ORDER BY s.created_at DESC''')
    signalements = cur.fetchall()
    
    # Statistiques par statut
    cur.execute('''SELECT status, COUNT(*) as count 
                   FROM signalements 
                   GROUP BY status''')
    stats_status = {row['status']: row['count'] for row in cur.fetchall()}
    
    # Statistiques par type
    cur.execute('''SELECT type, COUNT(*) as count 
                   FROM signalements 
                   GROUP BY type''')
    stats_type = {row['type']: row['count'] for row in cur.fetchall()}
    
    return render_template('BIQ/admin_signalements.html', 
                         signalements=signalements,
                         stats_status=stats_status,
                         stats_type=stats_type)


@app.route('/biq/logout')
def biq_logout():
    """Déconnexion BIQ"""
    username = session.get('username', 'utilisateur')
    session.clear()
    flash(f'Déconnexion réussie. À bientôt {username}!', 'success')
    return redirect(url_for('biq_index'))


@app.route('/rdkq/logout')
def rdkq_logout():
    """Déconnexion RDKQ"""
    session.clear()
    flash('Déconnexion réussie. À bientôt!', 'success')
    return redirect(url_for('rdkq_index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Route de connexion simple pour tester le système admin"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if email:
            # Vérifier si l'utilisateur existe et est actif
            db = get_mysql_db()
            cur = db.cursor(dictionary=True)
            cur.execute('SELECT * FROM membres WHERE email = %s AND is_admin = %s', (email, 1))
            user = cur.fetchone()
            
            if user:
                session['user_id'] = user['id']
                session['user_email'] = user['email']
                session['is_admin'] = bool(user['is_admin'])
                flash('Connexion réussie!', 'success')
                return redirect(url_for('rdkq_index'))
            else:
                flash('Utilisateur non trouvé ou compte non activé.', 'danger')
        else:
            flash('Email requis.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Route de déconnexion"""
    session.clear()
    flash('Déconnexion réussie.', 'success')
    return redirect(url_for('index'))


@app.route('/admin/users', methods=['GET', 'POST'])
def admin_users():
    """Gestion des utilisateurs - réservé aux admins"""
    if not session.get('user_id') or not session.get('is_admin'):
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('rdkq_index'))
    
    db = get_mysql_db()
    cur = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        
        if action == 'toggle_admin' and user_id:
            # Basculer le statut admin
            cur.execute('SELECT is_admin FROM membres WHERE id = %s', (user_id,))
            current_status = cur.fetchone()
            if current_status:
                new_status = 0 if current_status['is_admin'] else 1
                cur.execute('UPDATE membres SET is_admin = %s WHERE id = %s', (new_status, user_id))
                db.commit()
                flash(f'Statut administrateur modifié pour l\'utilisateur ID {user_id}', 'success')
    
    # Récupérer tous les utilisateurs
    cur.execute('SELECT id, username, email, is_admin, created_at FROM membres ORDER BY created_at DESC')
    users = cur.fetchall()
    
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
def admin_edit_user(user_id):
    """Éditer un utilisateur (admin only)"""
    if not session.get('user_id') or not session.get('is_admin'):
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('rdkq_index'))

    db = get_mysql_db()
    cur = db.cursor(dictionary=True)

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        is_admin_flag = 1 if request.form.get('is_admin') else 0
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # validate password if provided
        if password:
            if password != password_confirm:
                flash('Les mots de passe ne correspondent pas.', 'danger')
                # fallthrough to re-render form with existing values
            elif len(password) < 6:
                flash('Le mot de passe doit contenir au moins 6 caractères.', 'danger')
            else:
                # hash and update including password
                try:
                    hashed = hash_code(password)
                    cur.execute('UPDATE membres SET username = %s, email = %s, is_admin = %s, password = %s WHERE id = %s',
                                (username, email, is_admin_flag, hashed, user_id))
                    db.commit()
                    flash('Utilisateur et mot de passe mis à jour.', 'success')
                    return redirect('/admin/users')
                except Exception as e:
                    print(f"Erreur mise à jour utilisateur (with password): {e}")
                    flash('Erreur lors de la mise à jour.', 'danger')
        else:
            # update without changing password
            try:
                cur.execute('UPDATE membres SET username = %s, email = %s, is_admin = %s WHERE id = %s',
                            (username, email, is_admin_flag, user_id))
                db.commit()
                flash('Utilisateur mis à jour.', 'success')
                return redirect('/admin/users')
            except Exception as e:
                print(f"Erreur mise à jour utilisateur: {e}")
                flash('Erreur lors de la mise à jour.', 'danger')

    # GET - récupérer l'utilisateur
    cur.execute('SELECT id, username, email, is_admin FROM membres WHERE id = %s', (user_id,))
    user = cur.fetchone()
    if not user:
        flash('Utilisateur introuvable.', 'danger')
        return redirect('/admin/users')

    return render_template('admin/user_form.html', user=user)

# Formulaire participatif (POST)
@app.route('/rdkq/participer', methods=['POST'])
def rdkq_participer():
    # Handle participatory form: save metadata and optional attachment to App_Data/Uploads
    nom = (request.form.get('nom') or '').strip()
    email = (request.form.get('email') or '').strip().lower()
    sujet = (request.form.get('sujet') or '').strip()
    message = (request.form.get('message') or '').strip()
    rgpd = request.form.get('rgpd')

    if not (nom and email and sujet and message and rgpd):
        return jsonify(ok=False, error="Champs obligatoires manquants"), 400

    # basic upload handling
    attachment = request.files.get('attachment')
    saved_filename = None
    if attachment and attachment.filename:
        # simple size check (5MB default)
        max_size = int(os.environ.get('MAX_UPLOAD_SIZE', str(5 * 1024 * 1024)))
        attachment.stream.seek(0, os.SEEK_END)
        size = attachment.stream.tell()
        attachment.stream.seek(0)
        if size > max_size:
            return jsonify(ok=False, error='Fichier trop volumineux'), 400

        # whitelist common safe extensions (adjust as needed)
        _, ext = os.path.splitext(secure_filename(attachment.filename))
        allowed_ext = {'.pdf', '.png', '.jpg', '.jpeg', '.txt', '.md'}
        if ext.lower() not in allowed_ext:
            return jsonify(ok=False, error='Type de fichier non autorisé'), 400

        uploads_dir = os.path.join(os.path.dirname(__file__), 'App_Data', 'Uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        guid = secrets.token_hex(16)
        saved_filename = f"{guid}{ext.lower()}"
        save_path = os.path.join(uploads_dir, saved_filename)
        # save file
        attachment.save(save_path)

    # persist submission in DB (simple table 'submissions')
    db = get_mysql_db()
    cur = db.cursor()
    now = datetime.now(timezone.utc).isoformat()
    try:
        cur.execute('''INSERT INTO submissions (nom, email, sujet, message, rgpd, attachment, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)''', (nom, email, sujet, message, int(bool(rgpd)), saved_filename, now))
        db.commit()
    except Exception as e:
        logger.exception('Failed to persist submission: %s', e)

    # send confirmation to submitter and notification to admin (best-effort)
    try:
        submission = {
            'nom': nom,
            'email': email,
            'sujet': sujet,
            'message': message,
            'attachment': saved_filename,
            'created_at': now
        }
        send_submission_email(email, submission)
    except Exception:
        logger.exception('Failed to send submission email')

    return jsonify(ok=True)

# Médiathèque (depuis MySQL)
@app.route('/rdkq/mediatheque')
def rdkq_mediatheque():
    """Récupérer les éléments de la médiathèque depuis MySQL"""
    try:
        db = get_mysql_db()
        cur = db.cursor(dictionary=True)
        
        # Récupérer tous les éléments publics de la médiathèque
        cur.execute('''
            SELECT id, title, description as desc, image_url as img, 
                   document_url as src, category, author, is_featured, views_count
            FROM mediatheque 
            WHERE is_public = TRUE 
            ORDER BY is_featured DESC, created_at DESC
        ''')
        
        mediatheque_items = cur.fetchall()
        
        # Convertir en format compatible avec le frontend existant
        formatted_items = []
        for item in mediatheque_items:
            formatted_item = {
                "id": item['id'],
                "title": item['title'],
                "desc": item['desc'] or "",
                "img": item['img'] or "/static/image/default-media.png",
                "src": item['src'] or "",
                "category": item['category'] or "",
                "author": item['author'] or "",
                "is_featured": bool(item['is_featured']),
                "views": item['views_count'] or 0
            }
            formatted_items.append(formatted_item)
        
        return jsonify(formatted_items)
        
    except Exception as e:
        print(f"Erreur lors de la récupération de la médiathèque: {e}")
        # Fallback vers des données statiques en cas d'erreur
        return jsonify([
            {"id": 1, "title": "Documentaire", "desc": "Contenu temporairement indisponible.", 
             "img": "/static/image/Plateforme Construction.png", "src": "#", "category": "info"}
        ])


@app.route('/rdkq/mediatheque/<int:media_id>/view', methods=['POST'])
def rdkq_mediatheque_view(media_id):
    """Incrémenter le compteur de vues d'un élément de médiathèque"""
    try:
        db = get_mysql_db()
        cur = db.cursor()
        
        # Incrémenter le compteur de vues
        cur.execute('UPDATE mediatheque SET views_count = views_count + 1 WHERE id = %s', (media_id,))
        db.commit()
        
        # Récupérer le nouveau nombre de vues
        cur.execute('SELECT views_count FROM mediatheque WHERE id = %s', (media_id,))
        result = cur.fetchone()
        
        if result:
            return jsonify({"ok": True, "views": result[0]})
        else:
            return jsonify({"ok": False, "error": "Media not found"}), 404
            
    except Exception as e:
        print(f"Erreur lors de la mise à jour des vues: {e}")
        return jsonify({"ok": False, "error": "Database error"}), 500


# Routes d'administration pour la médiathèque RDKQ
@app.route('/rdkq/admin/mediatheque')
def rdkq_admin_mediatheque():
    """Page d'administration de la médiathèque RDKQ"""
    if 'user_id' not in session:
        return redirect('/rdkq/login')
    
    # Vérifier si l'utilisateur est admin
    try:
        db = get_mysql_db()
        cur = db.cursor()
        cur.execute('SELECT is_admin FROM membres WHERE id = %s', (session['user_id'],))
        result = cur.fetchone()
        
        if not result or not result[0]:
            return "Accès non autorisé - Seuls les administrateurs peuvent accéder à cette page", 403
            
    except Exception as e:
        print(f"Erreur de vérification admin: {e}")
        return "Erreur de base de données", 500
    
    return render_template('RepubliqueduKwebec/admin/mediatheque.html')


@app.route('/rdkq/admin/mediatheque/data')
def rdkq_admin_mediatheque_data():
    """API pour récupérer les données de la médiathèque avec statistiques"""
    if 'user_id' not in session:
        return jsonify({"ok": False, "error": "Non connecté"}), 401
    
    try:
        db = get_mysql_db()
        cur = db.cursor()
        
        # Vérifier si l'utilisateur est admin
        cur.execute('SELECT is_admin FROM membres WHERE id = %s', (session['user_id'],))
        result = cur.fetchone()
        
        if not result or not result[0]:
            return jsonify({"ok": False, "error": "Accès non autorisé"}), 403
        
        # Récupérer toutes les données de la médiathèque
        cur.execute('''
            SELECT id, title, description, image_url, document_url, category, author, 
                   is_public, is_featured, views_count, created_at, updated_at
            FROM mediatheque 
            ORDER BY created_at DESC
        ''')
        
        columns = [col[0] for col in cur.description]
        media_list = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        # Calculer les statistiques
        stats = {
            "total": len(media_list),
            "public": sum(1 for m in media_list if m['is_public']),
            "featured": sum(1 for m in media_list if m['is_featured']),
            "total_views": sum(m['views_count'] or 0 for m in media_list)
        }
        
        return jsonify({"ok": True, "media": media_list, "stats": stats})
        
    except Exception as e:
        print(f"Erreur lors de la récupération des données admin: {e}")
        return jsonify({"ok": False, "error": "Erreur de base de données"}), 500


@app.route('/rdkq/admin/mediatheque/<int:media_id>/toggle-visibility', methods=['POST'])
def rdkq_admin_toggle_visibility(media_id):
    """Basculer la visibilité d'un média"""
    if 'user_id' not in session:
        return jsonify({"ok": False, "error": "Non connecté"}), 401
    
    try:
        db = get_mysql_db()
        cur = db.cursor()
        
        # Vérifier si l'utilisateur est admin
        cur.execute('SELECT is_admin FROM membres WHERE id = %s', (session['user_id'],))
        result = cur.fetchone()
        
        if not result or not result[0]:
            return jsonify({"ok": False, "error": "Accès non autorisé"}), 403
        
        # Récupérer les données de la requête
        data = request.get_json()
        is_public = data.get('is_public', False)
        
        # Mettre à jour la visibilité
        cur.execute('UPDATE mediatheque SET is_public = %s WHERE id = %s', (is_public, media_id))
        db.commit()
        
        return jsonify({"ok": True})
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour de visibilité: {e}")
        return jsonify({"ok": False, "error": "Erreur de base de données"}), 500


@app.route('/rdkq/admin/mediatheque/<int:media_id>/toggle-featured', methods=['POST'])
def rdkq_admin_toggle_featured(media_id):
    """Basculer le statut vedette d'un média"""
    if 'user_id' not in session:
        return jsonify({"ok": False, "error": "Non connecté"}), 401
    
    try:
        db = get_mysql_db()
        cur = db.cursor()
        
        # Vérifier si l'utilisateur est admin
        cur.execute('SELECT is_admin FROM membres WHERE id = %s', (session['user_id'],))
        result = cur.fetchone()
        
        if not result or not result[0]:
            return jsonify({"ok": False, "error": "Accès non autorisé"}), 403
        
        # Récupérer les données de la requête
        data = request.get_json()
        is_featured = data.get('is_featured', False)
        
        # Mettre à jour le statut vedette
        cur.execute('UPDATE mediatheque SET is_featured = %s WHERE id = %s', (is_featured, media_id))
        db.commit()
        
        return jsonify({"ok": True})
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du statut vedette: {e}")
        return jsonify({"ok": False, "error": "Erreur de base de données"}), 500


@app.route('/rdkq/admin/mediatheque/<int:media_id>', methods=['DELETE'])
def rdkq_admin_delete_media(media_id):
    """Supprimer un média"""
    if 'user_id' not in session:
        return jsonify({"ok": False, "error": "Non connecté"}), 401
    
    try:
        db = get_mysql_db()
        cur = db.cursor()
        
        # Vérifier si l'utilisateur est admin
        cur.execute('SELECT is_admin FROM membres WHERE id = %s', (session['user_id'],))
        result = cur.fetchone()
        
        if not result or not result[0]:
            return jsonify({"ok": False, "error": "Accès non autorisé"}), 403
        
        # Supprimer le média
        cur.execute('DELETE FROM mediatheque WHERE id = %s', (media_id,))
        db.commit()
        
        return jsonify({"ok": True})
        
    except Exception as e:
        print(f"Erreur lors de la suppression: {e}")
        return jsonify({"ok": False, "error": "Erreur de base de données"}), 500


@app.route('/rdkq/admin/mediatheque/new', methods=['GET', 'POST'])
def rdkq_admin_new_media():
    """Créer un nouveau média"""
    if 'user_id' not in session:
        return redirect('/rdkq/login')
    
    # Vérifier si l'utilisateur est admin
    try:
        db = get_mysql_db()
        cur = db.cursor()
        cur.execute('SELECT is_admin FROM membres WHERE id = %s', (session['user_id'],))
        result = cur.fetchone()
        
        if not result or not result[0]:
            return "Accès non autorisé - Seuls les administrateurs peuvent accéder à cette page", 403
    except Exception as e:
        print(f"Erreur de vérification admin: {e}")
        return "Erreur de base de données", 500
    
    if request.method == 'GET':
        return render_template('RepubliqueduKwebec/admin/media_form.html')
    
    # POST - Créer le média
    try:
        data = request.get_json()
        
        # Validation des données requises
        if not data.get('title'):
            return jsonify({"ok": False, "error": "Le titre est requis"}), 400
        
        # Insérer le nouveau média
        cur.execute('''
            INSERT INTO mediatheque (title, description, image_url, document_url, 
                                   category, author, is_public, is_featured, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ''', (
            data.get('title'),
            data.get('description', ''),
            data.get('image_url', ''),
            data.get('document_url', ''),
            data.get('category', ''),
            data.get('author', ''),
            data.get('is_public', True),
            data.get('is_featured', False)
        ))
        
        db.commit()
        return jsonify({"ok": True, "message": "Média créé avec succès"})
        
    except Exception as e:
        print(f"Erreur lors de la création du média: {e}")
        return jsonify({"ok": False, "error": "Erreur de base de données"}), 500


@app.route('/rdkq/admin/mediatheque/<int:media_id>/edit', methods=['GET', 'POST'])
def rdkq_admin_edit_media(media_id):
    """Éditer un média existant"""
    if 'user_id' not in session:
        return redirect('/rdkq/login')
    
    # Vérifier si l'utilisateur est admin
    try:
        db = get_mysql_db()
        cur = db.cursor()
        cur.execute('SELECT is_admin FROM membres WHERE id = %s', (session['user_id'],))
        result = cur.fetchone()
        
        if not result or not result[0]:
            return "Accès non autorisé - Seuls les administrateurs peuvent accéder à cette page", 403
    except Exception as e:
        print(f"Erreur de vérification admin: {e}")
        return "Erreur de base de données", 500
    
    if request.method == 'GET':
        # Récupérer les données du média
        try:
            cur.execute('''
                SELECT id, title, description, image_url, document_url, 
                       category, author, is_public, is_featured
                FROM mediatheque WHERE id = %s
            ''', (media_id,))
            
            result = cur.fetchone()
            if not result:
                return "Média non trouvé", 404
            
            # Convertir en dictionnaire
            columns = [col[0] for col in cur.description]
            media = dict(zip(columns, result))
            
            return render_template('RepubliqueduKwebec/admin/media_form.html', media=media)
            
        except Exception as e:
            print(f"Erreur lors de la récupération du média: {e}")
            return "Erreur de base de données", 500
    
    # POST - Mettre à jour le média
    try:
        data = request.get_json()
        
        # Validation des données requises
        if not data.get('title'):
            return jsonify({"ok": False, "error": "Le titre est requis"}), 400
        
        # Mettre à jour le média
        cur.execute('''
            UPDATE mediatheque 
            SET title = %s, description = %s, image_url = %s, document_url = %s,
                category = %s, author = %s, is_public = %s, is_featured = %s,
                updated_at = NOW()
            WHERE id = %s
        ''', (
            data.get('title'),
            data.get('description', ''),
            data.get('image_url', ''),
            data.get('document_url', ''),
            data.get('category', ''),
            data.get('author', ''),
            data.get('is_public', True),
            data.get('is_featured', False),
            media_id
        ))
        
        db.commit()
        return jsonify({"ok": True, "message": "Média mis à jour avec succès"})
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du média: {e}")
        return jsonify({"ok": False, "error": "Erreur de base de données"}), 500


# Profil public (JSON simulé) - route moved to rdkq_api.py
import os
import hashlib
import secrets
import smtplib
import logging
try:
    import resend
except Exception:
    resend = None

# simple logger for email/provider diagnostics
logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

# Configuration from environment
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
CODE_TTL_MINUTES = int(os.environ.get('UMAN_CODE_TTL_MINUTES', '30'))

# track last email provider and result for health checks
_email_status = {
    'last_provider': None,
    'last_result': None,
    'last_detail': None,
}


def get_db():
    """Compatibilité avec l'ancien code SQLite - remplacé par MySQL"""
    return get_mysql_db()


def init_db():
    """Initialisation de la base de données - MySQL est déjà configuré"""
    # La base de données MySQL est déjà créée via create_mysql_schema.py
    pass


@app.teardown_appcontext
def close_connection(exception):
    """Fermer la connexion MySQL"""
    close_mysql_db()


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode('utf-8')).hexdigest()


def hash_password(password: str) -> str:
    """Hacher un mot de passe avec sel et pbkdf2"""
    import secrets
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"pbkdf2:sha256:100000${salt}${password_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Vérifier un mot de passe contre son hash"""
    if password_hash == 'activated':
        # Ancien système - accepter n'importe quel mot de passe pour les comptes "activated"
        return True
    
    if not password_hash.startswith('pbkdf2:sha256:'):
        # Hash non reconnu
        return False
    
    try:
        # Format: pbkdf2:sha256:100000$salt$hash
        parts = password_hash.split('$')
        if len(parts) != 3:
            return False
            
        algorithm_info, salt, stored_hash = parts
        iterations = int(algorithm_info.split(':')[-1])
        
        password_check = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
        return password_check.hex() == stored_hash
    except Exception as e:
        print(f"Erreur lors de la vérification du mot de passe: {e}")
        return False


def send_code_email(to_email: str, code: str):
    # Prepare rendered email templates (HTML + plain text)
    from_addr = os.environ.get('SMTP_FROM', 'info@uman-api.com')
    html_body = render_template('emails/confirmation.html', code=code, minutes=CODE_TTL_MINUTES, to_email=to_email, from_email=from_addr)
    text_body = render_template('emails/confirmation.txt', code=code, minutes=CODE_TTL_MINUTES, to_email=to_email, from_email=from_addr)

    # If RESEND_API_KEY is provided and the SDK is available, prefer Resend (API)
    resend_api_key = os.environ.get('RESEND_API_KEY')
    if resend_api_key and resend is not None:
        try:
            resend.api_key = resend_api_key
            params = {
                'from': from_addr,
                'to': [to_email],
                'subject': 'Votre code de confirmation UMan',
                'html': html_body,
            }
            # include plain text if SDK supports it (safe to include)
            try:
                params['text'] = text_body
            except Exception:
                pass
            resend.Emails.send(params)
            logger.info('Email sent via Resend to %s', to_email)
            _email_status.update({
                'last_provider': 'resend',
                'last_result': 'ok',
                'last_detail': None,
                'last_ts': datetime.now(timezone.utc).isoformat()
            })
            return
        except Exception as e:
            logger.exception('Resend send failed, will fallback to SMTP/staging: %s', e)
            _email_status.update({
                'last_provider': 'resend',
                'last_result': 'error',
                'last_detail': str(e),
                'last_ts': datetime.now(timezone.utc).isoformat()
            })

    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')

    subject = 'Votre code de confirmation UMan'
    body = f"Bonjour,\n\nVoici votre code de confirmation pour activer votre profil UMan: {code}\n\nCe code est valide pendant {CODE_TTL_MINUTES} minutes.\n\nSi vous n'avez pas demandé ce code, ignorez ce message.\n\nUMan API"

    # Staging mock: if UMAN_ENV=staging write a small file entry instead of sending
    uenv = os.environ.get('UMAN_ENV', '').lower()
    if uenv == 'staging':
        out_dir = os.environ.get('UMAN_STAGING_OUT', os.path.join(os.path.dirname(__file__), 'tmp'))
        os.makedirs(out_dir, exist_ok=True)
        fname = os.path.join(out_dir, f"email_{datetime.now(timezone.utc).isoformat()}.txt")
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(f"To: {to_email}\nSubject: {subject}\n\n{body}\n")
        _email_status.update({
            'last_provider': 'staging',
            'last_result': 'ok',
            'last_detail': fname,
            'last_ts': datetime.now(timezone.utc).isoformat()
        })
        return

    # If SMTP not configured, just print to console (useful for dev)
    if not smtp_host or not smtp_user or not smtp_pass:
        print(f"[UMAN] Would send email to {to_email}: {body}")
        _email_status.update({
            'last_provider': 'console',
            'last_result': 'ok',
            'last_detail': 'console',
            'last_ts': datetime.now(timezone.utc).isoformat()
        })
        return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_email
    msg.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    _email_status.update({
        'last_provider': 'smtp',
        'last_result': 'ok',
        'last_detail': f'{smtp_host}:{smtp_port}',
        'last_ts': datetime.now(timezone.utc).isoformat()
    })


def send_submission_email(to_email: str, submission: dict):
    """Send a confirmation to the submitter and a notification to admin.
    Uses the same provider selection as send_code_email.
    """
    from_addr = os.environ.get('SMTP_FROM', 'info@uman-api.com')
    admin_email = os.environ.get('ADMIN_EMAIL')

    subject_user = f"Confirmation de réception : {submission.get('sujet')}"
    body_user = f"Bonjour {submission.get('nom')},\n\nNous avons bien reçu votre participation (sujet: {submission.get('sujet')}).\n\nMessage:\n{submission.get('message')}\n\nSi un fichier a été joint, il a été reçu et conservé de manière sécurisée.\n\nCordialement,\nRDKQ\n"

    subject_admin = f"Nouvelle participation reçue: {submission.get('sujet')}"
    body_admin = f"Nouvelle soumission de {submission.get('nom')} <{submission.get('email')}>\n\nSujet: {submission.get('sujet')}\nMessage:\n{submission.get('message')}\n\nAttachment: {submission.get('attachment')}\n\nReçu: {submission.get('created_at')}\n"

    # Try Resend first if available
    resend_api_key = os.environ.get('RESEND_API_KEY')
    if resend_api_key and resend is not None:
        try:
            resend.api_key = resend_api_key
            # to user
            resend.Emails.send({'from': from_addr, 'to': [to_email], 'subject': subject_user, 'text': body_user})
            # to admin if configured
            if admin_email:
                resend.Emails.send({'from': from_addr, 'to': [admin_email], 'subject': subject_admin, 'text': body_admin})
            _email_status.update({'last_provider': 'resend', 'last_result': 'ok', 'last_ts': datetime.now(timezone.utc).isoformat()})
            return
        except Exception as e:
            logger.exception('Resend failed for submission email: %s', e)
            _email_status.update({'last_provider': 'resend', 'last_result': 'error', 'last_detail': str(e), 'last_ts': datetime.now(timezone.utc).isoformat()})

    # Staging mock
    uenv = os.environ.get('UMAN_ENV', '').lower()
    if uenv == 'staging':
        out_dir = os.environ.get('UMAN_STAGING_OUT', os.path.join(os.path.dirname(__file__), 'tmp'))
        os.makedirs(out_dir, exist_ok=True)
        fname = os.path.join(out_dir, f"submission_{datetime.now(timezone.utc).isoformat()}.txt")
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(f"To: {to_email}\nSubject: {subject_user}\n\n{body_user}\n\nADMIN:\nTo: {admin_email}\nSubject: {subject_admin}\n\n{body_admin}\n")
        _email_status.update({'last_provider': 'staging', 'last_result': 'ok', 'last_detail': fname, 'last_ts': datetime.now(timezone.utc).isoformat()})
        return

    # Fallback to SMTP or console
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')

    if not smtp_host or not smtp_user or not smtp_pass:
        print(f"[UMAN] Submission email to {to_email}: {body_user}")
        if admin_email:
            print(f"[UMAN] Admin notification to {admin_email}: {body_admin}")
        _email_status.update({'last_provider': 'console', 'last_result': 'ok', 'last_ts': datetime.now(timezone.utc).isoformat()})
        return

    # send via SMTP
    msg = EmailMessage()
    msg['From'] = from_addr
    msg['To'] = to_email
    msg['Subject'] = subject_user
    msg.set_content(body_user)
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

    if admin_email:
        msg2 = EmailMessage()
        msg2['From'] = from_addr
        msg2['To'] = admin_email
        msg2['Subject'] = subject_admin
        msg2.set_content(body_admin)
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg2)

    _email_status.update({'last_provider': 'smtp', 'last_result': 'ok', 'last_detail': f'{smtp_host}:{smtp_port}', 'last_ts': datetime.now(timezone.utc).isoformat()})


@app.before_request
def ensure_db():
    # init DB lazily on first request
    init_db()


@app.before_request
def handle_domain():
    """Gérer les différents domaines (uman-api.com vs peupleun.live).
    Définit `g.current_domain`, `g.site_name`, `g.site_theme` pour templates.
    """
    host = request.headers.get('Host', '').lower()
    if 'peupleun.live' in host:
        g.current_domain = 'peupleun.live'
        g.site_name = 'Peuple Un'
        g.site_theme = 'peupleun'
    else:
        g.current_domain = 'uman-api.com'
        g.site_name = 'UMan API'
        g.site_theme = 'uman'
    
    # Vérifier le statut admin depuis la base de données MySQL
    if session.get('user_id'):
        db = get_mysql_db()
        cur = db.cursor(dictionary=True)
        cur.execute('SELECT is_admin FROM membres WHERE id = %s', (session['user_id'],))
        user = cur.fetchone()
        session['is_admin'] = bool(user['is_admin']) if user else False
    else:
        session['is_admin'] = False


@app.route('/')
def index():
    """Route principale qui redirige selon le domaine"""
    host = request.headers.get('Host', '').lower()
    
    # Gestion du domaine peupleun.live
    if 'peupleun.live' in host:
        return render_template('peupleun/index.html')
    
    # si le domaine est uman-api.com ou par défaut, servir la page principale
    domain = getattr(g, 'current_domain', 'uman-api.com')
    if domain == 'peupleun.live':
        return render_template('RepubliqueduKwebec/index.html')
    return render_template('index.html')


@app.route('/profil')
def profil():
    return render_template('profil.html')


# --- Democratie Directe simple static routes (PRD v1) ---
@app.route('/democratie')
def DemocratieDirecte_index():
    return render_template('DemocratieDirecte/index.html')

@app.route('/democratie/mandats')
def DemocratieDirecte_mandats():
    return render_template('DemocratieDirecte/mandats.html')

@app.route('/democratie/devenir-membre')
def DemocratieDirecte_devenir_membre():
    return render_template('DemocratieDirecte/devenir_membre.html')

@app.route('/democratie/benevole')
def DemocratieDirecte_benevole():
    return render_template('DemocratieDirecte/benevole.html')

@app.route('/democratie/candidature')
def DemocratieDirecte_candidature():
    return render_template('DemocratieDirecte/candidature.html')

@app.route('/democratie/constitution')
def DemocratieDirecte_constitution():
    return render_template('DemocratieDirecte/constitution.html')

@app.route('/democratie/statuts')
def DemocratieDirecte_statuts():
    return render_template('DemocratieDirecte/statuts.html')

@app.route('/democratie/comite')
def DemocratieDirecte_comite():
    return render_template('DemocratieDirecte/comite.html')

@app.route('/democratie/contact')
def DemocratieDirecte_contact():
    return render_template('DemocratieDirecte/contact.html')


@app.route('/democratie/documentation')
def DemocratieDirecte_documentation():
    return render_template('DemocratieDirecte/documentation.html')


@app.route('/democratie/assets/<path:filename>')
def democratie_assets(filename):
    img_dir = os.path.join(os.path.dirname(__file__), 'templates', 'DemocratieDirecte', 'DD')
    # safe serve: ensure path traversal is not permitted by send_from_directory
    return send_from_directory(img_dir, filename, as_attachment=False)


# --- Routes Cyberdémocratie PRD ---
@app.route('/cyberdemocratie')
def cyberdemocratie_index():
    """Page principale du PRD Cyberdémocratie"""
    return render_template('Cyberdemocratie/index.html')


@app.route('/cyberdemocratie/architecture')
def cyberdemocratie_architecture():
    """Architecture technique du système"""
    return render_template('Cyberdemocratie/architecture.html')


@app.route('/cyberdemocratie/user-stories')
def cyberdemocratie_user_stories():
    """User Stories et fonctionnalités"""
    return render_template('Cyberdemocratie/user-stories.html')


@app.route('/cyberdemocratie/roadmap')
def cyberdemocratie_roadmap():
    """Roadmap détaillé sur 6 mois"""
    return render_template('Cyberdemocratie/roadmap.html')


@app.route('/cyberdemocratie/metrics')
def cyberdemocratie_metrics():
    """Métriques et KPIs de performance"""
    return render_template('Cyberdemocratie/metrics.html')


@app.route('/cyberdemocratie/sprint1')
def cyberdemocratie_sprint1():
    """Sprint 1 - Authentification & Accès détaillé"""
    return render_template('Cyberdemocratie/sprint1.html')


# Serve the background image used by the DemocratieDirecte static page
@app.route('/democratie/assets/dd-bg.jpg')
def democratie_bg():
    img_dir = os.path.join(os.path.dirname(__file__), 'templates', 'DemocratieDirecte', 'DD')
    # the file on disk is named 'DD VERSION 1.jpg'
    return send_from_directory(img_dir, 'DD VERSION 1.jpg', as_attachment=False)



@app.route('/health')
def health():
    # If HEALTH_TOKEN is set, require it (Bearer header or ?token=)
    token_required = os.environ.get('HEALTH_TOKEN')
    if token_required:
        # check header
        auth = request.headers.get('Authorization', '')
        provided = None
        if auth.lower().startswith('bearer '):
            provided = auth.split(None, 1)[1].strip()
        if not provided:
            provided = request.args.get('token')
        if provided != token_required:
            return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    # report configured email provider options and last result
    providers = {
        'resend_configured': bool(os.environ.get('RESEND_API_KEY')) and resend is not None,
        'smtp_configured': bool(os.environ.get('SMTP_HOST') and os.environ.get('SMTP_USER') and os.environ.get('SMTP_PASS')),
        'staging': os.environ.get('UMAN_ENV', '').lower() == 'staging'
    }
    status = {
        'ok': True,
        'providers': providers,
        'last_email': _email_status
    }
    return jsonify(status)


@app.route('/register', methods=['POST'])
def register():
    data = request.form
    prenom = data.get('prenom', '').strip()
    nom = data.get('nom', '').strip()
    email = data.get('email', '').strip().lower()
    organisation = data.get('organisation', '').strip()
    telephone = data.get('telephone', '').strip()

    if not email:
        flash('Courriel requis', 'danger')
        return redirect(url_for('profil'))

    code = secrets.token_urlsafe(8)
    code_hash = hash_code(code)
    expires_dt = datetime.now(timezone.utc) + timedelta(minutes=CODE_TTL_MINUTES)
    expires = expires_dt.isoformat()

    db = get_mysql_db()
    cur = db.cursor(dictionary=True)
    now = datetime.now(timezone.utc).isoformat()
    
    try:
        # Vérifier si l'utilisateur existe déjà
        cur.execute('SELECT id FROM membres WHERE email = %s', (email,))
        existing_user = cur.fetchone()
        
        if existing_user:
            # Mettre à jour l'utilisateur existant
            cur.execute('''UPDATE membres SET username = %s, password = %s 
                          WHERE email = %s''',
                       (prenom + ' ' + nom, code_hash, email))
        else:
            # Créer un nouvel utilisateur
            cur.execute('''INSERT INTO membres (username, password, email, is_admin, created_at) 
                          VALUES (%s, %s, %s, %s, %s)''',
                       (prenom + ' ' + nom, code_hash, email, 0, now))
        db.commit()
    except Exception as e:
        logger.exception('Failed to save user: %s', e)
        flash('Erreur lors de l\'enregistrement', 'danger')
        return redirect(url_for('profil'))

    # send email (may be no-op if SMTP vars not set)
    send_code_email(email, code)

    # For tests/dev: if env var TESTING_RETURN_CODE is set, return JSON with code
    if os.environ.get('TESTING_RETURN_CODE') == '1':
        return jsonify({'email': email, 'code': code})

    # If the request is AJAX, return a JSON success so frontend can open the confirm modal
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'message': 'code sent'})

    flash('Un code de confirmation a été envoyé à votre courriel.', 'success')
    return redirect(url_for('profil'))


@app.route('/register/confirm', methods=['POST'])
def register_confirm():
    email = request.form.get('email', '').strip().lower()
    code = request.form.get('code', '').strip()
    if not email or not code:
        return jsonify({'ok': False, 'error': 'email and code required'}), 400

    db = get_mysql_db()
    cur = db.cursor(dictionary=True)
    cur.execute('SELECT * FROM membres WHERE email = %s', (email,))
    user = cur.fetchone()
    
    if not user:
        return jsonify({'ok': False, 'error': 'user not found'}), 404

    # Vérifier le code
    if hash_code(code) != user['password']:
        return jsonify({'ok': False, 'error': 'invalid code'}), 400

    # Activer l'utilisateur (supprimer le code temporaire)
    cur.execute('UPDATE membres SET password = %s WHERE email = %s', 
               ('activated', email))
    db.commit()
    
    # Connexion automatique après activation
    session['user_id'] = user['id']
    session['user_email'] = user['email']
    session['is_admin'] = bool(user['is_admin'])
    
    return jsonify({'ok': True, 'message': 'profile activated'})


# Routes de compatibilité (redirection vers les nouvelles routes RDKQ)
@app.route('/admin/mediatheque')
def admin_mediatheque_redirect():
    """Redirection vers la nouvelle route RDKQ pour compatibilité"""
    return redirect('/rdkq/admin/mediatheque')

@app.route('/admin/mediatheque/data')
def admin_mediatheque_data_redirect():
    """Redirection vers la nouvelle API RDKQ pour compatibilité"""
    return redirect('/rdkq/admin/mediatheque/data')

@app.route('/admin/mediatheque/new', methods=['GET', 'POST'])
def admin_new_media_redirect():
    """Redirection vers la nouvelle route RDKQ pour compatibilité"""
    if request.method == 'POST':
        return redirect('/rdkq/admin/mediatheque/new')
    return redirect('/rdkq/admin/mediatheque/new')

@app.route('/admin/mediatheque/<int:media_id>/edit', methods=['GET', 'POST'])
def admin_edit_media_redirect(media_id):
    """Redirection vers la nouvelle route RDKQ pour compatibilité"""
    if request.method == 'POST':
        return redirect(f'/rdkq/admin/mediatheque/{media_id}/edit')
    return redirect(f'/rdkq/admin/mediatheque/{media_id}/edit')


if __name__ == '__main__':
    # Configuration des sessions
    app.secret_key = os.environ.get('SECRET_KEY', 'rdkq_secret_key_2024_change_in_production')
    app.config['SESSION_TYPE'] = 'filesystem'
    
    debug_flag = os.environ.get('FLASK_DEBUG', '1') == '1'
    # Port configuré pour correspondre au tunnel Cloudflare
    app.run(host='127.0.0.1', port=8002, debug=debug_flag)
