import sqlite3
import cv2
import os
import time
import tkinter as tk
from tkinter import messagebox, Toplevel
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode

# Change le répertoire de travail courant pour celui du fichier Python
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Chemins vers les bases de données
DB_FILE = "data/articles.db"

# Variables globales
scanned_products = {}  # Dictionnaire des produits scannés {code_barre: [nom, prix, quantité]}
scan_cooldown = 3  # Délai entre deux scans du même code
last_scan_time = {}  # Dictionnaire des derniers scans
running = True  # État du programme
camera_active = True  # Contrôle si la caméra doit tourner

# Vérifier si un produit est dans la base de données
def check_product_in_db(code_barre):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE code_barre=?", (code_barre,))
    product = cursor.fetchone()
    conn.close()
    return product

# Supprimer un produit sélectionné
def remove_product():
    try:
        selection = listbox.curselection()[0]
        code_barre = list(scanned_products.keys())[selection]
        del scanned_products[code_barre]
        update_product_list()
    except IndexError:
        messagebox.showwarning("Attention", "Sélectionnez un produit à supprimer.")

# Modifier la quantité d'un produit sélectionné
def modify_quantity(delta):
    try:
        selection = listbox.curselection()[0]
        code_barre = list(scanned_products.keys())[selection]
        scanned_products[code_barre][2] += delta

        if scanned_products[code_barre][2] <= 0:
            del scanned_products[code_barre]
        update_product_list()
    except IndexError:
        messagebox.showwarning("Attention", "Sélectionnez un produit pour modifier la quantité.")

# Mettre à jour la liste des produits scannés
def update_product_list():
    listbox.delete(0, tk.END)
    for code_barre, (nom, prix, quantite) in scanned_products.items():
        listbox.insert(tk.END, f"{nom} - {prix:.2f}€ x {quantite}")

# Fonction d'affichage du ticket de caisse
def show_receipt():
    global camera_active
    if not scanned_products:
        messagebox.showwarning("Achat vide", "Aucun produit scanné.")
        return

    camera_active = False  # Désactiver la caméra
    
    receipt_window = Toplevel(root)
    receipt_window.title("Ticket de caisse")
    receipt_window.geometry("400x400")
    receipt_window.transient(root)  # Associe cette fenêtre à la fenêtre principale
    receipt_window.grab_set()  # Bloque les interactions avec la fenêtre principale
    receipt_window.attributes("-topmost", True)  # Garde la fenêtre toujours devant

    receipt_text = tk.Text(receipt_window, wrap=tk.WORD, font=("Arial", 12))
    receipt_text.pack(fill=tk.BOTH, expand=True)

    total_price = 0
    receipt_text.insert(tk.END, "=== Ticket de caisse ===\n\n")

    for code_barre, (nom, prix, quantite) in scanned_products.items():
        subtotal = prix * quantite
        total_price += subtotal
        receipt_text.insert(tk.END, f"{nom} - {prix:.2f}€ x {quantite} = {subtotal:.2f}€\n")

    receipt_text.insert(tk.END, f"\nTotal: {total_price:.2f}€\n")

    # Bouton pour payer et réinitialiser les achats
    def pay_and_close():
        global scanned_products, camera_active
        scanned_products = {}  # Réinitialisation
        update_product_list()
        camera_active = True  # Réactiver la caméra
        receipt_window.destroy()

    # Bouton pour fermer simplement la fenêtre
    def close_window():
        global camera_active
        camera_active = True  # Réactiver la caméra
        receipt_window.destroy()

    frame_buttons = tk.Frame(receipt_window)
    frame_buttons.pack(pady=10, fill=tk.X)

    btn_payer = tk.Button(frame_buttons, text="Payer", bg="green", fg="white", font=("Arial", 14), command=pay_and_close)
    btn_payer.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    btn_retour = tk.Button(frame_buttons, text="Retourner à l'achat", bg="gray", fg="white", font=("Arial", 14), command=close_window)
    btn_retour.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

# Fonction de capture vidéo
def update_video():
    global running, camera_active
    if not camera_active:
        root.after(10, update_video)
        return
    
    ret, frame = cap.read()
    if not ret or not running:
        return
    
    barcodes = decode(frame)
    current_time = time.time()

    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')

        if barcode_data not in last_scan_time or (current_time - last_scan_time[barcode_data]) > scan_cooldown:
            print(f"Code-barres scanné : {barcode_data}")

            product = check_product_in_db(barcode_data)
            if product:
                nom, prix = product[1], float(product[4])
                if barcode_data in scanned_products:
                    scanned_products[barcode_data][2] += 1
                else:
                    scanned_products[barcode_data] = [nom, prix, 1]

                last_scan_time[barcode_data] = current_time
                update_product_list()
            else:
                print(f"Produit non trouvé : {barcode_data}")

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    img_tk = ImageTk.PhotoImage(image=img)

    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    canvas.img_tk = img_tk

    if running:
        root.after(10, update_video)

# Interface graphique avec Tkinter
root = tk.Tk()
root.title("Scanner de code-barres")
root.attributes('-fullscreen', True)
root.bind("<Escape>", lambda event: root.attributes('-fullscreen', False))

frame_main = tk.Frame(root)
frame_main.pack(fill=tk.BOTH, expand=True)

# Frame vidéo
frame_video = tk.Frame(frame_main)
frame_video.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

canvas = tk.Canvas(frame_video)
canvas.pack(fill=tk.BOTH, expand=True)

# Frame des produits
frame_list = tk.Frame(frame_main)
frame_list.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

listbox = tk.Listbox(frame_list, width=40, height=20)
listbox.pack(fill=tk.BOTH, expand=True)

frame_buttons = tk.Frame(frame_list)
frame_buttons.pack(pady=5, fill=tk.X)

btn_increase = tk.Button(frame_buttons, text="+", command=lambda: modify_quantity(1))
btn_increase.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

btn_decrease = tk.Button(frame_buttons, text="-", command=lambda: modify_quantity(-1))
btn_decrease.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

btn_remove = tk.Button(frame_buttons, text="Supprimer", command=remove_product)
btn_remove.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

btn_validate = tk.Button(frame_list, text="Valider l'achat", command=show_receipt, bg="red", fg="white")
btn_validate.pack(pady=20, fill=tk.X)

cap = cv2.VideoCapture(0)
update_video()

root.mainloop()
cap.release()
cv2.destroyAllWindows()
