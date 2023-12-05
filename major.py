import pygame


pygame.init()
clock = pygame.time.Clock()
fps = 60
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')
tile_size = 50
game_over = 0
bg_img = pygame.image.load('img/bg.png')
restart_img = pygame.image.load('img/restart.png')


class Buton():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self):
        action = False
        position = pygame.mouse.get_pos()
        if self.rect.collidepoint(position):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        screen.blit(self.image, self.rect)


class Player():
    def __init__(self, x, y):
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
            # get keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False:
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
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if below the ground i.e. jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # check if above the ground i.e. falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
            if pygame.sprite.spritecollide(self, ice_group, False):
                game_over = -1
            self.rect.x += dx
            self.rect.y += dy
        elif game_over == -1:
            self.image = self.dead_image
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        return game_over

    def draw_lives(self, screen):
        font = pygame.font.SysFont(None, 36)
        text = font.render('Lives:', True, (255, 255, 255))
        screen.blit(text, (10, 10))
        for i in range(self.lives):
            screen.blit(self.heart_animations[self.heart_frame], (80 + i * 35, 10))
        if self.frame_counter % 5 == 0:
            self.heart_frame += 1
            if self.heart_frame >= len(self.heart_animations):
                self.heart_frame = 0
        self.frame_counter += 1

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        self.lives = 3
        self.frame_counter = 0
        self.heart_animations = []
        for i in range(1, 8):
            heart_img = pygame.image.load(f'img/Cuore{i}.png')
            heart_img = pygame.transform.scale(heart_img, (30, 30))
            self.heart_animations.append(heart_img)
        self.heart_frame = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/Walk{num}.png')
            img_right = pygame.transform.scale(img_right, (50, 60))
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


class World():
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
                if tile == 1:
                    img = pygame.transform.scale(land_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(snowland_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == 6:
                    ice = Ice(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    ice_group.add(ice)
                if tile == 8:
                    img = pygame.transform.scale(lf_snowland_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 9:
                    img = pygame.transform.scale(rg_snowland_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 10:
                    img = pygame.transform.scale(lf_obrez_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 11:
                    img = pygame.transform.scale(rg_obrez_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


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


class Ice(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/ice.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
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
    [1, 0, 0, 0, 0, 8, 8, 2, 2, 6, 6, 6, 6, 6, 10, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

player = Player(100, screen_height - 130)
blob_group = pygame.sprite.Group()
ice_group = pygame.sprite.Group()
world = World(world_data)
restart_button = Buton(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)

run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))
    world.draw()
    if game_over == 0:
        blob_group.update()
    blob_group.draw(screen)
    ice_group.draw(screen)
    game_over = player.update(game_over)
    if game_over == -1:
        restart_button.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    player.draw_lives(screen)
    pygame.display.update()
pygame.quit()
