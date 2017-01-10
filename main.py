import direct.directbase.DirectStart
from direct.fsm import FSM
import sys

# My imports.
from game import *
from splash import *

base.disableMouse()
#messenger.toggleVerbose()

base.enableParticles()

# FSM for managing application states.
class App(FSM.FSM):
    def __init__(self):
        FSM.FSM.__init__(self, "AppFSM")
        self.game = Game()
        self.splash = SplashScreen()
    def enterSplash(self):
        self.splash.start()
    def exitSplash(self):
        self.splash.stop()
    def enterGame(self):
        self.game.start()
    def exitGame(self):
        self.game.stop()
    def enterQuit(self):
        self.splash.cleanup()
        self.game.cleanup()
        sys.exit()
    def exitQuit(self):
        pass
##end class

# Handle special app-level key presses.
def toggleOOBE(): base.oobe()
def openPlacer(): render.place()
def quitApp(): app.request("Quit")
dobject = DirectObject.DirectObject()
dobject.accept("f11", toggleOOBE)
dobject.accept("f12", openPlacer)
dobject.accept("escape", quitApp)

# Handle requests to switch states.
def switchToGame(): app.request("Game")
dobject.accept("state_game", switchToGame)

app = App()
app.request("Splash")
run()
