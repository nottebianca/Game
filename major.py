import pygame

from pygame import mixer
from os import path

import pickle

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
mixer.init()
clock = pygame.time.Clock()
fps = 60
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')
tile_size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 7
score = 0
pause = False

font = pygame.font.SysFont(None, 70)
font_score = pygame.font.SysFont(None, 36)
red = (255, 0, 0)
white = (255, 255, 255)
bg_img = pygame.image.load('img/bg.png')
start_menu_img = pygame.image.load('img/start_menu.png')
exit_menu_img = pygame.image.load('img/exit_menu.png')
continue_img = pygame.image.load('img/continue.png')
exit_img = pygame.image.load('img/exit.png')

present_sound = pygame.mixer.Sound('sound/present.mp3')
present_sound.set_volume(0.5)
jump_sound = pygame.mixer.Sound('sound/jump.mp3')
jump_sound.set_volume(0.5)
menu_sound = pygame.mixer.Sound('sound/HappyNewYear.mp3')
menu_sound.set_volume(0.1)
game_over_sound = pygame.mixer.Sound('sound/game_over.wav')
game_over_sound.set_volume(0.3)
level_sound = pygame.mixer.Sound('sound/level_up.mp3')
level_sound.set_volume(0.1)

menu_music_playing = False
game_over_music_played = False


def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


def reset_level(level):
    player.reset(100, screen_height - 130)
    blob_group.empty()
    ice_group.empty()
    exit_group.empty()
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)
    return world


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        position = pygame.mouse.get_pos()
        if self.rect.collidepoint(position):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        screen.blit(self.image, self.rect)
        return action


