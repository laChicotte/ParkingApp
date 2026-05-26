# coding:utf-8
import os
from tkinter import *
from datetime import datetime
from tkinter import messagebox
import cv2

test = False


def test_phone(a):
    try:
        a = int(a)
    except ValueError:
        return False, "Ce n'est pas un numéro que vous avez saisi"
    if int(610000000) < a < int(669999999):
        return True, ''
    else:
        return False, str(a) + " n'est pas un numéro tél valide !"


def today(n):
    presently = datetime.now()
    if n == 0:
        return str(presently.strftime('%Hh%Mmin'))
    if n == 1:
        return str(presently.strftime('%d-%m-%Y'))


def convertir_caracteres_en_chiffres(code):
    try:
        int(code)
        return str(code).zfill(6)
    except Exception:
        mapping = {
            'à': '0', '&': '1', 'é': '2', '"': '3', "'": '4', '(': '5',
            '-': '6', 'è': '7', '_': '8', 'ç': '9'
        }
        chiffres = ""
        for char in code:
            chiffres += mapping.get(char, char)
        return chiffres.zfill(6)


def capture_with_preview(image_name):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Erreur", "Impossible d'accéder à la webcam.")
        return

    from app.config import paths
    paths.IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Photo error", "Impossible de lancer la WebCam")
            break

        cv2.imshow("Webcam - Appuyez sur espace pour capturer ou 'Q' pour quitter", frame)

        key = cv2.waitKey(1) & 0xFF
        image_name = str(image_name).zfill(6)
        if key == ord(' '):
            resized_frame = cv2.resize(frame, (722, 712))
            from app.config import paths as p
            image_path = p.get_image_path(f"{image_name}.png")
            cv2.imwrite(str(image_path), resized_frame)
            messagebox.showinfo("Succès", f"Photo capturée et sauvegardée sous : {image_path}")
            break
        elif key == ord('q') or key == ord('Q'):
            messagebox.showinfo("Annulé", "Aucune photo n'a été prise")
            break

    cap.release()
    cv2.destroyAllWindows()


def scan_qr_camera(callback):
    """
    Ouvre la caméra et détecte les QR codes et codes-barres 1D.
    Espace = confirmer le code détecté | Q = annuler.
    Appelle callback(code_converti) lorsqu'un code est confirmé.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Erreur", "Impossible d'accéder à la webcam.")
        return

    qr_detector = cv2.QRCodeDetector()

    # pyzbar pour codes-barres 1D (optionnel — nécessite libzbar0 + pip install pyzbar)
    try:
        from pyzbar import pyzbar as _pyzbar
        _use_pyzbar = True
    except ImportError:
        _pyzbar = None
        _use_pyzbar = False

    detected_code = None
    window_name = "Scan — Espace: confirmer | Q: annuler"

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Erreur caméra", "Impossible de lire le flux vidéo.")
            break

        display = frame.copy()
        found = None

        # Détection QR code
        data, bbox, _ = qr_detector.detectAndDecode(frame)
        if data:
            found = data
            if bbox is not None:
                try:
                    import numpy as np
                    pts = bbox.astype(int)
                    cv2.polylines(display, [pts], True, (0, 220, 0), 3)
                except Exception:
                    pass

        # Détection code-barres 1D via pyzbar si QR non trouvé
        if not found and _use_pyzbar:
            for bc in _pyzbar.decode(frame):
                found = bc.data.decode("utf-8")
                x, y, w, h = bc.rect
                cv2.rectangle(display, (x, y), (x + w, y + h), (0, 180, 255), 3)
                break

        if found:
            detected_code = found
            cv2.putText(display, f"Code: {found}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 200, 0), 2)
            cv2.putText(display, "ESPACE = Confirmer", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        else:
            cv2.putText(display, "Pointez un QR code ou code-barres...", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 180, 180), 2)

        cv2.putText(display, "Q = Annuler", (10, display.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 255), 2)

        cv2.imshow(window_name, display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' ') and detected_code:
            cap.release()
            cv2.destroyAllWindows()
            code_converti = convertir_caracteres_en_chiffres(detected_code)
            callback(code_converti)
            return
        elif key in (ord('q'), ord('Q')):
            break

    cap.release()
    cv2.destroyAllWindows()
