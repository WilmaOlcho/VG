##Directly from PRONET_manual_V1_25.pdf
#
#Title: ProNet Series AC Servo User's Manual
#Version: V1.25
#Vendor: ESTUN AUTOMATION TECHNOLOGY CO., LTD
#Revision: 2012-03, V1.25
#
#
class Pronet_constants(): 
    #############Control mode parameters#############
    SERVO_ON            = (0,('bit',0),'rw') #register adress, bitdeclaration, bitnumber
    P_OT                = (0,('bit',1),'rw')
    N_OT                = (0,('bit',2),'rw')
    Alarm_O             = (0,('bit',3),'rw')
    CCW                 = (1,('bit',0),'rw')
    Analog_Vlimit       = (1,('bit',1),'rw')
    Analog_Tlimit       = (1,('bit',2),'rw')
    ElectronicGear2     = (1,('bit',3),'rw')
    EGswitchingMode     = (2,('bit',0),'rw')
    ABSencoderselect    = (2,('bit',2),'rw')
    LSpeedcomp          = (3,('bit',2),'rw')
    OverloadEnhcmt      = (3,('bit',3),'rw')
    StopMode            = (4,('hex',0),'rw') #register adress, hex value declaration (4bits), position in register
    ErrCntClrMode       = (4,('hex',1),'rw')
    RefPulseForm        = (4,('hex',2),'rw')
    InversePulse        = (4,('hex',3),'rw')
    QfeedforwMode       = (5,('hex',0),'rw')
    ControlMode         = (5,('hex',1),'rw')
    ControlMode_values  = {
        'SpeedControl_Aref':0,
        'PositionControl_Ptrain':1,
        'TorqueControl_Aref':2,
        'SpeedControl_Cref-SpeedControl_Zref':3,
        'SpeedControl_Cref-SpeedControl_Aref':4,
        'SpeedControl_Cref-SpeedControl_Ptrain':5,
        'SpeedControl_Cref-TorqueControl_Aref':6,
        'PositionControl_Ptrain-SpeedControl_Aref':7,
        'PositionControl_Ptrain-TorqueControl_Aref':8,
        'TorqueControl_Aref-SpeedControl_Aref':9,
        'SpeedControl_Aref-ZeroClamp':10,
        'PositionControl_Ptrain-PositionControl_inhibit':11,
        'PositionControl_Cref':12,
        'SpeedControl_Pref':13,
        'PressureControl-Aref':14}
    OOTAlarmSelect      = (5,('hex',2),'rw')
    ServomotorModel     = (5,('hex',3),'rw')
    BusMode             = (6,('hex',0),'rw')
    LFreqJitterSupSw    = (6,('hex',2),'rw')
    RefInFilterforOC    = (6,('hex',3),'rw')
    #############Parameters of servo gain#############
    OnlineAutotuning    = (100,('int',0),'rw') #Register adress, int value
    OnlineAutotuning_values = {
        'ManualGainAdjustment':0,
        'NormalMode':{
            'WithoutVariation':1,
            'LittleVariation':2,
            'GreatVariation':3},
        'VerticalLoad':{
            'WithoutVariation':4,
            'LittleVariation':5,
            'GreatVariation':6}}
    MachineRigidity     = (101,('int',0),'rw')
    SpeedLoopGain       = (102,('int',0),'rw')
    SpdLoopIntTConst    = (103,('int',0),'rw')
    PosLoopGain         = (104,('int',0),'rw')
    QRefFilterTConst    = (105,('int',0),'rw')
    LoadInertiaPerc     = (106,('int',0),'rw')
    SpeedLoopGain2      = (107,('int',0),'rw')
    SpdLoopIntTConst2   = (108,('int',0),'rw')
    PosLoopGain2        = (109,('int',0),'rw')
    QRefFilterTConst2   = (110,('int',0),'rw')
    SpeedBias           = (111,('int',0),'rw')
    Feedforward         = (112,('int',0),'rw')
    FeedforvardFilter   = (113,('int',0),'rw')
    TorqueFeedforvard   = (114,('int',0),'rw')
    TorqueFeedforvardFil= (115,('int',0),'rw')
    PPISwCondition      = (116,('int',0),'rw')
    PPISwCondition_values = {
        'TorqueReferencePercentage':0,
        'ValueOfOffsetCounter':1,
        'ValueOfAccelerationSpeedSetting':2,
        'ValueOfSpeedSetting':3,
        'FixedPI':4}
    TorqueSwTreshold    = (117,('int',0),'rw')
    OffsetCntSwTreshold = (118,('int',0),'rw')
    SetAccSpdSwTreshhold= (119,('int',0),'rw')
    SetSpdSwTreshhold   = (120,('int',0),'rw')
    GainSwCondition     = (121,('int',0),'rw')
    GainSwCondition_values = {
        'FixTo1stGroupGain':0,
        'ExtSwGainSwitching':1,
        'TorquePercentage':2,
        'ValueOfOffsetCnt':3,
        'ValueOfAccSpdSet':4,
        'ValueOfSpdSet':5,
        'SpdRefInput':6}
    SwitchindDelayTime  = (122,('int',0),'rw')
    TresholdSwitchingLvl= (123,('int',0),'rw')
    PosGainSwTime       = (125,('int',0),'rw')
    HysteresisSwitching = (126,('int',0),'rw')
    LowSpdDetectFilter  = (127,('int',0),'rw')
    SpdGainAccrelDOAutot= (128,('int',0),'rw')
    LowSpdCorrectionCoef= (129,('int',0),'rw')
    FrictionLoad        = (130,('int',0),'rw')
    FrictCompSpdHysArea = (131,('int',0),'rw')
    StickingFrictLoad   = (132,('int',0),'rw')
    #############Position control related parameters#############
    PGDividedRatio      = (200,('int',0),'rw')
    EGear1Numerator     = (201,('int',0),'rw')
    EGear1Denominator   = (202,('int',0),'rw')
    EGear2Numerator     = (203,('int',0),'rw')
    PosRefAccDeccTConst = (204,('int',0),'rw')
    PosRefFilterFormSel = (205,('int',0),'rw')
    #############Speed control related parameters#############
    SpdRefInputGain     = (300,('int',0),'rw')
    AnalogSpdGivenZBias = (301,('int',0),'rw')
    ParameterSpeed      = (304,('int',0),'rw')
    JOGSpeed            = (305,('int',0),'rw')
    SoftStartAccTime    = (306,('int',0),'rw')
    SoftStartDecelTime  = (307,('int',0),'rw')
    SpdFilterTimeConst  = (308,('int',0),'rw')
    SCurveRisetime      = (309,('int',0),'rw')
    SpdRefCurveForm     = (310,('int',0),'rw')
    SpdRefCurveForm_values = {
        'Slope':0,
        'SCurve':1,
        'FstOrderFilter':2,
        'ScndOrderFilter':3}
    SFormSelection      = (311,('int',0),'rw')
    SFormSelection_values = {
        'Slope':0,
        'SCurve':1,
        'FstOrderFilter':2,
        'ScndOrderFilter':3}
    DPCommJOGSpeed      = (312,('int',0),'rw')
    InternalSpd1        = (316,('int',0),'rw')
    InternalSpd2        = (317,('int',0),'rw')
    InternalSpd3        = (318,('int',0),'rw')
    InternalSpd4        = (319,('int',0),'rw')
    InternalSpd5        = (320,('int',0),'rw')
    InternalSpd6        = (321,('int',0),'rw')
    InternalSpd7        = (322,('int',0),'rw')
    #############Torque control related parameters#############
    TorqueRefGain       = (400,('int',0),'rw')
    FwdQInternalLimit   = (401,('int',0),'rw')
    RevQInternalLimit   = (402,('int',0),'rw')
    FwdExternalQLimit   = (403,('int',0),'rw')
    RevExternalQLimit   = (404,('int',0),'rw')
    PlugBrakingQLimit   = (405,('int',0),'rw')
    SpdLimitDQControl   = (406,('int',0),'rw')
    NotchFilter1Freq    = (407,('int',0),'rw')
    NotchFilter1Depth   = (408,('int',0),'rw')
    NotchFilter2Freq    = (409,('int',0),'rw')
    NotchFilter2Depth   = (410,('int',0),'rw')
    LFreqJitterFreq     = (411,('int',0),'rw')
    LFreqJitterDamp     = (412,('int',0),'rw')
    TorqueCtrlDelayT    = (413,('int',0),'rw')
    TorqueCtrlSpdHys    = (414,('int',0),'rw')
    AnalogQGivenZBias   = (415,('int',0),'rw')
    #############Parameters to control I/O port#############
    PositioningError    = (500,('int',0),'rw')
    CoincidenceDiff     = (501,('int',0),'rw')
    ZeroClampSpd        = (502,('int',0),'rw')
    RotDetectionSpdTGON = (503,('int',0),'rw')
    OffsetCntOverflowAlm= (504,('int',0),'rw')
    ServoONWaitingTime  = (505,('int',0),'rw')
    BasicWaitingFlow    = (506,('int',0),'rw')
    BrakeWaitingSpeed   = (507,('int',0),'rw')
    BrakeWaitingTime    = (508,('int',0),'rw')
    AllocateCN1_14ToTerm= (509,('hex',0),'rw')
    AllocateCN1_14ToTerm_values = {
        'S-ON':0,
        'P-CON':1,
        'P-OT':2,
        'N-OT':3,
        'ALMRST':4,
        'CLR':5,
        'P-CL':6,
        'N-CL':7,
        'G-SEL':8,
        'JDPOS-JOG+':9,
        'JDPOS-JOG-':10,
        'JDPOS-HALT':11,
        'HmRef':12,
        'SHOM':13,
        'ORG':14}
    AllocateCN1_15ToTerm= (509,('hex',1),'rw')
    AllocateCN1_15ToTerm_values = AllocateCN1_14ToTerm_values #The same values
    AllocateCN1_16ToTerm= (509,('hex',2),'rw')
    AllocateCN1_16ToTerm_values = AllocateCN1_14ToTerm_values #The same values
    AllocateCN1_17ToTerm= (509,('hex',3),'rw')
    AllocateCN1_17ToTerm_values = AllocateCN1_14ToTerm_values #The same values
    AllocateCN1_39ToTerm= (510,('hex',0),'rw')
    AllocateCN1_39ToTerm_values = AllocateCN1_14ToTerm_values #The same values
    AllocateCN1_40ToTerm= (511,('hex',1),'rw')
    AllocateCN1_40ToTerm_values = AllocateCN1_14ToTerm_values #The same values
    AllocateCN1_41ToTerm= (512,('hex',2),'rw')
    AllocateCN1_41ToTerm_values = AllocateCN1_14ToTerm_values #The same values 
    AllocateCN1_42ToTerm= (513,('hex',3),'rw')
    AllocateCN1_42ToTerm_values = AllocateCN1_14ToTerm_values #The same values
    AllocCN1_11t12ToTerm= (511,('int',0),'rw')
    AllocCN1_11t12ToTerm_values = {
        '/COIN/VMCP':0,
        '/TGON':1,
        '/S-RDY':2,
        '/CLT':3,
        '/BK':4,
        '/PGC':5,
        'OT':6,
        '/RD':7,
        '/HOME':8}
    AllocCN1_05t06ToTerm= (511,('int',1),'rw')
    AllocCN1_05t06ToTerm_values = AllocCN1_11t12ToTerm_values #The same values
    AllocCN1_09t10ToTerm= (511,('int',2),'rw')
    AllocCN1_09t10ToTerm_values = AllocCN1_11t12ToTerm_values #The same values
    BusCtrlInputNode1_14= (512,('bit',0),'rw') #Low bit - Enabled
    BusCtrlInputNode1_15= (512,('bit',1),'rw')
    BusCtrlInputNode1_16= (512,('bit',2),'rw')
    BusCtrlInputNode1_17= (512,('bit',3),'rw')
    BusCtrlInputNode1_39= (513,('bit',0),'rw')
    BusCtrlInputNode1_40= (513,('bit',1),'rw')
    BusCtrlInputNode1_41= (513,('bit',2),'rw')
    BusCtrlInputNode1_42= (513,('bit',3),'rw')
    InputPortFilter     = (514,('int',0),'rw')
    IPortInversion1_14  = (516,('bit',0),'rw') #High bit - Enabled
    IPortInversion1_15  = (516,('bit',1),'rw')
    IPortInversion1_15  = (516,('bit',2),'rw')
    IPortInversion1_16  = (516,('bit',3),'rw')
    IPortInversion1_39  = (517,('bit',0),'rw')
    IPortInversion1_40  = (517,('bit',1),'rw')
    IPortInversion1_41  = (517,('bit',2),'rw')
    IPortInversion1_42  = (517,('bit',3),'rw')
    ExtRegenerativeRes  = (521,('bit',0),'rw')
    ExtRegenerativeRes_values = {
        'ConnectExternallyRegenerativeResistor':0,
        'DoesNotConnectExternallyRegenerativeResistor':1}
    #############Point-to-Point control related parameters#############
    PosPulseInPtPCtrl00 = (600,('int',0),'rw') #10k pulses per unit
    PosPulseInPtPCtrl01 = (601,('int',0),'rw') #1 pulse per unit
    PosPulseInPtPCtrl02 = (602,('int',0),'rw')
    PosPulseInPtPCtrl03 = (603,('int',0),'rw')
    PosPulseInPtPCtrl04 = (604,('int',0),'rw')
    PosPulseInPtPCtrl05 = (605,('int',0),'rw')
    PosPulseInPtPCtrl06 = (606,('int',0),'rw')
    PosPulseInPtPCtrl07 = (607,('int',0),'rw')
    PosPulseInPtPCtrl08 = (608,('int',0),'rw')
    PosPulseInPtPCtrl09 = (609,('int',0),'rw')
    PosPulseInPtPCtrl10 = (610,('int',0),'rw')
    PosPulseInPtPCtrl11 = (611,('int',0),'rw')
    PosPulseInPtPCtrl12 = (612,('int',0),'rw')
    PosPulseInPtPCtrl13 = (613,('int',0),'rw')
    PosPulseInPtPCtrl14 = (614,('int',0),'rw')
    PosPulseInPtPCtrl15 = (615,('int',0),'rw')
    PosPulseInPtPCtrl16 = (616,('int',0),'rw')
    PosPulseInPtPCtrl17 = (617,('int',0),'rw')
    PosPulseInPtPCtrl18 = (618,('int',0),'rw')
    PosPulseInPtPCtrl19 = (619,('int',0),'rw')
    PosPulseInPtPCtrl20 = (620,('int',0),'rw')
    PosPulseInPtPCtrl21 = (621,('int',0),'rw')
    PosPulseInPtPCtrl22 = (622,('int',0),'rw')
    PosPulseInPtPCtrl23 = (623,('int',0),'rw')
    PosPulseInPtPCtrl24 = (624,('int',0),'rw')
    PosPulseInPtPCtrl25 = (625,('int',0),'rw')
    PosPulseInPtPCtrl26 = (626,('int',0),'rw')
    PosPulseInPtPCtrl27 = (627,('int',0),'rw')
    PosPulseInPtPCtrl28 = (628,('int',0),'rw')
    PosPulseInPtPCtrl29 = (629,('int',0),'rw')
    PosPulseInPtPCtrl30 = (630,('int',0),'rw')
    PosPulseInPtPCtrl31 = (631,('int',0),'rw')
    PtPSpeedCtrl00      = (632,('int',0),'rw')
    PtPSpeedCtrl01      = (633,('int',0),'rw')
    PtPSpeedCtrl02      = (634,('int',0),'rw')
    PtPSpeedCtrl03      = (635,('int',0),'rw')
    PtPSpeedCtrl04      = (636,('int',0),'rw')
    PtPSpeedCtrl05      = (637,('int',0),'rw')
    PtPSpeedCtrl06      = (638,('int',0),'rw')
    PtPSpeedCtrl07      = (639,('int',0),'rw')
    PtPSpeedCtrl08      = (640,('int',0),'rw')
    PtPSpeedCtrl09      = (641,('int',0),'rw')
    PtPSpeedCtrl10      = (642,('int',0),'rw')
    PtPSpeedCtrl11      = (643,('int',0),'rw')
    PtPSpeedCtrl12      = (644,('int',0),'rw')
    PtPSpeedCtrl13      = (645,('int',0),'rw')
    PtPSpeedCtrl14      = (646,('int',0),'rw')
    PtPSpeedCtrl15      = (647,('int',0),'rw')
    PtPFrstOrderFilter00= (648,('int',0),'rw')
    PtPFrstOrderFilter01= (649,('int',0),'rw')
    PtPFrstOrderFilter02= (650,('int',0),'rw')
    PtPFrstOrderFilter03= (651,('int',0),'rw')
    PtPFrstOrderFilter04= (652,('int',0),'rw')
    PtPFrstOrderFilter05= (653,('int',0),'rw')
    PtPFrstOrderFilter06= (654,('int',0),'rw')
    PtPFrstOrderFilter07= (655,('int',0),'rw')
    PtPFrstOrderFilter08= (656,('int',0),'rw')
    PtPFrstOrderFilter09= (657,('int',0),'rw')
    PtPFrstOrderFilter10= (658,('int',0),'rw')
    PtPFrstOrderFilter11= (659,('int',0),'rw')
    PtPFrstOrderFilter12= (660,('int',0),'rw')
    PtPFrstOrderFilter13= (661,('int',0),'rw')
    PtPFrstOrderFilter14= (662,('int',0),'rw')
    PtPFrstOrderFilter15= (663,('int',0),'rw')
    StopTime00          = (663,('int',0),'rw')
    StopTime01          = (664,('int',0),'rw')
    StopTime02          = (665,('int',0),'rw')
    StopTime03          = (666,('int',0),'rw')
    StopTime04          = (667,('int',0),'rw')
    StopTime05          = (668,('int',0),'rw')
    StopTime06          = (669,('int',0),'rw')
    StopTime07          = (670,('int',0),'rw')
    StopTime08          = (671,('int',0),'rw')
    StopTime09          = (672,('int',0),'rw')
    StopTime10          = (673,('int',0),'rw')
    StopTime11          = (674,('int',0),'rw')
    StopTime12          = (675,('int',0),'rw')
    StopTime13          = (676,('int',0),'rw')
    StopTime14          = (677,('int',0),'rw')
    StopTime15          = (678,('int',0),'rw')
    StopTime16          = (679,('int',0),'rw')
    SingCyStartRef      = (681,('hex',0),'rw')
    SingCyStartRef_values = {
        'CyclicOperation-PCLStart-NCLSearch':0,
        'SingleOperation-PCLStart-NCLSearch':1,
        'CyclicOperation-NCLStart-PCLSearch':2,
        'SingleOperation-NCLStart-PCLSearch':3}
    ChangeStepnStartMode= (681,('hex',1),'rw')
    ChangeStepnStartMode = {
        'DelayToChangeStep,DelayToStartAfterS-ON':0,
        'PCONToChangeStep,PCONdelayToStart':1,
        'DelayToChangeStep,StartSignal':2,
        'PCONToChangeStep,StartSignal':3}
    ChangeStepInputMode = (681,('hex',2),'rw')
    ChangeStepInputMode_values = {
        'ElectricalLevelMode':0,
        'SignalPulseMode':1}
    ProgrammeMode       = (682,('bit',0),'rw')
    ProgrammeMode_values = {
        'Incremental':0,
        'Absolute':1}
    ProgrammeStartStep  = (683,('int',0),'rw')
    ProgrammeStopStep   = (684,('int',0),'rw')
    STravelSpdInPosCtrl = (685,('int',0),'rw') #Two meanings depends on ControlMode register
    SpdFindRefPtInHCtrlH= (685,('int',0),'rw') #   #Hitting the ref point
    LvTravelSwInPosCtrl = (686,('int',0),'rw') #
    SpdFindRefPtInHCtrlL= (686,('int',0),'rw') #   #Leaving the ref point
    PosTeachingPulse10k = (687,('int',0),'rw')     #10k pulses per unit
    PosTeachingPulse    = (688,('int',0),'rw')     #1 pulse per unit
    HomingModeSetting   = (689,('bit',0),'rw')
    HomingModeSetting_values = {
        'HomingForvard':0,
        'HomingReverse':1}
    SearchCPulseHoming  = (689,('bit',1),'rw')
    SearchCPulseHoming_values = {
        'ReturnToSearchCPulse':0,
        'DirectlySearchCPulse':1}
    HomingTrigStarting  = (689,('bit',2),'rw')
    HomingTrigStarting_values = {
        'HomingDisabled':0,
        'HomingTriggeredBySHOM':1}
    NumberErrsDHoming10k= (690,('int',0),'rw')     #10k pulses per unit
    NumberErrsDHoming   = (691,('int',0),'rw')     #1 pulse per unit
    #############Communication parameters#############
    MODBUSBaudrate      = (700,('hex',0),'rw')
    MODBUSBaudrate_values = {
        '4800':0,
        '9600':1,
        '19200':2}
    MODBUSProtocol      = (700,('hex',1),'rw')
    MODBUSProtocol_values = {
        '7bits,Parity=NONE,StopBits=2,MODBUS ASCII':0,
        '7bits,Parity=Even,StopBits=1,MODBUS ASCII':1,
        '7bits,Parity=Odd,StopBits=1,MODBUS ASCII':2,
        '8bits,Parity=NONE,StopBits=2,MODBUS ASCII':3,
        '8bits,Parity=Even,StopBits=1,MODBUS ASCII':4,
        '8bits,Parity=Odd,StopBits=1,MODBUS ASCII':5,
        '8bits,Parity=NONE,StopBits=2,MODBUS RTU':6,
        '8bits,Parity=Even,StopBits=1,MODBUS RTU':7,
        '8bits,Parity=Odd,StopBits=1,MODBUS RTU':8}
    CommProtocol        = (700,('hex',2),'rw')
    CommProtocol_values = {
        'NoSCI':0,
        'MODBUSSCI':1}
    MODBUSAxisAdress    = (701,('int',0),'rw')
    CANSpeed            = (703,('int',0),'rw')
    CANSpeed_values = {
        '50k':0,
        '100k':1,
        '125k':2,
        '250k':3,
        '500k':4,
        '1M':5}
    CANContact          = (704,('int',0),'rw')
    EncoderModel        = (840,('hex',0),'rw')
    EncoderModel_values = {
        '17bitAbsEncoder':3,
        '17bitIncEncoder':4,
        'Resolver':5,
        'IncrementalWire-savingEncoder':6} #2500P/R
    #################Alarms to read#####################
    Alarm0              = (0x7F1,('int',0),'r') #Latest alarm
    Alarm1              = (0x7F2,('int',0),'r')
    Alarm2              = (0x7F3,('int',0),'r')
    Alarm3              = (0x7F4,('int',0),'r')
    Alarm4              = (0x7F5,('int',0),'r')
    Alarm5              = (0x7F6,('int',0),'r')
    Alarm6              = (0x7F7,('int',0),'r')
    Alarm7              = (0x7F8,('int',0),'r')
    Alarm8              = (0x7F9,('int',0),'r')
    Alarm9              = (0x7FA,('int',0),'r')
    ##################Offsets to read###################
    SpeedRefZeroOffset  = (0x7FB,('int',0),'r')
    TorqueRefZeroOffset = (0x7FC,('int',0),'r')
    luZeroOffset        = (0x7FD,('int',0),'r')
    lvZeroOffset        = (0x7FE,('int',0),'r')
    ##################Monitoring registers##############
    SpeedFedback        = (0x806,('int',0),'r')
    InputSpeedRefValue  = (0x807,('int',0),'r')
    InputTorqueRefPerc  = (0x808,('int',0),'r')
    InternTorqueRefPerc = (0x809,('int',0),'r')
    EncRotationPulses   = (0x80A,('int',0),'r')
    InputSignalState    = (0x80B,('int',0),'r')
    EncSignalState      = (0x80C,('int',0),'r')
    OutputSignalState   = (0x80D,('int',0),'r')
    PulseSetting        = (0x80E,('int',0),'r')
    LowbitsOfpresentPos = (0x80F,('int',0),'r') #1 pulse per unit
    HighbitsOfpresentPos= (0x810,('int',0),'r') #10k pulses per unit
    ErrPulseCntLSBs     = (0x811,('int',0),'r')
    ErrPulseCNtMSBs     = (0x812,('int',0),'r')
    SettingPulseCntLSBs = (0x813,('int',0),'r') #1 pulse per unit
    SettingPulseCntMSBs = (0x814,('int',0),'r') #10k pulses per unit
    LoadInertiaPercValue= (0x815,('int',0),'r')
    ServoOverloadingProp= (0x816,('int',0),'r')
    CurrentAlarm        = (0x817,('int',0),'r')
    #############MODBUS Control IO Signals#############
    MODBUSIO            = (0x900,('int',0),'rw')
    #############Version###############################
    DSPver              = (0x90E,('int',0),'r')
    CPLDver             = (0x90F,('int',0),'r')
    #################Special Registers#################
    EncoderRevolutions  = (0x1010,('int',0),'r')
    EncoderPoseLSBs     = (0x1011,('int',0),'r')
    EncoderPoseMSBs     = (0x1012,('int',0),'r')
    ClearHistAlarms     = (0x1021,('int',0),'w') #0x01 to clear
    ClearCurrentAlarms  = (0x1022,('int',0),'w') #0x01 to clear
    JOGEnable           = (0x1023,('int',0),'rw')
    JOGEnable_values = {
        'ENABLE':1,
        'Disable':0}
    JOGForvardRot       = (0x1024,('int',0),'rw')
    JOGForvardRot_values = {
        'FORVARD':1,
        'STOP':0}
    JOGReverseRot       = (0x1025,('int',0),'rw')
    JOGReverseRot_values = {
        'REVERSE':1,
        'STOP':0}
    JOGForvardRotAtNode = (0x1026,('int',0),'rw')
    JOGForvardRotAtNode_values = JOGForvardRot_values
    JOGReverseRotAtNode = (0x1027,('int',0),'rw')
    JOGReverseRotAtNode_values = JOGReverseRot_values
    PauseAtNodePosition = (0x1028,('int',0),'rw')
    ClearEncoderAlarm   = (0x1040,('int',0),'w') #0x01 to clear
    ClrEncMultiturnData = (0x1041,('int',0),'w') #0x01 to clear #Corresponding to EncoderRevolutions and EncoderPose registers
    ##################Alarm codes#######################
    AlarmCodes = {
        '00':'Not an error',
        '01':'Parameter breakdown',
        '02':'AD shift channels breakdown',
        '03':'Overspeed',
        '04':'Overload',
        '05':'Position error counter overflow',
        '06':'Position error pulse overflow',
        '07':'The setting of electronic gear or given pulse is not reasonable',
        '08':'The 1st channel of current detection is wrong',
        '09':'The 2nd channel of current detection is wrong',
        '10':'Incremental encoder is break off',
        '11':'',
        '12':'Overcurrent',
        '13':'Overvoltage',
        '14':'Undervoltage',
        '15':'Bleeder resistor error',
        '16':'Regeneration error',
        '17':'Resolver error',
        '18':'IGBT superheat alarm',
        '19':'',
        '20':'Power line open phase',
        '21':'Instantaneous power off alarm',
        '22':'', '23':'', '24':'', '25':'',
        '26':'', '27':'', '28':'', '29':'',
        '30':'', '31':'', '32':'', '33':'',
        '34':'', '35':'', '36':'', '37':'',
        '38':'', '39':'', '40':'', '41':'',
        '42':'Servomotor type error',
        '43':'Servodrive type error',
        '44':'',
        '45':'Absolute encoder multiturn information error',
        '46':'Absolute encoder multiturn information overflow',
        '47':'Baterry voltage below 2.5V',
        '48':'Baterry voltage below 3.1V',
        '49':'',
        '50':'Serial encoder communication overtime',
        '51':'Absolute encoder overspeed alarm detected',
        '52':'Absolute state of serial encoder error',
        '53':'Serial encoder calculation error',
        '54':'Parity bit or end bit in serial encoder control domain error',
        '55':'Serial encoder communication data checking error',
        '56':'End bit in serial encoder control domain error',
        '57':'',
        '58':'Serial encoder data empty',
        '59':'Serial encoder data format error',
        '60':'Communication module not detected',
        '61':'Communication unsuccessfull',
        '62':'Servodrive can not receive the period data of communication module',
        '63':'Communication module can not receive the servodrive response data',
        '64':'Communication module and bus connectionless',
        '65':'',
        '66':'CAN communication abnormal',
        '67':'Receiving heartbeat timeout',
        '68':'',
        '69':'Synchronisation signal monitoring cycle is longer than setting'}
    ###############Parameter types####################
    WRITE_ONLY = 'w'
    READ_ONLY = 'r'
    READ_WRITE = 'rw'

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)