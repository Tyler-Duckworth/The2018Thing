import wpilib
from wpilib.command import Command
import subsystems
from commands.auto.sameside import SameSide
from commands.auto.invsameside import InvSameSide
from commands.drivetodistance import DriveToDistance

def Left_POS(_data):
    data = list(_data)
    if data[1] == "R":
        return InvSameSide(True)
    elif data[1] == "L":
        return SameSide(True)
    else:
        return DriveToDistance(3.048, 3.048)
