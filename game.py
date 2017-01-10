from direct.showbase import DirectObject
from pandac.PandaModules import *
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
import math
import random

# My imports.
from player import *
from input import *
from bunny import *
from monster import *
from util import *

BUNNY_COUNT = 15
PEOPLE_COUNT = 25
GAME_MUSIC_VOLUME = .5

#-------------------------------
# Contains actual gameplay code.
class Game():
    
    #-----------------------------
    # Creates and starts the game.
    def __init__(self):
        
        self.node = NodePath("GameNode")
        self.node2d = NodePath("GameNode2D")
        
        # Create environment.
        environ = loader.loadModel("models/square/square.bam")
        def instanceEnviron(i, pos):
            instance = self.node.attachNewNode("EnvironInstance_" + str(i))
            instance.setPos(pos)
            environ.setScale(.5)
            environ.instanceTo(instance)
        ##end def
        instanceEnviron(0, Vec3(-100,-100,0))
        instanceEnviron(1, Vec3(0,-100,0))
        instanceEnviron(2, Vec3(100,-100,0))
        instanceEnviron(3, Vec3(-100,0,0))
        instanceEnviron(4, Vec3(0,0,0))
        instanceEnviron(5, Vec3(100,0,0))
        instanceEnviron(6, Vec3(-100,100,0))
        instanceEnviron(7, Vec3(0,100,0))
        instanceEnviron(8, Vec3(100,100,0))
        
        instanceEnviron(8, Vec3(-200,-200,0))
        instanceEnviron(8, Vec3(-100,-200,0))
        instanceEnviron(8, Vec3(0,-200,0))
        instanceEnviron(8, Vec3(100,-200,0))
        instanceEnviron(8, Vec3(200,-200,0))
        instanceEnviron(8, Vec3(-200,-100,0))
        instanceEnviron(8, Vec3(200,-100,0))
        instanceEnviron(8, Vec3(-200,0,0))
        instanceEnviron(8, Vec3(200,0,0))
        instanceEnviron(8, Vec3(-200,100,0))
        instanceEnviron(8, Vec3(200,100,0))        
        instanceEnviron(8, Vec3(-200,200,0))
        instanceEnviron(8, Vec3(-100,200,0))
        instanceEnviron(8, Vec3(0,200,0))
        instanceEnviron(8, Vec3(100,200,0))
        instanceEnviron(8, Vec3(200,200,0))

        
        # Create skybox.
        self.__skybox = loader.loadModel("models/alice-farm--farmsky/farmsky.bam")
        self.__skybox.setScale(1)
        self.__skybox.setPos(0,0,-200)
        self.__skybox.reparentTo(self.node)
        self.__skyboxMat = Material()
        self.__skyboxMat.setEmission(VBase4(.75, .75, .75, 1))
        self.__skybox.setMaterial(self.__skyboxMat)
        self.__skybox.setBin("background", 0)
        
        # Create victory skybox.
        self.__victorySkybox = loader.loadModel("models/alice-skies--blue-sky-sphere/blue-sky-sphere.bam")
        self.__victorySkybox.setScale(.15)
        self.__victorySkybox.setPos(0,0,-200)
        self.__victorySkybox.setTransparency(TransparencyAttrib.MAlpha)
        self.__victorySkybox.reparentTo(self.node)
        self.__victorySkybox.setColorScale(VBase4(1, 1, 1, 0))
        self.__victorySkybox.hide()
        self.__victorySkyboxMat = Material()
        self.__victorySkyboxMat.setEmission(VBase4(1, 1, 1, 1))
        self.__victorySkybox.setMaterial(self.__victorySkyboxMat)
        self.__skybox.setBin("background", 0)
        
        # Setup collisions.
        self.cTrav = CollisionTraverser("CollisionTraverser")
        
        # Setup collision planes.
        plane0 = CollisionPlane(Plane(Vec3(1, 0, 0), Point3(-150, 0, 0)))
        plane0NP = self.node.attachNewNode(CollisionNode("Plane_0"))
        plane0NP.node().addSolid(plane0)
        plane1 = CollisionPlane(Plane(Vec3(-1, 0, 0), Point3(150, 0, 0)))
        plane1NP = self.node.attachNewNode(CollisionNode("Plane_1"))
        plane1NP.node().addSolid(plane1)
        plane2 = CollisionPlane(Plane(Vec3(0, 1, 0), Point3(0, -150, 0)))
        plane2NP = self.node.attachNewNode(CollisionNode("Plane_2"))
        plane2NP.node().addSolid(plane2)
        plane3 = CollisionPlane(Plane(Vec3(0, -1, 0), Point3(0, 150, 0)))
        plane3NP = self.node.attachNewNode(CollisionNode("Plane_3"))
        plane3NP.node().addSolid(plane3)

        # Create player.
        self.input = InputHandler()
        self.player = Player(self, self.input, Vec3(0, 95, 0))
        
        # Create monster.
        self.monster = Monster(self, Vec3(0, 0, 10))
        
        # Create bunnies.
        self.bunnies = []
        for i in range(0, BUNNY_COUNT):
            x = random.random() * 300 - 150
            y = random.random() * 300 - 150
            h = random.random() * 360
            self.bunnies.append(Bunny(self, Vec3(x, y, 0), h))
        ##end for
        
        # Create light on camera.
        self.__plight = PointLight("Player_PointLight_" + str(id(self)))
        self.__plight.setColor(VBase4(1, 1, 1, 1))
        self.__plight.setAttenuation(Point3(0, 0, 0))
        
        # Create ambient light.
        self.__alight = AmbientLight("alight")
        self.__alight.setColor(VBase4(.2, .2, .2, 1))
        self.__alnp = self.node.attachNewNode(self.__alight)
        self.node.setLight(self.__alnp)
        
        # Create collision handler on camera.
        collisionSphere = CollisionSphere(0, 0, 0, .5)
        self.__cameraCollider = NodePath(CollisionNode("Camera_CollisionSphere_" + str(id(self))))
        self.__cameraCollider.node().addSolid(collisionSphere)
        #self.__cameraCollider.node().setFromCollideMask(CAMERA_COLLIDE_FROM_MASK)
        self.__cameraCollider.setCollideMask(0)
        pusher = CollisionHandlerPusher()
        pusher.addCollider(self.__cameraCollider, base.camera)
        self.cTrav.addCollider(self.__cameraCollider, pusher)
        
        # Load music and sounds.
        self.__music = loader.loadSfx("sounds/game_music.mp3")
        self.__music.setVolume(GAME_MUSIC_VOLUME)
        self.__defeatMusic = loader.loadSfx("sounds/defeat_music.mp3")
        self.__victoryMusic = loader.loadSfx("sounds/victory_music.mp3")
        self.__victorySound = loader.loadSfx("sounds/victory.wav")
        self.__defeatSound = loader.loadSfx("sounds/defeat.wav")
        
        # Load signs.
        cardMaker = CardMaker("Signs")
        aspectRatio = base.getAspectRatio()
        SIGN_WIDTH = 2
        SIGN_HEIGHT = .25
        SIGN_LEFT = -SIGN_WIDTH / 2.0
        SIGN_RIGHT = SIGN_LEFT + SIGN_WIDTH
        SIGN_BOTTOM = -SIGN_HEIGHT / 2.0
        SIGN_TOP = SIGN_BOTTOM + SIGN_HEIGHT
        cardMaker.setFrame(SIGN_LEFT, SIGN_RIGHT, SIGN_BOTTOM, SIGN_TOP)
        self.__signNP = NodePath(cardMaker.generate())
        self.__signNP.setTransparency(TransparencyAttrib.MAlpha)
        self.__victoryTex = loader.loadTexture("textures/victory.png")
        self.__defeatTex = loader.loadTexture("textures/defeat.png")
        
        # Make buildings.
        self.buildings = []
        beachHouseModel = loader.loadModel("models/alice-beach--beachhouse2/beachhouse2.bam")
        churchModel = loader.loadModel("models/alice-city--church/church.bam")
        cityHallModel = loader.loadModel("models/alice-city--cityhall/cityhall.bam")
        townhouseModel = loader.loadModel("models/alice-city--townhouse1/townhouse1.bam")
        farmhouseModel = loader.loadModel("models/alice-farm--farmhouse/farmhouse.bam")
        dojoModel = loader.loadModel("models/alice-japan--dojo/dojo")
        def makeBuilding(model, scale, pos, hpr):
            instance = self.node.attachNewNode(model.getName())
            model.instanceTo(instance)
            instance.setPos(pos)
            instance.setScale(scale)
            instance.setHpr(hpr)
            instance.setColorScale(VBase4(.5,.5,.5,1))
            self.buildings.append(instance)
        ##end def
        makeBuilding(beachHouseModel, 1, Vec3(-160,0,-1), Vec3(0,0,0))
        makeBuilding(beachHouseModel, 1, Vec3(160,0,-1), Vec3(0,0,0))
        makeBuilding(beachHouseModel, 1, Vec3(0,-160,-1), Vec3(0,0,0))
        makeBuilding(beachHouseModel, 1, Vec3(0,160,-1), Vec3(0,0,0))
        makeBuilding(churchModel, 1, Vec3(-178,-78,-1), Vec3(0,0,0))
        makeBuilding(churchModel, 1, Vec3(178,-78,-1), Vec3(0,0,0))
        makeBuilding(churchModel, 1, Vec3(-178,78,-1), Vec3(0,0,0))
        makeBuilding(churchModel, 1, Vec3(178,78,-1), Vec3(0,0,0))
        makeBuilding(cityHallModel, 1, Vec3(-54,-167,-1), Vec3(0,0,0))
        makeBuilding(cityHallModel, 1, Vec3(54,167,-1), Vec3(0,0,0))
        makeBuilding(townhouseModel, 1, Vec3(-23,158,-1), Vec3(180,0,0))
        makeBuilding(townhouseModel, 1, Vec3(-158,-23,-1), Vec3(270,0,0))
        makeBuilding(townhouseModel, 1, Vec3(23,-158,-1), Vec3(0,0,0))
        makeBuilding(townhouseModel, 1, Vec3(158,-23,-1), Vec3(90,0,0))
        makeBuilding(townhouseModel, 1, Vec3(-38,158,-1), Vec3(180,0,0))
        makeBuilding(townhouseModel, 1, Vec3(-158,-38,-1), Vec3(270,0,0))
        makeBuilding(townhouseModel, 1, Vec3(38,-158,-1), Vec3(0,0,0))
        makeBuilding(townhouseModel, 1, Vec3(158,-38,-1), Vec3(90,0,0))
        makeBuilding(townhouseModel, 1, Vec3(-53,158,-1), Vec3(180,0,0))
        makeBuilding(townhouseModel, 1, Vec3(-158,-53,-1), Vec3(270,0,0))
        makeBuilding(townhouseModel, 1, Vec3(53,-158,-1), Vec3(0,0,0))
        makeBuilding(townhouseModel, 1, Vec3(158,-53,-1), Vec3(90,0,0))
        makeBuilding(farmhouseModel, 1, Vec3(90,-161,-1), Vec3(0,0,0))
        makeBuilding(farmhouseModel, 1, Vec3(-90,161,-1), Vec3(0,0,0))
        makeBuilding(dojoModel, .075, Vec3(-160,-160,-1), Vec3(0,0,0))
        makeBuilding(dojoModel, .075, Vec3(160,-160,-1), Vec3(0,0,0))
        makeBuilding(dojoModel, .075, Vec3(-160,160,-1), Vec3(0,0,0))
        makeBuilding(dojoModel, .075, Vec3(160,160,-1), Vec3(0,0,0))
        makeBuilding(farmhouseModel, 1, Vec3(163,37,-1), Vec3(90,0,0))
        makeBuilding(farmhouseModel, 1, Vec3(-163,37,-1), Vec3(90,0,0))
        makeBuilding(farmhouseModel, 1, Vec3(-119,-161,-1), Vec3(180,0,0))
        makeBuilding(farmhouseModel, 1, Vec3(119,161,-1), Vec3(180,0,0))
        makeBuilding(beachHouseModel, 1, Vec3(127,-160,-1), Vec3(90,0,0))
        makeBuilding(beachHouseModel, 1, Vec3(-127,160,-1), Vec3(90,0,0))
        makeBuilding(townhouseModel, 1, Vec3(162,105,-1), Vec3(90,0,0))
        makeBuilding(townhouseModel, 1, Vec3(162,-105,-1), Vec3(90,0,0))
        makeBuilding(townhouseModel, 1, Vec3(-162,105,-1), Vec3(270,0,0))
        makeBuilding(townhouseModel, 1, Vec3(-162,-105,-1), Vec3(270,0,0))
        makeBuilding(townhouseModel, 1, Vec3(162,125,-1), Vec3(90,0,0))
        makeBuilding(townhouseModel, 1, Vec3(162,-125,-1), Vec3(90,0,0))
        makeBuilding(townhouseModel, 1, Vec3(-162,125,-1), Vec3(270,0,0))
        makeBuilding(townhouseModel, 1, Vec3(-162,-125,-1), Vec3(270,0,0))
        
        # Make people.
        peopleModels = []
        peopleModels.append(loader.loadModel("models/bvw-f2004--brotherlittle/littlebrother.bam"))
        peopleModels.append(loader.loadModel("models/bvw-f2004--brotherolder/olderbrother.bam"))
        self.people = []
        for i in range(0, PEOPLE_COUNT):
            instance = self.node.attachNewNode("Person_" + str(i))
            model = peopleModels[random.randrange(len(peopleModels))]
            model.instanceTo(instance)
            x = random.random() * 300 - 150
            y = random.random() * 300 - 150
            h = random.random() * 360
            instance.setPos(Vec3(x, y, 0))
            instance.setScale(3)
            instance.setHpr(Vec3(h, 0, 0))
            instance.setColorScale(VBase4(1,1,1,0))
            instance.setTransparency(TransparencyAttrib.MAlpha)
            instance.hide()
            self.people.append(instance)
        ##end for
        
        # Make credits.
        creditsText = "EXPLODING DEMON BUNNIES VS\nTHE EYEBALL MONSTER\n\n"
        creditsText += "A BVW 2009 Project 0 Production\n\n\n"
        creditsText += "GAME DESIGN by Walt Destler\n\n"
        creditsText += "PROGRAMMING by Walt Destler\n\n"
        creditsText += "MODELS from Panda3D's art-gallery.zip\n\n"
        creditsText += "SOUND EFFECTS and SOME MUSIC from \\\\Randon\n\n"
        creditsText += "VICTORY MUSIC by Silver Blade (Creative Commons)\n\n"
        creditsText += "DEFEAT MUSIC by Stubl007 (Creative Commons)\n\n"
        creditsText += "PLAYTESTING by ETC class of 2011\n\n"
        creditsText += "SPECIAL THANKS to the BVW TAs (especially Whitney) and\n"
        creditsText += "    my fellow programmers: Dan Driscoll and Amy Goodwin\n\n\n"
        creditsText += "Copyright (c) 2009 Walt Destler"
        self.__credits = OnscreenText(text=creditsText, pos=(-1,-1.5), scale=.1, fg=(1.0,1.0,1.0,1.0), align=TextNode.ALeft)
        self.__credits.hide()
        self.__credits.reparentTo(self.node2d)
    ##end def
    
    #-----------------
    # Starts the game.
    def start(self):
        # Show game.
        self.node.reparentTo(render)
        self.node2d.reparentTo(aspect2d)
        base.cTrav = self.cTrav

        # Attach camera to player.
        base.camera.reparentTo(self.player.actor)
        self.cameraPos = Vec3(0, 24, 6)
        base.camera.setPos(self.cameraPos)
        base.camera.lookAt(self.player.actor)
        base.camera.setP(0)
        
        # Attach light to camera.
        self.__plnp = base.camera.attachNewNode(self.__plight)
        self.node.setLight(self.__plnp)
        
        # Attach collider to camera.
        self.__cameraCollider.reparentTo(base.camera)
        
        # Start game objects.
        self.input.start()
        self.player.start()
        self.monster.start()
        for bunny in self.bunnies:
            bunny.start()
            
        # Reparent sign.
        self.__signNP.reparentTo(self.node2d)
        self.__signNP.hide()
    ##end def
    
    #----------------
    # Stops the game.
    def stop(self):
        self.__signNP.detachNode()
        for bunny in self.bunnies:
            bunny.stop()
        self.monster.stop()
        self.player.stop()
        self.input.stop()
        self.__cameraCollider.detachNode()
        self.__plnp.detachNode()
        base.camera.reparentTo(render)
        base.cTrav = None
        self.node2d.detachNode()
        self.node.detachNode()
        self.__music.stop()
    ##end def
    
    #------------------------------------------
    # Cleans up all resources used by the game.
    def cleanup(self):
        self.__signNP.removeNode()
        for bunny in self.bunnies:
            bunny.cleanup()
        self.monster.cleanup()
        self.player.cleanup()
        self.input.cleanup()
        self.__plnp.removeNode()
        self.node2d.removeNode()
        self.node.removeNode()
    ##end def
    
    #-------------------------------------------
    # Removes the specified bunny from the game.
    def removeBunny(self, bunny):
        self.bunnies.remove(bunny)
        if self.player.bunny == bunny:
            self.player.bunny = None
    ##end def
    
    #---------------------------------------------
    # Plays a sound effect relative to the player.
    def playPlayerRelativeSound(self, sound, x, y, range):
        playerX = self.player.actor.getX(self.node)
        playerY = self.player.actor.getY(self.node)
        playRangedSound(sound, playerX, playerY, x, y, range)
    ##end def
    
    #----------------------------
    # Starts rolling the credits.
    def startCredits(self):
        self.__credits.show()
        endPos = Vec3(
            self.__credits.getX(),
            self.__credits.getY(),
            10)
        LerpPosInterval(self.__credits, 200.0, endPos).start()
    ##end def
    
    #------------------------------------
    # Puts the game into a victory state.
    def doVictory(self):
        #self.__signNP.setTexture(self.__victoryTex)
        #self.__signNP.show()
        self.__victorySound.play()
        self.__victoryMusic.setLoop(True)
        self.__victoryMusic.play()
        self.monster.hideBossBar()
        self.player.hideHearts()
        self.startCredits()
        
        # Put bunnies into victory state.
        for bunny in self.bunnies:
            bunny.doVictory()
            
        # Show people in prep to fade in.
        for person in self.people:
            person.show()
        
        # Do mood change.
        alightStartColor = VBase4(self.__alight.getColor())
        ALIGHT_END_COLOR = VBase4(.5, .5, .5, 1)
        alightColorDiff = ALIGHT_END_COLOR - alightStartColor
        skyboxStartColor = VBase4(self.__skyboxMat.getEmission())
        SKYBOX_END_COLOR = VBase4(1, 1, 1, 1)
        skyboxColorDiff = SKYBOX_END_COLOR - skyboxStartColor
        buildingStartColor = VBase4(self.buildings[0].getColorScale())
        BUILDING_END_COLOR = VBase4(1, 1, 1, 1)
        buildingColorDiff = BUILDING_END_COLOR - buildingStartColor
        def lerpLightFunc(value):
            self.__alight.setColor(alightStartColor + alightColorDiff*value)
            self.__skyboxMat.setEmission(skyboxStartColor + skyboxColorDiff*value)
            self.__skybox.setMaterial(self.__skyboxMat)
            for building in self.buildings:
                building.setColorScale(buildingStartColor + buildingColorDiff*value)
        ##end def
        def lerpVictorySkyboxFunc(value):
            self.__victorySkybox.setColorScale(VBase4(1, 1, 1, value))
        ##end def
        def lerpPeopleFunc(value):
            for person in self.people:
                person.setColorScale(VBase4(1, 1, 1, value))
        ##end def
        self.__victorySkybox.show()
        Sequence(
            LerpFunc(lerpLightFunc, fromData=0, toData=1, duration=5.0),
            LerpFunc(lerpVictorySkyboxFunc, fromData=0, toData=1, duration=5.0),
            LerpFunc(lerpPeopleFunc, fromData=0, toData=1, duration=5.0)).start()
    ##end def
    
    #-----------------------------------
    # Puts the game into a defeat state.
    def doDefeat(self):
        #self.__signNP.setTexture(self.__defeatTex)
        #self.__signNP.show()
        self.__defeatSound.play()
        self.monster.hideBossBar()
        self.player.hideHearts()
        self.startCredits()
        def playDefeatMusic():
            self.__defeatMusic.setLoop(True)
            self.__defeatMusic.play()
        ##end def
        Sequence(
            Wait(3.0),
            Func(playDefeatMusic)).start()
    ##end def
    
    #----------------------
    # Plays the game music.
    def playMusic(self):
        self.__music.setLoop(True)
        self.__music.play()
    ##end def
    
    #----------------------
    # Stops the game music.
    def stopMusic(self):
        self.__music.stop()
    ##end def

##end class