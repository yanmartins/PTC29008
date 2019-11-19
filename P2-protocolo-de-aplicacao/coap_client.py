from random import randint
from enum import Enum
import socket

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
    EMPTY = (0,0)
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
        self.tkl = 1 # byte
        self.payload_marker = 0b11111111

        self.state = FSM.inicio.value

        self.type = 0
        self.code = 0
        self.mid = 0
        self.payload = 0
        self.token = 0
        self.options = 0

        self.servidor = ('::1', 5683)
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.bind(('::', 0))

    def make_header(self, type, code, payload=None, options=None):
        print('Type: ', type)
        msg = bytearray()
        token = randint(0, 255)
        mid1 = randint(0, 255)
        mid2 = randint(0, 255)

        msg.append(self.version << 6 | type << 4 | self.tkl << 0)
        msg.append(code[0] << 5 | code[1] << 0)

        msg.append(mid1)
        msg.append(mid2)
        msg.append(token)

        if not options == None:
            msg.append(options)
        msg.append(self.payload_marker)
        if not payload == None:
            for i in range(len(payload)):
                msg.append(payload[i])

        self.sock.sendto(msg,self.servidor)
        return msg

    def send_ack(self, mid1, mid2):
        msg = bytearray()
        msg.append(self.version << 6 | Type.ACK.value << 4)
        msg.append(Code.EMPTY.value[0] << 5 | Code.EMPTY.value[1] << 0)
        msg.append(mid1)
        msg.append(mid2)

        self.sock.sendto(msg, self.servidor)
        return msg

    def make_get(self, type=Type.CON.value):
        self.make_header(self, type, Code.GET.value)

    def make_post(self, payload, type=Type.CON.value):
        self.make_header(self, type, Code.POST.value, payload)

    def handle_fsm(self):
        if self.state == FSM.inicio.value:
            self._inicio()
        elif self.state ==  FSM.wait_conf.value:
            self._wait_conf()
        elif self.state == FSM.ativo.value:
            self._ativo()
        else:
            self._wait_ack()

    def _inicio(self):
        pass

    def _wait_conf(self):
        pass

    def _ativo(self):
        pass

    def _wait_ack(self):
        pass

    def handle(self):
        pass

if __name__ == "__main__":
    # version = 1
    # type = Type.CON.value
    # tkl = 4
    # msg = bytearray()
    # msg.append(version << 6 | type << 4 | tkl << 0)
    # codigo = (2,1)
    # msg.append(codigo[0] << 5 | codigo[1] << 0)
    # print(codigo)
    # print(msg)
    c = CoapClient()
    print(c.make_header(Type.CON.value, Code.GET.value))
    print(c.make_get())
