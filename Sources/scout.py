import socket
import json
import re
from .common import ErrorEventWrite, EventManager
from .TactWatchdog import TactWatchdog
WDT = TactWatchdog.WDT

class KDrawTCPInterface(socket.socket):
    def __init__(self, lockerinstance, configfile, *args, **kwargs):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM,)
        self.sendingqueue = []
        try:
            with open(configfile) as jsonfile:
                self.config = json.load(jsonfile)
        except Exception as e:
            errstring = "KDrawTCPInterface can't load json file: " + str(e)
            ErrorEventWrite(lockerinstance, errstring)
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['recipesdir'] = self.config['Receptures']

    def connect(self, lockerinstance):
        address = self.config['connection']['IP']
        port = self.config['connection']['port']
        super().connect((address,port))
        with lockerinstance[0].lock:
            lockerinstance[0].events['ScoutManagerReadyToSend'] = True
    
    def retrievequeue(self, lockerinstance):
        if self.sendingqueue:
            with lockerinstance[0].lock:
                event = lockerinstance[0].events['ScoutManagerReadyToSend']
            if event:
                with lockerinstance[0].lock:
                    lockerinstance[0].events['ScoutManagerReadyToSend'] = False
                self.sendall(self.sendingqueue.pop(0))
                self.receive(lockerinstance)

    def send_message(self, lockerinstance, bytes_message):
        if bytes_message in self.sendingqueue:
            return None
        else:
            self.sendingqueue.append(bytes_message)

    def receive(self, lockerinstance):
        def start(lockerinstance = lockerinstance):
            with lockerinstance[0].lock:
                lockerinstance[0].scout['connectionbuffer'] = b''
        def loop(obj = self, lockerinstance = lockerinstance):
            try:
                data = obj.recv(1024)
            except:
                data = b''
            finally:
                print(data.decode())
                with lockerinstance[0].lock:
                    lockerinstance[0].scout['connectionbuffer'] += data
                    if b'\r\n' in lockerinstance[0].scout['connectionbuffer']:
                        lockerinstance[0].events['KDrawMessageReceived'] = True
        def catch(obj = self, lockerinstance = lockerinstance):
            obj.decode_messsage(lockerinstance)
        WDT(lockerinstance, additionalFuncOnExceed = catch, additionalFuncOnCatch = catch, additionalFuncOnLoop = loop, additionalFuncOnStart = start ,errToRaise = "KDrawTCPInterface recv() timeout error\n", limitval = 60, scale = 's', eventToCatch = "KDrawMessageReceived")

    def encode_message(self, lockerinstance, message):
        string = ''
        for element in message: #message is an list of parameters
            string += str(element) + ',' #parameters are splitted by coma
        if string[-1] == ',': string = string[:-1] #removing last coma from string
        _bytes = string.encode() #convert to utf-8
        _bytes += b'\r\n' #end of message
        return _bytes

    def decode_messsage(self, lockerinstance):
        with lockerinstance[0].lock:
            rawmessage = lockerinstance[0].scout['connectionbuffer']
        lines = rawmessage.decode().splitlines()
        contents = []
        for line in lines:
            contents.extend(line.split(','))
        #mesage is in one bytes() line ended with \r\n
        #it contains values splitted by ','
        if contents:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['LastMessageType'] = contents[0]
            if contents[0] == 'STATUS': self.rec_write_status(lockerinstance, contents[1:])
            elif contents[0] == 'AL_REPORT': self.rec_AlarmReport(lockerinstance, contents[1:])
            elif contents[0] == 'AL_RESET': self.rec_AlarmReset(lockerinstance, contents[1:])
            elif contents[0] == 'VER': self.rec_Version(lockerinstance, contents[1:])
            elif contents[0] == 'AT_START': self.rec_AtStart(lockerinstance, contents[1:])
            elif contents[0] == 'RECIPE_CHANGE': self.rec_RecipeChange(lockerinstance, contents[1:])
            elif contents[0] == 'WELD_RUN': self.rec_WeldRun(lockerinstance, contents[1:])
            elif contents[0] == 'AT_STOP': self.rec_AtStop(lockerinstance, contents[1:])
            elif contents[0] == 'LASER_CTRL': self.rec_LaserCTRL(lockerinstance, contents[1:])
            elif contents[0] == 'SCAN_WOBBLE': self.rec_ScanWobble(lockerinstance, contents[1:])
            elif contents[0] == 'MANUAL_ALIGN': self.rec_ManualAlign(lockerinstance, contents[1:])
            elif contents[0] == 'MANUAL_WELD': self.rec_ManualWeld(lockerinstance, contents[1:])
            elif contents[0] == 'GET_ALIGN_INFO': self.rec_GetAlignInfo(lockerinstance, contents[1:])
            elif contents[0] == 'FIELD_ALIGN': self.rec_FieldAlign(lockerinstance, contents[1:])
            else:
                ErrorEventWrite(lockerinstance, 'SCOUT responded unusable data: ' + str(contents))
        else:
            ErrorEventWrite(lockerinstance, 'SCOUT responded empty message: ' + str(contents))
        with lockerinstance[0].lock:
            lockerinstance[0].events['ScoutManagerReadyToSend'] = True

    def rec_write_status(self, lockerinstance, statusdata):
        with lockerinstance[0].lock:
            statusreceived = lockerinstance[0].scout['LastMessageType'] == 'STATUS'
        if statusreceived:
            if len(statusdata[1]) == 7 and statusdata[0] != '0':
                scout = lockerinstance[0].scout
                scout['StatusCheckCode'] = bool(int(statusdata[0]))
                with lockerinstance[0].lock:
                    for i, status in enumerate(['ReadyOn','AutoStart','Alarm', 'rsv','WeldingProgress','LaserIsOn','Wobble']):
                        scout['status'][status] = bool(int(statusdata[1][i]))
                    scout['MessageAck'] = True
            else:
                ErrorEventWrite(lockerinstance, 'SCOUT status data was not fully received: ' + str(statusdata))

    def rec_AlarmReport(self, lockerinstance, data):
        if len(data)==3:
            ErrorEventWrite(lockerinstance, 'SCOUT reported alarm message with code: {}\n{}'.format(data[1],data[2]))
            with lockerinstance[0].lock:
                lockerinstance[0].scout['MessageAck'] = True
        else:
            ErrorEventWrite(lockerinstance, "SCOUT reported alarm message, but it's ioncomplete:\n{}".format(data))

    def rec_AlarmReset(self, lockerinstance, data):
        if len(data) == 1:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['MessageAck'] = True
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete reset ack message:\n{}".format(data))

    def rec_Version(self, lockerinstance, data):
        if len(data) == 2:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['MessageAck'] = True
                lockerinstance[0].scout['version'] = data[1]
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete version message:\n{}".format(data))

    def rec_AtStart(self, lockerinstance, data):
        if len(data) == 1:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['MessageAck'] = True
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete Autostart ack message:\n{}".format(data))

    def rec_RecipeChange(self, lockerinstance, data):
        if len(data) == 2:
            with lockerinstance[0].lock:
                savedrecipe = lockerinstance[0].scout['recipe']
            savedrecipe = self.__removefromstring(savedrecipe, '.dsg')
            recipechanged = data[1] == savedrecipe
            if recipechanged:
                with lockerinstance[0].lock:
                    lockerinstance[0].scout['MessageAck'] = True
                    lockerinstance[0].scout['Recipechangedsuccesfully'] = True
            if not recipechanged:
                ErrorEventWrite(lockerinstance, "SCOUT returned wrong Recipe Change ack message:\n{}".format(data))
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete Recipe Change ack message:\n{}".format(data))

    def rec_WeldRun(self, lockerinstance, data):
        with lockerinstance[0].lock:
            count = lockerinstance[0].scout['weldrunpagescount']
        if len(data) == 2 + count:
            with lockerinstance[0].lock:
                recipeok = data[0] == lockerinstance[0].scout['recipe']
                checkcode = int(data[1])
                if recipeok and checkcode == 1:
                    lockerinstance[0].scout['MessageAck'] = True
            if checkcode == 0:
                ErrorEventWrite(lockerinstance, "SCOUT returned wrong Recipe in WeldRun ack message:\n{}".format(data))
            elif checkcode == -1:
                ErrorEventWrite(lockerinstance, "SCOUT returned format error in WeldRun ack message:\n{}".format(data))
            elif checkcode == -2:
                ErrorEventWrite(lockerinstance, "SCOUT returned no welding data on page in WeldRun ack message:\n{}".format(data))
            elif checkcode == -3:
                ErrorEventWrite(lockerinstance, "SCOUT returned stop status in WeldRun ack message:\n{}".format(data))
            if not recipeok:
                ErrorEventWrite(lockerinstance, "SCOUT returned wrong Recipe in WeldRun ack message:\n{}".format(data))
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete WeldRun ack message:\n{}".format(data))

    def rec_AtStop(self, lockerinstance, data):
        if len(data) == 1:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['MessageAck'] = True
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete Autostop ack message:\n{}".format(data))

    def rec_LaserCTRL(self, lockerinstance, data):
        if len(data) == 2:
            with lockerinstance[0].lock:
                laserack = bool(int(data[1])) == lockerinstance[0].scout['LaserOn']
                if laserack: lockerinstance[0].scout['MessageAck'] = True
            if not laserack:
                ErrorEventWrite(lockerinstance, "SCOUT returned wrong LaserCTRL ack message:\n{}".format(data))
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete LaserCTRL ack message:\n{}".format(data))

    def rec_ScanWobble(self, lockerinstance, data):
        if len(data) == 5:
            with lockerinstance[0].lock:
                mode = data[1] == lockerinstance[0].scout['scanwobble']['mode']
                frequency = data[2] == lockerinstance[0].scout['scanwobble']['frequency']
                amplitude = data[3] == lockerinstance[0].scout['scanwobble']['amplitude']
                power = data[4] == lockerinstance[0].scout['scanwobble']['power']
                if mode and frequency and amplitude and power: lockerinstance[0].scout['MessageAck'] = True
            if (not mode) or (not frequency) or (not amplitude) or (not power):
                ErrorEventWrite(lockerinstance, "SCOUT returned wrong ScanWobble ack message:\n{}".format(data))
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete ScanWobble ack message:\n{}".format(data))

    def rec_ManualAlign(self, lockerinstance, data):
        if len(data) == 2:
            with lockerinstance[0].lock:
                checkcode = int(data[0])
                alignpage = int(data[1]) == lockerinstance[0].scout['ManualAlignPage']
                if checkcode and alignpage:
                    lockerinstance[0].scout['ManualAlignCheck'] = True
                lockerinstance[0].scout['MessageAck'] = True
            if not checkcode:
                ErrorEventWrite(lockerinstance, "SCOUT returned ManualAlign fail:\n{}".format(data))
            if not alignpage:
                ErrorEventWrite(lockerinstance, "SCOUT returned wrong page for manual align fail:\n{}".format(data))
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete ManualAlign ack message:\n{}".format(data))

    def rec_ManualWeld(self, lockerinstance, data):
        if len(data) == 2:
            with lockerinstance[0].lock:
                checkcode = int(data[0])
                weldpage = int(data[1]) == lockerinstance[0].scout['ManualWeldPage']
                if checkcode and weldpage:
                    lockerinstance[0].scout['ManualWeldCheck'] = True
                lockerinstance[0].scout['MessageAck'] = True
            if not checkcode:
                ErrorEventWrite(lockerinstance, "SCOUT returned ManualWeld went wrong:\n{}".format(data))
            if not weldpage:
                ErrorEventWrite(lockerinstance, "SCOUT returned wrong page for manual weld fail:\n{}".format(data))
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete ManualWeld ack message:\n{}".format(data))

    def rec_GetAlignInfo(self, lockerinstance, data):
        if len(data) == 9:
            if data[0] == 1 and data[2] == 1:
                with lockerinstance[0].lock:
                    for i, value in enumerate(['0','1','2','A','dotA','X','dotX','Y','dotY']):
                        lockerinstance[0].scout['AlignInfo'][value] = int(data[i])
                    lockerinstance[0].scout['MessageAck'] = True
            else:
                ErrorEventWrite(lockerinstance, "SCOUT returned GetAlignInfo failed:\n{}".format(data))
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete GetAlignInfo message:\n{}".format(data))

    def rec_FieldAlign(self, lockerinstance, data):#TODO 
        if len(data) == 6:
            if data[0] == 1:
                with lockerinstance[0].lock:
                    lockerinstance[0].scout['MessageAck'] = True
            elif data[0] == -1:
                ErrorEventWrite(lockerinstance, "SCOUT returned FieldAlign parameter mismatch:\n{}".format(data))
            elif data[0] == -2:
                ErrorEventWrite(lockerinstance, "SCOUT returned FieldAlign parsing error:\n{}".format(data))
            else:
                ErrorEventWrite(lockerinstance, "SCOUT returned wrong FieldAlign ack message:\n{}".format(data))
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete GetAlignInfo message:\n{}".format(data))

    def GetStatus(self, lockerinstance):
        message = self.encode_message(lockerinstance, ['STATUS'])
        self.send_message(lockerinstance, message)

    def GetAlarmReport(self, lockerinstance):
        message = self.encode_message(lockerinstance, ['AL_REPORT'])
        self.send_message(lockerinstance, message)

    def AlarmReset(self, lockerinstance):
        message = self.encode_message(lockerinstance, ['AL_RESET'])
        self.send_message(lockerinstance, message)

    def GetVersion(self, lockerinstance):
        message = self.encode_message(lockerinstance, ['VER'])
        self.send_message(lockerinstance, message)

    def SetAutoStart(self, lockerinstance):
        message = self.encode_message(lockerinstance, ['AT_START'])
        self.send_message(lockerinstance, message)

    def StopAutoStart(self, lockerinstance):
        message = self.encode_message(lockerinstance, ['AT_STOP'])
        self.send_message(lockerinstance, message)

    def TurnOnLaser(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].scout['LaserOn'] = True
        message = self.encode_message(lockerinstance, ['LASER_CTRL','1'])
        self.send_message(lockerinstance, message)

    def TurnOffLaser(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].scout['LaserOn'] = False
        message = self.encode_message(lockerinstance, ['LASER_CTRL','0'])
        self.send_message(lockerinstance, message)

    def __removefromstring(self, string, substring):
        while True:
            searchresult = re.search(substring, string)
            if searchresult:
                newstring = ''
                for i, character in enumerate(string):
                    if i in range(*searchresult.regs[0]): continue
                    newstring += character
            if string != newstring:
                string = newstring
            else: break
        return string

    def ChangeRecipe(self, lockerinstance, recipe = ''):
        with lockerinstance[0].lock:
            if not recipe:
                recipe = lockerinstance[0].scout['recipe']
            else:
                lockerinstance[0].scout['recipe'] = recipe
        recipe = self.__removefromstring(recipe, '.dsg')
        message = self.encode_message(lockerinstance, ['RECIPE_CHANGE',recipe])
        self.send_message(lockerinstance, message)

    def SetWobble(self, lockerinstance):
        with lockerinstance[0].lock:
            mode = lockerinstance[0].scout['scanwobble']['mode']
            frequency = lockerinstance[0].scout['scanwobble']['frequency']
            amplitude = lockerinstance[0].scout['scanwobble']['amplitude']
            power = lockerinstance[0].scout['scanwobble']['power']
        message = self.encode_message(lockerinstance, ['SCAN_WOBBLE', mode, frequency, amplitude, power])
        self.send_message(lockerinstance, message)

    def ManualAlign(self, lockerinstance):
        with lockerinstance[0].lock:
            page = lockerinstance[0].scout['ManualAlignPage']
        message = self.encode_message(lockerinstance, ['MANUAL_ALIGN', page])
        self.send_message(lockerinstance, message)

    def ManualWeld(self, lockerinstance):
        with lockerinstance[0].lock:
            page = lockerinstance[0].scout['ManualWeldPage']
        message = self.encode_message(lockerinstance, ['MANUAL_WELD', page])
        self.send_message(lockerinstance, message)

    def WeldRun(self, lockerinstance):
        with lockerinstance[0].lock:
            pages = lockerinstance[0].scout['pagesToWeld'].copy()
            lockerinstance[0].scout['weldrunpagescount'] = len(pages)
        message = self.encode_message(lockerinstance, ['WELD_RUN', len(pages), *pages])
        self.send_message(lockerinstance, message)

