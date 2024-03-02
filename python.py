from tkinter import Tk, Canvas, Menu, filedialog, simpledialog, Toplevel, Label, Button, NW, colorchooser
import pygame.font
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont
pygame.font.init()
import pygame.mixer
import os

class FilterDialog:
    def __init__(self, parent, filter_types):
        self.parent = parent
        self.filter_types = filter_types
        self.result = None

        self.dialog = Toplevel(parent)
        self.dialog.title("Выберите фильтр")

        Label(self.dialog, text="Выберите фильтр:").pack(pady=5)

        for filter_type in filter_types:
            Button(self.dialog, text=filter_type, command=lambda f=filter_type: self.on_button_click(f)).pack()

    def on_button_click(self, filter_type):
        self.result = filter_type
        self.dialog.destroy()


class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("редактор изображений")

        self.image_path = None
        self.edited_image = None
        self.original_image = None  # Save the original image
        self.save_original_image()  # Save the original image when it is first loaded
        self.display_scale = 1.0  # Initial display scale
        self.zoom_step = 0.2  # Zoom step size

        self.canvas = Canvas(root, cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        self.menu_bar = Menu(root)
        root.config(menu=self.menu_bar)

        file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть", command=self.open_image)
        file_menu.add_command(label="Сохранить", command=self.save_image)

        edit_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Редактировать", menu=edit_menu)
        edit_menu.add_command(label="Обрезать", command=self.crop_image)
        edit_menu.add_command(label="Применить фильтр", command=self.apply_filter)
        edit_menu.add_command(label="Изменить яркость/контрастность", command=self.adjust_brightness_contrast)
        edit_menu.add_command(label="Повернуть", command=self.rotate_image)
        edit_menu.add_command(label="Отразить по вертикали", command=self.flip_vertical)
        edit_menu.add_command(label="Отразить по горизонтали", command=self.flip_horizontal)
        edit_menu.add_command(label="Вернуть к исходному", command=self.reset_image)  # Added reset option

        retouch_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Ретушь", menu=retouch_menu)
        retouch_menu.add_command(label="Сгладить", command=self.smooth_image)
        retouch_menu.add_command(label="Улучшить резкость", command=self.enhance_sharpness)

        text_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Текст", menu=text_menu)
        text_menu.add_command(label="Добавить текст", command=self.add_text_layer)
        text_menu.add_command(label="Удалить текст", command=self.remove_text_layer)
        text_menu.add_separator()
        text_menu.add_command(label="Изменить шрифт", command=self.change_text_font)

        view_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="Увеличить", command=self.zoom_in)
        view_menu.add_command(label="Уменьшить", command=self.zoom_out)

        shape_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Фигуры", menu=shape_menu)
        shape_menu.add_command(label="Нарисовать круг", command=self.draw_circle)
        shape_menu.add_command(label="Нарисовать квадрат", command=self.draw_square)

        brush_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Кисть", menu=brush_menu)
        brush_menu.add_command(label="Активировать кисть", command=self.activate_brush)
        brush_menu.add_command(label="Деактивировать кисть", command=self.deactivate_brush)
        brush_menu.add_command(label="Изменить размер кисти", command=self.change_brush_size)
        brush_menu.add_command(label="Выбрать цвет кисти", command=self.choose_brush_color)


        pygame.mixer.init()


        self.brush_sound = pygame.mixer.Sound(os.path.join("C:\\Users\\Acer\\Desktop\\сабақ\\звки\\", "карандаш.mp3"))
        self.camera_sound = pygame.mixer.Sound(os.path.join("C:\\Users\\Acer\\Desktop\\сабақ\\звки\\", "камера.mp3"))

        self.text_entries = []  # Keep track of added text entries

        # Variables for cropping
        self.start_x = None
        self.start_y = None
        self.crop_rect = None


        self.is_crop_active = False
        self.text_entries = []
        self.text_font = ImageFont.load_default()

        root.bind("<Control-o>", lambda event: self.open_image())
        root.bind("<Control-s>", lambda event: self.save_image())
        root.bind("<Control-c>", lambda event: self.crop_image())
        root.bind("<Control-f>", lambda event: self.apply_filter())
        root.bind("<Control-b>", lambda event: self.adjust_brightness_contrast())
        root.bind("<Control-r>", lambda event: self.rotate_image())
        root.bind("<Control-m>", lambda event: self.smooth_image())
        root.bind("<Control-e>", lambda event: self.enhance_sharpness())
        root.bind("<Control-t>", lambda event: self.add_text_layer())
        root.bind("<Control-d>", lambda event: self.remove_text_layer())
        root.bind("<Control-v>", lambda event: self.flip_vertical())
        root.bind("<Control-h>", lambda event: self.flip_horizontal())
        root.bind("<Control-z>", lambda event: self.reset_image())
        root.bind("<Control-plus>", lambda event: self.zoom_in())
        root.bind("<Control-minus>", lambda event: self.zoom_out())
        root.bind("<B>", lambda event: self.activate_brush())
        root.bind("<E>", lambda event: self.activate_eraser())

    def play_sound(self, sound_type):
        if sound_type == "brush":
            pygame.mixer.Sound.play(self.brush_sound)
        elif sound_type == "camera":
            pygame.mixer.Sound.play(self.camera_sound)

    def save_original_image(self):
        if self.edited_image:
            self.original_image = self.edited_image.copy()

    def reset_image(self):
        if self.original_image:
            self.edited_image = self.original_image.copy()
            self.display_image()

    def start_crop(self):
        if not self.is_crop_active:
            # Bind mouse events for cropping
            self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
            self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
            self.is_crop_active = True

            # Display message to guide the user
            self.status_label = Label(self.root, text="Drag to select area, click again to finish cropping", bd=1,
                                      relief="sunken")
            self.status_label.pack(side="bottom", fill="x")

            # Reset cropping variables
            self.start_x = None
            self.start_y = None
            self.crop_rect = None

    def finish_crop(self):
        if self.is_crop_active:
            self.canvas.unbind("<ButtonPress-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            self.is_crop_active = False


            self.status_label.destroy()


            if self.crop_rect:
                self.canvas.delete(self.crop_rect)
                self.crop_rect = None

    def on_mouse_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        if self.crop_rect:
            self.canvas.delete(self.crop_rect)

        self.crop_rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                                      outline="red")

    def on_mouse_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        self.canvas.coords(self.crop_rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)

        if self.edited_image:
            x1, y1, x2, y2 = self.canvas.coords(self.crop_rect)
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            cropped_image = self.edited_image.crop((x1, y1, x2, y2))
            self.edited_image = cropped_image.copy()
            self.display_image()


            self.canvas.delete(self.crop_rect)
            self.crop_rect = None

    def draw_circle(self):
        self.finish_crop()
        if self.edited_image:
            center_x = simpledialog.askinteger("Центр круга", "Введите координату x центра круга:")
            center_y = simpledialog.askinteger("Центр круга", "Введите координату y центра круга:")
            radius = simpledialog.askinteger("Радиус круга", "Введите радиус круга:")

            if center_x is not None and center_y is not None and radius is not None:
                color = colorchooser.askcolor()[1]
                if color:
                    draw = ImageDraw.Draw(self.edited_image)
                    draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius),
                                 fill=color)
                    self.display_image()
                    self.play_sound("brush")

    def draw_square(self):
        self.finish_crop()
        if self.edited_image:
            center_x = simpledialog.askinteger("Центр квадрата", "Введите координату x центра квадрата:")
            center_y = simpledialog.askinteger("Центр квадрата", "Введите координату y центра квадрата:")
            side_length = simpledialog.askinteger("Сторона квадрата", "Введите длину стороны квадрата:")

            if center_x is not None and center_y is not None and side_length is not None:
                color = colorchooser.askcolor()[1]
                if color:
                    draw = ImageDraw.Draw(self.edited_image)
                    draw.rectangle((center_x - side_length / 2, center_y - side_length / 2, center_x + side_length / 2,
                                    center_y + side_length / 2), fill=color)
                    self.display_image()
                    self.play_sound("brush")

    def open_image(self):
        self.finish_crop()
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image_path = file_path
            self.edited_image = Image.open(file_path)
            self.save_original_image()
            self.display_image()
            self.play_sound("camera")

    def save_image(self):
        self.finish_crop()
        if self.edited_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"),
                                                                ("JPEG files", "*.jpg"),
                                                                ("All files", "*.*")])
            if file_path:
                self.edited_image.save(file_path)
                self.play_sound("camera")

    def display_image(self):
        self.finish_crop()
        if self.edited_image:
            displayed_image = self.edited_image.resize((int(self.edited_image.width * self.display_scale),
                                                        int(self.edited_image.height * self.display_scale)))
            photo = ImageTk.PhotoImage(displayed_image)
            self.canvas.config(width=photo.width(), height=photo.height())
            self.canvas.create_image(0, 0, anchor=NW, image=photo)
            self.canvas.photo = photo

    def zoom_in(self):
        self.display_scale += self.zoom_step
        self.display_image()

    def zoom_out(self):
        if self.display_scale > self.zoom_step:
            self.display_scale -= self.zoom_step
            self.display_image()

    def crop_image(self):
        self.finish_crop()
        self.start_crop()

    def apply_filter(self):
        self.finish_crop()
        if self.edited_image:
            filter_types = ["BLUR", "CONTOUR", "DETAIL", "EDGE_ENHANCE", "EMBOSS", "SHARPEN", "GRAYSCALE",
                            "SEPIA"]

            dialog = FilterDialog(self.root, filter_types)
            self.root.wait_window(dialog.dialog)

            chosen_filter = dialog.result
            if chosen_filter:
                try:
                    if chosen_filter == "GRAYSCALE":
                        filtered_image = self.edited_image.convert("L")
                    elif chosen_filter == "SEPIA":
                        filtered_image = self.edited_image.filter(ImageFilter.SEPIA)
                    else:
                        chosen_filter = getattr(ImageFilter, chosen_filter)
                        filtered_image = self.edited_image.filter(chosen_filter)
                    self.edited_image = filtered_image.copy()
                    self.display_image()
                    self.play_sound("brush")
                except AttributeError:
                    pass

    def adjust_brightness_contrast(self):
        self.finish_crop()  # Finish any ongoing cropping session
        if self.edited_image:
            brightness_factor = simpledialog.askfloat("Настройка яркости",
                                                      "Введите коэффициент яркости (обычно от 0.5 до 2.0):")
            contrast_factor = simpledialog.askfloat("Настройка контрастности",
                                                    "Введите коэффициент контрастности (обычно от 0.5 до 2.0):")

            if brightness_factor is not None and contrast_factor is not None:
                enhancer = ImageEnhance.Brightness(self.edited_image)
                brightened_image = enhancer.enhance(brightness_factor)

                enhancer = ImageEnhance.Contrast(brightened_image)
                contrasted_image = enhancer.enhance(contrast_factor)

                self.edited_image = contrasted_image.copy()
                self.display_image()
                self.play_sound("brush")

    def rotate_image(self):
        self.finish_crop()
        if self.edited_image:
            angle = simpledialog.askinteger("Поворот изображения", "Введите угол поворота (в градусах):", minvalue=-360,
                                            maxvalue=360)
            if angle is not None:
                rotated_image = self.edited_image.rotate(angle, expand=True)
                self.edited_image = rotated_image.copy()
                self.display_image()
                self.play_sound("camera")

    def smooth_image(self):
        self.finish_crop()
        if self.edited_image:
            radius = simpledialog.askinteger("Сглаживание изображения", "Введите радиус сглаживания:")
            if radius is not None:
                smoothed_image = self.edited_image.filter(ImageFilter.GaussianBlur(radius))
                self.edited_image = smoothed_image.copy()
                self.display_image()
                self.play_sound("brush")

    def enhance_sharpness(self):
        self.finish_crop()
        if self.edited_image:
            sharpness_factor = simpledialog.askfloat("Улучшение резкости",
                                                     "Введите коэффициент улучшения резкости (обычно от 1.0 до 3.0):")
            if sharpness_factor is not None:
                enhancer = ImageEnhance.Sharpness(self.edited_image)
                sharpened_image = enhancer.enhance(sharpness_factor)
                self.edited_image = sharpened_image.copy()
                self.display_image()
                self.play_sound("brush")

    def change_text_font(self):
        font_path = filedialog.askopenfilename(filetypes=[("Font files", "*.ttf"), ("All files", "*.*")])
        if font_path:
            try:
                self.text_font = ImageFont.truetype(font_path, size=self.text_font.getsize("A"))
            except OSError:
                pass

    def add_text_layer(self):
        self.finish_crop()
        text_entry = simpledialog.askstring("Добавление текстового слоя", "Введите текст:")
        if text_entry is not None:
            text_position = simpledialog.askstring("Позиция текста", "Укажите координаты (x, y):")
            text_font_size = simpledialog.askinteger("Размер шрифта", "Введите размер шрифта:")
            text_color = simpledialog.askstring("Цвет текста", "Введите цвет текста (например, 'red', '#00FF00'):")
            if text_position and text_font_size and text_color:
                try:
                    x, y = [int(coord) for coord in text_position.split(',')]
                    font = ImageFont.truetype("arial.ttf", size=text_font_size)
                    draw = ImageDraw.Draw(self.edited_image)
                    draw.text((x, y), text_entry, font=font, fill=text_color)
                    self.text_entries.append({"text": text_entry, "position": (x, y), "font_size": text_font_size,
                                              "font_color": text_color, "font": font})
                    self.display_image()
                    self.play_sound("brush")
                except (ValueError, OSError):
                    pass

    def remove_text_layer(self):
        if self.text_entries:
            text_to_remove = simpledialog.askstring("Удаление текстового слоя", "Введите текст, который хотите удалить:")
            if text_to_remove is not None:
                self.text_entries = [entry for entry in self.text_entries if entry["text"] != text_to_remove]
                self.edited_image = self.original_image.copy()  # Restore the original image
                for entry in self.text_entries:
                    draw = ImageDraw.Draw(self.edited_image)
                    draw.text(entry["position"], entry["text"], font=entry["font"], fill=entry["font_color"])
                self.display_image()
                self.play_sound("brush")

    def flip_vertical(self):
        self.finish_crop()
        if self.edited_image:
            flipped_image = self.edited_image.transpose(Image.FLIP_TOP_BOTTOM)
            self.edited_image = flipped_image.copy()
            self.display_image()
            self.play_sound("camera")

    def flip_horizontal(self):
        self.finish_crop()
        if self.edited_image:
            flipped_image = self.edited_image.transpose(Image.FLIP_LEFT_RIGHT)
            self.edited_image = flipped_image.copy()
            self.display_image()
            self.play_sound("camera")

    def activate_brush(self):
        self.finish_crop()
        self.canvas.bind("<B1-Motion>", self.brush_paint)

    def deactivate_brush(self):
        self.finish_crop()
        self.canvas.unbind("<B1-Motion>")

    def brush_paint(self, event):
        if self.edited_image:
            x1, y1 = (event.x - 1), (event.y - 1)
            x2, y2 = (event.x + 1), (event.y + 1)


            draw_original = ImageDraw.Draw(self.original_image)
            draw_edited = ImageDraw.Draw(self.edited_image)

            draw_original.ellipse([x1, y1, x2, y2], fill="black")
            draw_edited.ellipse([x1, y1, x2, y2], fill="black")

            self.display_image()
            self.play_sound("brush")

    def activate_eraser(self):
        self.finish_crop()
        self.canvas.bind("<B1-Motion>", self.eraser_erase)

    def eraser_erase(self, event):
        if self.edited_image:
            x1, y1 = (event.x - 5), (event.y - 5)
            x2, y2 = (event.x + 5), (event.y + 5)


            draw_original = ImageDraw.Draw(self.original_image)
            draw_edited = ImageDraw.Draw(self.edited_image)

            draw_original.rectangle([x1, y1, x2, y2], fill="white")
            draw_edited.rectangle([x1, y1, x2, y2], fill="white")

            self.display_image()
            self.play_sound("brush")

    def change_brush_size(self):
        brush_size = simpledialog.askinteger("Размер кисти", "Введите размер кисти:")
        if brush_size is not None:
            self.brush_size = brush_size

    def choose_brush_color(self):
        brush_color = colorchooser.askcolor()[1]
        if brush_color:
            self.brush_color = brush_color

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = Tk()
    root.geometry("800x600")
    app = ImageEditor(root)
    app.run()
