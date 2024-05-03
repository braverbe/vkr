import tkinter as tk
import cv2
import util
from PIL import Image, ImageTk
import psycopg2
import numpy as np
from imgbeddings import imgbeddings
from PIL import Image

class App:
    def __init__(self):
        self.haar_cascade = cv2.CascadeClassifier('content/recogn_algoritm/haarcascade_frontalface_default.xml')
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")

        self.login_button_main_window = util.get_button(self.main_window, 'Сделать фото', 'green', self.login_button_click, )
        self.login_button_main_window.place(x=750, y=400)

        from tkinter.ttk import Combobox
        self.document_type_combobox = util.get_combo_box(self.main_window)
        self.document_type_combobox['values'] = ('Тип Документа','Паспорт', 'Студ. билет')
        self.document_type_combobox.current(0)
        self.document_type_combobox.place(x=750, y=100)

        self.document_id_value = util.get_entry_text(self.main_window, height=1, width=14)
        self.document_id_value.place(x=750, y=200)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        DB_NAME = "face_recognization"
        DB_USER = "postgres"
        DB_PASSWORD = "pass"
        DB_HOST = "localhost"  # or your database host
        DB_PORT = "5432"  # or your database port

        self.conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label

        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        self.most_recent_capture_arr = frame

        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)

        self.most_recent_capture_pil = Image.fromarray(img_)

        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)

        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def start(self):
        self.main_window.mainloop()

    def login(self):
        pass

    def login_button_click(self):
        self.login_user_window = tk.Toplevel(self.main_window)
        self.login_user_window.geometry("1200x520+350+100")

        self.capture_label = util.get_img_label(self.login_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        doctype = self.document_type_combobox.current()
        docid = self.document_id_value.get("1.0","end-1c")
        print(f'doctype: "{doctype}", docid: "{docid}"')

        img = self.most_recent_capture_arr

        gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        faces = self.haar_cascade.detectMultiScale(
            gray_img, scaleFactor=1.05, minNeighbors=1, minSize=(100, 100)
        )
        i = 0
        user_image_maxx = 0
        user_image_maxy = 0
        user_image_maxw = 0
        user_image_maxh = 0
        user_image_maxi = 0
        cropped_image = 0
        for x, y, w, h in faces:
            if (user_image_maxh < h and user_image_maxw < w):
                user_image_maxh = h
                user_image_maxw = w
                user_image_maxi = i
                cropped_image = img[y: y + h, x: x + w]


        pil_image = Image.fromarray(cropped_image)
        ibed = imgbeddings()

        embedding = ibed.to_embeddings(pil_image)


        cur = self.conn.cursor()
        string_representation = "[" + ", ".join(str(x) for x in embedding[0].tolist()) + "]"

        cur.execute("SELECT picture, embedding FROM pictures;")
        rows = cur.fetchall()

        # Initialize variables for storing the nearest neighbor information
        nearest_neighbor = None
        min_distance = float('inf')

        # Calculate the distance or similarity for each row
        for row in rows:
            picture, stored_embedding = row
            stored_embedding = np.array(stored_embedding)  # Convert stored embedding to numpy array
            distance = np.linalg.norm(stored_embedding - embedding[0].tolist())  # Calculate Euclidean distance
            # Alternatively, you can use other similarity metrics such as cosine similarity
            # print(f'{picture}: {distance}')
            # Update nearest neighbor information if the current row has a smaller distance
            if distance < min_distance:
                # print(distance, min_distance, min_distance-distance)
                nearest_neighbor = picture
                min_distance = distance

        if (min_distance < 16):
            print(f"Nearest neighbor: {nearest_neighbor}, distance: {min_distance}")
        else:
            print("No nearest persons, distance: ", min_distance, "closest:", nearest_neighbor)

        cur.close()



    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)

        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.add_new_user_capture = self.most_recent_capture_arr.copy()

if __name__=="__main__":
    app = App()
    app.start()