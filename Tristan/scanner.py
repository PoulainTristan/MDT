import sqlite3
import cv2
import os
import time
import tkinter as tk
from tkinter import messagebox, Toplevel
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import subprocess
import psutil  # pip install psutil

# Répertoire de travail courant
os.chdir(os.path.dirname(os.path.abspath(__file__)))

###############################
# Vérification et lancement de update_articles.py
###############################

def is_update_script_running():
    """
    Vérifie si update_articles.py est déjà lancé.
    """
    for proc in psutil.process_iter(attrs=['cmdline']):
        try:
            cmd = proc.info['cmdline']
            if cmd and any("update_articles.py" in part for part in cmd):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def launch_update_script():
    """
    Lance le script update_articles.py dans un processus séparé.
    """
    # On suppose que le script update_articles.py se trouve dans le même répertoire
    subprocess.Popen(["python", "update_articles.py"])
    print("Lancement de update_articles.py...")

if not is_update_script_running():
    launch_update_script()
else:
    print("update_articles.py est déjà en cours d'exécution.")

# Chemin vers la base de données
DB_FILE = "data/articles.db"

# Variables globales
scanned_products = {}  # Dictionnaire des produits scannés {code_barre: [nom, prix, quantité]}
scan_cooldown = 3  # Délai entre deux scans du même code
last_scan_time = {}  # Dictionnaire des derniers scans
running = True  # État du programme
camera_active = True  # Contrôle si la caméra doit tourner
admin_window_open = False  # Variable pour vérifier si la fenêtre admin est ouverte
weight_check_windows = {}  # Dictionnaire pour gérer les fenêtres de vérification de poids par produit


# Fonction de récupération du produit depuis la base de données
def check_product_in_db(code_barre):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE code_barre=?", (code_barre,))
    product = cursor.fetchone()
    conn.close()
    return product


# Fonction de mise à jour de la liste des produits scannés
def update_product_list():
    listbox.delete(0, tk.END)
    for code_barre, (nom, prix, quantite) in scanned_products.items():
        listbox.insert(tk.END, f"{nom} - {prix:.2f}€ x {quantite}")


# Fonction pour supprimer un produit sélectionné
def remove_product():
    try:
        selection = listbox.curselection()[0]
        code_barre = list(scanned_products.keys())[selection]
        del scanned_products[code_barre]
        update_product_list()
    except IndexError:
        messagebox.showwarning("Attention", "Sélectionnez un produit à supprimer.")


# Fonction pour modifier la quantité d'un produit sélectionné
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


# Fonction pour afficher le ticket de caisse
def show_receipt():
    global camera_active
    if not scanned_products:
        messagebox.showwarning("Achat vide", "Aucun produit scanné.")
        return

    camera_active = False  # Désactiver la caméra
    
    receipt_window = Toplevel(root)
    receipt_window.title("Ticket de caisse")
    receipt_window.geometry("400x400")
    receipt_window.transient(root)
    receipt_window.grab_set()
    receipt_window.attributes("-topmost", True)

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
        scanned_products = {}
        update_product_list()
        camera_active = True
        receipt_window.destroy()

    # Bouton pour fermer simplement la fenêtre
    def close_window():
        global camera_active
        camera_active = True
        receipt_window.destroy()

    frame_buttons = tk.Frame(receipt_window)
    frame_buttons.pack(pady=10, fill=tk.X)

    btn_payer = tk.Button(frame_buttons, text="Payer", bg="green", fg="white", font=("Arial", 14), command=pay_and_close)
    btn_payer.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    btn_retour = tk.Button(frame_buttons, text="Retourner à l'achat", bg="gray", fg="white", font=("Arial", 14), command=close_window)
    btn_retour.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)


