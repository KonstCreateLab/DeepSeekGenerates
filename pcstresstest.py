import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import math
import psutil
import random
import os
from datetime import datetime

class PCStressTester:
    def __init__(self, root):
        self.root = root
        self.root.title("PC Stress Tester (Educational)")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        # Переменные
        self.is_running = False
        self.test_thread = None
        self.cpu_load = 0
        self.ram_load = 0
        self.test_duration = 60  # секунд по умолчанию
        self.start_time = None
        
        # Создание интерфейса
        self.create_widgets()
        
        # Запуск мониторинга
        self.update_system_info()
    
    def create_widgets(self):
        # Стили
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'))
        
        # Заголовок
        title_frame = ttk.Frame(self.root)
        title_frame.pack(pady=10)
        
        ttk.Label(title_frame, text="PC Stress Tester", style='Title.TLabel').pack()
        ttk.Label(title_frame, text="Educational Purposes Only!", font=('Arial', 10)).pack()
        
        # Фрейм с информацией о системе
        info_frame = ttk.LabelFrame(self.root, text="System Information", padding=10)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        self.cpu_label = ttk.Label(info_frame, text="CPU Usage: --%")
        self.cpu_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        self.ram_label = ttk.Label(info_frame, text="RAM Usage: --%")
        self.ram_label.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        self.temp_label = ttk.Label(info_frame, text="CPU Temp: --°C")
        self.temp_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        
        self.freq_label = ttk.Label(info_frame, text="CPU Freq: -- GHz")
        self.freq_label.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Фрейм настроек теста
        settings_frame = ttk.LabelFrame(self.root, text="Test Settings", padding=10)
        settings_frame.pack(fill='x', padx=20, pady=10)
        
        # Нагрузка ЦПУ
        ttk.Label(settings_frame, text="CPU Load (%):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.cpu_slider = ttk.Scale(settings_frame, from_=10, to=100, orient='horizontal')
        self.cpu_slider.set(70)
        self.cpu_slider.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        self.cpu_value_label = ttk.Label(settings_frame, text="70%")
        self.cpu_value_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Нагрузка ОЗУ
        ttk.Label(settings_frame, text="RAM Load (%):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.ram_slider = ttk.Scale(settings_frame, from_=10, to=90, orient='horizontal')
        self.ram_slider.set(50)
        self.ram_slider.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        self.ram_value_label = ttk.Label(settings_frame, text="50%")
        self.ram_value_label.grid(row=1, column=2, padx=5, pady=5)
        
        # Длительность теста
        ttk.Label(settings_frame, text="Duration (sec):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.duration_var = tk.StringVar(value="60")
        duration_spin = ttk.Spinbox(settings_frame, from_=10, to=3600, textvariable=self.duration_var, width=10)
        duration_spin.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        # Тип теста
        ttk.Label(settings_frame, text="Test Type:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.test_type = tk.StringVar(value="cpu_ram")
        ttk.Radiobutton(settings_frame, text="CPU + RAM", variable=self.test_type, value="cpu_ram").grid(row=3, column=1, sticky='w', padx=5)
        ttk.Radiobutton(settings_frame, text="CPU Only", variable=self.test_type, value="cpu_only").grid(row=3, column=2, sticky='w', padx=5)
        ttk.Radiobutton(settings_frame, text="RAM Only", variable=self.test_type, value="ram_only").grid(row=3, column=3, sticky='w', padx=5)
        
        # Привязка событий слайдеров
        self.cpu_slider.configure(command=self.update_cpu_label)
        self.ram_slider.configure(command=self.update_ram_label)
        
        # Прогресс теста
        self.progress_frame = ttk.LabelFrame(self.root, text="Test Progress", padding=10)
        self.progress_frame.pack(fill='x', padx=20, pady=10)
        
        self.time_label = ttk.Label(self.progress_frame, text="Time elapsed: 0s / 0s")
        self.time_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        # Кнопки управления
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start Stress Test", command=self.start_test, width=20)
        self.start_button.grid(row=0, column=0, padx=10)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Test", command=self.stop_test, width=20, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=10)
        
        # Статус
        self.status_label = ttk.Label(self.root, text="Ready", relief='sunken', anchor='w')
        self.status_label.pack(fill='x', padx=20, pady=10)
        
        # Консоль вывода
        console_frame = ttk.LabelFrame(self.root, text="Log", padding=10)
        console_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.console_text = tk.Text(console_frame, height=6, width=80)
        self.console_text.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(self.console_text, command=self.console_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.console_text.configure(yscrollcommand=scrollbar.set)
        
        # Заполнение информацией
        self.log_message("PC Stress Tester initialized")
        self.log_message("WARNING: For educational purposes only!")
        self.log_message("Use with caution - may cause system instability")
    
    def update_cpu_label(self, value):
        self.cpu_value_label.config(text=f"{int(float(value))}%")
    
    def update_ram_label(self, value):
        self.ram_value_label.config(text=f"{int(float(value))}%")
    
    def update_system_info(self):
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_label.config(text=f"CPU Usage: {cpu_percent:.1f}%")
            
            # RAM usage
            ram = psutil.virtual_memory()
            self.ram_label.config(text=f"RAM Usage: {ram.percent:.1f}%")
            
            # CPU frequency
            freq = psutil.cpu_freq()
            if freq:
                self.freq_label.config(text=f"CPU Freq: {freq.current/1000:.2f} GHz")
            
            # CPU temperature (только для Linux)
            try:
                temps = psutil.sensors_temperatures()
                if 'coretemp' in temps:
                    core_temp = temps['coretemp'][0].current
                    self.temp_label.config(text=f"CPU Temp: {core_temp:.1f}°C")
            except:
                self.temp_label.config(text="CPU Temp: N/A")
                
        except Exception as e:
            self.log_message(f"Error updating system info: {e}")
        
        # Повторяем каждую секунду
        if not self.is_running:
            self.root.after(1000, self.update_system_info)
    
    def start_test(self):
        if self.is_running:
            return
        
        self.cpu_load = int(self.cpu_slider.get())
        self.ram_load = int(self.ram_slider.get())
        
        try:
            self.test_duration = int(self.duration_var.get())
        except:
            self.test_duration = 60
        
        if self.test_duration < 10:
            self.test_duration = 10
        
        self.is_running = True
        self.start_time = time.time()
        
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        self.progress_bar['maximum'] = self.test_duration
        self.progress_bar['value'] = 0
        
        # Запуск теста в отдельном потоке
        self.test_thread = threading.Thread(target=self.run_stress_test, daemon=True)
        self.test_thread.start()
        
        self.log_message(f"Starting stress test: CPU={self.cpu_load}%, RAM={self.ram_load}%, Duration={self.test_duration}s")
        self.status_label.config(text=f"Test running...")
        
        # Запуск обновления прогресса
        self.update_progress()
    
    def run_stress_test(self):
        test_type = self.test_type.get()
        
        if test_type in ["cpu_ram", "cpu_only"]:
            self.cpu_stress_thread = threading.Thread(target=self.cpu_stress, daemon=True)
            self.cpu_stress_thread.start()
        
        if test_type in ["cpu_ram", "ram_only"]:
            self.ram_stress_thread = threading.Thread(target=self.ram_stress, daemon=True)
            self.ram_stress_thread.start()
        
        # Ожидание завершения теста
        time.sleep(self.test_duration)
        
        if self.is_running:
            self.root.after(0, self.test_completed)
    
    def cpu_stress(self):
        """Создание нагрузки на CPU"""
        self.log_message("CPU stress test started")
        
        target_load = self.cpu_load / 100.0
        
        while self.is_running:
            start_time = time.time()
            
            # Вычисления для создания нагрузки
            for _ in range(int(100000 * target_load)):
                math.sqrt(random.random() * 1000)
                math.sin(random.random() * 3.14)
                math.log(random.random() + 1)
            
            # Корректировка времени для достижения целевой нагрузки
            work_time = time.time() - start_time
            sleep_time = work_time * ((1 - target_load) / target_load) if target_load > 0 else 0.1
            
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def ram_stress(self):
        """Создание нагрузки на RAM"""
        self.log_message("RAM stress test started")
        
        target_mb = (psutil.virtual_memory().total * (self.ram_load / 100.0)) / (1024 * 1024)
        chunk_size = 10  # MB за раз
        data_chunks = []
        
        try:
            while self.is_running and len(data_chunks) * chunk_size < target_mb:
                # Выделяем память
                data_chunks.append(bytearray(chunk_size * 1024 * 1024))
                
                # Записываем случайные данные
                for i in range(0, len(data_chunks[-1]), 4096):
                    data_chunks[-1][i] = random.randint(0, 255)
                
                current_mb = len(data_chunks) * chunk_size
                if current_mb % 100 == 0:
                    self.log_message(f"Allocated {current_mb} MB of RAM")
                
                time.sleep(0.1)
            
            # Удерживаем память до конца теста
            while self.is_running:
                # Читаем/записываем в память для создания активности
                if data_chunks:
                    chunk = random.choice(data_chunks)
                    if len(chunk) > 0:
                        chunk[0] = (chunk[0] + 1) % 256
                time.sleep(0.5)
                
        finally:
            # Освобождаем память
            self.log_message(f"Releasing {len(data_chunks) * chunk_size} MB of RAM")
            data_chunks.clear()
    
    def update_progress(self):
        if not self.is_running:
            return
        
        elapsed = time.time() - self.start_time
        progress = min(elapsed, self.test_duration)
        
        self.progress_bar['value'] = progress
        self.time_label.config(text=f"Time elapsed: {int(elapsed)}s / {self.test_duration}s")
        
        if elapsed >= self.test_duration:
            self.test_completed()
        else:
            self.root.after(100, self.update_progress)
    
    def test_completed(self):
        self.is_running = False
        
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        self.status_label.config(text="Test completed")
        self.log_message("Stress test completed successfully")
        
        # Обновляем информацию о системе
        self.update_system_info()
    
    def stop_test(self):
        if not self.is_running:
            return
        
        self.is_running = False
        
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        self.status_label.config(text="Test stopped by user")
        self.log_message("Stress test stopped by user")
        
        # Ждем завершения потоков
        if self.test_thread and self.test_thread.is_alive():
            self.test_thread.join(timeout=2)
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        
        self.console_text.insert('end', log_line)
        self.console_text.see('end')
        
        # Ограничиваем размер лога
        lines = int(self.console_text.index('end-1c').split('.')[0])
        if lines > 100:
            self.console_text.delete('1.0', '2.0')
    
    def on_closing(self):
        if self.is_running:
            if messagebox.askokcancel("Quit", "Stress test is running. Are you sure you want to quit?"):
                self.is_running = False
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = PCStressTester(root)
    
    # Обработка закрытия окна
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    # Проверка наличия psutil
    try:
        import psutil
    except ImportError:
        print("Installing required package: psutil")
        import subprocess
        subprocess.check_call(["pip", "install", "psutil"])
        import psutil
    
    main()
