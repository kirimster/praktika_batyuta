# main.py - Initial commit
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import os


class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing App")
        self.root.geometry("1000x700")

        self.original_image = None
        self.current_image = None
        self.photo = None

        self.display_width = 800
        self.display_height = 500

        self.create_widgets()

    def create_widgets(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame, bg='gray')
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(fill=tk.X, pady=5)

        self.load_button = tk.Button(self.control_frame, text="Загрузить изображение", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.camera_button = tk.Button(self.control_frame, text="Сделать фото", command=self.capture_from_camera)
        self.camera_button.pack(side=tk.LEFT, padx=5)

    def load_image(self):
        file_types = [("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        file_path = filedialog.askopenfilename(filetypes=file_types)

        if file_path:
            try:
                img_pil = Image.open(file_path)
                self.original_image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
                self.current_image = self.original_image.copy()
                self.show_image()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")

    def show_image(self):
        if self.current_image is not None:
            try:
                image_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(image_rgb)

                width_ratio = self.display_width / img_pil.width
                height_ratio = self.display_height / img_pil.height
                scale = min(width_ratio, height_ratio, 1)

                new_size = (int(img_pil.width * scale), int(img_pil.height * scale))
                img_pil = img_pil.resize(new_size, Image.LANCZOS)

                self.photo = ImageTk.PhotoImage(img_pil)
                self.canvas.delete("all")
                self.canvas.create_image(
                    self.display_width // 2,
                    self.display_height // 2,
                    anchor=tk.CENTER,
                    image=self.photo
                )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка отображения: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()