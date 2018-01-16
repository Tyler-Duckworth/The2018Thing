from wpilib.command import Command

import subsystems
import oi

from robotmap import axes

class TankDriveJoystick(Command):
    """

    Joystick control the tank drive

    """

    def __init__(self):
        super().__init__('TankDriveJoystick')

        self.requires(subsystems.tankdrive)

    def execute(self):
        joy = oi.get_joystick()
        lpow = joy.getRawAxis(axes.L_y)
        rpow = joy.getRawAxis(axes.R_y)
        subsystems.tankdrive.set_power(lpow, rpow)

    def end(self):
        subsystems.tankdrive.set_power(0, 0)
