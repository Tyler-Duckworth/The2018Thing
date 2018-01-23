import wpilib

from wpilib.command.subsystem import Subsystem 
from hardware.navx import NavX
from robotmap import navx_type


'''
A class for the various sensors on the robot. 
Currently includes Kauai Labs NavX.abs

Created on 1-20-2018 by Tyler Duckworth
'''

class Sensors(Subsystem):
    
    def __init__(self):
        self.navx = NavX(navx_type)
