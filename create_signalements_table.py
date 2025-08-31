#!/usr/bin/env python3
"""
Script pour créer la table signalements BIQ dans MySQL
"""

import mysql.connector
from mysql.connector import Error
from config_mysql import MYSQL_CONFIG

def create_signalements_table():
    """Créer la table signalements pour BIQ"""
    
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        print("🚨 Création de la table signalements BIQ...")
        
        # Créer la table signalements
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS signalements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            type VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            contact VARCHAR(255),
            status VARCHAR(50) DEFAULT 'nouveau',
            priority VARCHAR(20) DEFAULT 'normale',
            assigned_to INT,
            resolution TEXT,
            created_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_type (type),
            INDEX idx_status (status),
            INDEX idx_priority (priority),
            INDEX idx_created_by (created_by),
            INDEX idx_assigned_to (assigned_to),
            INDEX idx_created_at (created_at),
            FOREIGN KEY (created_by) REFERENCES membres(id) ON DELETE SET NULL,
            FOREIGN KEY (assigned_to) REFERENCES membres(id) ON DELETE SET NULL
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_sql)
        print("✅ Table 'signalements' créée")
        
        # Ajouter des données d'exemple
        print("\n📝 Ajout de données d'exemple...")
        
        sample_data = [
            (
                "Violation des droits lors d'un placement",
                "violation_droits",
                "Placement d'un enfant sans justification valable, refus d'accès aux parents, non-respect des procédures légales.",
                "parent.concerne@email.com",
                "en_cours",
                "haute",
                None,
                None,
                None
            ),
            (
                "Falsification de documents par la DPJ",
                "falsification",
                "Modification de rapports psychosociaux pour justifier des décisions non fondées.",
                "(514) 555-0123",
                "nouveau",
                "critique",
                None,
                None,
                None
            ),
            (
                "Négligence dans le suivi d'un dossier",
                "negligence",
                "Absence de suivi pendant 6 mois, non-retour d'appels, dossier laissé à l'abandon.",
                "famille.oubliee@email.com",
                "nouveau",
                "normale",
                None,
                None,
                None
            ),
            (
                "Abus de pouvoir d'un intervenant",
                "abus_dpj",
                "Menaces répétées, chantage psychologique, dépassement de mandat.",
                "victime.abus@email.com",
                "resolu",
                "haute",
                None,
                "Signalement transmis aux autorités compétentes. Intervenant suspendu.",
                None
            )
        ]
        
        insert_sql = """
        INSERT INTO signalements (title, type, description, contact, status, priority, assigned_to, resolution, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.executemany(insert_sql, sample_data)
        connection.commit()
        
        print(f"✅ {len(sample_data)} signalements d'exemple ajoutés")
        
        # Vérifier les données
        cursor.execute("SELECT COUNT(*) FROM signalements")
        count = cursor.fetchone()[0]
        print(f"📊 Total de signalements: {count}")
        
        # Afficher les signalements par statut
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM signalements 
            GROUP BY status 
            ORDER BY status
        """)
        stats = cursor.fetchall()
        
        print(f"\n📋 Répartition par statut:")
        for stat in stats:
            print(f"   {stat[0]}: {stat[1]} signalement(s)")
        
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Erreur lors de la création de la table: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Création de la table signalements BIQ")
    print(f"📍 Serveur: {MYSQL_CONFIG['host']}")
    print(f"📂 Base: {MYSQL_CONFIG['database']}")
    print("-" * 50)
    
    if create_signalements_table():
        print(f"\n🎉 Table signalements créée avec succès!")
        print(f"✅ Données d'exemple ajoutées")
        print(f"✅ Prête pour l'intégration BIQ")
    else:
        print(f"\n❌ Échec de la création de la table")
