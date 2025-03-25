import sqlite3

# Fonction pour créer la base et la table
def create_database():
    conn = sqlite3.connect("caddie.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            code_barre TEXT UNIQUE NOT NULL,
            poids REAL NOT NULL,
            prix REAL NOT NULL,
            image TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("✅ Base de données créée !")
