import layer, crc, time
from random import randint

class ARQ_MAC(layer.Layer):
    '''
    Classe ARQ_MAC, responsável por servir a garantia de entrega
    ao protocolo e o controle de acesso ao meio.
    '''
    # Estados para a FSM
    zero = 0
    um = 1
    dois = 2
    tres = 3

    # Tipos de cabeçalhos de Controle (tipo, n_seq)
    data0 = 0x00    # 00000000
    data1 = 0x08    # 00000100
    ack0 = 0x80     # 10000000
    ack1 = 0x88     # 10000100

    def __init__(self, timeout, time_slot, id, max_retries):
        '''
        Cria um objeto do tipo ARQ_MAC
        :param timeout: Tempo de timeout em segundos
        :param time_slot: Tempo de cada slot do backoff em segundos
        :param id: identificador da sessão
        :param max_retries: número máximo de tentativas de reenvio
        '''
        self.seq_rx = 0                 # Sequência de recepção
        self.seq_tx = 0                 # Sequência de transmissão

        self.limit_retries = max_retries
        self.retries = 0  # Número de tentativas

        self.id_sessao = id  # Identificador da sessão

        self.tout = timeout             # Tempo de espera por ACK
        self.time_slot = time_slot      # Tempo dos slotes para o Slotted Aloha
        self.fila_de_msgs = []          # Fila para armazenar mensagens
        self.estado = self.zero         # Estado inicial da FSM

        self.msg = bytearray()          # Vetor de bytes com os dados enviados

        self.upper = None
        self.lower = None

        self.is_ack = True              # Recepção ou não de um ACK

        layer.Layer.__init__(self, None, timeout)

        self.enable()
        self.disable_timeout()          # Desativa o Timeout

    def handle_fsm(self, data):
        '''
        Máquina de estado que trata o envio e recepção de mensagens
        :param data: mensagem recebida
        '''
        if self.estado == self.zero:
            self._zero(data)
        elif self.estado == self.um:
            self._um(data)
        elif self.estado == self.dois:
            self._dois(data)
        else:
            self._tres(data)

    def _zero(self, data):
        '''
        Estado inicial de transmissão e para recepção
        :param data: mensagem recebida
        '''
        # Recebe uma nova mensagem e envia um ACK
        if ((self.seq_rx == 1) and (data[0] == self.data1)) or ((self.seq_rx == 0) and (data[0] == self.data0)):
            self.estado = self.zero
            self._ack(False)
            self.upper.notifica(data)

        # Recebe uma mensagem já recebida e reenvia um ACK
        elif ((self.seq_rx == 0) and (data[0] == self.data1)) or ((self.seq_rx == 1) and (data[0] == self.data0)):
            self.estado = self.zero
            self._ack(True)

        # Caso tenha recebido o ACK, envia uma nova mensagem
        elif(self.is_ack and not ((data[0] == self.ack1) or (data[0] == self.ack0))):
            self.is_ack = False

            if (self.seq_tx == 1):
                controle = self.data1
            else:
                controle = self.data0

            self.monta_quadro(controle, data)
            self.estado = self.um
            self.upper.disable_all_upper()

            self.recarrega_timeout(self.tout)
            self.lower.envia(self.msg)  # Envia para a subcamada inferior (Enquadramento)

    def monta_quadro(self, controle, data):
        '''
        Monta o quadro com as características do ARQ_MAC
        :param controle: Define tipo DATA ou ACK e número de sequência
        :param data: Quadro originado pela subcamada superior
        :return:
        '''
        self.msg.clear()
        self.msg.append(controle)
        self.msg.append(self.id_sessao)
        self.msg = self.msg + data

    def _um(self, data):
        '''
        Estado final de transmissão e completo para recepção
        :param data: mensagem recebida
        '''

        # Se recebeu o ACK correto, está apto a enviar uma nova mensagem
        if((self.seq_tx == 1) and (data[0] == self.ack1)) or ((self.seq_tx == 0) and (data[0] == self.ack0)):  # esperando seq 1
            self.is_ack = True
            self.seq_tx = not self.seq_tx
            self.estado = self.dois

            backoff = randint(0,7)*self.time_slot
            self.recarrega_timeout(backoff)

        # Recebe uma nova mensagem e envia um ACK
        elif((self.seq_rx == 1) and (data[0] == self.data1)) or ((self.seq_rx == 0) and (data[0] == self.data0)):
            self.estado = self.um
            self._ack(False)
            self.upper.notifica(data)

        # Recebe uma mensagem já recebida e reenvia um ACK
        elif((self.seq_rx == 0) and (data[0] == self.data1)) or ((self.seq_rx == 1) and (data[0] == self.data0)):
            self.estado = self.um
            self._ack(True)

        # Se recebeu o ACK errado, reenvia a mensagem
        else:
            backoff = randint(0,7)*self.time_slot
            self.recarrega_timeout(backoff)
            self.estado = self.tres

    def _dois(self, data):
        # Recebe uma nova mensagem e envia um ACK
        if ((self.seq_rx == 1) and (data[0] == self.data1)) or ((self.seq_rx == 0) and (data[0] == self.data0)):
            self.estado = self.dois
            self.upper.notifica(data)
            self._ack(False)

        # Recebe uma mensagem já recebida e reenvia um ACK
        elif ((self.seq_rx == 0) and (data[0] == self.data1)) or ((self.seq_rx == 1) and (data[0] == self.data0)):
            self.estado = self.dois
            self._ack(True)

    def _tres(self, data):
        # Recebe uma nova mensagem e envia um ACK
        if ((self.seq_rx == 1) and (data[0] == self.data1)) or ((self.seq_rx == 0) and (data[0] == self.data0)):
            self.estado = self.tres
            self.upper.notifica(data)
            self._ack(False)

        # Recebe uma mensagem já recebida e reenvia um ACK
        elif ((self.seq_rx == 0) and (data[0] == self.data1)) or ((self.seq_rx == 1) and (data[0] == self.data0)):
            self.estado = self.tres
            self._ack(True)

    def _ack(self, reenvio):
        '''
        Define o cabeçalho de controle para um ACK
        :param reenvio: garante que o ACK correto seja enviado
        '''
        ack = bytearray()
        seq_envio = self.seq_rx

        # Corrige o número de sequência para o reenvio de ACK
        if(reenvio):
            seq_envio = not self.seq_rx

        if (seq_envio == 1):
            controle = self.ack1
        else:
            controle = self.ack0
        ack.append(controle)
        ack.append(self.id_sessao)

        # Altera o número de sequência de rx quando não for um reenvio de ACK
        if (not reenvio):
            self.seq_rx = not self.seq_rx
        self.lower.envia(ack)    # Envia para a subcamada inferior (Enquadramento)

    def reenvia(self):
        '''
        Realiza o reenvio da mensagem em caso
        de Timeout ou de ACK incorreto
        '''
        self.retries += 1
        self.recarrega_timeout(self.tout)
        self.lower.envia(self.msg)

    def handle(self):
        pass

    def handle_timeout(self):
        '''
        Monitora o timeout a fim de controlar os tempos de backoff e
        reenviar a mensagem quando necessário
        '''
        if self.estado == self.um:
            backoff = randint(0,7)*self.time_slot
            self.recarrega_timeout(backoff)
            self.estado = self.tres

        elif self.estado == self.dois:
            self.disable_timeout()
            self.estado = self.zero

            # Caso haja algo na fila de mensagens, a envia.
            if(len(self.fila_de_msgs) > 0):
                dado = self.fila_de_msgs.pop(0)
                self.handle_fsm(dado)

            self.upper.enable_all_upper()

        elif self.estado == self.tres:
            self.recarrega_timeout(self.tout)
            self.estado = self.um

            # Caso atinja o limite de tentativas de reenvio, declara ERRO FATAL
            if (self.retries == self.limit_retries-1):
                print('\nERRO FATAL: limite de tentativas atingido\n')
                self.retries = 0
                self.is_ack = True
                self.disable_timeout()
                self.estado = self.zero
                self.upper.notifica_erro()
                self.upper.enable_all_upper()
            else:
                self.reenvia()

    def recarrega_timeout(self, timeout):
        '''
        Carrega um novo valor de timeout e o recarrega
        :param timeout: tempo de espera
        '''
        self.base_timeout = timeout
        self.enable_timeout()
        self.reload_timeout()

    def envia(self, data):
        '''
        Recebe uma mensagem e a trata na FSM
        :param data: mensagem a ser enviada
        '''
        # Caso recebeu o ACK da mensagem anterior, envia uma nova mensagem
        if(self.is_ack and self.estado == self.zero):
            self.handle_fsm(data)

        # Trata mensagens inesperadas
        else:
            self.fila_de_msgs.append(data)

    def notifica(self, data):
        '''
        Trata mensagens vindas da subcamada inferior (Enquadramento)
        :param data: mensagem recebida a ser verificada
        '''
        if (data[1] == self.id_sessao):
            print('\nrx: ', data)
            self.handle_fsm(data)