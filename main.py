from engine import *
import pygame

pygame.init()
screen = pygame.display.set_mode((750, 750))
all_sprites = pygame.sprite.Group()
screen.fill((66, 40, 53))
level, player_cord = load_level('test_level.txt')
all_sprites.add(level)
walking = None
player = Player(*player_cord, all_sprites)
camera = Camera([player.rect.x, player.rect.y])
r = camera.movement()
all_sprites.update(r=r)
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                all_sprites.update(r)
                player.align_change('right')
                walking = 'right'
                player.status = 'right'
            elif event.key == pygame.K_a:
                walking = 'left'
                player.align_change('left')
                player.status = 'left'
            player.anim_n = 60
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_w, pygame.K_a, pygame.K_d, pygame.K_s]:
                walking = None
                player.status = 'idle'
                player.anim_n = 60
    if walking == 'left':
        all_sprites.update(camera.movement('left'))
    elif walking == 'right':
        all_sprites.update(camera.movement('right'))
    screen.fill((66, 40, 53))
    all_sprites.draw(screen)
    pygame.display.flip()
    player.update()
pygame.quit()