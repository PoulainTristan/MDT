import sqlite3

conn = sqlite3.connect("caddie.db")
cursor = conn.cursor()

# Ajoute la colonne code_barre si elle n'existe pas
cursor.execute("ALTER TABLE articles ADD COLUMN code_barre TEXT UNIQUE")

conn.commit()
conn.close()

print("✅ Colonne code_barre ajoutée !")
