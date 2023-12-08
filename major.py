import pygame
import random
from pygame import mixer
from os import path
import pickle
import sqlite3

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
        old_global.screen.blit(self.image, self.rect)
        return action

class Player():
    def __init__(self, x, y):
        self.death_images_loaded = False
        self.lives = 3
        self.reset(x, y)
        self.images_right = []
        self.images_left = []
        for num in range(1, 15):
            img_right = pygame.image.load(f'img/Walk{num}.png')
            img_right = pygame.transform.scale(img_right, (45, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.death_images = []
        for i in range(1, 18):
            img = pygame.image.load(f'img/Dead{i}.png')
            img = pygame.transform.scale(img, (50, 60))
            self.death_images.append(img)
        self.death_index = 0

        self.dead_image = pygame.image.load('img/Dead12.png')
        self.dead_image = pygame.transform.scale(self.dead_image, (50, 60))
        self.image = self.images_right[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True
        self.invulnerable = False
        self.invulnerable_timer = 0

    def reset_position(self):
        self.rect.x = 100
        self.rect.y = old_global.screen_height - 130
        self.vel_y = 0
        self.in_air = False

    def make_invulnerable(self):
        self.invulnerable = True
        self.invulnerable_timer = pygame.time.get_ticks()

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        colusion = 20
        if self.invulnerable:
            if pygame.time.get_ticks() - self.invulnerable_timer > 1000:
                self.invulnerable = False

        if not self.invulnerable:
            if pygame.sprite.spritecollide(self, old_global.blob_group, False) or pygame.sprite.spritecollide(self, old_global.ice_group,
                                                                                                   False):
                self.lives -= 1
                if self.lives == 1:
                    self.reset_position()
                elif self.lives <= 0:
                    game_over = -1
                else:
                    self.reset(100, old_global.screen_height - 130)
                    self.make_invulnerable()

        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                old_global.jump_sound.play()
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
            if pygame.sprite.spritecollide(self, old_global.blob_group, False):
                game_over = -1
            if pygame.sprite.spritecollide(self, old_global.ice_group, False):
                game_over = -1
            if pygame.sprite.spritecollide(self, old_global.exit_group, False):
                game_over = 1

            for platform in old_global.platform_group:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if abs((self.rect.top + dy) - platform.rect.bottom) < colusion:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < colusion:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.death_images[self.death_index]
            self.death_index += 1
            if self.death_index >= len(self.death_images):
                self.death_index = len(self.death_images) - 1

        old_global.screen.blit(self.image, self.rect)
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
        self.heart_animations = []
        self.images_right = []
        self.images_left = []
        self.frame_counter = 0
        self.heart_animations = []
        for i in range(1, 8):
            heart_img = pygame.image.load(f'img/Cuore{i}.png')
            heart_img = pygame.transform.scale(heart_img, (30, 30))
            self.heart_animations.append(heart_img)
        self.heart_frame = 0
        for num in range(1, 15):
            img_right = pygame.image.load(f'img/Walk{num}.png')
            img_right = pygame.transform.scale(img_right, (45, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.dead_image = pygame.image.load('img/Dead12.png')
        self.dead_image = pygame.transform.scale(self.dead_image, (50, 60))
        self.image = self.images_right[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = False
        self.death_index = 0
        self.invulnerable = False
        self.invulnerable_timer = 0

class Old_Global:
    def __init__(self):
        self.conn = sqlite3.connect('scores.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS scores (score INTEGER)''')
        self.conn.commit()

        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        mixer.init()
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.screen_width = 1000
        self.screen_height = 1000
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Platformer')
        self.tile_size = 50
        self.game_over = 0
        self.main_menu = True
        self.level = 1
        self.max_levels = 6
        self.score = 0
        self.pause = False

        self.font = pygame.font.SysFont(None, 70)
        self.font_score = pygame.font.SysFont(None, 36)
        self.red = (255, 0, 0)
        self.white = (255, 255, 255)

        self.menu_music_playing = False
        self.game_over_music_played = False
        self.bg_img = pygame.image.load('img/bg.png')
        self.start_menu_img = pygame.image.load('img/start_menu.png')
        self.exit_menu_img = pygame.image.load('img/exit_menu.png')
        self.score_present = None
        self.present_sound = pygame.mixer.Sound('sound/present.mp3')
        self.present_sound.set_volume(0.5)
        self.jump_sound = pygame.mixer.Sound('sound/jump.mp3')
        self.jump_sound.set_volume(0.5)
        self.menu_sound = pygame.mixer.Sound('sound/HappyNewYear.mp3')
        self.menu_sound.set_volume(0.1)
        self.game_over_sound = pygame.mixer.Sound('sound/game_over.wav')
        self.game_over_sound.set_volume(0.3)
        self.level_sound = pygame.mixer.Sound('sound/level_up.mp3')
        self.level_sound.set_volume(0.1)
        self.y_offset = 50
        self.button_size = (200, 200)
        self.restart_img = pygame.image.load('img/restart.png')
        self.present_group = pygame.sprite.Group()
        self.exit_group = pygame.sprite.Group()
        self.ice_group = pygame.sprite.Group()
        self.blob_group = pygame.sprite.Group()
        self.platform_group = pygame.sprite.Group()
        self.player = Player(100, self.screen_height - 130)
        self.restart_img = pygame.transform.scale(self.restart_img, self.button_size)
        self.button_x = self.screen_width // 2 - self.button_size[0] // 2
        self.button_y = self.screen_height // 2 - self.button_size[1] // 2 - self.y_offset
        self.restart_button = Button(self.button_x, self.button_y, self.restart_img)

        self.start_menu_img_scaled = pygame.transform.scale(self.start_menu_img,
                                                            (self.start_menu_img.get_width() // 2,
                                                             self.start_menu_img.get_height() // 2))
        self.exit_menu_img_scaled = pygame.transform.scale(self.exit_menu_img,
                                                           (self.exit_menu_img.get_width() // 2,
                                                            self.exit_menu_img.get_height() // 2))

        self.start_menu_button_y = self.screen_height // 2 - 200
        self.exit_menu_button_y = self.screen_height // 2 + 50

        self.start_menu_button = Button(self.screen_width // 2 - self.start_menu_img_scaled.get_width() // 2,
                                        self.start_menu_button_y,
                                        self.start_menu_img_scaled)
        self.exit_menu_button = Button(self.screen_width // 2 - self.exit_menu_img_scaled.get_width() // 2,
                                       self.exit_menu_button_y,
                                       self.exit_menu_img_scaled)

        self.pause_img = pygame.image.load('img/pause.png')
        self.pause_img_small = pygame.transform.scale(self.pause_img, (100, 100))
        self.continue_img = pygame.image.load('img/pause.png')
        self.exit_img = pygame.image.load('img/escape.png')

        self.pause_button = Button(880, 0, self.pause_img_small)
        self.continue_button = Button(self.screen_width // 2 - 150, self.screen_height // 2 - 450, self.continue_img)
        self.exit_button = Button(self.screen_width // 2 - 180, self.screen_height // 2 + 100, self.exit_img)

        self.exit_game_over_img = pygame.transform.scale(self.exit_img, (250, 250))
        self.exit_game_over_button = Button(self.screen_width // 2 - 130, self.screen_height // 2 + 120,
                                            self.exit_game_over_img)

    def draw_text(self, text, font, text_color, x, y):
        img = font.render(text, True, text_color)
        self.screen.blit(img, (x, y))

    def reset_level(self, level):
        old_global.player.reset(100, self.screen_height - 130)
        old_global.platform_group.empty()
        old_global.present_group.empty()
        old_global.blob_group.empty()
        old_global.ice_group.empty()
        old_global.exit_group.empty()
        if 'score_present' in globals():
            old_global.present_group.remove(old_global.score_present)
        self.score_present = Present((self.tile_size // 2) + 110, (self.tile_size // 2) + 35)
        old_global.present_group.add(self.score_present)

        if path.exists(f'level{level}'):
            pickle_in = open(f'level{level}', 'rb')
            world_data = pickle.load(pickle_in)
        world = World(world_data)
        return world

game_over = 0
main_menu = True
level = 1
max_levels = 6
score = 0
old_global = Old_Global()


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
                    img = pygame.transform.scale(self.land_img, (old_global.tile_size, old_global.tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * old_global.tile_size
                    img_rect.y = row_count * old_global.tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 2:
                    img = pygame.transform.scale(self.snowland_img, (old_global.tile_size, old_global.tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * old_global.tile_size
                    img_rect.y = row_count * old_global.tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 3:
                    blob = Enemy(col_count * old_global.tile_size, row_count * old_global.tile_size + 15)
                    old_global.blob_group.add(blob)
                elif tile == 4:
                    platform = Platform(col_count * old_global.tile_size, row_count * old_global.tile_size, 1, 0)
                    old_global.platform_group.add(platform)
                elif tile == 5:
                    platform = Platform(col_count * old_global.tile_size, row_count * old_global.tile_size, 0, 1)
                    old_global.platform_group.add(platform)
                elif tile == 6:
                    ice = Ice(col_count * old_global.tile_size, row_count * old_global.tile_size + (old_global.tile_size // 2))
                    old_global.ice_group.add(ice)
                elif tile == 7:
                    present = Present(col_count * old_global.tile_size + (old_global.tile_size // 2),
                                      row_count * old_global.tile_size + (old_global.tile_size // 2))
                    old_global.present_group.add(present)
                elif tile == 12:
                    img = pygame.transform.scale(self.lf_snowland_img, (old_global.tile_size, old_global.tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * old_global.tile_size
                    img_rect.y = row_count * old_global.tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 9:
                    img = pygame.transform.scale(self.rg_snowland_img, (old_global.tile_size, old_global.tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * old_global.tile_size
                    img_rect.y = row_count * old_global.tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 10:
                    img = pygame.transform.scale(self.lf_obrez_img, (old_global.tile_size, old_global.tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * old_global.tile_size
                    img_rect.y = row_count * old_global.tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 11:
                    img = pygame.transform.scale(self.rg_obrez_img, (old_global.tile_size, old_global.tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * old_global.tile_size
                    img_rect.y = row_count * old_global.tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 8:
                    exit = Win(col_count * old_global.tile_size, row_count * old_global.tile_size)
                    old_global.exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            old_global.screen.blit(tile[0], tile[1])


def save_score(score):
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute("INSERT INTO scores (score) VALUES (?)", (score,))
    conn.commit()
    conn.close()


def get_top_scores(limit=5):
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute("SELECT score FROM scores ORDER BY score DESC LIMIT ?", (limit,))
    top_scores = c.fetchall()
    conn.close()
    return top_scores


def draw_top_scores(current_score=None):
    top_scores = get_top_scores(3)
    y = 100
    for index, score in enumerate(top_scores):
        title = f'High Score {index + 1}'
        old_global.draw_text(f'{title}: {score[0]}', old_global.font_score, old_global.white, old_global.screen_width // 2 - 50, y)
        y += 40
    if current_score is not None:
        old_global.draw_text(f'Your Score: {current_score}', old_global.font_score, old_global.white, old_global.screen_width // 2 - 50, y)
        y += 40



class Snowflake():
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed

    def update(self):
        self.y += self.speed
        if self.y > old_global.screen_height:
            self.y = -50
            self.x = random.randint(0, old_global.screen_width)

    def draw(self):
        pygame.draw.circle(old_global.screen, (255, 255, 255), (self.x, self.y), self.size)


snowflakes = [Snowflake(random.randint(0, old_global.screen_width), random.randint(0, old_global.screen_height), random.randint(2, 5),
                        random.randint(1, 4)) for _ in range(100)]


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


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/platform.png')
        self.image = pygame.transform.scale(self.image, (old_global.tile_size, old_global.tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Win(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/portal.png')
        self.image = pygame.transform.scale(img, (old_global.tile_size, int(old_global.tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Ice(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/ice.png')
        self.image = pygame.transform.scale(img, (old_global.tile_size, old_global.tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Present(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/present.png')
        self.image = pygame.transform.scale(img, (old_global.tile_size // 2, old_global.tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)



if path.exists(f'level{old_global.level}'):
    pickle_in = open(f'level{old_global.level}', 'rb')
world_data = pickle.load(pickle_in)
world = World(world_data)
menu_music_playing = False
main_menu = True
run = True
pause = False
restart_button = Button(old_global.button_x, old_global.button_y, old_global.restart_img)

while run:
    old_global.clock.tick(old_global.fps)
    old_global.screen.blit(old_global.bg_img, (0, 0))

    if main_menu:
        for snowflake in snowflakes:
            snowflake.update()
        old_global.screen.blit(old_global.bg_img, (0, 0))
        for snowflake in snowflakes:
            snowflake.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        if not menu_music_playing:
            old_global.menu_sound.play(-1)
            menu_music_playing = True
        if old_global.exit_menu_button.draw():
            run = False
        if old_global.start_menu_button.draw():
            main_menu = False
            old_global.menu_sound.stop()
            menu_music_playing = False
    else:
        if not pause:
            world.draw()
            if game_over == 0:
                old_global.present_group.draw(old_global.screen)
                old_global.blob_group.update()
                old_global.platform_group.update()
                if pygame.sprite.spritecollide(old_global.player, old_global.present_group, True):
                    old_global.score += 1
                    old_global.present_sound.play()
                old_global.draw_text('Score: ' + str(old_global.score), old_global.font_score, old_global.white, old_global.tile_size - 40, 50)
            old_global.platform_group.draw(old_global.screen)
            old_global.blob_group.draw(old_global.screen)
            old_global.ice_group.draw(old_global.screen)
            old_global.exit_group.draw(old_global.screen)
            game_over = old_global.player.update(game_over)
            for snowflake in snowflakes:
                snowflake.update()
                snowflake.draw()

            if game_over == -1:
                draw_top_scores(current_score=old_global.score)
                if not old_global.game_over_music_played:
                    old_global.game_over_sound.play()
                    old_global.game_over_music_played = True
                old_global.draw_text('GAME OVER', old_global.font, old_global.red, (old_global.screen_width // 2) - 150, (old_global.screen_height // 2) - 200)
                if restart_button.draw():
                    save_score(old_global.score)
                    old_global.game_over_music_played = False
                    old_global.player.full_reset(100, old_global.screen_height - 130)
                    level = 1
                    world_data = []
                    world = old_global.reset_level(level)
                    game_over = 0
                    score = 0
                    pause = False

                if old_global.exit_game_over_button.draw():
                    save_score(score)
                    run = False
            old_global.player.draw_lives(old_global.screen)
            if game_over == 1:
                old_global.level_sound.play()
                level += 1
                if level <= old_global.max_levels:
                    world_data = []
                    world = old_global.reset_level(level)
                    game_over = 0
                else:
                    old_global.draw_text('YOU WIN!!!', old_global.font, old_global.red, (old_global.screen_width // 2) - 140, (old_global.screen_height // 2) - 200)
                    if restart_button.draw():
                        save_score(score)
                        game_over_music_played = False
                        old_global.player.full_reset(100, old_global.screen_height - 130)
                        level = 1
                        world_data = []
                        world = old_global.reset_level(level)
                        game_over = 0
                        score = 0
                        pause = False
            if not game_over and not main_menu:
                if old_global.pause_button.draw():
                    pause = True
        else:
            if old_global.continue_button.draw():
                pause = False
            if old_global.exit_button.draw():
                run = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()