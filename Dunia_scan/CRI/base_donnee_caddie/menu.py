import sqlite3
from operations import add_article, get_articles, update_price, delete_article, get_article_by_barcode

def afficher_menu():
    print("\n📋 MENU :")
    print("1️⃣ Ajouter un article")
    print("2️⃣ Afficher les articles")
    print("3️⃣ Modifier le prix d'un article")
    print("4️⃣ Supprimer un article")
    print("5️⃣ Rechercher un article par code-barres")
    print("0️⃣ Quitter")

def menu_interactif():
    while True:
        afficher_menu()
        choix = input("👉 Choisissez une option : ")
        
        if choix == "1":
            nom = input("Nom de l'article : ")
            code_barre = input("Code-barres : ")
            poids = float(input("Poids (en grammes) : "))
            prix = float(input("Prix (€) : "))
            image = input("Nom de l'image : ")
            add_article(nom, code_barre, poids, prix, image)
            print("✅ Article ajouté avec succès !")
        
        elif choix == "2":
            articles = get_articles()
            if not articles:
                print("❌ Aucun article trouvé.")
            else:
                print("\n📦 Liste des articles :")
                for article in articles:
                    print(f"ID: {article[0]}, Nom: {article[1]}, Code-barres: {article[2]}, Poids: {article[3]}g, Prix: {article[4]}€, Image: {article[5]}")
        
        elif choix == "3":
            nom = input("Nom de l'article à modifier : ")
            nouveau_prix = float(input("Nouveau prix (€) : "))
            update_price(nom, nouveau_prix)
            print("✅ Prix mis à jour !")
        
        elif choix == "4":
            nom = input("Nom de l'article à supprimer : ")
            delete_article(nom)
            print("🗑️ Article supprimé !")
        
        elif choix == "5":
            code_barre = input("Code-barres de l'article : ")
            article = get_article_by_barcode(code_barre)
            if article:
                print(f"\n📦 Article trouvé : Nom: {article[1]}, Poids: {article[2]}g, Prix: {article[3]}€, Image: {article[4]}")
            else:
                print("❌ Aucun article trouvé avec ce code-barres.")
        
        elif choix == "0":
            print("👋 Au revoir !")
            break
        
        else:
            print("❌ Choix invalide, réessayez.")

if __name__ == "__main__":
    menu_interactif()
