from direct.showbase import DirectObject
from direct.task import Task
import math

#---------------------------------------------------------
# Retrieves user input and converts it to character input.
class InputHandler(DirectObject.DirectObject):
    
    #---------------------------
    # Creates the input handler.
    def __init__(self):
        self.__turnLeft = False
        self.__turnLeft2 = False
        self.__turnRight = False
        self.__turnRight2 = False
        self.__moveForeward = False
        self.__moveForeward2 = False
        self.__moveReverse = False
        self.__moveReverse2 = False
    ##end def
    
    #-----------------------
    # Starts handling input.
    def start(self):
        self.accept("space", self.__doAction)
        self.accept("arrow_left", self.__doTurnLeft)
        self.accept("arrow_left-up", self.__noTurnLeft)
        self.accept("a", self.__doTurnLeft2)
        self.accept("a-up", self.__noTurnLeft2)
        self.accept("arrow_right", self.__doTurnRight)
        self.accept("arrow_right-up", self.__noTurnRight)
        self.accept("d", self.__doTurnRight2)
        self.accept("d-up", self.__noTurnRight2)
        self.accept("arrow_up", self.__doMoveForeward)
        self.accept("arrow_up-up", self.__noMoveForeward)
        self.accept("w", self.__doMoveForeward2)
        self.accept("w-up", self.__noMoveForeward2)
        self.accept("arrow_down", self.__doMoveReverse)
        self.accept("arrow_down-up", self.__noMoveReverse)
        self.accept("s", self.__doMoveReverse2)
        self.accept("s-up", self.__noMoveReverse2)
    ##end def
    
    #----------------------
    # Stops handling input.
    def stop(self):
        self.ignoreAll()
    ##end def
    
    # Cleans up all resources used by the input handler.
    def cleanup(self):
        pass
    ##end def
    
    def __doAction(self): messenger.send("do_action")
    
    def __doTurnLeft(self): self.__turnLeft = True
    def __noTurnLeft(self): self.__turnLeft = False
    def __doTurnLeft2(self): self.__turnLeft2 = True
    def __noTurnLeft2(self): self.__turnLeft2 = False
    def __doTurnRight(self): self.__turnRight = True
    def __noTurnRight(self): self.__turnRight = False
    def __doTurnRight2(self): self.__turnRight2 = True
    def __noTurnRight2(self): self.__turnRight2 = False
    def __doMoveForeward(self): self.__moveForeward = True
    def __noMoveForeward(self): self.__moveForeward = False
    def __doMoveForeward2(self): self.__moveForeward2 = True
    def __noMoveForeward2(self): self.__moveForeward2 = False
    def __doMoveReverse(self): self.__moveReverse = True
    def __noMoveReverse(self): self.__moveReverse = False
    def __doMoveReverse2(self): self.__moveReverse2 = True
    def __noMoveReverse2(self): self.__moveReverse2 = False
    
    def getTurnLeft(self): return self.__turnLeft or self.__turnLeft2
    def getTurnRight(self): return self.__turnRight or self.__turnRight2
    def getMoveForeward(self): return self.__moveForeward or self.__moveForeward2
    def getMoveReverse(self): return self.__moveReverse or self.__moveReverse2
    turnLeft = property(getTurnLeft)
    turnRight = property(getTurnRight)
    moveForeward = property(getMoveForeward)
    moveReverse = property(getMoveReverse)
    
##end class