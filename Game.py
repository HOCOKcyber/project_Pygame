import pygame
import sys
import os
import sqlite3
import time

FPS = 50
SIZE = WIDTH, HEIGHT = 550, 550
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption('Smile')
icon = pygame.image.load('data/icon.png')
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

pygame.mixer.init()
music = pygame.mixer.music.load('data/background.mp3')

coin = pygame.mixer.Sound('data/coin_1.wav')

X_out = 0
Y_out = 0
COLOR = 'g'
F = None


class button:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def draw(self, x, y, message, action, font_size):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pygame.draw.rect(screen, (70, 100, 200), (x, y, self.width, self.height))

            if click[0] == 1:
                if action == quit:
                    pygame.quit()
                    quit()
                else:
                    action()
        else:
            pygame.draw.rect(screen, (50, 90, 150), (x, y, self.width, self.height))

        print_text(message=message, x=x + 10, y=y + 10, font_size=font_size, font_cl=(0, 0, 0))


def print_text(message, x, y, font_cl, font_size=40, font_type=os.path.join('data', 'font.ttf')):
    font_type = pygame.font.Font(font_type, font_size)
    text = font_type.render(message, True, font_cl)
    screen.blit(text, (x, y))


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


tile_images = {
    'wall': load_image('wall.png'),
    'empty': load_image('floor.png'),
    'coin': load_image('coin.png'),
    'output': load_image('output_close.png')
}

tile_width = tile_height = 50

player = None

# Чем больше групп, тем меньше багов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
BOX_group = pygame.sprite.Group()
Coin_group = pygame.sprite.Group()
Output_group = pygame.sprite.Group()
Fugu_group = pygame.sprite.Group()


