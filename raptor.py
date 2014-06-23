import pygame
from pygame.locals import *
import os
import sys
import time

pygame.init()
screenSize = (1024,768)
pygame.display.set_caption("Raptor")
icon = pygame.Surface((1,1))
icon.set_alpha(0)
pygame.display.set_icon(icon)
screen = pygame.display.set_mode(screenSize)

clock = pygame.time.Clock()

pygame.mouse.set_visible(0)

class Player():
    def __init__(self):
        self.name = "player"
        self.image = pygame.image.load("player.png")
        self.size = [64,64]
        self.pos = [512, 512]
        self.rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
        self.origin = [self.pos[0]+16,self.pos[1]+16]
        self.speed = [0.0,0.0]
        self.grounded = 0

    def draw(self):
        screen.blit(self.image, self.pos)

    def setPos(self, pos):
        self.pos = (x, y)

    def movePos(self, speed):
        self.pos = [self.pos[0]+speed[0], self.pos[1]+speed[1]]
        self.rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
        self.origin = [self.pos[0]+16,self.pos[1]+16]
        
    #move the player
    def move(self):
        gravity = .2
        self.speed[1] += gravity
        self.movePos(self.speed)
        
    #Resolve collisions that have to do with the player
    def collide(self, objects):
        elasticity = 0.5

        #TODO: Figure out how to do collision detection against platforms
        for object in objects:
            if object.solid:
                if object.pos[0] <= self.origin[0] <= object.pos[0]+self.size[0]:
                    pass
                if object.pos[1] <= self.origin[1] <= object.pos[1]+self.size[1]:
                    pass
            
        
class Object:
    def __init__(self, name, image, size, pos, dynamic=False, solid=False):
        self.name = name
        self.image = image
        self.size = size
        self.pos = pos
        self.rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
        self.dynamic = dynamic
        self.solid = solid
        self.speed = 0.0

    def draw(self):
        screen.blit(self.image, self.pos)

    def movePos(self, speed):
        self.pos = (self.pos[0]+speed[0], self.pos[1]+speed[1])
        self.rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
        self.origin = (self.pos[0]+16,self.pos[1]+32)

    def move(self):
        if self.dynamic:
            self.movePos(self.speed)
        else:
            pass

    def collide(self):
        if self.solid:
            pass
        else:
            pass

class Level:
    def __init__(self, name, image, objects):
        self.name = name
        self.map = image
        self.objects = []
        self.objects = objects
        
    def draw(self):
        screen.blit(self.map, (0,0))

        for block in self.objects:
            block.draw()

        player.draw()

    def move(self):
        player.move()

    def collide(self):
        player.collide(self.objects)
        

def getInput(): #Get game controls
    global curLvl, player
    help = 0
    keystate = pygame.key.get_pressed()
    mousestate = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == QUIT or keystate[K_ESCAPE]:
            pygame.quit()
            sys.exit()

    if keystate[K_a]:
        player.speed[0] = -10.0
    if keystate[K_d]:
        player.speed[0] = 10.0
    if not (keystate[K_a] or keystate[K_d]):
        player.speed[0] = 0.0
    if keystate[K_w]:
        pass#player.speed[1] = -10.0
    if keystate[K_s]:
        pass#player.speed[1] = 10.0
    if keystate[K_SPACE]:
        player.speed[1] = -5
    if not (keystate[K_w] or keystate[K_s]):
        pass#player.speed[1] = 0.0
    if mousestate[0]:
        pass
    if not mousestate[0]:
        pass
        

def draw():
    global curLvl, player
    curLvl.draw()
    pygame.display.flip()

def move():
    global curLvl, player
    curLvl.move()
    

def collide():
    global curLvl, player
    curLvl.collide()

curLvl = None
player = Player()


blockImg = pygame.image.load("block.png")
blocks = []
for i in range(32):
    if i % 3 == 0:
        blocks.append(Object("block", blockImg, (32,32), (32*i,screenSize[1]-32), True))

curLvl = Level("main", pygame.image.load("map.png"), blocks)

def main():
    global curLvl, player
    pygame.mouse.set_pos(screenSize)
    player.speed = [0,1]
    while True:
        getInput()
        #TODO: Collide, then move. Check if object's next position would be a collision
        collide()
        move()
        draw()
        clock.tick(100)

if __name__ == '__main__':
    main()
