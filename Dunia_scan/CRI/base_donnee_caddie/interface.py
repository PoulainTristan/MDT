import tkinter as tk
from tkinter import Label, Entry, Button
from PIL import Image, ImageTk
from operations import get_article_by_barcode
import cv2
from pyzbar.pyzbar import decode

def update_interface(article):
    if article:
        label_result.config(text=f"📦 {article[1]}\n⚖ Poids: {article[2]} g\n💰 Prix: {article[3]} €")
        show_image(article[4])
    else:
        label_result.config(text="❌ Article non trouvé")
        label_image.config(image='')
        label_image.image = None

def show_image(image_path):
    try:
        img = Image.open(image_path)
        img = img.resize((150, 150))
        img = ImageTk.PhotoImage(img)
        label_image.config(image=img)
        label_image.image = img
    except Exception as e:
        label_result.config(text="❌ Image non trouvée")

def scan_barcode():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        for barcode in decode(frame):
            barcode_data = barcode.data.decode('utf-8')
            cap.release()
            cv2.destroyAllWindows()
            entry_barcode.delete(0, tk.END)
            entry_barcode.insert(0, barcode_data)
            article = get_article_by_barcode(barcode_data)
            update_interface(article)
            return
        cv2.imshow("Scan Barcode", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

root = tk.Tk()
root.title("Scanner de Code-Barres")
entry_barcode = Entry(root, width=20)
entry_barcode.pack(pady=10)
btn_search = Button(root, text="Rechercher", command=lambda: update_interface(get_article_by_barcode(entry_barcode.get())))
btn_search.pack(pady=5)
btn_scan = Button(root, text="Scanner Code-Barres", command=scan_barcode)
btn_scan.pack(pady=5)
label_result = Label(root, text="🔍 Entrez un code-barres ou scannez un produit", font=("Arial", 12))
label_result.pack(pady=10)
label_image = Label(root)
label_image.pack(pady=10)
root.mainloop()
