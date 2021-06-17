import struct
from pymodbus.framer import ModbusFramer
from binascii import b2a_hex, a2b_hex

import logging
_logger = logging.getLogger(__name__)


BASE32_LITERALS =  ['0','1','2','3','4','5','6','7','8','9',
                    'A','B','C','D','E','F','G','H','I','J',
                    'K','L','M','N','O','P','Q','R','S','T',
                    'U','V']
class MRJ4Framer(ModbusFramer):

    """
    [] - 1 ASCII character frame
    Frame sending:
    [SOH][Station][command][command][STX][addr][addr]:[data]...[data][ETX][LRC][LRC] (if presetting value)
                                                     :[ETX][LRC][LRC]                (if reading value)
    Frame receiving:
    [STX][Station][ErrorCode]:[data]...[data][ETX][LRC][LRC]  (when reading)
                             :[ETX][LRC][LRC]                 (when setting) 

    data - 4 to 16 characters
    Station - int base 32 value (0-V) int(Station,32)


    """

    def __init__(self, decoder, client=None, *args, **kwargs):
        self.byteorder = kwargs.pop('byteorder','<')
        self._buffer = b''
        self._header = {'lrc': '0000', 'len': 0, 'uid': 0x00}
        self._hsize = 0x02
        self._head = b'\x01'
        self._text = b'\x02'
        self._endtext = b'\x03'
        self._endcomm = b"\x04"
        self.decoder = decoder
        self.client = client



    def decode_data(self, data):
        if len(data) > 1:
            uid = int(data[1:3], 32)
            fcode = int(data[3:5], 16)
            return dict(unit=uid, fcode=fcode)
        return dict()

    def checkFrame(self):
        start = self._buffer.find(self._text)
        if start == -1:
            return False
        if start > 0:  # go ahead and skip old bad data
            self._buffer = self._buffer[start:]
            start = 0

        end = self._buffer.find(self._endtext)
        if end != -1:
            self._header['len'] = end
            self._header['uid'] = int(self._buffer[1:2].decode(), 16)
            self._header['lrc'] = int(self._buffer[end:end+2].decode(), 16)
            data = self._buffer[start + 1:end].decode()
            return self.checkLRC(data, self._header['lrc'])
        return False

    def computeLRC(self, data):
        sum = 0
        for byte in data:
            sum += int(byte,16)
        return hex(sum)[-2:]

    def checkLRC(self, data, lrc):
        return True if self.computeLRC(data) == lrc else False

    def advanceFrame(self):
        self._buffer = self._buffer[self._header['len'] + 2:]
        self._header = {'lrc': '0000', 'len': 0, 'uid': 0x00}

    def isFrameReady(self):
        return len(self._buffer) > 1

    def addToFrame(self, message):
        self._buffer += message

    def getFrame(self):
        start = self._buffer.find(self._text)
        end = self._buffer.find(self._endtext)
        if -1 in [start,end]:
            return b''
        if end > 0:
            return a2b_hex(self._buffer[start+1:end-1])
        return b''

    def resetFrame(self):
        self._buffer = b''
        self._header = {'lrc': '0000', 'len': 0, 'uid': 0x00}

    def populateResult(self, result):
        result.unit_id = self._header['uid']

    def processIncomingPacket(self, data, callback, unit, **kwargs):
        if not isinstance(unit, (list, tuple)):
            unit = [unit]
        single = kwargs.get('single', False)
        self.addToFrame(data)
        while self.isFrameReady():
            if self.checkFrame():
                if self._validate_unit_id(unit, single):
                    frame = self.getFrame()
                    result = self.decoder.decode(frame)
                    if result is None:
                        pass
                        #raise ModbusIOException("Unable to decode response")
                    self.populateResult(result)
                    self.advanceFrame()
                    callback(result)  # defer this
                else:
                    _logger.error("Not a valid unit id - {}, "
                                  "ignoring!!".format(self._header['uid']))
                    self.resetFrame()
            else:
                break

    def base32(self,parameter):
        if isinstance(parameter, str):
            result = 0
            for iterator, element in enumerate(parameter):
                if element in BASE32_LITERALS:
                    result += pow(32,(len(parameter)-iterator-1))*BASE32_LITERALS.index(element)
                else:
                    return None
            return result
        elif isinstance(parameter, int):
            digitlist = []
            while parameter > 0:
                digitlist.append(parameter%32)
                parameter=int(parameter/32)
            result = ''
            for digit in digitlist:
                result += BASE32_LITERALS[digit]
            result = result[::-1]
            while result[0] == '0' and len(result > 1):
                result = result[1:]
            return result
        

    def buildPacket(self, message):
        encoded = message.encode()
        uid = self.base32(message.unit_id).encode()
        fc = ('%02x' % message.function_code).encode()
        buffer = struct.pack('>BBB', uid,
                             fc)
        checksum = self.computeLRC(encoded + buffer)
        packet = bytearray()
        packet.extend(self._start)
        packet.extend(uid)
        packet.extend(fc)
        packet.extend(b2a_hex(encoded))
        packet.extend(('%02x' % checksum).encode())
        packet.extend(self._end)
        return bytes(packet).upper()


# __END__

