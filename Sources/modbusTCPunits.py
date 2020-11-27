from pymodbus.client.sync import ModbusTcpClient as ModbusClient
#from misc import *
from functools import wraps, partial
import re

class ADAMModule(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.CommonParameters = {
            'ClearGCLCounterCh0':(0x00301,('bit',0),"w"),
            'ClearGCLCounterCh1':(0x00302,('bit',0),"w"),
            'ClearGCLCounterCh2':(0x00303,('bit',0),"w"),
            'ClearGCLCounterCh3':(0x00304,('bit',0),"w"),
            'ClearGCLCounterCh4':(0x00305,('bit',0),"w"),
            'ClearGCLCounterCh5':(0x00306,('bit',0),"w"),
            'ClearGCLCounterCh6':(0x00307,('bit',0),"w"),
            'ClearGCLCounterCh7':(0x00308,('bit',0),"w"),
            'GCLInternalFlagValue':(0x40305,('int',0),"rw")
        }
        self.ADAM6000GCLInternalCounterValue:{
            'GCLInternalCounterValueCh0':(0x40311,('word',0),"w"),
            'GCLInternalCounterValueCh1':(0x40313,('word',0),"w"),
            'GCLInternalCounterValueCh2':(0x40315,('word',0),"w"),
            'GCLInternalCounterValueCh3':(0x40317,('word',0),"w"),
            'GCLInternalCounterValueCh4':(0x40319,('word',0),"w"),
            'GCLInternalCounterValueCh5':(0x40321,('word',0),"w"),
            'GCLInternalCounterValueCh6':(0x40323,('word',0),"w"),
            'GCLInternalCounterValueCh7':(0x40325,('word',0),"w")
        }
        self.AnalogParameters = {
            'ADAM600AI0-5':{
                'BurnoutFlagCh0':(0x00121,('bit',0),"r"),
                'BurnoutFlagCh1':(0x00122,('bit',0),"r"),
                'BurnoutFlagCh2':(0x00123,('bit',0),"r"),
                'BurnoutFlagCh3':(0x00124,('bit',0),"r"),
                'AIValueCh0':(0x40001,('int',0),"r"),
                'AIValueCh1':(0x40002,('int',0),"r"),
                'AIValueCh2':(0x40003,('int',0),"r"),
                'AIValueCh3':(0x40004,('int',0),"r"),
                'AIStatusCh0':(0x40021,('word',0),"r"),
                'AIStatusCh1':(0x40022,('word',0),"r"),
                'AIStatusCh2':(0x40023,('word',0),"r"),
                'AIStatusCh3':(0x40024,('word',0),"r"),
                'TypeCodeCh0':(0x40201,('int',0),"rw"),
                'TypeCodeCh1':(0x40202,('int',0),"rw"),
                'TypeCodeCh2':(0x40203,('int',0),"rw"),
                'TypeCodeCh3':(0x40204,('int',0),"rw"),
                'BurnoutFlagCh4':(0x00125,('bit',0),"r"),
                'BurnoutFlagCh5':(0x00126,('bit',0),"r"),
                'HighAlarmFlagCh4':(0x00135,('bit',0),"r"),
                'HighAlarmFlagCh5':(0x00136,('bit',0),"r"),
                'LowAlarmFlagCh4':(0x00145,('bit',0),"r"),
                'LowAlarmFlagCh5':(0x00146,('bit',0),"r"),
                'AIValueCh4':(0x40005,('int',0),"r"),
                'AIValueCh5':(0x40006,('int',0),"r"),
                'AIStatusCh4':(0x40025,('word',0),"r"),
                'AIStatusCh5':(0x40026,('word',0),"r"),
                'TypeCodeCh4':(0x40205,('int',0),"rw"),
                'TypeCodeCh5':(0x40206,('int',0),"rw")
            },
            'AI0-3':{
                'ResetHistoricalMaxCh0':(0x00101,('bit',0),"w"),
                'ResetHistoricalMaxCh1':(0x00102,('bit',0),"w"),
                'ResetHistoricalMaxCh2':(0x00103,('bit',0),"w"),
                'ResetHistoricalMaxCh3':(0x00104,('bit',0),"w"),
                'ResetHistoricalMinCh0':(0x00111,('bit',0),"w"),
                'ResetHistoricalMinCh1':(0x00112,('bit',0),"w"),
                'ResetHistoricalMinCh2':(0x00113,('bit',0),"w"),
                'ResetHistoricalMinCh3':(0x00114,('bit',0),"w"),
                'BurnoutFlagCh0':(0x00121,('bit',0),"r"),
                'BurnoutFlagCh1':(0x00122,('bit',0),"r"),
                'BurnoutFlagCh2':(0x00123,('bit',0),"r"),
                'BurnoutFlagCh3':(0x00124,('bit',0),"r"),
                'HighAlarmFlagCh0':(0x00131,('bit',0),"r"),
                'HighAlarmFlagCh1':(0x00132,('bit',0),"r"),
                'HighAlarmFlagCh2':(0x00133,('bit',0),"r"),
                'HighAlarmFlagCh3':(0x00134,('bit',0),"r"),
                'LowAlarmFlagCh0':(0x00141,('bit',0),"r"),
                'LowAlarmFlagCh1':(0x00142,('bit',0),"r"),
                'LowAlarmFlagCh2':(0x00143,('bit',0),"r"),
                'LowAlarmFlagCh3':(0x00144,('bit',0),"r"),
                'AIValueCh0':(0x40001,('int',0),"r"),
                'AIValueCh1':(0x40002,('int',0),"r"),
                'AIValueCh2':(0x40003,('int',0),"r"),
                'AIValueCh3':(0x40004,('int',0),"r"),
                'HistoricalMaxAIValueCh0':(0x40011,('int',0),"r"),
                'HistoricalMaxAIValueCh1':(0x40012,('int',0),"r"),
                'HistoricalMaxAIValueCh2':(0x40013,('int',0),"r"),
                'HistoricalMaxAIValueCh3':(0x40014,('int',0),"r"),
                'HistoricalMinAIValueCh0':(0x40021,('int',0),"r"),
                'HistoricalMinAIValueCh1':(0x40022,('int',0),"r"),
                'HistoricalMinAIValueCh2':(0x40023,('int',0),"r"),
                'HistoricalMinAIValueCh3':(0x40024,('int',0),"r"),
                'AIStatusCh0':(0x40101,('word',0),"r"),
                'AIStatusCh1':(0x40103,('word',0),"r"),
                'AIStatusCh2':(0x40105,('word',0),"r"),
                'AIStatusCh3':(0x40107,('word',0),"r"),
                'AIFloatingValueCh0':(0x40031,('word',0),"r"),
                'AIFloatingValueCh1':(0x40033,('word',0),"r"),
                'AIFloatingValueCh2':(0x40035,('word',0),"r"),
                'AIFloatingValueCh3':(0x40037,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh0':(0x40051,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh1':(0x40053,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh2':(0x40055,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh3':(0x40057,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh0':(0x40071,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh1':(0x40073,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh2':(0x40075,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh3':(0x40077,('word',0),"r"),
                'TypeCodeCh0':(0x40201,('int',0),"rw"),
                'TypeCodeCh1':(0x40202,('int',0),"rw"),
                'TypeCodeCh2':(0x40203,('int',0),"rw"),
                'TypeCodeCh3':(0x40204,('int',0),"rw")
            },
            'AI4-5':{
                'ResetHistoricalMaxCh4':(0x00105,('bit',0),"w"),
                'ResetHistoricalMaxCh5':(0x00106,('bit',0),"w"),
                'ResetHistoricalMinCh4':(0x00115,('bit',0),"w"),
                'ResetHistoricalMinCh5':(0x00116,('bit',0),"w"),
                'BurnoutFlagCh4':(0x00125,('bit',0),"r"),
                'BurnoutFlagCh5':(0x00126,('bit',0),"r"),
                'HighAlarmFlagCh4':(0x00135,('bit',0),"r"),
                'HighAlarmFlagCh5':(0x00136,('bit',0),"r"),
                'LowAlarmFlagCh4':(0x00145,('bit',0),"r"),
                'LowAlarmFlagCh5':(0x00146,('bit',0),"r"),
                'AIValueCh4':(0x40005,('int',0),"r"),
                'AIValueCh5':(0x40006,('int',0),"r"),
                'HistoricalMaxAIValueCh4':(0x40015,('int',0),"r"),
                'HistoricalMaxAIValueCh5':(0x40016,('int',0),"r"),
                'HistoricalMinAIValueCh4':(0x40025,('int',0),"r"),
                'HistoricalMinAIValueCh5':(0x40026,('int',0),"r"),
                'AIStatusCh4':(0x40109,('word',0),"r"),
                'AIStatusCh5':(0x40111,('word',0),"r"),
                'AIFloatingValueCh4':(0x40039,('word',0),"r"),
                'AIFloatingValueCh5':(0x40041,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh4':(0x40059,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh5':(0x40061,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh4':(0x40079,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh5':(0x40081,('word',0),"r"),
                'TypeCodeCh4':(0x40205,('int',0),"rw"),
                'TypeCodeCh5':(0x40206,('int',0),"rw")
            },
            'AI4-6':{
                **self.AnalogParameters['AI4-5'],
                'ResetHistoricalMaxCh6':(0x00107,('bit',0),"w"),
                'ResetHistoricalMinCh6':(0x00117,('bit',0),"w"),
                'BurnoutFlagCh6':(0x00127,('bit',0),"r"),
                'HighAlarmFlagCh6':(0x00137,('bit',0),"r"),
                'LowAlarmFlagCh6':(0x00147,('bit',0),"r"),
                'AIValueCh6':(0x40007,('int',0),"r"),
                'HistoricalMaxAIValueCh6':(0x40017,('int',0),"r"),
                'HistoricalMinAIValueCh6':(0x40027,('int',0),"r"),
                'AIStatusCh6':(0x40113,('word',0),"r"),
                'AIFloatingValueCh6':(0x40043,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh6':(0x40063,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh6':(0x40083,('word',0),"r"),
                'TypeCodeCh6':(0x40207,('int',0),"rw")
            },
            'AI4-7':{
                **self.AnalogParameters['AI4-6'],
                'ResetHistoricalMaxCh7':(0x00108,('bit',0),"w"),
                'ResetHistoricalMinCh7':(0x00118,('bit',0),"w"),
                'BurnoutFlagCh7':(0x00128,('bit',0),"r"),
                'HighAlarmFlagCh7':(0x00138,('bit',0),"r"),
                'LowAlarmFlagCh7':(0x00148,('bit',0),"r"),
                'AIValueCh7':(0x40008,('int',0),"r"),
                'HistoricalMaxAIValueCh7':(0x40018,('int',0),"r"),
                'HistoricalMinAIValueCh7':(0x40028,('int',0),"r"),
                'AIStatusCh7':(0x40115,('word',0),"r"),
                'AIFloatingValueCh7':(0x40045,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh7':(0x40065,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh7':(0x40085,('word',0),"r"),
                'TypeCodeCh7':(0x40208,('int',0),"rw")
            },
            'CommonAI':{
                'AIStatusBitmask':{
                    '0x00000001':'Failed to provide AI value (UART timeout)',
                    '0x00000002':'Over Range',
                    '0x00000004':'Under Range',
                    '0x00000008':'Open circuit(Burnout)',
                    '0x00000080':'AD Converter failed',
                    '0x00000200':'Zero/Span Calibration Error'},
                'ResetHistoricalMaxAvCh0-7':(0x00109,('bit',0),"w"),
                'ResetHistoricalMinAvCh0-7':(0x00119,('bit',0),"w"),
                'HighAlarmFlagAvCh0-7':(0x00139,('bit',0),"r"),
                'LowAlarmFlagAvCh0-7':(0x00149,('bit',0),"r"),
                'AIValueAvCh0-7':(0x40009,('int',0),"r"),
                'HistoricalMaxAIValueAvCh0-7':(0x40019,('int',0),"r"),
                'HistoricalMinAIValueAvCh0-7':(0x40029,('int',0),"r"),
                'AIFloatingValueAvCh0-7':(0x40047,('word',0),"r"),
                'HistoricalMaxAIFloatingValueAvCh0-7':(0x40067,('word',0),"r"),
                'HistoricalMinAIFloatingValueAvCh0-7':(0x40087,('word',0),"r"),
                'TypeCodeAvCh0-7':(0x40209,('int',0),"rw"),
                'AIChannelEnable':(0x40221,('int',0),"rw")
            },
            'ADAM600AO0-1':{
                'AOValueCh0':(0x40001,('int',0),"rw"),
                'AOValueCh1':(0x40002,('int',0),"rw"),
                'AOStatusCh0':(0x40101,('word',0),"r"), #4bytes
                'AOStatusCh1':(0x40103,('word',0),"r"),
                'AOStatusBitmask':{
                    '0x00000001':'Failed to provide AO value (UART timeout)',
                    '0x00000004':'No Output Current',
                    '0x00000080':'AD Converter failed',
                    '0x00000200':'Zero/Span Calibration Error',
                    '0x00010000':'DI triggered to Safety Value',
                    '0x00040200':'DI triggered to Statup Value',
                    '0x00080200':'AO triggered to Fail Safety Value'},
                    'TypeCodeCh0':(0x40201,('int',0),"rw"), #2bytes
                    'TypeCodeCh1':(0x40202,('int',0),"rw")
            },
            'AO0-1':{
                'AOValueCh0':(0x40001,('int',0),"rw"),
                'AOValueCh1':(0x40002,('int',0),"rw"),
                'AOStatusCh0':(0x40101,('word',0),"r"), #4bytes
                'AOStatusCh1':(0x40103,('word',0),"r"),
                'AOStatusBitmask':{
                    '0x00000001':'Failed to provide AO value (UART timeout)',
                    '0x00000004':'No Output Current',
                    '0x00000080':'AD Converter failed',
                    '0x00000200':'Zero/Span Calibration Error',
                    '0x00010000':'DI triggered to Safety Value',
                    '0x00040200':'DI triggered to Statup Value',
                    '0x00080200':'AO triggered to Fail Safety Value'},
                    'TypeCodeCh0':(0x40201,('int',0),"rw"), #2bytes
                    'TypeCodeCh1':(0x40202,('int',0),"rw")
            },
            'AO0-3':{
                **self.AnalogParameters['AO0-1'],
                'AOValueCh2':(0x40003,('int',0),"rw"),
                'AOValueCh3':(0x40004,('int',0),"rw"),
                'AOStatusCh2':(0x40105,('word',0),"r"),
                'AOStatusCh3':(0x40107,('word',0),"r"),
                
                'TypeCodeCh2':(0x40203,('int',0),"rw"),
                'TypeCodeCh3':(0x40204,('int',0),"rw"),
                'TypeCodeAvCh0-7':(0x40209,('int',0),"rw"),
            },
            'AO4-7':{

            },
            'CommonAO':{

            },
            'Common':{
                'TypeCode_values':{
                '0x0143':'+/- 10 V',
                '0x0142':'+/- 5 V',
                '0x0140':'+/- 1 V',
                '0x0104':'+/- 500 mV',
                '0x0103':'+/- 150 mV',
                '0x0181':'+/- 20 mA',
                '0x0182':'0 ~ 20 mA',
                '0x0180':'4 ~ 20 mA',
                '0x0105':'0 ~ 150 mV',
                '0x0106':'0 ~ 500 mV',
                '0x0145':'0 ~ 1 V',
                '0x0147':'0 ~ 5 V',
                '0x0148':'0 ~ 10 V',
                '0x03A4':'PT100(385) -50 ~ 150 C',
                '0x03a5':'PT100(385) 0 ~ 100 C',
                '0x03A6':'PT100(385) 0 ~ 200 C',
                '0x03A7':'PT100(385) 0 ~ 400 C',
                '0x03A2':'PT100(385) -200 ~ 200 C',
                '0x03C4':'PT100(392) -50 ~ 150 C',
                '0x03C5':'PT100(392) 0 ~ 100 C',
                '0x03C6':'PT100(392) 0 ~ 200 C',
                '0x03C7':'PT100(392) 0 ~ 400 C',
                '0x03C2':'PT100(392) -200 ~ 200 C',
                '0x03E2':'PT1000 -40 ~ 160 C',
                '0x0300':'Balco500 -30 ~ 120 C',
                '0x0320':'NI604(518) -80 ~ 100 C',
                '0x0321':'NI604(518) 0 ~ 100 C'
                },
            }
        }
        self.DigitalParameters = {
            'DI0-1':{
                'DI0':(0x00001,('bit',0),'r'),
                'DI1':(0x00002,('bit',0),'r')
            },
            'DI0-3':{
                **self.DigitalParameters['DI0-1'],
                'DI2':(0x00003,('bit',0),'r'),
                'DI3':(0x00004,('bit',0),'r')
            },
            'DI4-7':{
                'DI4':(0x00005,('bit',0),'r'),
                'DI5':(0x00006,('bit',0),'r'),
                'DI6':(0x00007,('bit',0),'r'),
                'DI7':(0x00008,('bit',0),'r')
            },
            'DI8-15':{
                'DI8':(0x00009,('bit',0),'r'),
                'DI9':(0x000010,('bit',0),'r'),
                'DI10':(0x00011,('bit',0),'r'),
                'DI11':(0x00012,('bit',0),'r'),
                'DI12':(0x00013,('bit',0),'r'),
                'DI13':(0x00014,('bit',0),'r'),
                'DI14':(0x00015,('bit',0),'r'),
                'DI15':(0x00016,('bit',0),'r')
            },
            'CommonDI':{
                'DIValue':(0x40301,('word',0),"r")
            },
            'DO0-1':{
                'DO0':(0x000017,('bit',0),'rw'),
                'DO1':(0x000018,('bit',0),'rw')
            },
            'DO0-3':{
                **self.DigitalParameters['DO0-1'],
                'DO2':(0x000019,('bit',0),'rw'),
                'DO3':(0x000020,('bit',0),'rw')
            },
            'DO4-7':{
                'DO4':(0x000021,('bit',0),'rw'),
                'DO5':(0x000022,('bit',0),'rw'),
                'DO6':(0x000023,('bit',0),'rw'),
                'DO7':(0x000024,('bit',0),'rw')
            },
            'DO8-11':{
                'DO8':(0x00025,('bit',0),'r'),
                'DO9':(0x00026,('bit',0),'r'),
                'DO10':(0x00027,('bit',0),'r'),
                'DO11':(0x00028,('bit',0),'r')
            },
            'DO8-15':{
                **self.DigitalParameters['DO8-11'],
                'DO12':(0x00029,('bit',0),'r'),
                'DO13':(0x00030,('bit',0),'r'),
                'DO14':(0x00031,('bit',0),'r'),
                'DO15':(0x00032,('bit',0),'r')
            },
            'CommonDO':{
                'DOValue':(0x40303,('word',0),"rw")
            },
            'Counter0-3':{
                'CounterStartStop0':(0x000033,('bit',0),'rw'),
                'CounterStartStop1':(0x000034,('bit',0),'rw'),
                'CounterStartStop2':(0x000035,('bit',0),'rw'),
                'CounterStartStop3':(0x000036,('bit',0),'rw'),
                'ClearCounter0':(0x000037,('bit',0),'rw'),
                'ClearCounter1':(0x000038,('bit',0),'rw'),
                'ClearCounter2':(0x000039,('bit',0),'rw'),
                'ClearCounter3':(0x000040,('bit',0),'rw'),
                'ClearOverflow0':(0x000041,('bit',0),'rw'),
                'ClearOverflow1':(0x000042,('bit',0),'rw'),
                'ClearOverflow2':(0x000043,('bit',0),'rw'),
                'ClearOverflow3':(0x000044,('bit',0),'rw'),
                **self.DigitalParameters['Counter/FrequencyValue0-3']
            },
            'Counter0-7':{
                'CounterStartStop0':(0x000033,('bit',0),'rw'),
                'CounterStartStop1':(0x000034,('bit',0),'rw'),
                'CounterStartStop2':(0x000035,('bit',0),'rw'),
                'CounterStartStop3':(0x000036,('bit',0),'rw'),
                'CounterStartStop4':(0x000037,('bit',0),'rw'),
                'CounterStartStop5':(0x000038,('bit',0),'rw'),
                'CounterStartStop6':(0x000039,('bit',0),'rw'),
                'CounterStartStop7':(0x000040,('bit',0),'rw'),
                'ClearCounter0':(0x000041,('bit',0),'rw'),
                'ClearCounter1':(0x000042,('bit',0),'rw'),
                'ClearCounter2':(0x000043,('bit',0),'rw'),
                'ClearCounter3':(0x000044,('bit',0),'rw'),
                'ClearCounter4':(0x000045,('bit',0),'rw'),
                'ClearCounter5':(0x000046,('bit',0),'rw'),
                'ClearCounter6':(0x000047,('bit',0),'rw'),
                'ClearCounter7':(0x000048,('bit',0),'rw'),
                'ClearOverflow0':(0x000049,('bit',0),'rw'),
                'ClearOverflow1':(0x000050,('bit',0),'rw'),
                'ClearOverflow2':(0x000051,('bit',0),'rw'),
                'ClearOverflow3':(0x000052,('bit',0),'rw'),
                'ClearOverflow4':(0x000053,('bit',0),'rw'),
                'ClearOverflow5':(0x000054,('bit',0),'rw'),
                'ClearOverflow6':(0x000055,('bit',0),'rw'),
                'ClearOverflow7':(0x000056,('bit',0),'rw'),
                **self.DigitalParameters['Counter/FrequencyValue0-3'],
                **self.DigitalParameters['Counter/FrequencyValue4-7']
            },
            'Counter/FrequencyValue0-3':{
                'Counter/FrequencyValue0':(0x40001,('word',0),"r"),
                'Counter/FrequencyValue1':(0x40003,('word',0),"r"),
                'Counter/FrequencyValue2':(0x40005,('word',0),"r"),
                'Counter/FrequencyValue3':(0x40007,('word',0),"r")
            },
            'Counter/FrequencyValue4-7':{
                'Counter/FrequencyValue4':(0x40009,('word',0),"r"),
                'Counter/FrequencyValue5':(0x40011,('word',0),"r"),
                'Counter/FrequencyValue6':(0x40013,('word',0),"r"),
                'Counter/FrequencyValue7':(0x40015,('word',0),"r")
            },
            'Counter/FrequencyValue0-11':{
                **self.DigitalParameters['Counter/FrequencyValue0-3'],
                **self.DigitalParameters['Counter/FrequencyValue4-7'],
                'Counter/FrequencyValue8':(0x40017,('word',0),"r"),
                'Counter/FrequencyValue9':(0x40019,('word',0),"r"),
                'Counter/FrequencyValue10':(0x40021,('word',0),"r"),
                'Counter/FrequencyValue11':(0x40023,('word',0),"r")
            },
            'PWMOutput0-3':{
                'PulseOutputLowLevelWidth0':(0x40009,('word',0),"rw"),
                'PulseOutputLowLevelWidth1':(0x40011,('word',0),"rw"),
                'PulseOutputLowLevelWidth2':(0x40013,('word',0),"rw"),
                'PulseOutputLowLevelWidth3':(0x40015,('word',0),"rw"),
                'PulseOutputHighLevelWidth0':(0x40017,('word',0),"rw"),
                'PulseOutputHighLevelWidth1':(0x40019,('word',0),"rw"),
                'PulseOutputHighLevelWidth2':(0x40021,('word',0),"rw"),
                'PulseOutputHighLevelWidth3':(0x40023,('word',0),"rw"),
                'SetAbsolutePulse0':(0x40025,('word',0),"rw"),
                'SetAbsolutePulse1':(0x40027,('word',0),"rw"),
                'SetAbsolutePulse2':(0x40029,('word',0),"rw"),
                'SetAbsolutePulse3':(0x40031,('word',0),"rw"),
                'SetIncrementalPulse0':(0x40033,('word',0),"rw"),
                'SetIncrementalPulse1':(0x40035,('word',0),"rw"),
                'SetIncrementalPulse2':(0x40037,('word',0),"rw"),
                'SetIncrementalPulse3':(0x40039,('word',0),"rw")
            },
            'ADAM6000PWMOutput0-5':{
                'PulseOutputLowLevelWidth0':(0x40025,('word',0),"r"),
                'PulseOutputLowLevelWidth1':(0x40027,('word',0),"r"),
                'PulseOutputLowLevelWidth2':(0x40029,('word',0),"r"),
                'PulseOutputLowLevelWidth3':(0x40031,('word',0),"r"),
                'PulseOutputLowLevelWidth4':(0x40033,('word',0),"r"),
                'PulseOutputLowLevelWidth5':(0x40035,('word',0),"r"),
                'PulseOutputHighLevelWidth0':(0x40037,('word',0),"r"),
                'PulseOutputHighLevelWidth1':(0x40039,('word',0),"r"),
                'PulseOutputHighLevelWidth2':(0x40041,('word',0),"r"),
                'PulseOutputHighLevelWidth3':(0x40043,('word',0),"r"),
                'PulseOutputHighLevelWidth4':(0x40045,('word',0),"r"),
                'PulseOutputHighLevelWidth5':(0x40047,('word',0),"r"),
                'SetAbsolutePulse0':(0x40049,('word',0),"r"),
                'SetAbsolutePulse1':(0x40051,('word',0),"r"),
                'SetAbsolutePulse2':(0x40053,('word',0),"r"),
                'SetAbsolutePulse3':(0x40055,('word',0),"r"),
                'SetAbsolutePulse4':(0x40057,('word',0),"r"),
                'SetAbsolutePulse5':(0x40059,('word',0),"r"),
                'SetIncrementalPulse0':(0x40061,('word',0),"r"),
                'SetIncrementalPulse1':(0x40063,('word',0),"r"),
                'SetIncrementalPulse2':(0x40065,('word',0),"r"),
                'SetIncrementalPulse3':(0x40067,('word',0),"r"),
                'SetIncrementalPulse4':(0x40069,('word',0),"r"),
                'SetIncrementalPulse5':(0x40071,('word',0),"r")
            },
            'PWMOutput0-5':{
                'PulseOutputLowLevelWidth0':(0x40001,('word',0),"rw"),
                'PulseOutputLowLevelWidth1':(0x40003,('word',0),"rw"),
                'PulseOutputLowLevelWidth2':(0x40005,('word',0),"rw"),
                'PulseOutputLowLevelWidth3':(0x40007,('word',0),"rw"),
                'PulseOutputLowLevelWidth4':(0x40009,('word',0),"rw"),
                'PulseOutputLowLevelWidth5':(0x40011,('word',0),"rw"),
                'PulseOutputHighLevelWidth0':(0x40013,('word',0),"rw"),
                'PulseOutputHighLevelWidth1':(0x40015,('word',0),"rw"),
                'PulseOutputHighLevelWidth2':(0x40017,('word',0),"rw"),
                'PulseOutputHighLevelWidth3':(0x40019,('word',0),"rw"),
                'PulseOutputHighLevelWidth4':(0x40021,('word',0),"rw"),
                'PulseOutputHighLevelWidth5':(0x40023,('word',0),"rw"),
                'SetAbsolutePulse0':(0x40025,('word',0),"rw"),
                'SetAbsolutePulse1':(0x40027,('word',0),"rw"),
                'SetAbsolutePulse2':(0x40029,('word',0),"rw"),
                'SetAbsolutePulse3':(0x40031,('word',0),"rw"),
                'SetAbsolutePulse4':(0x40033,('word',0),"rw"),
                'SetAbsolutePulse5':(0x40035,('word',0),"rw"),
                'SetIncrementalPulse0':(0x40037,('word',0),"rw"),
                'SetIncrementalPulse1':(0x40039,('word',0),"rw"),
                'SetIncrementalPulse2':(0x40041,('word',0),"rw"),
                'SetIncrementalPulse3':(0x40043,('word',0),"rw"),
                'SetIncrementalPulse4':(0x40045,('word',0),"rw"),
                'SetIncrementalPulse5':(0x40047,('word',0),"rw")
            },
            'PWMOutput0-6':{
                'PulseOutputLowLevelWidth0':(0x40017,('word',0),"rw"),
                'PulseOutputLowLevelWidth1':(0x40019,('word',0),"rw"),
                'PulseOutputLowLevelWidth2':(0x40021,('word',0),"rw"),
                'PulseOutputLowLevelWidth3':(0x40023,('word',0),"rw"),
                'PulseOutputLowLevelWidth4':(0x40025,('word',0),"rw"),
                'PulseOutputLowLevelWidth5':(0x40027,('word',0),"rw"),
                'PulseOutputLowLevelWidth6':(0x40029,('word',0),"rw"),
                'PulseOutputHighLevelWidth0':(0x40031,('word',0),"rw"),
                'PulseOutputHighLevelWidth1':(0x40033,('word',0),"rw"),
                'PulseOutputHighLevelWidth2':(0x40035,('word',0),"rw"),
                'PulseOutputHighLevelWidth3':(0x40037,('word',0),"rw"),
                'PulseOutputHighLevelWidth4':(0x40039,('word',0),"rw"),
                'PulseOutputHighLevelWidth5':(0x40041,('word',0),"rw"),
                'PulseOutputHighLevelWidth6':(0x40043,('word',0),"rw"),
                'SetAbsolutePulse0':(0x40045,('word',0),"rw"),
                'SetAbsolutePulse1':(0x40047,('word',0),"rw"),
                'SetAbsolutePulse2':(0x40049,('word',0),"rw"),
                'SetAbsolutePulse3':(0x40051,('word',0),"rw"),
                'SetAbsolutePulse4':(0x40053,('word',0),"rw"),
                'SetAbsolutePulse5':(0x40055,('word',0),"rw"),
                'SetAbsolutePulse6':(0x40057,('word',0),"rw"),
                'SetIncrementalPulse0':(0x40059,('word',0),"rw"),
                'SetIncrementalPulse1':(0x40061,('word',0),"rw"),
                'SetIncrementalPulse2':(0x40063,('word',0),"rw"),
                'SetIncrementalPulse3':(0x40065,('word',0),"rw"),
                'SetIncrementalPulse4':(0x40067,('word',0),"rw"),
                'SetIncrementalPulse5':(0x40069,('word',0),"rw"),
                'SetIncrementalPulse6':(0x40071,('word',0),"rw")
            },
            'PWMOutput0-7':{
                'PulseOutputLowLevelWidth0':(0x40017,('word',0),"rw"),
                'PulseOutputLowLevelWidth1':(0x40019,('word',0),"rw"),
                'PulseOutputLowLevelWidth2':(0x40021,('word',0),"rw"),
                'PulseOutputLowLevelWidth3':(0x40023,('word',0),"rw"),
                'PulseOutputLowLevelWidth4':(0x40025,('word',0),"rw"),
                'PulseOutputLowLevelWidth5':(0x40027,('word',0),"rw"),
                'PulseOutputLowLevelWidth6':(0x40029,('word',0),"rw"),
                'PulseOutputLowLevelWidth7':(0x40031,('word',0),"rw"),
                'PulseOutputHighLevelWidth0':(0x40033,('word',0),"rw"),
                'PulseOutputHighLevelWidth1':(0x40035,('word',0),"rw"),
                'PulseOutputHighLevelWidth2':(0x40037,('word',0),"rw"),
                'PulseOutputHighLevelWidth3':(0x40039,('word',0),"rw"),
                'PulseOutputHighLevelWidth4':(0x40041,('word',0),"rw"),
                'PulseOutputHighLevelWidth5':(0x40043,('word',0),"rw"),
                'PulseOutputHighLevelWidth6':(0x40045,('word',0),"rw"),
                'PulseOutputHighLevelWidth7':(0x40047,('word',0),"rw"),
                'SetAbsolutePulse0':(0x40049,('word',0),"rw"),
                'SetAbsolutePulse1':(0x40051,('word',0),"rw"),
                'SetAbsolutePulse2':(0x40053,('word',0),"rw"),
                'SetAbsolutePulse3':(0x40055,('word',0),"rw"),
                'SetAbsolutePulse4':(0x40057,('word',0),"rw"),
                'SetAbsolutePulse5':(0x40059,('word',0),"rw"),
                'SetAbsolutePulse6':(0x40061,('word',0),"rw"),
                'SetAbsolutePulse7':(0x40063,('word',0),"rw"),
                'SetIncrementalPulse0':(0x40065,('word',0),"rw"),
                'SetIncrementalPulse1':(0x40067,('word',0),"rw"),
                'SetIncrementalPulse2':(0x40069,('word',0),"rw"),
                'SetIncrementalPulse3':(0x40071,('word',0),"rw"),
                'SetIncrementalPulse4':(0x40073,('word',0),"rw"),
                'SetIncrementalPulse5':(0x40075,('word',0),"rw"),
                'SetIncrementalPulse6':(0x40077,('word',0),"rw"),
                'SetIncrementalPulse7':(0x40079,('word',0),"rw")
            },
            'PWMOutput0-15':{
                'PulseOutputLowLevelWidth0':(0x40001,('word',0),"rw"),
                'PulseOutputLowLevelWidth1':(0x40003,('word',0),"rw"),
                'PulseOutputLowLevelWidth2':(0x40005,('word',0),"rw"),
                'PulseOutputLowLevelWidth3':(0x40007,('word',0),"rw"),
                'PulseOutputLowLevelWidth4':(0x40009,('word',0),"rw"),
                'PulseOutputLowLevelWidth5':(0x40011,('word',0),"rw"),
                'PulseOutputLowLevelWidth6':(0x40013,('word',0),"rw"),
                'PulseOutputLowLevelWidth7':(0x40015,('word',0),"rw"),
                'PulseOutputLowLevelWidth8':(0x40017,('word',0),"rw"),
                'PulseOutputLowLevelWidth9':(0x40019,('word',0),"rw"),
                'PulseOutputLowLevelWidth10':(0x40021,('word',0),"rw"),
                'PulseOutputLowLevelWidth11':(0x40023,('word',0),"rw"),
                'PulseOutputLowLevelWidth12':(0x40025,('word',0),"rw"),
                'PulseOutputLowLevelWidth13':(0x40027,('word',0),"rw"),
                'PulseOutputLowLevelWidth14':(0x40029,('word',0),"rw"),
                'PulseOutputLowLevelWidth15':(0x40031,('word',0),"rw"),
                'PulseOutputHighLevelWidth0':(0x40033,('word',0),"rw"),
                'PulseOutputHighLevelWidth1':(0x40035,('word',0),"rw"),
                'PulseOutputHighLevelWidth2':(0x40037,('word',0),"rw"),
                'PulseOutputHighLevelWidth3':(0x40039,('word',0),"rw"),
                'PulseOutputHighLevelWidth4':(0x40041,('word',0),"rw"),
                'PulseOutputHighLevelWidth5':(0x40043,('word',0),"rw"),
                'PulseOutputHighLevelWidth6':(0x40045,('word',0),"rw"),
                'PulseOutputHighLevelWidth7':(0x40047,('word',0),"rw"),
                'PulseOutputHighLevelWidth8':(0x40049,('word',0),"rw"),
                'PulseOutputHighLevelWidth9':(0x40051,('word',0),"rw"),
                'PulseOutputHighLevelWidth10':(0x40053,('word',0),"rw"),
                'PulseOutputHighLevelWidth11':(0x40055,('word',0),"rw"),
                'PulseOutputHighLevelWidth12':(0x40057,('word',0),"rw"),
                'PulseOutputHighLevelWidth13':(0x40059,('word',0),"rw"),
                'PulseOutputHighLevelWidth14':(0x40061,('word',0),"rw"),
                'PulseOutputHighLevelWidth15':(0x40063,('word',0),"rw"),
                'SetAbsolutePulse0':(0x40065,('word',0),"rw"),
                'SetAbsolutePulse1':(0x40067,('word',0),"rw"),
                'SetAbsolutePulse2':(0x40069,('word',0),"rw"),
                'SetAbsolutePulse3':(0x40071,('word',0),"rw"),
                'SetAbsolutePulse4':(0x40073,('word',0),"rw"),
                'SetAbsolutePulse5':(0x40075,('word',0),"rw"),
                'SetAbsolutePulse6':(0x40077,('word',0),"rw"),
                'SetAbsolutePulse7':(0x40079,('word',0),"rw"),
                'SetAbsolutePulse8':(0x40081,('word',0),"rw"),
                'SetAbsolutePulse9':(0x40083,('word',0),"rw"),
                'SetAbsolutePulse10':(0x40085,('word',0),"rw"),
                'SetAbsolutePulse11':(0x40087,('word',0),"rw"),
                'SetAbsolutePulse12':(0x40089,('word',0),"rw"),
                'SetAbsolutePulse13':(0x40091,('word',0),"rw"),
                'SetAbsolutePulse14':(0x40093,('word',0),"rw"),
                'SetAbsolutePulse15':(0x40095,('word',0),"rw"),
                'SetIncrementalPulse0':(0x40097,('word',0),"rw"),
                'SetIncrementalPulse1':(0x40099,('word',0),"rw"),
                'SetIncrementalPulse2':(0x40101,('word',0),"rw"),
                'SetIncrementalPulse3':(0x40103,('word',0),"rw"),
                'SetIncrementalPulse4':(0x40105,('word',0),"rw"),
                'SetIncrementalPulse5':(0x40107,('word',0),"rw"),
                'SetIncrementalPulse6':(0x40109,('word',0),"rw"),
                'SetIncrementalPulse7':(0x40111,('word',0),"rw"),
                'SetIncrementalPulse8':(0x40113,('word',0),"rw"),
                'SetIncrementalPulse9':(0x40115,('word',0),"rw"),
                'SetIncrementalPulse10':(0x40117,('word',0),"rw"),
                'SetIncrementalPulse11':(0x40119,('word',0),"rw"),
                'SetIncrementalPulse12':(0x40121,('word',0),"rw"),
                'SetIncrementalPulse13':(0x40123,('word',0),"rw"),
                'SetIncrementalPulse14':(0x40125,('word',0),"rw"),
                'SetIncrementalPulse15':(0x40127,('word',0),"rw")
            },
            'ADAM6000Counter0-7':{
                'CounterStartStop0':(0x000033,('bit',0),'rw'),
                'ClearCounter0':(0x000034,('bit',0),'w'),
                'ClearOverflow0':(0x000035,('bit',0),'rw'),
                'DILatchStatus0':(0x000036,('bit',0),'rw'),
                'CounterStartStop1':(0x000037,('bit',0),'rw'),
                'ClearCounter1':(0x000038,('bit',0),'w'),
                'ClearOverflow1':(0x000039,('bit',0),'rw'),
                'DILatchStatus1':(0x000040,('bit',0),'rw'),
                'CounterStartStop2':(0x000041,('bit',0),'rw'),
                'ClearCounter2':(0x000042,('bit',0),'w'),
                'ClearOverflow2':(0x000043,('bit',0),'rw'),
                'DILatchStatus2':(0x000044,('bit',0),'rw'),
                'CounterStartStop3':(0x000045,('bit',0),'rw'),
                'ClearCounter3':(0x000046,('bit',0),'w'),
                'ClearOverflow3':(0x000047,('bit',0),'rw'),
                'DILatchStatus3':(0x000048,('bit',0),'rw'),
                'CounterStartStop4':(0x000049,('bit',0),'rw'),
                'ClearCounter4':(0x000050,('bit',0),'w'),
                'ClearOverflow4':(0x000051,('bit',0),'rw'),
                'DILatchStatus4':(0x000052,('bit',0),'rw'),
                'CounterStartStop5':(0x000053,('bit',0),'rw'),
                'ClearCounter5':(0x000054,('bit',0),'w'),
                'ClearOverflow5':(0x000055,('bit',0),'rw'),
                'DILatchStatus5':(0x000056,('bit',0),'rw'),
                'CounterStartStop6':(0x000057,('bit',0),'rw'),
                'ClearCounter6':(0x000058,('bit',0),'w'),
                'ClearOverflow6':(0x000059,('bit',0),'rw'),
                'DILatchStatus6':(0x000060,('bit',0),'rw'),
                'CounterStartStop7':(0x000061,('bit',0),'rw'),
                'ClearCounter7':(0x000062,('bit',0),'w'),
                'ClearOverflow7':(0x000063,('bit',0),'rw'),
                'DILatchStatus7':(0x000064,('bit',0),'rw')
            },
            'ADAM6000Counter0-11':{
                **self.DigitalParameters['ADAM6000Counter0-7'],
                'CounterStartStop8':(0x000065,('bit',0),'rw'),
                'ClearCounter8':(0x000066,('bit',0),'w'),
                'ClearOverflow8':(0x000067,('bit',0),'rw'),
                'DILatchStatus8':(0x000068,('bit',0),'rw'),
                'CounterStartStop9':(0x00069,('bit',0),'rw'),
                'ClearCounter9':(0x000070,('bit',0),'w'),
                'ClearOverflow9':(0x000071,('bit',0),'rw'),
                'DILatchStatus9':(0x000072,('bit',0),'rw'),
                'CounterStartStop10':(0x000073,('bit',0),'rw'),
                'ClearCounter10':(0x000074,('bit',0),'w'),
                'ClearOverflow10':(0x000075,('bit',0),'rw'),
                'DILatchStatus10':(0x000076,('bit',0),'rw'),
                'CounterStartStop11':(0x000077,('bit',0),'rw'),
                'ClearCounter11':(0x000078,('bit',0),'w'),
                'ClearOverflow11':(0x000079,('bit',0),'rw'),
                'DILatchStatus11':(0x000080,('bit',0),'rw')
            },
            'Counter0-15':{
                'CounterStartStop0':(0x000033,('bit',0),'rw'),
                'CounterStartStop1':(0x000034,('bit',0),'rw'),
                'CounterStartStop2':(0x000035,('bit',0),'rw'),
                'CounterStartStop3':(0x000036,('bit',0),'rw'),
                'CounterStartStop4':(0x000037,('bit',0),'rw'),
                'CounterStartStop5':(0x000038,('bit',0),'rw'),
                'CounterStartStop6':(0x000039,('bit',0),'rw'),
                'CounterStartStop7':(0x000040,('bit',0),'rw'),
                'CounterStartStop8':(0x000041,('bit',0),'rw'),
                'CounterStartStop9':(0x000042,('bit',0),'rw'),
                'CounterStartStop10':(0x000043,('bit',0),'rw'),
                'CounterStartStop11':(0x000044,('bit',0),'rw'),
                'CounterStartStop12':(0x000045,('bit',0),'rw'),
                'CounterStartStop13':(0x000046,('bit',0),'rw'),
                'CounterStartStop14':(0x000047,('bit',0),'rw'),
                'CounterStartStop15':(0x000048,('bit',0),'rw'),
                'ClearCounter0':(0x000049,('bit',0),'rw'),
                'ClearCounter1':(0x000050,('bit',0),'rw'),
                'ClearCounter2':(0x000051,('bit',0),'rw'),
                'ClearCounter3':(0x000052,('bit',0),'rw'),
                'ClearCounter4':(0x000053,('bit',0),'rw'),
                'ClearCounter5':(0x000054,('bit',0),'rw'),
                'ClearCounter6':(0x000055,('bit',0),'rw'),
                'ClearCounter7':(0x000056,('bit',0),'rw'),
                'ClearCounter8':(0x000057,('bit',0),'rw'),
                'ClearCounter9':(0x000058,('bit',0),'rw'),
                'ClearCounter10':(0x000059,('bit',0),'rw'),
                'ClearCounter11':(0x000060,('bit',0),'rw'),
                'ClearCounter12':(0x000061,('bit',0),'rw'),
                'ClearCounter13':(0x000062,('bit',0),'rw'),
                'ClearCounter14':(0x000063,('bit',0),'rw'),
                'ClearCounter15':(0x000064,('bit',0),'rw'),
                'ClearOverflow0':(0x000065,('bit',0),'rw'),
                'ClearOverflow1':(0x000066,('bit',0),'rw'),
                'ClearOverflow2':(0x000067,('bit',0),'rw'),
                'ClearOverflow3':(0x000068,('bit',0),'rw'),
                'ClearOverflow4':(0x000069,('bit',0),'rw'),
                'ClearOverflow5':(0x000070,('bit',0),'rw'),
                'ClearOverflow6':(0x000071,('bit',0),'rw'),
                'ClearOverflow7':(0x000072,('bit',0),'rw'),
                'ClearOverflow8':(0x000073,('bit',0),'rw'),
                'ClearOverflow9':(0x000074,('bit',0),'rw'),
                'ClearOverflow10':(0x000075,('bit',0),'rw'),
                'ClearOverflow11':(0x000076,('bit',0),'rw'),
                'ClearOverflow12':(0x000077,('bit',0),'rw'),
                'ClearOverflow13':(0x000078,('bit',0),'rw'),
                'ClearOverflow14':(0x000079,('bit',0),'rw'),
                'ClearOverflow15':(0x000080,('bit',0),'rw'),
                **self.DigitalParameters['Counter/FrequencyValue0-11'],
                'Counter/FrequencyValue12':(0x40025,('word',0),"r"),
                'Counter/FrequencyValue13':(0x40027,('word',0),"r"),
                'Counter/FrequencyValue14':(0x40029,('word',0),"r"),
                'Counter/FrequencyValue15':(0x40031,('word',0),"r")
            },
            'Common':{
                
            }
        }
        self.ADAM6250 = {
            **self.DigitalParameters['DI0-3'],
            **self.DigitalParameters['DI4-7'],
            **self.DigitalParameters['DO0-3'],
            **self.DigitalParameters['DO4-7'],
            **self.DigitalParameters['CommonDI'],
            **self.DigitalParameters['CommonDO'],
            **self.DigitalParameters['PWMOutput0-6'],
            **self.DigitalParameters['Common'],
            **self.DigitalParameters['Counter0-7'],
            **self.CommonParameters,
            'DILatchStatus0':(0x000057,('bit',0),'rw'),
            'DILatchStatus1':(0x000058,('bit',0),'rw'),
            'DILatchStatus2':(0x000059,('bit',0),'rw'),
            'DILatchStatus3':(0x000060,('bit',0),'rw'),
            'DILatchStatus4':(0x000061,('bit',0),'rw'),
            'DILatchStatus5':(0x000062,('bit',0),'rw'),
            'DILatchStatus6':(0x000063,('bit',0),'rw'),
            'DILatchStatus7':(0x000064,('bit',0),'rw')
        }
        self.ADAM6050 = {
            **self.DigitalParameters['DI0-3'],
            **self.DigitalParameters['DI4-7'],
            **self.DigitalParameters['DI8-11'], 
            **self.DigitalParameters['DO0-3'],
            **self.DigitalParameters['DO4-5'],
            **self.DigitalParameters['CommonDO'],
            **self.DigitalParameters['CommonDI'],
            **self.DigitalParameters['Counter/FrequencyValue0-11'],
            **self.DigitalParameters['ADAM6000PWMOutput0-5'],
            **self.ADAM6000GCLInternalCounterValue,
            **self.CommonParameters,
            'ModuleName1':(0x40211,('int',0),'r'),
            'ModuleName2':(0x40212,('int',0),'r')
        }
        self.ADAM6050D = {
            **self.ADAM6050,
            'DODiagnosticStatus':(0x40307,('word',0),'r')
            
        }
        self.ADAM6051 = {} #TODO
        self.ADAM6052 = {
            **self.DigitalParameters['DI0-3'],
            **self.DigitalParameters['DI4-7'],
            **self.DigitalParameters['DO0-3'],
            **self.DigitalParameters['DO4-7'],
            **self.DigitalParameters['CommonDI'],
            **self.DigitalParameters['CommonDO'],
            **self.DigitalParameters['Counter/FrequencyValue0-3'],
            **self.DigitalParameters['Counter/FrequencyValue4-7'],
            **self.DigitalParameters['ADAM6000Counter0-7'],
            **self.DigitalParameters['PWMOutput0-7'],
            **self.CommonParameters,
        }
        self.ADAM6051 = {
            **self.DigitalParameters['DI0-3'],
            **self.DigitalParameters['DI4-7'],
            **self.DigitalParameters['DI8-15']
            **self.DigitalParameters['CommonDI'],
            **self.DigitalParameters['Common'],
            **self.DigitalParameters['Counter'],
            **self.CommonParameters,
            'DILatchStatus0':(0x000081,('bit',0),'rw'),
            'DILatchStatus1':(0x000082,('bit',0),'rw'),
            'DILatchStatus2':(0x000083,('bit',0),'rw'),
            'DILatchStatus3':(0x000084,('bit',0),'rw'),
            'DILatchStatus4':(0x000085,('bit',0),'rw'),
            'DILatchStatus5':(0x000086,('bit',0),'rw'),
            'DILatchStatus6':(0x000087,('bit',0),'rw'),
            'DILatchStatus7':(0x000088,('bit',0),'rw'),
            'DILatchStatus8':(0x000089,('bit',0),'rw'),
            'DILatchStatus9':(0x000090,('bit',0),'rw'),
            'DILatchStatus10':(0x000091,('bit',0),'rw'),
            'DILatchStatus11':(0x000092,('bit',0),'rw'),
            'DILatchStatus12':(0x000093,('bit',0),'rw'),
            'DILatchStatus13':(0x000094,('bit',0),'rw'),
            'DILatchStatus14':(0x000095,('bit',0),'rw'),
            'DILatchStatus15':(0x000096,('bit',0),'rw')
        }
        self.ADAM6056 = {
            **self.DigitalParameters['DO0-3'],
            **self.DigitalParameters['DO4-7'],
            **self.DigitalParameters['DO8-15'],
            **self.DigitalParameters['PWMOutputs0-15'],
            **self.DigitalParameters['CommonDO'],
            **self.DigitalParameters['Common'],
            **self.CommonParameters
        }
        self.ADAM6260 = {
            **self.DigitalParameters['DO0-3'],
            **self.DigitalParameters['PWMOutputs0-5'],
            **self.DigitalParameters['CommonDO'],
            **self.DigitalParameters['Common'],
            **self.CommonParameters,
            'DO4':(0x000021,('bit',0),'rw'),
            'DO5':(0x000022,('bit',0),'rw'),
        }
        self.ADAM6266 = {
            **self.DigitalParameters['DO0-3'],
            **self.DigitalParameters['DI0-3'],
            **self.DigitalParameters['Counter0-3'],
            **self.DigitalParameters['PWMOutputs0-3'],
            **self.DigitalParameters['CommonDI'],
            **self.DigitalParameters['CommonDO'],
            **self.DigitalParameters['Common'],
            **self.CommonParameters,
            'DILatchStatus0':(0x000045,('bit',0),'rw'),
            'DILatchStatus1':(0x000046,('bit',0),'rw'),
            'DILatchStatus2':(0x000047,('bit',0),'rw'),
            'DILatchStatus3':(0x000048,('bit',0),'rw'),
        }
        self.ADAM6224 = {
            **self.DigitalParameters['DI0-3'],
            **self.DigitalParameters['CommonDI'],
            **self.AnalogParameters['AO0-3'],
            **self.AnalogParameters['CommonAO'],
            **self.CommonParameters,
            'SafetyValue0':(0x40411,('int',0),"rw"),
            'SafetyValue1':(0x40412,('int',0),"rw"),
            'SafetyValue2':(0x40413,('int',0),"rw"),
            'SafetyValue3':(0x40414,('int',0),"rw"),
            'StartupValue0':(0x40401,('int',0),"rw"),
            'StartupValue1':(0x40402,('int',0),"rw"),
            'StartupValue2':(0x40403,('int',0),"rw"),
            'StartupValue3':(0x40404,('int',0),"rw"),
            'DIEventStatus0':(0x40111,('int',0),"r"),
            'DIEventStatus1':(0x40112,('int',0),"r"),
            'DIEventStatus2':(0x40113,('int',0),"r"),
            'DIEventStatus3':(0x40114,('int',0),"r"),
            'DIEventStatusBitmask':{
                    '0x01':'Unreliable DI value (UART timeout)',
                    '0x02':'Safety Value triggered',
                    '0x04':'Startup Value triggered'}
        }
        self.ADAM6217 = {
            **self.AnalogParameters['AI0-3'],
            **self.AnalogParameters['AI4-7'],
            **self.AnalogParameters['CommonAI'],
            **self.AnalogParameters['common'],
            **self.CommonParameters
        }
        self.ADAM6017 = {
            **self.ADAM6217,
            **self.ADAM6000GCLInternalCounterValue
        }
        self.ADAM6018 = {
            **self.ADAM6217,
            **self.DigitalParameters['DO0-3'],
            **self.DigitalParameters['DO4-7'],
            **self.DigitalParameters['CommonDO']
        }
        self.ADAM6024 = {
            **self.DigitalParameters['DI0-1'],
            **self.DigitalParameters['DO0-1'],
            **self.AnalogParameters['ADAM6000DI0-5'],
            **self.AnalogParameters['ADAM6000DO0-1'],
            **self.DigitalParameters['CommonDI'],
            **self.DigitalParameters['CommonDO']
            **self.CommonParameters
        }
        self.ADAM6015 = {
            **self.AnalogParameters['AI0-3'],
            **self.AnalogParameters['AI4-6'],
            **self.AnalogParameters['CommonAI'],
            **self.AnalogParameters['common'],
            **self.CommonParameters,
            'ModuleName1':(0x40211,('int',0),'r'),
            'ModuleName2':(0x40212,('int',0),'r')
        }
        self.ADAM6060 = {} #TODO
        self.ADAM6066 = {} #TODO

class ADAMDataAcquisitionModule(ModbusClient):
    def __init__(self, shared, lock, moduleName = 'ADAM6052', address = '192.168.0.1', port = 502, *args, **kwargs):
        super().__init__(address, port, *args, **kwargs)
        self.moduleName = moduleName
        self.Shared = shared
        self.Lock = lock
        try:
            self.addresses = eval('ADAMModule().' + str(moduleName))
        except:
            raise ParameterDictionaryError(self.Shared, self.Lock, 'ADAMDataAcquisitionModule.__init__, parameter = ' + str(moduleName))

    def WithLock(self, f, *args, **kwargs):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            self.Lock.acquire()
            value = f(self, *args, **kwargs)
            self.Lock.release()
            return value
        return wrapper

    def __getAddress(self, parameterName):
        try:
            return self.addresses[parameterName][0]
        except:
            raise ParameterDictionaryError(self.Shared, self.Lock, self.moduleName + ' __getAddress, parameter = ' + str(parameterName))

    def read_coils(self, input = 'DI0', NumberOfCoils = 1, **kwargs):
        inputError = partial(ParameterDictionaryError, self.Shared, self.Lock, self.moduleName + ' read_coils, parameter = ' + str(input))
        accessError = partial(ParameterIsNotReadable, self.Shared, self.Lock, self.moduleName + ' read_coils, parameter = ' + str(input))
        access = ''
        if isinstance(input,str):
            if 'I' in input or 'DI' in input:
                try:
                    with self.addresses['DI' + ''.join(re.findall(r'\d',input))] as ParameterTuple:
                        address, access = ParameterTuple[::len(ParameterTuple)-1]
                except:
                    raise inputError
            else:
                raise inputError
        if isinstance(input,int):
            try:
                with self.addresses['DI' + str(input)] as ParameterTuple:
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise inputError
        if access == 'w':
            raise accessError
        return super().read_coils(address, NumberOfCoils, **kwargs)

    def write_coils(self, startCoil = 'DO0', listOfValues = [True], **kwargs):
        inputError = partial(ParameterDictionaryError, self.Shared, self.Lock, self.moduleName + ' write_coils, parameter = ' + str(startCoil))
        accessError = partial(ParameterIsNotWritable, self.Shared, self.Lock, self.moduleName + ' write_coils, parameter = ' + str(startCoil))
        access = ''
        if isinstance(startCoil,str):
            if 'O' in startCoil or 'DO' in startCoil:
                try:
                    with self.addresses['DO' + ''.join(re.findall(r'\d',startCoil))] as ParameterTuple:
                        address, access = ParameterTuple[::len(ParameterTuple)-1]
                except:
                    raise inputError
            else:
                raise inputError
        if isinstance(startCoil,int):
            try:
                with self.addresses['DO' + str(startCoil)] as ParameterTuple:
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise inputError
        if access == 'r':
            raise accessError
        return super().write_coils(address, listOfValues, **kwargs)

    def write_coil(self, Coil, value, **kwargs):
        inputError = partial(ParameterDictionaryError, self.Shared, self.Lock, self.moduleName + ' write_coil, parameter = ' + str(Coil))
        accessError = partial(ParameterIsNotWritable, self.Shared, self.Lock, self.moduleName + ' write_coil, parameter = ' + str(Coil))
        access = ''
        if isinstance(Coil,str):
            if 'O' in Coil or 'DO' in Coil:
                try:
                    with self.addresses['DO' + ''.join(re.findall(r'\d',Coil))] as ParameterTuple:
                        address, access = ParameterTuple[::len(ParameterTuple)-1]
                except:
                    raise inputError
            else:
                raise inputError
        if isinstance(Coil,int):
            try:
                with self.addresses['DO' + str(Coil)] as ParameterTuple:
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise inputError
        if access == 'r':
            raise accessError
        return super().write_coil(address, value, **kwargs)

    def read_discrete_inputs(self, InputToStartFrom = 'DI0', count=1, **kwargs):
        inputError = partial(ParameterDictionaryError, self.Shared, self.Lock, self.moduleName + ' read_discrete_inputs, parameter = ' + str(InputToStartFrom))
        accessError = partial(ParameterIsNotReadable, self.Shared, self.Lock, self.moduleName + ' read_discrete_inputs, parameter = ' + str(InputToStartFrom))
        access = ''
        if isinstance(InputToStartFrom,str):
            if 'I' in InputToStartFrom or 'DI' in InputToStartFrom:
                try:
                    with self.addresses['DI' + ''.join(re.findall(r'\d',InputToStartFrom))] as ParameterTuple:
                        address, access = ParameterTuple[::len(ParameterTuple)-1]
                except:
                    raise inputError
            else:
                raise inputError
        if isinstance(InputToStartFrom,int):
            try:
                with self.addresses['DO' + str(InputToStartFrom)] as ParameterTuple:
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise inputError
        if access == 'w':
            raise accessError
        return super().read_discrete_inputs(address, count, **kwargs)
    
    def read_holding_registers(self, registerToStartFrom = 'Counter/FrequencyValue0', count=1, **kwargs):
        inputError = partial(ParameterDictionaryError, self.Shared, self.Lock, self.moduleName + ' read_holding_registers, parameter = ' + str(registerToStartFrom))
        accessError = partial(ParameterIsNotReadable, self.Shared, self.Lock, self.moduleName + ' read_holding_registers, parameter = ' + str(registerToStartFrom))
        access = ''
        if isinstance(registerToStartFrom,str):
            try:
                with self.addresses[registerToStartFrom] as ParameterTuple:
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise inputError
        else:
            raise inputError
        if access == 'w':
            raise accessError
        return super().read_holding_registers(address, count, **kwargs)

    def read_input_registers(self, registerToStartFrom = 'DIvalue', count=1, **kwargs):
        inputError = partial(ParameterDictionaryError, self.Shared, self.Lock, self.moduleName + ' read_input_registers, parameter = ' + str(registerToStartFrom))
        accessError = partial(ParameterIsNotReadable, self.Shared, self.Lock, self.moduleName + ' read_input_registers, parameter = ' + str(registerToStartFrom))
        access = ''
        if isinstance(registerToStartFrom,str):
            try:
                with self.addresses[registerToStartFrom] as ParameterTuple:
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise inputError
        else:
            raise inputError
        if access == 'w':
            raise accessError
        return super().read_input_registers(address, count, **kwargs)
    
    def write_register(self, register = '', value = 0xFFFF, **kwargs):
        inputError = partial(ParameterDictionaryError, self.Shared, self.Lock, self.moduleName + ' write_register, parameter = ' + str(register))
        accessError = partial(ParameterIsNotWritable, self.Shared, self.Lock, self.moduleName + ' write_register, parameter = ' + str(register))
        access = ''
        if isinstance(register,str):
            try:
                with self.addresses[register] as ParameterTuple:
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise inputError
        else:
            raise inputError
        if access == 'r':
            raise accessError
        return super().write_registers(address, value, **kwargs)

    def write_registers(self, registerToStartFrom = '', values = [0xFFFF], **kwargs):
        inputError = partial(ParameterDictionaryError, self.Shared, self.Lock, self.moduleName + ' write_registers, parameter = ' + str(registerToStartFrom))
        accessError = partial(ParameterIsNotWritable, self.Shared, self.Lock, self.moduleName + ' write_registers, parameter = ' + str(registerToStartFrom))
        access = ''
        if isinstance(registerToStartFrom,str):
            try:
                with self.addresses[registerToStartFrom] as ParameterTuple:
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise inputError
        else:
            raise inputError
        if access == 'r':
            raise accessError
        return super().write_registers(address, values, **kwargs)

class ParameterDictionaryError(ValueError):
    def __init__(self, shared, lock, *args, **kwargs):
        self.args = args
        lock.acquire()
        shared['Errors'] += 'Invalid key for parameter dictionary in ' + ''.join(map(str, *args))
        shared['Error'][2] = True #High errorLevel
        lock.release()
    
class ParameterIsNotReadable(TypeError):
    def __init__(self, shared, lock, *args, **kwargs):
        self.args = args
        lock.acquire()
        shared['Errors'] += 'Trying to read from write-only register in ' + ''.join(map(str, *args))
        shared['Error'][2] = True #High errorLevel
        lock.release()

class ParameterIsNotWritable(TypeError):
    def __init__(self, shared, lock, *args, **kwargs):
        self.args = args
        lock.acquire()
        shared['Errors'] += 'Trying to write to read-only register in ' + ''.join(map(str, *args))
        shared['Error'][2] = True #High errorLevel
        lock.release()
    
