from random import randint
from enum import Enum

class Type(Enum):
    CON = 0     # Confirmable
    NCON = 1    # Non-confirmable
    ACK = 2     # Acknowledgement
    RST = 3     # Reset

class Code(Enum):
    # Request codes
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4

    # Response Codes
    Created = 65
    Deleted = 66
    Valid = 67
    Changed = 68
    Content = 69

class Tx(Enum):
    ACK_TIMEOUT = 2
    ACK_RANDOM_FACTOR = 1.5
    MAX_RETRANSMIT = 4
    NSTART = 1
    DEFAULT_LEISURE = 5
    PROBING_RATE = 1        # byte/second

class CoapClient():

    def __init__(self):
        self.msg = bytearray()
        self.version = 1
        self.type = 0
        self.code = 0
        self.mid = 0
        self.payload = 0
        self.token = 0
        self.options = 0

    def make_header(self, type, code, payload, token, options):
        tkl = len(token)
        msg.append(self.version << 6 | type << 4 | tkl << 0)
        self.msg.append(code)

        mid1 = randint(0, 255)
        mid2 = randint(0, 255)
        self.msg.append(mid1)
        self.msg.append(mid2)

        if (not tkl == 0):
            self.msg.append(token)
        if (not options == 0):
            self.msg.append(options)
        payload_marker = 0b11111111
        self.msg.append(payload_marker)
        self.msg.append(payload)

if __name__ == "__main__":

    version = 1
    type = Type.CON.value
    tkl = 4
    msg = bytearray()
    msg.append(version << 6 | type << 4 | tkl << 0)
    codigo = (2,5)
    msg.append(codigo)
    print(codigo)
    print(msg)