# coding:utf-8
# from subprocess import *
import os
from tkinter import *
from datetime import datetime 
from tkinter import messagebox
import cv2
test = False


# Verification du numero de telephone
def test_phone(a):
    try:
        a = int(a)
    except ValueError:
        return False, "Ce n'est pas un numéro que vous avez saisi"
    if int(610000000) < a < int(669999999):
        return True, ''
    else:
        return False, str(a) + " n'est pas un numéro tél valide !"


# Heures et date du 20e jour precedent
def today(n):
    presently = datetime.now()
    if n == 0:
        # Retoune l'heure sous le format d'une chaine de : 14h20min
        return str(presently.strftime('%Hh%Mmin'))
    if n == 1:
        # Retoune la date sous le format d'une chaine de : 20-07-2020
        return str(presently.strftime('%d-%m-%Y'))
   
    
def convertir_caracteres_en_chiffres(code):    
    # Dictionnaire de correspondance entre les caractères spéciaux et les chiffres
    try:
        int(code)
        return str(code).zfill(6)
    except:
        mapping = {
            'à': '0', '&': '1', 'é': '2', '"': '3', "'": '4', '(': '5', 
            '-': '6', 'è': '7', '_': '8', 'ç': '9'
        }
        
        # Convertir chaque caractère de la chaîne
        chiffres = ""
        for char in code:
            if char in mapping:
                chiffres += mapping[char]  # Remplacer par le chiffre correspondant
            else:
                chiffres += char  # Garder le caractère original s'il n'est pas dans le mapping
        return chiffres


def capture_with_preview(image_name):
    cap = cv2.VideoCapture(0)  # Ouvre la webcam (0 = première caméra)

    if not cap.isOpened():
        messagebox.showerror("Erreur : Impossible d'accéder à la webcam.")
        return

    # Assurez-vous que le dossier 'images' existe
    from app.config import paths
    paths.IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        # Lire les images de la webcam
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Photo error", "Impossible de lancer la WebCam")
            break

        # Afficher l'image en direct dans une fenêtre
        cv2.imshow("Webcam - Appuyez sur espace pour capturer ou 'Q' pour quitter", frame)

        # Gérer les entrées clavier
        key = cv2.waitKey(1) & 0xFF
        image_name = str(image_name).zfill(6)
        if key == ord(' '):  # Appuyez sur 'C' pour capturer une photo

            resized_frame = cv2.resize(frame, (722, 712))
            # Chemin de sauvegarde dans le sous-dossier 'images'
            from app.config import paths
            image_path = paths.get_image_path(f"{image_name}.png")
            file_path = str(image_path)

            # Enregistrer l'image
            # cv2.imwrite(file_path, frame)
            cv2.imwrite(file_path, resized_frame)
            messagebox.showinfo("Succès", "DPhoto capturée et sauvegardée sous : {}".format(file_path))
            break
        elif key == ord('q') or key == ord('Q'):  # Appuyez sur 'Q' pour quitter
            messagebox.showinfo("Annulé", "Aucune photo n'a été prise")
            break
    cap.release()
    cv2.destroyAllWindows()
