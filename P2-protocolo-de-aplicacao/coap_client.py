from random import randint
from enum import Enum

class Type(Enum):
    '''
    Campo typo (2 bits)
    '''
    CON = 0     # Confirmable
    NCON = 1    # Non-confirmable
    ACK = 2     # Acknowledgement
    RST = 3     # Reset

class Code(Enum):
    '''
    Campo code (8 bits)
    '''
    # Request codes
    GET = (0,1)
    POST = (0,2)
    PUT = (0,3)
    DELETE = (0,4)

    # Response Codes
    Created = (2,1)
    Deleted = (2,2)
    Valid = (2,3)
    Changed = (2,4)
    Content = (2,5)
    Continue = (2, 31)

class Tx(Enum):
    '''
    Parâmetros de transmissão
    '''
    ACK_TIMEOUT = 2
    ACK_RANDOM_FACTOR = 1.5
    MAX_RETRANSMIT = 4
    NSTART = 1
    DEFAULT_LEISURE = 5
    PROBING_RATE = 1        # byte/second

class FSM(Enum):
    '''
    Estados da máquina de estados finita
    '''
    inicio = 0
    wait_conf = 1
    ativo = 2
    wait_ack = 3

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
        self.msg.append(self.version << 6 | type << 4 | tkl << 0)
        self.msg.append(code[0] << 5 | code[1] << 0)

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
    codigo = (2,1)
    msg.append(codigo[0] << 5 | codigo[1] << 0)
    print(codigo)
    print(msg)