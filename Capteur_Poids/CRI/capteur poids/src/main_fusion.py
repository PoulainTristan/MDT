import serial
import time
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from operations import get_article_by_barcode
import tkinter as tk
from PIL import Image, ImageTk
import os

# Configuration du port série (à adapter selon ton ESP32)
SERIAL_PORT = "COM3"  # Remplace par le bon port
BAUD_RATE = 115200

def get_weight():
    """ Récupère le poids depuis l'ESP32 via Serial """
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
            ser.flush()  # Nettoyer le buffer série
            time.sleep(1)
            ser.write(b'\n')  # Envoyer un signal pour recevoir le poids
            poids = ser.readline().decode().strip()
            return float(poids) if poids else None
    except Exception as e:
        print(f"Erreur lors de la lecture du poids: {e}")
        return None

def verifier_poids(barcode):
    """ Vérifie si le poids mesuré correspond à celui de la base de données """
    article = get_article_by_barcode(barcode)
    if article:
        nom, code_barre, poids_attendu, prix, image_name = article
        poids_mesure = get_weight()
        if poids_mesure is None:
            print("❌ Impossible de lire le poids.")
            return

        print(f"📦 Article : {nom}, Poids attendu : {poids_attendu}g, Poids mesuré : {poids_mesure}g")
        if abs(poids_mesure - poids_attendu) > 10:  # Tolérance de 10g
            print("⚠️ Poids incorrect ! Rescanner l'article.")
        else:
            print("✅ Poids validé !")
    else:
        print("❌ Article non trouvé")

def scan_barcode():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray)
        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            print(f"📸 Code-barres détecté: {barcode_data}")
            verifier_poids(barcode_data)
            time.sleep(2)  # Pause pour éviter les doublons

        cv2.imshow("Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    scan_barcode()
