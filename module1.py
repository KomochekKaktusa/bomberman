import pygame
import random

# Константы
BACKGROUND_COLOR = (255, 239, 213)
FPS = 40
BLOCK_SIZE = 40
GRID_WIDTH = 13
GRID_HEIGHT = 13
EXPLOSION_DURATION = 1 * FPS  # Взрыв длится 1 секунду
MAX_LIVES = 2  # Количество жизней
GAME_DURATION = 3 * 60 * FPS  # 3 минуты в кадрах

pygame.init()
window = pygame.display.set_mode((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
window.fill(BACKGROUND_COLOR)

clock = pygame.time.Clock()

class Area:
    def __init__(self, x=0, y=0, width=10, height=10, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.rect_color = color

    def colliderect(self, rect):
        return self.rect.colliderect(rect)

    def fill(self):
        pygame.draw.rect(window, self.rect_color, self.rect)

class Picture(Area):
    def __init__(self, x, y, width, height, filename=None):
        super().__init__(x, y, width, height)
        if filename:
            self.image = pygame.image.load(filename)
            self.image = pygame.transform.scale(self.image, (width, height))
        else:
            self.image = None

    def draw(self):
        if self.image:
            window.blit(self.image, (self.rect.x, self.rect.y))
        else:
            self.fill()

class Player(Picture):
    def __init__(self, x, y, width, height, filename=None):
        super().__init__(x, y, width, height, filename)
        self.speed = BLOCK_SIZE
        self.lives = MAX_LIVES

    def move(self, dx, dy, walls):
        new_rect = self.rect.move(dx * self.speed, dy * self.speed)
        if not any(new_rect.colliderect(wall.rect) for wall in walls):
            self.rect = new_rect

class Bomb(Picture):
    def __init__(self, x, y, width, height, filename=None):
        super().__init__(x, y, width, height, filename)
        self.timer = 3 * FPS  # 3 секунды до взрыва
        self.explosion_timer = None

    def update(self):
        self.timer -= 1
        if self.timer <= 0 and self.explosion_timer is None:
            self.explosion_timer = EXPLOSION_DURATION  # Запускаем таймер взрыва
            return True  # Взрыв начинается
        if self.explosion_timer is not None:
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                return False  # Взрыв заканчивается
        return True

class Block(Picture):
    def __init__(self, x, y, width, height, destructible, filename=None):
        super().__init__(x, y, width, height, filename)
        self.destructible = destructible

def generate_level(player_rect):
    level = []
    player_x = player_rect.x // BLOCK_SIZE
    player_y = player_rect.y // BLOCK_SIZE

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if x == 0 or y == 0 or x == GRID_WIDTH - 1 or y == GRID_HEIGHT - 1:
                level.append(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, False, 'img/wall_block.png'))
            elif x % 2 == 0 and y % 2 == 0:
                level.append(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, False, 'img/wall_block.png'))
            elif random.random() < 0.4:
                # Проверяем, что блок не находится в радиусе 2 клеток от игрока
                if abs(x - player_x) > 2 or abs(y - player_y) > 2:
                    level.append(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, True, 'img/destruct_block.png'))
    return level

