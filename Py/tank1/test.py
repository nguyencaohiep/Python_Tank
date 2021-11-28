import button
import pygame
import random
pygame.init()


IMAGE = {
    'icon': pygame.image.load("tank1/images/icon.png"),
    'tank_blue' : [
        pygame.image.load('tank1/images/tank_blue_{}.png'.format(i)) for i in ['right','down','left','up']
    ],
    'tank_sand' : [
        pygame.image.load('tank1/images/tank_sand_{}.png'.format(i)) for i in ['right','down','left','up']
    ],
    'bulletblue' : [
        pygame.image.load('tank1/images/bulletblue{}.png'.format(i)) for i in ['right','down','left','up']
    ],
    'bulletsand' : [
        pygame.image.load('tank1/images/bulletsand{}.png'.format(i)) for i in ['right','down','left','up']
    ],
    'explode' : [
        pygame.image.load('tank1/images/exploding_box/exploding_box_{}.png'.format(i)) for i in range(1, 7)
    ],
    'bgrass' : pygame.image.load('tank1/images/bgrass.png'),
    'wall' : pygame.image.load('tank1/images/wall.png'),
    'explosion0' : pygame.image.load('tank1/images/explosion0.png'),
    'explosion1' : pygame.image.load('tank1/images/explosion1.png'),
    'restart_btn' : pygame.image.load('tank1/images/restart_btn.png'),
    'start_btn' : pygame.image.load('tank1/images/start_btn.png'),
    'exit_btn' : pygame.image.load('tank1/images/exit_btn.png'),
}

tank_explosion = pygame.mixer.Sound('tank1/sounds/gun9.wav')
tank_explosion.set_volume(0.05)
wall_explosion = pygame.mixer.Sound('tank1/sounds/gun10.wav')
wall_explosion.set_volume(0.05)

DEFAULT_PLAYER_CONTROLS = {
    'up': pygame.K_UP,
    'down': pygame.K_DOWN,
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'shoot': pygame.K_q,
}

moving_right = False
moving_down = False
moving_left = False
moving_up = False

PAUSE_KEY = pygame.K_ESCAPE
SELECT_KEY = pygame.K_RETURN
UP_KEY = pygame.K_UP 
DOWN_KEY = pygame.K_DOWN

HEIGHT = 600
WIDTH = 800
SIZE_UNIT = 25
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Battle Tank')
pygame.display.set_icon(IMAGE['icon'])
clock = pygame.time.Clock()

