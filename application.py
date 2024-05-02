import tkinter as tk
import cv2
import util
from PIL import Image, ImageTk

class App:
    def __init__(self):
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

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)

        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.add_new_user_capture = self.most_recent_capture_arr.copy()

if __name__=="__main__":
    app = App()
    app.start()