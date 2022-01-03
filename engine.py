from PIL import Image
import pygame


class Player(pygame.sprite.Sprite):
    image = pygame.image.load('data/animations/Idle/Idle_1.png')

    def __init__(self, x, y, *args):
        super(Player, self).__init__(*args)
        self.first = True
        self.anim_n = 60
        self.align = 'right'
        self.rect = self.image.get_rect()
        self.rect.x = x * 32
        self.rect.y = y * 32 + 14
        self.status = 'idle'

    def update(self, r=None):
        if self.first:
            self.first = False
            x, y = r
            self.rect.x = x + 32
            self.rect.y = y + 52
        self.anim_n += 5
        if self.status == 'idle':
            if self.anim_n >= 600:
                self.anim_n = 60
            if self.align == 'right':
                self.image = pygame.image.load(f'data/animations/Idle/Idle_{self.anim_n // 60}.png')
            else:
                self.image = pygame.transform.flip(pygame.image.load(f'data/animations/Idle/Idle_{self.anim_n // 60}.png'), True, False)
        elif self.status == 'right':
            if self.anim_n == 600:
                self.anim_n = 60
            self.image = pygame.image.load(f'data/animations/Walk/Run_{self.anim_n // 60}.png')
        elif self.status == 'left':
            if self.anim_n == 600:
                self.anim_n = 60
            self.image = pygame.transform.flip(pygame.image.load(f'data/animations/Walk/Run_{self.anim_n // 60}.png'), True, False)


    def align_change(self, side):
        if self.align != side:
            self.image = pygame.transform.flip(self.image, True, False)
            self.align = side
        self.status = 'idle'
        self.anim_n = 60


class Camera:
    def __init__(self, player_cord):
        self.r = list(map(lambda i: 750 // 2 - i * 2, player_cord))

    def movement(self, side=None):
        if not side:
            return self.r
        elif side == 'left':
            x, y = self.r
            self.r = [x + 5, y]
            return self.r
        elif side == 'right':
            x, y = self.r
            self.r = [x - 5, y]
            return self.r
        elif side == 'up':
            x, y = self.r
            self.r = [x, y - 5]
            return self.r
        elif side == 'down':
            x, y = self.r
            self.r = [x, y + 5]
            return self.r


class Level(pygame.sprite.Sprite):
    def __init__(self, image, size, *args):
        super(Level, self).__init__(*args)
        self.image = pygame.image.frombuffer(image, size, 'RGB')
        self.rect = self.image.get_rect()

    def update(self, r):
        x, y = r
        self.rect.x = x
        self.rect.y = y


def load_level(filename):
    file = open(f'data/levels/{filename}', 'rt').read().split('\n')
    im = Image.new('RGB', (len(file[0]) * 32, len(file) * 32), (66, 40, 53))
    wall = Image.open('data/wall.png')
    wall_2 = Image.open('data/wall_2.png')
    for i in range(len(file)):
        for j in range(len(file[0])):
            symbol = file[i][j]
            if symbol == '#':
                im.paste(wall_2, (j * 32, i * 32, (j + 1) * 32, (i + 1) * 32))
            elif symbol == '@':
                im.paste(wall, (j * 32, i * 32, (j + 1) * 32, (i + 1) * 32))
                player_cord = (j, i)
            else:
                im.paste(wall, (j * 32, i * 32, (j + 1) * 32, (i + 1) * 32))
    level = Level(im.tobytes(), im.size)
    im.save('eagaegr.png')
    return level, player_cord