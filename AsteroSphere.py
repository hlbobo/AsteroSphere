import pygame, sys, random

def draw_bg():
    screen.blit(bg_surface, (bg_x_pos,0))
    screen.blit(bg_surface, (bg_x_pos + 1280,0))

def createAstCluster():
    cluster = []
    num_asteroids = random.randint(2, 4)  # Number per cluster

    for i in range(num_asteroids):
        random_x = random.randint(1700, 2500)
        random_y = random.randint(120, 900)
        scale = random.uniform(0.3, 0.95)
        surface = pygame.transform.rotozoom(asteroid_surface, 0, scale)
        rect = surface.get_rect(center=(random_x, random_y))
        cluster.append((surface, rect))
    return cluster

def moveAst(asteroids):
    moved_asteroids = []
    for surface, rect in asteroids:
        rect.centerx -= 5
        moved_asteroids.append((surface, rect))
    return moved_asteroids

def drawAst(asteroids):
    for surface, rect in asteroids:
        screen.blit(surface, rect)

def check_AstCollision(asteroids):
    for surface, rect in asteroids:
        if collision_rect.colliderect(rect):
            return False
    if collision_rect.top <= -100 or collision_rect.bottom >= 1280:
        return False
    return True

def check_BulletCollision(bullet, asteroid_rect):
    return bullet.colliderect(asteroid_rect)

screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width,screen_height))
clock = pygame.time.Clock()
game_run = True

# variabile joc
gravity = 0.175

# gloanțe
bullet_width = 5
bullet_height = 10
bullet_speed = 6
bullets = []

# fundal
bg_surface = pygame.transform.scale_by((pygame.image.load('assets/bg.png')), 0.8).convert()
bg_x_pos = 0

# navă
ship_surface = pygame.image.load('assets/ship_hq.png').convert_alpha()
ship_rect = ship_surface.get_rect(center = (200,360))
collision_rect = ship_rect.inflate(-40, -20)
ship_movement_y = 0
ship_movement_x = 0
ship_rotation = 0

# dash
dash_timer = 0
dash_duration = 750
dashing = False
returning = False
return_point = 200

# asteroizi
asteroid_surface = pygame.image.load('assets/asteroid.png').convert_alpha()
asteroid_list = []
SPAWNAST = pygame.USEREVENT
pygame.time.set_timer(SPAWNAST,1700)

while True:
    events=pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        keys = pygame.key.get_pressed()
        if event.type == pygame.KEYDOWN:
            if keys[pygame.K_r] and game_run:
                ship_rotation += 1
            if ship_rotation == 0:
                if keys[pygame.K_SPACE] and game_run:
                    ship_movement_y = 0
                    ship_movement_y -= 8

                if keys[pygame.K_a] and game_run:
                    ship_movement_x = 0
                    ship_movement_x += 2
                    dash_timer = pygame.time.get_ticks()
                    dashing = True
                    returning = False

                if keys[pygame.K_d] and game_run:
                    ship_movement_x = 0
                    ship_movement_x -= 3
                    dash_timer = pygame.time.get_ticks()
                    dashing = True
                    returning = False

                if keys[pygame.K_w] and game_run:
                    bullet_x = ship_rect.centerx 
                    bullet_y = ship_rect.centery + ship_rect.height // 2 - bullet_height // 2
                    bullet_rect = pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height)
                    bullets.append({"rect": bullet_rect, "dir": "up"})
                    
            if ship_rotation == 1:
                if keys[pygame.K_SPACE] and game_run:
                    ship_movement_y = 0
                    ship_movement_y -= 8

                if keys[pygame.K_a] and game_run:
                    ship_movement_x = 0
                    ship_movement_x += 2
                    dash_timer = pygame.time.get_ticks()
                    dashing = True
                    returning = False

                if keys[pygame.K_d] and game_run:
                    bullet_x = ship_rect.centerx + ship_rect.width // 2 - bullet_width // 2
                    bullet_y = ship_rect.centery
                    bullet_rect = pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height)
                    bullets.append({"rect": bullet_rect, "dir": "right"})

                if keys[pygame.K_w] and game_run:
                    ship_movement_y = 0
                    ship_movement_y += 5
                    dash_timer = pygame.time.get_ticks()
                    dashing = True
            
            if ship_rotation == 2:
                if keys[pygame.K_SPACE] and game_run:
                    ship_movement_y = 0
                    ship_movement_y -= 8

                if keys[pygame.K_a] and game_run:
                    bullet_x = ship_rect.centerx + ship_rect.width // 2 - bullet_width // 2
                    bullet_y = ship_rect.centery
                    bullet_rect = pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height)
                    bullets.append({"rect": bullet_rect, "dir": "left"})

                if keys[pygame.K_d] and game_run:
                    ship_movement_x = 0
                    ship_movement_x -= 3
                    dash_timer = pygame.time.get_ticks()
                    dashing = True
                    returning = False
                    
                if keys[pygame.K_w] and game_run:
                    ship_movement_y = 0
                    ship_movement_y += 5
                    dash_timer = pygame.time.get_ticks()
                    dashing = True

            if keys[pygame.K_SPACE] and game_run == False:
                game_run = True
                asteroid_list.clear()
                bullets.clear()
                ship_rect.center = (200,360)
                ship_rotation = 0
                ship_movement_y = 0
                ship_movement_x = 0

        if event.type == SPAWNAST:
            asteroid_list.extend(createAstCluster())
    
    bg_x_pos -= 1
    draw_bg()
    if bg_x_pos < -1280:
        bg_x_pos = 0

    if game_run:
        # ship
        collision_rect = ship_rect.inflate((-40, -20))
        ship_movement_y += gravity
        ship_rect.centery += ship_movement_y
        ship_rect.centerx += ship_movement_x
        screen.blit(ship_surface, ship_rect)

        # dash
        if dashing and pygame.time.get_ticks() - dash_timer >= dash_duration:
            ship_movement_x = 0
            ship_movement_y -= 0.2
            dashing = False
            returning = True

        if returning:
            if abs(ship_rect.centerx - return_point) < 1:
                ship_rect.centerx = return_point
                returning = False
            elif ship_rect.centerx > return_point:
                ship_rect.centerx -= 1
            elif ship_rect.centerx < return_point:
                ship_rect.centerx += 0.5

        # gloanțe
        for bullet in bullets:
            if bullet["dir"] == "up":
                bullet["rect"].y -= bullet_speed
            elif bullet["dir"] == "right":
                bullet["rect"].x += bullet_speed
            elif bullet["dir"] == "left":
                bullet["rect"].x -= bullet_speed

        bullets = [
            bullet for bullet in bullets
            if 0 < bullet["rect"].x < screen_width and 0 < bullet["rect"].y < screen_height
        ]
        
        for bullet in bullets:
            pygame.draw.rect(screen, (255, 255, 255), bullet["rect"])

        for bullet in bullets[:]:
            for surface, asteroid_rect in asteroid_list[:]:
                if check_BulletCollision(bullet["rect"], asteroid_rect):
                    bullets.remove(bullet)
                    asteroid_list.remove((surface, asteroid_rect))
                    break


        # asteroids
        game_run = check_AstCollision(asteroid_list)
        asteroid_list = moveAst(asteroid_list)
        drawAst(asteroid_list)

    pygame.display.update()
    clock.tick(120)