import pgzrun
import random 

WIDTH = 700 # 700 / 50 = 14 hàng gạch 
HEIGHT = 400 # 400 / 50 = 8 hàng gạch 
SIZE_TANK = 25

walls = []
bullets = []
enemy_bullets = []
enemies = []
bullets_holdoff = 0
enemy_move_count = 0
choice = 0
game_over = False

tank = Actor("tank_blue")
tank.pos = (WIDTH/2,HEIGHT - 25)
tank.angle = 90

for i in range(1,7):
    tank_enemy = Actor("tank_red")
    tank_enemy.x =  i * 100 + SIZE_TANK
    tank_enemy.y = SIZE_TANK
    tank_enemy.angle = random.randint(0,3) * 90
    enemies.append(tank_enemy)

background = Actor("grass")


def myTank_set():
    original_x = tank.x
    original_y = tank.y
    if keyboard.left: 
        tank.x -= 2
        tank.angle = 180
    elif keyboard.right:
        tank.x += 2
        tank.angle = 0
    elif keyboard.down:
        tank.y += 2
        tank.angle = 270
    elif keyboard.up:
        tank.y -= 2 
        tank.angle = 90

    if tank.collidelist(walls) != -1:
        tank.x = original_x
        tank.y = original_y

    if tank.x < SIZE_TANK or tank.x > (WIDTH - SIZE_TANK) or tank.y < SIZE_TANK or tank.y > (HEIGHT - SIZE_TANK):
        tank.x = original_x
        tank.y = original_y

def tankEnemy_set():
    global enemy_move_count, bullets_holdoff
    for tank_enemy in enemies:
        original_x = tank_enemy.x
        original_y = tank_enemy.y
        choice = random.randint(0,2)
        if enemy_move_count > 0:
            enemy_move_count -= 1
            if tank_enemy.angle == 0:
                tank_enemy.x += 2  
            elif tank_enemy.angle == 90:
                tank_enemy.y -= 2
            elif tank_enemy.angle == 180:
                tank_enemy.x -= 2
            elif tank_enemy.angle == 270:
                tank_enemy.y += 2
            if tank_enemy.x < SIZE_TANK or tank_enemy.x >(WIDTH - SIZE_TANK) or tank_enemy.y < SIZE_TANK or tank_enemy.y > (HEIGHT - SIZE_TANK):
                tank_enemy.x = original_x
                tank_enemy.y = original_y
                enemy_move_count = 0
            if tank_enemy.collidelist(walls) != -1:
                tank_enemy.x = original_x
                tank_enemy.y = original_y
                enemy_move_count = 0
        elif choice == 0: # tank địch di chuyển
            enemy_move_count = 30
        elif choice == 1:# tank địch đổi hướng
            tank_enemy.angle = random.randint(0,3) * 90
        else:
            if bullets_holdoff  == 0:
                bullet = Actor("bulletred2")
                bullet.angle = tank_enemy.angle
                bullet.pos = tank_enemy.pos
                enemy_bullets.append(bullet)
                bullets_holdoff = 40
            else:
                bullets_holdoff -= 1
        
def myTank_bullets_set(): # đạn cho tank phe ta
    global bullets_holdoff
    if bullets_holdoff == 0:
        if keyboard.space:
            bullet = Actor("bulletblue2")        
            bullet.angle = tank.angle
            bullet.pos = tank.pos
            if bullet.angle == 0:
                bullet.x = bullet.x + SIZE_TANK
            if bullet.angle == 180:
                bullet.x = bullet.x - SIZE_TANK
            if bullet.angle == 90:
                bullet.y = bullet.y - SIZE_TANK
            if bullet.angle == 270:
                bullet.x = bullet.y + SIZE_TANK
            bullets.append(bullet)
            bullets_holdoff = 20
    else:
        bullets_holdoff -= 1 
    for bullet in bullets:
        if bullet.angle == 0:
            bullet.x = bullet.x + 5
        if bullet.angle == 180:
            bullet.x = bullet.x - 5
        if bullet.angle == 90:
            bullet.y = bullet.y - 5
        if bullet.angle == 270:
            bullet.y = bullet.y + 5
    for bullet in bullets: # mảng tường bị phá hủy khi trúng đạn
        walls_index = bullet.collidelist(walls)
        if walls_index != -1:
            sounds.gun9.play()
            del walls[walls_index]
            bullets.remove(bullet) 
        if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
            bullets.remove(bullet) 
        enemy_index = bullet.collidelist(enemies)
        if enemy_index != -1:
            sounds.exp.play()
            bullets.remove(bullet)
            del enemies[enemy_index]

def enemy_bullet_set():
    global enemies, game_over
    for bullet in enemy_bullets:
        if bullet.angle == 0:
            bullet.x = bullet.x + 5
        if bullet.angle == 180:
            bullet.x = bullet.x - 5
        if bullet.angle == 90:
            bullet.y = bullet.y - 5
        if bullet.angle == 270:
            bullet.y = bullet.y + 5
    for bullet in enemy_bullets: # mảng tường bị phá hủy khi trúng đạn
        walls_index = bullet.collidelist(walls)
        if walls_index != -1:
            sounds.gun10.play()
            del walls[walls_index]
            enemy_bullets.remove(bullet) 
        if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
            enemy_bullets.remove(bullet) 
        if bullet.colliderect(tank):
            game_over = True
            enemies = []


for x in range(14): # random tạo ra các mảng tường
    for y in range(6):
        if random.randint(0,100) < 50:
            wall = Actor("wall")
            wall.x = x * 50 + SIZE_TANK
            wall.y = y * 50 + SIZE_TANK * 3
            walls.append(wall) 

def update():
    myTank_set()
    myTank_bullets_set()
    tankEnemy_set()

def draw():
    if game_over:
        screen.fill((0,0,0))
        screen.draw.text('You Lose',(200,180),color=(255,255,255),fontsize = 100)
    elif len(enemies) == 0:
        screen.fill((0,0,0))
        screen.draw.text('You Win',(200,180),color=(255,255,255),fontsize = 100)
    else:
        background.draw()
        tank.draw()
        for wall in walls:
            wall.draw()
        for bullet in bullets:
            bullet.draw()
        for tank_enemy in enemies:
            tank_enemy.draw()
        for bullet in enemy_bullets:
            bullet.draw()
        enemy_bullet_set()



pgzrun.go()