"""

    DONE: Make collision detection bound to sprites.
    DONE: Make sprites 32x32
    DONE: Make small bullet sprite (easier to see)
    LATERVERSION*TODO: Make background with "doors" and a tile floor
    LATERVERSION*TODO: Set enemy spawning at doors with a random movement speed
    DONE: Make enemies shoot at current player position
    DONE: Add gun sound, bullet hit enemy sound, bullet hit wall sound,
    enemy death sound, player death sound, music
    DONE: Remove any unnecessary code
    DONE: Player health System
    DONE: Life and Health display
    LATERVERSION*TODO: Each enemy's heath hovers over their head on a display.
    >>Critical
    *Optional
    
    Written by John Miller
    W00975996
    
    
    """

import pygame, pygame.mixer
from pygame.locals import *
import sys, os
if sys.platform == 'win32' or sys.platform == 'win64':
    os.environ['SDL_VIDEO_CENTERED'] = '1'
import math
from math import *
import random
from random import randint
pygame.init()

gun1 = pygame.mixer.Sound('gun1.wav')
gun3 = pygame.mixer.Sound('gun3.wav')

hit1 = pygame.mixer.Sound('hit1.wav')
hit2 = pygame.mixer.Sound('hit2.wav')
hit3 = pygame.mixer.Sound('hit3.wav')
hit4 = pygame.mixer.Sound('hit4.wav')
hit5 = pygame.mixer.Sound('hit5.wav')






bg = pygame.image.load("map.png")

Screen = (640,480)
pygame.display.set_caption("Bullet Mania")
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
Surface = pygame.display.set_mode(Screen)


clock = pygame.time.Clock()

pygame.mouse.set_visible(0)


Bullets = []
EBullets = []
BulletSpeed = 20
rof = 0
choice = 0

jack = pygame.image.load("jack3.png")
agent = pygame.image.load("agent2.png")
jackhurt = pygame.image.load("jackwounded.png")
jackwhite = pygame.image.load("jackwhite.png")
agenthurt  = pygame.image.load("agentwounded.png")
bullet = pygame.image.load("bullet.png")
xhair = pygame.image.load("xhair.png")




Level = 1
NewLevelTextBrightness = 255

Font = pygame.font.SysFont(None,16)
Font2 = pygame.font.SysFont(None,64)
Font3 = pygame.font.SysFont(None,32)

Score = 0

class Player ():    #player object, contains its surface, position, angle of rotation, etc
    def __init__(self):
        self.image          = jack
        self.pos           = [Screen[0]/2.0,Screen[1]/2.0]
        self.rect           = pygame.Rect(self.pos[0]-16,self.pos[1]-16,32,32)
        self.speed         = [0, 0]
        self.rot           = 180
        self.scale         = 0.5
        self.lives         = 3
        self.invincibility = 0
        self.health = 10
        self.fire = 0
        self.fired = 0
    def die(self):
        global Level, Score, Bullets
        deathpos = self.pos
        self.pos = [-50,-50]
        self.speed = [0, 0]
        collisionframe = 0
        while collisionframe < 100:
            Move()
            Draw()
            collisionframe += 1
            self.image = jack
        self.lives -= 1
        if self.lives < 0:
            GameOver()
            self.lives = 3
            Bullets = []
            Level = 1
            Score = 0
        NewLevel()
        self.pos = deathpos
    
player1 = Player()

Enemies = []
enemyspeed = 1
class Enemy (): #enemy object, contains its surface, position, angle of rotation, etc
    def __init__(self):
        self.image = agent
        self.pos = [random.randint(0,Screen[0]),random.randint(0,Screen[1])]
        self.speed = [enemyspeed*random.random(),enemyspeed*random.random()]
        self.rect = pygame.Rect(self.pos[0]-16,self.pos[1]-16,32,32)
        self.health = 10
        self.rot = 180
        self.fire = 0
       
    def hit(self):
        self.health -= 4
        