def start_game():
    player = Player(BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, 'img/ball.png')
    bombs = []
    explosions = []
    level = generate_level(player.rect)
    exit_block = random.choice([block for block in level if block.destructible])
    exit_block.rect_color = (255, 0, 0)  # Маркируем выход

    run = True
    game = True
    game_timer = GAME_DURATION  # Таймер на 3 минуты
    can_place_bomb = True  # Игрок может поставить бомбу

    while run:
        clock.tick(FPS)
        game_timer -= 1  # Уменьшаем таймер

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.move(-1, 0, level)
                if event.key == pygame.K_RIGHT:
                    player.move(1, 0, level)
                if event.key == pygame.K_UP:
                    player.move(0, -1, level)
                if event.key == pygame.K_DOWN:
                    player.move(0, 1, level)
                if event.key == pygame.K_SPACE and can_place_bomb:
                    bomb = Bomb(player.rect.x, player.rect.y, BLOCK_SIZE, BLOCK_SIZE, 'img/tnt.png')
                    bombs.append(bomb)
                    can_place_bomb = False  # Игрок больше не может ставить бомбу

        if game:
            window.fill(BACKGROUND_COLOR)
            for block in level:
                block.draw()
            player.draw()

            # Отображение жизней
            font = pygame.font.SysFont('Arial Black', 20)
            lives_text = font.render(f"Lives: {player.lives}", True, (135, 206, 235))
            window.blit(lives_text, (10, 10))

            # Отображение таймера
            timer_text = font.render(f"Time: {game_timer // FPS // 60:02}:{game_timer // FPS % 60:02}", True, (135, 206, 235))
            window.blit(timer_text, (10, 40))

            # Проверка на завершение времени
            if game_timer <= 0:
                font1 = pygame.font.SysFont('verdana', 40)
                text = font1.render('Время вышло!', True, (255, 0, 0))
                window.blit(text, (150, 200))
                pygame.display.update()
                pygame.time.wait(2000)  # Задержка перед завершением
                return show_end_menu()

            for bomb in bombs[:]:
                bomb.draw()
                if bomb.update():
                    if bomb.timer <= 0 and bomb.explosion_timer == EXPLOSION_DURATION:  # Взрыв начинается
                        explosion_rects = [pygame.Rect(bomb.rect.x, bomb.rect.y, BLOCK_SIZE, BLOCK_SIZE)]
                        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                        for dx, dy in directions:
                            x = bomb.rect.x // BLOCK_SIZE + dx
                            y = bomb.rect.y // BLOCK_SIZE + dy
                            # Проверяем, не является ли следующий блок неразрушаемым
                            block_found = False
                            for block in level:
                                if block.rect.x // BLOCK_SIZE == x and block.rect.y // BLOCK_SIZE == y:
                                    if not block.destructible:
                                        block_found = True
                                    break
                            if not block_found:
                                explosion_rects.append(pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                        explosions.append((explosion_rects, EXPLOSION_DURATION))

                        # Уничтожение блоков
                        for rect in explosion_rects:
                            for block in level[:]:
                                if block.rect.colliderect(rect) and block.destructible:
                                    level.remove(block)
                                    if block == exit_block:
                                        font1 = pygame.font.SysFont('verdana', 40)
                                        text = font1.render('Победа!', True, (81, 200, 120))
                                        window.blit(text, (150, 200))
                                        pygame.display.update()
                                        pygame.time.wait(2000)  # Задержка перед завершением
                                        return show_end_menu()

                        # Проверка попадания игрока
                        if any(player.rect.colliderect(rect) for rect in explosion_rects):
                            player.lives -= 1
                            if player.lives <= 0:
                                return start_game()  # Начинаем заново

                    continue
                bombs.remove(bomb)
                can_place_bomb = True  # Игрок снова может ставить бомбу

            for explosion in explosions[:]:
                explosion_rects, timer = explosion
                for rect in explosion_rects:
                    pygame.draw.rect(window, (255, 0, 0), rect)
                if timer <= 0:
                    explosions.remove(explosion)
                else:
                    explosions[explosions.index(explosion)] = (explosion_rects, timer - 1)

            pygame.display.update()
    return show_end_menu()

class Label(Area):
    def set_text(self, text, fsize=18, text_color=(0, 0, 0)):
        self.image = pygame.font.SysFont('verdana', fsize).render(text, True, text_color)

    def draw(self, shift_x=0, shift_y=0):
        self.fill()
        window.blit(self.image, (self.rect.x + shift_x, self.rect.y + shift_y))

def show_end_menu():
    question = Label(150, 200, 200, 50, BACKGROUND_COLOR)
    question.set_text("Продолжить? (Y)", 20, (139, 0, 255))
    question.draw(10, 10)

    exit_button = Label(150, 250, 200, 50, BACKGROUND_COLOR)
    exit_button.set_text("Нажмите Q для выхода", 20, (139, 0, 255))
    exit_button.draw(10, 10)

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