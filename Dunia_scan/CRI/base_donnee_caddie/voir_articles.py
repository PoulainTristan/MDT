import sqlite3

conn = sqlite3.connect("caddie.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM articles")
articles = cursor.fetchall()

for article in articles:
    print(article)  # Affiche tous les articles enregistrés

conn.close()