def NewLevel(): # restarts the level
    global Enemies, player1, Bullets, NewLevelTextBrightness
    Bullets = []
    Enemies = []
    player1.speed = [0,0]
    for x in xrange(Level):
        Enemies.append(Enemy())
    if Level % 5 == 0.0:
        player1.lives += 1
    player1.invincibility = 200
    NewLevelTextBrightness = 255
    
    
    
def GetInput2():    #metagame input
    keystate = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT or keystate[K_ESCAPE]:
            pygame.quit(); sys.exit()
    if keystate[K_RETURN]:
        return "new"
    
    
def GameOver(): #game over screen
    angle = 0
    while True:
        todo = GetInput2()
        if todo == "new": return
        Surface.fill((0,0,0))
        color = (100*sin(radians(angle)))+150
        Text = Font2.render("Game Over", True, (int(color),int(color),int(color)))
        Posx = (Screen[0]/2.0)-(Text.get_width()/2.0)
        Posy = (Screen[1]/2.0)-45
        Surface.blit(Text,(Posx,Posy))
        Text2 = Font.render('Bullet Mania!', True, (255,255,255))
        Posx = (Screen[0]/2.0)-(Text2.get_width()/2.0)
        Posy = (Screen[1]/2.0)+10
        Surface.blit(Text2,(Posx,Posy))
        Text3 = Font.render("Press ESC to Exit.", True, (255,255,255))
        Posx = (Screen[0]/2.0)-(Text3.get_width()/2.0)
        Posy = (Screen[1]/2.0)+30
        Surface.blit(Text3,(Posx,Posy))
        Text4 = Font.render("Press ENTER to start new game.", True, (255,255,255))
        Posx = (Screen[0]/2.0)-(Text4.get_width()/2.0)
        Posy = (Screen[1]/2.0)+50
        Surface.blit(Text4,(Posx,Posy))
        Text5 = Font.render("Final Score: "+str(Score), True, (255,255,255))
        Posx = (Screen[0]/2.0)-(Text5.get_width()/2.0)
        Posy = (Screen[1]/2.0)+70
        Surface.blit(Text5,(Posx,Posy))
        pygame.display.flip()
        angle += 0.1
        if angle == 360: angle = 0

def EnemyFire():    #Enemy "AI"
    global EFire
    for a in Enemies:
        if a.fire == 0:
            Pos = [a.pos[0]+(7.5*cos(radians(-a.rot+90))),
               a.pos[1]+(7.5*sin(radians(-a.rot+90)))]
            Speedx = BulletSpeed*cos(radians(-a.rot+90))
            Speedy = BulletSpeed*sin(radians(-a.rot+90))
            Speed = [Speedx,Speedy]
            EBullets.append([Pos, Speed, 0])
            gun3.play()
            rof = random.randint(1,4)
            if rof == 1:
                a.fire = 100
            elif rof == 2:
                a.fire = 80
            elif rof == 3:
                a.fire = 50
            else:
                a.fire = 100
        if a.fire > 0:
            a.fire -= 1

def FireBullet():   #Handles player shooting
        Pos = [player1.pos[0]+(7.5*cos(radians(-player1.rot+90))),
               player1.pos[1]+(7.5*sin(radians(-player1.rot+90)))]
        Speedx = BulletSpeed*cos(radians(-player1.rot+90))
        Speedy = BulletSpeed*sin(radians(-player1.rot+90))
        Speed = [Speedx,Speedy]
        Bullets.append([Pos,Speed,0])
        gun1.play()



