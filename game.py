import pygame
import time
import sys
import os


'''
Objects
'''
# python classes and functions
pygame.display.set_mode()

img_player = pygame.image.load(os.path.join('images', 'hero.png')).convert()


def draw_text(surface, color, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    # the boolean is weither you want anti-aliased or not True = anti-aliased ( smoother )
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


class Player(pygame.sprite.Sprite):
    '''
    Spawn a player
    '''

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0
        self.movey = 0
        self.frame = 0  # count frames

        self.health = 10

        img_player.convert_alpha()
        img_player.set_colorkey(ALPHA)

        self.images = []
        self.images.append(img_player)

        self.image = self.images[0]

        self.rect = self.image.get_rect()

    def control(self, x, y):
        '''
        control player movement
        '''
        self.movex += x
        self.movey += y

    def update(self):
        '''
        Update sprite position
        '''
        # gravity jump
        self.calc_grav()

        # Move left/right
        self.rect.x += self.movex
        # self.rect.y += self.movey

        # collision with enemies
        hit_list = pygame.sprite.spritecollide(self, enemy_list, False)
        for enemy in hit_list:
            if self.health > 0:
                self.health -= 1
            print(self.health)

    def calc_grav(self):
        # Calculate the effect of gravity when jumping
        if self.movey == 0:
            self.movey = 1
        else:
            self.movey += 35

        if self.rect.y >= worldy - self.rect.height + 400 and self.movey >= 400:
            self.movey = 400
            self.rect.y = worldy - self.rect.height + 400

    ''' for animation

    # moving left
        if self.movex < 0:
            self.frame += 1
            if self.frame > 3*ani:
                self.frame = 0
            self.image = self.images[self.frame//ani]

        # moving right
        if self.movex > 0:
            self.frame += 1
            if self.frame > 3*ani:
                self.frame = 0
            self.image = self.images[(self.frame//ani)+4]
    '''


class Enemy(pygame.sprite.Sprite):
    # Spawn an enemy
    def __init__(self, x, y, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(
            'images', img)).convert()

        self.image.convert_alpha()
        self.image.set_colorkey(ALPHA)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.counter = 0

    def move(self):
        # ai movements lol
        distance = 50
        speed = 5

        if self.counter >= 0 and self.counter <= distance:
            self.rect.x += speed
        elif self.counter >= distance and self.counter <= distance*2:
            self.rect.x -= speed
        else:
            self.counter = 0

        self.counter += 1


class Platform(pygame.sprite.Sprite):

    def __init__(self, xloc, yloc, imgw, imgh, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images', img)).convert()
        self.image.convert_alpha()
        self.image.set_colorkey(ALPHA)

        self.rect = self.image.get_rect()
        self.rect.x = xloc
        self.rect.y = yloc


class Level():
    def enemyLvl(lvl, eloc):
        if lvl == 1:
            enemy = Enemy(eloc[0], eloc[1], 'spr_scarab.png')
            enemy_list = pygame.sprite.Group()
            enemy_list.add(enemy)

        if lvl == 2:
            print("Level " + str(lvl))

        return enemy_list

    def ground(lvl, x, y, w, h):
        ground_list = pygame.sprite.Group()
        if lvl == 1:
            ground = Platform(x, y, w, h, 'tileGround.png')
            ground_list.add(ground)

        if lvl == 2:
            print("Level " + str(lvl))

        return ground_list

    def platform(lvl):
        plat_list = pygame.sprite.Group()
        if lvl == 1:
            plat = Platform(200, worldy-400, 285, 67, 'block-air.png')
            plat_list.add(plat)
            plat = Platform(500, worldy-97-320, 197, 54, 'block-air.png')
            plat_list.add(plat)
            plat = Platform(100, 400, 197, 54, 'spike_A.png')
            plat_list.add(plat)

        if lvl == 2:
            print("Level " + str(lvl))

        return plat_list


# run-once code
main = True

BLUE = (25, 25, 200)
BLACK = (23, 23, 23)
WHITE = (254, 254, 254)
ALPHA = (0, 0, 0)
RED = (255, 0, 0)

worldx = 800
worldy = 600

fps = 40  # frame rate
ani = 4  # animation cycles

clock = pygame.time.Clock()
pygame.init()

world = pygame.display.set_mode([worldx, worldy])
backdrop = pygame.image.load(os.path.join('images', 'stage.jpg')).convert()
backdropbox = world.get_rect()


# bring the playerinto the game
player = Player()   # spawn player
player.rect.x = 0   # go to x
player.rect.y = 400   # go to y
player_list = pygame.sprite.Group()
player_list.add(player)
steps = 10  # how many pixels to move/ vitesse

# pop the ennemy/mobs
eloc = []
eloc = [550, 400]
enemy_list = Level.enemyLvl(1, eloc)
ground_list = Level.ground(1, 0, worldy-97, 1080, 97)
plat_list = Level.platform(1)


'''
Main Loop
'''
# game loop
while main:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
            main = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                player.control(-steps, 0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player.control(steps, 0)
            if event.key == pygame.K_UP or event.key == ord('w'):
                print("jump")

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                # to return the sprites momentum back to 0 -> stops
                player.control(steps, 0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player.control(-steps, 0)
            if event.key == ord('q'):
                pygame.quit()
                sys.exit()
                main = False

    world.blit(backdrop, backdropbox)
    player.update()  # to update visually the player position
    player_list.draw(world)  # draw player
    enemy_list.draw(world)
    for e in enemy_list:
        e.move()

    ground_list.draw(world)
    plat_list.draw(world)

    pygame.display.flip()
    clock.tick(fps)