restart_button = button.Button(WIDTH // 2 - 111, HEIGHT * 2 // 3, IMAGE['restart_btn'], 2)
start_button = button.Button(WIDTH // 2 - 130, HEIGHT // 3, IMAGE['start_btn'], 1)
exit_button = button.Button(WIDTH // 2 - 111, HEIGHT * 2 // 3, IMAGE['exit_btn'], 1)


class Bullet:
    def __init__(self, role, color, pos, direction):
        self.role = role
        self.color = color
        self.direction = direction
        self.assets = IMAGE['bullet' + color]
        self.image = self.assets[direction]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def fly(self):
        if self.direction == 0:
            self.rect.topleft = (self.rect.topleft[0] + 7, self.rect.topleft[1])
        if self.direction == 2:
            self.rect.topleft = (self.rect.topleft[0] - 7, self.rect.topleft[1])
        if self.direction == 3:
            self.rect.topleft = (self.rect.topleft[0], self.rect.topleft[1] - 7)
        if self.direction == 1:
            self.rect.topleft = (self.rect.topleft[0], self.rect.topleft[1] + 7)
    
    def draw(self):
        screen.blit(self.image, self.rect.topleft)


class Tank:
    def __init__(self, role, color, pos, direction, bullets_holdoff):
        self.role = role
        self.color = color
        self.direction = direction
        self.assets = IMAGE['tank_' + color]
        self.rect = self.assets[self.direction].get_rect()
        self.rect.topleft = pos
        self.bullets = []
        self.bullets_holdoff = bullets_holdoff
        self.bullets_holdoff_tmp = 0
    
    def draw(self):
        screen.blit(self.assets[self.direction], self.rect.topleft)

    def die(self):
        screen.blit(IMAGE['explosion0'], self.rect.topleft)
        screen.blit(IMAGE['explosion1'], self.rect.topleft)

    def cooldown(self):
        if self.bullets_holdoff_tmp > 0:
            self.bullets_holdoff_tmp -= 1

    def shoot(self):
        if self.bullets_holdoff_tmp == 0:
            self.bullets_holdoff_tmp = self.bullets_holdoff
            pos = [0, 0]
            if self.direction == 0:
                pos = [46, 17]
            if self.direction == 2:
                pos = [-13, 17]
            if self.direction == 3:
                pos = [17, -13]
            if self.direction == 1:
                pos = [17, 46]

            bullet = Bullet(self.role, self.color, (self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]), self.direction)
            self.bullets.append(bullet)

    def move(self, moving_right, moving_left, moving_up, moving_down, distance=3):
        original_x = self.rect.topleft[0]
        original_y = self.rect.topleft[1]
        if moving_left:
            original_x -= 3
            self.direction = 2
        elif moving_right:
            original_x += 3
            self.direction = 0
        elif moving_up:
            original_y -= 3
            self.direction = 3
        elif moving_down:
            original_y += 3
            self.direction = 1
        rect = self.assets[self.direction].get_rect()
        rect.topleft = (original_x, original_y)

        if original_x >= 0 and original_x <= (WIDTH-SIZE_UNIT*2) and original_y >= 0 and original_y <= (HEIGHT-SIZE_UNIT*2) and rect.collidelist(walls) < 0:
            self.rect.topleft = (original_x, original_y)


class Enemy(Tank):
    def __init__(self, role, color, pos, direction, bullets_holdoff, enemy_move_count=0):
        self.role = role
        self.color = color
        self.direction = direction
        self.assets = IMAGE['tank_' + color]
        self.rect = self.assets[self.direction].get_rect()
        self.rect.topleft = pos
        self.bullets = []
        self.bullets_holdoff = bullets_holdoff
        self.bullets_holdoff_tmp = 0
        self.enemy_move_count = enemy_move_count

    def auto(self):
        original_x = self.rect.topleft[0]
        original_y = self.rect.topleft[1]
        choice = random.randint(0, 2)
        if self.enemy_move_count > 0:
            self.enemy_move_count -= 1
            self.move(self.direction == 0, self.direction == 2, self.direction == 3, self.direction == 1)
            if original_x == self.rect.topleft[0] and original_y == self.rect.topleft[1]:
                self.enemy_move_count = 0

        elif choice == 0:             # xe tăng địch di chuyển
            self.enemy_move_count = 23
        elif choice == 1:               # xe tăng địch đổi hướng
            direction = random.randint(0, 3)
            self.move(direction == 0, direction == 2, direction == 3, direction == 1)
        if choice == 2:
            self.shoot()

    
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGE['wall']
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def explode(self):
        screen.blit(IMAGE['explode'][2], self.rect.topleft)


def destroy():
    global game_over
    for enemy in enemies:
        for bullet in enemy.bullets:
            wall_index = bullet.rect.collidelist(walls)
            if wall_index != -1:
                walls[wall_index].explode()
                del walls[wall_index]
                enemy.bullets.remove(bullet)
                wall_explosion.play()
        if player.rect.collidelist(enemy.bullets) != -1:
            tank_explosion.play()
            player.die()
            game_over = True


    for bullet in player.bullets:
        wall_index = bullet.rect.collidelist(walls)
        if wall_index != -1:
            walls[wall_index].explode()
            del walls[wall_index]
            player.bullets.remove(bullet)
            wall_explosion.play()
        enemy_index = bullet.rect.collidelist(enemies)
        if enemy_index != -1:
            enemies[enemy_index].die()
            del enemies[enemy_index]
            player.bullets.remove(bullet)
            tank_explosion.play()
        if bullet.rect.topleft[0] < 0 or bullet.rect.topleft[0] > WIDTH or bullet.rect.topleft[1] < 0 or bullet.rect.topleft[1] > HEIGHT:
            player.bullets.remove(bullet)


def set_map():
    global background, walls
    background = IMAGE['bgrass']
    walls = []
    for x in range(16):
        for y in range(10):
            if random.randint(0, 100) < 50:
                wall = Wall(x * 50, y * 50 + SIZE_UNIT * 2)
                walls.append(wall)

def set_objects():
    global player, enemies
    player = Tank('player', 'blue', (WIDTH / 2 - SIZE_UNIT, HEIGHT - SIZE_UNIT * 2), 3, 20)
    enemies = []
    for i in range(7):
        enemy = Enemy('enemy', 'sand', (i * 100 + 100, 0), 1, 33)
        enemies.append(enemy)


def cooldown():
    player.cooldown()
    for enemy in enemies:
        enemy.cooldown()

def bullet_fly():
    for bl in player.bullets:
        bl.fly()
    for enemy in enemies:
        for bl in enemy.bullets:
            bl.fly()


def draw():
    screen.blit(background, (0, 0))
    for wall in walls:
        screen.blit(wall.image, wall.rect.topleft)
    player.draw()
    for bl in player.bullets:
        bl.draw()
    for enemy in enemies:
        enemy.draw()
        for bl in enemy.bullets:
            bl.draw()

game_over = False
start_game = False
run = True
while run:
    clock.tick(35)
    if game_over:
        screen.fill((0, 0, 0))
        font = pygame.font.Font("tank1/fonts/prstart.ttf", 40)
        text = font.render('YOU LOSE', True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (WIDTH // 2, HEIGHT // 2)
        screen.blit(text, textRect)
        restart_button.draw(screen)
        if restart_button.is_clicked():
            start_game = True
            game_over = False
            set_map()
            set_objects()    

    elif start_game == False:
        screen.fill((144, 201, 120))
        start_button.draw(screen)
        exit_button.draw(screen)        
        if start_button.is_clicked():
            start_game = True
            set_map()
            set_objects()            
        if exit_button.is_clicked():
            run = False

    elif len(enemies) == 0:
        screen.fill((0, 0, 0))
        font = pygame.font.Font("tank1/fonts/prstart.ttf", 40)
        text = font.render('YOU WIN', True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (WIDTH // 2, HEIGHT // 2)
        screen.blit(text, textRect)

    else:
        draw()
        cooldown()
        bullet_fly()
        destroy()
        for enemy in enemies:
            enemy.auto()
        player.move(moving_right, moving_left, moving_up, moving_down)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                player.shoot()
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_UP:
                moving_up = True
            if event.key == pygame.K_DOWN:
                moving_down = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_UP:
                moving_up = False
            if event.key == pygame.K_DOWN:
                moving_down = False
	        
    pygame.display.update()

pygame.quit()