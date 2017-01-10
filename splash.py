from direct.showbase import DirectObject
from pandac.PandaModules import *

SPLASH_MUSIC_VOLUME = 1

#-------------------------------------------------------------------
# The splash screen shown to the user when starting the application.
class SplashScreen(DirectObject.DirectObject):
    def __init__(self):
        self.node2d = NodePath("SplashNode")
        
        cardMaker = CardMaker("SplashScreen")
        aspectRatio = base.getAspectRatio()
        cardMaker.setFrame(-aspectRatio, aspectRatio, -1, 1)
        splashTexture = loader.loadTexture("textures/splash.png")
        splashNP = NodePath(cardMaker.generate())
        splashNP.setTexture(splashTexture)
        splashNP.reparentTo(self.node2d)
        
        self.__music = loader.loadSfx("sounds/splash_music.wav")
        self.__music.setVolume(SPLASH_MUSIC_VOLUME)
    ##end def
    def start(self):
        self.node2d.reparentTo(aspect2d)
        self.__music.setLoop(True)
        self.__music.play()
        self.accept("space", self.__doClose)
        self.accept("mouse1", self.__doClose)
    ##end def
    def stop(self):
        self.ignoreAll()
        self.__music.stop()
        self.node2d.detachNode()
    ##end def
    def cleanup(self):
        self.node2d.removeNode()
    ##end def
    def __doClose(self):
        messenger.send("state_game")
    #end def
##end class