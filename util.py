import os
import pickle

import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Combobox, Style
# import face_recognition


def get_button(window, text, color, command, fg='white', width=20):
    button = tk.Button(
                        window,
                        text=text,
                        activebackground="black",
                        activeforeground="white",
                        fg=fg,
                        bg=color,
                        command=command,
                        height=2,
                        width=width,
                        font=('Helvetica bold', 20)
                    )

    return button


def get_img_label(window):
    label = tk.Label(window)
    label.grid(row=0, column=0)
    return label


def get_text_label(window, text):
    label = tk.Label(window, text=text)
    label.config(font=("sans-serif", 21), justify="left")
    return label


def get_entry_text(window, height=2, width=15):
    inputtxt = tk.Text(window,
                       height=height,
                       width=width, font=("Arial", 32))
    return inputtxt


def get_combo_box(window):
    combo_style = Style()
    combo_style.theme_use('clam')  # Choose one of the available themes

    # Define a custom style for the combo box
    combo_style.configure('Custom.TCombobox', font=("Arial", 12), background='#f0f0f0', foreground='#333333', fieldbackground='#f0f0f0', selectbackground='#e0e0e0', selectforeground='#333333', arrowsize=12)

    combo = Combobox(window, style='Custom.TCombobox', state='readonly', width=20)
    return combo


def msg_box(title, description):
    messagebox.showinfo(title, description)


# def recognize(img, db_path):
#     # it is assumed there will be at most 1 match in the db
#
#     embeddings_unknown = face_recognition.face_encodings(img)
#     if len(embeddings_unknown) == 0:
#         return 'no_persons_found'
#     else:
#         embeddings_unknown = embeddings_unknown[0]
#
#     db_dir = sorted(os.listdir(db_path))
#
#     match = False
#     j = 0
#     while not match and j < len(db_dir):
#         path_ = os.path.join(db_path, db_dir[j])
#
#         file = open(path_, 'rb')
#         embeddings = pickle.load(file)
#
#         match = face_recognition.compare_faces([embeddings], embeddings_unknown)[0]
#         j += 1
#
#     if match:
#         return db_dir[j - 1][:-7]
#     else:
#         return 'unknown_person'
