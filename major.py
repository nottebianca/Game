import pygame
import random

pygame.init()

CLOCK = pygame.time.Clock()
FPS = 60
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
TILE_SIZE = 50

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Platformer')

BG_IMG = pygame.image.load('img/bg.png')
LAND_IMG = pygame.image.load('img/land.png')
SNOWLAND_IMG = pygame.image.load('img/snowland.png')


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
            if self.direction == 1:
                self.image = self.images_right[self.index]
            elif self.direction == -1:
                self.image = self.images_left[self.index]

        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right):
                self.index = 0
            if self.direction == 1:
                self.image = self.images_right[self.index]
            elif self.direction == -1:
                self.image = self.images_left[self.index]

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

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(LAND_IMG, (TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    self.tile_list.append((img, img_rect))
                elif tile == 2:
                    img = pygame.transform.scale(SNOWLAND_IMG, (TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    self.tile_list.append((img, img_rect))
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


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


snowflakes = [Snowflake(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT),
                        random.randint(2, 5), random.randint(1, 4)) for _ in range(100)]

world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 2, 2, 2, 1],
[1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1],
[1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
[1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1],
[1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

player = Player(100, SCREEN_HEIGHT - 130)
world = World(world_data)

run = True
while run:
    CLOCK.tick(FPS)

    for snowflake in snowflakes:
        snowflake.update()

    screen.blit(BG_IMG, (0, 0))
    world.draw()
    player.update()

    for snowflake in snowflakes:
        snowflake.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
