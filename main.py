from engine import *
import pygame
import time
import sys

pygame.init()
display_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
fullscreen = False
pygame.display.set_icon(pygame.image.load('data/icon.png'))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill((66, 40, 53))
clock = pygame.time.Clock()
sys.setrecursionlimit(9999)


def main(hp, n=1, total_time=0, *args):
    global clock, screen
    with open('data/saves/save.txt', 'wt') as f:
        f.write(f'{int(total_time)} 0 {hp} {n}')
    pause = False
    WIDTH, HEIGHT = screen.get_size()
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
    bar = Bar(hp, (20, HEIGHT // 1.5), HEIGHT)
    bar.update(HEIGHT, hp + 1, cords=(20, HEIGHT // 1.5))
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
        elif key == 'd':
            x, y = arr[0]
            x -= 1
            door = Door((x * 32, y * 32), r)
            continue
        elif key == 'P':
            x, y = arr[0]
            y += 1
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
    die_n = 0
    font = pygame.font.Font('data/font.ttf', 50)
    font2 = pygame.font.Font('data/font.ttf', 70)
    text = font.render(f'Floor {n}', True, (212, 100, 59))

    start_time = time.time()
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
                            elif event.key == pygame.K_ESCAPE:
                                pause = not pause
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
                                screen = pygame.display.set_mode((750, 750), 32, 32)
                                screen = pygame.display.set_mode((750, 750), pygame.RESIZABLE)
                                fullscreen = False
                                player.right = player.rect.topright
                                player.left = player.rect.topleft
                    else:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                pause = True
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
            if not pause:
                all_sprites.update(r=camera.r)
                bosses.update(player.rect, camera.r)
                bar.update(HEIGHT, player.hp, cords=(20, HEIGHT // 1.5))
                res = door.update(player.rect, r)
                if res:
                    x, y = camera.r
                    if player.status != 'dash':
                        camera.r = [x + 6, y]
                    else:
                        camera.r = [x + 25, y]
                player.update()
                enemies.update(player_rect=player.rect, r=camera.r, tiles=tiles, attack_rect=player.get_attack_rect())
            screen.fill((66, 40, 53))
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
            if door.status == 'closed' and bosses.sprites()[0].status == 'death':
                door.status = 'opening'
            screen.blit(door.image, door.rect)
            screen.blit(text, pygame.Rect(WIDTH - text.get_size()[0] - 50, 50, *text.get_size()))
            screen.blit(bar.image, bar.rect)
            if pause:
                mx, my = pygame.mouse.get_pos()
                pause_text = font2.render('Pause', True, (212, 100, 59))
                con_text = font.render('Continue', True, (188, 92, 57))
                con_rect = pygame.Rect((WIDTH - con_text.get_width()) // 2, 100 + pause_text.get_height(),
                                                  *con_text.get_size())
                if con_rect.collidepoint(mx, my) and pygame.mouse.get_pressed(3)[0]:
                    pause = False
                load_text = font.render('Load', True, (188, 92, 57))
                load_rect = pygame.Rect((WIDTH - load_text.get_width()) // 2, 150 + pause_text.get_height()
                                                   + con_text.get_height(), *load_text.get_size())
                if load_rect.collidepoint(mx, my) and pygame.mouse.get_pressed(3)[0]:
                    load()
                menu_text = font.render('Main Menu', True, (188, 92, 57))
                menu_rect = pygame.Rect((WIDTH - menu_text.get_width()) // 2, 200 + pause_text.get_height() +
                                        con_text.get_height() + load_text.get_height(), *menu_text.get_size())
                if menu_rect.collidepoint(mx, my) and pygame.mouse.get_pressed(3)[0]:
                    menu()
                pygame.draw.rect(screen, pygame.Color(0, 0, 0, 30), (0, 0, WIDTH, HEIGHT))
                screen.blit(pause_text, pygame.Rect((WIDTH - pause_text.get_width()) // 2, 50, *pause_text.get_size()))
                screen.blit(con_text, con_rect)
                screen.blit(load_text, load_rect)
                screen.blit(menu_text, menu_rect)
        except PlayerDamaged:
            player.hp -= 1
        except NextLevel:
            end_time = time.time() - start_time
            cleared(player.hp, n, end_time, end_time + total_time)
        pygame.display.flip()
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
                with open('data/saves/save.txt', 'rt') as f:
                    tt, t, hp, n = map(int, f.read().split())
                    main(hp, n, tt, WIDTH, HEIGHT)
        elif pygame.Rect(50, 50 + HEIGHT // 3.5 * 2, *ng_size).collidepoint(mx, my):
            if click:
                main(20, 1, 0, WIDTH, HEIGHT)
            color_2 = (144, 77, 48)
        screen.fill((199, 120, 90))

        screen.blit(font.render('Dungeon Platformer', True, (64, 35, 32)), (50, 50))
        screen.blit(font2.render('Load Game', True, color_1), (50, 50 + HEIGHT // 3.5))
        screen.blit(font2.render('New Game', True, color_2), (50, 50 + HEIGHT // 3.5 * 2))
        pygame.display.flip()


def cleared(hp, n, time, total_time):
    global clock, screen
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font('data/font.ttf', 70)
    font2 = pygame.font.Font('data/font.ttf', 50)
    fc_text = font.render(f'Floor {n} cleared!', True, (64, 35, 32))
    tt_text = font2.render(f'Total time - {int(total_time // 60)}:{int(total_time % 60)}', True, (179, 98, 61))
    t_text = font2.render(f'Time - {int(time // 60)}:{int(time % 60)}', True, (179, 98, 61))
    next_text = font.render(f'Press Enter', True, (64, 35, 32))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main(hp, n + 1, total_time + time)
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                screen = pygame.display.set_mode((WIDTH, HEIGHT))
        screen.fill((199, 120, 90))
        screen.blit(fc_text, pygame.Rect((WIDTH - fc_text.get_width()) // 2, 50, *fc_text.get_size()))
        screen.blit(tt_text, pygame.Rect((WIDTH - tt_text.get_width()) // 2, 100 + fc_text.get_height(),
                    *tt_text.get_size()))
        screen.blit(t_text, pygame.Rect((WIDTH - t_text.get_width()) // 2, 150 + fc_text.get_height()
                                        + tt_text.get_height(), *t_text.get_size()))
        screen.blit(next_text, pygame.Rect((WIDTH - next_text.get_width()) // 2, 220 + fc_text.get_height()
                                           + tt_text.get_height() + t_text.get_height(), *next_text.get_size()))
        pygame.display.flip()


def load():
    with open('data/saves/save.txt', 'rt') as f:
        tt, t, hp, n, *args = map(int, f.read().split())
        main(hp, n, tt)


menu()
pygame.quit()
