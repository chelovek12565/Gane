from engine import *
import pygame

pygame.init()
screen = pygame.display.set_mode((750, 750))
all_sprites = pygame.sprite.Group()
screen.fill((66, 40, 53))
level, player_cord = load_level('test_level.txt')
all_sprites.add(level)
walking = {
    'left': False,
    'right': False
}
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
                walking['right'] = True
                player.status = 'right'
            elif event.key == pygame.K_a:
                walking['left'] = True
                player.align_change('left')
                player.status = 'left'
            elif event.key == pygame.K_w and not player.jumping:
                player.jumping = 'up'
            player.anim_n = 60
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                walking['right'] = False
            elif event.key == pygame.K_a:
                walking['left'] = False

    if player.jumping:
        player.jump()
    if walking[player.align]:
        all_sprites.update(camera.movement(player.align))
    elif player.align == 'left' and walking['right']:
        all_sprites.update(camera.movement('right'))
        player.align = 'right'
        player.status = 'right'
        player.anim_n = 60
    elif player.align == 'right' and walking['left']:
        all_sprites.update(camera.movement('right'))
        player.align = 'left'
        player.status = 'left'
    if not walking['left'] and not walking['right']:
        player.status = 'idle'
        player.anim_n = 60
    screen.fill((66, 40, 53))
    all_sprites.draw(screen)
    pygame.display.flip()
    player.update()
pygame.quit()