class Player():
    def __init__(self, x, y):
        self.lives = 3
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        if pygame.sprite.spritecollide(self, blob_group, False) or pygame.sprite.spritecollide(self, ice_group, False):
            self.lives -= 1
            if self.lives <= 0:
                game_over = -1
            else:
                self.rect.x = 100
                self.rect.y = screen_height - 130
            return game_over
        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_sound.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y
            self.in_air = True
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
            if pygame.sprite.spritecollide(self, ice_group, False):
                game_over = -1
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1
            self.rect.x += dx
            self.rect.y += dy
        elif game_over == -1:
            self.image = self.dead_image
            draw_text('You lose', font, red, (screen_width // 2) - 100, (screen_height // 2) - 200)
        screen.blit(self.image, self.rect)
        return game_over

    def draw_lives(self, screen):
        font = pygame.font.SysFont(None, 36)
        text = font.render('Lives:', True, (255, 255, 255))
        screen.blit(text, (10, 10))
        if self.lives is not None:
            for i in range(self.lives):
                screen.blit(self.heart_animations[self.heart_frame], (80 + i * 35, 10))
        if self.frame_counter % 5 == 0:
            self.heart_frame += 1
            if self.heart_frame >= len(self.heart_animations):
                self.heart_frame = 0
        self.frame_counter += 1

    def full_reset(self, x, y):
        self.lives = 3
        self.reset(x, y)

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        self.frame_counter = 0
        self.heart_animations = []
        for i in range(1, 8):
            heart_img = pygame.image.load(f'img/Cuore{i}.png')
            heart_img = pygame.transform.scale(heart_img, (30, 30))
            self.heart_animations.append(heart_img)
        self.heart_frame = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/Walk{num}.png')
            img_right = pygame.transform.scale(img_right, (45, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/Dead12.png')
        self.dead_image = pygame.transform.scale(self.dead_image, (50, 60))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World():
    def __init__(self, data):
        self.data = data
        self.land_img = pygame.image.load('img/land.png')
        self.snowland_img = pygame.image.load('img/snowland.png')
        self.lf_snowland_img = pygame.image.load('img/leftsnow.png')
        self.rg_snowland_img = pygame.image.load('img/rightsnow.png')
        self.lf_obrez_img = pygame.image.load('img/left_obrez.png')
        self.rg_obrez_img = pygame.image.load('img/right_obrez.png')
        self.create_world()

    def create_world(self):
        self.tile_list = []
        row_count = 0
        for row in self.data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(self.land_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 2:
                    img = pygame.transform.scale(self.snowland_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                elif tile == 6:
                    ice = Ice(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    ice_group.add(ice)
                elif tile == 7:
                    present = Present(col_count * tile_size + (tile_size // 2),
                                      row_count * tile_size + (tile_size // 2))
                    present_group.add(present)
                elif tile == 12:
                    img = pygame.transform.scale(self.lf_snowland_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 9:
                    img = pygame.transform.scale(self.rg_snowland_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 10:
                    img = pygame.transform.scale(self.lf_obrez_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 11:
                    img = pygame.transform.scale(self.rg_obrez_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 8:
                    exit = Win(col_count * tile_size, row_count * tile_size)
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/slime_mob.png')
        self.image = pygame.transform.scale(img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Win(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/portal.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Ice(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/ice.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Present(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/present.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


y_offset = 50
button_size = (200, 200)
restart_img = pygame.image.load('img/restart.png')
restart_img = pygame.transform.scale(restart_img, button_size)
button_x = screen_width // 2 - button_size[0] // 2
button_y = screen_height // 2 - button_size[1] // 2 - y_offset
restart_button = Button(button_x, button_y, restart_img)

start_menu_img_scaled = pygame.transform.scale(start_menu_img,
                                               (start_menu_img.get_width() // 2, start_menu_img.get_height() // 2))
exit_menu_img_scaled = pygame.transform.scale(exit_menu_img,
                                              (exit_menu_img.get_width() // 2, exit_menu_img.get_height() // 2))

start_menu_button_y = screen_height // 2 - 200
exit_menu_button_y = screen_height // 2 + 50

start_menu_button = Button(screen_width // 2 - start_menu_img_scaled.get_width() // 2, start_menu_button_y,
                           start_menu_img_scaled)
exit_menu_button = Button(screen_width // 2 - exit_menu_img_scaled.get_width() // 2, exit_menu_button_y,
                          exit_menu_img_scaled)



player = Player(100, screen_height - 130)
blob_group = pygame.sprite.Group()
ice_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
present_group = pygame.sprite.Group()
score_present = Present((tile_size // 2) + 110, (tile_size // 2) + 35)
present_group.add(score_present)
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
world_data = pickle.load(pickle_in)
world = World(world_data)

run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))
    if main_menu == True:
        if not menu_music_playing:
            menu_sound.play(-1)
            menu_music_playing = True
        if exit_menu_button.draw() == True:
            run = False
        if start_menu_button.draw() == True:
            main_menu = False
            menu_sound.stop()
            menu_music_playing = False
    else:
        world.draw()

        if game_over == 0:
            present_group.draw(screen)
            blob_group.update()
            if pygame.sprite.spritecollide(player, present_group, True):
                score += 1
                present_sound.play()
            draw_text('Score: ' + str(score), font_score, white, tile_size - 40, 50)
        blob_group.draw(screen)
        ice_group.draw(screen)
        exit_group.draw(screen)
        game_over = player.update(game_over)
        if game_over == -1:
            if not game_over_music_played:
                game_over_sound.play()
                game_over_music_played = True
            draw_text('GAME OVER', font, red, (screen_width // 2) - 150, (screen_height // 2) - 200)
            if restart_button.draw():
                game_over_music_played = False
                player.full_reset(100, screen_height - 130)
                world_data = []
                world = reset_level(level)
                game_over = 0
                blob_group = pygame.sprite.Group()
                ice_group = pygame.sprite.Group()
                world.create_world()
                game_over = 0
                score = 0
        player.draw_lives(screen)
        if game_over == 1:
            level_sound.play()
            level += 1
            if level <= max_levels:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('YOU WIN!!!', font, red, (screen_width // 2) - 140, (screen_height // 2) - 200)
                if restart_button.draw():
                    level = 1
                    player.full_reset(100, screen_height - 130)
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()