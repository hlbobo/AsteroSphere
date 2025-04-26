import pygame, sys, random
from sys import exit

class Button:
    def __init__(self, pos, image, text_input, base_clr, hover_clr):
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.image = image
        self.base_clr = base_clr
        self.hover_clr = hover_clr
        self.text_input = text_input
        self.text = game_font.render(self.text_input, True, "white")
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
    
    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkClick(self, position):
        return self.rect.collidepoint(position)
    
    def changeColor(self, position):
        if self.rect.collidepoint(position):
            self.text = game_font.render(self.text_input, True, self.hover_clr)
        else:
            self.text = game_font.render(self.text_input, True, self.base_clr)    

class Quadtree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary
        self.capacity = capacity
        self.objects = []
        self.divided = False 

    def subdivide(self):
        x, y, w, h = self.boundary
        half_w, half_h = w // 2, h // 2
        
        # Define boundaries for the four child nodes
        self.northeast = Quadtree(pygame.Rect(x + half_w, y, half_w, half_h), self.capacity)
        self.northwest = Quadtree(pygame.Rect(x, y, half_w, half_h), self.capacity)
        self.southeast = Quadtree(pygame.Rect(x + half_w, y + half_h, half_w, half_h), self.capacity)
        self.southwest = Quadtree(pygame.Rect(x, y + half_h, half_w, half_h), self.capacity)
        
        self.divided = True

    def insert(self, obj):
        if not self.boundary.colliderect(obj):
            return False

        if len(self.objects) < self.capacity:
            self.objects.append(obj)
            return True
        else:
            if not self.divided:
                self.subdivide()
            return (self.northeast.insert(obj) or
                    self.northwest.insert(obj) or
                    self.southeast.insert(obj) or
                    self.southwest.insert(obj))

    def query(self, range_rect, found_objects):
        if not self.boundary.colliderect(range_rect):
            return found_objects

        for obj in self.objects:
            if range_rect.colliderect(obj):
                found_objects.append(obj)

        if self.divided:
            self.northwest.query(range_rect, found_objects)
            self.northeast.query(range_rect, found_objects)
            self.southwest.query(range_rect, found_objects)
            self.southeast.query(range_rect, found_objects)

        return found_objects

class Bullet:
    WIDTH = 20
    HEIGHT = 5
    speed = 6

    def __init__(self):
        self.active = False
        self.rect = pygame.Rect(0, 0, Bullet.WIDTH, Bullet.HEIGHT)

    def reset(self, x_pos, y_pos, speed, direction):
        if direction == "up":
            self.rect = pygame.Rect(0, 0, Bullet.HEIGHT, Bullet.WIDTH)
        else:
            self.rect = pygame.Rect(0, 0, Bullet.WIDTH, Bullet.HEIGHT)
        self.rect.center = (x_pos, y_pos)
        self.speed = speed
        self.active = True
        self.dir = direction

    def update(self):
        if self.active:
            if self.dir == "right":
                self.rect.x += self.speed
            elif self.dir == "left":
                self.rect.x -= self.speed
            elif self.dir == "up":
                self.rect.y -= self.speed

            if (
                self.rect.right < 0 or self.rect.left > screen_width or
                self.rect.bottom < 0 or self.rect.top > screen_height
            ):
                self.active = False

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, (255, 255, 255), self.rect)      

screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("AsteroSphere")
icon=pygame.image.load('assets/Images/icon.ico').convert()
pygame.display.set_icon(icon)
pygame.font.init()
pygame.mixer.init(frequency = 44100, size = -16, channels = 2, buffer = 2**12)
channel1 = pygame.mixer.Channel(1)
shoot = pygame.mixer.Sound('assets/Audio/laser.mp3')
bgm = pygame.mixer.music.load('assets/Audio/bgm.mp3')
clock = pygame.time.Clock()

