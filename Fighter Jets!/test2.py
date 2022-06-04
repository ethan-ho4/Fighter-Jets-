import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 600, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fighter Jets!")

# Load images
JET_1_FLIPPED = pygame.image.load(os.path.join("images", "jet1.png"))
JET_2_FLIPPED = pygame.image.load(os.path.join("images", "jet2.png"))
JET_3_FLIPPED = pygame.image.load(os.path.join("images", "jet3.png"))

#rotate images
JET_1 = pygame.transform.rotate(JET_1_FLIPPED, 180)
JET_2 = pygame.transform.rotate(JET_2_FLIPPED, 180)
JET_3 = pygame.transform.rotate(JET_3_FLIPPED, 180)

# Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("images", "player_jet.png"))

# Lasers
LASER_1 = pygame.image.load(os.path.join("images", "laser1.png"))
LASER_2 = pygame.image.load(os.path.join("images", "laser2.png"))
LASER_3 = pygame.image.load(os.path.join("images", "laser3.png"))
LASER_4 = pygame.image.load(os.path.join("images", "arrow.png"))

# Background
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("images", "background.png")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Jet:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.jet_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldown_counter = 0

    def draw(self, window):
        window.blit(self.jet_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x + 25, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1

    def get_width(self):
        return self.jet_img.get_width()

    def get_height(self):
        return self.jet_img.get_height()


class Player(Jet):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.jet_img = YELLOW_SPACE_SHIP
        self.laser_img = LASER_4
        self.mask = pygame.mask.from_surface(self.jet_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.jet_img.get_height() + 10, self.jet_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.jet_img.get_height() + 10, self.jet_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Jet):
    COLOR_MAP = {
                "red": (JET_1, LASER_1),
                "green": (JET_2, LASER_2),
                "blue": (JET_3, LASER_3)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.jet_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.jet_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x + 10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 30)
    lost_font = pygame.font.SysFont("comicsans", 30)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 8

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        SCREEN.blit(BACKGROUND, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        SCREEN.blit(lives_label, (10, 10))
        SCREEN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(SCREEN)

        player.draw(SCREEN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            SCREEN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 30)
    run = True
    while run:
        SCREEN.blit(BACKGROUND, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        SCREEN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()