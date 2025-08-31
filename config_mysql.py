import mysql.connector
from mysql.connector import Error
import os
from flask import g

# Configuration MySQL
MYSQL_CONFIG = {
    'host': '192.168.50.101',
    'database': 'peupleun',
    'user': 'gsicloud',
    'password': 'TCOChoosenOne204$',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': True
}

def get_mysql_db():
    """Obtenir une connexion MySQL pour le schéma peupleun"""
    db = getattr(g, '_mysql_database', None)
    if db is None:
        try:
            db = g._mysql_database = mysql.connector.connect(**MYSQL_CONFIG)
            db.autocommit = True
        except Error as e:
            print(f"Erreur de connexion MySQL: {e}")
            raise
    return db

def close_mysql_db():
    """Fermer la connexion MySQL"""
    db = getattr(g, '_mysql_database', None)
    if db is not None:
        db.close()