class SCOUT():
    def __init__(self, lockerinstance, configfile):
        while True:
            try:
                with open(configfile) as filehandle:
                    self.config = json.load(filehandle)
            except Exception as e:
                ErrorEventWrite(lockerinstance, 'SCOUT manager cant load json file:\n{}'.format(str(e)))
            else:
                self.Alive = True
                with lockerinstance[0].lock:
                    lockerinstance[0].scout['Alive'] = True
                    lockerinstance[0].scout['recipesdir'] = self.config['Receptures']
                self.connection = KDrawTCPInterface(lockerinstance, configfile)
                try:
                    self.connection.connect(lockerinstance)
                    self.connection.setblocking(False)
                except Exception as e:
                    ErrorEventWrite(lockerinstance, 'SCOUT manager cant connect with k-draw:\n{}'.format(str(e)))
                else:
                    self.loop(lockerinstance)
            finally:
                with lockerinstance[0].lock:
                    self.Alive = lockerinstance[0].scout['Alive']
                    letdie = lockerinstance[0].events['closeApplication']
                if not self.Alive or letdie:
                    self.connection.close()
                    break

    def loop(self, lockerinstance):
        while self.Alive:
            with lockerinstance[0].lock:
                self.Alive = lockerinstance[0].scout['Alive'] and not lockerinstance[0].events['closeApplication']
                if not self.Alive: break
                lastrecv = lockerinstance[0].scout['LastMessageType']
                alarm = lockerinstance[0].scout['status']['Alarm']
                alarmReset = lockerinstance[0].scout['AlarmReset']
                if alarmReset: lockerinstance[0].scout['AlarmReset'] = False
                tlaseron = lockerinstance[0].scout['TurnLaserOn']
                if tlaseron: lockerinstance[0].scout['TurnLaserOn'] = False
                tlaseroff = lockerinstance[0].scout['TurnLaserOff']
                if tlaseroff: lockerinstance[0].scout['TurnLaserOff'] = False
                version = lockerinstance[0].scout['GetVersion']
                if version: lockerinstance[0].scout['GetVersion'] = False
                recipe = lockerinstance[0].scout['SetRecipe']
                if recipe: lockerinstance[0].scout['SetRecipe'] = False
                atstart = lockerinstance[0].scout['AutostartOn']
                if atstart: lockerinstance[0].scout['AutostartOn'] = False
                atstop = lockerinstance[0].scout['AutostartOff']
                if atstop: lockerinstance[0].scout['AutostartOff'] = False
                weld = lockerinstance[0].scout['WeldStart']
                if weld: lockerinstance[0].scout['WeldStart'] = False
                wobbler = lockerinstance[0].scout['Wobble']
                if wobbler: lockerinstance[0].scout['Wobble'] = False
                malign = lockerinstance[0].scout['ManualAlign']
                if malign: lockerinstance[0].scout['ManualAlign'] = False
                mweld = lockerinstance[0].scout['ManualWeld']
                if mweld: lockerinstance[0].scout['ManualWeld'] = False #TODO laserctrl
            if alarm and lastrecv != 'AL_REPORT': self.connection.GetAlarmReport(lockerinstance)
            if tlaseron: self.connection.TurnOnLaser(lockerinstance)
            if tlaseroff: self.connection.TurnOffLaser(lockerinstance)
            if alarmReset: self.connection.AlarmReset(lockerinstance)
            if version and lastrecv != 'VER': self.connection.GetVersion(lockerinstance)
            if recipe: self.connection.ChangeRecipe(lockerinstance)
            if atstart and lastrecv != 'AT_START': self.connection.SetAutoStart(lockerinstance)
            if atstop and lastrecv != 'AT_STOP': self.connection.StopAutoStart(lockerinstance)
            if weld: self.connection.WeldRun(lockerinstance)
            if wobbler: self.connection.SetWobble(lockerinstance)
            if mweld: self.connection.ManualWeld(lockerinstance)
            if malign: self.connection.ManualAlign(lockerinstance)
            self.connection.GetStatus(lockerinstance)
            self.connection.retrievequeue(lockerinstance)
