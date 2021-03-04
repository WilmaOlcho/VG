import socket
import json
from Sources import ErrorEventWrite, WDT

class KDrawTCPInterface(socket.socket):
    def __init__(self, lockerinstance, configfile, *args, **kwargs):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        try:
            with open(configfile) as jsonfile:
                self.config = json.load(jsonfile)
        except Exception as e:
            errstring = "KDrawTCPInterface can't load json file: " + str(e)
            ErrorEventWrite(lockerinstance, errstring)

    def receive(self, lockerinstance):
        def start(lockerinstance = lockerinstance):
            with lockerinstance[0].lock:
                lockerinstance[0].scout['connectionbuffer'] = 0
        def loop(obj = self, lockerinstance = lockerinstance):
            data = obj.recv(1024)
            with lockerinstance[0].lock:
                lockerinstance[0].scout['connectionbuffer'] += data
                if b'\r\n' in lockerinstance[0].scout['connectionbuffer']:
                    lockerinstance[0].events['KDrawMessageReceived'] = True
        def catch(obj = self, lockerinstance = lockerinstance):
            obj.decode_messsage(lockerinstance)
        WDT(lockerinstance, additionalFuncOnCatch = catch, additionalFuncOnLoop = loop, additionalFuncOnStart = start ,errToRaise = "KDrawTCPInterface recv() timeout error\n", timeout = 2, eventtocatch = "KDrawMessageReceived")
        
    def write_status(self, lockerinstance, statusdata):
        with lockerinstance[0].lock:
            statusreceived = lockerinstance[0].scout['LastMessageType'] == 'STATUS'
        if statusreceived:
            if len(statusdata) == 8 and statusdata[0] != '0':
                scout = lockerinstance[0].scout
                with lockerinstance[0].lock:
                    for i, status in enumerate(['ReadyOn','AutoStart','Alarm','rsv','WeldingProgress','LaserIsOn','Wobble']):
                        if i == 0: continue #statusdata[0] is checkcode
                        scout['status'][status] = bool(statusdata[i])
            else:
                ErrorEventWrite(lockerinstance, 'SCOUT status data was not fully received: ' + str(statusdata))

    def decode_messsage(self, lockerinstance):
        with lockerinstance[0].lock:
            rawmessage = lockerinstance[0].scout['connectionbuffer']
        contents = rawmessage.decode().splitlines()[0].split(',')
        #mesage is in one bytes() line ended with \r\n
        #it contains values splitted by ','
        if contents:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['LastMessageType'] = contents[0]
            if contents[0] == 'STATUS': self.write_status(lockerinstance,contents[1:])
            elif contents[0] == 'AL_REPORT': pass
            elif contents[0] == 'AL_RESET': pass
            elif contents[0] == 'VER': pass
            elif contents[0] == 'AT_START': pass
            elif contents[0] == 'RECIPE_CHANGE': pass
            elif contents[0] == 'WELD_RUN': pass
            elif contents[0] == 'AT_STOP': pass
            elif contents[0] == 'LASER_CTRL': pass
            elif contents[0] == 'SCAN_WOBBLE': pass
            elif contents[0] == 'MANUAL_ALIGN': pass
            elif contents[0] == 'MANUAL_WELD': pass
            elif contents[0] == 'GET_ALIGN_INFO': pass
            elif contents[0] == 'FIELD_ALIGN': pass
            else:
                ErrorEventWrite(lockerinstance, 'SCOUT responded unusable data: ' + str(contents))
        else:
            ErrorEventWrite(lockerinstance, 'SCOUT responded empty message: ' + str(contents))


class SCOUT():
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

