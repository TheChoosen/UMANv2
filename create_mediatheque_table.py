#!/usr/bin/env python3
"""
Script pour créer la table mediatheque dans MySQL
"""

import mysql.connector
from mysql.connector import Error
from config_mysql import MYSQL_CONFIG

def create_mediatheque_table():
    """Créer la table mediatheque"""
    
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        print("📚 Création de la table médiathèque...")
        
        # Créer la table mediatheque
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS mediatheque (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            image_url VARCHAR(500),
            document_url VARCHAR(500),
            category VARCHAR(100),
            author VARCHAR(255),
            is_public BOOLEAN DEFAULT TRUE,
            is_featured BOOLEAN DEFAULT FALSE,
            views_count INT DEFAULT 0,
            created_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_category (category),
            INDEX idx_public (is_public),
            INDEX idx_featured (is_featured),
            INDEX idx_created_at (created_at),
            FOREIGN KEY (created_by) REFERENCES membres(id) ON DELETE SET NULL
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_sql)
        print("✅ Table 'mediatheque' créée")
        
        # Ajouter des données d'exemple
        print("\n📝 Ajout de données d'exemple...")
        
        sample_data = [
            (
                "Documentaire : Fondements de la République du Kwébec",
                "Présentation complète des principes fondateurs de notre République, incluant la sociocratie, l'autonomie et la souveraineté informationnelle.",
                "/static/image/Plateforme Construction.png",
                "/static/RepubliqueduKwebec/docs/fondements-rdkq.pdf",
                "documentaire",
                "République du Kwébec",
                True,
                True,
                0
            ),
            (
                "Guide pratique : Sociocratie et prise de décision",
                "Manuel complet sur les méthodes de prise de décision collective et l'organisation sociocratique au sein des cercles locaux.",
                "/static/image/Plateforme Fabrication.png",
                "/static/RepubliqueduKwebec/docs/guide-sociocratie.pdf",
                "guide",
                "Équipe Formation",
                True,
                True,
                0
            ),
            (
                "Webinaire : Monnaie souveraine et économie locale",
                "Capsule vidéo explicative sur le système monétaire de la République du Kwébec et les principes d'économie décentralisée.",
                "/static/image/Plateforme Hotellerie.png",
                "/static/RepubliqueduKwebec/videos/monnaie-souveraine.mp4",
                "video",
                "Banque du Peuple",
                True,
                False,
                0
            ),
            (
                "Formation : Tribunaux citoyens et justice populaire",
                "Formation complète sur le fonctionnement des tribunaux citoyens, la médiation et les principes de justice restaurative.",
                "/static/RepubliqueduKwebec/Photo/formation-justice.png",
                "/static/RepubliqueduKwebec/docs/formation-tribunaux.pdf",
                "formation",
                "Tribunaux Citoyens",
                True,
                False,
                0
            ),
            (
                "Manifeste de la République du Kwébec",
                "Document fondateur présentant la vision, les valeurs et les objectifs de notre mouvement souverainiste numérique.",
                "/static/RepubliqueduKwebec/Photo/manifeste.png",
                "/static/RepubliqueduKwebec/docs/manifeste-rdkq.pdf",
                "document",
                "République du Kwébec",
                True,
                True,
                0
            ),
            (
                "Tutoriel : Registre foncier souverain",
                "Guide d'utilisation du registre foncier de la République du Kwébec pour l'enregistrement de biens immobiliers.",
                "/static/RepubliqueduKwebec/Photo/registre-foncier.png",
                "/static/RepubliqueduKwebec/docs/tutoriel-registre.pdf",
                "tutoriel",
                "Registre Foncier",
                True,
                False,
                0
            )
        ]
        
        insert_sql = """
        INSERT INTO mediatheque (title, description, image_url, document_url, category, author, is_public, is_featured, views_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.executemany(insert_sql, sample_data)
        connection.commit()
        
        print(f"✅ {len(sample_data)} éléments ajoutés à la médiathèque")
        
        # Vérifier les données
        cursor.execute("SELECT COUNT(*) FROM mediatheque")
        count = cursor.fetchone()[0]
        print(f"📊 Total d'éléments dans la médiathèque: {count}")
        
        # Afficher les éléments créés
        cursor.execute("SELECT id, title, category, is_featured FROM mediatheque ORDER BY created_at DESC")
        items = cursor.fetchall()
        
        print(f"\n📋 Éléments de la médiathèque:")
        for item in items:
            featured = "⭐" if item[3] else ""
            print(f"   {item[0]:2d}. {item[1]} ({item[2]}) {featured}")
        
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Erreur lors de la création de la table: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Création de la table médiathèque MySQL")
    print(f"📍 Serveur: {MYSQL_CONFIG['host']}")
    print(f"📂 Base: {MYSQL_CONFIG['database']}")
    print("-" * 50)
    
    if create_mediatheque_table():
        print(f"\n🎉 Table médiathèque créée avec succès!")
        print(f"✅ Données d'exemple ajoutées")
        print(f"✅ Prête pour l'intégration avec l'application web")
    else:
        print(f"\n❌ Échec de la création de la table")
