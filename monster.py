from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import *

from util import *

INIT_MONSTER_SPEED = 1
MONSTER_SPEED_INCREMENT = .7
MONSTER_ROT_SPEED = 25

MONSTER_COLLIDE_INTO_MASK = 0x3

MONSTER_MAX_HEALTH = 5

MONSTER_SOUND_RANGE = 100

#-----------------------------
# A monster that roams around.
class Monster:
    
    #-------------------
    # Creates a monster.
    def __init__(self, game, pos):
        self.__game = game
        self.__health = MONSTER_MAX_HEALTH
        self.__speed = INIT_MONSTER_SPEED
        self.__startPos = pos
        self.__go = False
        
        # Load boss bars.
        bbarMaker = CardMaker("BossbarMaker")
        BBAR_WIDTH = 1.5
        BBAR_HEIGHT = .12
        BBAR_LEFT = -BBAR_WIDTH / 2
        BBAR_RIGHT = BBAR_LEFT + BBAR_WIDTH
        BBAR_TOP = 1
        BBAR_BOTTOM = BBAR_TOP - BBAR_HEIGHT
        def makeBossBar(texfile):
            bbarMaker.setFrame(BBAR_LEFT, BBAR_RIGHT, BBAR_BOTTOM, BBAR_TOP)
            bbar = NodePath(bbarMaker.generate())
            bbarTex = loader.loadTexture(texfile)
            bbar.setTexture(bbarTex)
            bbar.setTransparency(TransparencyAttrib.MAlpha)
            bbar.hide()
            return bbar
        ##end def
        self.__bossbars = []
        self.__bossbars.append(makeBossBar("textures/bossbar00.png"))
        self.__bossbars.append(makeBossBar("textures/bossbar20.png"))
        self.__bossbars.append(makeBossBar("textures/bossbar40.png"))
        self.__bossbars.append(makeBossBar("textures/bossbar60.png"))
        self.__bossbars.append(makeBossBar("textures/bossbar80.png"))
        self.__bossbars.append(makeBossBar("textures/bossbar100.png"))
        self.__bossbars[-1].show()
        
        # Create actor.
        self.__actor = Actor.Actor("models/bvw-f2004--monster/monster1.bam",
            {"pincer-attack-left":"models/bvw-f2004--monster/monster1-pincer-attack-left.bam",
             "pincer-attack-right":"models/bvw-f2004--monster/monster1-pincer-attack-right.bam",
             "tentacle-attack":"models/bvw-f2004--monster/monster1-tentacle-attack.bam"})
        self.__actor.setScale(7.5)
        recursiveSetTag(self.__actor, "monster", "")
        recursiveSetName(self.__actor, "monster")
        self.__actor.setPos(pos)
        self.__actor.setZ(100)
        self.__actor.setBlend(frameBlend = True)
        self.__actor.setCollideMask(MONSTER_COLLIDE_INTO_MASK)
        
        # Load textures for displaying damage.
        self.__hurt0 = loader.loadTexture("models/bvw-f2004--monster/monster1.png")
        self.__hurt1 = loader.loadTexture("models/bvw-f2004--monster/hurt1.png")
        self.__hurt2 = loader.loadTexture("models/bvw-f2004--monster/hurt2.png")
        self.__hurt3 = loader.loadTexture("models/bvw-f2004--monster/hurt3.png")
        self.__hurt4 = loader.loadTexture("models/bvw-f2004--monster/hurt4.png")
        
        # Load sounds.
        self.__hurtSound = loader.loadSfx("sounds/monster_hurt.wav")
        self.__deathSound = loader.loadSfx("sounds/monster_death.wav")
        self.__fallSound = loader.loadSfx("sounds/monster_fall.wav")
        self.__mouthSound = loader.loadSfx("sounds/monster_mouth.wav")
        self.__pincer1Sound = loader.loadSfx("sounds/monster_pincer1.wav")
        self.__pincer2Sound = loader.loadSfx("sounds/monster_pincer2.wav")
    ##end def
    
    #--------------------
    # Starts the monster.
    def start(self):
        # Show boss bars.
        for bbar in self.__bossbars:
            bbar.reparentTo(self.__game.node2d)
            bbar.hide()
        ##end for
        bossbarPos = self.__bossbars[self.__health].getPos()
        self.__bossbars[self.__health].setZ(.2)
        self.__bossbars[self.__health].show()
        
        # Show actor.
        self.__actor.reparentTo(self.__game.node)
        
        # Animate attack sequence.
        def playRelativeSound(sound):
            self.__game.playPlayerRelativeSound(
                sound,
                self.__actor.getX(),
                self.__actor.getY(),
                MONSTER_SOUND_RANGE)
        ##end def
        def playMouthSound(): playRelativeSound(self.__mouthSound)
        def playPincer1Sound(): playRelativeSound(self.__pincer1Sound)
        def playPincer2Sound(): playRelativeSound(self.__pincer2Sound)
        self.__attackInterval = Sequence(
            Func(playPincer1Sound),
            self.__actor.actorInterval("pincer-attack-left"),
            Func(playPincer2Sound),
            self.__actor.actorInterval("pincer-attack-right"),
            Func(playMouthSound),
            self.__actor.actorInterval("tentacle-attack"))
        self.__attackInterval.loop()
        
        # Setup update task.
        self.__updateTaskName = "Monster_UpdateTask_" + str(id(self))
        taskMgr.add(self.__updateTask, self.__updateTaskName)
        
        # Fall in from sky.
        cameraPos = base.camera.getPos()
        def playFallSound(): self.__fallSound.play()
        def doGo():
            self.__go = True
            self.__game.playMusic()
        ##end def
        Sequence(
            Wait(.5),
            Func(playFallSound),
            Wait(.6),
            LerpPosInterval(self.__actor, 1.0, self.__startPos),
            Func(doGo),
            Parallel(
                Sequence(
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,1)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,-1)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,.9)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,-.9)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,.8)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,-.8)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,.7)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,-.7)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,.6)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,-.6)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,.5)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,-.5)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,.4)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,-.4)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,.3)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,-.3)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,.2)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,-.2)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,.1)),
                    LerpPosInterval(base.camera, .1, cameraPos + Vec3(0,0,-.1)),
                    LerpPosInterval(base.camera, .1, cameraPos)),
                LerpPosInterval(self.__bossbars[self.__health], .5, bossbarPos))
            ).start()
    ##end def
    
    #--------------------
    # Stops this monster.
    def stop(self):
        taskMgr.remove(self.__updateTaskName)
        self.__attackInterval.finish()
        self.__actor.detachNode()
        for bbar in self.__bossbars:
            bbar.detachNode()
    ##end def
    
    #----------------------------------------------
    # Cleans up all resources used by this monster.
    def cleanup(self):
        self.__actor.cleanup()
        self.__actor.removeNode()
        for bbar in self.__bossbars:
            bbar.removeNode()
    ##end def
    
    #--------------------
    # Hides the boss bar.
    def hideBossBar(self):
        for bbar in self.__bossbars:
            bbar.hide()
    ##end def
    
    #---------------------------
    # Stops the attack sequence.
    def stopAttackSequence(self):
        self.__attackInterval.finish()
    ##end def
    
    #----------------------
    # Updates this monster.
    def __updateTask(self, task):
        
        # Only move if not dead.
        if self.__go and self.__health > 0 and self.__game.player.health > 0:
            # Move foreward.
            self.__actor.setFluidY(self.__actor, self.__speed * globalClock.getDt())
            
            # Rotate towards player.
            xToPlayer = self.__game.player.actor.getX(self.__actor)
            if xToPlayer < 0:
                self.__actor.setH(self.__actor, MONSTER_ROT_SPEED * globalClock.getDt())
            elif xToPlayer > 0:
                self.__actor.setH(self.__actor, -MONSTER_ROT_SPEED * globalClock.getDt())
        ##end if
        
        return task.cont
    ##end def
    
    #------------------------
    # Sets the hurt textures.
    def __setHurt0(self): self.__actor.setTexture(self.__hurt0, 1)
    def __setHurt1(self): self.__actor.setTexture(self.__hurt1, 1)
    def __setHurt2(self): self.__actor.setTexture(self.__hurt2, 1)
    def __setHurt3(self): self.__actor.setTexture(self.__hurt3, 1)
    def __setHurt4(self): self.__actor.setTexture(self.__hurt4, 1)
    
    #-------------------------
    # Takes a point of damage.
    def damage(self):
        if self.__health > 0:
            self.__bossbars[self.__health].hide()
            self.__bossbars[self.__health-1].show()
            self.__health -= 1
            if self.__health >= 5: self.__setHurt0()
            elif self.__health == 4: self.__setHurt1()
            elif self.__health == 3: self.__setHurt2()
            elif self.__health == 2: self.__setHurt3()
            elif self.__health == 1: self.__setHurt4()
            LerpColorScaleInterval(self.__actor, .5, VBase4(1,1,1,1), VBase4(1,0,0,1)).start()
            startH = self.__actor.getH()
            def setH(value): self.__actor.setH(startH + value)
            
            # Not dead yet?
            if self.__health > 0:
                Sequence(
                    Wait(.5),
                    SoundInterval(self.__hurtSound)).start()
                LerpFunc(setH, fromData=0.0, toData=360.0, duration=.5).start()
                self.__speed += MONSTER_SPEED_INCREMENT
            # Dead.
            else:
                def doVictory(): self.__game.doVictory()
                self.__game.stopMusic()
                self.stopAttackSequence()
                Sequence(
                    Parallel(
                        SoundInterval(self.__deathSound),
                        LerpScaleInterval(self.__actor, 9.0, Vec3(0,0,0), blendType="easeOut"),
                        LerpFunc(setH, fromData=0.0, toData=6480.0, duration=9.0)),
                    Func(doVictory)).start()
            ##end if
        ##end if
    ##end def
    
    def getActor(self): return self.__actor
    actor = property(getActor)
    
##end class