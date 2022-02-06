from engine import *
import pygame
import sys

pygame.init()
display_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
fullscreen = False
pygame.display.set_icon(pygame.image.load('data/icon.png'))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill((66, 40, 53))
# pygame.display.set
clock = pygame.time.Clock()
sys.setrecursionlimit(999)


def main(hp, *args):
    global clock, screen
    WIDTH, HEIGHT = screen.get_size()
    print(screen.get_size())
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    all_sprites = pygame.sprite.Group()
    level, player_cord, tiles, enemies_c = create_level(4)
    all_sprites.add(level)
    walking = {
        'left': False,
        'right': False
    }
    player = Player((WIDTH, HEIGHT), all_sprites)
    all_sprites.add(player)
    bosses = pygame.sprite.Group()
    camera = Camera([player.rect.x, player.rect.y], player_cord)
    r = camera.r
    enemies = pygame.sprite.Group()
    bar = Bar(player.hp, (20, HEIGHT // 1.5), HEIGHT)
    bar.update(HEIGHT, player.hp, cords=(20, HEIGHT // 1.5))
    for key in enemies_c:
        arr = enemies_c[key]
        if key == 'Z':
            path = 'data/animations/Big_zombie'
        elif key == 'D':
            path = 'data/animations/Big_demon'
        elif key == 'c':
            path = 'data/animations/Chort'
        elif key == 'I':
            path = 'data/animations/Imp'
        elif key == 'O':
            path = 'data/animations/Ogre'
        elif key == 'S':
            path = 'data/animations/Skeleton'
        elif key == 'P':
            x, y = arr[0]
            y -= 1
            Portal((x * 32, y * 32), r, enemies)
            continue
        elif key == 'G':
            x, y = arr[0]
            Golem((x * 32, y * 32), r, bosses)
            continue
        for x, y in arr:
            e = Enemy((x * 32, y * 32), r, path, 100, 8, 1, enemies, all_sprites)
    all_sprites.update(r=r)
    enemies.update(r=r)
    level.update(r)
    player.right = player.rect.topright
    player.left = player.rect.topleft
    running = True
    fullscreen = False
    player.hp = hp
    while running:
        clock.tick(60)
        WIDTH, HEIGHT = screen.get_size()
        try:
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
                    sys.exit()
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
                                player.rect = player.image.get_rect()
                                player.rect.x, player.rect.y = WIDTH // 2 - player.image.get_width() // 2, HEIGHT // 2 - \
                                                               player.image.get_height() // 2
                                camera.re_init((player.rect.x, player.rect.y))
                                all_sprites.update(r=camera.r)
                                fullscreen = True
                                player.right = player.rect.topright
                                player.left = player.rect.topleft
                            else:
                                WIDTH, HEIGHT = 750, 750
                                player.rect = player.image.get_rect()
                                player.rect.x, player.rect.y = WIDTH // 2 - player.image.get_width() // 2, HEIGHT // 2 - \
                                                               player.image.get_height() // 2
                                camera.re_init((player.rect.x, player.rect.y))
                                all_sprites.update(r=camera.r)
                                screen = pygame.display.set_mode((750, 750), pygame.RESIZABLE)
                                fullscreen = False
                                player.right = player.rect.topright
                                player.left = player.rect.topleft
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
                        player.rect = player.image.get_rect()
                        player.rect.x, player.rect.y = WIDTH // 2 - player.image.get_width() // 2, HEIGHT // 2 - \
                                                       player.image.get_height() // 2
                        camera.re_init((player.rect.x, player.rect.y))
                        all_sprites.update(r=camera.r)
                        player.right = player.rect.topright
                        player.left = player.rect.topleft
            if player.status != 'dying' and player.status and player.hp <= 0:
                player.status = 'dying'
                player.anim_n = 80
            screen.fill((66, 40, 53))
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
                for i in range(len(bosses.sprites()[0].dusts)):
                    enemies.add(bosses.sprites()[0].dusts.pop())
            enemies.draw(screen)
            enemies.update(player_rect=player.rect, r=camera.r, tiles=tiles, attack_rect=player.get_attack_rect())
            screen.blit(bar.image, bar.rect)
            pygame.display.flip()
            player.update()
        except PlayerDamaged:
            player.hp -= 1
        except NextLevel:
            main(player.hp, WIDTH, HEIGHT)
    return False


def menu(): # TODO menu
    global clock, screen
    global WIDTH, HEIGHT
    running = True
    font = pygame.font.Font('data/font.ttf', 70)
    font2 = pygame.font.Font('data/font.ttf', 50)
    ng_size = font2.render('New Game', True, (0, 0, 0)).get_size()
    lg_size = font2.render('Load Game', True, (0, 0, 0)).get_size()
    while True:
        clock.tick(60)
        color_1 = (179, 98, 61)
        color_2 = (179, 98, 61)
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click = True
        mx, my = pygame.mouse.get_pos()
        if pygame.Rect(50, 50 + HEIGHT // 3.5, *lg_size).collidepoint(mx, my):
            color_1 = (144, 77, 48)
            if click:
                main(20, WIDTH, HEIGHT)
        elif pygame.Rect(50, 50 + HEIGHT // 3.5 * 2, *ng_size).collidepoint(mx, my):
            color_2 = (144, 77, 48)
        screen.fill((199, 120, 90))

        screen.blit(font.render('Dungeon Platformer', True, (64, 35, 32)), (50, 50))
        screen.blit(font2.render('Load Game', True, color_1), (50, 50 + HEIGHT // 3.5))
        screen.blit(font2.render('New Game', True, color_2), (50, 50 + HEIGHT // 3.5 * 2))
        pygame.display.flip()


menu()
pygame.quit()
