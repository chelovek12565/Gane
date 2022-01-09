from engine import *
import pygame

pygame.init()
display_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
fullscreen = False
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
all_sprites = pygame.sprite.Group()
screen.fill((66, 40, 53))
level, player_cord, tiles, enemies_c = load_level('test_level.txt')
all_sprites.add(level)
walking = {
    'left': False,
    'right': False
}
player = Player(all_sprites)
all_sprites.add(player)
camera = Camera([player.rect.x, player.rect.y], player_cord)
r = camera.r
enemies = pygame.sprite.Group()
for x, y in enemies_c:
    Enemy((x * 32, y * 32), r, 'data/animations/Skeleton', 100, enemies, all_sprites)
all_sprites.update(r=r)
enemies.update(r=r)
level.update(r)
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)
    movement = [0, 0]
    if player.status == 'dash':
        if player.align == 'right':
            movement[0] += 25
        else:
            movement[0] -= 25
    else:
        if walking[player.align]:
            if player.align == 'right':
                movement[0] += 6
            else:
                movement[0] -= 6
        elif player.align == 'left' and walking['right']:
            movement[0] += 6
        elif player.align == 'right' and walking['left']:
            movement[0] -= 6
        if not walking['left'] and not walking['right'] and player.status != 'idle':
            player.status = 'idle'
            player.anim_n = 60
        r = camera.r
        if player.jumping:
            player.jump()
            movement[1] -= 12
        else:
            movement[1] += 12
    rect, collisions, b = player.move(movement, tiles, camera.r)
    camera.r = camera.r[0] - (rect.x - player.rect.x), camera.r[1] - (rect.y - player.rect.y)
    all_sprites.update(r=camera.r)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                all_sprites.update(r=r)
                player.align_change('right')
                walking['right'] = True
                player.status = 'right'
            elif event.key == pygame.K_a:
                walking['left'] = True
                player.align_change('left')
                player.status = 'left'
            elif event.key == pygame.K_w and not player.jumping and collisions['bottom']:
                player.jumping = 'up'
            elif event.key == pygame.K_LSHIFT:
                player.set_dash()
            elif event.key == pygame.K_F11:
                if not fullscreen:
                    screen = pygame.display.set_mode(display_size, pygame.FULLSCREEN)

                    WIDTH, HEIGHT = display_size
                    player.rect.x, player.rect.y = WIDTH // 2 - player.image.get_width() // 2, HEIGHT // 2 - \
                                                   player.image.get_height() // 2
                    camera.re_init((player.rect.x, player.rect.y))
                    all_sprites.update(r=camera.r)

                    fullscreen = True
                else:
                    WIDTH, HEIGHT = 750, 750
                    player.rect.x, player.rect.y = WIDTH // 2 - player.image.get_width() // 2, HEIGHT // 2 - \
                                                   player.image.get_height() // 2
                    camera.re_init((player.rect.x, player.rect.y))
                    all_sprites.update(r=camera.r)
                    screen = pygame.display.set_mode((750, 750), pygame.RESIZABLE)
                    fullscreen = False

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                walking['right'] = False
            elif event.key == pygame.K_a:
                walking['left'] = False
        elif event.type == pygame.VIDEORESIZE:
            if not fullscreen:
                WIDTH, HEIGHT = event.w, event.h
                player.rect.x, player.rect.y = WIDTH // 2 - player.image.get_width() // 2, HEIGHT // 2 - \
                                               player.image.get_height() // 2
                camera.re_init((player.rect.x, player.rect.y))
                all_sprites.update(r=camera.r)
                enemies.update((player.rect.x, player.rect.y), camera.r)
    screen.fill((66, 40, 53))
    enemies.update((player.rect.x, player.rect.y), camera.r)

    all_sprites.draw(screen)

    pygame.display.flip()
    player.update()
pygame.quit()
