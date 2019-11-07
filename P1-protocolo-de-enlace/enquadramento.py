import layer, crc

class Enquadramento(layer.Layer):
    '''
    Classe Enquadramento, responsável por montar quadros
    e realizar o controle de erros.
    '''
    # Estados para a FSM
    idle = 0
    rx = 1
    esc = 2

    def __init__(self, serial, bytes_max, timeout):
        '''
        Construtor da classe Enquadramento
        :param serial: Interface serial por qual os dados serão lidos ou escritos
        :param bytes_max: Número máximo de bytes por quadro
        :param timeout: Tempo de timeout em segundos
        '''
        self.serial = serial            # Interface serial
        self.bytes_max = bytes_max      # Número máximo de bytes por quadro
        self.n_bytes = 0                # Número de bytes recebidos
        #self.timeout = timeout

        self.recebido = bytearray()     # Vetor de bytes com os dados recebidos
        self.fcs = crc.CRC16('')        # Objeto do CRC
        self.estado = self.idle         # Estado inicial da FSM

        self.upper = None
        self.lower = None

        self.tout = timeout

        layer.Layer.__init__(self, serial, timeout)

        self.enable()                   # Ativa o monitoramento do objeto
        self.disable_timeout()          # Desativa o Timeout

    def envia(self, data):
        '''
        Realiza a montagem do quadro e o escreve na serial
        :param data: quadro a ser tratado
        :return: quadro já tratado
        '''
        self.fcs = crc.CRC16(data)       # Calcula o FCS
        data_fcs = self.fcs.gen_crc()    # Retorna um objeto bytes com os dados seguidos do valor de FCS

        msg = bytearray()
        msg.append(0x7E)            # Adiciona delimitador de quadro de início

        for octeto in data_fcs:
            if (octeto == 0x7E or octeto == 0x7D):
                i = octeto ^ 0x20   # Realiza a operação XOR 20 com os bytes especiais
                msg.append(0x7D)    # Adiciona byte de escape
                msg.append(i)
            else:
                msg.append(octeto)
        msg.append(0x7E)            # Adiciona delimitador de quadro de fim

        print('tx:', msg)
        self.serial.write(msg)      # Envia a mensagem pela serial


    def notifica(self, data):
        pass

    def handle_fsm(self, byte):
        '''
        Máquina de estado que trata um byte recebido
        :param byte: byte recebido
        '''
        byte = byte.hex()
        byte = int(byte, 16)

        if self.estado == self.idle:
            self._idle(byte)
        elif self.estado == self.rx:
            self._rx(byte)
        else:
            self._esc(byte)

    def _idle(self, byte):
        '''
        Estado inicial da FSM
        :param byte: byte recebido
        '''
        if (byte == 0x7e): # ~
            self.n_bytes = 0
            self.recebido.clear()
            self.recarrega_timeout(self.tout)
            self.estado = self.rx

        else:
            self.estado = self.idle

    def _rx(self, byte):
        '''
        Estado da FSM que lê todos os dados do quadro e trata possíveis erros
        :param byte: byte recebido
        '''
        if (byte == 0x7e and self.n_bytes > 0):
            self.fcs = crc.CRC16('')
            self.fcs.clear()
            self.fcs.update(self.recebido)
            if(self.fcs.check_crc()):
                self.upper.notifica(self.recebido)
            self.disable_timeout()
            self.estado = self.idle

        elif(self.n_bytes > self.bytes_max): # ADICIONAR TIMEOUT
            self.recebido.clear()
            self.disable_timeout()
            self.estado = self.idle

        elif(byte == 0x7e and self.n_bytes == 0):
            self.recarrega_timeout(self.tout)
            self.estado = self.rx

        elif(byte == 0x7d):
            self.estado = self.esc

        else:
            self.n_bytes = self.n_bytes + 1
            self.recebido.append(byte)
            self.recarrega_timeout(self.tout)
            self.estado = self.rx

    def _esc(self, byte):
        '''
        Estado da FSM que trata os bytes especiais
        :param byte: byte recebido
        '''
        if(byte == 0x7e or byte == 0x7d): # ADICIONAR TIMEOUT
            self.recebido.clear()
            self.disable_timeout()
            self.estado = self.idle

        else:
            convertido = byte ^ 0x20
            self.n_bytes = self.n_bytes + 1
            self.recebido.append(convertido)
            self.recarrega_timeout(self.tout)
            self.estado = self.rx

    def handle(self):
        '''
        Lê os dados vindos da serial
        '''
        lido = self.serial.read()
        self.handle_fsm(lido)

    def handle_timeout(self):
        if(self.estado == self.rx) or (self.estado == self.esc):
            self.recebido.clear()
            self.estado == self.idle

    def recarrega_timeout(self, timeout):
        self.base_timeout = timeout
        self.enable_timeout()
        self.reload_timeout()