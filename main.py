import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np


class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing App")
        self.root.geometry("1000x700")

        # Переменные для изображений
        self.original_image = None
        self.current_image = None
        self.photo = None
        self.image_stack = []  # Стек для отмены изменений
        self.redo_stack = []  # Стек для возврата изменений

        # Размеры области отображения
        self.display_width = 800
        self.display_height = 500

        self.create_widgets()
        self.root.bind('<Configure>', self.on_window_resize)

    def create_widgets(self):
        # Главный контейнер
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas с прокруткой
        self.canvas = tk.Canvas(self.main_frame, bg='gray')
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Скроллбары
        self.h_scroll = tk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        # Панель управления
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(fill=tk.X, pady=5)

        # Кнопки загрузки
        self.load_button = tk.Button(self.control_frame, text="Загрузить изображение", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.camera_button = tk.Button(self.control_frame, text="Сделать фото", command=self.capture_from_camera)
        self.camera_button.pack(side=tk.LEFT, padx=5)

        # Панель обработки изображений
        self.processing_frame = tk.LabelFrame(self.root, text="Обработка изображения")
        self.processing_frame.pack(fill=tk.X, pady=5)

        # Выбор канала
        self.channel_var = tk.StringVar(value="none")
        tk.Label(self.processing_frame, text="Канал:").grid(row=0, column=0, padx=5)
        tk.Radiobutton(self.processing_frame, text="Красный", variable=self.channel_var, value="red").grid(row=0,
                                                                                                           column=1,
                                                                                                           padx=5)
        tk.Radiobutton(self.processing_frame, text="Зеленый", variable=self.channel_var, value="green").grid(row=0,
                                                                                                             column=2,
                                                                                                             padx=5)
        tk.Radiobutton(self.processing_frame, text="Синий", variable=self.channel_var, value="blue").grid(row=0,
                                                                                                          column=3,
                                                                                                          padx=5)
        self.channel_button = tk.Button(self.processing_frame, text="Применить", command=self.apply_channel)
        self.channel_button.grid(row=0, column=4, padx=5)

        # Границы
        tk.Label(self.processing_frame, text="Граница:").grid(row=1, column=0, padx=5)
        self.border_size = tk.Spinbox(self.processing_frame, from_=1, to=100, width=5)
        self.border_size.grid(row=1, column=1, padx=5)
        self.border_button = tk.Button(self.processing_frame, text="Добавить", command=self.apply_border)
        self.border_button.grid(row=1, column=2, padx=5)

        # Оттенки серого
        self.grayscale_button = tk.Button(self.processing_frame, text="Оттенки серого", command=self.apply_grayscale)
        self.grayscale_button.grid(row=1, column=3, padx=5)

        # Линия
        self.line_frame = tk.Frame(self.processing_frame)
        self.line_frame.grid(row=2, column=0, columnspan=5, pady=5)
        tk.Label(self.line_frame, text="Линия (x1,y1,x2,y2):").pack(side=tk.LEFT, padx=5)
        self.x1_entry = tk.Entry(self.line_frame, width=4)
        self.x1_entry.pack(side=tk.LEFT)
        self.y1_entry = tk.Entry(self.line_frame, width=4)
        self.y1_entry.pack(side=tk.LEFT)
        self.x2_entry = tk.Entry(self.line_frame, width=4)
        self.x2_entry.pack(side=tk.LEFT)
        self.y2_entry = tk.Entry(self.line_frame, width=4)
        self.y2_entry.pack(side=tk.LEFT)
        tk.Label(self.line_frame, text="Толщина:").pack(side=tk.LEFT, padx=5)
        self.thickness_entry = tk.Entry(self.line_frame, width=3)
        self.thickness_entry.insert(0, "2")
        self.thickness_entry.pack(side=tk.LEFT)
        self.line_button = tk.Button(self.line_frame, text="Нарисовать", command=self.apply_draw_line)
        self.line_button.pack(side=tk.LEFT, padx=5)

        # Кнопки отмены/возврата
        self.undo_button = tk.Button(self.processing_frame, text="Отменить (Ctrl+Z)",
                                     command=self.undo_changes, state=tk.DISABLED)
        self.undo_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.redo_button = tk.Button(self.processing_frame, text="Вернуть (Ctrl+Y)",
                                     command=self.redo_changes, state=tk.DISABLED)
        self.redo_button.grid(row=3, column=2, columnspan=3, pady=5)

        # Кнопка сброса
        self.reset_button = tk.Button(self.processing_frame, text="Сбросить все",
                                      command=self.reset_all_changes, state=tk.DISABLED)
        self.reset_button.grid(row=4, column=0, columnspan=5, pady=5)

        # Горячие клавиши
        self.root.bind('<Control-z>', lambda e: self.undo_changes())
        self.root.bind('<Control-y>', lambda e: self.redo_changes())

    def save_state(self):
        """Сохраняет текущее состояние в стек"""
        if self.current_image is not None:
            self.image_stack.append(self.current_image.copy())
            self.undo_button.config(state=tk.NORMAL)
            self.redo_stack = []  # Очищаем стек возврата при новом действии
            self.redo_button.config(state=tk.DISABLED)
            self.reset_button.config(state=tk.NORMAL)

    def undo_changes(self):
        """Отменяет последнее изменение"""
        if len(self.image_stack) > 0:
            # Сохраняем текущее состояние в стек возврата
            if self.current_image is not None:
                self.redo_stack.append(self.current_image.copy())
                self.redo_button.config(state=tk.NORMAL)

            # Восстанавливаем предыдущее состояние
            self.current_image = self.image_stack.pop()
            self.show_image()

            if len(self.image_stack) == 0:
                self.undo_button.config(state=tk.DISABLED)

    def redo_changes(self):
        """Возвращает отмененное изменение"""
        if len(self.redo_stack) > 0:
            # Сохраняем текущее состояние в стек отмены
            if self.current_image is not None:
                self.image_stack.append(self.current_image.copy())
                self.undo_button.config(state=tk.NORMAL)

            # Восстанавливаем состояние из стека возврата
            self.current_image = self.redo_stack.pop()
            self.show_image()

            if len(self.redo_stack) == 0:
                self.redo_button.config(state=tk.DISABLED)

    def reset_all_changes(self):
        """Сбрасывает все изменения к оригиналу"""
        if self.original_image is not None:
            self.save_state()
            self.current_image = self.original_image.copy()
            self.show_image()

    def apply_operation(self, operation_func, *args):
        """Применяет операцию к изображению с сохранением состояния"""
        if self.current_image is not None:
            self.save_state()
            operation_func(*args)
            self.show_image()

    def load_image(self):
        """Загрузка изображения из файла"""
        file_types = [
            ("JPEG files", "*.jpg;*.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]

        file_path = filedialog.askopenfilename(filetypes=file_types)
        if not file_path:
            return

        try:
            # Загрузка через PIL с конвертацией в OpenCV
            img_pil = Image.open(file_path)
            self.original_image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            self.current_image = self.original_image.copy()

            # Сброс стеков изменений
            self.image_stack = []
            self.redo_stack = []
            self.undo_button.config(state=tk.DISABLED)
            self.redo_button.config(state=tk.DISABLED)
            self.reset_button.config(state=tk.NORMAL)

            self.show_image()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")

    def capture_from_camera(self):
        """Захват изображения с веб-камеры"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Ошибка", "Не удалось подключиться к веб-камере")
            return

        # Окно предпросмотра
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

        # Кнопка захвата
        capture_btn = tk.Button(preview, text="Снять фото",
                                command=lambda: self.take_photo(cap, preview))
        capture_btn.pack(pady=10)

        update_preview()

    def take_photo(self, cap, preview_window):
        """Сохранение фото с камеры"""
        ret, frame = cap.read()
        if ret:
            self.original_image = frame
            self.current_image = self.original_image.copy()

            # Сброс стеков изменений
            self.image_stack = []
            self.redo_stack = []
            self.undo_button.config(state=tk.DISABLED)
            self.redo_button.config(state=tk.DISABLED)
            self.reset_button.config(state=tk.NORMAL)

            self.show_image()

        cap.release()
        preview_window.destroy()

    def show_image(self):
        """Отображение изображения с масштабированием"""
        if self.current_image is not None:
            try:
                # Конвертация в RGB
                image_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(image_rgb)

                # Масштабирование
                img_width, img_height = img_pil.size
                width_ratio = self.display_width / img_width
                height_ratio = self.display_height / img_height
                scale_ratio = min(width_ratio, height_ratio, 1)

                new_size = (int(img_width * scale_ratio), int(img_height * scale_ratio))
                img_pil = img_pil.resize(new_size, Image.LANCZOS)

                # Отображение
                self.photo = ImageTk.PhotoImage(img_pil)
                self.canvas.delete("all")
                self.canvas.create_image(
                    self.display_width // 2,
                    self.display_height // 2,
                    anchor=tk.CENTER,
                    image=self.photo
                )
                self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка отображения: {str(e)}")

    def apply_channel(self):
        """Применение выбранного цветового канала"""
        if self.current_image is not None:
            channel = self.channel_var.get()
            if channel != "none":
                self.save_state()

                # Создаем копию изображения
                channel_img = self.current_image.copy()

                if channel == "red":
                    channel_img[:, :, 0] = 0  # Убираем синий
                    channel_img[:, :, 1] = 0  # Убираем зеленый
                elif channel == "green":
                    channel_img[:, :, 0] = 0  # Убираем синий
                    channel_img[:, :, 2] = 0  # Убираем красный
                elif channel == "blue":
                    channel_img[:, :, 1] = 0  # Убираем зеленый
                    channel_img[:, :, 2] = 0  # Убираем красный

                self.current_image = channel_img
                self.show_image()

    def apply_border(self):
        """Добавление границы к изображению"""
        if self.current_image is not None:
            try:
                size = int(self.border_size.get())
                self.save_state()

                bordered_img = cv2.copyMakeBorder(
                    self.current_image,
                    size, size, size, size,
                    cv2.BORDER_CONSTANT,
                    value=[0, 0, 0]
                )
                self.current_image = bordered_img
                self.show_image()

            except ValueError:
                messagebox.showerror("Ошибка", "Введите целое число для размера границы")

    def apply_grayscale(self):
        """Конвертация в оттенки серого"""
        if self.current_image is not None:
            self.save_state()

            gray_img = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            gray_img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)  # Конвертируем обратно в 3 канала
            self.current_image = gray_img
            self.show_image()

    def apply_draw_line(self):
        """Рисование линии на изображении"""
        if self.current_image is not None:
            try:
                x1 = int(self.x1_entry.get())
                y1 = int(self.y1_entry.get())
                x2 = int(self.x2_entry.get())
                y2 = int(self.y2_entry.get())
                thickness = int(self.thickness_entry.get())

                self.save_state()

                line_img = self.current_image.copy()
                cv2.line(line_img, (x1, y1), (x2, y2), (0, 255, 0), thickness)
                self.current_image = line_img
                self.show_image()

            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные координаты и толщину линии")

    def on_window_resize(self, event):
        """Обработчик изменения размера окна"""
        if self.current_image is not None:
            self.display_width = event.width - 20
            self.display_height = event.height - 200
            self.show_image()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()