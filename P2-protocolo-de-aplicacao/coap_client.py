from random import randint
from enum import Enum
import socket

class CoapClient():

    class Type(Enum):
        '''
        Campo typo (2 bits)
        '''
        CON = 0  # Confirmable
        NON = 1  # Non-confirmable
        ACK = 2  # Acknowledgement
        RST = 3  # Reset

    class Code(Enum):
        '''
        Campo code (8 bits)
        '''
        # Request codes
        EMPTY = (0, 0)
        GET = (0, 1)
        POST = (0, 2)
        PUT = (0, 3)
        DELETE = (0, 4)
        # Response Codes
        Created = (2, 1)
        Deleted = (2, 2)
        Valid = (2, 3)
        Changed = (2, 4)
        Content = (2, 5)
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
        PROBING_RATE = 1  # byte/second

    class FSM(Enum):
        '''
        Estados da máquina de estados finita
        '''
        inicio = 0
        wait_conf = 1
        ativo = 2
        wait_ack = 3

    def __init__(self):
        self.msg = bytearray()

        self.version = 1
        self.tkl = 1    # byte
        self.payload_marker = 0b11111111
        self.uri_path = 11

        self.state = self.FSM.inicio.value
        self.type = 0
        self.code = 0
        self.mid = 0
        self.payload = 0
        self.token = 0
        self.options = 0

        self.servidor = ('::1', 5683)
        self.caminho = ('::', 0)
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.bind(self.caminho)

    def make_header(self, type, code, payload=None, uris=None):
        msg = bytearray()
        token = randint(0, 255)
        mid1 = randint(0, 255)
        mid2 = randint(0, 255)

        msg.append(self.version << 6 | type << 4 | self.tkl << 0)
        msg.append(code[0] << 5 | code[1] << 0)

        msg.append(mid1)
        msg.append(mid2)
        msg.append(token)

        msg.append(self.uri_path << 4 | (len(uris) << 0))

        for i in range(len(uris)):
            msg.append(ord(uris[i]))

        if not payload == None:
            for i in range(len(payload)):
                if i == 0:
                    msg.append(self.payload_marker)
                msg.append(payload[i])

        self.sock.sendto(msg,self.servidor)
        return msg

    def make_ack(self, mid1, mid2):
        msg = bytearray()
        msg.append(self.version << 6 | self.Type.ACK.value << 4)
        msg.append(self.Code.EMPTY.value[0] << 5 | self.Code.EMPTY.value[1] << 0)
        msg.append(mid1)
        msg.append(mid2)
        self.sock.sendto(msg, self.servidor)
        return msg

    def make_get(self, type=Type.CON.value):
        msg = self.make_header(type, self.Code.GET.value)
        return msg

    def make_post(self, payload, uri, type=Type.CON.value):
        msg =self.make_header(type, self.Code.POST.value, payload, uri)
        return msg

    def handle_fsm(self):
        if self.state == self.FSM.inicio.value:
            self._inicio()
        elif self.state == self.FSM.wait_conf.value:
            self._wait_conf()
        elif self.state == self.FSM.ativo.value:
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
    c = CoapClient()
    #print(c.make_header(c.Type.CON.value, c.Code.GET.value))
    #print(c.make_header(c.Type.CON.value, c.Code.POST.value, b'22 graus'))
    print(c.make_ack(12,12))
    print(c.make_get())
    print(c.make_post(b'22 graus'))
