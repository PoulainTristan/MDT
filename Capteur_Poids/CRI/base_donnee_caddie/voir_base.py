import sqlite3

conn = sqlite3.connect("caddie.db")  # Chemin vers ta base
cursor = conn.cursor()

# Vérifie la structure de la table
cursor.execute("PRAGMA table_info(articles)")
columns = cursor.fetchall()

conn.close()

# Affiche les colonnes existantes
for col in columns:
    print(col)
