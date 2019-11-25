import socket
import sensorapp_pb2
from coap import Coap
from random import randint
import time
import poller
from enum import Enum

class Coletor(poller.Callback):
    '''
    Classe Coletor:
    Responsável por coletar amostras de sensores e enviá-los para um servidor
    '''

    class FSM(Enum):
        '''
        Estados da máquina de estados finita
        '''
        inicio = 0
        wait_conf = 1
        ativo = 2
        wait_ack = 3

    def __init__(self, placa, l_sensor, periodo, uri):
        '''
        Cria um objeto Coletor
        :param placa: nome da placa
        :param l_sensor: lista de sensores
        :param periodo: período de amostragem
        :param uri: caminho da uri em bytes
        '''
        self.coap = Coap()
        self.placa = placa
        self.l_sensor = l_sensor
        self.periodo = periodo
        self.uri = uri

        self.state = self.FSM.inicio.value
        self.servidor = ('', 5683)
        self.caminho = ('', 0)
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.bind(self.caminho)

        poller.Callback.__init__(self, self.sock, 5)
        self.enable()

    def sensor_temperatura(self):
        '''
        Simulador de um sensor de temperatura
        :return: nome do sensor, inteiro aleatório, timestamp
        '''
        return 'temperatura', randint(16,30), int(time.time())

    def sensor_luz(self):
        '''
        Simulador de um sensor de luz
        :return: nome do sensor, inteiro aleatório, timestamp
        '''
        return 'luz', randint(0,100), int(time.time())

    def sensor_umidade(self):
        '''
        Simulador de um sensor de umidade
        :return: nome do sensor, inteiro aleatório, timestamp
        '''
        return 'umidade', randint(0,100), int(time.time())

    def coleta_amostras(self):
        '''
        Realiza a coleta das amostras dos sensores e as insere em uma mensagem
        utilizando o formato do Protocol Buffer
        '''
        amostras = []

        msg_temp = sensorapp_pb2.Sensor()
        msg_temp.nome, msg_temp.valor, msg_temp.timestamp = self.sensor_temperatura()
        amostras.append(msg_temp)

        msg_luz = sensorapp_pb2.Sensor()
        msg_luz.nome, msg_luz.valor, msg_luz.timestamp = self.sensor_luz()
        amostras.append(msg_luz)

        msg_umi = sensorapp_pb2.Sensor()
        msg_umi.nome, msg_umi.valor, msg_umi.timestamp = self.sensor_umidade()
        amostras.append(msg_umi)

        dados = sensorapp_pb2.Mensagem()
        dados.placa = 'placa_teste'
        dados.dados.amostras.extend(amostras)
        payload = dados.SerializeToString()

        coleta = self.coap.make_post(payload=payload, uri=self.uri)
        self.handle_fsm(coleta)

    def config(self):
        '''
        Monta um payload do tipo Config que utiliza o formato  do Protocol Buffer
        '''
        msg = sensorapp_pb2.Mensagem()
        msg.placa = self.placa
        msg.config.periodo = self.periodo
        msg.config.sensores.extend(self.l_sensor)
        payload = msg.SerializeToString()

        configuracao = self.coap.make_post(payload=payload, uri=self.uri)
        self.handle_fsm(configuracao)

    def start(self):
        '''
        Inicia a aplicação
        '''
        self.config()

    def handle_fsm(self, msg):
        '''
        Determina o funcionamento da aplicação
        :param msg: mensagem recebida ou que será enviada
        '''
        if self.state == self.FSM.inicio.value:
            self._inicio(msg)
        elif self.state == self.FSM.wait_conf.value:
            self._wait_conf(msg)
        elif self.state == self.FSM.ativo.value:
            self._ativo(msg)
        else:
            self._wait_ack(msg)

    def _inicio(self, msg):
        '''
        Primeiro estado da FSM, responsável por enviar a mensagem de
        configuração.
        :param msg: mesangem de configuração
        '''
        print('inicio >> wait_conf')
        self.state = self.FSM.wait_conf.value
        self.coap.clean_retries()
        self.recarrega_timeout(self.coap.random_ack_timeout())
        self.send(msg)

    def _wait_conf(self, msg):
        '''
        Aguarda a configuração ser aceita. (ACK 2.01 Created)
        :param msg: mensagem recebida.
        '''
        if self.coap.check_code(msg, self.coap.Code.Created.value):
            print('wait_conf >> ativo')
            self.state = self.FSM.ativo.value
        elif self.coap.check_client_error(msg) or self.coap.check_server_error(msg):
            print('wait_conf >> inicio')
            self.state = self.FSM.inicio.value

    def _ativo(self, msg):
        '''
        O sistema está ativo e enviará as amostras disponíveis.
        :param msg: amostras a serem enviadas.
        '''
        print('ativo >> wait_ack')
        self.state = self.FSM.wait_ack.value
        self.recarrega_timeout(self.coap.random_ack_timeout())
        self.coap.clean_retries()
        self.send(msg)

    def _wait_ack(self, msg):
        '''
        Aguarda as amostras serem aceitas. (ACK 2.03 Valid)
        :param msg: mensagem recebida.
        '''
        if self.coap.check_code(msg, self.coap.Code.Valid.value):
            print('wait_ack >> ativo')
            self.state = self.FSM.ativo.value
            self.recarrega_timeout(self.periodo)
        elif self.coap.check_client_error(msg) or self.coap.check_server_error(msg):
            print('wait_ack >> inicio')
            self.state = self.FSM.inicio.value

    def send(self, msg):
        '''
        Envia uma mensagem.
        :param msg: mensagem a ser enviada.
        '''
        print('Msg Enviada: ', msg)
        self.sock.sendto(msg, self.servidor)

    def handle(self):
        '''
        Aguarda receber alguma mensagem via sockets, e então a envia
        para a máquina de estados finita.
        :return:
        '''
        msg_rcv, cliente = self.sock.recvfrom(4096)
        print('Msg Recebida: ', msg_rcv)
        self.handle_fsm(msg_rcv)

    def handle_timeout(self):
        '''
        Monitora o timeout a fim de controlar os tempos de transmissão das amostras
        e reenviar mensagens quando necessário
        '''
        if self.state == self.FSM.ativo.value:
            self.coap.clean_retries()
            self.coleta_amostras()

        elif self.state == self.FSM.wait_ack.value:
            if self.coap.check_retries():
                self.send(self.coap.retransmit())
            else:
                self.state = self.FSM.inicio.value

        elif self.state == self.FSM.wait_conf.value:
            if self.coap.check_retries():
                self.send(self.coap.retransmit())
            else:
                self.state = self.FSM.inicio.value

        else:
            self.start()

    def recarrega_timeout(self, timeout):
        '''
        Carrega um novo valor de timeout e o recarrega
        :param timeout: tempo de espera
        '''
        self.base_timeout = timeout
        self.enable_timeout()
        self.reload_timeout()

if __name__ == "__main__":

    placa = 'placa_teste'
    l_sensor = ['luz', 'temperatura', 'umidade']
    periodo = 5
    uri = b'ptc'

    c = Coletor(placa, l_sensor, periodo, uri)
    c.start()

    sched = poller.Poller()
    sched.adiciona(c)
    sched.despache()