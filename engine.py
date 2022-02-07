from PIL import Image, ImageDraw
from random import randint, sample
import pygame
import pprint
WIDTH, HEIGHT = 1200, 850


class Enemy(pygame.sprite.Sprite):
    def __init__(self, loc, r, path, visibility, def_mom, hp, *args):
        super(Enemy, self).__init__(*args)
        self.image = pygame.image.load(f'{path}/Idle/Idle_1.png')
        self.rect = self.image.get_rect()
        self.path = path
        self.align = 'left'
        self.hp = hp
        self.cd = 0
        self.status = 'idle'
        self.def_momentum = def_mom
        self.anim_n = 60
        self.r = r
        self.momentum = 0
        self.prev_coll = {'left': False, 'right': False, 'top': False, 'bottom': False}
        self.rect.x, self.rect.y = loc[0] + r[0], loc[1] + r[1]
        self.visibility = visibility

    def update(self, player_rect=None, r=None, tiles=None, attack_rect=None):
        self.anim_n += 6
        if self.cd > 0:
            self.cd -= 1
        if r:
            r1 = self.r
            self.r = r
            r = [r[0] - r1[0], r[1] - r1[1]]
            self.rect.x = self.rect.x + r[0]
            self.rect.y = self.rect.y + r[1]
        if player_rect:
            player_pos = [player_rect.x, player_rect.y]
            movement = [0, 0]
            if 500 > abs(self.rect.x - player_pos[0]) > 6 and self.status and self.status != 'death':
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
            elif abs(self.rect.x - player_pos[0]) > 500 and self.status != 'idle' and self.status:
                self.status = 'idle'
                self.anim_n = 60
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
            if self.status != 'death':
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
            elif self.status == 'death':
                if self.anim_n >= 760:
                    self.status = None
                    self.image = pygame.Surface((1, 1))
                    self.kill()
                    return
                image = pygame.image.load(f'{self.path}/Idle/Idle_1.png')
                size = (250 // (250 // max(image.get_height(), image.get_width())),
                        200 // (200 // max(image.get_height(), image.get_width())))
                self.image = pygame.transform.scale(pygame.image.load(
                    f'data/animations/Explosion/Exp_{(self.anim_n + 180) // 240}.png'), size)
            if not attack_rect and self.rect.colliderect(player_rect) and not self.cd and self.status and self.status \
                    != 'death':
                self.cd = 60
                raise PlayerDamaged

        if attack_rect:
            if self.rect.colliderect(attack_rect):
                self.hp -= 1
                if self.hp == 0:
                    self.status = 'death'
                    self.anim_n = 90

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

    def __init__(self, wh=None, *args):
        super(Player, self).__init__(*args)
        self.falling = False
        self.first = True
        self.jump_n = 0
        self.jumping = False
        self.hp = 20
        self.anim_n = 60
        self.align = 'right'
        self.right = None
        self.left = None
        self.rect = self.image.get_rect()
        if wh:
            self.rect.x = wh[0] // 2 - self.rect.x
            self.rect.y = wh[1] // 2 - self.rect.y + 22
            self.wh = wh
        else:
            self.rect.x = WIDTH // 2 - self.rect.x
            self.rect.y = HEIGHT // 2 - self.rect.y + 22
        self.status = 'idle'

    def get_attack_rect(self):
        if self.status == 'attack':
            return self.rect
        return None

    def update(self, r=None, attack_rects=None):
        if self.first:
            self.first = False
            self.rect.x = self.wh[0] // 2 - 32
            self.rect.y = self.wh[1] // 2 + 22
        self.anim_n += 6
        if self.status == 'idle':
            if self.anim_n >= 600:
                self.anim_n = 60
            if self.align == 'right':
                self.image = pygame.image.load(f'data/animations/Idle/Idle_{self.anim_n // 60}.png')
            else:
                self.image = pygame.transform.flip(
                    pygame.image.load(f'data/animations/Idle/Idle_{self.anim_n // 60}.png'), True, False)
        elif self.status == 'dying':
            if self.anim_n >= 800:
                self.status = None
                if self.align == 'right':
                    self.image = pygame.image.load('data/animations/Death/Death_10.png')
                else:
                    self.image = pygame.transform.flip(pygame.image.load('data/animations/Death/Death_10.png'), True,
                                                       False)
                return
            if self.align == 'right':
                self.image = pygame.image.load(f'data/animations/Death/Death_{self.anim_n // 80}.png')
            else:
                self.image = pygame.transform.flip(
                    pygame.image.load(f'data/animations/Death/Death_{self.anim_n // 80}.png'), True, False)
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
            if self.anim_n >= 240:
                self.status = self.align
                self.anim_n = 60
                self.rect.y += 6
                if self.align == 'left':
                    self.image = pygame.image.load('data/animations/Idle/Idle_1.png')
                    self.rect.topright = self.right
                    self.rect.x = self.right[0] - 42
                return
            if self.align == 'right':
                self.image = pygame.image.load(f'data/animations/Attack/Attack_{self.anim_n // 60}.png')
                self.rect = self.image.get_rect()
                self.rect.topleft = self.left
            else:
                self.image = pygame.transform.flip(
                    pygame.image.load(f'data/animations/Attack/Attack_{self.anim_n // 60}.png'), True, False)
                self.rect = self.image.get_rect()
                self.rect.topright = self.right
        if self.status != 'dash' and self.status != 'attacking':
            n = self.jump_n // 5
            if not n:
                n += 1
            if self.jump_n and self.align == 'right':
                self.image = pygame.image.load(f'data/animations/Jump/Jump_{n}.png')
            elif self.jump_n and self.align == 'left':
                self.image = pygame.transform.flip(pygame.image.load(f'data/animations/Jump/Jump_{n}.png'), True, False)
        if attack_rects:
            for rect in attack_rects:
                if self.rect.colliderect(rect):
                    self.hp -= 1
        tl = self.rect.topleft
        self.rect = self.image.get_rect()
        self.rect.topleft = tl

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
        if self.status == 'attack' and self.align == 'left':
            rect.x += 100
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
        # if self.status == 'attacking' and self.align == 'left':
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
    def __init__(self, n, cords, size, *args, **kwargs):
        super(Bar, self).__init__(*args)
        self.n = n
        self.size = size
        im = Image.open('data/HealthBar.png')
        hp = Image.open('data/hp.png').resize((int(2.85 * self.n), 4))
        im.paste(hp, (19, 8, 19 + int(2.85 * self.n), 12))
        self.image = pygame.transform.scale(pygame.image.frombuffer(im.tobytes(), im.size, 'RGBA'),
                                            (int(size // 10 * 3.8), size // 10))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = cords

    def update(self, size, n, cords=None):
        if size != self.size:
            self.image = pygame.transform.scale(self.image,
                                                (int(size // 10 * 3.8), size // 10))

        if n != self.n:
            im = Image.open('data/HealthBar.png')
            if self.n > 0:
                hp = Image.open('data/hp.png').resize((int(2.85 * self.n), 4))
                im.paste(hp, (19, 8, 19 + int(2.85 * self.n), 12))
            self.image = pygame.transform.scale(pygame.image.frombuffer(im.tobytes(), im.size, 'RGBA'),
                                                (int(size // 10 * 3.8), size // 10))
            self.n = n
        if cords:
            self.rect.x, self.rect.y = cords


def level_create(arr):
    tiles = []
    enemies = {}
    im = Image.new('RGB', (len(arr[0][0]) * 32, len(arr[0]) * 32), (66, 40, 53))
    wall = Image.open('data/wall.png')
    wall_2 = Image.open('data/wall_2.png')
    for i in range(len(arr[0])):
        for j in range(len(arr[0][i])):
            try:
                symbol = arr[0][i][j]
                if symbol == '#':
                    tiles.append([j * 32, i * 32, 32, 32])
                    im.paste(wall_2, (j * 32, i * 32, (j + 1) * 32, (i + 1) * 32))
                elif symbol == '@':
                    im.paste(wall, (j * 32, i * 32, (j + 1) * 32, (i + 1) * 32))
                    player_cord = (j, i)
                elif symbol == '.':
                    im.paste(wall, (j * 32, i * 32, (j + 1) * 32, (i + 1) * 32))
                elif symbol == '_':
                    draw = ImageDraw.ImageDraw(im)
                    draw.rectangle((j * 32, i * 32, (j + 1) * 32, (i + 1) * 32), (66, 40, 53))
                else:
                    im.paste(wall, (j * 32, i * 32, (j + 1) * 32, (i + 1) * 32))
                    if symbol not in enemies.keys():
                        enemies[symbol] = [(j, i)]
                    else:
                        enemies[symbol].append((j, i))
            except IndexError:
                pass

    level = Level(im.tobytes(), im.size)
    return level, player_cord, tiles, enemies


def create_level(l=2):
    names = sample(range(1, 8), k=l)
    if 7 in names:
        print(7)
    arr = []
    files = []
    with open('data/levels/in.txt', 'rt') as f:
        files.append(f.read().split('\n'))
        f.close()
    for i in names:
        with open(f'data/levels/{i}.txt', 'rt') as f:
            files.append(f.read().split('\n'))
            f.close()
    with open('data/levels/bosses/golem.txt', 'rt') as f:
        files.append(f.read().split('\n'))
    with open('data/levels/out.txt', 'rt') as f:
        files.append(f.read().split('\n'))
        f.close()
    for i in range(len(files)):
        for _ in range(max(map(lambda x: len(x), files)) - len(files[i])):
            files[i].insert(0, '_' * len(files[i][0]))
    arr.append(files[0])
    for i in range(1, len(files)):
        for j in range(len(arr[0])):
            arr[0][j] += files[i][j]

    return level_create(arr)


class PlayerDamaged(Exception):
    pass


class NextLevel(Exception):
    pass


class Golem(pygame.sprite.Sprite):
    def __init__(self, cords, r, *args):
        super(Golem, self).__init__(*args)
        self.image = pygame.image.load('data/animations/Golem/Idle/Idle_1.png')
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = cords
        self.laser = None
        self.dusts = []
        self.hp = 20
        self.align = 'left'
        self.r = r
        self.status = 'idle'
        self.anim_n = 60

    def update(self, player_rect, r, attack_rect=None):
        self.anim_n += 6
        r1 = self.r
        self.r = r
        r = [r[0] - r1[0], r[1] - r1[1]]
        self.rect.x = self.rect.x + r[0]
        self.rect.y = self.rect.y + r[1]
        abs_y = self.rect.y - self.r[1]
        if self.rect.x - player_rect.x <= 500 and self.status != 'attacking' and self.status\
                != 'death' and self.status:
            if abs(self.rect.y - player_rect.y) >= 4:
                if self.rect.y > player_rect.y:
                    self.rect.y -= 4
                else:
                    if abs_y < 471:
                        self.rect.y += 4

            elif self.status != 'attack' and self.status != 'attacking':
                self.status = 'attack'
                self.anim_n = 30
            if player_rect.x < self.rect.centerx:
                self.align = 'left'
            else:
                self.align = 'right'
            if self.align == 'left':
                if abs(self.rect.x - player_rect.x) <= 100 and abs(self.rect.y - player_rect.y) <= 70 \
                        and self.status != 'melee' and abs_y == 471:
                    self.status = 'melee'
                    self.anim_n = 60
            else:
                if abs((self.rect.x + self.image.get_width() // 2) - player_rect.x) <= 100 and abs(self.rect.y - player_rect.y) <= 70 \
                        and self.status != 'melee' and abs_y == 471:
                    self.status = 'melee'
                    self.anim_n = 60
        if self.status == 'idle':
            if self.anim_n >= 240:
                self.anim_n = 60
            if self.align == 'left':
                self.image = pygame.transform. \
                    flip(pygame.image.load(f'data/animations/Golem/Idle/Idle_{self.anim_n // 60}.png'), True, False)
            else:
                self.image = pygame.image.load(f'data/animations/Golem/Idle/Idle_{self.anim_n // 60}.png')
        elif self.status == 'attack':
            if self.anim_n >= 210:
                self.status = 'attacking'
            if self.align == 'left':
                self.image = pygame.transform.flip(pygame.image.load(f'data/animations/Golem/Attack/Attack'
                                                                     f'_{self.anim_n // 30}.png'), True, False)
            else:
                self.image = pygame.image.load(f'data/animations/Golem/Attack/Attack_{self.anim_n // 30}.png')
        elif self.status == 'attacking':
            if self.laser:
                if self.laser.completed:
                    self.laser = None
                    self.status = 'idle'
                else:
                    self.laser.update(self.r)
            else:
                self.laser = Laser((self.rect.x, self.rect.y), self.align, self.r)
        elif self.status == 'melee':
            if self.anim_n >= 240:
                self.status = 'idle'
                if self.align == 'left':
                    self.rect.x += 36
                self.anim_n = 60
            if self.align == 'left':
                if self.anim_n == 210:
                    self.rect.x -= 36
                    self.dusts.append(Dust((self.rect.x + 15, self.rect.bottom), self.r))
                self.image = pygame.transform.flip(
                    pygame.image.load(f'data/animations/Golem/Melee/Melee_{self.anim_n // 30}.png'), True, False)
            else:
                if self.anim_n == 210:
                    self.dusts.append(Dust((self.rect.x + 153, self.rect.bottom), self.r))
                self.image = pygame.image.load(f'data/animations/Golem/Melee/Melee_{self.anim_n // 30}.png')
        elif self.status == 'death':
            if self.anim_n >= 780:
                self.status = None
                return
            if self.anim_n < 600:
                if abs_y > 411:
                    if abs_y - 411 < 6:
                        self.rect.y -= abs_y - 411
                    else:
                        self.rect.y -= 6
                    self.anim_n = 60
                    return
                elif abs_y < 411:
                    if 411 - abs_y < 6:
                        self.rect.y += 411 - abs_y
                    else:
                        self.rect.y += 6
                    return
                self.bl = self.rect.bottomleft
            if self.align == 'right':
                self.image = pygame.image.load(f'data/animations/Golem/Death/Death_{self.anim_n // 60}.png')
            else:
                self.image = pygame.transform.flip(pygame.image.load(
                    f'data/animations/Golem/Death/Death_{self.anim_n // 60}.png'), True, False)
            x, y = self.rect.x, self.rect.y
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = x, y
            if self.anim_n >= 600:
                self.rect = self.image.get_rect()
                self.rect.bottomleft = self.bl[0] + r[0], 454 - self.r[1]
                self.bl = self.rect.bottomleft
        if attack_rect:
            if self.rect.colliderect(attack_rect):
                self.hp -= 1
                if self.hp == 0:
                    self.status = 'death'
                    self.anim_n = 60


class Laser(pygame.sprite.Sprite):
    def __init__(self, cords, align, r, *args):
        super(Laser, self).__init__(*args)
        self.align = align
        self.image = pygame.image.load('data/animations/Golem/Laser/Laser_1.png')
        self.rect = self.image.get_rect()
        self.completed = False
        self.damaged = False
        self.r = r
        self.rect.x, self.rect.y = cords
        self.rect.y += 5
        self.anim_n = 15
        if align == 'right':
            self.rect.x += 58
        else:
            self.rect.x -= 1835
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, r, *args, **kwargs):
        r1 = self.r
        self.r = r
        r = [r[0] - r1[0], r[1] - r1[1]]
        self.rect.x = self.rect.x + r[0]
        self.rect.y = self.rect.y + r[1]
        self.anim_n += 6
        if self.anim_n >= 210:
            self.completed = True
            return
        if self.align == 'left':
            self.image = pygame.transform.flip\
                (pygame.image.load(f'data/animations/Golem/Laser/Laser_{self.anim_n // 15}.png'), True, False)
        else:
            self.image = pygame.image.load(f'data/animations/Golem/Laser/Laser_{self.anim_n // 15}.png')


class Dust(pygame.sprite.Sprite):
    def __init__(self, middle_bottom, r):
        super(Dust, self).__init__()
        self.completed = False
        self.damaged = False
        self.anim_n = 30
        self.r = r
        self.image = pygame.image.load(f'data/animations/Dust/Dust_1.png')
        self.rect = self.image.get_rect()
        self.midbottom = middle_bottom
        self.rect.midbottom = middle_bottom

    def update(self, player_rect=None, r=None, *args, **kwargs):
        self.anim_n += 6
        if self.anim_n >= 260:
            self.completed = True
            self.kill()
            return
        self.image = pygame.image.load(f'data/animations/Dust/Dust_{self.anim_n // 30}.png')
        if player_rect:
            if player_rect.colliderect(self.rect) and not self.damaged:
                self.damaged = True
                raise PlayerDamaged
        if r:
            r1 = self.r
            self.r = r
            r = [r[0] - r1[0], r[1] - r1[1]]
            self.rect.x = self.rect.x + r[0]
            self.rect.y = self.rect.y + r[1]


class Portal(pygame.sprite.Sprite):
    def __init__(self, bl, r, *args):
        super(Portal, self).__init__(*args)
        self.image = pygame.image.load('data/portal.png')
        self.rect = self.image.get_rect()
        self.bl = bl
        self.rect.bottomleft = bl
        self.rect.x += r[0]
        self.rect.y += r[1]
        self.r = r

    def update(self, r=None, player_rect=None, *args, **kwargs):
        if r:
            r1 = self.r
            self.r = r
            r = [r[0] - r1[0], r[1] - r1[1]]
            self.rect.x = self.rect.x + r[0]
            self.rect.y = self.rect.y + r[1]
        if player_rect:
            if player_rect.collidepoint(self.rect.center):
                raise NextLevel


class Door(pygame.sprite.Sprite):
    def __init__(self, tl, r, *args):
        super(Door, self).__init__(*args)
        self.image = pygame.image.load('data/door.png')
        self.rect = self.image.get_rect()
        self.r = r
        self.anim_n = 0
        self.rect.topleft = tl
        self.rect.x += r[0]
        self.rect.y += r[1]
        self.status = 'closed'

    def update(self, player_rect=None, r=None):
        if r:
            r1 = self.r
            self.r = r
            r = [r[0] - r1[0], r[1] - r1[1]]
            self.rect.x = self.rect.x + r[0]
            self.rect.y = self.rect.y + r[1]
        if player_rect:
            if player_rect.colliderect(self.rect) and self.status:
                return 'move'
        if self.status == 'opening':
            if self.anim_n < 128:
                self.anim_n += 4
                self.rect.y -= 4
            else:
                self.status = None
        return None
