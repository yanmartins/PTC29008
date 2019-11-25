from random import randint, uniform
from enum import Enum

class Coap():
    '''
    Classe que possui a implementação parcial do protocolo CoAP
    '''
    class Type(Enum):
        '''
        Campo type (2 bits)
        '''
        CON = 0  # Confirmable
        NON = 1  # Non-confirmable
        ACK = 2  # Acknowledgement
        RST = 3  # Reset

    class Code(Enum):
        '''
        Campo code (8 bits)
        '''
        # Request
        EMPTY = (0, 0)
        GET = (0, 1)
        POST = (0, 2)
        PUT = (0, 3)
        DELETE = (0, 4)

        # Success Response
        Created = (2, 1)
        Deleted = (2, 2)
        Valid = (2, 3)
        Changed = (2, 4)
        Content = (2, 5)
        Continue = (2, 31)

        # Client Error Response
        Bad_Request = (4, 0)
        Unauthorized = (4, 1)
        Bad_Option = (4, 2)
        Forbidden = (4, 3)
        Not_Found = (4, 4)
        Method_Not_Allowed = (4, 5)
        Not_Acceptable = (4, 6)
        Precondition_Failed = (4, 12)
        Request_Entity_Too_Large = (4, 13)
        Unsupported_Content_Format = (4, 15)

        # Server Error Response
        Internal_Server_Error = (5, 0)
        Not_Implemented = (5, 1)
        Bad_Gateway = (5, 2)
        Service_Unavailable = (5, 3)
        Gateway_Timeout = (5, 4)
        Proxying_Not_Supported = (5, 5)

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
        self.tkl = 1   # 2 bits
        self.payload_marker = 0b11111111
        self.uri_path = 11

        self.type = 0
        self.code = 0
        self.mid = 0
        self.payload = 0
        self.token = 0
        self.options = 0

        self.retries = 0

    def make_header(self, type, code, payload=None, uri=None, mid1=None, mid2=None):
        '''
        Monta um cabeçalho CoAP
        :param type: tipo da mensagem (CON, NON, ACK ou RST)
        :param code: códigos (request ou response)
        :param payload: conteúdo do quadro
        :param uri: uri-path
        :return: cabeçalho pronto para ser enviado
        '''
        self.msg.clear()
        token = randint(0, 255)

        if (mid1 or mid2) == None:
            mid1 = randint(0, 255)
            mid2 = randint(0, 255)

        # 8 bytes: Ver (2 bits), Type (2 bits), TKL (4 bits)
        self.msg.append(self.version << 6 | type << 4 | self.tkl << 0)

        # 8 bytes: Code
        self.msg.append(code[0] << 5 | code[1] << 0)

        # 16 bytes: Identificador da mensagem
        self.msg.append(mid1)
        self.msg.append(mid2)

        # 8 bytes: Token
        self.msg.append(token)

        if not uri == None:
            self.msg.append(self.uri_path << 4 | (len(uri) << 0))


            self.msg = self.msg + uri

        if not payload == None:
            self.msg.append(self.payload_marker)
            self.msg = self.msg + payload
        return self.msg

    def make_ack(self, mid1, mid2, uri, code=Code.Valid.value):
        '''
        Monta um cabeçalho do tipo ACK.
        :param mid1: primeiro byte do identificador
        :param mid2: segundo byte do identificador
        :param uri: caminho da uri
        :param code: código (defaut: 2.03 Valid)
        :return: cabeçalho pronto para ser enviado
        '''
        msg = self.make_header(self.Type.ACK.value, code, uri=uri, mid1=mid1, mid2=mid2)
        return msg

    def make_get(self, uri=None, type=Type.CON.value):
        '''
        Monta um cabeçalho do tipo GET.
        :param uri: caminho da URI.
        :param type: confirmável ou não-confirmável (default: CON).
        :return: cabeçalho pronto para ser enviado.
        '''
        msg = self.make_header(type, self.Code.GET.value, uri=uri)
        return msg

    def make_post(self, payload, uri=None, type=Type.CON.value):
        '''
        Monta um cabeçalho do tipo GET.
        :param payload: conteúdo da mensagem.
        :param uri: caminho da URI.
        :param type: confirmável ou não-confirmável (default: CON).
        :return: cabeçalho pronto para ser enviado.
        '''
        msg = self.make_header(type, self.Code.POST.value, payload=payload, uri=uri)
        return msg

    def check_client_error(self, msg):
        '''
        Verifica se a mensagem contém código de Client Error.
        :param msg: mensagem a ser verificada.
        :return: resultado booleano.
        '''
        if (msg[1] >> 5) == 4:
            return True
        else: return False

    def check_server_error(self, msg):
        '''
        Verifica se a mensagem contém código de Server Error.
        :param msg: mensagem a ser verificada.
        :return: resultado booleano.
        '''
        if (msg[1] >> 5) == 5:
            return True
        else: return False

    def check_code(self, msg, code):
        '''
        Verifica se a mensagem contém determinado código.
        :param msg: mensagem a ser verificada.
        :param code: código que será comparado.
        :return: resultado booleano.
        '''
        if msg[1] == (code[0] << 5 | code[1] << 0):
            return True
        else: return False

    def random_ack_timeout(self):
        '''
        Sorteia um valor para timeout de recepção de uma mensagem do tipo ACK
        :return: valor sorteado
        '''
        return uniform(self.Tx.ACK_TIMEOUT.value, self.Tx.ACK_TIMEOUT.value*self.Tx.ACK_RANDOM_FACTOR.value)

    def retransmit(self):
        '''
        Incrementa o número de tentativas de reenvio.
        :return: mensagem a ser reenviada.
        '''
        self.retries = self.retries + 1
        return self.msg

    def check_retries(self):
        '''
        Verifica se foi atingido o número máximo de retransmissões.
        :return: resultado booleano.
        '''
        if self.retries < self.Tx.MAX_RETRANSMIT.value - 1:
            return True
        else:
            return False

    def clean_retries(self):
        '''
        Reinicia a contagem de número de tentativas de reenvio.
        '''
        self.retries = 0

    def get_mids(self, msg):
        '''
        Obtem os dois bytes correspondentes aos identificadores
        de uma determinada mensagem. Útil para o ACK.
        :param msg: mensagem cuja serão coletados os mids.
        :return: mids coletados.
        '''
        mid1 = msg[2]
        mid2 = msg[3]
        return mid1, mid2