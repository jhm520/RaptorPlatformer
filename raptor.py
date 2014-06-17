import pygame
from pygame.locals import *
import os
import sys
import time

pygame.init()
pygame.display.set_caption("Raptor")
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
Surface = pygame.display.set_mode((640,480))

clock = pygame.time.Clock()

pygame.mouse.set_visible(0)



class Level:
    def __init__(self, name, lvlMap):
        self.name = name
        self.map = lvlMap

    def draw(self):
        Surface.blit(self.map, (0,0))
        pygame.display.flip()

    def move(self):
        pass
        

def getInput(): #Get game controls
    help = 0
    keystate = pygame.key.get_pressed()
    mousestate = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == QUIT or keystate[K_ESCAPE]:
            pygame.quit()
            sys.exit()

def draw():
    global curLvl
    curLvl.draw()

def move():
    global curLvl
    curLvl.move()

curLvl = Level("main", pygame.image.load("map.png"))

def main():
    pygame.mouse.set_pos((640,480))

    while True:
        getInput()
        draw()
        move()
        clock.tick(100)

if __name__ == '__main__':
    main()
