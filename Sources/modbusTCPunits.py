from pymodbus.client.sync import ModbusTcpClient
from functools import wraps, partial
from pymodbus.transaction import ModbusAsciiFramer, ModbusSocketFramer, ModbusBinaryFramer, ModbusRtuFramer
from pymodbus.factory import ClientDecoder
from pymodbus.register_read_message import ReadHoldingRegistersResponse
from Sources.TactWatchdog import TactWatchdog as WDT
from Sources import Bits, ErrorEventWrite
import re, json
import struct
from pymodbus.framer import SOCKET_FRAME_HEADER

class ADAMModule(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.CommonParameters = {
            'ClearGCLCounterCh0':(301,('bit',0),"w"),
            'ClearGCLCounterCh1':(302,('bit',0),"w"),
            'ClearGCLCounterCh2':(303,('bit',0),"w"),
            'ClearGCLCounterCh3':(304,('bit',0),"w"),
            'ClearGCLCounterCh4':(305,('bit',0),"w"),
            'ClearGCLCounterCh5':(306,('bit',0),"w"),
            'ClearGCLCounterCh6':(307,('bit',0),"w"),
            'ClearGCLCounterCh7':(308,('bit',0),"w"),
            'GCLInternalFlagValue':(40305,('int',0),"rw")}
        self.ADAM6000GCLInternalCounterValue = {
            'GCLInternalCounterValueCh0':(40311,('word',0),"w"),
            'GCLInternalCounterValueCh1':(40313,('word',0),"w"),
            'GCLInternalCounterValueCh2':(40315,('word',0),"w"),
            'GCLInternalCounterValueCh3':(40317,('word',0),"w"),
            'GCLInternalCounterValueCh4':(40319,('word',0),"w"),
            'GCLInternalCounterValueCh5':(40321,('word',0),"w"),
            'GCLInternalCounterValueCh6':(40323,('word',0),"w"),
            'GCLInternalCounterValueCh7':(40325,('word',0),"w")}
        self.AnalogParameters = {
            'ADAM600AI0-5':{
                'BurnoutFlagCh0':(121,('bit',0),"r"),
                'BurnoutFlagCh1':(122,('bit',0),"r"),
                'BurnoutFlagCh2':(123,('bit',0),"r"),
                'BurnoutFlagCh3':(124,('bit',0),"r"),
                'AIValueCh0':(40001,('int',0),"r"),
                'AIValueCh1':(40002,('int',0),"r"),
                'AIValueCh2':(40003,('int',0),"r"),
                'AIValueCh3':(40004,('int',0),"r"),
                'AIStatusCh0':(40021,('word',0),"r"),
                'AIStatusCh1':(40022,('word',0),"r"),
                'AIStatusCh2':(40023,('word',0),"r"),
                'AIStatusCh3':(40024,('word',0),"r"),
                'TypeCodeCh0':(40201,('int',0),"rw"),
                'TypeCodeCh1':(40202,('int',0),"rw"),
                'TypeCodeCh2':(40203,('int',0),"rw"),
                'TypeCodeCh3':(40204,('int',0),"rw"),
                'BurnoutFlagCh4':(125,('bit',0),"r"),
                'BurnoutFlagCh5':(126,('bit',0),"r"),
                'HighAlarmFlagCh4':(135,('bit',0),"r"),
                'HighAlarmFlagCh5':(136,('bit',0),"r"),
                'LowAlarmFlagCh4':(145,('bit',0),"r"),
                'LowAlarmFlagCh5':(146,('bit',0),"r"),
                'AIValueCh4':(40005,('int',0),"r"),
                'AIValueCh5':(40006,('int',0),"r"),
                'AIStatusCh4':(40025,('word',0),"r"),
                'AIStatusCh5':(40026,('word',0),"r"),
                'TypeCodeCh4':(40205,('int',0),"rw"),
                'TypeCodeCh5':(40206,('int',0),"rw")},
            'AI0-3':{
                'ResetHistoricalMaxCh0':(101,('bit',0),"w"),
                'ResetHistoricalMaxCh1':(102,('bit',0),"w"),
                'ResetHistoricalMaxCh2':(103,('bit',0),"w"),
                'ResetHistoricalMaxCh3':(104,('bit',0),"w"),
                'ResetHistoricalMinCh0':(111,('bit',0),"w"),
                'ResetHistoricalMinCh1':(112,('bit',0),"w"),
                'ResetHistoricalMinCh2':(113,('bit',0),"w"),
                'ResetHistoricalMinCh3':(114,('bit',0),"w"),
                'BurnoutFlagCh0':(121,('bit',0),"r"),
                'BurnoutFlagCh1':(122,('bit',0),"r"),
                'BurnoutFlagCh2':(123,('bit',0),"r"),
                'BurnoutFlagCh3':(124,('bit',0),"r"),
                'HighAlarmFlagCh0':(131,('bit',0),"r"),
                'HighAlarmFlagCh1':(132,('bit',0),"r"),
                'HighAlarmFlagCh2':(133,('bit',0),"r"),
                'HighAlarmFlagCh3':(134,('bit',0),"r"),
                'LowAlarmFlagCh0':(141,('bit',0),"r"),
                'LowAlarmFlagCh1':(142,('bit',0),"r"),
                'LowAlarmFlagCh2':(143,('bit',0),"r"),
                'LowAlarmFlagCh3':(144,('bit',0),"r"),
                'AIValueCh0':(40001,('int',0),"r"),
                'AIValueCh1':(40002,('int',0),"r"),
                'AIValueCh2':(40003,('int',0),"r"),
                'AIValueCh3':(40004,('int',0),"r"),
                'HistoricalMaxAIValueCh0':(40011,('int',0),"r"),
                'HistoricalMaxAIValueCh1':(40012,('int',0),"r"),
                'HistoricalMaxAIValueCh2':(40013,('int',0),"r"),
                'HistoricalMaxAIValueCh3':(40014,('int',0),"r"),
                'HistoricalMinAIValueCh0':(40021,('int',0),"r"),
                'HistoricalMinAIValueCh1':(40022,('int',0),"r"),
                'HistoricalMinAIValueCh2':(40023,('int',0),"r"),
                'HistoricalMinAIValueCh3':(40024,('int',0),"r"),
                'AIStatusCh0':(40101,('word',0),"r"),
                'AIStatusCh1':(40103,('word',0),"r"),
                'AIStatusCh2':(40105,('word',0),"r"),
                'AIStatusCh3':(40107,('word',0),"r"),
                'AIFloatingValueCh0':(40031,('word',0),"r"),
                'AIFloatingValueCh1':(40033,('word',0),"r"),
                'AIFloatingValueCh2':(40035,('word',0),"r"),
                'AIFloatingValueCh3':(40037,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh0':(40051,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh1':(40053,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh2':(40055,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh3':(40057,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh0':(40071,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh1':(40073,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh2':(40075,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh3':(40077,('word',0),"r"),
                'TypeCodeCh0':(40201,('int',0),"rw"),
                'TypeCodeCh1':(40202,('int',0),"rw"),
                'TypeCodeCh2':(40203,('int',0),"rw"),
                'TypeCodeCh3':(40204,('int',0),"rw")},
            'AI4-5':{
                'ResetHistoricalMaxCh4':(105,('bit',0),"w"),
                'ResetHistoricalMaxCh5':(106,('bit',0),"w"),
                'ResetHistoricalMinCh4':(115,('bit',0),"w"),
                'ResetHistoricalMinCh5':(116,('bit',0),"w"),
                'BurnoutFlagCh4':(125,('bit',0),"r"),
                'BurnoutFlagCh5':(126,('bit',0),"r"),
                'HighAlarmFlagCh4':(135,('bit',0),"r"),
                'HighAlarmFlagCh5':(136,('bit',0),"r"),
                'LowAlarmFlagCh4':(145,('bit',0),"r"),
                'LowAlarmFlagCh5':(146,('bit',0),"r"),
                'AIValueCh4':(40005,('int',0),"r"),
                'AIValueCh5':(40006,('int',0),"r"),
                'HistoricalMaxAIValueCh4':(40015,('int',0),"r"),
                'HistoricalMaxAIValueCh5':(40016,('int',0),"r"),
                'HistoricalMinAIValueCh4':(40025,('int',0),"r"),
                'HistoricalMinAIValueCh5':(40026,('int',0),"r"),
                'AIStatusCh4':(40109,('word',0),"r"),
                'AIStatusCh5':(40111,('word',0),"r"),
                'AIFloatingValueCh4':(40039,('word',0),"r"),
                'AIFloatingValueCh5':(40041,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh4':(40059,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh5':(40061,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh4':(40079,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh5':(40081,('word',0),"r"),
                'TypeCodeCh4':(40205,('int',0),"rw"),
                'TypeCodeCh5':(40206,('int',0),"rw")},
            'AI4-6':{
                'ResetHistoricalMaxCh4':(105,('bit',0),"w"),
                'ResetHistoricalMaxCh5':(106,('bit',0),"w"),
                'ResetHistoricalMinCh4':(115,('bit',0),"w"),
                'ResetHistoricalMinCh5':(116,('bit',0),"w"),
                'BurnoutFlagCh4':(125,('bit',0),"r"),
                'BurnoutFlagCh5':(126,('bit',0),"r"),
                'HighAlarmFlagCh4':(135,('bit',0),"r"),
                'HighAlarmFlagCh5':(136,('bit',0),"r"),
                'LowAlarmFlagCh4':(145,('bit',0),"r"),
                'LowAlarmFlagCh5':(146,('bit',0),"r"),
                'AIValueCh4':(40005,('int',0),"r"),
                'AIValueCh5':(40006,('int',0),"r"),
                'HistoricalMaxAIValueCh4':(40015,('int',0),"r"),
                'HistoricalMaxAIValueCh5':(40016,('int',0),"r"),
                'HistoricalMinAIValueCh4':(40025,('int',0),"r"),
                'HistoricalMinAIValueCh5':(40026,('int',0),"r"),
                'AIStatusCh4':(40109,('word',0),"r"),
                'AIStatusCh5':(40111,('word',0),"r"),
                'AIFloatingValueCh4':(40039,('word',0),"r"),
                'AIFloatingValueCh5':(40041,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh4':(40059,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh5':(40061,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh4':(40079,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh5':(40081,('word',0),"r"),
                'TypeCodeCh4':(40205,('int',0),"rw"),
                'TypeCodeCh5':(40206,('int',0),"rw"),
                'ResetHistoricalMaxCh6':(107,('bit',0),"w"),
                'ResetHistoricalMinCh6':(117,('bit',0),"w"),
                'BurnoutFlagCh6':(127,('bit',0),"r"),
                'HighAlarmFlagCh6':(137,('bit',0),"r"),
                'LowAlarmFlagCh6':(147,('bit',0),"r"),
                'AIValueCh6':(40007,('int',0),"r"),
                'HistoricalMaxAIValueCh6':(40017,('int',0),"r"),
                'HistoricalMinAIValueCh6':(40027,('int',0),"r"),
                'AIStatusCh6':(40113,('word',0),"r"),
                'AIFloatingValueCh6':(40043,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh6':(40063,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh6':(40083,('word',0),"r"),
                'TypeCodeCh6':(40207,('int',0),"rw")},
            'AI4-7':{
                'ResetHistoricalMaxCh4':(105,('bit',0),"w"),
                'ResetHistoricalMaxCh5':(106,('bit',0),"w"),
                'ResetHistoricalMinCh4':(115,('bit',0),"w"),
                'ResetHistoricalMinCh5':(116,('bit',0),"w"),
                'BurnoutFlagCh4':(125,('bit',0),"r"),
                'BurnoutFlagCh5':(126,('bit',0),"r"),
                'HighAlarmFlagCh4':(135,('bit',0),"r"),
                'HighAlarmFlagCh5':(136,('bit',0),"r"),
                'LowAlarmFlagCh4':(145,('bit',0),"r"),
                'LowAlarmFlagCh5':(146,('bit',0),"r"),
                'AIValueCh4':(40005,('int',0),"r"),
                'AIValueCh5':(40006,('int',0),"r"),
                'HistoricalMaxAIValueCh4':(40015,('int',0),"r"),
                'HistoricalMaxAIValueCh5':(40016,('int',0),"r"),
                'HistoricalMinAIValueCh4':(40025,('int',0),"r"),
                'HistoricalMinAIValueCh5':(40026,('int',0),"r"),
                'AIStatusCh4':(40109,('word',0),"r"),
                'AIStatusCh5':(40111,('word',0),"r"),
                'AIFloatingValueCh4':(40039,('word',0),"r"),
                'AIFloatingValueCh5':(40041,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh4':(40059,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh5':(40061,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh4':(40079,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh5':(40081,('word',0),"r"),
                'TypeCodeCh4':(40205,('int',0),"rw"),
                'TypeCodeCh5':(40206,('int',0),"rw"),
                'ResetHistoricalMaxCh6':(107,('bit',0),"w"),
                'ResetHistoricalMinCh6':(117,('bit',0),"w"),
                'BurnoutFlagCh6':(127,('bit',0),"r"),
                'HighAlarmFlagCh6':(137,('bit',0),"r"),
                'LowAlarmFlagCh6':(147,('bit',0),"r"),
                'AIValueCh6':(40007,('int',0),"r"),
                'HistoricalMaxAIValueCh6':(40017,('int',0),"r"),
                'HistoricalMinAIValueCh6':(40027,('int',0),"r"),
                'AIStatusCh6':(40113,('word',0),"r"),
                'AIFloatingValueCh6':(40043,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh6':(40063,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh6':(40083,('word',0),"r"),
                'TypeCodeCh6':(40207,('int',0),"rw"),
                'ResetHistoricalMaxCh7':(108,('bit',0),"w"),
                'ResetHistoricalMinCh7':(118,('bit',0),"w"),
                'BurnoutFlagCh7':(128,('bit',0),"r"),
                'HighAlarmFlagCh7':(138,('bit',0),"r"),
                'LowAlarmFlagCh7':(148,('bit',0),"r"),
                'AIValueCh7':(40008,('int',0),"r"),
                'HistoricalMaxAIValueCh7':(40018,('int',0),"r"),
                'HistoricalMinAIValueCh7':(40028,('int',0),"r"),
                'AIStatusCh7':(40115,('word',0),"r"),
                'AIFloatingValueCh7':(40045,('word',0),"r"),
                'HistoricalMaxAIFloatingValueCh7':(40065,('word',0),"r"),
                'HistoricalMinAIFloatingValueCh7':(40085,('word',0),"r"),
                'TypeCodeCh7':(40208,('int',0),"rw")},
            'CommonAI':{
                'AIStatusBitmask':{
                    '0x00000001':'Failed to provide AI value (UART timeout)',
                    '0x00000002':'Over Range',
                    '0x00000004':'Under Range',
                    '0x00000008':'Open circuit(Burnout)',
                    '0x00000080':'AD Converter failed',
                    '0x00000200':'Zero/Span Calibration Error'},
                'ResetHistoricalMaxAvCh0-7':(109,('bit',0),"w"),
                'ResetHistoricalMinAvCh0-7':(119,('bit',0),"w"),
                'HighAlarmFlagAvCh0-7':(139,('bit',0),"r"),
                'LowAlarmFlagAvCh0-7':(149,('bit',0),"r"),
                'AIValueAvCh0-7':(40009,('int',0),"r"),
                'HistoricalMaxAIValueAvCh0-7':(40019,('int',0),"r"),
                'HistoricalMinAIValueAvCh0-7':(40029,('int',0),"r"),
                'AIFloatingValueAvCh0-7':(40047,('word',0),"r"),
                'HistoricalMaxAIFloatingValueAvCh0-7':(40067,('word',0),"r"),
                'HistoricalMinAIFloatingValueAvCh0-7':(40087,('word',0),"r"),
                'TypeCodeAvCh0-7':(40209,('int',0),"rw"),
                'AIChannelEnable':(40221,('int',0),"rw")},
            'ADAM600AO0-1':{
                'AOValueCh0':(40001,('int',0),"rw"),
                'AOValueCh1':(40002,('int',0),"rw"),
                'AOStatusCh0':(40101,('word',0),"r"), #4bytes
                'AOStatusCh1':(40103,('word',0),"r"),
                'AOStatusBitmask':{
                    '0x00000001':'Failed to provide AO value (UART timeout)',
                    '0x00000004':'No Output Current',
                    '0x00000080':'AD Converter failed',
                    '0x00000200':'Zero/Span Calibration Error',
                    '0x00010000':'DI triggered to Safety Value',
                    '0x00040200':'DI triggered to Statup Value',
                    '0x00080200':'AO triggered to Fail Safety Value'},
                    'TypeCodeCh0':(40201,('int',0),"rw"), #2bytes
                    'TypeCodeCh1':(40202,('int',0),"rw")},
            'AO0-1':{
                'AOValueCh0':(40001,('int',0),"rw"),
                'AOValueCh1':(40002,('int',0),"rw"),
                'AOStatusCh0':(40101,('word',0),"r"), #4bytes
                'AOStatusCh1':(40103,('word',0),"r")},
            'AO0-3':{
                'AOValueCh0':(40001,('int',0),"rw"),
                'AOValueCh1':(40002,('int',0),"rw"),
                'AOStatusCh0':(40101,('word',0),"r"), #4bytes
                'AOStatusCh1':(40103,('word',0),"r"),
                'AOValueCh2':(40003,('int',0),"rw"),
                'AOValueCh3':(40004,('int',0),"rw"),
                'AOStatusCh2':(40105,('word',0),"r"),
                'AOStatusCh3':(40107,('word',0),"r"),
                'TypeCodeCh2':(40203,('int',0),"rw"),
                'TypeCodeCh3':(40204,('int',0),"rw"),
                'TypeCodeAvCh0-7':(40209,('int',0),"rw")},
            'AO4-7':{},
            'CommonAO':{
                'AOStatusBitmask':{
                '0x00000001':'Failed to provide AO value (UART timeout)',
                '0x00000004':'No Output Current',
                '0x00000080':'AD Converter failed',
                '0x00000200':'Zero/Span Calibration Error',
                '0x00010000':'DI triggered to Safety Value',
                '0x00040200':'DI triggered to Statup Value',
                '0x00080200':'AO triggered to Fail Safety Value'},
                'TypeCodeCh0':(40201,('int',0),"rw"), #2bytes
                'TypeCodeCh1':(40202,('int',0),"rw")},
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
                '0x0321':'NI604(518) 0 ~ 100 C'},}}
        self.DigitalParameters = {
            'DI0-1':{
                'DI0':(1,('bit',0),'r'),
                'DI1':(2,('bit',0),'r')},
            'DI0-3':{
                'DI0':(1,('bit',0),'r'),
                'DI1':(2,('bit',0),'r'),
                'DI2':(3,('bit',0),'r'),
                'DI3':(4,('bit',0),'r')},
            'DI4-7':{
                'DI4':(5,('bit',0),'r'),
                'DI5':(6,('bit',0),'r'),
                'DI6':(7,('bit',0),'r'),
                'DI7':(8,('bit',0),'r')},
            'DI8-11':{
                'DI8':(9,('bit',0),'r'),
                'DI9':(10,('bit',0),'r'),
                'DI10':(11,('bit',0),'r'),
                'DI11':(12,('bit',0),'r')},
            'DI8-15':{
                'DI8':(9,('bit',0),'r'),
                'DI9':(10,('bit',0),'r'),
                'DI10':(11,('bit',0),'r'),
                'DI11':(12,('bit',0),'r'),
                'DI12':(13,('bit',0),'r'),
                'DI13':(14,('bit',0),'r'),
                'DI14':(15,('bit',0),'r'),
                'DI15':(16,('bit',0),'r')},
            'CommonDI':{
                'DIValue':(40301,('word',0),"r")},
            'DO0-1':{
                'DO0':(17,('bit',0),'rw'),
                'DO1':(18,('bit',0),'rw')},
            'DO0-3':{
                'DO0':(17,('bit',0),'rw'),
                'DO1':(18,('bit',0),'rw'),
                'DO2':(19,('bit',0),'rw'),
                'DO3':(20,('bit',0),'rw')},
            'DO4-5':{
                'DO4':(21,('bit',0),'rw'),
                'DO5':(22,('bit',0),'rw')},
            'DO4-7':{
                'DO4':(21,('bit',0),'rw'),
                'DO5':(22,('bit',0),'rw'),
                'DO6':(23,('bit',0),'rw'),
                'DO7':(24,('bit',0),'rw')},
            'DO8-11':{
                'DO8':(25,('bit',0),'r'),
                'DO9':(26,('bit',0),'r'),
                'DO10':(27,('bit',0),'r'),
                'DO11':(28,('bit',0),'r')},
            'DO8-15':{
                'DO8':(25,('bit',0),'r'),
                'DO9':(26,('bit',0),'r'),
                'DO10':(27,('bit',0),'r'),
                'DO11':(28,('bit',0),'r'),
                'DO12':(29,('bit',0),'r'),
                'DO13':(30,('bit',0),'r'),
                'DO14':(31,('bit',0),'r'),
                'DO15':(32,('bit',0),'r')},
            'CommonDO':{
                'DOValue':(40303,('word',0),"rw")},
            'Counter0-3':{
                'CounterStartStop0':(33,('bit',0),'rw'),
                'CounterStartStop1':(34,('bit',0),'rw'),
                'CounterStartStop2':(35,('bit',0),'rw'),
                'CounterStartStop3':(36,('bit',0),'rw'),
                'ClearCounter0':(37,('bit',0),'rw'),
                'ClearCounter1':(38,('bit',0),'rw'),
                'ClearCounter2':(39,('bit',0),'rw'),
                'ClearCounter3':(40,('bit',0),'rw'),
                'ClearOverflow0':(41,('bit',0),'rw'),
                'ClearOverflow1':(42,('bit',0),'rw'),
                'ClearOverflow2':(43,('bit',0),'rw'),
                'ClearOverflow3':(44,('bit',0),'rw'),
                'Counter/FrequencyValue0':(40001,('word',0),"r"),
                'Counter/FrequencyValue1':(40003,('word',0),"r"),
                'Counter/FrequencyValue2':(40005,('word',0),"r"),
                'Counter/FrequencyValue3':(40007,('word',0),"r")},
            'Counter0-7':{
                'CounterStartStop0':(33,('bit',0),'rw'),
                'CounterStartStop1':(34,('bit',0),'rw'),
                'CounterStartStop2':(35,('bit',0),'rw'),
                'CounterStartStop3':(36,('bit',0),'rw'),
                'CounterStartStop4':(37,('bit',0),'rw'),
                'CounterStartStop5':(38,('bit',0),'rw'),
                'CounterStartStop6':(39,('bit',0),'rw'),
                'CounterStartStop7':(40,('bit',0),'rw'),
                'ClearCounter0':(41,('bit',0),'rw'),
                'ClearCounter1':(42,('bit',0),'rw'),
                'ClearCounter2':(43,('bit',0),'rw'),
                'ClearCounter3':(44,('bit',0),'rw'),
                'ClearCounter4':(45,('bit',0),'rw'),
                'ClearCounter5':(46,('bit',0),'rw'),
                'ClearCounter6':(47,('bit',0),'rw'),
                'ClearCounter7':(48,('bit',0),'rw'),
                'ClearOverflow0':(49,('bit',0),'rw'),
                'ClearOverflow1':(50,('bit',0),'rw'),
                'ClearOverflow2':(51,('bit',0),'rw'),
                'ClearOverflow3':(52,('bit',0),'rw'),
                'ClearOverflow4':(53,('bit',0),'rw'),
                'ClearOverflow5':(54,('bit',0),'rw'),
                'ClearOverflow6':(55,('bit',0),'rw'),
                'ClearOverflow7':(56,('bit',0),'rw'),
                'Counter/FrequencyValue0':(40001,('word',0),"r"),
                'Counter/FrequencyValue1':(40003,('word',0),"r"),
                'Counter/FrequencyValue2':(40005,('word',0),"r"),
                'Counter/FrequencyValue3':(40007,('word',0),"r"),
                'Counter/FrequencyValue4':(40009,('word',0),"r"),
                'Counter/FrequencyValue5':(40011,('word',0),"r"),
                'Counter/FrequencyValue6':(40013,('word',0),"r"),
                'Counter/FrequencyValue7':(40015,('word',0),"r")},
            'Counter/FrequencyValue0-3':{
                'Counter/FrequencyValue0':(40001,('word',0),"r"),
                'Counter/FrequencyValue1':(40003,('word',0),"r"),
                'Counter/FrequencyValue2':(40005,('word',0),"r"),
                'Counter/FrequencyValue3':(40007,('word',0),"r")},
            'Counter/FrequencyValue4-7':{
                'Counter/FrequencyValue4':(40009,('word',0),"r"),
                'Counter/FrequencyValue5':(40011,('word',0),"r"),
                'Counter/FrequencyValue6':(40013,('word',0),"r"),
                'Counter/FrequencyValue7':(40015,('word',0),"r")},
            'Counter/FrequencyValue0-11':{
                'Counter/FrequencyValue0':(40001,('word',0),"r"),
                'Counter/FrequencyValue1':(40003,('word',0),"r"),
                'Counter/FrequencyValue2':(40005,('word',0),"r"),
                'Counter/FrequencyValue3':(40007,('word',0),"r"),
                'Counter/FrequencyValue4':(40009,('word',0),"r"),
                'Counter/FrequencyValue5':(40011,('word',0),"r"),
                'Counter/FrequencyValue6':(40013,('word',0),"r"),
                'Counter/FrequencyValue7':(40015,('word',0),"r"),
                'Counter/FrequencyValue8':(40017,('word',0),"r"),
                'Counter/FrequencyValue9':(40019,('word',0),"r"),
                'Counter/FrequencyValue10':(40021,('word',0),"r"),
                'Counter/FrequencyValue11':(40023,('word',0),"r")},
            'PWMOutput0-3':{
                'PulseOutputLowLevelWidth0':(40009,('word',0),"rw"),
                'PulseOutputLowLevelWidth1':(40011,('word',0),"rw"),
                'PulseOutputLowLevelWidth2':(40013,('word',0),"rw"),
                'PulseOutputLowLevelWidth3':(40015,('word',0),"rw"),
                'PulseOutputHighLevelWidth0':(40017,('word',0),"rw"),
                'PulseOutputHighLevelWidth1':(40019,('word',0),"rw"),
                'PulseOutputHighLevelWidth2':(40021,('word',0),"rw"),
                'PulseOutputHighLevelWidth3':(40023,('word',0),"rw"),
                'SetAbsolutePulse0':(40025,('word',0),"rw"),
                'SetAbsolutePulse1':(40027,('word',0),"rw"),
                'SetAbsolutePulse2':(40029,('word',0),"rw"),
                'SetAbsolutePulse3':(40031,('word',0),"rw"),
                'SetIncrementalPulse0':(40033,('word',0),"rw"),
                'SetIncrementalPulse1':(40035,('word',0),"rw"),
                'SetIncrementalPulse2':(40037,('word',0),"rw"),
                'SetIncrementalPulse3':(40039,('word',0),"rw")},
            'ADAM6000PWMOutput0-5':{
                'PulseOutputLowLevelWidth0':(40025,('word',0),"r"),
                'PulseOutputLowLevelWidth1':(40027,('word',0),"r"),
                'PulseOutputLowLevelWidth2':(40029,('word',0),"r"),
                'PulseOutputLowLevelWidth3':(40031,('word',0),"r"),
                'PulseOutputLowLevelWidth4':(40033,('word',0),"r"),
                'PulseOutputLowLevelWidth5':(40035,('word',0),"r"),
                'PulseOutputHighLevelWidth0':(40037,('word',0),"r"),
                'PulseOutputHighLevelWidth1':(40039,('word',0),"r"),
                'PulseOutputHighLevelWidth2':(40041,('word',0),"r"),
                'PulseOutputHighLevelWidth3':(40043,('word',0),"r"),
                'PulseOutputHighLevelWidth4':(40045,('word',0),"r"),
                'PulseOutputHighLevelWidth5':(40047,('word',0),"r"),
                'SetAbsolutePulse0':(40049,('word',0),"r"),
                'SetAbsolutePulse1':(40051,('word',0),"r"),
                'SetAbsolutePulse2':(40053,('word',0),"r"),
                'SetAbsolutePulse3':(40055,('word',0),"r"),
                'SetAbsolutePulse4':(40057,('word',0),"r"),
                'SetAbsolutePulse5':(40059,('word',0),"r"),
                'SetIncrementalPulse0':(40061,('word',0),"r"),
                'SetIncrementalPulse1':(40063,('word',0),"r"),
                'SetIncrementalPulse2':(40065,('word',0),"r"),
                'SetIncrementalPulse3':(40067,('word',0),"r"),
                'SetIncrementalPulse4':(40069,('word',0),"r"),
                'SetIncrementalPulse5':(40071,('word',0),"r")},
            'PWMOutput0-5':{
                'PulseOutputLowLevelWidth0':(40001,('word',0),"rw"),
                'PulseOutputLowLevelWidth1':(40003,('word',0),"rw"),
                'PulseOutputLowLevelWidth2':(40005,('word',0),"rw"),
                'PulseOutputLowLevelWidth3':(40007,('word',0),"rw"),
                'PulseOutputLowLevelWidth4':(40009,('word',0),"rw"),
                'PulseOutputLowLevelWidth5':(40011,('word',0),"rw"),
                'PulseOutputHighLevelWidth0':(40013,('word',0),"rw"),
                'PulseOutputHighLevelWidth1':(40015,('word',0),"rw"),
                'PulseOutputHighLevelWidth2':(40017,('word',0),"rw"),
                'PulseOutputHighLevelWidth3':(40019,('word',0),"rw"),
                'PulseOutputHighLevelWidth4':(40021,('word',0),"rw"),
                'PulseOutputHighLevelWidth5':(40023,('word',0),"rw"),
                'SetAbsolutePulse0':(40025,('word',0),"rw"),
                'SetAbsolutePulse1':(40027,('word',0),"rw"),
                'SetAbsolutePulse2':(40029,('word',0),"rw"),
                'SetAbsolutePulse3':(40031,('word',0),"rw"),
                'SetAbsolutePulse4':(40033,('word',0),"rw"),
                'SetAbsolutePulse5':(40035,('word',0),"rw"),
                'SetIncrementalPulse0':(40037,('word',0),"rw"),
                'SetIncrementalPulse1':(40039,('word',0),"rw"),
                'SetIncrementalPulse2':(40041,('word',0),"rw"),
                'SetIncrementalPulse3':(40043,('word',0),"rw"),
                'SetIncrementalPulse4':(40045,('word',0),"rw"),
                'SetIncrementalPulse5':(40047,('word',0),"rw")},
            'PWMOutput0-6':{
                'PulseOutputLowLevelWidth0':(40017,('word',0),"rw"),
                'PulseOutputLowLevelWidth1':(40019,('word',0),"rw"),
                'PulseOutputLowLevelWidth2':(40021,('word',0),"rw"),
                'PulseOutputLowLevelWidth3':(40023,('word',0),"rw"),
                'PulseOutputLowLevelWidth4':(40025,('word',0),"rw"),
                'PulseOutputLowLevelWidth5':(40027,('word',0),"rw"),
                'PulseOutputLowLevelWidth6':(40029,('word',0),"rw"),
                'PulseOutputHighLevelWidth0':(40031,('word',0),"rw"),
                'PulseOutputHighLevelWidth1':(40033,('word',0),"rw"),
                'PulseOutputHighLevelWidth2':(40035,('word',0),"rw"),
                'PulseOutputHighLevelWidth3':(40037,('word',0),"rw"),
                'PulseOutputHighLevelWidth4':(40039,('word',0),"rw"),
                'PulseOutputHighLevelWidth5':(40041,('word',0),"rw"),
                'PulseOutputHighLevelWidth6':(40043,('word',0),"rw"),
                'SetAbsolutePulse0':(40045,('word',0),"rw"),
                'SetAbsolutePulse1':(40047,('word',0),"rw"),
                'SetAbsolutePulse2':(40049,('word',0),"rw"),
                'SetAbsolutePulse3':(40051,('word',0),"rw"),
                'SetAbsolutePulse4':(40053,('word',0),"rw"),
                'SetAbsolutePulse5':(40055,('word',0),"rw"),
                'SetAbsolutePulse6':(40057,('word',0),"rw"),
                'SetIncrementalPulse0':(40059,('word',0),"rw"),
                'SetIncrementalPulse1':(40061,('word',0),"rw"),
                'SetIncrementalPulse2':(40063,('word',0),"rw"),
                'SetIncrementalPulse3':(40065,('word',0),"rw"),
                'SetIncrementalPulse4':(40067,('word',0),"rw"),
                'SetIncrementalPulse5':(40069,('word',0),"rw"),
                'SetIncrementalPulse6':(40071,('word',0),"rw")},
            'PWMOutput0-7':{
                'PulseOutputLowLevelWidth0':(40017,('word',0),"rw"),
                'PulseOutputLowLevelWidth1':(40019,('word',0),"rw"),
                'PulseOutputLowLevelWidth2':(40021,('word',0),"rw"),
                'PulseOutputLowLevelWidth3':(40023,('word',0),"rw"),
                'PulseOutputLowLevelWidth4':(40025,('word',0),"rw"),
                'PulseOutputLowLevelWidth5':(40027,('word',0),"rw"),
                'PulseOutputLowLevelWidth6':(40029,('word',0),"rw"),
                'PulseOutputLowLevelWidth7':(40031,('word',0),"rw"),
                'PulseOutputHighLevelWidth0':(40033,('word',0),"rw"),
                'PulseOutputHighLevelWidth1':(40035,('word',0),"rw"),
                'PulseOutputHighLevelWidth2':(40037,('word',0),"rw"),
                'PulseOutputHighLevelWidth3':(40039,('word',0),"rw"),
                'PulseOutputHighLevelWidth4':(40041,('word',0),"rw"),
                'PulseOutputHighLevelWidth5':(40043,('word',0),"rw"),
                'PulseOutputHighLevelWidth6':(40045,('word',0),"rw"),
                'PulseOutputHighLevelWidth7':(40047,('word',0),"rw"),
                'SetAbsolutePulse0':(40049,('word',0),"rw"),
                'SetAbsolutePulse1':(40051,('word',0),"rw"),
                'SetAbsolutePulse2':(40053,('word',0),"rw"),
                'SetAbsolutePulse3':(40055,('word',0),"rw"),
                'SetAbsolutePulse4':(40057,('word',0),"rw"),
                'SetAbsolutePulse5':(40059,('word',0),"rw"),
                'SetAbsolutePulse6':(40061,('word',0),"rw"),
                'SetAbsolutePulse7':(40063,('word',0),"rw"),
                'SetIncrementalPulse0':(40065,('word',0),"rw"),
                'SetIncrementalPulse1':(40067,('word',0),"rw"),
                'SetIncrementalPulse2':(40069,('word',0),"rw"),
                'SetIncrementalPulse3':(40071,('word',0),"rw"),
                'SetIncrementalPulse4':(40073,('word',0),"rw"),
                'SetIncrementalPulse5':(40075,('word',0),"rw"),
                'SetIncrementalPulse6':(40077,('word',0),"rw"),
                'SetIncrementalPulse7':(40079,('word',0),"rw")},
            'PWMOutput0-15':{
                'PulseOutputLowLevelWidth0':(40001,('word',0),"rw"),
                'PulseOutputLowLevelWidth1':(40003,('word',0),"rw"),
                'PulseOutputLowLevelWidth2':(40005,('word',0),"rw"),
                'PulseOutputLowLevelWidth3':(40007,('word',0),"rw"),
                'PulseOutputLowLevelWidth4':(40009,('word',0),"rw"),
                'PulseOutputLowLevelWidth5':(40011,('word',0),"rw"),
                'PulseOutputLowLevelWidth6':(40013,('word',0),"rw"),
                'PulseOutputLowLevelWidth7':(40015,('word',0),"rw"),
                'PulseOutputLowLevelWidth8':(40017,('word',0),"rw"),
                'PulseOutputLowLevelWidth9':(40019,('word',0),"rw"),
                'PulseOutputLowLevelWidth10':(40021,('word',0),"rw"),
                'PulseOutputLowLevelWidth11':(40023,('word',0),"rw"),
                'PulseOutputLowLevelWidth12':(40025,('word',0),"rw"),
                'PulseOutputLowLevelWidth13':(40027,('word',0),"rw"),
                'PulseOutputLowLevelWidth14':(40029,('word',0),"rw"),
                'PulseOutputLowLevelWidth15':(40031,('word',0),"rw"),
                'PulseOutputHighLevelWidth0':(40033,('word',0),"rw"),
                'PulseOutputHighLevelWidth1':(40035,('word',0),"rw"),
                'PulseOutputHighLevelWidth2':(40037,('word',0),"rw"),
                'PulseOutputHighLevelWidth3':(40039,('word',0),"rw"),
                'PulseOutputHighLevelWidth4':(40041,('word',0),"rw"),
                'PulseOutputHighLevelWidth5':(40043,('word',0),"rw"),
                'PulseOutputHighLevelWidth6':(40045,('word',0),"rw"),
                'PulseOutputHighLevelWidth7':(40047,('word',0),"rw"),
                'PulseOutputHighLevelWidth8':(40049,('word',0),"rw"),
                'PulseOutputHighLevelWidth9':(40051,('word',0),"rw"),
                'PulseOutputHighLevelWidth10':(40053,('word',0),"rw"),
                'PulseOutputHighLevelWidth11':(40055,('word',0),"rw"),
                'PulseOutputHighLevelWidth12':(40057,('word',0),"rw"),
                'PulseOutputHighLevelWidth13':(40059,('word',0),"rw"),
                'PulseOutputHighLevelWidth14':(40061,('word',0),"rw"),
                'PulseOutputHighLevelWidth15':(40063,('word',0),"rw"),
                'SetAbsolutePulse0':(40065,('word',0),"rw"),
                'SetAbsolutePulse1':(40067,('word',0),"rw"),
                'SetAbsolutePulse2':(40069,('word',0),"rw"),
                'SetAbsolutePulse3':(40071,('word',0),"rw"),
                'SetAbsolutePulse4':(40073,('word',0),"rw"),
                'SetAbsolutePulse5':(40075,('word',0),"rw"),
                'SetAbsolutePulse6':(40077,('word',0),"rw"),
                'SetAbsolutePulse7':(40079,('word',0),"rw"),
                'SetAbsolutePulse8':(40081,('word',0),"rw"),
                'SetAbsolutePulse9':(40083,('word',0),"rw"),
                'SetAbsolutePulse10':(40085,('word',0),"rw"),
                'SetAbsolutePulse11':(40087,('word',0),"rw"),
                'SetAbsolutePulse12':(40089,('word',0),"rw"),
                'SetAbsolutePulse13':(40091,('word',0),"rw"),
                'SetAbsolutePulse14':(40093,('word',0),"rw"),
                'SetAbsolutePulse15':(40095,('word',0),"rw"),
                'SetIncrementalPulse0':(40097,('word',0),"rw"),
                'SetIncrementalPulse1':(40099,('word',0),"rw"),
                'SetIncrementalPulse2':(40101,('word',0),"rw"),
                'SetIncrementalPulse3':(40103,('word',0),"rw"),
                'SetIncrementalPulse4':(40105,('word',0),"rw"),
                'SetIncrementalPulse5':(40107,('word',0),"rw"),
                'SetIncrementalPulse6':(40109,('word',0),"rw"),
                'SetIncrementalPulse7':(40111,('word',0),"rw"),
                'SetIncrementalPulse8':(40113,('word',0),"rw"),
                'SetIncrementalPulse9':(40115,('word',0),"rw"),
                'SetIncrementalPulse10':(40117,('word',0),"rw"),
                'SetIncrementalPulse11':(40119,('word',0),"rw"),
                'SetIncrementalPulse12':(40121,('word',0),"rw"),
                'SetIncrementalPulse13':(40123,('word',0),"rw"),
                'SetIncrementalPulse14':(40125,('word',0),"rw"),
                'SetIncrementalPulse15':(40127,('word',0),"rw")},
            'ADAM6000Counter0-7':{
                'CounterStartStop0':(33,('bit',0),'rw'),
                'ClearCounter0':(34,('bit',0),'w'),
                'ClearOverflow0':(35,('bit',0),'rw'),
                'DILatchStatus0':(36,('bit',0),'rw'),
                'CounterStartStop1':(37,('bit',0),'rw'),
                'ClearCounter1':(38,('bit',0),'w'),
                'ClearOverflow1':(39,('bit',0),'rw'),
                'DILatchStatus1':(40,('bit',0),'rw'),
                'CounterStartStop2':(41,('bit',0),'rw'),
                'ClearCounter2':(42,('bit',0),'w'),
                'ClearOverflow2':(43,('bit',0),'rw'),
                'DILatchStatus2':(44,('bit',0),'rw'),
                'CounterStartStop3':(45,('bit',0),'rw'),
                'ClearCounter3':(46,('bit',0),'w'),
                'ClearOverflow3':(47,('bit',0),'rw'),
                'DILatchStatus3':(48,('bit',0),'rw'),
                'CounterStartStop4':(49,('bit',0),'rw'),
                'ClearCounter4':(50,('bit',0),'w'),
                'ClearOverflow4':(51,('bit',0),'rw'),
                'DILatchStatus4':(52,('bit',0),'rw'),
                'CounterStartStop5':(53,('bit',0),'rw'),
                'ClearCounter5':(54,('bit',0),'w'),
                'ClearOverflow5':(55,('bit',0),'rw'),
                'DILatchStatus5':(56,('bit',0),'rw'),
                'CounterStartStop6':(57,('bit',0),'rw'),
                'ClearCounter6':(58,('bit',0),'w'),
                'ClearOverflow6':(59,('bit',0),'rw'),
                'DILatchStatus6':(60,('bit',0),'rw'),
                'CounterStartStop7':(61,('bit',0),'rw'),
                'ClearCounter7':(62,('bit',0),'w'),
                'ClearOverflow7':(63,('bit',0),'rw'),
                'DILatchStatus7':(64,('bit',0),'rw')},
            'ADAM6000Counter0-11':{
                'CounterStartStop0':(33,('bit',0),'rw'),
                'ClearCounter0':(34,('bit',0),'w'),
                'ClearOverflow0':(35,('bit',0),'rw'),
                'DILatchStatus0':(36,('bit',0),'rw'),
                'CounterStartStop1':(37,('bit',0),'rw'),
                'ClearCounter1':(38,('bit',0),'w'),
                'ClearOverflow1':(39,('bit',0),'rw'),
                'DILatchStatus1':(40,('bit',0),'rw'),
                'CounterStartStop2':(41,('bit',0),'rw'),
                'ClearCounter2':(42,('bit',0),'w'),
                'ClearOverflow2':(43,('bit',0),'rw'),
                'DILatchStatus2':(44,('bit',0),'rw'),
                'CounterStartStop3':(45,('bit',0),'rw'),
                'ClearCounter3':(46,('bit',0),'w'),
                'ClearOverflow3':(47,('bit',0),'rw'),
                'DILatchStatus3':(48,('bit',0),'rw'),
                'CounterStartStop4':(49,('bit',0),'rw'),
                'ClearCounter4':(50,('bit',0),'w'),
                'ClearOverflow4':(51,('bit',0),'rw'),
                'DILatchStatus4':(52,('bit',0),'rw'),
                'CounterStartStop5':(53,('bit',0),'rw'),
                'ClearCounter5':(54,('bit',0),'w'),
                'ClearOverflow5':(55,('bit',0),'rw'),
                'DILatchStatus5':(56,('bit',0),'rw'),
                'CounterStartStop6':(57,('bit',0),'rw'),
                'ClearCounter6':(58,('bit',0),'w'),
                'ClearOverflow6':(59,('bit',0),'rw'),
                'DILatchStatus6':(60,('bit',0),'rw'),
                'CounterStartStop7':(61,('bit',0),'rw'),
                'ClearCounter7':(62,('bit',0),'w'),
                'ClearOverflow7':(63,('bit',0),'rw'),
                'DILatchStatus7':(64,('bit',0),'rw'),
                'CounterStartStop8':(65,('bit',0),'rw'),
                'ClearCounter8':(66,('bit',0),'w'),
                'ClearOverflow8':(67,('bit',0),'rw'),
                'DILatchStatus8':(68,('bit',0),'rw'),
                'CounterStartStop9':(69,('bit',0),'rw'),
                'ClearCounter9':(70,('bit',0),'w'),
                'ClearOverflow9':(71,('bit',0),'rw'),
                'DILatchStatus9':(72,('bit',0),'rw'),
                'CounterStartStop10':(73,('bit',0),'rw'),
                'ClearCounter10':(74,('bit',0),'w'),
                'ClearOverflow10':(75,('bit',0),'rw'),
                'DILatchStatus10':(76,('bit',0),'rw'),
                'CounterStartStop11':(77,('bit',0),'rw'),
                'ClearCounter11':(78,('bit',0),'w'),
                'ClearOverflow11':(79,('bit',0),'rw'),
                'DILatchStatus11':(80,('bit',0),'rw')},
            'Counter0-15':{
                'CounterStartStop0':(33,('bit',0),'rw'),
                'CounterStartStop1':(34,('bit',0),'rw'),
                'CounterStartStop2':(35,('bit',0),'rw'),
                'CounterStartStop3':(36,('bit',0),'rw'),
                'CounterStartStop4':(37,('bit',0),'rw'),
                'CounterStartStop5':(38,('bit',0),'rw'),
                'CounterStartStop6':(39,('bit',0),'rw'),
                'CounterStartStop7':(40,('bit',0),'rw'),
                'CounterStartStop8':(41,('bit',0),'rw'),
                'CounterStartStop9':(42,('bit',0),'rw'),
                'CounterStartStop10':(43,('bit',0),'rw'),
                'CounterStartStop11':(44,('bit',0),'rw'),
                'CounterStartStop12':(45,('bit',0),'rw'),
                'CounterStartStop13':(46,('bit',0),'rw'),
                'CounterStartStop14':(47,('bit',0),'rw'),
                'CounterStartStop15':(48,('bit',0),'rw'),
                'ClearCounter0':(49,('bit',0),'rw'),
                'ClearCounter1':(50,('bit',0),'rw'),
                'ClearCounter2':(51,('bit',0),'rw'),
                'ClearCounter3':(52,('bit',0),'rw'),
                'ClearCounter4':(53,('bit',0),'rw'),
                'ClearCounter5':(54,('bit',0),'rw'),
                'ClearCounter6':(55,('bit',0),'rw'),
                'ClearCounter7':(56,('bit',0),'rw'),
                'ClearCounter8':(57,('bit',0),'rw'),
                'ClearCounter9':(58,('bit',0),'rw'),
                'ClearCounter10':(59,('bit',0),'rw'),
                'ClearCounter11':(60,('bit',0),'rw'),
                'ClearCounter12':(61,('bit',0),'rw'),
                'ClearCounter13':(62,('bit',0),'rw'),
                'ClearCounter14':(63,('bit',0),'rw'),
                'ClearCounter15':(64,('bit',0),'rw'),
                'ClearOverflow0':(65,('bit',0),'rw'),
                'ClearOverflow1':(66,('bit',0),'rw'),
                'ClearOverflow2':(67,('bit',0),'rw'),
                'ClearOverflow3':(68,('bit',0),'rw'),
                'ClearOverflow4':(69,('bit',0),'rw'),
                'ClearOverflow5':(70,('bit',0),'rw'),
                'ClearOverflow6':(71,('bit',0),'rw'),
                'ClearOverflow7':(72,('bit',0),'rw'),
                'ClearOverflow8':(73,('bit',0),'rw'),
                'ClearOverflow9':(74,('bit',0),'rw'),
                'ClearOverflow10':(75,('bit',0),'rw'),
                'ClearOverflow11':(76,('bit',0),'rw'),
                'ClearOverflow12':(77,('bit',0),'rw'),
                'ClearOverflow13':(78,('bit',0),'rw'),
                'ClearOverflow14':(79,('bit',0),'rw'),
                'ClearOverflow15':(80,('bit',0),'rw'),
                'Counter/FrequencyValue0':(40001,('word',0),"r"),
                'Counter/FrequencyValue1':(40003,('word',0),"r"),
                'Counter/FrequencyValue2':(40005,('word',0),"r"),
                'Counter/FrequencyValue3':(40007,('word',0),"r"),
                'Counter/FrequencyValue4':(40009,('word',0),"r"),
                'Counter/FrequencyValue5':(40011,('word',0),"r"),
                'Counter/FrequencyValue6':(40013,('word',0),"r"),
                'Counter/FrequencyValue7':(40015,('word',0),"r"),
                'Counter/FrequencyValue8':(40017,('word',0),"r"),
                'Counter/FrequencyValue9':(40019,('word',0),"r"),
                'Counter/FrequencyValue10':(40021,('word',0),"r"),
                'Counter/FrequencyValue11':(40023,('word',0),"r"),
                'Counter/FrequencyValue12':(40025,('word',0),"r"),
                'Counter/FrequencyValue13':(40027,('word',0),"r"),
                'Counter/FrequencyValue14':(40029,('word',0),"r"),
                'Counter/FrequencyValue15':(40031,('word',0),"r")},
            'Common':{}}
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
            'DILatchStatus0':(57,('bit',0),'rw'),
            'DILatchStatus1':(58,('bit',0),'rw'),
            'DILatchStatus2':(59,('bit',0),'rw'),
            'DILatchStatus3':(60,('bit',0),'rw'),
            'DILatchStatus4':(61,('bit',0),'rw'),
            'DILatchStatus5':(62,('bit',0),'rw'),
            'DILatchStatus6':(63,('bit',0),'rw'),
            'DILatchStatus7':(64,('bit',0),'rw')}
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
            'ModuleName1':(40211,('int',0),'r'),
            'ModuleName2':(40212,('int',0),'r')}
        self.ADAM6050D = {
            **self.ADAM6050,
            'DODiagnosticStatus':(40307,('word',0),'r')}
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
            **self.CommonParameters,}
        self.ADAM6051 = {
            **self.DigitalParameters['DI0-3'],
            **self.DigitalParameters['DI4-7'],
            **self.DigitalParameters['DI8-15'],
            **self.DigitalParameters['CommonDI'],
            **self.DigitalParameters['Common'],
            #*self.DigitalParameters['Counter'], #TODO read the documentation again and make this key
            **self.CommonParameters,
            'DILatchStatus0':(81,('bit',0),'rw'),
            'DILatchStatus1':(82,('bit',0),'rw'),
            'DILatchStatus2':(83,('bit',0),'rw'),
            'DILatchStatus3':(84,('bit',0),'rw'),
            'DILatchStatus4':(85,('bit',0),'rw'),
            'DILatchStatus5':(86,('bit',0),'rw'),
            'DILatchStatus6':(87,('bit',0),'rw'),
            'DILatchStatus7':(88,('bit',0),'rw'),
            'DILatchStatus8':(89,('bit',0),'rw'),
            'DILatchStatus9':(90,('bit',0),'rw'),
            'DILatchStatus10':(91,('bit',0),'rw'),
            'DILatchStatus11':(92,('bit',0),'rw'),
            'DILatchStatus12':(93,('bit',0),'rw'),
            'DILatchStatus13':(94,('bit',0),'rw'),
            'DILatchStatus14':(95,('bit',0),'rw'),
            'DILatchStatus15':(96,('bit',0),'rw')}
        self.ADAM6056 = {
            **self.DigitalParameters['DO0-3'],
            **self.DigitalParameters['DO4-7'],
            **self.DigitalParameters['DO8-15'],
            **self.DigitalParameters['PWMOutput0-15'],
            **self.DigitalParameters['CommonDO'],
            **self.DigitalParameters['Common'],
            **self.CommonParameters}
        self.ADAM6260 = {
            **self.DigitalParameters['DO0-3'],
            **self.DigitalParameters['PWMOutput0-5'],
            **self.DigitalParameters['CommonDO'],
            **self.DigitalParameters['Common'],
            **self.CommonParameters,
            'DO4':(21,('bit',0),'rw'),
            'DO5':(22,('bit',0),'rw'),}
        self.ADAM6266 = {
            **self.DigitalParameters['DO0-3'],
            **self.DigitalParameters['DI0-3'],
            **self.DigitalParameters['Counter0-3'],
            **self.DigitalParameters['PWMOutput0-3'],
            **self.DigitalParameters['CommonDI'],
            **self.DigitalParameters['CommonDO'],
            **self.DigitalParameters['Common'],
            **self.CommonParameters,
            'DILatchStatus0':(45,('bit',0),'rw'),
            'DILatchStatus1':(46,('bit',0),'rw'),
            'DILatchStatus2':(47,('bit',0),'rw'),
            'DILatchStatus3':(48,('bit',0),'rw'),}
        self.ADAM6224 = {
            **self.DigitalParameters['DI0-3'],
            **self.DigitalParameters['CommonDI'],
            **self.AnalogParameters['AO0-3'],
            **self.AnalogParameters['CommonAO'],
            **self.CommonParameters,
            'SafetyValue0':(40411,('int',0),"rw"),
            'SafetyValue1':(40412,('int',0),"rw"),
            'SafetyValue2':(40413,('int',0),"rw"),
            'SafetyValue3':(40414,('int',0),"rw"),
            'StartupValue0':(40401,('int',0),"rw"),
            'StartupValue1':(40402,('int',0),"rw"),
            'StartupValue2':(40403,('int',0),"rw"),
            'StartupValue3':(40404,('int',0),"rw"),
            'DIEventStatus0':(40111,('int',0),"r"),
            'DIEventStatus1':(40112,('int',0),"r"),
            'DIEventStatus2':(40113,('int',0),"r"),
            'DIEventStatus3':(40114,('int',0),"r"),
            'DIEventStatusBitmask':{
                    '0x01':'Unreliable DI value (UART timeout)',
                    '0x02':'Safety Value triggered',
                    '0x04':'Startup Value triggered'}}
        self.ADAM6217 = {
            **self.AnalogParameters['AI0-3'],
            **self.AnalogParameters['AI4-7'],
            **self.AnalogParameters['CommonAI'],
            **self.AnalogParameters['Common'],
            **self.CommonParameters}
        self.ADAM6017 = {
            **self.ADAM6217,
            **self.ADAM6000GCLInternalCounterValue}
        self.ADAM6018 = {
            **self.ADAM6217,
            **self.DigitalParameters['DO0-3'],
            **self.DigitalParameters['DO4-7'],
            **self.DigitalParameters['CommonDO']}
        #self.ADAM6024 = { #TODO
        #    **self.DigitalParameters['DI0-1'],
        #    **self.DigitalParameters['DO0-1'],
        #    **self.AnalogParameters['ADAM6000DI0-5'],
        #    **self.AnalogParameters['ADAM6000DO0-1'],
        #    **self.DigitalParameters['CommonDI'],
        #    **self.DigitalParameters['CommonDO']
        #    **self.CommonParameters}
        self.ADAM6015 = {
            **self.AnalogParameters['AI0-3'],
            **self.AnalogParameters['AI4-6'],
            **self.AnalogParameters['CommonAI'],
            **self.AnalogParameters['Common'],
            **self.CommonParameters,
            'ModuleName1':(40211,('int',0),'r'),
            'ModuleName2':(40212,('int',0),'r')}
        self.ADAM6060 = {} #TODO
        self.ADAM6066 = {} #TODO

class ADAMDataAcquisitionModule(ModbusTcpClient):
    def __init__(self, lockerinstance, moduleName = 'ADAM6052', address = '192.168.0.1', port = 502, *args, **kwargs):
        super().__init__(host = address, port = port, *args, **kwargs)
        self.moduleName = moduleName
        stringtoeval = 'ADAMModule().' + self.moduleName
        try:
            self.addresses = eval(stringtoeval)
        except:
            raise ParameterDictionaryError(lockerinstance, 'ADAMDataAcquisitionModule.__init__, parameter = ' + str(self.moduleName))

    def __getAddress(self, lockerinstance, parameterName=''):
        try:
            return self.addresses[parameterName][0]
        except:
            raise ParameterDictionaryError(lockerinstance, self.moduleName + ' __getAddress, parameter = ' + str(parameterName))

    def read_coils(self, lockerinstance, input = 'DI0', NumberOfCoils = 1, **kwargs):
        access = ''
        if isinstance(input,str):
            if 'I' in input or 'DI' in input:
                try:
                    ParameterTuple = self.addresses['DI' + ''.join(re.findall(r'\d',input))]
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
                except:
                    raise ParameterDictionaryError(lockerinstance, self.moduleName + ' read_coils, parameter = ' + str(input))
            elif 'O' in input or 'DO' in input:
                try:
                    ParameterTuple = self.addresses['DO' + ''.join(re.findall(r'\d',input))]
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
                except:
                    raise ParameterDictionaryError(lockerinstance, self.moduleName + ' read_coils, parameter = ' + str(input))
            else:
                raise ParameterDictionaryError(lockerinstance, self.moduleName + ' read_coils, parameter = ' + str(input))
        if isinstance(input,int):
            try:
                ParameterTuple = self.addresses['DI' + str(input)]
                address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise ParameterDictionaryError(lockerinstance, self.moduleName + ' read_coils, parameter = ' + str(input))
        if access == 'w':
            raise ParameterIsNotReadable(lockerinstance, self.moduleName + ' read_coils, parameter = ' + str(input))
        return super().read_coils(address-1, NumberOfCoils, **kwargs).bits

    def write_coils(self, lockerinstance, startCoil = 'DO0', listOfValues = [True], **kwargs):
        access = ''
        if isinstance(startCoil,str):
            if 'O' in startCoil or 'DO' in startCoil:
                try:
                    ParameterTuple = self.addresses['DO' + ''.join(re.findall(r'\d',startCoil))]
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
                except:
                    raise ParameterDictionaryError(lockerinstance, self.moduleName + ' write_coils, parameter = ' + str(startCoil))
            else:
                raise ParameterDictionaryError(lockerinstance, self.moduleName + ' write_coils, parameter = ' + str(startCoil))
        if isinstance(startCoil,int):
            try:
                ParameterTuple = self.addresses['DO' + str(startCoil)]
                address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise ParameterDictionaryError(lockerinstance, self.moduleName + ' write_coils, parameter = ' + str(startCoil))
        if access == 'r':
            raise ParameterIsNotWritable(lockerinstance, self.moduleName + ' write_coils, parameter = ' + str(startCoil))
        return super().write_coils(address-1, listOfValues, **kwargs)

    def write_coil(self, lockerinstance, Coil='DO0', value=0, **kwargs):
        access = ''
        if isinstance(Coil,str):
            if 'O' in Coil or 'DO' in Coil:
                try:
                    ParameterTuple = self.addresses['DO' + ''.join(re.findall(r'\d',Coil))]
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
                except:
                    raise ParameterDictionaryError(lockerinstance, self.moduleName + ' write_coil, parameter = ' + str(Coil))
            else:
                raise ParameterDictionaryError(lockerinstance, self.moduleName + ' write_coil, parameter = ' + str(Coil))
        if isinstance(Coil,int):
            try:
                ParameterTuple = self.addresses['DO' + str(Coil)]
                address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise ParameterDictionaryError(lockerinstance, self.moduleName + ' write_coil, parameter = ' + str(Coil))
        if access == 'r':
            raise ParameterIsNotWritable(lockerinstance, self.moduleName + ' write_coil, parameter = ' + str(Coil))
        return super().write_coil(address-1, value, **kwargs)

    def read_discrete_inputs(self, lockerinstance, InputToStartFrom = 'DI0', count=1, **kwargs):
        access = ''
        if isinstance(InputToStartFrom,str):
            if 'I' in InputToStartFrom or 'DI' in InputToStartFrom:
                try:
                    ParameterTuple = self.addresses['DI' + ''.join(re.findall(r'\d',InputToStartFrom))]
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
                except:
                    raise ParameterDictionaryError(lockerinstance, self.moduleName + ' read_discrete_inputs, parameter = ' + str(InputToStartFrom))
            else:
                raise ParameterDictionaryError(lockerinstance, self.moduleName + ' read_discrete_inputs, parameter = ' + str(InputToStartFrom))
        if isinstance(InputToStartFrom,int):
            try:
                ParameterTuple = self.addresses['DO' + str(InputToStartFrom)]
                address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise ParameterDictionaryError(lockerinstance, self.moduleName + ' read_discrete_inputs, parameter = ' + str(InputToStartFrom))
        if access == 'w':
            raise ParameterIsNotReadable(lockerinstance, self.moduleName + ' read_discrete_inputs, parameter = ' + str(InputToStartFrom))
        return super().read_discrete_inputs(address-1, count, **kwargs)
    
    def read_holding_registers(self, lockerinstance, registerToStartFrom = 'Counter/FrequencyValue0', count=1, **kwargs):
        access = ''
        if isinstance(registerToStartFrom,str):
            try:
                ParameterTuple = self.addresses[registerToStartFrom]
                address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise ParameterDictionaryError(lockerinstance, self.moduleName + ' read_holding_registers, parameter = ' + str(registerToStartFrom))
        else:
            raise ParameterDictionaryError(lockerinstance, self.moduleName + ' read_holding_registers, parameter = ' + str(registerToStartFrom))
        if access == 'w':
            raise ParameterIsNotReadable(lockerinstance, self.moduleName + ' read_holding_registers, parameter = ' + str(registerToStartFrom))
        return super().read_holding_registers(address, count, **kwargs)

    def read_input_registers(self, lockerinstance, registerToStartFrom = 'DIvalue', count=1, **kwargs):
        access = ''
        if isinstance(registerToStartFrom,str):
            try:
                ParameterTuple = self.addresses[registerToStartFrom]
                address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise ParameterDictionaryError(lockerinstance, self.moduleName + ' read_input_registers, parameter = ' + str(registerToStartFrom))
        else:
            raise ParameterDictionaryError(lockerinstance, self.moduleName + ' read_input_registers, parameter = ' + str(registerToStartFrom))
        if access == 'w':
            raise ParameterIsNotReadable(lockerinstance, self.moduleName + ' read_input_registers, parameter = ' + str(registerToStartFrom))
        return super().read_input_registers(address, count, **kwargs)
    
    def write_register(self, lockerinstance, register = '', value = 0xFFFF, **kwargs):
        access = ''
        if isinstance(register,str):
            try:
                ParameterTuple = self.addresses[register]
                address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise ParameterDictionaryError(lockerinstance, self.moduleName + ' write_register, parameter = ' + str(register))
        else:
            raise ParameterDictionaryError(lockerinstance, self.moduleName + ' write_register, parameter = ' + str(register))
        if access == 'r':
            raise ParameterIsNotWritable(lockerinstance, self.moduleName + ' write_register, parameter = ' + str(register))
        return super().write_registers(address, value, **kwargs)

    def write_registers(self, lockerinstance, registerToStartFrom = '', values = [0xFFFF], **kwargs):
        access = ''
        if isinstance(registerToStartFrom,str):
            try:
                ParameterTuple = self.addresses[registerToStartFrom]
                address, access = ParameterTuple[::len(ParameterTuple)-1]
            except:
                raise ParameterDictionaryError(lockerinstance, self.moduleName + ' write_registers, parameter = ' + str(registerToStartFrom))
        else:
            raise ParameterDictionaryError(lockerinstance, self.moduleName + ' write_registers, parameter = ' + str(registerToStartFrom))
        if access == 'r':
            raise ParameterIsNotWritable(lockerinstance, self.moduleName + ' write_registers, parameter = ' + str(registerToStartFrom))
        return super().write_registers(address, values, **kwargs)

class ParameterDictionaryError(ValueError):
    def __init__(self, lockerinstance, *args, **kwargs):
        self.args = args
        errstring = '\nInvalid key for parameter dictionary in ' + ''.join(map(str, *args))
        ErrorEventWrite(lockerinstance, errstring, errorlevel = 2)
    
class ParameterIsNotReadable(TypeError):
    def __init__(self, lockerinstance, *args, **kwargs):
        self.args = args
        errstring = '\nTrying to read from write-only register in ' + ''.join(map(str, *args))
        ErrorEventWrite(lockerinstance, errstring, errorlevel = 2)

class ParameterIsNotWritable(TypeError):
    def __init__(self, lockerinstance, *args, **kwargs):
        errstring = '\nTrying to write to read-only register in ' + ''.join(map(str, *args))
        self.args = args
        ErrorEventWrite(lockerinstance, errstring, errorlevel = 2)

class Kawasaki(ModbusTcpClient):
    def __init__(self, lockerinstance, address = '192.168.0.1', port = 9200, *args, **kwargs):
        super().__init__(address, port, framer=ModbusAsciiFramer, *args, **kwargs)
        params = kwargs.pop('params',{})
        if isinstance(params,str):
            try:
                with open(params) as Hfile:
                        self.parameters = json.load(Hfile)["Registers"]
            except Exception as e:
                raise ParameterDictionaryError(lockerinstance, 'Unable to read JSON file with Registers descriptions' + params)
        elif isinstance(params,dict):
            self.params = params
        self.addresses = {}
        for subkey in self.params.keys():
            self.addresses.update(self.params[subkey])

    def __getAddress(self, lockerinstance, parameterName=''):
        try:
            return self.addresses[parameterName][0]
        except:
            with lockerinstance[0].lock:
                lockerinstance[0].robot['error'] = True
            raise ParameterDictionaryError(lockerinstance, 'Kawasaki __getAddress, parameter = ' + str(parameterName))

    def read_coils(self, lockerinstance, input = 'I1', NumberOfCoils = 1, **kwargs):
        access = ''
        result = []
        if isinstance(input,str):
            if 'I' in input:
                try:
                    ParameterTuple = self.addresses['I' + ''.join(re.findall(r'\d',input))]
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
                    if isinstance(address, str):
                        address = int(address,16)
                except:
                    with lockerinstance[0].lock:
                        lockerinstance[0].robot['error'] = True
                    raise ParameterDictionaryError(lockerinstance, 'Kawasaki read_coils, parameter = ' + input)
            elif 'O' in input:
                try:
                    ParameterTuple = self.addresses['O' + ''.join(re.findall(r'\d',input))]
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
                    if isinstance(address, str):
                        address = int(address,16)
                except:
                    with lockerinstance[0].lock:
                        lockerinstance[0].robot['error'] = True
                    raise ParameterDictionaryError(lockerinstance, 'Kawasaki read_coils, parameter = ' + input)
            else:
                with lockerinstance[0].lock:
                    lockerinstance[0].robot['error'] = True
                raise ParameterDictionaryError(lockerinstance, 'Kawasaki read_coils, parameter = ' + input)
        if isinstance(input,int):
            try:
                ParameterTuple = self.addresses['I' + str(input)]
                address, access = ParameterTuple[::len(ParameterTuple)-1]
                if isinstance(address, str):
                    address = int(address,16)
            except:
                with lockerinstance[0].lock:
                    lockerinstance[0].robot['error'] = True
                raise ParameterDictionaryError(lockerinstance, 'Kawasaki read_coils, parameter = ' + str(input))
        if 'r' not in access:
            with lockerinstance[0].lock:
                lockerinstance[0].robot['error'] = True
            raise ParameterIsNotReadable(lockerinstance, 'Kawasaki read_coils, parameter = ' + str(input))
        try:
            result = super().read_coils(address, NumberOfCoils, **kwargs)
            assert (not isinstance(result,Exception))
        except Exception as e:
            with lockerinstance[0].lock:
                lockerinstance[0].robot['error'] = True
                errstring = str(e)
                if errstring not in lockerinstance[0].shared['Errors']: lockerinstance[0].shared['Errors'] += errstring
            result = []
        finally:
            return result

    def write_coil(self, lockerinstance, Coil='DO0', value=0, **kwargs):
        access = ''
        result = []
        if isinstance(Coil,str):
            if 'O' in Coil:
                try:
                    ParameterTuple = self.addresses['O' + ''.join(re.findall(r'\d',Coil))]
                    address, access = ParameterTuple[::len(ParameterTuple)-1]
                    if isinstance(address, str):
                        address = int(address,16)
                except:
                    with lockerinstance[0].lock:
                        lockerinstance[0].robot['error'] = True
                    raise ParameterDictionaryError(lockerinstance, 'Kawasaki write_coil, parameter = ' + str(Coil))
            else:
                with lockerinstance[0].lock:
                    lockerinstance[0].robot['error'] = True
                raise ParameterDictionaryError(lockerinstance, 'KawasakiVG write_coil, parameter = ' + str(Coil))
        if isinstance(Coil,int):
            try:
                ParameterTuple = self.addresses['O' + str(Coil)]
                address, access = ParameterTuple[::len(ParameterTuple)-1]
                if isinstance(address, str):
                    address = int(address,16)
            except:
                with lockerinstance[0].lock:
                    lockerinstance[0].robot['error'] = True
                raise ParameterDictionaryError(lockerinstance, 'Kawasaki write_coil, parameter = ' + str(Coil))
        if access == 'r':
            with lockerinstance[0].lock:
                lockerinstance[0].robot['error'] = True
            raise ParameterIsNotWritable(lockerinstance, 'Kawasaki write_coil, parameter = ' + str(Coil))
        try:
            result = super().write_coil(address, value, **kwargs)
            assert (not isinstance(result,Exception))
        except Exception as e:
            with lockerinstance[0].lock:
                lockerinstance[0].robot['error'] = True
                errstring = str(e)
                if errstring not in lockerinstance[0].shared['Errors']: lockerinstance[0].shared['Errors'] += errstring
            result = []
        finally:
            return result

    def read_holding_registers(self, lockerinstance, registerToStartFrom = 'command', count=1, **kwargs):
        access = ''
        result = []
        if isinstance(registerToStartFrom,str):
            try:
                ParameterTuple = self.addresses[registerToStartFrom]
                address, access = ParameterTuple[::len(ParameterTuple)-1]
                if isinstance(address, str):
                    address = int(address,16)
            except:
                with lockerinstance[0].lock:
                    lockerinstance[0].robot['error'] = True
                raise ParameterDictionaryError(lockerinstance, 'Kawasaki read_holding_registers, parameter = ' + registerToStartFrom)
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].robot['error'] = True
            raise ParameterDictionaryError(lockerinstance, 'Kawasaki read_holding_registers, parameter = ' + str(registerToStartFrom))
        if access == 'w':
            with lockerinstance[0].lock:
                lockerinstance[0].robot['error'] = True
            raise ParameterIsNotReadable(lockerinstance, 'Kawasaki read_holding_registers, parameter = ' + str(registerToStartFrom))
        try:
            result = super().read_holding_registers(address, count, **kwargs)
            assert (not isinstance(result,Exception))
        except Exception as e:
            with lockerinstance[0].lock:
                lockerinstance[0].robot['error'] = True
                errstring = str(e)
                if errstring not in lockerinstance[0].shared['Errors']: lockerinstance[0].shared['Errors'] += errstring
            result = []
        finally:
            if isinstance(result,ReadHoldingRegistersResponse): result = result.registers
            return result

    def write_register(self, lockerinstance, register = '', value = 0xFFFF, **kwargs):
        access = ''
        result = []
        #print('write register',register, value)
        if isinstance(register,str):
            try:
                ParameterTuple = self.addresses[register]
                address, access = ParameterTuple[::len(ParameterTuple)-1]
                if isinstance(address, str):
                    address = int(address,16)
            except:
                with lockerinstance[0].lock:
                    lockerinstance[0].robot['error'] = True
                raise ParameterDictionaryError(lockerinstance, 'Kawasaki write_register, parameter = ' + str(register))
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].robot['error'] = True
            raise ParameterDictionaryError(lockerinstance, 'Kawasaki write_register, parameter = ' + str(register))
        if access == 'r':
            with lockerinstance[0].lock:
                lockerinstance[0].robot['error'] = True
            raise ParameterIsNotWritable(lockerinstance, 'Kawasaki write_register, parameter = ' + str(register))
        try:
            result = super().write_register(address, value, **kwargs)
            assert (not isinstance(result,Exception))
        except Exception as e:
            with lockerinstance[0].lock:
                lockerinstance[0].robot['error'] = True
                errstring = str(e)
                if errstring not in lockerinstance[0].shared['Errors']: lockerinstance[0].shared['Errors'] += errstring
            result = []
        finally:
            return result
