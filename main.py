import pygame
import sys
import os
import time

pygame.init()
FPS = 50
pygame.display.set_caption('Платформы')
size = WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
clock = pygame.time.Clock()
t0 = time.time()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()

    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def finish_screen():
    intro_text = open('data/res.txt').readlines()[1:]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'portal': load_image('portal.png')
}
player_image = load_image('hero1.png')
buu_image = load_image('hero.png')
tile_width = tile_height = 50
tile_qroup = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, posx, posy):
        super().__init__(tile_qroup, all_sprites)
        self.image = tile_images[tile_type]
        if tile_type == 'wall':
            wall_group.add(self)
        if tile_type == 'portal':
            portal_group.add(self)
        self.rect = self.image.get_rect().move(tile_width * posx, tile_height * posy)


player_group = pygame.sprite.Group()
player = None

buu_group = pygame.sprite.Group()
buug = []


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 7, tile_height * pos_y + 5)


class Buu(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(buu_group, all_sprites)
        self.image = buu_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 7, tile_height * pos_y + 5)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '8':
                Tile('empty', x, y)
                Tile('portal', x, y)
            elif level[y][x] == '^':
                Tile('empty', x, y)
                buug.append([Buu(x, y), True])
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def newlvl(name):
    global tile_qroup
    global wall_group
    global portal_group
    global buug
    global buu_group
    tile_qroup = pygame.sprite.Group()
    wall_group = pygame.sprite.Group()
    portal_group = pygame.sprite.Group()

    global player, player_group
    player_group = pygame.sprite.Group()
    player = None

    buu_group = pygame.sprite.Group()
    buug = []

    running = True
    player, level_x, level_y = generate_level(load_level(name + '.txt'))

    lifes = 3

    while running:
        for i in buug:
            if i[1]:
                i[0].rect.top += 1
                if pygame.sprite.spritecollideany(i[0], wall_group):
                    i[0].rect.top -= 1
                    i[1] = False
            else:
                i[0].rect.top -= 1
                if pygame.sprite.spritecollideany(i[0], wall_group):
                    i[0].rect.top += 1
                    i[1] = True
        buu_group.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if player is not None:
                if pygame.sprite.spritecollideany(player, wall_group) is None:

                    if pygame.sprite.spritecollideany(player, buu_group):

                        lifes -= 1
                        if lifes != 0:
                            player_group = pygame.sprite.Group()
                            player = None
                            tile_qroup = pygame.sprite.Group()
                            wall_group = pygame.sprite.Group()
                            portal_group = pygame.sprite.Group()
                            buug = []
                            buu_group = pygame.sprite.Group()

                            player, level_x, level_y = generate_level(load_level(name + '.txt'))
                        else:
                            running = False

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                        player.rect.top += 50
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.top -= 50
                        if pygame.sprite.spritecollideany(player, portal_group):
                            if name == 'lwvel4':
                                f = open('data/res.txt', 'r+')
                                f.writelines(f'{int(f.readlines()[-1].split()[0]) + 1} {int(time.time() - t0)}' + '\n')
                                f.close()
                                running = False
                            else:
                                player_group = pygame.sprite.Group()
                                player = None
                                tile_qroup = pygame.sprite.Group()
                                wall_group = pygame.sprite.Group()
                                portal_group = pygame.sprite.Group()
                                buug = []
                                buu_group = pygame.sprite.Group()
                                name = name[:-1] + str(int(name[-1]) + 1)

                                player, level_x, level_y = generate_level(load_level(name + '.txt'))
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                        player.rect.top -= 50
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.top += 50
                        if pygame.sprite.spritecollideany(player, portal_group):

                            if name == 'lwvel4':
                                f = open('data/res.txt', 'r+')
                                f.writelines(f'{int(f.readlines()[-1].split()[0]) + 1} {int(time.time() - t0)}' + '\n')
                                f.close()
                                running = False
                            else:
                                player_group = pygame.sprite.Group()
                                player = None
                                tile_qroup = pygame.sprite.Group()
                                wall_group = pygame.sprite.Group()
                                portal_group = pygame.sprite.Group()
                                buug = []
                                buu_group = pygame.sprite.Group()
                                name = name[:-1] + str(int(name[-1]) + 1)

                                player, level_x, level_y = generate_level(load_level(name + '.txt'))
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                        player.rect.left -= 50
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.left += 50
                        if pygame.sprite.spritecollideany(player, portal_group):
                            if name == 'lwvel4':
                                f = open('data/res.txt', 'r+')
                                f.writelines(f'{int(f.readlines()[-1].split()[0]) + 1} {int(time.time() - t0)}' + '\n')
                                f.close()
                                running = False
                            else:
                                player_group = pygame.sprite.Group()
                                player = None
                                tile_qroup = pygame.sprite.Group()
                                wall_group = pygame.sprite.Group()
                                portal_group = pygame.sprite.Group()
                                buug = []
                                buu_group = pygame.sprite.Group()
                                name = name[:-1] + str(int(name[-1]) + 1)

                                player, level_x, level_y = generate_level(load_level(name + '.txt'))
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                        player.rect.left += 50
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.left -= 50
                        if pygame.sprite.spritecollideany(player, portal_group):
                            if name == 'lwvel4':
                                f = open('data/res.txt', 'r+')
                                f.writelines(f'{int(f.readlines()[-1].split()[0]) + 1} {int(time.time() - t0)}' + '\n')
                                f.close()
                                running = False
                            else:
                                player_group = pygame.sprite.Group()
                                player = None
                                tile_qroup = pygame.sprite.Group()
                                wall_group = pygame.sprite.Group()
                                portal_group = pygame.sprite.Group()
                                buug = []
                                buu_group = pygame.sprite.Group()
                                name = name[:-1] + str(int(name[-1]) + 1)

                                player, level_x, level_y = generate_level(load_level(name + '.txt'))
        screen.fill((255, 255, 255))
        all_sprites.draw(screen)
        all_sprites.update()
        tile_qroup.draw(screen)
        player_group.draw(screen)
        buu_group.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()


if __name__ == '__main__':
    start_screen()
    newlvl('lwvel2')
    finish_screen()
    pygame.quit()
