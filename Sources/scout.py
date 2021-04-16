import socket
import json
import re
from .common import ErrorEventWrite, EventManager
from .TactWatchdog import TactWatchdog
WDT = TactWatchdog.WDT

class KDrawTCPInterface(socket.socket):
    '''Klasa dziedzicząca po socket.socket, zawierająca metody służące
    do bezpośredniego wykonywania poleceń dla K-Draw po TCP\\IP'''
    
    def __init__(self, lockerinstance, configfile, *args, **kwargs):
        '''
        Metoda inicjująca połączenie, przyjmuje słownik lockerinstance z
        zawartą instancją klasy posiadającej atrybuty lock i scout i plik
        konfiguracyjny w formacie json.
        lockerinstance[0] -> odniesienie do obiektu
        lockerinstance[0].lock -> obiekt multiprocessing.Lock()
        lockerinstance[0].scout -> obiekt multiprocessing.Manager().dictproxy()

        Plik konfiguracyjny przyjmuje postać:
        {
            "connection":{
                "IP":"192.168.4.200", <- adres serwera K-draw dla socketu
                "port":3000 <- port serwera K-draw
            },
            "ProgramPath":"C:\\K-Draw\\", <- główny folder programu K-Draw
            "Receptures":"C:\\K-Draw\\Design" <- folder z recepturami K-Draw
        }
        '''
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
        '''
        Metoda uruchamiająca połączenie przez socket pod
        wybranym w pliku konfiguracyjnym adresem.
        '''
        address = self.config['connection']['IP']
        port = self.config['connection']['port']
        super().connect((address,port)) #Wykonanie metody klasy nadrzędnej
        with lockerinstance[0].lock:
            lockerinstance[0].events['ScoutManagerReadyToSend'] = True #ustawienie flagi gotowości do wysyłania danych
    
    def retrievequeue(self, lockerinstance):
        '''
        Metoda odświeżająca kolejkę wysyłania poleceń do K-draw,
        kolejka umożliwia realizowanie zadań po kolei, bez ryzyka
        pominięcia któregoś z nich. Kolejka działa według zasady FIFO.
        '''
        if self.sendingqueue:
            with lockerinstance[0].lock:
                event = lockerinstance[0].events['ScoutManagerReadyToSend']
            if event:
                with lockerinstance[0].lock:
                    lockerinstance[0].events['ScoutManagerReadyToSend'] = False
                self.sendall(self.sendingqueue.pop(0))
                self.receive(lockerinstance)

    def add_to_queue(self, lockerinstance, bytes_message):
        '''
        Metoda dodająca do kolejki pełne polecenie
        SCOUT w przypadku gdy takie nie oczekuje na wykonanie.
        '''
        if bytes_message in self.sendingqueue:
            return None
        else:
            self.sendingqueue.append(bytes_message)

    def receive(self, lockerinstance):
        '''
        Metoda realizująca funkcję oczekiwania na dane zwrotne z K-Draw.
        Deklarowane są metody: 'start', 'loop' i 'catch', które kolejno
        służą do czynności przy uruchomieniu pętli timera, przy każdym
        jego cyklu i w przypadku przekroczenia jego czasu lub wykrycia
        zdarzenia przerywającego pętlę. Timer WDT tworzy nowy wątek. 
        '''
        def start(lockerinstance = lockerinstance): #Metoda wykonywana przy uruchomieniu timera
            with lockerinstance[0].lock:
                lockerinstance[0].scout['connectionbuffer'] = b''
        def loop(obj = self, lockerinstance = lockerinstance): #Metoda wykonywana przy obrocie timera przez własną pętlę
            try:
                data = obj.recv(1024)
            except:
                data = b''
            finally:
                with lockerinstance[0].lock:
                    lockerinstance[0].scout['WaitingForData'] = True
                    lockerinstance[0].scout['connectionbuffer'] += data
                    if b'\r\n' in lockerinstance[0].scout['connectionbuffer']:
                        lockerinstance[0].events['KDrawMessageReceived'] = True #Utworzenie zdarzenia przerywającego odbiór danych w przypadku ich kompletności
        def catch(obj = self, lockerinstance = lockerinstance): #Metoda wywoływana przy zakończeniu działania timera
            lockerinstance[0].scout['WaitingForData'] = False
            obj.decode_messsage(lockerinstance)
        WDT(lockerinstance, additionalFuncOnExceed = catch, additionalFuncOnCatch = catch, additionalFuncOnLoop = loop, additionalFuncOnStart = start ,errToRaise = "KDrawTCPInterface recv() timeout error\n", limitval = 60, scale = 's', eventToCatch = "KDrawMessageReceived")

    def encode_message(self, lockerinstance, message):
        '''
        Metoda tworząca polecenie z zadanych parametrów zgodnie z dokumentacją
        SCOUT. Tworzony format przyjmuje postać:
        [COMMAND] , [data[1]] , [data[2]] , ... \r\n
        gdzie COMMAND oznacza polecenie, ',' jest separatorem, a każde polecenie
        zakończone jest znakami zakończenia linii \r\n
        '''
        string = ''
        for element in message: #message is an list of parameters
            string += str(element) + ',' #parameters are splitted by coma
        if string[-1] == ',': string = string[:-1] #removing last coma from string
        _bytes = string.encode() #convert to utf-8
        _bytes += b'\r\n' #end of message
        return _bytes

    def decode_messsage(self, lockerinstance):
        '''
        Metoda przetwarzająca odebrane dane i przekazujące je do obsługi przez
        przypisane do nich metody
        '''
        with lockerinstance[0].lock:
            rawmessage = lockerinstance[0].scout['connectionbuffer']
        lines = rawmessage.decode().splitlines() #Podział danych na linie przez znaki \r\n nie wykluczają istnienia danych poza ramką SCOUT
        contents = []
        for line in lines:
            contents.extend(line.split(','))
        #mesage is in one bytes() line ended with \r\n
        #it contains values splitted by ','
        if contents: ##Przekazywanie danych do metod dekodujących konkretne dane
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
        '''
        Metoda obsługująca ramkę zwrotną STATUS
        '''
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
        '''
        Metoda obsługująca ramkę zwrotną AL_REPORT
        '''
        if len(data)==3:
            ErrorEventWrite(lockerinstance, 'SCOUT reported alarm message with code: {}\n{}'.format(data[1],data[2]))
            with lockerinstance[0].lock:
                lockerinstance[0].scout['MessageAck'] = True
        else:
            ErrorEventWrite(lockerinstance, "SCOUT reported alarm message, but it's ioncomplete:\n{}".format(data))

    def rec_AlarmReset(self, lockerinstance, data):
        '''
        Metoda obsługująca ramkę zwrotną AL_RESET
        '''
        if len(data) == 1:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['MessageAck'] = True
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete reset ack message:\n{}".format(data))

    def rec_Version(self, lockerinstance, data):
        '''
        Metoda obsługująca ramkę zwrotną VER
        '''
        if len(data) == 2:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['MessageAck'] = True
                lockerinstance[0].scout['version'] = data[1]
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete version message:\n{}".format(data))

    def rec_AtStart(self, lockerinstance, data):
        '''
        Metoda obsługująca ramkę zwrotną AT_START
        '''
        if len(data) == 1:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['MessageAck'] = True
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete Autostart ack message:\n{}".format(data))

    def rec_RecipeChange(self, lockerinstance, data):
        '''
        Metoda obsługująca ramkę zwrotną RECIPE_CHANGE
        '''
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
        '''
        Metoda obsługująca ramkę zwrotną WELD_RUN
        '''
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
        '''
        Metoda obsługująca ramkę zwrotną AT_STOP
        '''
        if len(data) == 1:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['MessageAck'] = True
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete Autostop ack message:\n{}".format(data))

    def rec_LaserCTRL(self, lockerinstance, data):
        '''
        Metoda obsługująca ramkę zwrotną LASER_CTRL
        '''
        if len(data) == 2:
            with lockerinstance[0].lock:
                laserack = bool(int(data[1])) == lockerinstance[0].scout['LaserOn']
                if laserack: lockerinstance[0].scout['MessageAck'] = True
            if not laserack:
                ErrorEventWrite(lockerinstance, "SCOUT returned wrong LaserCTRL ack message:\n{}".format(data))
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete LaserCTRL ack message:\n{}".format(data))

    def rec_ScanWobble(self, lockerinstance, data):
        '''
        Metoda obsługująca ramkę zwrotną SCAN_WOBBLE
        '''
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
        '''
        Metoda obsługująca ramkę zwrotną MANUAL_ALIGN
        '''
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
        '''
        Metoda obsługująca ramkę zwrotną MANUAL_WELD
        '''
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
        '''
        Metoda obsługująca ramkę zwrotną GET_ALIGN_INFO
        '''
        if len(data) == 9 or len(data) == 6:
            if data[0] == 1 and data[2] == 1:
                with lockerinstance[0].lock:
                    if len(data) == 6:
                        axy = data[3:]
                        data = data[:3]
                        for i in range(3):
                            integer = int(axy[i])
                            afterdot = axy[i] - integer
                            data.expand([integer, afterdot])
                    for i, value in enumerate(['0','1','2','A','dotA','X','dotX','Y','dotY']):
                        lockerinstance[0].scout['AlignInfo'][value] = int(data[i])  
                    lockerinstance[0].scout['MessageAck'] = True
            else:
                ErrorEventWrite(lockerinstance, "SCOUT returned GetAlignInfo failed:\n{}".format(data))
        else:
            ErrorEventWrite(lockerinstance, "SCOUT returned incomplete GetAlignInfo message:\n{}".format(data))

    def GetAlignInfo(self, lockerinstance):
        '''
        Metoda kodująca ramkę GET_ALIGN_INFO
        '''
        message = self.encode_message(lockerinstance, ['GET_ALIGN_INFO'])
        self.add_to_queue(lockerinstance, message)

    def rec_FieldAlign(self, lockerinstance, data):
        '''
        Metoda kodująca ramkę FIELD_ALIGN //TODO - niekompletna
        '''
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
        '''
        Metoda kodująca ramkę STATUS
        '''
        message = self.encode_message(lockerinstance, ['STATUS'])
        self.add_to_queue(lockerinstance, message)

    def LaserCTRL(self, lockerinstance):
        with lockerinstance[0].lock:
            value = lockerinstance[0].scout['LaserCTRVal']
        message = self.encode_message(lockerinstance, ['LASER_CTRL', value])
        self.add_to_queue(lockerinstance, message)

    def GetAlarmReport(self, lockerinstance):
        '''
        Metoda kodująca ramkę AL_REPORT
        '''
        message = self.encode_message(lockerinstance, ['AL_REPORT'])
        self.add_to_queue(lockerinstance, message)

    def AlarmReset(self, lockerinstance):
        '''
        Metoda kodująca ramkę AL_RESET
        '''
        message = self.encode_message(lockerinstance, ['AL_RESET'])
        self.add_to_queue(lockerinstance, message)

    def GetVersion(self, lockerinstance):
        '''
        Metoda kodująca ramkę VER
        '''
        message = self.encode_message(lockerinstance, ['VER'])
        self.add_to_queue(lockerinstance, message)

    def SetAutoStart(self, lockerinstance):
        '''
        Metoda kodująca ramkę AT_START
        '''
        message = self.encode_message(lockerinstance, ['AT_START'])
        self.add_to_queue(lockerinstance, message)

    def StopAutoStart(self, lockerinstance):
        '''
        Metoda kodująca ramkę AT_STOP
        '''
        message = self.encode_message(lockerinstance, ['AT_STOP'])
        self.add_to_queue(lockerinstance, message)

    def TurnOnLaser(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].scout['LaserOn'] = True
        message = self.encode_message(lockerinstance, ['LASER_CTRL','1'])
        self.add_to_queue(lockerinstance, message)

    def TurnOffLaser(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].scout['LaserOn'] = False
        message = self.encode_message(lockerinstance, ['LASER_CTRL','0'])
        self.add_to_queue(lockerinstance, message)

    def __removefromstring(self, string, substring):
        '''
        Metoda usuwająca zadany fragment zmiennej string
        string  <- kikutituki.jpg
        substring <- tuki
        return -> kikuti.jpg
        '''
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
        '''
        Metoda kodująca ramkę RECIPE_CHANGE
        '''
        with lockerinstance[0].lock:
            if not recipe:
                recipe = lockerinstance[0].scout['recipe']
            else:
                lockerinstance[0].scout['recipe'] = recipe
        recipe = self.__removefromstring(recipe, '.dsg')
        message = self.encode_message(lockerinstance, ['RECIPE_CHANGE',recipe])
        self.add_to_queue(lockerinstance, message)

    def SetWobble(self, lockerinstance):
        '''
        Metoda kodująca ramkę SCAN_WOBBLE
        '''
        with lockerinstance[0].lock:
            mode = lockerinstance[0].scout['scanwobble']['mode']
            frequency = lockerinstance[0].scout['scanwobble']['frequency']
            amplitude = lockerinstance[0].scout['scanwobble']['amplitude']
            power = lockerinstance[0].scout['scanwobble']['power']
        message = self.encode_message(lockerinstance, ['SCAN_WOBBLE', mode, frequency, amplitude, power])
        self.add_to_queue(lockerinstance, message)

    def ManualAlign(self, lockerinstance):
        '''
        Metoda kodująca ramkę MANUAL_ALIGN
        '''
        with lockerinstance[0].lock:
            page = lockerinstance[0].scout['ManualAlignPage']
        message = self.encode_message(lockerinstance, ['MANUAL_ALIGN', str(page)])
        self.add_to_queue(lockerinstance, message)

    def ManualWeld(self, lockerinstance):
        '''
        Metoda kodująca ramkę MANUAL_WELD
        '''
        with lockerinstance[0].lock:
            page = lockerinstance[0].scout['ManualWeldPage']
        message = self.encode_message(lockerinstance, ['MANUAL_WELD', page])
        self.add_to_queue(lockerinstance, message)

    def WeldRun(self, lockerinstance):
        '''
        Metoda kodująca ramkę WELD_RUN
        '''
        with lockerinstance[0].lock:
            pages = lockerinstance[0].scout['pagesToWeld'].copy()
            lockerinstance[0].scout['weldrunpagescount'] = len(pages)
        message = self.encode_message(lockerinstance, ['WELD_RUN', len(pages), *pages])
        self.add_to_queue(lockerinstance, message)

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
                if mweld: lockerinstance[0].scout['ManualWeld'] = False
                getaligninfo = lockerinstance[0].scout['GetAlignInfo']
                if getaligninfo: lockerinstance[0].scout['GetAlignInfo'] = False
                laserctrl = lockerinstance[0].scout['LaserCTRL']
                if laserctrl: lockerinstance[0].scout['LaserCTRL'] = False
                 #TODO laserctrl
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
            if getaligninfo: self.connection.GetAlignInfo(lockerinstance)
            if laserctrl: self.connection.LaserCTRL(lockerinstance)
            self.connection.GetStatus(lockerinstance)
            self.connection.retrievequeue(lockerinstance)
