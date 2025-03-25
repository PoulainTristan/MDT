import sqlite3

# Ajouter un article
def add_article(nom, code_barre, poids, prix, image):
    conn = sqlite3.connect("caddie.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO articles (nom, poids,code_barre, prix, image) VALUES (?, ?, ?, ?, ?)", (nom, poids, code_barre, prix, image))
    conn.commit()
    conn.close()

# Lire tous les articles
def get_articles():
    conn = sqlite3.connect("caddie.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles")
    articles = cursor.fetchall()
    conn.close()
    return articles

# Mettre à jour le prix d'un article
def update_price(nom, nouveau_prix):
    conn = sqlite3.connect("caddie.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE articles SET prix = ? WHERE nom = ?", (nouveau_prix, nom))
    conn.commit()
    conn.close()

# Supprimer un article
def delete_article(nom):
    conn = sqlite3.connect("caddie.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles WHERE nom = ?", (nom,))
    conn.commit()
    conn.close()

# Récupérer un article par son code-barres
def get_article_by_barcode(code_barre):
    conn = sqlite3.connect("caddie.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nom, code_barre, poids, prix, image FROM articles WHERE code_barre = ?", (code_barre,))
    article = cursor.fetchone()
    conn.close()
    return article  # Retourne un tuple (nom, code_barre, poids, prix, image)
