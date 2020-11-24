


class Modbus_constants():
    def __init__(self, *args, **kwargs):
        self.functionCodes = {
            'Read Coil Status':1,
            'Read Input Status':2,
            'Read Holding Registers':3,
            'Read Input Registers':4,
            'Force Single Coil':5,
            'Preset Single Register':6,
            'Loopback Diagnosis':8,
            'Force Multiple Coils':15,
            'Preset Multiple Registers':16,
            'Masked Write Register':22}
        self.READ_COIL = 1
        self.WRITE_COIL = 5
        self.READ_INPUT = 2
        self.WRITE_COILS = 15
        self.WRITE_REGISTERS = 16
        self.READ_HOLDING_REGISTERS = 3
        self.READ_INPUT_HOLDING_REGISTERS = 4
        self.WRITE_REGISTER = 6
        self.LOOPBACK_DIAGNOSIS = 8
        self.MASKED_REGISTER = 22
        super().__init__(self, *args, **kwargs)