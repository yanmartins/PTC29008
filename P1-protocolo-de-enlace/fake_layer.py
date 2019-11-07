import layer
import sys

class FakeLayer(layer.Layer):
    '''
    Classe FakeLayer, responsável por subsituir a TunLayer.
    '''

    def __init__(self, obj):
        '''
        Cria um objeto da FakeLayer responsável por substituir a subcamada TunLayer.
        :param obj: objeto que será monitorado pelo poller
        '''
        self.upper = None           # Camada superior
        self.lower = None           # Camada inferior

        layer.Layer.__init__(self, obj)

        self.enable()               # Ativa o monitoramento do objeto
        self.disable_timeout()      # Desativa o Timeout

    def handle(self):
        '''
        Monitora a entrada padrão de dados.
        '''
        lido = sys.stdin.readline()        # Lê linha do teclado
        self.envia(lido.encode())

    def handle_timeout(self):
        pass

    def envia(self, data):
        '''
        Envia os dados lidos da entrada padrão de dados
        para a subcamada inferior (Sessão).
        :param data: Mensagem lida
        '''
        self.lower.envia(data)

    def notifica(self, data):
        '''
        Exibe mensagens vindas da camada inferior (Sessão)
        :param data: Mensagem recebida
        '''
        print('rx_msg: ', data.decode())