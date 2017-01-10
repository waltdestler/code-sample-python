from direct.showbase import DirectObject
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import *

from util import WalkAnimFSM

PLAYER_SPEED = 50
PLAYER_REVERSE_RATIO = .5
PLAYER_TURN_SPEED = 100
WALK_ANIM_FACTOR = .03
TURN_ANIM_FACTOR = .005
PLAYER_HEAVEN_SPEED = .03

PLAYER_COLLIDE_FROM_MASK = 0x1
PLAYER_COLLIDE_INTO_MASK = 0

BUNNY_NAB_DIST = 3

PLAYER_MAX_HEALTH = 3

INVINCIBLE_DURATION = 5.0

#-----------------------------------------------------
# Manages the player and the actor associated with it.
class Player(DirectObject.DirectObject):
    
    #--------------------
    # Creates the player.
    def __init__(self, game, input, pos):
        self.__game = game
        self.__input = input
        self.bunny = None
        self.__health = PLAYER_MAX_HEALTH
        self.__invincible = False
        self.__ghost = False
        
        # Create the hearts.
        self.__hearts = []
        heartMaker = CardMaker("HeartMaker")
        heartTex = loader.loadTexture("textures/heart.png")
        HEART_WIDTH = .2
        HEART_HEIGHT = .2
        HEART_BOTTOM = -1
        HEART_TOP = HEART_BOTTOM + HEART_HEIGHT
        TOTAL_HEART_WIDTH = HEART_WIDTH * PLAYER_MAX_HEALTH
        for i in range(0, PLAYER_MAX_HEALTH):
            heartLeft = -TOTAL_HEART_WIDTH/2 + i*HEART_WIDTH
            heartRight = heartLeft + HEART_WIDTH
            heartMaker.setFrame(heartLeft, heartRight, HEART_BOTTOM, HEART_TOP)
            heart = NodePath(heartMaker.generate())
            heart.setTexture(heartTex)
            heart.setTransparency(TransparencyAttrib.MAlpha)
            self.__hearts.append(heart)
        ##end for
        
        # Setup actor.
        self.__actor = Actor.Actor("models/bvw-f2004--eve/eve.bam",
            {"walk":"models/bvw-f2004--eve/eve-run.bam",
             "jump":"models/bvw-f2004--eve/eve-jump.bam"})
        self.__actor.setScale(1)
        self.__actor.setPos(pos)
        self.__actor.setBlend(frameBlend = True)
        self.__actor.setTransparency(TransparencyAttrib.MAlpha)
        
        # Setup walking animation.
        walkRate = PLAYER_SPEED * WALK_ANIM_FACTOR
        reverseWalkRate = walkRate * PLAYER_REVERSE_RATIO
        turnWalkRate = PLAYER_TURN_SPEED * TURN_ANIM_FACTOR
        self.__animFSM = WalkAnimFSM(self.__actor, walkRate, reverseWalkRate, turnWalkRate)
        
        # Setup collision.
        collisionSphere = CollisionSphere(0, 0, 2.3, 2)
        self.__collider = self.__actor.attachNewNode(CollisionNode("Player_CollisionSphere_" + str(id(self))))
        self.__collider.node().addSolid(collisionSphere)
        self.__collider.node().setFromCollideMask(PLAYER_COLLIDE_FROM_MASK)
        self.__collider.setCollideMask(PLAYER_COLLIDE_INTO_MASK)
        pusher = CollisionHandlerPusher()
        pusher.addCollider(self.__collider, self.__actor)
        pusher.addInPattern("player-into-%in")
        self.__game.cTrav.addCollider(self.__collider, pusher)
        
        # Load sounds.
        self.__hurtSound = loader.loadSfx("sounds/player_hurt.wav")
        self.__deathSound = loader.loadSfx("sounds/player_death.wav")
        self.__heartbeatSound = loader.loadSfx("sounds/player_heartbeat.wav")
    ##end def
    
    #-------------------
    # Starts the player.
    def start(self):
        # Show hearts.
        for heart in self.__hearts:
            heart.reparentTo(self.__game.node2d)
            
        # Show actor.
        self.__actor.reparentTo(self.__game.node)

        # Setup tasks.
        self.__updateTaskName = "Player_UpdateTask_" + str(id(self))
        taskMgr.add(self.__updateTask, self.__updateTaskName)
        
        # Set initial animation.
        self.__animFSM.request("Still")
        
        # Listen for input events.
        self.accept("do_action", self.__doAction)
        def onPlayerIntoMonster(entry): self.damage()
        self.accept("player-into-monster", onPlayerIntoMonster)
    ##end def
    
    #------------------
    # Stops the player.
    def stop(self):
        self.ignoreAll()
        self.__animFSM.request("Still")
        taskMgr.remove(self.__updateTaskName)
        self.__actor.detachNode()
        for heart in self.__hearts:
            heart.detachNode()
    ##end def
    
    #---------------------------------------------
    # Cleans up all resources used by this player.
    def cleanup(self):
        self.__game.cTrav.removeCollider(self.__collider)
        self.__actor.cleanup()
        self.__actor.removeNode()
        for heart in self.__hearts:
            heart.removeNode()
    ##end def
    
    #------------------------------------------
    # Moves the player according to user input.
    def __updateTask(self, task):
        shouldAnimStill = True
        
        if self.bunny != None:
            self.bunny.model.setX(0)
            self.bunny.model.setY(0)
        ##end if
        
        # Are we alive?
        if self.__health > 0:
            base.camera.setFluidPos(self.__game.cameraPos)
            
            if self.__input.moveForeward:
                self.__actor.setFluidY(self.__actor, -PLAYER_SPEED * globalClock.getDt())
                self.__animFSM.request("Walk")
                shouldAnimStill = False
            elif self.__input.moveReverse:
                self.__actor.setFluidY(self.__actor, PLAYER_SPEED * PLAYER_REVERSE_RATIO * globalClock.getDt())
                self.__animFSM.request("ReverseWalk")
                shouldAnimStill = False
            if self.__input.turnLeft:
                self.__actor.setH(self.__actor, PLAYER_TURN_SPEED * globalClock.getDt())
                if shouldAnimStill:
                    self.__animFSM.request("TurnWalk")
                    shouldAnimStill = False
            elif self.__input.turnRight:
                self.__actor.setH(self.__actor, -PLAYER_TURN_SPEED * globalClock.getDt())
                if shouldAnimStill:
                    self.__animFSM.request("TurnWalk")
                    shouldAnimStill = False
            
            # Try to catch a bunny if jumping.
            if self.bunny == None and self.__actor.getCurrentAnim() == "jump":
                # Search all bunnies and pick up one if found.
                for bunny in self.__game.bunnies:
                    if bunny.state != "Hopping": continue
                    bunnyX = bunny.model.getX()
                    bunnyY = bunny.model.getY()
                    playerX = self.__actor.getX()
                    playerY = self.__actor.getY()
                    xDiff = bunnyX - playerX
                    yDiff = bunnyY - playerY
                    distSquared = xDiff*xDiff + yDiff*yDiff
                    if distSquared <= BUNNY_NAB_DIST*BUNNY_NAB_DIST:
                        self.bunny = bunny
                        bunny.model.reparentTo(self.__actor)
                        bunny.model.setPos(0, 0, 3.5)
                        bunny.model.setH(self.__actor, 0)
                        bunny.request("Carried")
                        break
                    ##end if
                ##end for
            ##end if
        elif self.__ghost:
            # Since we're dead, need to rise up to heaven.
            self.__actor.setY(self.__actor, -PLAYER_HEAVEN_SPEED)
            
            # Make camera look at ghost, but no until ghost has risen high enough.
            oldHpr = base.camera.getHpr()
            base.camera.lookAt(self.__actor)
            if base.camera.getP() < 0:
                base.camera.setHpr(oldHpr)
        ##end if
        
        if shouldAnimStill:
            self.__animFSM.request("Still")
        return task.cont
    ##end def
    
    # Performs a context-sensitive action when the user presses the action key.
    def __doAction(self):
        # Are we not carrying a bunny?
        if self.bunny == None and self.__health > 0 and self.__actor.getCurrentAnim() != "jump":
            self.__actor.play("jump")
        # If we're carrying a bunny, then release it.
        elif self.bunny != None:
            bunny = self.bunny
            self.bunny = None
            bunny.model.wrtReparentTo(self.__game.node)
            bunny.request("MadHopping")
        ##end if
    ##end def
    
    #-------------------------
    # Hides all of the hearts.
    # Also stops any heartbeat sound effect.
    def hideHearts(self):
        self.__heartbeatSound.stop()
        for heart in self.__hearts:
            heart.hide()
    ##end def
    
    #-------------------------
    # Takes a point of damage.
    def damage(self):
        if not self.__invincible and self.__health > 0:
            # If more than 1 health left, take a point of damage.
            if self.__health > 1:
                self.__health -= 1
                self.__hearts[self.__health].hide()
                LerpColorScaleInterval(self.__actor, .5, VBase4(1,1,1,.3), VBase4(1,0,0,1)).start()
                self.__hurtSound.play()
                
                # Start heartbeat if almost dead.
                if self.__health == 1:
                    self.__heartbeatSound.setLoop(True)
                    self.__heartbeatSound.play()
                
                # Make momentarily invincible.
                self.__invincible = True
                def makeNotInvincible(): self.__invincible = False
                Sequence(
                    Wait(INVINCIBLE_DURATION),
                    Func(makeNotInvincible),
                    LerpColorScaleInterval(self.__actor, .5, VBase4(1,1,1,1))
                    ).start()
            # Otherwise, die and lose the game.
            else:
                self.__health = 0
                self.__hearts[0].hide()
                LerpColorScaleInterval(self.__actor, .5, VBase4(1,1,1,1), VBase4(1,0,0,1)).start()
                self.__game.stopMusic()
                self.__game.monster.stopAttackSequence()
                self.__deathSound.play()
                base.camera.wrtReparentTo(self.__game.node)
                self.__collider.node().setFromCollideMask(0)
                def doDefeat():
                    self.__game.doDefeat()
                    
                    # Make ghost
                    self.__ghost = True
                    self.__actor.setColorScale(VBase4(0,0,1,.3))
                    
                    # Spawn body.
                    body = Actor.Actor("models/bvw-f2004--eve/eve")
                    body.setScale(1)
                    body.setPos(self.__actor.getPos())
                    body.setHpr(self.__actor.getHpr())
                    body.reparentTo(self.__game.node)
                ##end def
                Sequence(
                    LerpFunc(self.__actor.setP, toData=-90.0, duration=.51),
                    Func(doDefeat)).start()
            ##end if
        ##end if
    ##end def
    
    def getActor(self): return self.__actor
    actor = property(getActor)
    
    def getPointLightNP(self): return self.__plnp
    pointLightNP = property(getPointLightNP)
    
    def getHealth(self): return self.__health
    health = property(getHealth)
    
##end class
