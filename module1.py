#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Студент
#
# Created:     08.10.2024
# Copyright:   (c) Студент 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import pygame

BACKGROUND_COLOR = (143, 232, 202)
FPS = 40

pygame.init()
window = pygame.display.set_mode((500, 500))
window.fill(BACKGROUND_COLOR)

clock = pygame.time.Clock()
clock.tick(FPS)

class Area:
    def __init__(self, x=0, y=0, width=10, height=10, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.rect_color = color

    def colliderect(self, rect):
        return self.rect.colliderect(rect)

    def fill(self):
        ''' Отрисовывает прямоугольник self.rect в игровой сцене window'''
        pygame.draw.rect(window, self.rect_color, self.rect)

    def outline(self, frame_color, thickness):
        ''' Отрисовывает рамку толщиной thickness и цветом frame_color'''
        pygame.draw.rect(window, frame_color, self.rect, thickness)

    def collidepoint(self, x, y):
        ''' Возвращает True, если точка с координатами x, y находится внутри прямоугольника self.rect'''
        return self.rect.collidepoint(x, y)

class Picture(Area):
    def __init__(self, x=0, y=0, width=5, height=5, filename='img/enemy.png'):
        super().__init__(x, y, width, height)
        self.image = pygame.image.load(filename)
        self.image = pygame.transform.scale(self.image, (width, height))

    def draw(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Label(Area):
    def set_text(self, text, fsize=18, text_color=BACKGROUND_COLOR):
        self.image = pygame.font.SysFont('verdana', fsize).render(text, True, text_color)

    def draw(self, frame_color, thickness, shift_x=0, shift_y=0):
        self.fill()
        self.outline(frame_color, thickness)
        window.blit(self.image, (self.rect.x + shift_x, self.rect.y + shift_y))


def start_game():

    platform = Picture(170, 450, 190, 13, 'img/platform.png')
    ball = Picture(200, 410, 40, 40, 'img/ball.png')

    monsters = []
    for row in range(3):
        for i in range(9 - row):
            monsters.append(Picture(5 + row * 25 + i * 55, 5 + row * 60, 50, 50))

    run = True
    game = True
    move_right, move_left = False, False
    speed_x, speed_y = 1, 1

    destroyed_monsters = 0
    increase_speed_interval = 1
    speed_increase_value = 1
    while run:
        clock.tick(FPS)
        if ball.rect.y > platform.rect.y + 35:
            font1 = pygame.font.SysFont('verdana', 40)
            text = font1.render('Проигрыш', True, (238, 49, 69))
            window.blit(text, (150, 200))
            pygame.display.update()
            game = False
            break
        if len(monsters) == 0:
            font1 = pygame.font.SysFont('verdana', 40)
            text = font1.render('Победа', True, (81, 200, 120))
            window.blit(text, (170, 200))
            pygame.display.update()
            game = False
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_left = True
                if event.key == pygame.K_RIGHT:
                    move_right = True
                if event.key == pygame.K_ESCAPE:
                    run = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    move_left = False
                if event.key == pygame.K_RIGHT:
                    move_right = False
        if game:
            window.fill(BACKGROUND_COLOR)
            ball.rect.x -= speed_x
            ball.rect.y -= speed_y

            if move_left:
                platform.rect.x -= 20
            if move_right:
                platform.rect.x += 20

            if ball.rect.x > 450 or ball.rect.x < 0:
                speed_x *= -1
            if ball.rect.y <= 0:
                speed_y *= -1

            if ball.colliderect(platform.rect):
                speed_y = - speed_y

            ball.draw()
            platform.draw()
            for monster in monsters:
                if ball.colliderect(monster):
                    monsters.remove(monster)
                    destroyed_monsters += 1
                    speed_y *= -1
                    if destroyed_monsters % increase_speed_interval == 0:
                        if speed_x > 0:
                            speed_x *= -speed_increase_value
                        else:
                            speed_x -= speed_increase_value

                        if speed_y > 0:
                            speed_y *= -speed_increase_value
                        else:
                            speed_y -= speed_increase_value
                else:
                    monster.draw()

            pygame.display.update()
    return show_end_menu()

def show_end_menu():

    question = Label(200, 250, 0.1, 0.1, BACKGROUND_COLOR)
    question.set_text("Продолжить? (Y)", 15, (139, 0, 255))
    question.draw(0, 0)

    exit_button = Label(175, 280, 0.1, 0.1, BACKGROUND_COLOR)
    exit_button.set_text("Нажмите Q для выхода", 15, (139, 0, 255))
    exit_button.draw(0, 0)

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()

game_running = True

while game_running:
    starting_over = start_game()