def CollisionDetect():  #All the collision data
    global Level, Score, player1, NewLevelTextBrightness
    elasticity = 0.5

    if   player1.pos[0] > Screen[0]: player1.pos[0]=Screen[0];player1.speed[0]*=-elasticity 
    elif player1.pos[0] < 0:         player1.pos[0]=0;player1.speed[0]*=-elasticity
    if   player1.pos[1] > Screen[1]: player1.pos[1]=Screen[1];player1.speed[1]*=-elasticity
    elif player1.pos[1] < 0:         player1.pos[1]=0;player1.speed[1]*=-elasticity

    for a in Enemies:
        if (a.pos[0]-a.health)<2: a.pos[0]=0+a.health+2;a.speed[0]*=-1
        elif (a.pos[0]+a.health)>Screen[0]-2: a.pos[0]=Screen[0]-a.health-2;a.speed[0]*=-1
        if (a.pos[1]-a.health)<2: a.pos[1]=0+a.health+2;a.speed[1]*=-1
        elif (a.pos[1]+a.health)>Screen[1]-2: a.pos[1]=Screen[1]-a.health-2;a.speed[1]*=-1



    for eb in EBullets: #Player1 collision with Enemy bullets
        if player1.rect.collidepoint(eb[0]):
            EBullets.remove(eb)
            if player1.invincibility == 0:
                player1.health -= 5
                hit5.play()
                if player1.health <= 0:
                    player1.die()
                    player1.health = 10
                continue

    for a in Enemies:   #Player1 collision with Enemy
        if a.rect.colliderect(player1.rect):
            if player1.invincibility == 0:
                if player1.invincibility == 0:
                    player1.health -= 5
                if player1.health <= 0:
                    player1.die()
                    player1.health = 10
                return
    
    for a in Enemies:   #Enemy collision with players bullets
        for b in Bullets:
            if a.rect.collidepoint(b[0]):
                Bullets.remove(b)
                Score += 10
                a.hit()
                if a.health <= 4:
                    hit5.play()
                    try:Enemies.remove(a); Score += 100
                    except: pass
                continue
    if Enemies == []:
        Level += 1
        NewLevel()
    if NewLevelTextBrightness > 0:
        NewLevelTextBrightness -= 1
def Move(): #Updates everything's position
    global player1
    player1.pos[0] += player1.speed[0]
    player1.pos[1] += player1.speed[1]
    player1.rect = pygame.Rect(player1.pos[0]-16,player1.pos[1]-16,32,32)
    if player1.invincibility > 0:
        player1.invincibility -= 1
    for b in Bullets:
        b[0][0] += b[1][0]
        b[0][1] += b[1][1]
        b[2] += 1
        if b[2] == 1000:
            Bullets.remove(b);continue
    
    for eb in EBullets:
        eb[0][0] += eb[1][0]
        eb[0][1] += eb[1][1]
        eb[2] += 1
        if eb[2] == 1000:
            EBullets.remove(eb);continue
    
    
    for a in Enemies:
        a.pos[0] += a.speed[0]
        a.pos[1] += a.speed[1]
        a.rect = pygame.Rect(a.pos[0]-16,a.pos[1]-16,32,32)
        
    
def GetInput(): #Get game controls
    global player1
    help = 0
    keystate = pygame.key.get_pressed()
    mousestate = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == QUIT or keystate[K_ESCAPE]:
            pygame.quit(); sys.exit()
    if keystate[K_a]:
        player1.speed[0] = -2.0
    if keystate[K_d]:
        player1.speed[0] = 2.0
    if not (keystate[K_a] or keystate[K_d]):
        player1.speed[0] = 0.0
    if keystate[K_w]:
        player1.speed[1] = -2
    if keystate[K_s]:
        player1.speed[1] = 2
    if not (keystate[K_w] or keystate[K_s]):
        player1.speed[1] = 0.0
    if mousestate[0] and player1.fired == 0:
        FireBullet()
        player1.fired = 1
    if not mousestate[0]:
        player1.fired = 0
        
def PointToMouse(): #Points the player at the mouse location
    global player1
    
    mouse_pos = pygame.mouse.get_pos()
    player_pos = player1.pos
    
    ydiff = mouse_pos[1] - player_pos[1]
    xdiff = mouse_pos[0] - player_pos[0]
    
    angle=math.atan2(-ydiff, xdiff)
    angle=math.degrees(angle)+90
    
    player1.rot = angle

