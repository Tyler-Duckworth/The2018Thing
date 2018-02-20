import time

from wpilib.command import CommandGroup

import subsystems

from commands.drivedist import DriveToDistance
from commands.turndrive import TurnDrive

class Sequence(CommandGroup):
    """

    This dumps the info

    """

    def __init__(self):
        super().__init__('Sequence')

        self.addSequential(DriveToDistance(1, 1), 1)
        self.addSequential(TurnDrive(90), 1)
        self.addSequential(DriveToDistance(1, 1), 1)
        self.addSequential(TurnDrive(-90), 1)
        self.addSequential(DriveToDistance(1, 1), 1)
