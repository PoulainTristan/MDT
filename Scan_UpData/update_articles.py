import os
import requests
import time

# Répertoire de travail courant
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Configuration
USERNAME = "PoulainTristan"         # Votre nom d'utilisateur GitHub
REPO_NAME = "MDT"                  # Le nom de votre dépôt
FILE_PATH = "Tristan/data/articles.db"  # Chemin relatif vers le fichier dans le dépôt
RAW_FILE_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPO_NAME}/main/{FILE_PATH}"
ETAG_FILE = "articles.etag"        # Fichier pour stocker l'ETag localement
LOCAL_FILE_PATH = "data/articles.db"  # Chemin local où le fichier sera stocké

# Optionnel : Si le fichier est privé, renseignez votre token
GITHUB_TOKEN = ""

def get_remote_etag():
    headers = {}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    try:
        response = requests.head(RAW_FILE_URL, headers=headers)
        if response.status_code == 200:
            etag = response.headers.get("ETag")
            if etag:
                print(f"ETag distant : {etag}")
                return etag
            else:
                print("L'en-tête ETag n'est pas présent.")
                return None
        else:
            print(f"Erreur HTTP {response.status_code} lors de la requête HEAD.")
            return None
    except requests.RequestException as e:
        print(f"Erreur lors de la requête HEAD : {e}")
        return None

def get_local_etag():
    if os.path.exists(ETAG_FILE):
        with open(ETAG_FILE, "r") as f:
            return f.read().strip()
    return None

def save_local_etag(etag):
    with open(ETAG_FILE, "w") as f:
        f.write(etag)

def download_file():
    headers = {}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    try:
        response = requests.get(RAW_FILE_URL, headers=headers)
        if response.status_code == 200:
            with open(LOCAL_FILE_PATH, "wb") as f:
                f.write(response.content)
            print(f"Le fichier a été téléchargé et sauvegardé sous {LOCAL_FILE_PATH}")
            # Mettre à jour l'ETag local
            etag = response.headers.get("ETag")
            if etag:
                save_local_etag(etag)
        else:
            print(f"Erreur lors du téléchargement du fichier : HTTP {response.status_code}")
    except requests.RequestException as e:
        print(f"Erreur lors du téléchargement : {e}")

def check_and_update_file():
    remote_etag = get_remote_etag()
    if not remote_etag:
        print("Impossible d'obtenir l'ETag distant. Téléchargement du fichier par précaution.")
        download_file()
        return

    local_etag = get_local_etag()
    if local_etag != remote_etag:
        print("Le fichier distant a changé (ETag différent). Téléchargement de la nouvelle version...")
        download_file()
    else:
        print("Le fichier local est à jour.")

if __name__ == "__main__":
    while True:
        check_and_update_file()
        # Attendre une heure (3600 secondes)
        time.sleep(3600)
