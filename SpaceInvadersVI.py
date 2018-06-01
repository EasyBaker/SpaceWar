# Imports
import sys
import os
import pygame
import random
from decimal import Decimal

if getattr(sys, 'frozen', False):
    current_path = sys._MEIPASS
else:
    current_path = os.path.dirname(__file__)

# Initialize game engine
pygame.init()

new_stage = True
# Window
WIDTH = 1280
HEIGHT = 1000
SIZE = (WIDTH, HEIGHT)
TITLE = "Space War"
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption(TITLE)


# Timer
clock = pygame.time.Clock()
refresh_rate = 60

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (100, 255, 100)

# Fonts
FONT_SM = pygame.font.Font(current_path + "/fonts/pdark.ttf", 24)
FONT_MD = pygame.font.Font(current_path + "/fonts/pdark.ttf", 32)
FONT_LG = pygame.font.Font(current_path + "/fonts/pdark.ttf", 64)
FONT_XL = pygame.font.Font(current_path + "/fonts/pdark.ttf", 96)

# Images
falcon_img = pygame.image.load(current_path + '/images/falcon.png')
XWing_img = pygame.image.load(current_path + '/images/X-wing.png')
laser_img = pygame.image.load(current_path + '/images/laserRed.png')
mob_img = pygame.image.load(current_path + '/images/Tiefighter.png')
bomb_img = pygame.image.load(current_path + '/images/bombGreen.png')
ufo_img = pygame.image.load(current_path + '/images/ufo.png')
background_img = pygame.image.load(current_path + '/images/background.png')
TieBomber_img = pygame.image.load(current_path + '/images/tie_bomber.png')
VTieFighter_img = pygame.image.load(current_path + '/images/v_tie_fighter.png')

# Sound Effects
EXPLOSION = pygame.mixer.Sound(current_path + '/sounds/Explosion3.wav')
SHOT_sound = pygame.mixer.Sound(current_path + '/sounds/Explosion5.wav')
BombDrop_sound = pygame.mixer.Sound(current_path + '/sounds/Pew-Pew.wav')

songs = [current_path + "/sounds/Cantina_Band.ogg",
         current_path + "/sounds/Parade_Of_The_Ewoks.ogg",
         current_path + "/sounds/Yoda_And_The_Younglings.ogg"]

# Stages
START = 0
PLAYING = 1
END = 2

ship_dead = False
mobs_dead = False
class Shots():
    global shots_taken, shots_hit
    shots_taken = 0

# Game classes
class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.speed = 10
        self.shield = 5

    def move_left(self):
        self.rect.x -= self.speed
        
    def move_right(self):
        self.rect.x += self.speed

    def shoot(self):
        laser = Laser(laser_img)
        laser.rect.centerx = self.rect.centerx
        laser.rect.centery = self.rect.top
        lasers.add(laser)

    def update(self, bombs):
        hit_list = pygame.sprite.spritecollide(self, bombs, True, pygame.sprite.collide_mask)

        for hit in hit_list:
            # play hit sound
            self.shield -= 1

        if self.rect.right < 0:
            self.rect.left = WIDTH      

        elif self.rect.left > WIDTH:
            self.rect.right = 0

        hit_list = pygame.sprite.spritecollide(self, mobs, False, pygame.sprite.collide_mask)
        if len(hit_list) > 0:
            self.shield = 0
            stage = END
            
        if self.shield == 0:
            EXPLOSION.play()
            self.kill()
            stage = END
            
