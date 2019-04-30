import pygame
import time
import sys
import os


pygame.init()

# music
pygame.mixer.init()
pygame.mixer.music.load(os.path.join('music', 'egyptMusic.ogg'))
pygame.mixer.music.play()


# Global constants

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

ALPHA = (0, 0, 0)

BROWN = (144, 118, 115)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

pygame.display.set_mode()
# images used in the game
img_player = pygame.image.load(os.path.join('images', 'hero.png')).convert()
img_mob1 = pygame.image.load(os.path.join('images', 'mob1.png')).convert()

block_air = pygame.image.load(os.path.join(
    'images', 'block-air.png')).convert()
block_air_left = pygame.image.load(os.path.join(
    'images', 'block-air-left.png')).convert()
block_air_right = pygame.image.load(os.path.join(
    'images', 'block-air-right.png')).convert()

tileGround = pygame.image.load(os.path.join(
    'images', 'tileGround.png')).convert()

obstacle1 = pygame.image.load(os.path.join('images', 'spike_A.png')).convert()

end = pygame.image.load(os.path.join('images', 'end.png')).convert()


score = 0


class Player(pygame.sprite.Sprite):
    """
    This class represents the bar at the bottom that the player controls.
    """

    # -- Methods
    def __init__(self):
        """ Constructor function """

        # Call the parent's constructor
        super().__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        # width = 40
        # height = 60
        #self.image = pygame.Surface([width, height])
        # self.image.fill(RED)

        img_player.convert_alpha()
        img_player.set_colorkey(ALPHA)

        self.images = []
        self.images.append(img_player)

        self.image = self.images[0]

        # Set a referance to the image rect.
        self.rect = self.image.get_rect()

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0

        # List of sprites we can bump against
        self.level = None

        # health bar
        self.health = 100

    def update(self):
        """ Move the player. """
        # Gravity
        self.calc_grav()

        # Move left/right
        self.rect.x += self.change_x

        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(
            self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(
            self, self.level.platform_list, False)
        for block in block_hit_list:

            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            # Stop our vertical movement
            self.change_y = 0

    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .35

        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        """ Called when user hits 'jump' button. """

        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down 1
        # when working with a platform moving down.
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(
            self, self.level.platform_list, False)
        self.rect.y -= 2

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -10

    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -6

    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 6

    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0


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
        distance = 100
        speed = 2

        if self.counter >= 0 and self.counter <= distance:
            self.rect.x += speed
        elif self.counter >= distance and self.counter <= distance*2:
            self.rect.x -= speed
        else:
            self.counter = 0

        self.counter += 1

    def hit(self):
        print('hit')


class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """

    def __init__(self, sprite):  # def __init___(self, width, height)
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this code.
            """
        super().__init__()

        # self.image = pygame.Surface([width, height])
        # self.image.fill(BROWN)

        self.image = sprite

        self.image.convert_alpha()
        self.image.set_colorkey(ALPHA)

        self.rect = self.image.get_rect()


class Level():
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """

    platform_list = None
    enemy_list = None
    background = None

    def __init__(self, player):
        """ Constructor. Pass in a handle to player. Needed for when moving
            platforms collide with the player. """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.player = player

        self.background = None

        # How far this world has been scrolled left/right
        self.world_shift = 0
        self.level_limit = -1000
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.player = player

    # Update everything on this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        self.enemy_list.update()

    def draw(self, screen):
        """ Draw everything on this level. """

        # Draw the background
        # screen.fill(BLUE)
        screen.blit(self.background, (self.world_shift // 3, 0))

        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        for e in self.enemy_list:
            e.move()

    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll
        everything: """

        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the sprite lists and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x

        for enemy in self.enemy_list:
            enemy.rect.x += shift_x

    def enemyLvl(lvl, eloc):
        if lvl == 1:
            enemy = Enemy(eloc[0], eloc[1], 'spr_scarab.png')
            enemy_list = pygame.sprite.Group()
            enemy_list.add(enemy)

        if lvl == 2:
            print("Level " + str(lvl))

        return enemy_list


# Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.background = pygame.image.load(
            os.path.join('images', 'stage2.jpg')).convert()

        self.level_limit = -1500

        # pop the ennemy/mobs
        eloc = []
        eloc = [370, 400]
        self.enemy_list.add(Level.enemyLvl(1, eloc))

        # Array with width, height, x, and y of platform
        level = [
                [block_air_left, 405, 500],
                [block_air, 500, 500],
                [block_air_right, 595, 500],

                [block_air_left, 705, 400],
                [block_air, 800, 400],
                [block_air_right, 895, 400],

                [block_air_left, 1025, 280],
                [block_air, 1120, 280],
                [block_air_right, 1215, 280],

                [block_air_left, 1425, 200],
                [block_air, 1520, 200],
                [block_air_right, 1615, 200],

                [block_air_left, 1825, 350],
                [block_air, 1920, 350],
                [block_air_right, 2015, 350],

                [obstacle1, 1025, 530],
                [obstacle1, 1100, 530],
                [obstacle1, 1175, 530],
                [obstacle1, 1250, 530],
                [obstacle1, 1325, 530],
                [obstacle1, 1400, 530],

                [end, 2200, 530],
                [end, 2200, 402],
                [end, 2200, 274],
                [end, 2200, 146],
                [end, 2200, 18],
                [end, 2200, 0],
        ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            # moving platforms needs to know the player's position at any time
            block.player = self.player
            self.platform_list.add(block)


# Create platforms for the level
class Level_02(Level):
    """ Definition for level 2. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.level_limit = -1000

        # Array with type of platform, and x, y location of the platform.
        level = [[block_air, 450, 570],
                 [block_air, 850, 420],
                 [block_air, 1000, 520],
                 [block_air, 1120, 280],
                 ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.platform_list.add(block)

"""
**************************************************
*              TEXT CLASS                        *
**************************************************
"""
class Text:
    def __init__(self,text,size=30):
        self.font = pygame.font.SysFont(None, size)
        self.text = self.font.render(text, True, GREEN)
        self.textrect = self.text.get_rect()
        

    def draw(self, screen,x,y,mode=0):
        
        if (mode == 1):
            self.textrect.x = x
        else:
            self.textrect.centerx = x
        self.textrect.centery = y
        screen.blit(self.text, self.textrect)


def draw_text(surface, color, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    # the boolean is weither you want anti-aliased or not True = anti-aliased ( smoother )
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


def main():
    """ Main Program """
    pygame.init()

    # Set the height and width of the screen
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    backdrop = pygame.image.load(
        os.path.join('images', 'stage2.jpg')).convert()
    backdropbox = screen.get_rect()

    pygame.display.set_caption("EgyptGame")

    # text
    font = pygame.font.SysFont('Times New Roman, Arial', 70, True, False)
    text = font.render('Score: ' + str(score), 1, BLACK)

    


   

    # Create the player
    player = Player()

    # Create all the levels
    level_list = []
    level_list.append(Level_01(player))
    level_list.append(Level_02(player))

    # Set the current level
    current_level_no = 0
    current_level = level_list[current_level_no]

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    player.rect.x = 340
    player.rect.y = SCREEN_HEIGHT - player.rect.height
    active_sprite_list.add(player)

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

        # Update the player.
        active_sprite_list.update()

        # Update items in the level
        current_level.update()

        # If the player gets near the right side, shift the world left (-x)
        if player.rect.right >= 500:
            diff = player.rect.right - 500
            player.rect.right = 500
            current_level.shift_world(-diff)

        # If the player gets near the left side, shift the world right (+x)
        if player.rect.left <= 120:
            diff = 120 - player.rect.left
            player.rect.left = 120
            current_level.shift_world(diff)

        # If the player gets to the end of the level, go to the next level
        current_position = player.rect.x + current_level.world_shift
        if current_position < current_level.level_limit:
            player.rect.x = 120
            if current_level_no < len(level_list)-1:
                current_level_no += 1
                current_level = level_list[current_level_no]
                player.level = current_level

        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        screen.blit(backdrop, backdropbox)

        screen.blit(text, (100, 100))

        current_level.draw(screen)
        active_sprite_list.draw(screen)

        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

        # Limit to 60 frames per second
        clock.tick(60)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.update()
        pygame.display.flip()

    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()


if __name__ == "__main__":
    main()
