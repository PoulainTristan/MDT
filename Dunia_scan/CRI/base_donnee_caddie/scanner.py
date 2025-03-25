import cv2
import numpy as np
from pyzbar.pyzbar import decode
from operations import get_article_by_barcode
import tkinter as tk
from PIL import Image, ImageTk
import os

# 📌 Chemin du dossier où sont stockées les images des articles
IMAGE_PATH = r"C:\Users\dunia\Desktop\cesi\CRI\base de donnees"

# ✅ Liste des codes-barres déjà scannés (pour éviter répétition d'affichage)
scanned_barcodes = set()

def afficher_article(nom, prix, poids, image_name):
    """ Affiche les infos et l'image de l'article dans une fenêtre Tkinter. """
    fenetre = tk.Toplevel()
    fenetre.title("Article détecté")
    
    # Construire le chemin absolu de l'image
    image_path = os.path.join(IMAGE_PATH, image_name)

    # Charger l'image
    try:
        img = Image.open(image_path)
        img = img.resize((200, 200))  # Redimensionner pour affichage
        photo = ImageTk.PhotoImage(img)

        # Afficher l'image
        label_image = tk.Label(fenetre, image=photo)
        label_image.image = photo  # Conserver la référence pour éviter la suppression
        label_image.pack()
    except Exception as e:
        label_image = tk.Label(fenetre, text=f"❌ Image introuvable\n{e}")
        label_image.pack()

    # Afficher les infos de l'article
    label_nom = tk.Label(fenetre, text=f"📌 Nom : {nom}", font=("Arial", 14))
    label_nom.pack()
    
    label_poids = tk.Label(fenetre, text=f"⚖️ Poids : {poids} g")
    label_poids.pack()
    
    label_prix = tk.Label(fenetre, text=f"💰 Prix : {prix} €")
    label_prix.pack()

def scan_barcode():
    cap = cv2.VideoCapture(0)  # Ouvre la caméra

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Convertir en niveaux de gris pour améliorer la détection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Détecter les codes-barres
        barcodes = decode(gray)

        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")  # Convertir en texte

            # 📌 Vérifier si ce code-barres a déjà été scanné (évite répétition)
            if barcode_data in scanned_barcodes:
                continue  # Passe au prochain

            scanned_barcodes.add(barcode_data)
            print(f"📸 Code-barres détecté: {barcode_data}")

            # Chercher l'article correspondant dans la base de données
            article = get_article_by_barcode(barcode_data)
            if article:
                nom, code_barre, poids, prix, image_name = article
                print(f"✅ Article trouvé : {nom}, {poids}g, {prix}€, image: {image_name}")

                afficher_article(nom, prix, poids, image_name)
            else:
                print("❌ Article non trouvé")

            # 📌 Dessiner un rectangle autour du code-barres
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Afficher la vidéo
        cv2.imshow("Scanner de Code-Barres", frame)

        # Quitter avec la touche 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale Tkinter
    scan_barcode()
