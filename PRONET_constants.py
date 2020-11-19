##Directly from PRONET_manual_V1_25.pdf
#
#Title: ProNet Series AC Servo User's Manual
#Version: V1.25
#Vendor: ESTUN AUTOMATION TECHNOLOGY CO., LTD
#Revision: 2012-03, V1.25
#
#
class Pronet_constants(): 
    def __init__(self, *args, **kwargs):
        #############Control mode parameters#############
        self.SERVO_ON            = (0,('bit',0),'rw') #register adress, bitdeclaration, bitnumber
        self.P_OT                = (0,('bit',1),'rw')
        self.N_OT                = (0,('bit',2),'rw')
        self.Alarm_O             = (0,('bit',3),'rw')
        self.CCW                 = (1,('bit',0),'rw')
        self.Analog_Vlimit       = (1,('bit',1),'rw')
        self.Analog_Tlimit       = (1,('bit',2),'rw')
        self.ElectronicGear2     = (1,('bit',3),'rw')
        self.EGswitchingMode     = (2,('bit',0),'rw')
        self.ABSencoderselect    = (2,('bit',2),'rw')
        self.LSpeedcomp          = (3,('bit',2),'rw')
        self.OverloadEnhcmt      = (3,('bit',3),'rw')
        self.StopMode            = (4,('hex',0),'rw') #register adress, hex value declaration (4bits), position in register
        self.ErrCntClrMode       = (4,('hex',1),'rw')
        self.RefPulseForm        = (4,('hex',2),'rw')
        self.InversePulse        = (4,('hex',3),'rw')
        self.QfeedforwMode       = (5,('hex',0),'rw')
        self.ControlMode         = (5,('hex',1),'rw')
        self.ControlMode_values  = {
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
        self.OOTAlarmSelect      = (5,('hex',2),'rw')
        self.ServomotorModel     = (5,('hex',3),'rw')
        self.BusMode             = (6,('hex',0),'rw')
        self.LFreqJitterSupSw    = (6,('hex',2),'rw')
        self.RefInFilterforOC    = (6,('hex',3),'rw')
        #############Parameters of servo gain#############
        self.OnlineAutotuning    = (100,('int',0),'rw') #Register adress, int value
        self.OnlineAutotuning_values = {
            'ManualGainAdjustment':0,
            'NormalMode':{
                'WithoutVariation':1,
                'LittleVariation':2,
                'GreatVariation':3},
            'VerticalLoad':{
                'WithoutVariation':4,
                'LittleVariation':5,
                'GreatVariation':6}}
        self.MachineRigidity     = (101,('int',0),'rw')
        self.SpeedLoopGain       = (102,('int',0),'rw')
        self.SpdLoopIntTConst    = (103,('int',0),'rw')
        self.PosLoopGain         = (104,('int',0),'rw')
        self.QRefFilterTConst    = (105,('int',0),'rw')
        self.LoadInertiaPerc     = (106,('int',0),'rw')
        self.SpeedLoopGain2      = (107,('int',0),'rw')
        self.SpdLoopIntTConst2   = (108,('int',0),'rw')
        self.PosLoopGain2        = (109,('int',0),'rw')
        self.QRefFilterTConst2   = (110,('int',0),'rw')
        self.SpeedBias           = (111,('int',0),'rw')
        self.Feedforward         = (112,('int',0),'rw')
        self.FeedforvardFilter   = (113,('int',0),'rw')
        self.TorqueFeedforvard   = (114,('int',0),'rw')
        self.TorqueFeedforvardFil= (115,('int',0),'rw')
        self.PPISwCondition      = (116,('int',0),'rw')
        self.PPISwCondition_values = {
            'TorqueReferencePercentage':0,
            'ValueOfOffsetCounter':1,
            'ValueOfAccelerationSpeedSetting':2,
            'ValueOfSpeedSetting':3,
            'FixedPI':4}
        self.TorqueSwTreshold    = (117,('int',0),'rw')
        self.OffsetCntSwTreshold = (118,('int',0),'rw')
        self.SetAccSpdSwTreshhold= (119,('int',0),'rw')
        self.SetSpdSwTreshhold   = (120,('int',0),'rw')
        self.GainSwCondition     = (121,('int',0),'rw')
        self.GainSwCondition_values = {
            'FixTo1stGroupGain':0,
            'ExtSwGainSwitching':1,
            'TorquePercentage':2,
            'ValueOfOffsetCnt':3,
            'ValueOfAccSpdSet':4,
            'ValueOfSpdSet':5,
            'SpdRefInput':6}
        self.SwitchindDelayTime  = (122,('int',0),'rw')
        self.TresholdSwitchingLvl= (123,('int',0),'rw')
        self.PosGainSwTime       = (125,('int',0),'rw')
        self.HysteresisSwitching = (126,('int',0),'rw')
        self.LowSpdDetectFilter  = (127,('int',0),'rw')
        self.SpdGainAccrelDOAutot= (128,('int',0),'rw')
        self.LowSpdCorrectionCoef= (129,('int',0),'rw')
        self.FrictionLoad        = (130,('int',0),'rw')
        self.FrictCompSpdHysArea = (131,('int',0),'rw')
        self.StickingFrictLoad   = (132,('int',0),'rw')
        #############Position control related parameters#############
        self.PGDividedRatio      = (200,('int',0),'rw')
        self.EGear1Numerator     = (201,('int',0),'rw')
        self.EGear1Denominator   = (202,('int',0),'rw')
        self.EGear2Numerator     = (203,('int',0),'rw')
        self.PosRefAccDeccTConst = (204,('int',0),'rw')
        self.PosRefFilterFormSel = (205,('int',0),'rw')
        #############Speed control related parameters#############
        self.SpdRefInputGain     = (300,('int',0),'rw')
        self.AnalogSpdGivenZBias = (301,('int',0),'rw')
        self.ParameterSpeed      = (304,('int',0),'rw')
        self.JOGSpeed            = (305,('int',0),'rw')
        self.SoftStartAccTime    = (306,('int',0),'rw')
        self.SoftStartDecelTime  = (307,('int',0),'rw')
        self.SpdFilterTimeConst  = (308,('int',0),'rw')
        self.SCurveRisetime      = (309,('int',0),'rw')
        self.SpdRefCurveForm     = (310,('int',0),'rw')
        self.SpdRefCurveForm_values = {
            'Slope':0,
            'SCurve':1,
            'FstOrderFilter':2,
            'ScndOrderFilter':3}
        self.SFormSelection      = (311,('int',0),'rw')
        self.SFormSelection_values = {
            'Slope':0,
            'SCurve':1,
            'FstOrderFilter':2,
            'ScndOrderFilter':3}
        self.DPCommJOGSpeed      = (312,('int',0),'rw')
        self.InternalSpd1        = (316,('int',0),'rw')
        self.InternalSpd2        = (317,('int',0),'rw')
        self.InternalSpd3        = (318,('int',0),'rw')
        self.InternalSpd4        = (319,('int',0),'rw')
        self.InternalSpd5        = (320,('int',0),'rw')
        self.InternalSpd6        = (321,('int',0),'rw')
        self.InternalSpd7        = (322,('int',0),'rw')
        #############Torque control related parameters#############
        self.TorqueRefGain       = (400,('int',0),'rw')
        self.FwdQInternalLimit   = (401,('int',0),'rw')
        self.RevQInternalLimit   = (402,('int',0),'rw')
        self.FwdExternalQLimit   = (403,('int',0),'rw')
        self.RevExternalQLimit   = (404,('int',0),'rw')
        self.PlugBrakingQLimit   = (405,('int',0),'rw')
        self.SpdLimitDQControl   = (406,('int',0),'rw')
        self.NotchFilter1Freq    = (407,('int',0),'rw')
        self.NotchFilter1Depth   = (408,('int',0),'rw')
        self.NotchFilter2Freq    = (409,('int',0),'rw')
        self.NotchFilter2Depth   = (410,('int',0),'rw')
        self.LFreqJitterFreq     = (411,('int',0),'rw')
        self.LFreqJitterDamp     = (412,('int',0),'rw')
        self.TorqueCtrlDelayT    = (413,('int',0),'rw')
        self.TorqueCtrlSpdHys    = (414,('int',0),'rw')
        self.AnalogQGivenZBias   = (415,('int',0),'rw')
        #############Parameters to control I/O port#############
        self.PositioningError    = (500,('int',0),'rw')
        self.CoincidenceDiff     = (501,('int',0),'rw')
        self.ZeroClampSpd        = (502,('int',0),'rw')
        self.RotDetectionSpdTGON = (503,('int',0),'rw')
        self.OffsetCntOverflowAlm= (504,('int',0),'rw')
        self.ServoONWaitingTime  = (505,('int',0),'rw')
        self.BasicWaitingFlow    = (506,('int',0),'rw')
        self.BrakeWaitingSpeed   = (507,('int',0),'rw')
        self.BrakeWaitingTime    = (508,('int',0),'rw')
        self.AllocateCN1_14ToTerm= (509,('hex',0),'rw')
        self.AllocateCN1_14ToTerm_values = {
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
        self.AllocateCN1_15ToTerm= (509,('hex',1),'rw')
        self.AllocateCN1_15ToTerm_values = self.AllocateCN1_14ToTerm_values #The same values
        self.AllocateCN1_16ToTerm= (509,('hex',2),'rw')
        self.AllocateCN1_16ToTerm_values = self.AllocateCN1_14ToTerm_values #The same values
        self.AllocateCN1_17ToTerm= (509,('hex',3),'rw')
        self.AllocateCN1_17ToTerm_values = self.AllocateCN1_14ToTerm_values #The same values
        self.AllocateCN1_39ToTerm= (510,('hex',0),'rw')
        self.AllocateCN1_39ToTerm_values = self.AllocateCN1_14ToTerm_values #The same values
        self.AllocateCN1_40ToTerm= (511,('hex',1),'rw')
        self.AllocateCN1_40ToTerm_values = self.AllocateCN1_14ToTerm_values #The same values
        self.AllocateCN1_41ToTerm= (512,('hex',2),'rw')
        self.AllocateCN1_41ToTerm_values = self.AllocateCN1_14ToTerm_values #The same values 
        self.AllocateCN1_42ToTerm= (513,('hex',3),'rw')
        self.AllocateCN1_42ToTerm_values = self.AllocateCN1_14ToTerm_values #The same values
        self.AllocCN1_11t12ToTerm= (511,('int',0),'rw')
        self.AllocCN1_11t12ToTerm_values = {
            '/COIN/VMCP':0,
            '/TGON':1,
            '/S-RDY':2,
            '/CLT':3,
            '/BK':4,
            '/PGC':5,
            'OT':6,
            '/RD':7,
            '/HOME':8}
        self.AllocCN1_05t06ToTerm= (511,('int',1),'rw')
        self.AllocCN1_05t06ToTerm_values = self.AllocCN1_11t12ToTerm_values #The same values
        self.AllocCN1_09t10ToTerm= (511,('int',2),'rw')
        self.AllocCN1_09t10ToTerm_values = self.AllocCN1_11t12ToTerm_values #The same values
        self.BusCtrlInputNode1_14= (512,('bit',0),'rw') #Low bit - Enabled
        self.BusCtrlInputNode1_15= (512,('bit',1),'rw')
        self.BusCtrlInputNode1_16= (512,('bit',2),'rw')
        self.BusCtrlInputNode1_17= (512,('bit',3),'rw')
        self.BusCtrlInputNode1_39= (513,('bit',0),'rw')
        self.BusCtrlInputNode1_40= (513,('bit',1),'rw')
        self.BusCtrlInputNode1_41= (513,('bit',2),'rw')
        self.BusCtrlInputNode1_42= (513,('bit',3),'rw')
        self.InputPortFilter     = (514,('int',0),'rw')
        self.IPortInversion1_14  = (516,('bit',0),'rw') #High bit - Enabled
        self.IPortInversion1_15  = (516,('bit',1),'rw')
        self.IPortInversion1_15  = (516,('bit',2),'rw')
        self.IPortInversion1_16  = (516,('bit',3),'rw')
        self.IPortInversion1_39  = (517,('bit',0),'rw')
        self.IPortInversion1_40  = (517,('bit',1),'rw')
        self.IPortInversion1_41  = (517,('bit',2),'rw')
        self.IPortInversion1_42  = (517,('bit',3),'rw')
        self.ExtRegenerativeRes  = (521,('bit',0),'rw')
        self.ExtRegenerativeRes_values = {
            'ConnectExternallyRegenerativeResistor':0,
            'DoesNotConnectExternallyRegenerativeResistor':1}
        #############Point-to-Point control related parameters#############
        self.PosPulseInPtPCtrl00 = (600,('int',0),'rw') #10k pulses per unit
        self.PosPulseInPtPCtrl01 = (601,('int',0),'rw') #1 pulse per unit
        self.PosPulseInPtPCtrl02 = (602,('int',0),'rw')
        self.PosPulseInPtPCtrl03 = (603,('int',0),'rw')
        self.PosPulseInPtPCtrl04 = (604,('int',0),'rw')
        self.PosPulseInPtPCtrl05 = (605,('int',0),'rw')
        self.PosPulseInPtPCtrl06 = (606,('int',0),'rw')
        self.PosPulseInPtPCtrl07 = (607,('int',0),'rw')
        self.PosPulseInPtPCtrl08 = (608,('int',0),'rw')
        self.PosPulseInPtPCtrl09 = (609,('int',0),'rw')
        self.PosPulseInPtPCtrl10 = (610,('int',0),'rw')
        self.PosPulseInPtPCtrl11 = (611,('int',0),'rw')
        self.PosPulseInPtPCtrl12 = (612,('int',0),'rw')
        self.PosPulseInPtPCtrl13 = (613,('int',0),'rw')
        self.PosPulseInPtPCtrl14 = (614,('int',0),'rw')
        self.PosPulseInPtPCtrl15 = (615,('int',0),'rw')
        self.PosPulseInPtPCtrl16 = (616,('int',0),'rw')
        self.PosPulseInPtPCtrl17 = (617,('int',0),'rw')
        self.PosPulseInPtPCtrl18 = (618,('int',0),'rw')
        self.PosPulseInPtPCtrl19 = (619,('int',0),'rw')
        self.PosPulseInPtPCtrl20 = (620,('int',0),'rw')
        self.PosPulseInPtPCtrl21 = (621,('int',0),'rw')
        self.PosPulseInPtPCtrl22 = (622,('int',0),'rw')
        self.PosPulseInPtPCtrl23 = (623,('int',0),'rw')
        self.PosPulseInPtPCtrl24 = (624,('int',0),'rw')
        self.PosPulseInPtPCtrl25 = (625,('int',0),'rw')
        self.PosPulseInPtPCtrl26 = (626,('int',0),'rw')
        self.PosPulseInPtPCtrl27 = (627,('int',0),'rw')
        self.PosPulseInPtPCtrl28 = (628,('int',0),'rw')
        self.PosPulseInPtPCtrl29 = (629,('int',0),'rw')
        self.PosPulseInPtPCtrl30 = (630,('int',0),'rw')
        self.PosPulseInPtPCtrl31 = (631,('int',0),'rw')
        self.PtPSpeedCtrl00      = (632,('int',0),'rw')
        self.PtPSpeedCtrl01      = (633,('int',0),'rw')
        self.PtPSpeedCtrl02      = (634,('int',0),'rw')
        self.PtPSpeedCtrl03      = (635,('int',0),'rw')
        self.PtPSpeedCtrl04      = (636,('int',0),'rw')
        self.PtPSpeedCtrl05      = (637,('int',0),'rw')
        self.PtPSpeedCtrl06      = (638,('int',0),'rw')
        self.PtPSpeedCtrl07      = (639,('int',0),'rw')
        self.PtPSpeedCtrl08      = (640,('int',0),'rw')
        self.PtPSpeedCtrl09      = (641,('int',0),'rw')
        self.PtPSpeedCtrl10      = (642,('int',0),'rw')
        self.PtPSpeedCtrl11      = (643,('int',0),'rw')
        self.PtPSpeedCtrl12      = (644,('int',0),'rw')
        self.PtPSpeedCtrl13      = (645,('int',0),'rw')
        self.PtPSpeedCtrl14      = (646,('int',0),'rw')
        self.PtPSpeedCtrl15      = (647,('int',0),'rw')
        self.PtPFrstOrderFilter00= (648,('int',0),'rw')
        self.PtPFrstOrderFilter01= (649,('int',0),'rw')
        self.PtPFrstOrderFilter02= (650,('int',0),'rw')
        self.PtPFrstOrderFilter03= (651,('int',0),'rw')
        self.PtPFrstOrderFilter04= (652,('int',0),'rw')
        self.PtPFrstOrderFilter05= (653,('int',0),'rw')
        self.PtPFrstOrderFilter06= (654,('int',0),'rw')
        self.PtPFrstOrderFilter07= (655,('int',0),'rw')
        self.PtPFrstOrderFilter08= (656,('int',0),'rw')
        self.PtPFrstOrderFilter09= (657,('int',0),'rw')
        self.PtPFrstOrderFilter10= (658,('int',0),'rw')
        self.PtPFrstOrderFilter11= (659,('int',0),'rw')
        self.PtPFrstOrderFilter12= (660,('int',0),'rw')
        self.PtPFrstOrderFilter13= (661,('int',0),'rw')
        self.PtPFrstOrderFilter14= (662,('int',0),'rw')
        self.PtPFrstOrderFilter15= (663,('int',0),'rw')
        self.StopTime00          = (663,('int',0),'rw')
        self.StopTime01          = (664,('int',0),'rw')
        self.StopTime02          = (665,('int',0),'rw')
        self.StopTime03          = (666,('int',0),'rw')
        self.StopTime04          = (667,('int',0),'rw')
        self.StopTime05          = (668,('int',0),'rw')
        self.StopTime06          = (669,('int',0),'rw')
        self.StopTime07          = (670,('int',0),'rw')
        self.StopTime08          = (671,('int',0),'rw')
        self.StopTime09          = (672,('int',0),'rw')
        self.StopTime10          = (673,('int',0),'rw')
        self.StopTime11          = (674,('int',0),'rw')
        self.StopTime12          = (675,('int',0),'rw')
        self.StopTime13          = (676,('int',0),'rw')
        self.StopTime14          = (677,('int',0),'rw')
        self.StopTime15          = (678,('int',0),'rw')
        self.StopTime16          = (679,('int',0),'rw')
        self.SingCyStartRef      = (681,('hex',0),'rw')
        self.SingCyStartRef_values = {
            'CyclicOperation-PCLStart-NCLSearch':0,
            'SingleOperation-PCLStart-NCLSearch':1,
            'CyclicOperation-NCLStart-PCLSearch':2,
            'SingleOperation-NCLStart-PCLSearch':3}
        self.ChangeStepnStartMode= (681,('hex',1),'rw')
        self.ChangeStepnStartMode = {
            'DelayToChangeStep,DelayToStartAfterS-ON':0,
            'PCONToChangeStep,PCONdelayToStart':1,
            'DelayToChangeStep,StartSignal':2,
            'PCONToChangeStep,StartSignal':3}
        self.ChangeStepInputMode = (681,('hex',2),'rw')
        self.ChangeStepInputMode_values = {
            'ElectricalLevelMode':0,
            'SignalPulseMode':1}
        self.ProgrammeMode       = (682,('bit',0),'rw')
        self.ProgrammeMode_values = {
            'Incremental':0,
            'Absolute':1}
        self.ProgrammeStartStep  = (683,('int',0),'rw')
        self.ProgrammeStopStep   = (684,('int',0),'rw')
        self.STravelSpdInPosCtrl = (685,('int',0),'rw') #Two meanings depends on ControlMode register
        self.SpdFindRefPtInHCtrlH= (685,('int',0),'rw') #   #Hitting the ref point
        self.LvTravelSwInPosCtrl = (686,('int',0),'rw') #
        self.SpdFindRefPtInHCtrlL= (686,('int',0),'rw') #   #Leaving the ref point
        self.PosTeachingPulse10k = (687,('int',0),'rw')     #10k pulses per unit
        self.PosTeachingPulse    = (688,('int',0),'rw')     #1 pulse per unit
        self.HomingModeSetting   = (689,('bit',0),'rw')
        self.HomingModeSetting_values = {
            'HomingForvard':0,
            'HomingReverse':1}
        self.SearchCPulseHoming  = (689,('bit',1),'rw')
        self.SearchCPulseHoming_values = {
            'ReturnToSearchCPulse':0,
            'DirectlySearchCPulse':1}
        self.HomingTrigStarting  = (689,('bit',2),'rw')
        self.HomingTrigStarting_values = {
            'HomingDisabled':0,
            'HomingTriggeredBySHOM':1}
        self.NumberErrsDHoming10k= (690,('int',0),'rw')     #10k pulses per unit
        self.NumberErrsDHoming   = (691,('int',0),'rw')     #1 pulse per unit
        #############Communication parameters#############
        self.MODBUSBaudrate      = (700,('hex',0),'rw')
        self.MODBUSBaudrate_values = {
            '4800':0,
            '9600':1,
            '19200':2}
        self.MODBUSProtocol      = (700,('hex',1),'rw')
        self.MODBUSProtocol_values = {
            '7bits,Parity=NONE,StopBits=2,MODBUS ASCII':0,
            '7bits,Parity=Even,StopBits=1,MODBUS ASCII':1,
            '7bits,Parity=Odd,StopBits=1,MODBUS ASCII':2,
            '8bits,Parity=NONE,StopBits=2,MODBUS ASCII':3,
            '8bits,Parity=Even,StopBits=1,MODBUS ASCII':4,
            '8bits,Parity=Odd,StopBits=1,MODBUS ASCII':5,
            '8bits,Parity=NONE,StopBits=2,MODBUS RTU':6,
            '8bits,Parity=Even,StopBits=1,MODBUS RTU':7,
            '8bits,Parity=Odd,StopBits=1,MODBUS RTU':8}
        self.CommProtocol        = (700,('hex',2),'rw')
        self.CommProtocol_values = {
            'NoSCI':0,
            'MODBUSSCI':1}
        self.MODBUSAxisAdress    = (701,('int',0),'rw')
        self.CANSpeed            = (703,('int',0),'rw')
        self.CANSpeed_values = {
            '50k':0,
            '100k':1,
            '125k':2,
            '250k':3,
            '500k':4,
            '1M':5}
        self.CANContact          = (704,('int',0),'rw')
        self.EncoderModel        = (840,('hex',0),'rw')
        self.EncoderModel_values = {
            '17bitAbsEncoder':3,
            '17bitIncEncoder':4,
            'Resolver':5,
            'IncrementalWire-savingEncoder':6} #2500P/R
        #################Alarms to read#####################
        self.Alarm0              = (0x7F1,('int',0),'r') #Latest alarm
        self.Alarm1              = (0x7F2,('int',0),'r')
        self.Alarm2              = (0x7F3,('int',0),'r')
        self.Alarm3              = (0x7F4,('int',0),'r')
        self.Alarm4              = (0x7F5,('int',0),'r')
        self.Alarm5              = (0x7F6,('int',0),'r')
        self.Alarm6              = (0x7F7,('int',0),'r')
        self.Alarm7              = (0x7F8,('int',0),'r')
        self.Alarm8              = (0x7F9,('int',0),'r')
        self.Alarm9              = (0x7FA,('int',0),'r')
        ##################Offsets to read###################
        self.SpeedRefZeroOffset  = (0x7FB,('int',0),'r')
        self.TorqueRefZeroOffset = (0x7FC,('int',0),'r')
        self.luZeroOffset        = (0x7FD,('int',0),'r')
        self.lvZeroOffset        = (0x7FE,('int',0),'r')
        ##################Monitoring registers##############
        self.SpeedFedback        = (0x806,('int',0),'r')
        self.InputSpeedRefValue  = (0x807,('int',0),'r')
        self.InputTorqueRefPerc  = (0x808,('int',0),'r')
        self.InternTorqueRefPerc = (0x809,('int',0),'r')
        self.EncRotationPulses   = (0x80A,('int',0),'r')
        self.InputSignalState    = (0x80B,('int',0),'r')
        self.bInputSignalState14 = (0x80B,('bit',0),'r')
        self.bInputSignalState15 = (0x80B,('bit',1),'r')
        self.bInputSignalState16 = (0x80B,('bit',2),'r')
        self.bInputSignalState17 = (0x80B,('bit',3),'r')
        self.bInputSignalState39 = (0x80B,('bit',4),'r')
        self.bInputSignalState40 = (0x80B,('bit',5),'r')
        self.bInputSignalState41 = (0x80B,('bit',6),'r')
        self.bInputSignalState42 = (0x80B,('bit',7),'r')
        self.EncSignalState      = (0x80C,('int',0),'r')
        self.OutputSignalState   = (0x80D,('int',0),'r')
        self.bOutputSignalState06= (0x80D,('bit',0),'r')
        self.bOutputSignalState08= (0x80D,('bit',1),'r')
        self.bOutputSignalState10= (0x80D,('bit',2),'r')
        self.bOutputSignalState12= (0x80D,('bit',3),'r')
        self.PulseSetting        = (0x80E,('int',0),'r')
        self.LowbitsOfpresentPos = (0x80F,('int',0),'r') #1 pulse per unit
        self.HighbitsOfpresentPos= (0x810,('int',0),'r') #10k pulses per unit
        self.ErrPulseCntLSBs     = (0x811,('int',0),'r')
        self.ErrPulseCNtMSBs     = (0x812,('int',0),'r')
        self.SettingPulseCntLSBs = (0x813,('int',0),'r') #1 pulse per unit
        self.SettingPulseCntMSBs = (0x814,('int',0),'r') #10k pulses per unit
        self.LoadInertiaPercValue= (0x815,('int',0),'r')
        self.ServoOverloadingProp= (0x816,('int',0),'r')
        self.CurrentAlarm        = (0x817,('int',0),'r')
        #############MODBUS Control IO Signals#############
        self.MODBUSIO            = (0x900,('int',0),'rw')
        #############Version###############################
        self.DSPver              = (0x90E,('int',0),'r')
        self.CPLDver             = (0x90F,('int',0),'r')
        #################Special Registers#################
        self.EncoderRevolutions  = (0x1010,('int',0),'r')
        self.EncoderPoseLSBs     = (0x1011,('int',0),'r')
        self.EncoderPoseMSBs     = (0x1012,('int',0),'r')
        self.ClearHistAlarms     = (0x1021,('int',0),'w') #0x01 to clear
        self.ClearCurrentAlarms  = (0x1022,('int',0),'w') #0x01 to clear
        self.JOGEnable           = (0x1023,('int',0),'rw')
        self.JOGEnable_values = {
            'ENABLE':1,
            'Disable':0}
        self.JOGForvardRot       = (0x1024,('int',0),'rw')
        self.JOGForvardRot_values = {
            'FORVARD':1,
            'STOP':0}
        self.JOGReverseRot       = (0x1025,('int',0),'rw')
        self.JOGReverseRot_values = {
            'REVERSE':1,
            'STOP':0}
        self.JOGForvardRotAtNode = (0x1026,('int',0),'rw')
        self.JOGForvardRotAtNode_values = self.JOGForvardRot_values
        self.JOGReverseRotAtNode = (0x1027,('int',0),'rw')
        self.JOGReverseRotAtNode_values = self.JOGReverseRot_values
        self.PauseAtNodePosition = (0x1028,('int',0),'rw')
        self.ClearEncoderAlarm   = (0x1040,('int',0),'w') #0x01 to clear
        self.ClrEncMultiturnData = (0x1041,('int',0),'w') #0x01 to clear #Corresponding to EncoderRevolutions and EncoderPose registers
        ##################Alarm codes#######################
        self.AlarmCodes = {
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
        self.WRITE_ONLY = 'w'
        self.READ_ONLY = 'r'
        self.READ_WRITE = 'rw'
        super().__init__(*args,**kwargs)