# Fonction de gestion de la fenêtre de vérification du poids
def open_weight_check_window(nom, prix, barcode_data, correct_weight):
    # Vérifier si une fenêtre de vérification du poids est déjà ouverte pour ce produit
    if barcode_data in weight_check_windows:
        return

    # Calcul du poids total des produits scannés
    total_weight = sum(scanned_products[code][2] * float(check_product_in_db(code)[3]) for code in scanned_products)

    def correct_weight_action():
        """Si le poids est correct, le produit est ajouté à la liste."""
        if barcode_data in scanned_products:
            scanned_products[barcode_data][2] += 1
        else:
            scanned_products[barcode_data] = [nom, prix, 1]
        update_product_list()
        weight_window.destroy()
        del weight_check_windows[barcode_data]

    def incorrect_weight_action():
        """Si le poids est incorrect, on affiche un message d'erreur et on ignore le produit."""
        messagebox.showerror("Poids incorrect", "Le poids du produit est incorrect. Retirer le produit.")
        weight_window.destroy()
        del weight_check_windows[barcode_data]

    def remove_product_action():
        """Réduire de 1 la quantité du produit scanné si le poids est incorrect."""
        if barcode_data in scanned_products:
            scanned_products[barcode_data][2] -= 1
            # Si la quantité devient 0 ou moins, on supprime le produit de la liste
            if scanned_products[barcode_data][2] <= 0:
                del scanned_products[barcode_data]
            update_product_list()
        weight_window.destroy()
        del weight_check_windows[barcode_data]

    # Créer la fenêtre modale de vérification du poids
    weight_window = Toplevel(root)
    weight_window.title("Vérification du poids")
    weight_window.geometry("300x200")
    weight_window.transient(root)
    weight_window.attributes("-topmost", True)
    
    message = f"Poids de {nom} : {correct_weight} kg\nLe poids détecté est-il le bon ?"
    label = tk.Label(weight_window, text=message, font=("Arial", 12))
    label.pack(pady=20)

    # Affichage du poids total des produits scannés
    total_weight_label = tk.Label(weight_window, text=f"Poids total des produits : {total_weight:.2f} kg", font=("Arial", 12))
    total_weight_label.pack(pady=10)

    frame_buttons = tk.Frame(weight_window)
    frame_buttons.pack(pady=10, fill=tk.X)

    btn_correct = tk.Button(frame_buttons, text="Poids ajouté", command=correct_weight_action, bg="green", fg="white")
    btn_correct.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    btn_incorrect = tk.Button(frame_buttons, text="Mauvais poids", command=incorrect_weight_action, bg="red", fg="white")
    btn_incorrect.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    btn_remove = tk.Button(frame_buttons, text="Poids retiré", command=remove_product_action, bg="orange", fg="white")
    btn_remove.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    # Ajouter la fenêtre au dictionnaire pour marquer qu'elle est ouverte
    weight_check_windows[barcode_data] = weight_window

    # Ajouter une fonction de nettoyage lors de la fermeture de la fenêtre modale
    weight_window.protocol("WM_DELETE_WINDOW", lambda: close_weight_window(barcode_data, weight_window))


# Fonction pour fermer proprement la fenêtre de vérification du poids
def close_weight_window(barcode_data, weight_window):
    # Nettoyer l'entrée du dictionnaire lorsque la fenêtre est fermée
    del weight_check_windows[barcode_data]
    weight_window.destroy()


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

        if barcode_data == "0000" and not admin_window_open:
            open_admin_window()

        if barcode_data not in last_scan_time or (current_time - last_scan_time[barcode_data]) > scan_cooldown:
            print(f"Code-barres scanné : {barcode_data}")

            product = check_product_in_db(barcode_data)
            if product:
                nom, prix = product[1], float(product[4])
                correct_weight = float(product[3])  # Poids correct provenant de la base de données
                open_weight_check_window(nom, prix, barcode_data, correct_weight)

                last_scan_time[barcode_data] = current_time
            else:
                print(f"Produit non trouvé : {barcode_data}")

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    img_tk = ImageTk.PhotoImage(image=img)

    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    canvas.img_tk = img_tk

    if running:
        root.after(10, update_video)


# Fonction de gestion de la fenêtre admin
def open_admin_window():
    global admin_window_open
    admin_window_open = True

    admin_window = Toplevel(root)
    admin_window.title("Fenêtre Admin 0000")
    admin_window.geometry("300x300")
    admin_window.transient(root)
    admin_window.attributes("-topmost", True)

    label = tk.Label(admin_window, text="Fenêtre Administrateur", font=("Arial", 14))
    label.pack(pady=20)

    frame_buttons = tk.Frame(admin_window)
    frame_buttons.pack(pady=10, fill=tk.X)

    btn_increase = tk.Button(frame_buttons, text="+", command=lambda: modify_quantity(1))
    btn_increase.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    btn_decrease = tk.Button(frame_buttons, text="-", command=lambda: modify_quantity(-1))
    btn_decrease.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    btn_remove = tk.Button(frame_buttons, text="Supprimer", command=remove_product)
    btn_remove.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    btn_close_admin = tk.Button(admin_window, text="Fermer", command=lambda: close_admin_window(admin_window))
    btn_close_admin.pack(pady=10)

    # Empêcher la fermeture de la fenêtre admin par la croix
    admin_window.protocol("WM_DELETE_WINDOW", lambda: None)


# Fonction de fermeture de la fenêtre admin
def close_admin_window(window):
    global admin_window_open
    admin_window_open = False
    window.destroy()


# Interface graphique avec Tkinter
root = tk.Tk()
root.title("Scanner de code-barres")
root.attributes('-fullscreen', True)
root.bind("<Escape>", lambda event: root.attributes('-fullscreen', False))

frame_main = tk.Frame(root)
frame_main.pack(fill=tk.BOTH, expand=True)

frame_video = tk.Frame(frame_main)
frame_video.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

canvas = tk.Canvas(frame_video)
canvas.pack(fill=tk.BOTH, expand=True)

frame_list = tk.Frame(frame_main)
frame_list.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

listbox = tk.Listbox(frame_list, width=40, height=20)
listbox.pack(fill=tk.BOTH, expand=True)

btn_validate = tk.Button(frame_list, text="Valider l'achat", command=show_receipt, bg="red", fg="white")
btn_validate.pack(pady=20, fill=tk.X)

cap = cv2.VideoCapture(0)
update_video()

root.mainloop()
cap.release()
cv2.destroyAllWindows()
