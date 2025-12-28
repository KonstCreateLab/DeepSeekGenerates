import pygame
import numpy as np
import random
import noise
import json
import os
from pygame.locals import *
from collections import defaultdict

class VoxelEngine:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("PyCraft")
        
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        # Параметры мира
        self.WORLD_SIZE = 128  # Увеличьте до 512 или 1024 для большего мира
        self.CHUNK_SIZE = 16
        self.RENDER_DISTANCE = 8
        
        # Генерация текстур (упрощенно)
        self.textures = self.generate_textures()
        
        # Камера
        self.camera_pos = [self.WORLD_SIZE//2, 20, self.WORLD_SIZE//2]
        self.camera_rot = [0, 0]
        
        # Мир
        self.world = {}
        self.generate_world()
        
        # UI
        self.font = pygame.font.SysFont('arial', 24)
        
        # Сохранение
        self.save_file = "world.json"
        
    def generate_textures(self):
        """Создание простых текстур"""
        textures = {}
        colors = {
            'grass': (34, 139, 34),
            'dirt': (101, 67, 33),
            'stone': (128, 128, 128),
            'sand': (194, 178, 128),
            'wood': (101, 67, 33),
            'leaf': (34, 139, 34),
            'water': (30, 144, 255),
            'cloud': (255, 255, 255)
        }
        
        for name, color in colors.items():
            tex = pygame.Surface((16, 16))
            tex.fill(color)
            # Добавляем простой шум для текстуры
            for i in range(50):
                x = random.randint(0, 15)
                y = random.randint(0, 15)
                shade = random.randint(-20, 20)
                tex.set_at((x, y), (
                    max(0, min(255, color[0] + shade)),
                    max(0, min(255, color[1] + shade)),
                    max(0, min(255, color[2] + shade))
                ))
            textures[name] = tex
            
        return textures
    
    def generate_world(self):
        """Генерация процедурного мира"""
        print("Генерация мира...")
        
        # Используем шум Перлина для генерации высот
        scale = 100.0
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0
        
        for x in range(self.WORLD_SIZE):
            for z in range(self.WORLD_SIZE):
                # Высота базового рельефа
                height = int(noise.pnoise2(x/scale, z/scale, 
                                          octaves=octaves,
                                          persistence=persistence,
                                          lacunarity=lacunarity) * 20 + 20)
                
                # Дополнительные детали
                detail = int(noise.pnoise2(x/25, z/25) * 5)
                height += detail
                
                # Создаем столбец блоков
                for y in range(height):
                    if y == height - 1:
                        block_type = 'grass' if random.random() > 0.1 else 'dirt'
                    elif y > height - 5:
                        block_type = 'dirt'
                    else:
                        if random.random() > 0.9 and y > 10:
                            block_type = 'stone'
                        else:
                            block_type = 'dirt'
                    
                    self.world[(x, y, z)] = block_type
                
                # Вода
                water_level = 15
                if height < water_level:
                    for y in range(height, water_level):
                        self.world[(x, y, z)] = 'water'
                
                # Деревья
                if height > water_level and random.random() > 0.99:
                    tree_height = random.randint(4, 7)
                    # Ствол
                    for y in range(height, height + tree_height):
                        self.world[(x, y, z)] = 'wood'
                    
                    # Листва
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            for dz in range(-2, 3):
                                if abs(dx) + abs(dy) + abs(dz) < 4:
                                    self.world[(x+dx, height+tree_height+dy, z+dz)] = 'leaf'
    
    def project_point(self, point):
        """Простая 3D проекция"""
        x, y, z = point
        
        # Относительно камеры
        x -= self.camera_pos[0]
        y -= self.camera_pos[1]
        z -= self.camera_pos[2]
        
        # Простая перспектива
        fov = 256
        factor = fov / (z + fov)
        
        screen_x = int(x * factor + self.width/2)
        screen_y = int(-y * factor + self.height/2)
        
        return screen_x, screen_y, factor
    
    def draw_block(self, pos, block_type):
        """Рисование одного блока"""
        if block_type not in self.textures:
            return
            
        screen_pos = self.project_point(pos)
        if screen_pos[2] > 0:  # Только если блок перед камерой
            size = max(4, int(16 * screen_pos[2]))
            tex = pygame.transform.scale(self.textures[block_type], (size, size))
            self.screen.blit(tex, (screen_pos[0] - size//2, screen_pos[1] - size//2))
    
    def handle_input(self):
        """Обработка ввода"""
        keys = pygame.key.get_pressed()
        speed = 0.5
        
        # Движение
        if keys[K_w]:
            self.camera_pos[2] += speed
        if keys[K_s]:
            self.camera_pos[2] -= speed
        if keys[K_a]:
            self.camera_pos[0] -= speed
        if keys[K_d]:
            self.camera_pos[0] += speed
        if keys[K_SPACE]:
            self.camera_pos[1] += speed
        if keys[K_LSHIFT]:
            self.camera_pos[1] -= speed
        
        # Вращение камеры мышью
        if pygame.mouse.get_focused():
            dx, dy = pygame.mouse.get_rel()
            self.camera_rot[0] += dx * 0.2
            self.camera_rot[1] = max(-90, min(90, self.camera_rot[1] + dy * 0.2))
            pygame.mouse.set_pos(self.width//2, self.height//2)
    
    def draw_ui(self):
        """Рисование интерфейса"""
        # FPS
        fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, (255, 255, 255))
        self.screen.blit(fps_text, (10, 10))
        
        # Позиция
        pos_text = self.font.render(
            f"Pos: {int(self.camera_pos[0])}, {int(self.camera_pos[1])}, {int(self.camera_pos[2])}", 
            True, (255, 255, 255)
        )
        self.screen.blit(pos_text, (10, 40))
        
        # Инструкции
        inst_text = self.font.render("WASD: Движение, SPACE/SHIFT: Вверх/Вниз, ESC: Выход", True, (255, 255, 255))
        self.screen.blit(inst_text, (10, self.height - 30))
    
    def save_world(self):
        """Сохранение мира в файл"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump({str(k): v for k, v in self.world.items()}, f)
            print("Мир сохранен!")
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
    
    def load_world(self):
        """Загрузка мира из файла"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    self.world = {eval(k): v for k, v in data.items()}
                print("Мир загружен!")
            except Exception as e:
                print(f"Ошибка загрузки: {e}")
    
    def run(self):
        """Главный игровой цикл"""
        running = True
        
        while running:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_p:
                        self.save_world()
                    elif event.key == K_l:
                        self.load_world()
                    elif event.key == K_r:
                        self.world = {}
                        self.generate_world()
            
            # Обновление
            self.handle_input()
            
            # Отрисовка
            self.screen.fill((135, 206, 235))  # Цвет неба
            
            # Рисование мира (оптимизированно)
            chunks_to_render = []
            camera_chunk = (
                int(self.camera_pos[0] // self.CHUNK_SIZE),
                int(self.camera_pos[2] // self.CHUNK_SIZE)
            )
            
            # Собираем блоки для отрисовки
            for dx in range(-self.RENDER_DISTANCE, self.RENDER_DISTANCE + 1):
                for dz in range(-self.RENDER_DISTANCE, self.RENDER_DISTANCE + 1):
                    chunk_x = camera_chunk[0] + dx
                    chunk_z = camera_chunk[1] + dz
                    
                    # Рисуем блоки в чанке
                    for x in range(chunk_x * self.CHUNK_SIZE, (chunk_x + 1) * self.CHUNK_SIZE):
                        for z in range(chunk_z * self.CHUNK_SIZE, (chunk_z + 1) * self.CHUNK_SIZE):
                            for y in range(64):  # Максимальная высота
                                if (x, y, z) in self.world:
                                    self.draw_block((x, y, z), self.world[(x, y, z)])
            
            # UI
            self.draw_ui()
            
            # Обновление экрана
            pygame.display.flip()
            self.clock.tick(self.FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = VoxelEngine()
    game.run()