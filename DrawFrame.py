import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageDraw


class DrawFrame(ctk.CTkFrame):
    """ Функція on_done - це функція з класу App - яку клас викликає коли малюнок збережено
            on_back - це функція для кнопки назад в App це show_main
        """

    def __init__(self, master, on_done, on_back):
        super().__init__(master, fg_color="transparent")
        self.on_done = on_done
        self.W, self.H = 600, 450
        self.last = None

        self.canvas = tk.Canvas(self, width=self.W, height=self.H,
                                bg="white", highlightthickness=0)
        self.canvas.pack(pady=10)

        self.new_picture()

        self.canvas.bind("<Button-1>", self.start)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.stop)

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=5)
        ctk.CTkButton(row, text="Очистити", command=self.clear).pack(side="left", padx=5)
        ctk.CTkButton(row, text="Зберегти і обробити", command=self.save).pack(side="left", padx=5)
        ctk.CTkButton(row, text="Назад", fg_color="gray", command=on_back).pack(side="left", padx=5)

    def new_picture(self):
        self.pil = Image.new("RGB", (self.W, self.H), "white")
        self.pen = ImageDraw.Draw(self.pil)

    def start(self, e):
        self.last = (e.x, e.y)

    def paint(self, e):
        x0, y0 = self.last
        self.canvas.create_line(x0, y0, e.x, e.y, width=5,
                                fill="black", capstyle="round")
        self.pen.line([x0, y0, e.x, e.y], fill="black", width=5)
        self.last = (e.x, e.y)

    def stop(self, e):
        self.last = None

    def clear(self):
        self.canvas.delete("all")
        self.new_picture()

    def save(self):
        path = "drawing.png"
        self.pil.save(path)
        self.on_done(path)
