import os
import random

import pygame
import time
from tkinter import *
import sqlite3

username = ''  # перменная имени игрока
execution = False  # переменная для основного цикла игры


def start_window():  # функция печати стартового окна
    def click():
        global username
        username = username_enter.get()
        root.destroy()
        global execution
        execution = True

    root = Tk()
    root.title('Имя')
    root.geometry('400x200')
    root.resizable(width=False, height=False)
    root['bg'] = '#fafafa'
    root.wm_attributes('-alpha', 0.7)
    username_label = Label(root, text='Введите имя', font='Arial 16 bold', bg='white', fg='black', padx=10, pady=8)
    username_label.pack()
    username_enter = Entry(root, bg='black', fg='lime', font='Arial 16')
    username_enter.pack()
    send = Button(root, text='Начать игру', command=click)
    send.pack(padx=10, pady=8)
    root.mainloop()


# если базы данных нет создаем ее
if not os.path.isfile('top_players.db'):
    db = sqlite3.connect(
        'top_players.db')
    c = db.cursor()
    c.execute("""CREATE TABLE top_players(
        name TEXT,
        coins INTEGER,
        tim REAL
    )""")
    db.close()
start_window()

pygame.init()
clock = pygame.time.Clock()
fps = 60
screen_width = 900  # определяем размеры окна программы
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))  # задаем размеры окна
pygame.display.set_caption('Platformer')  # имя программы

font_end = pygame.font.SysFont('Arial', 30, bold=True)  # определяем шрифты
font = pygame.font.SysFont('Bauhaus 93', 70)
white = (255, 255, 255)  # определяем цвета шрифтов
green = (0, 255, 0)
red = (255, 0, 0)

tile_size = 30  # размер плитки
game_over = 0  # переменная конца игры
score = 0  # счет монеток
menu = True

# иницализация переменных времени
start = time.perf_counter()
end = time.perf_counter()

# загрузка изображений
background = pygame.image.load('img/background.jpg')
restart_img = pygame.image.load('img/restart.png')
start_img = pygame.image.load('img/start.png')
end_img = pygame.image.load('img/end.png')
start_img = pygame.transform.scale(start_img, (200, 70))
end_img = pygame.transform.scale(end_img, (200, 70))


# def draw_grid():  # рисование сетки
#     for line in range(0, 30):
#         pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
#         pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))

def draw_text(text, font, color, x, y):  # печать текста в окно
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


class Btn():  # класс кнопки
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.click = False

    def draw(self):
        action = False
        mouse_pos = pygame.mouse.get_pos()  # позиция мыши
        if self.rect.collidepoint(mouse_pos):  # условие наведения мыши на кнопку
            if pygame.mouse.get_pressed()[0] == 1 and self.click == False:
                action = True
                self.click = True
                global start
                start = time.perf_counter()
        if pygame.mouse.get_pressed()[0] == 0:
            self.click = False

        screen.blit(self.image, self.rect)

        return action


class Player():  # класс персонажа
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cd = 5

        if game_over == 0:
            # слушаем нажатия клавиш
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jump == False and self.in_air == False:
                self.gr_y = -13
                self.jump = True
            if key[pygame.K_SPACE] == False:
                self.jump = False
            if key[pygame.K_LEFT]:
                dx -= 4
                self.counter += 1
                self.direct = -1
            if key[pygame.K_RIGHT]:
                dx += 4
                self.counter += 1
                self.direct = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direct == 1:
                    self.image = self.images_right[self.index]
                if self.direct == -1:
                    self.image = self.images_left[self.index]

            # обработка анимации персонажа
            if self.counter > walk_cd:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direct == 1:
                    self.image = self.images_right[self.index]
                if self.direct == -1:
                    self.image = self.images_left[self.index]

            # добавление гравитации
            self.gr_y += 1
            if self.gr_y > 10:
                self.gr_y = 10
            dy += self.gr_y

            # обработка столкновений c островками
            self.in_air = True
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.gr_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.gr_y = 0
                    elif self.gr_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.gr_y = 0
                        self.gr_y = 0
                        self.in_air = False

            # обработка столкновений c препятствиями
            if pygame.sprite.spritecollide(self, obstacle_group, False):
                global end
                end = time.perf_counter()
                game_over = -1

            if pygame.sprite.spritecollide(self, exit_group, False):
                end = time.perf_counter()
                game_over = 1

            # обновление координат
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER!', font, red, (screen_width // 2) - 200, screen_height // 2)
        # рисование персонажа
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    def reset(self, x, y):  # функция сброса положения персонажа
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):  # загрузка картинок состояний персонажа когда он смотрит влево или вправо
            img_right = pygame.image.load(f'img/player{num}.png.')
            img_right = pygame.transform.scale(img_right, (40, 70))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/death.png')
        self.dead_image = pygame.transform.scale(self.dead_image, (60, 60))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.gr_y = 0
        self.jump = False
        self.direct = 0
        self.in_air = True


class World():  # класс игрового мира
    def __init__(self, data):
        self.tile_list = []  # список плиток

        island_img = pygame.image.load('img/island.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 2:  # вывод изображения островка
                    img = pygame.transform.scale(island_img,
                                                 (tile_size, tile_size))  # масштабирование до размера плитки
                    img_rect = img.get_rect()  # преобразование картинки в прямоугольник
                    img_rect.x = col_count * tile_size  # координаты
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)  # кортеж из изображения и координат прямоугольника
                    self.tile_list.append(tile)
                if tile == 3:  # вывод изображения препятствия
                    obs = Obstacle(col_count * tile_size, row_count * tile_size + 6)
                    obstacle_group.add(obs)
                if tile == 4:  # вывод изображения монетки
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 1:  # вывод изображения выхода
                    exit = Exit(col_count * tile_size, row_count * tile_size - tile_size)
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):  # рисование плиток
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


