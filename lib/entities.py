import pygame
from pygame.locals import *
import copy
import time
import anim

Kleft = K_a
Kright = K_d
Kup = K_w
Kdown = K_s
Kjump = K_SPACE
Kcrouch = K_DOWN
Kgrab = K_LSHIFT

NORTH = 'north'
SOUTH = 'south'
EAST = 'east'
WEST = 'west'
AXISX = 'x'
AXISY = 'y'

LEFT = 'left'
RIGHT = 'right'

class Entity(object):
    color = (255, 0, 0)
    
    maxSpeed = 15
    #accel_amt = 1.5
    #airaccel_amt = 1
    accel_amt = 1
    airaccel_amt = .25
    #deaccel_amt = 5
    deaccel_amt = 1
    boost = 10
    
    fallAccel = 1
    jumpMod = 2.5
    jumpAccel = 15
    #jumpAccel = 25
    maxFallSpeed = 20
    
    def __init__(self, level, rectTuple, image=None):
        self.rect = pygame.Rect((rectTuple[0] * level.blockWidth),
                                (rectTuple[1] * level.blockHeight),
                                 rectTuple[2], rectTuple[3])
        self.normalHeight = self.rect.height

        self.cameraRect = copy.copy(self.rect)

        self.animation_speed = 0.030
        
        if type(image) is pygame.Surface:
            self.image = image
        elif type(image) is str:
            try:
                spritesheet = pygame.image.load(image)
            except pygame.error:
                self.image = pygame.Surface((self.rect.width, self.rect.height))
                self.image.fill(self.color) 
        elif image == None:
            self.image = pygame.Surface((self.rect.width, self.rect.height))
            self.image.fill(self.color)

        self.rot = 0
        
        self.accelX = 0
        self.speedX = 0
        self.speedY = 0
        self.jumping = False
        self.onBlock = False
        self.onWall = False
        self.onCeiling = False
        self.jumped = False
        self.wallRan = False
        
    def update(self):
        pass
        
    def load_frames(self, filename):
    
        # Set up spritesheet
        spritesheet = pygame.image.load(filename)
        spritesheetWidth, spritesheetHeight = spritesheet.get_size()
        
        # Make individual tiles
        frames = []
        for frame in range(spritesheetWidth/self.rect.width):
            newFrameRect = pygame.Rect(frame*self.rect.width, 
                                       0, 
                                       self.rect.width, 
                                       spritesheetHeight)
            frames.append(spritesheet.subsurface(newFrameRect))
        
        return frames
        
    def updateAnim(self):
        if time.time() - self.lastFrame >= 0.2:
            self.lastFrame = time.time()
            self.currentFrame += 1
            if self.currentFrame > len(self.frames)-1:
                self.currentFrame = 0
        self.image = self.frames[self.currentFrame]
        
    
        
    def jump(self, speed, onBlock, onWall, wallSide, keys):
        if onBlock and not self.jumped:
            speed[1] -= self.jumpAccel
            self.jumped = True
                
        elif self.wallHanging and keys[Kup] and not self.jumped:
            if keys[Kleft] and self.wallSide == LEFT:
                pass
            elif keys[Kright] and self.wallSide == RIGHT:
                pass
            elif not keys[Kright] and not keys[Kleft]:
                pass
            else:
                speed[1] -= self.jumpAccel
                self.jumped = True
                

                
        # Gravity is decreased while jumping so the player can control
        # the height of his jump.
        if self.wallRunning:
            speed[1] += self.fallAccel*.5
        else:
            speed[1] += self.fallAccel
        
        
        # Simulate terminal velocity
        if speed[1] > self.maxFallSpeed:
            speed[1] = self.maxFallSpeed

        if speed[1] < -self.maxFallSpeed:
            speed[1] = -self.maxFallSpeed
        
        return speed
    
    def fall(self, speed):
        if self.wallHanging:
            if speed > 0:
                speed -= self.deaccel_amt
                if speed < 0:
                    speed = 0
            if speed < 0:
                speed += self.deaccel_amt
                if speed > 0:
                    speed = 0
        elif self.wallRunning:
            speed += self.fallAccel*.5 #- self.jumpMod
        else:
            speed += self.fallAccel
        
        # Simulate terminal velocity
        if speed > self.maxFallSpeed:
            speed = self.maxFallSpeed
        elif speed < -self.maxFallSpeed:
            speed = -self.maxFallSpeed
            
        return speed
        
    def get_shortest_distance(self, rect, speed, axis, level):
        # Check which way the player is moving
        dir = self.check_dir(speed, axis)
        if dir == WEST:
            front = rect.left
        elif dir == EAST:
            front = rect.right
        elif dir == NORTH:
            front = rect.top
        elif dir == SOUTH:
            front = rect.bottom
        
        # Calculate the minimum distance
        linesToCheck = self.check_lines(rect, axis, level)
        if dir:
            minDistance = self.calculate_distance(front, linesToCheck, dir, level)
        else:
            minDistance = 0
        
        # If the minumum distance is shorter than the player's delta,
        # move the player by that distance instead.
        if self.check_collision(speed, minDistance):
            return minDistance
        else:
            return speed
            
    def check_dir(self, speed, axis):
        if axis == AXISX:
            if speed < 0:
                return WEST
            elif speed > 0:
                return EAST
                
        elif axis == AXISY:
            if speed < 0:
                return NORTH
            elif speed > 0:
                return SOUTH
                
    def check_lines(self, rect, axis, level):
        linesToCheck = []
        if axis == AXISX:
            for y in range(level.levelHeight):
                if rect.colliderect((0, 
                                     y*level.blockHeight, 
                                     level.rightEdge, 
                                     level.blockHeight)):
                    linesToCheck.append(y)
                    
        elif axis == AXISY:
            for x in range(level.levelWidth):
                if rect.colliderect((x*level.blockWidth, 
                                     0, 
                                     level.blockWidth, 
                                     level.bottomEdge)):
                    linesToCheck.append(x)
        
        return linesToCheck
    
    def calculate_distance(self, coord, lines, dir, level):
        distances = []
        if dir == WEST or dir == EAST:
            playerTile = self.convert_pixel_to_level(coord, 0, level)[0]
        elif dir == NORTH or dir == SOUTH:
            playerTile = self.convert_pixel_to_level(0, coord, level)[1]
        
        # Which blocks are scanned are dependent on which direction the player is moving in.
        if dir == WEST:
            for line in lines:
                nearestBlock = self.scan_line(line, playerTile, -1, -1, AXISX, level)
                distances.append(abs(nearestBlock * level.blockWidth + level.blockWidth - coord))

        elif dir == EAST:
            for line in lines:
                nearestBlock = self.scan_line(line, playerTile, level.levelWidth, 1, AXISX, level)
                distances.append(abs(nearestBlock * level.blockWidth - coord))
                
        elif dir == NORTH:
            for line in lines:
                nearestBlock = self.scan_line(line, playerTile, -1, -1, AXISY, level)
                distances.append(abs(nearestBlock * level.blockHeight + level.blockHeight - coord))
                
        elif dir == SOUTH:
            for line in lines:
                nearestBlock = self.scan_line(line, playerTile, level.levelHeight, 1, AXISY, level)
                distances.append(abs(nearestBlock * level.blockHeight - coord))
        
        # The function should return the shortest or longest distance 
        # depending on which direction the player was moving in.
        desiredValue = min(distances)
        if dir == WEST or dir == NORTH:
            return -desiredValue
        elif dir == EAST or dir == SOUTH:
            return desiredValue
            
    def convert_pixel_to_level(self, x, y, level):
        for levelX in range(level.levelWidth):
            for levelY in range(level.levelHeight):
                tempRect = pygame.Rect(levelX * level.blockWidth, 
                                       levelY * level.blockHeight, 
                                       level.blockWidth, level.blockHeight)
                if tempRect.collidepoint(x, y):
                    return (levelX, levelY)
    
    def scan_line(self, line, start, end, dir, axis, level):
        if axis == AXISX:
            for tile in range(start, end, dir):
                if level.collisionLayer[line][tile] == level.block:
                    return tile
        elif axis == AXISY:
            for tile in range(start, end, dir):
                if level.collisionLayer[tile][line] == level.block:
                    return tile
        return start
        
    def check_collision(self, speed, minDistance):
        # If minumum X distance is shorter than the player's deltaX,
        # move the player by that distance instead.
        if (speed < 0 and minDistance > speed) or\
           (speed > 0 and minDistance < speed):
           return True
                
        return False
        
    def check_on_block(self, rect, level):
        # is there a better way than checking every block in the level?
        for x in range(level.levelWidth):
            for y in range(level.levelHeight):
                if level.collisionLayer[y][x] == level.blank:
                    continue
                elif level.collisionLayer[y][x] == level.block:
                    tempCheckRect = copy.copy(rect)
                    tempLevelRect = pygame.Rect(x*level.blockWidth, 
                                                y*level.blockHeight, 
                                                level.blockWidth, level.blockHeight)
                    tempCheckRect.bottom += 1
                    if tempLevelRect.colliderect(tempCheckRect):
                        return True
        return False

    def check_on_ceiling(self, rect, level):
        for x in range(level.levelWidth):
            for y in range(level.levelHeight):
                if level.collisionLayer[y][x] == level.blank:
                    continue
                elif level.collisionLayer[y][x] == level.block:
                    tempCheckRect = copy.copy(rect)
                    tempLevelRect = pygame.Rect(x*level.blockWidth, 
                                                y*level.blockHeight, 
                                                level.blockWidth, level.blockHeight)
                    tempCheckRect.top -= 1
                    if tempLevelRect.colliderect(tempCheckRect):
                        return True
        return False

    def check_on_wall(self, rect, level):
        for x in range(level.levelWidth):
            for y in range(level.levelHeight):
                if level.collisionLayer[y][x] == level.blank:
                    continue
                elif level.collisionLayer[y][x] == level.block:
                    tempCheckRect = copy.copy(rect)
                    tempLevelRect = pygame.Rect(x*level.blockWidth, 
                                                y*level.blockHeight, 
                                                level.blockWidth, level.blockHeight)
                    tempCheckRect.left -= 1
                    #tempCheckRect.right += 1
                    if tempLevelRect.colliderect(tempCheckRect):
                        return [True, LEFT]

                    tempCheckRect.left += 1
                    
                    tempCheckRect.right += 1

                    if tempLevelRect.colliderect(tempCheckRect):
                        return [True, RIGHT]

                    tempCheckRect.right -= 1
                    
        return [False, False]

    def check_head_collision(self, level):
        '''
        Checks the current player's original bounding rectangle to see if standing up
        after crouching would cause a collision. If this returns True, the player should not be
        allowed to stand up
        '''
        if not self.crouching:
            return False
        x, y = self.get_coords(level)
        # we need to see check the three blocks above the players head
        levelBlocks = (level.collisionLayer[y-1][x-1],
                       level.collisionLayer[y-1][x],
                       level.collisionLayer[y-1][x+1],)
        
        if all(block == level.blank for block in levelBlocks):
            #all of the blocks above me are blank so there is no chance of collision
            return False
        else: # if level.collisionLayer[y-1][x] == level.block:
            standingRect = copy.deepcopy(self.rect)
            standingRect.top += (self.normalHeight - self.crouchHeight)
            # make bounding rectangles for each of the three blocks above player
            levelRects = [pygame.Rect(i*level.blockWidth,
                                      y*level.blockHeight,
                                      level.blockWidth,
                                      level.blockHeight,)
                              for i in range(x-1,x+2)]
            
            return any(levelBlocks[a] == level.block and
                       levelRects[a].colliderect(standingRect)
                       for a in range(len(levelBlocks)))
        
    def get_coords(self, level):
        return self.convert_pixel_to_level(self.rect.centerx, self.rect.centery, level)


    def get_accelY(self, keys):
        accelY = 0
        if self.onBlock and self.jumping and not self.jumped:
            accelY = self.jumpAccel
            self.jumped = True
        elif self.onWall and self.jumping and not self.jumped:
            if self.wallSide == LEFT and keys[Kleft]:
                pass
            elif self.wallSide == RIGHT and keys[Kright]:
                pass
            elif keys[Kup]:
                accelY = self.jumpAccel
                self.jumped = True
            elif keys[Kdown]:
                accelY = -self.jumpAccel
                self.jumped = True
            else:
                pass
        elif self.onCeiling and self.jumping and not self.jumped:
            if keys[Kdown]:
                accelY = -self.jumpAccel
                self.jumped = True
            else:
                accelY = -self.fallAccel
                self.jumped = True

        return accelY

    def get_speedY(self, keys, accelY, speedY):
        
        speedY -= accelY
        
        if self.onBlock:
            speedY += 0
        elif self.onWall:
            speedY += self.fallAccel*.25
        elif self.onCeiling:
            speedY += 0
        else:
            speedY += self.fallAccel

        if speedY > self.maxFallSpeed:
            speedY = self.maxFallSpeed
        elif speedY < -self.maxFallSpeed:
            speedY = -self.maxFallSpeed
            
        return speedY

    def get_accelX(self, keys):
        accelX = 0
        if self.onBlock:
            if self.jumping and not self.jumped:
                accelX = (keys[Kright] - keys[Kleft]) * self.boost
            else:
                accelX = (keys[Kright] - keys[Kleft]) * self.accel_amt
        elif self.onWall:
            if self.jumping and not self.jumped:
                if self.wallSide == LEFT and keys[Kright]:
                    accelX = keys[Kright] * self.boost
                elif self.wallSide == RIGHT and keys[Kleft]:
                    accelX = -keys[Kleft] * self.boost
                elif (keys[Kright] - keys[Kleft]) == 0:
                    if self.wallSide == LEFT:
                        accelX = self.boost*.5
                    elif self.wallSide == RIGHT:
                        accelX = -self.boost*.5
        elif self.onCeiling:
            if self.jumping and not self.jumped:
                if keys[Kright]:
                    accelX = keys[Kright] * self.boost
                elif keys[Kleft]:
                    accelX = -keys[Kleft] * self.boost
                elif (keys[Kright] - keys[Kleft]) == 0:
                    accelX = 0
            else:
                accelX = (keys[Kright] - keys[Kleft]) * self.accel_amt
                
                
        else:
            accelX = (keys[Kright] - keys[Kleft]) * self.airaccel_amt

        return accelX

    #TODO: Get ceiling running working
    def get_speedX(self, keys, accel, speed):
        if accel != 0:
            if ((speed < 0) and (accel > 0)):
                speed += accel
            elif ((speed > 0) and (accel < 0)):
                speed += accel
            else:
                if not self.onCeiling:
                    speed += accel
        else:
            if self.onBlock:
                if speed > 0:
                    speed -= self.deaccel_amt
                    if speed < 0:
                        speed = 0
                elif speed < 0:
                    speed += self.deaccel_amt
                    if speed > 0:
                        speed = 0
            elif self.onCeiling:
                if speed > 0:
                    speed -= self.deaccel_amt*.1
                    if speed < 0:
                        speed = 0
                elif speed < 0:
                    speed += self.deaccel_amt*.1
                    if speed > 0:
                        speed = 0
                        
        

        if speed > self.maxSpeed:
            #speed -= deaccel
            speed = self.maxSpeed
        if speed < -self.maxSpeed:
            #speed += deaccel
            speed = -self.maxSpeed

        return speed

        
        
        