# variabile joc
logo_font = pygame.font.Font('assets/Fonts/Gamer.ttf', 150)
game_font = pygame.font.Font('assets/Fonts/Gamer.ttf', 55)
vol_sfx = 0.2
vol_mus = 0.2
subtitle_font = pygame.font.Font('assets/Fonts/Gamer.ttf', 90)
gravity = 0.175

level = 0
level_is_up = False
score = 0
highscore = 0
score_increment = 100
update_score_event = pygame.USEREVENT + 2 

button_surface = pygame.transform.scale_by(pygame.image.load('assets/Images/button.png'), 1.70).convert_alpha()
button1_surface = pygame.transform.scale_by(pygame.image.load('assets/Images/button1.png'),1.90).convert_alpha()
game_run = True
current_state = "main_menu"

# gloanțe
bullet_pool = [Bullet() for _ in range(50)]

# fundal
bg_surface = pygame.transform.scale_by((pygame.image.load('assets/Images/bg.png')), 0.8).convert()
bg_x_pos = 0

# navă
ship_surface = pygame.transform.scale_by(pygame.image.load('assets/Images/ship/ship-0.png'), 0.85).convert_alpha()
ship_rect = ship_surface.get_rect(center = (270,360))
collision_rect = ship_rect.inflate(-35, -35)
ship_movement_y = 0
ship_movement_x = 0
ship_rotation = 0

# dash
dash_timer = 0
dash_duration = 750
dash_cooldown = 2000
last_dash_time = 0
dashing = False
returning = False
return_point = 270

# combustibil
current_fuel = 2400
fuel_display = 100
fuel_can_surface = pygame.transform.scale_by(pygame.image.load('assets/Images/fuel.png'), 0.85).convert_alpha()
fuel_cans = []
SPAWNFUEL = pygame.USEREVENT

# asteroizi
asteroid_surface = pygame.image.load('assets/Images/asteroid.png').convert_alpha()
asteroid_list = []
SPAWNAST = pygame.USEREVENT+1

def draw_bg(): # afișează fundalul
    screen.blit(bg_surface, (bg_x_pos, 0))
    screen.blit(bg_surface, (bg_x_pos + 1280,0))

def createAstCluster(): # creează mulțimea de asteroizi
    cluster = []
    num_asteroids = random.randint(1 + level, 2 + level)

    for i in range(num_asteroids):
        random_x = random.randint(1700, 2600)
        random_y = random.randint(100, 700)
        scale = random.uniform(0.35, 0.95)
        surface = pygame.transform.rotozoom(asteroid_surface, 0, scale)
        rect = surface.get_rect(center=(random_x, random_y))
        cluster.append((surface, rect))
    return cluster

def moveAst(asteroids): # mișcă asteroizii
    moved_asteroids = []
    for surface, rect in asteroids:
        rect.centerx -= 6
        moved_asteroids.append((surface, rect))
    return moved_asteroids

def drawAst(asteroids): # afișează asteroizii
    for surface, rect in asteroids:
        screen.blit(surface, rect)

def checkAstCollision(asteroids): # verifică dacă jucătorul se izbește de asteroizi
    for surface, rect in asteroids:
        if collision_rect.colliderect(rect):
            return False
    return True

def other_death(): # condiții ca jocul să se sfârșească
    if collision_rect.top <= -100 or collision_rect.bottom >= 1280 or collision_rect.left <= -90 or current_fuel<=0:
        return False
    return True

def shoot_bullet():
    bullet = get_bullet()
    if not bullet:
        return

    if ship_rotation == 0:
        bullet_x = ship_rect.centerx
        bullet_y = ship_rect.centery + ship_rect.height // 2 - Bullet.HEIGHT // 2
        bullet.reset(bullet_x, bullet_y, Bullet.speed, direction="up")

    elif ship_rotation == 1:
        bullet_x = ship_rect.centerx + ship_rect.width // 2 - Bullet.WIDTH // 2
        bullet_y = ship_rect.centery
        bullet.reset(bullet_x, bullet_y, Bullet.speed, direction="right")

    elif ship_rotation == 2:
        bullet_x = ship_rect.centerx + ship_rect.width // 2 - Bullet.WIDTH // 2
        bullet_y = ship_rect.centery
        bullet.reset(bullet_x, bullet_y, Bullet.speed, direction="left")

    global current_fuel
    current_fuel -= 50
    channel1.play(shoot)

