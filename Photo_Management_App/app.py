import os
import sqlite3
import cv2
import numpy as np
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import filedialog

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

# =========================
# CONFIG
# =========================

PHOTO_DIR = "photos"
DB_FILE = "photo_ai.db"

os.makedirs(PHOTO_DIR, exist_ok=True)

AZURE_KEY = "AZURE-KEY"
AZURE_ENDPOINT = "AZURE-ENDPOINT"

vision_client = ComputerVisionClient(
    AZURE_ENDPOINT,
    CognitiveServicesCredentials(AZURE_KEY)
)

# =========================
# DATABASE
# =========================

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS photos(
id INTEGER PRIMARY KEY,
path TEXT,
caption TEXT,
objects TEXT
)
""")

conn.commit()

# =========================
# FACE DETECTION
# =========================

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def detect_faces(path):

    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5
    )

    return len(faces)

# =========================
# AZURE ANALYSIS
# =========================

def analyze_image(path):

    with open(path, "rb") as img:

        analysis = vision_client.analyze_image_in_stream(
            img,
            visual_features=["Description","Objects"]
        )

    caption = ""
    objects = []

    if analysis.description.captions:
        caption = analysis.description.captions[0].text

    if analysis.objects:
        for obj in analysis.objects:
            objects.append(obj.object_property)

    return caption, ", ".join(objects)

# =========================
# PROCESS PHOTO
# =========================

def process_photo(path):

    caption, objects = analyze_image(path)
    faces = detect_faces(path)

    cur.execute(
        "INSERT INTO photos(path,caption,objects) VALUES(?,?,?)",
        (path,caption,objects)
    )

    conn.commit()

    return caption, objects, faces

# =========================
# UI
# =========================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("AI Photo Manager")
app.geometry("1300x850")

selected_photo = None

# Sidebar
sidebar = ctk.CTkFrame(app, width=220)
sidebar.pack(side="left", fill="y", padx=10, pady=10)

# Gallery
gallery = ctk.CTkScrollableFrame(app)
gallery.pack(fill="both", expand=True, padx=10, pady=10)

# Info panel
info_panel = ctk.CTkTextbox(app, height=140)
info_panel.pack(fill="x", padx=10, pady=10)

# =========================
# GALLERY FUNCTIONS
# =========================

def select_photo(path):

    global selected_photo
    selected_photo = path

    cur.execute("SELECT caption, objects FROM photos WHERE path=?", (path,))
    result = cur.fetchone()

    info_panel.delete("1.0", "end")

    if result:
        caption, objects = result
        info_panel.insert("end", f"Photo: {os.path.basename(path)}\n\n")
        info_panel.insert("end", f"Caption: {caption}\n\n")
        info_panel.insert("end", f"Objects: {objects}\n")

def load_gallery():

    for widget in gallery.winfo_children():
        widget.destroy()

    cur.execute("SELECT path FROM photos")
    photos = cur.fetchall()

    row = 0
    col = 0

    for (path,) in photos:

        try:

            img = Image.open(path)
            img.thumbnail((170,170))

            tk_img = ImageTk.PhotoImage(img)

            btn = ctk.CTkButton(
                gallery,
                image=tk_img,
                text="",
                width=170,
                height=170,
                command=lambda p=path: select_photo(p)
            )

            btn.image = tk_img
            btn.grid(row=row, column=col, padx=8, pady=8)

            col += 1

            if col == 6:
                col = 0
                row += 1

        except:
            pass

# =========================
# ADD PHOTO
# =========================

def add_photo():

    path = filedialog.askopenfilename(
        filetypes=[("Images","*.jpg *.jpeg *.png *.bmp *.webp")]
    )

    if not path:
        return

    filename = os.path.basename(path)
    save_path = os.path.join(PHOTO_DIR, filename)

    img = Image.open(path)
    img.save(save_path)

    caption, objects, faces = process_photo(save_path)

    info_panel.insert("end", "\nPhoto Added\n")
    info_panel.insert("end", f"Caption: {caption}\n")
    info_panel.insert("end", f"Objects: {objects}\n")
    info_panel.insert("end", f"Faces Detected: {faces}\n")

    load_gallery()

# =========================
# REMOVE PHOTO
# =========================

def remove_photo():

    global selected_photo

    if not selected_photo:
        return

    cur.execute("DELETE FROM photos WHERE path=?", (selected_photo,))
    conn.commit()

    try:
        os.remove(selected_photo)
    except:
        pass

    selected_photo = None

    info_panel.delete("1.0","end")

    load_gallery()

# =========================
# SIDEBAR BUTTONS
# =========================

add_btn = ctk.CTkButton(
    sidebar,
    text="Add Photo",
    command=add_photo
)
add_btn.pack(pady=20, padx=10)

delete_btn = ctk.CTkButton(
    sidebar,
    text="Remove Selected",
    command=remove_photo
)
delete_btn.pack(pady=10, padx=10)

refresh_btn = ctk.CTkButton(
    sidebar,
    text="Refresh Gallery",
    command=load_gallery
)
refresh_btn.pack(pady=10, padx=10)

# =========================
# START
# =========================

load_gallery()

app.mainloop()