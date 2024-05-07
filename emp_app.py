import datetime
import os
import tkinter as tk
import cv2
from dotenv import load_dotenv
from imgbeddings import imgbeddings

import util
from PIL import Image, ImageTk
import psycopg2

class App:
    def __init__(self):
        self.haar_cascade = cv2.CascadeClassifier('content/recogn_algoritm/haarcascade_frontalface_default.xml')
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")



        self.login_button_main_window = util.get_button(self.main_window, 'Логин пользователя', 'blue', self.login_button_click, width=24)
        self.login_button_main_window.place(x=750, y=400)

        self.login_button_main_window = util.get_button(self.main_window, 'Регистрация пользователя', 'blue',
                                                        self.register_button_click, width=24)
        self.login_button_main_window.place(x=750, y=300)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        self.gates_id = 2


        load_dotenv()
        DB_NAME = os.getenv('DB_NAME')
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_HOST = os.getenv('DB_HOST')
        DB_PORT = os.getenv('DB_PORT')

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

    def login_button_click(self):
        self.login_user_window = tk.Toplevel(self.main_window)
        self.login_user_window.geometry("1200x520+370+120")

        self.capture_label = util.get_img_label(self.login_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.document_type_combobox = util.get_combo_box(self.login_user_window)
        self.document_type_combobox['values'] = ('Тип Документа', 'Паспорт', 'Студ. билет')
        self.document_type_combobox.current(0)
        self.document_type_combobox.place(x=750, y=100)

        self.document_id_value = util.get_entry_text(self.login_user_window, height=1, width=14)
        self.document_id_value.place(x=750, y=200)

        self.login_button_main_window = util.get_button(self.login_user_window, 'Логин пользователя', 'blue',
                                                        self.login_user_emp_button_clicked, width=24)
        self.login_button_main_window.place(x=750, y=400)

        # doctype = self.document_type_combobox.current()
        # docid = self.document_id_value.get("1.0", "end-1c")
        # print(f'doctype: "{doctype}", docid: "{docid}"')



    def login_user_emp_button_clicked(self):
        doctype_num = self.document_type_combobox.current()
        docid = self.document_id_value.get("1.0", "end-1c")
        if doctype_num==0 and docid=='':
            msg = util.msg_box("Не указаны данные", "Укажите данные")
            self.login_user_window.destroy()
        elif doctype_num==0:
            msg = util.msg_box("Неправильный тип документа", "Укажите тип документа")
            self.login_user_window.destroy()
        elif docid=='':
            msg = util.msg_box("Неправильный id пользователя", "Укажите id пользователя")
            self.login_user_window.destroy()
        else:
            if doctype_num == 1:
                doctype = "passport"
            elif doctype_num == 2:
                doctype = "studID"
            img = self.add_new_user_capture

            gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            faces = self.haar_cascade.detectMultiScale(
                gray_img, scaleFactor=1.05, minNeighbors=1, minSize=(100, 100)
            )
            user_image_maxw = 0
            user_image_maxh = 0
            cropped_image = None
            for x, y, w, h in faces:
                if (user_image_maxh < h and user_image_maxw < w):
                    user_image_maxh = h
                    user_image_maxw = w
                    cropped_image = img[y: y + h, x: x + w]

            pil_image = Image.fromarray(cropped_image)
            ibed = imgbeddings()

            embedding = ibed.to_embeddings(pil_image)

            cur = self.conn.cursor()
            cur.execute("SELECT * FROM users WHERE doctype = %s AND docid = %s", (doctype, docid))

            rows = cur.fetchall()
            if len(rows)==0:
                msg = util.msg_box("Пользователь не найден",
                                   "Пользователя с данным сочетанием документа и номера документа нет в БД")
            elif len(rows)>1:
                msg = util.msg_box("Ошибка",
                                   "Найдено несколько пользователей с данным сочетанием документа и номера документа")
            else:
                row = rows[0]
                id, docid, doctype, stored_embedding = row

                filename = str(datetime.datetime.now()).replace(" ", "_").replace(":", '_').split('.')[0] + ".jpg"
                target_file_name = "stored-faces-2/" + filename
                cv2.imwrite(target_file_name, cropped_image)
                print(id, self.gates_id, filename)
                print(embedding[0].tolist(), id)
                cur.execute("INSERT INTO authentifications (users_id, gates_id, picture) VALUES (%s, %s, %s)",
                            (id, self.gates_id, filename))
                cur.execute("UPDATE users SET embedding = %s WHERE id = %s", (embedding[0].tolist(), id))
                self.conn.commit()
                msg = util.msg_box("Добро пожаловать",
                                   "Заходите!")
                self.login_user_window.destroy()




    def register_button_click(self):
        self.register_user_window = tk.Toplevel(self.main_window)
        self.register_user_window.geometry("1200x520+370+120")

        self.capture_label = util.get_img_label(self.register_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.document_type_combobox = util.get_combo_box(self.register_user_window)
        self.document_type_combobox['values'] = ('Тип Документа', 'Паспорт', 'Студ. билет')
        self.document_type_combobox.current(0)
        self.document_type_combobox.place(x=750, y=100)

        self.document_id_value = util.get_entry_text(self.register_user_window, height=1, width=14)
        self.document_id_value.place(x=750, y=200)

        self.register_button_main_window = util.get_button(self.register_user_window, 'Регистрация пользователя', 'blue',
                                                        self.register_user_emp_button_clicked, width=24)
        self.register_button_main_window.place(x=750, y=400)

    def register_user_emp_button_clicked(self):
        doctype_num = self.document_type_combobox.current()
        docid = self.document_id_value.get("1.0", "end-1c")
        if doctype_num == 0 and docid == '':
            msg = util.msg_box("Не указаны данные", "Укажите данные")
            self.register_user_window.destroy()
        elif doctype_num == 0:
            msg = util.msg_box("Неправильный тип документа", "Укажите тип документа")
            self.register_user_window.destroy()
        elif docid == '':
            msg = util.msg_box("Неправильный id пользователя", "Укажите id пользователя")
            self.register_user_window.destroy()
        else:
            if doctype_num == 1:
                doctype = "passport"
            elif doctype_num == 2:
                doctype = "studID"
            img = self.add_new_user_capture

            gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            faces = self.haar_cascade.detectMultiScale(
                gray_img, scaleFactor=1.05, minNeighbors=1, minSize=(100, 100)
            )
            user_image_maxw = 0
            user_image_maxh = 0
            cropped_image = None
            for x, y, w, h in faces:
                if (user_image_maxh < h and user_image_maxw < w):
                    user_image_maxh = h
                    user_image_maxw = w
                    cropped_image = img[y: y + h, x: x + w]

            pil_image = Image.fromarray(cropped_image)
            ibed = imgbeddings()

            embedding = ibed.to_embeddings(pil_image)

            cur = self.conn.cursor()
            cur.execute("SELECT * FROM users WHERE doctype = %s AND docid = %s", (doctype, docid))

            rows = cur.fetchall()
            if len(rows) > 0:
                msg = util.msg_box("Ошибка",
                                   "Найден пользователь с данным сочетанием документа и номера документа")
            else:
                filename = str(datetime.datetime.now()).replace(" ", "_").replace(":", '_').split('.')[0] + ".jpg"
                target_file_name = "stored-faces-2/" + filename
                cv2.imwrite(target_file_name, cropped_image)
                cur.execute("INSERT INTO users (docid, doctype, embedding) VALUES (%s, %s, %s)", (docid, doctype, embedding[0].tolist()))
                self.conn.commit()
                cur.execute("SELECT id FROM users WHERE doctype = %s AND docid = %s", (doctype, docid))
                id = cur.fetchall()[0]
                print(id)
                cur.execute("INSERT INTO authentifications (users_id, gates_id, picture) VALUES (%s, %s, %s)",
                            (id, self.gates_id, filename))
                # cur.execute("UPDATE users SET embedding = %s WHERE id = %s", (embedding[0].tolist(), id))
                self.conn.commit()
                msg = util.msg_box("Добро пожаловать",
                                   "Заходите!")
                self.register_user_window.destroy()

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)

        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.add_new_user_capture = self.most_recent_capture_arr.copy()

if __name__=="__main__":
    app = App()
    app.start()