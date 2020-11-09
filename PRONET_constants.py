
class Pronet_constants():
    SERVO_ON        = (0,('bit',0)) #register adress, bitdeclaration, bitnumber
    P_OT            = (0,('bit',1))
    N_OT            = (0,('bit',2))
    Alarm_O         = (0,('bit',3))
    CCW             = (1,('bit',0))
    Analog_Vlimit   = (1,('bit',1))
    Analog_Tlimit   = (1,('bit',2))
    ElectronicGear2 = (1,('bit',3))
    EGswitchingMode = (2,('bit',0))
    ABSencoderselect= (2,('bit',2))
    LSpeedcomp      = (3,('bit',2))
    OverloadEnhcmt  = (3,('bit',3))
    StopMode        = (4,('hex',0)) #register adress, hex value declaration (4bits), position in register
    ErrCntClrMode   = (4,('hex',1))
    RefPulseForm    = (4,('hex',2))
    InversePulse    = (4,('hex',3))
    TfeedforwMode   = (5,('hex',0))
    ControlMode     = (5,('hex',0))
    ControlMode_values = {
        'SpeedControl_Aref':0,
        'PositionControl_Ptrain':1,
        'TorqueControl_Aref':2,
        'SpeedControl_Cref-Zref':3,
        'SpeedControl_Cref-Aref':4,
        'SpeedControl_Cref-Ptrain':5,
        'SpeedControl_Cref-Zref':3,
        'SpeedControl_Cref-Zref':3,
        'SpeedControl_Cref-Zref':3,
        'SpeedControl_Cref-Zref':3,
        'SpeedControl_Cref-Zref':3

    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)