class Player(Entity):
    crouching = False
    crouchHeight = 70
    crouchMaxSpeed = 6
    
    
    def __init__(self, level, rectTuple, image=None):
        super(Player, self).__init__(level, rectTuple, image)
        try:
            self.runAnim = anim.Animation("lib\\player.png", self.rect.width, self.animation_speed)
            self.crouchAnim = anim.Animation("lib\\crouching.png", self.rect.width, 0.07)
            self.idle = anim.Animation("lib\\idle.png", self.rect.width, 0)
            self.idleCrouching = anim.Animation("lib\\idle_crouching.png", self.rect.width, 0)
            self.hasAnim = True
        except pygame.error:
            self.hasAnim = False
        self.defMaxSpeed = self.maxSpeed
    
    def update(self, keys, level):
        # disable midair crouching by only allowing crouching while on the ground
        # similar to how the mario series handles this

        #get if the player is on a block, the ceiling, or a wall, and the wall side
        self.onBlock = self.check_on_block(self.rect, level)
        self.onCeiling = self.check_on_ceiling(self.rect, level)
        [self.onWall, self.wallSide] = self.check_on_wall(self.rect, level)
        
        # Crouch the player if needed
        if keys[Kcrouch] and not self.crouching and self.onBlock:
            self.crouching = True
            self.maxSpeed = self.crouchMaxSpeed
            self.rect.height = self.crouchHeight
            self.rect.bottom += self.normalHeight - self.crouchHeight
            
        elif not keys[Kcrouch] and self.crouching and self.onBlock:
            # check to see if you can uncrouch here
            if not self.check_head_collision(level):
                self.crouching = False
                self.maxSpeed = self.defMaxSpeed
                self.rect.height = self.normalHeight
                self.rect.bottom -= self.normalHeight - self.crouchHeight

        # Update the player's image to the new rect size
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill(self.color)

        # Calculate movement on Y-axis
        #check if the player is jumping
        self.jumping = keys[Kjump]

        if not self.jumping:
            self.jumped = 0
        
        # Calculate movement on X-axis
        self.accelX = self.get_accelX(keys)
        self.speedX = self.get_speedX(keys, self.accelX, self.speedX)

        # Calculate movement on Y-axis
        self.accelY = self.get_accelY(keys)
        self.speedY = self.get_speedY(keys, self.accelY, self.speedY)
        
        # Check if player needs to be stopped at an obstacle:
        # For X-axis
        try:
            self.minXDistance = self.get_shortest_distance(self.rect, self.speedX, AXISX, level)
        except (TypeError, IndexError, ValueError):
            self.minXDistance = self.speedX
        if abs(self.minXDistance) < abs(self.speedX):
            self.speedX = 0
        
        self.rect.left += self.minXDistance
        
        # For Y-axis
        try:
            self.minYDistance = self.get_shortest_distance(self.rect, self.speedY, AXISY, level)
        except (TypeError, IndexError, ValueError):
            self.minYDistance = self.speedY
        if abs(self.minYDistance) < abs(self.speedY):
            self.speedY = 0
            
        self.rect.top  += self.minYDistance
        
        # Update camera rect 
        self.cameraRect.bottom = self.rect.bottom
        self.cameraRect.left = self.rect.left
        
        # Update frames of player if possible
        if self.hasAnim:
            if self.speedX > 0:
                if self.runAnim.reversed or self.crouchAnim.reversed:
                    self.runAnim.reverse()
                    self.crouchAnim.reverse()
                    self.idle.reverse()
                    self.idleCrouching.reverse()
                self.runAnim.update()
                self.image = self.runAnim.image
            elif self.speedX < 0:
                if not self.runAnim.reversed or not self.crouchAnim.reversed:
                    self.runAnim.reverse()
                    self.crouchAnim.reverse()
                    self.idle.reverse()
                    self.idleCrouching.reverse()

            if self.onWall and not self.onBlock:
                if self.wallSide == RIGHT:
                    self.rot = 90
                elif self.wallSide == LEFT:
                    self.rot = -90
            else:
                self.rot = 0
                    
            if not self.crouching:        
                self.runAnim.update()
                self.image = self.runAnim.image
            elif self.crouching:
                self.crouchAnim.update()
                self.image = self.crouchAnim.image
                
            if self.speedY != 0 or (self.jumping and not self.jumped):
                if self.onWall:
                    if self.speedY < 0:
                        if self.runAnim.reversed or self.crouchAnim.reversed:
                            self.runAnim.reverse()
                            self.crouchAnim.reverse()
                            self.idle.reverse()
                            self.idleCrouching.reverse()
                        self.runAnim.update()
                        self.image = self.runAnim.image
                    elif self.speedY > 0:
                        if not self.runAnim.reversed or not self.crouchAnim.reversed:
                            self.runAnim.reverse()
                            self.crouchAnim.reverse()
                            self.idle.reverse()
                            self.idleCrouching.reverse()
                            
                    if self.wallSide == LEFT:
                        self.image = pygame.transform.flip(self.image, True, False)
                else:
                    self.image = self.runAnim.frames[4]
            elif self.speedX == 0 and self.speedY == 0:
                if not self.crouching:
                    self.image = self.idle.frames[0]
                elif self.crouching:
                    self.image = self.idleCrouching.frames[0]
                self.runAnim.reset()
                self.crouchAnim.reset()
