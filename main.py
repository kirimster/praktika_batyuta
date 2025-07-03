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

    # Добавляем в класс ImageProcessingApp
    def capture_from_camera(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Ошибка", "Не удалось подключиться к веб-камере")
            return

        preview = tk.Toplevel(self.root)
        preview.title("Веб-камера")
        preview_label = tk.Label(preview)
        preview_label.pack()

        def update_preview():
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                preview_label.imgtk = imgtk
                preview_label.configure(image=imgtk)
                preview_label.after(10, update_preview)
            else:
                cap.release()
                preview.destroy()

        capture_btn = tk.Button(preview, text="Снять фото",
                                command=lambda: self.take_photo(cap, preview))
        capture_btn.pack(pady=10)

        update_preview()

    def take_photo(self, cap, preview_window):
        ret, frame = cap.read()
        if ret:
            self.original_image = frame
            self.current_image = self.original_image.copy()
            self.show_image()

        cap.release()
        preview_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()