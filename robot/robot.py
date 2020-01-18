import math
import magicbot
import wpilib
import wpilib.drive

import navx
from networktables import NetworkTables

from ctre import WPI_TalonSRX as CANTalon

from components import drive, lift, grabber, intake
from common.encoder import ExternalEncoder
import control
from controller.angle_controller import AngleController

from marsutils.decorator import with_ctrl_manager

ENCODER_REVOLUTION = 360
WHEEL_DIAMETER = 4
WHEEL_REVOLUTION = (math.pi * WHEEL_DIAMETER) / ENCODER_REVOLUTION

LIFT_HUB_DIAMETER = 3 + (7 / 8)
LIFT_HUB_REVOLUTION = (math.pi * LIFT_HUB_DIAMETER) / ENCODER_REVOLUTION


@with_ctrl_manager
class Stanley(magicbot.MagicRobot):
    # Magic components
    drive: drive.Drive
    lift: lift.Lift
    intake: intake.Intake
    grabber: grabber.Grabber

    # Control modes
    joystick_control: control.Joystick
    # Gamepad or "Zach" controls
    gamepad_control: control.Gamepad
    mateo_control: control.Mateo
    trevor_control: control.Trevor
    lift_override_control: control.LiftOverride

    angle_ctrl: AngleController

    def createObjects(self):
        # Inputs
        # TODO: Update these dynamically
        self.stick = wpilib.Joystick(2)
        # self.gamepad = wpilib.XboxController(1)
        # self.gamepad_alt = wpilib.XboxController(2)
        self.gamepad = wpilib.XboxController(0)
        self.gamepad_alt = wpilib.XboxController(1)

        # Drive motors
        self.left_motor = wpilib.Spark(0)
        self.right_motor = wpilib.Spark(1)

        self.drive_train = wpilib.drive.DifferentialDrive(
            self.left_motor, self.right_motor
        )
        self.drive_train.deadband = .04

        # Elevator encoder (gearbox)
        self.lift_encoder = ExternalEncoder(0, 1)
        # TODO: Fix the pid
        # self.lift_encoder.encoder.setDistancePerPulse(WHEEL_REVOLUTION)

        # Drive encoders
        self.left_encoder = ExternalEncoder(2, 3)
        self.right_encoder = ExternalEncoder(4, 5, True)
        self.left_encoder.encoder.setDistancePerPulse(WHEEL_REVOLUTION)
        self.right_encoder.encoder.setDistancePerPulse(WHEEL_REVOLUTION)

        # Elevator motors
        self.lift_master = CANTalon(2)
        self.lift_follower1 = CANTalon(3)
        self.lift_follower2 = CANTalon(4)
        self.lift_follower1.follow(self.lift_master)
        self.lift_follower2.follow(self.lift_master)

        # Intake motors
        self.left_intake_motor = wpilib.Spark(2)
        self.right_intake_motor = wpilib.Spark(3)
        self.right_intake_motor.setInverted(True)

        # Intake grabbers
        self.grabber_solenoid = wpilib.DoubleSolenoid(1, 0, 1)

        # PDP
        self.pdp = wpilib.PowerDistributionPanel(0)
        wpilib.SmartDashboard.putData("PowerDistributionPanel", self.pdp)

        # Misc
        self.navx = navx.AHRS.create_spi()

        self.net_table = NetworkTables.getTable("SmartDashboard")
        self.vision_table = NetworkTables.getTable("limelight")
        self.limelight_x = self.vision_table.getEntry("tx")
        self.limelight_valid = self.vision_table.getEntry("tv")
        self.dashboard_has_target = self.vision_table.getEntry("hastarget")

        # Launch camera server
        wpilib.CameraServer.launch()

    def autonomous(self):
        """Prepare for autonomous mode"""

        magicbot.MagicRobot.autonomous(self)


if __name__ == "__main__":
    # Run robot
    wpilib.run(Stanley)
