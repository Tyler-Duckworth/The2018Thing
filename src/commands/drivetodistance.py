import wpilib

from wpilib.command import Command
from wpilib.pidcontroller import PIDController
import subsystems
from robotmap import pid, Gearing, waits

'''
PARAMS:
The distance is in meters.
Remember 
1 meter = 3.28084 feet.
1 meter = 39.3701 inches.
'''


class DriveToDistance(Command):
    def __init__(self, _ldist, _rdist, dummy = None):
        super().__init__('DriveToDistance')
        self.requires(subsystems.tankdrive)

        self.ldist = _ldist
        self.rdist = _rdist

        self.pid = {}
        self.pid["L"] = PIDController(pid.dist_L[0], pid.dist_L[1], pid.dist_L[2], pid.dist_L[3], subsystems.tankdrive.get_left_distance, subsystems.tankdrive.set_left)
        self.pid["R"] = PIDController(pid.dist_R[0], pid.dist_R[1], pid.dist_R[2], pid.dist_R[3], subsystems.tankdrive.get_right_distance, subsystems.tankdrive.set_right)

        self.applyPID(lambda p: p.setInputRange(-10**8, 10**8))
        self.applyPID(lambda p: p.setOutputRange(-.7, .7))
        self.applyPID(lambda p: p.setContinuous(False))
        #self.applyPID(lambda p: p.useDistance())
        
        #self.applyPID(lambda p: p.setPIDSourceType(PIDController.PIDSourceType.kDisplacement))

        self.applyPID(lambda p: p.setAbsoluteTolerance(.07))
        
        
        self.is_init = False

    def applyPID(self, func):
        func(self.pid["L"])
        func(self.pid["R"])

    def initialize(self):

        subsystems.tankdrive.set_gearing(Gearing.LOW)

        self.lset, self.rset = subsystems.tankdrive.encoders["L"].getDistance() + self.ldist, subsystems.tankdrive.encoders["R"].getDistance() + self.rdist

        self.pid["L"].setSetpoint(self.lset)
        self.pid["R"].setSetpoint(self.rset)

        self.applyPID(lambda pid: pid.enable())

        self.is_init = False

    def execute(self):

        self.pid["L"].setSetpoint(self.lset)
        self.pid["R"].setSetpoint(self.rset)

        self.applyPID(lambda pid: pid.enable())

        wpilib.SmartDashboard.putData("tankdrive_left_distance_pid", self.pid["L"])
        wpilib.SmartDashboard.putData("tankdrive_right_distance_pid", self.pid["R"])

        self.is_init = True


    def end(self):
        self.applyPID(lambda pid: pid.disable())
        subsystems.tankdrive.set(0, 0)

    def isFinished(self):
        return self.pid["L"].onTarget() and self.pid["R"].onTarget() and self.is_init

    def interrupted(self):
        self.end()
