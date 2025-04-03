from database import create_database
from operations import add_article, get_articles, update_price, delete_article, get_article_by_barcode

# Créer la base si elle n'existe pas
create_database()

# Ajouter des articles
add_article("chips", "1234567890128", 60, 0.9, "chips_lays.png")
add_article("Canette Coca-Cola", "0987654321098", 330, 0.7, "coca.png")
add_article("Bouteille d'eau 1L", "5678901234562", 1000, 1.15, "bouteille_eau.png")

# Afficher tous les articles
print("\n📋 Liste des articles :")
for article in get_articles():
    print(f"ID: {article[0]}, Nom: {article[1]}, Poids: {article[2]}g, Prix: {article[3]}€, Image: {article[4]} ")

# Modifier le prix d'un article
update_price("Canette Coca-Cola", 0.8)

# Supprimer un article
delete_article("Bouteille d'eau 1L")

# Afficher les articles après modification
print("\n📋 Liste mise à jour des articles :")
for article in get_articles():
    print(f"ID: {article[0]}, Nom: {article[1]}, Poids: {article[2]}g, Prix: {article[3]}€, Image: {article[4]}")


# Vérifier un article par son code-barres
article = get_article_by_barcode("0987654321098")
if article:
    print(f"\n📦 Article trouvé : ID: {article[0]}, Nom: {article[1]}, Poids: {article[2]}g, Prix: {article[3]}€, Image: {article[4]}")
else:
    print("\n❌ Aucun article trouvé avec ce code-barres.")