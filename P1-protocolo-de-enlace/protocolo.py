import enquadramento
import serial
import sys, time, os
import arq_mac
import sessao
import fake_layer
import poller
from tun import Tun
import tun_layer

class Protocolo():
    '''
    Classe Protocolo, responsável por administrar a criação de todos os
    objetos e subcamadas necessários para a execução do protocolo.
    '''

    def __init__(self, porta, use_fake, id_sessao, time_slot, max_retries, timeout_arq, timeout_session, check_interval):
        '''
        Cria um objeto Protocolo, responsável por inicializar
        todas as subcamadas
        '''
        if (use_fake):
            self.cb = fake_layer.FakeLayer(sys.stdin)
        else:
            tun = Tun("tun0", "10.0.0.1", "10.0.0.2", mask="255.255.255.252", mtu=1500, qlen=4)
            tun.start()

            self.cb = tun_layer.TunLayer(tun)

        self.e = enquadramento.Enquadramento(porta, 1024, 3)
        self.a = arq_mac.ARQ_MAC(timeout_arq, time_slot, id_sessao, max_retries)
        self.s = sessao.Sessao(timeout_session, check_interval)

        # Define organização das subcamadas
        self.cb.set_lower(self.s)
        self.s.set_upper(self.cb)
        self.s.set_lower(self.a)
        self.a.set_upper(self.s)
        self.a.set_lower(self.e)
        self.e.set_upper(self.a)

    def inicia(self):
        '''
        Inicia o protocolo
        '''
        self.s.start()
        sched = poller.Poller()
        sched.adiciona(self.cb)
        sched.adiciona(self.e)
        sched.adiciona(self.a)
        sched.adiciona(self.s)
        sched.despache()

def instrucoes():
    '''
    Exibe as instruções de uso do protocolo
    '''
    print('Uso: ./protocolo --serial /dev/XXX [opções]\n')
    print('Uso obrigatório:')
    print('--serial /dev/XXX:   caminho da serial\n')
    print('Opções:')
    print('-h:                  mostra esta ajuda')
    print('--fakelayer:         usa o terminal para enviar e receber dados, ao invés da interface tun')
    print('--maxretries n:      limite de retransmissões do ARQ (default: 3)')
    print('--arqtimeout t:      tempo de espera por ACK no ARQ, em segundos (default: 1)')
    print('--idsessao id:       número de identificaçao de sessão (default: 2)')

if __name__ == '__main__':

    use_fake = False
    baudrate = 9600

    # Parâmetros defaults para ARQ_MAC
    id_sessao = 2
    time_slot = 0.5
    max_retries = 3
    timeout_arq = 1

    # Parâmetros defaults para Sessão
    timeout_session = 15
    check_interval = 25

    try:
        for i in range(len(sys.argv)):
            if sys.argv[i] == "-h":
                raise KeyboardInterrupt

            if sys.argv[i] == "--serial":
                num_porta = sys.argv[i + 1]

            if sys.argv[i] == "--fakelayer":
                use_fake = True

            if sys.argv[i] == "--idsessao":
                id_sessao = sys.argv[i + 1]

            if sys.argv[i] == "--maxretries":
                max_retries = sys.argv[i + 1]

            if sys.argv[i] == "--arqtimeout":
                timeout_arq = sys.argv[i + 1]

        porta = serial.Serial(num_porta, baudrate)

        # Converte os valores inseridos
        id_sessao = int(id_sessao)
        time_slot = float(time_slot)
        max_retries = int(max_retries)
        timeout_arq = int(timeout_arq)

        # Calcula o tempo de espera da Sessão de acordo com os tempos de garantia de entrega
        timeout_session = ((time_slot*7)*max_retries) + (timeout_arq*max_retries)

        p = Protocolo(porta, use_fake, id_sessao, time_slot, max_retries, timeout_arq, timeout_session, check_interval)
        p.inicia()

    except:
        instrucoes()

