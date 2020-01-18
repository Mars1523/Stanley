import wpilib
from networktables.entry import NetworkTableEntry
from wpilib.interfaces.generichid import GenericHID
import marsutils

import components
from networktables import NetworkTables


class Mateo(marsutils.ControlInterface):
    """
        Implements gamepad control via a xbox style gamepad
        
        Currently Gamepad and Mateo control modes are the same
    """

    _DISPLAY_NAME = "Mateo"
    _SORT = 9

    gamepad: wpilib.XboxController
    gamepad_alt: wpilib.XboxController

    drive: components.drive.Drive
    lift: components.lift.Lift
    intake: components.intake.Intake
    grabber: components.grabber.Grabber

    limelight_x: NetworkTableEntry
    limelight_valid: NetworkTableEntry
    dashboard_has_target: NetworkTableEntry

    def teleopPeriodic(self):
        forward_speed = self.gamepad.getTriggerAxis(GenericHID.Hand.kRight)
        reverse_speed = -self.gamepad.getTriggerAxis(GenericHID.Hand.kLeft)
        total_speed = forward_speed + reverse_speed
        if self.lift.lift_encoder.get() > 700:
            total_speed *= 0.8
        if self.lift.get_setpoint() > 1500:
            total_speed *= 0.8

        if self.limelight_valid.getNumber(0) == 0:
            self.dashboard_has_target.setBoolean(False)
        else:
            self.dashboard_has_target.setBoolean(True)
        auto = self.gamepad.getBButton()

        if auto:
            x = self.limelight_x.getNumber(0)
            if x < -4:
                self.drive.drive(0, .65)
            if x > 4:
                self.drive.drive(0, -.65)

        # self.drive.drive(0, .65)
        else:
            self.drive.drive(total_speed, -self.gamepad.getX(GenericHID.Hand.kLeft) * .75)

        self.intake.set_speed(-self.gamepad_alt.getY(GenericHID.Hand.kRight))
        # self.intake.left_intake_motor.set(self.gamepad_alt.getRawAxis(0))
        # self.intake.right_intake_motor.set(-xself.gamepad_alt.getRawAxis(0))

        if self.gamepad_alt.getRawButton(6):
            self.grabber.grab()
        elif self.gamepad_alt.getRawButton(5):
            self.grabber.release()

        # if self.gamepad_alt.getAButton():
        #     self.lift.set_setpoint(0)
        # elif self.gamepad_alt.getXButton():
        #     self.lift.set_setpoint(30)
        # elif self.gamepad_alt.getYButton():
        #     self.lift.set_setpoint(80)
        # elif self.gamepad_alt.getBButton():
        #     self.lift.set_setpoint(105)
        # 2323
        if self.gamepad_alt.getAButton():
            self.lift.set_setpoint(0)
        elif self.gamepad_alt.getXButton():
            self.lift.set_setpoint(600)
        elif self.gamepad_alt.getYButton():
            self.lift.set_setpoint(1600)
        elif self.gamepad_alt.getBButton():
            self.lift.set_setpoint(1800)

        setpoint = self.lift.get_setpoint()
        if self.gamepad_alt.getRawAxis(3) > 0.02:
            self.lift.set_setpoint(setpoint + (self.gamepad_alt.getRawAxis(3) * 60))
        if self.gamepad_alt.getRawAxis(2) > 0.02:
            self.lift.set_setpoint(setpoint - (self.gamepad_alt.getRawAxis(2) * 60))
