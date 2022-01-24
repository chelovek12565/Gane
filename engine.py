from PIL import Image
from random import randint
import pygame

WIDTH, HEIGHT = 1200, 850


class Enemy(pygame.sprite.Sprite):
    def __init__(self, loc, r, path, visibility, def_mom, hp, *args):
        super(Enemy, self).__init__(*args)
        self.image = pygame.image.load(f'{path}/Idle/Idle_1.png')
        self.rect = self.image.get_rect()
        self.path = path
        self.align = 'left'
        self.hp = hp
        self.status = 'idle'
        self.def_momentum = def_mom
        self.anim_n = 60
        self.r = r
        self.momentum = 0
        self.prev_coll = {'left': False, 'right': False, 'top': False, 'bottom': False}
        self.rect.x, self.rect.y = loc[0] + r[0], loc[1] + r[1]
        self.visibility = visibility

    def update(self, player_pos=None, r=None, tiles=None):
        self.anim_n += 6
        if r:
            r1 = self.r
            self.r = r
            r = [r[0] - r1[0], r[1] - r1[1]]
            self.rect.x = self.rect.x + r[0]
            self.rect.y = self.rect.y + r[1]
        if player_pos:
            movement = [0, 0]
            if abs(self.rect.x - player_pos[0]) > 6:
                if self.rect.x > player_pos[0]:
                    if self.align != 'right':
                        self.align = 'right'
                        self.status = 'walking'
                        self.anim_n = 60
                    movement[0] -= randint(4, 6)
                elif self.rect.x < player_pos[0]:
                    if self.align != 'left':
                        self.align = 'left'
                        self.status = 'walking'
                        self.anim_n = 60
                    movement[0] += randint(4, 6)
            tiles_n = []
            for tile in tiles:
                tiles_n.append(pygame.Rect([tile[0] + r1[0], tile[1] + r1[1], 32, 32]))
            if self.align == 'left':
                if player_pos[1] / self.rect.y < 0.9 and not self.momentum and self.prev_coll['bottom'] and abs(
                        self.rect.x - player_pos[0]) <= 250 \
                        and self.collision_test(pygame.Rect(self.rect.x + self.image.get_width() // 2,
                                                            self.rect.y - 120 + self.image.get_height() // 2,
                                                            self.def_momentum * 8, 140), tiles_n):
                    self.momentum = 24
            elif self.align == 'right':
                if player_pos[1] / self.rect.y < 0.9 and not self.momentum and self.prev_coll['bottom'] and abs(
                        self.rect.x - player_pos[0]) <= 250 \
                        and self.collision_test(
                    pygame.Rect(self.rect.x - (self.def_momentum * 8) + self.image.get_width() // 2,
                                self.rect.y - 140 + self.image.get_height() // 2,
                                self.def_momentum * 8, 140), tiles_n):
                    self.momentum = 24
            if self.momentum:
                self.momentum -= 1
                movement[1] -= 6
            else:
                movement[1] += 6
            rect, collisions, tiles = self.move(movement, tiles, r1)
            self.prev_coll = collisions
            self.rect.x = rect.x
            self.rect.y = rect.y
            if self.status == 'walking':
                if self.anim_n >= 240:
                    self.anim_n = 60
                if self.align == 'left':
                    self.image = pygame.image.load(f'{self.path}/Run/Run_{self.anim_n // 60}.png')
                elif self.align == 'right':
                    self.image = pygame.transform.flip(
                        pygame.image.load(f'{self.path}/Run/Run_{self.anim_n // 60}.png'), True, False)
            elif self.status == 'idle':
                if self.anim_n >= 240:
                    self.anim_n = 60
                self.image = pygame.image.load(f'{self.path}/Idle/Idle_{self.anim_n // 60}.png')

    def collision_test(self, rect, tiles):
        hit_list = []
        for tile in tiles:
            if rect.colliderect(tile):
                hit_list.append(tile)
        return hit_list

    def move(self, movement, tiles_f, r):
        tiles = []
        for tile in tiles_f:
            tiles.append(pygame.Rect([tile[0] + r[0], tile[1] + r[1], 32, 32]))
        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
        rect = pygame.Rect([self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height()])
        rect.x += movement[0]
        hit_list = self.collision_test(rect, tiles)
        for tile in hit_list:
            if movement[0] > 0:
                rect.right = tile.left
                collision_types['right'] = True
            elif movement[0] < 0:
                rect.left = tile.right
                collision_types['left'] = True
        rect.y += movement[1]
        hit_list = self.collision_test(rect, tiles)
        for tile in hit_list:
            if movement[1] > 0:
                rect.bottom = tile.top
                collision_types['bottom'] = True
            elif movement[1] < 0:
                rect.top = tile.bottom
                # rect.y -= 55
                collision_types['top'] = True
        return rect, collision_types, tiles


