import layer
import time

class Sessao(layer.Layer):
    '''
    Classe Sessao, responsável pelo gerenaciamento da sessão,
    manutenção e terminação
    '''
    # Estados para a FSM
    DISC = 0    # Desconectado
    HAND1 = 1   # Em aguardo por confirmação de pedido de conexão
    HAND2 = 2   # Em aguardo por confirmação de pedido de conexão, após receber pedido de conexão do outro lado
    HAND3 = 3   # Em aguardo por pedido de conexão
    CON = 4     # Conectado
    CHECK = 5   # Aguardando resposta para Keep Alive
    HALF1 = 6   # Half-close, quando tomou a iniciativa de terminá-lo
    HALF2 = 7   # Half-close, quando o outro lado tomou a iniciativa

    # Campo ID Proto
    id_proto = 0x00
    id_proto_ipv4 = 0x01
    id_proto_ipv6 = 0x02
    id_proto_sessao = 0xFF

    # Campo Dados
    CR = 0  # Connect request
    CC = 1  # Connect confirm
    KR = 2  # Keep Alive Request
    KC = 3  # Keep Alive Confirm
    DR = 4  # Disconnect Request
    DC = 5  # Disconnect Confirm

    def __init__(self, timeout, check_interval):
        '''
        Cria um objeto Sessao
        :param timeout: valor de timeout em segundos
        :param check_interval: valor de tempo para persistência da conexão
        '''
        self.msg = bytearray()

        self.estado = self.DISC     # Estado inicial da FSM

        self.is_online = False

        self.upper = None
        self.lower = None

        self.tout = timeout                     # Tempo de espera por mensagem
        self.check_interval = check_interval    # Tempo para verificar estado da conexão
        self.timeout_grande = 30                # Tempo para sair do estado HALF2

        layer.Layer.__init__(self, None, timeout)

        self.enable()
        self.disable_timeout()  # Desativa o Timeout

    def handle_fsm(self, data):
        '''
        Máquina de estado que trata o envio e recepção de mensagens do tipo sessão
        :param data: mensagem recebida
        '''
        if self.estado == self.DISC:
            self._desconectado()
        elif self.estado == self.HAND1:
            self._hand1(data)
        elif self.estado == self.HAND2:
            self._hand2(data)
        elif self.estado == self.HAND3:
            self._hand3(data)
        elif self.estado == self.CON:
            self._conectado(data)
        elif self.estado == self.CHECK:
            self._check(data)
        elif self.estado == self.HALF1:
            self._half1(data)
        else:
            self._half2(data)

    def _desconectado(self):
        self.start()

    def _hand1(self, data):
        self.recarrega_timeout(self.tout)
        if(data[3] == self.CR):
            self.estado = self.HAND2
            self.monta_quadro_manutencao(self.CC)
        elif(data[3] == self.CC):
            self.estado = self.HAND3

    def _hand2(self, data):
        if(data[3] == self.CC):
            self.estado = self.CON
            self.is_online = True
            print('CONECTADO!')
            self.recarrega_timeout(self.check_interval)

        elif(data[3] == self.DR):
            self.estado = self.HALF2
            self.recarrega_timeout(self.timeout_grande)
            self.monta_quadro_manutencao(self.DR)

    def _hand3(self, data):
        if(data[3] == self.CR):
            self.estado = self.CON
            self.is_online = True
            print('CONECTADO!')
            self.recarrega_timeout(self.check_interval)
            self.monta_quadro_manutencao(self.CC)

    def _conectado(self, data):
        if(data[3] == self.DR):
            self.estado = self.HALF2
            self.recarrega_timeout(self.timeout_grande)
            self.monta_quadro_manutencao(self.DR)

        elif(data[3] == self.KR):
            self.estado = self.CON
            print('Tô vivo!')
            self.recarrega_timeout(self.check_interval)
            self.monta_quadro_manutencao(self.KC)

        # Se for uma mensagem do tipo dados
        elif(data[2] == self.id_proto_ipv4) or (data[2] == self.id_proto_ipv6) or (data[2] == self.id_proto):
            self.estado = self.CON
            self.recarrega_timeout(self.check_interval)
            self.upper.notifica(data[3:-2])

    def _check(self, data):
        if(data[3] == self.KC):
            self.estado = self.CON
            self.recarrega_timeout(self.check_interval)

        elif(data[3] == self.KR):
            self.estado = self.CHECK
            print('Tô vivo!')
            self.recarrega_timeout(self.tout)
            self.monta_quadro_manutencao(self.KC)

        elif(data[3] == self.DR):
            self.estado = self.HALF2
            self.recarrega_timeout(self.timeout_grande)
            self.monta_quadro_manutencao(self.DR)

        elif (data[2] == self.id_proto_ipv4) or (data[2] == self.id_proto_ipv6) or (data[2] == self.id_proto):
            self.estado = self.CON
            self.recarrega_timeout(self.check_interval)
            self.upper.notifica(data[3:-2])

    def _half1(self, data):
        if (data[3] == self.DR):
            self.estado = self.DISC
            self.monta_quadro_manutencao(self.DC)
            print('Desconectado')

        elif (data[3] == self.KR):
            self.estado = self.HALF1
            self.monta_quadro_manutencao(self.DR)

    def _half2(self, data):
        if (data[3] == self.DC):
            self.estado = self.DISC
            print('Desconectado')

        elif(data[3] == self.DR):
            self.estado = self.HALF2
            self.monta_quadro_manutencao(self.DR)

    def handle_timeout(self):
        print('deu tout')
        if (self.estado == self.CON):
            #print('timeout no CON')
            print('Tás vivo?')
            self.estado = self.CHECK
            self.recarrega_timeout(self.tout)
            self.monta_quadro_manutencao(self.KR)

        elif self.estado == self.HAND1:
            self.estado = self.HAND1
            self.recarrega_timeout(self.tout)
            self.monta_quadro_manutencao(self.CR)

        elif self.estado == self.HAND2:
            self.estado = self.HAND1
            self.recarrega_timeout(self.tout)
            self.monta_quadro_manutencao(self.CR)

        elif self.estado == self.HAND3:
            self.estado = self.HAND1
            self.recarrega_timeout(self.tout)
            self.monta_quadro_manutencao(self.CR)

        elif self.estado == self.HALF2:
            self.estado = self.DISC
            self.is_online = False
            print('Desconectado')

    def start(self):
        '''
        Inicia o processo de conexão
        '''
        if (self.estado == self.DISC):
            self.estado = self.HAND1
            self.recarrega_timeout(self.tout)
            self.monta_quadro_manutencao(self.CR)

    def close(self):
        '''
        Inicia o processo de desconexão
        '''
        if (self.estado == self.CON):
            self.estado = self.HALF1
            self.monta_quadro_manutencao(self.DR)

    def recarrega_timeout(self, timeout):
        '''
        Carrega um novo valor de timeout e o recarrega
        :param timeout: tempo de espera
        '''
        self.base_timeout = timeout
        self.reload_timeout()
        self.enable_timeout()

    def handle(self):
        pass

    def monta_quadro_manutencao(self, data):
        '''
        Monta um quadro de dados do tipo sessão
        :param data: mensagem do tipo sessão
        '''
        self.msg.clear()
        self.msg.append(self.id_proto_sessao)
        self.msg.append(data)
        self.lower.envia(self.msg)

    def monta_quadro_msg(self, data):
        '''
        Monta um quadro de dados no formato de uma mensagem
        :param data: mensagem a ser transmitida
        '''
        self.msg.clear()
        self.msg.append(self.id_proto_ipv4)
        self.msg = self.msg + data
        self.lower.envia(self.msg)

    def envia(self, data):
        '''
        Trata mensagens vindas da subcamada superior (Fake Layer ou Tun Layer)
        Monta o quadro e o envia para a subcamada inferior (ARQ_MAC)
        :param data: mensagem de dados
        '''
        if (self.is_online):
            self.recarrega_timeout(self.check_interval)
            self.monta_quadro_msg(data)
        else:
           print('\nNÃO HÁ NENHUMA CONEXÃO ESTABELECIDA NO MOMENTO\n')

    def notifica(self, data):
        '''
        Trata mensagens vindas da camada inferior (ARQ_MAC)
        :param data: mensagem para manuntenção da conexão
        '''
        self.handle_fsm(data)

    def notifica_erro(self):
        '''
        Subcamada ARQ_MAC atingiu o limite de tentativas de envio
        e declarou que houve um erro fatal
        '''
        if (self.estado == self.HAND1) or (self.estado == self.HAND2) or \
                (self.estado == self.HAND3) or (self.estado == self.CON) or \
                (self.estado == self.CHECK):
            self.estado = self.HAND1
            self.is_online = False
            self.recarrega_timeout(self.tout)
            self.monta_quadro_manutencao(self.CR)

        elif (self.estado == self.HALF1):
            self.estado = self.DISC
            print('Desconectado')
            self.is_online = False