class Obstacle(pygame.sprite.Sprite):  # класс препятствия
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/obstacle.png')
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Study(pygame.sprite.Sprite):  # класс обучения управлению
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/study.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):  # класс монеток
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/coin.png')
        self.image = pygame.transform.scale(self.image, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):  # класс выхода из игры
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(self.image, (tile_size, int(tile_size * 2)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# рандомизация монеток в верхней левой окрестности окна
def rand_coins():
    for i in range(2, 7):
        for j in range(1, 9):
            if grid_data[i][j] == 4:
                grid_data[i][j] = 0
    for i in range(2, 7):
        for j in range(1, 9):
            rand_num = random.randint(1, 8)
            if grid_data[i][j] == 0 and j == rand_num:
                grid_data[i][j] = 4


grid_data = [  # данные игрового мира: 0 - ничего  1 - выход 2 - островок  3 - препятствие 4 - монетка
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 0, 0, 0, 0, 0, 0, 4, 4, 4, 1, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 2, 2, 2, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 3, 3, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2],
    [2, 0, 4, 2, 2, 2, 2, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 2],
    [2, 0, 2, 0, 0, 0, 0, 0, 0, 4, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2],
    [2, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 2, 0, 0, 0, 0, 2],
    [2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 4, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 4, 4, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 3, 3, 3, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
]
rand_coins()

player = Player(30, screen_height - 120)  # создаем персонажа
obstacle_group = pygame.sprite.Group()  # создаем препятствия
study_group = pygame.sprite.Group()  # создаем обучение управлению
coin_group = pygame.sprite.Group()  # создаем монетки
exit_group = pygame.sprite.Group()  # создаем выход
world = World(grid_data)  # создаем мир
score_coin = Coin(tile_size // 2, tile_size // 2)  # создаем монетку для счетчика монеток
coin_group.add(score_coin)

# создаем кнопки
restart_button = Btn(screen_width // 2 - 50, screen_height // 2 + 200, restart_img)
start_button = Btn(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Btn(screen_width // 2 + 150, screen_height // 2, end_img)
global check
check = False

while execution:  # основной цикл игры
    clock.tick(fps)
    screen.blit(background, (0, 0))
    if menu == True:
        study_group.add(Study(0, 0))
        study_group.draw(screen)
        if exit_button.draw():
            execution = False
        if start_button.draw():
            menu = False
        start_button.draw()
    else:
        world.draw()
        if game_over == 0:  # если игра выполняется
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
            draw_text(str(score), font_end, white, tile_size, 0)
        obstacle_group.draw(screen)
        coin_group.draw(screen)
        game_over = player.update(game_over)
        exit_group.draw(screen)
        if game_over == -1:  # если игра проиграна
            if restart_button.draw():
                rand_coins()
                coin_group.empty()
                world = World(grid_data)
                player.reset(30, screen_height - 120)
                game_over = 0
                score = 0

        if game_over == 1:  # если игра выиграна
            draw_text(' YOU WIN!', font, green, (screen_width // 2) - 140, screen_height - 550)
            draw_text('Score: ' + str(score), font_end, white, (screen_width // 2) - 40, screen_height // 2 - 180)
            draw_text(f"Time {end - start:0.4f}", font_end, white, (screen_width // 2) - 60, screen_height // 2 - 130)

            # вывод топ 5 игроков по времени прохождения из базы данных
            if check == False:
                db = sqlite3.connect('top_players.db')  # подключение к базе данных с данными топ игроков с полями:
                # имя, кол-во очков, время
                c = db.cursor()
                c.execute("INSERT INTO top_players VALUES(?, ?, ?)", (username, score, end - start))
                db.commit()
                db.close()
                db = sqlite3.connect('top_players.db')
                c = db.cursor()
                top_players = (c.execute("SELECT * FROM top_players ORDER by tim limit 5")).fetchall()
                count_of_players = len(c.execute("SELECT * FROM top_players").fetchall())
                db.close()
                check = True
            draw_text("Топ игроков", font_end, white, (screen_width // 2) - 63, screen_height // 2 - 70)
            draw_text("Name" + " "*22 + "Score" + " "*22 + "Time", font_end, white, (screen_width // 2) - 250,
                      screen_height // 2 - 35)
            if count_of_players >= 5:
                for i in range(0, 5):
                    draw_text(str(top_players[i][0]), font_end, white, (screen_width // 2) - 250,
                              screen_height // 2 + i * 30)
                    draw_text(str(top_players[i][1]), font_end, white, (screen_width // 2), screen_height // 2 + i * 30)
                    draw_text(f"{top_players[i][2]:0.4f}", font_end, white, (screen_width // 2) + 190,
                              screen_height // 2 + i * 30)
            if count_of_players < 5:
                for i in range(0, count_of_players):
                    draw_text(str(top_players[i][0]), font_end, white, (screen_width // 2) - 250,
                              screen_height // 2 + i * 30)
                    draw_text(str(top_players[i][1]), font_end, white, (screen_width // 2), screen_height // 2 + i * 30)
                    draw_text(f"{top_players[i][2]:0.4f}", font_end, white, (screen_width // 2) + 190,
                              screen_height // 2 + i * 30)
            if restart_button.draw():
                rand_coins()
                coin_group.empty()
                world = World(grid_data)
                player.reset(30, screen_height - 120)
                check = False
                game_over = 0
                score = 0
    # draw_grid()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # условие выхода из игры
            execution = False
    pygame.display.update()

pygame.quit()
