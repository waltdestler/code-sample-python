from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from direct.fsm import FSM
from pandac.PandaModules import *
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.ForceGroup import ForceGroup
import random

BUNNY_HOP_INIT_VEL = 10
BUNNY_HOP_GRAVITY = -20
BUNNY_HOP_INTERVAL = 1.2
BUNNY_SPEED = 10
BUNNY_TURN = 45

BUNNY_MAD_HOP_INIT_VEL = 10
BUNNY_MAD_HOP_GRAVITY = -40
BUNNY_MAD_HOP_INTERVAL = .55
BUNNY_MAD_SPEED = 20

BUNNY_COLLIDE_FROM_MASK = 0x2
BUNNY_COLLIDE_INTO_MASK = 0

MONSTER_EXPLOSION_RADIUS = 35
PLAYER_EXPLOSION_RADIUS = 25

HOP_SOUND_RANGE = 45

#--------------------------
# A bunny that hops around.
class Bunny(FSM.FSM):
    
    #-----------------
    # Creates a bunny.
    def __init__(self, game, pos, orientation):
        FSM.FSM.__init__(self, "Bunny_" + str(id(self)))
        
        self.__game = game
        self.__hopInterval = None
        self.__madHopInterval = None
        self.__madColorInterval = None
        self.__madProgressInterval = None
        self.__zVel = 0;
        
        # Turn left or right?
        self.__turnLeft = random.randrange(2) == 0
        
        # Create model.
        self.__model = loader.loadModel("models/bvw-f2004--bunny/bunny.bam")
        self.__model.setScale(1)
        self.__model.setPos(pos)
        self.__model.setH(orientation)
        self.__victoryTex = loader.loadTexture("models/bvw-f2004--bunny/bunny_victory.png")
        
        # Setup collision.
        collisionSphere = CollisionSphere(0, 0, 2, 2)
        self.__collider = self.__model.attachNewNode(CollisionNode("Bunny_CollisionSphere_" + str(id(self))))
        self.__collider.node().addSolid(collisionSphere)
        self.__collider.node().setFromCollideMask(BUNNY_COLLIDE_FROM_MASK)
        self.__collider.setCollideMask(BUNNY_COLLIDE_INTO_MASK)
        pusher = CollisionHandlerPusher()
        pusher.addCollider(self.__collider, self.__model)
        self.__game.cTrav.addCollider(self.__collider, pusher)
        
        # Load sounds.
        self.__hopSound = loader.loadSfx("sounds/bunny_hop.wav")
        self.__explosionSound = loader.loadSfx("sounds/bunny_explosion.wav")
        self.__beepSound = loader.loadSfx("sounds/bunny_beep.wav")
        self.__beepSound2 = loader.loadSfx("sounds/bunny_beep.wav")
        
        # Load explode particle effect.
        self.__explodePEffect = ParticleEffect()
        self.__explodePEffect.loadConfig(Filename("particles/smoke.ptf"))
    ##end def
    
    #-------------------
    # Starts this bunny.
    def start(self):
        # Show model.
        self.__model.reparentTo(self.__game.node)
        
        # Setup update task.
        self.__updateTaskName = "Bunny_UpdateTask_" + str(id(self))
        taskMgr.add(self.__updateTask, self.__updateTaskName)
        
        # Start the jump routine after a random amount of time.
        def startHopping():
            self.request("Hopping")
        self.__startHopInterval = Sequence(
            Wait(random.random() * BUNNY_HOP_INTERVAL),
            Func(startHopping))
        self.__startHopInterval.start()
    ##end def
    
    #------------------
    # Stops this bunny.
    def stop(self):
        if self.__startHopInterval != None:
            self.__startHopInterval.finish()
            self.__startHopInterval = None
        if self.__hopInterval != None:
            self.__hopInterval.finish()
            self.__hopInterval = None
        if self.__madHopInterval != None:
            self.__madHopInterval.finish()
            self.__madHopInterval = None
        if self.__madProgressInterval != None:
            self.__madProgressInterval.finish()
            self.__madProgressInterval = None
        if self.__madColorInterval != None:
            self.__madColorInterval.finish()
            self.__madColorInterval = None
        
        taskMgr.remove(self.__updateTaskName)
        
        self.__model.detachNode()
    ##end def
    
    #-----------------------------------
    # Cleans up all intervals and tasks.
    def cleanup(self):
        self.__game.cTrav.removeCollider(self.__collider)
        self.__model.removeNode()
    ##end def
    
    #--------------------
    # Updates this bunny.
    def __updateTask(self, task):
        if self.state == "Hopping":
            # Apply Z velocity to height of bunny.
            if self.__zVel > 0 or self.__model.getZ() > 0:
                self.__model.setZ(self.__model, self.__zVel * globalClock.getDt())
                self.__zVel += BUNNY_HOP_GRAVITY * globalClock.getDt()
                # Also move foreward when jumping.
                self.__model.setY(self.__model, -BUNNY_SPEED * globalClock.getDt())
            else:
                self.__model.setZ(0)
            ##end if
        elif self.state == "MadHopping":
            # Apply Z velocity to height of bunny.
            if self.__zVel > 0 or self.__model.getZ() > 0:
                self.__model.setZ(self.__model, self.__zVel * globalClock.getDt())
                self.__zVel += BUNNY_MAD_HOP_GRAVITY * globalClock.getDt()
                # Also move foreward when jumping
                self.__model.setY(self.__model, -BUNNY_MAD_SPEED * globalClock.getDt())
            else:
                self.__model.setZ(0)
            ##end if
        ##end if
        
        return task.cont
    ##end def
    
    #------------------------
    # Plays the bounce sound.
    def __playHopSound(self):
        # No sound if player is dead.
        if self.__game.player.health > 0:
            bunnyX = self.__model.getX(self.__game.node)
            bunnyY = self.__model.getY(self.__game.node)
            self.__game.playPlayerRelativeSound(
                self.__hopSound,
                bunnyX,
                bunnyY,
                HOP_SOUND_RANGE)
        ##end if
    ##end def
    
    #--------------------------
    # Causes the bunny to hop.
    def __hop(self):
        if self.__model.getZ() <= 0:
            self.__zVel = BUNNY_HOP_INIT_VEL
            if self.__turnLeft:
                self.__model.setH(self.__model, BUNNY_TURN)
            else:
                self.__model.setH(self.__model, -BUNNY_TURN)
            self.__playHopSound()
    ##end def
    
    #------------------------------------
    # Causes the bunny to hop extra-fast.
    def __madHop(self):
        if self.__model.getZ() <= 0:
            self.__zVel = BUNNY_MAD_HOP_INIT_VEL
            self.__playHopSound()
    ##end def
    
    #-------------------------------------------------------------------------
    # Causes the bunny to explode, thus damaging any player or monster nearby.
    def explode(self):
        self.__explodeAgainstMonster()
        self.__explodeAgainstPlayer()
        self.__createExplodeEffect()
        self.stop()
        self.cleanup()
        self.__game.removeBunny(self)
    ##end def
    
    #--------------------------------------------------------------------------------
    # Checks to see if the monster is within explosion radius and, if so, damages it.
    def __explodeAgainstMonster(self):
        monster = self.__game.monster
        monsterX = monster.actor.getX(self.__game.node)
        monsterY = monster.actor.getY(self.__game.node)
        bunnyX = self.__model.getX(self.__game.node)
        bunnyY = self.__model.getY(self.__game.node)
        xDiff = monsterX - bunnyX
        yDiff = monsterY - bunnyY
        distSquared = xDiff*xDiff + yDiff*yDiff
        if distSquared <= MONSTER_EXPLOSION_RADIUS*MONSTER_EXPLOSION_RADIUS:
            print "Exploded against Monster!"
            monster.damage()
        ##end if
    ##end def
    
    #-------------------------------------------------------------------------------
    # Checks to see if the player is within explosion radius and, if so, damages it.
    def __explodeAgainstPlayer(self):
        player = self.__game.player
        playerX = player.actor.getX(self.__game.node)
        playerY = player.actor.getY(self.__game.node)
        bunnyX = self.__model.getX(self.__game.node)
        bunnyY = self.__model.getY(self.__game.node)
        xDiff = playerX - bunnyX
        yDiff = playerY - bunnyY
        distSquared = xDiff*xDiff + yDiff*yDiff
        if distSquared <= PLAYER_EXPLOSION_RADIUS*PLAYER_EXPLOSION_RADIUS:
            print "Exploded against player!"
            player.damage()
    ##end def
    
    #-----------------------------------------------------
    # Creates an explosion effect on top of this bunny.
    def __createExplodeEffect(self):
        sphere = loader.loadModel("models/alice-shapes--sphere/sphere")
        sphere.setScale(.75)
        sphere.setPos(self.__model.getPos(self.__game.node))
        sphere.setZ(sphere, 5)
        sphere.setColorScale(VBase4(1,1,0,1))
        sphere.setTransparency(TransparencyAttrib.MAlpha)
        sphere.reparentTo(self.__game.node)
        
        def destroySphere(): sphere.removeNode()
        Sequence(
            Parallel(
                LerpScaleInterval(sphere, .5, 10),
                LerpColorScaleInterval(sphere, .5, VBase4(1,0,0,0), blendType = "easeIn")),
            Func(destroySphere)).start()
            
        self.__explosionSound.play()
        
        self.__explodePEffect.setPos(Vec3(0,0,.3))
        particleNode = self.__game.node.attachNewNode("Particles")
        particleNode.setPos(self.__model.getPos(self.__game.node))
        particleNode.setScale(15.0)
        self.__explodePEffect.start(particleNode, particleNode)
        def stopParticles(): self.__explodePEffect.softStop()
        Sequence(
            Wait(1),
            Func(stopParticles)).start()
    ##end def
    
    #--------------------------------------
    # Puts this bunny into a victory state.
    def doVictory(self):
        self.__model.setTexture(self.__victoryTex, 1)
    ##end def
    
    #--------------
    # Bunny states.
    def enterHopping(self):
        self.__hopInterval = Parallel(
            Wait(BUNNY_HOP_INTERVAL),
            Func(self.__hop))
        self.__hopInterval.loop()
    ##end def
    def exitHopping(self):
        self.__hopInterval.finish()
        self.__hopInterval = None
    ##end def
    def enterMadHopping(self):
        self.__madHopInterval = Parallel(
            Wait(BUNNY_MAD_HOP_INTERVAL),
            Func(self.__madHop))
        self.__madHopInterval.loop()
    ##end def
    def exitMadHopping(self):
        self.__madHopInterval.finish()
        self.__madColorInterval.finish()
        self.__madProgressInterval.finish()
        self.__madHopInterval = None
        self.__madColorInterval = None
        self.__madProgressInterval = None
    ##end def
    def enterCarried(self):
        
        # Beep and cycle colors.
        def playBeepSound():
            # Sounds can overlap, so don't reuse sound.
            if self.__beepSound.status() != 2:
                self.__beepSound.play()
            else:
                self.__beepSound2.play()
        ##end def
        self.__madColorInterval = Sequence(
            #LerpColorScaleInterval(self.__model, 1.0, VBase4(1,0,0,1)),
            Func(playBeepSound),
            LerpColorScaleInterval(self.__model, 2.0, VBase4(1,1,1,1), VBase4(1,0,0,1)))
        self.__madColorInterval.loop()
        
        # This controls the progress of the self-destruct sequence.
        def progress(rate):
            self.__madColorInterval.pause()
            self.__madColorInterval.setPlayRate(rate)
            self.__madColorInterval.resume()
        ##end def
        def progress1(): progress(1)
        def progress2(): progress(2)
        def progress3(): progress(3)
        def progress4(): progress(4)
        def progress5(): progress(5)
        def progress6(): progress(6)
        def progress7(): progress(7)
        def progress8(): progress(8)
        def progress9(): progress(9)
        def progress10(): progress(10)
        self.__madProgressInterval = Sequence(
            Func(progress1),
            Wait(1.0),
            Func(progress2),
            Wait(1.0),
            Func(progress3),
            Wait(1.0),
            Func(progress4),
            Wait(1.0),
            Func(progress5),
            Wait(1.0),
            Func(progress6),
            Wait(1.0),
            Func(progress7),
            Wait(1.0),
            Func(progress8),
            Wait(1.0),
            Func(progress9),
            Wait(1.0),
            Func(progress10),
            Wait(1.0),
            Func(self.explode))
        self.__madProgressInterval.start()
    ##end def
    def exitCarried(self):
        pass
    ##end def
    
    def getModel(self): return self.__model
    model = property(getModel)
    
#end class