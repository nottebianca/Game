import pygame
import random

pygame.init()
clock = pygame.time.Clock()
FPS = 60
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Platformer')
TILE_SIZE = 50
BG_IMG = pygame.image.load('img/bg.png')

class Player:
    def __init__(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 14):
            img_right = pygame.image.load(f'img/Walk{num}.png')
            img_right = pygame.transform.scale(img_right, (60, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0

    def update(self):
        dx = 0
        dy = 0
        walk_cooldown = 5
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and not self.jumped:
            self.vel_y = -15
            self.jumped = True
        if not key[pygame.K_SPACE]:
            self.jumped = False
        if key[pygame.K_LEFT]:
            dx -= 5
            self.counter += 1
            self.direction = -1
        if key[pygame.K_RIGHT]:
            dx += 5
            self.counter += 1
            self.direction = 1
        if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
            self.counter = 0
            self.index = 0
            self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]
        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right):
                self.index = 0
            self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y
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
        self.rect.x += dx
        self.rect.y += dy
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            dy = 0
        screen.blit(self.image, self.rect)

class World:
    def __init__(self, data):
        self.tile_list = []
        land_img = pygame.image.load('img/land.png')
        snowland_img = pygame.image.load('img/snowland.png')
        lf_snowland_img = pygame.image.load('img/leftsnow.png')
        rg_snowland_img = pygame.image.load('img/rightsnow.png')
        lf_obrez_img = pygame.image.load('img/left_obrez.png')
        rg_obrez_img = pygame.image.load('img/right_obrez.png')
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                img = None
                if tile == 1:
                    img = pygame.transform.scale(land_img, (TILE_SIZE, TILE_SIZE))
                elif tile == 2:
                    img = pygame.transform.scale(snowland_img, (TILE_SIZE, TILE_SIZE))
                elif tile == 3:
                    blob = Enemy(col_count * TILE_SIZE, row_count * TILE_SIZE + 15)
                    blob_group.add(blob)
                elif tile == 6:
                    ice = Ice(col_count * TILE_SIZE, row_count * TILE_SIZE + (TILE_SIZE // 2))
                    ice_group.add(ice)
                elif tile == 8:
                    img = pygame.transform.scale(lf_snowland_img, (TILE_SIZE, TILE_SIZE))
                elif tile == 9:
                    img = pygame.transform.scale(rg_snowland_img, (TILE_SIZE, TILE_SIZE))
                elif tile == 10:
                    img = pygame.transform.scale(lf_obrez_img, (TILE_SIZE, TILE_SIZE))
                elif tile == 11:
                    img = pygame.transform.scale(rg_obrez_img, (TILE_SIZE, TILE_SIZE))

                if img:
                    img_rect = img.get_rect()
                    img_rect.x = col_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('img/slime_mob.png')
        self.image = pygame.transform.scale(img, (40, 40))
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

class Ice(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('img/ice.png')
        self.image = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 8, 2, 2, 1],
[1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 8, 9, 0, 7, 0, 5, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 8, 9, 0, 0, 0, 0, 0, 1],
[1, 7, 0, 0, 8, 2, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
[1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 8, 2, 2, 2, 2, 2, 2, 2, 2, 9, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 10, 1, 1, 1, 1, 1, 1, 1, 1, 11, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 2, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 2, 2, 2, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 8, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 0, 8, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
[1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

player = Player(100, SCREEN_HEIGHT - 130)
blob_group = pygame.sprite.Group()
ice_group = pygame.sprite.Group()
world = World(world_data)

class Snowflake:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = -50
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.size)

snowflakes = [Snowflake(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.randint(2, 5), random.randint(1, 4)) for _ in range(100)]

run = True
while run:
    clock.tick(FPS)
    for snowflake in snowflakes:
        snowflake.update()
    screen.blit(BG_IMG, (0, 0))
    world.draw()
    blob_group.update()
    blob_group.draw(screen)
    ice_group.draw(screen)
    player.update()
    for snowflake in snowflakes:
        snowflake.draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()
