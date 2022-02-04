from engine import *
import pygame

pygame.init()
display_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
fullscreen = False
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
all_sprites = pygame.sprite.Group()
screen.fill((66, 40, 53))
level, player_cord, tiles, enemies_c = create_level(3)
all_sprites.add(level)
walking = {
    'left': False,
    'right': False
}
player = Player(all_sprites)
all_sprites.add(player)
bosses = pygame.sprite.Group()
camera = Camera([player.rect.x, player.rect.y], player_cord)
r = camera.r
enemies = pygame.sprite.Group()
bar = Bar(player.hp, (20, HEIGHT // 1.5), HEIGHT)
for key in enemies_c:
    arr = enemies_c[key]
    if key == 'Z':
        path = 'data/animations/Big_zombie'
    elif key == 'D':
        path = 'data/animations/Big_demon'
    elif key == 'G':
        x, y = arr[0]
        Golem((x * 32, y * 32), r, bosses)
        continue
    for x, y in arr:
        e = Enemy((x * 32, y * 32), r, path, 100, 8, 1, enemies, all_sprites)
all_sprites.update(r=r)
enemies.update(r=r)
level.update(r)
clock = pygame.time.Clock()
running = True
while running:
    try:
        clock.tick(60)
        movement = [0, 0]
        if player.status != 'attacking':
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
                if not walking['left'] and not walking['right'] and player.status != 'idle' and player.hp > 0:
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
        if player.status == 'attacking' and not collisions['bottom']:
            rect, *not_need = player.move([0, 12], tiles, camera.r)
            camera.r = camera.r[0], camera.r[1] - (rect.y - player.rect.y)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if player.status:
                    if player.status != 'attacking':
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
                        elif event.key == pygame.K_SPACE and player.status != 'attacking':
                            player.status = 'attacking'
                            if player.align == 'right':
                                rect = pygame.Rect(player.rect.x, player.rect.y,
                                                   90, player.image.get_height())
                            else:
                                rect = pygame.Rect(player.rect.x - 48, player.rect.y, 90,
                                   player.image.get_height())
                            enemies.update(attack_rect=rect)
                            bosses.update(player.rect, camera.r, rect)
                            player.rect.y -= 6
                            player.anim_n = 60
                    if event.key == pygame.K_F11:
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
                else:
                    pass

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
        screen.fill((66, 40, 53))
        enemies.update(player.rect, camera.r, tiles)
        if player.status != 'dying' and player.status and player.hp <= 0:
            player.status = 'dying'
            player.anim_n = 80
        enemies.draw(screen)
        all_sprites.update(r=camera.r)
        bosses.update(player.rect, camera.r)
        bar.update(HEIGHT, player.hp, cords=(20, HEIGHT // 1.5))
        all_sprites.draw(screen)
        bosses.draw(screen)
        if type(bosses.sprites()[0]) == Golem:
            if bosses.sprites()[0].laser:
                screen.blit(bosses.sprites()[0].laser.image, bosses.sprites()[0].laser.rect)
                if bosses.sprites()[0].laser.rect.colliderect(player.rect) and not bosses.sprites()[0].laser.damaged \
                        and bosses.sprites()[0].laser.anim_n >= 145:
                    bosses.sprites()[0].laser.damaged = True
                    player.hp -= 1
        screen.blit(bar.image, bar.rect)
        pygame.display.flip()
        player.update()
    except PlayerDamaged:
        player.hp -= 1
pygame.quit()