class Player(pygame.sprite.Sprite):
    image = pygame.image.load('data/animations/Idle/Idle_1.png')

    def __init__(self, *args):
        super(Player, self).__init__(*args)
        self.falling = False
        self.first = True
        self.jump_n = 0
        self.jumping = False
        self.anim_n = 60
        self.align = 'right'
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH // 2 - self.rect.x
        self.rect.y = HEIGHT // 2 - self.rect.y
        self.status = 'idle'

    def update(self, r=None):
        if self.first:
            self.first = False
            self.rect.x = WIDTH // 2 - 32
            self.rect.y = HEIGHT // 2 + 22
        self.anim_n += 6
        if self.status == 'idle':
            if self.anim_n >= 600:
                self.anim_n = 60
            if self.align == 'right':
                self.image = pygame.image.load(f'data/animations/Idle/Idle_{self.anim_n // 60}.png')
            else:
                self.image = pygame.transform.flip(
                    pygame.image.load(f'data/animations/Idle/Idle_{self.anim_n // 60}.png'), True, False)
        elif self.status == 'right':
            if self.anim_n == 600:
                self.anim_n = 60
            self.image = pygame.image.load(f'data/animations/Walk/Run_{self.anim_n // 60}.png')
        elif self.status == 'left':
            if self.anim_n == 600:
                self.anim_n = 60
            self.image = pygame.transform.flip(pygame.image.load(f'data/animations/Walk/Run_{self.anim_n // 60}.png'),
                                               True, False)
        elif self.status == 'dash':
            if self.anim_n >= 150:
                self.status = self.align
                self.anim_n = 60
                return
            if self.align == 'right':
                self.image = pygame.image.load(f'data/animations/Dash/Dash_{self.anim_n // 75}.png')
            else:
                self.image = pygame.transform.flip(
                    pygame.image.load(f'data/animations/Dash/Dash_{self.anim_n // 75}.png'), True, False)
        elif self.status == 'attacking':
            if self.anim_n >= 480:
                self.status = self.align
                self.anim_n = 60
                self.rect.y += 6
                if self.align == 'left':
                    self.rect.x += 70
                    self.image = pygame.image.load('data/animations/Idle/Idle_1.png')
                return
            if self.align == 'right':
                self.image = pygame.image.load(f'data/animations/Attack/Attack_{self.anim_n // 120}.png')
            else:
                if self.anim_n == 240:
                    self.rect.x -= 70
                self.image = pygame.transform.flip(
                    pygame.image.load(f'data/animations/Attack/Attack_{self.anim_n // 120}.png'), True, False)
        if self.status != 'dash':
            n = self.jump_n // 5
            if not n:
                n += 1
            if self.jump_n and self.align == 'right':
                self.image = pygame.image.load(f'data/animations/Jump/Jump_{n}.png')
            elif self.jump_n and self.align == 'left':
                self.image = pygame.transform.flip(pygame.image.load(f'data/animations/Jump/Jump_{n}.png'), True, False)

    def align_change(self, side):
        if self.align != side:
            self.image = pygame.transform.flip(self.image, True, False)
            self.align = side
        self.status = 'idle'
        self.anim_n = 60

    def set_dash(self):
        self.status = 'dash'
        self.anim_n = 75

    def jump(self):
        self.jump_n += 1
        if self.jumping == 'up':
            if self.jump_n == 15:
                self.jump_n = 0
                self.jumping = None

    def collision_test(self, rect, tiles):
        hit_list = []
        for tile in tiles:
            if rect.colliderect(tile):
                hit_list.append(tile)
        return hit_list

    def move(self, movement, tiles_f, r):
        tiles = []
        for tile in tiles_f:
            tiles.append(pygame.Rect([tile[0] + r[0], tile[1] + r[1], 32, 32]))
        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
        rect = pygame.Rect([self.rect.x, self.rect.y, 42, 76])
        rect.x += movement[0]
        hit_list = self.collision_test(rect, tiles)
        for tile in hit_list:
            if movement[0] > 0:
                rect.right = tile.left
                collision_types['right'] = True
            elif movement[0] < 0:
                rect.left = tile.right
                collision_types['left'] = True
        rect.y += movement[1]
        hit_list = self.collision_test(rect, tiles)
        for tile in hit_list:
            if movement[1] > 0:
                rect.bottom = tile.top
                collision_types['bottom'] = True
            elif movement[1] < 0:
                rect.top = tile.bottom
                collision_types['top'] = True
        return rect, collision_types, tiles