def get_bullet():
    for bullet in bullet_pool:
        if not bullet.active:
            return bullet
    return None

def upAndDrawBullets():
    for bullet in bullet_pool:
        bullet.update()
        bullet.draw(screen)

def check_BulletCollision(bullet, asteroid_rect): # verifică dacă gloanțele lovesc asteroizii
    return bullet.colliderect(asteroid_rect)

def handle_BulletCollision(quadtree):
    to_remove = []
    global score, highscore

    for bullet in bullet_pool:
        if bullet.active:
            collision_range = pygame.Rect(bullet.rect.x - 10, bullet.rect.y - 10, 20, 20)
            nearby_asteroids = quadtree.query(collision_range, [])

            for asteroid_rect in nearby_asteroids:
                if bullet.rect.colliderect(asteroid_rect):
                    bullet.active = False
                    for surface, rect in asteroid_list:
                        if rect == asteroid_rect:
                            to_remove.append((surface, rect))
                            break
                    score += score_increment
                    if score > highscore:
                        highscore = score
                        save_high_score(score, "highscore.txt")
                    break

    for asteroid in to_remove:
        if asteroid in asteroid_list:
            asteroid_list.remove(asteroid)

def createFuelCans(): # creează canistrele de combustibil
    random_x = random.randint(1700, 2600)
    random_y = random.randint(145, 650)
    new_can = fuel_can_surface.get_rect(center=(random_x,random_y))
    return new_can
    
def moveFuelCan(fuel_cans): # mișcă canistrele de combustibil
    for fuel_can in fuel_cans:
        fuel_can.centerx -= 5.5
    return fuel_cans

def drawFuelCan(fuel_cans): # afișează canistrele de combustibil
    for fuel_can in fuel_cans:
        screen.blit(fuel_can_surface,fuel_can)

def draw_fuel_gauge(screen, x, y, width, height, current, max_fuel):
    percent = max(min(current / max_fuel, 1), 0)
    fill_width = int(width * percent)

    if percent > 0.5:
        color = (0, 255, 0)  # green
    elif percent > 0.25:
        color = (255, 165, 0)  # orange
    else:
        color = (255, 0, 0)  # red

    # outline
    pygame.draw.rect(screen, (255, 255, 255), (x-2.5, y-3.5, width+6, height+8), border_radius=8)

    # Draw background
    pygame.draw.rect(screen, (60, 60, 60), (x, y, width, height), border_radius=7)
    
    # Draw fuel fill
    pygame.draw.rect(screen, color, (x, y, fill_width, height), border_radius=7)

def checkFuelCollision(fuel_cans): # verifci dacă jucătorul atinge asteroidul
    for fuel_can in fuel_cans:
        if collision_rect.colliderect(fuel_can):
            return True
    return False