class Laser(pygame.sprite.Sprite):
    
    def __init__(self, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        
        self.speed = 5

    def update(self):
        self.rect.y -= self.speed

        if self.rect.bottom < 0:
            self.kill()

class UFO(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.moving_right = True
        self.speed = 40

    def move(self):
        for u in UFOs:
            if self.moving_right:
                u.rect.x += self.speed
                if u.rect.right >= WIDTH:
                    self.kill()

    def update(self, lasers, player):
        self.move()
        hit_list = pygame.sprite.spritecollide(self, lasers, True, pygame.sprite.collide_mask)

        for hit in hit_list:
            EXPLOSION.play()
            player.score += 100
            self.kill()

    
class Mob(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.shield = 3

    def drop_bomb(self):
        bomb = Bomb(bomb_img)
        bomb.rect.centerx = self.rect.centerx
        bomb.rect.centery = self.rect.bottom
        bombs.add(bomb)
    
    def update(self, lasers, player):
        hit_list = pygame.sprite.spritecollide(self, lasers, True, pygame.sprite.collide_mask)
        
        for hit in hit_list:
            # play hit sound
            self.shield -= 1

            if self.shield == 0:
                EXPLOSION.play()
                player.score += 5
                self.kill()
        
        if self.rect.top > HEIGHT:
            self.kill()

        if len(hit_list) == 0:
            mobs_dead = True
            done = True
            stage = END

class Bomb(pygame.sprite.Sprite):
    
    def __init__(self, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        
        self.speed = 3

    def update(self):
        self.rect.y += self.speed

        if self.rect.bottom < 0:
            self.kill()
    
class Fleet:

    def __init__(self, mobs):
        self.mobs = mobs
        self.moving_right = True
        self.speed = 8
        self.bomb_rate = 60

    def move(self):
        reverse = False
        
        for m in mobs:
            if self.moving_right:
                m.rect.x += self.speed
                if m.rect.right >= WIDTH:
                    reverse = True
            else:
                m.rect.x -= self.speed
                if m.rect.left <=0:
                    reverse = True

        if reverse == True:
            self.moving_right = not self.moving_right
            for m in mobs:
                m.rect.y += 32
            

    def choose_bomber(self):
        rand = random.randrange(0, self.bomb_rate)
        all_mobs = mobs.sprites()
        
        if len(all_mobs) > 0 and rand == 0:
            return random.choice(all_mobs)
        else:
            return None
    
    def update(self):
        self.move()

        bomber = self.choose_bomber()
        if bomber != None:
            bomber.drop_bomb()

def setup():
    global player, lasers, mobs, UFOs, bombs, fleet, stage, ship, high_score, ufo, accuracy, shots_taken

    ufo_position = random.randint(-2000, -200)
    # Make game objects
    ship = Ship(614.4, 853.3333, falcon_img)
    ufo = UFO(ufo_position, 10, VTieFighter_img)
    mob1 = Mob(80, 106.6666, TieBomber_img)
    mob2 = Mob(272, 106.6666, TieBomber_img)
    mob3 = Mob(464, 106.6666, TieBomber_img)
    mob4 = Mob(656, 106.6666, TieBomber_img)
    mob5 = Mob(848, 106.6666, TieBomber_img)
    mob6 = Mob(1040, 106.6666, TieBomber_img)
    mob7 = Mob(128, 298.3333, mob_img)
    mob8 = Mob(288, 298.3333, mob_img)
    mob9 = Mob(448, 298.3333, mob_img)
    mob10 = Mob(608, 293.3333, mob_img)
    mob11 = Mob(768, 293.3333, mob_img)
    mob12 = Mob(928, 293.3333, mob_img)
    mob13= Mob(1088, 293.3333, mob_img)


    with open('high_score.txt') as high_score_file:
        high_score = int(high_score_file.read())
 
    # Make sprite groups
    player = pygame.sprite.GroupSingle()
    player.add(ship)
    player.score = 0

    lasers = pygame.sprite.Group()

    mobs = pygame.sprite.Group()
    mobs.add(mob1, mob2, mob3, mob4, mob5, mob6, mob7, mob8, mob9, mob10, mob11, mob12, mob13)

    UFOs = pygame.sprite.Group()
    UFOs.add(ufo)


    bombs = pygame.sprite.Group()

    fleet = Fleet(mobs)

    stage = START

    
    accuracy = 0

    shots_taken = 0


# Game helper functions
def show_title_screen():
    title_text = FONT_XL.render("Space Wars", 1, WHITE)
    title_text_rect = title_text.get_rect(center=(WIDTH/2, 400))
    screen.blit(title_text, title_text_rect)

def show_subtitle_screen():
    subtitle_text = FONT_MD.render("A Star Wars Story", 1, WHITE)
    subtitle_text_rect = subtitle_text.get_rect(center=(WIDTH/2, 480))
    screen.blit(subtitle_text, subtitle_text_rect)

def show_stats():
    score_text = FONT_MD.render("Score " + str(player.score), 1, WHITE)
    '''high_score_text = FONT_MD.render("High Score " + str(high_score), 1, WHITE)'''
    shield_text = FONT_MD.render("Shield " + str(ship.shield), 1, WHITE)
    screen.blit(score_text, (32, 32))
    '''screen.blit(high_score_text, (32, 64))'''
    screen.blit(shield_text, (32, 96))

def show_accuracy():
    accuracy_text = FONT_MD.render("Accuracy " + str(accuracy) + "%", 1, WHITE)
    accuracy_text_rect = accuracy_text.get_rect(center=(WIDTH/2, 680))
    screen.blit(accuracy_text, accuracy_text_rect)

def show_kills():
    kills_text = FONT_XL.render("Kills " + "13", 1, WHITE)
    kills_text_rect = kills_text.get_rect(center=(WIDTH/2, 60))
    screen.blit(kills_text, kills_text_rect)

def show_restart():
    restart_text = FONT_MD.render("Press space to restart", 1, WHITE)
    restart_text_rect = restart_text.get_rect(center=(WIDTH/2, HEIGHT/2))
    screen.blit(restart_text, restart_text_rect)
    
def choose_music():
    song = random.choice(songs)
    pygame.mixer.music.load(song) 
    pygame.mixer.music.play(2)
             
# Game loop
setup()
choose_music()

done = False

while not done:
    # Event processing (React to key presses, mouse clicks, etc.)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if stage == START:
                if event.key == pygame.K_SPACE or event.key == pygame.K_a or event.key == pygame.K_d:
                    stage = PLAYING
                    choose_music()
            elif stage == PLAYING:
                if event.key == pygame.K_SPACE:
                    SHOT_sound.play()
                    shots_taken += 1
                    ship.shoot()
            elif stage == END:
                if event.key == pygame.K_SPACE:
                    setup()
                    
    if stage == PLAYING:
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_a]:
            ship.move_left()
        elif pressed[pygame.K_d]:
            ship.move_right()
    
    # Game logic (Check for collisions, update points, etc.)
    if stage == PLAYING:
        player.update(bombs)
        lasers.update()   
        mobs.update(lasers, player)
        UFOs.update(lasers, player)
        bombs.update()
        fleet.update()
        if ship.shield == 0:
            new_stage = True
            stage = END
            choose_music()
        elif len(mobs) == 0:
            new_stage = True
            stage = END
            choose_music()
            
        
    # Drawing code (Describe the picture. It isn't actually drawn yet.)
    screen.fill(BLACK)
    screen.blit(background_img, (0,0))
    screen.blit(ufo_img, (200,150))
    lasers.draw(screen)
    player.draw(screen)
    bombs.draw(screen)
    mobs.draw(screen)
    UFOs.draw(screen)
    show_stats()

    if stage == START:
        show_title_screen()
        show_subtitle_screen()

    if stage == END:
        print(shots_taken)
        mobs_left = len(mobs)
        shots_hit = 3 * (13 - len(mobs))
        if shots_taken > 0:
            x = ((shots_hit / shots_taken) * 100)
            accuracy = round(x,2)
        else:
            accuracy = 0
        show_kills()
        show_accuracy()
        show_restart()
        if player.score > high_score:
            writehighscore = open("high_score.txt", "w")
            writehighscore.write(str(player.score))
        
    
    # Update screen (Actually draw the picture in the window.)
    pygame.display.flip()


    # Limit refresh rate of game loop 
    clock.tick(refresh_rate)


# Close window and quit
pygame.quit()
