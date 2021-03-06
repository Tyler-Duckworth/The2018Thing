import time

from wpilib.command import Command
from wpilib.pidcontroller import PIDController

import subsystems
import oi
from pid.pidmotor import PIDMotorSource, PIDMotorOutput

import math

from puremath.scaling import transform

import robotmap
from robotmap import axes, pid, Gearing, joystick_info
import wpilib


class PIDTankDriveJoystick(Command):
    """

    Joystick control the tank drive

    """


    def __init__(self):
        super().__init__('PIDTankDriveJoystick')

        self.requires(subsystems.tankdrive)
        self.pid_n = 20

        self.use_pid = True

        self.pid = {}

        self.pid["L"] = PIDController(pid.L[0], pid.L[1], pid.L[2], pid.L[3], subsystems.tankdrive.encoders["L"], subsystems.tankdrive.set_left)
        self.pid["R"] = PIDController(pid.R[0], pid.R[1], pid.R[2], pid.R[3], subsystems.tankdrive.encoders["R"], subsystems.tankdrive.set_right)


    def update_pid(self):
        # self.applyPID(lambda p: p.setPIDSourceType(PIDController.PIDSourceType.kRate))
        self.applyPID(lambda p: p.setPIDSourceType(PIDController.PIDSourceType.kRate))
        self.applyPID(lambda p: p.setOutputRange(-1, 1))
        self.applyPID(lambda p: p.setContinuous(False))

        gearing = subsystems.tankdrive.get_gearing()
        lrange = 0.0
        rrange = 0.0

        if gearing == Gearing.LOW:
            self.pid["L"].setInputRange(*robotmap.drive_encoders.L_L)
            self.pid["R"].setInputRange(*robotmap.drive_encoders.R_L)
            lrange = abs(robotmap.drive_encoders.L_L[1] - robotmap.drive_encoders.L_L[0])
            rrange = abs(robotmap.drive_encoders.R_L[1] - robotmap.drive_encoders.R_L[0])
            
        elif gearing == Gearing.HIGH:
            self.pid["L"].setInputRange(*robotmap.drive_encoders.L_H)
            self.pid["R"].setInputRange(*robotmap.drive_encoders.R_H)
            lrange = abs(robotmap.drive_encoders.L_H[1] - robotmap.drive_encoders.L_H[0])
            rrange = abs(robotmap.drive_encoders.R_H[1] - robotmap.drive_encoders.R_H[0])


        # needs to be within 2.5 % of value
        self.pid["L"].setAbsoluteTolerance(lrange * .025)
        self.pid["R"].setAbsoluteTolerance(rrange * .025)

    def initialize(self):
        self.applyPID(lambda pid: pid.enable())
        self.readings = []
        self.use_pid = True

    def end(self):
        self.applyPID(lambda pid: pid.disable())


    def applyPID(self, func):
        func(self.pid["L"])
        func(self.pid["R"])

    def execute(self):

        self.update_pid()

        wpilib.SmartDashboard.putData("tankdrive_left_speed_pid", self.pid["L"])
        wpilib.SmartDashboard.putData("tankdrive_right_speed_pid", self.pid["R"])
        # wpilib.LiveWindow.addSensor("Ticks", "Left Encoder",
        #                             subsystems.tankdrive.encoders["L"])
        # wpilib.LiveWindow.addSensor("Ticks", "Right Encoder",
        #                            subsystems.tankdrive.encoders["R"])

        joy = oi.joystick
        lpow = joy.getRawAxis(axes.L_y) * -1
        rpow = joy.getRawAxis(axes.R_y) * -1

        avg_pow = (lpow + rpow) / 2.0
        diff = abs(lpow - rpow)

        """
        
        diffrange = 0.12

        if diff < diffrange:
            # hard average
            #lpow, rpow = avg_pow, avg_pow
            d_p = diff / diffrange
            #d_p = d_p ** 3
            d_p = math.pow(d_p, 1.0 / 3.0)

            ldiff = lpow - avg_pow
            rdiff = rpow - avg_pow

            lpow = avg_pow + d_p * ldiff
            rpow = avg_pow + d_p * rdiff

        """

        if abs(lpow) <= joystick_info.error: 
            lpow = 0.0

        if abs(rpow) <= joystick_info.error: 
            rpow = 0.0
                        

        reading = {
            "l_pow":lpow,
            "l_rate":subsystems.tankdrive.encoders["L"].getRate(),
            "r_pow":rpow,
            "r_rate":subsystems.tankdrive.encoders["R"].getRate()
        }
        
        self.readings = [reading] + self.readings

        if len(self.readings) > self.pid_n:
            del self.readings[self.pid_n:]
        
        is_changed = False


        if self.readings[-1]["l_pow"] != 0:
            v = self.readings[-1]["l_rate"]
            for i in self.readings:
                if i["l_rate"] != v:
                    is_changed = True

        if self.readings[-1]["r_pow"] != 0:
            v = self.readings[-1]["r_rate"]
            for i in self.readings:
                if i["r_rate"] != v:
                    is_changed = True


        jr = (-1, 1)
        gearing = subsystems.tankdrive.get_gearing()

        slpow, srpow = 0.0, 0.0

        if gearing == Gearing.LOW:
            slpow = transform(lpow, jr, robotmap.drive_encoders.L_L)
            srpow = transform(rpow, jr, robotmap.drive_encoders.R_L)

        elif gearing == Gearing.HIGH:
            slpow = transform(lpow, jr, robotmap.drive_encoders.L_H)
            srpow = transform(rpow, jr, robotmap.drive_encoders.R_H)

        use_pid = is_changed or (self.readings[-1]["l_pow"] == 0 and self.readings[-1]["r_pow"] == 0)

        if use_pid and self.use_pid:
            self.applyPID(lambda pid: pid.enable())
            
            self.pid["L"].setSetpoint(slpow)
            self.pid["R"].setSetpoint(srpow)
            wpilib.SmartDashboard.putNumber("tankdrive_left_speed_setpoint", self.pid["L"].getSetpoint())
            wpilib.SmartDashboard.putNumber("tankdrive_right_speed_setpoint", self.pid["R"].getSetpoint())
        else:
            self.use_pid = False
            self.applyPID(lambda pid: pid.disable())
            subsystems.tankdrive.set(lpow, rpow)
            print("Bruh, you done mess up the encoders.")

        wpilib.SmartDashboard.putBoolean("tankdrive_pid", self.use_pid)

