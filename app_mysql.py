# --- RDKQ (République du Kwébec) minimal site ---
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g, send_from_directory, session
import os

# Import the API blueprint
from rdkq_api import rdkq_api
from werkzeug.utils import secure_filename

# Import MySQL configuration
from config_mysql import get_mysql_db, close_mysql_db

# create app early so decorators below can reference it

app = Flask(__name__)
app.register_blueprint(rdkq_api)

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Route de connexion simple pour tester le système admin"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if email:
            # Vérifier si l'utilisateur existe et est actif
            db = get_mysql_db()
            cur = db.cursor(dictionary=True)
            cur.execute('SELECT * FROM users WHERE email = %s AND is_admin = %s', (email, 1))
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
    return redirect(url_for('rdkq_index'))


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
            cur.execute('SELECT is_admin FROM users WHERE id = %s', (user_id,))
            current_status = cur.fetchone()
            if current_status:
                new_status = 0 if current_status['is_admin'] else 1
                cur.execute('UPDATE users SET is_admin = %s WHERE id = %s', (new_status, user_id))
                db.commit()
                flash(f'Statut administrateur modifié pour l\'utilisateur ID {user_id}', 'success')
    
    # Récupérer tous les utilisateurs
    cur.execute('SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC')
    users = cur.fetchall()
    
    return render_template('admin/users.html', users=users)

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

# Médiathèque (JSON simulé)
@app.route('/rdkq/mediatheque')
def rdkq_mediatheque():
    # Prototype: retourne une liste statique
    return jsonify([
        {"id": 1, "title": "Documentaire 1", "desc": "Présentation du projet.", "img": "/static/image/Plateforme Construction.png", "src": "/static/RepubliqueduKwebec/doc1.pdf"},
        {"id": 2, "title": "Capsule vidéo", "desc": "Capsule citoyenne.", "img": "/static/image/Plateforme Fabrication.png", "src": "/static/RepubliqueduKwebec/doc2.pdf"},
        {"id": 3, "title": "Cours", "desc": "Cours sur la souveraineté.", "img": "/static/image/Plateforme Hotellerie.png", "src": "/static/RepubliqueduKwebec/doc3.pdf"}
    ])

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
        cur.execute('SELECT is_admin FROM users WHERE id = %s', (session['user_id'],))
        user = cur.fetchone()
        session['is_admin'] = bool(user['is_admin']) if user else False
    else:
        session['is_admin'] = False


@app.route('/')
def index():
    # si le domaine est peupleun.live, servir la page RDKQ (RepubliqueduKwebec)
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
        cur.execute('SELECT id FROM users WHERE email = %s', (email,))
        existing_user = cur.fetchone()
        
        if existing_user:
            # Mettre à jour l'utilisateur existant
            cur.execute('''UPDATE users SET username = %s, password = %s 
                          WHERE email = %s''',
                       (prenom + ' ' + nom, code_hash, email))
        else:
            # Créer un nouvel utilisateur
            cur.execute('''INSERT INTO users (username, password, email, is_admin, created_at) 
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
    cur.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cur.fetchone()
    
    if not user:
        return jsonify({'ok': False, 'error': 'user not found'}), 404

    # Vérifier le code
    if hash_code(code) != user['password']:
        return jsonify({'ok': False, 'error': 'invalid code'}), 400

    # Activer l'utilisateur (supprimer le code temporaire)
    cur.execute('UPDATE users SET password = %s WHERE email = %s', 
               ('activated', email))
    db.commit()
    
    # Connexion automatique après activation
    session['user_id'] = user['id']
    session['user_email'] = user['email']
    session['is_admin'] = bool(user['is_admin'])
    
    return jsonify({'ok': True, 'message': 'profile activated'})


if __name__ == '__main__':
    # Configuration des sessions
    app.secret_key = os.environ.get('SECRET_KEY', 'rdkq_secret_key_2024_change_in_production')
    app.config['SESSION_TYPE'] = 'filesystem'
    
    debug_flag = os.environ.get('FLASK_DEBUG', '1') == '1'
    # Changer le port pour correspondre à la configuration Cloudflare
    app.run(host='127.0.0.1', port=8002, debug=debug_flag)