class Camera:
    def __init__(self, player_cord, default_cords):
        x, y = default_cords
        self.def_cords = default_cords
        x *= 32
        y *= 32 - 5
        px, py = player_cord
        self.r = [px - x, py - y]
        self.r0 = self.r.copy()

    def movement(self, n=6, player=None, side=None):
        if not side:
            return self.r
        can = 0
        for i in range(1, n + 1):
            if player.can_go(side, self.r, i):
                can += 1
        if side == 'left':
            x, y = self.r
            self.r = [x + can, y]
            return self.r
        elif side == 'right':
            x, y = self.r
            self.r = [x - can, y]
            return self.r
        elif side == 'down':
            x, y = self.r
            self.r = [x, y - can]
            return self.r
        elif side == 'up':
            x, y = self.r
            self.r = [x, y + can]
            return self.r

    def re_init(self, new_player_cords):
        x, y = self.def_cords
        x *= 32
        y *= 32 - 5
        px, py = new_player_cords
        went = self.r[0] - self.r0[0], self.r[1] - self.r0[1]
        self.r = [px - x + went[0], py - y + went[1]]
        self.r0 = [px - x, py - y]


class Level(pygame.sprite.Sprite):
    def __init__(self, image, size, *args):
        super(Level, self).__init__(*args)
        self.image = pygame.image.frombuffer(image, size, 'RGB')
        self.rect = self.image.get_rect()

    def update(self, r):
        x, y = r
        self.rect.x = x
        self.rect.y = y


class Bar(pygame.sprite.Sprite):
    def __init__(self, n, path, cords, size, *args):
        super(Bar, self).__init__(*args)
        self.n = n
        self.image = pygame.image.load(path)
        self.rect.x, self.rect.y = cords

    # def update(self, cords, n):


def load_level(filename):
    file = open(f'data/levels/{filename}', 'rt').read().split('\n')

    tiles = []
    enemies = []
    im = Image.new('RGB', (len(file[0]) * 32, len(file) * 32), (66, 40, 53))
    wall = Image.open('data/wall.png')
    wall_2 = Image.open('data/wall_2.png')
    for i in range(len(file)):
        for j in range(len(file[0])):
            symbol = file[i][j]
            if symbol == '#':
                tiles.append([j * 32, i * 32, 32, 32])
                im.paste(wall_2, (j * 32, i * 32, (j + 1) * 32, (i + 1) * 32))
            elif symbol == '@':
                im.paste(wall, (j * 32, i * 32, (j + 1) * 32, (i + 1) * 32))
                player_cord = (j, i)
            elif symbol == 'e':
                enemies.append((j, i))
                im.paste(wall, (j * 32, i * 32, (j + 1) * 32, (i + 1) * 32))
            else:
                im.paste(wall, (j * 32, i * 32, (j + 1) * 32, (i + 1) * 32))

    level = Level(im.tobytes(), im.size)
    return level, player_cord, tiles, enemies
