import sys
import os
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pygame import mixer

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_volume = 50
        self.current_position = 0
        self.playlist = []
        self.current_song_index = -1
        self.is_playing = False
        self.start_time = 0  # Время начала воспроизведения
        self.paused_time = 0  # Время на момент паузы
        mixer.init()
        self.init_ui()
        
    def init_ui(self):
        # Настройка главного окна
        self.setWindowTitle('Музыкальный проигрыватель')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QListWidget {
                background-color: #3a3a3a;
                color: white;
                border: none;
                font-size: 14px;
            }
            QSlider {
                background-color: transparent;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Панель информации о треке
        info_panel = QHBoxLayout()
        self.song_label = QLabel('Трек не выбран')
        self.song_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        info_panel.addWidget(self.song_label)
        info_panel.addStretch()
        
        # Время трека
        self.time_label = QLabel('00:00 / 00:00')
        info_panel.addWidget(self.time_label)
        
        main_layout.addLayout(info_panel)
        
        # Прогресс трека
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.sliderMoved.connect(self.seek_position)
        self.progress_slider.sliderPressed.connect(self.slider_pressed)
        self.progress_slider.sliderReleased.connect(self.slider_released)
        main_layout.addWidget(self.progress_slider)
        
        # Кнопки управления
        controls_layout = QHBoxLayout()
        
        self.prev_button = QPushButton('⏮')
        self.prev_button.clicked.connect(self.prev_song)
        self.prev_button.setFixedSize(50, 50)
        
        self.play_button = QPushButton('▶')
        self.play_button.clicked.connect(self.toggle_play)
        self.play_button.setFixedSize(60, 60)
        
        self.next_button = QPushButton('⏭')
        self.next_button.clicked.connect(self.next_song)
        self.next_button.setFixedSize(50, 50)
        
        controls_layout.addStretch()
        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.next_button)
        controls_layout.addStretch()
        
        main_layout.addLayout(controls_layout)
        
        # Громкость
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel('Громкость:'))
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.current_volume)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        
        main_layout.addLayout(volume_layout)
        
        # Список воспроизведения
        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected_song)
        main_layout.addWidget(QLabel('Плейлист:'))
        main_layout.addWidget(self.playlist_widget)
        
        # Кнопки управления плейлистом
        playlist_controls = QHBoxLayout()
        
        self.add_button = QPushButton('Добавить файлы')
        self.add_button.clicked.connect(self.add_songs)
        
        self.remove_button = QPushButton('Удалить выбранное')
        self.remove_button.clicked.connect(self.remove_song)
        
        self.clear_button = QPushButton('Очистить плейлист')
        self.clear_button.clicked.connect(self.clear_playlist)
        
        playlist_controls.addWidget(self.add_button)
        playlist_controls.addWidget(self.remove_button)
        playlist_controls.addWidget(self.clear_button)
        playlist_controls.addStretch()
        
        main_layout.addLayout(playlist_controls)
        
        # Таймер для обновления прогресса
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)  # Обновление каждые 100 мс для плавности
        
        # Переменные для отслеживания времени
        self.slider_dragging = False
        self.current_song_length = 0
        
    def add_songs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            'Выберите музыкальные файлы',
            '',
            'Audio Files (*.mp3 *.wav *.ogg *.flac)'
        )
        
        for file in files:
            self.playlist.append(file)
            filename = os.path.basename(file)
            self.playlist_widget.addItem(filename)
            
        if self.current_song_index == -1 and self.playlist:
            self.current_song_index = 0
            self.load_song(self.current_song_index)
    
    def remove_song(self):
        current_row = self.playlist_widget.currentRow()
        if current_row >= 0:
            self.playlist_widget.takeItem(current_row)
            del self.playlist[current_row]
            
            if current_row == self.current_song_index:
                self.stop_music()
                self.current_song_index = -1
                if self.playlist:
                    self.current_song_index = min(current_row, len(self.playlist) - 1)
                    self.load_song(self.current_song_index)
    
    def clear_playlist(self):
        self.playlist_widget.clear()
        self.playlist = []
        self.stop_music()
        self.current_song_index = -1
        self.song_label.setText('Трек не выбран')
        self.time_label.setText('00:00 / 00:00')
        self.progress_slider.setValue(0)
    
    def load_song(self, index):
        if 0 <= index < len(self.playlist):
            mixer.music.load(self.playlist[index])
            filename = os.path.basename(self.playlist[index])
            self.song_label.setText(f'Сейчас играет: {filename}')
            self.playlist_widget.setCurrentRow(index)
            
            # Получаем длину трека
            try:
                sound = mixer.Sound(self.playlist[index])
                self.current_song_length = sound.get_length()
            except:
                self.current_song_length = 0
                
            # Сбрасываем таймеры
            self.start_time = time.time()
            self.paused_time = 0
            self.progress_slider.setValue(0)
    
    def play_selected_song(self, item):
        index = self.playlist_widget.row(item)
        if index != self.current_song_index or not self.is_playing:
            self.current_song_index = index
            self.load_song(index)
            self.play_music()
        else:
            self.pause_music()
    
    def toggle_play(self):
        if not self.playlist:
            return
            
        if not self.is_playing:
            if self.current_song_index == -1:
                self.current_song_index = 0
                self.load_song(self.current_song_index)
            self.play_music()
        else:
            self.pause_music()
    
    def play_music(self):
        if self.current_song_index >= 0:
            if self.paused_time > 0:
                # Продолжаем с места паузы
                mixer.music.play(start=self.paused_time)
                self.start_time = time.time() - self.paused_time
                self.paused_time = 0
            else:
                mixer.music.play()
                self.start_time = time.time()
            
            self.is_playing = True
            self.play_button.setText('⏸')
            mixer.music.set_volume(self.current_volume / 100)
    
    def pause_music(self):
        if self.is_playing:
            mixer.music.pause()
            self.paused_time = time.time() - self.start_time
            self.is_playing = False
            self.play_button.setText('▶')
    
    def stop_music(self):
        mixer.music.stop()
        self.is_playing = False
        self.play_button.setText('▶')
        self.paused_time = 0
        self.progress_slider.setValue(0)
        self.time_label.setText('00:00 / 00:00')
    
    def prev_song(self):
        if not self.playlist:
            return
            
        self.stop_music()
        self.current_song_index = (self.current_song_index - 1) % len(self.playlist)
        self.load_song(self.current_song_index)
        self.play_music()
    
    def next_song(self):
        if not self.playlist:
            return
            
        self.stop_music()
        self.current_song_index = (self.current_song_index + 1) % len(self.playlist)
        self.load_song(self.current_song_index)
        self.play_music()
    
    def set_volume(self, value):
        self.current_volume = value
        mixer.music.set_volume(value / 100)
    
    def slider_pressed(self):
        self.slider_dragging = True
    
    def slider_released(self):
        self.slider_dragging = False
        if self.is_playing and self.current_song_length > 0:
            position = self.progress_slider.value() / 1000
            seek_pos = position * self.current_song_length
            mixer.music.play(start=seek_pos)
            self.start_time = time.time() - seek_pos
    
    def seek_position(self, position):
        # Обновляем слайдер при перетаскивании
        if self.slider_dragging and self.current_song_length > 0:
            current_time = (position / 1000) * self.current_song_length
            total_time = self.current_song_length
            self.time_label.setText(f'{self.format_time(current_time)} / {self.format_time(total_time)}')
    
    def update_progress(self):
        if self.is_playing and self.current_song_index >= 0 and not self.slider_dragging:
            if self.current_song_length > 0:
                # Рассчитываем текущее время
                current_time = time.time() - self.start_time
                
                # Проверяем, не закончился ли трек
                if current_time >= self.current_song_length:
                    self.next_song()
                    return
                
                # Обновляем слайдер
                progress = (current_time / self.current_song_length) * 1000
                self.progress_slider.setValue(int(progress))
                
                # Обновляем время
                total_time = self.current_song_length
                self.time_label.setText(f'{self.format_time(current_time)} / {self.format_time(total_time)}')
    
    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f'{minutes:02d}:{seconds:02d}'
    
    def closeEvent(self, event):
        mixer.music.stop()
        mixer.quit()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Установка стиля
    app.setStyle('Fusion')
    
    player = MusicPlayer()
    player.show()
    
    sys.exit(app.exec_())
