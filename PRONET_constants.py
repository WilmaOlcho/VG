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
    SERVO_ON            = (0,('bit',0)) #register adress, bitdeclaration, bitnumber
    P_OT                = (0,('bit',1))
    N_OT                = (0,('bit',2))
    Alarm_O             = (0,('bit',3))
    CCW                 = (1,('bit',0))
    Analog_Vlimit       = (1,('bit',1))
    Analog_Tlimit       = (1,('bit',2))
    ElectronicGear2     = (1,('bit',3))
    EGswitchingMode     = (2,('bit',0))
    ABSencoderselect    = (2,('bit',2))
    LSpeedcomp          = (3,('bit',2))
    OverloadEnhcmt      = (3,('bit',3))
    StopMode            = (4,('hex',0)) #register adress, hex value declaration (4bits), position in register
    ErrCntClrMode       = (4,('hex',1))
    RefPulseForm        = (4,('hex',2))
    InversePulse        = (4,('hex',3))
    QfeedforwMode       = (5,('hex',0))
    ControlMode         = (5,('hex',1))
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
    OOTAlarmSelect      = (5,('hex',2))
    ServomotorModel     = (5,('hex',3))
    BusMode             = (6,('hex',0))
    LFreqJitterSupSw    = (6,('hex',2))
    RefInFilterforOC    = (6,('hex',3))
    #############Parameters of servo gain#############
    OnlineAutotuning    = (100,('int',0)) #Register adress, int value
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
    MachineRigidity     = (101,('int',0))
    SpeedLoopGain       = (102,('int',0))
    SpdLoopIntTConst    = (103,('int',0))
    PosLoopGain         = (104,('int',0))
    QRefFilterTConst    = (105,('int',0))
    LoadInertiaPerc     = (106,('int',0))
    SpeedLoopGain2      = (107,('int',0))
    SpdLoopIntTConst2   = (108,('int',0))
    PosLoopGain2        = (109,('int',0))
    QRefFilterTConst2   = (110,('int',0))
    SpeedBias           = (111,('int',0))
    Feedforward         = (112,('int',0))
    FeedforvardFilter   = (113,('int',0))
    TorqueFeedforvard   = (114,('int',0))
    TorqueFeedforvardFil= (115,('int',0))
    PPISwCondition      = (116,('int',0))
    PPISwCondition_values = {
        'TorqueReferencePercentage':0,
        'ValueOfOffsetCounter':1,
        'ValueOfAccelerationSpeedSetting':2,
        'ValueOfSpeedSetting':3,
        'FixedPI':4}
    TorqueSwTreshold    = (117,('int',0))
    OffsetCntSwTreshold = (118,('int',0))
    SetAccSpdSwTreshhold= (119,('int',0))
    SetSpdSwTreshhold   = (120,('int',0))
    GainSwCondition     = (121,('int',0))
    GainSwCondition_values = {
        'FixTo1stGroupGain':0,
        'ExtSwGainSwitching':1,
        'TorquePercentage':2,
        'ValueOfOffsetCnt':3,
        'ValueOfAccSpdSet':4,
        'ValueOfSpdSet':5,
        'SpdRefInput':6}
    SwitchindDelayTime  = (122,('int',0))
    TresholdSwitchingLvl= (123,('int',0))
    PosGainSwTime       = (125,('int',0))
    HysteresisSwitching = (126,('int',0))
    LowSpdDetectFilter  = (127,('int',0))
    SpdGainAccrelDOAutot= (128,('int',0))
    LowSpdCorrectionCoef= (129,('int',0))
    FrictionLoad        = (130,('int',0))
    FrictCompSpdHysArea = (131,('int',0))
    StickingFrictLoad   = (132,('int',0))
    #############Position control related parameters#############
    PGDividedRatio      = (200,('int',0))
    EGear1Numerator     = (201,('int',0))
    EGear1Denominator   = (202,('int',0))
    EGear2Numerator     = (203,('int',0))
    PosRefAccDeccTConst = (204,('int',0))
    PosRefFilterFormSel = (205,('int',0))
    #############Speed control related parameters#############
    SpdRefInputGain     = (300,('int',0))
    AnalogSpdGivenZBias = (301,('int',0))
    ParameterSpeed      = (304,('int',0))
    JOGSpeed            = (305,('int',0))
    SoftStartAccTime    = (306,('int',0))
    SoftStartDecelTime  = (307,('int',0))
    SpdFilterTimeConst  = (308,('int',0))
    SCurveRisetime      = (309,('int',0))
    SpdRefCurveForm     = (310,('int',0))
    SpdRefCurveForm_values = {
        'Slope':0,
        'SCurve':1,
        'FstOrderFilter':2,
        'ScndOrderFilter':3}
    SFormSelection      = (311,('int',0))
    SFormSelection_values = {
        'Slope':0,
        'SCurve':1,
        'FstOrderFilter':2,
        'ScndOrderFilter':3}
    DPCommJOGSpeed      = (312,('int',0))
    InternalSpd1        = (316,('int',0))
    InternalSpd2        = (317,('int',0))
    InternalSpd3        = (318,('int',0))
    InternalSpd4        = (319,('int',0))
    InternalSpd5        = (320,('int',0))
    InternalSpd6        = (321,('int',0))
    InternalSpd7        = (322,('int',0))
    #############Torque control related parameters#############
    TorqueRefGain       = (400,('int',0))
    FwdQInternalLimit   = (401,('int',0))
    RevQInternalLimit   = (402,('int',0))
    FwdExternalQLimit   = (403,('int',0))
    RevExternalQLimit   = (404,('int',0))
    PlugBrakingQLimit   = (405,('int',0))
    SpdLimitDQControl   = (406,('int',0))
    NotchFilter1Freq    = (407,('int',0))
    NotchFilter1Depth   = (408,('int',0))
    NotchFilter2Freq    = (409,('int',0))
    NotchFilter2Depth   = (410,('int',0))
    LFreqJitterFreq     = (411,('int',0))
    LFreqJitterDamp     = (412,('int',0))
    TorqueCtrlDelayT    = (413,('int',0))
    TorqueCtrlSpdHys    = (414,('int',0))
    AnalogQGivenZBias   = (415,('int',0))
    #############Parameters to control I/O port#############
    PositioningError    = (500,('int',0))
    CoincidenceDiff     = (501,('int',0))
    ZeroClampSpd        = (502,('int',0))
    RotDetectionSpdTGON = (503,('int',0))
    OffsetCntOverflowAlm= (504,('int',0))
    ServoONWaitingTime  = (505,('int',0))
    BasicWaitingFlow    = (506,('int',0))
    BrakeWaitingSpeed   = (507,('int',0))
    BrakeWaitingTime    = (508,('int',0))
    AllocateCN1_14ToTerm= (509,('hex',0))
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
    AllocateCN1_15ToTerm= (509,('hex',1))
    AllocateCN1_15ToTerm_values = AllocateCN1_14ToTerm_values #The same values
    AllocateCN1_16ToTerm= (509,('hex',2))
    AllocateCN1_16ToTerm_values = AllocateCN1_14ToTerm_values #The same values
    AllocateCN1_17ToTerm= (509,('hex',3))
    AllocateCN1_17ToTerm_values = AllocateCN1_14ToTerm_values #The same values
    AllocateCN1_39ToTerm= (510,('hex',0))
    AllocateCN1_39ToTerm_values = AllocateCN1_14ToTerm_values #The same values
    AllocateCN1_40ToTerm= (511,('hex',1))
    AllocateCN1_40ToTerm_values = AllocateCN1_14ToTerm_values #The same values
    AllocateCN1_41ToTerm= (512,('hex',2))
    AllocateCN1_41ToTerm_values = AllocateCN1_14ToTerm_values #The same values 
    AllocateCN1_42ToTerm= (513,('hex',3))
    AllocateCN1_42ToTerm_values = AllocateCN1_14ToTerm_values #The same values
    AllocCN1_11t12ToTerm= (511,('int',0))
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
    AllocCN1_05t06ToTerm= (511,('int',1))
    AllocCN1_05t06ToTerm_values = AllocCN1_11t12ToTerm_values #The same values
    AllocCN1_09t10ToTerm= (511,('int',2))
    AllocCN1_09t10ToTerm_values = AllocCN1_11t12ToTerm_values #The same values
    BusCtrlInputNode1_14= (512,('bit',0)) #Low bit - Enabled
    BusCtrlInputNode1_15= (512,('bit',1))
    BusCtrlInputNode1_16= (512,('bit',2))
    BusCtrlInputNode1_17= (512,('bit',3))
    BusCtrlInputNode1_39= (513,('bit',0))
    BusCtrlInputNode1_40= (513,('bit',1))
    BusCtrlInputNode1_41= (513,('bit',2))
    BusCtrlInputNode1_42= (513,('bit',3))
    InputPortFilter     = (514,('int',0))
    IPortInversion1_14  = (516,('bit',0)) #High bit - Enabled
    IPortInversion1_15  = (516,('bit',1))
    IPortInversion1_15  = (516,('bit',2))
    IPortInversion1_16  = (516,('bit',3))
    IPortInversion1_39  = (517,('bit',0))
    IPortInversion1_40  = (517,('bit',1))
    IPortInversion1_41  = (517,('bit',2))
    IPortInversion1_42  = (517,('bit',3))
    ExtRegenerativeRes  = (521,('bit',0))
    ExtRegenerativeRes_values = {
        'ConnectExternallyRegenerativeResistor':0,
        'DoesNotConnectExternallyRegenerativeResistor':1}
    #############Point-to-Point control related parameters#############
    PosPulseInPtPCtrl00 = (600,('int',0)) #10k pulses per unit
    PosPulseInPtPCtrl01 = (601,('int',0)) #1 pulse per unit
    PosPulseInPtPCtrl02 = (602,('int',0))
    PosPulseInPtPCtrl03 = (603,('int',0))
    PosPulseInPtPCtrl04 = (604,('int',0))
    PosPulseInPtPCtrl05 = (605,('int',0))
    PosPulseInPtPCtrl06 = (606,('int',0))
    PosPulseInPtPCtrl07 = (607,('int',0))
    PosPulseInPtPCtrl08 = (608,('int',0))
    PosPulseInPtPCtrl09 = (609,('int',0))
    PosPulseInPtPCtrl10 = (610,('int',0))
    PosPulseInPtPCtrl11 = (611,('int',0))
    PosPulseInPtPCtrl12 = (612,('int',0))
    PosPulseInPtPCtrl13 = (613,('int',0))
    PosPulseInPtPCtrl14 = (614,('int',0))
    PosPulseInPtPCtrl15 = (615,('int',0))
    PosPulseInPtPCtrl16 = (616,('int',0))
    PosPulseInPtPCtrl17 = (617,('int',0))
    PosPulseInPtPCtrl18 = (618,('int',0))
    PosPulseInPtPCtrl19 = (619,('int',0))
    PosPulseInPtPCtrl20 = (620,('int',0))
    PosPulseInPtPCtrl21 = (621,('int',0))
    PosPulseInPtPCtrl22 = (622,('int',0))
    PosPulseInPtPCtrl23 = (623,('int',0))
    PosPulseInPtPCtrl24 = (624,('int',0))
    PosPulseInPtPCtrl25 = (625,('int',0))
    PosPulseInPtPCtrl26 = (626,('int',0))
    PosPulseInPtPCtrl27 = (627,('int',0))
    PosPulseInPtPCtrl28 = (628,('int',0))
    PosPulseInPtPCtrl29 = (629,('int',0))
    PosPulseInPtPCtrl30 = (630,('int',0))
    PosPulseInPtPCtrl31 = (631,('int',0))
    PtPSpeedCtrl00      = (632,('int',0))
    PtPSpeedCtrl01      = (633,('int',0))
    PtPSpeedCtrl02      = (634,('int',0))
    PtPSpeedCtrl03      = (635,('int',0))
    PtPSpeedCtrl04      = (636,('int',0))
    PtPSpeedCtrl05      = (637,('int',0))
    PtPSpeedCtrl06      = (638,('int',0))
    PtPSpeedCtrl07      = (639,('int',0))
    PtPSpeedCtrl08      = (640,('int',0))
    PtPSpeedCtrl09      = (641,('int',0))
    PtPSpeedCtrl10      = (642,('int',0))
    PtPSpeedCtrl11      = (643,('int',0))
    PtPSpeedCtrl12      = (644,('int',0))
    PtPSpeedCtrl13      = (645,('int',0))
    PtPSpeedCtrl14      = (646,('int',0))
    PtPSpeedCtrl15      = (647,('int',0))
    PtPFrstOrderFilter00= (648,('int',0))
    PtPFrstOrderFilter01= (649,('int',0))
    PtPFrstOrderFilter02= (650,('int',0))
    PtPFrstOrderFilter03= (651,('int',0))
    PtPFrstOrderFilter04= (652,('int',0))
    PtPFrstOrderFilter05= (653,('int',0))
    PtPFrstOrderFilter06= (654,('int',0))
    PtPFrstOrderFilter07= (655,('int',0))
    PtPFrstOrderFilter08= (656,('int',0))
    PtPFrstOrderFilter09= (657,('int',0))
    PtPFrstOrderFilter10= (658,('int',0))
    PtPFrstOrderFilter11= (659,('int',0))
    PtPFrstOrderFilter12= (660,('int',0))
    PtPFrstOrderFilter13= (661,('int',0))
    PtPFrstOrderFilter14= (662,('int',0))
    PtPFrstOrderFilter15= (663,('int',0))
    StopTime00          = (663,('int',0))
    StopTime01          = (664,('int',0))
    StopTime02          = (665,('int',0))
    StopTime03          = (666,('int',0))
    StopTime04          = (667,('int',0))
    StopTime05          = (668,('int',0))
    StopTime06          = (669,('int',0))
    StopTime07          = (670,('int',0))
    StopTime08          = (671,('int',0))
    StopTime09          = (672,('int',0))
    StopTime10          = (673,('int',0))
    StopTime11          = (674,('int',0))
    StopTime12          = (675,('int',0))
    StopTime13          = (676,('int',0))
    StopTime14          = (677,('int',0))
    StopTime15          = (678,('int',0))
    StopTime16          = (679,('int',0))
    SingCyStartRef      = (681,('hex',0))
    SingCyStartRef_values = {
        'CyclicOperation-PCLStart-NCLSearch':0,
        'SingleOperation-PCLStart-NCLSearch':1,
        'CyclicOperation-NCLStart-PCLSearch':2,
        'SingleOperation-NCLStart-PCLSearch':3}
    ChangeStepnStartMode= (681,('hex',1))
    ChangeStepnStartMode = {
        'DelayToChangeStep,DelayToStartAfterS-ON':0,
        'PCONToChangeStep,PCONdelayToStart':1,
        'DelayToChangeStep,StartSignal':2,
        'PCONToChangeStep,StartSignal':3}
    ChangeStepInputMode = (681,('hex',2))
    ChangeStepInputMode_values = {
        'ElectricalLevelMode':0,
        'SignalPulseMode':1}
    ProgrammeMode       = (682,('bit',0))
    ProgrammeMode_values = {
        'Incremental':0,
        'Absolute':1}
    ProgrammeStartStep  = (683,('int',0))
    ProgrammeStopStep   = (684,('int',0))
    STravelSpdInPosCtrl = (685,('int',0)) #Two meanings depends on ControlMode register
    SpdFindRefPtInHCtrlH= (685,('int',0)) #   #Hitting the ref point
    LvTravelSwInPosCtrl = (686,('int',0)) #
    SpdFindRefPtInHCtrlL= (686,('int',0)) #   #Leaving the ref point
    PosTeachingPulse10k = (687,('int',0))     #10k pulses per unit
    PosTeachingPulse    = (688,('int',0))     #1 pulse per unit
    HomingModeSetting   = (689,('bit',0))
    HomingModeSetting_values = {
        'HomingForvard':0,
        'HomingReverse':1}
    SearchCPulseHoming  = (689,('bit',1))
    SearchCPulseHoming_values = {
        'ReturnToSearchCPulse':0,
        'DirectlySearchCPulse':1}
    HomingTrigStarting  = (689,('bit',2))
    HomingTrigStarting_values = {
        'HomingDisabled':0,
        'HomingTriggeredBySHOM':1}
    NumberErrsDHoming10k= (690,('int',0))     #10k pulses per unit
    NumberErrsDHoming   = (691,('int',0))     #1 pulse per unit
    #############Communication parameters#############
    MODBUSBaudrate      = (700,('hex',0))
    MODBUSBaudrate_values = {
        '4800':0,
        '9600':1,
        '19200':2}
    MODBUSProtocol      = (700,('hex',1))
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
    CommProtocol        = (700,('hex',2))
    CommProtocol_values = {
        'NoSCI':0,
        'MODBUSSCI':1}
    MODBUSAxisAdress    = (701,('int',0))
    CANSpeed            = (703,('int',0))
    CANSpeed_values = {
        '50k':0,
        '100k':1,
        '125k':2,
        '250k':3,
        '500k':4,
        '1M':5}
    CANContact          = (704,('int',0))
    EncoderModel        = (840,('hex',0))
    EncoderModel_values = {
        '17bitAbsEncoder':3,
        '17bitIncEncoder':4,
        'Resolver':5,
        'IncrementalWire-savingEncoder':6} #2500P/R
    #################Alarms to read#####################
    Alarm0              = (0x7F1,('int',0)) #Latest alarm
    Alarm1              = (0x7F2,('int',0))
    Alarm2              = (0x7F3,('int',0))
    Alarm3              = (0x7F4,('int',0))
    Alarm4              = (0x7F5,('int',0))
    Alarm5              = (0x7F6,('int',0))
    Alarm6              = (0x7F7,('int',0))
    Alarm7              = (0x7F8,('int',0))
    Alarm8              = (0x7F9,('int',0))
    Alarm9              = (0x7FA,('int',0))
    ##################Offsets to read###################
    SpeedRefZeroOffset  = (0x7FB,('int',0))
    TorqueRefZeroOffset = (0x7FC,('int',0))
    luZeroOffset        = (0x7FD,('int',0))
    lvZeroOffset        = (0x7FE,('int',0))
    ##################Monitoring registers##############
    SpeedFedback        = (0x806,('int',0))
    InputSpeedRefValue  = (0x807,('int',0))
    InputTorqueRefPerc  = (0x808,('int',0))
    InternTorqueRefPerc = (0x809,('int',0))
    EncRotationPulses   = (0x80A,('int',0))
    InputSignalState    = (0x80B,('int',0))
    EncSignalState      = (0x80C,('int',0))
    OutputSignalState   = (0x80D,('int',0))
    PulseSetting        = (0x80E,('int',0))
    LowbitsOfpresentPos = (0x80F,('int',0)) #1 pulse per unit
    HighbitsOfpresentPos= (0x810,('int',0)) #10k pulses per unit
    ErrPulseCntLSBs     = (0x811,('int',0))
    ErrPulseCNtMSBs     = (0x812,('int',0))
    SettingPulseCntLSBs = (0x813,('int',0)) #1 pulse per unit
    SettingPulseCntMSBs = (0x814,('int',0)) #10k pulses per unit
    LoadInertiaPercValue= (0x815,('int',0))
    ServoOverloadingProp= (0x816,('int',0))
    CurrentAlarm        = (0x817,('int',0))
    #############MODBUS Control IO Signals#############
    MODBUSIO            = (0x900,('int',0))
    #############Version###############################
    DSPver              = (0x90E,('int',0))
    CPLDver             = (0x90F,('int',0))
    #################Special Registers#################
    EncoderRevolutions  = (0x1010,('int',0))
    EncoderPoseLSBs     = (0x1011,('int',0))
    EncoderPoseMSBs     = (0x1012,('int',0))
    ClearHistAlarms     = (0x1021,('int',0)) #0x01 to clear
    ClearCurrentAlarms  = (0x1022,('int',0)) #0x01 to clear
    JOGEnable           = (0x1023,('int',0))
    JOGEnable_values = {
        'ENABLE':1,
        'Disable':0}
    JOGForvardRot       = (0x1024,('int',0))
    JOGForvardRot_values = {
        'FORVARD':1,
        'STOP':0}
    JOGReverseRot       = (0x1025,('int',0))
    JOGReverseRot_values = {
        'REVERSE':1,
        'STOP':0}
    JOGForvardRotAtNode = (0x1026,('int',0))
    JOGForvardRotAtNode_values = JOGForvardRot_values
    JOGReverseRotAtNode = (0x1027,('int',0))
    JOGReverseRotAtNode_values = JOGReverseRot_values
    PauseAtNodePosition = (0x1028,('int',0))
    ClearEncoderAlarm   = (0x1040,('int',0)) #0x01 to clear
    ClrEncMultiturnData = (0x1041,('int',0)) #0x01 to clear #Corresponding to EncoderRevolutions and EncoderPose registers
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)