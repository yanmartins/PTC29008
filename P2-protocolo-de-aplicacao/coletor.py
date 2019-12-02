import sensorapp_pb2
from coap import CoAP
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

    def __init__(self, placa, l_sensor, periodo_ms, uri, coap):
        '''
        Cria um objeto Coletor.
        :param placa: nome da placa
        :param l_sensor: lista de sensores
        :param periodo_ms: período de amostragem (ms)
        :param uri: caminho da uri em bytes
        :param coap: objeto do tipo CoAP
        '''
        self.coap = coap

        self.placa = placa
        self.l_sensor = l_sensor
        self.periodo_ms = periodo_ms
        self.periodo = periodo_ms/1000
        self.uri = uri
        self.configuracao = bytearray()

        self.state = self.FSM.inicio.value

        poller.Callback.__init__(self, None, self.periodo)
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
        dados.placa = self.placa
        dados.dados.amostras.extend(amostras)
        payload = dados.SerializeToString()

        #coleta = self.coap.make_post(payload=payload, uri=self.uri)
        self.handle_fsm(payload)

    def config(self):
        '''
        Monta um payload do tipo Config que utiliza o formato  do Protocol Buffer
        '''
        msg = sensorapp_pb2.Mensagem()
        msg.placa = self.placa
        msg.config.periodo = self.periodo_ms
        msg.config.sensores.extend(self.l_sensor)
        payload = msg.SerializeToString()
        self.handle_fsm(payload)
        self.configuracao = payload

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
        print('App: inicio >> wait_conf')
        self.state = self.FSM.wait_conf.value
        self.coap.postar_msg(msg, self.uri)

    def _wait_conf(self, msg):
        '''
        Aguarda a configuração ser aceita.
        :param msg: mensagem recebida.
        '''
        if msg == self.configuracao:
            print('Configuração aceita!')
            self.recarrega_timeout(self.periodo)
            self.state = self.FSM.ativo.value
        else:
            print('Configuração recusada!')
            self.state = self.FSM.inicio.value
            self.disable_timeout()
            self.start()

    def _ativo(self, msg):
        '''
        O sistema está ativo e enviará as amostras disponíveis.
        :param msg: amostras a serem enviadas.
        '''
        print('App: ativo >> wait_ack')
        self.state = self.FSM.wait_ack.value
        self.disable_timeout()
        self.coap.postar_msg(msg, self.uri)

    def _wait_ack(self, msg):
        '''
        Aguarda as amostras serem aceitas.
        :param msg: mensagem recebida.
        '''
        if msg == b'' or msg == self.configuracao:
            print('App: wait_ack >> ativo')
            self.state = self.FSM.ativo.value
            self.recarrega_timeout(self.periodo)

    def handle_timeout(self):
        '''
        Monitora o timeout a fim de controlar os tempos de transmissão das amostras.
        '''
        if self.state == self.FSM.ativo.value:
            self.coap.clean_retries()
            self.coleta_amostras()
            self.disable_timeout()

    def recarrega_timeout(self, timeout):
        '''
        Carrega um novo valor de timeout e o recarrega
        :param timeout: tempo de espera
        '''
        self.base_timeout = timeout
        self.enable_timeout()
        self.reload_timeout()

    def notifica(self, msg):
        '''
        Recebe a notificação da camada inferior
        de que uma mensagem foi recebida.
        '''
        self.handle_fsm(msg)

    def notifica_erro(self):
        '''
        Recebe a notificação da camada inferior
        de que ocorreu um erro.
        '''
        self.state = self.FSM.inicio.value
        self.disable_timeout()
        self.start()

if __name__ == "__main__":

    placa = 'placa_teste'
    l_sensor = ['luz', 'temperatura', 'umidade']
    periodo_ms = 5000
    uri = b'ptc'

    coap = CoAP()
    coletor = Coletor(placa, l_sensor, periodo_ms, uri, coap)
    coap.obter_msg(uri)
    coap.set_upper(coletor)
    coletor.start()

    sched = poller.Poller()
    sched.adiciona(coletor)
    sched.adiciona(coap)
    sched.despache()