def volumeBar(vols, slider_x, slider_y): # desenare bară volum
    slider_width = 200
    slider_height = 50
    pygame.draw.rect(screen, (100, 100, 100), (slider_x, slider_y, slider_width, slider_height), border_radius=5)

    # Volume level indicator
    filled_width = int(slider_width * vols)
    pygame.draw.rect(screen, (0, 200, 0), (slider_x, slider_y, filled_width, slider_height), border_radius=5)

    # Volume percentage text
    volume_text = game_font.render(f"{int(vols*100)}%", True, (255, 255, 255))
    screen.blit(volume_text, (screen_width // 2 - volume_text.get_width() // 2, slider_y))

def load_high_score(filename="highscore.txt"): # încarcă cel mai mare scor
    try:
        with open(filename, "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0
    
def save_high_score(score, filename="highscore.txt"): # salvează cel mai mare scor
    with open(filename, "w") as file:
        file.write(str(score))

def game(): # ecranul de joc
    screen.blit(bg_surface, (0,0))

    global ship_surface, ship_rotation, ship_rect, ship_movement_y, ship_movement_x, collision_rect
    global current_fuel, fuel_display, bullet, fuel_cans, level_is_up, surface
    global game_run, level, asteroid_list, bg_x_pos, score, highscore, score_increment
    global dash_timer, dash_duration, dash_cooldown, last_dash_time, dashing, returning

    game_run = True
    asteroid_list.clear()
    bullet = get_bullet()
    fuel_cans.clear()
    pygame.time.set_timer(SPAWNFUEL, 0)
    pygame.time.set_timer(SPAWNFUEL, 10000)
    ship_rect.center = (270,360)
    ship_rotation = 0
    score = 0
    level = 0
    current_fuel = 2400
    fuel_display = 100
    ship_movement_y = 0
    ship_movement_x = 0
    
    while True:
        quadtree = Quadtree(pygame.Rect(0, 0, screen_width, screen_height), capacity=4)

        # Insert all asteroid bounding boxes into the quadtree
        for surface, asteroid_rect in asteroid_list:
            quadtree.insert(asteroid_rect)

        events=pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_run:
                    ship_rotation = (ship_rotation + 1) % 3

                if ship_rotation == 0:
                    ship_surface = pygame.image.load('assets/Images/ship/ship-0.png').convert_alpha()
                    if event.key == pygame.K_SPACE and game_run:
                        ship_movement_y = 0
                        ship_movement_y -= 8

                    if event.key == pygame.K_a and game_run:
                        current_time = pygame.time.get_ticks()
                        if current_time - last_dash_time > dash_cooldown:
                            ship_movement_x = 0
                            ship_movement_x += 2
                            current_fuel -= 150
                            dash_timer = current_time
                            last_dash_time = current_time
                            dashing = True
                            returning = False

                    if event.key == pygame.K_d and game_run:
                        current_time = pygame.time.get_ticks()
                        if current_time - last_dash_time > dash_cooldown:
                            ship_movement_x = 0
                            ship_movement_x -= 3
                            current_fuel -= 150
                            dash_timer = current_time
                            last_dash_time = current_time
                            dashing = True
                            returning = False

                    if event.key == pygame.K_w and game_run:
                        shoot_bullet()
                        
                if ship_rotation == 1:
                    ship_surface = pygame.image.load('assets/Images/ship/ship-7.png').convert_alpha()
                    if event.key == pygame.K_SPACE and game_run:
                        ship_movement_y = 0
                        ship_movement_y -= 8

                    if event.key == pygame.K_a and game_run:
                        current_time = pygame.time.get_ticks()
                        if current_time - last_dash_time > dash_cooldown:
                            ship_movement_x = 0
                            ship_movement_x += 2
                            current_fuel -= 150
                            dash_timer = current_time
                            last_dash_time = current_time
                            dashing = True
                            returning = False

                    if event.key == pygame.K_d and game_run:
                        shoot_bullet()

                    if event.key == pygame.K_w and game_run:
                        current_time = pygame.time.get_ticks()
                        if current_time - last_dash_time > dash_cooldown:
                            ship_movement_y = 0
                            ship_movement_y += 3
                            current_fuel -= 150
                            dash_timer = current_time
                            last_dash_time = current_time
                            dashing = True
                            returning = False
                
                if ship_rotation == 2:
                    ship_surface = pygame.image.load('assets/Images/ship/ship-8.png').convert_alpha()
                    if event.key == pygame.K_SPACE and game_run:
                        ship_movement_y = 0
                        ship_movement_y -= 8

                    if event.key == pygame.K_a and game_run:
                        shoot_bullet()

                    if event.key == pygame.K_d and game_run:
                        current_time = pygame.time.get_ticks()
                        if current_time - last_dash_time > dash_cooldown:
                            ship_movement_x = 0
                            ship_movement_x -= 3
                            current_fuel -= 150
                            dash_timer = current_time
                            last_dash_time = current_time
                            dashing = True
                            returning = False
                        
                    if event.key == pygame.K_w and game_run:
                        current_time = pygame.time.get_ticks()
                        if current_time - last_dash_time > dash_cooldown:
                            ship_movement_y = 0
                            ship_movement_y += 3
                            current_fuel -= 150
                            dash_timer = current_time
                            last_dash_time = current_time
                            dashing = True
                            returning = False

            if event.type == update_score_event:
                score += score_increment

            if event.type == SPAWNAST:
                asteroid_list.extend(createAstCluster())

            if event.type == SPAWNFUEL:
                fuel_cans.append(createFuelCans())

        bg_x_pos -= 1
        draw_bg()
        if bg_x_pos < -1280:
            bg_x_pos = 0

        if game_run:
            # gloanțe
            upAndDrawBullets()
            handle_BulletCollision(quadtree)

            # navă
            global collision_rect
            collision_rect = ship_rect.inflate((-35, -35))
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
                    ship_rect.centerx += 1

            # asteroizi
            asteroid_list = moveAst(asteroid_list)
            drawAst(asteroid_list)
            game_run = checkAstCollision(asteroid_list)
            if game_run == False:
                return "game_over"

            game_run = other_death()
            if game_run == False:
                return "game_over"
            
            # combustibil
            current_fuel -= 1
            fuel_display -= 1
            fuel_icon = pygame.transform.scale_by((pygame.image.load('assets/Images/fuel.png')), 0.5)
            fuel_icon_rect = fuel_icon.get_rect(center=(70, 60))
            screen.blit(fuel_icon, fuel_icon_rect)
            draw_fuel_gauge(screen, x=100, y=50, width=200, height=25, current=current_fuel, max_fuel=2400)
            fuel_cans = moveFuelCan(fuel_cans)
            drawFuelCan(fuel_cans)

            got_fuel = checkFuelCollision(fuel_cans)
            if got_fuel:
                current_fuel = 2400
                fuel_cans.clear()

            # scor
            score_text = game_font.render(f"Score: {score}", True, (255,255,255))
            screen.blit(score_text, (50, 90))

            level = score // 1000
           
        pygame.display.update()
        clock.tick(120)

def options(): # meniul de setări
    options_Text = subtitle_font.render("Options", True, "white")
    options_rect = options_Text.get_rect(center=(640, 200))

    controls_button = Button(pos=(360, 360), image=button_surface, text_input="Controls", base_clr="white", hover_clr="Green")
    volume_button = Button(pos=(640, 360), image=button_surface, text_input="Volume", base_clr="white", hover_clr="Green")
    back_button = Button(pos=(640, 500), image=button_surface, text_input="Back", base_clr="white", hover_clr="Green")
    fullscreen_button = Button(pos=(920,360), image=button_surface, text_input="Fullscreen", base_clr="white", hover_clr="green")
    while True:
        screen.blit(bg_surface, (0,0))

        options_MousePos = pygame.mouse.get_pos()

        screen.blit(options_Text, options_rect)

        for button in [controls_button, volume_button, fullscreen_button, back_button]:
            button.changeColor(options_MousePos)
            button.update(screen)

        events=pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if fullscreen_button.checkClick(options_MousePos):
                    pygame.display.toggle_fullscreen()

                if controls_button.checkClick(options_MousePos):
                    return "controls"
                
                if volume_button.checkClick(options_MousePos):
                    return "volume"

                if back_button.checkClick(options_MousePos):
                    return "main_menu"

        pygame.display.update()
        clock.tick(120)

def controls(): # lista cu controale
    controls_Text = subtitle_font.render("Controls", True, "white")
    controls_rect = controls_Text.get_rect(center=(640,150))

    controls_text_l1 = game_font.render("Rotation 1:", True, "white")
    controls_l1_rect = controls_text_l1.get_rect(center=(320, 250))
    controls_l1_jump = game_font.render("Jump: SPACE", True, "white")
    controls_l1_jump_rect = controls_l1_jump.get_rect(center=(320, 300))
    controls_l1_dashright = game_font.render("Dash Right: A", True, "white")
    controls_l1_dashright_rect = controls_l1_dashright.get_rect(center=(320, 350))
    controls_l1_dashleft = game_font.render("Dash Left: D", True, "white")
    controls_l1_dashleft_rect = controls_l1_dashleft.get_rect(center=(320, 400))
    controls_l1_shoot = game_font.render("Shoot: W", True, "white")
    controls_l1_shoot_rect = controls_l1_shoot.get_rect(center=(320, 450))

    controls_text_l2 = game_font.render("Rotation 2:", True, "white")
    controls_l2_rect = controls_text_l2.get_rect(center=(640, 250))
    controls_l2_jump = game_font.render("Jump: SPACE", True, "white")
    controls_l2_jump_rect = controls_l2_jump.get_rect(center=(640, 300))
    controls_l2_dashright = game_font.render("Dash Right: A", True, "white")
    controls_l2_dashright_rect = controls_l2_dashright.get_rect(center=(640, 350))
    controls_l2_dashdown = game_font.render("Dash Down: W", True, "white")
    controls_l2_dashdown_rect = controls_l2_dashdown.get_rect(center=(640, 400))
    controls_l2_shoot = game_font.render("Shoot: D", True, "white")
    controls_l2_shoot_rect = controls_l2_shoot.get_rect(center=(640, 450))

    controls_text_l3 = game_font.render("Rotation 3:", True, "white")
    controls_l3_rect = controls_text_l3.get_rect(center=(960, 250))
    controls_l3_jump = game_font.render("Jump: SPACE", True, "white")
    controls_l3_jump_rect = controls_l3_jump.get_rect(center=(960, 300))
    controls_l3_dashleft = game_font.render("Dash Left: D", True, "white")
    controls_l3_dashleft_rect = controls_l3_dashleft.get_rect(center=(960, 350))
    controls_l3_dashdown = game_font.render("Dash Down: W", True, "white")
    controls_l3_dashdown_rect = controls_l3_dashdown.get_rect(center=(960, 400))
    controls_l3_shoot = game_font.render("Shoot: A", True, "white")
    controls_l3_shoot_rect = controls_l3_shoot.get_rect(center=(960, 450))

    back_button = Button(pos=(640, 550), image=button_surface, text_input="Back", base_clr="white", hover_clr="Green")
    while True:
        screen.blit(bg_surface, (0,0))

        controls_MousePos = pygame.mouse.get_pos()

        screen.blit(controls_Text, controls_rect)
        screen.blit(controls_text_l1, controls_l1_rect)
        screen.blit(controls_l1_jump, controls_l1_jump_rect)
        screen.blit(controls_l1_dashright, controls_l1_dashright_rect)
        screen.blit(controls_l1_dashleft, controls_l1_dashleft_rect)
        screen.blit(controls_l1_shoot, controls_l1_shoot_rect)

        screen.blit(controls_text_l2, controls_l2_rect)
        screen.blit(controls_l2_jump, controls_l2_jump_rect)
        screen.blit(controls_l2_dashright, controls_l2_dashright_rect)
        screen.blit(controls_l2_dashdown, controls_l2_dashdown_rect)
        screen.blit(controls_l2_shoot, controls_l2_shoot_rect)

        screen.blit(controls_text_l3, controls_l3_rect)
        screen.blit(controls_l3_jump, controls_l3_jump_rect)
        screen.blit(controls_l3_dashleft, controls_l3_dashleft_rect)
        screen.blit(controls_l3_dashdown, controls_l3_dashdown_rect)
        screen.blit(controls_l3_shoot, controls_l3_shoot_rect)

        for button in [back_button]:
            button.changeColor(controls_MousePos)
            button.update(screen)

        events=pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.checkClick(controls_MousePos):
                    return "options"

        pygame.display.update()
        clock.tick(120)

def volume(): # control volum
    global vol_sfx, vol_mus
    volume_Text = subtitle_font.render("Volume", True, "white")
    volume_rect = volume_Text.get_rect(center=(640, 190))

    vol_sfx_txt = game_font.render("SFX:", True, "white")
    vol_sfx_rect = vol_sfx_txt.get_rect(center=(640, 245))
    vol_sfx1_button = Button(pos=(800, 295), image=button1_surface, text_input="+1", base_clr="white", hover_clr="Green")
    vol_sfx2_button = Button(pos=(480, 295), image=button1_surface, text_input="-1", base_clr="white", hover_clr="Green")
    vol_sfx3_button = Button(pos=(900, 295), image=button1_surface, text_input="+10", base_clr="white", hover_clr="Green")
    vol_sfx4_button = Button(pos=(380, 295), image=button1_surface, text_input="-10", base_clr="white", hover_clr="green")

    vol_mus_txt = game_font.render("BGM:", True, "white")
    vol_mus_rect = vol_mus_txt.get_rect(center=(640, 385))
    vol_mus1_button = Button(pos=(800, 435), image=button1_surface, text_input="+1", base_clr="white", hover_clr="Green")
    vol_mus2_button = Button(pos=(480, 435), image=button1_surface, text_input="-1", base_clr="white", hover_clr="Green")
    vol_mus3_button = Button(pos=(900, 435), image=button1_surface, text_input="+10", base_clr="white", hover_clr="Green")
    vol_mus4_button = Button(pos=(380, 435), image=button1_surface, text_input="-10", base_clr="white", hover_clr="green")

    back_button = Button(pos=(640, 570), image=button_surface, text_input="Back", base_clr="white", hover_clr="Green")
    while True:
        
        screen.blit(bg_surface, (0,0))
        screen.blit(vol_sfx_txt, vol_sfx_rect)
        screen.blit(vol_mus_txt, vol_mus_rect)
        volume_MousePos = pygame.mouse.get_pos()
        volumeBar(vol_sfx, 540, 270)
        volumeBar(vol_mus, 540, 410)
        
        screen.blit(volume_Text, volume_rect)

        for button in [back_button, vol_sfx1_button, vol_sfx2_button, vol_sfx3_button, vol_sfx4_button, vol_mus1_button, vol_mus2_button, vol_mus3_button, vol_mus4_button]:
            button.changeColor(volume_MousePos)
            button.update(screen)

        events=pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.checkClick(volume_MousePos):
                    return "options"

                if vol_sfx1_button.checkClick(volume_MousePos):
                    vol_sfx = round(min(vol_sfx + 0.01, 1.0), 2)
                    channel1.set_volume(vol_sfx)

                if vol_sfx2_button.checkClick(volume_MousePos):
                    vol_sfx = round(max(vol_sfx - 0.01, 0.0), 2)
                    channel1.set_volume(vol_sfx)
                
                if vol_sfx3_button.checkClick(volume_MousePos):
                    vol_sfx = round(min(vol_sfx + 0.1, 1.0), 2)
                    channel1.set_volume(vol_sfx)

                if vol_sfx4_button.checkClick(volume_MousePos):
                    vol_sfx = round(max(vol_sfx - 0.1, 0.0), 2)
                    channel1.set_volume(vol_sfx)

                if vol_mus1_button.checkClick(volume_MousePos):
                    vol_mus = round(min(vol_mus + 0.01, 1.0), 2)
                    pygame.mixer.music.set_volume(vol_mus)

                if vol_mus2_button.checkClick(volume_MousePos):
                    vol_mus = round(max(vol_mus - 0.01, 0.0), 2)
                    pygame.mixer.music.set_volume(vol_mus)
                
                if vol_mus3_button.checkClick(volume_MousePos):
                    vol_mus = round(min(vol_mus + 0.1, 1.0), 2)
                    pygame.mixer.music.set_volume(vol_mus)

                if vol_mus4_button.checkClick(volume_MousePos):
                    vol_mus = round(max(vol_mus - 0.1, 0.0), 2)
                    pygame.mixer.music.set_volume(vol_mus)

        pygame.display.update()
        clock.tick(120)

def main_menu(): # meniul principal
    menu_Text = logo_font.render("AsteroSphere", True, "white")
    menu_rect = menu_Text.get_rect(center=(640, 200))

    play_button = Button(pos=(640, 350), image=button_surface, text_input="Play", base_clr="white", hover_clr="Green")
    options_button = Button(pos=(640, 450), image=button_surface, text_input="Options", base_clr="white", hover_clr="Green")
    quit_button = Button(pos=(640, 550), image=button_surface, text_input="Quit", base_clr="white", hover_clr="Green")
    while True:
        screen.blit(bg_surface, (0,0))

        menu_MousePos = pygame.mouse.get_pos()

        screen.blit(menu_Text, menu_rect)

        for button in [play_button, options_button, quit_button]:
            button.changeColor(menu_MousePos)
            button.update(screen)

        events=pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkClick(menu_MousePos):
                    return "game"
                
                if options_button.checkClick(menu_MousePos):
                    return "options"

                if quit_button.checkClick(menu_MousePos):
                    return "quit"

        pygame.display.update()
        clock.tick(120)

def game_over():
    game_over_Text = subtitle_font.render("Game Over", True, "white")
    game_over_rect = game_over_Text.get_rect(center=(640, 250))

    highscore_Text = game_font.render(f"High Score: {load_high_score("highscore.txt")}", True, (255,255,255))
    highscore_rect = highscore_Text.get_rect(center=(640,310))

    retry_button = Button(pos=(640, 420), image=button_surface, text_input="Retry", base_clr="white", hover_clr="Green")
    back_button = Button(pos=(640, 550), image=button_surface, text_input="Back", base_clr="white", hover_clr="Green")
    while True:
        screen.blit(bg_surface, (0,0))

        game_over_MousePos = pygame.mouse.get_pos()

        screen.blit(game_over_Text, game_over_rect)
        screen.blit(highscore_Text, highscore_rect)

        for button in [back_button, retry_button]:
            button.changeColor(game_over_MousePos)
            button.update(screen)

        events=pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "game"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.checkClick(game_over_MousePos):
                    pygame.mixer.music.rewind()
                    return "main_menu"
                
                if retry_button.checkClick(game_over_MousePos):
                    pygame.mixer.music.rewind()
                    return "game"

        pygame.display.update()
        clock.tick(120)

def main():
    state = "main_menu"
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)
    channel1.set_volume(0.2)
    pygame.time.set_timer(update_score_event, 2000)
    pygame.time.set_timer(SPAWNFUEL, 0)
    pygame.time.set_timer(SPAWNFUEL, 10000)
    pygame.time.set_timer(SPAWNAST, 2000)

    while True:
        if state == "main_menu":
            state = main_menu()
        elif state == "game":
            state = game()
        elif state == "options":
            state = options()
        elif state == "volume":
            state = volume()
        elif state == "controls":
            state = controls() 
        elif state == "game_over":
            state = game_over()
        elif state == "quit":
            pygame.quit()
            exit()

main()
