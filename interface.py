from os import mkdir
from tkinter import filedialog
import os

import customtkinter as ctk
from PIL import Image
from DrawFrame import DrawFrame
import cv2
import numpy as np
from core import Ocr, Easyocr
from docx import Document
import sqlite3 as sql
import time
from pathlib import Path
import shutil


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.history_saved = False
        self.time = None
        self.image = None
        self.result_image = None
        self.file_path = None
        self.history_dir_path = Path("drawing_image")
        self.title("Custom Tkinter")
        self.geometry("1600x1200")

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.button = ctk.CTkButton(self.main_frame, text="Вибрати файл",
                                    height=40, command=self.choice_file)
        self.button.pack(padx=0, pady=10)

        self.draw_button = ctk.CTkButton(self.main_frame, text="Малювати",
                                         height=40, command=self.show_draw)
        self.draw_button.pack(pady=5)

        self.label = ctk.CTkLabel(self.main_frame, text="Файл не вибраний",
                                  wraplength=400)
        self.label.pack(padx=10, pady=10)
        #  Кнопка для змінення мови для розпізнання
        self.language_button = ctk.CTkButton(self.main_frame, text="Українська та англійська",
                                             command=self.change_language,
                                             hover_color="#9200D1",
                                             fg_color="#5F0087"
                                             )
        self.language_button.pack(padx=10, pady=10)

        # Спільний бордер
        self.border = ctk.CTkFrame(self.main_frame, border_width=2,
                                   border_color="gray", corner_radius=10,
                                   fg_color="transparent")
        self.border.pack(fill="both", expand=True, padx=10, pady=10)

        # Сітка для зображень
        self.border.grid_columnconfigure((0, 1), weight=1)
        self.border.grid_rowconfigure(2, weight=1)

        # заголовки
        self.original_title = ctk.CTkLabel(self.border, text="Original Image")
        self.original_title.grid(row=0, column=0, pady=(10, 5))

        self.result_title = ctk.CTkLabel(self.border, text="Result Image")
        self.result_title.grid(row=0, column=1, pady=(10, 5))

        # Дві картинки
        self.original_image_label = ctk.CTkLabel(self.border, text="", anchor="n", height=500, width=500)
        self.original_image_label.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        self.result_image_label = ctk.CTkLabel(self.border, text="", anchor="n", height=500, width=500)
        self.result_image_label.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        # Кнопка для отримання результату
        self.result_button = ctk.CTkButton(self.border, text="Отримати результат",
                                           hover_color="#9200D1",
                                           fg_color="#5F0087",
                                           height=40,
                                           width=120,
                                           command=self.get_result
                                           )
        self.result_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        # Кнопка для вибору збереження
        self.save_mode_button = ctk.CTkButton(self.border, text="Режим збереження: TXT",
                                              fg_color="#0000A3",
                                              hover_color="#2E2EFF",
                                              command=self.change_save_mode
                                              )
        self.save_mode_button.grid(row=3, column=1, columnspan=2, padx=10, pady=5)

        # Кнопка для збереження тексту
        self.save_button = ctk.CTkButton(self.border, text="Зберегти текст",
                                         fg_color="#0000A3",
                                         hover_color="#2E2EFF",
                                         command=self.save_text)
        self.save_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        # Кнопка для збереження історії
        self.save_to_history_button = ctk.CTkButton(self.border, text="Зберегти в історію",
                                                    fg_color="#0000A3",
                                                    hover_color="#2E2EFF",
                                                    command=self.save_to_history
                                                    )
        self.save_to_history_button.grid(row=3, column=0, columnspan=2, padx=(0, 800), pady=5)

        # Текст під картинками
        self.text_label = ctk.CTkTextbox(self.border, height=320, wrap="word",
                                         fg_color=("gray85", "gray20"),
                                         corner_radius=10)
        self.text_label.insert("1.0", "")
        self.text_label.configure(state="disabled")

        self.text_label.grid(row=4, column=0, columnspan=2, padx=10, pady=(5, 25),
                             sticky="ew")

        # Frame для малювання
        self.draw_frame = DrawFrame(self, on_done=self.use_drawing,
                                    on_back=self.show_main)

        self.show_main()

    # Функція для зміни мови для розпізнання
    def change_language(self):
        if self.language_button.cget("text") == "Українська та англійська":
            self.language_button.configure(text="Українська")
        elif self.language_button.cget("text") == "Українська":
            self.language_button.configure(text="Англійська")
        else:
            self.language_button.configure(text="Українська та англійська")

    def change_save_mode(self):
        if self.save_mode_button.cget("text") == "Режим збереження: TXT":
            self.save_mode_button.configure(text="Режим збереження: DOCX")
        else:
            self.save_mode_button.configure(text="Режим збереження: TXT")

    def save_document(self):
        text = self.text_label.get('1.0', 'end').strip()
        if not text:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word", "*.docx"),("Текстовий файл", "*.txt")]
        )
        if not path:
            return

        doc = Document()
        doc.add_paragraph(text)
        doc.save(path)

    def save_txt(self):
        text = self.text_label.get('1.0', 'end').strip()
        if not text:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовий файл", "*.txt"), ("Word", "*.docx")]
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def save_text(self):
        if self.save_mode_button.cget("text") == "Режим збереження: DOCX":
            self.save_document()
        else:
            self.save_txt()

    def save_to_history(self):
        if self.history_saved:
            return
        con = sql.connect("history.db")
        con.execute("CREATE TABLE if not exists history (path TEXT,mode TEXT,text TEXT,time TEXT)")
        path = Path(self.file_path)
        is_path_drawing = path.name == "drawing.png"
        if is_path_drawing:
            self.history_dir_path.mkdir(exist_ok=True)
            if list(path.glob("*.png")):
                i = 0
            else:
                i = int(list(self.history_dir_path.iterdir())[-1].name.rstrip(".png").lstrip("drawing"))
                i += 1

            new_path = self.history_dir_path / f"drawing{i}.png"
            shutil.copy2(path, new_path)
            path = new_path.name

        if is_path_drawing:
            mode = "Рукописний англійська(Ocr)"
        else:
            mode = f"{self.language_button.cget("text")}(EasyOcr)"
        text = self.text_label.get('1.0', 'end').strip()
        t = self.time
        con.execute("INSERT INTO history (path, mode, text,time) VALUES (?, ?, ?,?)", (str(path), mode, text, t))
        con.commit()
        self.history_saved = True

    # Перемикання
    def show_main(self):
        self.draw_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)

    def show_draw(self):
        self.main_frame.pack_forget()
        self.draw_frame.pack(fill="both", expand=True)

    def use_drawing(self, path):
        self.show_main()
        self.load_image(path)

    # Робота з файлом
    def choice_file(self):
        path = filedialog.askopenfilename(
            title="Оберіть зображення",
            filetypes=[("Зображення", "*.png *.jpg *.jpeg")],
        )
        if path:
            self.load_image(path)

    @staticmethod
    def image_convert(image):
        img = cv2.imdecode(np.fromfile(image, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return Image.fromarray(binary)

    def set_text(self, text):
        self.text_label.configure(state="normal")
        self.text_label.delete("1.0", "end")
        self.text_label.insert("1.0", text)
        self.text_label.configure(state="disabled")

    def get_result(self):
        self.history_saved = False
        start = time.time()
        path = self.file_path
        if not path:
            self.set_text("Спочатку виберіть файл")
            end = time.time()
            self.time = end - start
            return

        if path == "drawing.png":
            self.set_text(Ocr.read_text(path))
            end = time.time()
            self.time = end - start
            return

        language = self.language_button.cget("text")
        if language == "Англійська":
            languages = ["en"]
        elif language == "Українська":
            languages = ["uk"]
        else:
            languages = ["en", "uk"]

        text = Easyocr.read_text(path, languages)
        self.set_text(text or "Текст не знайдено")
        end = time.time()
        self.time = end - start

    def load_image(self, path):
        self.file_path = path
        self.label.configure(text=f"Успішно завантажено файл: {os.path.basename(path)}")

        pil_image = Image.open(path)
        self.image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image,
                                  size=(300, 300))
        self.original_image_label.configure(image=self.image)

        result = self.image_convert(path)
        if result is None:
            self.label.configure(text="Не вдалося обробити файл")
            return None

        self.result_image = ctk.CTkImage(light_image=result, dark_image=result,
                                         size=(300, 300))
        self.result_image_label.configure(image=self.result_image)

        return self.result_image


if __name__ == "__main__":
    app = App()
    app.mainloop()
