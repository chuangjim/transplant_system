import serial

class ReqResSerial(serial.Serial):
    def __init__(self, port, 
                       baudrate = 115200, terminator = "", encode = 'ascii', 
                       *args, **kwargs):
        super().__init__(port, baudrate, *args, **kwargs)
        self._terminator = terminator
        self._encode = encode

    def request(self, cmd, timeout = None, retry_times = 0):
        self.timeout = timeout

        for i in range(1+retry_times):
            self.write((cmd + self._terminator).encode(self._encode, 'ascii'))
            response = self.read_until(self._terminator.encode('ascii')).decode('ascii')
            if response: break

        return response if response else None