import wpilib
from wpilib.command import Command
import subsystems

'''
A module that holds the commands used to activate/disable the solenoids on the robot's grabber.
It contains some logic that calls on an object created in TankDrive.py
Created on 1-20-2018
Author: Tyler Duckworth
'''


class Grabber(Command):
    def __init__(self, solenoid_setting):
        super().__init__("Grabber")

        self.solenoid_setting = solenoid_setting

    def initialize(self):
        self.isDone = False

    def execute(self):
        if subsystems.arm.extender_solenoid is not None:
            subsystems.arm.set_extender(self.solenoid_setting)
        else:
            print("warning: subsystems.tankdrive.grabber is None!")
        self.isDone = True

    def isFinished(self):
        return self.isDone