def PointInDir(Enemy):  #Points the enemies in the player's direction
    """makes enemies point in direction of the player"""
    global player1
    
    y1 = Enemy.pos[1]
    x1 = Enemy.pos[0]
    
    y2 = player1.pos[1]
    x2 = player1.pos[0]
    
    vecy = y2-y1
    vecx  = x2-x1
    
    angle=math.atan2(-vecy,vecx)
    angle=math.degrees(angle)+90
    
    Enemy.rot = angle
    
    
def Draw(): #Updates all drawings
    global jack
    Surface.blit(bg, (0,0))
    
    if player1.health < 10:
        player1.image = jackhurt
    
    
    if player1.invincibility > 0:
        if player1.invincibility % 15 > 6:
            player1.image = jackwhite
        else:
            player1.image = jack
            
    Surface.blit(pygame.transform.rotate(player1.image, player1.rot), (player1.pos[0]-16,player1.pos[1]-16))
            
    
    for b in Bullets:
        Surface.set_at((int(b[0][0]),int(b[0][1])),(0,0,0))
        Surface.blit(bullet, (int(b[0][0]),int(b[0][1])))
    
    for eb in EBullets:
        Surface.set_at((int(eb[0][0]),int(eb[0][1])),(0,0,0))
        Surface.blit(bullet, (int(eb[0][0]),int(eb[0][1])))
    
    for a in Enemies:
        PointInDir(a)
        if a.health < 10:
            a.image = agenthurt
        #pygame.draw.rect(Surface, (0,0,255), a.rect)
        Surface.blit(pygame.transform.rotate(a.image, a.rot), (a.pos[0]-16,a.pos[1]-16))
    
    mousex, mousey = pygame.mouse.get_pos()
    Surface.blit(xhair, (mousex-8, mousey-8))
        
    HelpText1 = Font.render("W, A, S, D to move.", True, (0,0,0))
    Surface.blit(HelpText1,(10,10))
    HelpText2 = Font.render("Mouse cursor to aim.", True, (0,0,0))
    Surface.blit(HelpText2,(10,25))
    HelpText3 = Font.render("Left mouse button to shoot.", True, (0,0,0))
    Surface.blit(HelpText3,(10,40))
    LevelText = Font.render("Level: "+str(Level), True, (0,0,0))
    Surface.blit(LevelText,(10,Screen[1]-10-12-15-15))
    LevelText = Font.render("Level: "+str(Level), True, (0,0,0))
    Surface.blit(LevelText,(10,Screen[1]-10-12-15-15))
    LivesText = Font.render("Lives: "+str(player1.lives), True, (0,0,0))
    Surface.blit(LivesText,(10,Screen[1]-10-12-15))
    ScoreText = Font.render("Score: "+str(Score), True, (0,0,0))
    Surface.blit(ScoreText,(10,Screen[1]-10-12))
    HealthText = Font.render("Health: "+str(player1.health), True, (0,0,0))
    Surface.blit(HealthText,(Screen[0]-120,Screen[1]-10-12-15-15))
    EnemiesLeftText = Font.render("Enemies Left: "+str(len(Enemies)), True, (0,0,0))
    Surface.blit(EnemiesLeftText,(Screen[0]-120,Screen[1]-10-12-15))
    FPSText = Font.render("FPS: "+str(round(clock.get_fps(),1)), True, (0,0,0))
    Surface.blit(FPSText,(Screen[0]-120,Screen[1]-10-12))
    
    
    if NewLevelTextBrightness > 0:
        LevelText = Font3.render("Level "+str(Level), True, (NewLevelTextBrightness,NewLevelTextBrightness,NewLevelTextBrightness))
        LevelText.set_alpha(NewLevelTextBrightness)
        LevelTextPos = [(Screen[0]/2.0)-(LevelText.get_width()/2.0),
                        (Screen[1]/2.0)-(LevelText.get_height()/2.0)]
        Surface.blit(LevelText,LevelTextPos)
    pygame.display.flip()
def main():
    NewLevel()
    pygame.mouse.set_pos(Screen)
    while True:
        GetInput()
        EnemyFire()
        Move()
        PointToMouse()
        CollisionDetect()
        Draw()
        clock.tick(100)
if __name__ == '__main__': main()
