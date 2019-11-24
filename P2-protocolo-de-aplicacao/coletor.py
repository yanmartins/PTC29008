import sensorapp_pb2
from coap_client import CoapClient
from random import randint
import time
import poller

class Coletor(poller.Callback):

    def __init__(self, placa, l_sensor, periodo):
        self.coap = CoapClient()
        self.placa = placa
        self.l_sensor = l_sensor
        self.periodo = periodo
        poller.Callback.__init__(self, None, periodo)
        self.enable()

    def sensor_temperatura(self):
        return 'temperatura', randint(16,30), int(time.time())

    def sensor_luz(self):
        return 'luz', randint(0,100), int(time.time())

    def sensor_umidade(self):
        return 'umidade', randint(0,100), int(time.time())

    def coleta_amostras(self):
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
        print(dados)
        print(self.coap.make_post(payload, 'ptc'))

    def config(self):
        msg = sensorapp_pb2.Mensagem()
        msg.placa = self.placa
        msg.config.periodo = self.periodo
        msg.config.sensores.extend(self.l_sensor)
        payload = msg.SerializeToString()
        print(msg)
        print(self.coap.make_post(payload, 'ptc'))

    def start(self):
        self.coleta_amostras()
        self.enable_timeout()

    def handle_timeout(self):
        self.coleta_amostras()

if __name__ == "__main__":

    placa = 'placa_teste'
    l_sensor = ['luz', 'temperatura', 'umidade']
    periodo = 5

    c = Coletor(placa, l_sensor, periodo)
    c.config()
    c.start()

    #c.config()
    #c.coleta_amostras()

    sched = poller.Poller()
    sched.adiciona(c)
    sched.despache()