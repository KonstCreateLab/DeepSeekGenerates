import tkinter as tk
from tkinter import ttk, font
import time
import datetime

class PrecisionClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Часы высокой точности")
        self.root.geometry("650x450")
        self.root.resizable(True, True)
        
        # Настройка стилей
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Запуск обновления времени
        self.update_time()
        
    def setup_styles(self):
        """Настройка стилей элементов"""
        self.clock_font = font.Font(family="DS-Digital", size=72, weight="bold")
        self.date_font = font.Font(family="Segoe UI", size=24)
        self.info_font = font.Font(family="Consolas", size=14)
        
        # Если шрифт DS-Digital не установлен, используем Consolas
        if "DS-Digital" not in font.families():
            self.clock_font = font.Font(family="Consolas", size=72, weight="bold")
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Название программы
        title_label = ttk.Label(
            main_frame,
            text="Часы с миллисекундной точностью",
            font=("Segoe UI", 20, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Основные часы (цифровые)
        clock_frame = ttk.LabelFrame(main_frame, text="Цифровые часы", padding="20")
        clock_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))
        
        self.clock_label = tk.Label(
            clock_frame,
            text="00:00:00.000",
            font=self.clock_font,
            bg="black",
            fg="#00FF00",
            padx=30,
            pady=20,
            relief="ridge",
            borderwidth=5
        )
        self.clock_label.pack()
        
        # Дата
        self.date_label = ttk.Label(
            clock_frame,
            text="",
            font=self.date_font
        )
        self.date_label.pack(pady=(15, 0))
        
        # Фрейм с дополнительной информацией
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Левая колонка с системным временем
        left_info = ttk.LabelFrame(info_frame, text="Системная информация", padding="15")
        left_info.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Часовой пояс
        tz_label = ttk.Label(left_info, text="Часовой пояс:", font=self.info_font)
        tz_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.tz_value = ttk.Label(left_info, text="", font=self.info_font)
        self.tz_value.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Текущая дата в разных форматах
        date_label = ttk.Label(left_info, text="Дата (ISO):", font=self.info_font)
        date_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.date_iso = ttk.Label(left_info, text="", font=self.info_font)
        self.date_iso.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        date_label2 = ttk.Label(left_info, text="Дата (полн.):", font=self.info_font)
        date_label2.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.date_full = ttk.Label(left_info, text="", font=self.info_font)
        self.date_full.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Правая колонка с технической информацией
        right_info = ttk.LabelFrame(info_frame, text="Техническая информация", padding="15")
        right_info.grid(row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Таймштамп UNIX
        unix_label = ttk.Label(right_info, text="UNIX время:", font=self.info_font)
        unix_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.unix_time = ttk.Label(right_info, text="", font=self.info_font)
        self.unix_time.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Частота обновления
        update_label = ttk.Label(right_info, text="Обновление:", font=self.info_font)
        update_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.update_freq = ttk.Label(right_info, text="1 мс", font=self.info_font)
        self.update_freq.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Точность
        precision_label = ttk.Label(right_info, text="Точность:", font=self.info_font)
        precision_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.precision = ttk.Label(right_info, text="±1 мс", font=self.info_font)
        self.precision.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        # Кнопка паузы/продолжения
        self.pause_button = ttk.Button(
            button_frame,
            text="Пауза",
            command=self.toggle_pause,
            width=15
        )
        self.pause_button.grid(row=0, column=0, padx=5)
        
        # Кнопка смены темы
        self.theme_button = ttk.Button(
            button_frame,
            text="Сменить тему",
            command=self.toggle_theme,
            width=15
        )
        self.theme_button.grid(row=0, column=1, padx=5)
        
        # Кнопка выхода
        exit_button = ttk.Button(
            button_frame,
            text="Выход",
            command=self.root.quit,
            width=15
        )
        exit_button.grid(row=0, column=2, padx=5)
        
        # Статусная строка
        self.status_bar = ttk.Label(
            main_frame,
            text="Часы активны. Обновление каждую миллисекунду.",
            relief="sunken",
            anchor=tk.W,
            padding=5
        )
        self.status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # Переменные состояния
        self.is_paused = False
        self.dark_theme = False
        self.last_update = time.time()
        self.update_count = 0
        
    def get_precise_time(self):
        """Получение точного времени с миллисекундами"""
        now = datetime.datetime.now()
        milliseconds = now.microsecond // 1000
        
        # Форматирование времени
        time_str = now.strftime(f"%H:%M:%S.{milliseconds:03d}")
        
        # Форматирование даты
        date_str = now.strftime("%d %B %Y года")
        date_iso = now.strftime("%Y-%m-%d")
        date_full = now.strftime("%A, %d %B %Y")
        
        # UNIX время с миллисекундами
        unix_time = time.time()
        
        return {
            'time': time_str,
            'date': date_str,
            'date_iso': date_iso,
            'date_full': date_full,
            'unix': unix_time,
            'tz': time.tzname[0],
            'hour': now.hour,
            'minute': now.minute,
            'second': now.second,
            'ms': milliseconds
        }
    
    def update_time(self):
        """Обновление отображения времени"""
        if not self.is_paused:
            # Получаем точное время
            time_data = self.get_precise_time()
            
            # Обновляем основные часы
            self.clock_label.config(text=time_data['time'])
            
            # Обновляем дату
            self.date_label.config(text=time_data['date'])
            
            # Обновляем дополнительную информацию
            self.tz_value.config(text=time_data['tz'])
            self.date_iso.config(text=time_data['date_iso'])
            self.date_full.config(text=time_data['date_full'])
            self.unix_time.config(text=f"{time_data['unix']:.3f}")
            
            # Меняем цвет в зависимости от времени суток
            self.update_clock_color(time_data['hour'])
            
            # Обновляем статусную строку
            current_time = time.time()
            if self.update_count % 100 == 0:  # Каждые 100 обновлений
                elapsed = current_time - self.last_update
                freq = 100 / elapsed if elapsed > 0 else 0
                self.status_bar.config(
                    text=f"Часы активны. Частота обновления: ~{freq:.1f} Гц. Время: {time_data['time']}"
                )
                self.last_update = current_time
                self.update_count = 0
            
            self.update_count += 1
        
        # Планируем следующее обновление
        self.root.after(1, self.update_time)
    
    def update_clock_color(self, hour):
        """Изменение цвета часов в зависимости от времени суток"""
        if self.dark_theme:
            bg_color = "black"
            fg_color = "#00FF00"
        else:
            # Дневной/ночной режим по времени
            if 6 <= hour < 18:
                bg_color = "white"
                fg_color = "black"
            else:
                bg_color = "#2C3E50"
                fg_color = "#ECF0F1"
        
        self.clock_label.config(bg=bg_color, fg=fg_color)
    
    def toggle_pause(self):
        """Пауза/продолжение обновления времени"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.pause_button.config(text="Продолжить")
            self.status_bar.config(text="Часы на паузе. Время остановлено.")
        else:
            self.pause_button.config(text="Пауза")
            self.status_bar.config(text="Часы активны. Обновление каждую миллисекунду.")
    
    def toggle_theme(self):
        """Переключение между светлой и темной темами"""
        self.dark_theme = not self.dark_theme
        
        if self.dark_theme:
            self.root.configure(bg="#2C3E50")
            self.status_bar.configure(background="#34495E", foreground="white")
            self.theme_button.config(text="Светлая тема")
        else:
            self.root.configure(bg="SystemButtonFace")
            self.status_bar.configure(background="SystemButtonFace", foreground="black")
            self.theme_button.config(text="Темная тема")

def main():
    """Основная функция запуска программы"""
    root = tk.Tk()
    
    # Настройка иконки
    try:
        root.iconbitmap(default="clock.ico")
    except:
        # Создаем простую иконку, если файл не найден
        pass
    
    # Установка минимального размера окна
    root.minsize(600, 400)
    
    # Настройка адаптивности
    for i in range(4):
        root.grid_rowconfigure(i, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    # Создание и запуск приложения
    app = PrecisionClock(root)
    
    # Запуск основного цикла
    root.mainloop()

if __name__ == "__main__":
    main()