def change_color(color):
    global COLOR
    if color == 'G':
        COLOR = 'g'
    else:
        COLOR = 'o'


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Fugu(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(Fugu_group, all_sprites, BOX_group)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = load_image('fugu.png')
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.o = 0
        self.time_2 = 0

    def up(self):
        time_1 = time.clock()
        if int(time_1) % 1 == 0 and int(time_1) != self.time_2:
            self.time_2 = int(time_1)
            self.o += 1
            sprite = pygame.sprite.Sprite()
            if self.o % 2 == 0:
                sprite.image = load_image("fugu_open.png")
                sprite.rect = sprite.image.get_rect().move(
                tile_width * (self.pos_x - 1), tile_height * (self.pos_y - 1))
                Fugu_group.add(sprite)
            else:
                Fugu_group.sprites()[0].kill()
                sprite.image = load_image("fugu.png")
                sprite.rect = sprite.image.get_rect().move(
                tile_width * self.pos_x, tile_height * self.pos_y)
                BOX_group.add(sprite)


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(Coin_group, all_sprites)
        self.image = load_image('coin.png')
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Output(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, t_f):
        super().__init__(Output_group, all_sprites, BOX_group)
        self.pos_x = pos_x
        self.pos_y = pos_y
        if t_f:
            self.image = load_image('output_close.png')
        else:
            self.image = load_image('output_open.png')
        self.rect = self.image.get_rect().move(
            tile_width * self.pos_x, tile_height * self.pos_y)


class Box(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(BOX_group, all_sprites)
        self.image = load_image('wall.png')
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        super().__init__(player_group, all_sprites)
        player_image = load_image(f'slime_{COLOR}.png')
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * self.pos_x, tile_height * self.pos_y)
        self.point = 0
        self.o = 0

    def move(self, u, d, r, l, n):
        global X_out, Y_out, F
        con = sqlite3.connect('data/statistics.db')
        cur = con.cursor()
        while not pygame.sprite.spritecollideany(self, BOX_group):
            if u:
                self.pos_y -= 1
            if d:
                self.pos_y += 1
            if r:
                self.pos_x += 1
            if l:
                self.pos_x -= 1
            self.rect = self.image.get_rect().move(tile_width * self.pos_x, tile_height * self.pos_y)

            if pygame.sprite.spritecollideany(self, Coin_group):
                pygame.mixer.Sound.play(coin)
                pygame.sprite.spritecollideany(self, Coin_group).kill()
                self.point += 1
                Tile('empty', self.pos_x, self.pos_y)
                result = cur.execute(f"""SELECT coin FROM lvl_{n}""").fetchall()
                count = result[0][0]
                count += 1
                cur.execute(f"""update lvl_{n}
                set coin = {count}""")

            if self.point == 5 and pygame.sprite.spritecollideany(self, Output_group):
                choice_lvl()

            if pygame.sprite.spritecollideany(self, Fugu_group):
                con = sqlite3.connect('data/statistics.db')
                cur = con.cursor()
                result = cur.execute(f"""SELECT dead FROM lvl_{n}""").fetchall()
                count = result[0][0]
                count += 1
                cur.execute(f"""update lvl_{n}
                                set dead = {count}""")
                con.commit()
                con.close()
                dead = button(550, 550)
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    dead.draw(0, 0, 'dead', choice_lvl, 100)
                    pygame.display.flip()

        if u:
            self.pos_y += 1
        if d:
            self.pos_y -= 1
        if r:
            self.pos_x -= 1
        if l:
            self.pos_x += 1

        self.rect = self.image.get_rect().move(
            tile_width * self.pos_x, tile_height * self.pos_y)
        if self.point == 5:
            Output(X_out, Y_out, False)
        con.commit()
        con.close()


def generate_level(level):
    global X_out, Y_out, F
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Box(x, y)
            elif level[y][x] == '+':
                Coin(x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '~':
                Output(x, y, True)
                X_out = x
                Y_out = y
            elif level[y][x] == '/':
                F = Fugu(x, y)

    return new_player, x, y


def menu():
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)
    fon = pygame.transform.scale(load_image('fon_g.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    start_btn = button(100, 60)
    quit_btn = button(100, 60)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        start_btn.draw(350, 150, 'Play', choice_lvl, 40)
        quit_btn.draw(350, 250, 'Quit', quit, 40)
        pygame.display.flip()
        clock.tick(FPS)


def choice_lvl():
    global COLOR
    lvl_1 = button(120, 60)
    lvl_2 = button(120, 60)
    lvl_3 = button(120, 60)

    Color_G = button(120, 60)
    Color_O = button(140, 60)

    while True:
        if COLOR == 'g':
            fon = pygame.transform.scale(load_image('fon_g.png'), (WIDTH, HEIGHT))
        else:
            fon = pygame.transform.scale(load_image('fon_o.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        lvl_1.draw(50, 230, 'Level 1', lambda: start_game(1), 30)
        lvl_2.draw(220, 230, 'Level 2', lambda: start_game(2), 30)
        lvl_3.draw(380, 230, 'Level 3', lambda: start_game(3), 30)

        Color_G.draw(200, 400, 'GREEN', lambda: change_color('G'), 30)
        Color_O.draw(370, 400, 'ORANGE', lambda: change_color('O'), 30)
        pygame.display.flip()
        clock.tick(FPS)


def start_game(n):
    global BOX_group, tiles_group, Coin_group, player_group, Output_group, all_sprites, Fugu_group, F
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    BOX_group = pygame.sprite.Group()
    Coin_group = pygame.sprite.Group()
    Output_group = pygame.sprite.Group()
    Fugu_group = pygame.sprite.Group()
    screen.fill((0, 0, 0))
    player, level_x, level_y = generate_level(load_level(f'map{n}.txt'))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move(True, False, False, False, n)
                elif event.key == pygame.K_DOWN:
                    player.move(False, True, False, False, n)
                elif event.key == pygame.K_LEFT:
                    player.move(False, False, False, True, n)
                elif event.key == pygame.K_RIGHT:
                    player.move(False, False, True, False, n)

        if n == 3:
            F.up()
        BOX_group.draw(screen)
        tiles_group.draw(screen)
        Coin_group.draw(screen)
        player_group.draw(screen)
        Output_group.draw(screen)
        Fugu_group.draw(screen)
        print_text(f'{player.point}/5', 225, 0, font_cl=(225, 225, 0))
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    pygame.init()
    menu()
